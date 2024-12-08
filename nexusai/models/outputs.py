from enum import StrEnum, auto
from pydantic import BaseModel, Field


class DecisionMakingOutput(BaseModel):
    """Output object of the decision making node."""

    requires_research: bool = Field(
        description="Whether the user query requires research or not."
    )
    answer: str | None = Field(
        default=None,
        description="The answer to the user query. It should be None if the user query requires research, otherwise it should be a direct answer to the user query.",
    )


class JudgeOutput(BaseModel):
    """Output object of the judge node."""

    is_good_answer: bool = Field(description="Whether the answer is good or not.")
    feedback: str | None = Field(
        default=None,
        description="Detailed feedback about why the answer is not good. It should be None if the answer is good.",
    )


class AgentMessageType(StrEnum):
    system = auto()
    human = auto()
    agent = auto()
    tool = auto()
    error = auto()
    final = auto()


class AgentMessage(BaseModel):
    type: AgentMessageType
    content: str
    tool_name: str | None = None
