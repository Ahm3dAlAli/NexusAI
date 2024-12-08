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


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY environment variable is not set. "
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
SEMANTIC_SCHOLAR_BASE_URL = "http://api.semanticscholar.org/graph/v1/paper/search/bulk"
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



# Figure Analysis Configuration
FIGURE_MIN_SIZE = 100  # Minimum pixel size for figures
FIGURE_MAX_SIZE = 4096  # Maximum pixel size for figure processing
FIGURE_FORMATS = ['jpg', 'jpeg', 'png', 'tiff']  # Supported figure formats
FIGURE_CACHE_EXPIRY = 86400 * 30  # 30 days cache for figures

# Claude Configuration
CLAUDE_MODEL = "claude-3-sonnet-20240229"
CLAUDE_MAX_TOKENS = 1000
CLAUDE_TEMPERATURE = 0.2