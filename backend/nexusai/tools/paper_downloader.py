import io
import time

import pdfplumber
import urllib3
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from nexusai.cache.cache_manager import CacheManager
from nexusai.tools.apis.exa import ExaAPIWrapper
from nexusai.config import (
    LLM_PROVIDER,
    MAX_PAGES,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_BASE_DELAY,
)
from nexusai.models.llm import ModelProviderType
from nexusai.utils.strings import arxiv_abs_to_pdf_url
from nexusai.utils.logger import logger

# Disable warnings for insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PaperDownloader:
    """Download a paper from a URL and return the text."""

    query: str | None = None
    chars_per_page: int = 5000  # NOTE: Assuming 5000 is the average page length

    def __init__(self, query: str | None):
        self.query = query
        PaperDownloader.query = query
        self.cache_manager = CacheManager()

        if LLM_PROVIDER == ModelProviderType.openai:
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        elif LLM_PROVIDER == ModelProviderType.azureopenai:
            self.embeddings = AzureOpenAIEmbeddings(
                model="text-embedding-3-small",
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

    def __filter_pages(self, pages: list[str]) -> list[str]:
        """Filter pages with RAG to keep only the most relevant ones."""
        logger.warning(
            f"The paper has more than {MAX_PAGES} pages, filtering content..."
        )
        if not self.query:
            logger.info(
                f"No query provided to filter content by relevance, returning the first {MAX_PAGES} pages"
            )
            return pages[:MAX_PAGES]

        logger.info(f"Generating embeddings for {len(pages)} pages...")
        db = FAISS.from_texts(
            pages,
            self.embeddings,
            metadatas=[{"page_number": i} for i in range(len(pages))],
        )
        logger.info("Searching for most relevant pages...")
        docs = db.similarity_search(self.query, k=MAX_PAGES)
        return [
            doc.page_content
            for doc in sorted(docs, key=lambda x: x.metadata["page_number"])
        ]

    def __convert_bytes_to_text(self, url: str, bytes_content: bytes) -> str:
        """Convert bytes to text."""
        logger.info(f"Converting bytes to text for {url}...")
        pdf_file = io.BytesIO(bytes_content)
        with pdfplumber.open(pdf_file) as pdf:
            pages = []
            for page in pdf.pages:
                pages.append(page.extract_text())
        logger.info(f"Done for {url}")

        self.cache_manager.store_pdf(url, pages)

        if len(pages) > MAX_PAGES:
            pages = self.__filter_pages(pages)

        return "\n\n".join(pages)

    def __filter_text(self, text: str) -> str:
        max_chars = self.chars_per_page * MAX_PAGES
        if len(text) > max_chars:
            logger.warning(
                f"The text is longer than {max_chars} characters, splitting into pages..."
            )
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chars_per_page, chunk_overlap=0
            )
            pages = text_splitter.split_text(text)
            return self.__filter_pages(pages)
        return text

    def download_pdf(self, url: str) -> str:
        """Get PDF from URL or cache if available."""
        logger.info(f"Downloading PDF from {url}...")

        if cached_pages := self.cache_manager.get_pdf(url):
            logger.info(f"Found PDF in cache for {url}")
            if len(cached_pages) > MAX_PAGES:
                cached_pages = self.__filter_pages(cached_pages)
            return "\n".join(cached_pages)

        http = urllib3.PoolManager(
            cert_reqs="CERT_NONE",
            timeout=urllib3.Timeout(connect=10, read=REQUEST_TIMEOUT),
        )
        # Mock browser headers to avoid 403 error
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Downloading PDF from {url} (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            try:
                response = http.request("GET", url, headers=headers)
                if 200 <= response.status < 300:
                    logger.info(f"Successfully downloaded PDF from {url}")
                    break
                elif attempt < MAX_RETRIES - 1 and response.status not in [
                    400,
                    403,
                    404,
                    500,
                ]:
                    logger.warning(
                        f"Got {response.status} response when downloading paper. Sleeping for {RETRY_BASE_DELAY ** (attempt + 1)} seconds before retrying..."
                    )
                    time.sleep(RETRY_BASE_DELAY ** (attempt + 1))
                else:
                    raise Exception(
                        f"Got error response when downloading paper: {response.status}. The URL might be invalid or not available for download."
                    )
            except urllib3.exceptions.TimeoutError:
                raise Exception("Request timed out. Please try again later.")

        return self.__convert_bytes_to_text(url, response.data)

    def download_url_content(self, url: str) -> str:
        """Download the full text of a paper from a given URL."""
        full_text = ExaAPIWrapper().download_url(url)
        return self.__filter_text(full_text)

    def download(self, url: str) -> str:
        """Download the full text of a paper from a given URL. Try to download from PDF first, if not possible, download from URL."""
        url = arxiv_abs_to_pdf_url(url)
        try:
            return self.download_pdf(url)
        except Exception as e:
            logger.warning(f"Error downloading PDF from {url}: {e}")
            return self.download_url_content(url)

    @tool("download-paper")
    @staticmethod
    def tool_function(url: str) -> str:
        """Download the full text of a paper from a given URL.

        Call this tool when you want to access the content of a paper to extract relevant insights.
        For example, the user is asking to analyze a specific paper, or the plan you must follow includes a step where you need to download a paper.

        The tool may occasionally return an error, for example if the provided URL is not available for download.
        If you get an error, acknowledge it and move forward.

        Do not underestimate the importance of this tool. If the user or the plan ask you to download a paper, you must use this tool to follow the plan. Otherwise, the quality of your answer will not be enough.

        Example:
        {"url": "https://sample.pdf"}
        """
        try:
            return PaperDownloader(PaperDownloader.query).download(url)
        except Exception as e:
            return f"Error downloading paper: {e}"
