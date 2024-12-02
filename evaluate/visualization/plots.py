import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, Any
from pathlib import Path

def plot_comparison_metrics(df: pd.DataFrame, timestamp: str):
    """Generate comparison plots for different metrics."""
    # Set up seaborn style without using plt.style
    sns.set_theme(style="whitegrid")
    sns.set_palette("husl")

    # Create subplot grid
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Service Comparison Metrics', fontsize=16, y=1.02)

    # Ensure the output directory exists
    Path("evaluation_plots").mkdir(exist_ok=True)

    try:
        # Latency plot
        sns.boxplot(data=df, x='service', y='latency', ax=axes[0, 0])
        axes[0, 0].set_title('Response Latency')
        axes[0, 0].set_ylabel('Seconds')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # Paper coverage plot
        if 'quality_paper_coverage' in df.columns:
            sns.barplot(data=df, x='service', y='quality_paper_coverage', ax=axes[0, 1])
            axes[0, 1].set_title('Paper Coverage')
            axes[0, 1].set_ylabel('Coverage Score')
            axes[0, 1].tick_params(axis='x', rotation=45)

        # Citation quality plot
        if 'quality_citation_quality' in df.columns:
            sns.barplot(data=df, x='service', y='quality_citation_quality', ax=axes[1, 0])
            axes[1, 0].set_title('Citation Quality')
            axes[1, 0].set_ylabel('Quality Score')
            axes[1, 0].tick_params(axis='x', rotation=45)

        # Scientific structure plot
        if 'scientific_structure' in df.columns:
            sns.barplot(data=df, x='service', y='scientific_structure', ax=axes[1, 1])
            axes[1, 1].set_title('Scientific Structure')
            axes[1, 1].set_ylabel('Structure Score')
            axes[1, 1].tick_params(axis='x', rotation=45)

        # Adjust layout and save
        plt.tight_layout()
        output_path = f'evaluation_plots/comparison_metrics_{timestamp}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Plots saved to: {output_path}")

    except Exception as e:
        print(f"Error generating plots: {e}")
        print("\nDataFrame information:")
        print(df.info())
        print("\nAvailable columns:", df.columns.tolist())
        raise

def plot_performance_trend(df: pd.DataFrame, timestamp: str):
    """Generate performance trend plots."""
    sns.set_theme(style="whitegrid")
    
    try:
        plt.figure(figsize=(12, 6))
        
        for service in df['service'].unique():
            service_df = df[df['service'] == service]
            plt.plot(range(len(service_df)), service_df['latency'], 
                    label=service, marker='o')
        
        plt.title('Performance Over Time')
        plt.xlabel('Query Number')
        plt.ylabel('Latency (seconds)')
        plt.legend()
        plt.grid(True)
        
        output_path = f'evaluation_plots/performance_trend_{timestamp}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Performance trend plot saved to: {output_path}")

    except Exception as e:
        print(f"Error generating performance trend plot: {e}")
        raise