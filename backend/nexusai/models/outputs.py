import re
from enum import StrEnum, auto

from pydantic import BaseModel, Field, computed_field


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
    order: int
    type: AgentMessageType
    content: str
    tool_name: str | None = None

    @computed_field
    @property
    def urls(self) -> list[str] | None:
        if self.type != AgentMessageType.final:
            return None

        links = re.findall(r"\[.*?\]\((.*?)\)", self.content)
        return list(dict.fromkeys(links))


class PaperOutput(BaseModel):
    """Output object for paper processing."""

    title: str = Field(
        description="The title of the research paper, extracted from the paper content or URL"
    )
    authors: str = Field(
        description="The authors of the paper, formatted as a comma-separated string"
    )
    summary: str = Field(
        description="A concise summary of the paper's key findings and contributions (2-3 paragraphs)"
    )
    url: str = Field(
        description="The original URL where the paper was found. If the paper is from arXiv make sure to replace arxiv.org/abs/ with arxiv.org/pdf/"
    )
