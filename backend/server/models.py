from nexusai.utils.messages import AgentMessage
from pydantic import BaseModel


class PapersRequest(BaseModel):
    urls: list[str]


class MessageRequest(BaseModel):
    history: list[AgentMessage] | None = None
    query: str | None = None
