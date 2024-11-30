import io
import time
import urllib3
import pdfplumber

from langchain_core.tools import tool

from ..config import MAX_RETRIES, RETRY_BASE_DELAY
from .core_api import CoreAPIWrapper
from ..models.inputs import SearchPapersInput

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
        http = urllib3.PoolManager(
            cert_reqs='CERT_NONE',
        )
        
        # Mock browser headers to avoid 403 error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        for attempt in range(MAX_RETRIES):
            response = http.request('GET', url, headers=headers)
            if 200 <= response.status < 300:
                pdf_file = io.BytesIO(response.data)
                with pdfplumber.open(pdf_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                return text
            elif attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY ** (attempt + 2))
            else:
                raise Exception(f"Got non 2xx when downloading paper: {response.status_code} {response.text}")
    except Exception as e:
        return f"Error downloading paper: {e}"

@tool("ask-human-feedback")
def ask_human_feedback(question: str) -> str:
    """You must call this tool when encountering unexpected errors or don't know how to proceed.
    The question must be in the same language as the user query.
    
    Example:
    After encountering an error downloading a paper, you call this tool with the following input:
    {"question": "There seems to be an issue downloading the paper with the given URL, how should I proceed?"}
    
    Returns:
        Further instructions from the human.
    """
    return input(question)

