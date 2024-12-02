import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

def generate_report(analysis: Dict[str, Any], config: Dict[str, Any], timestamp: str) -> None:
    """Generate a detailed evaluation report."""
    try:
        # Create reports directory if it doesn't exist
        Path("evaluation_reports").mkdir(exist_ok=True)

        report = {
            "timestamp": timestamp,
            "evaluation_config": {
                "num_runs": config.NUM_RUNS,
                "queries": config.DEFAULT_QUERIES,
                "services": [s.value for s in config.get_enabled_services()]
            },
            "results": analysis,
            "summary": _generate_summary(analysis),
            "recommendations": _generate_recommendations(analysis)
        }
        
        # Save as JSON
        json_path = f'evaluation_reports/report_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        _generate_html_report(report, timestamp)
        
        print(f"Reports generated:\n - JSON: {json_path}\n - HTML: evaluation_reports/report_{timestamp}.html")
        
    except Exception as e:
        print(f"Error generating report: {e}")
        print("Analysis data:", analysis)
        raise

def _generate_summary(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a summary of the evaluation results."""
    summary = {}
    try:
        if not analysis:
            return {"warning": "No analysis data available"}

        # Find best performing service for each metric
        latency_data = [
            (service, data.get("average_latency", float('inf'))) 
            for service, data in analysis.items()
        ]
        best_latency = min(latency_data, key=lambda x: x[1]) if latency_data else None
        
        # Only include metrics if they exist
        coverage_data = [
            (service, data.get("paper_coverage", 0)) 
            for service, data in analysis.items()
            if "paper_coverage" in data
        ]
        best_coverage = max(coverage_data, key=lambda x: x[1]) if coverage_data else None
        
        quality_data = [
            (service, data.get("citation_quality", 0)) 
            for service, data in analysis.items()
            if "citation_quality" in data
        ]
        best_quality = max(quality_data, key=lambda x: x[1]) if quality_data else None

        summary = {
            "best_performance": {
                "service": best_latency[0],
                "latency": best_latency[1]
            } if best_latency else None,
        }

        if best_coverage:
            summary["best_coverage"] = {
                "service": best_coverage[0],
                "score": best_coverage[1]
            }

        if best_quality:
            summary["best_quality"] = {
                "service": best_quality[0],
                "score": best_quality[1]
            }

        return summary

    except Exception as e:
        print(f"Error generating summary: {e}")
        return {"error": str(e)}

def _generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on the analysis."""
    recommendations = []
    
    try:
        for service, metrics in analysis.items():
            service_recs = []
            
            # Performance recommendations
            if metrics.get("average_latency", 0) > 5.0:  # threshold in seconds
                service_recs.append(
                    f"Consider optimizing response time for {service} "
                    "(current average > 5s)"
                )

            # Coverage recommendations
            if metrics.get("paper_coverage", 1.0) < 0.8:  # 80% threshold
                service_recs.append(
                    f"Improve paper discovery for {service} "
                    "(current coverage < 80%)"
                )

            # Quality recommendations
            if metrics.get("citation_quality", 1.0) < 0.7:  # 70% threshold
                service_recs.append(
                    f"Enhance citation quality for {service} "
                    "(current quality < 70%)"
                )

            recommendations.extend(service_recs)

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        recommendations.append(f"Error analyzing results: {str(e)}")

    return recommendations or ["No specific recommendations generated."]

def _generate_html_report(report: Dict[str, Any], timestamp: str) -> None:
    """Generate an HTML version of the report."""
    try:
        html = f"""
        <html>
            <head>
                <title>Evaluation Report {timestamp}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .metric {{ margin: 20px 0; padding: 10px; background: #f5f5f5; }}
                    .highlight {{ color: #2c5282; font-weight: bold; }}
                    .warning {{ color: #c53030; }}
                </style>
            </head>
            <body>
                <h1>Evaluation Report</h1>
                <p>Generated on: {datetime.fromtimestamp(int(timestamp.split('_')[0])).strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Summary</h2>
                <div class="metric">
                    {_format_summary_html(report['summary'])}
                </div>
                
                <h2>Recommendations</h2>
                <ul>
                    {''.join(f'<li>{r}</li>' for r in report['recommendations'])}
                </ul>
                
                <h2>Detailed Results</h2>
                {_format_results_html(report['results'])}
            </body>
        </html>
        """
        
        with open(f'evaluation_reports/report_{timestamp}.html', 'w') as f:
            f.write(html)
            
    except Exception as e:
        print(f"Error generating HTML report: {e}")
        raise

def _format_summary_html(summary: Dict[str, Any]) -> str:
    """Format summary section for HTML report."""
    if "error" in summary:
        return f'<p class="warning">Error generating summary: {summary["error"]}</p>'
    
    if "warning" in summary:
        return f'<p class="warning">{summary["warning"]}</p>'
    
    html_parts = []
    
    if summary.get("best_performance"):
        html_parts.append(
            f'<p>Best Performance: <span class="highlight">{summary["best_performance"]["service"]}</span> '
            f'({summary["best_performance"]["latency"]:.2f}s)</p>'
        )
    
    if summary.get("best_coverage"):
        html_parts.append(
            f'<p>Best Coverage: <span class="highlight">{summary["best_coverage"]["service"]}</span> '
            f'({summary["best_coverage"]["score"]:.2f})</p>'
        )
    
    if summary.get("best_quality"):
        html_parts.append(
            f'<p>Best Quality: <span class="highlight">{summary["best_quality"]["service"]}</span> '
            f'({summary["best_quality"]["score"]:.2f})</p>'
        )
    
    return '\n'.join(html_parts) or '<p class="warning">No summary data available</p>'

def _format_results_html(results: Dict[str, Any]) -> str:
    """Format results section for HTML report."""
    if not results:
        return '<p class="warning">No results data available</p>'
    
    html_parts = []
    
    for service, metrics in results.items():
        metric_parts = []
        
        if "average_latency" in metrics:
            metric_parts.append(f'<p>Average Latency: {metrics["average_latency"]:.2f}s</p>')
        if "paper_coverage" in metrics:
            metric_parts.append(f'<p>Paper Coverage: {metrics["paper_coverage"]*100:.1f}%</p>')
        if "citation_quality" in metrics:
            metric_parts.append(f'<p>Citation Quality: {metrics["citation_quality"]*100:.1f}%</p>')
        if "scientific_accuracy" in metrics:
            metric_parts.append(f'<p>Scientific Accuracy: {metrics["scientific_accuracy"]*100:.1f}%</p>')
        
        html_parts.append(f'''
            <div class="metric">
                <h3>{service}</h3>
                {''.join(metric_parts)}
            </div>
        ''')
    
    return '\n'.join(html_parts)