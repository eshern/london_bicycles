{{
    config(
        materialized='table'
    )
}}

select
    station_id,
    station_name,
    latitude,
    longitude,
    -- Calculate if station is in central London (rough bounds)
    case
        when latitude between 51.50 and 51.52 and longitude between -0.14 and -0.12 then 'Central'
        else 'Outer'
    end as station_area
from {{ ref('stg_stations') }}
