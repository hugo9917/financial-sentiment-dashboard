{{
  config(
    materialized='view'
  )
}}

WITH source AS (
  SELECT * FROM {{ source('raw', 'financial_data') }}
  WHERE _airbyte_data::text LIKE '%"title"%'
),

parsed AS (
  SELECT
    _airbyte_ab_id,
    _airbyte_emitted_at,
    _airbyte_data,
    _airbyte_data->>'title' as title,
    _airbyte_data->>'description' as description,
    _airbyte_data->>'url' as url,
    _airbyte_data->>'publishedAt' as published_at,
    _airbyte_data->>'source'->>'name' as source_name,
    _airbyte_data->>'sentiment_score' as sentiment_score,
    _airbyte_data->>'sentiment_subjectivity' as sentiment_subjectivity
  FROM source
)

SELECT
  _airbyte_ab_id as id,
  title,
  description,
  url,
  published_at::timestamp as published_at,
  source_name,
  sentiment_score::float as sentiment_score,
  sentiment_subjectivity::float as sentiment_subjectivity,
  _airbyte_emitted_at as ingested_at
FROM parsed
WHERE title IS NOT NULL 