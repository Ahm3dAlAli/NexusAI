import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o"  # The model used in the original notebook
TEMPERATURE = 0.0

# CORE API Configuration
CORE_API_KEY = os.getenv("CORE_API_KEY")
CORE_API_BASE_URL = "https://api.core.ac.uk/v3"

# Request Configuration
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2  # seconds

# PDF Processing Configuration
PDF_CHUNK_SIZE = 4000  # characters
MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB

# State Management Configuration
MAX_FEEDBACK_ATTEMPTS = 2

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Please set it in your .env file."
    )

if not CORE_API_KEY:
    raise ValueError(
        "CORE_API_KEY environment variable is not set. "
        "Please set it in your .env file."
    )

# API Headers Configuration
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Tool Configuration
TOOL_CONFIGS = {
    "search_papers": {
        "default_max_papers": 1,
        "max_allowed_papers": 10
    },
    "download_paper": {
        "timeout": 30,  # seconds
        "verify_ssl": False
    }
}