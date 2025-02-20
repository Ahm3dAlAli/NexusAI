import hashlib
import json

import redis
from nexusai.config import REDIS_URL
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger


class CacheManager:
    """Manages caching using Redis."""

    def __init__(self, provider: str = ""):
        self.provider = provider
        if not REDIS_URL:
            raise ValueError("Redis is not enabled.")

        try:
            if REDIS_URL.startswith("rediss://"):
                # SSL enabled
                kwargs = {
                    "decode_responses": False,
                    "ssl_cert_reqs": None,
                }
            else:
                kwargs = {"decode_responses": False}
            self.redis = redis.Redis.from_url(REDIS_URL, **kwargs)
        except redis.exceptions.ConnectionError as e:
            raise Exception(f"Failed to connect to Redis. Reason: {e}")

    def __generate_key(self, url: str) -> str:
        """Generate a unique key based on URL."""
        return f"url:{self.provider}:{hashlib.sha256(url.encode()).hexdigest()}"

    def get_content(self, url: str) -> list[str] | None:
        """Retrieve cached content for a URL."""
        key = self.__generate_key(url)
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_content(
        self, url: str, content: list[str], expire_seconds: int = 86400 * 7
    ) -> None:
        """Store content in cache."""
        logger.info(f"Storing content in cache for {url}")
        key = self.__generate_key(url)
        self.redis.set(key, json.dumps(content), ex=expire_seconds)

    def get_search_results(self, input: SearchPapersInput) -> str | None:
        """Retrieve cached search results."""
        key = f"search:{self.provider}:{hashlib.sha256(input.model_dump_json().encode()).hexdigest()}"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_search_results(
        self, input: SearchPapersInput, results: str, expire_seconds: int = 86400
    ) -> None:
        """Cache search results."""
        logger.info(
            f"Storing search results for provider '{self.provider}' and input '{input.model_dump_json()}'"
        )
        key = f"search:{self.provider}:{hashlib.sha256(input.model_dump_json().encode()).hexdigest()}"
        self.redis.set(key, json.dumps(results), ex=expire_seconds)
