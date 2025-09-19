{{ config(materialized='table') }}
select distinct publish_date as date, extract(year from publish_date) as year, extract(month from publish_date) as month, format_date('%Y-%m', publish_date) as yyyymm from {{ ref('stg_youtube_mostpopular') }} where publish_date is not null
