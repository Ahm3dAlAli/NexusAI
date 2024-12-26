"""Build agent configuration."""

import os

from dotenv import load_dotenv
from nexusai.utils.logger import logger

# Load environment variables from .env file
load_dotenv()

# Frontend URL
if FRONTEND_URL := os.getenv("FRONTEND_URL"):
    logger.info(f"Frontend URL set to: {FRONTEND_URL}")
else:
    raise ValueError(
        "FRONTEND_URL environment variable is not set. "
        "Please set it in your .env file."
    )

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
if CORE_API_KEY := os.getenv("CORE_API_KEY"):
    PROVIDERS.append("core")
    logger.info("Found CORE API key. CORE was added to the list of providers.")
else:
    logger.warning("CORE_API_KEY environment variable is not set. Not using CORE API.")

# Google SERP API
SERP_API_BASE_URL = "https://serpapi.com"
if SERP_API_KEY := os.getenv("SERP_API_KEY"):
    PROVIDERS.append("serp")
    logger.info("Found SERP API key. SERP was added to the list of providers.")
else:
    logger.warning("SERP_API_KEY environment variable is not set. Not using SERP API.")

logger.info(f"Using providers: {PROVIDERS}")

# Redis
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    logger.warning("REDIS_URL environment variable is not set. Not using cache.")

# Traceability with langsmith
LANGCHAIN_PROJECT = "nexusai"
if LANGCHAIN_API_KEY := os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    logger.info("Langsmith tracing enabled.")
else:
    logger.warning(
        "LANGCHAIN_API_KEY environment variable is not set. Agent runs will not be traced."
    )

# Request Configuration
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2  # seconds

# State Management Configuration
MAX_FEEDBACK_REQUESTS = 2
RECURSION_LIMIT = 50

# PDF Downloader Configuration
MAX_PAGES = 20
