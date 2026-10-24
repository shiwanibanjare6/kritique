from app.core.config import settings
from app.schemas.review import AgentResult

SEVERITY_RANK = {"info": 0, "warning": 1, "critical": 2}


def _weights() -> dict[str, float]:
    weights = {
        "security": settings.SECURITY_SCORE_WEIGHT,
        "style": settings.STYLE_SCORE_WEIGHT,
        "architecture": settings.ARCHITECTURE_SCORE_WEIGHT,
    }
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Review score weights must sum to a positive value")
    return {name: weight / total for name, weight in weights.items()}


def merge_file_results(results: list[AgentResult]) -> dict:
    by_agent = {result.agent: result for result in results}
    required = {"security", "style", "architecture"}
    if set(by_agent) != required:
        raise ValueError("A file review requires exactly one result from each specialist")
    weights = _weights()
    agent_order = ("security", "style", "architecture")
    final_score = sum(by_agent[name].score * weights[name] for name in agent_order)

    findings = [
        (result.agent, finding)
        for result in results
        for finding in result.findings
    ]
    findings.sort(key=lambda pair: (-SEVERITY_RANK[pair[1].severity], pair[0], pair[1].line or 0))
    max_severity = max((finding.severity for _, finding in findings), key=SEVERITY_RANK.get, default="info")

    # A critical finding always blocks merge. Otherwise score bands and warnings
    # map explicitly to risk and recommendation, independent of LLM prose.
    if max_severity == "critical" or final_score < 60:
        risk_level, recommendation = "High", "Changes Required"
    elif max_severity == "warning" or final_score < 80:
        risk_level, recommendation = "Medium", "Merge After Minor Changes"
    else:
        risk_level, recommendation = "Low", "Ready to Merge"

    ordered_results = sorted(
        results,
        key=lambda result: (
            -max((SEVERITY_RANK[f.severity] for f in result.findings), default=0),
            ("security", "style", "architecture").index(result.agent),
        ),
    )
    summary = " ".join(f"{result.agent.title()}: {result.summary.strip()}" for result in ordered_results)
    strengths = [result.summary.strip() for result in results if result.score >= 80]
    weaknesses = [result.reason.strip() for result in results if result.score < 80 and result.reason.strip()]
    comments = [
        {
            "line": finding.line,
            "severity": finding.severity,
            "comment": finding.message,
            "category": finding.category,
            "suggestion": finding.suggestion,
            "agent": agent,
        }
        for agent, finding in findings
    ]
    for _, finding in findings:
        if finding.severity in {"warning", "critical"} and finding.message not in weaknesses:
            weaknesses.append(finding.message)

    return {
        "status": "reviewed",
        "summary": summary,
        "security_score": by_agent["security"].score,
        "security_reason": by_agent["security"].reason,
        "style_score": by_agent["style"].score,
        "style_reason": by_agent["style"].reason,
        "architecture_score": by_agent["architecture"].score,
        "architecture_reason": by_agent["architecture"].reason,
        "final_score": final_score,
        "risk_level": risk_level,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "merge_recommendation": recommendation,
        "comments": comments,
        "agent_results": [result.model_dump(mode="json") for result in results],
    }


def merge_pull_request_results(file_reviews: list[dict]) -> dict:
    """Aggregate only successful file reviews; critical findings always block."""
    if not file_reviews:
        raise ValueError("Cannot aggregate a pull request with no successful file reviews")
    fields = ("security_score", "style_score", "architecture_score", "final_score")
    scores = {name: sum(float(item[name]) for item in file_reviews) / len(file_reviews) for name in fields}
    risk_order = {"Low": 0, "Medium": 1, "High": 2}
    risk_level = max((item["risk_level"] for item in file_reviews), key=risk_order.get)
    critical = any(
        comment.get("severity") == "critical"
        for item in file_reviews
        for comment in item.get("comments", [])
    )
    if critical or scores["final_score"] < 60 or risk_level == "High":
        recommendation = "Changes Required"
    elif risk_level == "Medium" or scores["final_score"] < 80:
        recommendation = "Merge After Minor Changes"
    else:
        recommendation = "Ready to Merge"
    strengths = list(dict.fromkeys(value for item in file_reviews for value in item.get("strengths", [])))
    weaknesses = list(dict.fromkeys(value for item in file_reviews for value in item.get("weaknesses", [])))
    code_summary = (
        f"Reviewed {len(file_reviews)} changed file(s). "
        f"The mean final score is {scores['final_score']:.2f}/100; "
        f"the highest file risk is {risk_level.lower()}."
    )
    return {
        **scores,
        "risk_level": risk_level,
        "merge_recommendation": recommendation,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "code_summary": code_summary,
    }
