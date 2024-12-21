from enum import StrEnum, auto

from pydantic import BaseModel, Field


class SearchOperator(StrEnum):
    AND = auto()
    OR = auto()


class SearchPapersInput(BaseModel):
    """Input schema for paper search."""

    keywords: list[str] | None = Field(
        default=None,
        description="List of keywords to search for. Do not use it if you want to search by title. Instead, use the title field.",
        examples=[
            ["Transformer architecture", "Machine Learning"],
            ["Marine Biology"],
            ["Mathematics"],
        ],
    )
    operator: SearchOperator = Field(
        default=SearchOperator.AND, description="Operator to combine the keywords."
    )
    title: str | None = Field(
        default=None,
        description="Title of the papers to search for.",
        examples=["Attention is all you need"],
    )
    year_range: list[int | None] | None = Field(
        default=None,
        description="Year range to search for papers. The first element is the start year (inclusive) and the second element is the end year (inclusive).",
        examples=[[2020, 2024], [2020, None], [None, 2024], [2023, 2023]],
    )
    max_papers: int = Field(
        default=1, ge=1, le=5, description="Maximum number of papers to return."
    )
