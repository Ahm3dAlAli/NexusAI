import http.client
import json

from nexusai.cache.cache_manager import CacheManager
from nexusai.config import (
    REQUEST_TIMEOUT,
    SERPER_API_KEY,
)
from nexusai.models.inputs import SearchPapersInput, SearchType
from nexusai.utils.logger import logger
from nexusai.utils.strings import arxiv_abs_to_pdf_url


class SerperAPIWrapper:
    """Wrapper around the Serper API.

    This wrapper uses the Serper API to perform a paper search.
    """

    name = "serper"

    def __init__(self):
        self.api_key = SERPER_API_KEY
        self.cache_manager = CacheManager(self.name)
        self.host = "google.serper.dev"
        self.path = "/scholar"

    def __build_query_and_payload(self, input: SearchPapersInput) -> tuple[str, dict]:
        query = input.query
        if input.search_type == SearchType.title:
            query = f'"{query}"'

        payload = {
            "q": query,
            "num": input.max_results,
        }
        if input.date_range:
            start_year, end_year = input.date_range[0], input.date_range[1]
            if start_year:
                payload["as_ylo"] = start_year
            if end_year:
                payload["as_yhi"] = end_year
        return query, payload

    def __get_search_results(self, input: SearchPapersInput) -> dict:
        """Execute the Serper search call with a retry mechanism."""
        query, payload = self.__build_query_and_payload(input)
        payload_str = json.dumps(payload)
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

        logger.info(f"[Serper API] Searching for '{query}'")
        try:
            conn = http.client.HTTPSConnection(self.host, timeout=REQUEST_TIMEOUT)
            conn.request("POST", self.path, payload_str, headers)
            response = conn.getresponse()

            if 200 <= response.status < 300:
                data = response.read()
                response_str = data.decode("utf-8")
                response_json = json.loads(response_str)
                if response_json.get("organic"):
                    return response_json
            raise Exception("No results found from Serper")
        except Exception as e:
            raise Exception(f"Serper API call failed. Details: {e}")

    def __format_results(self, response: dict) -> str:
        """Format the Serper response into a string."""
        results = response.get("organic", [])
        docs = []
        for res in results:
            title = res.get("title", "No title")
            if res.get("pdfUrl") or res.get("link"):
                link = arxiv_abs_to_pdf_url(res.get("pdfUrl") or res["link"])
            else:
                link = "No URL"
            publication_info = res.get("publicationInfo", "No publication info")
            snippet = res.get("snippet", "No snippet")
            doc_info = [
                f"* Title: {title}",
                f"* Link: {link}",
                f"* Publication Info: {publication_info}",
                f"* Snippet: {snippet}",
                f"* Year: {res.get('year', 'Unknown year')}",
                f"* Cited By: {res.get('citedBy', 'Unknown citations')}",
            ]
            docs.append("\n".join(doc_info))
        return "\n-----\n".join(docs)

    def search(self, input: SearchPapersInput) -> str:
        """Search for papers using the Serper API and format results."""
        # Use cache if available
        if cached_results := self.cache_manager.get_search_results(input):
            logger.info(f"[Serper API] Cached search results found for input: {input}")
            return cached_results

        response = self.__get_search_results(input)
        formatted_results = self.__format_results(response)
        self.cache_manager.store_search_results(input, formatted_results)
        return formatted_results
