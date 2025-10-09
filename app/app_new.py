"""
Lumia Robo-Advisor - Modern Component-Based UI
"""

import streamlit as st
import sys
import os

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database import get_db
from roboadvisor.user_profile import build_user_profile
from roboadvisor.recommender import generate_recommendation

# Import components
from components import (
    metric_card, section_header, create_donut_chart, create_bar_chart,
    create_score_distribution, create_risk_return_gauge, chat_message
)
from styles import get_main_styles
from chat_ai import LumiaAI

# Page config
st.set_page_config(
    page_title="Lumia Investment Management",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply styles
st.markdown(get_main_styles(), unsafe_allow_html=True)


def format_currency(amount):
    """Format currency in Indian style"""
    if amount >= 10000000:
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


def render_portfolio_table(asset_type: str, assets: list):
    """Render asset table with proper data"""
    if not assets:
        return
    
    st.markdown(f"### {asset_type.replace('_', ' ').title()}")
    
    table_html = '<table class="data-table"><thead><tr>'
    table_html += '<th>Symbol</th><th>Name</th><th>Allocation</th><th>Percentage</th><th>Score</th><th>Sector</th>'
    table_html += '</tr></thead><tbody>'
    
    for asset in assets:
        # Get values with defaults - using correct field names
        symbol = asset.get("symbol", "N/A")
        name = asset.get("name", "Unknown")[:45]
        amount = asset.get("allocation_amount", asset.get("amount", 0))
        percentage = asset.get("allocation_percentage", asset.get("percentage", 0)) * 100
        score = asset.get("score", 0)
        sector = asset.get("sector", "N/A")[:25]
        
        table_html += '<tr>'
        table_html += f'<td><strong style="color: #2563eb !important;">{symbol}</strong></td>'
        table_html += f'<td style="color: #111827 !important;">{name}</td>'
        table_html += f'<td><strong style="color: #111827 !important;">{format_currency(amount)}</strong></td>'
        table_html += f'<td style="color: #111827 !important;">{percentage:.2f}%</td>'
        table_html += f'<td><span style="color: #16a34a !important; font-weight: 600;">{score:.1f}/100</span></td>'
        table_html += f'<td style="color: #6b7280 !important;">{sector}</td>'
        table_html += '</tr>'
    
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def main():
    # Initialize session state
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'lumia_ai' not in st.session_state:
        st.session_state.lumia_ai = LumiaAI()
    
    # Header
    st.markdown("""
    <div class="app-header">
        <h1>LUMIA INVESTMENT MANAGEMENT</h1>
        <p>AI-Powered Portfolio Management & Advisory Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration Section
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(section_header("Portfolio Configuration", "Configure your investment preferences"), unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        capital = st.number_input(
            "💰 Investment Capital (₹)",
            min_value=10000,
            max_value=100000000,
            value=100000,
            step=10000,
            help="Minimum investment: ₹10,000"
        )
    
    with col2:
        risk_level = st.selectbox(
            "📊 Risk Tolerance",
            ["Conservative (20%)", "Moderate (50%)", "Aggressive (75%)", "Very Aggressive (90%)"],
            index=1
        )
        risk_map = {
            "Conservative (20%)": 20,
            "Moderate (50%)": 50,
            "Aggressive (75%)": 75,
            "Very Aggressive (90%)": 90
        }
        risk_score = risk_map[risk_level]
    
    with col3:
        years = st.selectbox(
            "⏱️ Time Horizon (Years)",
            [1, 2, 3, 5, 7, 10, 15, 20, 25, 30],
            index=4
        )
    
    with col4:
        target_return = st.number_input(
            "🎯 Expected Growth (%/year)",
            min_value=1.0,
            max_value=1000.0,
            value=12.0,
            step=0.5,
            help="Target annual return percentage"
        )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_btn = st.button("Generate Portfolio", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate Portfolio
    if generate_btn:
        with st.spinner("Analyzing market data and building your portfolio..."):
            try:
                db = next(get_db())
                
                profile = build_user_profile(
                    capital=capital,
                    risk_score=risk_score,
                    years=years,
                    expected_return=target_return/100
                )
                
                result = generate_recommendation(db, profile, optimize=True)
                st.session_state.portfolio = result
                
                st.success("✅ Portfolio generated successfully!")
                db.close()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display Results
    if st.session_state.portfolio:
        result = st.session_state.portfolio
        profile = result['profile']
        metrics = result['metrics']
        portfolio = result['portfolio']
        
        # Metrics Cards
        st.markdown(section_header("Portfolio Overview", "Key performance metrics"), unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(metric_card("Portfolio Value", format_currency(profile['capital']), color="#2563eb"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(metric_card("Total Assets", str(result.get('total_assets', 0)), color="#16a34a"), unsafe_allow_html=True)
        
        with col3:
            st.markdown(metric_card("Expected Return", f"{metrics['expected_return']*100:.2f}%", delta=f"+{metrics['expected_return']*100:.1f}%", color="#2563eb"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(metric_card("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}", color="#16a34a"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts Section
        st.markdown(section_header("Visual Analysis", "Interactive portfolio visualizations"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            donut_fig = create_donut_chart(portfolio, "Asset Allocation")
            if donut_fig:
                st.plotly_chart(donut_fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("No allocation data available")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            bar_fig = create_bar_chart(portfolio, "Holdings by Asset Type")
            if bar_fig:
                st.plotly_chart(bar_fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("No holdings data available")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Risk/Return Gauges
        col1, col2, col3 = st.columns(3)
        
        fig_return, fig_risk, fig_sharpe = create_risk_return_gauge(
            metrics['expected_return'],
            metrics['expected_risk'],
            metrics['sharpe_ratio']
        )
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.plotly_chart(fig_return, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.plotly_chart(fig_risk, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.plotly_chart(fig_sharpe, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Score Distribution
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        score_fig = create_score_distribution(portfolio)
        if score_fig:
            st.plotly_chart(score_fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Portfolio Holdings
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(section_header("Portfolio Holdings", "Detailed breakdown of all investments"), unsafe_allow_html=True)
        
        for asset_type, assets in portfolio.items():
            if assets:
                render_portfolio_table(asset_type, assets)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat Section
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(section_header("AI Portfolio Assistant", "Get personalized insights and answers"), unsafe_allow_html=True)
        
        # Display chat history first
        if st.session_state.chat_history:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for msg in st.session_state.chat_history[-10:]:
                st.markdown(chat_message(msg['content'], msg['role'] == 'user'), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input at bottom
        user_input = st.text_input(
            "Ask me anything about your portfolio:", 
            placeholder="e.g., Why this allocation? What if I invest in single stock?", 
            key="chat_input"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            send_btn = st.button("💬 Send", use_container_width=True)
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        if send_btn and user_input:
            # Add user message
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            
            # Generate AI response using Lumia AI
            response = st.session_state.lumia_ai.analyze_question(user_input, result)
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
