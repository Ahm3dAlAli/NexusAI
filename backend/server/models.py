from nexusai.utils.messages import AgentMessage
from pydantic import BaseModel


class MessageRequest(BaseModel):
    history: list[AgentMessage] | None = None
    query: str | None = None
