from typing import Dict, Any
import requests
from .base import BaseServiceEvaluator
import asyncio


class PerplexityEvaluator(BaseServiceEvaluator):
    """Evaluator for simple chat completion using Perplexity API."""
    
    def __init__(self, service_config):
        super().__init__(service_config)
        self.api_key = service_config.api_key
        self.model = "llama-3.1-sonar-small-128k-online"
        
    async def query(self, text: str) -> Dict[str, Any]:
        """Execute a basic chat completion query."""
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.2
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Make async request using asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(url, json=payload, headers=headers)
            )
            
            response.raise_for_status()
            result = response.json()
            print("Raw result from api call")
            # Extract and format token usage
            usage = result.get("usage", {})
            token_metrics = {
                "completion_tokens": usage.get("completion_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
    
            return {
                "answer": result["choices"][0]["message"]["content"],
                "metadata": {
                    "model_used": result.get("model", self.model),
                    "tokens": token_metrics,
                    "citations": result.get("citations", []),
                    "price": 0.03
                }
            }
            
        except Exception as e:
            print(f"Error in Perplexity API call: {str(e)}")
            print(f"Response status: {getattr(response, 'status_code', 'N/A')}")
            print(f"Response text: {getattr(response, 'text', 'N/A')}")
            raise Exception(f"Perplexity API error: {str(e)}")