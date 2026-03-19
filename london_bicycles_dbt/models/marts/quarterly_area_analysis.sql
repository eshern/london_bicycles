{{
    config(
        materialized='table'
    )
}}

select
    extract(quarter from t.trip_date) as quarter,
    extract(year from t.trip_date) as year,
    case
        when s.latitude between 51.50 and 51.52 and s.longitude between -0.14 and -0.12 then 'Central'
        else 'Outer'
    end as station_area,
    t.user_type,
    count(distinct t.trip_id) as trip_count,
    avg(t.duration_minutes) as avg_duration_minutes,
    count(distinct t.bike_id) as unique_bikes,
    count(distinct t.start_station_id) as stations_visited
from {{ ref('stg_trips') }} t
left join {{ ref('stg_stations') }} s on t.start_station_id = s.station_id
group by
    extract(quarter from t.trip_date),
    extract(year from t.trip_date),
    station_area,
    t.user_type
order by year, quarter
