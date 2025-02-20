from enum import StrEnum, auto

from pydantic import BaseModel, Field


class SearchType(StrEnum):
    title = auto()
    narrow = auto()
    broad = auto()


class SearchPapersInput(BaseModel):
    """Input schema for paper search."""

    query: str = Field(
        description=(
            "Search query to use to find papers and articles. "
            "You should use different queries to search for more papers. Make sure to include the following in your trials:\n"
            "1. The user query\n"
            "2. Queries that are more specific than the user query\n"
            "3. Queries that are more general than the user query"
        ),
    )
    search_type: SearchType = Field(
        default=SearchType.narrow,
        description=(
            "Type of scientific research to perform from the most specific to the most general:\n"
            "* 'title': Use this option if your plan requires searching for a paper by title. "
            "* 'narrow': Use this option if your plan requires you to download and analyze the papers you find. "
            "* 'broad': Use this option when your plan does not require downloading papers or as a fallback when the 'narrow' option does not return enough results."
        ),
    )
    date_range: list[int | None] = Field(
        default=[None, None],
        description=(
            "A list of two integers to filter the search by date. "
            "The first integer is the start year, and the second integer is the end year. "
            "If not provided, no date filtering will be applied."
        ),
        examples=[
            [None, None],
            [2020, None],
            [None, 2024],
            [2020, 2024],
        ],
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
        le=10,
        description="Number of results to return. Adjust this number based on the user query. It must be <=10.",
    )
