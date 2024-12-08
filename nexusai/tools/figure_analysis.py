import io
import base64
import asyncio
import time
from typing import List, Dict, Any
from PIL import Image
import fitz  # PyMuPDF
from anthropic import Anthropic
from langchain_core.tools import tool
from pydantic import BaseModel

from nexusai.cache.cache_manager import CacheManager
from nexusai.config import (
    ANTHROPIC_API_KEY,
    MAX_RETRIES,
    RETRY_BASE_DELAY,
    FIGURE_MIN_SIZE,
    CLAUDE_MODEL
)
from nexusai.utils.logger import logger

class FigureAnalyzer:
    """Tool for analyzing figures from PDFs using Claude."""
    query: str = ""

    def __init__(self, query: str):
        self.query = query
        FigureAnalyzer.query = query
        self.cache_manager = CacheManager()
        self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def __extract_figures_from_pdf(self, url: str, pdf_content: bytes) -> List[Dict[str, Any]]:
        """Extract figures from PDF content."""
        logger.info(f"Extracting figures from PDF for {url}...")
        figures = []
        
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_list = page.get_images(full=True)
                
                # Extract text blocks for context
                blocks = page.get_text("blocks")
                text_blocks = [b[4] for b in blocks]
                
                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Load image to check dimensions
                        image = Image.open(io.BytesIO(image_bytes))
                        width, height = image.size
                        
                        if width < FIGURE_MIN_SIZE or height < FIGURE_MIN_SIZE:
                            continue
                            
                        # Convert to base64 for Claude
                        image_b64 = base64.b64encode(image_bytes).decode()
                        
                        # Find nearby text for context
                        figure_rect = page.get_image_bbox(img)
                        nearby_text = ""
                        for block in text_blocks:
                            if "figure" in block.lower() and any(
                                word in block.lower() 
                                for word in ["shows", "displays", "illustrates", "depicts"]
                            ):
                                nearby_text += block + "\n"
                        
                        figures.append({
                            "image": image_b64,
                            "metadata": {
                                "page_number": page_num + 1,
                                "figure_index": img_idx + 1,
                                "width": width,
                                "height": height,
                                "content_type": base_image["ext"],
                                "nearby_text": nearby_text
                            }
                        })
                        
                    except Exception as e:
                        logger.error(f"Error processing image {img_idx} on page {page_num}: {str(e)}")
                        continue
            
            pdf_document.close()
            logger.info(f"Successfully extracted {len(figures)} figures from {url}")
            return figures
            
        except Exception as e:
            logger.error(f"Error extracting figures from PDF: {str(e)}")
            raise

    async def __analyze_figure_with_claude(self, figure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a figure using Claude."""
        try:
            system_message = """You are an expert at analyzing scientific figures and graphs.
            Analyze the provided figure and extract key information about its type, content, methodology, and findings.
            Focus on technical accuracy and detail."""
            
            messages = [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": f"image/{figure['metadata']['content_type']}",
                                "data": figure['image']
                            }
                        },
                        {
                            "type": "text",
                            "text": "Please analyze this figure and provide:\n"
                                   "1. Figure type (e.g., graph, chart, diagram)\n"
                                   "2. Main components and elements\n"
                                   "3. Key findings or insights\n"
                                   "4. Methodology used (if applicable)\n"
                                   "5. Data representation quality"
                        }
                    ]
                }
            ]

            response = await self.anthropic_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1000,
                messages=messages
            )
            
            return {
                "analysis": response.content[0].text,
                "metadata": figure["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing figure with Claude: {str(e)}")
            raise

    async def analyze_figures(self, url: str, pdf_content: bytes) -> str:
        """Extract and analyze figures from PDF."""
        try:
            # Check cache first
            cache_key = f"figures_{url}"
            if cached_figures := self.cache_manager.get_query_results(cache_key):
                logger.info(f"Found figures in cache for {url}")
                figures = cached_figures
            else:
                # Extract figures
                figures = self.__extract_figures_from_pdf(url, pdf_content)
                # Cache the results
                self.cache_manager.store_query_results(cache_key, figures)
            
            if not figures:
                return "No figures found in the document."
            
            # Analyze each figure with Claude
            analyses = []
            for figure in figures:
                analysis = await self.__analyze_figure_with_claude(figure)
                metadata = analysis["metadata"]
                
                result = (
                    f"\nFigure (Page {metadata['page_number']}):\n"
                    f"Dimensions: {metadata['width']}x{metadata['height']}\n"
                    f"Context: {metadata['nearby_text']}\n"
                    f"Analysis:\n{analysis['analysis']}\n"
                )
                
                analyses.append(result)
            
            return "\n---\n".join(analyses)
            
        except Exception as e:
            logger.error(f"Error analyzing figures: {str(e)}")
            return f"Error analyzing figures: {str(e)}"

    @tool("analyze-figures")
    @staticmethod
    def tool_function(url: str, pdf_content: bytes) -> str:
        """Analyze figures from a PDF document using Claude vision capabilities.

        Example:
        {"url": "https://example.com/paper.pdf", "pdf_content": <bytes>}

        Returns:
            A detailed analysis of the figures found in the document.
        """
        try:
            analyzer = FigureAnalyzer(FigureAnalyzer.query)
            return asyncio.run(analyzer.analyze_figures(url, pdf_content))
        except Exception as e:
            return f"Error analyzing figures: {e}"