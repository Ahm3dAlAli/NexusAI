from langchain_core.tools import BaseTool

from nexusai.tools.core_api import CoreAPIWrapper
from nexusai.tools.semantic_api import SemanticScholarAPIWrapper
from nexusai.tools.pdf_downloader import PDFDownloader
from nexusai.tools.table_analysis import TableAnalyzer



def setup_tools(query: str) -> list[BaseTool]:
    """Setup and return the list of available tools."""
    return [CoreAPIWrapper().tool_function,
            SemanticScholarAPIWrapper().tool_function, 
            PDFDownloader(query).tool_function,
            TableAnalyzer().extract_tables,
            TableAnalyzer().compare_tables]
