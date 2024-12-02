
import asyncio
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd

# Use absolute imports
from .config import EvalConfig, ServiceType
from .services.our_agent import OurAgentEvaluator
from .services.perplexity import PerplexityEvaluator
from .services.anthropic import AnthropicEvaluator
from .visualization.plots import plot_comparison_metrics
from .visualization.reports import generate_report

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
        # Save raw results
        result_path = Path(f"evaluation_results/results_{self.timestamp}.json")
        with open(result_path, "w") as f:
            json.dump(results, f, indent=2)

        # Convert to DataFrame with proper structure
        rows = []
        for service_name, service_results in results.items():
            for result in service_results:
                # Create base row with service info
                row = {
                    "service": service_name,
                    "query": result.get("query", ""),
                    "latency": result.get("latency", 0.0),
                }

                # Add metrics if available
                metrics = {
                    "quality": result.get("quality_metrics", {}),
                    "performance": result.get("performance_metrics", {}),
                    "scientific": result.get("scientific_metrics", {})
                }

                # Flatten metrics into the row
                for metric_type, metric_values in metrics.items():
                    if isinstance(metric_values, dict):
                        for key, value in metric_values.items():
                            row[f"{metric_type}_{key}"] = value

                rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Save processed results
        df.to_csv(f"evaluation_results/metrics_{self.timestamp}.csv", index=False)
        
        print("\nDataFrame columns:", df.columns.tolist())
        print("\nDataFrame head:")
        print(df.head())
        
        return df

    def _analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze evaluation results."""
        analysis = {}
        
        # Check if DataFrame is empty
        if df.empty:
            print("Warning: No results to analyze")
            return {}

        try:
            for service in df["service"].unique():
                service_df = df[df["service"] == service]
                
                # Initialize metrics with guaranteed metrics
                metrics = {
                    "average_latency": service_df["latency"].mean(),
                    "p95_latency": service_df["latency"].quantile(0.95),
                    "success_rate": len(service_df) / len(df) * len(df["service"].unique()),
                }
                
                # Add quality metrics if available
                metric_mappings = {
                    "quality_paper_coverage": "paper_coverage",
                    "quality_citation_quality": "citation_quality",
                    "scientific_structure": "scientific_accuracy"
                }
                
                for col, metric_name in metric_mappings.items():
                    if col in service_df.columns:
                        try:
                            metrics[metric_name] = service_df[col].mean()
                        except Exception as e:
                            print(f"Warning: Could not calculate {metric_name}: {e}")
                
                analysis[service] = metrics
                
                # Debug output
                print(f"\nMetrics calculated for {service}:")
                for metric, value in metrics.items():
                    print(f"  {metric}: {value}")
        
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
            ServiceType.PERPLEXITY: PerplexityEvaluator,
            ServiceType.ANTHROPIC: AnthropicEvaluator
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
        """Display evaluation results in the console."""
        print("\nEvaluation Results Summary:")
        print("=" * 50)
        
        if not analysis:
            print("\nNo results available for display.")
            return

        for service, metrics in analysis.items():
            print(f"\n{service.upper()}:")
            
            # Display latency metrics
            if "average_latency" in metrics:
                print(f"  Average Latency: {metrics['average_latency']:.2f}s")
            if "p95_latency" in metrics:
                print(f"  95th Percentile Latency: {metrics['p95_latency']:.2f}s")
            if "success_rate" in metrics:
                print(f"  Success Rate: {metrics['success_rate']*100:.1f}%")
            
            # Display quality metrics if available
            if "paper_coverage" in metrics:
                print(f"  Paper Coverage: {metrics['paper_coverage']*100:.1f}%")
            if "citation_quality" in metrics:
                print(f"  Citation Quality: {metrics['citation_quality']*100:.1f}%")
            if "scientific_accuracy" in metrics:
                print(f"  Scientific Accuracy: {metrics['scientific_accuracy']*100:.1f}%")

            # Display additional metrics if present
            additional_metrics = set(metrics.keys()) - {
                'average_latency', 'p95_latency', 'success_rate',
                'paper_coverage', 'citation_quality', 'scientific_accuracy'
            }
            for metric in additional_metrics:
                value = metrics[metric]
                if isinstance(value, (int, float)):
                    print(f"  {metric.replace('_', ' ').title()}: {value:.2f}")
                else:
                    print(f"  {metric.replace('_', ' ').title()}: {value}")

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