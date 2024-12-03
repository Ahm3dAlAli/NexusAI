from typing import Dict, Any
import requests
from .base import BaseServiceEvaluator

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
            print(f"Sending request to Perplexity API...")
            print(f"Model: {self.model}")
            print(f"Payload: {payload}")
            
            response = requests.post(url, json=payload, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "answer": result["choices"][0]["message"]["content"],
                "metadata": {
                    "model_used": self.model,
                    "usage": result.get("usage", {}),
                    "citations": result.get("citations", [])
                }
            }
            
        except Exception as e:
            print(f"Error details: {str(e)}")
            print(f"Response status: {getattr(response, 'status_code', 'N/A')}")
            print(f"Response text: {getattr(response, 'text', 'N/A')}")
            raise Exception(f"Perplexity API error: {str(e)}")