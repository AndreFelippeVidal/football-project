with

source as (

    select * from {{ source('raw_football', 'teams') }}

),

raw_football_teams as (

    select

        ----------  ids
        id,
        competition_id,
        team_id,

        ---------- text
        name as team_name,
        short_name as team_short_name,
        tla,
        crest,
        address,
        website,
        club_colors,
        venue,

        ---------- json
        area,
        running_competitions,
        coach,
        staff,
        squad,

        ---------- numerics
        founded,

        ---------- timestamps
        last_updated as last_updated_in_source,
        load_timestamp

    from source

)

select * from raw_football_teams