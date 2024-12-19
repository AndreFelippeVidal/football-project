with

source as (

    select * from {{ source('raw_football', 'matches_today') }}

),

raw_football_matches_today as (

    select

        ----------  ids
        id,


        ---------- Normalized Columns
        area->>'id' as match_area_id,
  		area->>'code' as match_area_code,
  		area->>'flag' as match_area_flag,
  		area->>'name'  as match_area_name,
        competition->>'id' as competition_id,
        competition->>'code' as competition_code,
        competition->>'name' as competition_name,
        competition->>'type' as competition_type,
        competition->>'emblem' as competition_emblem,
        home_team->>'id' as home_team_id,
        home_team->>'tla' as home_team_tla,
        home_team->>'short_name' as home_team_short_name,
        home_team->>'crest' as home_team_crest,
        away_team->>'id' as away_team_id,
        away_team->>'tla' as away_team_tla,
        away_team->>'short_name' as away_team_short_name,
        away_team->>'crest' as away_team_crest,
        score->>'winner' as match_winner,
        score->>'duration' as match_duration,
        score->>'full_time' as final_score,
        score->>'half_time' as half_time_score,
        score->'full_time'->>'home' as home_final_score,
        score->'full_time'->>'away' as away_final_score,

        ---------- text
        status,
        stage,
        which_group,


        ---------- json
        season,
        odds,
        referees,

        ---------- numerics
        matchday,

        ---------- timestamps
        utc_date,
        last_updated as last_updated_in_source,
        date_from,
        load_timestamp

    from source

)

select * from raw_football_matches_today