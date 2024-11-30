
# scientific_paper_agent/__init__.py
"""Scientific Paper Agent package."""
__version__ = "0.1.0"

# scientific_paper_agent/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CORE_API_KEY = os.getenv("CORE_API_KEY")

# Model Configuration
MODEL_NAME = "gpt-4-0613"
TEMPERATURE = 0.0

# API Configuration
CORE_API_BASE_URL = "https://api.core.ac.uk/v3"

# Retry Configuration
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2  # seconds

# Validate required environment variables
if not OPENAI_API_KEY or not CORE_API_KEY:
    raise ValueError(
        "Missing required environment variables. "
        "Please ensure OPENAI_API_KEY and CORE_API_KEY are set in your .env file."
    )