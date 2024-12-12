
from typing import Dict, Any, List
import time
from metrics.performance import PerformanceMetrics
from metrics.quality import QualityMetrics
from metrics.scientific import ScientificMetrics

class BaseServiceEvaluator:
    def __init__(self, service_config):
        self.config = service_config
        self.performance_metrics = PerformanceMetrics()
        self.quality_metrics = QualityMetrics()
        self.scientific_metrics = ScientificMetrics()

    async def evaluate_queries(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate a list of queries with all metrics."""
        results = []
        
        for query_data in queries:
            start_time = time.time()
            try:
                # Execute query
                result = await self.query(query_data["query"])
                latency = time.time() - start_time

                # Calculate all metrics
                perf_metrics = self.performance_metrics.evaluate(result, latency)
                qual_metrics = self.quality_metrics.evaluate(result, query_data)
                sci_metrics = self.scientific_metrics.evaluate(result, query_data)

                # Build complete result structure
                complete_result = {
                    "success": True,
                    "query": query_data["query"],
                    "latency": latency,
                    "answer": result["answer"],
                    "performance_metrics": perf_metrics,
                    "quality_metrics": qual_metrics,
                    "scientific_metrics": sci_metrics,
                    "metadata": result.get("metadata", {})
                }
                
                results.append(complete_result)
                
            except Exception as e:
                # Log the error and continue
                print(f"Error processing query: {str(e)}")
                results.append({
                    "success": False,
                    "query": query_data["query"],
                    "error": str(e),
                    "latency": time.time() - start_time
                })
                
        return results

