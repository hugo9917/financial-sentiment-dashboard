#!/usr/bin/env python3
"""
Script para cargar datos existentes de CSV a la base de datos PostgreSQL.
"""

import pandas as pd
import psycopg2
import logging
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",  # Desde fuera del contenedor
    "database": "financial_sentiment",
    "user": "postgres",
    "password": os.getenv(
        "DB_PASSWORD", "password"
    ),  # Debe coincidir con docker-compose
    "port": 5432,
}


def get_db_connection():
    """Crear conexión a PostgreSQL."""
    try:
        print(f"🔍 Intentando conectar a PostgreSQL...")
        print(f"   Host: {DB_CONFIG['host']}")
        print(f"   Puerto: {DB_CONFIG['port']}")
        print(f"   Base: {DB_CONFIG['database']}")
        print(f"   Usuario: {DB_CONFIG['user']}")

        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexión exitosa!")
        return conn
    except Exception as e:
        print(f"❌ Error de conexión a BD: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        return None


def load_stock_prices():
    """Cargar precios de acciones desde CSV."""
    try:
        logger.info("📈 Cargando precios de acciones...")
        df = pd.read_csv("stock_prices.csv")

        conn = get_db_connection()
        if not conn:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for _, row in df.iterrows():
            try:
                cursor.execute(
                    """
                    INSERT INTO stock_prices 
                    (symbol, timestamp, open, high, low, close, volume, ingested_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """,
                    (
                        row["symbol"],
                        row["timestamp"],
                        float(row["open"]),
                        float(row["high"]),
                        float(row["low"]),
                        float(row["close"]),
                        int(row["volume"]),
                        datetime.utcnow().isoformat(),
                    ),
                )
                inserted += 1
            except Exception as e:
                logger.error(f"Error insertando precio: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✅ Insertados {inserted} precios de acciones")
        return inserted

    except Exception as e:
        logger.error(f"Error cargando precios: {e}")
        return 0


def load_news_data():
    """Cargar noticias desde CSV."""
    try:
        logger.info("📰 Cargando noticias...")
        df = pd.read_csv("news_with_sentiment.csv")

        conn = get_db_connection()
        if not conn:
            return 0

        cursor = conn.cursor()
        inserted = 0

        for _, row in df.iterrows():
            try:
                cursor.execute(
                    """
                    INSERT INTO news_with_sentiment 
                    (symbol, title, description, url, source_name, published_at, sentiment_score, sentiment_subjectivity, ingested_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """,
                    (
                        row["symbol"],
                        row["title"],
                        row["description"],
                        row["url"],
                        row["source_name"],
                        row["published_at"],
                        float(row["sentiment_score"]),
                        float(row["sentiment_subjectivity"]),
                        datetime.utcnow().isoformat(),
                    ),
                )
                inserted += 1
            except Exception as e:
                logger.error(f"Error insertando noticia: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✅ Insertadas {inserted} noticias")
        return inserted

    except Exception as e:
        logger.error(f"Error cargando noticias: {e}")
        return 0


def main():
    """Función principal."""
    logger.info("🚀 Iniciando carga de datos existentes...")

    # Cargar precios
    prices_count = load_stock_prices()

    # Cargar noticias
    news_count = load_news_data()

    logger.info(f"\n🎉 Carga completada!")
    logger.info(f"📈 Precios cargados: {prices_count}")
    logger.info(f"📰 Noticias cargadas: {news_count}")
    logger.info(f"\n🌐 Dashboard disponible en: http://localhost:3000")


if __name__ == "__main__":
    main()
