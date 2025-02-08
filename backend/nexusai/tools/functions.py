from langchain_core.tools import BaseTool, tool
from nexusai.models.inputs import SearchPapersInput, SearchType
from nexusai.tools.apis import *
from nexusai.tools.pdf_downloader import PDFDownloader
from nexusai.utils.logger import logger


@tool("search-papers", args_schema=SearchPapersInput)
def search_papers(**kwargs) -> str:
    """Search engine for scientific papers and articles. Use this tool to search for scientific papers and articles online.

    This tool has access to most of the web, and should be able to find relevant content or include results with a link to download a specific paper.
    However, keep in mind that this tool is not perfect, it might return irrelevant results or not work on a first try, or simply doesn't have access to the URL of a specific resource, for example if it's behind a paywall.
    Before assuming relevant results cannot be found, try calling the tool several times with different queries or search types.
    If you have called the tool several times, with different search approaches, and were unable to find relevant results, inform the user and move forward.

    Your query must be in English. You're only allowed to use non-English terms if you are looking for specific items, like a paper with a non-English title.
    The coverage for non-English papers might be limited.
    """
    try:
        input = SearchPapersInput(**kwargs)

        # SerperAPI works better when searching for a specific title or a date range
        if input.search_type == SearchType.title or any(input.date_range):
            providers = [SerperAPIWrapper(), ExaAPIWrapper()]
        else:
            providers = [ExaAPIWrapper(), SerperAPIWrapper()]

        for provider in providers:
            try:
                return provider.search(input)
            except Exception as e:
                logger.warning(
                    f"Error performing paper search with {provider.__class__.__name__}: {e}"
                )
    except Exception as e:
        logger.error(f"Error performing paper search: {e}")
        return "No results found."


def setup_tools(query: str) -> list[BaseTool]:
    """Setup and return the list of available tools."""
    return [
        search_papers,
        PDFDownloader(query).tool_function,
    ]
