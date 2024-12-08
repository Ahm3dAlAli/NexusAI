import hashlib
import json

import redis

from nexusai.config import REDIS_URL
from nexusai.utils.logger import logger


class CacheManager:
    def __init__(self):
        self.redis = (
            redis.Redis.from_url(REDIS_URL, decode_responses=False)
            if REDIS_URL
            else None
        )

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
        """Store PDF in cache."""
        if not self.redis:
            return None

        logger.info(f"Storing PDF in cache for {url}")
        key = self.__generate_key("pdf", url)
        self.redis.set(key, json.dumps(pages))

    def get_query_results(self, query: str) -> dict | None:
        """Get query results from cache."""
        if not self.redis:
            return None

        key = self.__generate_key("query", query)
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_query_results(
        self, query: str, results: list, expire_seconds: int = 86400 * 7
    ) -> None:
        """Store query results in cache with 7-day default expiration."""
        if not self.redis:
            return None

        logger.info(f"Storing query results in cache for '{query}'")
        key = self.__generate_key("query", query)
        self.redis.set(key, json.dumps(results), ex=expire_seconds)
