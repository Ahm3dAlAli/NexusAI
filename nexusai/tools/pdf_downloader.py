import asyncio
import io
import time

import pdfplumber
import urllib3
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings

from nexusai.cache.cache_manager import CacheManager
from nexusai.config import MAX_PAGES, MAX_RETRIES, RETRY_BASE_DELAY
from nexusai.utils.logger import logger

# Disable warnings for insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PDFDownloader:
    query: str = ""

    def __init__(self, query: str):
        self.query = query
        PDFDownloader.query = query
        self.cache_manager = CacheManager()
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def __filter_pages(self, pages: list[str]) -> list[str]:
        """Filter pages with RAG to keep only the most relevant ones."""
        logger.warning(f"The PDF has {MAX_PAGES}, filtering content...")
        logger.info(f"Generating embeddings for {len(pages)} pages...")
        start_time = time.time()
        embeddings = asyncio.run(self.embeddings.aembed_documents(pages))
        db = FAISS.from_embeddings(
            zip(pages, embeddings),
            self.embeddings,
            metadatas=[{"page_number": i} for i in range(len(pages))],
        )
        logger.info(f"Searching for most relevant pages...")
        docs = db.similarity_search(self.query, k=MAX_PAGES)
        end_time = time.time()
        logger.info(f"Filtering pages took {end_time - start_time:.2f} seconds")
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

    def download_pdf(self, url: str) -> str:
        """Get PDF from URL or cache if available."""
        if cached_pages := self.cache_manager.get_pdf(url):
            logger.info(f"Found PDF in cache for {url}")
            if len(cached_pages) > MAX_PAGES:
                cached_pages = self.__filter_pages(cached_pages)
            return "\n".join(cached_pages)

        http = urllib3.PoolManager(
            cert_reqs="CERT_NONE",
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
            response = http.request("GET", url, headers=headers)
            if 200 <= response.status < 300:
                logger.info(f"Successfully downloaded PDF from {url}")
                break
            elif attempt < MAX_RETRIES - 1:
                logger.warning(
                    f"Got {response.status} response when downloading paper. Sleeping for {RETRY_BASE_DELAY ** (attempt + 2)} seconds before retrying..."
                )
                time.sleep(RETRY_BASE_DELAY ** (attempt + 2))
            else:
                raise Exception(
                    f"Got non 2xx when downloading paper: {response.status}"
                )

        return self.__convert_bytes_to_text(url, response.data)

    @tool("download-paper")
    @staticmethod
    def tool_function(url: str) -> str:
        """Download a specific scientific paper from a given URL.

        Example:
        {"url": "https://sample.pdf"}

        Returns:
            The paper content.
        """
        try:
            # Make sure arxiv urls are correctly formatted
            url = url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
            return PDFDownloader(PDFDownloader.query).download_pdf(url)
        except Exception as e:
            return f"Error downloading paper: {e}"
