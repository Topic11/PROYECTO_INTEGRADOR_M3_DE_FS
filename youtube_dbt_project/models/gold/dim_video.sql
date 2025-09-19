{{ config(materialized='table') }}
with ranked as (select m.video_id, any_value(m.title) as title, any_value(m.channel_title) as channel_title, any_value(m.region) as region, min(m.publish_ts) as publish_ts, min(m.publish_date) as publish_date, any_value(m.category_id) as category_id from {{ ref('stg_youtube_mostpopular') }} m group by m.video_id)
select video_id, title, channel_title, region, publish_ts, publish_date, category_id from ranked
