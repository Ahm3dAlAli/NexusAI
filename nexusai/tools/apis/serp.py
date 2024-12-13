import time

import urllib3
from dotenv import load_dotenv

from nexusai.cache.cache_manager import CacheManager
from nexusai.config import (
    MAX_RETRIES,
    RETRY_BASE_DELAY,
    SERP_API_BASE_URL,
    SERP_API_KEY,
)
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger

load_dotenv()


class SerpAPIWrapper:
    """Wrapper around the Google SERP API for academic search.

    It enriches the Google query by filtering for databases for academic papers and PDF results to increase the relevance of the results.
    It doesn't use the Google Scholar API as it doesn't have the same coverage as Google Search.

    It's used as the final API in the pipeline to get relevant results.
    """

    name = "serp"

    def __init__(self):
        self.base_url = SERP_API_BASE_URL
        self.api_key = SERP_API_KEY
        self.sites = [
            "core.ac.uk",
            "doaj.org",
            "scienceopen.org",
            "ncbi.nlm.nih.gov/pmc",
            "arxiv.org",
            "zenodo.org",
            "scielo.org",
        ]

        # Redis cache
        self.cache_manager = CacheManager()

    def __build_query(self, input: SearchPapersInput) -> str:
        """Build the query for the SERP API."""
        query = ""
        if input.keywords:
            query += f" {input.operator.value.upper()} ".join(
                [f"'{keyword}'" for keyword in input.keywords]
            )
        if input.title:
            query += f" intitle:'{input.title}'"
        if input.year_range:
            if input.year_range[0]:
                query += f" after:{input.year_range[0]}"
            if input.year_range[1]:
                query += f" before:{input.year_range[1] + 1}"
        query = f"site:({' OR '.join(self.sites)}) {query} filetype:pdf"
        logger.info(f"Built SERP query: {query}")
        return query

    def __get_search_results(self, query: str, max_papers: int = 1) -> list:
        """Execute search query with retry mechanism."""
        http = urllib3.PoolManager()
        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Searching SERP for '{query}' (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            response = http.request(
                "GET",
                f"{self.base_url}/search",
                fields={
                    "api_key": self.api_key,
                    "q": query,
                    "num": max_papers,
                    "engine": "google",
                },
            )
            if 200 <= response.status < 300:
                results = response.json().get("organic_results", [])
                if not results:
                    raise Exception(f"No results found from SERP for '{query}'")
                logger.info(f"Successfully got SERP search results for '{query}'")
                return results
            elif attempt < MAX_RETRIES - 1 and response.status not in [429, 500]:
                sleep_time = RETRY_BASE_DELAY ** (attempt + 2)
                logger.warning(
                    f"Got {response.status} response from SERP API. "
                    f"Sleeping for {sleep_time} seconds before retrying..."
                )
                time.sleep(sleep_time)
            else:
                raise Exception(
                    f"Got non 2xx response from SERP API: {response.status}"
                )

    def __format_results(self, results: list) -> str:
        """Format the search results into a string."""
        docs = []
        for result in results:
            authors_str = result.get("author", [])
            published_date = result.get("date", "")

            doc_info = [
                f"* Title: {result.get('title', '')}",
                f"* Published Date: {published_date}",
                f"* Authors: {authors_str}",
                f"* Abstract: {result.get('snippet', '')}",
                f"* Paper URLs: {result.get('link', '')}",
            ]
            docs.append("\n".join(doc_info))

        return "\n-----\n".join(docs)

    def search(self, input: SearchPapersInput) -> str:
        """Search for papers and format results."""
        if cached_results := self.cache_manager.get_search_results(input):
            logger.info(
                f"Found SERP search results for '{input.model_dump_json()}' in cache"
            )
            return cached_results

        query = self.__build_query(input)
        results = self.__get_search_results(query, input.max_papers)
        formatted_results = self.__format_results(results)

        # Cache the results
        self.cache_manager.store_search_results(input, formatted_results)
        return formatted_results
