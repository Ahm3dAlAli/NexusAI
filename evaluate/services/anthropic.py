
from typing import Dict, Any
import anthropic
from .base import BaseServiceEvaluator

class AnthropicEvaluator(BaseServiceEvaluator):
    """Evaluator for Anthropic/Claude API."""
    
    def __init__(self, service_config):
        super().__init__(service_config)
        self.client = anthropic.Anthropic(api_key=service_config.api_key)
        self.model = service_config.model_name or "claude-3-opus-20240229"
        
    async def query(self, text: str) -> Dict[str, Any]:
        """Execute a query using Anthropic's Claude API."""
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a scientific research assistant. Provide detailed information about scientific papers with proper citations and thorough analysis."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.2,  # Lower temperature for more focused responses
            )
            
            return {
                "answer": message.content[0].text,
                "metadata": {
                    "model_used": self.model,
                    "stop_reason": message.stop_reason,
                    "usage": message.usage
                }
            }
            
        except Exception as e:
            raise Exception(f"Error querying Anthropic API: {str(e)}")

    async def batch_query(self, queries: list[str]) -> list[Dict[str, Any]]:
        """Execute multiple queries in batch."""
        results = []
        for query in queries:
            try:
                result = await self.query(query)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "metadata": {"model_used": self.model}
                })
        return results