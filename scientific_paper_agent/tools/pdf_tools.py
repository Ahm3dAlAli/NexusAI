
# scientific_paper_agent/tools/pdf_tools.py
import io
import time
import urllib3
import pdfplumber
from typing import Optional

from ..config import MAX_RETRIES, RETRY_BASE_DELAY

def download_paper(url: str) -> str:
    """
    Download and extract text from a scientific paper PDF.
    
    Args:
        url (str): URL of the PDF document
        
    Returns:
        str: Extracted text content or error message
    """
    try:
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Mock browser headers to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # Implement retry mechanism
        for attempt in range(MAX_RETRIES):
            try:
                response = http.request('GET', url, headers=headers)
                
                if 200 <= response.status < 300:
                    return _extract_text_from_pdf(response.data)
                    
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY ** (attempt + 2))
                else:
                    raise Exception(
                        f"Failed to download PDF: HTTP {response.status}"
                    )
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise Exception(f"Error downloading PDF: {str(e)}")
                time.sleep(RETRY_BASE_DELAY ** (attempt + 2))
                
    except Exception as e:
        return f"Error downloading paper: {str(e)}"

def _extract_text_from_pdf(pdf_data: bytes) -> str:
    """
    Extract text content from PDF data.
    
    Args:
        pdf_data (bytes): Raw PDF data
        
    Returns:
        str: Extracted text content
    """
    pdf_file = io.BytesIO(pdf_data)
    text = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or '')
            
    return '\n'.join(text)