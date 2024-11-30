with

teams as (

    select * from {{ ref('stg_fb__teams') }}

),

competitions as (

    select * from {{ ref('stg_fb__competitions') }}

),

competitions_summary as (

    select
        t.competition_id,
        c.competition_name,

        count(t.team_id) as teams_count,
        max(t.last_updated_in_source) as last_updated_in_source
        
    from teams t 
         inner join competitions c 
             on t.competition_id = c.competition_id

    group by 1, 2
    order by 3 desc

)

select * from competitions_summary