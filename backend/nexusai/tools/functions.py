from langchain_core.tools import BaseTool, tool
from nexusai.models.inputs import SearchPapersInput
from nexusai.tools.apis import *
from nexusai.tools.paper_downloader import PaperDownloader
from nexusai.utils.logger import logger


@tool("search-papers", args_schema=SearchPapersInput)
def search_papers(**kwargs) -> str:
    """Search engine for scientific papers and articles. Use this tool to search for scientific papers and articles online.

    This tool has access to most of the web. Its results should include a link to the paper PDF or page on the publisher website.
    However, results might not always be relevant or include a link, for example if the paper is behind a paywall.
    If the results are not useful to answer the user query, you must try several times with different queries or search types, to make sure you're not missing any relevant results.
    Only afterwards, you can assume there are no relevant results and inform the user.

    Your query must be in English unless the user is asking for specific items, like a paper with a non-English title.
    """
    try:
        input = SearchPapersInput(**kwargs)
        providers = [SerperAPIWrapper(), ExaAPIWrapper()]
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
        PaperDownloader(query).tool_function,
    ]
