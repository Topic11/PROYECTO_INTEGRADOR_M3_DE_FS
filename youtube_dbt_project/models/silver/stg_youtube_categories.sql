with src as (select 'US' as region, category_id, category_name from {{ source('raw','youtube_categories') }})
select region, category_id, category_name from src where category_name is not null
