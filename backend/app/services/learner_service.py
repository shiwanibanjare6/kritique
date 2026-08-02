class LearnerService:
    def __init__(self) -> None:
        self.name = "learner"

    def learn(self, feedback: list[dict]) -> dict:
        return {"learned": len(feedback)}
