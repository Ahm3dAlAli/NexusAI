from enum import StrEnum, auto

from pydantic import BaseModel


class ModelProviderType(StrEnum):
    default = auto()
    azureopenai = auto()
    openai = auto()


class ProviderDetails(BaseModel):
    key: str | None = None
    endpoint: str | None = None
