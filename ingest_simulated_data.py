#!/usr/bin/env python3
"""
Script para ingestar datos simulados de precios y noticias para probar el sistema.
"""

import random
from datetime import datetime, timedelta
from backend.ingestion_main import insert_news_pg, insert_stock_pg, STOCK_SYMBOLS
import time

def generate_simulated_prices(symbol, days=30):
    """Generar datos simulados de precios para los últimos 'days' días."""
    prices = []
    base_price = random.uniform(50, 500)  # Precio base aleatorio
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        
        # Simular volatilidad diaria
        daily_change = random.uniform(-0.05, 0.05)  # ±5% cambio diario
        base_price *= (1 + daily_change)
        
        # Generar OHLCV
        open_price = base_price
        high_price = open_price * random.uniform(1.0, 1.03)
        low_price = open_price * random.uniform(0.97, 1.0)
        close_price = random.uniform(low_price, high_price)
        volume = random.randint(1000000, 10000000)
        
        stock_item = {
            'symbol': symbol,
            'close': round(close_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'volume': volume,
            'timestamp': date.strftime('%Y-%m-%d')
        }
        prices.append(stock_item)
    
    return prices

def generate_simulated_news(symbol, days=30):
    """Generar datos simulados de noticias para los últimos 'days' días."""
    news_items = []
    
    # Títulos de noticias simuladas
    news_templates = [
        f"{symbol} Reports Strong Quarterly Earnings",
        f"Analysts Upgrade {symbol} Stock Rating",
        f"{symbol} Announces New Product Launch",
        f"Market Reacts to {symbol} CEO Statement",
        f"{symbol} Expands Global Operations",
        f"Investors Bullish on {symbol} Future Prospects",
        f"{symbol} Partners with Major Tech Company",
        f"Regulatory Approval for {symbol} New Initiative",
        f"{symbol} Stock Hits New 52-Week High",
        f"Industry Experts Praise {symbol} Innovation"
    ]
    
    sources = ["Reuters", "Bloomberg", "CNBC", "Wall Street Journal", "Financial Times", "MarketWatch"]
    
    for i in range(days):
        # Generar 1-3 noticias por día
        daily_news_count = random.randint(1, 3)
        
        for _ in range(daily_news_count):
            date = datetime.now() - timedelta(days=i, hours=random.randint(0, 23))
            
            # Generar sentimiento aleatorio
            sentiment_score = random.uniform(-1.0, 1.0)
            sentiment_subjectivity = random.uniform(0.0, 1.0)
            
            news_item = {
                'title': random.choice(news_templates),
                'description': f"Simulated news article about {symbol} for testing purposes.",
                'url': f"https://example.com/news/{symbol.lower()}-{i}",
                'published_at': date.isoformat(),
                'source': random.choice(sources),
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_subjectivity': round(sentiment_subjectivity, 3),
                'symbol': symbol
            }
            news_items.append(news_item)
    
    return news_items

def main():
    """Función principal para generar e insertar datos simulados."""
    print(f"[{datetime.now()}] 🚀 Iniciando ingesta de datos simulados...")
    print(f"📊 Generando datos para {len(STOCK_SYMBOLS)} símbolos")
    print("⚠️  Nota: Estos son datos simulados para pruebas del sistema\n")
    
    total_news = 0
    total_prices = 0
    
    for i, symbol in enumerate(STOCK_SYMBOLS):
        print(f"\n--- {symbol} ({i+1}/{len(STOCK_SYMBOLS)}) ---")
        
        # Generar precios simulados
        try:
            prices = generate_simulated_prices(symbol, days=30)
            print(f"  📈 Precios generados: {len(prices)} días")
            
            # Insertar precios
            for price in prices:
                insert_stock_pg(price)
            total_prices += len(prices)
            print(f"  ✅ Precios insertados correctamente")
            
        except Exception as e:
            print(f"  ❌ Error con precios para {symbol}: {e}")
        
        # Generar noticias simuladas
        try:
            news = generate_simulated_news(symbol, days=30)
            print(f"  📰 Noticias generadas: {len(news)} artículos")
            
            # Insertar noticias
            insert_news_pg(news)
            total_news += len(news)
            print(f"  ✅ Noticias insertadas correctamente")
            
        except Exception as e:
            print(f"  ❌ Error con noticias para {symbol}: {e}")
        
        # Pequeño delay para no sobrecargar la base de datos
        time.sleep(0.5)
    
    print(f"\n🎉 Ingesta de datos simulados completada!")
    print(f"📊 Resumen:")
    print(f"   - Total de precios insertados: {total_prices}")
    print(f"   - Total de noticias insertadas: {total_news}")
    print(f"   - Símbolos procesados: {len(STOCK_SYMBOLS)}")
    print(f"\n[{datetime.now()}] ✅ Sistema probado exitosamente!")

if __name__ == "__main__":
    main() 