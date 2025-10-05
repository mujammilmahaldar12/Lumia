"""
REASONING ENGINE - Generate Human-Readable Explanations

This module generates detailed explanations for WHY each asset was recommended.
The goal is to make the AI's decision-making transparent and trustworthy.

KEY PRINCIPLE:
"Show your work" - Like a math teacher, we explain every step:
1. What data we analyzed
2. What patterns we found
3. Why those patterns matter
4. What risks exist
5. What outcome we expect

This builds user trust and helps them learn about investing.
"""

from typing import Dict, List
from datetime import datetime


# ============================================================================
# RECOMMENDATION REASONING
# ============================================================================

def generate_asset_reasoning(asset_data: Dict) -> str:
    """
    Generate detailed reasoning for a single asset recommendation
    
    REASONING STRUCTURE:
    1. Introduction - Asset name and overall score
    2. Technical Analysis - Price patterns and momentum
    3. Fundamental Analysis - Financial health metrics
    4. Market Sentiment - News analysis and investor mood
    5. Risk Assessment - Volatility and drawdown analysis
    6. Allocation Rationale - Why this % of portfolio
    7. Risk Warnings - What could go wrong
    8. Expected Outcome - Target returns and timeline
    
    Args:
        asset_data: Dictionary with asset, scores, analysis, allocation
    
    Returns:
        Formatted reasoning text
    """
    asset = asset_data['asset']
    score = asset_data['score']
    analysis = asset_data['analysis']
    allocation_pct = asset_data.get('allocation_pct', 0)
    capital = asset_data.get('capital_allocated', 0)
    
    # Extract analysis components
    technical = analysis.get('technical', {})
    fundamental = analysis.get('fundamental', {})
    sentiment = analysis.get('sentiment', {})
    risk = analysis.get('risk', {})
    
    reasoning = []
    
    # 1. INTRODUCTION
    reasoning.append(f"## {asset.name} ({asset.symbol})")
    reasoning.append(f"**Overall Score: {score:.1f}/100** {'🟢' if score >= 75 else '🟡' if score >= 60 else '🔴'}")
    reasoning.append(f"**Allocation: {allocation_pct:.1f}% (₹{capital:,.0f})**")
    reasoning.append(f"**Asset Type: {asset.type.upper()}** | **Sector: {asset.sector or 'N/A'}**")
    reasoning.append("")
    
    # 2. TECHNICAL ANALYSIS
    reasoning.append("### 📈 Technical Analysis")
    reasoning.append(f"**Score: {technical.get('technical_score', 0):.1f}/100**")
    reasoning.append("")
    
    tech_breakdown = technical.get('breakdown', {})
    tech_scores = technical.get('individual_scores', {})
    
    # Moving Average
    ma_signal = tech_breakdown.get('ma_signal', '')
    if ma_signal:
        reasoning.append(f"- **Moving Average:** {ma_signal}")
        if 'Bullish' in ma_signal:
            reasoning.append(f"  *The 50-day moving average is above the 200-day (Golden Cross), indicating strong upward momentum.*")
        reasoning.append("")
    
    # RSI
    rsi_info = tech_breakdown.get('rsi', '')
    if rsi_info:
        reasoning.append(f"- **RSI (Relative Strength Index):** {rsi_info}")
        if 'Oversold' in rsi_info:
            reasoning.append(f"  *The asset is oversold, suggesting it may be undervalued - a good buying opportunity.*")
        elif 'Overbought' in rsi_info:
            reasoning.append(f"  *The asset is overbought - caution advised as a correction may occur.*")
        reasoning.append("")
    
    # MACD
    macd_info = tech_breakdown.get('macd', '')
    if macd_info:
        reasoning.append(f"- **MACD:** {macd_info}")
        if 'Bullish' in macd_info:
            reasoning.append(f"  *MACD line crossed above signal line, confirming bullish momentum.*")
        reasoning.append("")
    
    # Momentum
    momentum_info = tech_breakdown.get('momentum', '')
    if momentum_info:
        reasoning.append(f"- **3-Month Momentum:** {momentum_info}")
        reasoning.append("")
    
    # 3. FUNDAMENTAL ANALYSIS
    reasoning.append("### 💰 Fundamental Analysis")
    reasoning.append(f"**Score: {fundamental.get('fundamental_score', 0):.1f}/100**")
    reasoning.append("")
    
    fund_breakdown = fundamental.get('breakdown', {})
    
    # P/E Ratio
    pe_info = fund_breakdown.get('pe_ratio', '')
    if pe_info and 'Not available' not in pe_info:
        reasoning.append(f"- **P/E Ratio:** {pe_info}")
        if 'Undervalued' in pe_info:
            reasoning.append(f"  *Lower P/E suggests the stock is trading at a discount compared to earnings.*")
        reasoning.append("")
    
    # Revenue Growth
    revenue_info = fund_breakdown.get('revenue_growth', '')
    if revenue_info and 'Not available' not in revenue_info:
        reasoning.append(f"- **Revenue Growth:** {revenue_info}")
        if 'Excellent' in revenue_info or 'Strong' in revenue_info:
            reasoning.append(f"  *Strong revenue growth indicates expanding market share and business success.*")
        reasoning.append("")
    
    # Profit Margin
    profit_info = fund_breakdown.get('profit_margin', '')
    if profit_info and 'Not available' not in profit_info:
        reasoning.append(f"- **Profit Margin:** {profit_info}")
        if 'Excellent' in profit_info:
            reasoning.append(f"  *High profit margins demonstrate operational efficiency and pricing power.*")
        reasoning.append("")
    
    # Debt Ratio
    debt_info = fund_breakdown.get('debt_ratio', '')
    if debt_info and 'Not available' not in debt_info:
        reasoning.append(f"- **Debt-to-Equity Ratio:** {debt_info}")
        if 'Low debt' in debt_info:
            reasoning.append(f"  *Low debt levels reduce financial risk and provide flexibility for growth.*")
        elif 'High debt' in debt_info:
            reasoning.append(f"  *⚠️ Higher debt levels increase financial risk during economic downturns.*")
        reasoning.append("")
    
    # ROE
    roe_info = fund_breakdown.get('roe', '')
    if roe_info and 'Not available' not in roe_info:
        reasoning.append(f"- **Return on Equity (ROE):** {roe_info}")
        if 'Excellent' in roe_info:
            reasoning.append(f"  *High ROE indicates management is efficiently using shareholders' equity to generate profits.*")
        reasoning.append("")
    
    # 4. MARKET SENTIMENT
    reasoning.append("### 📰 Market Sentiment (AI Analysis)")
    reasoning.append(f"**Score: {sentiment.get('sentiment_score', 0):.1f}/100**")
    reasoning.append("")
    
    positive_count = sentiment.get('positive_count', 0)
    negative_count = sentiment.get('negative_count', 0)
    neutral_count = sentiment.get('neutral_count', 0)
    total_articles = positive_count + negative_count + neutral_count
    recent_sentiment = sentiment.get('recent_sentiment', 'Unknown')
    
    if total_articles > 0:
        reasoning.append(f"- **News Analysis:** Analyzed {total_articles} recent articles using FinBERT AI")
        reasoning.append(f"  - Positive: {positive_count} ({positive_count/total_articles*100:.0f}%)")
        reasoning.append(f"  - Neutral: {neutral_count} ({neutral_count/total_articles*100:.0f}%)")
        reasoning.append(f"  - Negative: {negative_count} ({negative_count/total_articles*100:.0f}%)")
        reasoning.append(f"- **Overall Sentiment:** {recent_sentiment}")
        reasoning.append("")
        
        if positive_count > negative_count * 2:
            reasoning.append(f"  *Predominantly positive news coverage suggests strong market confidence.*")
        elif negative_count > positive_count:
            reasoning.append(f"  *⚠️ Negative news sentiment may indicate near-term headwinds.*")
        reasoning.append("")
    else:
        reasoning.append("- **News Analysis:** Limited recent news coverage")
        reasoning.append("")
    
    # 5. RISK ASSESSMENT
    reasoning.append("### ⚠️ Risk Assessment")
    reasoning.append(f"**Score: {risk.get('risk_score', 0):.1f}/100** *(Higher = Lower Risk)*")
    reasoning.append("")
    
    risk_breakdown = risk.get('breakdown', {})
    
    # Beta
    beta_info = risk_breakdown.get('beta', '')
    if beta_info:
        reasoning.append(f"- **Beta:** {beta_info}")
        if 'Low volatility' in beta_info:
            reasoning.append(f"  *Lower volatility than market average makes this a more stable investment.*")
        reasoning.append("")
    
    # Drawdown
    drawdown_info = risk_breakdown.get('drawdown', '')
    if drawdown_info:
        reasoning.append(f"- **Maximum Drawdown:** {drawdown_info}")
        if 'Low drawdown' in drawdown_info:
            reasoning.append(f"  *Small historical declines indicate stability and resilience.*")
        elif 'High drawdown' in drawdown_info:
            reasoning.append(f"  *⚠️ Significant historical declines suggest higher volatility risk.*")
        reasoning.append("")
    
    # Volatility
    vol_info = risk_breakdown.get('volatility', '')
    if vol_info:
        reasoning.append(f"- **Volatility:** {vol_info}")
        reasoning.append("")
    
    # Sharpe Ratio
    sharpe_info = risk_breakdown.get('sharpe', '')
    if sharpe_info:
        reasoning.append(f"- **Sharpe Ratio:** {sharpe_info}")
        if 'Excellent' in sharpe_info:
            reasoning.append(f"  *Strong risk-adjusted returns - you're being well compensated for the risk taken.*")
        reasoning.append("")
    
    # 6. ALLOCATION RATIONALE
    reasoning.append("### 🎯 Allocation Rationale")
    reasoning.append(f"We allocated **{allocation_pct:.1f}%** of your portfolio to this asset because:")
    reasoning.append("")
    
    if allocation_pct > 15:
        reasoning.append(f"- **Core Holding:** High score ({score:.0f}/100) and strong fundamentals make this a core position")
    elif allocation_pct > 10:
        reasoning.append(f"- **Significant Position:** Good score ({score:.0f}/100) warrants meaningful allocation")
    else:
        reasoning.append(f"- **Diversification Play:** Adds sector/asset type diversity to portfolio")
    
    reasoning.append(f"- **Risk Balance:** Fits your risk profile and enhances portfolio diversification")
    reasoning.append(f"- **Sector Exposure:** Provides exposure to {asset.sector or 'this sector'}")
    reasoning.append("")
    
    # 7. RISK WARNINGS
    reasoning.append("### ⚠️ Risk Warnings")
    reasoning.append("")
    
    warnings = []
    
    # Check for high debt
    if 'High debt' in debt_info:
        warnings.append("- **High Debt Levels:** Financial leverage increases risk during market downturns")
    
    # Check for overbought
    if 'Overbought' in rsi_info:
        warnings.append("- **Overbought Condition:** May experience short-term price correction")
    
    # Check for negative sentiment
    if negative_count > positive_count:
        warnings.append("- **Negative Sentiment:** Recent news is predominantly negative")
    
    # Check for high volatility
    if 'High' in vol_info and 'Risky' in vol_info:
        warnings.append("- **High Volatility:** Expect larger price swings")
    
    # Market risk
    warnings.append(f"- **Market Risk:** All investments carry risk of loss; past performance doesn't guarantee future results")
    
    # Asset-specific risks
    if asset.type == 'crypto':
        warnings.append("- **Crypto Risk:** Highly volatile and speculative; regulatory changes could impact value")
    elif asset.type == 'stock':
        warnings.append("- **Company Risk:** Individual stock performance depends on company execution and industry trends")
    
    for warning in warnings:
        reasoning.append(warning)
    reasoning.append("")
    
    # 8. EXPECTED OUTCOME
    reasoning.append("### 📊 Expected Outcome")
    reasoning.append("")
    
    # Estimate expected return based on score
    if score >= 80:
        expected_return = "15-25%"
        outlook = "Strong potential for above-average returns"
    elif score >= 70:
        expected_return = "12-18%"
        outlook = "Good potential for solid returns"
    elif score >= 60:
        expected_return = "8-15%"
        outlook = "Moderate return expectations"
    else:
        expected_return = "5-10%"
        outlook = "Conservative return expectations"
    
    reasoning.append(f"- **Target Return:** {expected_return} annually")
    reasoning.append(f"- **Investment Horizon:** 12-36 months recommended")
    reasoning.append(f"- **Outlook:** {outlook}")
    reasoning.append(f"- **Projected Value:** ₹{capital:,.0f} → ₹{capital * 1.15:,.0f} (@ 15% return)")
    reasoning.append("")
    
    return "\n".join(reasoning)


# ============================================================================
# PORTFOLIO SUMMARY REASONING
# ============================================================================

def generate_portfolio_summary(portfolio_result: Dict) -> str:
    """
    Generate overall portfolio reasoning
    
    Explains:
    1. Portfolio composition
    2. Diversification strategy
    3. Risk-return profile
    4. Overall expected outcome
    
    Args:
        portfolio_result: Result from build_portfolio()
    
    Returns:
        Formatted portfolio summary
    """
    if not portfolio_result.get('success'):
        return "Portfolio could not be built: " + portfolio_result.get('error', 'Unknown error')
    
    portfolio = portfolio_result['portfolio']
    capital = portfolio_result['total_capital']
    risk_profile = portfolio_result['risk_profile']
    metrics = portfolio_result['metrics']
    
    summary = []
    
    # Header
    summary.append("# 🎯 YOUR PERSONALIZED INVESTMENT PORTFOLIO")
    summary.append("")
    summary.append("---")
    summary.append("")
    
    # Overview
    summary.append("## 📋 Portfolio Overview")
    summary.append("")
    summary.append(f"**Total Investment:** ₹{capital:,.0f}")
    summary.append(f"**Risk Profile:** {risk_profile.upper()}")
    summary.append(f"**Number of Assets:** {metrics['num_assets']}")
    summary.append(f"**Average Score:** {metrics['avg_score']:.1f}/100")
    summary.append(f"**Average Sentiment:** {metrics['avg_sentiment']:.1f}/100")
    summary.append("")
    
    # Asset breakdown
    summary.append("## 📊 Asset Allocation")
    summary.append("")
    
    # Count by type
    type_allocation = {}
    for item in portfolio:
        asset_type = item['asset'].type
        allocation = item.get('capital_allocated', 0)
        type_allocation[asset_type] = type_allocation.get(asset_type, 0) + allocation
    
    for asset_type, amount in sorted(type_allocation.items(), key=lambda x: x[1], reverse=True):
        pct = (amount / capital) * 100
        summary.append(f"- **{asset_type.upper()}:** ₹{amount:,.0f} ({pct:.1f}%)")
    summary.append("")
    
    # Sector diversification
    summary.append("## 🌐 Sector Diversification")
    summary.append("")
    
    sector_allocation = {}
    for item in portfolio:
        sector = item['asset'].sector or 'Other'
        allocation = item.get('capital_allocated', 0)
        sector_allocation[sector] = sector_allocation.get(sector, 0) + allocation
    
    for sector, amount in sorted(sector_allocation.items(), key=lambda x: x[1], reverse=True):
        pct = (amount / capital) * 100
        summary.append(f"- **{sector}:** ₹{amount:,.0f} ({pct:.1f}%)")
    summary.append("")
    
    # Strategy explanation
    summary.append("## 🎯 Investment Strategy")
    summary.append("")
    summary.append(f"Your portfolio was built using a **{risk_profile}** approach with these key strategies:")
    summary.append("")
    summary.append("1. **Modern Portfolio Theory (MPT):** Optimized allocation to maximize risk-adjusted returns")
    summary.append("2. **Diversification:** Spread across multiple sectors and asset types to reduce risk")
    summary.append("3. **AI-Powered Analysis:** Each asset analyzed using 4 scoring dimensions:")
    summary.append("   - Technical Analysis (price patterns, momentum)")
    summary.append("   - Fundamental Analysis (financial health, growth)")
    summary.append("   - Sentiment Analysis (AI-powered news analysis)")
    summary.append("   - Risk Analysis (volatility, drawdown)")
    summary.append("")
    
    # Risk-return profile
    summary.append("## ⚖️ Risk-Return Profile")
    summary.append("")
    
    if risk_profile == 'conservative':
        summary.append("**Conservative Strategy:**")
        summary.append("- Focus on capital preservation and stable returns")
        summary.append("- Lower volatility, less downside risk")
        summary.append("- Expected return: 8-12% annually")
        summary.append("- Suitable for: Risk-averse investors, near-term goals")
    elif risk_profile == 'moderate':
        summary.append("**Moderate Strategy:**")
        summary.append("- Balanced approach between growth and stability")
        summary.append("- Moderate volatility with controlled risk")
        summary.append("- Expected return: 12-18% annually")
        summary.append("- Suitable for: Most investors, medium-term goals")
    else:
        summary.append("**Aggressive Strategy:**")
        summary.append("- Focus on maximum growth potential")
        summary.append("- Higher volatility, greater upside potential")
        summary.append("- Expected return: 18-25% annually")
        summary.append("- Suitable for: Risk-tolerant investors, long-term goals")
    summary.append("")
    
    # Action items
    summary.append("## ✅ Next Steps")
    summary.append("")
    summary.append("1. **Review Each Recommendation:** Read the detailed reasoning for each asset below")
    summary.append("2. **Understand the Risks:** Pay attention to risk warnings for each holding")
    summary.append("3. **Monitor Regularly:** Review your portfolio monthly and rebalance quarterly")
    summary.append("4. **Stay Diversified:** Don't concentrate too much in any single asset")
    summary.append("5. **Think Long-Term:** Markets fluctuate; stay invested for your target timeline")
    summary.append("")
    summary.append("---")
    summary.append("")
    
    return "\n".join(summary)


# ============================================================================
# COMPLETE RECOMMENDATION REPORT
# ============================================================================

def generate_complete_report(portfolio_result: Dict) -> str:
    """
    Generate complete recommendation report
    
    Includes:
    1. Portfolio summary
    2. Individual asset reasoning (all assets)
    3. Disclaimer
    
    Args:
        portfolio_result: Result from build_portfolio()
    
    Returns:
        Complete formatted report
    """
    report = []
    
    # Portfolio summary
    report.append(generate_portfolio_summary(portfolio_result))
    
    # Individual recommendations
    report.append("# 📈 INDIVIDUAL ASSET RECOMMENDATIONS")
    report.append("")
    report.append("---")
    report.append("")
    
    for i, item in enumerate(portfolio_result['portfolio'], 1):
        report.append(f"## Recommendation #{i}")
        report.append("")
        report.append(generate_asset_reasoning(item))
        report.append("---")
        report.append("")
    
    # Disclaimer
    report.append("## ⚠️ Important Disclaimer")
    report.append("")
    report.append("This recommendation is generated by AI analysis and should be considered as educational information only.")
    report.append("- **Not Financial Advice:** This is not personalized financial advice. Consult a licensed financial advisor.")
    report.append("- **Past Performance:** Historical data does not guarantee future results.")
    report.append("- **Risk of Loss:** All investments carry risk of loss. Only invest what you can afford to lose.")
    report.append("- **Do Your Research:** Always conduct your own research before investing.")
    report.append("")
    report.append(f"*Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    return "\n".join(report)
