from dataclasses import dataclass, field

@dataclass
class ReviewState:
    repository: str = ""
    pull_request_number: int = 0
    findings: list[dict] = field(default_factory=list)
