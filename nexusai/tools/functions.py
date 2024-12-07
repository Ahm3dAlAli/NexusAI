import io
import pdfplumber
from langchain_core.tools import tool, BaseTool

from nexusai.tools.pdf_downloader import PDFDownloader
from nexusai.tools.core_api import CoreAPIWrapper
from nexusai.models.inputs import SearchPapersInput


@tool("search-papers", args_schema=SearchPapersInput)
def search_papers(query: str, max_papers: int = 1) -> str:
    """Search for scientific papers using the CORE API. Queries must be in English.

    Example:
    {"query": "Attention is all you need", "max_papers": 1}

    Returns:
        A list of the relevant papers found with the corresponding relevant information.
    """
    try:
        return CoreAPIWrapper(top_k_results=max_papers).search(query)
    except Exception as e:
        return f"Error performing paper search: {e}"

@tool("download-paper")
def download_paper(url: str) -> str:
    """Download a specific scientific paper from a given URL.

    Example:
    {"url": "https://sample.pdf"}

    Returns:
        The paper content.
    """
    try:
        # Make sure arxiv urls are correctly formatted
        url = url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
        return PDFDownloader().download_pdf(url)
    except Exception as e:
        return f"Error downloading paper: {e}"

def setup_tools() -> list[BaseTool]:
    """Setup and return the list of available tools."""
    return [
        search_papers,
        download_paper
    ]