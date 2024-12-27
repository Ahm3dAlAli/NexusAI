"""Build agent configuration."""

import os

from dotenv import load_dotenv
from nexusai.utils.logger import logger

# Load environment variables from .env file
load_dotenv()

# LLM provider
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
if all([OPENAI_API_VERSION, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT]):
    LLM_PROVIDER = "azure"
elif OPENAI_API_KEY := os.getenv("OPENAI_API_KEY"):
    LLM_PROVIDER = "openai"
else:
    raise ValueError(
        "Neither OpenAI nor Azure OpenAI environment variables are set. "
        "Please set at least one in your .env file."
    )
logger.info(f"Using LLM provider: {LLM_PROVIDER}")

# Arxiv API
ARXIV_API_BASE_URL = "http://export.arxiv.org/api"
PROVIDERS = ["arxiv"]

# Bing API
BING_API_BASE_URL = "https://api.bing.microsoft.com"
if BING_API_KEY := os.getenv("BING_API_KEY"):
    PROVIDERS.append("bing")
    logger.info("Found Bing API key. Bing was added to the list of providers.")
else:
    logger.warning("BING_API_KEY environment variable is not set. Not using Bing API.")

# CORE API
CORE_API_BASE_URL = "https://api.core.ac.uk/v3"
if CORE_API_KEY := os.getenv("CORE_API_KEY"):
    PROVIDERS.append("core")
    logger.info("Found CORE API key. CORE was added to the list of providers.")
else:
    logger.warning("CORE_API_KEY environment variable is not set. Not using CORE API.")

# Google Serp API
SERP_API_BASE_URL = "https://serpapi.com"
if SERP_API_KEY := os.getenv("SERP_API_KEY"):
    PROVIDERS.append("serp")
    logger.info("Found Serp API key. Serp was added to the list of providers.")
else:
    logger.warning("SERP_API_KEY environment variable is not set. Not using Serp API.")

logger.info(f"Using providers: {PROVIDERS}")

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

# Redis
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    logger.warning("REDIS_URL environment variable is not set. Not using cache.")

# Frontend URL
if FRONTEND_URL := os.getenv("FRONTEND_URL"):
    logger.info(f"Frontend URL set to: {FRONTEND_URL}")
else:
    raise ValueError(
        "FRONTEND_URL environment variable is not set. "
        "Please set it in your .env file."
    )

# Request Configuration
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2  # seconds

# State Management Configuration
MAX_FEEDBACK_REQUESTS = 2
RECURSION_LIMIT = 50

# PDF Downloader Configuration
MAX_PAGES = 20
