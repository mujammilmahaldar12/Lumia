"""
Reusable UI Components for Lumia Robo-Advisor
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any


def metric_card(label: str, value: str, delta: str = None, color: str = "#2563eb"):
    """Reusable metric card component"""
    delta_html = f'<div style="color: #16a34a; font-size: 0.875rem; margin-top: 0.5rem;">↑ {delta}</div>' if delta else ''
    
    return f"""
    <div style="
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'" 
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 1px 3px rgba(0,0,0,0.1)'">
        <div style="font-size: 0.75rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
            {label}
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: {color}; line-height: 1;">
            {value}
        </div>
        {delta_html}
    </div>
    """


def section_header(title: str, subtitle: str = None):
    """Section header component"""
    subtitle_html = f'<p style="color: #6b7280; font-size: 0.9375rem; margin: 0.5rem 0 0 0;">{subtitle}</p>' if subtitle else ''
    
    return f"""
    <div style="margin-bottom: 2rem;">
        <h2 style="font-size: 1.5rem; font-weight: 700; color: #111827; margin: 0;">
            {title}
        </h2>
        {subtitle_html}
    </div>
    """


def create_donut_chart(portfolio: Dict, title: str = "Asset Allocation"):
    """Create interactive donut chart"""
    labels = []
    values = []
    colors = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe']
    
    for asset_type, assets in portfolio.items():
        if assets:
            total = sum(a.get('allocation_amount', a.get('amount', 0)) for a in assets)
            if total > 0:
                labels.append(asset_type.replace('_', ' ').title())
                values.append(total)
    
    if not values:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(
            colors=colors[:len(labels)],
            line=dict(color='white', width=3)
        ),
        textfont=dict(size=14, family='Inter', color='#111827'),
        textposition='outside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#111827', family='Inter')),
        showlegend=False,
        height=400,
        margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter', size=13, color='#111827')
    )
    
    return fig


def create_bar_chart(portfolio: Dict, title: str = "Asset Count by Type"):
    """Create bar chart for asset counts"""
    asset_types = []
    counts = []
    colors = []
    
    color_map = {
        'stocks': '#2563eb',
        'etf': '#3b82f6',
        'mutual_funds': '#60a5fa',
        'crypto': '#93c5fd',
        'bonds': '#dbeafe'
    }
    
    for asset_type, assets in portfolio.items():
        if assets:
            asset_types.append(asset_type.replace('_', ' ').title())
            counts.append(len(assets))
            colors.append(color_map.get(asset_type, '#2563eb'))
    
    if not asset_types:
        return None
    
    fig = go.Figure(data=[go.Bar(
        x=asset_types,
        y=counts,
        marker=dict(color=colors, line=dict(color='white', width=2)),
        text=counts,
        textposition='outside',
        textfont=dict(size=14, color='#111827', family='Inter'),
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#111827', family='Inter')),
        xaxis=dict(
            title=dict(text='Asset Type', font=dict(size=13)), 
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(text='Number of Holdings', font=dict(size=13)), 
            tickfont=dict(size=12)
        ),
        height=350,
        margin=dict(t=60, b=60, l=60, r=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter', color='#111827'),
        showlegend=False
    )
    
    return fig


def create_score_distribution(portfolio: Dict):
    """Create score distribution chart"""
    all_scores = []
    all_types = []
    
    for asset_type, assets in portfolio.items():
        for asset in assets:
            all_scores.append(asset.get('score', 0))
            all_types.append(asset_type.replace('_', ' ').title())
    
    if not all_scores:
        return None
    
    fig = go.Figure(data=[go.Box(
        y=all_scores,
        x=all_types,
        marker=dict(color='#2563eb'),
        boxmean='sd',
        name='Score Distribution'
    )])
    
    fig.update_layout(
        title=dict(text='Asset Quality Scores', font=dict(size=16, color='#111827', family='Inter')),
        xaxis=dict(title=dict(text='Asset Type', font=dict(size=13))),
        yaxis=dict(title=dict(text='Score (out of 100)', font=dict(size=13)), range=[0, 100]),
        height=350,
        margin=dict(t=60, b=60, l=60, r=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter', color='#111827'),
        showlegend=False
    )
    
    return fig


def create_risk_return_gauge(expected_return: float, expected_risk: float, sharpe_ratio: float):
    """Create gauge charts for risk/return metrics"""
    
    # Return gauge
    fig_return = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=expected_return * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Expected Return", 'font': {'size': 16, 'color': '#111827'}},
        number={'suffix': "%", 'font': {'size': 28, 'color': '#2563eb'}},
        gauge={
            'axis': {'range': [0, 30], 'tickwidth': 1, 'tickcolor': "#111827"},
            'bar': {'color': "#2563eb"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e5e7eb",
            'steps': [
                {'range': [0, 8], 'color': '#fee2e2'},
                {'range': [8, 15], 'color': '#fef3c7'},
                {'range': [15, 30], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "#16a34a", 'width': 4},
                'thickness': 0.75,
                'value': 20
            }
        }
    ))
    
    fig_return.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font={'family': 'Inter', 'color': '#111827'},
        height=250,
        margin=dict(t=60, b=20, l=20, r=20)
    )
    
    # Risk gauge
    fig_risk = go.Figure(go.Indicator(
        mode="gauge+number",
        value=expected_risk * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Portfolio Risk", 'font': {'size': 16, 'color': '#111827'}},
        number={'suffix': "%", 'font': {'size': 28, 'color': '#dc2626'}},
        gauge={
            'axis': {'range': [0, 40], 'tickwidth': 1, 'tickcolor': "#111827"},
            'bar': {'color': "#dc2626"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e5e7eb",
            'steps': [
                {'range': [0, 12], 'color': '#d1fae5'},
                {'range': [12, 25], 'color': '#fef3c7'},
                {'range': [25, 40], 'color': '#fee2e2'}
            ],
        }
    ))
    
    fig_risk.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font={'family': 'Inter', 'color': '#111827'},
        height=250,
        margin=dict(t=60, b=20, l=20, r=20)
    )
    
    # Sharpe gauge
    fig_sharpe = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sharpe_ratio,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Sharpe Ratio", 'font': {'size': 16, 'color': '#111827'}},
        number={'font': {'size': 28, 'color': '#16a34a'}},
        gauge={
            'axis': {'range': [0, 3], 'tickwidth': 1, 'tickcolor': "#111827"},
            'bar': {'color': "#16a34a"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e5e7eb",
            'steps': [
                {'range': [0, 0.5], 'color': '#fee2e2'},
                {'range': [0.5, 1], 'color': '#fef3c7'},
                {'range': [1, 3], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "#16a34a", 'width': 4},
                'thickness': 0.75,
                'value': 1
            }
        }
    ))
    
    fig_sharpe.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font={'family': 'Inter', 'color': '#111827'},
        height=250,
        margin=dict(t=60, b=20, l=20, r=20)
    )
    
    return fig_return, fig_risk, fig_sharpe


def chat_message(content: str, is_user: bool = False):
    """Chat message component with markdown support"""
    # Convert markdown-like syntax to HTML
    import re
    
    if not is_user:
        # Bold text
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        # Bullet points
        content = content.replace('• ', '<br>• ')
        # Line breaks
        content = content.replace('\n', '<br>')
    
    if is_user:
        return f"""
        <div style="
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 16px;
            margin: 1rem 0 1rem auto;
            max-width: 75%;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
            font-size: 0.95rem;
        ">
            <div style="font-weight: 600; margin-bottom: 0.5rem; font-size: 0.8rem; opacity: 0.95; letter-spacing: 0.5px;">YOU</div>
            <div style="line-height: 1.6;">{content}</div>
        </div>
        """
    else:
        return f"""
        <div style="
            background: white;
            border: 2px solid #e5e7eb;
            color: #111827;
            padding: 1.25rem 1.5rem;
            border-radius: 16px;
            margin: 1rem auto 1rem 0;
            max-width: 90%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        ">
            <div style="font-weight: 700; margin-bottom: 0.75rem; font-size: 0.8rem; color: #2563eb; letter-spacing: 0.5px;">💡 LUMIA AI</div>
            <div style="line-height: 1.8; color: #1f2937; font-size: 0.95rem;">{content}</div>
        </div>
        """
