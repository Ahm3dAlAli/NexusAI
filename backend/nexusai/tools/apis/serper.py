import http.client
import json
import time

from nexusai.cache.cache_manager import CacheManager
from nexusai.config import (
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_BASE_DELAY,
    SERPER_API_KEY,
)
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger


class SerperAPIWrapper:
    """Wrapper around the Serper API.

    This wrapper uses the Serper API to perform a paper search.
    """

    name = "serper"

    def __init__(self):
        self.api_key = SERPER_API_KEY
        self.cache_manager = CacheManager(self.name)
        self.host = "google.serper.dev"
        self.path = "/search"

    def __build_query(self, input: SearchPapersInput) -> str:
        query = input.query
        start_year, end_year = input.date_range[0], input.date_range[1]
        if start_year:
            query += f" after:{start_year}"
        if end_year:
            query += f" before:{end_year}"

        query += f" filetype:pdf"
        return query

    def __get_search_results(self, input: SearchPapersInput) -> dict:
        """Execute the Serper search call with a retry mechanism."""
        query = self.__build_query(input)
        payload = {
            "q": query,
            "num": input.max_results,
        }
        payload_str = json.dumps(payload)
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Searching Serper for '{query}' (attempt {attempt + 1}/{MAX_RETRIES})"
            )
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
                    else:
                        raise Exception("No results found from Serper")
                elif attempt < MAX_RETRIES - 1 and response.status not in [
                    400,
                    403,
                    404,
                    500,
                ]:
                    delay = RETRY_BASE_DELAY ** (attempt + 1)
                    logger.warning(
                        f"Serper API call failed with status {response.status}. Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                else:
                    raise Exception(
                        f"Serper API call failed with status code {response.status}."
                    )
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY ** (attempt + 1)
                    logger.warning(
                        f"Error during Serper API call: {e}. Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                else:
                    raise Exception(
                        f"Serper API call failed after {MAX_RETRIES} attempts: {e}"
                    )

    def __format_results(self, response: dict) -> str:
        """Format the Serper response into a string."""
        results = response.get("organic", [])
        docs = []
        for res in results:
            title = res.get("title", "No Title")
            link = res.get("link", "No URL")
            snippet = res.get("snippet", "No Snippet")
            date = res.get("date", "Unknown Date")
            doc_info = [
                f"* Title: {title}",
                f"* Link: {link}",
                f"* Snippet: {snippet}",
                f"* Date: {date}",
            ]
            docs.append("\n".join(doc_info))
        return "\n-----\n".join(docs)

    def search(self, input: SearchPapersInput) -> str:
        """Search for papers using the Serper API and format results."""
        # Use cache if available
        if cached_results := self.cache_manager.get_search_results(input):
            logger.info(
                f"Found Serper search results for '{input.model_dump_json()}' in cache"
            )
            return cached_results

        response = self.__get_search_results(input)
        formatted_results = self.__format_results(response)

        self.cache_manager.store_search_results(input, formatted_results)
        return formatted_results
