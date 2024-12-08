import time
import urllib3

from langchain_core.tools import tool

from nexusai.cache.cache_manager import CacheManager
from nexusai.config import (
    CORE_API_KEY,
    CORE_API_BASE_URL,
    MAX_RETRIES,
    RETRY_BASE_DELAY,
)
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger


class CoreAPIWrapper:
    """Simple wrapper around the CORE API."""

    def __init__(self):
        self.base_url = CORE_API_BASE_URL
        self.api_key = CORE_API_KEY
        self.cache_manager = CacheManager()

    def __get_search_results(self, query: str, max_papers: int = 1) -> list:
        """Execute search query with retry mechanism."""
        if cached_results := self.cache_manager.get_query_results(query):
            logger.info(f"Found search results for '{query}' in cache")
            return cached_results

        http = urllib3.PoolManager()
        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Searching for '{query}' (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            response = http.request(
                "GET",
                f"{self.base_url}/search/outputs",
                headers={"Authorization": f"Bearer {self.api_key}"},
                fields={"q": query, "limit": max_papers},
            )
            if 200 <= response.status < 300:
                logger.info(f"Successfully got search results for '{query}'")
                break
            elif attempt < MAX_RETRIES - 1:
                sleep_time = (
                    60 if response.status == 429 else RETRY_BASE_DELAY ** (attempt + 2)
                )
                logger.warning(
                    f"Got {response.status} response from CORE API. "
                    f"Sleeping for {sleep_time} seconds before retrying..."
                )
                time.sleep(sleep_time)
            else:
                raise Exception(
                    f"Got non 2xx response from CORE API: {response.status}"
                )

        # Store results in cache
        results = response.json().get("results", [])
        self.cache_manager.store_query_results(query, results)
        return results

    def __format_results(self, results: list) -> str:
        """Format the results into a string."""
        if not results:
            return "No relevant results were found"

        docs = []
        for result in results:
            published_date = result.get("publishedDate") or result.get(
                "yearPublished", ""
            )
            authors = result.get("authors", [])
            authors_str = " and ".join([item["name"] for item in authors])
            urls = result.get("sourceFulltextUrls") or result.get("downloadUrl", "")

            doc_info = [
                f"* ID: {result.get('id', '')}",
                f"* Title: {result.get('title', '')}",
                f"* Published Date: {published_date}",
                f"* Authors: {authors_str}",
                f"* Abstract: {result.get('abstract', '')}",
                f"* Paper URLs: {urls}",
            ]
            docs.append("\n".join(doc_info))

        return "\n-----\n".join(docs)

    def search(self, query: str, max_papers: int = 1) -> str:
        """Search for papers and format results."""
        results = self.__get_search_results(query, max_papers)
        formatted_results = self.__format_results(results)
        return formatted_results

    @tool("search-papers", args_schema=SearchPapersInput)
    @staticmethod
    def tool_function(query: str, max_papers: int = 1) -> str:
        """Search for scientific papers using the CORE API. Queries must be in English.

        Example:
        {"query": "Attention is all you need", "max_papers": 1}

        Returns:
            A list of the relevant papers found with the corresponding relevant information.
        """
        try:
            return CoreAPIWrapper().search(query, max_papers)
        except Exception as e:
            return f"Error performing paper search: {e}"
