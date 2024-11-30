import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.0

# CORE API Configuration
CORE_API_KEY = os.getenv("CORE_API_KEY")
CORE_API_BASE_URL = "https://api.core.ac.uk/v3"

# Request Configuration
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2  # seconds

# State Management Configuration
MAX_FEEDBACK_REQUESTS = 2

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