class NotificationService:
    def __init__(self) -> None:
        self.name = "notification"

    def send(self, message: str) -> dict:
        return {"sent": True, "message": message}
