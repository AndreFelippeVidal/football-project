with

source as (

    select * from {{ source('raw_football', 'competitions_standings') }}

),

raw_football_competitions_standings as (

    select

        ----------  ids
        id,
        competition_id,

        ---------- Normalized Columns
        team->>'id' as team_id,
        team->>'tla' as team_tla,
        team->>'short_name' as team_short_name,
        team->>'crest' as team_crest,


        ---------- text
        form,


        ---------- json
        season_info,
        

        ---------- numerics
        season,
        position,
        played_games,
        won,
        draw,
        lost,
        points,
        goals_for,
        goals_against,
        goal_difference,

        ---------- timestamps
        load_timestamp

    from source

)

select * from raw_football_competitions_standings