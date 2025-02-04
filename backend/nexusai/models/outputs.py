import re
from enum import StrEnum, auto

from nexusai.utils.arxiv import url_to_pdf_url
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

        links: list[str] = re.findall(r"\[.*?\]\((.*?)\)", self.content)
        links = list(dict.fromkeys(links))

        # Make sure arxiv urls are correctly formatted
        links = [url_to_pdf_url(link) for link in links]
        return links


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
    url: str = Field(description="The paper URL.")
