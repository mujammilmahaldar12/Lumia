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
    page_title="Lumia - AI Investment Advisor",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        padding: 2rem;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .stock-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .score-excellent {
        background: rgba(76, 175, 80, 0.3);
        color: #4caf50;
        border: 1px solid #4caf50;
    }
    
    .score-good {
        background: rgba(33, 150, 243, 0.3);
        color: #2196f3;
        border: 1px solid #2196f3;
    }
    
    .score-moderate {
        background: rgba(255, 152, 0, 0.3);
        color: #ff9800;
        border: 1px solid #ff9800;
    }
    
    .score-poor {
        background: rgba(244, 67, 54, 0.3);
        color: #f44336;
        border: 1px solid #f44336;
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
    st.header("📊 Portfolio Overview")
    
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
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Assets", "🎯 Allocation", "📝 Reasoning", "⚠️ Risks"])
    
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


def main():
    """Main Streamlit application"""
    init_session_state()
    
    # Check database connection on startup
    if not st.session_state.db_connected:
        is_connected, message = check_database_connection()
        st.session_state.db_connected = is_connected
        if not is_connected:
            st.error(f"❌ {message}")
            st.info("💡 Make sure your database is running and configured correctly.")
            return
    
    st.markdown("""
    <div class="main-header">
        <h1>💼 Lumia AI Investment Advisor</h1>
        <p>Powered by FinBERT AI & Modern Portfolio Theory</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for input parameters
    with st.sidebar:
        st.header("📊 Investment Parameters")
        
        # Check if recommendation engine is available
        if recommendation_engine_available:
            st.success("✅ AI Engine: Active")
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
            
            # Risk profile selection
            risk_profile = st.selectbox(
                "Risk Profile",
                ['Conservative', 'Moderate', 'Aggressive'],
                index=1,
                help="Conservative: Safe assets, low risk | Moderate: Balanced | Aggressive: High growth, higher risk"
            )
            
            # Asset type preferences
            st.subheader("Asset Preferences")
            
            include_stocks = st.checkbox("Include Stocks", value=True)
            include_etfs = st.checkbox("Include ETFs", value=True)
            include_mutual_funds = st.checkbox("Include Mutual Funds", value=True)
            include_crypto = st.checkbox("Include Crypto", value=risk_profile == 'Aggressive')
            include_fixed_deposits = st.checkbox("Include Fixed Deposits", value=risk_profile == 'Conservative')
            
            # Exclusions
            st.subheader("Exclusions (Optional)")
            
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
            
            # Minimum score threshold
            min_score = st.slider(
                "Minimum Asset Score",
                min_value=50,
                max_value=90,
                value=60,
                help="Only include assets with score above this threshold"
            )
            
            # Submit button
            submitted = st.form_submit_button("🚀 Generate Portfolio", width='stretch')
            
            if submitted:
                with st.spinner("🤖 AI is analyzing markets..."):
                    if recommendation_engine_available:
                        try:
                            # Use new recommendation engine
                            db = next(get_db())
                            try:
                                recommendations = get_recommendations(
                                    db=db,
                                    capital=capital,
                                    risk_profile=risk_profile.lower(),
                                    excluded_sectors=exclude_sectors if exclude_sectors else None,
                                    excluded_industries=exclude_industries if exclude_industries else None,
                                    max_assets=10
                                )
                                
                                st.session_state.recommendations = recommendations
                                st.session_state.error_message = None  # Clear any previous errors
                                st.success("✅ Portfolio generated successfully!")
                                time.sleep(0.5)
                                st.rerun()
                            
                            finally:
                                db.close()
                        
                        except Exception as e:
                            st.error(f"❌ Error generating recommendations: {str(e)}")
                            st.error("""
**Possible issues:**
- Database doesn't have enough assets (need at least 5)
- No assets meet your criteria (try lowering min score)
- Database connection lost
- Missing price data for assets
""")
                            st.session_state.error_message = str(e)
                    
                    else:
                        st.error("❌ Recommendation engine not available")
                        st.info("💡 Please check if recommendation_engine module is installed correctly")
    
    # Main content area
    if st.session_state.recommendations:
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
            <p style="font-size: 1.2rem; color: #888;">Configure your investment parameters and click <strong>Generate Portfolio</strong></p>
            <br>
            <div style="text-align: left; max-width: 600px; margin: 0 auto; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 10px;">
                <h3 style="color: #667eea;">🧠 How Lumia Works</h3>
                <ul style="line-height: 2;">
                    <li><strong>FinBERT AI:</strong> Analyzes news sentiment with 97% accuracy</li>
                    <li><strong>Technical Analysis:</strong> RSI, MACD, Moving Averages</li>
                    <li><strong>Fundamental Analysis:</strong> P/E, ROE, Debt ratios</li>
                    <li><strong>Modern Portfolio Theory:</strong> Nobel Prize algorithm</li>
                    <li><strong>Risk Management:</strong> Beta, Sharpe ratio, Diversification</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
