with src as (select 'US' as region, video_id, title, channel_title, publish_time as publish_ts, cast(date(publish_time) as date) as publish_date, category_id, view_count, like_count, comment_count from {{ source('raw','youtube_mostpopular') }})
select region, video_id, title, channel_title, publish_ts, publish_date, category_id, view_count, like_count, comment_count from src
