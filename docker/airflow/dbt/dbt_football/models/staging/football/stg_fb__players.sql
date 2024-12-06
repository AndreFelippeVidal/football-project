WITH players_data AS (
    SELECT
        team_id,
        player_data->>'id' AS player_id,
        player_data->>'name' AS player_name,
        player_data->>'position' AS player_position,
        player_data->>'nationality' AS player_nationality,
        player_data->>'date_of_birth' AS player_date_of_birth
    FROM
        {{ ref('stg_fb__teams') }},
        jsonb_array_elements(squad) AS player_data
)

SELECT distinct team_id,
        player_id,
        player_name,
        player_position,
        player_nationality,
        player_date_of_birth
    FROM players_data
