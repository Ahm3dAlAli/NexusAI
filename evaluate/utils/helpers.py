import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
from pathlib import Path

class EvaluationLogger:
    """Logger for evaluation process."""
    
    def __init__(self, output_dir: str = "evaluation_logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.output_dir / f"evaluation_{self.timestamp}.log"
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp} [{level}] {message}\n")

class QueryBatcher:
    """Helper for batching queries."""
    
    @staticmethod
    async def process_in_batches(
        queries: List[Dict[str, Any]],
        batch_size: int,
        processor,
        max_concurrency: int = 3
    ) -> List[Dict[str, Any]]:
        """Process queries in batches with concurrency control."""
        results = []
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def process_with_semaphore(query):
            async with semaphore:
                return await processor(query)
        
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[process_with_semaphore(q) for q in batch]
            )
            results.extend(batch_results)
            
        return results

class ResultsManager:
    """Manager for evaluation results."""
    
    def __init__(self, output_dir: str = "evaluation_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def save_json(self, data: Dict[str, Any], filename: str):
        """Save results as JSON."""
        filepath = self.output_dir / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
            
    def save_csv(self, df: pd.DataFrame, filename: str):
        """Save results as CSV."""
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False)
        
    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON results."""
        filepath = self.output_dir / filename
        with open(filepath) as f:
            return json.load(f)
            
    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV results."""
        filepath = self.output_dir / filename
        return pd.read_csv(filepath)

def calculate_improvement_metrics(
    baseline_results: Dict[str, Any],
    our_results: Dict[str, Any]
) -> Dict[str, float]:
    """Calculate improvement metrics compared to baseline."""
    improvements = {}
    
    for metric in ["latency", "paper_coverage", "citation_quality", "scientific_accuracy"]:
        baseline = baseline_results.get(metric, 0)
        ours = our_results.get(metric, 0)
        
        if baseline > 0:
            relative_improvement = ((ours - baseline) / baseline) * 100
            improvements[f"{metric}_improvement"] = relative_improvement
        else:
            improvements[f"{metric}_improvement"] = 0
            
    return improvements

async def retry_with_exponential_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Any:
    """Retry a function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
                
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)