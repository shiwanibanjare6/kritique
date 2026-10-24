"""Run real old/new review pipelines against saved patches and Groq.

Examples (from repository root):
  python metrics/bench_review.py --fixture-json C:/tmp/pr-diff.json --mode both --runs 3 --files-concurrency 4
  python metrics/bench_review.py --pr-id 123 --mode new --runs 5

The fixture must be a JSON list of {"filename": ..., "patch": ...} objects,
or an object containing that list under "files". No latency is simulated.
"""

import argparse
import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv(BACKEND_DIR / ".env", override=False)

from app.database.session import AsyncSessionLocal
from app.models.pull_request_file import PullRequestFile
from app.services.ai_review_service import AIReviewService


def _read_fixture(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    files = data.get("files") if isinstance(data, dict) else data
    if not isinstance(files, list):
        raise ValueError("Fixture JSON must be a list or an object with a `files` list")
    normalized = []
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("filename"), str):
            raise ValueError("Every fixture file needs a string `filename`")
        normalized.append({"filename": entry["filename"], "patch": entry.get("patch")})
    if not normalized:
        raise ValueError("The fixture contains no pull-request files")
    return normalized


async def _load_pr_files(pr_id: int) -> list[dict]:
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(PullRequestFile.filename, PullRequestFile.patch)
            .where(PullRequestFile.pull_request_id == pr_id)
            .order_by(PullRequestFile.id)
        )).all()
    if not rows:
        raise ValueError(f"No saved diff rows found for pull request id {pr_id}")
    return [{"filename": row.filename, "patch": row.patch} for row in rows]


async def _one_run(files: list[dict], *, mode: str, files_concurrency: int) -> dict:
    service = AIReviewService()
    started = time.perf_counter()
    reviewed = []
    failed = 0
    skipped = 0
    try:
        if mode == "old":
            # Reproduce the former one-call-per-file loop in sequence, then its
            # separate overall PR call. Empty patches made no real provider call.
            summaries = []
            for item in files:
                if not item.get("patch"):
                    skipped += 1
                    continue
                try:
                    result = await service.review_code_legacy(item["filename"], item["patch"])
                    reviewed.append(result)
                    summaries.append(
                        f"File: {item['filename']}\n{result['summary']}\n"
                        f"Scores: security {result['security_score']}, style {result['style_score']}, "
                        f"architecture {result['architecture_score']}, final {result['final_score']}"
                    )
                except Exception:
                    failed += 1
            if reviewed:
                await service.review_pull_request_legacy(summaries)
        else:
            file_gate = asyncio.Semaphore(max(1, files_concurrency))

            async def run_file(item):
                nonlocal skipped, failed
                reason = service.skip_reason(item["filename"], item.get("patch"))
                if reason:
                    skipped += 1
                    return
                async with file_gate:
                    try:
                        result = await service.review_code(item["filename"], item["patch"])
                        reviewed.append(result)
                    except Exception:
                        failed += 1

            await asyncio.gather(*(run_file(item) for item in files))
            if reviewed:
                await service.review_pull_request(reviewed)

        duration = (time.perf_counter() - started) * 1000
        metrics = list(service.pipeline_metrics)
        calls = sum(1 + int(item.get("retries", 0)) for item in metrics)
        return {
            "duration_ms": duration,
            "calls": calls,
            "prompt_tokens": sum(int(item.get("prompt_tokens", 0)) for item in metrics),
            "completion_tokens": sum(int(item.get("completion_tokens", 0)) for item in metrics),
            "estimated_cost": sum(float(item.get("estimated_cost", 0)) for item in metrics),
            "files_reviewed": len(reviewed),
            "files_skipped": skipped,
            "files_failed": failed,
        }
    finally:
        await service.close()


async def _run(args, files):
    modes = ("old", "new") if args.mode == "both" else (args.mode,)
    for mode in modes:
        samples = [
            await _one_run(files, mode=mode, files_concurrency=args.files_concurrency)
            for _ in range(args.runs)
        ]
        median = lambda key: statistics.median(sample[key] for sample in samples)
        total_files = args.runs * len(files)
        failed = sum(sample["files_failed"] for sample in samples)
        attempted = failed + sum(sample["files_reviewed"] + sample["files_skipped"] for sample in samples)
        failure_rate = (failed / attempted * 100) if attempted else 0.0
        print(f"mode={mode} runs={args.runs} files_concurrency={args.files_concurrency}")
        print(f"median_total_ms={median('duration_ms'):.1f}")
        print(f"median_provider_calls={median('calls'):.1f}")
        print(f"median_prompt_tokens={median('prompt_tokens'):.1f}")
        print(f"median_completion_tokens={median('completion_tokens'):.1f}")
        print(f"median_estimated_cost_usd={median('estimated_cost'):.6f}")
        print(f"files_failed={failed}/{attempted} ({failure_rate:.2f}%) across {total_files} input slots")
        print("samples=" + json.dumps(samples, separators=(",", ":")))


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark real Groq review latency and token cost")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--fixture-json", type=Path)
    source.add_argument("--pr-id", type=int)
    parser.add_argument("--mode", choices=("old", "new", "both"), default="new")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--files-concurrency", type=int, default=4)
    args = parser.parse_args()
    if args.runs < 1 or args.files_concurrency < 1:
        parser.error("--runs and --files-concurrency must be positive")
    files = _read_fixture(args.fixture_json) if args.fixture_json else asyncio.run(_load_pr_files(args.pr_id))
    asyncio.run(_run(args, files))


if __name__ == "__main__":
    main()
