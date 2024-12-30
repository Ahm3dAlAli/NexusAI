import time

import urllib3
from dotenv import load_dotenv
from nexusai.cache.cache_manager import CacheManager
from nexusai.config import (BING_API_BASE_URL, BING_API_KEY, MAX_RETRIES,
                            RETRY_BASE_DELAY)
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger

load_dotenv()


class BingAPIWrapper:
    """Wrapper around the Bing API for academic search.

    It enriches the Bing query by filtering for databases for academic papers and PDF results to increase the relevance of the results.
    """

    name = "bing"

    def __init__(self):
        self.base_url = BING_API_BASE_URL
        self.api_key = BING_API_KEY
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
        self.cache_manager = CacheManager(self.name)

    def __build_query(self, input: SearchPapersInput) -> str:
        """Build the query for the Bing API."""
        query = ""
        if input.keywords:
            query += f" {input.operator.value.upper()} ".join(
                [f"'{keyword}'" for keyword in input.keywords]
            )
        if input.title:
            query += f" intitle:'{input.title}'"
        if input.year_range:
            if input.year_range[0]:
                query += f" after:{input.year_range[0]}-01-01"
            if input.year_range[1]:
                query += f" before:{input.year_range[1]}-12-31"
        query = f"site:({' OR '.join(self.sites)}) {query} filetype:pdf"
        logger.info(f"Built Bing query: {query}")
        return query

    def __get_search_results(self, query: str, max_papers: int = 1) -> list:
        """Execute search query with retry mechanism."""
        http = urllib3.PoolManager()
        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Searching Bing for '{query}' (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            response = http.request(
                "GET",
                f"{self.base_url}/v7.0/search",
                headers={
                    "Ocp-Apim-Subscription-Key": self.api_key,
                },
                fields={
                    "q": query,
                    "count": max_papers,
                },
            )
            if 200 <= response.status < 300:
                results = response.json().get("webPages", {}).get("value", [])
                if not results:
                    raise Exception(f"No results found from Bing for '{query}'")
                logger.info(f"Successfully got Bing search results for '{query}'")
                return results
            elif attempt < MAX_RETRIES - 1 and response.status not in [429, 500]:
                sleep_time = RETRY_BASE_DELAY ** (attempt + 2)
                logger.warning(
                    f"Got {response.status} response from Bing API. "
                    f"Sleeping for {sleep_time} seconds before retrying..."
                )
                time.sleep(sleep_time)
            else:
                raise Exception(
                    f"Got non 2xx response from Bing API: {response.status}"
                )

    def __format_results(self, results: list) -> str:
        """Format the search results into a string."""
        docs = []
        for result in results:
            doc_info = [
                f"* Title: {result.get('name', '')}",
                f"* Abstract: {result.get('snippet', '')}",
                f"* Paper URLs: {result.get('url', '')}",
            ]
            docs.append("\n".join(doc_info))

        return "\n-----\n".join(docs)

    def search(self, input: SearchPapersInput) -> str:
        """Search for papers and format results."""
        if cached_results := self.cache_manager.get_search_results(input):
            logger.info(
                f"Found Bing search results for '{input.model_dump_json()}' in cache"
            )
            return cached_results

        query = self.__build_query(input)
        results = self.__get_search_results(query, input.max_papers)
        formatted_results = self.__format_results(results)

        # Cache the results
        self.cache_manager.store_search_results(input, formatted_results)
        return formatted_results


if __name__ == "__main__":
    bing = BingAPIWrapper()
    print(
        bing.search(
            SearchPapersInput(
                title="Attention is all you need", max_papers=5, year_range=[2015, 2020]
            )
        )
    )
