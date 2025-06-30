{{
  config(
    materialized='view'
  )
}}

WITH source AS (
  SELECT * FROM {{ source('raw', 'financial_data') }}
  WHERE _airbyte_data::text LIKE '%"1. open"%'
),

parsed AS (
  SELECT
    _airbyte_ab_id,
    _airbyte_emitted_at,
    _airbyte_data,
    jsonb_object_keys(_airbyte_data->'Time Series (1min)') as timestamp_key,
    _airbyte_data->'Time Series (1min)'->jsonb_object_keys(_airbyte_data->'Time Series (1min)') as price_data
  FROM source
),

flattened AS (
  SELECT
    _airbyte_ab_id as id,
    timestamp_key::timestamp as timestamp,
    price_data->>'1. open' as open_price,
    price_data->>'2. high' as high_price,
    price_data->>'3. low' as low_price,
    price_data->>'4. close' as close_price,
    price_data->>'5. volume' as volume,
    _airbyte_emitted_at as ingested_at
  FROM parsed
)

SELECT
  id,
  timestamp,
  open_price::float as open_price,
  high_price::float as high_price,
  low_price::float as low_price,
  close_price::float as close_price,
  volume::integer as volume,
  ingested_at
FROM flattened
WHERE timestamp IS NOT NULL 