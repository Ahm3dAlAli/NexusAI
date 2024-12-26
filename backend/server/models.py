from enum import StrEnum, auto
from pydantic import BaseModel, model_validator

from nexusai.utils.messages import AgentMessage

class MessageType(StrEnum):
    query = auto()
    init = auto()

class MessageRequest(BaseModel):
    type: MessageType
    messages: list[AgentMessage] | None = None
    query: str | None = None

    @model_validator(mode='after')
    def validate_fields(self) -> 'MessageRequest':
        if self.type == MessageType.init and self.messages is None:
            raise ValueError("Messages are required for init type")
        if self.type == MessageType.query and self.query is None:
            raise ValueError("Query is required for query type")
        return self