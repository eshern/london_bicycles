{{
    config(
        materialized='table'
    )
}}

select
    trip_date,
    start_hour,
    count(distinct trip_id) as num_trips,
    avg(duration_minutes) as avg_trip_duration_minutes,
    min(duration_minutes) as min_trip_duration_minutes,
    max(duration_minutes) as max_trip_duration_minutes,
    count(distinct bike_id) as num_unique_bikes,
    count(distinct user_type) as num_user_types
from {{ ref('stg_trips') }}
group by trip_date, start_hour
order by trip_date, start_hour
