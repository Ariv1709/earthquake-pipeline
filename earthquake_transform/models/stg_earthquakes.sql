{{ config(materialized='table') }}

WITH raw_data AS (
    SELECT * FROM {{ source('raw_usgs', 'earthquakes') }}
)

SELECT
    id,
    mag as magnitude,
    -- Convert milliseconds to readable UTC timestamp
    TIMESTAMP_MILLIS(CAST(time AS INT64)) AS event_time,
    place,
    longitude,
    latitude,
    depth,
    -- Logic to categorize the earthquake for your dashboard later
    CASE 
        WHEN mag < 3.0 THEN 'Micro'
        WHEN mag >= 3.0 AND mag < 5.0 THEN 'Minor'
        WHEN mag >= 5.0 AND mag < 7.0 THEN 'Strong'
        ELSE 'Major'
    END AS magnitude_category
FROM raw_data
WHERE mag IS NOT NULL