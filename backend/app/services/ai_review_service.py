import json

from openai import AsyncOpenAI

from app.core.config import settings


class AIReviewService:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

    async def review_code(
        self,
        filename: str,
        patch: str,
    ) -> dict:

        if not patch:
            return {
                "summary": "No code changes available.",
                "security_score": 100,
                "style_score": 100,
                "architecture_score": 100,
                "final_score": 100,
                "comments": [],
            }

        prompt = f"""
You are a Senior Software Engineer reviewing a GitHub Pull Request.

Analyze the following git diff.

Filename:
{filename}

Git Diff:
{patch}

Return ONLY valid JSON.

JSON format:

{{
    "summary":"Overall review summary",

    "security_score":90,
    "style_score":90,
    "architecture_score":90,
    "final_score":90,

    "comments":[
        {{
            "line":1,
            "severity":"info",
            "comment":"Your suggestion."
        }}
    ]
}}

Rules:

- Return ONLY JSON.
- No markdown.
- No explanation.
- line must refer to the added line number if possible.
- severity must be one of:
  info
  warning
  critical
- If there are no issues return an empty comments array.
"""

        response = await self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert software engineer and GitHub code reviewer."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)

        except Exception:

            return {
                "summary": content,
                "security_score": 80,
                "style_score": 80,
                "architecture_score": 80,
                "final_score": 80,
                "comments": [],
            }