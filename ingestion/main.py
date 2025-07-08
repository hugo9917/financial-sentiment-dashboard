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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
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
    "AAPL",
    "GOOGL",
    "MSFT",
    "AMZN",
    "TSLA",
    "META",
    "NVDA",
    "NFLX",
    "JPM",
    "JNJ",
    "V",
    "PG",
    "UNH",
    "HD",
    "MA",
    "DIS",
    "PYPL",
    "BAC",
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
    "BAC": ["Bank of America", "BAC"],
}

# PostgreSQL local config
PG_HOST = os.getenv("DB_HOST", "postgres")
PG_DB = os.getenv("DB_NAME", "financial_sentiment")
PG_USER = os.getenv("DB_USER", "postgres")
PG_PASSWORD = os.getenv("DB_PASSWORD", "password")
PG_PORT = int(os.getenv("DB_PORT", "5432"))


def insert_news_pg(news_items):
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD,
            port=PG_PORT,
        )
        cur = conn.cursor()
        for item in news_items:
            cur.execute(
                """
                INSERT INTO news_with_sentiment (title, description, url, published_at, source_name, sentiment_score, sentiment_subjectivity, symbol)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    item.get("title"),
                    item.get("description"),
                    item.get("url"),
                    item.get("published_at"),
                    item.get("source"),
                    item.get("sentiment_score", 0),
                    item.get("sentiment_subjectivity", 0),
                    item.get("symbol"),
                ),
            )
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Inserted {len(news_items)} news items into PostgreSQL")
    except Exception as e:
        logger.error(f"Error inserting news into PostgreSQL: {e}")


def insert_stock_pg(stock_item):
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD,
            port=PG_PORT,
        )
        cur = conn.cursor()
        # Calcular promedios reales de sentimiento y subjetividad desde la base
        cur.execute(
            """
            SELECT AVG(sentiment_score), AVG(sentiment_subjectivity)
            FROM news_with_sentiment
            WHERE symbol = %s AND published_at >= NOW() - INTERVAL '24 hours'
        """,
            (stock_item.get("symbol"),),
        )
        avg_sentiment_score, avg_sentiment_subjectivity = cur.fetchone()
        avg_sentiment_score = avg_sentiment_score or 0
        avg_sentiment_subjectivity = avg_sentiment_subjectivity or 0
        cur.execute(
            """
            INSERT INTO financial_sentiment_correlation (hour, sentiment_category, avg_sentiment_score, avg_sentiment_subjectivity, avg_close_price, max_high_price, min_low_price, total_volume, price_points, price_change_percent, sentiment_change, news_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                datetime.utcnow(),
                "Neutral",
                avg_sentiment_score,
                avg_sentiment_subjectivity,
                stock_item.get("close"),
                stock_item.get("high"),
                stock_item.get("low"),
                stock_item.get("volume"),
                1,
                0,
                0,
                1,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
        logger.info(
            f"Inserted stock item for {stock_item.get('symbol')} into PostgreSQL"
        )
    except Exception as e:
        logger.error(f"Error inserting stock into PostgreSQL: {e}")


class DataIngestionManager:
    """Manages data ingestion from multiple sources."""

    def __init__(self):
        """Initialize the data ingestion manager."""
        self.kinesis_client = boto3.client("kinesis", region_name=AWS_REGION)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Financial-Sentiment-Pipeline/1.0"})

    async def fetch_news_data(self, symbol: str) -> List[Dict]:
        """Fetch news data for a given stock symbol."""
        if not NEWS_API_KEY:
            logger.warning("NEWS_API_KEY not configured, skipping news ingestion")
            return []

        company_names = COMPANY_NAMES.get(symbol, [symbol])
        all_news = []

        for company_name in company_names:
            try:
                # Fetch news from NewsAPI
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": f'"{company_name}" AND (stock OR market OR financial OR earnings)',
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 10,
                    "apiKey": NEWS_API_KEY,
                }

                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()

                if data.get("status") == "ok":
                    articles = data.get("articles", [])

                    for article in articles:
                        # Calcular sentimiento y subjetividad
                        text = (
                            (article.get("title", "") or "")
                            + " "
                            + (article.get("description", "") or "")
                        )
                        blob = TextBlob(text)
                        sentiment_score = blob.sentiment.polarity
                        sentiment_subjectivity = blob.sentiment.subjectivity
                        news_item = {
                            "type": "news",
                            "symbol": symbol,
                            "company_name": company_name,
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "content": article.get("content", ""),
                            "url": article.get("url", ""),
                            "source": article.get("source", {}).get("name", ""),
                            "published_at": article.get("publishedAt", ""),
                            "ingested_at": datetime.utcnow().isoformat(),
                            "sentiment_score": sentiment_score,
                            "sentiment_subjectivity": sentiment_subjectivity,
                        }
                        all_news.append(news_item)

                logger.info(f"Fetched {len(articles)} news articles for {company_name}")

            except requests.RequestException as e:
                logger.error(f"Error fetching news for {company_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching news for {company_name}: {e}")

        return all_news

    async def fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """Fetch stock price data for a given symbol."""
        if not ALPHA_VANTAGE_API_KEY:
            logger.warning(
                "ALPHA_VANTAGE_API_KEY not configured, skipping stock data ingestion"
            )
            return None

        try:
            # Fetch real-time stock data from Alpha Vantage
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": "1min",
                "apikey": ALPHA_VANTAGE_API_KEY,
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Get the latest price data
            time_series = data.get("Time Series (1min)", {})
            if time_series:
                latest_time = max(time_series.keys())
                latest_data = time_series[latest_time]

                stock_item = {
                    "type": "stock_price",
                    "symbol": symbol,
                    "timestamp": latest_time,
                    "open": float(latest_data.get("1. open", 0)),
                    "high": float(latest_data.get("2. high", 0)),
                    "low": float(latest_data.get("3. low", 0)),
                    "close": float(latest_data.get("4. close", 0)),
                    "volume": int(latest_data.get("5. volume", 0)),
                    "ingested_at": datetime.utcnow().isoformat(),
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
                PartitionKey=partition_key,
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
            stock["symbol"] = symbol
            insert_stock_pg(stock)

    async def run_ingestion_cycle(self) -> None:
        """Run a complete ingestion cycle for solo un símbolo (AAPL)."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            symbols = ["AAPL"]  # Solo procesar AAPL
            task = progress.add_task("Ingesting data...", total=len(symbols))
            for symbol in symbols:
                progress.update(task, description=f"Ingesting data for {symbol}...")
                await self.ingest_data_for_symbol(symbol)
                progress.advance(task)
                await asyncio.sleep(1)

    async def run_continuous_ingestion(self, interval_minutes: int = 5) -> None:
        """Run continuous ingestion with specified interval."""
        logger.info(
            f"Starting continuous ingestion with {interval_minutes} minute intervals"
        )

        while True:
            try:
                start_time = time.time()

                await self.run_ingestion_cycle()

                elapsed_time = time.time() - start_time
                sleep_time = max(0, (interval_minutes * 60) - elapsed_time)

                logger.info(
                    f"Ingestion cycle completed in {elapsed_time:.2f}s. Sleeping for {sleep_time:.2f}s"
                )
                await asyncio.sleep(sleep_time)

            except KeyboardInterrupt:
                logger.info("Ingestion stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in ingestion cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying


async def main():
    """Main function to run the data ingestion."""
    console.print("[bold blue]Financial Data Ingestion Pipeline[/bold blue]")
    console.print("=" * 50)

    # Validate configuration
    if not NEWS_API_KEY and not ALPHA_VANTAGE_API_KEY:
        console.print(
            "[red]Error: No API keys configured. Please set NEWS_API_KEY or ALPHA_VANTAGE_API_KEY[/red]"
        )
        return

    if not KINESIS_STREAM_NAME:
        console.print("[red]Error: KINESIS_STREAM_NAME not configured[/red]")
        return

    # Initialize ingestion manager
    ingestion_manager = DataIngestionManager()

    # Check if running in continuous mode
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        await ingestion_manager.run_continuous_ingestion(interval)
    else:
        # Run single ingestion cycle
        await ingestion_manager.run_ingestion_cycle()
        console.print("[green]Ingestion completed successfully![/green]")


if __name__ == "__main__":
    asyncio.run(main())
