with

source as (

    select * from {{ source('raw_football', 'competitions') }}

),

raw_football_competitions as (

    select

        ----------  ids
        id as competition_id,

        ---------- text
        name as competition_name,
        code,
        type,
        emblem,
        plan,

        ---------- json
        area,
        current_season,

        ---------- numerics
        number_of_available_seasons,

        ---------- timestamps
        last_updated as last_updated_in_source,
        load_timestamp

    from source

)

select * from raw_football_competitions