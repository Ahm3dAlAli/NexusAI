import asyncio
import io
import time
import random
import requests

import pdfplumber
import urllib3
import cloudscraper
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
from bs4 import (
    BeautifulSoup,
)  # Make sure to install BeautifulSoup: pip install beautifulsoup4

# Disable warnings for insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PaperDownloader:
    """Download content from a URL and extract text."""

    query: str | None = None
    chars_per_page: int = 5000  # Average page length

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

        self.scraper = cloudscraper.create_scraper()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        ]

    def __generate_embeddings(self, pages: list[str]) -> list[str]:
        logger.info(f"Generating embeddings for {len(pages)} pages...")
        embeddings = asyncio.run(self.embeddings.aembed_documents(pages))
        return embeddings

    def __filter_pages(self, pages: list[str]) -> list[str]:
        """Filter pages to keep the most relevant ones."""
        logger.warning(f"The content has more than {MAX_PAGES} pages, filtering...")
        if not self.query:
            logger.info(f"No query provided, returning the first {MAX_PAGES} pages")
            return pages[:MAX_PAGES]

        embeddings = self.__generate_embeddings(pages)
        db = FAISS.from_embeddings(
            zip(pages, embeddings),
            self.embeddings,
            metadatas=[{"page_number": i} for i in range(len(pages))],
        )
        logger.info("Searching for relevant pages...")
        docs = db.similarity_search(self.query, k=MAX_PAGES)
        return [
            doc.page_content
            for doc in sorted(docs, key=lambda x: x.metadata["page_number"])
        ]

    def __convert_text_to_pages(self, url: str, text: str) -> list[str]:
        """Process long text by splitting and filtering if necessary."""
        max_chars = self.chars_per_page * MAX_PAGES
        if len(text) > max_chars:
            logger.warning(
                f"The text is longer than {max_chars} characters, splitting into chunks..."
            )
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chars_per_page, chunk_overlap=0
            )
            pages = text_splitter.split_text(text)
            self.cache_manager.store_content(url, pages)
            return self.__filter_pages(pages)

        pages = [text]
        self.cache_manager.store_content(url, pages)
        return pages

    def __convert_bytes_to_pages(self, url: str, bytes_content: bytes) -> list[str]:
        """Convert PDF bytes to pages."""
        logger.info(f"Converting PDF bytes to pages for {url}...")
        pdf_file = io.BytesIO(bytes_content)
        with pdfplumber.open(pdf_file) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        logger.info(f"Conversion done for {url}")

        self.cache_manager.store_content(url, pages)
        if len(pages) > MAX_PAGES:
            pages = self.__filter_pages(pages)

        return pages

    def _get_random_headers(self) -> dict:
        """Return randomized headers to mimic a browser."""
        header_sets = [
            {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://onlinelibrary.wiley.com/",
                "Upgrade-Insecure-Requests": "1",
            },
            {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://onlinelibrary.wiley.com/",
                "Cache-Control": "max-age=0",
            },
        ]
        return random.choice(header_sets)

    def __handle_response(self, url: str, response: requests.Response) -> str:
        """Convert response content to pages based on content type."""
        content_type = response.headers.get("Content-Type", "").lower()
        if "application/pdf" in content_type:
            logger.info("Processing as PDF...")
            pages = self.__convert_bytes_to_pages(url, response.content)
        else:
            logger.info("Processing as text...")
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            pages = self.__convert_text_to_pages(url, text)
        return "\n\n".join(pages)

    def download_content(self, url: str) -> str:
        """Download content from a URL and process it."""
        url = arxiv_abs_to_pdf_url(url)
        logger.info(f"Downloading content from {url}...")

        if cached_content := self.cache_manager.get_content(url):
            logger.info(f"Found cached content for {url}")
            return "\n\n".join(cached_content)

        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Downloading content from {url} (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            try:
                headers = self._get_random_headers()
                response = self.scraper.get(
                    url, headers=headers, timeout=REQUEST_TIMEOUT
                )
                if 200 <= response.status_code < 300:
                    return self.__handle_response(url, response)
                elif response.status_code == 403:
                    logger.warning("403 Forbidden. Retrying with different headers...")
                    time.sleep(random.uniform(1, 3))
                elif attempt < MAX_RETRIES - 1 and response.status_code not in [
                    400,
                    404,
                    500,
                ]:
                    delay = RETRY_BASE_DELAY ** (attempt + 1)
                    logger.warning(
                        f"Received {response.status_code}. Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                else:
                    raise Exception(
                        f"Error {response.status_code} downloading content from {url}."
                    )
            except Exception as e:
                logger.warning(f"Error: {e}. Retrying...")
                time.sleep(random.uniform(1, 3))
        raise Exception(
            f"Failed to download content from {url} after {MAX_RETRIES} attempts."
        )

    def download(self, url: str) -> str:
        """Attempt to download content, fallback to Exa API if necessary."""
        try:
            return self.download_content(url)
        except Exception as e:
            logger.warning(f"Error downloading content from {url}: {e}")
            logger.warning(f"Fallback to Exa API for {url}")
            return ExaAPIWrapper().download_url(url)

    @tool("download-paper")
    @staticmethod
    def tool_function(url: str) -> str:
        """
        Download a paper from a given URL.

        Call this tool when the user is asking to analyze a specific paper or the plan you must follow tells you to download the paper.

        The tool may return an error, for example if the provided URL is not available for download.
        In that case, acknowledge it and move forward.

        **Important:** If the user or the plan ask you to download a paper, you must use this tool to follow the plan. Otherwise, the quality of your answer will not be enough.

        Example:
        {"url": "https://sample.pdf"}
        """
        try:
            return PaperDownloader(PaperDownloader.query).download(url)
        except Exception as e:
            return f"Error downloading paper: {e}"


if __name__ == "__main__":
    sample_url = "https://blog.samaltman.com/how-to-be-successful"
    print(PaperDownloader(None).download_content(sample_url))
