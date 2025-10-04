"""
Advanced Chart Components for Lumia Investment Advisor

This module contains enhanced chart components with better styling and interactivity.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any, Optional
import numpy as np

class ChartComponents:
    """Advanced chart components with enhanced styling"""
    
    @staticmethod
    def get_chart_theme():
        """Get consistent chart theme"""
        return {
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': '#e2e8f0', 'family': 'Inter, Poppins, sans-serif'},
            'margin': {'l': 40, 'r': 40, 't': 60, 'b': 40},
            'showlegend': True,
            'legend': {
                'bgcolor': 'rgba(255,255,255,0.05)',
                'bordercolor': 'rgba(255,255,255,0.1)',
                'borderwidth': 1,
                'font': {'color': '#e2e8f0'}
            }
        }
    
    @staticmethod
    def render_enhanced_pie_chart(data: Dict[str, float], title: str = "Distribution", 
                                 hole_size: float = 0.5, height: int = 400):
        """Enhanced pie chart with animations and better styling"""
        
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b']
        
        fig = go.Figure(data=[go.Pie(
            labels=list(data.keys()),
            values=list(data.values()),
            hole=hole_size,
            marker=dict(
                colors=colors[:len(data)],
                line=dict(color='rgba(255,255,255,0.2)', width=2)
            ),
            textfont=dict(size=14, color='white'),
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        # Add center text for donut charts
        if hole_size > 0:
            total_value = sum(data.values())
            fig.add_annotation(
                text=f"<b>Total</b><br>{total_value:.1f}",
                x=0.5, y=0.5,
                font=dict(size=16, color='#e2e8f0'),
                showarrow=False
            )
        
        theme = ChartComponents.get_chart_theme()
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, color='#667eea'), x=0.5),
            height=height,
            **theme,
            annotations=[
                dict(
                    text=f"<b>Total</b><br>{sum(data.values()):.1f}" if hole_size > 0 else "",
                    x=0.5, y=0.5,
                    font=dict(size=16, color='#e2e8f0'),
                    showarrow=False
                )
            ]
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    @staticmethod
    def render_growth_projection_chart(capital: float, years: int, annual_return: float, 
                                     title: str = "Portfolio Growth Projection"):
        """Enhanced growth projection chart with multiple scenarios"""
        
        years_range = list(range(0, years + 1))
        
        # Calculate different scenarios
        conservative_return = annual_return * 0.7
        optimistic_return = annual_return * 1.3
        
        conservative_values = [capital * (1 + conservative_return/100) ** year for year in years_range]
        normal_values = [capital * (1 + annual_return/100) ** year for year in years_range]
        optimistic_values = [capital * (1 + optimistic_return/100) ** year for year in years_range]
        
        fig = go.Figure()
        
        # Add optimistic scenario (fill area)
        fig.add_trace(go.Scatter(
            x=years_range + years_range[::-1],
            y=optimistic_values + conservative_values[::-1],
            fill='toself',
            fillcolor='rgba(102, 126, 234, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Projection Range',
            hoverinfo='skip'
        ))
        
        # Conservative scenario
        fig.add_trace(go.Scatter(
            x=years_range,
            y=conservative_values,
            mode='lines',
            name=f'Conservative ({conservative_return:.1f}%)',
            line=dict(color='#f5576c', width=2, dash='dot'),
            hovertemplate='Year %{x}<br>Value: ₹%{y:,.0f}<extra></extra>'
        ))
        
        # Normal scenario
        fig.add_trace(go.Scatter(
            x=years_range,
            y=normal_values,
            mode='lines+markers',
            name=f'Expected ({annual_return:.1f}%)',
            line=dict(color='#667eea', width=4),
            marker=dict(size=8, color='#667eea'),
            hovertemplate='Year %{x}<br>Value: ₹%{y:,.0f}<extra></extra>'
        ))
        
        # Optimistic scenario
        fig.add_trace(go.Scatter(
            x=years_range,
            y=optimistic_values,
            mode='lines',
            name=f'Optimistic ({optimistic_return:.1f}%)',
            line=dict(color='#48bb78', width=2, dash='dot'),
            hovertemplate='Year %{x}<br>Value: ₹%{y:,.0f}<extra></extra>'
        ))
        
        # Initial investment line
        fig.add_trace(go.Scatter(
            x=years_range,
            y=[capital] * len(years_range),
            mode='lines',
            name='Initial Investment',
            line=dict(color='rgba(255,255,255,0.5)', width=2, dash='dash'),
            hovertemplate='Initial: ₹%{y:,.0f}<extra></extra>'
        ))
        
        theme = ChartComponents.get_chart_theme()
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, color='#667eea'), x=0.5),
            xaxis=dict(
                title="Years",
                gridcolor='rgba(255,255,255,0.1)',
                color='#e2e8f0'
            ),
            yaxis=dict(
                title="Portfolio Value (₹)",
                gridcolor='rgba(255,255,255,0.1)',
                color='#e2e8f0',
                tickformat='₹,.0f'
            ),
            height=450,
            **theme
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    @staticmethod
    def render_risk_return_scatter(portfolio_data: List[Dict], title: str = "Risk vs Return Analysis"):
        """Enhanced risk-return scatter plot"""
        
        if not portfolio_data:
            return
        
        symbols = [item['stock'].symbol for item in portfolio_data]
        returns = [((item['stock'].target_price / item['stock'].current_price) - 1) * 100 
                  for item in portfolio_data]
        risks = [item['stock'].risk_score for item in portfolio_data]
        sizes = [item.get('allocation_percentage', 10) for item in portfolio_data]
        sectors = [item['stock'].sector for item in portfolio_data]
        
        # Color mapping for sectors
        sector_colors = {
            'Technology': '#667eea',
            'Banking': '#764ba2',
            'Healthcare': '#f093fb',
            'Energy': '#f5576c',
            'Manufacturing': '#4facfe'
        }
        colors = [sector_colors.get(sector, '#99a3b5') for sector in sectors]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=risks,
            y=returns,
            mode='markers+text',
            marker=dict(
                size=[s*2 for s in sizes],  # Scale bubble size
                color=colors,
                opacity=0.8,
                line=dict(width=2, color='rgba(255,255,255,0.3)')
            ),
            text=symbols,
            textposition='middle center',
            textfont=dict(color='white', size=10),
            hovertemplate='<b>%{text}</b><br>Risk: %{x:.1f}/5<br>Expected Return: %{y:.1f}%<extra></extra>'
        ))
        
        # Add quadrant lines
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig.add_vline(x=2.5, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        
        # Add quadrant labels
        fig.add_annotation(x=1.25, y=max(returns)*0.8, text="Low Risk<br>High Return", 
                          bgcolor="rgba(72,187,120,0.2)", font=dict(color="#48bb78"))
        fig.add_annotation(x=3.75, y=max(returns)*0.8, text="High Risk<br>High Return", 
                          bgcolor="rgba(255,193,7,0.2)", font=dict(color="#ffc107"))
        
        theme = ChartComponents.get_chart_theme()
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, color='#667eea'), x=0.5),
            xaxis=dict(
                title="Risk Score",
                range=[0, 5],
                gridcolor='rgba(255,255,255,0.1)',
                color='#e2e8f0'
            ),
            yaxis=dict(
                title="Expected Return (%)",
                gridcolor='rgba(255,255,255,0.1)',
                color='#e2e8f0'
            ),
            height=450,
            **theme
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    @staticmethod
    def render_gauge_chart(value: float, title: str, max_value: float = 100, 
                          color_ranges: List[Dict] = None):
        """Enhanced gauge chart for metrics like risk scores"""
        
        if color_ranges is None:
            color_ranges = [
                {'range': [0, 30], 'color': '#48bb78'},      # Green (Low)
                {'range': [30, 70], 'color': '#ffc107'},     # Yellow (Medium)  
                {'range': [70, 100], 'color': '#f56565'}     # Red (High)
            ]
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title, 'font': {'color': '#e2e8f0', 'size': 18}},
            number = {'font': {'color': '#667eea', 'size': 28}},
            gauge = {
                'axis': {'range': [None, max_value], 'tickcolor': '#e2e8f0'},
                'bar': {'color': '#667eea', 'thickness': 0.3},
                'bgcolor': 'rgba(255,255,255,0.1)',
                'borderwidth': 2,
                'bordercolor': 'rgba(255,255,255,0.2)',
                'steps': [
                    {'range': [cr['range'][0], cr['range'][1]], 'color': f"{cr['color']}33"}
                    for cr in color_ranges
                ],
                'threshold': {
                    'line': {'color': '#667eea', 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ))
        
        theme = ChartComponents.get_chart_theme()
        fig.update_layout(height=300, **theme)
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    @staticmethod
    def render_heatmap_correlation(correlation_data: Dict[str, Dict[str, float]], 
                                  title: str = "Asset Correlation Matrix"):
        """Enhanced correlation heatmap"""
        
        assets = list(correlation_data.keys())
        correlation_matrix = []
        
        for asset1 in assets:
            row = []
            for asset2 in assets:
                row.append(correlation_data[asset1].get(asset2, 0))
            correlation_matrix.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=assets,
            y=assets,
            colorscale=[
                [0, '#f56565'],     # Red for negative correlation
                [0.5, '#e2e8f0'],   # Light for no correlation
                [1, '#48bb78']      # Green for positive correlation
            ],
            zmid=0,
            text=correlation_matrix,
            texttemplate='%{text:.2f}',
            textfont={'color': 'white', 'size': 12},
            hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        theme = ChartComponents.get_chart_theme()
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, color='#667eea'), x=0.5),
            height=400,
            **theme
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Export chart components
PieChart = ChartComponents.render_enhanced_pie_chart
GrowthChart = ChartComponents.render_growth_projection_chart
RiskReturnScatter = ChartComponents.render_risk_return_scatter
GaugeChart = ChartComponents.render_gauge_chart
HeatmapChart = ChartComponents.render_heatmap_correlation