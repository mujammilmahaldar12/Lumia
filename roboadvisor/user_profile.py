# roboadvisor/user_profile.py
"""
USER PROFILING MODULE
Builds comprehensive investor profiles through interactive questionnaire
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class RiskType(Enum):
    """Investment risk categories"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"

@dataclass
class UserProfile:
    """Complete user investment profile"""
    capital: float
    risk_score: int  # 0-100
    risk_type: RiskType
    years: int
    expected_return: float  # Annual % (e.g., 0.12 = 12%)
    exclusions: List[str]  # Asset types or sectors to exclude
    
    # Derived attributes
    age_bracket: str = None  # young, mid, senior
    investment_goal: str = None  # wealth, retirement, income
    rebalancing_frequency: str = "quarterly"  # monthly, quarterly, yearly
    
    def __post_init__(self):
        """Calculate derived attributes"""
        # Determine age bracket from investment horizon
        if self.years <= 5:
            self.age_bracket = "short_term"
            self.investment_goal = "wealth"
        elif self.years <= 15:
            self.age_bracket = "mid_term"
            self.investment_goal = "growth"
        else:
            self.age_bracket = "long_term"
            self.investment_goal = "retirement"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "capital": self.capital,
            "risk_score": self.risk_score,
            "risk_type": self.risk_type.value,
            "years": self.years,
            "expected_return": self.expected_return,
            "exclusions": self.exclusions,
            "age_bracket": self.age_bracket,
            "investment_goal": self.investment_goal,
            "rebalancing_frequency": self.rebalancing_frequency
        }

def build_user_profile(
    capital: float,
    risk_score: int,
    years: int,
    expected_return: float,
    exclusions: List[str] = None
) -> UserProfile:
    """
    Create a user investment profile
    
    Args:
        capital: Total investment amount
        risk_score: Risk appetite (0-100)
        years: Investment horizon in years
        expected_return: Expected annual return (as decimal, e.g., 0.12 = 12%)
        exclusions: List of asset types or sectors to exclude
    
    Returns:
        UserProfile object
    """
    # Determine risk type from score
    if risk_score < 25:
        risk_type = RiskType.CONSERVATIVE
    elif risk_score < 60:
        risk_type = RiskType.MODERATE
    elif risk_score < 85:
        risk_type = RiskType.AGGRESSIVE
    else:
        risk_type = RiskType.VERY_AGGRESSIVE
    
    return UserProfile(
        capital=capital,
        risk_score=risk_score,
        risk_type=risk_type,
        years=years,
        expected_return=expected_return,
        exclusions=exclusions or []
    )

def interactive_profiling() -> UserProfile:
    """
    Interactive terminal-based user profiling
    Asks questions to build complete investment profile
    """
    print("\n" + "="*70)
    print("🤖 LUMIA ROBO-ADVISOR - INVESTMENT PROFILE BUILDER")
    print("="*70)
    print("\nLet's build your personalized investment strategy!\n")
    
    # Question 1: Capital
    while True:
        try:
            capital_input = input("💰 How much capital do you want to invest? (₹): ").strip()
            capital = float(capital_input.replace(",", "").replace("₹", ""))
            if capital <= 0:
                print("❌ Please enter a positive amount.")
                continue
            break
        except ValueError:
            print("❌ Invalid input. Please enter a number (e.g., 100000)")
    
    # Question 2: Risk Appetite
    print("\n📊 Risk Appetite Scale:")
    print("  0-25:  Conservative (Safe, stable returns)")
    print("  26-60: Moderate (Balanced risk-reward)")
    print("  61-85: Aggressive (Higher risk, higher returns)")
    print("  86-100: Very Aggressive (Maximum growth potential)")
    
    while True:
        try:
            risk_score = int(input("\n🎯 What's your risk appetite? (0-100): ").strip())
            if 0 <= risk_score <= 100:
                break
            print("❌ Please enter a number between 0 and 100.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
    
    # Question 3: Investment Horizon
    while True:
        try:
            years = int(input("\n⏰ For how many years do you want to invest?: ").strip())
            if years > 0:
                break
            print("❌ Please enter a positive number of years.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
    
    # Question 4: Expected Return
    print("\n📈 Expected Return Guide:")
    print("  Conservative: 6-8% per year")
    print("  Moderate: 10-12% per year")
    print("  Aggressive: 15-20% per year")
    
    while True:
        try:
            return_pct = float(input("\n💹 What annual return are you expecting? (%): ").strip().replace("%", ""))
            if 0 < return_pct <= 100:
                expected_return = return_pct / 100  # Convert to decimal
                break
            print("❌ Please enter a realistic return percentage (e.g., 12 for 12%)")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
    
    # Question 5: Exclusions
    print("\n🚫 Asset Exclusions (Optional):")
    print("  Available asset types: stocks, etf, mutual_funds, crypto, bonds")
    print("  Press Enter to skip, or enter comma-separated types to exclude")
    
    exclusions_input = input("\n❌ Exclude any asset types?: ").strip().lower()
    if exclusions_input:
        exclusions = [x.strip() for x in exclusions_input.split(",")]
    else:
        exclusions = []
    
    # Build profile
    profile = build_user_profile(capital, risk_score, years, expected_return, exclusions)
    
    # Display summary
    print("\n" + "="*70)
    print("✅ PROFILE CREATED SUCCESSFULLY")
    print("="*70)
    print(f"Capital:          ₹{capital:,.2f}")
    print(f"Risk Type:        {profile.risk_type.value.title()}")
    print(f"Risk Score:       {risk_score}/100")
    print(f"Investment Years: {years} years")
    print(f"Expected Return:  {return_pct}% per year")
    print(f"Goal:             {profile.investment_goal.title()}")
    print(f"Exclusions:       {', '.join(exclusions) if exclusions else 'None'}")
    print("="*70 + "\n")
    
    return profile
