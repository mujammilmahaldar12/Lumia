import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import time
from typing import Dict, List, Any
import json

# Page config
st.set_page_config(
    page_title="Lumia Investment Advisor",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for themes and styling
def load_css():
    st.markdown("""
    <style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark theme styles */
    .dark-theme {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Light theme styles */
    .light-theme {
        background-color: #ffffff;
        color: #262730;
    }
    
    /* Custom components */
    .metric-card {
        background: linear-gradient(145deg, #f0f2f6, #ffffff);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    
    .dark-theme .metric-card {
        background: linear-gradient(145deg, #262730, #1e1e1e);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 4px solid #00d4ff;
    }
    
    .investment-card {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .investment-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .dark-theme .investment-card {
        background: #262730;
        border: 1px solid #404040;
    }
    
    .dark-theme .investment-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .chat-message {
        background: #f1f3f4;
        border-radius: 20px;
        padding: 15px 20px;
        margin: 10px 0;
        max-width: 80%;
    }
    
    .user-message {
        background: #1f77b4;
        color: white;
        margin-left: auto;
    }
    
    .ai-message {
        background: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    
    .dark-theme .ai-message {
        background: #1a2332;
        border-left: 4px solid #00d4ff;
        color: #fafafa;
    }
    
    .sidebar-metric {
        text-align: center;
        padding: 15px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .recommendation-tag {
        display: inline-block;
        background: #1f77b4;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 5px;
    }
    
    .risk-low { background: #4caf50 !important; }
    .risk-medium { background: #ff9800 !important; }
    .risk-high { background: #f44336 !important; }
    
    /* Animation styles */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Progress bar */
    .progress-container {
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 10px;
        background: linear-gradient(90deg, #1f77b4, #00d4ff);
        transition: width 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}

# Theme toggle
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Dummy data generators
def generate_stock_recommendations(capital: float, growth_expectation: float, 
                                 investment_time: int, domains: List[str]) -> Dict[str, Any]:
    """Generate dummy stock recommendations based on user inputs"""
    
    # Dummy stock data
    stock_universe = {
        'Technology': [
            {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services', 'sector': 'IT Services', 'risk': 'Low', 'expected_return': 15.2},
            {'symbol': 'INFY.NS', 'name': 'Infosys Limited', 'sector': 'IT Services', 'risk': 'Low', 'expected_return': 14.8},
            {'symbol': 'HCLTECH.NS', 'name': 'HCL Technologies', 'sector': 'IT Services', 'risk': 'Medium', 'expected_return': 16.5},
            {'symbol': 'TECHM.NS', 'name': 'Tech Mahindra', 'sector': 'IT Services', 'risk': 'Medium', 'expected_return': 13.9}
        ],
        'Healthcare': [
            {'symbol': 'SUNPHARMA.NS', 'name': 'Sun Pharmaceutical', 'sector': 'Pharmaceuticals', 'risk': 'Medium', 'expected_return': 12.8},
            {'symbol': 'DRREDDY.NS', 'name': 'Dr. Reddy\'s Labs', 'sector': 'Pharmaceuticals', 'risk': 'Medium', 'expected_return': 14.2},
            {'symbol': 'CIPLA.NS', 'name': 'Cipla Limited', 'sector': 'Pharmaceuticals', 'risk': 'Low', 'expected_return': 11.5}
        ],
        'Finance': [
            {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank', 'sector': 'Banking', 'risk': 'Low', 'expected_return': 13.5},
            {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank', 'sector': 'Banking', 'risk': 'Medium', 'expected_return': 15.8},
            {'symbol': 'SBIN.NS', 'name': 'State Bank of India', 'sector': 'Banking', 'risk': 'Medium', 'expected_return': 16.2}
        ],
        'Energy': [
            {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries', 'sector': 'Oil & Gas', 'risk': 'Medium', 'expected_return': 14.0},
            {'symbol': 'ONGC.NS', 'name': 'Oil & Natural Gas Corp', 'sector': 'Oil & Gas', 'risk': 'High', 'expected_return': 18.5},
            {'symbol': 'POWERGRID.NS', 'name': 'Power Grid Corp', 'sector': 'Utilities', 'risk': 'Low', 'expected_return': 10.8}
        ]
    }
    
    # Filter stocks based on selected domains
    selected_stocks = []
    for domain in domains:
        if domain in stock_universe:
            selected_stocks.extend(stock_universe[domain])
    
    # If no domains selected, use all stocks
    if not selected_stocks:
        for stocks in stock_universe.values():
            selected_stocks.extend(stocks)
    
    # Risk tolerance based on investment time and growth expectation
    if investment_time >= 10 and growth_expectation >= 15:
        risk_tolerance = 'High'
    elif investment_time >= 5 and growth_expectation >= 12:
        risk_tolerance = 'Medium'
    else:
        risk_tolerance = 'Low'
    
    # Filter by risk tolerance
    suitable_stocks = [s for s in selected_stocks if s['risk'] == risk_tolerance]
    if len(suitable_stocks) < 5:  # Ensure minimum stocks
        suitable_stocks = selected_stocks[:8]
    
    # Portfolio allocation
    portfolio = suitable_stocks[:6]  # Top 6 stocks
    total_weight = sum(np.random.uniform(0.8, 1.2) for _ in portfolio)
    
    for i, stock in enumerate(portfolio):
        weight = np.random.uniform(0.8, 1.2) / total_weight
        stock['allocation_percentage'] = round(weight * 100, 1)
        stock['investment_amount'] = round(capital * weight, 2)
        stock['projected_value'] = round(
            stock['investment_amount'] * (1 + stock['expected_return']/100) ** investment_time, 2
        )
    
    # Calculate portfolio metrics
    portfolio_return = sum(s['expected_return'] * s['allocation_percentage']/100 for s in portfolio)
    total_projected_value = sum(s['projected_value'] for s in portfolio)
    
    return {
        'portfolio': portfolio,
        'risk_tolerance': risk_tolerance,
        'expected_annual_return': round(portfolio_return, 2),
        'projected_total_value': round(total_projected_value, 2),
        'total_gain': round(total_projected_value - capital, 2),
        'cagr': round(((total_projected_value / capital) ** (1/investment_time) - 1) * 100, 2)
    }

def generate_market_analysis() -> Dict[str, Any]:
    """Generate dummy market analysis data"""
    
    # Generate market trends data
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    market_data = {
        'date': dates,
        'nifty_50': 18000 + np.cumsum(np.random.normal(2, 50, len(dates))),
        'sensex': 60000 + np.cumsum(np.random.normal(8, 200, len(dates))),
        'bank_nifty': 43000 + np.cumsum(np.random.normal(3, 80, len(dates)))
    }
    
    # Sector performance
    sectors = ['Technology', 'Banking', 'Healthcare', 'Energy', 'FMCG', 'Auto', 'Metals', 'Pharma']
    sector_performance = {
        sector: {
            'ytd_return': np.random.uniform(-10, 25),
            'pe_ratio': np.random.uniform(15, 35),
            'market_cap': np.random.uniform(50000, 500000)
        }
        for sector in sectors
    }
    
    return {
        'market_data': pd.DataFrame(market_data),
        'sector_performance': sector_performance,
        'market_sentiment': np.random.choice(['Bullish', 'Bearish', 'Neutral'], p=[0.4, 0.3, 0.3]),
        'vix': np.random.uniform(12, 25)
    }

def main():
    load_css()
    init_session_state()
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.title("💎 Lumia Investment Advisor")
        st.markdown("*AI-Powered Investment Research & Portfolio Management*")
    
    with col2:
        if st.button("🌓 Toggle Theme"):
            toggle_theme()
    
    with col3:
        st.markdown(f"**Theme:** {st.session_state.theme.title()}")
    
    # Apply theme class
    theme_class = f"{st.session_state.theme}-theme"
    st.markdown(f'<div class="{theme_class}">', unsafe_allow_html=True)
    
    # Sidebar - Investment Parameters
    with st.sidebar:
        st.header("📊 Investment Parameters")
        
        # Investment inputs
        capital = st.number_input(
            "💰 Investment Capital (₹)", 
            min_value=10000, 
            max_value=10000000, 
            value=500000,
            step=10000,
            help="Enter your total investment amount"
        )
        
        expected_growth = st.slider(
            "📈 Expected Annual Return (%)", 
            min_value=5, 
            max_value=30, 
            value=15,
            help="Your expected annual return percentage"
        )
        
        investment_time = st.selectbox(
            "⏰ Investment Horizon",
            options=[1, 2, 3, 5, 7, 10, 15, 20],
            index=4,
            help="How long do you plan to invest?"
        )
        
        domains = st.multiselect(
            "🏢 Preferred Domains",
            options=['Technology', 'Healthcare', 'Finance', 'Energy', 'Manufacturing', 'Consumer'],
            default=['Technology', 'Healthcare'],
            help="Select your preferred investment sectors"
        )
        
        risk_appetite = st.radio(
            "⚖️ Risk Appetite",
            options=['Conservative', 'Moderate', 'Aggressive'],
            index=1
        )
        
        # Analysis button
        if st.button("🔍 Analyze Portfolio", type="primary"):
            with st.spinner("Analyzing market data and generating recommendations..."):
                time.sleep(2)  # Simulate analysis time
                st.session_state.analysis_results = generate_stock_recommendations(
                    capital, expected_growth, investment_time, domains
                )
                st.success("Analysis completed!")
    
    # Main content area
    if st.session_state.analysis_results:
        display_analysis_results(st.session_state.analysis_results, capital, investment_time)
    else:
        display_welcome_screen()
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_welcome_screen():
    """Display welcome screen with market overview"""
    
    st.markdown("## 🌟 Welcome to Lumia Investment Advisor")
    
    # Market overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 NIFTY 50</h3>
            <h2 style="color: #4caf50;">21,456.78</h2>
            <p style="color: #4caf50;">+1.24% ↗</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 SENSEX</h3>
            <h2 style="color: #4caf50;">70,842.33</h2>
            <p style="color: #4caf50;">+0.98% ↗</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🏦 BANK NIFTY</h3>
            <h2 style="color: #f44336;">46,234.12</h2>
            <p style="color: #f44336;">-0.45% ↘</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>😰 VIX</h3>
            <h2 style="color: #ff9800;">16.78</h2>
            <p style="color: #ff9800;">+0.12% ↗</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Features overview
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 AI-Powered Analysis
        - Advanced machine learning algorithms
        - Real-time market sentiment analysis
        - Risk assessment and optimization
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Comprehensive Research
        - 16,000+ stocks and assets
        - Technical and fundamental analysis
        - Sector-wise performance tracking
        """)
    
    with col3:
        st.markdown("""
        ### 💬 Intelligent Chat
        - Ask questions about investments
        - Get personalized recommendations
        - Understand market trends
        """)
    
    # Getting started guide
    st.markdown("---")
    st.markdown("### 🚀 Getting Started")
    st.info("""
    **To get personalized investment recommendations:**
    
    1. 💰 Enter your investment capital in the sidebar
    2. 📈 Set your expected return and investment horizon
    3. 🏢 Select your preferred investment domains
    4. 🔍 Click 'Analyze Portfolio' to get AI-powered recommendations
    """)

def display_analysis_results(results: Dict[str, Any], capital: float, investment_time: int):
    """Display comprehensive analysis results"""
    
    # Portfolio overview
    st.markdown("## 📊 Your Personalized Investment Portfolio")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Expected Annual Return",
            f"{results['expected_annual_return']}%",
            delta=f"{results['expected_annual_return'] - 12:.1f}% vs Market"
        )
    
    with col2:
        st.metric(
            "Projected Value",
            f"₹{results['projected_total_value']:,.0f}",
            delta=f"₹{results['total_gain']:,.0f}"
        )
    
    with col3:
        st.metric(
            "CAGR",
            f"{results['cagr']}%",
            delta=f"{results['cagr'] - 10:.1f}% vs FD"
        )
    
    with col4:
        st.metric(
            "Risk Level",
            results['risk_tolerance'],
            delta="Optimized"
        )
    
    # Portfolio allocation chart
    st.markdown("### 🥧 Portfolio Allocation")
    
    portfolio_df = pd.DataFrame(results['portfolio'])
    
    fig_pie = px.pie(
        portfolio_df, 
        values='allocation_percentage', 
        names='name',
        title="Portfolio Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=500)
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Investment timeline
    st.markdown("### 📈 Investment Growth Projection")
    
    # Generate growth projection data
    years = list(range(investment_time + 1))
    portfolio_values = [capital * (1 + results['expected_annual_return']/100) ** year for year in years]
    fd_values = [capital * (1 + 6.5/100) ** year for year in years]  # FD comparison
    
    fig_growth = go.Figure()
    
    fig_growth.add_trace(go.Scatter(
        x=years, 
        y=portfolio_values,
        mode='lines+markers',
        name='Lumia Portfolio',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig_growth.add_trace(go.Scatter(
        x=years,
        y=fd_values,
        mode='lines+markers',
        name='Fixed Deposit (6.5%)',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    
    fig_growth.update_layout(
        title="Investment Growth Comparison",
        xaxis_title="Years",
        yaxis_title="Portfolio Value (₹)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # Detailed stock analysis
    st.markdown("### 📋 Detailed Stock Analysis")
    
    for i, stock in enumerate(results['portfolio']):
        with st.expander(f"📊 {stock['name']} ({stock['symbol']})"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"**Allocation:** {stock['allocation_percentage']}%")
                st.markdown(f"**Investment:** ₹{stock['investment_amount']:,.0f}")
            
            with col2:
                st.markdown(f"**Sector:** {stock['sector']}")
                st.markdown(f"**Risk Level:** {stock['risk']}")
            
            with col3:
                st.markdown(f"**Expected Return:** {stock['expected_return']}%")
                st.markdown(f"**Projected Value:** ₹{stock['projected_value']:,.0f}")
            
            with col4:
                gain = stock['projected_value'] - stock['investment_amount']
                st.markdown(f"**Expected Gain:** ₹{gain:,.0f}")
                
                # Risk tag
                risk_class = f"risk-{stock['risk'].lower()}"
                st.markdown(f"""
                <span class="recommendation-tag {risk_class}">
                    {stock['risk']} Risk
                </span>
                """, unsafe_allow_html=True)
    
    # Chat interface
    st.markdown("---")
    display_chat_interface(results)

def display_chat_interface(results: Dict[str, Any]):
    """Display interactive chat interface"""
    
    st.markdown("### 💬 Investment Assistant Chat")
    
    # Sample questions
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("❓ Why these stocks?"):
            add_chat_message("user", "Why did you recommend these specific stocks?")
            add_chat_message("ai", f"""
            Based on your investment profile, I recommended these stocks because:
            
            🎯 **Risk Alignment**: Your {results['risk_tolerance'].lower()} risk tolerance matches these stocks
            📈 **Return Potential**: Expected portfolio return of {results['expected_annual_return']}% meets your goals
            🏢 **Sector Diversification**: Balanced exposure across your preferred domains
            ⏰ **Time Horizon**: {len(results['portfolio'])} stocks suitable for your investment timeline
            
            Each stock has been analyzed for:
            - Financial health and growth prospects
            - Technical momentum indicators
            - Sector leadership position
            - ESG compliance scores
            """)
    
    with col2:
        if st.button("📊 Market outlook?"):
            add_chat_message("user", "What's the current market outlook?")
            add_chat_message("ai", """
            **Current Market Analysis:**
            
            📈 **Overall Sentiment**: Cautiously Optimistic
            - Markets showing resilience despite global uncertainties
            - Domestic consumption story remains strong
            
            🏢 **Sector Highlights**:
            - Technology: AI and digital transformation driving growth
            - Healthcare: Post-pandemic recovery and innovation focus
            - Banking: Credit growth and improving asset quality
            
            ⚠️ **Key Risks**:
            - Global inflation concerns
            - Geopolitical tensions
            - Interest rate fluctuations
            
            💡 **Recommendation**: Maintain diversified approach with quality stocks
            """)
    
    with col3:
        if st.button("🔄 Portfolio optimization?"):
            add_chat_message("user", "How can I optimize my portfolio further?")
            add_chat_message("ai", """
            **Portfolio Optimization Suggestions:**
            
            🎯 **Rebalancing Strategy**:
            - Review allocation quarterly
            - Book profits on outperformers
            - Add to underperformers with strong fundamentals
            
            📊 **Enhancement Options**:
            - Add international exposure (5-10%)
            - Consider adding gold/commodities (5%)
            - Explore ESG/sustainable investing themes
            
            🔍 **Monitoring Framework**:
            - Track quarterly earnings
            - Monitor sector rotation trends
            - Watch for policy changes affecting your sectors
            
            💡 **Next Steps**: Set up systematic investment plan (SIP) for disciplined investing
            """)
    
    # Chat history display
    if st.session_state.chat_history:
        st.markdown("**Chat History:**")
        for message in st.session_state.chat_history[-6:]:  # Show last 6 messages
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🤖 Lumia AI:</strong><br>{message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Custom question input
    custom_question = st.text_input("💭 Ask a custom question about your portfolio or investments:")
    
    if custom_question:
        add_chat_message("user", custom_question)
        
        # Generate dummy AI response based on keywords
        if any(word in custom_question.lower() for word in ['risk', 'safe', 'loss']):
            response = """
            **Risk Management Perspective:**
            
            🛡️ Your portfolio is designed with risk management in mind:
            - Diversification across sectors reduces concentration risk
            - Quality stocks with strong fundamentals
            - Regular monitoring and rebalancing recommended
            
            💡 **Risk Mitigation Strategies**:
            - Never invest more than you can afford to lose
            - Maintain emergency fund (6-12 months expenses)
            - Consider systematic investment approach (SIP)
            """
        elif any(word in custom_question.lower() for word in ['tax', 'save', 'benefit']):
            response = """
            **Tax Optimization Insights:**
            
            💰 **Tax-Efficient Strategies**:
            - Hold investments for >1 year for LTCG benefits
            - Consider ELSS funds for 80C deduction
            - Use tax-loss harvesting for optimization
            
            📊 **Current Tax Implications**:
            - Long-term capital gains: 10% (>₹1 lakh)
            - Short-term capital gains: 15%
            - Dividend income: Added to total income
            """
        else:
            response = f"""
            Thank you for your question about: "{custom_question}"
            
            🤖 **AI Analysis**: Based on your investment profile and current market conditions, here are my thoughts:
            
            - Your portfolio is well-positioned for long-term growth
            - Continue monitoring quarterly results and sector trends
            - Consider consulting with a financial advisor for personalized advice
            
            💡 **Pro Tip**: Stay disciplined with your investment strategy and avoid emotional decisions based on short-term market volatility.
            """
        
        add_chat_message("ai", response)
        st.rerun()

def add_chat_message(role: str, content: str):
    """Add message to chat history"""
    st.session_state.chat_history.append({
        'role': role,
        'content': content,
        'timestamp': datetime.datetime.now()
    })

if __name__ == "__main__":
    main()