import time

import urllib3

from nexusai.cache.cache_manager import CacheManager
from nexusai.config import (
    CORE_API_BASE_URL,
    CORE_API_KEY,
    MAX_RETRIES,
    RETRY_BASE_DELAY,
)
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger


class CoreAPIWrapper:
    """Wrapper around the CORE API."""

    name = "core"

    def __init__(self):
        self.base_url = CORE_API_BASE_URL
        self.api_key = CORE_API_KEY

        # Redis cache
        self.cache_manager = CacheManager()

    def __build_query(self, input: SearchPapersInput) -> str:
        """Build the query for the CORE API."""
        query = ""
        if input.keywords:
            query += f" {input.operator.value.upper()} ".join(
                [f'"{keyword}"' for keyword in input.keywords]
            )
        if input.title:
            query += f' title:"{input.title}"'
        if input.year_range:
            if input.year_range[0]:
                query += f" yearPublished>={input.year_range[0]}"
            if input.year_range[1]:
                query += f" yearPublished<={input.year_range[1]}"
        logger.info(f"Built CORE query: {query}")
        return query

    def __get_search_results(self, query: str, max_papers: int = 1) -> list:
        """Execute search query with retry mechanism."""
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
                results = response.json().get("results")
                if not results:
                    raise Exception(f"No results found from CORE for '{query}'")
                logger.info(f"Successfully got CORE search results for '{query}'")
                return results
            elif attempt < MAX_RETRIES - 1 and response.status not in [429, 500]:
                sleep_time = RETRY_BASE_DELAY ** (attempt + 2)
                logger.warning(
                    f"Got {response.status} response from CORE API. "
                    f"Sleeping for {sleep_time} seconds before retrying..."
                )
                time.sleep(sleep_time)
            else:
                raise Exception(
                    f"Got non 2xx response from CORE API: {response.status}"
                )

    def __format_results(self, results: list) -> str:
        """Format the results into a string."""
        docs = []
        for result in results:
            published_date = result.get("publishedDate") or result.get(
                "yearPublished", ""
            )
            authors = result.get("authors", [])
            authors_str = " and ".join([item["name"] for item in authors])
            urls = result.get("sourceFulltextUrls") or result.get("downloadUrl", "")

            doc_info = [
                f"* Title: {result.get('title', '')}",
                f"* Published Date: {published_date}",
                f"* Authors: {authors_str}",
                f"* Abstract: {result.get('abstract', '')}",
                f"* Paper URLs: {urls}",
            ]
            docs.append("\n".join(doc_info))

        return "\n-----\n".join(docs)

    def search(self, input: SearchPapersInput) -> str:
        """Search for papers and format results."""
        if cached_results := self.cache_manager.get_search_results(input):
            logger.info(
                f"Found CORE search results for '{input.model_dump_json()}' in cache"
            )
            return cached_results

        query = self.__build_query(input)
        results = self.__get_search_results(query, input.max_papers)
        formatted_results = self.__format_results(results)

        # Cache the results
        self.cache_manager.store_search_results(input, formatted_results)
        return formatted_results
