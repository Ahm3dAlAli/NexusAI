from typing import Dict, Any
import re

class ScientificMetrics:
    """
    Evaluates the academic and scientific rigor of research agent responses.
    Measures citation quality and scientific structure of responses.
    """
    def evaluate(self, result: Dict[str, Any], query_data: Dict[str, Any]) -> Dict[str, float]:
        
        """
        Analyzes the scientific quality of responses.
        
        Args:
            result: Response containing answer text and metadata
            query_data: Original query parameters and requirements
            
        Returns:
            Dictionary of scientific metrics:
                - citation_quality: Quality of references and citations (0.0-1.0)
                - scientific_structure: Presence of scientific elements (0.0-1.0)
                
        Metric Details:
            Citation Quality considers:
            - Standard citations [1] or (2023)
            - DOI references
            - URLs to papers
            
            Scientific Structure checks for:
            - Methodology discussion
            - Results/findings presentation
            
        Example:
            {
                "citation_quality": 0.85,    # High citation quality
                "scientific_structure": 1.0   # Contains both methodology and results
            }
        """
        text = str(result.get("answer", ""))
        
        # Count citations and references
        citations = len(re.findall(r"\[\d+\]|\(\d{4}\)", text))
        dois = len(re.findall(r"doi\.org|DOI:", text))
        urls = len(re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text))
        
        # Check for scientific elements
        has_methodology = any(word in text.lower() for word in ["method", "approach", "technique"])
        has_results = any(word in text.lower() for word in ["result", "finding", "conclusion"])
        
        metrics = {
            "citation_quality": (citations + dois + urls) / (3 * max(1, citations + dois + urls)),
            "scientific_structure": (has_methodology + has_results) / 2,
        }
        
        return metrics