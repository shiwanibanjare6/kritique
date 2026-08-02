from pydantic import BaseModel


class WebhookPayload(BaseModel):
    action: str
    repository: str
    number: int