{{
  config(
    materialized='table'
  )
}}

WITH news_hourly AS (
  SELECT
    DATE_TRUNC('hour', published_at) as hour,
    AVG(sentiment_score) as avg_sentiment_score,
    COUNT(*) as news_count,
    AVG(sentiment_subjectivity) as avg_sentiment_subjectivity
  FROM {{ ref('stg_news') }}
  WHERE published_at >= CURRENT_DATE - INTERVAL '7 days'
  GROUP BY DATE_TRUNC('hour', published_at)
),

stock_hourly AS (
  SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(close_price) as avg_close_price,
    MAX(high_price) as max_high_price,
    MIN(low_price) as min_low_price,
    SUM(volume) as total_volume,
    COUNT(*) as price_points
  FROM {{ ref('stg_stock_prices') }}
  WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
  GROUP BY DATE_TRUNC('hour', timestamp)
),

correlation_data AS (
  SELECT
    COALESCE(n.hour, s.hour) as hour,
    n.avg_sentiment_score,
    n.news_count,
    n.avg_sentiment_subjectivity,
    s.avg_close_price,
    s.max_high_price,
    s.min_low_price,
    s.total_volume,
    s.price_points,
    CASE 
      WHEN n.avg_sentiment_score > 0.1 THEN 'Positive'
      WHEN n.avg_sentiment_score < -0.1 THEN 'Negative'
      ELSE 'Neutral'
    END as sentiment_category
  FROM news_hourly n
  FULL OUTER JOIN stock_hourly s ON n.hour = s.hour
  WHERE n.hour IS NOT NULL OR s.hour IS NOT NULL
)

SELECT
  hour,
  avg_sentiment_score,
  news_count,
  avg_sentiment_subjectivity,
  avg_close_price,
  max_high_price,
  min_low_price,
  total_volume,
  price_points,
  sentiment_category,
  CASE 
    WHEN LAG(avg_close_price) OVER (ORDER BY hour) IS NOT NULL 
    THEN ((avg_close_price - LAG(avg_close_price) OVER (ORDER BY hour)) / LAG(avg_close_price) OVER (ORDER BY hour)) * 100
    ELSE NULL 
  END as price_change_percent,
  CASE 
    WHEN LAG(avg_sentiment_score) OVER (ORDER BY hour) IS NOT NULL 
    THEN avg_sentiment_score - LAG(avg_sentiment_score) OVER (ORDER BY hour)
    ELSE NULL 
  END as sentiment_change
FROM correlation_data
ORDER BY hour DESC 