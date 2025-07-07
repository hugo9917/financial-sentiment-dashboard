import asyncio
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

import boto3
import pandas as pd
import psycopg2
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from auth import (authenticate_user, create_access_token,
                  get_current_active_user, require_role)
from rate_limiting_middleware import create_rate_limiting_middleware

# Configurar logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)
logger = logging.getLogger(__name__)

# Configurar CloudWatch para métricas (si estamos en AWS)
cloudwatch = None
try:
    cloudwatch = boto3.client(
        "cloudwatch", region_name=os.getenv("AWS_REGION", "us-east-1")
    )
except Exception as e:
    logger.warning(f"CloudWatch no disponible: {e}")


# Métricas de la aplicación
class MetricsCollector:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.db_connection_errors = 0
        self.api_response_times = []

    def increment_request(self):
        self.request_count += 1

    def increment_error(self):
        self.error_count += 1

    def increment_db_error(self):
        self.db_connection_errors += 1

    def record_response_time(self, duration):
        self.api_response_times.append(duration)
        if len(self.api_response_times) > 100:  # Mantener solo las últimas 100
            self.api_response_times.pop(0)

    def get_avg_response_time(self):
        if not self.api_response_times:
            return 0
        return sum(self.api_response_times) / len(self.api_response_times)

    def send_metrics_to_cloudwatch(self):
        if not cloudwatch:
            return

        try:
            cloudwatch.put_metric_data(
                Namespace="FinancialSentiment/API",
                MetricData=[
                    {
                        "MetricName": "RequestCount",
                        "Value": self.request_count,
                        "Unit": "Count",
                    },
                    {
                        "MetricName": "ErrorCount",
                        "Value": self.error_count,
                        "Unit": "Count",
                    },
                    {
                        "MetricName": "DBConnectionErrors",
                        "Value": self.db_connection_errors,
                        "Unit": "Count",
                    },
                    {
                        "MetricName": "AverageResponseTime",
                        "Value": self.get_avg_response_time(),
                        "Unit": "Milliseconds",
                    },
                ],
            )
            # Reset counters after sending
            self.request_count = 0
            self.error_count = 0
            self.db_connection_errors = 0
        except Exception as e:
            logger.error(f"Error sending metrics to CloudWatch: {e}")


metrics = MetricsCollector()

# Background task para enviar métricas cada 5 minutos


async def send_metrics_periodically():
    while True:
        await asyncio.sleep(300)  # 5 minutes
        metrics.send_metrics_to_cloudwatch()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Financial Sentiment API")
    asyncio.create_task(send_metrics_periodically())
    yield
    # Shutdown
    logger.info("Shutting down Financial Sentiment API")


app = FastAPI(
    title="Financial Sentiment API",
    description="API para análisis de sentimiento financiero y correlación con precios",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Middleware para logging y métricas
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
    )

    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Log response
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": round(duration, 2),
            },
        )

        # Record metrics
        metrics.increment_request()
        metrics.record_response_time(duration)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(round(duration, 2))

        return response

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
                "duration_ms": round(duration, 2),
            },
        )
        metrics.increment_error()
        raise


# Configurar CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middleware de rate limiting personalizado
rate_limiting_middleware = create_rate_limiting_middleware(limiter)
app.middleware("http")(rate_limiting_middleware)

# Configuración de la base de datos desde variables de entorno
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "database": os.getenv("DB_NAME", "financial_sentiment"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "port": int(os.getenv("DB_PORT", "5432")),
}


def get_db_connection():
    """Crear conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.debug("Database connection established successfully")
        return conn
    except Exception as e:
        logger.error(
            f"Database connection error: {str(e)}",
            extra={
                "error_type": "database_connection",
                "db_host": DB_CONFIG.get("host"),
                "db_name": DB_CONFIG.get("database"),
            },
        )
        metrics.increment_db_error()
        # Para desarrollo, devolver datos de ejemplo si no hay BD
        return None


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Financial Sentiment API v1.0.0", "status": "running"}


@app.post("/auth/login")
@limiter.limit("5/minute")  # Máximo 5 intentos por minuto
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint de login"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    logger.info(f"User {user['username']} logged in successfully")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
        },
    }


@app.get("/auth/me")
async def get_current_user_info(current_user=Depends(get_current_active_user)):
    """Obtener información del usuario actual"""
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
    }


@app.get("/auth/protected")
async def protected_route(current_user=Depends(get_current_active_user)):
    """Ruta protegida de ejemplo"""
    return {"message": "This is a protected route", "user": current_user["username"]}


@app.get("/auth/admin")
async def admin_route(current_user=Depends(require_role("admin"))):
    """Ruta solo para administradores"""
    return {"message": "Admin only route", "user": current_user["username"]}


@app.get("/health")
async def health_check():
    """Verificar estado de la API y base de datos"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            logger.info("Health check passed - database connected")
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
            }
        else:
            logger.warning("Health check - database disconnected, using sample data")
            return {
                "status": "healthy",
                "database": "disconnected",
                "message": "Using sample data",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "message": "Using sample data",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }


@app.get("/metrics")
@limiter.limit("30/minute")  # Máximo 30 requests por minuto
async def get_metrics(request: Request):
    """Obtener métricas de la aplicación"""
    return {
        "request_count": metrics.request_count,
        "error_count": metrics.error_count,
        "db_connection_errors": metrics.db_connection_errors,
        "average_response_time_ms": round(metrics.get_avg_response_time(), 2),
        "uptime": "TODO: Implement uptime tracking",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/rate-limit/status")
@limiter.limit("10/minute")  # Máximo 10 requests por minuto
async def get_rate_limit_status(request: Request):
    """Obtener estado del rate limiting para la IP actual"""
    from slowapi.util import get_remote_address

    from rate_limiting_middleware import AdvancedRateLimiter

    client_ip = get_remote_address(request)
    advanced_limiter = AdvancedRateLimiter(limiter)

    rate_limit_info = advanced_limiter.get_rate_limit_info(client_ip)

    return {
        "ip": client_ip,
        "rate_limit_info": rate_limit_info,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/sentiment/summary")
@limiter.limit("60/minute")  # Máximo 60 requests por minuto
async def get_sentiment_summary(request: Request, hours: int = 24):
    """Obtener resumen de sentimiento de las últimas N horas"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("No database connection available, returning sample data")
            return {
                "summary": [
                    {
                        "sentiment_category": "Positive",
                        "count": 45,
                        "avg_score": 0.65,
                        "avg_subjectivity": 0.45,
                    },
                    {
                        "sentiment_category": "Neutral",
                        "count": 30,
                        "avg_score": 0.12,
                        "avg_subjectivity": 0.35,
                    },
                    {
                        "sentiment_category": "Negative",
                        "count": 25,
                        "avg_score": -0.45,
                        "avg_subjectivity": 0.55,
                    },
                ],
                "total_records": 100,
                "time_range_hours": hours,
            }

        # Query mejorada para obtener datos reales
        query = """
        SELECT
            CASE
                WHEN avg_sentiment_score > 0.1 THEN 'Positive'
                WHEN avg_sentiment_score < -0.1 THEN 'Negative'
                ELSE 'Neutral'
            END as sentiment_category,
            COUNT(*) as count,
            AVG(avg_sentiment_score) as avg_score,
            AVG(avg_sentiment_subjectivity) as avg_subjectivity
        FROM financial_sentiment_correlation
        WHERE hour >= NOW() - INTERVAL %s hours
            AND avg_sentiment_score IS NOT NULL
        GROUP BY
            CASE
                WHEN avg_sentiment_score > 0.1 THEN 'Positive'
                WHEN avg_sentiment_score < -0.1 THEN 'Negative'
                ELSE 'Neutral'
            END
        ORDER BY count DESC
        """

        cursor = conn.cursor()
        cursor.execute(query, (hours,))
        results = cursor.fetchall()

        summary = []
        total_records = 0

        for row in results:
            sentiment_category, count, avg_score, avg_subjectivity = row
            summary.append(
                {
                    "sentiment_category": sentiment_category,
                    "count": count,
                    "avg_score": float(avg_score) if avg_score else 0,
                    "avg_subjectivity": (
                        float(avg_subjectivity) if avg_subjectivity else 0
                    ),
                }
            )
            total_records += count

        cursor.close()
        conn.close()

        logger.info(
            f"Retrieved sentiment summary: {len(summary)} categories, "
            f"{total_records} total records"
        )

        return {
            "summary": summary,
            "total_records": total_records,
            "time_range_hours": hours,
        }
    except Exception as e:
        logger.error(f"Error in sentiment summary: {str(e)}")
        # Datos de ejemplo en caso de error
        return {
            "summary": [
                {
                    "sentiment_category": "Positive",
                    "count": 45,
                    "avg_score": 0.65,
                    "avg_subjectivity": 0.45,
                },
                {
                    "sentiment_category": "Neutral",
                    "count": 30,
                    "avg_score": 0.12,
                    "avg_subjectivity": 0.35,
                },
                {
                    "sentiment_category": "Negative",
                    "count": 25,
                    "avg_score": -0.45,
                    "avg_subjectivity": 0.55,
                },
            ],
            "total_records": 100,
            "time_range_hours": hours,
        }


@app.get("/api/sentiment/timeline")
@limiter.limit("60/minute")  # Máximo 60 requests por minuto
async def get_sentiment_timeline(
    request: Request, hours: int = 24, interval: str = "hour"
):
    """Obtener línea de tiempo de sentimiento"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "timeline": [
                    {
                        "time_period": "2024-01-15T10:00:00",
                        "sentiment_score": 0.65,
                        "avg_price": 150.25,
                        "news_count": 15,
                        "total_volume": 1000000,
                    },
                    {
                        "time_period": "2024-01-15T09:00:00",
                        "sentiment_score": 0.45,
                        "avg_price": 149.80,
                        "news_count": 12,
                        "total_volume": 950000,
                    },
                    {
                        "time_period": "2024-01-15T08:00:00",
                        "sentiment_score": 0.25,
                        "avg_price": 148.90,
                        "news_count": 8,
                        "total_volume": 800000,
                    },
                ],
                "interval": interval,
                "time_range_hours": hours,
            }

        if interval == "hour":
            group_by = "DATE_TRUNC('hour', hour)"
        elif interval == "day":
            group_by = "DATE_TRUNC('day', hour)"
        else:
            group_by = "DATE_TRUNC('hour', hour)"

        query = f"""
        SELECT
            {group_by} as time_period,
            AVG(avg_sentiment_score) as sentiment_score,
            AVG(avg_close_price) as avg_price,
            COUNT(*) as news_count,
            SUM(total_volume) as total_volume
        FROM financial_sentiment_correlation
        WHERE hour >= NOW() - INTERVAL '{hours} hours'
        GROUP BY {group_by}
        ORDER BY time_period DESC
        """

        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()

        return {
            "timeline": df.to_dict("records"),
            "interval": interval,
            "time_range_hours": hours,
        }
    except Exception:
        # Datos de ejemplo en caso de error
        return {
            "timeline": [
                {
                    "time_period": "2024-01-15T10:00:00",
                    "sentiment_score": 0.65,
                    "avg_price": 150.25,
                    "news_count": 15,
                    "total_volume": 1000000,
                },
                {
                    "time_period": "2024-01-15T09:00:00",
                    "sentiment_score": 0.45,
                    "avg_price": 149.80,
                    "news_count": 12,
                    "total_volume": 950000,
                },
                {
                    "time_period": "2024-01-15T08:00:00",
                    "sentiment_score": 0.25,
                    "avg_price": 148.90,
                    "news_count": 8,
                    "total_volume": 800000,
                },
            ],
            "interval": interval,
            "time_range_hours": hours,
        }


@app.get("/api/correlation/analysis")
@limiter.limit(
    "30/minute"
)  # Máximo 30 requests por minuto (más restrictivo)
async def get_correlation_analysis(request: Request, hours: int = 24):
    """Obtener análisis de correlación entre sentimiento y precios"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "correlation_analysis": [
                    {
                        "sentiment_category": "Positive",
                        "avg_price_change": 2.5,
                        "avg_sentiment_change": 0.15,
                        "data_points": 45,
                        "correlation_coefficient": 0.75,
                    },
                    {
                        "sentiment_category": "Neutral",
                        "avg_price_change": 0.2,
                        "avg_sentiment_change": 0.02,
                        "data_points": 30,
                        "correlation_coefficient": 0.12,
                    },
                    {
                        "sentiment_category": "Negative",
                        "avg_price_change": -1.8,
                        "avg_sentiment_change": -0.12,
                        "data_points": 25,
                        "correlation_coefficient": -0.68,
                    },
                ],
                "time_range_hours": hours,
            }

        query = """
        SELECT
            sentiment_category,
            AVG(price_change_percent) as avg_price_change,
            AVG(sentiment_change) as avg_sentiment_change,
            COUNT(*) as data_points,
            CORR(avg_sentiment_score, avg_close_price) as correlation_coefficient
        FROM financial_sentiment_correlation
        WHERE hour >= NOW() - INTERVAL '{hours} hours'
            AND price_change_percent IS NOT NULL
        GROUP BY sentiment_category
        ORDER BY avg_price_change DESC
        """

        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()

        return {
            "correlation_analysis": df.to_dict("records"),
            "time_range_hours": hours,
        }
    except Exception:
        # Datos de ejemplo en caso de error
        return {
            "correlation_analysis": [
                {
                    "sentiment_category": "Positive",
                    "avg_price_change": 2.5,
                    "avg_sentiment_change": 0.15,
                    "data_points": 45,
                    "correlation_coefficient": 0.75,
                },
                {
                    "sentiment_category": "Neutral",
                    "avg_price_change": 0.2,
                    "avg_sentiment_change": 0.02,
                    "data_points": 30,
                    "correlation_coefficient": 0.12,
                },
                {
                    "sentiment_category": "Negative",
                    "avg_price_change": -1.8,
                    "avg_sentiment_change": -0.12,
                    "data_points": 25,
                    "correlation_coefficient": -0.68,
                },
            ],
            "time_range_hours": hours,
        }


@app.get("/api/stocks/prices")
@limiter.limit("60/minute")  # Máximo 60 requests por minuto
async def get_stock_prices(request: Request, hours: int = 24):
    """Obtener datos de precios de acciones"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "stock_prices": [
                    {
                        "hour": "2024-01-15T10:00:00",
                        "avg_close_price": 150.25,
                        "max_high_price": 151.50,
                        "min_low_price": 149.80,
                        "total_volume": 1000000,
                        "price_points": 100,
                    },
                    {
                        "hour": "2024-01-15T09:00:00",
                        "avg_close_price": 149.80,
                        "max_high_price": 150.90,
                        "min_low_price": 148.90,
                        "total_volume": 950000,
                        "price_points": 95,
                    },
                    {
                        "hour": "2024-01-15T08:00:00",
                        "avg_close_price": 148.90,
                        "max_high_price": 149.75,
                        "min_low_price": 147.50,
                        "total_volume": 800000,
                        "price_points": 80,
                    },
                ],
                "time_range_hours": hours,
            }

        query = """
        SELECT
            hour,
            avg_close_price,
            max_high_price,
            min_low_price,
            total_volume,
            price_points
        FROM financial_sentiment_correlation
        WHERE hour >= NOW() - INTERVAL '{hours} hours'
            AND avg_close_price IS NOT NULL
        ORDER BY hour DESC
        """

        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()

        return {"stock_prices": df.to_dict("records"), "time_range_hours": hours}
    except Exception:
        # Datos de ejemplo en caso de error
        return {
            "stock_prices": [
                {
                    "hour": "2024-01-15T10:00:00",
                    "avg_close_price": 150.25,
                    "max_high_price": 151.50,
                    "min_low_price": 149.80,
                    "total_volume": 1000000,
                    "price_points": 100,
                },
                {
                    "hour": "2024-01-15T09:00:00",
                    "avg_close_price": 149.80,
                    "max_high_price": 150.90,
                    "min_low_price": 148.90,
                    "total_volume": 950000,
                    "price_points": 95,
                },
                {
                    "hour": "2024-01-15T08:00:00",
                    "avg_close_price": 148.90,
                    "max_high_price": 149.75,
                    "min_low_price": 147.50,
                    "total_volume": 800000,
                    "price_points": 80,
                },
            ],
            "time_range_hours": hours,
        }


@app.get("/api/news/latest")
@limiter.limit("60/minute")  # Máximo 60 requests por minuto
async def get_latest_news(request: Request, limit: int = 10):
    """Obtener las últimas noticias con sentimiento"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("No database connection available, returning sample data")
            return {
                "news": [
                    {
                        "title": "Apple Reports Strong Q4 Earnings",
                        "description": (
                            "Apple Inc. reported better-than-expected "
                            "quarterly earnings..."
                        ),
                        "url": "https://example.com/apple-earnings",
                        "published_at": "2024-01-15T10:30:00",
                        "source_name": "Financial Times",
                        "sentiment_score": 0.75,
                        "sentiment_subjectivity": 0.45,
                    },
                    {
                        "title": "Tech Stocks Face Market Volatility",
                        "description": (
                            "Technology stocks experienced significant "
                            "volatility..."
                        ),
                        "url": "https://example.com/tech-volatility",
                        "published_at": "2024-01-15T09:15:00",
                        "source_name": "Reuters",
                        "sentiment_score": -0.25,
                        "sentiment_subjectivity": 0.35,
                    },
                ],
                "total_count": 2,
            }

        # Query mejorada para obtener noticias reales
        query = """
        SELECT
            title,
            description,
            url,
            published_at,
            COALESCE(source_name, 'Unknown') as source_name,
            sentiment_score,
            sentiment_subjectivity,
            symbol
        FROM news_with_sentiment
        WHERE published_at IS NOT NULL
        ORDER BY published_at DESC
        LIMIT %s
        """

        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        results = cursor.fetchall()

        news = []
        for row in results:
            (
                title,
                description,
                url,
                published_at,
                source_name,
                sentiment_score,
                sentiment_subjectivity,
                symbol,
            ) = row
            news.append(
                {
                    "title": title or "Sin título",
                    "description": description or "Sin descripción",
                    "url": url or "#",
                    "published_at": published_at.isoformat() if published_at else None,
                    "source_name": source_name,
                    "sentiment_score": float(sentiment_score) if sentiment_score else 0,
                    "sentiment_subjectivity": (
                        float(sentiment_subjectivity) if sentiment_subjectivity else 0
                    ),
                    "symbol": symbol,
                }
            )

        cursor.close()
        conn.close()

        logger.info(f"Retrieved {len(news)} latest news articles")

        return {"news": news, "total_count": len(news)}
    except Exception as e:
        logger.error(f"Error in latest news: {str(e)}")
        # Datos de ejemplo en caso de error
        return {
            "news": [
                {
                    "title": "Apple Reports Strong Q4 Earnings",
                    "description": (
                        "Apple Inc. reported better-than-expected "
                        "quarterly earnings..."
                    ),
                    "url": "https://example.com/apple-earnings",
                    "published_at": "2024-01-15T10:30:00",
                    "source_name": "Financial Times",
                    "sentiment_score": 0.75,
                    "sentiment_subjectivity": 0.45,
                },
                {
                    "title": "Tech Stocks Face Market Volatility",
                    "description": (
                        "Technology stocks experienced significant "
                        "volatility..."
                    ),
                    "url": "https://example.com/tech-volatility",
                    "published_at": "2024-01-15T09:15:00",
                    "source_name": "Reuters",
                    "sentiment_score": -0.25,
                    "sentiment_subjectivity": 0.35,
                },
            ],
            "total_count": 2,
        }


@app.get("/test-db")
async def test_database():
    """Endpoint de prueba para verificar la conexión a la base de datos"""
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "No database connection"}

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM financial_sentiment_correlation")
        total_count = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM financial_sentiment_correlation "
            "WHERE hour >= NOW() - INTERVAL '720 HOUR'"
        )
        recent_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {
            "total_records": total_count,
            "recent_records": recent_count,
            "connection": "success",
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/dashboard/stats")
@limiter.limit(
    "30/minute"
)  # Máximo 30 requests por minuto (más restrictivo)
async def get_dashboard_stats(request: Request, hours: int = 8760):
    """Obtener estadísticas generales del dashboard"""
    try:
        conn = get_db_connection()
        if not conn:
            return {
                "general_stats": {
                    "total_records": 1250,
                    "overall_sentiment": 0.15,
                    "avg_stock_price": 150.25,
                    "latest_data_time": datetime.now().isoformat(),
                },
                "sentiment_distribution": [
                    {"sentiment_category": "Positive", "count": 45},
                    {"sentiment_category": "Neutral", "count": 30},
                    {"sentiment_category": "Negative", "count": 25},
                ],
            }

        # Usar cursor directo en lugar de pandas para evitar problemas con intervalos
        cursor = conn.cursor()

        # Debug: verificar la query que se está ejecutando
        stats_query = f"""
        SELECT
            COUNT(*) as total_records,
            AVG(avg_sentiment_score) as overall_sentiment,
            AVG(avg_close_price) as avg_stock_price,
            MAX(hour) as latest_data_time
        FROM financial_sentiment_correlation
        WHERE hour >= NOW() - INTERVAL '{hours} hours'
        """
        logger.info(f"Executing query: {stats_query}")
        cursor.execute(stats_query)
        stats_row = cursor.fetchone()

        logger.info(f"Query result: {stats_row}")

        # Debug adicional: verificar el tipo de datos
        if stats_row:
            total_records, overall_sentiment, avg_stock_price, latest_data_time = (
                stats_row
            )
            logger.info(
                f"Parsed values - total_records: {total_records} "
                f"(type: {type(total_records)})"
            )
            logger.info(
                f"Parsed values - overall_sentiment: {overall_sentiment} "
                f"(type: {type(overall_sentiment)})"
            )
            logger.info(
                f"Parsed values - avg_stock_price: {avg_stock_price} "
                f"(type: {type(avg_stock_price)})"
            )
            logger.info(
                f"Parsed values - latest_data_time: {latest_data_time} "
                f"(type: {type(latest_data_time)})"
            )
        else:
            total_records, overall_sentiment, avg_stock_price, latest_data_time = (
                0,
                0,
                0,
                None,
            )
            logger.warning("Query returned no results")

        # Distribución de sentimiento
        dist_query = f"""
        SELECT sentiment_category, COUNT(*) as count
        FROM financial_sentiment_correlation
        WHERE hour >= NOW() - INTERVAL '{hours} hours'
        GROUP BY sentiment_category
        ORDER BY count DESC
        """
        cursor.execute(dist_query)
        dist_results = cursor.fetchall()

        sentiment_distribution = []
        for row in dist_results:
            sentiment_category, count = row
            sentiment_distribution.append(
                {"sentiment_category": sentiment_category, "count": count}
            )

        cursor.close()
        conn.close()

        logger.info(
            f"Dashboard stats: {total_records} records, "
            f"sentiment: {overall_sentiment}, price: {avg_stock_price}"
        )

        return {
            "general_stats": {
                "total_records": int(total_records) if total_records else 0,
                "overall_sentiment": (
                    float(overall_sentiment) if overall_sentiment else 0
                ),
                "avg_stock_price": float(avg_stock_price) if avg_stock_price else 0,
                "latest_data_time": (
                    latest_data_time.isoformat() if latest_data_time else None
                ),
            },
            "sentiment_distribution": sentiment_distribution,
        }
    except Exception:
        logger.error("Error in dashboard stats")
        return {
            "general_stats": {
                "total_records": 0,
                "overall_sentiment": 0,
                "avg_stock_price": 0,
                "latest_data_time": None,
            },
            "sentiment_distribution": [],
            "error": "Database error",
        }


@app.get("/api/sentiment/summary_by_symbol")
async def get_sentiment_summary_by_symbol(hours: int = 24):
    """Obtener resumen de sentimiento por símbolo de las últimas N horas"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "summary": [
                    {
                        "symbol": "AAPL",
                        "avg_sentiment": 0.12,
                        "avg_subjectivity": 0.45,
                        "news_count": 8,
                    },
                    {
                        "symbol": "MSFT",
                        "avg_sentiment": 0.08,
                        "avg_subjectivity": 0.38,
                        "news_count": 5,
                    },
                ],
                "total_records": 13,
                "time_range_hours": hours,
            }
        query = """
        SELECT
            symbol,
            AVG(sentiment_score) as avg_sentiment,
            AVG(sentiment_subjectivity) as avg_subjectivity,
            COUNT(*) as news_count
        FROM news_with_sentiment
        WHERE published_at >= NOW() - INTERVAL '{hours} hours'
        GROUP BY symbol
        ORDER BY news_count DESC
        """
        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()
        return {
            "summary": df.to_dict("records"),
            "total_records": len(df),
            "time_range_hours": hours,
        }
    except Exception:
        return {
            "summary": [
                {
                    "symbol": "AAPL",
                    "avg_sentiment": 0.12,
                    "avg_subjectivity": 0.45,
                    "news_count": 8,
                },
                {
                    "symbol": "MSFT",
                    "avg_sentiment": 0.08,
                    "avg_subjectivity": 0.38,
                    "news_count": 5,
                },
            ],
            "total_records": 13,
            "time_range_hours": hours,
        }


@app.get("/api/stocks/prices_by_symbol")
async def get_stock_prices_by_symbol(hours: int = 24):
    """Obtener precios de acciones por símbolo y fecha/hora"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "stock_prices": [
                    {
                        "symbol": "AAPL",
                        "hour": "2024-06-24T10:00:00",
                        "close": 189.5,
                        "high": 190.2,
                        "low": 188.7,
                        "volume": 1200000,
                    },
                    {
                        "symbol": "MSFT",
                        "hour": "2024-06-24T10:00:00",
                        "close": 340.1,
                        "high": 342.0,
                        "low": 339.0,
                        "volume": 950000,
                    },
                ],
                "time_range_hours": hours,
            }
        query = """
        SELECT
            symbol,
            hour,
            avg_close_price as close,
            max_high_price as high,
            min_low_price as low,
            total_volume as volume
        FROM financial_sentiment_correlation
        WHERE hour >= NOW() - INTERVAL '{hours} hours'
            AND symbol IS NOT NULL
        ORDER BY symbol, hour DESC
        """
        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()
        return {"stock_prices": df.to_dict("records"), "time_range_hours": hours}
    except Exception:
        return {
            "stock_prices": [
                {
                    "symbol": "AAPL",
                    "hour": "2024-06-24T10:00:00",
                    "close": 189.5,
                    "high": 190.2,
                    "low": 188.7,
                    "volume": 1200000,
                },
                {
                    "symbol": "MSFT",
                    "hour": "2024-06-24T10:00:00",
                    "close": 340.1,
                    "high": 342.0,
                    "low": 339.0,
                    "volume": 950000,
                },
            ],
            "time_range_hours": hours,
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
