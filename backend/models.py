import os
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Float, Integer, String,
                        Text, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "database": os.getenv("DB_NAME", "financial_sentiment"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "port": int(os.getenv("DB_PORT", "5432")),
}

# Crear engine de SQLAlchemy
DATABASE_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


class FinancialSentimentCorrelation(Base):
    """Modelo para la tabla de correlación financiera-sentimiento"""

    __tablename__ = "financial_sentiment_correlation"

    id = Column(Integer, primary_key=True, index=True)
    hour = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(10), nullable=True, index=True)
    avg_sentiment_score = Column(Float, nullable=True)
    avg_sentiment_subjectivity = Column(Float, nullable=True)
    avg_close_price = Column(Float, nullable=True)
    max_high_price = Column(Float, nullable=True)
    min_low_price = Column(Float, nullable=True)
    total_volume = Column(Integer, nullable=True)
    price_points = Column(Integer, nullable=True)
    news_count = Column(Integer, nullable=True)
    sentiment_category = Column(String(20), nullable=True)
    price_change_percent = Column(Float, nullable=True)
    sentiment_change = Column(Float, nullable=True)
    correlation_coefficient = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NewsWithSentiment(Base):
    """Modelo para la tabla de noticias con sentimiento"""

    __tablename__ = "news_with_sentiment"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    source_name = Column(String(100), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_subjectivity = Column(Float, nullable=True)
    symbol = Column(String(10), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StockPrices(Base):
    """Modelo para la tabla de precios de acciones"""

    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """Modelo para la tabla de usuarios"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Función para crear todas las tablas
def create_tables():
    Base.metadata.create_all(bind=engine)


# Función para obtener metadata para Alembic
def get_metadata():
    return Base.metadata
