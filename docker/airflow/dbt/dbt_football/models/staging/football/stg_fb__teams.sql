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
        area->>'id' as team_area_id,
  		area->>'code' as team_area_code,
  		area->>'flag' as team_area_flag,
  		area->>'name'  as team_area_name,

        ---------- text
        name as team_name,
        short_name as team_short_name,
        tla,
        crest,
        address,
        website,
        club_colors,
        venue,
        coach->>'id' as coach_id,
		coach->>'name' as coach_name,
        coach->'contract'->>'start' as coach_contract_start,
        coach->'contract'->>'until' as coach_contract_end,
		coach->>'first_name' as coach_first_name,
		coach->>'last_name' as coach_last_name,
		coach->>'nationality' as coach_nationality,
		coach->>'date_of_birth' as coach_date_of_birth,

        ---------- json
        running_competitions,
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