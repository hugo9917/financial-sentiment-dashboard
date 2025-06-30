import csv
import random
from datetime import datetime, timedelta
import os

def generate_sample_data():
    """Genera datos de ejemplo para probar el dashboard."""
    
    # Datos de ejemplo para noticias
    sample_news = [
        "Apple reports strong quarterly earnings",
        "Google faces antitrust investigation",
        "Microsoft cloud services grow rapidly",
        "Amazon expands into new markets",
        "Tesla announces new electric vehicle",
        "Meta launches new social media features",
        "NVIDIA chip demand surges",
        "Netflix subscriber growth slows",
        "JPMorgan beats profit expectations",
        "Johnson & Johnson vaccine approved",
        "Visa reports record transaction volume",
        "Procter & Gamble raises prices",
        "UnitedHealth expands coverage",
        "Home Depot sales increase",
        "Mastercard partners with fintech",
        "Disney streaming service grows",
        "PayPal introduces new features",
        "Bank of America reports strong quarter"
    ]
    
    # Datos de ejemplo para precios (valores realistas)
    base_prices = {
        "AAPL": 150.0, "GOOGL": 2800.0, "MSFT": 300.0, "AMZN": 3300.0,
        "TSLA": 800.0, "META": 300.0, "NVDA": 200.0, "NFLX": 500.0,
        "JPM": 150.0, "JNJ": 170.0, "V": 250.0, "PG": 140.0,
        "UNH": 400.0, "HD": 300.0, "MA": 350.0, "DIS": 180.0,
        "PYPL": 250.0, "BAC": 40.0
    }
    
    # Generar noticias con sentimiento
    news_data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for symbol in base_prices.keys():
        for i in range(10):  # 10 noticias por símbolo
            date = start_date + timedelta(days=random.randint(0, 30))
            sentiment = random.uniform(-1, 1)  # Sentimiento entre -1 y 1
            
            news_data.append({
                'symbol': symbol,
                'company': symbol,
                'title': f"{sample_news[random.randint(0, len(sample_news)-1)]} - {symbol}",
                'description': f"Financial news about {symbol} company performance and market trends.",
                'published_at': date.isoformat(),
                'url': f"https://example.com/news/{symbol}_{i}",
                'sentiment': round(sentiment, 3),
                'ingested_at': datetime.now().isoformat()
            })
    
    # Generar precios de acciones
    prices_data = []
    for symbol, base_price in base_prices.items():
        for i in range(20):  # 20 puntos de precio por símbolo
            date = start_date + timedelta(hours=random.randint(0, 720))  # 30 días * 24 horas
            price_change = random.uniform(-0.1, 0.1)  # ±10% cambio
            current_price = base_price * (1 + price_change)
            
            prices_data.append({
                'symbol': symbol,
                'timestamp': date.isoformat(),
                'open': round(current_price * 0.99, 2),
                'high': round(current_price * 1.02, 2),
                'low': round(current_price * 0.98, 2),
                'close': round(current_price, 2),
                'volume': random.randint(1000000, 10000000),
                'ingested_at': datetime.now().isoformat()
            })
    
    # Guardar en CSV
    if news_data:
        with open('news_with_sentiment.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=news_data[0].keys())
            writer.writeheader()
            writer.writerows(news_data)
        print(f"Generados {len(news_data)} registros de noticias en news_with_sentiment.csv")
    
    if prices_data:
        with open('stock_prices.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=prices_data[0].keys())
            writer.writeheader()
            writer.writerows(prices_data)
        print(f"Generados {len(prices_data)} registros de precios en stock_prices.csv")

if __name__ == "__main__":
    generate_sample_data() 