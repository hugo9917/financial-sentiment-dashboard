#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el estado de las APIs.
"""

import requests
import os
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv("config.env")

# Configuración de APIs
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def test_alpha_vantage():
    """Probar la API de Alpha Vantage con un símbolo simple."""
    print("🔍 Probando Alpha Vantage API...")
    print(f"API Key: {ALPHA_VANTAGE_API_KEY[:10]}..." if ALPHA_VANTAGE_API_KEY else "❌ No API key configurada")
    
    if not ALPHA_VANTAGE_API_KEY:
        print("❌ ALPHA_VANTAGE_API_KEY no está configurada en config.env")
        return
    
    # Probar con AAPL
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': 'AAPL',
        'outputsize': 'compact',  # Solo últimos 100 días para ser más rápido
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        print("📡 Haciendo request a Alpha Vantage...")
        response = requests.get(url, params=params, timeout=20)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response recibida correctamente")
            
            # Verificar si hay datos
            time_series = data.get('Time Series (Daily)', {})
            if time_series:
                print(f"✅ Datos encontrados: {len(time_series)} días")
                # Mostrar el primer día como ejemplo
                first_date = list(time_series.keys())[0]
                first_data = time_series[first_date]
                print(f"📊 Ejemplo - {first_date}: Close=${first_data.get('4. close', 'N/A')}")
            else:
                print("❌ No se encontraron datos de precios")
                print("📄 Response completa:")
                print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_news_api():
    """Probar la API de NewsAPI."""
    print("\n🔍 Probando NewsAPI...")
    print(f"API Key: {NEWS_API_KEY[:10]}..." if NEWS_API_KEY else "❌ No API key configurada")
    
    if not NEWS_API_KEY:
        print("❌ NEWS_API_KEY no está configurada en config.env")
        return
    
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': 'AAPL',
        'language': 'en',
        'pageSize': 5,
        'apiKey': NEWS_API_KEY
    }
    
    try:
        print("📡 Haciendo request a NewsAPI...")
        response = requests.get(url, params=params, timeout=20)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response recibida correctamente")
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                print(f"✅ Artículos encontrados: {len(articles)}")
            else:
                print(f"❌ Error en response: {data}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def check_config():
    """Verificar la configuración."""
    print("🔧 Verificando configuración...")
    print(f"ALPHA_VANTAGE_API_KEY: {'✅ Configurada' if ALPHA_VANTAGE_API_KEY else '❌ No configurada'}")
    print(f"NEWS_API_KEY: {'✅ Configurada' if NEWS_API_KEY else '❌ No configurada'}")
    
    if ALPHA_VANTAGE_API_KEY:
        print(f"   Alpha Vantage Key: {ALPHA_VANTAGE_API_KEY[:10]}...")
    if NEWS_API_KEY:
        print(f"   NewsAPI Key: {NEWS_API_KEY[:10]}...")

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de APIs...\n")
    check_config()
    test_alpha_vantage()
    test_news_api()
    print("\n✨ Diagnóstico completado.") 