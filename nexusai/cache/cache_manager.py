import hashlib
import json

import redis

from nexusai.config import REDIS_URL
from nexusai.models.inputs import SearchPapersInput
from nexusai.utils.logger import logger


class CacheManager:
    """Cache manager for the agent.

    It uses Redis to minimize latency and cost of the APIs.
    """

    def __init__(self):
        if not REDIS_URL:
            self.redis = None
            return

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

    def __generate_key(self, key_type: str, value: str) -> str:
        """Generate a unique cache key based on type and value."""
        return f"{key_type}:{hashlib.sha256(value.encode()).hexdigest()}"

    def get_pdf(self, url: str) -> list[str] | None:
        """Get PDF from cache."""
        if not self.redis:
            return None

        key = self.__generate_key("pdf", url)
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_pdf(self, url: str, pages: list[str]) -> None:
        """Store PDF in cache as a list of pages."""
        if not self.redis:
            return None

        logger.info(f"Storing PDF in cache for {url}")
        key = self.__generate_key("pdf", url)
        self.redis.set(key, json.dumps(pages))

    def get_search_results(self, input: SearchPapersInput) -> str | None:
        """Get search results from cache."""
        if not self.redis:
            return None

        key = self.__generate_key("search", input.model_dump_json())
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_search_results(
        self, input: SearchPapersInput, results: str, expire_seconds: int = 86400 * 7
    ) -> None:
        """Store search results in cache with 7-day default expiration."""
        if not self.redis:
            return None

        logger.info(f"Storing search results in cache for '{input.model_dump_json()}'")
        key = self.__generate_key("search", input.model_dump_json())
        self.redis.set(key, json.dumps(results), ex=expire_seconds)
