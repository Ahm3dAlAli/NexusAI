"""Build agent configuration."""

import os

from dotenv import load_dotenv
from nexusai.models.llm import ModelProviderType
from nexusai.utils.logger import logger

# Load environment variables from .env file
load_dotenv()

# LLM provider
if all(
    [
        os.getenv("OPENAI_API_VERSION"),
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
    ]
):
    LLM_PROVIDER = ModelProviderType.azureopenai
elif os.getenv("OPENAI_API_KEY"):
    LLM_PROVIDER = ModelProviderType.openai
    logger.warning(
        "Using OpenAI instead of Azure OpenAI. "
        "Since OpenAI's quotas for gpt-4o are more restrictive for low-tier users, the agent will use gpt-4o-mini, which may degrade performance."
    )
else:
    raise ValueError(
        "Neither OpenAI nor Azure OpenAI environment variables are set. "
        "Please set at least one in your .env file."
    )
logger.info(f"Using LLM provider: {LLM_PROVIDER}")

# Exa API Configuration
EXA_API_KEY = os.getenv("EXA_API_KEY")
if EXA_API_KEY:
    PROVIDERS = ["exa"]
    logger.info(
        "Found Exa API key. Exa will be the only provider used for paper searches."
    )
else:
    raise ValueError(
        "EXA_API_KEY environment variable is not set. Please set it in your .env file."
    )

logger.info(f"Using providers: {PROVIDERS}")

# Traceability with langsmith
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = "nexusai"
    logger.info("Langsmith tracing enabled.")
else:
    logger.warning(
        "LANGCHAIN_API_KEY environment variable is not set. LLM calls will not be traced."
    )

# Redis
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError(
        "REDIS_URL environment variable is not set. Please set it in your .env file."
    )

# Frontend URL
if FRONTEND_URL := os.getenv("FRONTEND_URL"):
    logger.info(f"Frontend URL set to: {FRONTEND_URL}")
else:
    raise ValueError(
        "FRONTEND_URL environment variable is not set. Please set it in your .env file."
    )

# Auth Secret
NEXTAUTH_SECRET = os.getenv("NEXTAUTH_SECRET")
if not NEXTAUTH_SECRET:
    raise ValueError(
        "NEXTAUTH_SECRET environment variable is not set. Please set it in your .env file."
    )

# Request Configuration
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2  # seconds
REQUEST_TIMEOUT = 30  # seconds

# State Management Configuration
MAX_FEEDBACK_REQUESTS = 2
RECURSION_LIMIT = 50

# PDF Downloader Configuration
MAX_PAGES = 20
