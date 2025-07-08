#!/usr/bin/env python3
"""
Ingesta de precios históricos reales usando Yahoo Finance para todos los símbolos.
"""
from backend.ingestion_main import (
    fetch_yahoo_prices,
    insert_historic_prices,
    STOCK_SYMBOLS,
)
from datetime import datetime

all_prices = []
print(
    f"[{datetime.now()}] Iniciando ingesta Yahoo Finance para {len(STOCK_SYMBOLS)} símbolos..."
)

for i, symbol in enumerate(STOCK_SYMBOLS):
    print(f"\n--- {symbol} ({i+1}/{len(STOCK_SYMBOLS)}) ---")
    try:
        prices = fetch_yahoo_prices(symbol, days=30)
        print(f"  Precios obtenidos: {len(prices)}")
        all_prices.extend(prices)
    except Exception as e:
        print(f"  Error obteniendo precios para {symbol}: {e}")

print(f"\nInsertando {len(all_prices)} precios en la base de datos...")
try:
    insert_historic_prices(all_prices)
    print("✅ Precios insertados correctamente.")
except Exception as e:
    print(f"❌ Error insertando precios: {e}")

print(f"\n[{datetime.now()}] Ingesta Yahoo Finance finalizada.")
print(f"Total de registros de precios insertados: {len(all_prices)}")
