import json
import time

from exa_py import Exa
from nexusai.cache.cache_manager import CacheManager
from nexusai.config import EXA_API_KEY, MAX_RETRIES, RETRY_BASE_DELAY
from nexusai.models.inputs import SearchPapersInput, SearchType
from nexusai.utils.logger import logger


class ExaAPIWrapper:
    """Wrapper around the Exa API.

    This wrapper uses the Exa Python client to perform a paper search.
    """

    name = "exa"

    def __init__(self):
        self.api_key = EXA_API_KEY
        self.cache_manager = CacheManager(self.name)
        self.client = Exa(api_key=self.api_key)

    def __format_urls(self, urls: list[str]) -> list[str]:
        formatted_urls = []
        for i, url in enumerate(set(urls)):
            if i > 10:
                break
            formatted_urls.append(f"[Link {i+1}]({url})")
        return ", ".join(formatted_urls)

    def __build_kwargs(self, input: SearchPapersInput) -> dict:
        """Build the kwargs for the Exa search call."""
        kwargs = {"extras": {"links": 10}}
        if input.search_type == SearchType.narrow:
            kwargs["category"] = "research paper"
        else:
            kwargs["category"] = "pdf"

        if input.summarization_prompt:
            kwargs["summary"] = {"query": input.summarization_prompt}
        else:
            kwargs["text"] = {"max_characters": 1000}

        return kwargs

    def __get_search_results(self, input: SearchPapersInput) -> dict:
        """Execute the Exa search call with a retry mechanism."""
        kwargs = self.__build_kwargs(input)

        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Searching Exa for '{input.query}' (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            try:
                response = self.client.search_and_contents(
                    query=input.query, num_results=input.max_results, **kwargs
                )
                # Verify the response structure from Exa
                if response.results:
                    logger.info(
                        f"Successfully got Exa search results for '{input.query}'"
                    )
                    return response
                else:
                    raise Exception(f"No results found from Exa for '{input.query}'")
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    sleep_time = RETRY_BASE_DELAY ** (attempt + 1)
                    logger.warning(
                        f"Exa API call failed with error: {e}. Retrying in {sleep_time} seconds..."
                    )
                    time.sleep(sleep_time)
                else:
                    raise Exception(
                        f"Exa API call failed after {MAX_RETRIES} attempts: {e}"
                    )

    def __format_results(self, response: dict) -> str:
        """Format the Exa response into a string."""
        results = response.results
        docs = []
        for res in results:
            title = res.title or "No Title"
            author = res.author or "Unknown Author"
            published_date = res.published_date or "Unknown Date"
            summary, text = res.summary or "", res.text or "No Text"
            url = res.url or "No URL"
            extra_links = res.extras.get("links", [])
            related_urls = self.__format_urls(extra_links) if extra_links else "No Related URLs"
            doc_info = [
                f"* Title: {title}",
                f"* Author: {author}",
                f"* Published Date: {published_date}",
                f"* Summary: {json.dumps(summary)}" if summary else f"* Text: {json.dumps(text)}",
                f"* URL: {url}",
                f"* Related URLs: {related_urls}",
            ]
            docs.append("\n".join(doc_info))
        return "\n-----\n".join(docs)

    def search(self, input: SearchPapersInput) -> str:
        """Search for papers using the Exa API and format results."""
        # Check if we already have cached results:
        if not input.summarization_prompt and (
            cached_results := self.cache_manager.get_search_results(input)
        ):
            logger.info(
                f"Found Exa search results for '{input.model_dump_json()}' in cache"
            )
            return cached_results

        response = self.__get_search_results(input)
        formatted_results = self.__format_results(response)

        # Cache the results
        if not input.summarization_prompt:
            self.cache_manager.store_search_results(input, formatted_results)
        return formatted_results


if __name__ == "__main__":
    input = SearchPapersInput(query="machine learning", max_results=3)
    print(ExaAPIWrapper().search(input))
