from pathlib import Path

from app.clients.openai_client import OpenAIReviewClient
from app.schemas.review import AgentResult

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"
SCHEMA_INSTRUCTIONS = """
Return exactly one JSON object with this shape:
{
  "agent": "security | style | architecture",
  "score": 0,
  "summary": "One sentence describing this specialist's review.",
  "reason": "Brief evidence-based reason for the score.",
  "findings": [{
    "line": 1,
    "severity": "info | warning | critical",
    "category": "short category",
    "message": "Specific issue present in the supplied diff",
    "suggestion": "Concrete fix or null"
  }]
}
Use null for an unknown line and null when there is no concrete suggestion. Use an empty findings list when no issue is found. Scores are integers from 0 to 100. Do not invent findings or refer to code outside the supplied patch.
""".strip()


class SpecialistAgent:
    name: str
    prompt_file: str
    focus: str

    def _prompt(self, filename: str, patch: str) -> str:
        existing_prompt = (PROMPT_DIR / self.prompt_file).read_text(encoding="utf-8").strip()
        return (
            f"Specialist: {self.name}. Focus: {self.focus}\n\n"
            "Review only the provided filename and patch. Existing review guidance follows; "
            "retain its intent and apply it to this specialist's domain.\n\n"
            f"Existing prompt:\n{existing_prompt}\n\n"
            f"{SCHEMA_INSTRUCTIONS}\n\nFilename: {filename}\n\nGit diff:\n{patch}"
        )

    async def analyze(
        self,
        client: OpenAIReviewClient,
        *,
        filename: str,
        patch: str,
        semaphore,
    ) -> AgentResult:
        return await client.complete_model(
            agent=self.name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a careful code-review specialist. Be evidence-based and return valid JSON only.",
                },
                {"role": "user", "content": self._prompt(filename, patch)},
            ],
            response_model=AgentResult,
            semaphore=semaphore,
        )
