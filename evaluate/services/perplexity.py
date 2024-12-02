
from typing import Dict, Any
import requests
from .base import BaseServiceEvaluator

class PerplexityEvaluator(BaseServiceEvaluator):
    """Evaluator for Perplexity API."""
    
    def __init__(self, service_config):
        super().__init__(service_config)
        self.api_key = service_config.api_key
        self.model = service_config.model_name or "llama-3.1-sonar-small-128k-online"
        
    async def query(self, text: str) -> Dict[str, Any]:
        """Execute a query using Perplexity API."""
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a scientific research assistant. Provide detailed, accurate information about scientific papers with proper citations."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "search_domain_filter": ["arxiv.org", "scholar.google.com", "science.org", "nature.com", "sciencedirect.com"],
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "year",  # Focus on recent papers
            "top_k": 10,  # Get more comprehensive results
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                "answer": result["choices"][0]["message"]["content"],
                "metadata": {
                    "model_used": self.model,
                    "finish_reason": result["choices"][0].get("finish_reason"),
                    "usage": result.get("usage", {})
                }
            }
            
        except Exception as e:
            raise Exception(f"Error querying Perplexity API: {str(e)}")