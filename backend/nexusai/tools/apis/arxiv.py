import time
from datetime import datetime

import feedparser
import urllib3
from nexusai.cache.cache_manager import CacheManager
from nexusai.config import ARXIV_API_BASE_URL, MAX_RETRIES, RETRY_BASE_DELAY
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger


class ArxivAPIWrapper:
    """Wrapper around the arXiv API."""

    name = "arxiv"

    def __init__(self):
        self.base_url = ARXIV_API_BASE_URL

        # Redis cache
        self.cache_manager = CacheManager()

    def __build_query(self, input: SearchPapersInput) -> str:
        """Build the query for the arXiv API."""
        query_parts = []

        if input.keywords:
            keywords_query = f"; {input.operator.value.upper()} ".join(
                [f'all:"{keyword}"' for keyword in input.keywords]
            )
            query_parts.append(keywords_query)

        if input.title:
            query_parts.append(f'ti:"{input.title}"')

        if input.year_range:
            query_parts.append(
                f"submittedDate:[{input.year_range[0] or 0000}0101 TO {input.year_range[1] or 9999}1231]"
            )

        query = "; ".join(query_parts)
        logger.info(f"Built Arxiv query: {query}")
        return query

    def __get_search_results(self, query: str, max_papers: int = 1) -> list:
        """Execute search query with retry mechanism."""
        http = urllib3.PoolManager()
        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Searching Arxiv for '{query}' (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            response = http.request(
                "GET",
                f"{self.base_url}/query",
                fields={
                    "search_query": query,
                    "max_results": max_papers,
                    "sortBy": "relevance",
                    "sortOrder": "descending",
                },
            )
            if 200 <= response.status < 300:
                feed = feedparser.parse(response.data)
                results = feed.entries
                print(results)
                if not results:
                    raise Exception(f"No results found from Arxiv for '{query}'")
                logger.info(f"Successfully got Arxiv search results for '{query}'")
                return results
            elif attempt < MAX_RETRIES - 1 and response.status not in [429, 500]:
                sleep_time = RETRY_BASE_DELAY ** (attempt + 2)
                logger.warning(
                    f"Got {response.status} response from arXiv API. "
                    f"Sleeping for {sleep_time} seconds before retrying..."
                )
                time.sleep(sleep_time)
            else:
                raise Exception(
                    f"Got non 2xx response from arXiv API: {response.status}"
                )

    def __format_results(self, results: list) -> str:
        """Format the search results into a string."""
        docs = []
        for result in results:
            # Parse and format the publication date
            published_date = datetime.strptime(
                result.published, "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%Y-%m-%d")

            # Extract authors
            authors = [author.name for author in result.authors]
            authors_str = " and ".join(authors)

            doc_info = [
                f"* Title: {result.title}",
                f"* Published Date: {published_date}",
                f"* Authors: {authors_str}",
                f"* Abstract: {result.summary}",
                f"* Paper URLs: {result.link}",
            ]
            docs.append("\n".join(doc_info))

        return "\n-----\n".join(docs)

    def search(self, input: SearchPapersInput) -> str:
        """Search for papers and format results."""
        if cached_results := self.cache_manager.get_search_results(input):
            logger.info(
                f"Found Arxiv search results for '{input.model_dump_json()}' in cache"
            )
            return cached_results

        query = self.__build_query(input)
        results = self.__get_search_results(query, input.max_papers)
        formatted_results = self.__format_results(results)

        # Cache the results
        self.cache_manager.store_search_results(input, formatted_results)
        return formatted_results
