from nexusai.utils.messages import AgentMessage
from pydantic import BaseModel, Field


class PapersRequest(BaseModel):
    urls: list[str] = Field(..., max_length=8, description="List of paper URLs to process. Maximum 8 papers at once.")


class MessageRequest(BaseModel):
    history: list[AgentMessage] | None = None
    query: str | None = None
    custom_instructions: list[str] = []
