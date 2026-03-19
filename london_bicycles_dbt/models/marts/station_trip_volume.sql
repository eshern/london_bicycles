{{
    config(
        materialized='table'
    )
}}

select
    t.start_station_id,
    t.start_station_name,
    s.latitude,
    s.longitude,
    count(distinct t.trip_id) as total_trips,
    count(distinct t.bike_id) as unique_bikes_used,
    avg(t.duration_minutes) as avg_trip_duration_minutes,
    min(t.duration_minutes) as min_trip_duration_minutes,
    max(t.duration_minutes) as max_trip_duration_minutes,
    count(distinct case when t.user_type = 'Subscriber' then t.trip_id end) as subscriber_trip_count,
    count(distinct case when t.user_type = 'Casual' then t.trip_id end) as casual_trip_count,
    round(100.0 * count(distinct case when t.user_type = 'Subscriber' then t.trip_id end) / 
          count(distinct t.trip_id), 2) as subscriber_trip_percentage,
    -- Rank stations by total trips
    rank() over (order by count(distinct t.trip_id) desc) as station_trip_volume_rank
from {{ ref('stg_trips') }} t
left join {{ ref('stg_stations') }} s on t.start_station_id = s.station_id
group by
    t.start_station_id,
    t.start_station_name,
    s.latitude,
    s.longitude
order by total_trips desc
