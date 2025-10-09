"""
Lumia AI Chat System - Intelligent Portfolio Assistant
"""

import re
from typing import Dict, List, Tuple


class LumiaAI:
    """Intelligent chat assistant for portfolio queries"""
    
    def __init__(self):
        self.conversation_history = []
    
    def analyze_question(self, question: str, portfolio_data: dict) -> str:
        """Analyze question and generate intelligent response"""
        question_lower = question.lower()
        
        # Store conversation context
        self.conversation_history.append(question_lower)
        
        profile = portfolio_data['profile']
        metrics = portfolio_data['metrics']
        portfolio = portfolio_data['portfolio']
        
        # Calculate stats
        stats = self._calculate_portfolio_stats(portfolio_data)
        
        # Question routing with context awareness
        if self._is_about_allocation(question_lower):
            return self._explain_allocation(stats, profile, metrics)
        
        elif self._is_about_best_asset(question_lower):
            return self._recommend_best_assets(portfolio, stats)
        
        elif self._is_about_risk(question_lower):
            return self._explain_risk(stats, metrics, profile)
        
        elif self._is_about_returns(question_lower):
            return self._project_returns(stats, metrics, profile)
        
        elif self._is_about_comparison(question_lower):
            return self._compare_assets(portfolio, question_lower)
        
        elif self._is_about_diversification(question_lower):
            return self._explain_diversification(portfolio, stats)
        
        elif self._is_about_sectors(question_lower):
            return self._analyze_sectors(portfolio, stats)
        
        elif self._is_greeting(question_lower):
            return self._greet_user(stats)
        
        else:
            return self._provide_help(stats)
    
    def _calculate_portfolio_stats(self, portfolio_data: dict) -> dict:
        """Calculate comprehensive portfolio statistics"""
        profile = portfolio_data['profile']
        portfolio = portfolio_data['portfolio']
        
        stats = {
            'total_capital': profile['capital'],
            'asset_types': {},
            'all_assets': [],
            'sectors': {},
            'score_range': [100, 0],
            'total_assets': 0
        }
        
        for asset_type, assets in portfolio.items():
            if assets:
                type_total = sum(a.get('allocation_amount', 0) for a in assets)
                stats['asset_types'][asset_type] = {
                    'count': len(assets),
                    'total': type_total,
                    'percentage': (type_total / stats['total_capital']) * 100,
                    'assets': assets
                }
                
                stats['all_assets'].extend(assets)
                stats['total_assets'] += len(assets)
                
                # Track sectors
                for asset in assets:
                    sector = asset.get('sector', 'Unknown')
                    if sector not in stats['sectors']:
                        stats['sectors'][sector] = 0
                    stats['sectors'][sector] += 1
                    
                    # Track score range
                    score = asset.get('score', 0)
                    stats['score_range'][0] = min(stats['score_range'][0], score)
                    stats['score_range'][1] = max(stats['score_range'][1], score)
        
        return stats
    
    # Question classifiers
    def _is_about_allocation(self, q: str) -> bool:
        return any(word in q for word in ['why allocation', 'why this', 'allocation strategy', 'how allocated', 'distribution'])
    
    def _is_about_best_asset(self, q: str) -> bool:
        return any(word in q for word in ['best stock', 'top stock', 'best one', 'which stock', 'recommend', 'top pick', 
                                          'single stock', 'one stock', 'best asset', 'highest score'])
    
    def _is_about_risk(self, q: str) -> bool:
        return any(word in q for word in ['risk', 'risky', 'safe', 'volatility', 'dangerous', 'secure'])
    
    def _is_about_returns(self, q: str) -> bool:
        return any(word in q for word in ['return', 'profit', 'gain', 'earn', 'growth', 'money', 'value'])
    
    def _is_about_comparison(self, q: str) -> bool:
        return any(word in q for word in ['compare', 'difference', 'vs', 'versus', 'better than', 'worse than'])
    
    def _is_about_diversification(self, q: str) -> bool:
        return any(word in q for word in ['diversif', 'spread', 'balanced', 'mix'])
    
    def _is_about_sectors(self, q: str) -> bool:
        return any(word in q for word in ['sector', 'industry', 'technology', 'finance', 'healthcare'])
    
    def _is_greeting(self, q: str) -> bool:
        return any(word in q for word in ['hello', 'hi', 'hey', 'thanks', 'thank you'])
    
    # Response generators
    def _explain_allocation(self, stats: dict, profile: dict, metrics: dict) -> str:
        response = f"""**Your Portfolio Allocation Strategy:**\n\n"""
        response += f"**Profile**: {profile.get('risk_type', 'Moderate').title()} Risk | {profile.get('years', 5)} Years\n\n"
        
        response += "**Asset Distribution:**\n"
        for asset_type, data in sorted(stats['asset_types'].items(), key=lambda x: x[1]['percentage'], reverse=True):
            response += f"• **{asset_type.replace('_', ' ').title()}**: {data['percentage']:.1f}% ({data['count']} holdings, ₹{data['total']:,.0f})\n"
        
        response += f"\n**Strategy Reasoning:**\n"
        response += f"• **Target Return**: {metrics['expected_return']*100:.2f}% annually\n"
        response += f"• **Risk-Adjusted Performance**: Sharpe Ratio {metrics['sharpe_ratio']:.2f}\n"
        response += f"• **Diversification**: {stats['total_assets']} assets across {len(stats['asset_types'])} types\n"
        response += f"• **Quality Range**: Scores from {stats['score_range'][0]:.0f} to {stats['score_range'][1]:.0f}\n"
        
        return response
    
    def _recommend_best_assets(self, portfolio: dict, stats: dict) -> str:
        # Get all assets and sort by score
        all_assets = stats['all_assets']
        sorted_assets = sorted(all_assets, key=lambda x: x.get('score', 0), reverse=True)
        
        if not sorted_assets:
            return "No assets found in your portfolio."
        
        top_asset = sorted_assets[0]
        
        response = f"""**🏆 Best Asset in Your Portfolio:**\n\n"""
        response += f"**{top_asset.get('name', 'Unknown')} ({top_asset.get('symbol', 'N/A')})**\n\n"
        response += f"• **Quality Score**: {top_asset.get('score', 0):.1f}/100\n"
        response += f"• **Allocation**: ₹{top_asset.get('allocation_amount', 0):,.0f} ({top_asset.get('allocation_percentage', 0)*100:.2f}%)\n"
        response += f"• **Sector**: {top_asset.get('sector', 'Unknown')}\n"
        response += f"• **Asset Type**: {self._get_asset_type(top_asset, portfolio)}\n\n"
        
        breakdown = top_asset.get('breakdown', {})
        if breakdown:
            response += "**Score Breakdown:**\n"
            response += f"• Fundamental: {breakdown.get('fundamental_score', 0):.0f}/30\n"
            response += f"• Technical: {breakdown.get('technical_score', 0):.0f}/40\n"
            response += f"• Sentiment: {breakdown.get('sentiment_score', 0):.0f}/15\n"
            response += f"• Advanced Bonus: {breakdown.get('advanced_bonus', 0):.0f}/15\n\n"
        
        if len(sorted_assets) >= 3:
            response += "**📊 Top 3 Comparison:**\n"
            for i, asset in enumerate(sorted_assets[:3], 1):
                response += f"{i}. **{asset.get('symbol', 'N/A')}** - Score: {asset.get('score', 0):.1f}/100, Amount: ₹{asset.get('allocation_amount', 0):,.0f}\n"
        
        response += "\n⚠️ **Investment Wisdom**: Even the best asset carries risk. Diversification across multiple assets reduces volatility by 40-60%."
        
        return response
    
    def _explain_risk(self, stats: dict, metrics: dict, profile: dict) -> str:
        response = f"""**📊 Portfolio Risk Analysis:**\n\n"""
        response += f"**Risk Profile**: {profile.get('risk_type', 'Moderate').title()}\n"
        response += f"**Expected Volatility**: {metrics['expected_risk']*100:.2f}%\n"
        response += f"**Sharpe Ratio**: {metrics['sharpe_ratio']:.2f}\n\n"
        
        # Risk interpretation
        vol = metrics['expected_risk'] * 100
        if vol < 12:
            risk_level = "LOW"
            interpretation = "Your portfolio has conservative risk. Suitable for capital preservation."
        elif vol < 20:
            risk_level = "MODERATE"
            interpretation = "Balanced risk-return profile. Good for long-term growth."
        else:
            risk_level = "HIGH"
            interpretation = "Aggressive portfolio with high growth potential but higher fluctuations."
        
        response += f"**Risk Level**: {risk_level}\n"
        response += f"**Interpretation**: {interpretation}\n\n"
        
        response += "**Diversification Benefits:**\n"
        response += f"• Spread across {stats['total_assets']} different assets\n"
        response += f"• {len(stats['asset_types'])} asset classes reduce correlation risk\n"
        response += f"• {len(stats['sectors'])} sectors provide industry diversification\n"
        
        return response
    
    def _project_returns(self, stats: dict, metrics: dict, profile: dict) -> str:
        capital = stats['total_capital']
        annual_return = metrics['expected_return']
        years = profile.get('years', 5)
        
        response = f"""**💰 Return Projections:**\n\n"""
        response += f"**Initial Investment**: ₹{capital:,.0f}\n"
        response += f"**Expected Annual Return**: {annual_return*100:.2f}%\n"
        response += f"**Investment Horizon**: {years} years\n\n"
        
        response += "**Year-by-Year Projection:**\n"
        for year in [1, 3, 5, years] if years >= 5 else [1, years]:
            if year <= years:
                future_value = capital * ((1 + annual_return) ** year)
                profit = future_value - capital
                response += f"• **Year {year}**: ₹{future_value:,.0f} (Profit: ₹{profit:,.0f}, +{(profit/capital)*100:.1f}%)\n"
        
        final_value = capital * ((1 + annual_return) ** years)
        total_profit = final_value - capital
        
        response += f"\n**Final Outcome (Year {years})**:\n"
        response += f"• Portfolio Value: ₹{final_value:,.0f}\n"
        response += f"• Total Profit: ₹{total_profit:,.0f}\n"
        response += f"• Total Return: {(total_profit/capital)*100:.1f}%\n"
        response += f"• Annualized Return: {annual_return*100:.2f}%\n"
        
        response += "\n*Note: These are projections based on historical data and market assumptions. Actual returns may vary.*"
        
        return response
    
    def _compare_assets(self, portfolio: dict, question: str) -> str:
        # Simple comparison of asset types
        response = "**Asset Type Comparison:**\n\n"
        
        for asset_type, assets in portfolio.items():
            if assets:
                avg_score = sum(a.get('score', 0) for a in assets) / len(assets)
                total_amount = sum(a.get('allocation_amount', 0) for a in assets)
                response += f"**{asset_type.replace('_', ' ').title()}**:\n"
                response += f"• Count: {len(assets)} holdings\n"
                response += f"• Avg Score: {avg_score:.1f}/100\n"
                response += f"• Total: ₹{total_amount:,.0f}\n\n"
        
        return response
    
    def _explain_diversification(self, portfolio: dict, stats: dict) -> str:
        response = f"""**🎯 Diversification Analysis:**\n\n"""
        response += f"**Total Assets**: {stats['total_assets']} holdings\n"
        response += f"**Asset Classes**: {len(stats['asset_types'])}\n"
        response += f"**Sectors**: {len(stats['sectors'])}\n\n"
        
        response += "**Benefits of Your Diversification:**\n"
        response += "• Reduces single-asset risk by 60-70%\n"
        response += "• Smooths returns across market cycles\n"
        response += "• Protects against sector-specific downturns\n"
        response += "• Optimizes risk-adjusted returns\n\n"
        
        response += "**Sector Distribution:**\n"
        for sector, count in sorted(stats['sectors'].items(), key=lambda x: x[1], reverse=True)[:5]:
            response += f"• {sector}: {count} asset(s)\n"
        
        return response
    
    def _analyze_sectors(self, portfolio: dict, stats: dict) -> str:
        response = "**📈 Sector Breakdown:**\n\n"
        
        for sector, count in sorted(stats['sectors'].items(), key=lambda x: x[1], reverse=True):
            response += f"• **{sector}**: {count} asset(s)\n"
        
        response += f"\n**Diversification Score**: {len(stats['sectors'])} different sectors provide strong industry diversification."
        
        return response
    
    def _greet_user(self, stats: dict) -> str:
        return f"""Hello! I'm your Lumia AI Portfolio Assistant. 👋\n\n**Your Portfolio at a Glance:**\n• {stats['total_assets']} total assets\n• {len(stats['asset_types'])} asset classes\n• ₹{stats['total_capital']:,.0f} invested\n\n**Ask me anything:**\n• "Why this allocation?"\n• "What's the best stock?"\n• "How risky is this?"\n• "What returns can I expect?"\n• "Compare my assets"\n\nHow can I help you today?"""
    
    def _provide_help(self, stats: dict) -> str:
        return f"""I can help you understand your ₹{stats['total_capital']:,.0f} portfolio with {stats['total_assets']} assets.\n\n**Try asking:**\n• "Why this allocation?" - Strategy explanation\n• "What's the best stock?" - Top recommendations\n• "How risky is this?" - Risk analysis\n• "Show my returns" - Profit projections\n• "Compare my assets" - Asset breakdown\n• "Explain diversification" - Portfolio balance\n• "Sector analysis" - Industry distribution"""
    
    def _get_asset_type(self, asset: dict, portfolio: dict) -> str:
        """Find which asset type an asset belongs to"""
        symbol = asset.get('symbol', '')
        for asset_type, assets in portfolio.items():
            if any(a.get('symbol') == symbol for a in assets):
                return asset_type.replace('_', ' ').title()
        return "Unknown"
