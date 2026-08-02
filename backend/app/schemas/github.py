from pydantic import BaseModel


class PullRequestInfo(BaseModel):

    repository: str

    owner: str

    number: int

    action: str