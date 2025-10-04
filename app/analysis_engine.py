"""
Advanced Investment Analysis Engine for Lumia

This module provides sophisticated investment analysis, portfolio optimization,
and market research capabilities with Google-style analysis depth.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import datetime
from dataclasses import dataclass
import json

@dataclass
class StockAnalysis:
    """Comprehensive stock analysis data structure"""
    symbol: str
    name: str
    sector: str
    current_price: float
    target_price: float
    recommendation: str
    risk_score: float
    esg_score: float
    financial_health_score: float
    technical_momentum: str
    analyst_consensus: str
    key_metrics: Dict[str, float]
    growth_drivers: List[str]
    risk_factors: List[str]

class LumiaAnalysisEngine:
    """Advanced analysis engine mimicking Google-style research depth"""
    
    def __init__(self):
        self.market_data = self._initialize_market_data()
        self.sector_analysis = self._initialize_sector_data()
        self.macro_indicators = self._generate_macro_indicators()
    
    def _initialize_market_data(self) -> Dict[str, Any]:
        """Initialize comprehensive market data"""
        return {
            'indices': {
                'NIFTY_50': {'current': 21456.78, 'change': 1.24, 'pe': 22.5, 'pb': 3.2},
                'SENSEX': {'current': 70842.33, 'change': 0.98, 'pe': 23.1, 'pb': 3.4},
                'BANK_NIFTY': {'current': 46234.12, 'change': -0.45, 'pe': 14.8, 'pb': 1.8},
                'NIFTY_IT': {'current': 32567.89, 'change': 2.34, 'pe': 28.4, 'pb': 5.1}
            },
            'market_sentiment': {
                'vix': 16.78,
                'put_call_ratio': 0.85,
                'fii_investment': 2340.5,  # Crores
                'dii_investment': 1876.3,  # Crores
                'sentiment_score': 'Cautiously Optimistic'
            }
        }
    
    def _initialize_sector_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive sector analysis data"""
        return {
            'Technology': {
                'market_cap': 18500000,  # Crores
                'pe_ratio': 26.8,
                'growth_rate': 15.2,
                'key_trends': ['AI/ML Adoption', 'Digital Transformation', 'Cloud Migration'],
                'challenges': ['Talent Shortage', 'Currency Fluctuation', 'Competition'],
                'outlook': 'Positive'
            },
            'Banking': {
                'market_cap': 12300000,
                'pe_ratio': 12.4,
                'growth_rate': 18.7,
                'key_trends': ['Digital Banking', 'Credit Growth', 'Financial Inclusion'],
                'challenges': ['NPA Management', 'Regulatory Changes', 'Interest Rate Risk'],
                'outlook': 'Positive'
            },
            'Healthcare': {
                'market_cap': 8900000,
                'pe_ratio': 24.6,
                'growth_rate': 12.8,
                'key_trends': ['Telemedicine', 'Generic Drugs Export', 'Healthcare Infrastructure'],
                'challenges': ['Regulatory Approvals', 'Price Controls', 'R&D Costs'],
                'outlook': 'Stable'
            },
            'Energy': {
                'market_cap': 11200000,
                'pe_ratio': 15.3,
                'growth_rate': 14.1,
                'key_trends': ['Renewable Energy', 'Energy Transition', 'Green Hydrogen'],
                'challenges': ['Oil Price Volatility', 'Environmental Regulations', 'Transition Costs'],
                'outlook': 'Mixed'
            }
        }
    
    def _generate_macro_indicators(self) -> Dict[str, Any]:
        """Generate macroeconomic indicators"""
        return {
            'gdp_growth': 6.8,
            'inflation_rate': 5.2,
            'repo_rate': 6.5,
            'crude_oil_price': 89.45,
            'usd_inr': 83.25,
            'gold_price': 62450,
            'bond_yield_10yr': 7.15,
            'economic_outlook': 'Moderate Growth'
        }
    
    def generate_stock_universe(self) -> Dict[str, List[StockAnalysis]]:
        """Generate comprehensive stock universe with detailed analysis"""
        
        # Technology Stocks
        tech_stocks = [
            StockAnalysis(
                symbol='TCS.NS', name='Tata Consultancy Services', sector='Technology',
                current_price=3650.0, target_price=4200.0, recommendation='BUY',
                risk_score=2.1, esg_score=8.4, financial_health_score=9.2,
                technical_momentum='Strong Bullish', analyst_consensus='Strong Buy',
                key_metrics={
                    'pe_ratio': 28.5, 'roe': 42.1, 'debt_to_equity': 0.08,
                    'revenue_growth': 16.8, 'profit_margin': 25.2
                },
                growth_drivers=[
                    'Strong digital transformation demand',
                    'AI and cloud services expansion',
                    'Robust client addition in BFSI'
                ],
                risk_factors=[
                    'Currency headwinds',
                    'Talent cost inflation',
                    'Visa restrictions impact'
                ]
            ),
            StockAnalysis(
                symbol='INFY.NS', name='Infosys Limited', sector='Technology',
                current_price=1420.0, target_price=1650.0, recommendation='BUY',
                risk_score=2.3, esg_score=8.7, financial_health_score=8.9,
                technical_momentum='Bullish', analyst_consensus='Buy',
                key_metrics={
                    'pe_ratio': 26.2, 'roe': 31.4, 'debt_to_equity': 0.05,
                    'revenue_growth': 14.2, 'profit_margin': 22.8
                },
                growth_drivers=[
                    'Cobalt and automation platform',
                    'Strong consulting business',
                    'Digital services growth'
                ],
                risk_factors=[
                    'Client concentration risk',
                    'Pricing pressure',
                    'Attrition challenges'
                ]
            )
        ]
        
        # Banking Stocks
        banking_stocks = [
            StockAnalysis(
                symbol='HDFCBANK.NS', name='HDFC Bank', sector='Banking',
                current_price=1620.0, target_price=1850.0, recommendation='BUY',
                risk_score=1.8, esg_score=7.9, financial_health_score=9.5,
                technical_momentum='Bullish', analyst_consensus='Strong Buy',
                key_metrics={
                    'pe_ratio': 18.4, 'roe': 17.2, 'book_value': 650.0,
                    'casa_ratio': 42.8, 'npa_ratio': 1.26
                },
                growth_drivers=[
                    'Strong retail franchise',
                    'Digital banking leadership',
                    'Credit growth momentum'
                ],
                risk_factors=[
                    'Asset quality concerns',
                    'Regulatory changes',
                    'Interest rate sensitivity'
                ]
            ),
            StockAnalysis(
                symbol='ICICIBANK.NS', name='ICICI Bank', sector='Banking',
                current_price=950.0, target_price=1100.0, recommendation='BUY',
                risk_score=2.4, esg_score=7.2, financial_health_score=8.6,
                technical_momentum='Moderate Bullish', analyst_consensus='Buy',
                key_metrics={
                    'pe_ratio': 15.8, 'roe': 16.8, 'book_value': 420.0,
                    'casa_ratio': 45.2, 'npa_ratio': 3.15
                },
                growth_drivers=[
                    'Improved asset quality',
                    'Strong digital adoption',
                    'Corporate banking recovery'
                ],
                risk_factors=[
                    'Economic slowdown impact',
                    'Competitive pressure',
                    'Credit cost normalization'
                ]
            )
        ]
        
        # Healthcare Stocks
        healthcare_stocks = [
            StockAnalysis(
                symbol='SUNPHARMA.NS', name='Sun Pharmaceutical', sector='Healthcare',
                current_price=1185.0, target_price=1350.0, recommendation='BUY',
                risk_score=2.7, esg_score=6.8, financial_health_score=8.1,
                technical_momentum='Moderate Bullish', analyst_consensus='Buy',
                key_metrics={
                    'pe_ratio': 22.4, 'roe': 18.6, 'debt_to_equity': 0.15,
                    'revenue_growth': 8.9, 'ebitda_margin': 24.5
                },
                growth_drivers=[
                    'Specialty drugs portfolio',
                    'US market recovery',
                    'Emerging markets expansion'
                ],
                risk_factors=[
                    'Regulatory compliance issues',
                    'Generic price erosion',
                    'R&D investment requirements'
                ]
            )
        ]
        
        # Energy Stocks
        energy_stocks = [
            StockAnalysis(
                symbol='RELIANCE.NS', name='Reliance Industries', sector='Energy',
                current_price=2485.0, target_price=2800.0, recommendation='BUY',
                risk_score=2.9, esg_score=6.5, financial_health_score=8.7,
                technical_momentum='Bullish', analyst_consensus='Buy',
                key_metrics={
                    'pe_ratio': 21.8, 'roe': 11.4, 'debt_to_equity': 0.35,
                    'revenue_growth': 22.1, 'ebitda_margin': 14.2
                },
                growth_drivers=[
                    'Jio 5G rollout',
                    'Retail expansion',
                    'Green energy transition'
                ],
                risk_factors=[
                    'Oil price volatility',
                    'Telecom competition',
                    'Capital allocation concerns'
                ]
            )
        ]
        
        return {
            'Technology': tech_stocks,
            'Banking': banking_stocks,
            'Healthcare': healthcare_stocks,
            'Energy': energy_stocks
        }
    
    def perform_portfolio_analysis(self, capital: float, risk_tolerance: str, 
                                 investment_horizon: int, sectors: List[str]) -> Dict[str, Any]:
        """Perform comprehensive portfolio analysis with Google-style depth"""
        
        stock_universe = self.generate_stock_universe()
        
        # Filter stocks based on user preferences
        available_stocks = []
        for sector in sectors:
            if sector in stock_universe:
                available_stocks.extend(stock_universe[sector])
        
        if not available_stocks:
            # If no sectors selected, use all stocks
            for stocks in stock_universe.values():
                available_stocks.extend(stocks)
        
        # Risk-based filtering
        risk_mapping = {'Conservative': 2.5, 'Moderate': 3.5, 'Aggressive': 5.0}
        max_risk = risk_mapping.get(risk_tolerance, 3.5)
        
        suitable_stocks = [s for s in available_stocks if s.risk_score <= max_risk]
        
        # Portfolio optimization (simplified)
        portfolio_size = min(8, len(suitable_stocks))
        selected_stocks = sorted(suitable_stocks, 
                               key=lambda x: (x.financial_health_score, -x.risk_score))[:portfolio_size]
        
        # Calculate allocations
        total_score = sum(s.financial_health_score for s in selected_stocks)
        
        portfolio_analysis = []
        for stock in selected_stocks:
            allocation = (stock.financial_health_score / total_score) * 100
            investment_amount = capital * (allocation / 100)
            
            # Calculate projections
            expected_return = ((stock.target_price / stock.current_price) - 1) * 100
            projected_value = investment_amount * (1 + expected_return/100) ** investment_horizon
            
            portfolio_analysis.append({
                'stock': stock,
                'allocation_percentage': round(allocation, 1),
                'investment_amount': round(investment_amount, 2),
                'expected_annual_return': round(expected_return, 2),
                'projected_value': round(projected_value, 2),
                'risk_adjusted_return': round(expected_return / stock.risk_score, 2)
            })
        
        # Portfolio metrics
        portfolio_return = sum(p['expected_annual_return'] * p['allocation_percentage']/100 
                             for p in portfolio_analysis)
        total_projected_value = sum(p['projected_value'] for p in portfolio_analysis)
        portfolio_risk = np.sqrt(sum((p['allocation_percentage']/100)**2 * p['stock'].risk_score**2 
                                   for p in portfolio_analysis))
        
        # Market comparison
        market_analysis = self._generate_market_comparison(portfolio_return, portfolio_risk)
        
        # Generate insights
        insights = self._generate_investment_insights(portfolio_analysis, market_analysis)
        
        return {
            'portfolio': portfolio_analysis,
            'portfolio_metrics': {
                'expected_annual_return': round(portfolio_return, 2),
                'projected_total_value': round(total_projected_value, 2),
                'total_gain': round(total_projected_value - capital, 2),
                'portfolio_risk_score': round(portfolio_risk, 2),
                'sharpe_ratio': round((portfolio_return - 6.5) / portfolio_risk, 2),  # Risk-free rate = 6.5%
                'diversification_score': self._calculate_diversification_score(portfolio_analysis)
            },
            'market_analysis': market_analysis,
            'investment_insights': insights,
            'sector_allocation': self._calculate_sector_allocation(portfolio_analysis),
            'risk_analysis': self._generate_risk_analysis(portfolio_analysis),
            'rebalancing_recommendations': self._generate_rebalancing_advice(portfolio_analysis)
        }
    
    def _generate_market_comparison(self, portfolio_return: float, portfolio_risk: float) -> Dict[str, Any]:
        """Generate market comparison analysis"""
        
        benchmark_returns = {
            'NIFTY_50': 12.8,
            'SENSEX': 13.2,
            'Balanced_Fund': 11.5,
            'Fixed_Deposit': 6.5,
            'Gold': 8.2
        }
        
        risk_scores = {
            'NIFTY_50': 3.2,
            'SENSEX': 3.4,
            'Balanced_Fund': 2.8,
            'Fixed_Deposit': 1.0,
            'Gold': 2.5
        }
        
        comparisons = {}
        for benchmark, return_val in benchmark_returns.items():
            risk_val = risk_scores[benchmark]
            comparisons[benchmark] = {
                'return_difference': round(portfolio_return - return_val, 2),
                'risk_difference': round(portfolio_risk - risk_val, 2),
                'risk_adjusted_performance': round((portfolio_return - 6.5) / portfolio_risk - 
                                                 (return_val - 6.5) / risk_val, 2)
            }
        
        return {
            'benchmarks': comparisons,
            'relative_performance': 'Outperforming' if portfolio_return > 12.8 else 'Underperforming',
            'risk_position': 'Higher Risk' if portfolio_risk > 3.2 else 'Lower Risk'
        }
    
    def _generate_investment_insights(self, portfolio: List[Dict], market_analysis: Dict) -> List[str]:
        """Generate AI-powered investment insights"""
        
        insights = []
        
        # Portfolio composition insights
        sector_count = len(set(p['stock'].sector for p in portfolio))
        if sector_count >= 3:
            insights.append("✅ Well-diversified portfolio across multiple sectors reduces concentration risk")
        else:
            insights.append("⚠️ Consider adding exposure to other sectors for better diversification")
        
        # Risk analysis
        avg_risk = np.mean([p['stock'].risk_score for p in portfolio])
        if avg_risk < 2.5:
            insights.append("🛡️ Conservative portfolio with lower volatility - suitable for stable returns")
        elif avg_risk > 3.5:
            insights.append("🚀 Aggressive portfolio with higher growth potential but increased volatility")
        else:
            insights.append("⚖️ Balanced risk profile with moderate growth potential")
        
        # ESG insights
        avg_esg = np.mean([p['stock'].esg_score for p in portfolio])
        if avg_esg > 7.5:
            insights.append("🌱 Strong ESG profile - aligned with sustainable investing principles")
        
        # Market timing insights
        if market_analysis['relative_performance'] == 'Outperforming':
            insights.append("📈 Portfolio positioned to outperform market benchmarks")
        
        # Quality insights
        high_quality_stocks = len([p for p in portfolio if p['stock'].financial_health_score > 8.5])
        if high_quality_stocks >= len(portfolio) * 0.6:
            insights.append("💎 High-quality stock selection with strong fundamentals")
        
        return insights
    
    def _calculate_diversification_score(self, portfolio: List[Dict]) -> float:
        """Calculate portfolio diversification score"""
        
        # Sector diversification
        sectors = [p['stock'].sector for p in portfolio]
        unique_sectors = len(set(sectors))
        max_sectors = 4  # Maximum expected sectors
        sector_score = min(unique_sectors / max_sectors, 1.0)
        
        # Allocation concentration
        allocations = [p['allocation_percentage'] for p in portfolio]
        max_allocation = max(allocations)
        concentration_score = 1.0 - (max_allocation - 100/len(portfolio)) / 100
        
        # Risk diversification
        risks = [p['stock'].risk_score for p in portfolio]
        risk_std = np.std(risks)
        risk_diversification = min(risk_std / 2.0, 1.0)  # Normalize to 0-1
        
        overall_score = (sector_score * 0.4 + concentration_score * 0.4 + risk_diversification * 0.2)
        return round(overall_score * 10, 1)  # Convert to 0-10 scale
    
    def _calculate_sector_allocation(self, portfolio: List[Dict]) -> Dict[str, float]:
        """Calculate sector-wise allocation"""
        
        sector_allocation = {}
        for p in portfolio:
            sector = p['stock'].sector
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += p['allocation_percentage']
        
        return {k: round(v, 1) for k, v in sector_allocation.items()}
    
    def _generate_risk_analysis(self, portfolio: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive risk analysis"""
        
        risks = {
            'market_risk': 'Medium',
            'sector_concentration_risk': 'Low' if len(set(p['stock'].sector for p in portfolio)) >= 3 else 'Medium',
            'liquidity_risk': 'Low',  # Assuming all stocks are liquid
            'currency_risk': 'Medium',  # For stocks with international exposure
            'interest_rate_risk': 'Low' if not any('Banking' in p['stock'].sector for p in portfolio) else 'Medium'
        }
        
        # Overall risk assessment
        risk_factors = [
            "Market volatility affecting all equity investments",
            "Sector-specific regulatory changes",
            "Macroeconomic factors (inflation, interest rates)",
            "Global economic uncertainty",
            "Currency fluctuation impact on earnings"
        ]
        
        # Risk mitigation strategies
        mitigation_strategies = [
            "Regular portfolio rebalancing (quarterly)",
            "Systematic investment approach (SIP)",
            "Maintaining adequate emergency fund",
            "Diversification across asset classes",
            "Long-term investment horizon maintenance"
        ]
        
        return {
            'risk_categories': risks,
            'key_risk_factors': risk_factors,
            'mitigation_strategies': mitigation_strategies,
            'overall_risk_level': self._calculate_overall_risk(portfolio)
        }
    
    def _calculate_overall_risk(self, portfolio: List[Dict]) -> str:
        """Calculate overall portfolio risk level"""
        
        avg_risk = np.mean([p['stock'].risk_score for p in portfolio])
        if avg_risk < 2.5:
            return 'Conservative'
        elif avg_risk < 3.5:
            return 'Moderate'
        else:
            return 'Aggressive'
    
    def _generate_rebalancing_advice(self, portfolio: List[Dict]) -> List[str]:
        """Generate portfolio rebalancing recommendations"""
        
        advice = []
        
        # Check for over-concentration
        max_allocation = max(p['allocation_percentage'] for p in portfolio)
        if max_allocation > 25:
            advice.append(f"Consider reducing allocation to largest holding (currently {max_allocation:.1f}%)")
        
        # Sector balance
        sector_allocation = self._calculate_sector_allocation(portfolio)
        if any(allocation > 40 for allocation in sector_allocation.values()):
            advice.append("Consider reducing sector concentration for better diversification")
        
        # Performance-based rebalancing
        advice.extend([
            "Review and rebalance quarterly or when allocation drifts >5%",
            "Book profits from outperformers and add to underperformers",
            "Consider tax implications while rebalancing",
            "Maintain long-term perspective during rebalancing decisions"
        ])
        
        return advice
    
    def generate_portfolio_recommendations(self, capital: float, risk_tolerance: str, 
                                         investment_horizon: str, sector_preference: str = None) -> Dict[str, Any]:
        """Generate portfolio recommendations - compatibility method for Streamlit app"""
        
        # Convert investment horizon to years
        horizon_map = {
            "1-3 months": 0.25,
            "3-6 months": 0.5, 
            "6-12 months": 1,
            "1-2 years": 1.5,
            "2-5 years": 3.5,
            "5+ years": 7
        }
        horizon_years = horizon_map.get(investment_horizon, 2)
        
        # Map sector preference to sectors list
        if sector_preference == "All Sectors" or sector_preference == "Diversified":
            sectors = ["Technology", "Banking", "Healthcare", "Consumer", "Manufacturing"]
        else:
            sectors = [sector_preference] if sector_preference else ["Technology", "Banking"]
        
        # Use the existing analysis method
        analysis_result = self.perform_portfolio_analysis(
            capital=capital,
            risk_tolerance=risk_tolerance,
            investment_horizon=int(horizon_years),
            sectors=sectors
        )
        
        # Convert to expected format for Streamlit app
        stock_recommendations = []
        if 'portfolio' in analysis_result:
            for stock_data in analysis_result['portfolio']:
                stock_analysis = StockAnalysis(
                    symbol=stock_data.get('symbol', 'N/A'),
                    name=stock_data.get('name', 'Unknown'),
                    sector=stock_data.get('sector', 'General'),
                    current_price=stock_data.get('current_price', 100.0),
                    target_price=stock_data.get('target_price', 110.0),
                    recommendation=stock_data.get('recommendation', 'Hold'),
                    risk_score=stock_data.get('risk_score', 3.0),
                    esg_score=stock_data.get('esg_score', 75.0),
                    financial_health_score=stock_data.get('financial_health_score', 80.0),
                    technical_momentum=stock_data.get('technical_momentum', 'Neutral'),
                    analyst_consensus=stock_data.get('analyst_consensus', 'Hold'),
                    key_metrics=stock_data.get('key_metrics', {}),
                    growth_drivers=stock_data.get('growth_drivers', []),
                    risk_factors=stock_data.get('risk_factors', [])
                )
                stock_recommendations.append(stock_analysis)
        
        # Create portfolio data structure expected by Streamlit
        portfolio_data = type('Portfolio', (), {
            'stock_recommendations': stock_recommendations,
            'analysis_summary': analysis_result.get('summary', 'Portfolio analysis completed'),
            'risk_assessment': analysis_result.get('risk_analysis', {}),
            'expected_return': analysis_result.get('expected_annual_return', 12.0),
            'recommended_allocation': analysis_result.get('portfolio', [])
        })()
        
        return portfolio_data

# Compatibility aliases
AnalysisEngine = LumiaAnalysisEngine

# Global instance
analysis_engine = LumiaAnalysisEngine()