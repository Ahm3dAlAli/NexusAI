import os

from dotenv import load_dotenv

from nexusai.utils.logger import logger

# Load environment variables from .env file
load_dotenv()

# LLMs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Please set it in your .env file."
    )

# CORE API Configuration
CORE_API_BASE_URL = "https://api.core.ac.uk/v3"
CORE_API_KEY = os.getenv("CORE_API_KEY")
if not CORE_API_KEY:
    raise ValueError(
        "CORE_API_KEY environment variable is not set. "
        "Please set it in your .env file."
    )

# SEMANTIC API Configuration 
ENDPOINTS = {
    "paper_search": "/paper/search",
    "paper_details": "/paper/{paper_id}"
}
SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
if not SEMANTIC_SCHOLAR_API_KEY:
    raise ValueError(
        "SEMANTIC_SCHOLAR_API_KEY environment variable is not set. "
        "Please set it in your .env file."
    )


# Redis
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    logger.warning("REDIS_URL environment variable is not set. Not using cache.")

# Request Configuration
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2  # seconds

# State Management Configuration
MAX_FEEDBACK_REQUESTS = 2

# PDF Downloader Configuration
MAX_PAGES = 50


