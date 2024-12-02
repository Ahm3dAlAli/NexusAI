from typing import Dict, Any
import re

class QualityMetrics:
    """
    Evaluates the quality and accuracy of research agent responses.
    Measures paper coverage, temporal accuracy, and response completeness.
    """
    def evaluate(self, result: Dict[str, Any], query_data: Dict[str, Any]) -> Dict[str, float]:

        """
        Analyzes response quality through multiple dimensions.
        
        Args:
            result: Response containing answer text and metadata
            query_data: Original query parameters including expected papers and date ranges
            
        Returns:
            Dictionary of quality metrics:
                - paper_coverage: Ratio of found papers to expected papers (0.0-1.0)
                - temporal_accuracy: Proportion of years within requested range (0.0-1.0)
                - response_completeness: Assessment of response detail (0.0-1.0)
                
        Metric Details:
            - paper_coverage: If 8 papers requested and 6 found: 6/8 = 0.75
            - temporal_accuracy: For date range 2020-2023, percentage of mentioned years in range
            - response_completeness: Based on response length, with 100+ characters considered complete
            
        Example:
            For a query requesting 5 papers from 2020-2023:
            {
                "paper_coverage": 0.8,      # Found 4 of 5 papers
                "temporal_accuracy": 0.9,    # 90% of years in range
                "response_completeness": 1.0 # Response longer than 100 chars
            }
        """
        
        text = str(result.get("answer", ""))
        
        # Count papers
        paper_count = len(re.findall(r"Title:", text))
        expected_papers = query_data.get("expected_papers", 0)
        
        # Check year constraints
        min_year = query_data.get("min_year")
        max_year = query_data.get("max_year")
        years_mentioned = re.findall(r"(\d{4})", text)
        years_in_range = 0
        if years_mentioned:
            for year in years_mentioned:
                year = int(year)
                if min_year and year < min_year:
                    continue
                if max_year and year > max_year:
                    continue
                years_in_range += 1
                
        metrics = {
            "paper_coverage": paper_count / expected_papers if expected_papers else 1.0,
            "temporal_accuracy": years_in_range / len(years_mentioned) if years_mentioned else 1.0,
            "response_completeness": 1.0 if len(text) > 100 else len(text) / 100,
        }
        
        return metrics