import asyncio
from types import SimpleNamespace

import pytest
from app.agents.merge_agent import merge_file_results, merge_pull_request_results
from app.clients.openai_client import OpenAIReviewClient, ReviewError
from app.schemas.review import AgentResult
from app.services.ai_review_service import AIReviewService


def agent_result(agent, *, score=90, severity=None):
    findings = [] if severity is None else [{
        "line": 7,
        "severity": severity,
        "category": "test",
        "message": f"{severity} finding",
        "suggestion": "Fix it",
    }]
    return AgentResult.model_validate({
        "agent": agent,
        "score": score,
        "summary": f"{agent} review summary.",
        "reason": f"{agent} evidence-based reason.",
        "findings": findings,
    })


class BarrierAgentClient:
    def __init__(self):
        self.started = set()
        self.all_started = asyncio.Event()

    async def complete_model(self, *, agent, **_kwargs):
        self.started.add(agent)
        if len(self.started) == 3:
            self.all_started.set()
        await asyncio.wait_for(self.all_started.wait(), timeout=1)
        return agent_result(agent)


def test_three_specialists_start_in_parallel_and_return_merged_review():
    client = BarrierAgentClient()
    service = AIReviewService(client=client)
    result = asyncio.run(service.review_code("src/example.py", "@@ -1 +1 @@\n-a\n+b"))

    assert client.started == {"security", "style", "architecture"}
    assert result["status"] == "reviewed"
    assert result["final_score"] == pytest.approx(90)
    assert result["risk_level"] == "Low"
    assert result["merge_recommendation"] == "Ready to Merge"


def test_weighted_score_and_deterministic_merge_rules():
    merged = merge_file_results([
        agent_result("security", score=100),
        agent_result("style", score=60, severity="warning"),
        agent_result("architecture", score=80),
    ])
    assert merged["final_score"] == pytest.approx(83)
    assert merged["risk_level"] == "Medium"
    assert merged["merge_recommendation"] == "Merge After Minor Changes"

    critical = merge_file_results([
        agent_result("security", score=99, severity="critical"),
        agent_result("style"),
        agent_result("architecture"),
    ])
    assert critical["risk_level"] == "High"
    assert critical["merge_recommendation"] == "Changes Required"


def test_pull_request_aggregates_successful_files_only():
    first = merge_file_results([
        agent_result("security", score=90), agent_result("style", score=90),
        agent_result("architecture", score=90),
    ])
    second = merge_file_results([
        agent_result("security", score=70), agent_result("style", score=70),
        agent_result("architecture", score=70),
    ])
    aggregate = merge_pull_request_results([first, second])
    assert aggregate["final_score"] == pytest.approx(80)
    assert aggregate["final_score"] == pytest.approx((first["final_score"] + second["final_score"]) / 2)
    with pytest.raises(ValueError, match="no successful"):
        merge_pull_request_results([])


def test_skip_patterns_and_patch_truncation(monkeypatch):
    from app.core.config import settings

    assert AIReviewService.skip_reason("assets/logo.png", "binary patch")
    assert AIReviewService.skip_reason("package-lock.json", "lock patch")
    assert AIReviewService.skip_reason("src/no.patch", None)
    assert AIReviewService.skip_reason("src/main.py", "patch") is None

    monkeypatch.setattr(settings, "MAX_PATCH_CHARS", 5)

    class CapturingClient:
        metrics = []

        async def complete_model(self, *, agent, **kwargs):
            assert "@@ ab" in kwargs["messages"][1]["content"]
            return agent_result(agent)

    result = asyncio.run(AIReviewService(client=CapturingClient()).review_code("a.py", "@@ abcdefgh"))
    assert result["truncated"] is True


class FakeCompletionClient:
    def __init__(self, content_responses):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
        self.responses = list(content_responses)
        self.messages = []

    async def create(self, **kwargs):
        self.messages.append(kwargs["messages"])
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=response))],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=4),
        )


def valid_agent_json(agent="security"):
    return (
        '{"agent":"%s","score":91,"summary":"No material issue found.",'
        '"reason":"The diff contains no concrete issue.","findings":[]}' % agent
    )


def test_invalid_agent_response_gets_one_repair_attempt():
    fake = FakeCompletionClient(["not json", valid_agent_json()])
    client = OpenAIReviewClient(fake)
    result = asyncio.run(client.complete_model(
        agent="security", messages=[{"role": "user", "content": "Review"}],
        response_model=AgentResult, semaphore=asyncio.Semaphore(1),
    ))
    assert result.score == 91
    assert len(fake.messages) == 2
    assert "Validation error:" in fake.messages[1][-1]["content"]
    assert client.metrics[0]["retries"] == 1


def test_invalid_response_twice_raises_typed_review_error():
    client = OpenAIReviewClient(FakeCompletionClient(["{}", "{}"] ))
    with pytest.raises(ReviewError, match="after one repair"):
        asyncio.run(client.complete_model(
            agent="security", messages=[{"role": "user", "content": "Review"}],
            response_model=AgentResult, semaphore=asyncio.Semaphore(1),
        ))


def test_retry_after_is_honored_for_429(monkeypatch):
    import app.clients.openai_client as module

    class TooManyRequests(Exception):
        status_code = 429
        response = SimpleNamespace(headers={"retry-after": "1.25"})

    fake = FakeCompletionClient([TooManyRequests("rate limited"), valid_agent_json()])
    client = OpenAIReviewClient(fake)
    sleeps = []

    async def record_sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr(module.asyncio, "sleep", record_sleep)
    result = asyncio.run(client.complete_model(
        agent="security", messages=[{"role": "user", "content": "Review"}],
        response_model=AgentResult, semaphore=asyncio.Semaphore(1),
    ))
    assert result.agent == "security"
    assert sleeps == [1.25]
    assert client.metrics[0]["retries"] == 1


def test_llm_semaphore_bounds_concurrent_requests():
    active = 0
    maximum = 0
    release = asyncio.Event()

    class BlockingClient:
        chat = SimpleNamespace()

        def __init__(self):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        async def create(self, **_kwargs):
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            if maximum == 2:
                release.set()
            await release.wait()
            active -= 1
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=valid_agent_json()))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    async def run():
        client = OpenAIReviewClient(BlockingClient())
        semaphore = asyncio.Semaphore(2)
        await asyncio.gather(*(
            client.complete_model(
                agent="security", messages=[{"role": "user", "content": str(index)}],
                response_model=AgentResult, semaphore=semaphore,
            )
            for index in range(6)
        ))

    asyncio.run(run())
    assert maximum == 2
