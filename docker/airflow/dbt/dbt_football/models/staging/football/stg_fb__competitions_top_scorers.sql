with

source as (

    select * from {{ source('raw_football', 'competitions_top_scorers') }}

),

raw_football_competitions_top_scorers as (

    select

        ----------  ids
        id,
        competition_id,

        ---------- Normalized Columns
        player->>'id' as player_id,
  		player->>'name' as player_name,
  		player->>'section' as player_section,
  		player->>'position'  as player_position,
        player->>'last_name'  as player_last_name,
        player->>'first_name'  as player_first_name,
        player->>'nationality'  as player_nationality,
        player->>'last_updated'  as player_last_updated,
        player->>'shirt_number'  as player_shirt_number,
        player->>'date_of_birth'  as player_date_of_birth,
        team->>'id' as team_id,
        team->>'tla' as team_tla,
        team->>'short_name' as team_short_name,
        team->>'crest' as team_crest,

        ---------- json
        season_info,

        ---------- numerics
        season,
        played_matches,
        goals,
        assists,
        penalties,

        ---------- timestamps
        load_timestamp

    from source

)

select * from raw_football_competitions_top_scorers