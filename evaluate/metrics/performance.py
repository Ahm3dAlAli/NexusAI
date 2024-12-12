from typing import Dict, Any
import re
from dataclasses import dataclass
from typing import Optional, List
@dataclass
class ToolCall:
    id: str
    function: Dict[str, str]
    type: str

@dataclass
class TokenUsage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

@dataclass
class ResponseMetadata:
    token_usage: TokenUsage
    model_name: str
    system_fingerprint: str
    finish_reason: str

class PerformanceMetrics:
    """
    Evaluates computational performance metrics of the research agent.
    Focuses on response time and processing efficiency metrics.
    """
    def evaluate(self, result: Dict[str, Any], latency: float) -> Dict[str, float]:
        """
        Calculates performance metrics based on response time and output size.
        
        Args:
            result: The response from the research agent, containing the answer and metadata
            latency: Time taken in seconds to generate the response
            
        Returns:
            Dictionary containing performance metrics:
            - latency: Raw response time in seconds
            - tokens_per_second: Token processing speed
            - total_tokens: Total tokens used in the interaction
        """
        # Extract token usage from response metadata
 
        token_usage = result.get("metadata", {}).get("tokens", {}).get("completion_tokens",0)
        
        metrics = {
            "latency": latency,
            "tokens_per_second": token_usage / latency if latency > 0 else 0
        }
        
        return metrics