#!/usr/bin/env python3
"""
Ingesta de noticias reales usando NewsAPI para todos los símbolos.
"""
from backend.ingestion_main import fetch_historic_news, insert_historic_news, STOCK_SYMBOLS
from datetime import datetime

all_news = []
print(f"[{datetime.now()}] Iniciando ingesta de noticias reales (NewsAPI) para {len(STOCK_SYMBOLS)} símbolos...")

for i, symbol in enumerate(STOCK_SYMBOLS):
    print(f"\n--- {symbol} ({i+1}/{len(STOCK_SYMBOLS)}) ---")
    try:
        news = fetch_historic_news(symbol, months=1)  # NewsAPI solo permite 30 días atrás
        print(f"  Noticias obtenidas: {len(news)}")
        all_news.extend(news)
    except Exception as e:
        print(f"  Error obteniendo noticias para {symbol}: {e}")

print(f"\nInsertando {len(all_news)} noticias en la base de datos...")
try:
    insert_historic_news(all_news)
    print("✅ Noticias insertadas correctamente.")
except Exception as e:
    print(f"❌ Error insertando noticias: {e}")

print(f"\n[{datetime.now()}] Ingesta de noticias reales finalizada.")
print(f"Total de noticias insertadas: {len(all_news)}") 