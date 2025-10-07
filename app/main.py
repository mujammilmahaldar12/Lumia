"""
Lumia Robo-Advisor - Professional Portfolio Management System
"""

import streamlit as st
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database import get_db
from roboadvisor.user_profile import build_user_profile
from roboadvisor.recommender import generate_recommendation

# Page config
st.set_page_config(
    page_title="Lumia Investment Management",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean professional styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container - LIGHT GRAY background */
    .main {
        background-color: #f5f5f5 !important;
        padding: 0 !important;
        max-width: 100%;
    }
    
    .block-container {
        padding: 2rem 3rem !important;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Header - WHITE with blue accent */
    .header-bar {
        background: #ffffff !important;
        border-bottom: 3px solid #2563eb;
        padding: 1.5rem 3rem;
        margin: -2rem -3rem 2rem -3rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    .header-bar h1 {
        margin: 0;
        font-size: 1.875rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.025em;
    }
    
    /* Section cards - PURE WHITE */
    .section-card {
        background: #ffffff !important;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
        margin: 0 0 2rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    /* Input styling with proper spacing */
    .stNumberInput, .stSelectbox, .stTextInput {
        margin-bottom: 0 !important;
    }
    
    .stNumberInput > label, .stSelectbox > label, .stTextInput > label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        padding: 0.625rem 0.875rem;
        font-size: 0.9375rem;
        background: #ffffff;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Button styling */
    .stButton {
        margin-top: 2rem;
    }
    
    .stButton > button {
        background: #2563eb;
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 6px;
        font-size: 0.9375rem;
        transition: all 0.2s;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .stButton > button:hover {
        background: #1d4ed8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }
    
    /* Metric cards - WHITE background */
    .metric-card {
        background: #ffffff !important;
        border: 1px solid #e0e0e0;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transform: translateY(-2px);
    }
    
    .metric-label {
        font-size: 0.8125rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
        display: block;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2563eb;
        line-height: 1;
    }
    
    /* Chart container - PURE WHITE */
    .chart-container {
        background: #ffffff !important;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Info box - light blue */
    .info-box {
        background: #eff6ff !important;
        border-left: 4px solid #2563eb;
        padding: 1.25rem;
        margin: 0;
        border-radius: 6px;
        color: #1e40af;
        line-height: 1.6;
    }
    
    /* Table - WHITE background */
    .asset-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        background: #ffffff !important;
    }
    
    .asset-table th {
        background: #f5f5f5 !important;
        padding: 1rem 1.25rem;
        text-align: left;
        font-size: 0.8125rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .asset-table td {
        padding: 1rem 1.25rem;
        border-bottom: 1px solid #e0e0e0;
        font-size: 0.9375rem;
        color: #111827 !important;
        background: #ffffff !important;
    }
    
    .asset-table tr:hover td {
        background: #f9fafb !important;
    }
    
    .asset-table td strong {
        color: #2563eb !important;
    }
    
    /* Q&A section - WHITE */
    .question {
        background: #f5f5f5 !important;
        padding: 1rem 1.25rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-weight: 500;
        color: #111827;
        border-left: 3px solid #2563eb;
    }
    
    .answer {
        padding: 1.25rem;
        color: #374151;
        line-height: 1.7;
        background: #ffffff !important;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    
    /* Streamlit overrides */
    .stApp {
        background-color: #f5f5f5 !important;
    }
    
    div[data-testid="stAppViewContainer"] {
        background-color: #f5f5f5 !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


def format_currency(amount):
    """Format currency in Indian style"""
    if amount >= 10000000:
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


def create_pie_chart(portfolio, capital):
    """Create allocation pie chart with white background"""
    labels = []
    values = []
    colors = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe']
    
    for asset_type, assets in portfolio.items():
        if assets:
            total = sum(a.get('amount', 0) for a in assets)
            labels.append(asset_type.replace('_', ' ').title())
            values.append(total)
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(
            colors=colors[:len(labels)],
            line=dict(color='white', width=3)
        ),
        textfont=dict(size=14, family='Inter', color='#111827'),
        textposition='outside',
        textinfo='label+percent'
    )])
    
    fig.update_layout(
        showlegend=False,
        height=380,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter', size=13, color='#111827')
    )
    
    return fig


def answer_question(question, portfolio_data):
    """Enhanced Q&A with better portfolio analysis"""
    q = question.lower()
    
    if not portfolio_data:
        return "Please generate a portfolio first to get specific answers about your investments."
    
    profile = portfolio_data['profile']
    metrics = portfolio_data['metrics']
    portfolio = portfolio_data['portfolio']
    
    # Dynamic responses based on actual data
    if 'risk' in q or 'safe' in q or 'volatile' in q:
        volatility = metrics['expected_risk'] * 100
        sharpe = metrics['sharpe_ratio']
        
        risk_level = "Low" if volatility < 12 else "Moderate" if volatility < 18 else "High" if volatility < 25 else "Very High"
        
        return f"""**Risk Analysis:**

**Your Risk Profile:** {profile['risk_type'].title()} ({profile['risk_score']}/100)

**Portfolio Volatility:** {volatility:.2f}% annually
- This is considered **{risk_level}** volatility
- Your portfolio may fluctuate ±{volatility:.1f}% in a typical year

**Risk-Adjusted Performance (Sharpe Ratio):** {sharpe:.2f}
- {"Excellent" if sharpe > 1 else "Good" if sharpe > 0.5 else "Fair" if sharpe > 0 else "Below expectations"}
- Higher Sharpe = Better returns for the risk taken

**What This Means:**
- Expect natural ups and downs in portfolio value
- Long-term focus ({profile['years']} years) helps smooth volatility
- Don't panic during short-term market corrections
- Review and rebalance quarterly
"""
    
    elif 'return' in q or 'profit' in q or 'gain' in q or 'money' in q or 'earn' in q:
        capital = profile['capital']
        years = profile['years']
        annual_return = metrics['expected_return']
        
        # Calculate projections
        future_value = capital * ((1 + annual_return) ** years)
        total_gain = future_value - capital
        monthly_sip = capital / (years * 12)
        
        return f"""**Return Projections:**

**Expected Annual Return:** {annual_return*100:.2f}%
**Your Investment:** {format_currency(capital)}
**Time Horizon:** {years} years

**Projected Growth:**
- Value after {years} years: **{format_currency(future_value)}**
- Total Gain: **{format_currency(total_gain)}** ({(total_gain/capital)*100:.1f}% total)
- Average Annual Gain: **{format_currency(total_gain/years)}**

**If investing monthly:**
- ₹{monthly_sip:,.0f}/month for {years} years
- Could grow to {format_currency(future_value)}

**Important Notes:**
✓ These are estimates based on historical performance
✓ Actual returns will vary with market conditions  
✓ Past performance doesn't guarantee future results
✓ Stay invested for full {years}-year period for best results
"""
    
    elif 'stock' in q or 'allocation' in q or 'why' in q or 'breakdown' in q:
        # Calculate actual allocations
        stock_pct = sum(a.get('percentage', 0) for a in portfolio.get('stocks', []))
        etf_pct = sum(a.get('percentage', 0) for a in portfolio.get('etf', []))
        mf_pct = sum(a.get('percentage', 0) for a in portfolio.get('mutual_funds', []))
        crypto_pct = sum(a.get('percentage', 0) for a in portfolio.get('crypto', []))
        
        return f"""**Allocation Strategy Explained:**

**Your Portfolio Breakdown:**
- Stocks: {stock_pct:.1f}%
- ETFs: {etf_pct:.1f}%
- Mutual Funds: {mf_pct:.1f}%
- Crypto: {crypto_pct:.1f}%

**Why This Allocation?**

1. **Risk Profile ({profile['risk_type'].title()}):**
   - Your risk score of {profile['risk_score']}/100 determines stock allocation
   - {"Higher risk tolerance = more stocks for growth" if profile['risk_score'] > 50 else "Lower risk = more bonds/MFs for stability"}

2. **Time Horizon ({profile['years']} years):**
   - Longer timeframes allow higher stock allocation
   - Time to recover from market downturns
   - Compound growth benefits

3. **Target Return ({profile['expected_return']*100:.1f}%):**
   - Your target requires balanced growth assets
   - Diversified across asset classes for stability

4. **Diversification Benefits:**
   - {len(portfolio.get('stocks', []))} stocks for growth potential
   - {len(portfolio.get('etf', []))} ETFs for broad market exposure  
   - {len(portfolio.get('mutual_funds', []))} mutual funds for professional management
   - {len(portfolio.get('crypto', []))} crypto for alternative growth

**Result:** A balanced portfolio optimized for your goals while managing risk effectively.
"""
    
    elif 'diversif' in q or 'spread' in q or 'variety' in q:
        total_assets = portfolio_data.get('total_assets', 0)
        asset_types = portfolio_data.get('asset_types_count', 0)
        
        # Count by category
        counts = {k: len(v) for k, v in portfolio.items() if v}
        
        return f"""**Diversification Analysis:**

**Portfolio Composition:**
- **{asset_types} Asset Classes** across {total_assets} individual investments

**Breakdown:**
{chr(10).join(f"- {k.replace('_', ' ').title()}: {v} holdings" for k, v in counts.items())}

**Diversification Benefits:**

✓ **Risk Reduction:** Spreading across {total_assets} assets reduces single-asset risk
✓ **Stability:** Different assets perform well at different times  
✓ **Smoother Returns:** Volatility is averaged across all holdings
✓ **Sector Protection:** Not dependent on any single industry
✓ **Geographic Spread:** Mix of Indian and international exposure

**Correlation:** Your assets are selected to have low correlation, meaning they don't all move together.

**Status:** Your portfolio is well-diversified according to modern portfolio theory.
"""
    
    elif 'when' in q or 'time' in q or 'start' in q:
        return f"""**Investment Timing Advice:**

**The Hard Truth:** Nobody can consistently predict market movements.

**Best Strategy:**

1. **Start Now** ✓
   - Time in market > Timing the market
   - Every day delayed = potential growth lost
   - Your {profile['years']}-year horizon gives time to recover from downturns

2. **Systematic Investment:**
   - Consider monthly SIP: ₹{(profile['capital']/(profile['years']*12)):,.0f}/month
   - Rupee cost averaging reduces timing risk
   - Builds discipline and consistency

3. **Don't Try to Time:**
   - ❌ Waiting for "the right time" = missed opportunities  
   - ❌ Trying to "buy the dip" = often too late
   - ✓ Stay invested through ups and downs

**For Your Portfolio:**
- Start with your ₹{format_currency(profile['capital'])} now
- Rebalance quarterly if allocations drift >5%
- Add more when you have surplus funds
- Stay the course for {profile['years']} years

**Remember:** Markets reward patience and discipline, not perfect timing.
"""
    
    else:
        return f"""**Portfolio Assistant**

I can help you understand:

💰 **Returns:** "What's my expected return?" or "How much profit?"
📊 **Risk:** "What's my risk level?" or "Is this safe?"
🎯 **Strategy:** "Why this allocation?" or "Explain the breakdown"
🔄 **Diversification:** "How diversified am I?"
⏰ **Timing:** "When should I invest?"

**Your Portfolio at a Glance:**
- Total Investment: {format_currency(profile['capital'])}
- Expected Return: {metrics['expected_return']*100:.2f}%/year
- Risk Level: {metrics['expected_risk']*100:.2f}% volatility
- Time Horizon: {profile['years']} years

Ask me a specific question about any of these topics!
"""


def main():
    # Initialize session state
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Header
    st.markdown("""
    <div class="header-bar">
        <h1>LUMIA INVESTMENT MANAGEMENT</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration Section
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Portfolio Configuration</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        capital = st.number_input(
            "Investment Amount (₹)",
            min_value=10000,
            max_value=100000000,
            value=100000,
            step=10000,
            help="Enter your total investment amount"
        )
    
    with col2:
        risk_level = st.selectbox(
            "Risk Profile",
            ["Conservative", "Moderate", "Aggressive", "Very Aggressive"],
            index=1,
            help="Select your risk tolerance level"
        )
        risk_map = {
            "Conservative": 20,
            "Moderate": 50,
            "Aggressive": 75,
            "Very Aggressive": 90
        }
        risk_score = risk_map[risk_level]
    
    with col3:
        years = st.selectbox(
            "Investment Horizon (Years)",
            [1, 2, 3, 5, 7, 10, 15, 20, 25, 30],
            index=4,
            help="Select your investment time period"
        )
    
    with col4:
        target_return = st.number_input(
            "Target Annual Return (%)",
            min_value=5.0,
            max_value=100.0,
            value=12.0,
            step=0.5,
            help="Enter your expected annual return (5-100%)"
        )
    
    # Remove validation - let user enter any valid values
    
    # Center the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_btn = st.button("Generate Portfolio", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate Portfolio
    if generate_btn:
        with st.spinner("Analyzing market data and generating portfolio..."):
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
                
                st.success("Portfolio generated successfully")
                db.close()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display Results
    if st.session_state.portfolio:
        result = st.session_state.portfolio
        profile = result['profile']
        metrics = result['metrics']
        portfolio = result['portfolio']
        
        # Metrics Section
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Portfolio Metrics</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portfolio Value</div>
                <div class="metric-value">{format_currency(profile['capital'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Assets</div>
                <div class="metric-value">{result.get('total_assets', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Expected Return</div>
                <div class="metric-value">{metrics['expected_return']*100:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Sharpe Ratio</div>
                <div class="metric-value">{metrics['sharpe_ratio']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Allocation Chart
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Asset Allocation</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container" style="padding: 1.5rem;">', unsafe_allow_html=True)
            fig = create_pie_chart(portfolio, profile['capital'])
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Investment Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">{result["summary"]}</div>', unsafe_allow_html=True)
            
            # Additional metrics
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown(f"**Risk Profile:** {profile['risk_type'].title()}")
            st.markdown(f"**Time Horizon:** {profile['years']} years")
            st.markdown(f"**Expected Volatility:** {metrics['expected_risk']*100:.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Assets Table
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Portfolio Holdings</div>', unsafe_allow_html=True)
        
        for asset_type, assets in portfolio.items():
            if not assets:
                continue
            
            st.markdown(f"**{asset_type.replace('_', ' ').title()}**")
            
            # Debug: Check if amounts exist
            # st.write(f"DEBUG: First asset data: {assets[0] if assets else 'No assets'}")
            
            # Create table
            table_html = '<table class="asset-table"><thead><tr>'
            table_html += '<th>Symbol</th><th>Name</th><th>Allocation</th><th>Percentage</th><th>Score</th><th>Sector</th>'
            table_html += '</tr></thead><tbody>'
            
            for asset in assets:
                amt = asset.get("amount", 0)
                pct = asset.get("percentage", 0)
                score = asset.get("score", 0)
                
                table_html += '<tr>'
                table_html += f'<td><strong style="color: #2563eb;">{asset.get("symbol", "N/A")}</strong></td>'
                table_html += f'<td style="color: #111827;">{asset.get("name", "Unknown")[:40]}</td>'
                table_html += f'<td style="color: #111827;"><strong>{format_currency(amt)}</strong></td>'
                table_html += f'<td style="color: #111827;">{pct:.2f}%</td>'
                table_html += f'<td style="color: #16a34a;"><strong>{score:.1f}/100</strong></td>'
                table_html += f'<td style="color: #6b7280;">{asset.get("sector", "N/A")[:20]}</td>'
                table_html += '</tr>'
            
            table_html += '</tbody></table>'
            st.markdown(table_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Q&A Section
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Portfolio Analysis</div>', unsafe_allow_html=True)
        
        user_input = st.text_input("Ask a question about your portfolio:", placeholder="e.g., Why this allocation strategy?")
        
        if user_input:
            # Add to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Get answer
            answer = answer_question(user_input, st.session_state.portfolio)
            
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': answer
            })
        
        # Display Q&A
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history[-4:]:  # Show last 2 exchanges
                if msg['role'] == 'user':
                    st.markdown(f'<div class="question">Q: {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="answer">{msg["content"]}</div>', unsafe_allow_html=True)
            
            if len(st.session_state.chat_history) > 4:
                if st.button("Clear History"):
                    st.session_state.chat_history = []
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
