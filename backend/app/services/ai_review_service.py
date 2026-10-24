import asyncio
import fnmatch

from app.agents.architecture_agent import ArchitectureAgent
from app.agents.merge_agent import merge_file_results, merge_pull_request_results
from app.agents.security_agent import SecurityAgent
from app.agents.style_agent import StyleAgent
from app.clients.openai_client import OpenAIReviewClient, ReviewError
from app.core.config import settings
from app.schemas.review import LegacyFileReview, LegacyPullRequestReview, OverallSummaryResponse


class AIReviewService:
    """Three parallel per-file specialists, bounded across the whole PR."""

    def __init__(self, client=None, *, max_concurrent_llm_calls: int | None = None):
        self.client = client or OpenAIReviewClient()
        self.semaphore = asyncio.Semaphore(max(1, max_concurrent_llm_calls or settings.MAX_CONCURRENT_LLM_CALLS))
        self.agents = (SecurityAgent(), StyleAgent(), ArchitectureAgent())

    @property
    def pipeline_metrics(self) -> list[dict]:
        return getattr(self.client, "metrics", [])

    async def review_code(self, filename: str, patch: str) -> dict:
        if not patch:
            raise ReviewError("GitHub did not provide a reviewable patch")
        truncated = len(patch) > settings.MAX_PATCH_CHARS
        patch_for_review = patch[: max(1, settings.MAX_PATCH_CHARS)] if truncated else patch
        results = await asyncio.gather(
            *(
                agent.analyze(
                    self.client,
                    filename=filename,
                    patch=patch_for_review,
                    semaphore=self.semaphore,
                )
                for agent in self.agents
            ),
            return_exceptions=True,
        )
        failures = [result for result in results if isinstance(result, BaseException)]
        if failures:
            first = failures[0]
            if isinstance(first, ReviewError):
                raise first
            raise ReviewError(f"Specialist agent failed: {type(first).__name__}: {first}") from first
        merged = merge_file_results(results)
        merged["truncated"] = truncated
        return merged

    @staticmethod
    def skip_reason(filename: str, patch: str | None) -> str | None:
        return get_skip_reason(filename, patch)

    async def review_pull_request(self, file_reviews: list[dict]) -> dict:
        aggregate = merge_pull_request_results(file_reviews)
        prompt = (
            "Write a concise overall pull-request summary using only the deterministic results below. "
            "Do not recalculate the scores or change risk/recommendation. Avoid inventing context. "
            "Return one JSON object with a single non-empty `summary` string.\n\n"
            f"Files reviewed: {len(file_reviews)}\n"
            f"Mean final score: {aggregate['final_score']:.2f}/100\n"
            f"Risk: {aggregate['risk_level']}\n"
            f"Recommendation: {aggregate['merge_recommendation']}\n"
            "File summaries:\n"
            + "\n".join(f"- {item['summary']}" for item in file_reviews)
        )
        summary_source = "model"
        try:
            result = await self.client.complete_model(
                agent="pull_request_summary",
                messages=[
                    {"role": "system", "content": "Summarize evidence accurately. Return JSON only."},
                    {"role": "user", "content": prompt},
                ],
                response_model=OverallSummaryResponse,
                semaphore=self.semaphore,
            )
            summary = result.summary
        except ReviewError:
            summary = aggregate["code_summary"]
            summary_source = "fallback"
        return {
            **aggregate,
            "summary": summary,
            "summary_source": summary_source,
        }

    async def review_code_legacy(self, filename: str, patch: str) -> dict:
        """One-call historical mode used only by the real benchmark script."""
        if not patch:
            raise ReviewError("Cannot benchmark an empty patch")
        prompt = f"""
You are a senior software engineer reviewing only this changed file and diff.
Filename: {filename}
Diff:
{patch[: max(1, settings.MAX_PATCH_CHARS)]}
Return JSON matching: summary; integer scores 0-100 for security_score, style_score,
architecture_score, final_score; security_reason, style_reason, architecture_reason;
risk_level Low|Medium|High; strengths and weaknesses string arrays;
merge_recommendation Ready to Merge|Merge After Minor Changes|Changes Required;
comments array of {{line (integer or null), severity (info|warning|critical), comment}}.
Mention only evidence from the diff and do not invent issues.
""".strip()
        result = await self.client.complete_model(
            agent="legacy_file_review",
            messages=[
                {"role": "system", "content": "Return a valid review JSON object and no prose outside it."},
                {"role": "user", "content": prompt},
            ],
            response_model=LegacyFileReview,
            semaphore=self.semaphore,
        )
        return result.model_dump(mode="json")

    async def review_pull_request_legacy(self, summaries: list[str]) -> dict:
        prompt = (
            "Review the entire pull request from these per-file summaries. Give a concise overall summary, "
            "merge recommendation, risk, strengths and weaknesses. Do not invent context. Return JSON only.\n\n"
            + "\n\n".join(summaries)
        )
        result = await self.client.complete_model(
            agent="legacy_pull_request_review",
            messages=[
                {"role": "system", "content": "You are a staff engineer completing a final pull-request review."},
                {"role": "user", "content": prompt},
            ],
            response_model=LegacyPullRequestReview,
            semaphore=self.semaphore,
        )
        return result.model_dump(mode="json")

    async def close(self) -> None:
        close = getattr(self.client, "close", None)
        if close is not None:
            await close()


def get_skip_reason(filename: str, patch: str | None) -> str | None:
    if not patch or not patch.strip():
        return "GitHub did not provide a diff patch for this file"
    normalized = filename.replace("\\", "/").casefold()
    patterns = [pattern.strip().casefold() for pattern in settings.REVIEW_FILE_PATTERNS.split(",") if pattern.strip()]
    if any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns):
        return "File matches configured non-reviewable file patterns"
    return None
