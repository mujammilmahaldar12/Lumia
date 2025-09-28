"""
Unified News Pipeline Orchestrator
Main coordinator for all news collectors with sentiment analysis and database storage
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    import schedule
except ImportError:
    schedule = None
    
try:
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
except ImportError:
    sessionmaker = None
    create_engine = None

from .base import NewsItem, CollectionResult
from .models import Base, NewsSource, NewsArticle, SentimentAnalysis, ExtractedEntity, StockMention, CollectionJob
from .stock_research_collector import StockResearchCollector
from .social_media_collector import SocialMediaCollector
from .company_website_collector import CompanyWebsiteCollector
from .algo_trading_collector import AlgoTradingNewsCollector
from .sentiment_analyzer import FinGPTAnalyzer

logger = logging.getLogger(__name__)

class UnifiedNewsPipeline:
    """
    Unified news collection and analysis pipeline
    
    Features:
    - Orchestrates all news collectors
    - Processes articles through sentiment analysis
    - Handles deduplication across sources
    - Stores results in database
    - Provides scheduling and monitoring
    - Generates alerts for high-impact news
    """
    
    def __init__(self, 
                 database_url: str,
                 api_keys: Dict[str, str] = None,
                 max_workers: int = 4,
                 enable_scheduling: bool = True):
        """
        Initialize the unified news pipeline
        
        Args:
            database_url: SQLAlchemy database URL
            api_keys: Dictionary of API keys for various services
            max_workers: Number of worker threads for parallel processing
            enable_scheduling: Whether to enable scheduled collection
        """
        self.database_url = database_url
        self.api_keys = api_keys or {}
        self.max_workers = max_workers
        self.enable_scheduling = enable_scheduling
        
        # Initialize database
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session_factory = Session
        
        # Initialize collectors
        self.collectors = {
            'stock_research': StockResearchCollector(self.api_keys),
            'social_media': SocialMediaCollector(self.api_keys),
            'company_website': CompanyWebsiteCollector(self.api_keys.get('sec_api_key')),
            'algo_trading': AlgoTradingNewsCollector()
        }
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = FinGPTAnalyzer()
        
        # Pipeline statistics
        self.stats = {
            'total_collections': 0,
            'total_articles_collected': 0,
            'total_articles_processed': 0,
            'total_articles_stored': 0,
            'errors': [],
            'last_collection_time': None,
            'average_processing_time': 0
        }
        
        # Collection configuration
        self.collection_config = {
            'default_hours_back': 24,
            'max_articles_per_source': 100,
            'batch_size_sentiment': 50,
            'deduplication_threshold': 0.8,
            'alert_impact_threshold': 0.7
        }
        
        # Initialize scheduling if enabled
        if enable_scheduling:
            self._setup_scheduling()
        
        logger.info("Unified News Pipeline initialized successfully")
    
    def collect_all_news(self, 
                        hours_back: int = None,
                        max_articles: int = None,
                        sources: List[str] = None) -> Dict[str, Any]:
        """
        Collect news from all sources
        
        Args:
            hours_back: Hours to look back (default from config)
            max_articles: Max articles per source (default from config)
            sources: List of specific sources to collect from (default: all)
            
        Returns:
            Dictionary with collection results and statistics
        """
        start_time = time.time()
        
        hours_back = hours_back or self.collection_config['default_hours_back']
        max_articles = max_articles or self.collection_config['max_articles_per_source']
        sources = sources or list(self.collectors.keys())
        
        logger.info(f"Starting news collection from {len(sources)} sources")
        
        # Create collection job record\n        job_id = self._create_collection_job('all_sources', {\n            'hours_back': hours_back,\n            'max_articles': max_articles,\n            'sources': sources\n        })\n        \n        all_articles = []\n        collection_results = {}\n        errors = []\n        \n        try:\n            # Collect from all sources in parallel\n            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:\n                # Submit collection tasks\n                future_to_source = {\n                    executor.submit(\n                        self.collectors[source].collect_recent_news,\n                        hours_back,\n                        max_articles\n                    ): source for source in sources if source in self.collectors\n                }\n                \n                # Process completed tasks\n                for future in as_completed(future_to_source):\n                    source = future_to_source[future]\n                    try:\n                        result = future.result()\n                        collection_results[source] = result\n                        all_articles.extend(result.items)\n                        \n                        logger.info(f\"Collected {result.items_collected} articles from {source}\")\n                        \n                    except Exception as e:\n                        error_msg = f\"Error collecting from {source}: {str(e)}\"\n                        logger.error(error_msg)\n                        errors.append(error_msg)\n            \n            # Deduplicate articles\n            unique_articles = self._deduplicate_articles(all_articles)\n            logger.info(f\"Deduplicated {len(all_articles)} -> {len(unique_articles)} articles\")\n            \n            # Process articles through sentiment analysis\n            processed_articles = self._process_articles_sentiment(unique_articles)\n            logger.info(f\"Processed sentiment for {len(processed_articles)} articles\")\n            \n            # Store articles in database\n            stored_count = self._store_articles_batch(processed_articles)\n            logger.info(f\"Stored {stored_count} articles in database\")\n            \n            # Generate alerts for high-impact news\n            alerts_generated = self._generate_news_alerts(processed_articles)\n            logger.info(f\"Generated {alerts_generated} news alerts\")\n            \n            # Update statistics\n            execution_time = time.time() - start_time\n            self._update_stats(len(unique_articles), len(processed_articles), stored_count, execution_time)\n            \n            # Update collection job\n            self._complete_collection_job(job_id, stored_count, len(processed_articles), len(errors))\n            \n            return {\n                'success': True,\n                'job_id': job_id,\n                'articles_collected': len(all_articles),\n                'articles_unique': len(unique_articles),\n                'articles_processed': len(processed_articles),\n                'articles_stored': stored_count,\n                'alerts_generated': alerts_generated,\n                'execution_time': execution_time,\n                'collection_results': collection_results,\n                'errors': errors\n            }\n            \n        except Exception as e:\n            error_msg = f\"Error in news collection pipeline: {str(e)}\"\n            logger.error(error_msg)\n            errors.append(error_msg)\n            \n            # Mark job as failed\n            self._fail_collection_job(job_id, error_msg)\n            \n            return {\n                'success': False,\n                'job_id': job_id,\n                'error': error_msg,\n                'errors': errors,\n                'execution_time': time.time() - start_time\n            }\n    \n    def collect_stock_news(self, \n                          stock_symbol: str,\n                          hours_back: int = None,\n                          max_articles: int = None) -> Dict[str, Any]:\n        \"\"\"\n        Collect news for a specific stock from all sources\n        \n        Args:\n            stock_symbol: Stock ticker symbol\n            hours_back: Hours to look back\n            max_articles: Max articles per source\n            \n        Returns:\n            Dictionary with collection results\n        \"\"\"\n        start_time = time.time()\n        \n        hours_back = hours_back or self.collection_config['default_hours_back']\n        max_articles = max_articles or self.collection_config['max_articles_per_source'] // 2\n        \n        logger.info(f\"Collecting news for stock: {stock_symbol}\")\n        \n        # Create collection job\n        job_id = self._create_collection_job('stock_specific', {\n            'stock_symbol': stock_symbol,\n            'hours_back': hours_back,\n            'max_articles': max_articles\n        })\n        \n        all_articles = []\n        collection_results = {}\n        errors = []\n        \n        try:\n            # Collect from all sources in parallel\n            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:\n                future_to_source = {\n                    executor.submit(\n                        collector.collect_stock_news,\n                        stock_symbol,\n                        hours_back,\n                        max_articles\n                    ): source for source, collector in self.collectors.items()\n                }\n                \n                # Process results\n                for future in as_completed(future_to_source):\n                    source = future_to_source[future]\n                    try:\n                        result = future.result()\n                        collection_results[source] = result\n                        all_articles.extend(result.items)\n                        \n                    except Exception as e:\n                        error_msg = f\"Error collecting {stock_symbol} news from {source}: {str(e)}\"\n                        logger.error(error_msg)\n                        errors.append(error_msg)\n            \n            # Process articles\n            unique_articles = self._deduplicate_articles(all_articles)\n            processed_articles = self._process_articles_sentiment(unique_articles)\n            stored_count = self._store_articles_batch(processed_articles)\n            alerts_generated = self._generate_news_alerts(processed_articles)\n            \n            execution_time = time.time() - start_time\n            self._complete_collection_job(job_id, stored_count, len(processed_articles), len(errors))\n            \n            return {\n                'success': True,\n                'stock_symbol': stock_symbol,\n                'articles_collected': len(all_articles),\n                'articles_stored': stored_count,\n                'alerts_generated': alerts_generated,\n                'execution_time': execution_time,\n                'errors': errors\n            }\n            \n        except Exception as e:\n            error_msg = f\"Error collecting news for {stock_symbol}: {str(e)}\"\n            logger.error(error_msg)\n            self._fail_collection_job(job_id, error_msg)\n            \n            return {\n                'success': False,\n                'stock_symbol': stock_symbol,\n                'error': error_msg,\n                'execution_time': time.time() - start_time\n            }\n    \n    def _deduplicate_articles(self, articles: List[NewsItem]) -> List[NewsItem]:\n        \"\"\"Remove duplicate articles across sources\"\"\"\n        seen_urls = set()\n        seen_titles = set()\n        unique_articles = []\n        \n        for article in articles:\n            # Check URL duplication\n            if article.url in seen_urls:\n                continue\n            \n            # Check title similarity (simple approach)\n            title_key = article.title.lower().strip()\n            if title_key in seen_titles:\n                continue\n            \n            seen_urls.add(article.url)\n            seen_titles.add(title_key)\n            unique_articles.append(article)\n        \n        return unique_articles\n    \n    def _process_articles_sentiment(self, articles: List[NewsItem]) -> List[Dict[str, Any]]:\n        \"\"\"Process articles through sentiment analysis\"\"\"\n        processed_articles = []\n        \n        # Process in batches for efficiency\n        batch_size = self.collection_config['batch_size_sentiment']\n        \n        for i in range(0, len(articles), batch_size):\n            batch = articles[i:i + batch_size]\n            \n            try:\n                # Analyze sentiment for batch\n                sentiment_results = self.sentiment_analyzer.batch_analyze_sentiment(batch)\n                \n                # Combine articles with sentiment analysis\n                for article, sentiment in zip(batch, sentiment_results):\n                    processed_article = {\n                        'article': article,\n                        'sentiment_analysis': sentiment\n                    }\n                    processed_articles.append(processed_article)\n                    \n            except Exception as e:\n                logger.error(f\"Error processing sentiment for batch {i//batch_size + 1}: {e}\")\n                # Add articles without sentiment analysis\n                for article in batch:\n                    processed_articles.append({\n                        'article': article,\n                        'sentiment_analysis': None\n                    })\n        \n        return processed_articles\n    \n    def _store_articles_batch(self, processed_articles: List[Dict[str, Any]]) -> int:\n        \"\"\"Store articles and analysis results in database\"\"\"\n        session = self.session_factory()\n        stored_count = 0\n        \n        try:\n            for item in processed_articles:\n                article = item['article']\n                sentiment = item['sentiment_analysis']\n                \n                try:\n                    # Create NewsArticle record\n                    db_article = NewsArticle(\n                        external_id=article.external_id,\n                        title=article.title,\n                        content=article.content,\n                        summary=article.summary,\n                        url=article.url,\n                        author=article.author,\n                        published_at=article.published_at,\n                        article_type=self._determine_article_type(article),\n                        category=article.category,\n                        language='en',\n                        raw_data=article.raw_data\n                    )\n                    \n                    session.add(db_article)\n                    session.flush()  # Get the ID\n                    \n                    # Store sentiment analysis if available\n                    if sentiment:\n                        self._store_sentiment_analysis(session, db_article.id, sentiment)\n                        \n                        # Store entities\n                        if sentiment.get('entities'):\n                            self._store_entities(session, db_article.id, sentiment['entities'])\n                        \n                        # Store stock mentions\n                        if sentiment.get('stock_mentions'):\n                            self._store_stock_mentions(session, db_article.id, sentiment['stock_mentions'])\n                    \n                    stored_count += 1\n                    \n                except Exception as e:\n                    logger.error(f\"Error storing article {article.external_id}: {e}\")\n                    session.rollback()\n                    continue\n            \n            session.commit()\n            return stored_count\n            \n        except Exception as e:\n            logger.error(f\"Error in batch storage: {e}\")\n            session.rollback()\n            return stored_count\n        finally:\n            session.close()\n    \n    def _generate_news_alerts(self, processed_articles: List[Dict[str, Any]]) -> int:\n        \"\"\"Generate alerts for high-impact news\"\"\"\n        alerts_generated = 0\n        threshold = self.collection_config['alert_impact_threshold']\n        \n        for item in processed_articles:\n            try:\n                sentiment = item['sentiment_analysis']\n                if not sentiment:\n                    continue\n                \n                impact_score = sentiment.get('market_impact', {}).get('market_impact_score', 0)\n                \n                if impact_score >= threshold:\n                    # Generate alert (implement alert system)\n                    logger.info(f\"High-impact news alert: {item['article'].title} (impact: {impact_score})\")\n                    alerts_generated += 1\n                    \n            except Exception as e:\n                logger.error(f\"Error generating alert: {e}\")\n        \n        return alerts_generated\n    \n    def _setup_scheduling(self):\n        \"\"\"Setup scheduled news collection\"\"\"\n        # Schedule regular collections\n        schedule.every(1).hours.do(self.collect_all_news, hours_back=2, max_articles=50)\n        schedule.every().day.at(\"09:00\").do(self.collect_all_news, hours_back=24, max_articles=200)\n        \n        logger.info(\"News collection scheduling configured\")\n    \n    def run_scheduler(self):\n        \"\"\"Run the scheduled tasks (call this in a loop or separate thread)\"\"\"\n        while True:\n            schedule.run_pending()\n            time.sleep(60)  # Check every minute\n    \n    def get_pipeline_stats(self) -> Dict[str, Any]:\n        \"\"\"Get pipeline statistics\"\"\"\n        return self.stats.copy()\n    \n    def get_recent_collections(self, limit: int = 10) -> List[Dict[str, Any]]:\n        \"\"\"Get recent collection job results\"\"\"\n        session = self.session_factory()\n        try:\n            jobs = session.query(CollectionJob).order_by(\n                CollectionJob.started_at.desc()\n            ).limit(limit).all()\n            \n            return [{\n                'job_id': job.job_id,\n                'collector_type': job.collector_type,\n                'status': job.status,\n                'started_at': job.started_at,\n                'completed_at': job.completed_at,\n                'articles_collected': job.articles_collected,\n                'articles_processed': job.articles_processed,\n                'errors_encountered': job.errors_encountered\n            } for job in jobs]\n            \n        finally:\n            session.close()\n    \n    # Helper methods\n    def _create_collection_job(self, collector_type: str, parameters: Dict) -> str:\n        \"\"\"Create a new collection job record\"\"\"\n        session = self.session_factory()\n        try:\n            job = CollectionJob(\n                collector_type=collector_type,\n                parameters=parameters,\n                started_at=datetime.utcnow(),\n                status='running'\n            )\n            session.add(job)\n            session.commit()\n            return job.job_id\n        finally:\n            session.close()\n    \n    def _complete_collection_job(self, job_id: str, articles_collected: int, articles_processed: int, errors: int):\n        \"\"\"Mark collection job as completed\"\"\"\n        session = self.session_factory()\n        try:\n            job = session.query(CollectionJob).filter_by(job_id=job_id).first()\n            if job:\n                job.completed_at = datetime.utcnow()\n                job.status = 'completed'\n                job.articles_collected = articles_collected\n                job.articles_processed = articles_processed\n                job.errors_encountered = errors\n                session.commit()\n        finally:\n            session.close()\n    \n    def _fail_collection_job(self, job_id: str, error_message: str):\n        \"\"\"Mark collection job as failed\"\"\"\n        session = self.session_factory()\n        try:\n            job = session.query(CollectionJob).filter_by(job_id=job_id).first()\n            if job:\n                job.completed_at = datetime.utcnow()\n                job.status = 'failed'\n                job.error_message = error_message\n                session.commit()\n        finally:\n            session.close()\n    \n    def _determine_article_type(self, article: NewsItem) -> str:\n        \"\"\"Determine article type from NewsItem\"\"\"\n        if hasattr(article, 'raw_data') and article.raw_data:\n            platform = article.raw_data.get('platform')\n            if platform == 'twitter':\n                return 'tweet'\n            elif platform == 'reddit':\n                return 'social_post'\n            elif article.raw_data.get('source') == 'sec_edgar':\n                return 'sec_filing'\n        \n        return 'news_article'\n    \n    def _store_sentiment_analysis(self, session, article_id: int, sentiment: Dict):\n        \"\"\"Store sentiment analysis results\"\"\"\n        sentiment_record = SentimentAnalysis(\n            article_id=article_id,\n            overall_sentiment=sentiment['sentiment']['label'],\n            sentiment_score=sentiment['sentiment']['score'],\n            confidence_score=sentiment['confidence_score'],\n            bullish_score=sentiment['financial_scores']['bullish_score'],\n            bearish_score=sentiment['financial_scores']['bearish_score'],\n            uncertainty_score=sentiment['financial_scores']['uncertainty_score'],\n            market_impact_score=sentiment['market_impact']['market_impact_score'],\n            urgency_score=sentiment['market_impact']['urgency_score'],\n            model_used=sentiment['model_used'],\n            raw_analysis=sentiment\n        )\n        session.add(sentiment_record)\n    \n    def _store_entities(self, session, article_id: int, entities: List[Dict]):\n        \"\"\"Store extracted entities\"\"\"\n        for entity in entities:\n            entity_record = ExtractedEntity(\n                article_id=article_id,\n                entity_text=entity['text'],\n                entity_type=entity['label'],\n                start_position=entity.get('start'),\n                end_position=entity.get('end'),\n                confidence_score=entity.get('confidence', 1.0)\n            )\n            session.add(entity_record)\n    \n    def _store_stock_mentions(self, session, article_id: int, mentions: List[Dict]):\n        \"\"\"Store stock mentions\"\"\"\n        for mention in mentions:\n            mention_record = StockMention(\n                article_id=article_id,\n                stock_symbol=mention['symbol'],\n                mention_context=mention['context'],\n                sentiment=mention.get('mention_sentiment', 'neutral'),\n                position_start=mention.get('position_start'),\n                position_end=mention.get('position_end'),\n                relevance_score=mention.get('relevance_score', 0.5)\n            )\n            session.add(mention_record)\n    \n    def _update_stats(self, collected: int, processed: int, stored: int, execution_time: float):\n        \"\"\"Update pipeline statistics\"\"\"\n        self.stats['total_collections'] += 1\n        self.stats['total_articles_collected'] += collected\n        self.stats['total_articles_processed'] += processed\n        self.stats['total_articles_stored'] += stored\n        self.stats['last_collection_time'] = datetime.utcnow()\n        \n        # Update average processing time\n        current_avg = self.stats['average_processing_time']\n        total_collections = self.stats['total_collections']\n        self.stats['average_processing_time'] = ((current_avg * (total_collections - 1)) + execution_time) / total_collections\n\n# Example usage and testing\nif __name__ == \"__main__\":\n    # Configuration\n    DATABASE_URL = \"postgresql://user:password@localhost/news_db\"\n    API_KEYS = {\n        'twitter_bearer': 'your_twitter_bearer_token',\n        'reddit_client_id': 'your_reddit_client_id',\n        'reddit_client_secret': 'your_reddit_client_secret',\n        'sec_api_key': 'your_sec_api_key'\n    }\n    \n    # Initialize pipeline\n    pipeline = UnifiedNewsPipeline(\n        database_url=DATABASE_URL,\n        api_keys=API_KEYS,\n        max_workers=4\n    )\n    \n    # Run collection\n    result = pipeline.collect_all_news(hours_back=24, max_articles=100)\n    print(f\"Collection completed: {result}\")\n    \n    # Get pipeline statistics\n    stats = pipeline.get_pipeline_stats()\n    print(f\"Pipeline Statistics: {stats}\")\n    \n    # Example: collect news for specific stock\n    stock_result = pipeline.collect_stock_news(\"AAPL\", hours_back=12)\n    print(f\"AAPL news collection: {stock_result}\")