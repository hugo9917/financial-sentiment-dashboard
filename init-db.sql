-- Grant privileges to the postgres user
GRANT ALL PRIVILEGES ON DATABASE financial_sentiment TO postgres;

-- Crear base de datos para Airflow si no existe
SELECT 'CREATE DATABASE airflow' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec

-- Conectar a la base de datos financial_sentiment
\c financial_sentiment;

-- Crear tabla para noticias con sentimiento
CREATE TABLE IF NOT EXISTS news_with_sentiment (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    url TEXT,
    published_at TIMESTAMP,
    source_name VARCHAR(255),
    sentiment_score DECIMAL(3,2),
    sentiment_subjectivity DECIMAL(3,2),
    symbol VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla para correlación de sentimiento financiero
CREATE TABLE IF NOT EXISTS financial_sentiment_correlation (
    id SERIAL PRIMARY KEY,
    hour TIMESTAMP,
    sentiment_category VARCHAR(50),
    avg_sentiment_score DECIMAL(3,2),
    avg_sentiment_subjectivity DECIMAL(3,2),
    avg_close_price DECIMAL(10,2),
    max_high_price DECIMAL(10,2),
    min_low_price DECIMAL(10,2),
    total_volume BIGINT,
    price_points INTEGER,
    price_change_percent DECIMAL(5,2),
    sentiment_change DECIMAL(3,2),
    news_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news_with_sentiment(published_at);
CREATE INDEX IF NOT EXISTS idx_news_sentiment_score ON news_with_sentiment(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_financial_hour ON financial_sentiment_correlation(hour);
CREATE INDEX IF NOT EXISTS idx_financial_sentiment_category ON financial_sentiment_correlation(sentiment_category);

-- Insertar datos de ejemplo solo si las tablas están vacías
INSERT INTO news_with_sentiment (title, description, url, published_at, source_name, sentiment_score, sentiment_subjectivity)
SELECT * FROM (VALUES
    ('Apple Reports Strong Q4 Earnings', 'Apple Inc. reported better-than-expected quarterly earnings driven by strong iPhone sales and services growth.', 'https://example.com/apple-earnings', '2024-01-15 10:30:00'::timestamp, 'Financial Times', 0.75, 0.45),
    ('Tech Stocks Face Market Volatility', 'Technology stocks experienced significant volatility as investors react to economic uncertainty.', 'https://example.com/tech-volatility', '2024-01-15 09:15:00'::timestamp, 'Reuters', -0.25, 0.35),
    ('Tesla Announces New Electric Vehicle Model', 'Tesla unveiled its latest electric vehicle model with advanced autonomous driving features.', 'https://example.com/tesla-new-model', '2024-01-15 08:45:00'::timestamp, 'Bloomberg', 0.60, 0.40),
    ('Federal Reserve Signals Interest Rate Changes', 'The Federal Reserve indicated potential changes to interest rate policy in response to economic indicators.', 'https://example.com/fed-rates', '2024-01-15 07:30:00'::timestamp, 'Wall Street Journal', 0.10, 0.55),
    ('Oil Prices Surge on Supply Concerns', 'Oil prices reached new highs as supply chain disruptions continue to impact global markets.', 'https://example.com/oil-prices', '2024-01-15 06:20:00'::timestamp, 'CNBC', -0.15, 0.30)
) AS v(title, description, url, published_at, source_name, sentiment_score, sentiment_subjectivity)
WHERE NOT EXISTS (SELECT 1 FROM news_with_sentiment LIMIT 1);

INSERT INTO financial_sentiment_correlation (hour, sentiment_category, avg_sentiment_score, avg_sentiment_subjectivity, avg_close_price, max_high_price, min_low_price, total_volume, price_points, price_change_percent, sentiment_change, news_count)
SELECT * FROM (VALUES
    ('2024-01-15 10:00:00'::timestamp, 'Positive', 0.65, 0.45, 150.25, 151.50, 149.80, 1000000, 100, 2.5, 0.15, 15),
    ('2024-01-15 09:00:00'::timestamp, 'Neutral', 0.12, 0.35, 149.80, 150.90, 148.90, 950000, 95, 0.2, 0.02, 12),
    ('2024-01-15 08:00:00'::timestamp, 'Negative', -0.45, 0.55, 148.90, 149.75, 147.50, 800000, 80, -1.8, -0.12, 8),
    ('2024-01-15 07:00:00'::timestamp, 'Positive', 0.55, 0.40, 149.20, 150.10, 148.30, 850000, 85, 1.2, 0.08, 10),
    ('2024-01-15 06:00:00'::timestamp, 'Neutral', 0.08, 0.30, 148.50, 149.20, 147.80, 750000, 75, 0.1, 0.01, 6)
) AS v(hour, sentiment_category, avg_sentiment_score, avg_sentiment_subjectivity, avg_close_price, max_high_price, min_low_price, total_volume, price_points, price_change_percent, sentiment_change, news_count)
WHERE NOT EXISTS (SELECT 1 FROM financial_sentiment_correlation LIMIT 1);

-- Crear usuario para la aplicación (opcional)
-- CREATE USER app_user WITH PASSWORD 'app_password';
-- GRANT ALL PRIVILEGES ON DATABASE financial_sentiment TO app_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user; 