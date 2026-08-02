class ReviewerService:
    def __init__(self) -> None:
        self.name = "reviewer"

    def review(self, payload: dict) -> dict:
        return {"summary": "Review pending", "payload": payload}
