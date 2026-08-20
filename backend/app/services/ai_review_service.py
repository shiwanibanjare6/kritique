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
    "summary":"Overall review summary",

    "strengths":[
        "Good code organization",
        "Readable implementation"
    ],

    "weaknesses":[
        "Temporary test code found"
    ],

    "recommendation":"Merge After Minor Changes",

    "risk_level":"Low",

    "security_score":90,
    "style_score":90,
    "architecture_score":90,
    "final_score":90,

    "comments":[
        {
            "line":1,
            "severity":"warning",
            "comment":"Remove temporary testing code before merging."
        }
    ]
}

        prompt = f"""
You are a Senior Software Engineer performing a professional GitHub Pull Request review.

You are reviewing ONLY ONE FILE.

Filename:
{filename}

Git Diff:
{patch}

Your job is to review ONLY the supplied git diff.

Analyse:

1. What was changed.
2. Why the change was made.
3. Code quality.
4. Readability.
5. Security.
6. Maintainability.
7. Performance.
8. Architecture.

Specifically detect:

- Debug statements
- Temporary test code
- Dummy values
- Hardcoded secrets
- TODO/FIXME comments
- Placeholder text
- Dead code
- Duplicate code
- Bad naming
- Missing validation
- Poor error handling

If the code is good, clearly say so.

When explaining the summary, mention the ACTUAL code changes whenever possible.

Examples:

GOOD:
"The pull request updates the dashboard layout by replacing fixed width containers with responsive layouts."

GOOD:
"A temporary string 'test webhook 6 august' was added inside the AI summary and should be removed."

BAD:
"This file contains some modifications."

Return ONLY valid JSON.

{{
    "summary":"Detailed review of this file.",

    "security_score":95,
    "security_reason":"Brief explanation.",

    "style_score":92,
    "style_reason":"Brief explanation.",

    "architecture_score":90,
    "architecture_reason":"Brief explanation.",

    "final_score":92,

    "risk_level":"Low",

    "strengths":[
        "...",
        "..."
    ],

    "weaknesses":[
        "...",
        "..."
    ],

    "merge_recommendation":"Ready to Merge | Merge After Minor Changes | Changes Required",

    "comments":[
        {{
            "line":15,
            "severity":"info",
            "comment":"Specific suggestion referring to the changed code."
        }}
    ]
}}

Rules:

- Return ONLY JSON.
- Do NOT invent issues.
- Mention only code present in the diff.
- Mention changed code whenever possible.
- Keep comments concise and actionable.
- Severity must be:
    info
    warning
    critical
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
                "security_reason": "",
                "style_score": 80,
                "style_reason": "",
                "architecture_score": 80,
                "architecture_reason": "",
                "final_score": 80,
                "risk_level": "Medium",
                "strengths": [],
                "weaknesses": [],
                "merge_recommendation": "Merge After Minor Changes",
                "comments": [],
            }

    async def review_pull_request(
        self,
        summaries: list[str],
    ) -> dict:

        prompt = f"""
You are now reviewing the ENTIRE Pull Request.

Below are the AI reviews generated for every changed file.

{chr(10).join(summaries)}

Your task is NOT to review individual files again.

Instead evaluate the WHOLE Pull Request.

Think like a Senior Engineering Manager deciding whether to approve the PR.

Provide:


1. A concise overall summary of the Pull Request.
2. Overall merge recommendation.
3. Overall project quality.
4. Overall risk.
5. Biggest strengths.
6. Biggest weaknesses.

Return ONLY JSON.

{{
    "summary": "Detailed overall assessment of the Pull Request.",
    
    "merge_recommendation":"Ready to Merge | Merge After Minor Changes | Changes Required",

    "risk_level":"Low | Medium | High",

    "strengths":[
        "...",
        "...",
        "..."
    ],

    "weaknesses":[
        "...",
        "...",
        "..."
    ]
}}

Rules:

- Consider the entire PR.
- Do not mention filenames.
- Do not repeat file summaries.
- Give practical strengths and weaknesses.
- Recommend "Ready to Merge" only if the PR is production ready.
"""

        response = await self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Staff Software Engineer performing a final Pull Request approval."
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
                "summary": "Unable to generate an overall Pull Request assessment.",
                "merge_recommendation": "Merge After Minor Changes",
                "risk_level": "Low",
                "strengths": [],
                "weaknesses": [],
            }