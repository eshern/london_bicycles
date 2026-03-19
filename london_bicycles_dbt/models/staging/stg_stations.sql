{{
    config(
        materialized='view'
    )
}}

select
    station_id,
    name as station_name,
    latitude,
    longitude
from {{ ref('stations') }}
