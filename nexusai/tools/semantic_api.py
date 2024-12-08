import time
import urllib3
from typing import Dict, List, Optional, Any
from langchain_core.tools import tool

from nexusai.cache.cache_manager import CacheManager
from nexusai.config import (
    SEMANTIC_SCHOLAR_BASE_URL,
    SEMANTIC_SCHOLAR_API_KEY,
    MAX_RETRIES,
    RETRY_BASE_DELAY,
    ENDPOINTS,
    DEFAULT_FIELDS,
    MAX_RESULTS_PER_PAGE
)
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger


class SemanticScholarAPIWrapper:
    """Simple wrapper around the Semantic Scholar API for paper search and details."""

    def __init__(self):
        self.base_url = SEMANTIC_SCHOLAR_BASE_URL
        self.api_key = SEMANTIC_SCHOLAR_API_KEY
        self.cache_manager = CacheManager()
        self.result_limit = MAX_RESULTS_PER_PAGE

    def __get_search_results(self, query: str, limit: int = None) -> dict:
        """Execute search query with retry mechanism."""
        if cached_results := self.cache_manager.get_query_results(query):
            logger.info(f"Found search results for '{query}' in cache")
            return cached_results

        http = urllib3.PoolManager()
        params = {
            'query': query,
            'limit': min(limit or self.result_limit, MAX_RESULTS_PER_PAGE),
            'fields': DEFAULT_FIELDS
        }

        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Searching for '{query}' (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            response = http.request(
                "GET",
                f"{self.base_url}{ENDPOINTS['paper_search']}",
                headers={"x-api-key": self.api_key},
                fields=params
            )

            if 200 <= response.status < 300:
                results = response.json()
                self.cache_manager.store_query_results(query, results)
                return results
            elif attempt < MAX_RETRIES - 1:
                sleep_time = (
                    60 if response.status == 429 else RETRY_BASE_DELAY ** (attempt + 2)
                )
                logger.warning(
                    f"Got {response.status} response from S2 API. "
                    f"Sleeping for {sleep_time} seconds before retrying..."
                )
                time.sleep(sleep_time)
            else:
                raise Exception(f"Got non 2xx response from S2 API: {response.status}")

    def __get_paper_details(self, paper_id: str) -> dict:
        """Get detailed information about a specific paper."""
        if cached_details := self.cache_manager.get_query_results(f"details_{paper_id}"):
            logger.info(f"Found paper details for '{paper_id}' in cache")
            return cached_details

        http = urllib3.PoolManager()
        endpoint = ENDPOINTS['paper_details'].format(paper_id=paper_id)

        for attempt in range(MAX_RETRIES):
            logger.info(f"Getting details for paper {paper_id}")
            response = http.request(
                "GET",
                f"{self.base_url}{endpoint}",
                headers={"x-api-key": self.api_key},
                fields={'fields': DEFAULT_FIELDS}
            )

            if 200 <= response.status < 300:
                details = response.json()
                self.cache_manager.store_query_results(f"details_{paper_id}", details)
                return details
            elif attempt < MAX_RETRIES - 1:
                sleep_time = RETRY_BASE_DELAY ** (attempt + 2)
                logger.warning(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise Exception(f"Failed to get paper details: {response.status}")

    def search_papers(self, query: str) -> tuple[int, List[Dict[str, Any]]]:
        """
        Search for papers and return total count and results.
        
        Returns:
            Tuple of (total_results, paper_list)
        """
        try:
            results = self.__get_search_results(query)
            return results.get("total", 0), results.get("data", [])
        except Exception as e:
            logger.error(f"Error in paper search: {str(e)}")
            return 0, []

    def get_paper_details(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific paper."""
        try:
            return self.__get_paper_details(paper_id)
        except Exception as e:
            logger.error(f"Error getting paper details: {str(e)}")
            return None

    def format_paper_list(self, papers: List[Dict[str, Any]]) -> str:
        """Format paper list for display."""
        formatted = []
        for idx, paper in enumerate(papers):
            authors = paper.get('authors', [])
            author_str = ' and '.join(author['name'] for author in authors[:3])
            if len(authors) > 3:
                author_str += ' et al.'

            formatted.append(
                f"{idx}. {paper['title']}\n"
                f"   Authors: {author_str}\n"
                f"   Year: {paper.get('year', 'N/A')}\n"
                f"   Citations: {paper.get('citations', 0)}\n"
                f"   URL: {paper['url']}\n"
            )
        return "\n".join(formatted)

    @tool("search-papers", args_schema=SearchPapersInput)
    @staticmethod
    def tool_function(query: str, max_papers: int = 10) -> str:
        """Search for scientific papers using the Semantic Scholar API.
        
        Example:
        {"query": "machine learning", "max_papers": 10}
        """
        try:
            api = SemanticScholarAPIWrapper()
            total, papers = api.search_papers(query)
            if not total:
                return "No matches found."
            
            return (
                f"Found {total} results. Showing up to {max_papers}.\n\n"
                f"{api.format_paper_list(papers[:max_papers])}"
            )
        except Exception as e:
            return f"Error performing paper search: {e}"