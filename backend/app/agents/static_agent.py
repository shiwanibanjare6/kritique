class StaticAgent:
    def __init__(self) -> None:
        self.name = "static"

    def analyze(self, text: str) -> dict:
        return {"message": "Static analysis placeholder", "text": text}
