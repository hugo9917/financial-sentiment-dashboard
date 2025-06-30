#!/usr/bin/env python3
"""
Script rápido para poblar la base de datos con datos reales.
Se ejecuta desde dentro del contenedor de backend.
"""

import os
import requests
import logging
from datetime import datetime, timedelta
import psycopg2
import yfinance as yf

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'postgres',
    'database': 'financial_sentiment',
    'user': 'postgres',
    'password': 'password',
    'port': 5432
}

# Símbolos para poblar (solo los más importantes)
STOCK_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "TSLA", "META"]

def get_db_connection():
    """Crear conexión a PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Error de conexión a BD: {e}")
        return None

def fetch_alpha_vantage_news(symbol):
    """Obtener noticias reales de Alpha Vantage."""
    api_key = "[REDACTED]"  # Tu clave de Alpha Vantage
    
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': symbol,
        'topics': 'technology,earnings',
        'limit': 10,
        'apikey': api_key
    }
    
    try:
        logger.info(f"Obteniendo noticias para {symbol}...")
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if 'feed' in data:
            articles = data['feed']
            logger.info(f"Encontradas {len(articles)} noticias para {symbol}")
            
            news_items = []
            for article in articles:
                sentiment_score = float(article.get('overall_sentiment_score', 0))
                
                news_item = {
                    'symbol': symbol,
                    'title': article.get('title', ''),
                    'description': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', ''),
                    'published_at': article.get('time_published', ''),
                    'sentiment_score': sentiment_score,
                    'sentiment_subjectivity': 0.5
                }
                news_items.append(news_item)
            
            return news_items
        else:
            logger.warning(f"No se encontraron noticias para {symbol}")
            return []
            
    except Exception as e:
        logger.error(f"Error obteniendo noticias para {symbol}: {e}")
        return []

def fetch_yahoo_prices(symbol, days=30):
    """Obtener precios reales de Yahoo Finance."""
    try:
        logger.info(f"Obteniendo precios para {symbol}...")
        end = datetime.now()
        start = end - timedelta(days=days)
        
        df = yf.download(symbol, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
        
        if df.empty:
            logger.warning(f"No se obtuvieron precios para {symbol}")
            return []
        
        prices = []
        for date, row in df.iterrows():
            price_item = {
                'symbol': symbol,
                'timestamp': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume']),
            }
            prices.append(price_item)
        
        logger.info(f"Obtenidos {len(prices)} precios para {symbol}")
        return prices
        
    except Exception as e:
        logger.error(f"Error obteniendo precios para {symbol}: {e}")
        return []

def insert_news_to_db(news_items, conn):
    """Insertar noticias en la base de datos."""
    if not news_items:
        return 0
    
    cursor = conn.cursor()
    inserted = 0
    
    for item in news_items:
        try:
            cursor.execute("""
                INSERT INTO news_with_sentiment 
                (symbol, title, description, url, source_name, published_at, sentiment_score, sentiment_subjectivity, ingested_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                item['symbol'],
                item['title'],
                item['description'],
                item['url'],
                item['source'],
                item['published_at'],
                item['sentiment_score'],
                item['sentiment_subjectivity'],
                datetime.utcnow().isoformat()
            ))
            inserted += 1
        except Exception as e:
            logger.error(f"Error insertando noticia: {e}")
    
    conn.commit()
    cursor.close()
    return inserted

def insert_prices_to_db(price_items, conn):
    """Insertar precios en la base de datos."""
    if not price_items:
        return 0
    
    cursor = conn.cursor()
    inserted = 0
    
    for item in price_items:
        try:
            cursor.execute("""
                INSERT INTO stock_prices 
                (symbol, timestamp, open, high, low, close, volume, ingested_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                item['symbol'],
                item['timestamp'],
                item['open'],
                item['high'],
                item['low'],
                item['close'],
                item['volume'],
                datetime.utcnow().isoformat()
            ))
            inserted += 1
        except Exception as e:
            logger.error(f"Error insertando precio: {e}")
    
    conn.commit()
    cursor.close()
    return inserted

def main():
    """Función principal."""
    logger.info("🚀 Iniciando población rápida de base de datos...")
    
    # Conectar a la base de datos
    conn = get_db_connection()
    if not conn:
        logger.error("❌ No se pudo conectar a la base de datos")
        return
    
    total_news = 0
    total_prices = 0
    
    for symbol in STOCK_SYMBOLS:
        logger.info(f"\n--- Procesando {symbol} ---")
        
        # Obtener noticias
        news_items = fetch_alpha_vantage_news(symbol)
        if news_items:
            inserted_news = insert_news_to_db(news_items, conn)
            total_news += inserted_news
            logger.info(f"✅ Insertadas {inserted_news} noticias para {symbol}")
        
        # Obtener precios
        price_items = fetch_yahoo_prices(symbol)
        if price_items:
            inserted_prices = insert_prices_to_db(price_items, conn)
            total_prices += inserted_prices
            logger.info(f"✅ Insertados {inserted_prices} precios para {symbol}")
    
    conn.close()
    
    logger.info(f"\n🎉 Población completada!")
    logger.info(f"📰 Total noticias insertadas: {total_news}")
    logger.info(f"📈 Total precios insertados: {total_prices}")

if __name__ == "__main__":
    main() 