import json
import time

from exa_py import Exa
from exa_py.api import Result, SearchResponse
from nexusai.cache.cache_manager import CacheManager
from nexusai.config import EXA_API_KEY, MAX_RETRIES, RETRY_BASE_DELAY
from nexusai.models.inputs import SearchPapersInput, SearchType
from nexusai.utils.logger import logger
from nexusai.utils.arxiv import arxiv_abs_to_pdf_url


class ExaAPIWrapper:
    """Wrapper around the Exa API.

    This wrapper uses the Exa Python client to perform a paper search and download URL content.
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
            formatted_urls.append(f"[Link {i+1}]({arxiv_abs_to_pdf_url(url)})")
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

    def __build_query(self, input: SearchPapersInput) -> str:
        base_query = input.query
        start_year, end_year = input.date_range[0], input.date_range[1]
        if start_year and end_year:
            base_query += f" {start_year}-{end_year}"
        elif start_year:
            base_query += f" {start_year}"
        elif end_year:
            base_query += f" {end_year}"
        return base_query.strip()

    def __get_search_results(self, input: SearchPapersInput) -> dict:
        """Execute the Exa search call with a retry mechanism."""
        kwargs = self.__build_kwargs(input)
        built_query = self.__build_query(input)

        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Searching Exa for '{built_query}' (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            try:
                response: SearchResponse = self.client.search_and_contents(
                    query=built_query, num_results=input.max_results, **kwargs
                )
                # Verify the response structure from Exa
                if response.results:
                    logger.info(
                        f"Successfully got Exa search results for '{built_query}'"
                    )
                    return response
                else:
                    raise Exception(f"No results found from Exa for '{built_query}'")
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

    def __format_results(self, response: SearchResponse) -> str:
        """Format the Exa response into a string."""
        results: list[Result] = response.results
        docs = []
        for res in results:
            title = res.title or "No Title"
            author = res.author or "Unknown Author"
            published_date = res.published_date or "Unknown Date"
            summary, text = res.summary or "", res.text or "No Text"
            url = arxiv_abs_to_pdf_url(res.url) if res.url else "No URL"
            extra_links = res.extras.get("links", [])
            related_urls = (
                self.__format_urls(extra_links) if extra_links else "No Related URLs"
            )
            doc_info = [
                f"* Title: {title}",
                f"* Author: {author}",
                f"* Published Date: {published_date}",
                (
                    f"* Summary: {json.dumps(summary)}"
                    if summary
                    else f"* Text: {json.dumps(text)}"
                ),
                f"* URL: {url}",
                f"* Related URLs: {related_urls}",
            ]
            docs.append("\n".join(doc_info))
        return "\n-----\n".join(docs)

    def search(self, input: SearchPapersInput) -> str:
        """Search for papers using the Exa API and format results."""
        logger.info(f"Searching Exa for '{input.model_dump_json()}'...")

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

    def download_url(self, url: str) -> str:
        """Download content from a URL using the Exa API and return it as a string."""
        logger.info(f"Downloading content from URL '{url}'...")

        if cached_text := self.cache_manager.get_url_content(url):
            logger.info(f"Found cached content for URL '{url}'")
            return cached_text

        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Downloading content from URL '{url}' (attempt {attempt + 1}/{MAX_RETRIES})"
            )
            try:
                response: SearchResponse = self.client.get_contents([url], text=True)
                if response.results:
                    downloaded_text = response.results[0].text
                    logger.info(f"Successfully downloaded content from URL '{url}'")
                    self.cache_manager.store_url_content(url, downloaded_text)
                    return downloaded_text
                else:
                    raise Exception("No text content found in the response")
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    sleep_time = RETRY_BASE_DELAY ** (attempt + 1)
                    logger.warning(
                        f"Failed to download content from URL '{url}' with error: {e}. Retrying in {sleep_time} seconds..."
                    )
                    time.sleep(sleep_time)
                else:
                    raise Exception(
                        f"Exa API download failed for URL '{url}' after {MAX_RETRIES} attempts: {e}"
                    )
