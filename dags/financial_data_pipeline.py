from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from datetime import datetime, timedelta
import os

# Configuración del DAG
default_args = {
    "owner": "financial-sentiment-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "financial_data_pipeline",
    default_args=default_args,
    description="Pipeline completo de datos financieros y análisis de sentimiento",
    schedule_interval="0 */4 * * *",  # Cada 4 horas
    catchup=False,
    tags=["financial", "sentiment", "data-pipeline"],
)


def ingest_financial_data(**context):
    """
    Función para ingesta de datos financieros desde APIs
    """
    import requests
    import pandas as pd
    import psycopg2
    from datetime import datetime, timedelta
    import os
    import logging

    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Configuración de la base de datos
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "postgres"),
        "database": os.getenv("DB_NAME", "financial_sentiment"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "port": int(os.getenv("DB_PORT", "5432")),
    }

    # Configuración de APIs
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo_key")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "demo_key")

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Obtener noticias financieras
        logger.info("Obteniendo noticias financieras...")

        if NEWS_API_KEY != "demo_key":
            # Usar API real
            symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
            all_news = []

            for symbol in symbols:
                news_url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}&pageSize=10&sortBy=publishedAt"
                response = requests.get(news_url, timeout=30)

                if response.status_code == 200:
                    news_data = response.json()
                    if news_data.get("articles"):
                        for article in news_data["articles"]:
                            article["symbol"] = symbol
                            all_news.append(article)
                else:
                    logger.warning(
                        f"Error obteniendo noticias para {symbol}: {response.status_code}"
                    )
        else:
            # Datos de ejemplo para desarrollo
            all_news = [
                {
                    "title": f'Sample Financial News for AAPL {datetime.now().strftime("%H:%M")}',
                    "description": "This is a sample financial news article for testing purposes.",
                    "publishedAt": datetime.now().isoformat(),
                    "url": "https://example.com",
                    "source": {"name": "Sample News"},
                    "symbol": "AAPL",
                },
                {
                    "title": f'Sample Financial News for MSFT {datetime.now().strftime("%H:%M")}',
                    "description": "Another sample financial news article for testing.",
                    "publishedAt": datetime.now().isoformat(),
                    "url": "https://example.com",
                    "source": {"name": "Sample News"},
                    "symbol": "MSFT",
                },
            ]

        # Obtener precios de acciones
        logger.info("Obteniendo precios de acciones...")

        if ALPHA_VANTAGE_KEY != "demo_key":
            # Usar API real
            symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
            all_stocks = []

            for symbol in symbols:
                stock_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={ALPHA_VANTAGE_KEY}"
                response = requests.get(stock_url, timeout=30)

                if response.status_code == 200:
                    stock_data = response.json()
                    if "Time Series (1min)" in stock_data:
                        for timestamp, values in stock_data[
                            "Time Series (1min)"
                        ].items():
                            values["symbol"] = symbol
                            values["timestamp"] = timestamp
                            all_stocks.append(values)
                else:
                    logger.warning(
                        f"Error obteniendo precios para {symbol}: {response.status_code}"
                    )
        else:
            # Datos de ejemplo para desarrollo
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            all_stocks = [
                {
                    "1. open": "150.00",
                    "2. high": "151.00",
                    "3. low": "149.00",
                    "4. close": "150.50",
                    "5. volume": "1000000",
                    "symbol": "AAPL",
                    "timestamp": current_time,
                },
                {
                    "1. open": "340.00",
                    "2. high": "342.00",
                    "3. low": "339.00",
                    "4. close": "341.50",
                    "5. volume": "800000",
                    "symbol": "MSFT",
                    "timestamp": current_time,
                },
            ]

        # Guardar noticias en la base de datos
        logger.info("Guardando noticias en la base de datos...")
        for news in all_news:
            cursor.execute(
                """
                INSERT INTO news_with_sentiment (title, description, url, published_at, source_name, symbol)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
            """,
                (
                    news.get("title", ""),
                    news.get("description", ""),
                    news.get("url", ""),
                    datetime.fromisoformat(news["publishedAt"].replace("Z", "+00:00")),
                    news.get("source", {}).get("name", "Unknown"),
                    news.get("symbol", "UNKNOWN"),
                ),
            )

        # Guardar precios en la base de datos
        logger.info("Guardando precios en la base de datos...")
        for stock in all_stocks:
            cursor.execute(
                """
                INSERT INTO stock_prices (symbol, timestamp, open_price, high_price, low_price, close_price, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, timestamp) DO NOTHING
            """,
                (
                    stock["symbol"],
                    datetime.strptime(stock["timestamp"], "%Y-%m-%d %H:%M:%S"),
                    float(stock["1. open"]),
                    float(stock["2. high"]),
                    float(stock["3. low"]),
                    float(stock["4. close"]),
                    int(stock["5. volume"]),
                ),
            )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(
            f"Pipeline completado: {len(all_news)} noticias, {len(all_stocks)} precios"
        )
        return f"Data ingested successfully: {len(all_news)} news, {len(all_stocks)} stock prices"

    except Exception as e:
        logger.error(f"Error in data ingestion: {str(e)}")
        raise


def process_sentiment(**context):
    """
    Función para procesar análisis de sentimiento usando TextBlob
    """
    import psycopg2
    import pandas as pd
    from textblob import TextBlob
    from datetime import datetime
    import os
    import logging

    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Configuración de la base de datos
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "postgres"),
        "database": os.getenv("DB_NAME", "financial_sentiment"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "port": int(os.getenv("DB_PORT", "5432")),
    }

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Obtener noticias sin análisis de sentimiento
        cursor.execute(
            """
            SELECT id, title, description 
            FROM news_with_sentiment 
            WHERE sentiment_score IS NULL
            ORDER BY published_at DESC
            LIMIT 100
        """
        )

        news_to_process = cursor.fetchall()
        logger.info(f"Procesando sentimiento para {len(news_to_process)} noticias")

        for news_id, title, description in news_to_process:
            # Combinar título y descripción para análisis
            text = f"{title} {description}"

            # Análisis de sentimiento con TextBlob
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity
            sentiment_subjectivity = blob.sentiment.subjectivity

            # Actualizar la base de datos
            cursor.execute(
                """
                UPDATE news_with_sentiment 
                SET sentiment_score = %s, sentiment_subjectivity = %s
                WHERE id = %s
            """,
                (sentiment_score, sentiment_subjectivity, news_id),
            )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(
            f"Análisis de sentimiento completado para {len(news_to_process)} noticias"
        )
        return f"Sentiment analysis completed for {len(news_to_process)} articles"

    except Exception as e:
        logger.error(f"Error in sentiment processing: {str(e)}")
        raise


def update_correlation_table(**context):
    """
    Función para actualizar la tabla de correlación
    """
    import psycopg2
    from datetime import datetime, timedelta
    import os
    import logging

    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Configuración de la base de datos
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "postgres"),
        "database": os.getenv("DB_NAME", "financial_sentiment"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "port": int(os.getenv("DB_PORT", "5432")),
    }

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Obtener datos de las últimas 24 horas
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)

        # Agrupar por hora y calcular promedios
        cursor.execute(
            """
            INSERT INTO financial_sentiment_correlation (
                hour, symbol, avg_sentiment_score, avg_sentiment_subjectivity,
                avg_close_price, max_high_price, min_low_price, total_volume,
                news_count, price_points
            )
            SELECT 
                DATE_TRUNC('hour', n.published_at) as hour,
                n.symbol,
                AVG(n.sentiment_score) as avg_sentiment_score,
                AVG(n.sentiment_subjectivity) as avg_sentiment_subjectivity,
                AVG(s.close_price) as avg_close_price,
                MAX(s.high_price) as max_high_price,
                MIN(s.low_price) as min_low_price,
                SUM(s.volume) as total_volume,
                COUNT(DISTINCT n.id) as news_count,
                COUNT(s.id) as price_points
            FROM news_with_sentiment n
            LEFT JOIN stock_prices s ON n.symbol = s.symbol 
                AND DATE_TRUNC('hour', n.published_at) = DATE_TRUNC('hour', s.timestamp)
            WHERE n.published_at BETWEEN %s AND %s
                AND n.sentiment_score IS NOT NULL
            GROUP BY DATE_TRUNC('hour', n.published_at), n.symbol
            ON CONFLICT (hour, symbol) DO UPDATE SET
                avg_sentiment_score = EXCLUDED.avg_sentiment_score,
                avg_sentiment_subjectivity = EXCLUDED.avg_sentiment_subjectivity,
                avg_close_price = EXCLUDED.avg_close_price,
                max_high_price = EXCLUDED.max_high_price,
                min_low_price = EXCLUDED.min_low_price,
                total_volume = EXCLUDED.total_volume,
                news_count = EXCLUDED.news_count,
                price_points = EXCLUDED.price_points
        """,
            (start_time, end_time),
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("Tabla de correlación actualizada")
        return "Correlation table updated successfully"

    except Exception as e:
        logger.error(f"Error updating correlation table: {str(e)}")
        raise


def validate_data_quality(**context):
    """
    Función para validar la calidad de los datos
    """
    import psycopg2
    from datetime import datetime, timedelta
    import os
    import logging

    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Configuración de la base de datos
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "postgres"),
        "database": os.getenv("DB_NAME", "financial_sentiment"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "port": int(os.getenv("DB_PORT", "5432")),
    }

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Validaciones
        issues = []

        # Verificar noticias recientes
        cursor.execute(
            """
            SELECT COUNT(*) FROM news_with_sentiment 
            WHERE published_at >= NOW() - INTERVAL '4 hours'
        """
        )
        recent_news = cursor.fetchone()[0]

        if recent_news < 10:
            issues.append(f"Pocas noticias recientes: {recent_news}")

        # Verificar precios recientes
        cursor.execute(
            """
            SELECT COUNT(*) FROM stock_prices 
            WHERE timestamp >= NOW() - INTERVAL '4 hours'
        """
        )
        recent_prices = cursor.fetchone()[0]

        if recent_prices < 50:
            issues.append(f"Pocos precios recientes: {recent_prices}")

        # Verificar análisis de sentimiento
        cursor.execute(
            """
            SELECT COUNT(*) FROM news_with_sentiment 
            WHERE sentiment_score IS NULL
        """
        )
        pending_sentiment = cursor.fetchone()[0]

        if pending_sentiment > 0:
            issues.append(f"Noticias pendientes de análisis: {pending_sentiment}")

        cursor.close()
        conn.close()

        if issues:
            logger.warning(f"Problemas de calidad detectados: {', '.join(issues)}")
            return f"Data quality issues: {', '.join(issues)}"
        else:
            logger.info("Validación de calidad exitosa")
            return "Data quality validation passed"

    except Exception as e:
        logger.error(f"Error in data quality validation: {str(e)}")
        raise


# Definir tareas
ingest_task = PythonOperator(
    task_id="ingest_financial_data", python_callable=ingest_financial_data, dag=dag
)

sentiment_task = PythonOperator(
    task_id="process_sentiment", python_callable=process_sentiment, dag=dag
)

correlation_task = PythonOperator(
    task_id="update_correlation_table",
    python_callable=update_correlation_table,
    dag=dag,
)

validation_task = PythonOperator(
    task_id="validate_data_quality", python_callable=validate_data_quality, dag=dag
)

# Tarea para mostrar información del pipeline
info_task = BashOperator(
    task_id="pipeline_info",
    bash_command='echo "Financial Data Pipeline completed successfully at $(date)"',
    dag=dag,
)

# Definir dependencias
ingest_task >> sentiment_task >> correlation_task >> validation_task >> info_task
