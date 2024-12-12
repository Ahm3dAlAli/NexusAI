from typing import Dict, Any, List
import re
from dataclasses import dataclass
from typing import Optional

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

class QualityMetrics:
    """
    Evaluates the quality and accuracy of research agent responses.
    Measures success rate, query relevance, and response completeness.
    """
    def evaluate(self, result: Dict[str, Any], query_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyzes response quality through multiple dimensions.
        
        Args:
            result: Response containing answer text and metadata
            query_data: Original query parameters
            
        Returns:
            Dictionary of quality metrics:
                - success_rate: Success based on content presence (0.0-1.0)
                - query_relevance: Assessment of response relevance to query (0.0-1.0)
                - response_completeness: Assessment of response completeness (0.0-1.0)
        """
        # Extract content
        content = self._extract_content(result)
        
        # Calculate success rate based on content presence
        success_rate = 1.0 if content.strip() else 0.0
        
        # Calculate query relevance
        query_terms = self._extract_query_terms(query_data)
        query_relevance = self._calculate_query_relevance(content, query_terms)
        
        # Calculate response completeness
        response_completeness = self._calculate_completeness(result)
        
        metrics = {
            "success_rate": success_rate,
            "query_relevance": query_relevance,
            "response_completeness": response_completeness
        }
        
        return metrics
    
    def _extract_content(self, result: Dict[str, Any]) -> str:
        """Extract content from response."""
        # Try different possible content locations
        content_locations = [
            result.get("content", ""),
            result.get("choices", [{}])[0].get("message", {}).get("content", ""),
            result.get("answer", "")
        ]
        
        # Return first non-empty content found
        for content in content_locations:
            if content and content.strip():
                return content.strip()
        return ""

    def _extract_query_terms(self, query_data: Dict[str, Any]) -> List[str]:
        """Extract key terms from the query for relevance calculation."""
        query = query_data.get("query", "")
        # Remove special operators and clean query
        clean_query = re.sub(r'AND|OR|\d{4}|[^\w\s]', '', query)
        return [term.lower() for term in clean_query.split()]

    def _calculate_query_relevance(self, content: str, query_terms: List[str]) -> float:
        """Calculate relevance of response to query terms."""
        if not query_terms or not content:
            return 0.0
        
        content_lower = content.lower()
        matches = sum(1 for term in query_terms if term in content_lower)
        return matches / len(query_terms)

    def _calculate_completeness(self, result: Dict[str, Any]) -> float:
        """Calculate response completeness based on multiple factors."""
        content = self._extract_content(result)
        token_usage = result.get("response_metadata", {}).get("token_usage", {})
        completion_tokens = token_usage.get("completion_tokens", 0)
        
        # Consider both content length and token usage
        has_sufficient_length = len(content) >= 50
        has_sufficient_tokens = completion_tokens >= 200
        
        if has_sufficient_length and has_sufficient_tokens:
            return 1.0
        elif has_sufficient_length or has_sufficient_tokens:
            return 0.75
        else:
            return max(len(content) / 100, completion_tokens / 50)