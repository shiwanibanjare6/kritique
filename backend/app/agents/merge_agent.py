class MergeAgent:
    def __init__(self) -> None:
        self.name = "merge"

    def evaluate(self, findings: list[dict]) -> dict:
        return {"mergeable": True, "findings": findings}
