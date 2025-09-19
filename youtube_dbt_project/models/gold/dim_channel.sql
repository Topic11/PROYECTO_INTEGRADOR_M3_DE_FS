{{ config(materialized='table') }}
with base as (select distinct m.region, m.channel_title from {{ ref('stg_youtube_mostpopular') }} m where m.channel_title is not null)
select region, channel_title from base
