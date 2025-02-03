from nexusai.models.inputs import ModelProviderType, ProviderDetails
from nexusai.utils.messages import AgentMessage
from pydantic import BaseModel, Field


class PapersRequest(BaseModel):
    urls: list[str] = Field(..., max_length=8)


class MessageRequest(BaseModel):
    history: list[AgentMessage] | None = None
    query: str | None = None
    custom_instructions: list[str] = []
    model_provider: ModelProviderType = ModelProviderType.default
    provider_details: ProviderDetails | None = None
