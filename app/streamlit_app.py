import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import time
import sys
import os

# CRITICAL: Add parent directory to Python path
# This allows imports from the Lumia root directory
parent_dir = os.path.join(os.path.dirname(__file__), '..')
parent_dir = os.path.abspath(parent_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import database directly
from database import get_db
from sqlalchemy import distinct

# Import models
from models.assets import Asset

# Import recommendation engine
try:
    from recommendation_engine import get_recommendations, analyze_single_asset
    recommendation_engine_available = True
except ImportError as e:
    print(f"❌ Recommendation engine import error: {e}")
    recommendation_engine_available = False


# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================

def check_database_connection() -> tuple[bool, str]:
    """Check if database connection is working"""
    try:
        from sqlalchemy import text
        db = next(get_db())
        try:
            db.execute(text("SELECT 1"))
            return True, "Database connection successful"
        finally:
            db.close()
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"


def get_available_sectors() -> list[str]:
    """Get list of unique sectors from database"""
    try:
        db = next(get_db())
        try:
            sectors = db.query(distinct(Asset.sector)).filter(
                Asset.sector.isnot(None)
            ).all()
            return sorted([s[0] for s in sectors if s[0]])
        finally:
            db.close()
    except Exception as e:
        print(f"Error getting sectors: {e}")
        return []


def get_available_industries() -> list[str]:
    """Get list of unique industries from database"""
    try:
        db = next(get_db())
        try:
            industries = db.query(distinct(Asset.industry)).filter(
                Asset.industry.isnot(None)
            ).all()
            return sorted([i[0] for i in industries if i[0]])
        finally:
            db.close()
    except Exception as e:
        print(f"Error getting industries: {e}")
        return []


# ============================================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================================


# Page configuration
st.set_page_config(
    page_title="Lumia - Professional Investment Advisory",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS - Clean, Modern Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main {
        background: linear-gradient(180deg, #0a0e1a 0%, #1a1f2e 100%);
        padding: 2rem 3rem;
    }
    
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        margin-bottom: 3rem;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(59, 130, 246, 0.3);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        font-size: 1.1rem;
        font-weight: 400;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.8rem 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
    }
    
    .metric-card div:first-child {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }
    
    .stock-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
    }
    
    .stock-card:hover {
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.1);
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.3rem 0.2rem;
        font-size: 0.85rem;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
    }
    
    .score-badge:hover {
        transform: scale(1.05);
    }
    
    .score-excellent {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .score-good {
        background: rgba(59, 130, 246, 0.15);
        color: #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    .score-moderate {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    
    .score-poor {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Professional button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%);
        border-color: rgba(59, 130, 246, 0.4);
        color: #3b82f6;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        font-weight: 500;
    }
    
    /* Remove default icons, use clean typography */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'db_connected' not in st.session_state:
        st.session_state.db_connected = False
    if 'selected_asset' not in st.session_state:
        st.session_state.selected_asset = None
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None


def get_score_badge_html(score: float, label: str) -> str:
    """Generate HTML for score badge with color coding"""
    if score >= 80:
        badge_class = "score-excellent"
    elif score >= 70:
        badge_class = "score-good"
    elif score >= 60:
        badge_class = "score-moderate"
    else:
        badge_class = "score-poor"
    
    return f'<span class="score-badge {badge_class}">{label}: {score:.0f}</span>'


def display_recommendations(recommendations: dict):
    """
    Display AI-generated portfolio recommendations
    
    This function shows:
    1. Portfolio summary metrics
    2. Individual asset cards with scores
    3. Sector allocation charts
    4. Complete reasoning for each asset
    5. Risk warnings and disclaimers
    """
    
    portfolio = recommendations.get('portfolio', [])
    summary = recommendations.get('summary', {})
    reasoning = recommendations.get('reasoning', '')
    
    # Display portfolio summary metrics
    st.header("Portfolio Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_capital = summary.get('total_capital', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div>Total Investment</div>
            <div class="metric-value">₹{total_capital:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        num_assets = len(portfolio)
        st.markdown(f"""
        <div class="metric-card">
            <div>Assets Selected</div>
            <div class="metric-value">{num_assets}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        risk_profile = summary.get('risk_profile', 'Moderate').title()
        st.markdown(f"""
        <div class="metric-card">
            <div>Risk Profile</div>
            <div class="metric-value">{risk_profile}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_score = sum([a.get('final_score', 0) for a in portfolio]) / len(portfolio) if portfolio else 0
        st.markdown(f"""
        <div class="metric-card">
            <div>Avg Score</div>
            <div class="metric-value">{avg_score:.1f}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Assets", "Allocation", "Reasoning", "Risk Analysis"])
    
    with tab1:
        st.subheader("Recommended Assets")
        
        for idx, asset_data in enumerate(portfolio, 1):
            asset = asset_data.get('asset')
            scores = asset_data.get('scores', {})
            allocation = asset_data.get('allocation_percentage', 0)
            amount = asset_data.get('amount', 0)
            
            with st.expander(f"**{idx}. {asset.get('symbol', 'N/A')} - {asset.get('name', 'Unknown')}** ({allocation:.1f}% | ₹{amount:,.0f})", expanded=idx==1):
                
                # Asset details
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    st.markdown(f"""
                    **Sector:** {asset.get('sector', 'N/A')}  
                    **Industry:** {asset.get('industry', 'N/A')}  
                    **Type:** {asset.get('asset_type', 'N/A')}
                    """)
                
                with col_b:
                    current_price = asset.get('current_price', 0)
                    if current_price:
                        st.metric("Current Price", f"₹{current_price:,.2f}")
                
                # Score breakdown
                st.markdown("**📊 Score Breakdown:**")
                score_html = ""
                score_html += get_score_badge_html(scores.get('technical_score', 0), "Technical")
                score_html += get_score_badge_html(scores.get('fundamental_score', 0), "Fundamental")
                score_html += get_score_badge_html(scores.get('sentiment_score', 0), "Sentiment")
                score_html += get_score_badge_html(scores.get('risk_score', 0), "Risk")
                score_html += get_score_badge_html(asset_data.get('final_score', 0), "Final")
                
                st.markdown(score_html, unsafe_allow_html=True)
                
                # Why this asset
                st.markdown("**💡 Why This Asset:**")
                reasoning_text = asset_data.get('reasoning', 'Detailed analysis in progress...')
                if reasoning_text and len(reasoning_text) > 200:
                    st.markdown(reasoning_text[:200] + "... *(see Reasoning tab for full analysis)*")
                else:
                    st.markdown(reasoning_text)
    
    with tab2:
        st.subheader("Portfolio Allocation")
        
        # Sector allocation pie chart
        sector_allocation = {}
        asset_type_allocation = {}
        
        for asset_data in portfolio:
            asset = asset_data.get('asset')
            allocation = asset_data.get('allocation_percentage', 0)
            
            sector = asset.get('sector', 'Unknown')
            asset_type = asset.get('asset_type', 'Unknown')
            
            sector_allocation[sector] = sector_allocation.get(sector, 0) + allocation
            asset_type_allocation[asset_type] = asset_type_allocation.get(asset_type, 0) + allocation
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**By Sector:**")
            if sector_allocation:
                fig = go.Figure(data=[go.Pie(
                    labels=list(sector_allocation.keys()),
                    values=list(sector_allocation.values()),
                    hole=0.4,
                    marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'])
                )])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=True,
                    height=400
                )
                st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.markdown("**By Asset Type:**")
            if asset_type_allocation:
                fig = go.Figure(data=[go.Pie(
                    labels=list(asset_type_allocation.keys()),
                    values=list(asset_type_allocation.values()),
                    hole=0.4,
                    marker=dict(colors=['#43e97b', '#38f9d7', '#fa709a', '#fee140', '#30cfd0'])
                )])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=True,
                    height=400
                )
                st.plotly_chart(fig, width='stretch')
        
        # Allocation table
        st.markdown("**📋 Detailed Allocation:**")
        allocation_df = pd.DataFrame([
            {
                'Asset': a.get('asset', {}).get('symbol', 'N/A'),
                'Name': a.get('asset', {}).get('name', 'Unknown'),
                'Type': a.get('asset', {}).get('asset_type', 'N/A'),
                'Allocation %': f"{a.get('allocation_percentage', 0):.2f}%",
                'Amount (₹)': f"₹{a.get('amount', 0):,.0f}",
                'Score': f"{a.get('final_score', 0):.0f}/100"
            }
            for a in portfolio
        ])
        st.dataframe(allocation_df, width='stretch', hide_index=True)
    
    with tab3:
        st.subheader("Complete Investment Reasoning")
        st.markdown(reasoning)
    
    with tab4:
        st.subheader("⚠️ Risk Warnings & Disclaimers")
        st.warning("""
        **Important Disclaimers:**
        
        1. **Not Financial Advice:** This is an AI-powered analysis tool and should NOT be considered as financial advice.
        
        2. **Market Risks:** All investments carry risk. Past performance doesn't guarantee future results.
        
        3. **Do Your Research:** Always conduct your own research before investing.
        
        4. **Consult Professionals:** Consider consulting a certified financial advisor for personalized advice.
        
        5. **Data Limitations:** Recommendations are based on available data and may not reflect real-time market conditions.
        
        6. **Algorithm Limitations:** AI models can make errors. Always verify critical information independently.
        """)
        
        st.info("""
        **How to Use These Recommendations:**
        
        - Treat this as a starting point for research
        - Verify each asset independently
        - Consider your personal financial situation
        - Diversify across multiple recommendations
        - Monitor your investments regularly
        - Rebalance portfolio periodically
        """)


def display_asset_screener():
    """Asset Screener - Original functionality"""
    # Sidebar for input parameters
    with st.sidebar:
        st.header("Investment Parameters")
        
        # Check if recommendation engine is available
        if recommendation_engine_available:
            st.success("✅ Expert AI Engine: Active")
        else:
            st.warning("⚠️ AI Engine: Limited Mode")
        
        with st.form("investment_form"):
            # Capital input
            capital = st.number_input(
                "Investment Amount (₹)", 
                min_value=10000, 
                max_value=100000000,
                value=100000, 
                step=10000,
                help="Enter your total investment capital"
            )
            
            # Risk tolerance as percentage
            st.subheader("Risk Tolerance")
            risk_percentage = st.slider(
                "Risk Level (%)",
                min_value=10,
                max_value=80,
                value=40,
                step=5,
                help="10-25%: Conservative | 30-50%: Moderate | 55-80%: Aggressive"
            )
            
            # Map percentage to risk profile
            if risk_percentage <= 25:
                risk_profile = 'conservative'
                risk_label = "🛡️ Conservative (Low Risk)"
            elif risk_percentage <= 50:
                risk_profile = 'moderate'
                risk_label = "⚖️ Moderate (Balanced)"
            else:
                risk_profile = 'aggressive'
                risk_label = "🚀 Aggressive (High Risk)"
            
            st.info(f"**Selected Profile:** {risk_label}")
            
            # Number of top picks to show
            top_picks = st.slider(
                "Number of Recommendations",
                min_value=5,
                max_value=50,
                value=20,
                step=5,
                help="Top N assets to show from analysis of ALL assets"
            )
            
            # Action filter
            action_filter = st.selectbox(
                "Show Recommendations",
                ['BUY Only', 'SELL Only', 'HOLD Only', 'All Actions'],
                index=0,
                help="Filter by recommendation type"
            )
            
            # Exclusions (Optional)
            with st.expander("⚙️ Advanced Filters (Optional)"):
                # Get available sectors
                try:
                    available_sectors = get_available_sectors()
                    available_industries = get_available_industries()
                except:
                    available_sectors = []
                    available_industries = []
                
                exclude_sectors = st.multiselect(
                    "Exclude Sectors",
                    options=available_sectors,
                    help="E.g., Tobacco, Alcohol, Gambling for ethical investing"
                )
                
                exclude_industries = st.multiselect(
                    "Exclude Industries",
                    options=available_industries,
                    help="More specific exclusions"
                )
            
            # Submit button
            submitted = st.form_submit_button("🚀 Analyze All Assets", use_container_width=True)
            
            if submitted:
                # Initialize progress display
                st.markdown("### 🔬 Professional Asset Analysis")
                st.markdown("*Analyzing all assets with real data from news, prices, and fundamentals...*")
                
                progress_container = st.container()
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                if recommendation_engine_available:
                    # Import professional analyzer
                    from recommendation_engine.professional_portfolio import ProfessionalPortfolioAnalyzer
                    from models.assets import Asset
                    from database import SessionLocal
                    
                    db = SessionLocal()
                    
                    try:
                        # Get ALL assets from database
                        query = db.query(Asset)
                        
                        # Apply exclusions if any
                        if exclude_sectors:
                            query = query.filter(~Asset.sector.in_(exclude_sectors))
                        if exclude_industries:
                            query = query.filter(~Asset.industry.in_(exclude_industries))
                        
                        assets = query.all()
                        total_assets = len(assets)
                        
                        st.info(f"📊 Analyzing {total_assets} assets with professional analysis...")
                        
                        # Initialize professional analyzer
                        def progress_callback(progress_data):
                            """Update progress display"""
                            total_steps = progress_data['total_steps']
                            steps = progress_data['steps']
                            
                            # Update progress bar
                            progress_pct = min(total_steps / (total_assets * 12), 1.0)  # ~12 steps per asset
                            progress_bar.progress(progress_pct)
                            
                            # Update status
                            if steps:
                                latest = steps[-1]
                                status_text.markdown(
                                    f"**{total_steps}/{total_assets * 12} steps** | Current: {latest['name']} *({latest['duration']:.2f}s)*"
                                )
                        
                        analyzer = ProfessionalPortfolioAnalyzer(progress_callback=progress_callback)
                        
                        # Map action filter
                        action_map = {
                            'BUY Only': 'BUY',
                            'SELL Only': 'SELL',
                            'HOLD Only': 'HOLD',
                            'All Actions': None
                        }
                        selected_action = action_map[action_filter]
                        
                        # Analyze each asset
                        results = []
                        
                        for idx, asset in enumerate(assets):
                            try:
                                # Perform professional analysis
                                analysis = analyzer.analyze_asset(db, asset, allocation_amount=100000)
                                
                                if analysis:
                                    score = analysis['scores']['overall']
                                    
                                    # Determine action based on score
                                    if score >= 75:
                                        action = 'BUY'
                                elif score >= 50:
                                    action = 'HOLD'
                                else:
                                    action = 'SELL'
                                
                                # Filter by action if specified
                                if selected_action is None or action == selected_action:
                                    results.append({
                                        'asset': asset,
                                        'analysis': analysis,
                                        'score': score,
                                        'action': action
                                    })
                            
                            except Exception as e:
                                print(f"[SCREENER] Error analyzing {asset.symbol}: {e}")
                                continue
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        # Sort by score (descending)
                        results.sort(key=lambda x: x['score'], reverse=True)
                        
                        # Take top N
                        top_results = results[:top_picks]
                        
                        # Store in session state
                        st.session_state.recommendations = {
                            'results': top_results,
                            'total_analyzed': total_assets,
                            'total_found': len(results),
                            'risk_profile': risk_profile,
                            'risk_percentage': risk_percentage,
                            'action_filter': action_filter,
                            'capital': capital,
                            'use_professional': True  # Flag to use professional display
                        }
                        st.session_state.error_message = None
                        
                        st.success(f"✅ Professional analysis complete! Found {len(results)} {action_filter} opportunities")
                        time.sleep(0.5)
                        st.rerun()
                    
                    except Exception as e:
                        import traceback
                        st.error(f"❌ Error during analysis: {str(e)}")
                        st.code(traceback.format_exc())
                        st.session_state.error_message = str(e)
                    
                    finally:
                        db.close()
                
                else:
                    st.error("❌ Recommendation engine not available")
                    st.info("💡 Please check if recommendation_engine module is installed correctly")    # Main content area
    if st.session_state.recommendations:
        # New expert recommendations display
        if 'results' in st.session_state.recommendations:
            display_expert_recommendations(st.session_state.recommendations)
        else:
            # Old portfolio display (legacy)
            display_recommendations(st.session_state.recommendations)
    elif st.session_state.error_message:
        st.error("⚠️ Unable to generate recommendations")
        st.code(st.session_state.error_message)
        st.info("💡 Try adjusting your parameters or check the database")
    else:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2 style="color: #667eea;">👈 Get Started</h2>
            <p style="font-size: 1.2rem; color: #888;">Configure your parameters and click <strong>Analyze All Assets</strong></p>
            <br>
            <div style="text-align: left; max-width: 700px; margin: 0 auto; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 10px;">
                <h3 style="color: #667eea;">🧠 Expert AI Engine Features</h3>
                <ul style="line-height: 2;">
                    <li><strong>Analyzes ALL 2,200+ Assets:</strong> Complete database scan - Stocks, ETFs, Mutual Funds & More</li>
                    <li><strong>Technical Analysis (25%):</strong> RSI, MACD, Bollinger Bands, 20+ indicators</li>
                    <li><strong>Fundamental Analysis (30%):</strong> P/E, ROE, Debt ratios, Revenue growth</li>
                    <li><strong>AI Sentiment (25%):</strong> FinBERT-powered news analysis</li>
                    <li><strong>Risk Assessment (20%):</strong> Volatility, Beta, Maximum Drawdown</li>
                    <li><strong>Smart Scoring:</strong> BUY ≥65 | HOLD 40-65 | SELL ≤40</li>
                </ul>
                <br>
                <h3 style="color: #667eea;">⚡ What's New</h3>
                <ul style="line-height: 2;">
                    <li>✅ <strong>No asset filters</strong> - Analyzes everything in database</li>
                    <li>✅ <strong>Risk as percentage</strong> - More intuitive control</li>
                    <li>✅ <strong>Action filtering</strong> - Show only BUY/SELL/HOLD</li>
                    <li>✅ <strong>Top N picks</strong> - Choose how many to display</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)


def display_expert_recommendations(data: dict):
    """
    Display expert AI recommendations from full database scan
    
    Shows:
    - Summary statistics (total analyzed, BUY/SELL/HOLD counts)
    - Top N recommendations with detailed scoring
    - Reasoning and targets for each pick
    """
    results = data.get('results', [])
    total_analyzed = data.get('total_analyzed', 0)
    total_found = data.get('total_found', 0)
    risk_profile = data.get('risk_profile', 'moderate').title()
    risk_percentage = data.get('risk_percentage', 40)
    action_filter = data.get('action_filter', 'All Actions')
    capital = data.get('capital', 0)
    use_professional = data.get('use_professional', False)  # Check if using professional analysis
    
    # Summary section
    st.header("Analysis Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div>Assets Analyzed</div>
            <div class="metric-value">{total_analyzed:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div>{action_filter} Found</div>
            <div class="metric-value">{total_found}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div>Risk Level</div>
            <div class="metric-value">{risk_percentage}%</div>
            <div style="font-size: 0.8rem; color: #888;">{risk_profile}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_score = sum([r['score'] for r in results]) / len(results) if results else 0
        st.markdown(f"""
        <div class="metric-card">
            <div>Avg Score</div>
            <div class="metric-value">{avg_score:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display recommendations
    st.subheader(f"🎯 Top {len(results)} Recommendations")
    
    for idx, result in enumerate(results, 1):
        asset = result['asset']
        
        # Handle both professional and old format
        if use_professional or 'analysis' in result:
            # Professional analysis format
            analysis = result.get('analysis', {})
            action = result.get('action', 'HOLD')
            overall_score = analysis.get('scores', {}).get('overall', 0)
            confidence = analysis.get('confidence', overall_score)
            
            scores = analysis.get('scores', {})
            reasoning = analysis.get('reasoning', '')
            targets = {}
            
            # Extract professional analysis data
            data_quality = analysis.get('data_quality', {})
            news_analysis = analysis.get('news_analysis', {})
            technical = analysis.get('technical_analysis', {})
            fundamental = analysis.get('fundamental_analysis', {})
            
        else:
            # Old format
            rec = result['recommendation']
            action = rec['recommendation']['action']
            overall_score = rec['recommendation']['overall_score']
            confidence = rec['recommendation']['confidence']
            
            scores = rec['scores']
            reasoning = rec.get('reasoning', {})
            targets = rec.get('targets', {})
        
        # Action emoji
        action_emoji = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡'
        }
        
        # Action color
        action_color = {
            'BUY': '#4caf50',
            'SELL': '#f44336',
            'HOLD': '#ff9800'
        }
        
        with st.expander(
            f"{action_emoji.get(action, '⚪')} **{idx}. {asset.symbol}** - {asset.name or 'N/A'} | "
            f"**{action}** | Score: **{overall_score:.1f}**/100 | Confidence: **{confidence:.1f}%**",
            expanded=(idx <= 3)
        ):
            # Asset info and scores
            col_a, col_b = st.columns([2, 1])
            
            with col_a:
                st.markdown(f"""
                **Company:** {asset.name or 'N/A'}  
                **Sector:** {asset.sector or 'N/A'}  
                **Industry:** {asset.industry or 'N/A'}
                """)
                
                # Score breakdown
                st.markdown("**📊 Score Breakdown:**")
                score_html = ""
                score_html += get_score_badge_html(scores.get('technical_score', 0), "Technical")
                score_html += get_score_badge_html(scores.get('fundamental_score', 0), "Fundamental")
                score_html += get_score_badge_html(scores.get('sentiment_score', 0), "Sentiment")
                score_html += get_score_badge_html(scores.get('risk_score', 0), "Risk")
                st.markdown(score_html, unsafe_allow_html=True)
            
            with col_b:
                # Recommendation box
                st.markdown(f"""
                <div style="background: {action_color.get(action, '#888')}22; 
                            border: 2px solid {action_color.get(action, '#888')}; 
                            border-radius: 10px; 
                            padding: 1rem; 
                            text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700; color: {action_color.get(action, '#888')};">
                        {action}
                    </div>
                    <div style="font-size: 0.9rem; color: #888;">
                        Score: {overall_score:.1f}/100
                    </div>
                    <div style="font-size: 0.9rem; color: #888;">
                        Confidence: {confidence:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Targets (for BUY recommendations)
            if action == 'BUY' and targets:
                st.markdown("**🎯 Price Targets:**")
                col_t1, col_t2, col_t3 = st.columns(3)
                
                current_price = targets.get('current_price', 0)
                target_price = targets.get('target_price', 0)
                stop_loss = targets.get('stop_loss', 0)
                upside = targets.get('potential_upside_percent', 0)
                
                with col_t1:
                    st.metric("Current Price", f"₹{current_price:,.2f}")
                
                with col_t2:
                    st.metric("Target Price", f"₹{target_price:,.2f}", f"+{upside:.1f}%")
                
                with col_t3:
                    st.metric("Stop Loss", f"₹{stop_loss:,.2f}")
            
            # Professional Analysis Data (if available)
            if use_professional or 'analysis' in result:
                st.markdown("---")
                st.markdown("### 📊 Professional Analysis Report")
                
                # Data Quality
                if data_quality:
                    col_dq1, col_dq2, col_dq3 = st.columns(3)
                    with col_dq1:
                        st.metric("📰 News Articles", f"{data_quality.get('news_articles', 0)} articles")
                    with col_dq2:
                        st.metric("📈 Price Data", f"{data_quality.get('price_points', 0)} points")
                    with col_dq3:
                        st.metric("💼 Fundamentals", data_quality.get('fundamentals_quarter', 'N/A'))
                
                # News Analysis
                if news_analysis and news_analysis.get('news_count', 0) > 0:
                    st.markdown("#### 📰 News Sentiment")
                    col_ns1, col_ns2, col_ns3, col_ns4 = st.columns(4)
                    with col_ns1:
                        st.metric("Sentiment", f"{news_analysis.get('avg_sentiment', 0)*100:.1f}/100")
                    with col_ns2:
                        st.metric("✅ Positive", news_analysis.get('positive_count', 0))
                    with col_ns3:
                        st.metric("⚠️ Neutral", news_analysis.get('neutral_count', 0))
                    with col_ns4:
                        st.metric("❌ Negative", news_analysis.get('negative_count', 0))
                
                # Technical Analysis
                if technical:
                    st.markdown("#### 📈 Technical Indicators")
                    col_ta1, col_ta2, col_ta3, col_ta4 = st.columns(4)
                    if technical.get('sma_20'):
                        with col_ta1:
                            st.metric("SMA 20", f"₹{technical['sma_20']:,.2f}")
                    if technical.get('sma_50'):
                        with col_ta2:
                            st.metric("SMA 50", f"₹{technical['sma_50']:,.2f}")
                    if technical.get('rsi'):
                        with col_ta3:
                            st.metric("RSI", f"{technical['rsi']:.1f}")
                    if technical.get('volatility'):
                        with col_ta4:
                            st.metric("Volatility", f"{technical['volatility']:.1f}%")
                
                # Fundamental Analysis
                if fundamental:
                    st.markdown("#### 💼 Fundamentals")
                    col_fa1, col_fa2, col_fa3, col_fa4 = st.columns(4)
                    if fundamental.get('pe_ratio'):
                        with col_fa1:
                            st.metric("P/E Ratio", f"{fundamental['pe_ratio']:.2f}")
                    if fundamental.get('roe'):
                        with col_fa2:
                            st.metric("ROE", f"{fundamental['roe']:.2f}%")
                    if fundamental.get('debt_to_equity'):
                        with col_fa3:
                            st.metric("D/E", f"{fundamental['debt_to_equity']:.2f}")
                    if fundamental.get('current_ratio'):
                        with col_fa4:
                            st.metric("Current Ratio", f"{fundamental['current_ratio']:.2f}")
            
            # Reasoning
            if reasoning:
                st.markdown("**💡 Why This Recommendation:**")
                
                # Handle both dict and string formats
                if isinstance(reasoning, dict):
                    summary = reasoning.get('summary', '')
                    key_factors = reasoning.get('key_factors', [])
                    risks = reasoning.get('risks', [])
                else:
                    # reasoning is a string
                    summary = str(reasoning)
                    key_factors = []
                    risks = []
                
                if summary:
                    st.info(summary)
                
                if key_factors:
                    st.markdown("**✅ Key Strengths:**")
                    for factor in key_factors:
                        st.markdown(f"- {factor}")
                
                if risks:
                    st.markdown("**⚠️ Risk Factors:**")
                    for risk in risks:
                        st.markdown(f"- {risk}")
    
    # Export option
    st.divider()
    if st.button("📥 Export Results to CSV"):
        # Create DataFrame
        export_data = []
        for idx, result in enumerate(results, 1):
            asset = result['asset']
            rec = result['recommendation']
            
            export_data.append({
                'Rank': idx,
                'Symbol': asset.symbol,
                'Company': asset.name or 'N/A',
                'Sector': asset.sector or 'N/A',
                'Industry': asset.industry or 'N/A',
                'Action': rec['recommendation']['action'],
                'Overall Score': f"{rec['recommendation']['overall_score']:.1f}",
                'Confidence': f"{rec['recommendation']['confidence']:.1f}%",
                'Technical Score': f"{rec['scores'].get('technical_score', 0):.1f}",
                'Fundamental Score': f"{rec['scores'].get('fundamental_score', 0):.1f}",
                'Sentiment Score': f"{rec['scores'].get('sentiment_score', 0):.1f}",
                'Risk Score': f"{rec['scores'].get('risk_score', 0):.1f}",
                'Current Price': rec.get('targets', {}).get('current_price', 'N/A'),
                'Target Price': rec.get('targets', {}).get('target_price', 'N/A'),
                'Upside %': rec.get('targets', {}).get('potential_upside_percent', 'N/A')
            })
        
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"lumia_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def display_asset_deep_insights(symbol, pick, db):
    """Display deep technical insights with charts and professional analysis"""
    from models.daily_price import DailyPrice
    from models.quarterly_fundamental import QuarterlyFundamental
    import numpy as np
    from datetime import timedelta
    
    # Fetch price data
    try:
        prices = db.query(DailyPrice).filter(
            DailyPrice.symbol == symbol
        ).order_by(DailyPrice.date.desc()).limit(90).all()
        
        if prices and len(prices) >= 10:
            prices = list(reversed(prices))  # Chronological order
            
            # Create price chart
            dates = [p.date for p in prices]
            closes = [p.close for p in prices]
            volumes = [p.volume if p.volume else 0 for p in prices]
            
            # Calculate technical indicators
            sma_20 = []
            sma_50 = []
            for i in range(len(closes)):
                if i >= 19:
                    sma_20.append(sum(closes[i-19:i+1]) / 20)
                else:
                    sma_20.append(None)
                
                if i >= 49:
                    sma_50.append(sum(closes[i-49:i+1]) / 50)
                else:
                    sma_50.append(None)
            
            # Create candlestick chart with indicators
            fig = go.Figure()
            
            # Price line
            fig.add_trace(go.Scatter(
                x=dates, y=closes,
                name='Price',
                line=dict(color='#667eea', width=2),
                hovertemplate='Price: ₹%{y:,.2f}<extra></extra>'
            ))
            
            # SMA 20
            fig.add_trace(go.Scatter(
                x=dates, y=sma_20,
                name='SMA 20',
                line=dict(color='#f093fb', width=1, dash='dash'),
                hovertemplate='SMA 20: ₹%{y:,.2f}<extra></extra>'
            ))
            
            # SMA 50
            fig.add_trace(go.Scatter(
                x=dates, y=sma_50,
                name='SMA 50',
                line=dict(color='#4facfe', width=1, dash='dot'),
                hovertemplate='SMA 50: ₹%{y:,.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"{symbol} - 90 Day Price Chart with Moving Averages",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                height=400,
                template="plotly_dark",
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate technical insights
            current_price = closes[-1]
            price_change_30d = ((closes[-1] - closes[-30]) / closes[-30] * 100) if len(closes) >= 30 else 0
            price_change_90d = ((closes[-1] - closes[0]) / closes[0] * 100) if len(closes) > 1 else 0
            
            # Volatility
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            volatility = np.std(returns) * np.sqrt(252) * 100  # Annualized
            
            # Trend analysis
            if sma_20[-1] and sma_50[-1]:
                if current_price > sma_20[-1] > sma_50[-1]:
                    trend = "🟢 Strong Uptrend"
                    trend_desc = "Price above both 20-day and 50-day moving averages, indicating bullish momentum"
                elif current_price < sma_20[-1] < sma_50[-1]:
                    trend = "🔴 Downtrend"
                    trend_desc = "Price below both moving averages, suggesting bearish pressure"
                elif sma_20[-1] > sma_50[-1]:
                    trend = "🟡 Bullish Crossover"
                    trend_desc = "20-day MA above 50-day MA (Golden Cross potential), momentum building"
                else:
                    trend = "🟡 Sideways/Consolidation"
                    trend_desc = "Mixed signals, price consolidating before next move"
            else:
                trend = "⚪ Insufficient Data"
                trend_desc = "Need more historical data for trend analysis"
            
            # Display technical insights
            st.markdown("### 📊 Technical Analysis Insights")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "30-Day Return",
                    f"{price_change_30d:+.2f}%",
                    delta=f"{price_change_30d:.2f}%"
                )
            
            with col2:
                st.metric(
                    "90-Day Return",
                    f"{price_change_90d:+.2f}%",
                    delta=f"{price_change_90d:.2f}%"
                )
            
            with col3:
                st.metric(
                    "Volatility (Annual)",
                    f"{volatility:.1f}%",
                    delta="Lower is stable" if volatility < 30 else "High risk"
                )
            
            # Trend analysis
            st.markdown(f"**📈 Trend:** {trend}")
            st.caption(trend_desc)
            
            # Professional technical commentary
            st.markdown("### 💡 Professional Technical Commentary")
            
            commentary = []
            
            # Price momentum
            if price_change_30d > 10:
                commentary.append("✅ **Strong Momentum:** Stock has gained over 10% in the last month, showing robust buying interest and positive sentiment.")
            elif price_change_30d > 5:
                commentary.append("✅ **Positive Momentum:** Steady upward movement with consistent gains, indicating investor confidence.")
            elif price_change_30d < -10:
                commentary.append("⚠️ **Bearish Pressure:** Significant decline in recent month. Consider if this is a temporary correction or trend reversal.")
            elif price_change_30d < -5:
                commentary.append("⚠️ **Weakness:** Recent price decline suggests profit booking or negative news flow.")
            else:
                commentary.append("➖ **Neutral Momentum:** Price consolidating in tight range, waiting for catalyst for next move.")
            
            # Volatility assessment
            if volatility < 20:
                commentary.append(f"✅ **Low Volatility ({volatility:.1f}%):** Stable price action, suitable for conservative investors. Lower risk of sudden drawdowns.")
            elif volatility < 35:
                commentary.append(f"➖ **Moderate Volatility ({volatility:.1f}%):** Normal market fluctuations, acceptable for balanced portfolios.")
            else:
                commentary.append(f"⚠️ **High Volatility ({volatility:.1f}%):** Significant price swings. Requires higher risk tolerance and longer investment horizon.")
            
            # Moving average signals
            if sma_20[-1] and sma_50[-1]:
                if sma_20[-1] > sma_50[-1]:
                    ma_crossover_pct = ((sma_20[-1] - sma_50[-1]) / sma_50[-1]) * 100
                    commentary.append(f"✅ **Golden Cross Formation:** 20-day MA is {ma_crossover_pct:.2f}% above 50-day MA. Bullish technical setup.")
                else:
                    ma_crossover_pct = ((sma_50[-1] - sma_20[-1]) / sma_20[-1]) * 100
                    commentary.append(f"⚠️ **Death Cross Risk:** 50-day MA is {ma_crossover_pct:.2f}% above 20-day MA. Bearish technical pattern.")
            
            # Price vs MA position
            if current_price > sma_20[-1]:
                price_above_ma = ((current_price - sma_20[-1]) / sma_20[-1]) * 100
                commentary.append(f"✅ **Above Moving Average:** Trading {price_above_ma:.2f}% above 20-day MA. Bulls in control.")
            else:
                price_below_ma = ((sma_20[-1] - current_price) / sma_20[-1]) * 100
                commentary.append(f"⚠️ **Below Moving Average:** Trading {price_below_ma:.2f}% below 20-day MA. Needs to reclaim this level.")
            
            # Volume analysis (if available)
            if volumes and sum(volumes) > 0:
                avg_volume = sum(volumes) / len(volumes)
                recent_volume = sum(volumes[-5:]) / 5  # Last 5 days avg
                
                if recent_volume > avg_volume * 1.5:
                    commentary.append("✅ **High Volume:** Above-average trading activity indicates strong institutional interest.")
                elif recent_volume < avg_volume * 0.5:
                    commentary.append("⚠️ **Low Volume:** Thin trading suggests lack of conviction. Wait for volume confirmation.")
            
            for comment in commentary:
                st.markdown(comment)
            
            # Historical performance comparison
            st.markdown("### 📅 Historical Performance Context")
            
            perf_col1, perf_col2 = st.columns(2)
            
            with perf_col1:
                st.markdown(f"""
                **Recent Performance:**
                - Last 7 Days: {((closes[-1] - closes[-7]) / closes[-7] * 100) if len(closes) >= 7 else 0:.2f}%
                - Last 30 Days: {price_change_30d:.2f}%
                - Last 90 Days: {price_change_90d:.2f}%
                """)
            
            with perf_col2:
                # Calculate max drawdown
                peak = closes[0]
                max_dd = 0
                for price in closes:
                    if price > peak:
                        peak = price
                    dd = (price - peak) / peak * 100
                    if dd < max_dd:
                        max_dd = dd
                
                st.markdown(f"""
                **Risk Metrics:**
                - Max Drawdown: {max_dd:.2f}%
                - Annualized Volatility: {volatility:.1f}%
                - Current Price: ₹{current_price:,.2f}
                """)
    
    except Exception as e:
        # Generate synthetic chart for demonstration
        st.info(f"📊 Generating illustrative chart for {symbol} (live data connection pending)")
        
        try:
            from datetime import datetime, timedelta
            import numpy as np
            
            # Generate synthetic price data based on scores
            tech_score = pick.get('score', 70)
            base_price = 100  # Starting price
            days = 90
            
            # Create trend based on score
            if tech_score >= 75:
                trend = 0.0008  # Strong uptrend
                volatility_factor = 0.015  # Low volatility
            elif tech_score >= 65:
                trend = 0.0004  # Moderate uptrend
                volatility_factor = 0.020  # Moderate volatility
            else:
                trend = 0.0002  # Slight uptrend
                volatility_factor = 0.025  # Higher volatility
            
            # Generate synthetic dates and prices
            dates = [datetime.now() - timedelta(days=days-i) for i in range(days)]
            prices = []
            current = base_price
            
            np.random.seed(hash(symbol) % 10000)  # Consistent randomness per symbol
            
            for i in range(days):
                # Trend component + random walk
                daily_return = trend + np.random.normal(0, volatility_factor)
                current *= (1 + daily_return)
                prices.append(current)
            
            # Calculate moving averages
            sma_20 = []
            sma_50 = []
            for i in range(len(prices)):
                if i >= 19:
                    sma_20.append(sum(prices[i-19:i+1]) / 20)
                else:
                    sma_20.append(None)
                
                if i >= 49:
                    sma_50.append(sum(prices[i-49:i+1]) / 50)
                else:
                    sma_50.append(None)
            
            # Create chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=prices,
                name='Price (Illustrative)',
                line=dict(color='#667eea', width=2),
                hovertemplate='Price: ₹%{y:,.2f}<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=sma_20,
                name='SMA 20',
                line=dict(color='#f093fb', width=1, dash='dash'),
                hovertemplate='SMA 20: ₹%{y:,.2f}<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=sma_50,
                name='SMA 50',
                line=dict(color='#4facfe', width=1, dash='dot'),
                hovertemplate='SMA 50: ₹%{y:,.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"{symbol} - Illustrative Price Trend (90 Days)",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                height=400,
                template="plotly_dark",
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate synthetic metrics
            current_price = prices[-1]
            price_change_30d = ((prices[-1] - prices[-30]) / prices[-30] * 100)
            price_change_90d = ((prices[-1] - prices[0]) / prices[0] * 100)
            
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            volatility = np.std(returns) * np.sqrt(252) * 100
            
            # Trend analysis
            if sma_20[-1] and sma_50[-1]:
                if current_price > sma_20[-1] > sma_50[-1]:
                    trend_label = "🟢 Strong Uptrend"
                    trend_desc = "Price above both 20-day and 50-day moving averages (illustrative pattern)"
                elif sma_20[-1] > sma_50[-1]:
                    trend_label = "🟡 Bullish Crossover"
                    trend_desc = "20-day MA above 50-day MA, momentum building (illustrative pattern)"
                else:
                    trend_label = "🟡 Consolidation"
                    trend_desc = "Price consolidating (illustrative pattern)"
            else:
                trend_label = "⚪ Building Pattern"
                trend_desc = "Trend formation in progress (illustrative)"
            
            st.markdown("### 📊 Illustrative Technical Insights")
            st.caption("⚠️ Note: Charts show expected patterns based on scoring. Connect live data for real-time analysis.")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("30-Day Pattern", f"{price_change_30d:+.2f}%", delta=f"{price_change_30d:.2f}%")
            
            with col2:
                st.metric("90-Day Pattern", f"{price_change_90d:+.2f}%", delta=f"{price_change_90d:.2f}%")
            
            with col3:
                st.metric("Expected Volatility", f"{volatility:.1f}%", delta="Based on score")
            
            st.markdown(f"**📈 Expected Trend:** {trend_label}")
            st.caption(trend_desc)
            
            st.markdown("### 💡 Pattern Analysis (Illustrative)")
            
            if tech_score >= 75:
                st.markdown("✅ **Strong Momentum Pattern:** High technical score suggests upward trajectory with controlled volatility.")
            elif tech_score >= 65:
                st.markdown("➖ **Moderate Pattern:** Balanced technical setup with steady growth potential.")
            else:
                st.markdown("⚠️ **Building Base:** Early-stage technical setup, higher volatility expected.")
            
            st.info("📡 **To see real price data:** Connect data collector to fetch historical prices from market sources.")
            
        except Exception as e2:
            st.warning(f"📊 Chart visualization unavailable")
            st.caption("Historical price data needed for visual analysis")
    
    # Fundamental insights (if available)
    try:
        fundamental = db.query(QuarterlyFundamental).filter(
            QuarterlyFundamental.symbol == symbol
        ).order_by(QuarterlyFundamental.quarter_end.desc()).first()
        
        if fundamental:
            st.markdown("### 💼 Fundamental Highlights")
            
            fund_col1, fund_col2, fund_col3 = st.columns(3)
            
            with fund_col1:
                if fundamental.pe_ratio:
                    pe_color = "🟢" if 10 <= fundamental.pe_ratio <= 30 else "🟡" if fundamental.pe_ratio <= 50 else "🔴"
                    st.metric("P/E Ratio", f"{fundamental.pe_ratio:.2f}", delta=f"{pe_color} {'Fair' if 10 <= fundamental.pe_ratio <= 30 else 'High' if fundamental.pe_ratio > 30 else 'Low'}")
            
            with fund_col2:
                if fundamental.roe:
                    roe_color = "🟢" if fundamental.roe > 15 else "🟡" if fundamental.roe > 10 else "🔴"
                    st.metric("ROE", f"{fundamental.roe:.2f}%", delta=f"{roe_color} {'Excellent' if fundamental.roe > 15 else 'Good' if fundamental.roe > 10 else 'Needs Improvement'}")
            
            with fund_col3:
                if fundamental.debt_to_equity:
                    debt_color = "🟢" if fundamental.debt_to_equity < 1 else "🟡" if fundamental.debt_to_equity < 2 else "🔴"
                    st.metric("Debt/Equity", f"{fundamental.debt_to_equity:.2f}", delta=f"{debt_color} {'Low' if fundamental.debt_to_equity < 1 else 'Moderate' if fundamental.debt_to_equity < 2 else 'High'}")
            
            # Fundamental commentary
            st.markdown("**💡 Fundamental Analysis:**")
            
            fund_comments = []
            
            if fundamental.pe_ratio:
                if 10 <= fundamental.pe_ratio <= 25:
                    fund_comments.append(f"✅ **Fairly Valued:** P/E ratio of {fundamental.pe_ratio:.2f} suggests reasonable valuation relative to earnings.")
                elif fundamental.pe_ratio < 10:
                    fund_comments.append(f"✅ **Undervalued:** P/E ratio of {fundamental.pe_ratio:.2f} indicates potential value opportunity. Deep dive into reasons for low valuation.")
                elif fundamental.pe_ratio > 40:
                    fund_comments.append(f"⚠️ **Expensive:** P/E ratio of {fundamental.pe_ratio:.2f} suggests premium valuation. Justified only if high growth expected.")
            
            if fundamental.roe:
                if fundamental.roe > 20:
                    fund_comments.append(f"✅ **Exceptional Returns:** ROE of {fundamental.roe:.2f}% demonstrates excellent capital efficiency and profitability.")
                elif fundamental.roe > 15:
                    fund_comments.append(f"✅ **Strong Returns:** ROE of {fundamental.roe:.2f}% indicates healthy business fundamentals.")
                elif fundamental.roe < 10:
                    fund_comments.append(f"⚠️ **Weak Returns:** ROE of {fundamental.roe:.2f}% below industry standards. Management effectiveness questionable.")
            
            if fundamental.debt_to_equity:
                if fundamental.debt_to_equity < 0.5:
                    fund_comments.append(f"✅ **Conservative Leverage:** D/E ratio of {fundamental.debt_to_equity:.2f} indicates low financial risk and strong balance sheet.")
                elif fundamental.debt_to_equity > 2:
                    fund_comments.append(f"⚠️ **High Leverage:** D/E ratio of {fundamental.debt_to_equity:.2f} suggests elevated financial risk. Monitor interest coverage.")
            
            for comment in fund_comments:
                st.markdown(comment)
    
    except Exception as e:
        st.caption("💼 Fundamental data: Limited availability")


def display_portfolio_builder():
    """FinRobot-Style Portfolio Builder"""
    st.header("Professional Portfolio Builder")
    st.markdown("""
    Complete robo-advisor that builds a **diversified investment strategy** across ALL asset types.
    Not just "Top 20 stocks" - a complete allocation guide with AI reasoning!
    """)
    
    with st.sidebar:
        st.header("Portfolio Configuration")
        
        with st.form("portfolio_form"):
            # Capital input (float)
            capital = st.number_input(
                "💰 Total Investment Capital (₹)",
                min_value=10000.0,
                max_value=100000000.0,
                value=100000.0,
                step=1000.0,
                format="%.2f",
                help="Total amount you want to invest (supports decimal values)"
            )
            
            # Investment time horizon
            st.markdown("📅 **Investment Time Horizon**")
            horizon_years = st.select_slider(
                "Investment Duration",
                options=[1, 2, 3, 5, 7, 10, 15, 20],
                value=5,
                format_func=lambda x: f"{x} year{'s' if x != 1 else ''}",
                help="How long you plan to stay invested (affects risk allocation)"
            )
            
            # Show horizon impact
            if horizon_years <= 2:
                st.caption("⚡ Short-term: Focus on stability and liquidity")
            elif horizon_years <= 5:
                st.caption("📈 Medium-term: Balanced growth with moderate risk")
            else:
                st.caption("🚀 Long-term: Higher growth potential, can weather volatility")
            
            # Risk appetite as fraction (0-1)
            risk_fraction = st.slider(
                "🎯 Risk Appetite",
                min_value=0.0,
                max_value=1.0,
                value=0.30,
                step=0.05,
                format="%.2f",
                help="0.0-0.30: Conservative | 0.31-0.60: Moderate | 0.61-1.0: Aggressive"
            )
            
            # Convert to percentage for display
            risk_pct = risk_fraction * 100
            
            # Show risk profile with dynamic adjustment based on horizon
            if risk_fraction <= 0.30:
                base_profile = "🛡️ **Conservative**: Capital preservation with moderate growth"
                if horizon_years >= 10:
                    base_profile += " (Long horizon allows for some equity exposure)"
            elif risk_fraction <= 0.60:
                base_profile = "⚖️ **Moderate**: Balanced growth with safety net"
                if horizon_years <= 2:
                    base_profile += " (Short horizon suggests more conservative allocation)"
            else:
                base_profile = "🚀 **Aggressive**: Maximum growth potential"
                if horizon_years <= 3:
                    base_profile += " (⚠️ High risk with short horizon - consider extending timeline)"
            
            st.info(base_profile)
            
            # Expected growth target (optional)
            st.markdown("🎯 **Return Expectations** (Optional)")
            has_growth_target = st.checkbox("Set specific return target", value=False)
            
            expected_growth = None
            if has_growth_target:
                expected_growth = st.slider(
                    "Expected Annual Return (%)",
                    min_value=5.0,
                    max_value=25.0,
                    value=12.0,
                    step=0.5,
                    format="%.1f%%",
                    help="Target annual return - portfolio will be optimized towards this goal"
                )
                
                # Reality check based on risk and horizon
                if expected_growth > 18 and risk_fraction < 0.6:
                    st.warning("⚠️ High return expectations may require higher risk appetite")
                elif expected_growth < 8 and risk_fraction > 0.7:
                    st.info("💡 Conservative return target with high risk tolerance - consider growth stocks")
            
            # Asset exclusions
            st.markdown("🚫 **Asset Exclusions** (Optional)")
            
            col_ex1, col_ex2 = st.columns(2)
            
            with col_ex1:
                # Symbol exclusions
                exclude_symbols_text = st.text_area(
                    "Exclude Specific Symbols",
                    placeholder="RELIANCE, TCS, INFY, HDFCBANK\n(comma-separated)",
                    height=60,
                    help="Specific assets you don't want in your portfolio"
                )
                
                # Parse symbols
                exclude_symbols = []
                if exclude_symbols_text.strip():
                    exclude_symbols = [s.strip().upper() for s in exclude_symbols_text.split(',') if s.strip()]
                
                if exclude_symbols:
                    st.caption(f"Excluding {len(exclude_symbols)} symbols: {', '.join(exclude_symbols[:5])}{'...' if len(exclude_symbols) > 5 else ''}")
            
            with col_ex2:
                # Sector/Industry exclusions
                with st.expander("⚙️ Sector/Industry Exclusions"):
                    try:
                        available_sectors = get_available_sectors()
                        available_industries = get_available_industries()
                    except:
                        available_sectors = []
                        available_industries = []
                    
                    exclude_sectors = st.multiselect(
                        "Exclude Sectors",
                        options=available_sectors,
                        help="E.g., Tobacco, Alcohol for ethical investing"
                    )
                    
                    exclude_industries = st.multiselect(
                        "Exclude Industries",
                        options=available_industries,
                        help="More specific industry exclusions"
                    )
            
            # Summary of parameters
            st.markdown("---")
            st.markdown("📋 **Portfolio Parameters Summary:**")
            
            summary_col1, summary_col2 = st.columns(2)
            
            with summary_col1:
                st.markdown(f"""
                - **Capital:** ₹{capital:,.2f}
                - **Time Horizon:** {horizon_years} years
                - **Risk Level:** {risk_fraction:.2f} ({risk_pct:.0f}%)
                """)
            
            with summary_col2:
                st.markdown(f"""
                - **Growth Target:** {f'{expected_growth:.1f}%' if expected_growth else 'Market-based'}
                - **Symbol Exclusions:** {len(exclude_symbols)} assets
                - **Sector Exclusions:** {len(exclude_sectors) if 'exclude_sectors' in locals() else 0} sectors
                """)
            
            submitted = st.form_submit_button("🎯 Generate Portfolio", use_container_width=True)
            
            if submitted:
                # Initialize progress display
                st.markdown("### 🔬 Professional Portfolio Analysis")
                st.markdown("*Performing comprehensive analysis with real data from news, prices, and fundamentals...*")
                
                progress_container = st.container()
                progress_bar = st.progress(0)
                status_text = st.empty()
                steps_expander = st.expander("📋 Detailed Analysis Steps", expanded=True)
                steps_placeholder = st.empty()
                
                all_steps = []
                
                def update_progress(progress_data):
                    """Update progress display"""
                    nonlocal all_steps
                    total_steps = progress_data['total_steps']
                    steps = progress_data['steps']
                    all_steps = steps
                    
                    # Update progress bar (assume ~50 total steps)
                    progress_pct = min(total_steps / 50, 1.0)
                    progress_bar.progress(progress_pct)
                    
                    # Update current status
                    if steps:
                        latest = steps[-1]
                        status_text.markdown(
                            f"**Current:** {latest['name']} *({latest['duration']:.2f}s)*"
                        )
                    
                    # Show last 15 steps
                    with steps_expander:
                        steps_html = ""
                        for step in steps[-15:]:
                            icon = "✅" if step['duration'] > 0 else "⏳"
                            steps_html += f"{icon} **{step['name']}** - {step['details']} *({step['duration']:.2f}s)*\n\n"
                        steps_placeholder.markdown(steps_html)
                
                try:
                    from recommendation_engine.professional_portfolio import (
                        ProfessionalPortfolioAnalyzer,
                        IntelligentAssetSelector
                    )
                    from recommendation_engine.portfolio import FinRobotPortfolio
                    from database import SessionLocal
                    
                    # Start analysis
                    analyzer = ProfessionalPortfolioAnalyzer(progress_callback=update_progress)
                    analyzer.progress.start_analysis()
                    
                    # STEP 1: Capital analysis
                    update_progress({
                        'total_steps': 1,
                        'steps': [{
                            'name': '💰 Analyzing capital',
                            'details': f'Processing Rs {capital:,.0f} with {risk_pct}% risk appetite',
                            'duration': 0.5
                        }]
                    })
                    time.sleep(0.5)
                    
                    # STEP 2: Asset selection
                    profile = 'conservative' if risk_pct < 40 else 'aggressive' if risk_pct > 70 else 'moderate'
                    selector = IntelligentAssetSelector()
                    included_assets = selector.select_asset_types(capital, profile)
                    
                    asset_types_str = ', '.join([k.upper() for k, v in included_assets.items() if v])
                    update_progress({
                        'total_steps': 2,
                        'steps': all_steps + [{
                            'name': '🎯 Asset selection complete',
                            'details': f'Selected {sum(included_assets.values())} types: {asset_types_str}',
                            'duration': 0.3
                        }]
                    })
                    time.sleep(0.3)
                    
                    # STEP 3: Use traditional portfolio builder with progress tracking
                    update_progress({
                        'total_steps': 3,
                        'steps': all_steps + [{
                            'name': '📊 Building portfolio',
                            'details': 'Applying capital allocation strategy...',
                            'duration': 0.5
                        }]
                    })
                    
                    allocator = FinRobotPortfolio()
                    portfolio = allocator.build_portfolio(
                        total_capital=capital,
                        risk_appetite=risk_pct,
                        exclude_sectors=exclude_sectors if exclude_sectors else None,
                        exclude_industries=exclude_industries if exclude_industries else None
                    )
                    
                    # STEP 4: Enhance each recommendation with professional analysis
                    db = SessionLocal()
                    try:
                        step_count = 3
                        for asset_type in ['stocks', 'etf', 'mutual_fund', 'crypto']:
                            if asset_type not in portfolio['picks']:
                                continue
                            
                            picks = portfolio['picks'][asset_type].get('picks', [])
                            for i, pick in enumerate(picks):
                                step_count += 1
                                symbol = pick.get('symbol', pick.get('name', 'Unknown'))
                                
                                update_progress({
                                    'total_steps': step_count,
                                    'steps': all_steps + [{
                                        'name': f'🔍 Analyzing {symbol}',
                                        'details': f'Starting comprehensive analysis...',
                                        'duration': 0
                                    }]
                                })
                                
                                # Query asset from database
                                from models.assets import Asset
                                asset = db.query(Asset).filter(Asset.symbol == symbol).first()
                                
                                if asset:
                                    # Perform real analysis
                                    analysis = analyzer.analyze_asset(
                                        db, asset, allocation_amount=pick.get('allocation', 0)
                                    )
                                    
                                    # Store analysis in pick
                                    pick['professional_analysis'] = analysis
                                    pick['data_quality'] = analysis['data_quality']
                                    
                        update_progress({
                            'total_steps': step_count + 1,
                            'steps': all_steps + [{
                                'name': '✅ Analysis complete',
                                'details': f'Portfolio generated with {step_count} analysis steps',
                                'duration': analyzer.progress.get_progress()['total_time']
                            }]
                        })
                        
                    finally:
                        db.close()
                    
                    # Store in session state
                    st.session_state['portfolio'] = portfolio
                    st.session_state['analysis_steps'] = all_steps
                    
                    # Complete
                    progress_bar.progress(1.0)
                    total_time = analyzer.progress.get_progress()['total_time']
                    st.success(f"✅ Professional analysis complete! Total time: {total_time:.1f} seconds | {step_count} steps executed")
                    time.sleep(1)
                    st.rerun()
                
                except Exception as e:
                    import traceback
                    st.error(f"❌ Error during analysis: {str(e)}")
                    with st.expander("🐛 Error Details"):
                        st.code(traceback.format_exc())

    
    # Display portfolio if generated
    if 'portfolio' in st.session_state and st.session_state['portfolio']:
        portfolio = st.session_state['portfolio']
        meta = portfolio['metadata']
        alloc = portfolio['allocation']
        picks = portfolio['picks']
        reasoning = portfolio['reasoning']
        
        # Summary cards with transaction costs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div>💰 Capital</div>
                <div class="metric-value">₹{meta['capital']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div>📊 Risk Level</div>
                <div class="metric-value">{meta.get('risk', 0.3):.2f}</div>
                <div style="font-size: 0.8rem; color: #888;">{meta.get('risk_profile', 'Moderate')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Show transaction costs if available
            if 'total_transaction_cost' in meta:
                cost_color = "#28a745" if meta['transaction_cost_percentage'] < 1.5 else "#ffc107" if meta['transaction_cost_percentage'] < 3.0 else "#dc3545"
                st.markdown(f"""
                <div class="metric-card">
                    <div>� Transaction Costs</div>
                    <div class="metric-value" style="color: {cost_color};">₹{meta['total_transaction_cost']:,.2f}</div>
                    <div style="color: {cost_color};">{meta['transaction_cost_percentage']:.2f}% of capital</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <div>🎯 Asset Types</div>
                    <div style="font-size: 1.2rem; color: #888;">{len([a for a in alloc if alloc[a].get('percentage', 0) > 0])}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div>�📅 Generated</div>
                <div style="font-size: 1rem; color: #888;">{meta['generated_at']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Show intelligent asset selection info
        if 'asset_types_included' in meta:
            asset_types_str = ', '.join([a.replace('_', ' ').title() for a in meta['asset_types_included']])
            st.info(f"🎯 **Intelligent Asset Selection:** Based on your capital of ₹{meta['capital']:,.0f}, we've selected {len(meta['asset_types_included'])} asset type(s) for optimal diversification: **{asset_types_str}**")
        
        st.markdown("---")
        
        # Allocation Breakdown
        st.subheader("💼 Allocation Breakdown")
        
        # Create enhanced bar chart with net amounts
        alloc_data = []
        for asset_type, data in alloc.items():
            if data.get('percentage', 0) > 0:
                alloc_data.append({
                    'Asset Type': asset_type.upper().replace('_', ' '),
                    'Percentage': data['percentage'],
                    'Gross Amount': data['amount'],
                    'Transaction Cost': data.get('transaction_cost', 0),
                    'Net Amount': data.get('net_amount', data['amount'])
                })
        
        alloc_df = pd.DataFrame(alloc_data)
        
        # Create side-by-side comparison charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Gross vs Net Amount Chart
            fig = go.Figure(data=[
                go.Bar(
                    name='Net Amount',
                    x=alloc_df['Asset Type'],
                    y=alloc_df['Net Amount'],
                    text=alloc_df['Net Amount'].apply(lambda x: f"₹{x:,.0f}"),
                    textposition='inside',
                    marker_color='#43e97b'
                ),
                go.Bar(
                    name='Transaction Cost',
                    x=alloc_df['Asset Type'],
                    y=alloc_df['Transaction Cost'],
                    text=alloc_df['Transaction Cost'].apply(lambda x: f"₹{x:.0f}" if x > 0 else ""),
                    textposition='inside',
                    marker_color='#f093fb'
                )
            ])
            
            fig.update_layout(
                title="Investment Breakdown (Net vs Costs)",
                xaxis_title="Asset Type",
                yaxis_title="Amount (₹)",
                height=400,
                template="plotly_dark",
                barmode='stack'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            # Percentage Allocation Pie Chart
            fig = go.Figure(data=[go.Pie(
                labels=alloc_df['Asset Type'],
                values=alloc_df['Percentage'],
                hole=0.4,
                marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b'])
            )])
            
            fig.update_layout(
                title="Allocation Distribution",
                height=400,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Allocation table with enhanced details
        st.dataframe(
            alloc_df.style.format({
                'Gross Amount': '₹{:,.0f}',
                'Transaction Cost': '₹{:,.2f}',
                'Net Amount': '₹{:,.0f}',
                'Percentage': '{:.1f}%'
            }),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Recommended Picks
        st.subheader("🎯 Recommended Picks")
        
        tabs = st.tabs(["📈 Stocks", "📊 ETFs", "💼 Mutual Funds", "🪙 Crypto", "🏦 Fixed Deposit"])
        
        # Stocks tab
        with tabs[0]:
            if 'stocks' in picks and picks['stocks']['picks']:
                for i, pick in enumerate(picks['stocks']['picks'], 1):
                    with st.expander(f"#{i} - {pick['symbol']} - {pick['name'][:50]}", expanded=(i==1)):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**💰 Investment Amount:** ₹{pick['allocation']:,.0f}")
                            st.markdown(f"**📊 Overall Score:** {pick['score']:.1f}/100")
                            st.markdown(f"**✅ Confidence:** {pick['confidence']:.0f}%")
                            if 'sector' in pick and pick['sector']:
                                st.markdown(f"**🏢 Sector:** {pick['sector']}")
                            if 'industry' in pick and pick['industry']:
                                st.markdown(f"**🏭 Industry:** {pick['industry']}")
                        with col2:
                            st.markdown("**Component Scores:**")
                            st.markdown(f"- 📈 Technical: {pick['technical']:.0f}")
                            st.markdown(f"- 💼 Fundamental: {pick['fundamental']:.0f}")
                            st.markdown(f"- 📰 Sentiment: {pick['sentiment']:.0f}")
                            st.markdown(f"- ⚠️ Risk: {pick['risk']:.0f}")
                        
                        # SHOW PROFESSIONAL ANALYSIS DATA IF AVAILABLE
                        if 'professional_analysis' in pick:
                            st.markdown("---")
                            st.markdown("### 📊 Professional Analysis Report")
                            analysis = pick['professional_analysis']
                            
                            # Data Quality
                            if 'data_quality' in analysis:
                                dq = analysis['data_quality']
                                col_dq1, col_dq2, col_dq3 = st.columns(3)
                                with col_dq1:
                                    st.metric("📰 News Articles", f"{dq.get('news_count', 0)} articles")
                                    if dq.get('news_date_range'):
                                        st.caption(f"From: {dq['news_date_range']}")
                                with col_dq2:
                                    st.metric("📈 Price Data", f"{dq.get('price_points', 0)} points")
                                    if dq.get('price_date_range'):
                                        st.caption(f"From: {dq['price_date_range']}")
                                with col_dq3:
                                    st.metric("💼 Fundamentals", dq.get('fundamentals_quarter', 'N/A'))
                            
                            # News Sentiment Details
                            if 'news_sentiment' in analysis:
                                ns = analysis['news_sentiment']
                                st.markdown("#### 📰 News Sentiment Analysis")
                                col_ns1, col_ns2, col_ns3, col_ns4 = st.columns(4)
                                with col_ns1:
                                    st.metric("Sentiment Score", f"{ns.get('score', 0):.1f}/100")
                                with col_ns2:
                                    st.metric("✅ Positive", ns.get('positive_count', 0))
                                with col_ns3:
                                    st.metric("⚠️ Neutral", ns.get('neutral_count', 0))
                                with col_ns4:
                                    st.metric("❌ Negative", ns.get('negative_count', 0))
                                
                                # Show recent headlines
                                if ns.get('recent_headlines'):
                                    with st.expander("📰 Recent Headlines"):
                                        for hl in ns['recent_headlines'][:5]:
                                            st.markdown(f"- {hl}")
                            
                            # Technical Analysis Details
                            if 'technical_analysis' in analysis:
                                ta = analysis['technical_analysis']
                                st.markdown("#### 📈 Technical Analysis")
                                col_ta1, col_ta2, col_ta3, col_ta4 = st.columns(4)
                                with col_ta1:
                                    st.metric("SMA 20", f"₹{ta.get('sma_20', 0):,.2f}")
                                with col_ta2:
                                    st.metric("SMA 50", f"₹{ta.get('sma_50', 0):,.2f}")
                                with col_ta3:
                                    st.metric("RSI", f"{ta.get('rsi', 0):.1f}")
                                with col_ta4:
                                    st.metric("Volatility", f"{ta.get('volatility', 0):.1f}%")
                                
                                if ta.get('trend'):
                                    trend_color = "🟢" if "UP" in ta['trend'] else "🔴" if "DOWN" in ta['trend'] else "🟡"
                                    st.info(f"{trend_color} **Trend:** {ta['trend']}")
                            
                            # Fundamental Analysis Details
                            if 'fundamental_analysis' in analysis:
                                fa = analysis['fundamental_analysis']
                                st.markdown("#### 💼 Fundamental Analysis")
                                col_fa1, col_fa2, col_fa3, col_fa4 = st.columns(4)
                                with col_fa1:
                                    pe = fa.get('pe_ratio', 0)
                                    st.metric("P/E Ratio", f"{pe:.2f}" if pe else "N/A")
                                with col_fa2:
                                    roe = fa.get('roe', 0)
                                    st.metric("ROE", f"{roe:.2f}%" if roe else "N/A")
                                with col_fa3:
                                    de = fa.get('debt_to_equity', 0)
                                    st.metric("D/E Ratio", f"{de:.2f}" if de else "N/A")
                                with col_fa4:
                                    cr = fa.get('current_ratio', 0)
                                    st.metric("Current Ratio", f"{cr:.2f}" if cr else "N/A")
                                
                                # Score breakdown
                                if fa.get('score_breakdown'):
                                    with st.expander("🧮 Score Calculation Breakdown"):
                                        sb = fa['score_breakdown']
                                        st.markdown(f"""
                                        - **P/E Score:** {sb.get('pe_score', 0):.1f}/30 pts
                                        - **ROE Score:** {sb.get('roe_score', 0):.1f}/30 pts  
                                        - **D/E Score:** {sb.get('de_score', 0):.1f}/20 pts
                                        - **Current Ratio Score:** {sb.get('cr_score', 0):.1f}/20 pts
                                        - **Total:** {fa.get('score', 0):.1f}/100 pts
                                        """)
                        
                        # SHOW DETAILED REASONING (Multi-paragraph format)
                        if 'reasoning' in pick and pick['reasoning']:
                            st.markdown("---")
                            st.markdown("### 🧠 Why This Stock?")
                            # Display as markdown to preserve formatting
                            st.markdown(pick['reasoning'])
                        
                        # DEEP INSIGHTS WITH CHARTS
                        st.markdown("---")
                        with st.spinner("Loading deep technical analysis..."):
                            try:
                                from database import get_db
                                db = next(get_db())
                                display_asset_deep_insights(pick['symbol'], pick, db)
                                db.close()
                            except Exception as e:
                                st.warning("📊 Advanced analytics temporarily unavailable")
            else:
                st.info("No stock recommendations available with current filters")
        
        # ETFs tab
        with tabs[1]:
            if 'etf' in picks and picks['etf']['picks']:
                for i, pick in enumerate(picks['etf']['picks'], 1):
                    with st.expander(f"#{i} - {pick['symbol']} - {pick['name'][:50]}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**💰 Investment Amount:** ₹{pick['allocation']:,.0f}")
                            st.markdown(f"**📊 Overall Score:** {pick['score']:.1f}/100")
                            st.markdown(f"**✅ Confidence:** {pick['confidence']:.0f}%")
                            if 'sector' in pick and pick['sector']:
                                st.markdown(f"**🏢 Sector:** {pick['sector']}")
                        with col2:
                            st.markdown("**Component Scores:**")
                            st.markdown(f"- 📈 Technical: {pick['technical']:.0f}")
                            st.markdown(f"- 💼 Fundamental: {pick['fundamental']:.0f}")
                            st.markdown(f"- 📰 Sentiment: {pick['sentiment']:.0f}")
                            st.markdown(f"- ⚠️ Risk: {pick['risk']:.0f}")
                        
                        # SHOW PROFESSIONAL ANALYSIS DATA IF AVAILABLE
                        if 'professional_analysis' in pick:
                            st.markdown("---")
                            st.markdown("### 📊 Professional Analysis Report")
                            analysis = pick['professional_analysis']
                            
                            # Data Quality
                            if 'data_quality' in analysis:
                                dq = analysis['data_quality']
                                col_dq1, col_dq2 = st.columns(2)
                                with col_dq1:
                                    st.metric("📰 News Articles", f"{dq.get('news_count', 0)} articles")
                                with col_dq2:
                                    st.metric("📈 Price Data", f"{dq.get('price_points', 0)} points")
                            
                            # Technical Analysis
                            if 'technical_analysis' in analysis:
                                ta = analysis['technical_analysis']
                                st.markdown("#### 📈 Technical Indicators")
                                col_ta1, col_ta2, col_ta3 = st.columns(3)
                                with col_ta1:
                                    st.metric("SMA 20", f"₹{ta.get('sma_20', 0):,.2f}")
                                with col_ta2:
                                    st.metric("RSI", f"{ta.get('rsi', 0):.1f}")
                                with col_ta3:
                                    st.metric("Volatility", f"{ta.get('volatility', 0):.1f}%")
                        
                        # SHOW DETAILED REASONING (Multi-paragraph format)
                        if 'reasoning' in pick and pick['reasoning']:
                            st.markdown("---")
                            st.markdown("### 🧠 Why This ETF?")
                            st.markdown(pick['reasoning'])
            else:
                st.info("No ETF recommendations available with current filters")
        
        # Mutual Funds tab
        with tabs[2]:
            if 'mutual_fund' in picks and picks['mutual_fund']['picks']:
                for i, pick in enumerate(picks['mutual_fund']['picks'], 1):
                    with st.expander(f"#{i} - {pick['symbol']} - {pick['name'][:50]}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**💰 Investment Amount:** ₹{pick['allocation']:,.0f}")
                            st.markdown(f"**📊 Overall Score:** {pick['score']:.1f}/100")
                            st.markdown(f"**✅ Confidence:** {pick['confidence']:.0f}%")
                            if 'sector' in pick and pick['sector']:
                                st.markdown(f"**🏢 Sector:** {pick['sector']}")
                        with col2:
                            st.markdown("**Component Scores:**")
                            st.markdown(f"- 📈 Technical: {pick['technical']:.0f}")
                            st.markdown(f"- 💼 Fundamental: {pick['fundamental']:.0f}")
                            st.markdown(f"- 📰 Sentiment: {pick['sentiment']:.0f}")
                            st.markdown(f"- ⚠️ Risk: {pick['risk']:.0f}")
                        
                        # SHOW PROFESSIONAL ANALYSIS DATA IF AVAILABLE
                        if 'professional_analysis' in pick:
                            st.markdown("---")
                            st.markdown("### 📊 Professional Analysis Report")
                            analysis = pick['professional_analysis']
                            
                            # Data Quality
                            if 'data_quality' in analysis:
                                dq = analysis['data_quality']
                                col_dq1, col_dq2 = st.columns(2)
                                with col_dq1:
                                    st.metric("📰 News Articles", f"{dq.get('news_count', 0)} articles")
                                with col_dq2:
                                    st.metric("📈 NAV History", f"{dq.get('price_points', 0)} points")
                        
                        # SHOW DETAILED REASONING (Multi-paragraph format)
                        if 'reasoning' in pick and pick['reasoning']:
                            st.markdown("---")
                            st.markdown("### 🧠 Why This Fund?")
                            st.markdown(pick['reasoning'])
            else:
                st.info("No mutual fund recommendations available with current filters")
        
        # Crypto tab
        with tabs[3]:
            if 'crypto' in picks and picks['crypto']['picks']:
                for i, pick in enumerate(picks['crypto']['picks'], 1):
                    with st.expander(f"#{i} - {pick['symbol']} - {pick['name'][:50]}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**💰 Investment Amount:** ₹{pick['allocation']:,.0f}")
                            st.markdown(f"**📊 Overall Score:** {pick['score']:.1f}/100")
                            st.markdown(f"**✅ Confidence:** {pick['confidence']:.0f}%")
                        with col2:
                            st.markdown("**Component Scores:**")
                            st.markdown(f"- 📈 Technical: {pick['technical']:.0f}")
                            st.markdown(f"- 💼 Fundamental: {pick['fundamental']:.0f}")
                            st.markdown(f"- 📰 Sentiment: {pick['sentiment']:.0f}")
                            st.markdown(f"- ⚠️ Risk: {pick['risk']:.0f}")
                        
                        # SHOW DETAILED REASONING
                        if 'reasoning' in pick and pick['reasoning']:
                            st.markdown("---")
                            st.markdown("**🧠 Why This Crypto?**")
                            st.info(pick['reasoning'])
            else:
                st.info("No crypto recommendations available with current filters")
        
        # Fixed Deposit tab
        with tabs[4]:
            if 'fd' in picks and picks['fd']['picks']:
                for pick in picks['fd']['picks']:
                    st.success(f"**{pick['name']}**")
                    st.markdown(f"**💰 Investment Amount:** ₹{pick['allocation']:,.0f}")
                    st.markdown(f"**🧠 Reasoning:** {pick['reasoning']}")
            else:
                st.info("No fixed deposit allocation")
        
        st.markdown("---")
        
        # AI Reasoning
        st.subheader("🤖 AI Portfolio Reasoning (FinGPT)")
        st.markdown(reasoning)
        
        # Export option
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Generate New Portfolio", use_container_width=True):
                del st.session_state['portfolio']
                st.rerun()
        with col2:
            # Create export data
            export_text = f"""
LUMIA PORTFOLIO ALLOCATION
{'='*60}

PROFILE:
Capital: ₹{meta['capital']:,.0f}
Risk Appetite: {meta['risk_appetite']}% ({meta['risk_profile']})
Generated: {meta['generated_at']}

ALLOCATION:
"""
            for asset_type, data in alloc.items():
                label = asset_type.upper().replace('_', ' ')
                export_text += f"{label}: {data['percentage']}% (₹{data['amount']:,.0f})\n"
            
            export_text += f"\n{reasoning}"
            
            st.download_button(
                label="📥 Download Report",
                data=export_text,
                file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    else:
        # Welcome screen for portfolio builder
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2 style="background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 700;">Configure Your Investment Strategy</h2>
            <p style="font-size: 1.1rem; color: #94a3b8; margin: 1rem 0;">Enter your investment preferences in the sidebar to generate a personalized portfolio</p>
            <br>
            <div style="text-align: left; max-width: 800px; margin: 0 auto; padding: 2.5rem; background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; backdrop-filter: blur(10px);">
                <h3 style="background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.5rem; margin-bottom: 1.5rem;">Professional Portfolio Builder</h3>
                <p style="line-height: 1.8; color: #cbd5e1; margin-bottom: 2rem;">Our AI-powered system analyzes thousands of assets to build comprehensive investment strategies tailored to your risk profile and financial goals.</p>
                
                <h4 style="color: #3b82f6; font-size: 1.1rem; margin: 1.5rem 0 1rem 0;">Key Features</h4>
                <ul style="line-height: 2; color: #cbd5e1; list-style: none; padding-left: 0;">
                    <li style="padding: 0.5rem 0; border-left: 3px solid #3b82f6; padding-left: 1rem; margin: 0.5rem 0;"><strong style="color: #3b82f6;">Multi-Asset Allocation</strong><br/>
                    Automatically distributes capital across Stocks, ETFs, Mutual Funds, Fixed Deposits, and Cryptocurrencies</li>
                    <li style="padding: 0.5rem 0; border-left: 3px solid #06b6d4; padding-left: 1rem; margin: 0.5rem 0;"><strong style="color: #06b6d4;">Risk-Based Strategy</strong><br/>
                    Allocation dynamically adjusts based on your risk tolerance and investment horizon</li>
                    <li style="padding: 0.5rem 0; border-left: 3px solid #3b82f6; padding-left: 1rem; margin: 0.5rem 0;"><strong style="color: #3b82f6;">Specific Recommendations</strong><br/>
                    Top picks in each asset category with exact investment amounts and reasoning</li>
                    <li style="padding: 0.5rem 0; border-left: 3px solid #06b6d4; padding-left: 1rem; margin: 0.5rem 0;"><strong style="color: #06b6d4;">AI-Powered Analysis</strong><br/>
                    Advanced algorithms analyze fundamentals, technicals, and market sentiment</li>
                </ul>
                <br>
                <h4 style="color: #3b82f6; font-size: 1.1rem; margin: 1.5rem 0 1rem 0;">Risk-Based Allocation Models</h4>
                <table style="width: 100%; margin-top: 1rem; border-collapse: collapse;">
                    <tr style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2);">
                        <th style="padding: 1rem; text-align: left; color: #3b82f6; font-weight: 600;">Risk Profile</th>
                        <th style="padding: 1rem; text-align: center; color: #3b82f6; font-weight: 600;">Equity</th>
                        <th style="padding: 1rem; text-align: center; color: #3b82f6; font-weight: 600;">Debt</th>
                        <th style="padding: 1rem; text-align: center; color: #3b82f6; font-weight: 600;">Expected Returns</th>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <td style="padding: 0.8rem; color: #cbd5e1;">Conservative (0-30%)</td>
                        <td style="padding: 0.8rem; text-align: center; color: #94a3b8;">35%</td>
                        <td style="padding: 0.8rem; text-align: center; color: #94a3b8;">60%</td>
                        <td style="padding: 0.8rem; text-align: center; color: #22c55e;">6-9% p.a.</td>
                    </tr>
                    <tr style="background: rgba(255, 255, 255, 0.02); border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <td style="padding: 0.8rem; color: #cbd5e1;">Moderate (31-60%)</td>
                        <td style="padding: 0.8rem; text-align: center; color: #94a3b8;">55%</td>
                        <td style="padding: 0.8rem; text-align: center; color: #94a3b8;">40%</td>
                        <td style="padding: 0.8rem; text-align: center; color: #22c55e;">9-13% p.a.</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <td style="padding: 0.8rem; color: #cbd5e1;">Aggressive (61-100%)</td>
                        <td style="padding: 0.8rem; text-align: center; color: #94a3b8;">75%</td>
                        <td style="padding: 0.8rem; text-align: center; color: #94a3b8;">20%</td>
                        <td style="padding: 0.8rem; text-align: center; color: #22c55e;">13-18% p.a.</td>
                    </tr>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    init_session_state()
    
    # Check database connection on startup
    if not st.session_state.db_connected:
        is_connected, message = check_database_connection()
        st.session_state.db_connected = is_connected
        if not is_connected:
            st.error(f"Database Connection Failed: {message}")
            st.info("Please ensure your database is running and configured correctly.")
            return
    
    st.markdown("""
    <div class="main-header">
        <h1>Lumia Investment Advisory</h1>
        <p>Professional Portfolio Management & Asset Analysis | 2,200+ Assets Analyzed</p>
    </div>
    """, unsafe_allow_html=True)
    
    # TOP LEVEL PAGE SELECTOR
    page = st.sidebar.radio(
        "Navigation",
        ["Asset Screener", "Portfolio Builder"],
        index=0,
        key="page_selector",
        help="Choose between individual asset analysis or complete portfolio allocation"
    )
    
    if page == "Portfolio Builder":
        display_portfolio_builder()
    else:
        display_asset_screener()


if __name__ == "__main__":
    main()
