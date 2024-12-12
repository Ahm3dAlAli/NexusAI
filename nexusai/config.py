import os

from dotenv import load_dotenv

from nexusai.utils.logger import logger

# Load environment variables from .env file
load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Please set it in your .env file."
    )

# Arxiv API
ARXIV_API_BASE_URL = "http://export.arxiv.org/api"
PROVIDERS = ["arxiv"]

# CORE API
CORE_API_BASE_URL = "https://api.core.ac.uk/v3"
CORE_API_KEY = os.getenv("CORE_API_KEY")
if CORE_API_KEY:
    PROVIDERS.append("core")
else:
    logger.warning("CORE_API_KEY environment variable is not set. Not using CORE API.")

# Google SERP API
SERP_API_BASE_URL = "https://serpapi.com"
SERP_API_KEY = os.getenv("SERP_API_KEY")
if SERP_API_KEY:
    PROVIDERS.append("serp")
else:
    logger.warning("SERP_API_KEY environment variable is not set. Not using SERP API.")

logger.info(f"Using providers: {PROVIDERS}")

# Redis
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    logger.warning("REDIS_URL environment variable is not set. Not using cache.")

# Request Configuration
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2  # seconds

# State Management Configuration
MAX_FEEDBACK_REQUESTS = 1

# PDF Downloader Configuration
MAX_PAGES = 50
