from pydantic import BaseModel, Field

class SearchPapersInput(BaseModel):
    """Input schema for paper search."""
    query: str = Field(description="The query to search for on the selected archive.")
    max_papers: int = Field(
        description="Maximum number of papers to return (1-10).",
        default=1,
        ge=1,
        le=10
    )
