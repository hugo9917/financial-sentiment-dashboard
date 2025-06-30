import os
import csv
import time
from datetime import datetime
from typing import List, Dict, Optional
import requests
from textblob import TextBlob
from dotenv import load_dotenv

# Cargar variables de entorno desde .env o config.env
load_dotenv()
if not os.getenv("NEWS_API_KEY"):
    load_dotenv("config.env")

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Debug: mostrar las keys que se están usando (ocultando parte por seguridad)
print(f"NEWS_API_KEY: {NEWS_API_KEY[:8]}..." if NEWS_API_KEY else "NEWS_API_KEY: No encontrada")
print(f"ALPHA_VANTAGE_API_KEY: {ALPHA_VANTAGE_API_KEY[:8]}..." if ALPHA_VANTAGE_API_KEY else "ALPHA_VANTAGE_API_KEY: No encontrada")

STOCK_SYMBOLS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX",
    "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "BAC"
]

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

NEWS_CSV = "news_with_sentiment.csv"
PRICES_CSV = "stock_prices.csv"


def fetch_news(symbol: str) -> List[Dict]:
    if not NEWS_API_KEY:
        print("NEWS_API_KEY not set.")
        return []
    all_news = []
    for company in COMPANY_NAMES.get(symbol, [symbol]):
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': f'"{company}" AND (stock OR market OR financial OR earnings)',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 5,
            'apiKey': NEWS_API_KEY
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            for article in data.get('articles', []):
                text = article.get('title', '') + ' ' + (article.get('description', '') or '')
                sentiment = TextBlob(text).sentiment.polarity if text else 0.0
                all_news.append({
                    'symbol': symbol,
                    'company': company,
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'published_at': article.get('publishedAt', ''),
                    'url': article.get('url', ''),
                    'sentiment': sentiment,
                    'ingested_at': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error fetching news for {company}: {e}")
    return all_news

def fetch_stock_price(symbol: str) -> Optional[Dict]:
    if not ALPHA_VANTAGE_API_KEY:
        print("ALPHA_VANTAGE_API_KEY not set.")
        return None
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '1min',
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        ts = data.get('Time Series (1min)', {})
        if ts:
            latest_time = max(ts.keys())
            latest = ts[latest_time]
            return {
                'symbol': symbol,
                'timestamp': latest_time,
                'open': latest.get('1. open', ''),
                'high': latest.get('2. high', ''),
                'low': latest.get('3. low', ''),
                'close': latest.get('4. close', ''),
                'volume': latest.get('5. volume', ''),
                'ingested_at': datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
    return None

def save_to_csv(filename: str, rows: List[Dict], fieldnames: List[str]):
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    all_news = []
    all_prices = []
    for symbol in STOCK_SYMBOLS:
        print(f"Fetching for {symbol}...")
        news = fetch_news(symbol)
        if news:
            save_to_csv(NEWS_CSV, news, list(news[0].keys()))
            all_news.extend(news)
        price = fetch_stock_price(symbol)
        if price:
            save_to_csv(PRICES_CSV, [price], list(price.keys()))
            all_prices.append(price)
        time.sleep(1)  # Avoid API rate limits
    print(f"Guardado {len(all_news)} noticias y {len(all_prices)} precios.")

if __name__ == "__main__":
    main() 