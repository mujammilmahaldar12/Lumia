"""
Streamlit Test UI for Lumia Portfolio Recommendation System.

This is a testing interface that allows users to interact with the recommendation
API and visualize portfolio suggestions.

Usage:
    streamlit run app/test_ui.py --server.port 8501
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


# Configuration
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Lumia Portfolio Recommendations",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 Lumia Portfolio Recommendation System")
    st.markdown("---")


def check_api_health() -> Dict[str, Any]:
    """Check if the recommendation API is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/recommend/health", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def display_health_status():
    """Display API health status in the sidebar."""
    with st.sidebar:
        st.subheader("🔧 System Status")
        
        health = check_api_health()
        
        if health.get("status") == "healthy":
            st.success("✅ API: Healthy")
        elif health.get("status") == "degraded":
            st.warning("⚠️ API: Degraded")
        else:
            st.error(f"❌ API: {health.get('message', 'Unknown error')}")
        
        # Display data freshness if available
        if "data_freshness" in health:
            freshness = health["data_freshness"]
            
            with st.expander("Data Freshness Details"):
                if freshness.get("warnings"):
                    for warning in freshness["warnings"]:
                        st.warning(f"⚠️ {warning}")
                
                if freshness.get("data_age"):
                    st.json(freshness["data_age"])
                
                if freshness.get("coverage"):
                    coverage = freshness["coverage"]
                    if "signals" in coverage:
                        sig_cov = coverage["signals"]
                        st.metric(
                            "Signal Coverage",
                            f"{sig_cov.get('coverage_percentage', 0):.1f}%",
                            f"{sig_cov.get('assets_with_signals', 0)} assets"
                        )


def get_user_inputs():
    """Get user inputs from the sidebar."""
    st.sidebar.subheader("💰 Investment Parameters")
    
    # Investment capital
    capital = st.sidebar.number_input(
        "Investment Capital ($)",
        min_value=1000.0,
        max_value=10000000.0,
        value=50000.0,
        step=1000.0,
        format="%.0f"
    )
    
    # Risk tolerance
    risk_labels = {
        0.2: "Very Conservative (20%)",
        0.4: "Conservative (40%)",
        0.5: "Balanced (50%)",
        0.6: "Moderate (60%)",
        0.8: "Aggressive (80%)",
        1.0: "Very Aggressive (100%)"
    }
    
    risk_value = st.sidebar.select_slider(
        "Risk Tolerance",
        options=list(risk_labels.keys()),
        value=0.5,
        format_func=lambda x: risk_labels[x]
    )
    
    # Investment horizon
    horizon = st.sidebar.slider(
        "Investment Horizon (Years)",
        min_value=1,
        max_value=30,
        value=5,
        step=1
    )
    
    # Expected growth
    expected_growth = st.sidebar.slider(
        "Expected Annual Growth (%)",
        min_value=3.0,
        max_value=25.0,
        value=8.0,
        step=0.5,
        format="%.1f%%"
    )
    
    # Exclusions
    st.sidebar.subheader("🚫 Exclusions")
    exclusions_text = st.sidebar.text_area(
        "Symbols to Exclude (comma-separated)",
        value="",
        placeholder="TSLA, GME, AMC",
        help="Enter stock symbols you want to exclude from recommendations"
    )
    
    exclusions = []
    if exclusions_text.strip():
        exclusions = [s.strip().upper() for s in exclusions_text.split(",") if s.strip()]
    
    return {
        "capital": capital,
        "risk": risk_value,
        "horizon_years": horizon,
        "expected_growth": expected_growth,
        "exclusions": exclusions
    }


def call_recommendation_api(params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Call the recommendation API with user parameters."""
    try:
        # Prepare API payload (exclude expected_growth as it's not in the API)
        api_params = {
            "capital": params["capital"],
            "risk": params["risk"],
            "horizon_years": params["horizon_years"],
            "exclusions": params["exclusions"]
        }
        
        with st.spinner("🤖 Generating AI-powered recommendations..."):
            response = requests.post(
                f"{API_BASE_URL}/api/recommend",
                json=api_params,
                timeout=API_TIMEOUT
            )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error("❌ No suitable assets found for recommendations. Try adjusting your criteria.")
            return None
        else:
            st.error(f"❌ API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. The system might be processing large datasets.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to API. Make sure the server is running on localhost:8000")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def display_portfolio_allocation(recommendations: Dict[str, Any], params: Dict[str, Any]):
    """Display portfolio allocation results."""
    buckets = recommendations["buckets"]
    total_allocated = recommendations["total_allocated"]
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Allocated", f"${total_allocated:,.0f}")
    
    with col2:
        allocation_pct = (total_allocated / params["capital"]) * 100
        st.metric("Allocation Rate", f"{allocation_pct:.1f}%")
    
    with col3:
        total_assets = len(buckets["stocks"]) + len(buckets["etfs"])
        st.metric("Total Assets", total_assets)
    
    with col4:
        expected_annual = params["expected_growth"] / 100 * total_allocated
        st.metric("Expected Annual Return", f"${expected_annual:,.0f}")
    
    # Portfolio composition charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Allocation by asset type
        type_data = []
        if buckets["stocks"]:
            stocks_total = sum(asset["allocated"] for asset in buckets["stocks"])
            type_data.append({"Type": "Stocks", "Allocation": stocks_total})
        
        if buckets["etfs"]:
            etfs_total = sum(asset["allocated"] for asset in buckets["etfs"])
            type_data.append({"Type": "ETFs", "Allocation": etfs_total})
        
        if type_data:
            df_types = pd.DataFrame(type_data)
            fig_pie = px.pie(
                df_types,
                values="Allocation",
                names="Type",
                title="Allocation by Asset Type"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Top allocations
        all_assets = buckets["stocks"] + buckets["etfs"]
        if all_assets:
            df_assets = pd.DataFrame(all_assets)
            df_top = df_assets.nlargest(8, "allocated")
            
            fig_bar = px.bar(
                df_top,
                x="allocated",
                y="symbol",
                orientation="h",
                title="Top Asset Allocations",
                labels={"allocated": "Allocation ($)", "symbol": "Symbol"}
            )
            fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_bar, use_container_width=True)


def display_detailed_breakdown(recommendations: Dict[str, Any]):
    """Display detailed asset breakdown."""
    buckets = recommendations["buckets"]
    
    # Stocks section
    if buckets["stocks"]:
        st.subheader("📈 Stock Allocations")
        
        stocks_data = []
        for asset in buckets["stocks"]:
            stocks_data.append({
                "Symbol": asset["symbol"],
                "Name": asset["name"][:40] + "..." if len(asset["name"]) > 40 else asset["name"],
                "Allocation": f"${asset['allocated']:,.0f}",
                "Percentage": f"{asset['percentage']:.1f}%",
                "Score": f"{asset['score']:.3f}",
                "Sentiment": f"{asset['breakdown'].get('sentiment', 0):.2f}",
                "Fundamental": f"{asset['breakdown'].get('fundamental', 0):.2f}",
                "Momentum": f"{asset['breakdown'].get('momentum', 0):.2f}",
                "Volatility": f"{asset['breakdown'].get('volatility', 0):.2f}"
            })
        
        df_stocks = pd.DataFrame(stocks_data)
        st.dataframe(df_stocks, use_container_width=True)
    
    # ETFs section
    if buckets["etfs"]:
        st.subheader("🏛️ ETF Allocations")
        
        etfs_data = []
        for asset in buckets["etfs"]:
            etfs_data.append({
                "Symbol": asset["symbol"],
                "Name": asset["name"][:40] + "..." if len(asset["name"]) > 40 else asset["name"],
                "Allocation": f"${asset['allocated']:,.0f}",
                "Percentage": f"{asset['percentage']:.1f}%",
                "Score": f"{asset['score']:.3f}",
                "Sentiment": f"{asset['breakdown'].get('sentiment', 0):.2f}",
                "Fundamental": f"{asset['breakdown'].get('fundamental', 0):.2f}",
                "Momentum": f"{asset['breakdown'].get('momentum', 0):.2f}",
                "Volatility": f"{asset['breakdown'].get('volatility', 0):.2f}"
            })
        
        df_etfs = pd.DataFrame(etfs_data)
        st.dataframe(df_etfs, use_container_width=True)


def display_risk_analysis(recommendations: Dict[str, Any], params: Dict[str, Any]):
    """Display risk analysis and scenario modeling."""
    st.subheader("⚠️ Risk Analysis")
    
    all_assets = recommendations["buckets"]["stocks"] + recommendations["buckets"]["etfs"]
    
    if not all_assets:
        st.warning("No assets to analyze")
        return
    
    # Risk metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution
        scores = [asset["score"] for asset in all_assets]
        allocations = [asset["allocated"] for asset in all_assets]
        
        weighted_score = sum(s * a for s, a in zip(scores, allocations)) / sum(allocations)
        
        st.metric("Portfolio Score", f"{weighted_score:.3f}")
        
        # Risk level indicator
        if params["risk"] <= 0.33:
            risk_level = "Conservative"
            risk_color = "🟢"
        elif params["risk"] <= 0.66:
            risk_level = "Balanced" 
            risk_color = "🟡"
        else:
            risk_level = "Aggressive"
            risk_color = "🔴"
        
        st.metric("Risk Profile", f"{risk_color} {risk_level}")
    
    with col2:
        # Diversification metrics
        num_assets = len(all_assets)
        max_allocation_pct = max(asset["percentage"] for asset in all_assets)
        
        st.metric("Diversification", f"{num_assets} assets")
        st.metric("Max Single Position", f"{max_allocation_pct:.1f}%")
    
    # Scenario analysis
    st.subheader("📊 Scenario Analysis")
    
    scenarios = {
        "Bull Market (+20%)": 1.20,
        "Normal Market (+8%)": 1.08,
        "Bear Market (-15%)": 0.85,
        "Crash (-30%)": 0.70
    }
    
    scenario_data = []
    for scenario_name, multiplier in scenarios.items():
        projected_value = recommendations["total_allocated"] * multiplier
        gain_loss = projected_value - params["capital"]
        gain_loss_pct = (gain_loss / params["capital"]) * 100
        
        scenario_data.append({
            "Scenario": scenario_name,
            "Portfolio Value": f"${projected_value:,.0f}",
            "Gain/Loss": f"${gain_loss:,.0f}",
            "Return %": f"{gain_loss_pct:+.1f}%"
        })
    
    df_scenarios = pd.DataFrame(scenario_data)
    st.dataframe(df_scenarios, use_container_width=True)


def display_explanation(recommendations: Dict[str, Any]):
    """Display AI explanation of the recommendations."""
    st.subheader("🤖 AI Explanation")
    
    explanation = recommendations.get("explanation_text", "No explanation available.")
    
    st.info(explanation)
    
    # Additional insights
    with st.expander("📋 Methodology Details"):
        st.markdown("""
        **How Recommendations Are Generated:**
        
        1. **Universe Building**: Active assets with recent signals and fundamental data
        2. **Signal Normalization**: All metrics normalized to 0-1 scale for fair comparison
        3. **Risk-Adjusted Scoring**: Weighted combination based on your risk profile:
           - Conservative: Emphasizes fundamentals and volatility
           - Balanced: Equal weight across all factors
           - Aggressive: Emphasizes sentiment and momentum
        4. **Capital Allocation**: Portfolio optimization with position sizing limits
        5. **Diversification**: Automatic spread across asset types and sectors
        
        **Data Sources:**
        - News sentiment analysis (FinBERT + VADER models)
        - Technical indicators and price momentum
        - Fundamental analysis scores
        - Market volatility metrics
        """)


def export_recommendations(recommendations: Dict[str, Any], params: Dict[str, Any]):
    """Provide export functionality for recommendations."""
    st.subheader("📁 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON export
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "parameters": params,
            "recommendations": recommendations
        }
        
        json_str = json.dumps(export_data, indent=2)
        st.download_button(
            label="📄 Download as JSON",
            data=json_str,
            file_name=f"lumia_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # CSV export
        all_assets = recommendations["buckets"]["stocks"] + recommendations["buckets"]["etfs"]
        
        if all_assets:
            df_export = pd.DataFrame([
                {
                    "Symbol": asset["symbol"],
                    "Name": asset["name"],
                    "Type": "Stock" if asset in recommendations["buckets"]["stocks"] else "ETF",
                    "Allocation_USD": asset["allocated"],
                    "Percentage": asset["percentage"],
                    "Score": asset["score"],
                    **asset["breakdown"]
                }
                for asset in all_assets
            ])
            
            csv_str = df_export.to_csv(index=False)
            st.download_button(
                label="📊 Download as CSV",
                data=csv_str,
                file_name=f"lumia_portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


def main():
    """Main Streamlit application."""
    configure_page()
    
    # Display health status
    display_health_status()
    
    # Get user inputs
    params = get_user_inputs()
    
    # Generate recommendations button
    if st.sidebar.button("🚀 Generate Recommendations", type="primary", use_container_width=True):
        recommendations = call_recommendation_api(params)
        
        if recommendations:
            # Store in session state for persistence
            st.session_state.recommendations = recommendations
            st.session_state.params = params
    
    # Display results if available
    if hasattr(st.session_state, 'recommendations') and st.session_state.recommendations:
        recommendations = st.session_state.recommendations
        params = st.session_state.params
        
        st.success("✅ Recommendations generated successfully!")
        
        # Main results tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Portfolio Overview", 
            "📋 Detailed Breakdown", 
            "⚠️ Risk Analysis", 
            "🤖 AI Explanation", 
            "📁 Export"
        ])
        
        with tab1:
            display_portfolio_allocation(recommendations, params)
        
        with tab2:
            display_detailed_breakdown(recommendations)
        
        with tab3:
            display_risk_analysis(recommendations, params)
        
        with tab4:
            display_explanation(recommendations)
        
        with tab5:
            export_recommendations(recommendations, params)
    
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to Lumia Portfolio Recommendations! 👋
        
        This AI-powered system provides personalized portfolio recommendations based on:
        
        - 📰 **Real-time news sentiment analysis**
        - 📈 **Technical price momentum indicators**  
        - 🏢 **Fundamental analysis scores**
        - ⚖️ **Risk-adjusted optimization**
        
        ### Getting Started:
        1. **Configure your parameters** in the sidebar
        2. **Set your risk tolerance** and investment horizon
        3. **Add any exclusions** (optional)
        4. **Click "Generate Recommendations"**
        
        ### System Features:
        - ✅ Real-time data freshness validation
        - 🤖 AI-powered sentiment analysis using FinBERT
        - 📊 Interactive portfolio visualization
        - 📁 Export capabilities (JSON/CSV)
        - ⚠️ Risk scenario analysis
        """)
        
        # Sample parameters display
        with st.expander("🔍 See Sample Parameters"):
            st.json({
                "capital": 50000,
                "risk": 0.5,
                "horizon_years": 5,
                "exclusions": ["TSLA", "GME"]
            })


if __name__ == "__main__":
    main()