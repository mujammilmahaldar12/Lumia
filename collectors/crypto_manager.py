"""
Crypto Manager - Fetches cryptocurrency information from CoinGecko API.
Handles major cryptocurrencies and tokens across different blockchains.

Similar pattern to other managers but specialized for cryptocurrency data.
"""

import requests
import time
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional
import logging
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our models
from models.assets import Asset
from database import get_db
from utils.logging_config import setup_unicode_logging


class CryptoManager:
    """
    Complete cryptocurrency management system.
    Uses CoinGecko API (free tier) to fetch crypto data.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.db = None
        
        # CoinGecko API endpoints (free tier)
        self.base_url = "https://api.coingecko.com/api/v3"
        self.coins_list_url = f"{self.base_url}/coins/list"
        self.coins_markets_url = f"{self.base_url}/coins/markets"
        
        # Top cryptocurrencies by market cap (for initial sync)
        self.top_crypto_ids = [
            # Top 20 by market cap
            'bitcoin', 'ethereum', 'tether', 'binancecoin', 'solana',
            'xrp', 'steth', 'dogecoin', 'cardano', 'avalanche-2',
            'tron', 'chainlink', 'polygon-pos', 'wrapped-bitcoin', 'shiba-inu',
            'polkadot', 'litecoin', 'bitcoin-cash', 'near', 'uniswap',
            # DeFi tokens
            'compound-ether', 'aave', 'maker', 'yearn-finance', 'sushi',
            # Layer 2 & Scaling
            'matic-network', 'optimism', 'arbitrum', 'loopring',
            # Stablecoins
            'usd-coin', 'dai', 'frax', 'terrausd',
            # Meme coins (popular)
            'pepe', 'floki', 'bonk'
        ]
        
        # Request rate limiting (CoinGecko free tier: 30 calls/minute)
        self.rate_limit_delay = 2.5  # 2.5 seconds between requests
    
    def _setup_logger(self):
        """Setup Unicode-safe logging for crypto manager."""
        return setup_unicode_logging(
            "lumia.crypto_manager",
            level='INFO',
            console=True
        )
    
    def get_db_session(self) -> Session:
        """Get database session."""
        if not self.db:
            self.db = next(get_db())
        return self.db
    
    def close_db_session(self):
        """Close database session."""
        if self.db:
            self.db.close()
            self.db = None

    # ========================================
    # FUNCTION 1: DOWNLOAD CRYPTO DATA
    # ========================================
    
    def download_crypto_list(self) -> List[Dict]:
        """
        Download complete list of cryptocurrencies from CoinGecko.
        Returns basic info for all coins.
        
        Returns:
            List of basic crypto info dictionaries
        """
        self.logger.info("📥 Downloading complete crypto list from CoinGecko...")
        
        try:
            response = requests.get(self.coins_list_url, timeout=30)
            response.raise_for_status()
            
            coins_data = response.json()
            self.logger.info(f"✅ Downloaded {len(coins_data)} cryptocurrencies")
            
            return coins_data
            
        except Exception as e:
            self.logger.error(f"❌ Error downloading crypto list: {str(e)}")
            return []
    
    def download_top_crypto_details(self) -> List[Dict]:
        """
        Download detailed data for top cryptocurrencies.
        Uses market data endpoint for comprehensive information.
        
        Returns:
            List of detailed crypto dictionaries
        """
        self.logger.info(f"📥 Getting detailed data for {len(self.top_crypto_ids)} top cryptocurrencies...")
        
        crypto_details = []
        
        # CoinGecko allows up to 250 coins per request
        batch_size = 100
        
        for i in range(0, len(self.top_crypto_ids), batch_size):
            batch_ids = self.top_crypto_ids[i:i + batch_size]
            
            try:
                self.logger.info(f"  Fetching batch {i//batch_size + 1}: {len(batch_ids)} coins...")
                
                # Build request parameters
                params = {
                    'vs_currency': 'usd',
                    'ids': ','.join(batch_ids),
                    'order': 'market_cap_desc',
                    'per_page': batch_size,
                    'page': 1,
                    'sparkline': False,
                    'price_change_percentage': '1h,24h,7d,30d'
                }
                
                response = requests.get(self.coins_markets_url, params=params, timeout=30)
                response.raise_for_status()
                
                batch_data = response.json()
                
                for coin in batch_data:
                    crypto_data = self._extract_crypto_data(coin)
                    if crypto_data:
                        crypto_details.append(crypto_data)
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Error fetching batch {i//batch_size + 1}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Successfully fetched {len(crypto_details)} cryptocurrency details")
        return crypto_details
    
    def _extract_crypto_data(self, coin_data: Dict) -> Optional[Dict]:
        """
        Extract and standardize cryptocurrency data from CoinGecko response.
        
        Args:
            coin_data: Raw coin data from CoinGecko
            
        Returns:
            Standardized crypto data dictionary
        """
        try:
            crypto_data = {
                'symbol': coin_data['id'],  # Use CoinGecko ID as symbol for uniqueness
                'name': coin_data['name'],
                'type': 'crypto',
                'subtype': self._classify_crypto_type(coin_data),
                'exchange': 'CoinGecko',  # Aggregated data source
                'country': 'GLOBAL',
                'currency': 'USD',
                'sector': 'Cryptocurrency',
                'industry': 'Digital Assets',
                'market_cap': coin_data.get('market_cap'),
                'current_price': coin_data.get('current_price'),
                'price_change_24h': coin_data.get('price_change_percentage_24h'),
                'price_change_7d': coin_data.get('price_change_percentage_7d_in_currency'),
                'volume_24h': coin_data.get('total_volume'),
                'circulating_supply': coin_data.get('circulating_supply'),
                'total_supply': coin_data.get('total_supply'),
                'max_supply': coin_data.get('max_supply'),
                'market_cap_rank': coin_data.get('market_cap_rank'),
                'ticker_symbol': coin_data.get('symbol', '').upper(),  # Trading symbol
                'is_active': True,
                'coingecko_id': coin_data['id'],  # Store original CoinGecko ID
                'last_updated': coin_data.get('last_updated')
            }
            
            return crypto_data
            
        except Exception as e:
            self.logger.error(f"Error extracting data for {coin_data.get('id', 'unknown')}: {str(e)}")
            return None
    
    def _classify_crypto_type(self, coin_data: Dict) -> str:
        """
        Classify cryptocurrency type based on coin data.
        
        Args:
            coin_data: Coin data from CoinGecko
            
        Returns:
            Crypto classification
        """
        coin_id = coin_data['id'].lower()
        symbol = coin_data.get('symbol', '').lower()
        
        # Bitcoin and forks
        if coin_id == 'bitcoin' or 'bitcoin' in coin_id:
            return 'bitcoin'
        # Ethereum and ERC-20 tokens
        elif coin_id == 'ethereum' or symbol == 'eth':
            return 'ethereum'
        # Stablecoins
        elif coin_id in ['tether', 'usd-coin', 'dai', 'frax', 'terrausd'] or 'usd' in symbol:
            return 'stablecoin'
        # DeFi tokens
        elif coin_id in ['aave', 'compound-ether', 'maker', 'uniswap', 'sushi', 'yearn-finance']:
            return 'defi'
        # Layer 1 blockchains
        elif coin_id in ['binancecoin', 'solana', 'cardano', 'avalanche-2', 'polkadot', 'near']:
            return 'layer1'
        # Layer 2 solutions
        elif coin_id in ['matic-network', 'optimism', 'arbitrum', 'loopring']:
            return 'layer2'
        # Meme coins
        elif coin_id in ['dogecoin', 'shiba-inu', 'pepe', 'floki', 'bonk']:
            return 'meme'
        # Exchange tokens
        elif 'binance' in coin_id or coin_id in ['cro', 'ftt', 'okb']:
            return 'exchange'
        else:
            return 'other'

    # ========================================
    # FUNCTION 2: CROSS-CHECK WITH DATABASE
    # ========================================
    
    def cross_check_cryptos(self, new_cryptos: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Cross-check downloaded cryptos with existing database records.
        
        Args:
            new_cryptos: List of crypto data dictionaries
            
        Returns:
            Tuple of (cryptos_to_add, cryptos_to_update, cryptos_unchanged)
        """
        self.logger.info("🔍 Cross-checking cryptocurrencies with database...")
        
        db = self.get_db_session()
        
        # Get existing cryptos from database
        existing_cryptos = db.query(Asset).filter(Asset.type == 'crypto').all()
        existing_symbols = {crypto.symbol: crypto for crypto in existing_cryptos}
        
        cryptos_to_add = []
        cryptos_to_update = []
        cryptos_unchanged = []
        
        for new_crypto in new_cryptos:
            symbol = new_crypto['symbol']
            
            if symbol in existing_symbols:
                # Crypto exists, check if update needed
                existing_crypto = existing_symbols[symbol]
                
                if self._needs_update(existing_crypto, new_crypto):
                    cryptos_to_update.append({
                        'existing': existing_crypto,
                        'new_data': new_crypto
                    })
                else:
                    cryptos_unchanged.append(new_crypto)
            else:
                # New crypto, add to database
                cryptos_to_add.append(new_crypto)
        
        self.logger.info(f"📊 Cross-check results:")
        self.logger.info(f"  - New cryptos to add: {len(cryptos_to_add)}")
        self.logger.info(f"  - Cryptos to update: {len(cryptos_to_update)}")
        self.logger.info(f"  - Cryptos unchanged: {len(cryptos_unchanged)}")
        
        return cryptos_to_add, cryptos_to_update, cryptos_unchanged
    
    def _needs_update(self, existing_crypto: Asset, new_data: Dict) -> bool:
        """Check if existing crypto record needs update."""
        # For cryptos, always update due to volatile nature
        # Check key fields that change frequently
        fields_to_check = ['current_price', 'market_cap', 'volume_24h', 'market_cap_rank']
        
        for field in fields_to_check:
            if field in new_data:
                existing_value = getattr(existing_crypto, field, None)
                new_value = new_data[field]
                
                # For prices, update if difference > 1%
                if field == 'current_price' and existing_value and new_value:
                    if abs((new_value - existing_value) / existing_value) > 0.01:
                        return True
                elif existing_value != new_value:
                    return True
        
        return False

    # ========================================
    # FUNCTION 3: UPDATE EXISTING CRYPTOS
    # ========================================
    
    def update_existing_cryptos(self, cryptos_to_update: List[Dict]):
        """Update existing crypto records with new data."""
        if not cryptos_to_update:
            self.logger.info("ℹ️ No cryptos to update")
            return
        
        self.logger.info(f"🔄 Updating {len(cryptos_to_update)} existing cryptocurrencies...")
        
        db = self.get_db_session()
        updated_count = 0
        
        try:
            for update_info in cryptos_to_update:
                existing_crypto = update_info['existing']
                new_data = update_info['new_data']
                
                # Update fields specific to cryptocurrencies
                existing_crypto.name = new_data.get('name', existing_crypto.name)
                existing_crypto.market_cap = new_data.get('market_cap', existing_crypto.market_cap)
                # Update timestamp
                existing_crypto.last_updated = datetime.now()
                
                updated_count += 1
                
                # Add crypto-specific fields (you may need to add these to Asset model)
                # existing_crypto.current_price = new_data.get('current_price')
                # existing_crypto.volume_24h = new_data.get('volume_24h')
                # existing_crypto.market_cap_rank = new_data.get('market_cap_rank')
                
                updated_count += 1
                self.logger.info(f"  ✅ Updated {existing_crypto.symbol}")
            
            db.commit()
            self.logger.info(f"✅ Successfully updated {updated_count} cryptocurrencies")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating cryptos: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 4: ADD NEW CRYPTOS
    # ========================================
    
    def add_new_cryptos(self, cryptos_to_add: List[Dict]):
        """Add new crypto records to database."""
        if not cryptos_to_add:
            self.logger.info("ℹ️ No new cryptos to add")
            return
        
        self.logger.info(f"➕ Adding {len(cryptos_to_add)} new cryptocurrencies...")
        
        db = self.get_db_session()
        added_count = 0
        
        try:
            for crypto_data in cryptos_to_add:
                # Create new Asset record for cryptocurrency
                new_asset = Asset(
                    symbol=crypto_data['symbol'],
                    name=crypto_data['name'],
                    type='crypto',
                    subtype=crypto_data.get('subtype', 'other'),
                    exchange=crypto_data.get('exchange', 'CoinGecko'),
                    country=crypto_data.get('country', 'GLOBAL'),
                    currency=crypto_data.get('currency', 'USD'),
                    sector=crypto_data.get('sector', 'Cryptocurrency'),
                    industry=crypto_data.get('industry', 'Digital Assets'),
                    market_cap=crypto_data.get('market_cap'),
                    is_active=True,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                db.add(new_asset)
                added_count += 1
                self.logger.info(f"  ➕ Added {crypto_data['symbol']}")
            
            db.commit()
            self.logger.info(f"✅ Successfully added {added_count} new cryptocurrencies")
            
        except Exception as e:
            self.logger.error(f"❌ Error adding cryptos: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 5: MAIN ORCHESTRATOR
    # ========================================
    
    def sync_all_cryptos(self):
        """
        Main function to sync all cryptocurrencies.
        Downloads, cross-checks, updates, and adds cryptos.
        """
        self.logger.info("🚀 Starting cryptocurrency synchronization...")
        
        try:
            # Step 1: Download crypto data
            # For now, focus on top cryptos (CoinGecko free tier limits)
            all_cryptos = self.download_top_crypto_details()
            
            self.logger.info(f"📊 Total cryptos downloaded: {len(all_cryptos)}")
            
            if not all_cryptos:
                self.logger.warning("⚠️ No crypto data downloaded, aborting sync")
                return
            
            # Step 2: Cross-check with database
            cryptos_to_add, cryptos_to_update, cryptos_unchanged = self.cross_check_cryptos(all_cryptos)
            
            # Step 3: Update existing cryptos
            self.update_existing_cryptos(cryptos_to_update)
            
            # Step 4: Add new cryptos
            self.add_new_cryptos(cryptos_to_add)
            
            # Step 5: Summary
            self.logger.info("🎉 Cryptocurrency synchronization completed!")
            self.logger.info(f"📈 Summary:")
            self.logger.info(f"  - Total cryptos processed: {len(all_cryptos)}")
            self.logger.info(f"  - New cryptos added: {len(cryptos_to_add)}")
            self.logger.info(f"  - Existing cryptos updated: {len(cryptos_to_update)}")
            self.logger.info(f"  - Cryptos unchanged: {len(cryptos_unchanged)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in crypto synchronization: {str(e)}")
            raise
        
        finally:
            self.close_db_session()
    
    def sync_top_cryptos_only(self, limit: int = 20):
        """
        Sync only top N cryptocurrencies by market cap.
        Useful for quick updates or testing.
        
        Args:
            limit: Number of top cryptos to sync
        """
        self.logger.info(f"🚀 Syncing top {limit} cryptocurrencies...")
        
        # Temporarily adjust the list
        original_list = self.top_crypto_ids.copy()
        self.top_crypto_ids = self.top_crypto_ids[:limit]
        
        try:
            self.sync_all_cryptos()
        finally:
            # Restore original list
            self.top_crypto_ids = original_list


# ========================================
# CONVENIENCE FUNCTIONS FOR EASY USE
# ========================================

def sync_cryptos():
    """Easy function to sync all cryptocurrencies."""
    manager = CryptoManager()
    manager.sync_all_cryptos()

def sync_top_cryptos(limit: int = 20):
    """Sync only top cryptocurrencies."""
    manager = CryptoManager()
    manager.sync_top_cryptos_only(limit)


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    print("₿ Lumia Crypto Manager")
    print("=" * 50)
    
    # You can run different functions:
    
    # Option 1: Sync all configured cryptos
    sync_cryptos()
    
    # Option 2: Sync only top 10 cryptos (faster for testing)
    # sync_top_cryptos(10)