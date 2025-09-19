{{ config(materialized='table') }}
with base as (select distinct region, category_id, category_name from {{ ref('stg_youtube_categories') }})
select region, category_id, category_name from base
