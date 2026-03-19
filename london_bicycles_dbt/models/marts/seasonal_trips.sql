{{
    config(
        materialized='table'
    )
}}

select
    extract(month from t.trip_date) as month,
    extract(year from t.trip_date) as year,
    case
        when extract(month from t.trip_date) = 1 then 'January'
        when extract(month from t.trip_date) = 2 then 'February'
        when extract(month from t.trip_date) = 3 then 'March'
        when extract(month from t.trip_date) = 4 then 'April'
        when extract(month from t.trip_date) = 5 then 'May'
        when extract(month from t.trip_date) = 6 then 'June'
        when extract(month from t.trip_date) = 7 then 'July'
        when extract(month from t.trip_date) = 8 then 'August'
        when extract(month from t.trip_date) = 9 then 'September'
        when extract(month from t.trip_date) = 10 then 'October'
        when extract(month from t.trip_date) = 11 then 'November'
        when extract(month from t.trip_date) = 12 then 'December'
    end as month_name,
    count(distinct t.trip_id) as total_trips,
    count(distinct t.bike_id) as unique_bikes,
    count(distinct t.user_type) as user_type_count,
    avg(t.duration_minutes) as avg_trip_duration_minutes,
    min(t.duration_minutes) as min_trip_duration_minutes,
    max(t.duration_minutes) as max_trip_duration_minutes,
    count(case when t.user_type = 'Subscriber' then 1 end) as subscriber_trips,
    count(case when t.user_type = 'Casual' then 1 end) as casual_trips
from {{ ref('stg_trips') }} t
group by 
    extract(month from t.trip_date),
    extract(year from t.trip_date),
    month_name
order by year, month
