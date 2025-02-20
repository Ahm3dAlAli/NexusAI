import json

from exa_py import Exa
from exa_py.api import Result, SearchResponse
from nexusai.cache.cache_manager import CacheManager
from nexusai.config import EXA_API_KEY, MAX_PAGES
from nexusai.models.inputs import SearchPapersInput, SearchType
from nexusai.utils.logger import logger
from nexusai.utils.strings import arxiv_abs_to_pdf_url
from langchain.text_splitter import RecursiveCharacterTextSplitter


class ExaAPIWrapper:
    """Wrapper around the Exa API.

    This wrapper uses the Exa Python client to perform a paper search and download URL content.
    """

    name = "exa"
    chars_per_page: int = 5000  # Average page length

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

    def __build_query_and_kwargs(self, input: SearchPapersInput) -> tuple[str, dict]:
        """
        Build the query string and kwargs for the Exa search call.
        Date filtering is added to the kwargs as start_published_date and end_published_date.
        """
        # Use the input query as entered.
        query = input.query.strip()

        # Build the base kwargs.
        kwargs = {"extras": {"links": 10}}
        if input.search_type == SearchType.narrow:
            kwargs["category"] = "research paper"
        else:
            kwargs["category"] = "pdf"

        if input.summarization_prompt:
            kwargs["summary"] = {"query": input.summarization_prompt}
        else:
            kwargs["text"] = {"max_characters": 1000}

        # Add proper date filtering parameters to the kwargs.
        if input.date_range:
            start_date, end_date = input.date_range[0], input.date_range[1]
            if start_date:
                kwargs["start_published_date"] = f"{start_date}-01-01T00:00:00.000Z"
            if end_date:
                kwargs["end_published_date"] = f"{end_date}-12-31T23:59:59.999Z"

        return query, kwargs

    def __get_search_results(self, input: SearchPapersInput) -> SearchResponse:
        """Execute the Exa search call with a retry mechanism."""
        query, kwargs = self.__build_query_and_kwargs(input)

        logger.info(f"[Exa API] Searching for '{query}'")
        try:
            response: SearchResponse = self.client.search_and_contents(
                query=query, num_results=input.max_results, **kwargs
            )
            if response.results:
                logger.info(
                    f"[Exa API] Successfully obtained search results for '{query}'"
                )
                return response
            else:
                raise Exception(f"No results found from Exa for '{query}'")
        except Exception as e:
            raise Exception(f"Exa API call failed. Details: {e}")

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
        logger.info(f"[Exa API] Searching with input: {input}")

        # Return cached results if available.
        if not input.summarization_prompt and (
            cached_results := self.cache_manager.get_search_results(input)
        ):
            logger.info(f"[Exa API] Cached search results found for input: {input}")
            return cached_results

        response = self.__get_search_results(input)
        formatted_results = self.__format_results(response)

        if not input.summarization_prompt:
            self.cache_manager.store_search_results(input, formatted_results)
        return formatted_results

    def download_url(self, url: str) -> str:
        """Download and split content from a URL using the Exa API."""
        url = arxiv_abs_to_pdf_url(url)
        logger.info(f"[Exa API] Downloading content from URL: '{url}'")

        if cached_pages := self.cache_manager.get_content(url):
            logger.info(f"[Exa API] Cached content found for URL: '{url}'")
            return "\n\n".join(cached_pages)

        logger.info(f"[Exa API] Downloading content from URL: '{url}'")
        try:
            response: SearchResponse = self.client.get_contents([url], text=True)
            if response.results:
                text = response.results[0].text
                logger.info(
                    f"[Exa API] Successfully downloaded content from URL: '{url}'"
                )
                if len(text) > self.chars_per_page * MAX_PAGES:
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=self.chars_per_page, chunk_overlap=0
                    )
                    pages = text_splitter.split_text(text)
                else:
                    pages = [text]
                self.cache_manager.store_content(url, pages)
                return "\n\n".join(pages)
            else:
                raise Exception("No text content found in the response")
        except Exception as e:
            raise Exception(f"Exa API download failed for URL '{url}'. Details: {e}")
