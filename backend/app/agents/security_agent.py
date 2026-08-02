class SecurityAgent:
    def __init__(self) -> None:
        self.name = "security"

    def analyze(self, text: str) -> dict:
        return {"message": "Security analysis placeholder", "text": text}
