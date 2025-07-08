#!/usr/bin/env python3
"""
Script para probar la ingesta de noticias usando Alpha Vantage News API.
"""

import os
import sys
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from textblob import TextBlob

# Agregar el directorio backend al path para importar las funciones
sys.path.append("backend")

# Cargar variables de entorno
load_dotenv("config.env")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Configuración
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Símbolos para probar
TEST_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "TSLA"]


def test_alpha_vantage_news_api():
    """Probar la API de noticias de Alpha Vantage."""
    if not ALPHA_VANTAGE_API_KEY:
        logger.error("ALPHA_VANTAGE_API_KEY no está configurada")
        return

    logger.info(
        f"Probando Alpha Vantage News API con key: {ALPHA_VANTAGE_API_KEY[:10]}..."
    )

    for symbol in TEST_SYMBOLS:
        logger.info(f"\n--- {symbol} ---")

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol,
            "topics": "technology,earnings,ipo,mearnings",
            "limit": 5,  # Solo 5 noticias para la prueba
            "apikey": ALPHA_VANTAGE_API_KEY,
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            logger.info(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                if "feed" in data:
                    articles = data["feed"]
                    logger.info(
                        f"✅ Encontradas {len(articles)} noticias para {symbol}"
                    )

                    for i, article in enumerate(
                        articles[:3], 1
                    ):  # Mostrar solo las primeras 3
                        title = article.get("title", "Sin título")
                        sentiment_score = article.get("overall_sentiment_score", "N/A")
                        sentiment_label = article.get("overall_sentiment_label", "N/A")
                        source = article.get("source", "N/A")
                        time_published = article.get("time_published", "N/A")

                        logger.info(f"  {i}. {title[:60]}...")
                        logger.info(
                            f"     Sentimiento: {sentiment_score} ({sentiment_label})"
                        )
                        logger.info(f"     Fuente: {source}")
                        logger.info(f"     Fecha: {time_published}")
                else:
                    logger.warning(f"❌ No se encontraron noticias para {symbol}")
                    logger.info(f"Response: {data}")
            else:
                logger.error(f"❌ Error HTTP: {response.status_code}")
                logger.error(f"Response: {response.text}")

        except Exception as e:
            logger.error(f"❌ Error al obtener noticias para {symbol}: {e}")


def test_alpha_vantage_news_ingestion():
    """Probar la ingesta completa de noticias."""
    if not ALPHA_VANTAGE_API_KEY:
        logger.error("ALPHA_VANTAGE_API_KEY no está configurada")
        return

    logger.info("\n" + "=" * 50)
    logger.info("PROBANDO INGESTA COMPLETA DE NOTICIAS")
    logger.info("=" * 50)

    # Importar las funciones de ingesta
    from backend.ingestion_main import fetch_historic_news, insert_historic_news

    total_news = 0

    for symbol in TEST_SYMBOLS:
        logger.info(f"\n--- {symbol} ---")
        try:
            news = fetch_historic_news(symbol, months=1)  # Solo 1 mes para la prueba
            logger.info(f"Noticias obtenidas: {len(news)}")

            if news:
                # Mostrar algunas noticias de ejemplo
                for i, item in enumerate(news[:2], 1):
                    logger.info(f"  {i}. {item['title'][:50]}...")
                    logger.info(f"     Sentimiento: {item['sentiment_score']}")

                # Insertar en la base de datos
                insert_historic_news(news)
                logger.info("✅ Noticias insertadas correctamente")
                total_news += len(news)
            else:
                logger.warning("No se obtuvieron noticias")

        except Exception as e:
            logger.error(f"Error procesando {symbol}: {e}")

    logger.info(f"\n{'='*50}")
    logger.info(f"INGESTA COMPLETADA")
    logger.info(f"Total de noticias insertadas: {total_news}")
    logger.info(f"{'='*50}")


if __name__ == "__main__":
    print("🚀 Iniciando pruebas de Alpha Vantage News API...\n")

    # Prueba 1: Verificar que la API funciona
    test_alpha_vantage_news_api()

    # Prueba 2: Probar la ingesta completa
    test_alpha_vantage_news_ingestion()

    print("\n✨ Pruebas completadas.")
