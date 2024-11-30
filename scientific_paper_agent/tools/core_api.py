# scientific_paper_agent/tools/core_api.py
import time
from typing import ClassVar
import urllib3
from pydantic import BaseModel, Field

from ..config import CORE_API_KEY, CORE_API_BASE_URL, MAX_RETRIES, RETRY_BASE_DELAY

class CoreAPIWrapper(BaseModel):
    """Simple wrapper around the CORE API."""
    base_url: ClassVar[str] = CORE_API_BASE_URL
    api_key: ClassVar[str] = CORE_API_KEY
    
    top_k_results: int = Field(
        description="Top k results obtained by running a query on Core",
        default=1
    )
    
    def _get_search_response(self, query: str) -> dict:
        """Execute search query with retry mechanism."""
        http = urllib3.PoolManager()
        
        for attempt in range(MAX_RETRIES):
            try:
                response = http.request(
                    'GET',
                    f"{self.base_url}/search/outputs", 
                    headers={"Authorization": f"Bearer {self.api_key}"}, 
                    fields={"q": query, "limit": self.top_k_results}
                )
                
                if 200 <= response.status < 300:
                    return response.json()
                    
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY ** (attempt + 2))
                else:
                    raise Exception(
                        f"Got non 2xx response from CORE API: "
                        f"{response.status} {response.data}"
                    )
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise Exception(f"Error accessing CORE API: {str(e)}")
                time.sleep(RETRY_BASE_DELAY ** (attempt + 2))

    def search(self, query: str) -> str:
        """Search for papers and format results."""
        response = self._get_search_response(query)
        results = response.get("results", [])
        
        if not results:
            return "No relevant results were found"
            
        docs = []
        for result in results:
            published_date = (
                result.get('publishedDate') or 
                result.get('yearPublished', '')
            )
            authors = result.get('authors', [])
            authors_str = ' and '.join(
                [item['name'] for item in authors]
            )
            urls = (
                result.get('sourceFulltextUrls') or 
                result.get('downloadUrl', '')
            )
            
            doc_info = [
                f"* ID: {result.get('id', '')}",
                f"* Title: {result.get('title', '')}",
                f"* Published Date: {published_date}",
                f"* Authors: {authors_str}",
                f"* Abstract: {result.get('abstract', '')}",
                f"* Paper URLs: {urls}"
            ]
            docs.append('\n'.join(doc_info))
            
        return "\n-----\n".join(docs)
