#!/usr/bin/env python3
"""
Main ingestion script for financial data pipeline.
Fetches news and stock data from APIs and sends to Kinesis streams.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import boto3
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
import psycopg2
from textblob import TextBlob
import sys
from dateutil.relativedelta import relativedelta
import yfinance as yf

# Load environment variables
load_dotenv("config.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()

# AWS Configuration
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
KINESIS_STREAM_NAME = os.getenv("KINESIS_STREAM_NAME", "financial-data-stream")

# API Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# Stock symbols to track
STOCK_SYMBOLS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX",
    "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "BAC"
]

# Company names for news search
COMPANY_NAMES = {
    "AAPL": ["Apple", "AAPL"],
    "GOOGL": ["Google", "Alphabet", "GOOGL"],
    "MSFT": ["Microsoft", "MSFT"],
    "AMZN": ["Amazon", "AMZN"],
    "TSLA": ["Tesla", "TSLA"],
    "META": ["Meta", "Facebook", "META"],
    "NVDA": ["NVIDIA", "NVDA"],
    "NFLX": ["Netflix", "NFLX"],
    "JPM": ["JPMorgan", "JPM"],
    "JNJ": ["Johnson & Johnson", "JNJ"],
    "V": ["Visa", "V"],
    "PG": ["Procter & Gamble", "PG"],
    "UNH": ["UnitedHealth", "UNH"],
    "HD": ["Home Depot", "HD"],
    "MA": ["Mastercard", "MA"],
    "DIS": ["Disney", "DIS"],
    "PYPL": ["PayPal", "PYPL"],
    "BAC": ["Bank of America", "BAC"]
}

# PostgreSQL local config
PG_HOST = os.getenv('DB_HOST', 'postgres')
PG_DB = os.getenv('DB_NAME', 'financial_sentiment')
PG_USER = os.getenv('DB_USER', 'postgres')
PG_PASSWORD = os.getenv('DB_PASSWORD', 'password')
PG_PORT = int(os.getenv('DB_PORT', '5432'))

def insert_news_pg(news_items):
    try:
        logger.info(f"Attempting to connect to PostgreSQL at {PG_HOST}:{PG_PORT}, database: {PG_DB}, user: {PG_USER}")
        conn = psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD, port=PG_PORT)
        cur = conn.cursor()
        
        logger.info(f"Successfully connected to PostgreSQL. Inserting {len(news_items)} news items...")
        
        for item in news_items:
            cur.execute('''
                INSERT INTO news_with_sentiment (title, description, url, published_at, source_name, sentiment_score, sentiment_subjectivity, symbol)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                item.get('title'),
                item.get('description'),
                item.get('url'),
                item.get('published_at'),
                item.get('source'),
                item.get('sentiment_score', 0),
                item.get('sentiment_subjectivity', 0),
                item.get('symbol')
            ))
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Successfully inserted {len(news_items)} news items into PostgreSQL")
    except psycopg2.OperationalError as e:
        logger.error(f"PostgreSQL connection error: {e}")
        logger.error(f"Connection details - Host: {PG_HOST}, Port: {PG_PORT}, Database: {PG_DB}, User: {PG_USER}")
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error: {e}")
        logger.error(f"Error code: {e.pgcode}, Error message: {e.pgerror}")
    except Exception as e:
        logger.error(f"Unexpected error inserting news into PostgreSQL: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def insert_stock_pg(stock_item):
    try:
        logger.info(f"Attempting to connect to PostgreSQL for stock data at {PG_HOST}:{PG_PORT}")
        conn = psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD, port=PG_PORT)
        cur = conn.cursor()
        
        # Calcular promedios reales de sentimiento y subjetividad desde la base
        cur.execute('''
            SELECT AVG(sentiment_score), AVG(sentiment_subjectivity)
            FROM news_with_sentiment
            WHERE symbol = %s AND published_at >= NOW() - INTERVAL '24 hours'
        ''', (stock_item.get('symbol'),))
        avg_sentiment_score, avg_sentiment_subjectivity = cur.fetchone()
        avg_sentiment_score = avg_sentiment_score or 0
        avg_sentiment_subjectivity = avg_sentiment_subjectivity or 0
        
        # Usar la fecha real del precio si está disponible
        hour_value = stock_item.get('timestamp', datetime.utcnow())
        cur.execute('''
            INSERT INTO financial_sentiment_correlation (hour, symbol, sentiment_category, avg_sentiment_score, avg_sentiment_subjectivity, avg_close_price, max_high_price, min_low_price, total_volume, price_points, price_change_percent, sentiment_change, news_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            hour_value,
            stock_item.get('symbol'),
            'Neutral',
            avg_sentiment_score,
            avg_sentiment_subjectivity,
            stock_item.get('close'),
            stock_item.get('high'),
            stock_item.get('low'),
            stock_item.get('volume'),
            1,
            0,
            0,
            1
        ))
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Successfully inserted stock item for {stock_item.get('symbol')} into PostgreSQL")
    except psycopg2.OperationalError as e:
        logger.error(f"PostgreSQL connection error for stock data: {e}")
        logger.error(f"Connection details - Host: {PG_HOST}, Port: {PG_PORT}, Database: {PG_DB}, User: {PG_USER}")
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error for stock data: {e}")
        logger.error(f"Error code: {e.pgcode}, Error message: {e.pgerror}")
    except Exception as e:
        logger.error(f"Unexpected error inserting stock into PostgreSQL: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

class DataIngestionManager:
    """Manages data ingestion from multiple sources."""
    
    def __init__(self):
        """Initialize the data ingestion manager."""
        self.kinesis_client = boto3.client('kinesis', region_name=AWS_REGION)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Financial-Sentiment-Pipeline/1.0'
        })
        
    async def fetch_news_data(self, symbol: str) -> List[Dict]:
        """Fetch news data for a given stock symbol using Alpha Vantage News API."""
        if not ALPHA_VANTAGE_API_KEY:
            logger.warning("ALPHA_VANTAGE_API_KEY not configured, skipping news ingestion")
            return []
            
        all_news = []
        
        try:
            # Fetch news from Alpha Vantage News API
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'topics': 'technology,earnings,ipo,mearnings',
                'limit': 10,  # Máximo 10 noticias por símbolo para el modo en tiempo real
                'apikey': ALPHA_VANTAGE_API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'feed' in data:
                articles = data['feed']
                
                for article in articles:
                    # Alpha Vantage ya proporciona análisis de sentimiento
                    sentiment_score = float(article.get('overall_sentiment_score', 0))
                    sentiment_label = article.get('overall_sentiment_label', 'neutral')
                    
                    # Convertir label a score si no hay score numérico
                    if sentiment_score == 0 and sentiment_label:
                        if sentiment_label.lower() == 'positive':
                            sentiment_score = 0.5
                        elif sentiment_label.lower() == 'negative':
                            sentiment_score = -0.5
                        else:
                            sentiment_score = 0.0
                    
                    news_item = {
                        'type': 'news',
                        'symbol': symbol,
                        'company_name': article.get('source', ''),
                        'title': article.get('title', ''),
                        'description': article.get('summary', ''),
                        'content': article.get('summary', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', ''),
                        'published_at': article.get('time_published', ''),
                        'ingested_at': datetime.utcnow().isoformat(),
                        'sentiment_score': sentiment_score,
                        'sentiment_subjectivity': 0.5  # Alpha Vantage no proporciona subjetividad
                    }
                    all_news.append(news_item)
                    
                logger.info(f"Fetched {len(articles)} news articles for {symbol}")
            else:
                logger.warning(f"No news data found for {symbol}")
                
        except requests.RequestException as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching news for {symbol}: {e}")
                
        return all_news
    
    async def fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """Fetch stock price data for a given symbol."""
        if not ALPHA_VANTAGE_API_KEY:
            logger.warning("ALPHA_VANTAGE_API_KEY not configured, skipping stock data ingestion")
            return None
            
        try:
            # Fetch real-time stock data from Alpha Vantage
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': '1min',
                'apikey': ALPHA_VANTAGE_API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Get the latest price data
            time_series = data.get('Time Series (1min)', {})
            if time_series:
                latest_time = max(time_series.keys())
                latest_data = time_series[latest_time]
                
                stock_item = {
                    'type': 'stock_price',
                    'symbol': symbol,
                    'timestamp': latest_time,
                    'open': float(latest_data.get('1. open', 0)),
                    'high': float(latest_data.get('2. high', 0)),
                    'low': float(latest_data.get('3. low', 0)),
                    'close': float(latest_data.get('4. close', 0)),
                    'volume': int(latest_data.get('5. volume', 0)),
                    'ingested_at': datetime.utcnow().isoformat()
                }
                
                logger.info(f"Fetched stock data for {symbol}: ${stock_item['close']}")
                return stock_item
                
        except requests.RequestException as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching stock data for {symbol}: {e}")
            
        return None
    
    async def send_to_kinesis(self, data: Dict, partition_key: str) -> bool:
        """Send data to Kinesis stream."""
        try:
            response = self.kinesis_client.put_record(
                StreamName=KINESIS_STREAM_NAME,
                Data=json.dumps(data),
                PartitionKey=partition_key
            )
            
            logger.debug(f"Sent data to Kinesis: {response['SequenceNumber']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data to Kinesis: {e}")
            return False
    
    async def ingest_data_for_symbol(self, symbol: str) -> None:
        """Ingest both news and stock data for a given symbol."""
        news = await self.fetch_news_data(symbol)
        if news:
            insert_news_pg(news)
        stock = await self.fetch_stock_data(symbol)
        if stock:
            stock['symbol'] = symbol
            insert_stock_pg(stock)
    
    async def run_ingestion_cycle(self) -> None:
        """Run a complete ingestion cycle for solo un símbolo (AAPL)."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            symbols = ['AAPL']  # Solo procesar AAPL
            task = progress.add_task("Ingesting data...", total=len(symbols))
            for symbol in symbols:
                progress.update(task, description=f"Ingesting data for {symbol}...")
                await self.ingest_data_for_symbol(symbol)
                progress.advance(task)
                await asyncio.sleep(1)
    
    async def run_continuous_ingestion(self, interval_minutes: int = 5) -> None:
        """Run continuous ingestion with specified interval."""
        logger.info(f"Starting continuous ingestion with {interval_minutes} minute intervals")
        
        while True:
            try:
                start_time = time.time()
                
                await self.run_ingestion_cycle()
                
                elapsed_time = time.time() - start_time
                sleep_time = max(0, (interval_minutes * 60) - elapsed_time)
                
                logger.info(f"Ingestion cycle completed in {elapsed_time:.2f}s. Sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("Ingestion stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in ingestion cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

def fetch_historic_prices(symbol, months=6):
    """Descargar precios diarios históricos de los últimos 'months' meses para un símbolo usando Alpha Vantage."""
    if not ALPHA_VANTAGE_API_KEY:
        logger.warning("ALPHA_VANTAGE_API_KEY not configured, skipping stock data ingestion")
        return []
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': symbol,
        'outputsize': 'full',
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    time_series = data.get('Time Series (Daily)', {})
    if not time_series:
        logger.warning(f"No price data for {symbol}")
        return []
    # Filtrar solo los últimos 'months' meses
    end_date = datetime.utcnow().date()
    start_date = end_date - relativedelta(months=months)
    prices = []
    for date_str, values in time_series.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if start_date <= date_obj <= end_date:
            prices.append({
                'symbol': symbol,
                'timestamp': date_str,
                'open': float(values.get('1. open', 0)),
                'high': float(values.get('2. high', 0)),
                'low': float(values.get('3. low', 0)),
                'close': float(values.get('4. close', 0)),
                'volume': int(values.get('6. volume', 0)),
            })
    logger.info(f"Fetched {len(prices)} daily prices for {symbol} (last {months} months)")
    return prices

def fetch_historic_news(symbol, months=6):
    """Descargar noticias históricas usando Alpha Vantage News API."""
    if not ALPHA_VANTAGE_API_KEY:
        logger.warning("ALPHA_VANTAGE_API_KEY not configured, skipping news ingestion")
        return []
    
    all_news = []
    
    # Alpha Vantage News API endpoint
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': symbol,
        'topics': 'technology,earnings,ipo,mearnings',
        'time_from': '20240101T0000',  # Desde enero 2024
        'limit': 50,  # Máximo 50 noticias por símbolo
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        logger.info(f"Fetching news for {symbol} using Alpha Vantage...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'feed' in data:
            articles = data['feed']
            logger.info(f"Found {len(articles)} news articles for {symbol}")
            
            for article in articles:
                # Alpha Vantage ya proporciona análisis de sentimiento
                sentiment_score = float(article.get('overall_sentiment_score', 0))
                sentiment_label = article.get('overall_sentiment_label', 'neutral')
                
                # Convertir label a score si no hay score numérico
                if sentiment_score == 0 and sentiment_label:
                    if sentiment_label.lower() == 'positive':
                        sentiment_score = 0.5
                    elif sentiment_label.lower() == 'negative':
                        sentiment_score = -0.5
                    else:
                        sentiment_score = 0.0
                
                news_item = {
                    'type': 'news',
                    'symbol': symbol,
                    'company_name': article.get('source', ''),
                    'title': article.get('title', ''),
                    'description': article.get('summary', ''),
                    'content': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', ''),
                    'published_at': article.get('time_published', ''),
                    'ingested_at': datetime.utcnow().isoformat(),
                    'sentiment_score': sentiment_score,
                    'sentiment_subjectivity': 0.5  # Alpha Vantage no proporciona subjetividad
                }
                all_news.append(news_item)
        else:
            logger.warning(f"No news data found for {symbol}. Response: {data}")
            
    except requests.RequestException as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching news for {symbol}: {e}")
    
    logger.info(f"Fetched {len(all_news)} news for {symbol}")
    return all_news

def insert_historic_prices(prices):
    for item in prices:
        stock_item = {
            'symbol': item.get('symbol'),
            'close': item.get('close'),
            'high': item.get('high'),
            'low': item.get('low'),
            'volume': item.get('volume'),
            'timestamp': item.get('timestamp')  # Usar la fecha real del precio
        }
        insert_stock_pg(stock_item)

def insert_historic_news(news):
    # news: lista de dicts
    insert_news_pg(news)

def fetch_yahoo_prices(symbol, days=30):
    """Descargar precios diarios históricos de los últimos 'days' días para un símbolo usando Yahoo Finance."""
    end = datetime.now()
    start = end - timedelta(days=days)
    df = yf.download(symbol, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
    prices = []
    for date, row in df.iterrows():
        prices.append({
            'symbol': symbol,
            'timestamp': date.strftime('%Y-%m-%d'),
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close']),
            'volume': int(row['Volume']),
        })
    return prices

async def main():
    """Main function to run the data ingestion."""
    console.print("[bold blue]Financial Data Ingestion Pipeline[/bold blue]")
    console.print("=" * 50)
    
    # Validate configuration
    if not NEWS_API_KEY and not ALPHA_VANTAGE_API_KEY:
        console.print("[red]Error: No API keys configured. Please set NEWS_API_KEY or ALPHA_VANTAGE_API_KEY[/red]")
        return
    
    if not KINESIS_STREAM_NAME:
        console.print("[red]Error: KINESIS_STREAM_NAME not configured[/red]")
        return
    
    # Initialize ingestion manager
    ingestion_manager = DataIngestionManager()
    
    # Check if running in continuous mode
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        await ingestion_manager.run_continuous_ingestion(interval)
    elif len(sys.argv) > 1 and sys.argv[1] == "--historic":
        months = 6
        for symbol in STOCK_SYMBOLS:
            # Precios históricos
            try:
                prices = fetch_historic_prices(symbol, months=months)
                insert_historic_prices(prices)
            except Exception as e:
                logger.error(f"Error fetching/inserting historic prices for {symbol}: {e}")
            # Noticias históricas
            try:
                news = fetch_historic_news(symbol, months=months)
                insert_historic_news(news)
            except Exception as e:
                logger.error(f"Error fetching/inserting historic news for {symbol}: {e}")
        logger.info("Historic data ingestion completed!")
    else:
        # Run single ingestion cycle
        await ingestion_manager.run_ingestion_cycle()
        console.print("[green]Ingestion completed successfully![/green]")


if __name__ == "__main__":
    asyncio.run(main()) 