{{
    config(
        materialized='table'
    )
}}

select
    t.trip_id,
    t.bike_id,
    t.start_station_id,
    t.end_station_id,
    ss.station_name as start_station_name,
    es.station_name as end_station_name,
    t.start_date,
    t.end_date,
    t.trip_date,
    t.duration_minutes,
    t.start_hour,
    t.day_of_week,
    t.user_type,
    t.member_gender,
    case
        when t.duration_minutes < 15 then 'short'
        when t.duration_minutes < 30 then 'medium'
        when t.duration_minutes < 60 then 'long'
        else 'very_long'
    end as trip_duration_category
from {{ ref('stg_trips') }} t
left join {{ ref('stg_stations') }} ss on t.start_station_id = ss.station_id
left join {{ ref('stg_stations') }} es on t.end_station_id = es.station_id
