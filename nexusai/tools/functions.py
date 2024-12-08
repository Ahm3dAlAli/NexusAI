from langchain_core.tools import BaseTool

from nexusai.tools.pdf_downloader import PDFDownloader
from nexusai.tools.core_api import CoreAPIWrapper


def setup_tools(query: str) -> list[BaseTool]:
    """Setup and return the list of available tools."""
    return [CoreAPIWrapper().tool_function, PDFDownloader(query).tool_function]
