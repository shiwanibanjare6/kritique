import asyncio
import json
import random
import re
import time
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import TypeVar

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.schemas.review import AgentResult

T = TypeVar("T", bound=BaseModel)


class ReviewError(Exception):
    """A provider or validation failure that must fail its file review."""

    def __init__(self, message: str, *, agent: str | None = None):
        super().__init__(message)
        self.agent = agent


def _validation_message(error: Exception) -> str:
    if isinstance(error, ValidationError):
        problems = error.errors(include_input=False)
        return "; ".join(
            f"{'.'.join(str(part) for part in issue.get('loc', ()))}: {issue.get('msg', 'invalid value')}"
            for issue in problems
        )[:500]
    return str(error)[:500]


def _status_code(error: Exception) -> int | None:
    response = getattr(error, "response", None)
    return getattr(error, "status_code", None) or getattr(response, "status_code", None)


def _retry_after_seconds(error: Exception) -> float | None:
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", None) or getattr(error, "headers", None) or {}
    value = headers.get("retry-after") or headers.get("Retry-After")
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        try:
            retry_at = parsedate_to_datetime(str(value))
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=UTC)
            return max(0.0, (retry_at - datetime.now(UTC)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


def _extract_json(content: str | None) -> str:
    if not content:
        raise ValueError("The model returned an empty response")
    candidate = content.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", candidate, flags=re.IGNORECASE)
    json.loads(candidate)
    return candidate


class OpenAIReviewClient:
    """OpenAI-compatible client for Groq with bounded retries and strict models."""

    def __init__(self, client=None):
        self.model = settings.REVIEW_MODEL
        self.client = client or AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
            timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=0,
        )
        self.metrics: list[dict] = []

    async def complete_model(
        self,
        *,
        agent: str,
        messages: list[dict[str, str]],
        response_model: type[T],
        semaphore: asyncio.Semaphore,
    ) -> T:
        started = time.perf_counter()
        prompt_tokens = 0
        completion_tokens = 0
        retries = 0
        error_message: str | None = None
        conversation = list(messages)
        try:
            for validation_attempt in range(2):
                response, request_retries = await self._request_with_retries(
                    agent=agent,
                    messages=conversation,
                    semaphore=semaphore,
                )
                retries += request_retries
                usage = getattr(response, "usage", None)
                prompt_tokens += int(getattr(usage, "prompt_tokens", 0) or 0)
                completion_tokens += int(getattr(usage, "completion_tokens", 0) or 0)
                content = response.choices[0].message.content
                try:
                    raw_json = _extract_json(content)
                    parsed = response_model.model_validate_json(raw_json)
                    if isinstance(parsed, AgentResult) and parsed.agent != agent:
                        raise ValueError(f"Expected agent={agent!r}, got {parsed.agent!r}")
                    return parsed
                except (ValidationError, ValueError, json.JSONDecodeError) as error:
                    error_message = _validation_message(error)
                    if validation_attempt == 1:
                        raise ReviewError(
                            f"{agent} response failed schema validation after one repair: {error_message}",
                            agent=agent,
                        ) from error
                    retries += 1
                    conversation.extend([
                        {"role": "assistant", "content": content or ""},
                        {
                            "role": "user",
                            "content": (
                                "Repair your previous response. It did not validate against the required schema. "
                                f"Validation error: {error_message}. Return only corrected JSON matching the schema."
                            ),
                        },
                    ])
        except ReviewError as error:
            error_message = str(error)
            raise
        except Exception as error:
            error_message = f"{type(error).__name__}"
            raise ReviewError(error_message, agent=agent) from error
        finally:
            cost = (
                prompt_tokens * settings.REVIEW_INPUT_USD_PER_MILLION / 1_000_000
                + completion_tokens * settings.REVIEW_OUTPUT_USD_PER_MILLION / 1_000_000
            )
            self.metrics.append({
                "agent": agent,
                "model": self.model,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "retries": retries,
                "estimated_cost": round(cost, 8),
                **({"error": error_message[:500]} if error_message else {}),
            })
        raise ReviewError("No model response was received", agent=agent)

    async def _request_with_retries(
        self,
        *,
        agent: str,
        messages: list[dict[str, str]],
        semaphore: asyncio.Semaphore,
    ):
        retries = 0
        while True:
            try:
                async with semaphore:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        temperature=0.2,
                        response_format={"type": "json_object"},
                        messages=messages,
                    )
                return response, retries
            except Exception as error:
                status = _status_code(error)
                retryable = (
                    isinstance(error, (APITimeoutError, APIConnectionError, RateLimitError))
                    or status == 429
                    or status == 408
                    or (status is not None and status >= 500)
                    or (isinstance(error, APIStatusError) and status is not None and status >= 500)
                )
                if not retryable or retries >= settings.LLM_MAX_RETRIES:
                    raise ReviewError(
                        f"{agent} model request failed ({type(error).__name__})",
                        agent=agent,
                    ) from error
                local_delay = min(
                    settings.LLM_RETRY_BASE_SECONDS * (2 ** retries) + random.uniform(0, settings.LLM_RETRY_JITTER_SECONDS),
                    settings.LLM_RETRY_MAX_SECONDS,
                )
                delay = max(local_delay, _retry_after_seconds(error) or 0.0)
                retries += 1
                await asyncio.sleep(delay)

    async def close(self) -> None:
        close = getattr(self.client, "close", None) or getattr(self.client, "aclose", None)
        if close is not None:
            await close()
