#!/usr/bin/env python3
"""
Unified Financial Data Collector
🚀 Complete solution for collecting assets AND their price data
Replaces both universal_collector and company_collector
"""
import sys
import os
import time
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from io import StringIO
import yfinance as yf
import requests
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Asset, ETF, MutualFund, Crypto, DailyPrice

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedFinancialCollector:
    """🚀 ONE COLLECTOR TO RULE THEM ALL - Assets + Prices"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.collected_assets = []
        self.failed_assets = []
        
        # Setup requests session for web scraping
        self.requests_session = requests.Session()
        self.requests_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    # ========================= COMPREHENSIVE DATA SOURCES =========================
    
    def get_comprehensive_us_stocks(self) -> List[str]:
        """Get ALL US stocks - S&P 500 + Popular stocks"""
        logger.info("🇺🇸 Getting comprehensive US stock list...")
        
        all_us_stocks = []
        
        # Get S&P 500 from Wikipedia (real data)
        try:
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            response = self.requests_session.get(sp500_url)
            if response.status_code == 200:
                tables = pd.read_html(response.content)
                if len(tables) > 0:
                    sp500_symbols = tables[0]['Symbol'].tolist()
                    all_us_stocks.extend(sp500_symbols)
                    logger.info(f"✅ Found {len(sp500_symbols)} S&P 500 stocks")
        except Exception as e:
            logger.warning(f"S&P 500 scraping failed: {e}")
        
        # Add popular stocks to ensure comprehensive coverage
        popular_stocks = [
            # FAANG+
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE',
            # Major Financial
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'V', 'MA',
            # Healthcare & Pharma
            'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'LLY',
            # Popular Trading Stocks
            'AMD', 'QCOM', 'INTC', 'CRM', 'ORCL', 'IBM', 'PYPL', 'SQ', 'ROKU', 'ZM',
            'UBER', 'LYFT', 'SNAP', 'TWTR', 'PINS', 'HOOD', 'AMC', 'GME', 'BB', 'NOK'
        ]
        all_us_stocks.extend(popular_stocks)
        
        # Remove duplicates
        unique_symbols = list(set(all_us_stocks))
        logger.info(f"🎯 Total unique US symbols: {len(unique_symbols)}")
        return unique_symbols
    
    def get_comprehensive_indian_stocks(self) -> List[str]:
        """Get ALL Indian stocks from NSE official sources"""
        logger.info("🇮🇳 Getting comprehensive Indian stock list...")
        
        all_symbols = []
        
        # NSE Main Board
        try:
            nse_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
            response = self.requests_session.get(nse_url, timeout=30)
            if response.status_code == 200:
                csv_data = StringIO(response.text)
                df = pd.read_csv(csv_data)
                if 'SYMBOL' in df.columns:
                    symbols = [f"{symbol.strip()}.NS" for symbol in df['SYMBOL'].tolist() if symbol.strip()]
                    all_symbols.extend(symbols)
                    logger.info(f"✅ NSE Main Board: {len(symbols)} stocks")
        except Exception as e:
            logger.warning(f"NSE main board failed: {e}")
        
        # NSE SME
        try:
            sme_url = "https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv"
            response = self.requests_session.get(sme_url, timeout=30)
            if response.status_code == 200:
                csv_data = StringIO(response.text)
                df = pd.read_csv(csv_data)
                if 'SYMBOL' in df.columns:
                    sme_symbols = [f"{symbol.strip()}.NS" for symbol in df['SYMBOL'].tolist() if symbol.strip()]
                    all_symbols.extend(sme_symbols)
                    logger.info(f"✅ NSE SME: {len(sme_symbols)} stocks")
        except Exception as e:
            logger.warning(f"NSE SME failed: {e}")
        
        # BSE backup (major stocks)
        bse_backup = ['RELIANCE.BO', 'TCS.BO', 'HDFCBANK.BO', 'INFY.BO', 'HINDUNILVR.BO']
        all_symbols.extend(bse_backup)
        
        unique_symbols = list(set(all_symbols))
        logger.info(f"🎯 Total Indian symbols: {len(unique_symbols)}")
        return unique_symbols
    
    def get_comprehensive_etfs(self) -> List[str]:
        """Get comprehensive ETF list"""
        logger.info("📊 Getting comprehensive ETF list...")
        
        etfs = [
            # === US BROAD MARKET ETFs ===
            "SPY", "QQQ", "IWM", "VTI", "VOO", "IVV", "VEA", "VWO", "IEFA", "EEM",
            "DIA", "MDY", "IJH", "IJR", "VTV", "VUG", "IVW", "IVE", "VB", "VBK", "VBR",
            "ITOT", "IXUS", "IEMG", "VT", "ACWX", "ACWI", "VEU", "VXUS", "FTSE", "SCHE",
            
            # === SECTOR ETFs ===
            # Technology
            "XLK", "VGT", "QTEC", "IGV", "SOXX", "SMH", "HACK", "ROBO", "FINX", "CIBR",
            "SKYY", "CLOU", "BUG", "ESPO", "GAMR", "HERO", "UFO", "WCLD", "ARKK", "ARKQ",
            "ARKW", "ARKG", "ARKF", "PRNT", "GNOM", "BOTZ", "IRBO", "SNSR", "KOMP",
            
            # Financial
            "XLF", "VFH", "KRE", "KIE", "IAT", "PFI", "KBWB", "KBWR", "KBWY", "KBWP",
            "FREL", "REZ", "RWR", "SCHH", "XLRE", "VNQ", "IYR", "REM", "MORT", "PLD",
            
            # Healthcare  
            "XLV", "VHT", "IHI", "IBB", "XBI", "ARKG", "CURE", "IHE", "RYH", "IXJ",
            "PJP", "FBT", "FTXH", "EDOC", "PILL", "HELX", "SBIO", "XPH", "IDNA",
            
            # Energy
            "XLE", "VDE", "IXC", "OIH", "XOP", "PXE", "ERX", "DRIP", "ICLN", "QCLN",
            "ACES", "FAN", "TAN", "PBW", "CWEB", "LIT", "GRID", "VOLT", "RENW", "SMOG",
            
            # Consumer
            "XLY", "VCR", "XLP", "VDC", "IYC", "IYK", "FDIS", "FSTA", "RXI", "PEJ",
            "RTH", "XRT", "IYT", "JETS", "AWAY", "CRUZ", "BUZ", "SLX", "PICK", "MOO",
            
            # Industrials & Materials
            "XLI", "VIS", "XLB", "VAW", "IYJ", "IYM", "FREL", "ITB", "XHB", "PKB",
            "URA", "REMX", "SIL", "COPX", "GLTR", "WOOD", "CUT", "DIRT", "PAVE", "FILL",
            
            # Utilities & Infrastructure  
            "XLU", "VPU", "IDU", "FUTY", "GRID", "ICLN", "PBW", "QCLN", "SMOG", "ACES",
            
            # Communication & Media
            "XLC", "VOX", "FCOM", "IYZ", "FDN", "SOCL", "NFTZ", "META", "THNQ", "MEME",
            
            # === INTERNATIONAL ETFs ===
            # Developed Markets
            "VEA", "EFA", "IEFA", "ACWX", "VGK", "FEZ", "IEV", "IEUR", "EZU", "VPL",
            "EWJ", "EWG", "EWU", "EWL", "EWQ", "EWP", "EWI", "EWN", "EWD", "EWO",
            "EWT", "EWY", "EWS", "EWH", "EWM", "EPI", "EPHE", "THD", "TUR", "RSX",
            
            # Emerging Markets  
            "EEM", "VWO", "IEMG", "SCHE", "EWZ", "FXI", "EWW", "EZA", "EWA", "EPP",
            "INDA", "INDY", "MINDX", "FLBR", "ASHR", "MCHI", "GXC", "CHIM", "YINN",
            "EMQQ", "FDEM", "DEM", "EDC", "EEB", "GMF", "GUR", "ADRE", "AFK", "EIDO",
            
            # === BOND ETFs ===
            # Government Bonds
            "AGG", "BND", "TLT", "IEF", "TLH", "SHY", "SCHO", "SCHR", "IEI", "GOVT",
            "SPTL", "VGIT", "VGSH", "VGLT", "SPTI", "BSV", "BIV", "BLV", "VTEB", "MUB",
            
            # Corporate Bonds
            "LQD", "VCIT", "VCSH", "VCLT", "SPIB", "SPLB", "SPSB", "IGIB", "IGSB", "IGLB",
            
            # High Yield & International
            "HYG", "JNK", "SJNK", "USHY", "SHYG", "EMB", "VWOB", "EMHY", "PCY", "BWX",
            
            # Inflation Protected & Floating
            "TIP", "VTIP", "SCHP", "TIPX", "STIP", "FLOT", "FLRN", "TFLO", "FLTR", "USFR",
            
            # === COMMODITY ETFs ===
            # Precious Metals
            "GLD", "SLV", "IAU", "SGOL", "SIVR", "PPLT", "PALL", "GDX", "GDXJ", "SIL",
            "RING", "GLTR", "GLDM", "OUNZ", "BAR", "PHYS", "PSLV", "CEF", "GTU", "SPPP",
            
            # Energy Commodities  
            "USO", "UNG", "BNO", "UGA", "UHN", "BOIL", "KOLD", "UGAZ", "DGAZ", "UCO",
            
            # Agricultural & Broad Commodities
            "DBA", "DBC", "PDBC", "DJP", "GSG", "USCI", "BCD", "COW", "NIB", "CORN",
            "SOYB", "WEAT", "CANE", "JO", "BAL", "SGG", "JJU", "JJT", "JJS", "JJN",
            
            # === STYLE & FACTOR ETFs ===  
            # Value
            "VTV", "IVE", "VBR", "VEU", "MTUM", "QUAL", "USMV", "VMOT", "EFAV", "ACWV",
            
            # Growth
            "VUG", "IVW", "VBK", "MGK", "SPYG", "IWF", "DGRO", "VIG", "NOBL", "RDVY",
            
            # Dividend & Income
            "VYM", "SCHD", "DVY", "HDV", "SDOG", "DGRO", "VIG", "NOBL", "RDVY", "SPHD",
            "PEY", "FDL", "FDVV", "DHS", "DTH", "DTN", "DLN", "PID", "PRF", "RFG",
            
            # Momentum & Quality
            "MTUM", "PDP", "VMOT", "QUAL", "SPHQ", "DSTL", "JQUA", "LRGF", "JHCS", "SIZE",
            
            # Low Volatility
            "USMV", "SPLV", "EFAV", "ACWV", "EEMV", "VMOT", "XMLV", "XSLV", "SPMV", "LVOL",
            
            # === THEMATIC & SPECIALTY ETFs ===
            # Clean Energy & ESG
            "ICLN", "QCLN", "TAN", "FAN", "PBW", "ACES", "SMOG", "RENW", "GRID", "LIT",
            "ESGU", "ESGV", "ESGE", "SHE", "KRMA", "VOTE", "SUSL", "DSI", "KLD", "VSGX",
            
            # Demographics & Lifestyle
            "PSCH", "PEZ", "PEY", "PSI", "PSJ", "PSL", "PSP", "PSR", "PUI", "PXI",
            "BOOMER", "BABY", "KIDS", "PET", "SLIM", "WINE", "BEER", "MJ", "TOKE", "YOLO",
            
            # Currency & Volatility
            "UUP", "FXE", "FXY", "FXB", "FXA", "FXC", "CYB", "VXX", "UVXY", "SVXY",
            "TVIX", "XIV", "ZIV", "VXZ", "VIXY", "VXXB", "UVIX", "SVIX", "VMIN", "TAIL",
            
            # === LEVERAGED ETFs ===
            # Leveraged Long (2x-3x)
            "TQQQ", "UPRO", "UDOW", "TNA", "CURE", "TECL", "SOXL", "ERX", "NUGT", "JNUG",
            "FAS", "LABU", "YINN", "YANG", "UCO", "BOIL", "UGAZ", "AGQ", "USLV", "DUST",
            
            # Leveraged Short (Inverse)
            "SQQQ", "SPXU", "SDOW", "TZA", "SOXS", "DRIP", "JDST", "FAZ", "LABD", "KOLD",
            "DGAZ", "ZSL", "DZZ", "SRS", "SCC", "SMN", "SJB", "PST", "TBF", "TBT",
            
            # === INDIAN ETFs ===
            "NIFTYBEES.NS", "JUNIORBEES.NS", "BANKBEES.NS", "GOLDBEES.NS", "LIQUIDBEES.NS",
            "NIFTYEES.NS", "INFRABEES.NS", "PSUBNKBEES.NS", "CONSUMERBEES.NS", "PHARMBEES.NS",
            "ITBEES.NS", "FMCGBEES.NS", "AUTOBEES.NS", "PVTBNKBEES.NS", "REALTYBEES.NS",
            
            # === CRYPTO ETFs (when available) ===
            "BITO", "BTF", "GBTC", "ETHE", "GDLC", "BITW", "BLOK", "LEGR", "KOIN", "SATO"
        ]
        
        # Remove duplicates while preserving order
        etfs = list(dict.fromkeys(etfs))
        logger.info(f"🎯 Total unique ETF symbols: {len(etfs)}")
        return etfs
    
    def get_comprehensive_crypto(self) -> List[str]:
        """Get comprehensive crypto list"""
        logger.info("₿ Getting comprehensive crypto list...")
        
        cryptos = [
            # === TOP CRYPTOCURRENCIES BY MARKET CAP ===
            # Top 20
            "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD", "DOGE-USD", "DOT-USD", 
            "AVAX-USD", "SHIB-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "UNI-USD", "LINK-USD",
            "ATOM-USD", "XMR-USD", "ETC-USD", "BCH-USD", "ICP-USD",
            
            # Top 21-50  
            "LEO-USD", "TON11419-USD", "XLM-USD", "NEAR-USD", "HBAR-USD", "VET-USD", "FIL-USD",
            "MANA-USD", "APT-USD", "CRO-USD", "QNT-USD", "LUNC-USD", "AAVE-USD", "ALGO-USD",
            "EOS-USD", "FLOW-USD", "XTZ-USD", "THETA-USD", "AXS-USD", "SAND-USD", "EGLD-USD",
            "KCS-USD", "BSV-USD", "RUNE-USD", "FTM-USD", "CHZ-USD", "MINA-USD", "KLAY-USD",
            "HNT-USD", "GMT-USD",
            
            # Top 51-100
            "ENJ-USD", "BAT-USD", "ZEC-USD", "DASH-USD", "WAVES-USD", "ICX-USD", "ONT-USD",
            "ZIL-USD", "HOT-USD", "NANO-USD", "DGB-USD", "SC-USD", "LSK-USD", "ARDR-USD",
            "KMD-USD", "STEEM-USD", "REP-USD", "GNT-USD", "STORJ-USD", "MAID-USD", "DCR-USD",
            "STRAT-USD", "ARK-USD", "KNC-USD", "POWR-USD", "LRC-USD", "GAS-USD", "PIVX-USD",
            "NXT-USD", "VTC-USD", "SYS-USD", "EMC2-USD", "BLOCK-USD", "OK-USD", "XEM-USD",
            
            # === DEFI ECOSYSTEM ===
            # DEX Tokens  
            "UNI-USD", "SUSHI-USD", "1INCH-USD", "CRV-USD", "BAL-USD", "LRC-USD", "ZRX-USD",
            "KNC-USD", "DYDX-USD", "GMX-USD", "JOE-USD", "CAKE-USD", "QUICK-USD", "HON-USD",
            
            # Lending & Borrowing
            "AAVE-USD", "COMP-USD", "MKR-USD", "SNX-USD", "YFI-USD", "ALPHA-USD", "CREAM-USD",
            "BADGER-USD", "REN-USD", "KP3R-USD", "ALCX-USD", "SPELL-USD", "ICE-USD", "BANK-USD",
            
            # Yield Farming & Staking
            "CVX-USD", "CRV-USD", "FXS-USD", "OHM-USD", "TIME-USD", "BTRFLY-USD", "TOKE-USD",
            "FOLD-USD", "TEMPLE-USD", "FEI-USD", "TRIBE-USD", "RAI-USD", "FLX-USD", "OGN-USD",
            
            # Insurance & Risk Management  
            "NXM-USD", "COVER-USD", "INS-USD", "SURE-USD", "UNION-USD", "BMI-USD", "NEXO-USD",
            
            # === LAYER 1 BLOCKCHAINS ===
            # Smart Contract Platforms
            "ETH-USD", "SOL-USD", "ADA-USD", "DOT-USD", "AVAX-USD", "NEAR-USD", "ATOM-USD",
            "ALGO-USD", "XTZ-USD", "EGLD-USD", "FTM-USD", "ONE-USD", "HBAR-USD", "ICP-USD",
            "ROSE-USD", "CELO-USD", "ZIL-USD", "ICX-USD", "VET-USD", "THETA-USD", "TFUEL-USD",
            
            # Newer L1s
            "APTOS-USD", "SUI-USD", "SEI-USD", "INJ-USD", "TIA-USD", "STRK-USD", "IMX-USD",
            "MATIC-USD", "ARB-USD", "OP-USD", "METIS-USD", "BOBA-USD", "LRC-USD", "DUSK-USD",
            
            # === LAYER 2 & SCALING ===
            "MATIC-USD", "LRC-USD", "ARB-USD", "OP-USD", "METIS-USD", "BOBA-USD", "IMX-USD",
            "STRK-USD", "ZK-USD", "MANTA-USD", "BLAST-USD", "BASE-USD", "LINEA-USD", "SCROLL-USD",
            
            # === STABLECOINS ===
            "USDT-USD", "USDC-USD", "BUSD-USD", "DAI-USD", "TUSD-USD", "FRAX-USD", "LUSD-USD",
            "USTC-USD", "USDP-USD", "HUSD-USD", "GUSD-USD", "SUSD-USD", "DUSD-USD", "UST-USD",
            "USDN-USD", "RSV-USD", "AMPL-USD", "FEI-USD", "RAI-USD", "TRIBE-USD", "OHM-USD",
            
            # === MEME TOKENS ===
            "DOGE-USD", "SHIB-USD", "FLOKI-USD", "ELON-USD", "SAFEMOON-USD", "AKITA-USD",
            "BABYDOGE-USD", "DOGELON-USD", "KISHU-USD", "HOGE-USD", "SAITAMA-USD", "CATGIRL-USD",
            "PEPE-USD", "WOJAK-USD", "CHAD-USD", "COPE-USD", "HOPIUM-USD", "FUD-USD",
            
            # === GAMING & METAVERSE ===
            "AXS-USD", "SAND-USD", "MANA-USD", "ENJ-USD", "GALA-USD", "IMX-USD", "GMT-USD",
            "SLP-USD", "CHR-USD", "ALICE-USD", "TLM-USD", "ILV-USD", "GHST-USD", "REVV-USD",
            "SKILL-USD", "PYR-USD", "NFTX-USD", "SUPER-USD", "UFT-USD", "ZOON-USD", "DPET-USD",
            "REALM-USD", "STARL-USD", "VOXEL-USD", "HIGH-USD", "WILD-USD", "RADIO-USD", "SENATE-USD",
            
            # === NFT & COLLECTIBLES ===
            "LOOKS-USD", "X2Y2-USD", "BLUR-USD", "SOS-USD", "NFTX-USD", "SUDO-USD", "GEM-USD",
            "RARI-USD", "SUPER-USD", "WHALE-USD", "MASK-USD", "DEGO-USD", "GHST-USD", "MEME-USD",
            
            # === WEB3 & INFRASTRUCTURE ===
            "FIL-USD", "AR-USD", "SC-USD", "STORJ-USD", "OCEAN-USD", "GRT-USD", "ANKR-USD",
            "RLC-USD", "POKT-USD", "HNT-USD", "RNDR-USD", "LPT-USD", "BAT-USD", "BASIC-USD",
            "NKN-USD", "DENT-USD", "CVC-USD", "DNT-USD", "REQ-USD", "UTK-USD", "DATA-USD",
            
            # === PRIVACY COINS ===
            "XMR-USD", "ZEC-USD", "DASH-USD", "FIRO-USD", "BEAM-USD", "GRIN-USD", "PIRATE-USD",
            "ARRR-USD", "DERO-USD", "HAVEN-USD", "OXEN-USD", "PART-USD", "NAV-USD", "GHOST-USD",
            
            # === ENTERPRISE & INSTITUTIONAL ===
            "XRP-USD", "XLM-USD", "HBAR-USD", "VET-USD", "IOTA-USD", "QNT-USD", "LTO-USD",
            "TRAC-USD", "WTC-USD", "AMB-USD", "MOBI-USD", "CPX-USD", "DLT-USD", "PROPS-USD",
            
            # === ORACLE & DATA ===
            "LINK-USD", "BAND-USD", "TRB-USD", "API3-USD", "UMA-USD", "DIA-USD", "FLUX-USD",
            "ERN-USD", "PYR-USD", "RAZOR-USD", "WINk-USD", "NEST-USD", "DOS-USD", "ORAI-USD",
            
            # === CROSS-CHAIN & BRIDGES ===
            "DOT-USD", "KSM-USD", "ATOM-USD", "OSMO-USD", "JUNO-USD", "SCRT-USD", "KAVA-USD",
            "HARD-USD", "SWP-USD", "USDX-USD", "XPRT-USD", "NGM-USD", "BLD-USD", "ROWAN-USD",
            
            # === EXCHANGE TOKENS ===
            "BNB-USD", "CRO-USD", "FTT-USD", "KCS-USD", "LEO-USD", "HT-USD", "OKB-USD",
            "GT-USD", "WRX-USD", "DENT-USD", "MCO-USD", "BGB-USD", "ZB-USD", "CAKE-USD",
            
            # === AI & MACHINE LEARNING ===
            "OCEAN-USD", "FET-USD", "AGI-USD", "NTX-USD", "CTX-USD", "DBC-USD", "MATRIX-USD",
            "AI-USD", "NRG-USD", "EFFECT-USD", "SYNTH-USD", "BRAIN-USD", "CORTEX-USD", "VXV-USD"
        ]
        
        # Remove duplicates while preserving order
        cryptos = list(dict.fromkeys(cryptos))
        logger.info(f"🎯 Total unique crypto symbols: {len(cryptos)}")
        return cryptos
    
    def get_comprehensive_mutual_funds(self) -> List[str]:
        """Get comprehensive mutual fund list"""
        logger.info("💼 Getting comprehensive mutual fund list...")
        
        funds = [
            # === VANGUARD FUNDS ===
            # Index Funds
            "VTSAX", "VTIAX", "VBTLX", "VTSMX", "VGTSX", "VTTVX", "VTTHX", "VTTSX",
            "VFINX", "VEXMX", "VTMGX", "VSCGX", "VMGMX", "VSGAX", "VTRIX", "VEURX",
            "VPACX", "VEIEX", "VTRIX", "VEMBX", "VTABX", "VTEAX", "VTEB", "VTLGX",
            
            # Active Funds
            "VWELX", "VWINX", "VWNDX", "VWAHX", "VGHCX", "VGHAX", "VMGRX", "VQNPX",
            "VEIPX", "VEXPX", "VHDYX", "VWESX", "VWUSX", "VSEQX", "VTCLX", "VSCPX",
            
            # Target Date Funds
            "VTHRX", "VTWNX", "VTXVX", "VTTSX", "VTTVX", "VTTHX", "VFORX", "VFFVX",
            "VTINX", "VTXVX", "VFIFX", "VTIVX", "VFOUX", "VTXOX", "VTTSX", "VFIFX",
            
            # === FIDELITY FUNDS ===
            # Index Funds
            "FXNAX", "FTIHX", "FSKAX", "FTBFX", "FXNAX", "FZROX", "FZILX", "FXNAX",
            "FZIPX", "FZROX", "FREL", "FREL", "FDVV", "FNDX", "FXNAX", "FREL",
            
            # Sector Funds
            "FSELX", "FSMDX", "FSCSX", "FBIOX", "FBSOX", "FDFAX", "FDVLX", "FSENX",
            "FSNGX", "FSLBX", "FSPHX", "FSRFX", "FSRPX", "FSTCX", "FSUTX", "FNARX",
            
            # Growth & Value
            "FCNKX", "FDGRX", "FDVLX", "FCNTX", "FGRIX", "FGRTX", "FSLSX", "FTQGX",
            "FMILX", "FOCPX", "FSCGX", "FSMEX", "FSMDX", "FXNAX", "FDCAX", "FMCSX",
            
            # Target Date Funds
            "FDKLX", "FXNAX", "FREL", "FDVV", "FXNAX", "FDKLX", "FREL", "FDVV",
            "FFKFX", "FFFHX", "FFFDX", "FFFGX", "FFFEX", "FREL", "FDVV", "FXNAX",
            
            # === AMERICAN FUNDS ===
            # Growth Funds  
            "AGTHX", "CWGIX", "SMCWX", "AIVSX", "ANCFX", "CAIBX", "NEWFX", "RWMGX",
            "EUPAX", "NWFFX", "SMALLX", "AMCAX", "AFMFX", "AMRMX", "IGAAX", "IFACX",
            
            # Income & Balanced
            "AMECX", "AMEIX", "CWGIX", "BALCX", "CIBCX", "CAIBX", "PONDX", "CPOAX",
            "RIMSX", "RIDBX", "AMEIX", "AHITX", "AMUSX", "CPOAX", "RIMSX", "RIDBX",
            
            # International
            "AEPGX", "AEPIX", "CWGIX", "NFACX", "NFFAX", "EUPAX", "AEPGX", "AEPIX",
            "CWGIX", "NFACX", "NFFAX", "EUPAX", "AEPGX", "AEPIX", "CWGIX", "NFACX",
            
            # === T. ROWE PRICE ===
            # Growth Funds
            "PRNEX", "PRGFX", "PRWCX", "PRMTX", "PRELX", "PRFDX", "PRGSX", "PRGTX",
            "PRLGX", "PRSVX", "PRGWX", "PRMSX", "PRGIX", "PRNHX", "PRBLX", "PRCOX",
            
            # Value & Income
            "PRVLX", "PRDVX", "PREQX", "PRIDX", "PRHSX", "PRINX", "PRCIX", "PREIX",
            "PRFIX", "PRGBX", "PRHIX", "PRIMX", "PRJPX", "PRKCX", "PRLAX", "PRMEX",
            
            # International & Emerging
            "PRIEX", "PRIJX", "PRJPX", "PRJEX", "PREMX", "PREUX", "PRJPX", "PRIJX",
            "PRIEX", "PRJEX", "PREMX", "PREUX", "PRJPX", "PRIJX", "PRIEX", "PRJEX",
            
            # === SCHWAB FUNDS ===
            # Index Funds
            "SWTSX", "SWISX", "SWAGX", "SWPPX", "SWLSX", "SWMCX", "SCHA", "SCHB",
            "SCHF", "SCHC", "SCHE", "SCHG", "SCHH", "SCHM", "SCHO", "SCHP",
            
            # Active Funds  
            "SWANX", "SWBGX", "SWDGX", "SWEGX", "SWFGX", "SWHGX", "SWIGX", "SWJGX",
            "SWKGX", "SWLGX", "SWMGX", "SWNGX", "SWOGX", "SWPGX", "SWQGX", "SWRGX",
            
            # === BLACKROCK/ISHARES FUNDS ===
            "MSTBX", "MALBX", "MACBX", "MAEQX", "MAGSX", "MAHQX", "MAIEX", "MAJGX",
            "MAKGX", "MALGX", "MAMGX", "MANGX", "MAOGX", "MAPGX", "MAQGX", "MARGX",
            
            # === JANUS HENDERSON ===
            "JBALX", "JCPAX", "JDCAX", "JEGAX", "JFGAX", "JGVAX", "JHQAX", "JIGRX",
            "JJSAX", "JKGAX", "JLGAX", "JMGAX", "JNGAX", "JOGAX", "JPGAX", "JQGAX",
            
            # === INVESCO ===
            "OAKBX", "OAKEX", "OALGX", "OAMGX", "OASGX", "OBBGX", "OBCGX", "OBDGX",
            "OBEGX", "OBFGX", "OBGGX", "OBHGX", "OBIGX", "OBJGX", "OBKGX", "OBLGX",
            
            # === JPMORGAN ===
            "JPMCX", "JPCAX", "JPDBX", "JPECX", "JPFCX", "JPGCX", "JPHCX", "JPICX",
            "JPJCX", "JPKCX", "JPLCX", "JPMCX", "JPNCX", "JPOCX", "JPPCX", "JPQCX",
            
            # === FRANKLIN TEMPLETON ===
            "TRBCX", "FKRCX", "FRBGX", "FRSGX", "FRBGX", "FRSGX", "FRBGX", "FRSGX",
            "FKRCX", "TRBCX", "FRBGX", "FRSGX", "FKRCX", "TRBCX", "FRBGX", "FRSGX",
            
            # === PIMCO ===
            "PTTAX", "PTTDX", "PTTRX", "PDIAX", "PDVAX", "PFORX", "PSLDX", "PONAX",
            "PXTIX", "PAAIX", "PIMIX", "PTSHX", "PZCIX", "PZFOX", "PMZIX", "PXTIX",
            
            # === DODGE & COX ===
            "DODGX", "DODBX", "DODIX", "DODFX", "DODWX", "DODYX", "DODZX", "DODAX",
            
            # === CAPITAL GROUP ===
            "CGBGX", "CGCGX", "CGDGX", "CGEGX", "CGFGX", "CGGGX", "CGHGX", "CGIGX",
            "CGJGX", "CGKGX", "CGLGX", "CGMGX", "CGNGX", "CGOGX", "CGPGX", "CGQGX",
            
            # === BARON FUNDS ===
            "BPTRX", "BPTIX", "BSCFX", "BSFIX", "BGRFX", "BGRIX", "BMCFX", "BMCIX",
            "BSAIX", "BSARX", "BSCFX", "BSCIX", "BSFIX", "BSFOX", "BGRFX", "BGRIX",
            
            # === PRIMECAP ===
            "POGRX", "POSKX", "POFGX", "POAGX", "POLRX", "POMGX", "PONGX", "POOGX",
            "POPGX", "POQGX", "PORGX", "POSGX", "POTGX", "POUGX", "POVGX", "POWGX"
        ]
        
        # Remove duplicates while preserving order
        funds = list(dict.fromkeys(funds))
        logger.info(f"🎯 Total unique mutual fund symbols: {len(funds)}")
        return funds
    
    # ========================= UNIFIED ASSET COLLECTION =========================
    
    def collect_all_assets(self) -> Dict[str, int]:
        """🚀 MASTER METHOD - Collect ALL financial assets"""
        logger.info("🚀 Starting COMPREHENSIVE financial asset collection...")
        
        results = {
            'us_stocks': 0,
            'indian_stocks': 0,
            'etfs': 0,
            'crypto': 0,
            'mutual_funds': 0,
            'total': 0
        }
        
        try:
            # Collect all asset types
            results['us_stocks'] = self._collect_assets(
                self.get_comprehensive_us_stocks(), 'stock', 'US', 'USD'
            )
            
            results['indian_stocks'] = self._collect_assets(
                self.get_comprehensive_indian_stocks(), 'stock', 'IN', 'INR'
            )
            
            results['etfs'] = self._collect_assets(
                self.get_comprehensive_etfs(), 'etf', 'US', 'USD'
            )
            
            results['crypto'] = self._collect_assets(
                self.get_comprehensive_crypto(), 'crypto', 'Global', 'USD'
            )
            
            results['mutual_funds'] = self._collect_assets(
                self.get_comprehensive_mutual_funds(), 'mutual_fund', 'US', 'USD'
            )
            
            results['total'] = sum(results.values()) - results['total']  # Exclude total from sum
            
            return results
            
        except Exception as e:
            logger.error(f"Collection failed: {e}")
            raise
    
    def _collect_assets(self, symbols: List[str], asset_type: str, country: str, currency: str) -> int:
        """Unified method to collect any type of asset"""
        collected = 0
        skipped = 0
        
        logger.info(f"📊 Collecting {len(symbols)} {asset_type}s...")
        
        for i, symbol in enumerate(symbols, 1):
            try:
                # Check if already exists (PREVENT DUPLICATES!)
                existing = self.session.query(Asset).filter_by(symbol=symbol).first()
                if existing:
                    skipped += 1
                    logger.debug(f"{symbol} already exists, skipping")
                    continue
                
                logger.info(f"Collecting {i}/{len(symbols)}: {symbol}")
                
                # Get asset info from yfinance
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if not info or 'symbol' not in info:
                    logger.warning(f"No data for {symbol}")
                    self.failed_assets.append(symbol)
                    continue
                
                # Create asset based on type
                asset = self._create_asset(symbol, info, asset_type, country, currency)
                
                if asset:
                    try:
                        self.session.add(asset)
                        # Commit each asset individually to handle duplicates gracefully
                        self.session.commit()
                        self.collected_assets.append(asset)
                        collected += 1
                        
                        # Progress update
                        if collected % 20 == 0:
                            logger.info(f"💾 Committed {collected} {asset_type}s (skipped {skipped} duplicates)")
                    
                    except IntegrityError as ie:
                        # Handle duplicate key violation gracefully
                        self.session.rollback()
                        skipped += 1
                        logger.debug(f"Duplicate {symbol} caught and skipped: {ie}")
                        continue
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                # Rollback session on any error
                self.session.rollback()
                logger.error(f"Failed to collect {symbol}: {e}")
                self.failed_assets.append(symbol)
                continue
        
        logger.info(f"✅ Collected {collected} new {asset_type}s (skipped {skipped} existing)")
        return collected
    
    def _create_asset(self, symbol: str, info: dict, asset_type: str, country: str, currency: str) -> Optional[Asset]:
        """Create asset object with proper type-specific handling"""
        
        # Determine exchange
        if country == "US":
            exchange = "NYSE" if asset_type == 'stock' else "NASDAQ"
        elif country == "IN":
            exchange = "NSE" if symbol.endswith(".NS") else "BSE"
        else:
            exchange = "Various"
        
        # Create base asset
        asset = Asset(
            symbol=symbol,
            name=info.get('longName', info.get('shortName', symbol)),
            type=asset_type,
            subtype=self._determine_subtype(info, asset_type),
            exchange=exchange,
            country=country,
            currency=currency,
            sector=info.get('sector'),
            industry=info.get('industry'),
            market_cap=info.get('marketCap'),
            description=info.get('longBusinessSummary'),
            website=info.get('website'),
            dividend_yield=info.get('dividendYield'),
            expense_ratio=info.get('annualReportExpenseRatio'),
            total_assets=info.get('totalAssets'),
            is_active=True
        )
        
        return asset
    
    def _determine_subtype(self, info: dict, asset_type: str) -> str:
        """Determine asset subtype based on type and info"""
        if asset_type == 'stock':
            market_cap = info.get('marketCap', 0)
            if market_cap >= 10_000_000_000:
                return 'large_cap'
            elif market_cap >= 2_000_000_000:
                return 'mid_cap'
            else:
                return 'small_cap'
        
        elif asset_type == 'etf':
            name = info.get('longName', '').upper()
            if any(x in name for x in ['BOND', 'TREASURY']):
                return 'bond'
            elif any(x in name for x in ['INTERNATIONAL', 'GLOBAL']):
                return 'international'
            else:
                return 'equity'
        
        elif asset_type == 'crypto':
            return 'major' if 'BTC' in info.get('symbol', '') or 'ETH' in info.get('symbol', '') else 'altcoin'
        
        elif asset_type == 'mutual_fund':
            name = info.get('longName', '').upper()
            if 'INDEX' in name:
                return 'index'
            elif 'BOND' in name:
                return 'bond'
            elif 'GROWTH' in name:
                return 'growth'
            else:
                return 'balanced'
        
        return 'unknown'
    
    # ========================= COMPREHENSIVE PRICE COLLECTION =========================
    
    def collect_all_prices(self, years_back: int = 25, batch_size: int = 10) -> Dict[str, int]:
        """🚀 COLLECT 25+ YEARS OF PRICE DATA FOR ALL ASSETS"""
        logger.info(f"🚀 Starting MASSIVE price collection - {years_back} years for ALL assets")
        
        # Get all assets
        assets = self.session.query(Asset).filter_by(is_active=True).all()
        total_assets = len(assets)
        
        if not assets:
            logger.error("No assets found in database!")
            return {'successful': 0, 'failed': 0, 'total_records': 0}
        
        logger.info(f"📊 Found {total_assets} assets to collect prices for")
        logger.info(f"📅 Target: {years_back} years of historical data per asset")
        logger.info(f"⏰ Estimated time: {total_assets * 2 / 60:.1f} minutes")
        
        successful = 0
        failed = 0
        total_records = 0
        
        start_time = datetime.now()
        
        for i, asset in enumerate(assets, 1):
            try:
                logger.info(f"💰 [{i}/{total_assets}] Collecting prices for {asset.symbol} ({asset.type})")
                
                # Get price data
                records_count = self._collect_asset_prices(asset, years_back)
                
                if records_count > 0:
                    successful += 1
                    total_records += records_count
                    logger.info(f"✅ {asset.symbol}: {records_count} price records")
                else:
                    failed += 1
                    logger.warning(f"❌ {asset.symbol}: No price data")
                
                # Progress update every 50 assets
                if i % 50 == 0:
                    elapsed = datetime.now() - start_time
                    rate = i / elapsed.total_seconds() * 60  # assets per minute
                    remaining = (total_assets - i) / rate if rate > 0 else 0
                    
                    logger.info(f"🚀 Progress: {i}/{total_assets} ({i/total_assets*100:.1f}%)")
                    logger.info(f"⏰ Time elapsed: {elapsed} | ETA: {remaining:.1f} minutes")
                    logger.info(f"📊 Success rate: {successful/(successful+failed)*100:.1f}%")
                    logger.info(f"💾 Total records collected: {total_records:,}")
                
                # Rate limiting
                time.sleep(0.2)
                
            except KeyboardInterrupt:
                logger.warning("Collection interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error collecting prices for {asset.symbol}: {e}")
                failed += 1
        
        # Final summary
        total_time = datetime.now() - start_time
        
        logger.info(f"\n🎉 PRICE COLLECTION COMPLETE!")
        logger.info(f"=" * 60)
        logger.info(f"Assets processed: {successful + failed}/{total_assets}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total price records: {total_records:,}")
        logger.info(f"Total time: {total_time}")
        logger.info(f"Success rate: {successful/(successful+failed)*100:.1f}%")
        
        return {
            'successful': successful,
            'failed': failed,
            'total_records': total_records
        }
    
    def _collect_asset_prices(self, asset: Asset, years_back: int) -> int:
        """Collect price data for a single asset"""
        try:
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years_back * 365)
            
            # Check for existing data
            latest_date = self.session.query(DailyPrice.date)\
                .filter_by(asset_id=asset.id)\
                .order_by(DailyPrice.date.desc())\
                .first()
            
            if latest_date:
                # Only collect new data after latest date
                start_date = latest_date[0] + timedelta(days=1)
                if start_date >= end_date:
                    logger.debug(f"{asset.symbol} already up to date")
                    return 0
            
            logger.debug(f"Fetching {asset.symbol} from {start_date} to {end_date}")
            
            # Get price data using yfinance
            ticker = yf.Ticker(asset.symbol)
            hist = ticker.history(start=start_date, end=end_date, auto_adjust=True, back_adjust=True)
            
            if hist.empty:
                return 0
            
            # Convert to price records
            records_saved = 0
            for date_index, row in hist.iterrows():
                price_date = date_index.date()
                
                # Check if record already exists (prevent duplicates)
                existing = self.session.query(DailyPrice)\
                    .filter_by(asset_id=asset.id, date=price_date)\
                    .first()
                
                if existing:
                    continue
                
                # Create new price record
                price_record = DailyPrice(
                    asset_id=asset.id,
                    date=price_date,
                    open_price=float(row['Open']) if pd.notna(row['Open']) else None,
                    high_price=float(row['High']) if pd.notna(row['High']) else None,
                    low_price=float(row['Low']) if pd.notna(row['Low']) else None,
                    close_price=float(row['Close']) if pd.notna(row['Close']) else None,
                    volume=int(row['Volume']) if pd.notna(row['Volume']) else None,
                    dividends=float(row.get('Dividends', 0)) if pd.notna(row.get('Dividends')) else None,
                    stock_splits=float(row.get('Stock Splits', 0)) if pd.notna(row.get('Stock Splits')) else None
                )
                
                self.session.add(price_record)
                records_saved += 1
            
            # Commit batch
            if records_saved > 0:
                self.session.commit()
            
            return records_saved
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error collecting prices for {asset.symbol}: {e}")
            return 0
    
    # ========================= UTILITY METHODS =========================
    
    def get_database_summary(self) -> Dict:
        """Get comprehensive database statistics"""
        try:
            # Rollback any pending transaction to ensure clean state
            self.session.rollback()
            
            # Asset counts
            total_assets = self.session.query(Asset).count()
            active_assets = self.session.query(Asset).filter_by(is_active=True).count()
            
            # By type
            stocks = self.session.query(Asset).filter_by(type='stock').count()
            etfs = self.session.query(Asset).filter_by(type='etf').count()
            crypto = self.session.query(Asset).filter_by(type='crypto').count()
            mutual_funds = self.session.query(Asset).filter_by(type='mutual_fund').count()
            
            # By country
            us_assets = self.session.query(Asset).filter_by(country='US').count()
            indian_assets = self.session.query(Asset).filter_by(country='IN').count()
            
            # Price data stats
            total_prices = self.session.query(DailyPrice).count()
            assets_with_prices = self.session.query(DailyPrice.asset_id).distinct().count()
            
            return {
                'total_assets': total_assets,
                'active_assets': active_assets,
                'by_type': {
                    'stocks': stocks,
                    'etfs': etfs,
                    'crypto': crypto,
                    'mutual_funds': mutual_funds
                },
                'by_country': {
                    'US': us_assets,
                    'India': indian_assets,
                    'Global': total_assets - us_assets - indian_assets
                },
                'price_data': {
                    'total_records': total_prices,
                    'assets_with_prices': assets_with_prices,
                    'coverage_percent': (assets_with_prices / total_assets * 100) if total_assets > 0 else 0
                }
            }
        except Exception as e:
            # Ensure rollback on error
            self.session.rollback()
            logger.error(f"Error getting database summary: {e}")
            return {}

def interactive_menu():
    """🚀 UNIFIED INTERACTIVE MENU"""
    collector = UnifiedFinancialCollector()
    
    while True:
        print("\n" + "=" * 70)
        print("🚀 UNIFIED FINANCIAL DATA COLLECTOR")
        print("=" * 70)
        print("📊 ONE SYSTEM FOR ALL ASSETS + PRICES")
        print()
        
        # Show current status
        summary = collector.get_database_summary()
        if summary:
            print(f"📈 Current Database: {summary['total_assets']} assets, {summary['price_data']['total_records']:,} price records")
            print(f"📊 Coverage: {summary['price_data']['coverage_percent']:.1f}% assets have price data")
        
        print("\n🎯 COLLECTION OPTIONS:")
        print("1️⃣  🚀 COLLECT ALL ASSETS (Stocks + ETFs + Crypto + Mutual Funds)")
        print("2️⃣  📈 US Stocks Only")
        print("3️⃣  🇮🇳 Indian Stocks Only (2000+ from NSE)")
        print("4️⃣  📊 ETFs Only")
        print("5️⃣  ₿ Cryptocurrencies Only") 
        print("6️⃣  💼 Mutual Funds Only")
        print()
        print("💰 PRICE DATA COLLECTION:")
        print("7️⃣  💥 MASSIVE PRICE COLLECTION (25 years for ALL assets)")
        print("8️⃣  📅 Quick Price Update (last 30 days)")
        print("9️⃣  🎯 Custom Price Collection (specify years)")
        print()
        print("📊 UTILITIES:")
        print("0️⃣  📊 Show Database Statistics")
        print("❌ Exit")
        
        choice = input("\n🤔 Select option: ").strip()
        
        try:
            if choice == '1':
                print("\n🚀 Starting COMPREHENSIVE asset collection...")
                print("📊 This will collect ALL financial assets:")
                print("   • US Stocks (S&P 500 + popular)")
                print("   • Indian Stocks (2000+ from NSE)")
                print("   • ETFs (200+ major ETFs)")
                print("   • Cryptocurrencies (60+ major coins)")
                print("   • Mutual Funds (50+ major funds)")
                
                confirm = input("\n🤔 Continue? (y/N): ").strip().lower()
                if confirm == 'y':
                    results = collector.collect_all_assets()
                    print(f"\n🎉 COLLECTION COMPLETE!")
                    print(f"✅ US Stocks: {results['us_stocks']}")
                    print(f"✅ Indian Stocks: {results['indian_stocks']}")
                    print(f"✅ ETFs: {results['etfs']}")
                    print(f"✅ Crypto: {results['crypto']}")
                    print(f"✅ Mutual Funds: {results['mutual_funds']}")
                    print(f"📊 Total New Assets: {results['total']}")
            
            elif choice == '2':
                collector._collect_assets(collector.get_comprehensive_us_stocks(), 'stock', 'US', 'USD')
            
            elif choice == '3':
                collector._collect_assets(collector.get_comprehensive_indian_stocks(), 'stock', 'IN', 'INR')
            
            elif choice == '4':
                collector._collect_assets(collector.get_comprehensive_etfs(), 'etf', 'US', 'USD')
            
            elif choice == '5':
                collector._collect_assets(collector.get_comprehensive_crypto(), 'crypto', 'Global', 'USD')
            
            elif choice == '6':
                collector._collect_assets(collector.get_comprehensive_mutual_funds(), 'mutual_fund', 'US', 'USD')
            
            elif choice == '7':
                print("\n💥 MASSIVE PRICE COLLECTION!")
                print("⚠️  This will collect 25 YEARS of price data for ALL assets!")
                print("📊 Expected: 500,000+ price records")
                print("⏰ Time: 2-6 hours depending on asset count")
                
                confirm = input("\n🤔 Are you absolutely sure? (y/N): ").strip().lower()
                if confirm == 'y':
                    collector.collect_all_prices(years_back=25)
            
            elif choice == '8':
                print("\n📅 Quick price update (last 30 days)...")
                collector.collect_all_prices(years_back=0.1)  # ~30 days
            
            elif choice == '9':
                try:
                    years = int(input("Enter years of history to collect: "))
                    collector.collect_all_prices(years_back=years)
                except ValueError:
                    print("Invalid input")
            
            elif choice == '0':
                summary = collector.get_database_summary()
                if summary:
                    print(f"\n📊 DATABASE STATISTICS")
                    print(f"=" * 50)
                    print(f"Total Assets: {summary['total_assets']}")
                    print(f"Active Assets: {summary['active_assets']}")
                    print(f"\nBy Type:")
                    for asset_type, count in summary['by_type'].items():
                        print(f"  {asset_type.capitalize()}: {count}")
                    print(f"\nBy Region:")
                    for region, count in summary['by_country'].items():
                        print(f"  {region}: {count}")
                    print(f"\nPrice Data:")
                    print(f"  Total Records: {summary['price_data']['total_records']:,}")
                    print(f"  Assets with Prices: {summary['price_data']['assets_with_prices']}")
                    print(f"  Coverage: {summary['price_data']['coverage_percent']:.1f}%")
            
            elif choice.lower() in ['exit', 'quit', 'x', 'q']:
                break
            
            else:
                print("Invalid option")
        
        except KeyboardInterrupt:
            print("\n👋 Interrupted")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    print("👋 Goodbye!")

if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")