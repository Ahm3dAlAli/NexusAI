from langchain_core.tools import BaseTool, tool

from nexusai.config import PROVIDERS
from nexusai.models.inputs import SearchPapersInput
from nexusai.tools.apis import providers_list
from nexusai.tools.pdf_downloader import PDFDownloader
from nexusai.utils.logger import logger
from nexusai.config import MEM0_API_KEY
from nexusai.tools.memory import MemoryTools

@tool("search-papers", args_schema=SearchPapersInput)
def search_papers(**kwargs) -> str:
    """Search engine for scientific papers.

    This search is limited to English papers. Therefore, keywords, title, and any other search terms must be in English.
    If you are asked to search for papers with non-English terms, translate them to English first.

    Returns:
        A list of the relevant papers found with the corresponding relevant information.
    """
    apis = [provider() for provider in providers_list if provider.name in PROVIDERS]

    input = SearchPapersInput(**kwargs)
    for api in apis:
        try:
            results = api.search(input)
            if results:
                return results
        except Exception as e:
            logger.warning(
                f"Error performing paper search with {api.__class__.__name__}: {e}"
            )
    return "No results found."


def setup_tools(query: str, user_id: str = None) -> list[BaseTool]:
    """Setup and return the list of available tools."""
    tools = [
        search_papers,
        PDFDownloader(query).tool_function,
    ]
    
    # Add memory tools if user_id is provided
    if user_id and MEM0_API_KEY:
        memory_tools = MemoryTools().get_tools()
        tools.extend(memory_tools)
    
    return tools