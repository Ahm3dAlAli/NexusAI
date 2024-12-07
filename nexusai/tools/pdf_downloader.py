import urllib3
import time
import io
import pdfplumber

from nexusai.cache.cache_manager import CacheManager
from nexusai.config import MAX_RETRIES, RETRY_BASE_DELAY
from nexusai.utils.logger import logger

# Disable warnings for insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PDFDownloader:
    def __init__(self):
        self.cache_manager = CacheManager()
        
    def __convert_bytes_to_text(self, bytes_content: bytes) -> str:
        """Convert bytes to text."""
        logger.info(f"Converting bytes to text...")
        pdf_file = io.BytesIO(bytes_content)
        with pdfplumber.open(pdf_file) as pdf:
            pages = []
            for page in pdf.pages:
                pages.append(page.extract_text())
        logger.info(f"Done")
        return "\n".join(pages)
    
    def download_pdf(self, url: str) -> str:
        """Get PDF from URL or cache if available."""
        if cached_content := self.cache_manager.get_pdf(url):
            logger.info(f"Found PDF in cache for {url}")
            return cached_content

        http = urllib3.PoolManager(
            cert_reqs='CERT_NONE',
        )
        # Mock browser headers to avoid 403 error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        for attempt in range(MAX_RETRIES):
            logger.info(f"Downloading PDF from {url} (attempt {attempt + 1}/{MAX_RETRIES})")
            response = http.request('GET', url, headers=headers)
            if 200 <= response.status < 300:
                logger.info(f"Successfully downloaded PDF from {url}")
                break
            elif attempt < MAX_RETRIES - 1:
                logger.warning(f"Got {response.status} response when downloading paper. Sleeping for {RETRY_BASE_DELAY ** (attempt + 2)} seconds before retrying...")
                time.sleep(RETRY_BASE_DELAY ** (attempt + 2))
            else:
                raise Exception(f"Got non 2xx when downloading paper: {response.status}")

        # Store in cache
        bytes_content = response.data
        content = self.__convert_bytes_to_text(bytes_content)
        logger.info(f"Storing PDF in cache for {url}")
        self.cache_manager.store_pdf(url, content)
        return content
