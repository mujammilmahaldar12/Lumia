#!/usr/bin/env python3
"""
Universal Asset Collector
Collects data for stocks, ETFs, mutual funds, and cryptocurrencies
"""
import sys
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from io import StringIO
import yfinance as yf
import requests
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Asset, ETF, MutualFund, Crypto

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalAssetCollector:
    """Collects all types of financial assets with comprehensive data extraction"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.collected_assets = []
        self.failed_assets = []
        
        # Setup requests session with headers (like company collector)
        self.requests_session = requests.Session()
        self.requests_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    # ========================= DATA SOURCE METHODS =========================
    
    def get_comprehensive_us_stock_list(self) -> List[str]:
        """Get comprehensive list of US stocks from multiple sources"""
        logger.info("🇺🇸 Getting comprehensive US stock list...")
        
        # Start with popular stocks (guaranteed to have good data)
        popular_us_stocks = [
            # Tech Giants (FAANG+)
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 
            'CRM', 'ORCL', 'IBM', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'MU', 'AMAT',
            
            # Financial Giants
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB', 'PNC', 'TFC',
            'COF', 'BK', 'STT', 'FITB', 'HBAN', 'RF', 'CFG', 'KEY', 'ZION', 'CMA',
            
            # Healthcare & Pharma
            'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'LLY', 'AMGN',
            'GILD', 'REGN', 'VRTX', 'BIIB', 'ISRG', 'SYK', 'BSX', 'MDT', 'EW', 'ZBH',
            
            # Consumer Staples & Discretionary
            'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'COST',
            'DIS', 'CMCSA', 'VZ', 'T', 'NFLX', 'ROKU', 'SNAP', 'TWTR', 'PINS', 'UBER',
            
            # Industrial & Manufacturing
            'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'FDX', 'LMT', 'RTX', 'DE', 'EMR',
            'ITW', 'PH', 'ETN', 'ROK', 'DOV', 'XYL', 'PCAR', 'CMI', 'EMR', 'FTV',
            
            # Energy & Utilities
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PXD', 'KMI', 'OXY', 'PSX', 'VLO', 'MPC',
            'NEE', 'DUK', 'SO', 'AEP', 'EXC', 'XEL', 'WEC', 'ES', 'AWK', 'ATO',
            
            # Materials & Chemicals
            'LIN', 'APD', 'SHW', 'ECL', 'DD', 'DOW', 'PPG', 'NEM', 'FCX', 'VMC', 'MLM',
            
            # Real Estate & REITs
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'EXR', 'AVB', 'EQR', 'WY', 'ARE',
            
            # Technology Services
            'V', 'MA', 'PYPL', 'SQ', 'ADSK', 'CRM', 'NOW', 'INTU', 'FISV', 'FIS', 'GPN',
            
            # Retail & E-commerce
            'AMZN', 'WMT', 'HD', 'TGT', 'LOW', 'COST', 'TJX', 'DLTR', 'DG', 'ROST',
            
            # Biotech & Life Sciences
            'MRNA', 'BNTX', 'MODERNA', 'REGN', 'GILD', 'AMGN', 'BIIB', 'CELG'
        ]
        
        # Try to get S&P 500 list from web sources
        try:
            # Wikipedia S&P 500 list
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            response = self.requests_session.get(sp500_url)
            if response.status_code == 200:
                tables = pd.read_html(response.content)
                if len(tables) > 0:
                    sp500_symbols = tables[0]['Symbol'].tolist()
                    logger.info(f"Found {len(sp500_symbols)} S&P 500 symbols from Wikipedia")
                    popular_us_stocks.extend(sp500_symbols)
        except Exception as e:
            logger.warning(f"Failed to fetch S&P 500 list: {e}")
        
        # Remove duplicates and return
        unique_symbols = list(set(popular_us_stocks))
        logger.info(f"Total unique US symbols: {len(unique_symbols)}")
        return unique_symbols
    
    def get_comprehensive_indian_stock_list(self) -> List[str]:
        """Get comprehensive list of Indian stocks from NSE"""
        logger.info("🇮🇳 Getting comprehensive Indian stock list...")
        
        all_symbols = []
        
        # 1. Get NSE Main Board Equity List (2100+ stocks)
        try:
            nse_equity_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
            logger.info(f"Fetching NSE equity list from: {nse_equity_url}")
            
            response = self.requests_session.get(nse_equity_url, timeout=30)
            if response.status_code == 200:
                from io import StringIO
                csv_data = StringIO(response.text)
                df = pd.read_csv(csv_data)
                
                # NSE CSV typically has 'SYMBOL' column
                if 'SYMBOL' in df.columns:
                    symbols = [f"{symbol.strip()}.NS" for symbol in df['SYMBOL'].tolist() if symbol.strip()]
                    all_symbols.extend(symbols)
                    logger.info(f"✅ Found {len(symbols)} NSE main board stocks")
                else:
                    logger.warning(f"SYMBOL column not found. Available columns: {df.columns.tolist()}")
            else:
                logger.warning(f"NSE equity CSV request failed with status: {response.status_code}")
        except Exception as e:
            logger.warning(f"NSE main board CSV failed: {e}")
        
        # 2. Get NSE SME (Small & Medium Enterprise) stocks
        try:
            nse_sme_url = "https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv"
            logger.info(f"Fetching NSE SME list from: {nse_sme_url}")
            
            response = self.requests_session.get(nse_sme_url, timeout=30)
            if response.status_code == 200:
                from io import StringIO
                csv_data = StringIO(response.text)
                df = pd.read_csv(csv_data)
                
                if 'SYMBOL' in df.columns:
                    sme_symbols = [f"{symbol.strip()}.NS" for symbol in df['SYMBOL'].tolist() if symbol.strip()]
                    all_symbols.extend(sme_symbols)
                    logger.info(f"✅ Found {len(sme_symbols)} NSE SME stocks")
                else:
                    logger.warning(f"SME SYMBOL column not found. Available columns: {df.columns.tolist()}")
            else:
                logger.warning(f"NSE SME CSV request failed with status: {response.status_code}")
        except Exception as e:
            logger.warning(f"NSE SME CSV failed: {e}")
        
        # 3. If we got data from NSE, return it
        if all_symbols:
            # Remove duplicates
            unique_symbols = list(set(all_symbols))
            logger.info(f"🎯 Total unique NSE symbols collected: {len(unique_symbols)}")
            return unique_symbols
        
        # 4. Try alternative sources if NSE direct CSV fails
        logger.warning("NSE CSV sources failed, trying alternative methods...")
        
        # Try to get BSE listed companies as additional source
        try:
            # BSE doesn't have a direct CSV, but we can use major BSE symbols
            major_bse_symbols = [
                'RELIANCE.BO', 'TCS.BO', 'HDFCBANK.BO', 'INFY.BO', 'HINDUNILVR.BO',
                'HDFC.BO', 'ICICIBANK.BO', 'KOTAKBANK.BO', 'ITC.BO', 'SBIN.BO',
                'LT.BO', 'AXISBANK.BO', 'ASIANPAINT.BO', 'MARUTI.BO', 'BAJFINANCE.BO',
                'BHARTIARTL.BO', 'WIPRO.BO', 'ULTRACEMCO.BO', 'DMART.BO', 'NESTLEIND.BO',
                'TATAMOTORS.BO', 'TATASTEEL.BO', 'JSWSTEEL.BO', 'HINDALCO.BO', 'VEDL.BO'
            ]
            all_symbols.extend(major_bse_symbols)
            logger.info(f"Added {len(major_bse_symbols)} major BSE symbols")
        except Exception as e:
            logger.warning(f"BSE symbols addition failed: {e}")
        
        # 5. Fallback: Comprehensive hardcoded list of major Indian companies (if all sources fail)
        if not all_symbols:
            logger.warning("All data sources failed, using comprehensive fallback list")
            
            # Comprehensive fallback list of major Indian companies
            major_indian_stocks = [
            # Banking & Financial Services (Top 50)
            'HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK', 'INDUSINDBK', 'FEDERALBNK', 
            'BANKBARODA', 'PNB', 'CANBK', 'IDFCFIRSTB', 'RBLBANK', 'YESBANK', 'AUBANK', 'BANDHANBNK',
            'DCBBANK', 'SOUTHBANK', 'IOB', 'UNIONBANK', 'INDIANB', 'CENTRALBK', 'UCO', 'JKBANK',
            
            # IT Services & Technology (Top 30)
            'TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTI', 'MINDTREE', 'MPHASIS', 'COFORGE', 'LTTS',
            'PERSISTENT', 'CYIENT', 'OFSS', 'SONATSOFTW', 'KPIT', 'INTELLECT', 'RAMCOIND', 'MASTEK',
            'ZENSAR', 'HEXATECHNO', 'NIITTECH', 'BIRLASOFT', '3IINFOTECH', 'ROLTA', 'NELCO',
            
            # Oil & Gas, Energy (Top 20)
            'RELIANCE', 'ONGC', 'IOC', 'BPCL', 'HINDPETRO', 'GAIL', 'OIL', 'MGL', 'IGL', 'PETRONET',
            'CASTROLIND', 'AEGISCHEM', 'DEEPAKFERT', 'GSFC', 'GNFC', 'CHAMBLFERT', 'MADRASFERT',
            
            # Automobiles & Auto Components (Top 25)
            'MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT', 'TVSMOTOR', 'ASHOKLEY',
            'FORCEMOT', 'ESCORTS', 'BALKRISIND', 'MRF', 'APOLLOTYRE', 'CEAT', 'JK TYRE', 'MOTHERSON',
            'BHARAT FORGE', 'EXIDEIND', 'AMARAJABAT', 'BOSCHLTD', 'WABCOINDIA', 'SUNDRMFAST', 'SUPRAJIT',
            
            # Pharmaceuticals & Healthcare (Top 30)
            'SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BIOCON', 'LUPIN', 'CADILAHC', 'GLENMARK',
            'TORNTPHARM', 'AUROPHARMA', 'ALKEM', 'LALPATHLAB', 'APOLLOHOSP', 'FORTIS', 'MAXHEALTH',
            'IPCALAB', 'STRIDES', 'GRANULES', 'DIVIS', 'SYNGENE', 'NATCOPHAR', 'ABBOTINDIA', 'PFIZER',
            'GSK', 'NOVARTIS', 'SANOFI', 'AJANTPHARM', 'STAR', 'WOCKPHARMA', 'FDC',
            
            # FMCG & Consumer Goods (Top 25)
            'HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR', 'GODREJCP', 'MARICO', 'COLPAL',
            'EMAMILTD', 'BAJAJCON', 'VBL', 'TATACONSUM', 'UBL', 'RADICO', 'MCDOWELL-N', 'UNITDSPR',
            'JYOTHYLAB', 'KANSAINER', 'PRSMJOHNSN', 'GILLETTE', 'HONAUT', 'WHIRLPOOL', 'VOLTAS', 'BLUESTAR', 'HAVELLS',
            
            # Metals & Mining (Top 30)
            'TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'VEDL', 'COALINDIA', 'SAIL', 'NMDC', 'JINDALSTEL',
            'ADANIENT', 'WELCORP', 'JSPL', 'RATNAMANI', 'APL', 'MOIL', 'NATIONALUM', 'HINDZINC',
            'HINDUSTAN ZINC', 'WELSPUNIND', 'LLOYDS METALS', 'KALYANKJIL', 'JSWENERGY', 'ADANIPORTS',
            
            # Cement & Construction (Top 20)
            'ULTRACEMCO', 'SHREECEM', 'ACC', 'AMBUJACEMENT', 'DALMIACEM', 'RAMCOCEM', 'HEIDELBERG', 'JK CEMENT',
            'ORIENT CEMENT', 'PRISM CEMENT', 'BURNPUR', 'KESORAMIND', 'BANGUR', 'STARCEMENT', 'DECCAN',
            
            # Telecom & Communication (Top 10)
            'BHARTIARTL', 'IDEA', 'RCOM', 'TATACOMM', 'GTLINFRA', 'INDUS TOWERS', 'TEJAS', 'STERLTECH',
            
            # Power & Utilities (Top 25)
            'NTPC', 'POWERGRID', 'ADANIPOWER', 'TATAPOWER', 'NHPC', 'SJVN', 'THERMAX', 'BHEL', 'JSW ENERGY',
            'RELINFRA', 'GMRINFRA', 'ADANIGREEN', 'SUZLON', 'ORIENTELEC', 'CROMPTON', 'KEC', 'KALPATPOWR',
            
            # Infrastructure & Logistics (Top 20)
            'LT', 'ADANIPORTS', 'CONCOR', 'IRB', 'SADBHAV', 'HCC', 'PNCINFRA', 'NBCC', 'GMBREW',
            'ARSS', 'J&KBANK', 'PFC', 'RECLTD', 'IRFC', 'HUDCO', 'IIFCL', 'TFCILTD',
            
            # Retail & Consumer Discretionary (Top 15)
            'DMART', 'TRENT', 'SHOPERSTOP', 'PANTALOONS', 'V-MART', 'ADITYA BIRLA FASHION', 'PAGE', 'RAYMOND',
            'SIYARAM', 'ARVIND', 'RUPA', 'DOLLAR', 'RELAXO', 'BATA', 'LIBERTY',
            
            # Insurance & NBFC (Top 25)
            'SBILIFE', 'HDFCLIFE', 'ICICIPRULI', 'BAJAJFINSV', 'BAJFINANCE', 'LICHSGFIN', 'SRTRANSFIN',
            'M&MFIN', 'CHOLAFIN', 'L&TFH', 'PEL', 'MANAPPURAM', 'MUTHOOTFIN', 'ABFRL', 'DHFL',
            'INDIABULL', 'EDELWEISS', 'CAPFIRST', 'RELIGARE', 'SHRIRAMCIT',
            
            # Media & Entertainment (Top 15)
            'ZEEL', 'SUNTV', 'NETWORK18', 'JAGRAN', 'SAREGAMA', 'TIPS', 'BALAJITELE', 'EROS',
            'INOXLEISUR', 'PVR', 'ADLABS', 'BSEL', 'UFO', 'MINDTECK', 'DEN',
            
            # Real Estate & Housing (Top 15)
            'DLF', 'GODREJPROP', 'OBEROIRLTY', 'BRIGADE', 'PRESTIGE', 'SOBHA', 'PURAVANKARA', 'UNITECH',
            'INDIABULLS REAL ESTATE', 'ANANT RAJ', 'ASHIANA', 'MAHLIFE', 'KOLTE-PATIL', 'PARSVNATH', 'OMAXE',
            
            # Chemicals & Specialty Chemicals (Top 20)
            'ASIANPAINT', 'BERGERPAINTS', 'PIDILITIND', 'DEEPAKNTR', 'SRF', 'AARTI', 'TATACHEM', 'GHCL',
            'NOCIL', 'NAVINFLOUR', 'ALKYLAMINE', 'BALRAMCHIN', 'CHEMPLAST', 'FERTILISERS', 'TATAELXSI', 'ROSSARI',
            
            # Capital Goods & Engineering (Top 25)
            'BHEL', 'BEL', 'HAL', 'BEML', 'CUMMINSIND', 'SIEMENS', 'ABB', 'SCHNEIDER', 'L&T', 'GODREJIND',
            'THERMAX', 'KIRLOSENG', 'SKFINDIA', 'TIMKEN', 'FAG', 'SCHAEFFLER', 'TEXRAIL', 'TITAGARH',
            
            # Agriculture & Food Processing (Top 15)
            'KRBL', 'LTKASHMIR', 'RUCHISOYA', 'ADANI WILMAR', 'GODREJAGRO', 'RALLIS', 'COROMANDEL', 'CHAMBAL',
            'NAGARFERT', 'MADHUCON', 'VARUN', 'VST', 'ZUARI', 'MANGALAM', 'KEIFERT'
        ]
        
            # Add .NS suffix for NSE listing
            symbols = [f"{symbol}.NS" for symbol in major_indian_stocks]
            
            # Also add BSE symbols for major companies
            major_bse = ['RELIANCE.BO', 'TCS.BO', 'HDFCBANK.BO', 'INFY.BO', 'HINDUNILVR.BO', 
                         'HDFC.BO', 'ICICIBANK.BO', 'KOTAKBANK.BO', 'ITC.BO', 'SBIN.BO']
            symbols.extend(major_bse)
            all_symbols = symbols
        
        # Remove duplicates and return final list
        final_symbols = list(set(all_symbols))
        logger.info(f"🎯 Total Indian symbols (final): {len(final_symbols)}")
        return final_symbols

    def get_comprehensive_etf_list(self) -> List[str]:
        """Get comprehensive list of ETFs from multiple categories"""
        logger.info("📈 Getting comprehensive ETF list...")
        
        etf_symbols = [
            # US Broad Market ETFs
            "SPY", "QQQ", "IWM", "VTI", "VOO", "IVV", "VEA", "VWO", "IEFA", "EEM", "ITOT", "SCHA", "SCHB",
            
            # Sector ETFs - Technology
            "XLK", "VGT", "FTEC", "IGV", "SOXX", "SMH", "KWEB", "ARKK", "ARKG", "ARKW",
            
            # Sector ETFs - Financial  
            "XLF", "VFH", "KRE", "KBE", "KBWB", "IAT", "FREL",
            
            # Sector ETFs - Healthcare
            "XLV", "VHT", "IHI", "IBB", "XBI", "ARKG", "LABU",
            
            # Sector ETFs - Energy & Utilities
            "XLE", "XLU", "VDE", "ICLN", "PBW", "QCLN", "ERX", "UCO",
            
            # Sector ETFs - Consumer
            "XLY", "XLP", "VCR", "VDC", "RTH", "PEJ", "FDIS",
            
            # Sector ETFs - Industrial & Materials
            "XLI", "XLB", "VIS", "VAW", "IYT", "PAVE", "JETS",
            
            # Real Estate
            "XLRE", "VNQ", "SCHH", "REM", "MORT", "REZ",
            
            # Bond ETFs - Government
            "AGG", "BND", "TLT", "IEF", "SHY", "GOVT", "SCHO", "SCHR", "SPTS",
            
            # Bond ETFs - Corporate
            "LQD", "HYG", "JNK", "VCIT", "VGIT", "IGIB", "SHYG", "SJNK",
            
            # Bond ETFs - International
            "BNDX", "VTEB", "MUB", "TFI", "SUB", "PZA",
            
            # Bond ETFs - Inflation Protected
            "TIP", "VTIP", "SCHP", "STIP", "LTPZ",
            
            # International Developed Markets
            "VGK", "VPL", "EFA", "IEFA", "VEA", "ACWI", "VXUS", "IXUS",
            
            # International - Regional/Country Specific
            "EWJ", "EWZ", "FXI", "EWY", "EWT", "EWU", "EWG", "EWC", "EWA", "EWS", "EWW", "EWH",
            
            # Emerging Markets
            "VWO", "EEM", "IEMG", "SCHE", "EWX", "VGE", "SPEM",
            
            # Commodities - Precious Metals
            "GLD", "SLV", "IAU", "SIVR", "PPLT", "PALL", "GLTR",
            
            # Commodities - Energy & Agriculture
            "USO", "UNG", "DBA", "DBC", "PDBC", "CORN", "SOYB", "WEAT",
            
            # Currency ETFs
            "UUP", "FXE", "FXY", "FXB", "CYB", "FXA", "FXC",
            
            # Alternative/Strategy ETFs
            "VIX", "UVXY", "SVXY", "TQQQ", "SQQQ", "UPRO", "SPXU", "TNA", "TZA",
            
            # Dividend ETFs
            "VYM", "SCHD", "DVY", "VIG", "DGRO", "NOBL", "HDV", "FDVV",
            
            # Growth/Value ETFs
            "VUG", "VTV", "IWF", "IWD", "MTUM", "QUAL", "USMV", "VMOT",
            
            # ESG/Sustainable ETFs
            "ESG", "ESGU", "ESGV", "DSI", "ICLN", "ESGE", "VSGX",
            
            # Indian ETFs (NSE)
            "NIFTYBEES.NS", "JUNIORBEES.NS", "BANKBEES.NS", "GOLDBEES.NS", "ICICINF50.NS", 
            "LIQUIDBEES.NS", "INFRABEES.NS", "PSUBNKBEES.NS", "PHARMABEES.NS", "ITBEES.NS",
            
            # Additional Popular ETFs
            "ARKF", "ARKG", "ARKQ", "PFF", "SPLG", "SPDW", "SPYG", "SPYV", "MGK", "MGV"
        ]
        
        logger.info(f"Total ETF symbols: {len(etf_symbols)}")
        return etf_symbols
    
    def get_comprehensive_crypto_list(self) -> List[str]:
        """Get comprehensive list of cryptocurrencies"""
        logger.info("₿ Getting comprehensive crypto list...")
        
        crypto_symbols = [
            # Top 10 by Market Cap
            "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD", "DOGE-USD", "DOT-USD", "AVAX-USD", "SHIB-USD",
            
            # Major Altcoins (11-30)
            "MATIC-USD", "LTC-USD", "TRX-USD", "UNI-USD", "LINK-USD", "ATOM-USD", "XMR-USD", "ETC-USD", "BCH-USD", "ICP-USD",
            "FIL-USD", "VET-USD", "HBAR-USD", "ALGO-USD", "MANA-USD", "SAND-USD", "AXS-USD", "CRV-USD", "SUSHI-USD", "COMP-USD",
            
            # DeFi Tokens
            "AAVE-USD", "MKR-USD", "YFI-USD", "SNX-USD", "BAL-USD", "REN-USD", "KNC-USD", "LRC-USD", "ZRX-USD", "BAND-USD",
            
            # Layer 1 Blockchains
            "NEAR-USD", "FTM-USD", "LUNA-USD", "ONE-USD", "CELO-USD", "ROSE-USD", "FLOW-USD", "EGLD-USD", "KLAY-USD", "XTZ-USD",
            
            # Exchange Tokens
            "HT-USD", "LEO-USD", "CRO-USD", "OKB-USD", "FTT-USD",
            
            # Meme Coins & Community
            "ELON-USD", "FLOKI-USD", "BABY DOGE-USD", "SAFEMOON-USD",
            
            # Enterprise/Institutional
            "XLM-USD", "USDC-USD", "USDT-USD", "BUSD-USD", "DAI-USD", "TUSD-USD",
            
            # Gaming & Metaverse
            "ENJ-USD", "GALA-USD", "CHZ-USD", "FLOW-USD", "IMX-USD", "AUDIO-USD",
            
            # Privacy Coins
            "ZEC-USD", "DASH-USD", "DCR-USD",
            
            # Infrastructure & Utility
            "BAT-USD", "GRT-USD", "LPT-USD", "NMR-USD", "REP-USD", "STORJ-USD"
        ]
        
        logger.info(f"Total crypto symbols: {len(crypto_symbols)}")
        return crypto_symbols

    # ========================= ENHANCED STOCK COLLECTION =========================
    
    def collect_us_stocks(self) -> int:
        """Collect comprehensive US stocks from various sources"""
        logger.info("🇺🇸 Collecting US stocks...")
        
        us_symbols = self.get_comprehensive_us_stock_list()
        logger.info(f"Found {len(us_symbols)} US stocks to collect")
        
        return self._collect_stocks(us_symbols, "US", "USD")
    
    def collect_indian_stocks(self) -> int:
        """Collect comprehensive Indian stocks from NSE/BSE"""
        logger.info("🇮🇳 Collecting Indian stocks...")
        
        indian_symbols = self.get_comprehensive_indian_stock_list()
        logger.info(f"Found {len(indian_symbols)} Indian stocks to collect")
        
        return self._collect_stocks(indian_symbols, "IN", "INR")
    
    def _get_sp500_stocks(self) -> List[str]:
        """Get S&P 500 stock symbols"""
        try:
            # Common S&P 500 stocks
            sp500_symbols = [
                "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "TSLA", "META", "NVDA",
                "BRK-B", "UNH", "JNJ", "JPM", "V", "PG", "HD", "MA", "BAC", "ABBV",
                "PFE", "KO", "AVGO", "PEP", "TMO", "COST", "DIS", "ABT", "DHR", "VZ",
                "ADBE", "NFLX", "XOM", "NKE", "WMT", "T", "CRM", "CSCO", "MRK", "CVX",
                "INTC", "QCOM", "TXN", "MDT", "UPS", "HON", "IBM", "AMGN", "C", "WFC"
            ]
            return sp500_symbols
        except Exception as e:
            logger.error(f"Failed to get S&P 500 stocks: {e}")
            return []
    
    def _get_nasdaq100_stocks(self) -> List[str]:
        """Get NASDAQ 100 stock symbols"""
        nasdaq100_symbols = [
            "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "TSLA", "META", "NVDA",
            "ADBE", "NFLX", "PYPL", "INTC", "CMCSA", "PEP", "CSCO", "COST", "TMUS",
            "AVGO", "TXN", "QCOM", "SBUX", "INTU", "ISRG", "AMD", "MU", "BKNG",
            "ATVI", "FISV", "ADP", "CSX", "VRTX", "GILD", "REGN", "MRNA", "MDLZ"
        ]
        return nasdaq100_symbols
    
    def _get_dow_jones_stocks(self) -> List[str]:
        """Get Dow Jones Industrial Average stocks"""
        dow_symbols = [
            "AAPL", "MSFT", "JNJ", "V", "PG", "JPM", "HD", "UNH", "DIS", "BA",
            "MCD", "CRM", "CAT", "GS", "AXP", "IBM", "WMT", "MMM", "TRV", "NKE",
            "KO", "HON", "MRK", "VZ", "CSCO", "CVX", "INTC", "WBA", "DOW"
        ]
        return dow_symbols
    
    def _get_popular_us_stocks(self) -> List[str]:
        """Get additional popular US stocks"""
        popular_stocks = [
            "SPCE", "PLTR", "RIOT", "MARA", "COIN", "HOOD", "AMC", "GME", "BB",
            "WISH", "CLOV", "SOFI", "LCID", "RIVN", "F", "GE", "AAL", "DAL",
            "UBER", "LYFT", "SNAP", "TWTR", "PINS", "ZM", "PTON", "ROKU", "SQ"
        ]
        return popular_stocks
    
    def _get_nse_stocks(self) -> List[str]:
        """Get NSE stock symbols"""
        nse_symbols = [
            # NIFTY 50 stocks
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
            "HDFC.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "BHARTIARTL.NS", "ITC.NS",
            "SBIN.NS", "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS",
            "BAJFINANCE.NS", "HCLTECH.NS", "WIPRO.NS", "ULTRACEMCO.NS", "DMART.NS",
            "NESTLEIND.NS", "TITAN.NS", "BAJAJFINSV.NS", "POWERGRID.NS", "TECHM.NS",
            
            # Additional popular NSE stocks
            "ADANIPORTS.NS", "COALINDIA.NS", "NTPC.NS", "ONGC.NS", "IOC.NS",
            "TATAMOTORS.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS",
            "VEDL.NS", "SAIL.NS", "NMDC.NS", "MOIL.NS", "CESC.NS", "NHPC.NS"
        ]
        return nse_symbols
    
    def _get_bse_stocks(self) -> List[str]:
        """Get BSE stock symbols"""
        bse_symbols = [
            # Major BSE stocks
            "RELIANCE.BO", "TCS.BO", "HDFCBANK.BO", "INFY.BO", "HINDUNILVR.BO",
            "HDFC.BO", "ICICIBANK.BO", "KOTAKBANK.BO", "ITC.BO", "SBIN.BO",
            "LT.BO", "AXISBANK.BO", "ASIANPAINT.BO", "MARUTI.BO", "BAJFINANCE.BO"
        ]
        return bse_symbols
    
    def _collect_stocks(self, symbols: List[str], country: str, currency: str) -> int:
        """Collect stock data using yfinance"""
        collected = 0
        
        for i, symbol in enumerate(symbols, 1):
            try:
                logger.info(f"Collecting stock {i}/{len(symbols)}: {symbol}")
                
                # Check if already exists
                existing = self.session.query(Asset).filter_by(symbol=symbol).first()
                if existing:
                    logger.info(f"Stock {symbol} already exists, skipping")
                    continue
                
                # Get stock info
                stock = yf.Ticker(symbol)
                info = stock.info
                
                if not info or 'symbol' not in info:
                    logger.warning(f"No data found for {symbol}")
                    self.failed_assets.append(symbol)
                    continue
                
                # Determine exchange
                exchange = self._determine_stock_exchange(symbol, country)
                
                # Create asset
                asset = Asset(
                    symbol=symbol,
                    name=info.get('longName', info.get('shortName', symbol)),
                    type='stock',
                    subtype=self._determine_stock_category(info.get('marketCap', 0)),
                    exchange=exchange,
                    country=country,
                    currency=currency,
                    sector=info.get('sector'),
                    industry=info.get('industry'),
                    market_cap=info.get('marketCap'),
                    description=info.get('longBusinessSummary'),
                    website=info.get('website'),
                    dividend_yield=info.get('dividendYield'),
                    is_active=True
                )
                
                self.session.add(asset)
                self.collected_assets.append(asset)
                collected += 1
                
                # Commit in batches
                if collected % 50 == 0:
                    self.session.commit()
                    logger.info(f"Committed {collected} stocks")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to collect {symbol}: {e}")
                self.failed_assets.append(symbol)
                continue
        
        self.session.commit()
        logger.info(f"✅ Collected {collected} stocks from {country}")
        return collected
    
    def _determine_stock_exchange(self, symbol: str, country: str) -> str:
        """Determine the exchange for a stock symbol"""
        if country == "US":
            if any(x in symbol for x in [".OB", ".PK"]):
                return "OTC"
            elif symbol in self._get_nasdaq100_stocks():
                return "NASDAQ"
            else:
                return "NYSE"
        elif country == "IN":
            if symbol.endswith(".NS"):
                return "NSE"
            elif symbol.endswith(".BO"):
                return "BSE"
        return "Unknown"
    
    def _determine_stock_category(self, market_cap: int) -> str:
        """Determine stock category based on market cap"""
        if not market_cap:
            return "unknown"
        
        if market_cap >= 10_000_000_000:  # $10B+
            return "large_cap"
        elif market_cap >= 2_000_000_000:  # $2B+
            return "mid_cap"
        else:
            return "small_cap"
    
    # ========================= ETF COLLECTION =========================
    
    def collect_etfs(self) -> int:
        """Collect comprehensive ETFs from all categories"""
        logger.info("📈 Collecting ETFs...")
        
        etf_symbols = self.get_comprehensive_etf_list()
        logger.info(f"Found {len(etf_symbols)} ETFs to collect")
        
        return self._collect_etfs(etf_symbols)
    
    def _collect_etfs(self, symbols: List[str]) -> int:
        """Collect ETF data"""
        collected = 0
        
        for i, symbol in enumerate(symbols, 1):
            try:
                logger.info(f"Collecting ETF {i}/{len(symbols)}: {symbol}")
                
                # Check if already exists
                existing = self.session.query(Asset).filter_by(symbol=symbol).first()
                if existing:
                    logger.info(f"ETF {symbol} already exists, skipping")
                    continue
                
                # Get ETF info
                etf = yf.Ticker(symbol)
                info = etf.info
                
                if not info or 'symbol' not in info:
                    logger.warning(f"No data found for {symbol}")
                    self.failed_assets.append(symbol)
                    continue
                
                # Determine details
                exchange = "NSE" if symbol.endswith(".NS") else "NYSE"
                country = "IN" if symbol.endswith(".NS") else "US"
                currency = "INR" if symbol.endswith(".NS") else "USD"
                
                # Create asset
                asset = Asset(
                    symbol=symbol,
                    name=info.get('longName', info.get('shortName', symbol)),
                    type='etf',
                    exchange=exchange,
                    country=country,
                    currency=currency,
                    market_cap=info.get('totalAssets'),
                    total_assets=info.get('totalAssets'),
                    expense_ratio=info.get('annualReportExpenseRatio'),
                    description=info.get('longBusinessSummary'),
                    is_active=True
                )
                
                self.session.add(asset)
                self.session.flush()  # Flush to get the asset.id
                
                # Add ETF-specific details if we have them
                if info.get('annualReportExpenseRatio') or info.get('totalAssets'):
                    etf_details = ETF(
                        asset_id=asset.id,
                        nav=info.get('navPrice', info.get('regularMarketPrice')),
                        expense_ratio=info.get('annualReportExpenseRatio'),
                        underlying_index=info.get('category')
                    )
                    self.session.add(etf_details)
                
                self.collected_assets.append(asset)
                collected += 1
                
                # Commit in batches
                if collected % 25 == 0:
                    self.session.commit()
                    logger.info(f"Committed {collected} ETFs")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to collect ETF {symbol}: {e}")
                self.failed_assets.append(symbol)
                continue
        
        self.session.commit()
        logger.info(f"✅ Collected {collected} ETFs")
        return collected
    
    # ========================= CRYPTO COLLECTION =========================
    
    def collect_cryptocurrencies(self) -> int:
        """Collect comprehensive cryptocurrency data"""
        logger.info("₿ Collecting cryptocurrencies...")
        
        crypto_symbols = self.get_comprehensive_crypto_list()
        logger.info(f"Found {len(crypto_symbols)} cryptocurrencies to collect")
        
        return self._collect_cryptos(crypto_symbols)

    # ========================= MUTUAL FUND COLLECTION =========================
    
    def collect_mutual_funds(self) -> int:
        """Collect comprehensive mutual fund data"""
        logger.info("💼 Collecting mutual funds...")
        
        mutual_fund_symbols = self.get_comprehensive_mutual_fund_list()
        logger.info(f"Found {len(mutual_fund_symbols)} mutual funds to collect")
        
        return self._collect_mutual_funds(mutual_fund_symbols)
    
    def get_comprehensive_mutual_fund_list(self) -> List[str]:
        """Get comprehensive list of mutual funds"""
        logger.info("💼 Getting comprehensive mutual fund list...")
        
        # Popular mutual funds from major fund families
        mutual_fund_symbols = [
            # Vanguard Funds
            "VTSAX", "VTIAX", "VBTLX", "VTSMX", "VGTSX", "VBMFX", "VTTVX", "VTTHX", "VTTSX",
            "VFWAX", "VTWAX", "VXUS", "VTIAX", "VTABX", "VTEB", "VGSLX", "VGENX",
            
            # Fidelity Funds  
            "FXNAX", "FTIHX", "FXNAX", "FSKAX", "FTBFX", "FDVV", "FREL", "FHLC", "FENY",
            "FSELX", "FSMDX", "FSCSX", "FBIOX", "FBSOX", "FDEEX", "FDGRX", "FCNTX",
            
            # American Funds
            "AGTHX", "CWGIX", "SMCWX", "AIVSX", "ANCFX", "CAIBX", "EUPAX", "NEWFX",
            
            # T. Rowe Price  
            "PRNEX", "PRGFX", "PRWCX", "PRMTX", "PRELX", "PRFDX", "PRHSX", "PRNHX",
            
            # Schwab Funds
            "SWTSX", "SWISX", "SWAGX", "SWPPX", "SWLSX", "SWMCX", "SWSCX", "SWOSX",
            
            # BlackRock/iShares
            "MALOX", "MDLOX", "MLPNX", "MSTSX", "MVPAX", "MWTIX", "MXVIX", "MYIFX",
            
            # Indian Mutual Funds (Major AMCs)
            "0P0000YVK8.BO", "0P00013CXZ.BO", "0P0000A1WY.BO", "0P0000YSPK.BO",  # Sample Indian MF codes
            
            # Target Date Funds
            "VTTVX", "VTTHX", "VTTSX", "VTHRX", "VTWNX", "VTXVX", "FDKLX", "FXNAX",
            
            # Sector/Theme Funds
            "FSELX", "FSMDX", "FSCSX", "FBIOX", "FBSOX", "FDEEX", "VGENX", "VGSLX",
            
            # International/Global Funds
            "FTIHX", "FXNAX", "VTIAX", "VGTSX", "VFWAX", "VTWAX", "NEWFX", "EUROPX"
        ]
        
        logger.info(f"Total mutual fund symbols: {len(mutual_fund_symbols)}")
        return mutual_fund_symbols
    
    def _collect_mutual_funds(self, symbols: List[str]) -> int:
        """Collect mutual fund data"""
        collected = 0
        
        for i, symbol in enumerate(symbols, 1):
            try:
                logger.info(f"Collecting mutual fund {i}/{len(symbols)}: {symbol}")
                
                # Check if already exists
                existing = self.session.query(Asset).filter_by(symbol=symbol).first()
                if existing:
                    logger.info(f"Mutual fund {symbol} already exists, skipping")
                    continue
                
                # Get mutual fund info
                fund = yf.Ticker(symbol)
                info = fund.info
                
                if not info or 'symbol' not in info:
                    logger.warning(f"No data found for {symbol}")
                    self.failed_assets.append(symbol)
                    continue
                
                # Determine details
                exchange = "NASDAQ" if not symbol.endswith(".BO") else "BSE"
                country = "US" if not symbol.endswith(".BO") else "IN"
                currency = "USD" if not symbol.endswith(".BO") else "INR"
                
                # Create asset
                asset = Asset(
                    symbol=symbol,
                    name=info.get('longName', info.get('shortName', symbol)),
                    type='mutual_fund',
                    subtype=self._determine_mutual_fund_category(info, symbol),
                    exchange=exchange,
                    country=country,
                    currency=currency,
                    market_cap=info.get('totalAssets'),
                    total_assets=info.get('totalAssets'),
                    expense_ratio=info.get('annualReportExpenseRatio'),
                    description=info.get('longBusinessSummary'),
                    is_active=True
                )
                
                self.session.add(asset)
                self.session.flush()  # Flush to get the asset.id
                
                # Add mutual fund-specific details if available
                if info.get('totalAssets') or info.get('annualReportExpenseRatio'):
                    fund_details = MutualFund(
                        asset_id=asset.id,
                        nav=info.get('navPrice', info.get('regularMarketPrice')),
                        expense_ratio=info.get('annualReportExpenseRatio'),
                        aum=info.get('totalAssets'),
                        amc_name=info.get('fundFamily', info.get('companyName', 'Unknown')),
                        category=self._determine_mutual_fund_category(info, symbol)
                    )
                    self.session.add(fund_details)
                
                self.collected_assets.append(asset)
                collected += 1
                
                # Commit in batches
                if collected % 25 == 0:
                    self.session.commit()
                    logger.info(f"Committed {collected} mutual funds")
                
                # Rate limiting
                time.sleep(0.15)
                
            except Exception as e:
                logger.error(f"Failed to collect mutual fund {symbol}: {e}")
                self.failed_assets.append(symbol)
                continue
        
        self.session.commit()
        logger.info(f"✅ Collected {collected} mutual funds")
        return collected
    
    def _determine_mutual_fund_category(self, info: dict, symbol: str) -> str:
        """Determine mutual fund category"""
        name = info.get('longName', '').upper()
        
        if any(term in name for term in ['TARGET', 'LIFECYCLE', 'RETIREMENT']):
            return 'target_date'
        elif any(term in name for term in ['INDEX', 'S&P', 'TOTAL STOCK']):
            return 'index'
        elif any(term in name for term in ['BOND', 'FIXED', 'INCOME']):
            return 'bond'
        elif any(term in name for term in ['GROWTH', 'AGGRESSIVE']):
            return 'growth'
        elif 'VALUE' in name:
            return 'value'
        elif any(term in name for term in ['INTERNATIONAL', 'GLOBAL', 'FOREIGN']):
            return 'international'
        elif any(term in name for term in ['SECTOR', 'TECHNOLOGY', 'HEALTH']):
            return 'sector'
        else:
            return 'balanced'
    
    def _collect_cryptos(self, symbols: List[str]) -> int:
        """Collect cryptocurrency data"""
        collected = 0
        
        for i, symbol in enumerate(symbols, 1):
            try:
                logger.info(f"Collecting crypto {i}/{len(symbols)}: {symbol}")
                
                # Check if already exists
                existing = self.session.query(Asset).filter_by(symbol=symbol).first()
                if existing:
                    logger.info(f"Crypto {symbol} already exists, skipping")
                    continue
                
                # Get crypto info
                crypto = yf.Ticker(symbol)
                info = crypto.info
                
                if not info or 'symbol' not in info:
                    logger.warning(f"No data found for {symbol}")
                    self.failed_assets.append(symbol)
                    continue
                
                # Create asset
                asset = Asset(
                    symbol=symbol,
                    name=info.get('longName', info.get('shortName', symbol.replace('-USD', ''))),
                    type='crypto',
                    subtype=self._determine_crypto_category(symbol),
                    exchange="Various",  # Crypto trades on multiple exchanges
                    country="Global",
                    currency="USD",
                    market_cap=info.get('marketCap'),
                    description=info.get('description'),
                    is_active=True
                )
                
                self.session.add(asset)
                self.session.flush()  # Flush to get the asset.id
                
                # Add crypto-specific details if available
                crypto_details = Crypto(
                    asset_id=asset.id,
                    circulating_supply=info.get('circulatingSupply'),
                    max_supply=info.get('maxSupply'),
                    algorithm=self._get_crypto_algorithm(symbol),
                    consensus_mechanism=self._get_consensus_mechanism(symbol),
                    blockchain=self._get_blockchain(symbol)
                )
                self.session.add(crypto_details)
                
                self.collected_assets.append(asset)
                collected += 1
                
                # Commit in batches
                if collected % 10 == 0:
                    self.session.commit()
                    logger.info(f"Committed {collected} cryptocurrencies")
                
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Failed to collect crypto {symbol}: {e}")
                self.failed_assets.append(symbol)
                continue
        
        self.session.commit()
        logger.info(f"✅ Collected {collected} cryptocurrencies")
        return collected
    
    def _determine_crypto_category(self, symbol: str) -> str:
        """Determine cryptocurrency category"""
        major_cryptos = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD"]
        if symbol in major_cryptos:
            return "major"
        elif "SHIB" in symbol or "DOGE" in symbol:
            return "meme"
        elif any(x in symbol for x in ["UNI", "SUSHI", "CRV", "COMP"]):
            return "defi"
        else:
            return "altcoin"
    
    def _get_crypto_algorithm(self, symbol: str) -> str:
        """Get crypto algorithm"""
        algorithms = {
            "BTC-USD": "SHA-256",
            "ETH-USD": "Ethash", 
            "LTC-USD": "Scrypt",
            "XMR-USD": "CryptoNight",
            "BCH-USD": "SHA-256"
        }
        return algorithms.get(symbol, "Unknown")
    
    def _get_consensus_mechanism(self, symbol: str) -> str:
        """Get consensus mechanism"""
        mechanisms = {
            "BTC-USD": "Proof of Work",
            "ETH-USD": "Proof of Stake",
            "ADA-USD": "Proof of Stake",
            "SOL-USD": "Proof of History",
            "DOT-USD": "Nominated Proof of Stake"
        }
        return mechanisms.get(symbol, "Unknown")
    
    def _get_blockchain(self, symbol: str) -> str:
        """Get blockchain name"""
        blockchains = {
            "BTC-USD": "Bitcoin",
            "ETH-USD": "Ethereum",
            "BNB-USD": "Binance Smart Chain",
            "ADA-USD": "Cardano",
            "SOL-USD": "Solana",
            "DOT-USD": "Polkadot"
        }
        return blockchains.get(symbol, symbol.replace('-USD', ''))
    
    # ========================= MAIN COLLECTION METHODS =========================
    
    def collect_all_assets(self) -> Dict[str, int]:
        """Collect all types of assets comprehensively"""
        logger.info("🚀 Starting comprehensive asset collection...")
        
        results = {
            'stocks_us': 0,
            'stocks_indian': 0,
            'etfs': 0,
            'cryptocurrencies': 0,
            'mutual_funds': 0,
            'total': 0
        }
        
        try:
            # Collect US stocks
            results['stocks_us'] = self.collect_us_stocks()
            
            # Collect Indian stocks
            results['stocks_indian'] = self.collect_indian_stocks()
            
            # Collect ETFs
            results['etfs'] = self.collect_etfs()
            
            # Collect cryptocurrencies
            results['cryptocurrencies'] = self.collect_cryptocurrencies()
            
            # Collect mutual funds
            results['mutual_funds'] = self.collect_mutual_funds()
            
            # Calculate total
            results['total'] = sum([
                results['stocks_us'],
                results['stocks_indian'], 
                results['etfs'],
                results['cryptocurrencies']
            ])
            
            return results
            
        except Exception as e:
            logger.error(f"Collection failed: {e}")
            raise
    
    def get_collection_summary(self) -> Dict:
        """Get summary of collected assets"""
        session = SessionLocal()
        try:
            total_assets = session.query(Asset).count()
            
            # Count by type
            stocks = session.query(Asset).filter_by(type='stock').count()
            etfs = session.query(Asset).filter_by(type='etf').count()
            cryptos = session.query(Asset).filter_by(type='crypto').count()
            mutual_funds = session.query(Asset).filter_by(type='mutual_fund').count()
            
            # Count by country
            us_assets = session.query(Asset).filter_by(country='US').count()
            indian_assets = session.query(Asset).filter_by(country='IN').count()
            
            return {
                'total_assets': total_assets,
                'by_type': {
                    'stocks': stocks,
                    'etfs': etfs,
                    'cryptocurrencies': cryptos,
                    'mutual_funds': mutual_funds
                },
                'by_country': {
                    'US': us_assets,
                    'India': indian_assets,
                    'Global': total_assets - us_assets - indian_assets
                }
            }
        finally:
            session.close()

def interactive_collection():
    """Interactive collection interface"""
    print("🌟 UNIVERSAL ASSET COLLECTOR")
    print("=" * 60)
    print("This will collect comprehensive financial asset data:")
    print("📈 Stocks (US + Indian)")
    print("📊 ETFs (Exchange Traded Funds)")
    print("₿ Cryptocurrencies")
    print()
    
    collector = UniversalAssetCollector()
    
    # Show current summary
    current_summary = collector.get_collection_summary()
    print(f"📊 Current database contains {current_summary['total_assets']} assets:")
    for asset_type, count in current_summary['by_type'].items():
        print(f"   {asset_type.capitalize()}: {count}")
    
    print("\n🎯 Collection Options:")
    print("1. Collect ALL assets (comprehensive - stocks, ETFs, crypto, mutual funds)")
    print("2. Collect US stocks only")
    print("3. Collect Indian stocks only") 
    print("4. Collect ETFs only")
    print("5. Collect Cryptocurrencies only")
    print("6. Collect Mutual Funds only")
    print("7. Show current summary")
    
    choice = input("\nSelect option (1-7): ").strip()
    
    try:
        if choice == "1":
            logger.info("Starting comprehensive collection...")
            results = collector.collect_all_assets()
            print(f"\n🎉 COLLECTION COMPLETED!")
            print(f"✅ US Stocks: {results['stocks_us']}")
            print(f"✅ Indian Stocks: {results['stocks_indian']}")
            print(f"✅ ETFs: {results['etfs']}")
            print(f"✅ Cryptocurrencies: {results['cryptocurrencies']}")
            print(f"✅ Mutual Funds: {results['mutual_funds']}")
            print(f"📊 Total Assets Collected: {results['total']}")
            
        elif choice == "2":
            count = collector.collect_us_stocks()
            print(f"✅ Collected {count} US stocks")
            
        elif choice == "3":
            count = collector.collect_indian_stocks()
            print(f"✅ Collected {count} Indian stocks")
            
        elif choice == "4":
            count = collector.collect_etfs()
            print(f"✅ Collected {count} ETFs")
            
        elif choice == "5":
            count = collector.collect_cryptocurrencies()
            print(f"✅ Collected {count} cryptocurrencies")
            
        elif choice == "6":
            count = collector.collect_mutual_funds()
            print(f"✅ Collected {count} mutual funds")
            
        elif choice == "7":
            summary = collector.get_collection_summary()
            print(f"\n📊 DATABASE SUMMARY:")
            print(f"Total Assets: {summary['total_assets']}")
            print(f"By Type:")
            for asset_type, count in summary['by_type'].items():
                print(f"  {asset_type.capitalize()}: {count}")
            print(f"By Region:")
            for region, count in summary['by_country'].items():
                print(f"  {region}: {count}")
        else:
            print("Invalid option selected")
            return
        
        # Show failed assets if any
        if collector.failed_assets:
            print(f"\n⚠️ Failed to collect {len(collector.failed_assets)} assets:")
            for symbol in collector.failed_assets[:10]:  # Show first 10
                print(f"   {symbol}")
            if len(collector.failed_assets) > 10:
                print(f"   ... and {len(collector.failed_assets) - 10} more")
        
        # Final summary
        final_summary = collector.get_collection_summary()
        print(f"\n📈 Updated database now contains {final_summary['total_assets']} assets")
        
    except Exception as e:
        logger.error(f"Collection failed: {e}")
        print(f"❌ Collection failed: {e}")
    
    finally:
        collector.session.close()

if __name__ == "__main__":
    interactive_collection()