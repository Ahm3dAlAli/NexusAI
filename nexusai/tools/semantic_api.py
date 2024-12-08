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
    DEFAULT_FIELDS,
    MAX_RESULTS_PER_PAGE
)
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger


class SemanticScholarAPIWrapper:
    """Simple wrapper around the Semantic Scholar API for bulk paper search."""

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
                self.base_url,
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

    def search_papers(self, query: str, limit: int = 100) -> tuple[int, List[Dict[str, Any]], Optional[str]]:
        """
        Search for papers using the bulk search endpoint.
        
        Args:
            query: Search query (the agent will construct appropriate query syntax)
            limit: Maximum number of results to return
            
        Returns:
            Tuple of (total_results, paper_list, next_token)
        """
        try:
            results = self.__get_search_results(query=query, limit=limit)
            return (
                results.get("total", 0),
                results.get("data", []),
                results.get("token")
            )
        except Exception as e:
            logger.error(f"Error in paper search: {str(e)}")
            return 0, [], None

    @tool("search-papers", args_schema=SearchPapersInput)
    @staticmethod
    def tool_function(query: str, max_papers: int = 10) -> str:
        """Search for scientific papers using the Semantic Scholar API.
        
        Example:
        {"query": "machine learning", "max_papers": 10}
        """
        try:
            api = SemanticScholarAPIWrapper()
            total, papers, next_token = api.search_papers(query, limit=max_papers)
            if not total:
                return "No matches found."
            
            # Format results
            formatted_papers = []
            for paper in papers:
                formatted_papers.append(
                    f"Title: {paper.get('title')}\n"
                    f"URL: {paper.get('url')}\n"
                )
            
            response = [
                f"Found {total} results. Showing {len(papers)} papers.",
                "\n\n".join(formatted_papers)
            ]
            
            if next_token:
                response.append(f"\nMore results available. Token: {next_token}")
                
            return "\n\n".join(response)
        except Exception as e:
            return f"Error performing paper search: {e}"