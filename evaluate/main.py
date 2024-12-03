
import asyncio
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd

# Use absolute imports
from config import EvalConfig, ServiceType
from services.our_agent import OurAgentEvaluator
from services.perplexity import PerplexityEvaluator
from visualization.plots import plot_comparison_metrics
from visualization.reports import generate_report

class Evaluator:
    """Main evaluation orchestrator."""

    def __init__(self, config: EvalConfig):
        self.config = config
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._setup_output_dirs()

    def _setup_output_dirs(self):
        """Create necessary output directories."""
        for dir_name in ["results", "plots", "reports"]:
            Path(f"evaluation_{dir_name}").mkdir(exist_ok=True)

    def _save_results(self, results: Dict[str, Any]) -> pd.DataFrame:
        """Save raw results and convert to DataFrame."""
        rows = []
        for service_name, service_results in results.items():
            for result in service_results:
                # Start with base info
                row = {
                    "service": service_name,
                    "query": result.get("query", ""),
                    "latency": result.get("latency", 0.0),
                    "success": result.get("success", False),
                    "answer": result.get("answer", "")
                }

                # Add performance metrics
                if "performance_metrics" in result:
                    for key, value in result["performance_metrics"].items():
                        row[f"performance_{key}"] = value

                # Add quality metrics
                if "quality_metrics" in result:
                    for key, value in result["quality_metrics"].items():
                        row[f"quality_{key}"] = value

                # Add scientific metrics
                if "scientific_metrics" in result:
                    for key, value in result["scientific_metrics"].items():
                        row[f"scientific_{key}"] = value

                rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Save raw results with all details
        result_path = Path(f"evaluation_results/results_{self.timestamp}.json")
        with open(result_path, "w") as f:
            json.dump(results, f, indent=2)

        # Save processed results
        df.to_csv(f"evaluation_results/metrics_{self.timestamp}.csv", index=False)
        
        # Debug output
        print("\nAvailable columns:", df.columns.tolist())
        print("\nSample data:")
        print(df.head())
        
        return df

    # In evaluate/main.py (update the _analyze_results method)

    def _analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze evaluation results across all metrics."""
        analysis = {}
        
        if df.empty:
            print("Warning: No results to analyze")
            return {}

        try:
            for service in df["service"].unique():
                service_df = df[df["service"] == service]
                
                # Calculate all available metrics
                metrics = {
                    # Performance metrics
                    "latency_metrics": {
                        "average_latency": float(service_df["latency"].mean()),
                        "p95_latency": float(service_df["latency"].quantile(0.95)),
                        "min_latency": float(service_df["latency"].min()),
                        "max_latency": float(service_df["latency"].max())
                    },
                    
                    # Quality metrics
                    "quality_metrics": {
                        "paper_coverage": float(service_df["quality_paper_coverage"].mean() if "quality_paper_coverage" in service_df else 0),
                        "temporal_accuracy": float(service_df["quality_temporal_accuracy"].mean() if "quality_temporal_accuracy" in service_df else 0),
                        "response_completeness": float(service_df["quality_response_completeness"].mean() if "quality_response_completeness" in service_df else 0)
                    },
                    
                    # Scientific metrics
                    "scientific_metrics": {
                        "citation_quality": float(service_df["scientific_citation_quality"].mean() if "scientific_citation_quality" in service_df else 0),
                        "scientific_structure": float(service_df["scientific_scientific_structure"].mean() if "scientific_scientific_structure" in service_df else 0),
                        "technical_depth": float(service_df["scientific_technical_depth"].mean() if "scientific_technical_depth" in service_df else 0),
                        "academic_rigor": float(service_df["scientific_academic_rigor"].mean() if "scientific_academic_rigor" in service_df else 0),
                    },
                    
                    # Overall statistics
                    "success_metrics": {
                        "success_rate": float(len(service_df[service_df["success"] == True]) / len(service_df)),
                        "error_rate": float(len(service_df[service_df["success"] == False]) / len(service_df)),
                        "completion_rate": float(len(service_df[service_df["answer"].str.len() > 0]) / len(service_df)),
                    }
                }
                
                # Calculate aggregate scores
                metrics["aggregate_scores"] = {
                    "overall_quality": sum(metrics["quality_metrics"].values()) / len(metrics["quality_metrics"]),
                    "scientific_rigor": sum(metrics["scientific_metrics"].values()) / len(metrics["scientific_metrics"]),
                    "performance_score": 1.0 / (1.0 + metrics["latency_metrics"]["average_latency"]),  # Higher is better
                    "reliability": (metrics["success_metrics"]["success_rate"] - metrics["success_metrics"]["error_rate"])/metrics["success_metrics"]["success_rate"]
                }
                
                analysis[service] = metrics
                
                # Debug output
                print(f"\nDetailed Metrics for {service}:")
                for category, category_metrics in metrics.items():
                    print(f"\n{category.replace('_', ' ').title()}:")
                    for metric_name, value in category_metrics.items():
                        print(f"  {metric_name}: {value:.3f}")
                
        except Exception as e:
            print(f"Error analyzing results: {e}")
            print("Available columns:", df.columns.tolist())
            print("\nSample data:")
            print(df.head())
            raise
        
        return analysis
    
    async def _run_service_evaluation(self, service_type: ServiceType) -> List[Dict[str, Any]]:
        """Run evaluation for a specific service."""
        service_config = self.config.SERVICES[service_type]
        service_map = {
            ServiceType.OUR_AGENT: OurAgentEvaluator,
            ServiceType.PERPLEXITY: PerplexityEvaluator
        }

        service = service_map[service_type](service_config)
        results = []

        for run in range(self.config.NUM_RUNS):
            print(f"Running evaluation for {service_type.value} (Run {run + 1}/{self.config.NUM_RUNS})")
            try:
                run_results = await service.evaluate_queries(self.config.DEFAULT_QUERIES)
                
                # Ensure each result has the basic required structure
                for result in run_results:
                    if isinstance(result, dict) and "success" in result:
                        result["service"] = service_type.value
                        results.append(result)
                    else:
                        print(f"Warning: Invalid result format: {result}")
            
            except Exception as e:
                print(f"Error in run {run + 1} for {service_type.value}: {e}")
                continue

        return results

    def _display_results(self, analysis: Dict[str, Any]):
        """Display comprehensive evaluation results."""
        print("\nEvaluation Results Summary:")
        print("=" * 100)
        
        if not analysis:
            print("\nNo results available for display.")
            return

        for service, metrics in analysis.items():
            print(f"\n{service.upper()}:")
            print("=" * 50)
            
            # Aggregate Scores
            print("\nAggregate Scores:")
            for metric, value in metrics["aggregate_scores"].items():
                print(f"  • {metric.replace('_', ' ').title()}: {value*100:.1f}%")
            
            # Performance Metrics
            print("\nPerformance Metrics:")
            for metric, value in metrics["latency_metrics"].items():
                if "latency" in metric:
                    print(f"  • {metric.replace('_', ' ').title()}: {value:.2f}s")
                else:
                    print(f"  • {metric.replace('_', ' ').title()}: {value:.1f}")
            
            # Quality Metrics
            print("\nQuality Metrics:")
            for metric, value in metrics["quality_metrics"].items():
                print(f"  • {metric.replace('_', ' ').title()}: {value*100:.1f}%")
            
            # Scientific Metrics
            print("\nScientific Metrics:")
            for metric, value in metrics["scientific_metrics"].items():
                print(f"  • {metric.replace('_', ' ').title()}: {value*100:.1f}%")
            
            # Success Metrics
            print("\nSuccess Metrics:")
            for metric, value in metrics["success_metrics"].items():
                print(f"  • {metric.replace('_', ' ').title()}: {value*100:.1f}%")
            
            print("\n" + "=" * 100)

    async def run(self, 
                 services: Optional[List[str]] = None, 
                 interactive: bool = False):
        """Run the full evaluation pipeline."""
        try:
            # Update enabled services if specified
            if services:
                enabled_services = [ServiceType[s.upper()] for s in services]
                for service_type in ServiceType:
                    self.config.SERVICES[service_type].enabled = service_type in enabled_services

            print("Starting evaluation...")
            print(f"Enabled services: {[s.value for s in self.config.get_enabled_services()]}")
            
            # Run evaluations
            results = {}
            for service_type in self.config.get_enabled_services():
                results[service_type.value] = await self._run_service_evaluation(service_type)

            # Process results
            print("\nProcessing results...")
            df = self._save_results(results)
            
            # Analyze results
            print("Analyzing results...")
            analysis = self._analyze_results(df)
            
            # Generate visualizations and report
            print("Generating visualizations and report...")
            plot_comparison_metrics(df, self.timestamp)
            generate_report(analysis, self.config, self.timestamp)
            
            if interactive:
                self._display_results(analysis)

            print(f"\nEvaluation complete! Results saved with timestamp: {self.timestamp}")

        except Exception as e:
            print(f"Error during evaluation: {str(e)}")
            raise

def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(description="Research Agent Evaluation Framework")
    
    parser.add_argument(
        "--services",
        nargs="+",
        choices=[s.value for s in ServiceType],
        help="Services to evaluate (default: all)"
    )
    
    parser.add_argument(
        "--runs",
        type=int,
        help="Number of evaluation runs"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Show detailed results in console"
    )
    
    args = parser.parse_args()
    
    # Initialize configuration
    config = EvalConfig()
    if args.runs:
        config.NUM_RUNS = args.runs
    
    # Run evaluation
    evaluator = Evaluator(config)
    asyncio.run(evaluator.run(services=args.services, interactive=args.interactive))

if __name__ == "__main__":
    main()