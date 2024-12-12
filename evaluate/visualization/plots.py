import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, Any
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
import seaborn as sns
import pandas as pd
from typing import Dict, Any
from pathlib import Path
import numpy as np

import numpy as np
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms


class ServiceTradeoffAnalyzer:
    """Analyzes and visualizes tradeoffs between different service metrics."""
    
    def __init__(self, df: pd.DataFrame, timestamp: str):
        self.df = df
        self.timestamp = timestamp
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(df['service'].unique())]
        Path("evaluation_plots").mkdir(exist_ok=True)
        
        # Define metrics structure
        self.metric_classes = {
            'Quality': ['success_rate', 'query_relevance', 'response_completeness'],
            'Scientific': ['scientific_structure', 'technical_depth', 'academic_rigor'],
            'Performance': ['latency', 'tokens_per_second']
        }

        # Set plotting style
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = '#f8f9fa'
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['grid.color'] = '#cccccc'
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 13
        plt.rcParams['lines.linewidth'] = 2
        plt.rcParams['patch.edgecolor'] = 'none'
        plt.rcParams['axes.grid'] = True
        plt.rcParams['axes.grid.axis'] = 'both'
        plt.rcParams['grid.linestyle'] = '--'

    def analyze_tradeoffs(self):
        """Generate comprehensive tradeoff analysis visualizations."""
        # 1. Multi-dimensional tradeoff plot
        self._plot_multidimensional_tradeoff()

        # 2. Multi-diemnsional tradeoff plot 
        self._plot_price_scientific_tradeoff()
        
        self._plot_reliability_cost_tradeoff()

        # 2. Radar chart for metric classes
        self._plot_class_radar()
        
        # 3. Statistical comparison within classes
        self._plot_intraclass_comparison()

    def _plot_multidimensional_tradeoff(self):
        """Create enhanced multi-dimensional tradeoff visualization."""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Fixed latency boundaries
        max_latency = 10
        mid_latency = 5

        # Create regions
        handles = []
        handles.append(ax.axvspan(0, mid_latency, ymin=0.5, ymax=1, alpha=0.1, 
                                color='green', label='Optimal Region'))
        handles.append(ax.axvspan(mid_latency, max_latency, ymin=0.5, ymax=1, alpha=0.1, 
                                color='yellow', label='Scientific Focus Region'))
        handles.append(ax.axvspan(0, mid_latency, ymin=0, ymax=0.5, alpha=0.1, 
                                color='yellow', label='Speed Focus Region'))
        handles.append(ax.axvspan(mid_latency, max_latency, ymin=0, ymax=0.5, alpha=0.1, 
                                color='red', label='Improvement Needed Region'))

        # Plot data points
        service_points = []
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Calculate metrics
            latency = service_df['latency'].mean()
            scientific_score = np.mean([
                service_df[col].mean() for col in self.metric_classes['Scientific']
            ]) * 100
            quality_score = np.mean([
                service_df[col].mean() for col in self.metric_classes['Quality']
            ]) * 100
            
            # Plot point with size based on quality score
            point = ax.scatter(latency, scientific_score,
                             s=300 * (quality_score/100),
                             c=[color],
                             alpha=0.7,
                             label=f'{service} (Q: {quality_score:.1f}%)')
            service_points.append(point)
            
        # Add region labels
        ax.text(mid_latency/2, 75, 'OPTIMAL\nFast & Accurate', 
                ha='center', va='center', alpha=0.7)
        ax.text(mid_latency*1.5, 75, 'QUALITY FOCUSED\nSlow but Accurate', 
                ha='center', va='center', alpha=0.7)
        ax.text(mid_latency/2, 25, 'FAST\nLower Quality', 
                ha='center', va='center', alpha=0.7)
        ax.text(mid_latency*1.5, 25, 'NEEDS IMPROVEMENT\nSlow & Lower Quality', 
                ha='center', va='center', alpha=0.7)

        # Customize plot
        ax.set_xlabel('Response Latency (seconds) - Lower is Better →')
        ax.set_ylabel('Scientific Rigor Score (%) - Higher is Better →')
        ax.set_title('Service Performance Analysis')
        ax.grid(True, alpha=0.3)
        
        # Add legends
        region_legend = ax.legend(handles, 
                                ['Optimal Region', 'Scientific Focus Region', 
                                 'Speed Focus Region', 'Improvement Needed Region'],
                                loc='upper right',
                                title='Performance Regions',
                                bbox_to_anchor=(1.15, 1))
        ax.add_artist(region_legend)
        service_legend = ax.legend(service_points,
                                 [p.get_label() for p in service_points],
                                 loc='lower right',
                                 title='Services',
                                 bbox_to_anchor=(1.15, 0))
        
        # Set limits
        ax.set_xlim(0, max_latency)
        ax.set_ylim(0, 100)
        ax.axvline(x=mid_latency, color='gray', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/multidim_tradeoff_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_price_scientific_tradeoff(self):
        """Create enhanced multi-dimensional tradeoff visualization for price vs scientific metrics."""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Fixed price boundaries
        max_price = 0.05  # $0.05 per request
        mid_price = 0.025  # $0.025 per request
        
        # Create regions
        handles = []
        handles.append(ax.axvspan(0, mid_price, ymin=0.5, ymax=1, alpha=0.1,
                                color='green', label='Optimal Region'))
        handles.append(ax.axvspan(mid_price, max_price, ymin=0.5, ymax=1, alpha=0.1,
                                color='yellow', label='Scientific Focus Region'))
        handles.append(ax.axvspan(0, mid_price, ymin=0, ymax=0.5, alpha=0.1,
                                color='yellow', label='Cost Focus Region'))
        handles.append(ax.axvspan(mid_price, max_price, ymin=0, ymax=0.5, alpha=0.1,
                                color='red', label='Improvement Needed Region'))
        
        # Plot data points
        service_points = []
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Calculate metrics with updated weights for scientific score
            scientific_score = (
                0.33 * service_df['academic_rigor'].mean() +
                0.33 * service_df['technical_depth'].mean() +
                0.33 * service_df['scientific_structure'].mean()
            ) * 100
            
            quality_score = np.mean([
                service_df[col].mean() for col in self.metric_classes['Quality']
            ]) * 100
            
            price = service_df['price'].mean()
            
            # Plot point with size based on quality score
            point = ax.scatter(price, scientific_score,
                            s=300 * (quality_score/100),
                            c=[color],
                            alpha=0.7,
                            label=f'{service} (Q: {quality_score:.1f}%)')
            service_points.append(point)
            
        # Add region labels
        ax.text(mid_price/2, 75, 'OPTIMAL\nHigh Scientific Quality & Low Cost',
                ha='center', va='center', alpha=0.7)
        ax.text(mid_price*1.5, 75, 'QUALITY FOCUSED\nHigh Scientific Quality but Expensive',
                ha='center', va='center', alpha=0.7)
        ax.text(mid_price/2, 25, 'BUDGET\nLow Cost but Lower Scientific Quality',
                ha='center', va='center', alpha=0.7)
        ax.text(mid_price*1.5, 25, 'NEEDS IMPROVEMENT\nExpensive & Lower Scientific Quality',
                ha='center', va='center', alpha=0.7)
        
        # Customize plot
        ax.set_xlabel('Cost per Request ($) - Lower is Better →')
        ax.set_ylabel('Scientific Rigor Score (%) - Higher is Better →')
        ax.set_title('Cost-Scientific Tradeoff Analysis')
        ax.grid(True, alpha=0.3)
        
        # Add legends
        region_legend = ax.legend(handles,
                                ['Optimal Region', 'Scientific Focus Region',
                                'Cost Focus Region', 'Improvement Needed Region'],
                                loc='upper right',
                                title='Performance Regions',
                                bbox_to_anchor=(1.15, 1))
        ax.add_artist(region_legend)
        service_legend = ax.legend(service_points,
                                [p.get_label() for p in service_points],
                                loc='lower right',
                                title='Services',
                                bbox_to_anchor=(1.15, 0))
        
        # Set limits
        ax.set_xlim(0, max_price)
        ax.set_ylim(0, 100)
        ax.axvline(x=mid_price, color='gray', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/price_scientific_tradeoff_{self.timestamp}.png',
                    dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_reliability_cost_tradeoff(self):

        """Create enhanced multi-dimensional tradeoff visualization for reliability vs cost."""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Fixed price boundaries
        max_price = 0.05  # $0.05 per request
        mid_price = 0.025  # $0.025 per request
        
        # Create regions
        handles = []
        handles.append(ax.axvspan(0, mid_price, ymin=0.5, ymax=1, alpha=0.1,
                                color='green', label='Optimal Region'))
        handles.append(ax.axvspan(mid_price, max_price, ymin=0.5, ymax=1, alpha=0.1,
                                color='yellow', label='Reliability Focus Region'))
        handles.append(ax.axvspan(0, mid_price, ymin=0, ymax=0.5, alpha=0.1,
                                color='yellow', label='Cost Focus Region'))
        handles.append(ax.axvspan(mid_price, max_price, ymin=0, ymax=0.5, alpha=0.1,
                                color='red', label='Improvement Needed Region'))
        
        # Plot data points
        service_points = []
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Calculate reliability score with specified weights
            reliability_score = (
                0.5 * service_df['academic_rigor'].mean() +     # 50% academic rigor
                0.2 * service_df['scientific_structure'].mean() + # 20% scientific structure
                0.3 * service_df['query_relevance'].mean()       # 30% query relevance
            ) * 100
            
            # Calculate other metrics
            scientific_score = np.mean([
                service_df[col].mean() for col in self.metric_classes['Scientific']
            ]) * 100
            
            price = service_df['price'].mean()
            
            # Plot point with size based on scientific score
            point = ax.scatter(price, reliability_score,
                            s=300 * (scientific_score/100),
                            c=[color],
                            alpha=0.7,
                            label=f'{service} (S: {scientific_score:.1f}%)')
            service_points.append(point)
        
        # Add region labels
        ax.text(mid_price/2, 75, 'OPTIMAL\nReliable & Cost-Effective',
                ha='center', va='center', alpha=0.7)
        ax.text(mid_price*1.5, 75, 'RELIABILITY FOCUSED\nReliable but Expensive',
                ha='center', va='center', alpha=0.7)
        ax.text(mid_price/2, 25, 'BUDGET\nLow Cost but Less Reliable',
                ha='center', va='center', alpha=0.7)
        ax.text(mid_price*1.5, 25, 'NEEDS IMPROVEMENT\nExpensive & Less Reliable',
                ha='center', va='center', alpha=0.7)
        
        # Customize plot
        ax.set_xlabel('Cost per Request ($) - Lower is Better →')
        ax.set_ylabel('Reliability Score (%) - Higher is Better →')
        ax.set_title('Reliability-Cost Tradeoff Analysis')
        ax.grid(True, alpha=0.3)
        
        # Add legends
        region_legend = ax.legend(handles,
                                ['Optimal Region', 'Reliability Focus Region',
                                'Cost Focus Region', 'Improvement Needed Region'],
                                loc='upper right',
                                title='Performance Regions',
                                bbox_to_anchor=(1.15, 1))
        ax.add_artist(region_legend)
        service_legend = ax.legend(service_points,
                                [p.get_label() for p in service_points],
                                loc='lower right',
                                title='Services',
                                bbox_to_anchor=(1.15, 0))
        
        # Set limits
        ax.set_xlim(0, max_price)
        ax.set_ylim(0, 100)
        ax.axvline(x=mid_price, color='gray', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/reliability_cost_tradeoff_{self.timestamp}.png',
                    dpi=300, bbox_inches='tight')
        plt.close()
    def _plot_class_radar(self):
        """Create radar chart comparing metric classes."""
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, projection='polar')

        # Define metrics and labels
        metrics = [
            'Quality Score',
            'Scientific Rigor',
            'Response Speed',
            'Completeness',
            'Technical Depth'
        ]
        
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)

        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Calculate scores
            quality_score = np.mean([
                service_df[m].mean() for m in self.metric_classes['Quality']
            ]) * 100
            
            scientific_score = np.mean([
                service_df[m].mean() for m in self.metric_classes['Scientific']
            ]) * 100
            
            response_speed = 100 * (1 / (1 + service_df['latency'].mean()))
            completeness = service_df['response_completeness'].mean() * 100
            technical_depth = service_df['technical_depth'].mean() * 100
            
            values = [
                quality_score,
                scientific_score,
                response_speed,
                completeness,
                technical_depth
            ]
            values = np.concatenate((values, [values[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2, label=service, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 100)
        ax.set_rticks([20, 40, 60, 80, 100])
        
        ax.text(0, 110, 'Service Performance Overview', 
               ha='center', va='center', fontsize=14)
        
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1),
                  title='Services')
        plt.savefig(f'evaluation_plots/class_radar_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_intraclass_comparison(self):
        """Create statistical comparison with significance indicators."""
        fig, axes = plt.subplots(len(self.metric_classes), 1, 
                                figsize=(15, 7*len(self.metric_classes)))
        
        for idx, (class_name, metrics) in enumerate(self.metric_classes.items()):
            ax = axes[idx]
            
            plot_data = []
            labels = []
            for metric in metrics:
                for service in self.df['service'].unique():
                    service_df = self.df[self.df['service'] == service]
                    values = service_df[metric].copy()
                    if 'latency' not in metric:
                        values = values * 100
                    plot_data.append(values)
                    labels.append(f"{service}\n{metric.replace('_', ' ').title()}")
            
            bp = ax.boxplot(plot_data, labels=labels, patch_artist=True)
            
            # Color boxes
            for i, service in enumerate(self.df['service'].unique()):
                for j in range(len(metrics)):
                    box_idx = i * len(metrics) + j
                    bp['boxes'][box_idx].set_facecolor(self.colors[i])
                    bp['boxes'][box_idx].set_alpha(0.6)
            
            # Add significance indicators
            if len(self.df['service'].unique()) >= 2:
                sig_height = np.max([np.max(x) for x in plot_data]) * 1.1
                services = list(self.df['service'].unique())
                for i, metric in enumerate(metrics):
                    s1_data = self.df[self.df['service'] == services[0]][metric]
                    s2_data = self.df[self.df['service'] == services[1]][metric]
                    if 'latency' not in metric:
                        s1_data = s1_data * 100
                        s2_data = s2_data * 100
                    
                    t_stat, p_val = stats.ttest_ind(s1_data, s2_data)
                    sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'
                    ax.text(i * 2 + 1.5, sig_height, sig, ha='center',
                           fontsize=12, fontweight='bold')

            metric_type = '(Lower is Better)' if 'Performance' in class_name and 'latency' in metrics[0] else '(Higher is Better)'
            ax.set_title(f'{class_name} Metrics Comparison {metric_type}')
            ax.set_ylabel('Score (%)' if class_name != 'Performance' else 'Value')
            ax.grid(True, axis='y')
            
            if idx == 0:
                ax.text(0.98, 0.98, 
                       'Significance: *** p<0.001, ** p<0.01, * p<0.05, ns: not significant',
                       transform=ax.transAxes, ha='right', va='top',
                       bbox=dict(facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig(f'evaluation_plots/intraclass_comparison_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

class StatisticalDashboardGenerator:
    def __init__(self, df: pd.DataFrame, timestamp: str):
        self.df = df
        self.timestamp = timestamp
        
        # Professional blue-based color scheme for services
        self.service_colors = {
            service: color for service, color in zip(
                df['service'].unique(),
                ['#1f77b4', '#2c91d1', '#55a8e2', '#7fbfee'][:len(df['service'].unique())]
            )
        }
        
        # Map unique queries to markers
        self.unique_queries = df['query'].unique()
        self.query_markers = {
            query: marker for query, marker in zip(
                self.unique_queries,
                ['o', 's', '^', 'D', 'v'][:len(self.unique_queries)]
            )
        }
        
        # Shorten query names for legends
        self.query_labels = {
            query: f'Q{i+1}' for i, query in enumerate(self.unique_queries)
        }
        
        Path("evaluation_plots").mkdir(exist_ok=True)
        
        # Updated metrics structure
        self.metrics = {
            'Quality': ['success_rate', 'query_relevance', 'response_completeness'],
            'Scientific': ['scientific_structure', 'academic_rigor', 'technical_depth'],
            'Performance': ['latency', 'tokens_per_second']
        }
        
        # Set better default style
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = '#f8f9fa'
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['grid.color'] = '#cccccc'
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 13

    def create_statistical_dashboard(self):
        """Create enhanced statistical analysis dashboard."""
        fig = plt.figure(figsize=(20, 15))
        gs = plt.GridSpec(2, 2, figure=fig)
        
        # 1. Performance vs Quality Tradeoff (Top Left)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_enhanced_tradeoff(ax1)
        
        # 2. Statistical Comparison (Top Right)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_statistical_comparison(ax2)
        
        # 3. Metric Correlations (Bottom Left)
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_enhanced_correlations(ax3)
        
        # 4. Performance Distribution (Bottom Right)
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_performance_distribution(ax4)
        
        plt.suptitle('Statistical Analysis of Service Performance', 
                    fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/statistical_dashboard_{self.timestamp}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_enhanced_tradeoff(self, ax):
        """Plot enhanced tradeoff analysis with query type differentiation."""
        for service in self.df['service'].unique():
            color = self.service_colors[service]
            
            for query in self.unique_queries:
                service_query_df = self.df[(self.df['service'] == service) & 
                                        (self.df['query'] == query)]
                
                if len(service_query_df) == 0:
                    continue
                
                # Calculate metrics
                quality_score = (
                    0.25 * service_query_df['success_rate'].mean() +
                    0.35 * service_query_df['query_relevance'].mean() +
                    0.40 * service_query_df['response_completeness'].mean()
                ) * 100
                
                latency = service_query_df['latency'].mean()
                scientific_score = (
                    0.33 * service_query_df['scientific_structure'].mean() +
                    0.33 * service_query_df['academic_rigor'].mean() +
                    0.34 * service_query_df['technical_depth'].mean()
                ) * 100
                
                # Size based on processing speed
                size = 300 * (1 / (1 + latency))
                
                # Plot main point
                marker = self.query_markers[query]
                ax.scatter(latency, scientific_score, 
                        s=size, color=color, alpha=0.7,
                        marker=marker,
                        label=f'{service} - {self.query_labels[query]}')
               
                # Add confidence ellipse if enough points
                if len(service_query_df) >= 3:
    
                        # Convert scientific score to array of same length as latency
                        scientific_values = np.full_like(
                            service_query_df['latency'].values,
                            scientific_score
                        )
                        
                        # Add confidence ellipse using external function
                        ellipse =confidence_ellipse(
                            x=service_query_df['latency'].values,
                            y=scientific_values,
                            ax=ax,
                            n_std=3,
                            facecolor=color,
                            alpha=0.1,
                            edgecolor=color,
                            linewidth=1
                        )
                        ax.add_patch(ellipse)
                # Annotate point
                ax.annotate(
                    f'{service} {self.query_labels[query]}\n'
                    f'Quality: {quality_score:.1f}%\n'
                    f'Scientific: {scientific_score:.1f}%\n'
                    f'Latency: {latency:.2f}s',
                    (latency, scientific_score),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(facecolor='white', alpha=0.8)
                )

        # Create custom legends
        from matplotlib.lines import Line2D
        
        # Service legend
        service_legend = [
            Line2D([0], [0], marker='o', color='w', 
                markerfacecolor=color, label=service, markersize=10)
            for service, color in self.service_colors.items()
        ]
        
        # Query type legend
        query_legend = [
            Line2D([0], [0], marker=self.query_markers[query], color='black', 
                label=f'{self.query_labels[query]}: {query[:30]}...' if len(query) > 30 else query,
                markersize=10)
            for query in self.unique_queries
        ]
        
        # Add both legends
        leg1 = ax.legend(handles=service_legend, title='Services', 
                        bbox_to_anchor=(1.05, 1))
        ax.add_artist(leg1)
        ax.legend(handles=query_legend, title='Queries',
                bbox_to_anchor=(1.05, 0.5))
        
        ax.set_xlabel('Response Latency (seconds) - Lower is Better →')
        ax.set_ylabel('Scientific Score (%) - Higher is Better →')
        ax.set_title('Service Performance Tradeoff Analysis')
        ax.grid(True, alpha=0.2)

    def _plot_statistical_comparison(self, ax):
        """Plot enhanced statistical comparison."""
        services = list(self.df['service'].unique())
        if len(services) < 2:
            ax.text(0.5, 0.5, 'Need multiple services for comparison',
                   ha='center', va='center')
            return
        
        # Define metrics to compare
        comparison_metrics = [
            ('Response Time', 'latency', 1.0),  # value is multiplier
            ('Scientific Quality', 'scientific_structure', 100.0),
            ('Query Relevance', 'query_relevance', 100.0)
        ]
        
        data = []
        for metric_name, column, multiplier in comparison_metrics:
            try:
                stat = stats.ttest_ind(
                    self.df[self.df['service'] == services[0]][column] * multiplier,
                    self.df[self.df['service'] == services[1]][column] * multiplier
                )
                
                data.append({
                    'Metric': metric_name,
                    'p_value': -np.log10(stat.pvalue),
                    'significant': stat.pvalue < 0.05
                })
            except Exception as e:
                print(f"Error calculating statistics for {metric_name}: {e}")
        
        if not data:
            ax.text(0.5, 0.5, 'No statistical comparison available',
                   ha='center', va='center')
            return
        
        # Create bar plot
        bars = ax.barh([d['Metric'] for d in data],
                      [d['p_value'] for d in data],
                      color=["#2c91d1" if d['significant'] else '#cccccc' for d in data])
        
        # Add significance threshold line
        ax.axvline(-np.log10(0.05), color='red', linestyle='--', alpha=0.5,
                   label='Significance Threshold (p=0.05)')
        
        # Add labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'p={10**(-width):.3f}',
                   ha='left', va='center', fontsize=10)
        
        ax.set_xlabel('-log10(p-value)')
        ax.set_title('Statistical Significance of Service Differences')
        ax.legend()

    def _plot_enhanced_correlations(self, ax):
        """Plot enhanced correlation matrix."""
        # Define key metrics for correlation analysis
        metrics = {
            'Response Time': 'latency',
            'Success Rate': 'success_rate',
            'Query Relevance': 'query_relevance',
            'Scientific Score': 'scientific_structure'
        }
        
        # Calculate correlation matrix
        corr_data = self.df[[v for v in metrics.values()]].corr()
        corr_data.index = metrics.keys()
        corr_data.columns = metrics.keys()
        
        # Create heatmap
        im = ax.imshow(corr_data, cmap='RdYlBu', aspect='auto')
        
        # Add correlation values
        for i in range(len(metrics)):
            for j in range(len(metrics)):
                text = ax.text(j, i, f'{corr_data.iloc[i, j]:.2f}',
                             ha='center', va='center',
                             color='black' if abs(corr_data.iloc[i, j]) < 0.7 else 'white')
        
        # Customize plot
        ax.set_xticks(range(len(metrics)))
        ax.set_yticks(range(len(metrics)))
        ax.set_xticklabels(metrics.keys(), rotation=45, ha='right')
        ax.set_yticklabels(metrics.keys())
        
        plt.colorbar(im, ax=ax, label='Correlation Coefficient')
        ax.set_title('Metric Correlations')

    def _plot_performance_distribution(self, ax):
        """Plot enhanced performance distribution with query type differentiation."""
        linestyles = ['-', '--', ':', '-.', '-']
        
        for service in self.df['service'].unique():
            color = self.service_colors[service]
            
            for i, query in enumerate(self.unique_queries):
                service_query_df = self.df[(self.df['service'] == service) & 
                                         (self.df['query'] == query)]
                
                if len(service_query_df) == 0:
                    continue
                
                # Plot latency distribution
                sns.kdeplot(data=service_query_df['latency'], ax=ax, 
                          color=color, linestyle=linestyles[i % len(linestyles)],
                          label=f'{service} - {self.query_labels[query]}', alpha=0.7)
                
                # Add mean marker
                mean_latency = service_query_df['latency'].mean()
                ax.axvline(mean_latency, color=color, linestyle=linestyles[i % len(linestyles)], 
                          alpha=0.5)
                ax.text(mean_latency, ax.get_ylim()[1] * (0.9 - 0.1 * i),
                       f'{self.query_labels[query]}: {mean_latency:.2f}s',
                       color=color, ha='right', va='top')
        
        ax.set_xlabel('Response Latency (seconds)')
        ax.set_ylabel('Density')
        ax.set_title('Response Time Distribution by Service and Query')
        ax.legend(bbox_to_anchor=(1.05, 1))
        ax.grid(True, alpha=0.2)

def confidence_ellipse(x, y, ax, n_std=3.0, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)
    
    scale_x = np.sqrt(cov[0, 0]) * n_std
    scale_y = np.sqrt(cov[1, 1]) * n_std
    
    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(np.mean(x), np.mean(y))
    
    ellipse.set_transform(transf + ax.transData)
    return ellipse


class DashboardGenerator:
    """Generates comprehensive evaluation dashboards."""
    
    def __init__(self, df: pd.DataFrame, timestamp: str):
        self.df = df
        self.timestamp = timestamp
        self.colors = ['#08519c', '#3182bd', '#6baed6', '#bdd7e7'][:len(df['service'].unique())]
        Path("evaluation_plots").mkdir(exist_ok=True)
        
        # Calculate weighted metrics once
        self._calculate_weighted_metrics()
    def _calculate_weighted_metrics(self):
        """Calculate weighted metrics for each service."""
        self.weighted_metrics = {}
        
        for service in self.df['service'].unique():
            service_df = self.df[self.df['service'] == service]
            
           
        
            # Calculate quality score
            quality_score = float(
                    0.25 * service_df['success_rate'].mean() +
                    0.35 * service_df['query_relevance'].mean() +
                    0.40 * service_df['response_completeness'].mean()
                ) * 100
                
            # Calculate scientific score
            scientific_score = float(
                    0.33 * service_df['scientific_structure'].mean() +
                    0.33 * service_df['academic_rigor'].mean() +
                    0.33 * service_df['technical_depth'].mean()
                ) * 100
                
            # Calculate performance and reliability scores
            performance_score = float(1 - (1.0 / (1.0 + service_df['latency'].mean()))) * 100
            reliability_score =  float(0.3* service_df["scientific_structure"].mean()+0.5*service_df["academic_rigor"].mean()+ 0.2*service_df["query_relevance"].mean()) *100
                
            self.weighted_metrics[service] = {
                    'Overall Quality': quality_score,
                    'Scientific Rigor': scientific_score,
                    'Performance Score': performance_score,
                    'Reliability': reliability_score
                }

    
    def create_main_dashboard(self):
        """Create main dashboard with all key metrics."""
        # Set better default style
        plt.rcParams['axes.facecolor'] = '#f0f0f0'
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['grid.color'] = '#cccccc'
        
        fig = plt.figure(figsize=(20, 15))
        gs = plt.GridSpec(3, 3, figure=fig)
        
        # 1. Aggregate Scores (Top Left)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_aggregate_scores(ax1)
        
        # 2. Radar Plot (Top Center)
        ax2 = fig.add_subplot(gs[0, 1], projection='polar')
        self._plot_radar(ax2)
        
        # 3. Cost-Benefit Analysis (Top Right)
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_cost_benefit(ax3)
        
        # 4. Performance Timeline (Middle Row)
        ax4 = fig.add_subplot(gs[1, :])
        self._plot_performance_timeline(ax4)
        
        # 5. Quality Metrics (Bottom Left)
        ax5 = fig.add_subplot(gs[2, 0])
        self._plot_quality_metrics(ax5)
        
        # 6. Scientific Metrics (Bottom Center)
        ax6 = fig.add_subplot(gs[2, 1])
        self._plot_scientific_metrics(ax6)
        
        # 7. Success Metrics (Bottom Right)
        ax7 = fig.add_subplot(gs[2, 2])
        self._plot_success_metrics(ax7)
        
        fig.suptitle('AI Research Assistant Performance Analysis', fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/main_dashboard_{self.timestamp}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_aggregate_scores(self, ax):
        """Plot aggregate scores for each service."""
        metrics = ['Overall Quality', 'Scientific Rigor', 'Performance Score', 'Reliability']
        x = np.arange(len(metrics))
        
        # Calculate width based on number of services
        n_services = len(self.weighted_metrics)
        width = 0.8 / n_services
        
        # Plot bars for each service
        for i, (service, scores) in enumerate(self.weighted_metrics.items()):
            # Convert values to floats, handling different formats
            values = []
            for metric in metrics:
                value = scores.get(metric, 0)
                values.append(value)

            # Convert to numpy array after ensuring all values are floats
            values = np.array(values, dtype=np.float64)
            
            # Create bars
            ax.bar(x + i * width,
                values,
                width,
                label=service,
                color=self.colors[i % len(self.colors)])
        
        # Customize plot
        ax.set_title('Aggregate Scores')
        ax.set_xticks(x + width * (n_services - 1) / 2)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        ax.set_ylabel('Score (%)')
        ax.set_ylim(0, 100)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_radar(self, ax):
        """Create radar plot for key metrics."""
        metrics = [
            'Response Time',
            'Overall Quality',
            'Scientific Rigor',
            'Performance Score',
            'Reliability'
        ]
        
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            scores = self.weighted_metrics[service]
            
            # Calculate response time score (inverse, since lower is better)
            response_time = float(service_df['latency'].quantile(0.95))
            response_score = max(0, min(100, 100 * (1 - response_time/10)))

            values = [
                response_score,
                scores['Overall Quality'],
                scores['Scientific Rigor'],
                scores['Performance Score'],
                scores['Reliability']
            ]
            values = np.concatenate((values, [values[0]]))


            ax.plot(angles, values, 'o-', linewidth=2, label=service, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 100)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

    def _plot_cost_benefit(self, ax):
        """Create enhanced cost-benefit analysis plot."""
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            scores = self.weighted_metrics[service]
            
            # Calculate benefit as weighted average of all scores
            benefit = (
                0.3 * scores['Overall Quality'] +
                0.3 * scores['Scientific Rigor'] +
                0.15 * scores['Performance Score'] +
                0.25 * scores['Reliability']
            )
            
            # Cost metric (price)
            cost = service_df['price'].mean()
            
            # Plot with size based on reliability
            size = 100 + scores['Reliability'] * 2
            scatter = ax.scatter(cost, benefit, s=size, label=service, color=color, alpha=0.7)
            
            # Add annotation
            ax.annotate(
                f"{service}\nQuality: {scores['Overall Quality']:.1f}%\n"
                f"Scientific: {scores['Scientific Rigor']:.1f}%\n"
                f"Performance: {scores['Performance Score']:.1f}%",
                (cost, benefit),
                xytext=(10, 10),
                textcoords='offset points',
                bbox=dict(facecolor='white', alpha=0.8)
            )
        
        ax.set_xlabel('Cost per Request ($)')
        ax.set_ylabel('Weighted Benefit Score (%)')
        ax.set_title('Cost-Benefit Analysis')
        ax.grid(True, alpha=0.3)
        ax.legend()

    def _plot_performance_timeline(self, ax):
        """Plot performance metrics over time."""
        metrics = {
            'Response Time': lambda x: x['latency'],
            'Success Rate': lambda x: x['success_rate'] * 100,
            'Quality Score': lambda x: (
                0.25 * x['success_rate'] +
                0.35 * x['query_relevance'] +
                0.40 * x['response_completeness']
            ) * 100
        }
        
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service].copy()
            service_df = service_df.sort_values('latency')  # Sort for better visualization
            runs = range(1, len(service_df) + 1)
            
            for metric_name, metric_func in metrics.items():
                try:
                    values = metric_func(service_df)
                    linestyle = '--' if metric_name != 'Response Time' else '-'
                    ax.plot(runs, values, label=f'{service} - {metric_name}',
                           color=color, marker='o', linestyle=linestyle, alpha=0.7)
                except Exception as e:
                    print(f"Couldn't plot {metric_name} for {service}: {e}")
        
        ax.set_title('Performance Metrics Over Time')
        ax.set_xlabel('Run Number')
        ax.set_ylabel('Value')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

    def _plot_quality_metrics(self, ax):
        """Plot quality metrics."""
        metrics = ['success_rate', 'query_relevance', 'response_completeness']
        labels = ['Success Rate', 'Query Relevance', 'Completeness']
        
        x = np.arange(len(metrics))
        width = 0.8 / len(self.df['service'].unique())
        
        for i, service in enumerate(self.df['service'].unique()):
            values = []
            for metric in metrics:
                try:
                    values.append(self.df[self.df['service'] == service][metric].mean() * 100)
                except Exception as e:
                    print(f"Couldn't calculate {metric} for {service}: {e}")
                    values.append(0)
            ax.bar(x + i*width, values, width, label=service, color=self.colors[i])
        
        ax.set_title('Quality Metrics')
        ax.set_xticks(x + width*(len(self.df['service'].unique())-1)/2)
        ax.set_xticklabels(labels, rotation=45)
        ax.set_ylabel('Score (%)')
        ax.set_ylim(0, 100)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_scientific_metrics(self, ax):
        """Plot scientific metrics."""
        metrics = ['scientific_structure', 'academic_rigor', 'technical_depth']
        labels = ['Structure', 'Academic Rigor', 'Technical Depth']
        
        x = np.arange(len(metrics))
        width = 0.8 / len(self.df['service'].unique())
        
        for i, service in enumerate(self.df['service'].unique()):
            values = []
            for metric in metrics:
                try:
                    values.append(self.df[self.df['service'] == service][metric].mean() * 100)
                except Exception as e:
                    print(f"Couldn't calculate {metric} for {service}: {e}")
                    values.append(0)
            ax.bar(x + i*width, values, width, label=service, color=self.colors[i])
        
        ax.set_title('Scientific Metrics')
        ax.set_xticks(x + width*(len(self.df['service'].unique())-1)/2)
        ax.set_xticklabels(labels, rotation=45)
        ax.set_ylabel('Score (%)')
        ax.set_ylim(0, 100)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_success_metrics(self, ax):
        """Plot success metrics."""
        metrics = {
            'Success Rate': lambda x: x['success_rate'].mean() * 100,
            'Quality Score': lambda x: x['response_completeness'].mean() * 50 + x['response_completeness'].mean() * 50,
            'Reliability': lambda x: x['scientific_structure'].mean() * 30 +x['academic_rigor'].mean() * 50+ x['query_relevance'].mean() * 20
        }
        
        x = np.arange(len(metrics))
        width = 0.8 / len(self.df['service'].unique())
        
        for i, service in enumerate(self.df['service'].unique()):
            service_df = self.df[self.df['service'] == service]
            values = []
            for metric_func in metrics.values():
                try:
                    values.append(metric_func(service_df))
                except Exception as e:
                    print(f"Couldn't calculate metric for {service}: {e}")
                    values.append(0)
            ax.bar(x + i*width, values, width, label=service, color=self.colors[i])
        
        ax.set_title('Success Metrics')
        ax.set_xticks(x + width*(len(self.df['service'].unique())-1)/2)
        ax.set_xticklabels(metrics.keys(), rotation=45)
        ax.set_ylabel('Score (%)')
        ax.set_ylim(0, 100)
        ax.legend()
        ax.grid(True, alpha=0.3)

class ScientificBenchmarkDashboard:
    def __init__(self, df: pd.DataFrame, timestamp: str):
        self.df = df
        self.timestamp = timestamp
        self.colors = ['#08519c',  # Dark Blue
                        '#3182bd',  # Medium Blue
                        '#6baed6',  # Light Blue
                        '#bdd7e7'   # Very Light Blue
                        ][:len(df['service'].unique())]
        
        Path("evaluation_plots").mkdir(exist_ok=True)
        
        # Define metric groups
        self.metrics = {
            'Quality': ['success_rate', 'query_relevance', 'response_completeness'],
            'Scientific': ['scientific_structure', 'academic_rigor', 'technical_depth'],
            'Performance': ['latency', 'tokens_per_second']
        }
        
    def create_benchmark_dashboard(self):
        """Generate comprehensive scientific benchmarking visualization."""
        fig = plt.figure(figsize=(20, 15))
        gs = plt.GridSpec(3, 2, figure=fig)
        
        # 1. Performance Metrics (Top Left)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_performance_metrics(ax1)
        
        # 2. Scientific Metrics vs Latency (Top Right)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_scientific_latency_tradeoff(ax2)
        
        # 3. Quality Analysis (Middle Left)
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_quality_analysis(ax3)
        
        # 4. Scientific Analysis (Middle Right)
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_scientific_analysis(ax4)
        
        # 5. Comparative Analysis (Bottom)
        ax5 = fig.add_subplot(gs[2, :], projection='polar')
        self._plot_comparative_analysis(ax5)
        
        plt.suptitle('Scientific Benchmark Analysis', fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/scientific_benchmark_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_performance_metrics(self, ax):
        """Plot performance metrics distribution."""
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Plot latency distribution
            sns.kdeplot(service_df['latency'], 
                       ax=ax, color=color, label=f"{service} - Latency")
            
            # Plot tokens per second
            sns.kdeplot(service_df['tokens_per_second'],
                       ax=ax, color=color, linestyle='--', 
                       label=f"{service} - Tokens/s")
        
        ax.set_xlabel('Value (Latency in seconds / Tokens per second)')
        ax.set_ylabel('Density')
        ax.set_title('Performance Metrics Distribution')
        ax.legend(bbox_to_anchor=(1.05, 1))
        ax.grid(True, alpha=0.3)

    def _plot_scientific_latency_tradeoff(self, ax):
        """Plot scientific metrics vs latency tradeoff."""
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Calculate weighted scientific score
            scientific_score = (
                0.33 * service_df['scientific_structure'].mean() +
                0.33 * service_df['academic_rigor'].mean() +
                0.34 * service_df['technical_depth'].mean()
            ) * 100
            
            latency = service_df['latency']
            
            # Plot scatter with confidence interval
            ax.scatter(latency, [scientific_score] * len(latency),
                      c=color, label=service, alpha=0.6, s=100)
            
            # Add confidence interval
            if len(service_df) > 2:
                confidence_ellipse(
                    latency.values,
                    np.array([scientific_score] * len(latency)),
                    ax, n_std=2.0, facecolor=color, alpha=0.1
                )
        
        ax.set_xlabel('Latency (seconds)')
        ax.set_ylabel('Scientific Score (%)')
        ax.set_title('Scientific Performance Trade-off')
        ax.legend(bbox_to_anchor=(1.05, 1))
        ax.grid(True, alpha=0.3)

    def _plot_quality_analysis(self, ax):
        """Plot quality metrics comparison."""
        metrics = self.metrics['Quality']
        labels = ['Success Rate', 'Query Relevance', 'Response Completeness']
        
        x = np.arange(len(metrics))
        width = 0.8 / len(self.df['service'].unique())
        
        for i, service in enumerate(self.df['service'].unique()):
            service_df = self.df[self.df['service'] == service]
            values = [service_df[m].mean() * 100 for m in metrics]
            ax.bar(x + i*width, values, width, label=service, color=self.colors[i])
        
        ax.set_xticks(x + width * (len(self.df['service'].unique()) - 1) / 2)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylabel('Score (%)')
        ax.set_ylim(0, 100)
        ax.set_title('Quality Metrics Comparison')
        ax.legend(bbox_to_anchor=(1.05, 1))
        ax.grid(True, alpha=0.3)

    def _plot_scientific_analysis(self, ax):
        """Plot scientific metrics comparison."""
        metrics = self.metrics['Scientific']
        labels = ['Structure', 'Academic Rigor', 'Technical Depth']
        
        x = np.arange(len(metrics))
        width = 0.8 / len(self.df['service'].unique())
        
        for i, service in enumerate(self.df['service'].unique()):
            service_df = self.df[self.df['service'] == service]
            values = [service_df[m].mean() * 100 for m in metrics]
            ax.bar(x + i*width, values, width, label=service, color=self.colors[i])
        
        ax.set_xticks(x + width * (len(self.df['service'].unique()) - 1) / 2)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylabel('Score (%)')
        ax.set_ylim(0, 100)
        ax.set_title('Scientific Metrics Comparison')
        ax.legend(bbox_to_anchor=(1.05, 1))
        ax.grid(True, alpha=0.3)

    def _plot_comparative_analysis(self, ax):
        """Create radar plot for comprehensive metric comparison."""
        metrics = [
            'Success Rate',
            'Scientific Rigor',
            'Technical Depth',
            'Response Speed',
            'Quality Score'
        ]
        
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Calculate composite scores
            values = [
                service_df['success_rate'].mean() * 100,
                (0.33 * service_df['scientific_structure'].mean() +
                 0.33 * service_df['academic_rigor'].mean() +
                 0.34 * service_df['technical_depth'].mean()) * 100,
                service_df['technical_depth'].mean() * 100,
                100 * (1 / (1 + service_df['latency'].mean())),  # Response speed
                (0.4 * service_df['success_rate'].mean() +
                 0.3 * service_df['query_relevance'].mean() +
                 0.3 * service_df['response_completeness'].mean()) * 100
            ]
            values = np.concatenate((values, [values[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2, label=service, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 100)
        ax.set_title('Comprehensive Metric Comparison')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        # Add circular gridlines
        ax.set_rticks([20, 40, 60, 80, 100])
        ax.grid(True, alpha=0.3)

class MetricsVisualizer:
    """Class for creating intuitive visualizations of metrics and tradeoffs."""
    
    def __init__(self, df: pd.DataFrame, timestamp: str):
        self.df = df
        self.timestamp = timestamp
        self.colors = sns.color_palette("husl", n_colors=len(df['service'].unique()))
        Path("evaluation_plots").mkdir(exist_ok=True)
        
        # Set better default style
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = '#f8f9fa'
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['grid.color'] = '#cccccc'
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 13

    def calculate_metrics(self, service_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate all key metrics for a service."""
        metrics = {
            'quality': (0.25 * service_df['success_rate'].mean() +
                       0.35 * service_df['query_relevance'].mean() +
                       0.40 * service_df['response_completeness'].mean()) * 100,
            
            'technical': (0.3 * service_df['technical_depth'].mean() +
                        0.5 * service_df['academic_rigor'].mean() +
                        0.2 * service_df['scientific_structure'].mean()) * 100,
            
            'reliability': (0.5 * service_df['academic_rigor'].mean() +
                          0.2 * service_df['scientific_structure'].mean() +
                          0.3 * service_df['query_relevance'].mean()) * 100,
            
            'speed': 100 * (1 / (1 + service_df['latency'].mean())),
            
            'cost_efficiency': 100 * (1 / (1 + service_df['price'].mean() * 1000)),
            
            'cost': service_df['price'].mean() * 1000  # Convert to millicents
        }
        return metrics

    def create_visualizations(self):
        """Create all visualizations."""
        # Create main figure with subplots
        fig = plt.figure(figsize=(20, 15))
        gs = plt.GridSpec(2, 2)
        
        # 1. Bubble Chart: Cost-Quality-Technical
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_bubble_tradeoff(ax1)
        
        # 2. Spider/Radar Chart: Key Metrics
        ax2 = fig.add_subplot(gs[0, 1], projection='polar')
        self._plot_spider_metrics(ax2)
        
        # 3. Stacked Bar: Metric Composition
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_stacked_metrics(ax3)
        
        # 4. Tradeoff Matrix
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_tradeoff_matrix(ax4)
        
        plt.suptitle('Metrics Tradeoff Analysis', fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/metrics_analysis_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_bubble_tradeoff(self, ax):
        """Create bubble chart showing cost vs quality with technical score as size."""
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            metrics = self.calculate_metrics(service_df)
            
            # Plot bubble with size based on technical score
            size = 500 * (metrics['technical']/100)
            scatter = ax.scatter(metrics['cost'], metrics['quality'], 
                               s=size, color=color, alpha=0.6,
                               label=f'{service}\nTech: {metrics["technical"]:.1f}%')
            
            # Add label
            ax.annotate(service,
                       (metrics['cost'], metrics['quality']),
                       xytext=(10, 10),
                       textcoords='offset points')
        
        ax.set_title('Cost-Quality Tradeoff\n(Bubble size indicates Technical Score)')
        ax.set_xlabel('Cost (millicents per request)')
        ax.set_ylabel('Quality Score (%)')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1))

    def _plot_spider_metrics(self, ax):
        """Create spider/radar chart for key metrics."""
        metrics = ['Quality', 'Technical', 'Reliability', 'Speed', 'Cost-Efficiency']
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            metrics_values = self.calculate_metrics(service_df)
            
            values = [
                metrics_values['quality'],
                metrics_values['technical'],
                metrics_values['reliability'],
                metrics_values['speed'],
                metrics_values['cost_efficiency']
            ]
            values = np.concatenate((values, [values[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2, label=service, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 100)
        ax.set_title('Metrics Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

    def _plot_stacked_metrics(self, ax):
        """Create stacked bar chart showing metric composition."""
        services = self.df['service'].unique()
        metrics = {
            'Academic': 'academic_rigor',
            'Technical': 'technical_depth',
            'Structure': 'scientific_structure',
            'Relevance': 'query_relevance',
            'Completeness': 'response_completeness'
        }
        
        bottoms = np.zeros(len(services))
        width = 0.8
        
        for metric_name, column in metrics.items():
            values = [self.df[self.df['service'] == service][column].mean() * 100 
                     for service in services]
            ax.bar(services, values, width, bottom=bottoms, label=metric_name)
            bottoms += values
        
        ax.set_title('Metric Composition by Service')
        ax.set_ylabel('Score (%)')
        ax.grid(True, alpha=0.3)
        ax.legend()

    def _plot_tradeoff_matrix(self, ax):
        """Create tradeoff matrix visualization."""
        services = self.df['service'].unique()
        n_services = len(services)
        
        # Calculate metrics for all services
        service_metrics = {
            service: self.calculate_metrics(self.df[self.df['service'] == service])
            for service in services
        }
        
        # Create tradeoff matrix
        matrix = np.zeros((n_services, n_services))
        for i, service1 in enumerate(services):
            for j, service2 in enumerate(services):
                if i != j:
                    # Calculate tradeoff score
                    s1, s2 = service_metrics[service1], service_metrics[service2]
                    
                    # Higher score means service1 is better
                    score = 0
                    score += (s1['quality'] - s2['quality']) / 100
                    score += (s1['technical'] - s2['technical']) / 100
                    score -= (s1['cost'] - s2['cost']) / (max(m['cost'] for m in service_metrics.values()))
                    
                    matrix[i, j] = score
        
        # Plot heatmap
        im = ax.imshow(matrix, cmap='RdYlBu')
        
        # Add labels
        ax.set_xticks(range(n_services))
        ax.set_yticks(range(n_services))
        ax.set_xticklabels(services)
        ax.set_yticklabels(services)
        
        plt.colorbar(im, ax=ax, label='Tradeoff Score')
        ax.set_title('Service Tradeoff Matrix\n(Higher score means row service better than column)')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

def create_query_performance_breakdown(df: pd.DataFrame, timestamp: str):
    """
    Create query-specific performance breakdown with Easy/Hard query labeling.
    First query is Easy, second query is Hard.
    
    Args:
        df: DataFrame containing evaluation results
        timestamp: Timestamp string for file naming
    """
    plt.figure(figsize=(15, 6))
    
    # Get unique queries and order them (First query = Easy, Second query = Hard)
    queries = df['query'].unique()
    query_order = sorted(queries)  # This ensures consistent ordering
    query_labels = ['Easy Query', 'Hard Query']  # First is Easy, Second is Hard
    
    x = np.arange(len(query_order))
    width = 0.35
    
    # Plot bars for each service
    for i, service in enumerate(df['service'].unique()):
        service_df = df[df['service'] == service]
        response_times = [
            service_df[service_df['query'] == query]['latency'].mean()
            for query in query_order
        ]
        
        # Create bars with service-specific styling
        bars = plt.bar(x + i*width, 
                      response_times, 
                      width, 
                      label=service,
                      alpha=0.8)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}s',
                    ha='center', va='bottom')
    
    # Customize plot
    plt.xlabel('Query Type', fontsize=12)
    plt.ylabel('Average Response Time (seconds)', fontsize=12)
    plt.title('Query Performance Comparison: Easy vs Hard Queries', fontsize=14, pad=20)
    
    # Set x-axis labels to Easy/Hard
    plt.xticks(x + width/2, query_labels, rotation=0, fontsize=11)
    
    # Add legend with custom styling
    plt.legend(title='Services', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Add grid for better readability
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save plot
    plt.savefig(f'evaluation_plots/query_performance_{timestamp}.png', 
                bbox_inches='tight', 
                dpi=300)
    plt.close()

def create_detailed_performance_visualization(df: pd.DataFrame, timestamp: str):
    """
    Creates a detailed performance visualization including latency statistics.
    First query is Easy, second query is Hard.
    
    Args:
        df: DataFrame containing evaluation results
        timestamp: Timestamp string for file naming
    """
    plt.figure(figsize=(15, 8))
    
    # Create subplot grid
    gs = plt.GridSpec(2, 2, height_ratios=[2, 1])
    
    # 1. Query Response Time Comparison (main plot)
    ax1 = plt.subplot(gs[0, :])
    
    # Get queries in correct order
    queries = df['query'].unique()
    query_order = sorted(queries)  # Ensure consistent ordering
    query_labels = ['Easy Query', 'Hard Query']  # First is Easy, Second is Hard
    
    x = np.arange(len(queries))
    width = 0.35
    
    for i, service in enumerate(df['service'].unique()):
        service_df = df[df['service'] == service]
        response_times = [
            service_df[service_df['query'] == query]['latency'].mean()
            for query in query_order
        ]
        
        bars = ax1.bar(x + i*width, response_times, width, label=service)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}s',
                    ha='center', va='bottom')
    
    ax1.set_ylabel('Response Time (seconds)')
    ax1.set_title('Query Response Time Comparison')
    ax1.set_xticks(x + width/2)
    ax1.set_xticklabels(query_labels)
    ax1.legend(title='Services')
    ax1.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # 2. Statistical Metrics (bottom left)
    ax2 = plt.subplot(gs[1, 0])
    
    for i, service in enumerate(df['service'].unique()):
        service_df = df[df['service'] == service]
        metrics = {
            'Min': service_df['latency'].min(),
            'Max': service_df['latency'].max(),
            'P95': service_df['latency'].quantile(0.95)
        }
        
        x_pos = np.arange(len(metrics))
        ax2.bar(x_pos + i*width, metrics.values(), width, label=service)
        
    ax2.set_xticks(x_pos + width/2)
    ax2.set_xticklabels(metrics.keys())
    ax2.set_title('Latency Statistics')
    ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # 3. Tokens per Second (bottom right)
    ax3 = plt.subplot(gs[1, 1])
    
    for i, service in enumerate(df['service'].unique()):
        service_df = df[df['service'] == service]
        tokens_per_second = service_df.apply(
            lambda row: len(str(row['answer'])) / row['latency'] 
            if row['latency'] > 0 else 0, axis=1
        ).mean()
        
        ax3.bar([i], [tokens_per_second], label=service)
        
    ax3.set_xticks(range(len(df['service'].unique())))
    ax3.set_xticklabels(df['service'].unique())
    ax3.set_title('Average Tokens per Second')
    ax3.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f'evaluation_plots/detailed_performance_{timestamp}.png', 
                bbox_inches='tight', 
                dpi=300)
    plt.close()

def generate_comprehensive_dashboard(df: pd.DataFrame, timestamp: str):
    """Generate all visualizations for the business dashboard."""
    # Create output directory
    Path("evaluation_plots").mkdir(exist_ok=True)
    
    # Generate all plots
 
    create_query_performance_breakdown(df, timestamp)
   
    create_detailed_performance_visualization(df, timestamp)
    
    
    generator = DashboardGenerator(df, timestamp)
    generator.create_main_dashboard()
    

    stat_generator = StatisticalDashboardGenerator(df, timestamp)
    stat_generator.create_statistical_dashboard()
    
    
    sci_generator = ScientificBenchmarkDashboard(df, timestamp)
    sci_generator.create_benchmark_dashboard()
    
    
    tradeoff_analyzer = ServiceTradeoffAnalyzer(df, timestamp)
    tradeoff_analyzer.analyze_tradeoffs()

    # Create visualizer and generate all plots
    visualizer = MetricsVisualizer(df, timestamp)
    visualizer.create_visualizations()


