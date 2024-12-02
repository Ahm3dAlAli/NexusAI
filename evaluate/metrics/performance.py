from typing import Dict, Any

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
            Dictionary containing:
                - latency: Raw response time in seconds
                - tokens_per_second: Processing speed (response length / time taken)
                
        Example:
            For a 1000-character response taking 2 seconds:
            {
                "latency": 2.0,
                "tokens_per_second": 500.0  # 1000 chars / 2 seconds
            }
        """
        return {
            "latency": latency,
            "tokens_per_second": len(str(result)) / latency if latency > 0 else 0,
        }
