{{
    config(
        materialized='view'
    )
}}

select
    trip_id,
    duration,
    start_station_id,
    start_station_name,
    end_station_id,
    end_station_name,
    timestamp(start_date) as start_date,
    timestamp(end_date) as end_date,
    bike_id,
    user_type,
    member_gender,
    -- Calculate trip duration in minutes for easier analysis
    round(duration / 60.0, 2) as duration_minutes,
    -- Extract date components from start_date
    date(timestamp(start_date)) as trip_date,
    extract(hour from timestamp(start_date)) as start_hour,
    extract(dayofweek from timestamp(start_date)) as day_of_week
from {{ ref('trips') }}
