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

    def __generate_key(self, key_type: str, value: str) -> str:
        """Generate a unique cache key based on type and value."""
        return (
            f"{key_type}:{self.provider}:{hashlib.sha256(value.encode()).hexdigest()}"
        )

    def get_pdf(self, url: str) -> list[str] | None:
        """Get PDF from cache."""
        key = self.__generate_key("pdf", url)
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_pdf(self, url: str, pages: list[str]) -> None:
        """Store PDF in cache as a list of pages."""
        logger.info(f"Storing PDF in cache for {url}")
        key = self.__generate_key("pdf", url)
        self.redis.set(key, json.dumps(pages))

    def get_search_results(self, input: SearchPapersInput) -> str | None:
        """Get search results from cache."""
        key = self.__generate_key(self.provider, input.model_dump_json())
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_search_results(
        self, input: SearchPapersInput, results: str, expire_seconds: int = 86400
    ) -> None:
        """Store search results in cache with 1-day default expiration."""
        logger.info(
            f"Storing search results in cache for provider '{self.provider}' and input '{input.model_dump_json()}'"
        )
        key = self.__generate_key(self.provider, input.model_dump_json())
        self.redis.set(key, json.dumps(results), ex=expire_seconds)

    def get_url_content(self, url: str) -> str | None:
        """Get URL content from cache."""
        key = self.__generate_key("url", url)
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_url_content(self, url: str, content: str) -> None:
        """Store URL content in cache."""
        logger.info(f"Storing URL content in cache for {url}")
        key = self.__generate_key("url", url)
        self.redis.set(key, json.dumps(content))
