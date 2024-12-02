
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
import asyncio
from datetime import datetime

from ..config import ServiceConfig
from ..metrics.quality import QualityMetrics
from ..metrics.performance import PerformanceMetrics
from ..metrics.scientific import ScientificMetrics

class BaseServiceEvaluator(ABC):
    """Base class for service evaluators."""
    
    def __init__(self, service_config: ServiceConfig):
        self.config = service_config
        self.quality_metrics = QualityMetrics()
        self.performance_metrics = PerformanceMetrics()
        self.scientific_metrics = ScientificMetrics()
        
    @abstractmethod
    async def query(self, text: str) -> Dict[str, Any]:
        """Execute a query and return results."""
        pass
        
    async def evaluate_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single query with metrics."""
        start_time = time.time()
        
        try:
            # Execute query
            result = await self.query(query_data["query"])
            end_time = time.time()
            
            # Calculate metrics
            metrics = {
                "query": query_data["query"],
                "timestamp": datetime.now().isoformat(),
                "latency": end_time - start_time,
                "success": True,
                "quality_metrics": self.quality_metrics.evaluate(
                    result, query_data
                ),
                "performance_metrics": self.performance_metrics.evaluate(
                    result, end_time - start_time
                ),
                "scientific_metrics": self.scientific_metrics.evaluate(
                    result, query_data
                ),
                "raw_response": result
            }
            
        except Exception as e:
            metrics = {
                "query": query_data["query"],
                "timestamp": datetime.now().isoformat(),
                "latency": time.time() - start_time,
                "success": False,
                "error": str(e)
            }
            
        return metrics

    async def evaluate_queries(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate a batch of queries."""
        tasks = [self.evaluate_query(query) for query in queries]
        return await asyncio.gather(*tasks)