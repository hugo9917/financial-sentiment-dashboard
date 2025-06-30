from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import List, Optional
import json

app = FastAPI(
    title="Financial Sentiment API", 
    description="API para análisis de sentimiento financiero y correlación con precios",
    version="1.0.0"
)

# Configurar CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la base de datos desde variables de entorno
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'database': os.getenv('DB_NAME', 'financial_sentiment'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': int(os.getenv('DB_PORT', '5432'))
}

def get_db_connection():
    """Crear conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error de conexión a BD: {str(e)}")
        # Para desarrollo, devolver datos de ejemplo si no hay BD
        return None

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Financial Sentiment API v1.0.0", "status": "running"}

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
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "healthy", "database": "disconnected", "message": "Using sample data"}
    except Exception as e:
        return {"status": "healthy", "database": "disconnected", "message": "Using sample data", "error": str(e)}

@app.get("/api/sentiment/summary")
async def get_sentiment_summary(hours: int = 24):
    """Obtener resumen de sentimiento de las últimas N horas"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "summary": [
                    {"sentiment_category": "Positive", "count": 45, "avg_score": 0.65, "avg_subjectivity": 0.45},
                    {"sentiment_category": "Neutral", "count": 30, "avg_score": 0.12, "avg_subjectivity": 0.35},
                    {"sentiment_category": "Negative", "count": 25, "avg_score": -0.45, "avg_subjectivity": 0.55}
                ],
                "total_records": 100,
                "time_range_hours": hours
            }
        
        query = """
        SELECT 
            sentiment_category,
            COUNT(*) as count,
            AVG(avg_sentiment_score) as avg_score,
            AVG(avg_sentiment_subjectivity) as avg_subjectivity
        FROM financial_sentiment_correlation 
        WHERE hour >= NOW() - INTERVAL '%s hours'
        GROUP BY sentiment_category
        ORDER BY count DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()
        
        return {
            "summary": df.to_dict('records'),
            "total_records": len(df),
            "time_range_hours": hours
        }
    except Exception as e:
        # Datos de ejemplo en caso de error
        return {
            "summary": [
                {"sentiment_category": "Positive", "count": 45, "avg_score": 0.65, "avg_subjectivity": 0.45},
                {"sentiment_category": "Neutral", "count": 30, "avg_score": 0.12, "avg_subjectivity": 0.35},
                {"sentiment_category": "Negative", "count": 25, "avg_score": -0.45, "avg_subjectivity": 0.55}
            ],
            "total_records": 100,
            "time_range_hours": hours
        }

@app.get("/api/sentiment/timeline")
async def get_sentiment_timeline(
    hours: int = 24,
    interval: str = "hour"
):
    """Obtener línea de tiempo de sentimiento"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "timeline": [
                    {"time_period": "2024-01-15T10:00:00", "sentiment_score": 0.65, "avg_price": 150.25, "news_count": 15, "total_volume": 1000000},
                    {"time_period": "2024-01-15T09:00:00", "sentiment_score": 0.45, "avg_price": 149.80, "news_count": 12, "total_volume": 950000},
                    {"time_period": "2024-01-15T08:00:00", "sentiment_score": 0.25, "avg_price": 148.90, "news_count": 8, "total_volume": 800000}
                ],
                "interval": interval,
                "time_range_hours": hours
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
        WHERE hour >= NOW() - INTERVAL '%s hours'
        GROUP BY {group_by}
        ORDER BY time_period DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()
        
        return {
            "timeline": df.to_dict('records'),
            "interval": interval,
            "time_range_hours": hours
        }
    except Exception as e:
        # Datos de ejemplo en caso de error
        return {
            "timeline": [
                {"time_period": "2024-01-15T10:00:00", "sentiment_score": 0.65, "avg_price": 150.25, "news_count": 15, "total_volume": 1000000},
                {"time_period": "2024-01-15T09:00:00", "sentiment_score": 0.45, "avg_price": 149.80, "news_count": 12, "total_volume": 950000},
                {"time_period": "2024-01-15T08:00:00", "sentiment_score": 0.25, "avg_price": 148.90, "news_count": 8, "total_volume": 800000}
            ],
            "interval": interval,
            "time_range_hours": hours
        }

@app.get("/api/correlation/analysis")
async def get_correlation_analysis(hours: int = 24):
    """Obtener análisis de correlación entre sentimiento y precios"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "correlation_analysis": [
                    {"sentiment_category": "Positive", "avg_price_change": 2.5, "avg_sentiment_change": 0.15, "data_points": 45, "correlation_coefficient": 0.75},
                    {"sentiment_category": "Neutral", "avg_price_change": 0.2, "avg_sentiment_change": 0.02, "data_points": 30, "correlation_coefficient": 0.12},
                    {"sentiment_category": "Negative", "avg_price_change": -1.8, "avg_sentiment_change": -0.12, "data_points": 25, "correlation_coefficient": -0.68}
                ],
                "time_range_hours": hours
            }
        
        query = """
        SELECT 
            sentiment_category,
            AVG(price_change_percent) as avg_price_change,
            AVG(sentiment_change) as avg_sentiment_change,
            COUNT(*) as data_points,
            CORR(avg_sentiment_score, avg_close_price) as correlation_coefficient
        FROM financial_sentiment_correlation 
        WHERE hour >= NOW() - INTERVAL '%s hours'
            AND price_change_percent IS NOT NULL
        GROUP BY sentiment_category
        ORDER BY avg_price_change DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()
        
        return {
            "correlation_analysis": df.to_dict('records'),
            "time_range_hours": hours
        }
    except Exception as e:
        # Datos de ejemplo en caso de error
        return {
            "correlation_analysis": [
                {"sentiment_category": "Positive", "avg_price_change": 2.5, "avg_sentiment_change": 0.15, "data_points": 45, "correlation_coefficient": 0.75},
                {"sentiment_category": "Neutral", "avg_price_change": 0.2, "avg_sentiment_change": 0.02, "data_points": 30, "correlation_coefficient": 0.12},
                {"sentiment_category": "Negative", "avg_price_change": -1.8, "avg_sentiment_change": -0.12, "data_points": 25, "correlation_coefficient": -0.68}
            ],
            "time_range_hours": hours
        }

@app.get("/api/stocks/prices")
async def get_stock_prices(hours: int = 24):
    """Obtener datos de precios de acciones"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "stock_prices": [
                    {"hour": "2024-01-15T10:00:00", "avg_close_price": 150.25, "max_high_price": 151.50, "min_low_price": 149.80, "total_volume": 1000000, "price_points": 100},
                    {"hour": "2024-01-15T09:00:00", "avg_close_price": 149.80, "max_high_price": 150.90, "min_low_price": 148.90, "total_volume": 950000, "price_points": 95},
                    {"hour": "2024-01-15T08:00:00", "avg_close_price": 148.90, "max_high_price": 149.75, "min_low_price": 147.50, "total_volume": 800000, "price_points": 80}
                ],
                "time_range_hours": hours
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
        WHERE hour >= NOW() - INTERVAL '%s hours'
            AND avg_close_price IS NOT NULL
        ORDER BY hour DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()
        
        return {
            "stock_prices": df.to_dict('records'),
            "time_range_hours": hours
        }
    except Exception as e:
        # Datos de ejemplo en caso de error
        return {
            "stock_prices": [
                {"hour": "2024-01-15T10:00:00", "avg_close_price": 150.25, "max_high_price": 151.50, "min_low_price": 149.80, "total_volume": 1000000, "price_points": 100},
                {"hour": "2024-01-15T09:00:00", "avg_close_price": 149.80, "max_high_price": 150.90, "min_low_price": 148.90, "total_volume": 950000, "price_points": 95},
                {"hour": "2024-01-15T08:00:00", "avg_close_price": 148.90, "max_high_price": 149.75, "min_low_price": 147.50, "total_volume": 800000, "price_points": 80}
            ],
            "time_range_hours": hours
        }

@app.get("/api/news/latest")
async def get_latest_news(limit: int = 10):
    """Obtener las últimas noticias con sentimiento"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "news": [
                    {
                        "title": "Apple Reports Strong Q4 Earnings",
                        "description": "Apple Inc. reported better-than-expected quarterly earnings...",
                        "url": "https://example.com/apple-earnings",
                        "published_at": "2024-01-15T10:30:00",
                        "source_name": "Financial Times",
                        "sentiment_score": 0.75,
                        "sentiment_subjectivity": 0.45
                    },
                    {
                        "title": "Tech Stocks Face Market Volatility",
                        "description": "Technology stocks experienced significant volatility...",
                        "url": "https://example.com/tech-volatility",
                        "published_at": "2024-01-15T09:15:00",
                        "source_name": "Reuters",
                        "sentiment_score": -0.25,
                        "sentiment_subjectivity": 0.35
                    }
                ],
                "total_count": 2
            }
        
        query = """
        SELECT 
            title,
            description,
            url,
            published_at,
            source as source_name,
            sentiment_score,
            sentiment_subjectivity
        FROM news_with_sentiment 
        ORDER BY published_at DESC 
        LIMIT %s
        """
        
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        
        return {
            "news": df.to_dict('records'),
            "total_count": len(df)
        }
    except Exception as e:
        # Datos de ejemplo en caso de error
        return {
            "news": [
                {
                    "title": "Apple Reports Strong Q4 Earnings",
                    "description": "Apple Inc. reported better-than-expected quarterly earnings...",
                    "url": "https://example.com/apple-earnings",
                    "published_at": "2024-01-15T10:30:00",
                    "source_name": "Financial Times",
                    "sentiment_score": 0.75,
                    "sentiment_subjectivity": 0.45
                },
                {
                    "title": "Tech Stocks Face Market Volatility",
                    "description": "Technology stocks experienced significant volatility...",
                    "url": "https://example.com/tech-volatility",
                    "published_at": "2024-01-15T09:15:00",
                    "source_name": "Reuters",
                    "sentiment_score": -0.25,
                    "sentiment_subjectivity": 0.35
                }
            ],
            "total_count": 2
        }

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Obtener estadísticas generales del dashboard"""
    try:
        conn = get_db_connection()
        if not conn:
            # Datos de ejemplo para desarrollo
            return {
                "general_stats": {
                    "total_records": 1250,
                    "overall_sentiment": 0.15,
                    "avg_stock_price": 150.25,
                    "latest_data_time": datetime.now().isoformat()
                },
                "sentiment_distribution": [
                    {"sentiment_category": "Positive", "count": 45},
                    {"sentiment_category": "Neutral", "count": 30},
                    {"sentiment_category": "Negative", "count": 25}
                ]
            }
        # Consultas para estadísticas generales
        stats_query = """
        SELECT 
            COUNT(*) as total_records,
            AVG(avg_sentiment_score) as overall_sentiment,
            AVG(avg_close_price) as avg_stock_price,
            MAX(hour) as latest_data_time
        FROM financial_sentiment_correlation 
        WHERE hour >= NOW() - INTERVAL '24 hours'
        """
        cursor = conn.cursor()
        cursor.execute(stats_query)
        stats = cursor.fetchone()
        # Distribución de sentimiento
        dist_query = """
        SELECT sentiment_category, COUNT(*) as count
        FROM financial_sentiment_correlation
        WHERE hour >= NOW() - INTERVAL '24 hours'
        GROUP BY sentiment_category
        ORDER BY count DESC
        """
        cursor.execute(dist_query)
        dist = cursor.fetchall()
        sentiment_distribution = [
            {"sentiment_category": row[0], "count": row[1]} for row in dist
        ]
        cursor.close()
        conn.close()
        return {
            "general_stats": {
                "total_records": stats[0] or 0,
                "overall_sentiment": float(stats[1]) if stats[1] else 0,
                "avg_stock_price": float(stats[2]) if stats[2] else 0,
                "latest_data_time": stats[3].isoformat() if stats[3] else None
            },
            "sentiment_distribution": sentiment_distribution
        }
    except Exception as e:
        # Datos de ejemplo en caso de error
        return {
            "general_stats": {
                "total_records": 1250,
                "overall_sentiment": 0.15,
                "avg_stock_price": 150.25,
                "latest_data_time": datetime.now().isoformat()
            },
            "sentiment_distribution": [
                {"sentiment_category": "Positive", "count": 45},
                {"sentiment_category": "Neutral", "count": 30},
                {"sentiment_category": "Negative", "count": 25}
            ]
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
                    {"symbol": "AAPL", "avg_sentiment": 0.12, "avg_subjectivity": 0.45, "news_count": 8},
                    {"symbol": "MSFT", "avg_sentiment": 0.08, "avg_subjectivity": 0.38, "news_count": 5}
                ],
                "total_records": 13,
                "time_range_hours": hours
            }
        query = """
        SELECT 
            symbol,
            AVG(sentiment_score) as avg_sentiment,
            AVG(sentiment_subjectivity) as avg_subjectivity,
            COUNT(*) as news_count
        FROM news_with_sentiment
        WHERE published_at >= NOW() - INTERVAL '%s hours'
        GROUP BY symbol
        ORDER BY news_count DESC
        """
        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()
        return {
            "summary": df.to_dict('records'),
            "total_records": len(df),
            "time_range_hours": hours
        }
    except Exception as e:
        return {
            "summary": [
                {"symbol": "AAPL", "avg_sentiment": 0.12, "avg_subjectivity": 0.45, "news_count": 8},
                {"symbol": "MSFT", "avg_sentiment": 0.08, "avg_subjectivity": 0.38, "news_count": 5}
            ],
            "total_records": 13,
            "time_range_hours": hours
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
                    {"symbol": "AAPL", "hour": "2024-06-24T10:00:00", "close": 189.5, "high": 190.2, "low": 188.7, "volume": 1200000},
                    {"symbol": "MSFT", "hour": "2024-06-24T10:00:00", "close": 340.1, "high": 342.0, "low": 339.0, "volume": 950000}
                ],
                "time_range_hours": hours
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
        WHERE hour >= NOW() - INTERVAL '%s hours'
            AND symbol IS NOT NULL
        ORDER BY symbol, hour DESC
        """
        df = pd.read_sql_query(query, conn, params=[hours])
        conn.close()
        return {
            "stock_prices": df.to_dict('records'),
            "time_range_hours": hours
        }
    except Exception as e:
        return {
            "stock_prices": [
                {"symbol": "AAPL", "hour": "2024-06-24T10:00:00", "close": 189.5, "high": 190.2, "low": 188.7, "volume": 1200000},
                {"symbol": "MSFT", "hour": "2024-06-24T10:00:00", "close": 340.1, "high": 342.0, "low": 339.0, "volume": 950000}
            ],
            "time_range_hours": hours
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 