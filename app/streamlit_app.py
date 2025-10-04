import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Import enhanced components
try:
    from components.ui_components import UIComponents, MetricCard, StockCard, ProgressRing, ChatContainer, ChatMessage
    from components.chart_components import ChartComponents, PieChart, GrowthChart, RiskReturnScatter, GaugeChart
    from components.layout_components import LayoutComponents, DashboardGrid, TabbedInterface
    from components.enhanced_styles import get_enhanced_css
    
    # Initialize component instances
    ui_components = UIComponents()
    chart_components = ChartComponents()
    layout_components = LayoutComponents()
    
    components_available = True
except ImportError as e:
    print(f"Enhanced components import error: {e}")
    components_available = False

# Import analysis engine with error handling
try:
    from analysis_engine import LumiaAnalysisEngine as AnalysisEngine
    analysis_engine_available = True
except ImportError as e:
    print(f"Analysis engine import error: {e}")
    AnalysisEngine = None
    analysis_engine_available = False

# Session state initialization
def init_session_state():
    """Initialize session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

def create_fallback_analysis(capital, investment_time):
    """Create fallback analysis when engine fails"""
    return {
        'portfolio_metrics': {
            'expected_annual_return': 12.5,
            'projected_total_value': capital * (1.125 ** investment_time),
            'total_gain': capital * (1.125 ** investment_time) - capital,
            'portfolio_risk_score': 2.5,
            'sharpe_ratio': 2.4,
            'diversification_score': 7.5
        },
        'portfolio': [
            {
                'stock': type('Stock', (), {
                    'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services',
                    'sector': 'Technology', 'current_price': 3650.0,
                    'target_price': 4200.0, 'recommendation': 'BUY', 'risk_score': 2.1
                })(),
                'allocation_percentage': 25.0,
                'investment_amount': capital * 0.25
            }
        ],
        'investment_insights': ["Fallback portfolio created - please check system configuration"],
        'sector_allocation': {"Technology": 50, "Banking": 30, "Healthcare": 20},
        'risk_analysis': {'overall_risk_level': 'Moderate'},
        'input_params': {
            'capital': capital, 'investment_time': investment_time,
            'expected_growth': 12.5, 'domains': ['Technology'], 'risk_appetite': 'Moderate'
        }
    }

# Enhanced CSS for morphism UI styling
def load_enhanced_css():
    """Load enhanced CSS with all component styles"""
    if components_available:
        st.markdown(get_enhanced_css(), unsafe_allow_html=True)
    else:
        # Fallback CSS if components not available
        st.markdown("""
        <style>
        /* Fallback minimal styles */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #0c0c1e 0%, #1a1a2e 50%, #16213e 100%);
            font-family: 'Inter', 'Poppins', sans-serif;
        }
        
        .main-header {
            text-align: center;
            padding: 3.5rem 2rem;
            margin-bottom: 2rem;
            background: rgba(102, 126, 234, 0.08);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .main-title {
            font-size: 3.5rem;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            letter-spacing: -1px;
        }
        </style>
        """, unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles with dark morphism theme */
    .main {
        font-family: 'Inter', sans-serif;
        padding: 0rem 1rem;
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%);
        color: #ffffff;
        min-height: 100vh;
    }
    
    /* Header styles with professional padding */
    .main-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 3.5rem 2rem;
        border-radius: 24px;
        margin: 1rem 0 3rem 0;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3.5rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: -1px;
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        opacity: 0.95;
        font-weight: 400;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    /* Glassmorphism metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2.2rem;
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.25);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.95rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #e2e8f0;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    /* Investment form with glassmorphism */
    .investment-form {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    .form-section {
        margin-bottom: 2.5rem;
        padding: 2rem;
        background: rgba(102, 126, 234, 0.08);
        backdrop-filter: blur(15px);
        border-radius: 18px;
        border-left: 4px solid rgba(102, 126, 234, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .form-section h4 {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
    }
    
    /* Chat interface with glassmorphism */
    .chat-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .chat-message {
        background: rgba(102, 126, 234, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        max-width: 85%;
        color: #e2e8f0;
    }
    
    .user-message {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
        border: 1px solid rgba(102, 126, 234, 0.4);
        margin-left: auto;
    }
    
    .ai-message {
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.2), rgba(56, 161, 105, 0.2));
        border: 1px solid rgba(72, 187, 120, 0.3);
    }
    
    /* Stock analysis cards with glassmorphism */
    .stock-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
    }
    
    .stock-card:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Enhanced recommendation tags */
    .recommendation-tag {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .tag-buy { 
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.3), rgba(56, 161, 105, 0.3)); 
        color: #68d391;
        border: 1px solid rgba(72, 187, 120, 0.5);
    }
    .tag-hold { 
        background: linear-gradient(135deg, rgba(237, 137, 54, 0.3), rgba(221, 107, 32, 0.3)); 
        color: #f6ad55;
        border: 1px solid rgba(237, 137, 54, 0.5);
    }
    .tag-sell { 
        background: linear-gradient(135deg, rgba(245, 101, 101, 0.3), rgba(229, 62, 62, 0.3)); 
        color: #fc8181;
        border: 1px solid rgba(245, 101, 101, 0.5);
    }
    .tag-risk-low { 
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.3), rgba(56, 161, 105, 0.3)); 
        color: #68d391;
        border: 1px solid rgba(72, 187, 120, 0.5);
    }
    .tag-risk-medium { 
        background: linear-gradient(135deg, rgba(237, 137, 54, 0.3), rgba(221, 107, 32, 0.3)); 
        color: #f6ad55;
        border: 1px solid rgba(237, 137, 54, 0.5);
    }
    .tag-risk-high { 
        background: linear-gradient(135deg, rgba(245, 101, 101, 0.3), rgba(229, 62, 62, 0.3)); 
        color: #fc8181;
        border: 1px solid rgba(245, 101, 101, 0.5);
    }
    
    /* Quick action buttons with glassmorphism */
    .quick-action-btn {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.4);
        border-radius: 15px;
        padding: 1rem 1.5rem;
        color: white;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4));
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.6);
    }
    
    /* Progress indicators */
    .progress-container {
        background: rgba(226, 232, 240, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        overflow: hidden;
        margin: 1rem 0;
        height: 8px;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transition: width 0.5s ease;
        border-radius: 15px;
    }
    
    /* Animations */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .animate-slide-up {
        animation: slideInUp 0.6s ease-out;
    }
    
    .animate-fade-scale {
        animation: fadeInScale 0.5s ease-out;
    }
    
    .animate-scale {
        animation: scaleIn 0.4s ease-out;
    }
    
    @keyframes scaleIn {
        from { transform: scale(0.95); opacity: 0.8; }
        to { transform: scale(1); opacity: 1; }
    }
    
    /* Form styling with glassmorphism */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:focus-within {
        border: 1px solid rgba(102, 126, 234, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border: 1px solid rgba(102, 126, 234, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    .stRadio > div {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 1rem !important;
    }
    
    .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
    }
    
    .stSlider > div > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom button styling with glassmorphism */
    .stButton > button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4)) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(102, 126, 234, 0.5) !important;
        color: white !important;
        border-radius: 15px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2) !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.6), rgba(118, 75, 162, 0.6)) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        border: 1px solid rgba(102, 126, 234, 0.7) !important;
    .insight-card {
        background: rgba(102, 126, 234, 0.08);
        backdrop-filter: blur(15px);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border-left: 4px solid rgba(102, 126, 234, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
    }
    
    .chat-container {
        background: rgba(102, 126, 234, 0.08);
        backdrop-filter: blur(15px);
        border-radius: 18px;
        padding: 2rem;
        margin-top: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .chat-message {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 3px solid #667eea;
    }
    
    /* Chart container styling */
    .plotly-graph-div {
        background: rgba(102, 126, 234, 0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px) !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Lumia Investment Advisor",
        page_icon="�",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    load_enhanced_css()
    init_session_state()
    
    # Enhanced Professional Header
    if components_available:
        UIComponents.render_enhanced_header(
            title="Lumia Investment Advisor",
            subtitle="AI-Powered Investment Research & Portfolio Management Platform",
            background_gradient=True
        )
    else:
        # Fallback header
        st.markdown("""
        <div class="main-header animate-fade-scale">
            <h1 class="main-title">Lumia Investment Advisor</h1>
            <p class="main-subtitle">AI-Powered Investment Research & Portfolio Management Platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content layout
    col1, col2 = st.columns([1, 2])
    
    # Investment Parameters Form (Left Column)
    with col1:
        st.markdown("""
        <div class="investment-form animate-slide-up">
            <h2 style="text-align: center; margin-bottom: 2rem; color: #e2e8f0; font-weight: 600;">
                Investment Parameters
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Create form
        with st.form("investment_form", clear_on_submit=False):
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown("#### Capital & Returns")
            
            capital = st.number_input(
                "Investment Capital (₹)", 
                min_value=100, 
                max_value=50000000, 
                value=50000,
                step=1000,
                help="Enter your investment amount (minimum ₹100)"
            )
            
            expected_growth = st.slider(
                "Expected Annual Return (%)", 
                min_value=5, 
                max_value=30, 
                value=15,
                help="What return do you expect annually?"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown("#### Investment Timeline")
            
            investment_time = st.selectbox(
                "Investment Horizon",
                options=[1, 2, 3, 5, 7, 10, 15, 20],
                index=4,
                help="How long will you invest?"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown("#### Investment Preferences")
            
            domains = st.multiselect(
                "Preferred Sectors",
                options=['Technology', 'Healthcare', 'Finance', 'Energy', 'Manufacturing', 'Consumer'],
                default=['Technology', 'Healthcare'],
                help="Choose sectors you're interested in"
            )
            
            risk_appetite = st.radio(
                "Risk Profile",
                options=['Conservative', 'Moderate', 'Aggressive'],
                index=1,
                help="How much risk can you handle?"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Analysis button
            submitted = st.form_submit_button(
                "Analyze My Portfolio",
                type="primary",
                help="Generate AI-powered investment recommendations"
            )
            
            if submitted:
                with st.spinner("🤖 AI is analyzing market data..."):
                    time.sleep(2)  # Simulate analysis time
                    
                    # Use advanced analysis engine
                    if analysis_engine_available and AnalysisEngine:
                        try:
                            engine = AnalysisEngine()
                            
                            # Convert domains to proper sector preference
                            if len(domains) > 2:
                                sector_pref = "Diversified"
                            elif domains:
                                sector_pref = domains[0] 
                            else:
                                sector_pref = "Technology"
                            
                            # Convert investment time to horizon format
                            horizon_map = {
                                1: "1-3 years", 2: "1-3 years", 3: "3-5 years", 
                                5: "3-5 years", 7: "5-10 years", 10: "5-10 years",
                                15: "10+ years", 20: "10+ years"
                            }
                            horizon = horizon_map.get(investment_time, "3-5 years")
                            
                            st.session_state.analysis_results = engine.perform_portfolio_analysis(
                                capital=capital,
                                risk_tolerance=risk_appetite,
                                investment_horizon=investment_time,
                                sectors=domains if domains else ["Technology", "Banking"]
                            )
                            st.session_state.analysis_results['input_params'] = {
                                'capital': capital,
                                'investment_time': investment_time,
                                'expected_growth': expected_growth,
                                'domains': domains,
                                'risk_appetite': risk_appetite
                            }
                        except Exception as e:
                            st.error(f"Analysis error: {e}")
                            st.session_state.analysis_results = create_fallback_analysis(capital, investment_time)
                    else:
                        st.session_state.analysis_results = create_fallback_analysis(capital, investment_time)
                    
                    st.success("✅ Analysis completed!")
                    st.rerun()
    
    # Results Display (Right Column)
    with col2:
        if st.session_state.analysis_results:
            display_analysis_results(st.session_state.analysis_results, capital, investment_time)
        else:
            display_welcome_screen()
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_welcome_screen():
    """Display enhanced welcome screen with market overview"""
    
    st.markdown("""
    <div class="animate-slide-up" style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #667eea; font-size: 2.5rem; margin-bottom: 1rem;">
            Welcome to Your AI Investment Journey
        </h2>
        <p style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 2rem;">
            Get personalized investment recommendations powered by advanced AI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Live Market Data Cards
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="text-align: center; color: #667eea; margin-bottom: 1.5rem;">
            Live Market Data
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card animate-fade-scale">
            <div class="metric-label">NIFTY 50</div>
            <div class="metric-value" style="color: #48bb78;">21,456</div>
            <div style="color: #48bb78; font-weight: 600;">↗️ +1.24%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card animate-fade-scale">
            <div class="metric-label">BANK NIFTY</div>
            <div class="metric-value" style="color: #f56565;">46,234</div>
            <div style="color: #f56565; font-weight: 600;">↘️ -0.45%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card animate-fade-scale">
            <div class="metric-label">SENSEX</div>
            <div class="metric-value" style="color: #48bb78;">70,842</div>
            <div style="color: #48bb78; font-weight: 600;">↗️ +0.98%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card animate-fade-scale">
            <div class="metric-label">NIFTY IT</div>
            <div class="metric-value" style="color: #48bb78;">32,567</div>
            <div style="color: #48bb78; font-weight: 600;">↗️ +2.34%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("""
    <div style="margin: 3rem 0;">
        <h3 style="text-align: center; color: #667eea; margin-bottom: 2rem;">
            ✨ AI-Powered Features
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stock-card animate-fade-scale">
            <h4 style="color: #667eea;">Smart Analysis</h4>
            <p>Advanced AI algorithms analyze 25+ years of market data</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stock-card animate-fade-scale">
            <h4 style="color: #667eea;">Portfolio Optimization</h4>
            <p>Personalized recommendations based on your risk profile</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stock-card animate-fade-scale">
            <h4 style="color: #667eea;">🛡️ Risk Management</h4>
            <p>Comprehensive risk assessment and mitigation strategies</p>
        </div>
        """, unsafe_allow_html=True)

def display_analysis_results(results, capital, investment_time):
    """Enhanced results display with comprehensive analytics and charts"""
    
    # Extract parameters
    params = results.get('input_params', {})
    capital = params.get('capital', capital)
    investment_time = params.get('investment_time', investment_time)
    
    # Portfolio metrics
    metrics = results.get('portfolio_metrics', {})
    expected_return = metrics.get('expected_annual_return', 12.5)
    projected_value = metrics.get('projected_total_value', capital * 1.125)
    total_gain = metrics.get('total_gain', projected_value - capital)
    
    st.markdown("""
    <div class="animate-slide-up" style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #667eea; font-size: 2.5rem; margin-bottom: 1rem; font-weight: 600;">
            Your Personalized Investment Portfolio
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics cards with enhanced components
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if components_available:
            MetricCard(
                title="Investment Capital",
                value=f"₹{capital:,.0f}",
                icon="💰",
                color_scheme="info"
            )
        else:
            st.markdown(f"""
            <div class="metric-card animate-scale">
                <div class="metric-label">Investment Capital</div>
                <div class="metric-value">₹{capital:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if components_available:
            MetricCard(
                title="Expected Return",
                value=f"{expected_return:.1f}%",
                change=f"+{expected_return - 10:.1f}% above average",
                icon="📈",
                color_scheme="success"
            )
        else:
            st.markdown(f"""
            <div class="metric-card animate-scale">
                <div class="metric-label">Expected Return</div>
                <div class="metric-value">{expected_return:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if components_available:
            MetricCard(
                title="Projected Value",
                value=f"₹{projected_value:,.0f}",
                change=f"₹{total_gain:,.0f} potential gain",
                icon="🎯",
                color_scheme="primary"
            )
        else:
            st.markdown(f"""
            <div class="metric-card animate-scale">
                <div class="metric-label">Projected Value</div>
                <div class="metric-value">₹{projected_value:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Charts Section
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="color: #667eea; text-align: center; margin-bottom: 1.5rem;">Portfolio Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Sector allocation pie chart
        sector_data = results.get('sector_allocation', {"Technology": 50, "Banking": 30, "Healthcare": 20})
        
        if components_available:
            chart_components.render_enhanced_pie_chart(
                data=sector_data,
                title="Sector Allocation",
                height=400
            )
        else:
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(sector_data.keys()),
                values=list(sector_data.values()),
                hole=0.4,
                marker=dict(
                    colors=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'],
                    line=dict(color='#1a1a2e', width=2)
                ),
                textfont=dict(size=12, color='white'),
                textinfo='label+percent'
            )])
            
            fig_pie.update_layout(
                title=dict(text="Sector Allocation", font=dict(color='#e2e8f0', size=16)),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                showlegend=True,
                legend=dict(font=dict(color='#e2e8f0'))
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with chart_col2:
        # Growth projection chart
        years = list(range(0, investment_time + 1))
        values = [capital * (1 + expected_return/100) ** year for year in years]
        
        if components_available:
            chart_components.render_growth_projection_chart(
                capital=capital,
                years=investment_time,
                annual_return=expected_return,
                title="Growth Projection"
            )
        else:
            fig_growth = go.Figure()
            
            fig_growth.add_trace(go.Scatter(
                x=years,
                y=values,
                mode='lines+markers',
                name='Portfolio Value',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, color='#667eea')
            ))
            
            fig_growth.add_trace(go.Scatter(
                x=years,
                y=[capital] * len(years),
                mode='lines',
                name='Initial Investment',
                line=dict(color='#f5576c', width=2, dash='dash'),
            ))
            
            fig_growth.update_layout(
                title=dict(text="Growth Projection", font=dict(color='#e2e8f0', size=16)),
                xaxis=dict(title="Years", color='#e2e8f0', gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(title="Value (₹)", color='#e2e8f0', gridcolor='rgba(255,255,255,0.1)'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                showlegend=True,
                legend=dict(font=dict(color='#e2e8f0'))
            )
            
            st.plotly_chart(fig_growth, use_container_width=True)
    
    # Stock recommendations
    if 'portfolio' in results and results['portfolio']:
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="color: #667eea; text-align: center; margin-bottom: 1.5rem;">Stock Recommendations</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create enhanced stock cards
        cols = st.columns(3)
        for i, item in enumerate(results['portfolio']):
            col = cols[i % 3]
            stock = item['stock']
            
            with col:
                if components_available:
                    StockCard({
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'current_price': stock.current_price,
                        'target_price': stock.target_price,
                        'market_cap': getattr(stock, 'market_cap', 'N/A'),
                        'sector': stock.sector,
                        'recommendation': stock.recommendation,
                        'analyst_rating': 5.0 - stock.risk_score,
                        'allocation_percentage': item.get('allocation_percentage', 0)
                    })
                else:
                    st.markdown(f"""
                    <div class="stock-card animate-fade-scale">
                        <div class="stock-header">
                            <div class="stock-symbol">{stock.symbol}</div>
                            <div class="stock-price">₹{stock.current_price:.2f}</div>
                        </div>
                        <div class="stock-info">
                            <div class="stock-name">{stock.name}</div>
                            <div class="stock-sector">{stock.sector}</div>
                            <div class="stock-allocation">Allocation: {item.get('allocation_percentage', 0):.1f}%</div>
                            <div class="stock-recommendation">{stock.recommendation}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Investment insights
    if 'investment_insights' in results:
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="color: #667eea; text-align: center; margin-bottom: 1.5rem;">AI Investment Insights</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for insight in results['investment_insights']:
            st.markdown(f"""
            <div class="insight-card animate-slide-up">
                <p style="margin: 0; color: #e2e8f0; font-size: 0.95rem;">{insight}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat Interface
    display_chat_interface(results)

def display_chat_interface(results):
    """Enhanced chat interface with dynamic AI responses"""
    
    # Use enhanced chat interface if available
    if components_available:
        # Get portfolio context for AI responses
        metrics = results.get('portfolio_metrics', {})
        expected_return = metrics.get('expected_annual_return', 12.5)
        risk_score = metrics.get('portfolio_risk_score', 2.5)
        
        # Initialize chat with context
        chat_interface = ChatContainer(
            title="AI Investment Assistant",
            context={
                'expected_return': expected_return,
                'risk_score': risk_score,
                'portfolio_metrics': metrics,
                'sector_allocation': results.get('sector_allocation', {})
            }
        )
        
        # Render enhanced chat interface
        chat_interface.render()
        
    else:
        # Fallback to original chat interface
        st.markdown("""
        <div class="chat-container animate-fade-scale">
            <h3 style="text-align: center; color: #667eea; margin-bottom: 1.5rem;">
                AI Investment Assistant
            </h3>
        """, unsafe_allow_html=True)
        
        # Extract portfolio metrics for intelligent responses
        metrics = results.get('portfolio_metrics', {})
        expected_return = metrics.get('expected_annual_return', 12.5)
        risk_score = metrics.get('portfolio_risk_score', 2.5)
        diversification = metrics.get('diversification_score', 7.5)
        sector_data = results.get('sector_allocation', {})
        
        # Quick action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Risk Analysis", key="risk_analysis"):
                risk_level = "Low" if risk_score < 2.5 else "Moderate" if risk_score < 3.5 else "High"
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>Risk Assessment:</strong> Your portfolio has a {risk_level.lower()} risk profile with a score of {risk_score:.1f}/5. 
                    The diversification score of {diversification:.1f}/10 {'provides good protection' if diversification > 7 else 'could be improved'} against market volatility.
                    {'Consider adding more defensive stocks to reduce risk.' if risk_score > 3.5 else 'Well-balanced risk exposure for your profile.'}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if st.button("Market Outlook", key="market_outlook"):
                sectors_text = ", ".join(list(sector_data.keys())[:3]) if sector_data else "diversified sectors"
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>Market Analysis:</strong> Current market conditions favor {sectors_text}. 
                    Your expected return of {expected_return:.1f}% is {'above' if expected_return > 12 else 'in line with'} market averages.
                    Consider maintaining your current allocation while monitoring quarterly results and market trends.
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if st.button("Optimization Tips", key="optimization"):
                top_sector = max(sector_data.keys(), key=sector_data.get) if sector_data else "Technology"
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>Optimization Tips:</strong> Your portfolio is weighted towards {top_sector}. 
                    Consider regular rebalancing every 3-6 months to maintain target allocations.
                    {'Reduce concentration in ' + top_sector if sector_data.get(top_sector, 0) > 40 else 'Current allocation looks balanced'}.
                    Set up systematic investment plans (SIP) for consistent investing.
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if st.button("Education", key="education"):
                st.markdown("""
                <div class="chat-message ai-message">
                    <strong>Investment Wisdom:</strong> Key principles for successful investing:
                    • Diversification reduces risk without sacrificing returns
                    • Time in market beats timing the market
                    • Regular rebalancing maintains your target allocation
                    • Stay informed but avoid emotional decision-making
                    • Review and adjust strategy annually based on life changes
                </div>
                """, unsafe_allow_html=True)
        
        # Interactive chat input
        st.markdown("---")
        user_question = st.text_input("Ask me anything about your portfolio:", placeholder="e.g., Should I invest more in technology stocks?")
        
        if user_question:
            # Simple AI-like responses based on keywords
            response = generate_ai_response(user_question, results)
            st.markdown(f"""
            <div class="chat-message ai-message">
                <strong>AI Assistant:</strong> {response}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def generate_ai_response(question, results):
    """Generate contextual AI responses based on portfolio data"""
    
    question_lower = question.lower()
    metrics = results.get('portfolio_metrics', {})
    expected_return = metrics.get('expected_annual_return', 12.5)
    risk_score = metrics.get('portfolio_risk_score', 2.5)
    
    # Keyword-based responses
    if any(word in question_lower for word in ['risk', 'safe', 'conservative']):
        if risk_score < 2.5:
            return f"Your portfolio has a conservative risk profile (score: {risk_score:.1f}/5). This provides stability but may limit growth potential. Consider adding some moderate-risk growth stocks if you're comfortable."
        else:
            return f"Your current risk level is {risk_score:.1f}/5. To reduce risk, consider increasing allocation to large-cap stocks and reducing exposure to volatile sectors."
    
    elif any(word in question_lower for word in ['return', 'profit', 'growth']):
        return f"Your portfolio targets {expected_return:.1f}% annual returns. This is {'above' if expected_return > 12 else 'in line with'} market averages. Focus on quality companies with strong fundamentals for sustainable growth."
    
    elif any(word in question_lower for word in ['technology', 'tech', 'it']):
        return "Technology sector offers high growth potential but with higher volatility. Consider maintaining 20-30% allocation to tech stocks, focusing on established players with strong competitive moats."
    
    elif any(word in question_lower for word in ['diversification', 'diversify', 'sectors']):
        return "Diversification across sectors reduces portfolio risk. Aim for exposure to 4-6 different sectors including defensive (banking, consumer goods) and growth sectors (technology, healthcare)."
    
    elif any(word in question_lower for word in ['when', 'timing', 'buy', 'sell']):
        return "Market timing is difficult even for professionals. Focus on systematic investing (SIP), dollar-cost averaging, and staying invested for the long term. Regular rebalancing is more important than timing."
    
    elif any(word in question_lower for word in ['emergency', 'fund', 'cash']):
        return "Maintain 6-12 months of expenses in emergency fund before investing. This provides financial security and prevents need to liquidate investments during emergencies."
    
    else:
        return "I'd be happy to help with your investment questions! I can provide insights on portfolio risk, expected returns, sector allocation, diversification strategies, and general investment principles based on your portfolio analysis."

if __name__ == "__main__":
    main()