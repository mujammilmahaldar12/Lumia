# 🏗️ LUMIA DATABASE ARCHITECTURE

## How Data Storage Works

### 📊 **Core Concept: Universal Asset Model**

All tradeable instruments (stocks, ETFs, crypto, mutual funds) use **ONE unified architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    ASSETS TABLE (Master)                     │
│  • Universal registry for ALL tradeable instruments          │
│  • Stores: symbol, name, type, sector, market_cap, etc.     │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ (One-to-Many Relationship)
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              DAILY_PRICES TABLE (Price History)              │
│  • Stores OHLCV data for ALL asset types                    │
│  • asset_id → Links to specific asset in ASSETS table       │
│  • Works for: Stocks, ETFs, Crypto, Mutual Funds            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **THE KEY INSIGHT**

**Question:** "How do crypto, ETFs, and stocks store their prices?"

**Answer:** They ALL use the **same `daily_prices` table**! 

The `asset_id` foreign key links each price record to its parent asset in the `assets` table.

---

## 📋 **Database Tables Breakdown**

### 1️⃣ **ASSETS Table** (Main Registry)
```sql
CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    symbol VARCHAR(50),           -- Ticker: "AAPL", "bitcoin", "VTSAX"
    name VARCHAR(500),            -- "Apple Inc.", "Bitcoin", "Vanguard Total Stock"
    type VARCHAR(50),             -- "stock", "crypto", "etf", "mutual_fund"
    subtype VARCHAR(100),         -- "large_cap", "altcoin", "index", "debt"
    exchange VARCHAR(100),        -- "NASDAQ", "CoinGecko", "NYSE"
    sector VARCHAR(100),          -- "Technology", "Cryptocurrency", "N/A"
    market_cap BIGINT,            -- Market capitalization in USD
    is_active BOOLEAN,
    ...
)
```

**Example Records:**
| id  | symbol  | name              | type         | exchange   |
|-----|---------|-------------------|--------------|------------|
| 1   | AAPL    | Apple Inc.        | stock        | NASDAQ     |
| 2   | bitcoin | Bitcoin           | crypto       | CoinGecko  |
| 3   | VTSAX   | Vanguard Total    | mutual_fund  | VANGUARD   |
| 4   | SPY     | SPDR S&P 500 ETF  | etf          | NYSE       |

---

### 2️⃣ **DAILY_PRICES Table** (Universal Price History)
```sql
CREATE TABLE daily_prices (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER,             -- FK → assets.id
    date DATE,                    -- Trading date
    open_price FLOAT,             -- Opening price
    high_price FLOAT,             -- Day's high
    low_price FLOAT,              -- Day's low
    close_price FLOAT,            -- Closing price
    adj_close FLOAT,              -- Adjusted close (splits/dividends)
    volume BIGINT,                -- Trading volume
    dividends FLOAT,              -- Dividend paid (if any)
    stock_splits FLOAT,           -- Split ratio (if any)
    UNIQUE(asset_id, date)        -- One record per asset per day
)
```

**Example Records:**
| id  | asset_id | date       | open_price | close_price | volume      |
|-----|----------|------------|------------|-------------|-------------|
| 1   | 1        | 2025-10-05 | 175.50     | 177.30      | 52,000,000  |
| 2   | 2        | 2025-10-05 | 62,500.00  | 63,200.00   | 25,000,000  |
| 3   | 3        | 2025-10-05 | 120.45     | 121.10      | 1,500,000   |
| 4   | 4        | 2025-10-05 | 450.20     | 451.80      | 80,000,000  |

> **Notice:** Bitcoin (asset_id=2) and Apple (asset_id=1) both use the same table structure!

---

### 3️⃣ **CRYPTOS Table** (Crypto-Specific Metadata)
```sql
CREATE TABLE cryptos (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER,             -- FK → assets.id
    circulating_supply BIGINT,    -- Coins in circulation
    total_supply BIGINT,          -- Total coins ever
    max_supply BIGINT,            -- Maximum possible supply
    algorithm VARCHAR(100),       -- "SHA-256", "Ethash"
    blockchain VARCHAR(100),      -- "Bitcoin", "Ethereum"
    contract_address VARCHAR(100),-- Smart contract address (tokens)
    is_minable BOOLEAN,
    ...
)
```

**Purpose:** Stores crypto-ONLY attributes that don't apply to stocks/ETFs.

---

### 4️⃣ **ETFS Table** (ETF-Specific Metadata)
```sql
CREATE TABLE etfs (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER,             -- FK → assets.id
    inception_date DATE,          -- When ETF launched
    net_assets BIGINT,            -- Total assets under management
    expense_ratio FLOAT,          -- Annual fee (%)
    dividend_yield FLOAT,         -- Annual dividend %
    holdings_count INTEGER,       -- Number of stocks in ETF
    ...
)
```

---

### 5️⃣ **MUTUAL_FUNDS Table** (Mutual Fund Metadata)
```sql
CREATE TABLE mutual_funds (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER,             -- FK → assets.id
    fund_family VARCHAR(200),     -- "Vanguard", "Fidelity"
    minimum_investment BIGINT,    -- Minimum to invest
    expense_ratio FLOAT,
    load_type VARCHAR(50),        -- "no-load", "front-load", "back-load"
    turnover_rate FLOAT,
    ...
)
```

---

## 🔄 **How Collectors Work**

### **Data Collection Flow:**

```
1. COLLECTOR STAGE (Asset Metadata)
   ├─ crypto_manager.py   → Fetches crypto info → Adds to ASSETS table
   ├─ stocks_manager.py   → Fetches stock info → Adds to ASSETS table
   ├─ etf_manager.py      → Fetches ETF info   → Adds to ASSETS table
   └─ mutual_fund_manager.py → Fetches fund info → Adds to ASSETS table

2. PRICE COLLECTION STAGE (Historical Data)
   └─ daily_price_collector.py
       ├─ For each asset in ASSETS table:
       │   ├─ Query asset by asset_id
       │   ├─ Fetch price history (25 years if possible)
       │   └─ Insert into DAILY_PRICES with asset_id foreign key
       │
       ├─ Stocks:  yfinance → daily_prices (asset_id=1,2,3...)
       ├─ Crypto:  CoinGecko API → daily_prices (asset_id=50,51,52...)
       ├─ ETFs:    yfinance → daily_prices (asset_id=100,101...)
       └─ Funds:   yfinance/Manual → daily_prices (asset_id=200,201...)
```

---

## 💡 **Example: How Bitcoin Price Gets Stored**

### Step 1: Asset Registration (crypto_manager.py)
```python
# crypto_manager.py creates the asset record
new_asset = Asset(
    symbol='bitcoin',
    name='Bitcoin',
    type='crypto',
    exchange='CoinGecko',
    market_cap=1_200_000_000_000  # $1.2 trillion
)
db.add(new_asset)
db.commit()  # Gets assigned asset_id = 50
```

### Step 2: Price History Collection (daily_price_collector.py)
```python
# daily_price_collector.py fetches Bitcoin prices
btc = db.query(Asset).filter(Asset.symbol == 'bitcoin').first()

for each day in last 25 years:
    price_record = DailyPrice(
        asset_id=btc.id,           # asset_id = 50
        date='2025-10-05',
        open_price=62500.00,
        close_price=63200.00,
        volume=25000000
    )
    db.add(price_record)

db.commit()  # Now Bitcoin has price history!
```

### Step 3: Querying Bitcoin Prices
```python
# Get Bitcoin asset
btc = db.query(Asset).filter(Asset.symbol == 'bitcoin').first()

# Get all Bitcoin prices (automatically linked via asset_id)
btc_prices = db.query(DailyPrice).filter(
    DailyPrice.asset_id == btc.id
).order_by(DailyPrice.date).all()

# Result: List of all Bitcoin daily prices for 25 years!
```

---

## 🎯 **Key Benefits of This Architecture**

### ✅ **1. Universal Price Storage**
- **One table** (`daily_prices`) for ALL asset types
- No need for `crypto_prices`, `stock_prices`, `etf_prices` tables
- Consistent schema across all instruments

### ✅ **2. Easy Querying**
```python
# Get ALL prices for ANY asset (stock, crypto, ETF, etc.)
asset = db.query(Asset).filter(Asset.symbol == 'AAPL').first()
prices = asset.daily_prices  # Relationship automatically handles it!
```

### ✅ **3. Type-Specific Metadata**
- Common attributes → `assets` table (symbol, name, market_cap)
- Type-specific → Separate tables (cryptos, etfs, mutual_funds)
- Price history → `daily_prices` (universal)

### ✅ **4. Scalability**
- Add new asset types without changing `daily_prices` table
- Add new assets without modifying schema
- Support 10,000+ assets with millions of price records

---

## 📊 **Table Relationships Diagram**

```
                    ┌─────────────────┐
                    │     ASSETS      │
                    │  (Master Table) │
                    │                 │
                    │ • symbol        │
                    │ • name          │
                    │ • type          │
                    │ • market_cap    │
                    └─────────┬───────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ↓             ↓             ↓
        ┌───────────┐  ┌────────────┐  ┌──────────┐
        │  CRYPTOS  │  │    ETFS    │  │  MUTUAL  │
        │           │  │            │  │  FUNDS   │
        │ • supply  │  │ • holdings │  │ • family │
        │ • algo    │  │ • expense  │  │ • load   │
        └───────────┘  └────────────┘  └──────────┘
                │
                │ (All assets use same price table)
                │
                ↓
        ┌──────────────────┐
        │  DAILY_PRICES    │
        │  (Universal)     │
        │                  │
        │ • asset_id (FK)  │
        │ • date           │
        │ • open/close     │
        │ • volume         │
        └──────────────────┘
```

---

## 🚀 **How Recommendation Engine Uses This**

The recommendation engine in `analyzer.py` queries data like this:

```python
def analyze_asset(db, asset_id, asset_type):
    # 1. Get price history (works for ANY asset type)
    prices_df = get_asset_prices_from_db(db, asset_id, days=365)
    
    # 2. Calculate technical scores
    technical = calculate_technical_score(prices_df)  # RSI, MACD, etc.
    
    # 3. Get fundamentals (if stock)
    if asset_type == 'stock':
        fundamentals = get_fundamentals_from_db(db, asset_id)
        fundamental = calculate_fundamental_score_stock(fundamentals)
    
    # 4. Get news sentiment
    news = get_asset_news_from_db(db, asset_id, days=30)
    sentiment = calculate_sentiment_score(news)
    
    # 5. Calculate final score
    final_score = (
        technical['score'] * 0.25 +
        fundamental['score'] * 0.30 +
        sentiment['score'] * 0.25 +
        risk['score'] * 0.20
    )
```

**Key Point:** Whether it's Bitcoin, Apple stock, or an ETF, they all:
1. Have an entry in `assets` table
2. Have price history in `daily_prices` table (linked by asset_id)
3. Get scored the SAME way by the recommendation engine

---

## 📝 **Summary**

| **Component** | **Purpose** | **Examples** |
|---------------|-------------|--------------|
| **assets** | Master registry of all tradeable instruments | AAPL, bitcoin, SPY, VTSAX |
| **daily_prices** | Universal price history (OHLCV data) | Stores prices for ALL asset types |
| **cryptos** | Crypto-only metadata | Supply, blockchain, algorithm |
| **etfs** | ETF-only metadata | Holdings, expense ratio |
| **mutual_funds** | Fund-only metadata | Fund family, minimum investment |

**The Magic:** 
- ✨ All assets share the **same price table** (`daily_prices`)
- 🔗 Linked via `asset_id` foreign key
- 📈 Enables universal analysis across ALL asset types
- 🎯 Powers the recommendation engine's scoring system

---

**Need More Details?** Check the model files:
- `models/assets.py` - Universal asset model
- `models/daily_price.py` - Price history model
- `collectors/daily_price_collector.py` - How prices get collected
