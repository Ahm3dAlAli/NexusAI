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
    def __init__(self, df: pd.DataFrame, timestamp: str):
        self.df = df
        self.timestamp = timestamp
        self.colors = sns.color_palette("husl", n_colors=len(df['service'].unique()))
        Path("evaluation_plots").mkdir(exist_ok=True)
        
        self.metric_classes = {
            'Quality': ['quality_paper_coverage', 'quality_temporal_accuracy', 'quality_response_completeness'],
            'Scientific': ['scientific_citation_quality', 'scientific_technical_depth', 'scientific_academic_rigor'],
            'Performance': ['latency', 'performance_tokens_per_second']
        }

    def analyze_tradeoffs(self):
        """Generate comprehensive tradeoff analysis visualizations."""
        # 1. Multi-dimensional tradeoff plot
        self._plot_multidimensional_tradeoff()
        
        # 2. Radar chart for metric classes
        self._plot_class_radar()
        
        # 3. Statistical comparison within classes
        self._plot_intraclass_comparison()

    def _plot_multidimensional_tradeoff(self):
        """Create enhanced multi-dimensional tradeoff visualization."""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Define colormap
        cmap = plt.cm.RdYlBu

        # Fixed latency boundaries
        max_latency = 10
        mid_latency = 5

        # Create the regions with legend
        handles = []
        handles.append(ax.axvspan(0, mid_latency, ymin=0.5, ymax=1, alpha=0.1, color='green', label='Optimal Region'))
        handles.append(ax.axvspan(mid_latency, max_latency, ymin=0.5, ymax=1, alpha=0.1, color='yellow', label='Scientific Focus Region'))
        handles.append(ax.axvspan(0, mid_latency, ymin=0, ymax=0.5, alpha=0.1, color='yellow', label='Speed Focus Region'))
        handles.append(ax.axvspan(mid_latency, max_latency, ymin=0, ymax=0.5, alpha=0.1, color='red', label='Improvement Needed Region'))

        # Plot data points for each service
        service_points = []
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            latency = service_df['latency'].mean()
            scientific_score = np.mean([service_df[col].mean() * 100 
                                      for col in self.metric_classes['Scientific']])
            
            # Plot point and add to legend handles
            point = ax.scatter(latency, scientific_score, 
                             s=300,
                             c=[color],
                             alpha=0.7,
                             label=f'{service}')
            service_points.append(point)

        # Add quadrant text without boxes
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
        
        # Add gridlines
        ax.grid(True, alpha=0.3)
        
        # Create two separate legends
        # Region legend (top right)
        region_legend = ax.legend(handles, 
                                ['Optimal Region', 'Scientific Focus Region', 
                                 'Speed Focus Region', 'Improvement Needed Region'],
                                loc='upper right',
                                title='Performance Regions',
                                bbox_to_anchor=(1.15, 1))
        
        # Add the first legend back
        ax.add_artist(region_legend)
        
        # Service legend (lower right)
        service_legend = ax.legend(service_points,
                                 [p.get_label() for p in service_points],
                                 loc='lower right',
                                 title='Services',
                                 bbox_to_anchor=(1.15, 0))
        
        # Set axis limits
        ax.set_xlim(0, max_latency)
        ax.set_ylim(0, 100)

        # Add vertical line at latency cutoff
        ax.axvline(x=mid_latency, color='gray', linestyle='--', alpha=0.5)
        
        # Adjust layout to prevent text cutoff
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/multidim_tradeoff_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_class_radar(self):
        """Create intuitive radar chart comparing metric classes."""
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, projection='polar')

        class_names = ['Quality\n(Higher Better)', 
                      'Scientific Rigor\n(Higher Better)', 
                      'Latency \n(Lower Better)']  # Changed from Speed
        angles = np.linspace(0, 2*np.pi, len(class_names), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)

        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Calculate normalized metrics
            quality_score = np.mean([service_df[m].mean() * 100 
                                   for m in self.metric_classes['Quality']])
            scientific_score = np.mean([service_df[m].mean() * 100 
                                      for m in self.metric_classes['Scientific']])
            # Invert latency score since lower is better
            latency_score = 100 * (1 / (1 + service_df['latency'].mean()))
            
            values = [quality_score, scientific_score, latency_score]
            values = np.concatenate((values, [values[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2, label=service, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(class_names)
        ax.set_ylim(0, 100)
        
        # Add circular gridlines with labels
        ax.set_rticks([20, 40, 60, 80, 100])
        ax.text(0, 110, 'Service Performance Overview', 
               ha='center', va='center', fontsize=14)
        
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1),
                  title='Services')

        """Create intuitive radar chart comparing metric classes."""
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, projection='polar')

        class_names = ['Quality\n(Higher Better)', 
                      'Scientific Rigor\n(Higher Better)', 
                      'Latency\n(Higher Better)']
        angles = np.linspace(0, 2*np.pi, len(class_names), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)

        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Calculate normalized metrics
            quality_score = np.mean([service_df[m].mean() * 100 
                                   for m in self.metric_classes['Quality']])
            scientific_score = np.mean([service_df[m].mean() * 100 
                                      for m in self.metric_classes['Scientific']])
            speed_score = 100 * (1 / (1 + service_df['latency'].mean()))
            
            values = [quality_score, scientific_score, speed_score]
            values = np.concatenate((values, [values[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2, label=service, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(class_names)
        ax.set_ylim(0, 100)
        
        # Add circular gridlines with labels
        ax.set_rticks([20, 40, 60, 80, 100])
        ax.text(0, 110, 'Performance Overview', 
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
            
            # Prepare data for boxplot
            plot_data = []
            labels = []
            for metric in metrics:
                for service in self.df['service'].unique():
                    service_df = self.df[self.df['service'] == service]
                    values = service_df[metric].copy()
                    if 'latency' not in metric:
                        values = values * 100
                    plot_data.append(values)
                    labels.append(f"{service}\n{metric.split('_')[-1]}")
            
            # Create enhanced boxplot
            bp = ax.boxplot(plot_data, labels=labels, patch_artist=True)
            
            # Color boxes by service
            for i, service in enumerate(self.df['service'].unique()):
                for j in range(len(metrics)):
                    box_idx = i * len(metrics) + j
                    bp['boxes'][box_idx].set_facecolor(self.colors[i])
                    bp['boxes'][box_idx].set_alpha(0.6)
            
            # Add statistical significance
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
            
            # Add explanation of significance
            if idx == 0:
                ax.text(0.98, 0.98, 
                       'Significance: *** p<0.001, ** p<0.01, * p<0.05, ns: not significant',
                       transform=ax.transAxes, ha='right', va='top',
                       bbox=dict(facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig(f'evaluation_plots/intraclass_comparison_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()


    def __init__(self, df: pd.DataFrame, timestamp: str):
        self.df = df
        self.timestamp = timestamp
        self.colors = sns.color_palette("husl", n_colors=len(df['service'].unique()))
        Path("evaluation_plots").mkdir(exist_ok=True)
        self.metrics = {
            'quality': ['quality_paper_coverage', 'quality_temporal_accuracy', 'quality_response_completeness'],
            'scientific': ['scientific_citation_quality', 'scientific_technical_depth', 'scientific_academic_rigor'],
            'performance': ['latency', 'performance_tokens_per_second']
        }
        
    def create_statistical_dashboard(self):
        """Create comprehensive statistical analysis dashboard."""
        fig = plt.figure(figsize=(20, 15))
        gs = plt.GridSpec(3, 2, figure=fig)
        
        # 1. T-Test Results (Top Left)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_ttest_results(ax1)
        
        # 2. Correlation Matrix (Top Right)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_correlation_matrix(ax2)
        
        # 3. Cost-Benefit Trade-offs (Middle Row)
        ax3 = fig.add_subplot(gs[1, :])
        self._plot_tradeoff_analysis(ax3)
        
        # 4. Distribution Analysis (Bottom Left)
        ax4 = fig.add_subplot(gs[2, 0])
        self._plot_distribution_analysis(ax4)
        
        # 5. Statistical Summary (Bottom Right)
        ax5 = fig.add_subplot(gs[2, 1])
        self._plot_statistical_summary(ax5)
        
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/statistical_dashboard_{self.timestamp}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_ttest_results(self, ax):
        """Plot t-test results between services for key metrics."""
        services = list(self.df['service'].unique())
        if len(services) < 2:
            ax.text(0.5, 0.5, 'Need at least 2 services\nfor statistical comparison',
                   ha='center', va='center')
            return
            
        results = []
        for metric in ['quality_paper_coverage', 'latency', 'scientific_technical_depth']:
            service1_data = self.df[self.df['service'] == services[0]][metric]
            service2_data = self.df[self.df['service'] == services[1]][metric]
            
            t_stat, p_val = stats.ttest_ind(service1_data, service2_data)
            results.append({
                'metric': metric.split('_')[-1].title(),
                'p_value': p_val,
                'significant': p_val < 0.05,
                't_statistic': t_stat
            })
        
        y_pos = np.arange(len(results))
        p_values = [-np.log10(r['p_value']) for r in results]
        
        ax.barh(y_pos, p_values)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([r['metric'] for r in results])
        ax.axvline(-np.log10(0.05), color='r', linestyle='--', label='p=0.05 threshold')
        ax.set_xlabel('-log10(p-value)')
        ax.set_title('Statistical Significance of Service Differences')
        ax.legend()

    def _plot_correlation_matrix(self, ax):
        """Plot correlation matrix between metrics."""
        metrics = ['latency', 'quality_paper_coverage', 'scientific_technical_depth',
                  'performance_tokens_per_second']
        
        corr_data = self.df[metrics].corr()
        sns.heatmap(corr_data, annot=True, cmap='coolwarm', ax=ax)
        ax.set_title('Metric Correlations')
        plt.xticks(rotation=45)

    def _plot_tradeoff_analysis(self, ax):
        """Plot trade-off analysis between different metrics."""
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            quality = service_df['quality_paper_coverage'].mean() * 100
            latency = service_df['latency'].mean()
            tokens_per_sec = service_df['performance_tokens_per_second'].mean()
            
            size = np.pi * (tokens_per_sec / 10) ** 2
            ax.scatter(latency, quality, s=size, label=service, color=color, alpha=0.6)
            
        ax.set_xlabel('Latency (s)')
        ax.set_ylabel('Quality Score (%)')
        ax.set_title('Quality-Latency Trade-off\n(bubble size represents tokens/sec)')
        ax.legend()
        ax.grid(True)

    def _plot_distribution_analysis(self, ax):
        """Plot distribution analysis for key metrics."""
        metrics = ['latency', 'quality_paper_coverage']
        
        for metric in metrics:
            for service, color in zip(self.df['service'].unique(), self.colors):
                data = self.df[self.df['service'] == service][metric]
                if 'quality' in metric:
                    data = data * 100
                sns.kdeplot(data=data, ax=ax, label=f'{service} - {metric}', color=color)
        
        ax.set_title('Metric Distributions')
        ax.legend()
        ax.grid(True)

    def _plot_statistical_summary(self, ax):
        """Plot statistical summary table."""
        summary_data = []
        
        for service in self.df['service'].unique():
            service_df = self.df[self.df['service'] == service]
            
            for metric_category, metric_list in self.metrics.items():
                for metric in metric_list:
                    if metric in service_df.columns:
                        data = service_df[metric]
                        if 'quality' in metric or 'scientific' in metric:
                            data = data * 100
                            
                        summary_data.append({
                            'Service': service,
                            'Metric': metric.split('_')[-1].title(),
                            'Mean': data.mean(),
                            'Std': data.std(),
                            'CV': data.std() / data.mean() if data.mean() != 0 else np.nan
                        })
        
        summary_df = pd.DataFrame(summary_data)
        ax.axis('off')
        table = ax.table(cellText=summary_df.values,
                        colLabels=summary_df.columns,
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        ax.set_title('Statistical Summary', pad=20)

    def create_advanced_analysis(self):
        """Create additional advanced statistical analysis plots."""
        #self._create_anova_analysis()
        #self._create_statistical_tests()

    def _create_anova_analysis(self):
        """Create ANOVA analysis plots."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Perform one-way ANOVA for quality scores across services
        quality_data = [group['quality_paper_coverage'].values * 100 
                       for name, group in self.df.groupby('service')]
        f_stat, p_val = stats.f_oneway(*quality_data)
        
        # Plot quality distributions
        sns.violinplot(data=self.df, x='service', y='quality_paper_coverage',
                      inner='box', ax=ax)
        ax.set_title(f'Quality Score Distribution by Service\nANOVA p-value: {p_val:.4f}')
        ax.set_ylabel('Quality Score')
        
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/anova_analysis_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _create_statistical_tests(self):
        """Create comprehensive statistical tests visualization."""
        results = []
        
        # Perform various statistical tests
        services = list(self.df['service'].unique())
        for metric in self.metrics['quality'] + self.metrics['performance']:
            if len(services) >= 2:
                # T-test
                service1_data = self.df[self.df['service'] == services[0]][metric]
                service2_data = self.df[self.df['service'] == services[1]][metric]
                t_stat, p_val = stats.ttest_ind(service1_data, service2_data)
                
                # Mann-Whitney U test
                u_stat, u_p_val = stats.mannwhitneyu(service1_data, service2_data, 
                                                    alternative='two-sided')
                
                results.append({
                    'Metric': metric,
                    'Test': 'T-test',
                    'Statistic': t_stat,
                    'pvalue': p_val  # Changed from 'P-value' to 'pvalue'
                })
                results.append({
                    'Metric': metric,
                    'Test': 'Mann-Whitney U',
                    'Statistic': u_stat,
                    'pvalue': u_p_val  # Changed from 'P-value' to 'pvalue'
                })
        
        # Create summary plot
        fig, ax = plt.subplots(figsize=(12, 8))
        results_df = pd.DataFrame(results)
        # Use 'pvalue' instead of 'P-value' in the scatter plot
        sns.scatterplot(data=results_df, x='pvalue', y='Metric', 
                    hue='Test', size='Statistic', ax=ax)
        ax.axvline(0.05, color='r', linestyle='--', label='p=0.05 threshold')
        ax.set_xscale('log')
        ax.set_title('Statistical Test Results')
        
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/statistical_tests_{self.timestamp}.png',
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
        
        self.metrics = {
            'Quality': ['quality_paper_coverage', 'quality_temporal_accuracy', 'quality_response_completeness'],
            'Scientific': ['scientific_citation_quality', 'scientific_technical_depth', 'scientific_academic_rigor'],
            'Performance': ['latency', 'performance_tokens_per_second']
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
        legend_elements = []
        
        for service in self.df['service'].unique():
            color = self.service_colors[service]
            
            for query in self.unique_queries:
                service_query_df = self.df[(self.df['service'] == service) & 
                                         (self.df['query'] == query)]
                
                if len(service_query_df) == 0:
                    continue
                
                # Calculate metrics
                quality = service_query_df['quality_paper_coverage'].mean() * 100
                latency = service_query_df['latency'].mean()
                scientific = service_query_df['scientific_technical_depth'].mean() * 100
                tokens_per_sec = service_query_df['performance_tokens_per_second'].mean()
                
                # Size based on processing speed
                size = 300 * (tokens_per_sec / self.df['performance_tokens_per_second'].max())
                
                # Plot main point
                marker = self.query_markers[query]
                scatter = ax.scatter(latency, scientific, 
                                   s=size, color=color, alpha=0.7,
                                   marker=marker,
                                   label=f'{service} - {self.query_labels[query]}')
                
                # Add confidence ellipse if enough points
                if len(service_query_df) > 2:
                    confidence_ellipse(
                        service_query_df['latency'].values,
                        service_query_df['scientific_technical_depth'].values * 100,
                        ax, n_std=2.0, facecolor=color, alpha=0.1
                    )
                
                # Annotate point
                ax.annotate(f'{service} {self.query_labels[query]}\nQuality: {quality:.1f}%\nLatency: {latency:.2f}s',
                           (latency, scientific),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(facecolor='white', alpha=0.8))

        # Create custom legend
        from matplotlib.lines import Line2D
        
        # Service legend
        service_legend = [Line2D([0], [0], marker='o', color='w', 
                               markerfacecolor=color, label=service, markersize=10)
                         for service, color in self.service_colors.items()]
        
        # Query type legend
        query_legend = [Line2D([0], [0], marker=self.query_markers[query], color='black', 
                             label=f'{self.query_labels[query]}: {query[:30]}...' if len(query) > 30 else query,
                             markersize=10)
                       for query in self.unique_queries]
        
        # Add both legends
        leg1 = ax.legend(handles=service_legend, title='Services', 
                        bbox_to_anchor=(1.05, 1))
        ax.add_artist(leg1)
        ax.legend(handles=query_legend, title='Queries',
                 bbox_to_anchor=(1.05, 0.5))
        
        ax.set_xlabel('Response Latency (seconds) - Lower is Better →')
        ax.set_ylabel('Scientific Quality (%) - Higher is Better →')
        ax.set_title('Service Performance Tradeoff Analysis')
        ax.grid(True, alpha=0.2)

    def _plot_statistical_comparison(self, ax):
        """Plot enhanced statistical comparison."""
        services = list(self.df['service'].unique())
        if len(services) < 2:
            ax.text(0.5, 0.5, 'Need multiple services for comparison',
                   ha='center', va='center')
            return
        
        metrics = ['Response Latency', 'Scientific Quality', 'Processing Speed']
        data = []
        
        for metric in metrics:
            if metric == 'Response Latency':
                stat = stats.ttest_ind(
                    self.df[self.df['service'] == services[0]]['latency'],
                    self.df[self.df['service'] == services[1]]['latency']
                )
            elif metric == 'Scientific Quality':
                stat = stats.ttest_ind(
                    self.df[self.df['service'] == services[0]]['scientific_technical_depth'] * 100,
                    self.df[self.df['service'] == services[1]]['scientific_technical_depth'] * 100
                )
            else:
                stat = stats.ttest_ind(
                    self.df[self.df['service'] == services[0]]['performance_tokens_per_second'],
                    self.df[self.df['service'] == services[1]]['performance_tokens_per_second']
                )
            
            data.append({
                'Metric': metric,
                'p_value': -np.log10(stat.pvalue),
                'significant': stat.pvalue < 0.05
            })
        
        # Create bar plot
        bars = ax.barh([d['Metric'] for d in data],
                      [d['p_value'] for d in data],
                      color=[self.colors[0] if d['significant'] else '#cccccc' for d in data])
        
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
        metrics = {
            'Response Time': 'latency',
            'Scientific Quality': 'scientific_technical_depth',
            'Processing Speed': 'performance_tokens_per_second',
            'Overall Quality': 'quality_paper_coverage'
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
        linestyles = ['-', '--', ':', '-.', '-']  # different line styles for queries
        
        for service in self.df['service'].unique():
            color = self.service_colors[service]
            
            for i, query in enumerate(self.unique_queries):
                service_query_df = self.df[(self.df['service'] == service) & 
                                         (self.df['query'] == query)]
                
                if len(service_query_df) == 0:
                    continue
                
                # Plot latency distribution
                sns.kdeplot(data=service_query_df['latency'], ax=ax, 
                          color=color, linestyle=linestyles[i],
                          label=f'{service} - {self.query_labels[query]}', alpha=0.7)
                
                # Add mean marker
                mean_latency = service_query_df['latency'].mean()
                ax.axvline(mean_latency, color=color, linestyle=linestyles[i], alpha=0.5)
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
    return ax.add_patch(ellipse)

class DashboardGenerator:
    """Generates comprehensive evaluation dashboards."""
    
    def __init__(self, df: pd.DataFrame, timestamp: str):

        self.df = df
        self.timestamp = timestamp
        self.colors = ['#08519c', '#3182bd', '#6baed6', '#bdd7e7'][:len(df['service'].unique())]
        Path("evaluation_plots").mkdir(exist_ok=True)
        self.calculate_aggregate_metrics()
        
        # Pre-calculate common metrics
        self.calculate_aggregate_metrics()

    def calculate_aggregate_metrics(self):
        """Calculate aggregate metrics for each service."""
        self.aggregates = {}
        
        for service in self.df['service'].unique():
            service_df = self.df[self.df['service'] == service]
            
            self.aggregates[service] = {
                'Overall Quality': np.mean([
                    service_df['quality_paper_coverage'].mean() * 100,
                    service_df['quality_temporal_accuracy'].mean() * 100,
                    service_df['quality_response_completeness'].mean() * 100
                ]),
                'Scientific Rigor': np.mean([
                    service_df['scientific_citation_quality'].mean() * 100,
                    service_df['scientific_scientific_structure'].mean() * 100,
                    service_df['scientific_technical_depth'].mean() * 100,
                    service_df['scientific_academic_rigor'].mean() * 100
                ]),
                'Performance Score': 100 * (1 / (1 + service_df['latency'].mean())),
                'Tokens/Second': service_df['performance_tokens_per_second'].mean(),
                'Reliability': service_df['success'].mean() * 100
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
        
        # Add overall title
        fig.suptitle('AI Research Assistant Performance Analysis', fontsize=16, y=1.02)
        
        # Adjust layout
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/main_dashboard_{self.timestamp}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_aggregate_scores(self, ax):
        """Plot aggregate scores for each service."""
        metrics = ['Overall Quality', 'Scientific Rigor', 'Performance Score', 'Reliability']
        
        x = np.arange(len(metrics))
        width = 0.35
        
        for i, service in enumerate(self.aggregates.keys()):
            values = [self.aggregates[service][m] for m in metrics]
            ax.bar(x + i*width, values, width, label=service, color=self.colors[i])
        
        ax.set_title('Aggregate Scores')
        ax.set_xticks(x + width/2)
        ax.set_xticklabels(metrics, rotation=45)
        ax.set_ylabel('Score (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_radar(self, ax):
        """Create radar plot for key metrics."""
        metrics = [
            'Paper Coverage',
            'Citation Quality',
            'Technical Depth',
            'Response Time',
            'Tokens/Second'
        ]
        
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            values = [
                service_df['quality_paper_coverage'].mean() * 100,
                service_df['scientific_citation_quality'].mean() * 100,
                service_df['scientific_technical_depth'].mean() * 100,
                100 * (1 / (1 + service_df['latency'].mean())),
                min(100, service_df['performance_tokens_per_second'].mean() / 10)
            ]
            values = np.concatenate((values, [values[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2, label=service, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 100)

    def _plot_cost_benefit(self, ax):
        """Create cost-benefit analysis plot."""
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            benefit = np.mean([
                service_df['quality_paper_coverage'].mean() * 100,
                service_df['scientific_citation_quality'].mean() * 100,
                service_df['scientific_technical_depth'].mean() * 100
            ])
            
            tokens_per_second = service_df['performance_tokens_per_second'].mean()
            
            ax.scatter(tokens_per_second, benefit, s=200, label=service, color=color)
            ax.annotate(service, (tokens_per_second, benefit), 
                       xytext=(10, 10), textcoords='offset points')
        
        ax.set_xlabel('Tokens per Second')
        ax.set_ylabel('Quality Score (%)')
        ax.set_title('Cost-Benefit Analysis')
        ax.grid(True)
        ax.legend()

    def _create_metric_dashboard(self, metrics, title, transform_funcs=None):
        """Create a dashboard for a specific category of metrics."""
        if transform_funcs is None:
            transform_funcs = {}

        fig, axes = plt.subplots(2, 1, figsize=(15, 12))
        
        # Box plots
        plot_data = []
        for metric in ['performance_latency','performance_tokens_per_second','success']:

            for service in self.df['service'].unique():

                service_data = self.df[self.df['service'] == service][metric]
                if metric in transform_funcs:
                    service_data = transform_funcs[metric](service_data)
                plot_data.append({
                    'Service': service,
                    'Metric': metric.split('_')[-1].replace('_', ' ').title(),
                    'Value': service_data.mean()
                })
        
        plot_df = pd.DataFrame(plot_data)
        sns.boxplot(data=plot_df, x='Metric', y='Value', hue='Service', ax=axes[0])
        axes[0].set_title(f'{title} Metrics Distribution')
        
        # Time series
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            for metric in ['performance_latency','performance_tokens_per_second','success']:
                data = service_df[metric]
                if metric in transform_funcs:
                    data = transform_funcs[metric](data)
                axes[1].plot(range(len(data)), data, 
                           label=f'{service} - {metric.split("_")[-1].title()}',
                           color=color, marker='o', linestyle='--')
        
        axes[1].set_title(f'{title} Metrics Over Time')
        axes[1].set_xlabel('Run Number')
        axes[1].set_ylabel('Value')
        axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/{title.lower()}_dashboard_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_performance_timeline(self, ax):
        """Plot performance metrics over time."""
        metrics = {
            'Response Time': lambda x: x['latency'],
            'Tokens/Second': lambda x: x['performance_tokens_per_second'],
            'Quality': lambda x: x['quality_paper_coverage'] * 100
        }
        
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            runs = range(1, len(service_df) + 1)
            
            for metric_name, metric_func in metrics.items():
                try:
                    values = metric_func(service_df)
                    label = f'{service} - {metric_name}'
                    ax.plot(runs, values, label=label, color=color, 
                        marker='o', linestyle='--' if metric_name != 'Response Time' else '-')
                except Exception as e:
                    print(f"Couldn't plot {metric_name} for {service}: {e}")
        
        ax.set_title('Performance Metrics Over Time')
        ax.set_xlabel('Run Number')
        ax.set_ylabel('Value')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

    def _plot_quality_metrics(self, ax):
        """Plot quality metrics."""
        metrics = ['paper_coverage', 'temporal_accuracy', 'response_completeness']
        x = np.arange(len(metrics))
        width = 0.35
        
        for i, service in enumerate(self.df['service'].unique()):
            values = []
            for metric in metrics:
                try:
                    col = f'quality_{metric}'
                    values.append(self.df[self.df['service'] == service][col].mean() * 100)
                except Exception as e:
                    print(f"Couldn't calculate {metric} for {service}: {e}")
                    values.append(0)
            ax.bar(x + i*width, values, width, label=service, color=self.colors[i])
        
        ax.set_title('Quality Metrics')
        ax.set_xticks(x + width/2)
        ax.set_xticklabels(['Coverage', 'Accuracy', 'Completeness'])
        ax.set_ylabel('Score (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_scientific_metrics(self, ax):
        """Plot scientific metrics."""
        metrics = ['citation_quality', 'scientific_structure', 'technical_depth', 'academic_rigor']
        x = np.arange(len(metrics))
        width = 0.35
        
        for i, service in enumerate(self.df['service'].unique()):
            values = []
            for metric in metrics:
                try:
                    col = f'scientific_{metric}'
                    values.append(self.df[self.df['service'] == service][col].mean() * 100)
                except Exception as e:
                    print(f"Couldn't calculate {metric} for {service}: {e}")
                    values.append(0)
            ax.bar(x + i*width, values, width, label=service, color=self.colors[i])
        
        ax.set_title('Scientific Metrics')
        ax.set_xticks(x + width/2)
        ax.set_xticklabels(['Citations', 'Structure', 'Technical', 'Academic'])
        ax.set_ylabel('Score (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_success_metrics(self, ax):
        """Plot success metrics."""
        metrics = {
            'Success Rate': lambda x: x['success'].mean() * 100,
            'Completion': lambda x: 100 - (x['error_count'].mean() * 10),
            'Quality Score': lambda x: x['quality_paper_coverage'].mean() * 100
        }
        
        x = np.arange(len(metrics))
        width = 0.35
        
        for i, service in enumerate(self.df['service'].unique()):
            service_df = self.df[self.df['service'] == service]
            values = []
            for metric_func in metrics.values():
                try:
                    values.append(metric_func(service_df))
                except Exception as e:
                    values.append(0)
            ax.bar(x + i*width, values, width, label=service, color=self.colors[i])
        
        ax.set_title('Success Metrics')
        ax.set_xticks(x + width/2)
        ax.set_xticklabels(metrics.keys())
        ax.set_ylabel('Score (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)

class ScientificBenchmarkDashboard:
    def __init__(self, df: pd.DataFrame, timestamp: str):
        self.df = df
        self.timestamp = timestamp
        self.colors = sns.color_palette("husl", n_colors=len(df['service'].unique()))
        Path("evaluation_plots").mkdir(exist_ok=True)
        
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
        
        plt.tight_layout()
        plt.savefig(f'evaluation_plots/scientific_benchmark_{self.timestamp}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_performance_metrics(self, ax):
        """Plot performance metrics."""
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            # Plot latency distribution
            sns.kdeplot(service_df['performance_latency'], 
                       ax=ax, color=color, label=f"{service} - Latency")
            
            # Plot tokens per second
            sns.kdeplot(service_df['performance_tokens_per_second'],
                       ax=ax, color=color, linestyle='--', 
                       label=f"{service} - Tokens/s")
            
        ax.set_xlabel('Value')
        ax.set_ylabel('Density')
        ax.set_title('Performance Metrics Distribution')
        ax.legend()
        ax.grid(True)

    def _plot_scientific_latency_tradeoff(self, ax):
        """Plot scientific metrics vs latency."""
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            
            scientific_score = np.mean([
                service_df['scientific_citation_quality'],
                service_df['scientific_academic_rigor'],
                service_df['scientific_technical_depth']
            ], axis=0) * 100
            
            ax.scatter(service_df['performance_latency'], scientific_score,
                      c=color, label=service, alpha=0.6, s=100)
            
        ax.set_xlabel('Latency (s)')
        ax.set_ylabel('Scientific Score (%)')
        ax.set_title('Scientific Performance Trade-off')
        ax.legend()
        ax.grid(True)

    def _plot_quality_analysis(self, ax):
        """Plot quality metrics comparison."""
        metrics = ['quality_paper_coverage', 'quality_temporal_accuracy', 
                  'quality_response_completeness']
        metric_labels = ['Paper Coverage', 'Temporal Accuracy', 'Completeness']
        
        x = np.arange(len(metrics))
        width = 0.35
        
        for i, service in zip(range(len(self.df['service'].unique())), 
                            self.df['service'].unique()):
            service_df = self.df[self.df['service'] == service]
            values = [service_df[m].mean() * 100 for m in metrics]
            ax.bar(x + i*width, values, width, label=service)
        
        ax.set_xticks(x + width/2)
        ax.set_xticklabels(metric_labels)
        ax.set_ylabel('Score (%)')
        ax.set_title('Quality Metrics Comparison')
        ax.legend()
        ax.grid(True)

    def _plot_scientific_analysis(self, ax):
        """Plot scientific metrics comparison."""
        metrics = ['scientific_citation_quality', 'scientific_technical_depth',
                  'scientific_academic_rigor']
        metric_labels = ['Citation', 'Technical', 'Academic']
        
        x = np.arange(len(metrics))
        width = 0.35
        
        for i, service in zip(range(len(self.df['service'].unique())), 
                            self.df['service'].unique()):
            service_df = self.df[self.df['service'] == service]
            values = [service_df[m].mean() * 100 for m in metrics]
            ax.bar(x + i*width, values, width, label=service)
        
        ax.set_xticks(x + width/2)
        ax.set_xticklabels(metric_labels)
        ax.set_ylabel('Score (%)')
        ax.set_title('Scientific Metrics Comparison')
        ax.legend()
        ax.grid(True)

    def _plot_comparative_analysis(self, ax):
        """Create radar plot for key metrics."""
        metrics = [
            'Paper Coverage',
            'Citation Quality',
            'Technical Depth',
            'Response Time',
            'Tokens/Second'
        ]
        
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        for service, color in zip(self.df['service'].unique(), self.colors):
            service_df = self.df[self.df['service'] == service]
            values = [
                service_df['quality_paper_coverage'].mean() * 100,
                service_df['scientific_citation_quality'].mean() * 100,
                service_df['scientific_technical_depth'].mean() * 100,
                100 * (1 / (1 + service_df['latency'].mean())),
                min(100, service_df['performance_tokens_per_second'].mean() / 10)
            ]
            values = np.concatenate((values, [values[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2, label=service, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 100)
        ax.set_title('Core Metrics Comparison')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

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
