from enum import StrEnum, auto

from pydantic import BaseModel, Field


class SearchType(StrEnum):
    narrow = auto()
    broad = auto()


class SearchPapersInput(BaseModel):
    """Input schema for paper search."""

    query: str = Field(
        ...,
        description=(
            "A descriptive, natural language query that will be used to search for papers and articles. "
            "It doesn't need to be keyword-optimized. Since results are ranked based on semantic similarity, it should be as semantically similar as possible to the results you are looking for. "
            "Using double-quotes (\") will make the search prioritize exact matches. Use them when looking for specific papers, authors, or titles."
        ),
    )
    search_type: SearchType = Field(
        default=SearchType.narrow,
        description=(
            "Type of scientific research to perform:\n"
            "* 'narrow': Use this option if your plan requires you to download and analyze the papers you find. "
            "* 'broad': Use this option when your plan does not require downloading papers or as a fallback when the 'narrow' option does not return enough results."
        ),
    )
    summarization_prompt: str | None = Field(
        default=None,
        description=(
            "A prompt that will be used by an LLM to summarize the content of each result of the search. "
            "If not provided, the first 1000 characters of each result will be returned. "
            "Use this option if you want to extract specific insights from the results. Be as detailed and clear as possible about the type of information you want to extract to guide the LLM effectively."
            "If you need high-level information without the need to go into details, avoid using this option as it will make the tool slower and more expensive."
        ),
    )
    max_results: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Number of results to return. Adjust this number based on the user query. It must be <=5.",
    )
