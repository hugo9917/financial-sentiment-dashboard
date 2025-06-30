#!/usr/bin/env python3
"""
Ingesta de precios históricos de los últimos 30 días para todos los símbolos.
"""

from backend.ingestion_main import fetch_historic_prices, insert_historic_prices, STOCK_SYMBOLS
from datetime import datetime
import time

all_prices = []

print(f"[{datetime.now()}] Iniciando ingesta de precios de los últimos 30 días para {len(STOCK_SYMBOLS)} símbolos...")
print("⚠️  Nota: Alpha Vantage tiene un límite de 5 requests por minuto en el plan gratuito.")
print("   El script agregará delays de 12 segundos entre cada símbolo para respetar el límite.\n")

for i, symbol in enumerate(STOCK_SYMBOLS):
    print(f"\n--- {symbol} ({i+1}/{len(STOCK_SYMBOLS)}) ---")
    
    # Precios
    try:
        prices = fetch_historic_prices(symbol, months=1)
        print(f"  Precios obtenidos: {len(prices)}")
        all_prices.extend(prices)
        
        # Agregar delay para respetar el límite de la API (5 requests/min = 12 segundos entre requests)
        if i < len(STOCK_SYMBOLS) - 1:  # No esperar después del último símbolo
            print(f"  Esperando 12 segundos antes del siguiente símbolo...")
            time.sleep(12)
            
    except Exception as e:
        print(f"  Error obteniendo precios para {symbol}: {e}")
        # Aún así esperar para no sobrecargar la API
        if i < len(STOCK_SYMBOLS) - 1:
            print(f"  Esperando 12 segundos antes del siguiente símbolo...")
            time.sleep(12)

# Insertar en la base de datos
print(f"\nInsertando {len(all_prices)} precios...")
try:
    insert_historic_prices(all_prices)
    print("✅ Precios insertados correctamente.")
except Exception as e:
    print(f"❌ Error insertando precios: {e}")

print(f"\n[{datetime.now()}] Ingesta de precios finalizada.")
print(f"Total de registros de precios insertados: {len(all_prices)}")
print(f"Tiempo estimado total: ~{len(STOCK_SYMBOLS) * 12 / 60:.1f} minutos") 