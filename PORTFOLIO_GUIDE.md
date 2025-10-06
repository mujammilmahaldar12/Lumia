# 🎯 LUMIA PORTFOLIO ALLOCATOR - USER GUIDE

## 🆕 **NEW FEATURE: FinRobot-Style Portfolio Builder**

Lumia now includes a **complete robo-advisor** that doesn't just tell you "Top 20 stocks" - it builds a **COMPLETE investment strategy** across ALL asset types!

---

## 🤖 What Is FinRobot-Style Portfolio?

Instead of just showing recommendations, Lumia now acts like a **robo-advisor**:

### **Traditional System (Old):**
```
Top 20 Stocks:
1. TCS.NS - BUY (Score: 85)
2. INFY.NS - BUY (Score: 82)
...
```

### **FinRobot System (NEW!):**
```
YOUR INVESTMENT STRATEGY:
- 30% Stocks (Rs 30,000) → TCS, INFY, RELIANCE
- 25% ETFs (Rs 25,000) → Nifty 50 ETF, Bank ETF
- 25% Mutual Funds (Rs 25,000) → HDFC Balanced, ICICI Flexi
- 15% Fixed Deposits (Rs 15,000) → Bank FD @ 7%
- 5% Crypto (Rs 5,000) → Bitcoin, Ethereum

AI REASONING: Your moderate risk (55%) balances growth with safety. 
55% equity captures market upside, 40% debt provides downside protection...
```

---

## 📊 How It Works

### **INPUT**
1. **Total Capital**: How much you want to invest (e.g., Rs 1,00,000)
2. **Risk Appetite**: 0-100% (30% = Conservative, 55% = Moderate, 80% = Aggressive)
3. **Exclusions**: Sectors/industries to avoid (e.g., Tobacco, Alcohol)

### **OUTPUT**
1. **Allocation Strategy**: % breakdown across asset types
2. **Specific Picks**: Top recommendations in each category
3. **Capital Distribution**: How much to invest in each asset
4. **AI Reasoning**: WHY this allocation suits your risk profile

---

## 🚀 Usage

### **Basic Portfolio Generation**
```bash
python main.py --portfolio --capital 100000 --risk-pct 30
```
- Capital: Rs 1,00,000
- Risk: 30% (Conservative)
- Result: 15% stocks, 20% ETFs, 35% mutual funds, 25% FDs, 5% crypto

### **Moderate Risk**
```bash
python main.py --portfolio --capital 100000 --risk-pct 55
```
- Capital: Rs 1,00,000
- Risk: 55% (Moderate)
- Result: 30% stocks, 25% ETFs, 25% mutual funds, 15% FDs, 5% crypto

### **Aggressive Risk**
```bash
python main.py --portfolio --capital 100000 --risk-pct 80
```
- Capital: Rs 1,00,000
- Risk: 80% (Aggressive)
- Result: 40% stocks, 20% ETFs, 20% mutual funds, 5% FDs, 15% crypto

### **With Exclusions**
```bash
python main.py --portfolio --capital 100000 --risk-pct 30 --exclude-sectors "Tobacco,Alcohol"
```
Excludes tobacco and alcohol sectors from recommendations.

---

## 📈 Risk Profiles

| Risk % | Profile | Equity | Debt | Crypto | Expected Returns | Volatility |
|--------|---------|--------|------|--------|------------------|------------|
| 0-30% | **Conservative** | 35% | 60% | 5% | 6-9% | Low (±5-10%) |
| 31-60% | **Moderate** | 55% | 40% | 5% | 9-13% | Medium (±10-20%) |
| 61-100% | **Aggressive** | 60% | 25% | 15% | 13-18% | High (±20-35%) |

**Equity** = Stocks + ETFs  
**Debt** = Mutual Funds + Fixed Deposits  
**Crypto** = Cryptocurrency  

---

## 💡 Example Output

```
====================================================================================================
YOUR PERSONALIZED INVESTMENT PORTFOLIO
====================================================================================================

Capital: Rs 100,000
Risk: 55% (Moderate)
Generated: 2025-01-06 09:35:47

====================================================================================================
ALLOCATION BREAKDOWN
====================================================================================================

STOCKS           30%  ███████████████  Rs       30,000
ETF              25%  ████████████     Rs       25,000
MUTUAL FUND      25%  ████████████     Rs       25,000
FD               15%  ███████          Rs       15,000
CRYPTO            5%  ██               Rs        5,000

====================================================================================================
RECOMMENDED PICKS
====================================================================================================

STOCKS (Rs 30,000):
  1. TCS.NS - Tata Consultancy Services Limited
     Invest: Rs 8,500
     Score: 78.5/100 (Confidence: 85%)
     Components: Tech 75 | Fund 82 | Sent 80 | Risk 72

  2. INFY.NS - Infosys Limited
     Invest: Rs 7,200
     Score: 75.2/100 (Confidence: 82%)
     Components: Tech 72 | Fund 78 | Sent 75 | Risk 75

ETF (Rs 25,000):
  1. NIFTYBEES.NS - Nippon India ETF Nifty BeES
     Invest: Rs 13,000
     Score: 72.0/100 (Confidence: 80%)
     
  2. BANKBEES.NS - Nippon India ETF Bank BeES
     Invest: Rs 12,000
     Score: 70.5/100 (Confidence: 78%)

... (continues for all asset types)

====================================================================================================

AI PORTFOLIO REASONING (FinGPT)

Capital: Rs 100,000
Risk: 55% (Moderate)

ALLOCATION STRATEGY:
- STOCKS: 30% (Rs 30,000)
  Direct equity exposure for capital appreciation. Diversified across sectors to mitigate risk.

- ETF: 25% (Rs 25,000)
  Index-based diversification with low expense ratios. Professional passive management.

- MUTUAL FUND: 25% (Rs 25,000)
  Active professional fund management with proven track records.

- FD: 15% (Rs 15,000)
  Capital preservation and liquidity buffer. Guaranteed returns.

- CRYPTO: 5% (Rs 5,000)
  Asymmetric upside potential in emerging digital asset class.

STRATEGY: Your moderate profile balances growth with safety. The 55% equity allocation
targets capital appreciation through market participation, while 40% debt instruments 
provide downside protection during market corrections. The 5% crypto allocation adds 
speculative upside potential.

EXPECTED RETURNS: 9-13%
VOLATILITY: Medium (±10-20%)
MAX DRAWDOWN: 15-25%
TIME HORIZON: 3-5 years minimum

REBALANCE: Every 6 months or when drift >5%

====================================================================================================
```

---

## 🎯 All Command Options

### **Portfolio Generation (NEW!)**
```bash
# Basic portfolio
python main.py --portfolio --capital <amount> --risk-pct <0-100>

# With exclusions
python main.py --portfolio --capital 100000 --risk-pct 30 --exclude-sectors "Tobacco,Alcohol"
python main.py --portfolio --capital 100000 --risk-pct 30 --exclude-industries "Distillery,Tobacco"
```

### **Individual Asset Analysis (Original)**
```bash
# Analyze all assets
python main.py

# Filter by asset type
python main.py --type stock
python main.py --type etf
python main.py --type mutual_fund
python main.py --type crypto
python main.py --type all

# Filter by recommendation
python main.py --action BUY
python main.py --action SELL
python main.py --action HOLD

# Show top N
python main.py --top 10

# Detailed scores
python main.py --detailed

# Export to CSV
python main.py --export results.csv
```

---

## 🎨 Streamlit UI (Coming Soon)

A visual portfolio builder with:
- Capital input slider
- Risk appetite slider (0-100%)
- Sector/industry exclusion checkboxes
- Live portfolio visualization
- Export to PDF/Excel

**Launch:**
```bash
streamlit run app/streamlit_app.py
```

---

## 🔧 Technical Details

### **Expert Recommendation Engine**
- **Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands (25% weight)
- **Fundamental Analysis**: P/E, ROE, Debt/Equity, Revenue Growth (30% weight)
- **Sentiment Analysis**: FinBERT + VADER news analysis (25% weight)
- **Risk Assessment**: Volatility, Beta, Max Drawdown (20% weight)

### **Decision Thresholds**
- **BUY**: Score ≥ 65
- **HOLD**: 40 ≤ Score < 65
- **SELL**: Score < 40

### **Database**
- PostgreSQL: `localhost/lumia_test`
- 2,205+ assets across stocks, ETFs, mutual funds, crypto

---

## 📝 Notes

1. **GPU Recommended**: FinBERT sentiment analysis benefits from GPU (CUDA-enabled PyTorch)
2. **Data Requirements**: Assets need sufficient price history (>30 days) for technical analysis
3. **News Disabled**: Live news fetching currently disabled (DuckDuckGo blocking). Sentiment defaults to neutral (50).
4. **Rebalancing**: Review portfolio every 6 months or when allocation drifts >5%

---

## 🆘 Troubleshooting

### **"No picks found"**
- Database lacks sufficient price data for analysis
- Try running collectors: `python scripts/lumia_collector.py`

### **"GPU not detected"**
- Activate virtual environment first: `.\env\Scripts\activate`
- Ensure CUDA-compatible PyTorch installed

### **"QueuePool limit reached"**
- Fixed! Database session management now prevents pool exhaustion

---

## 📚 Further Reading

- **Modern Portfolio Theory (MPT)**: Harry Markowitz's Nobel Prize-winning diversification theory
- **Sharpe Ratio**: Risk-adjusted return measurement
- **Risk Parity**: Each asset contributes equally to overall portfolio risk
- **Rebalancing**: Maintaining target allocations to preserve risk profile

---

**Built with ❤️ using:**
- Python 3.10+
- PostgreSQL
- SQLAlchemy
- FinBERT (AI Sentiment)
- PyTorch (GPU-accelerated)
- Streamlit (UI)
