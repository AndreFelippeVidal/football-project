WITH running_competitions_data AS (
    SELECT
        team_id,
        running_competitions->>'id' AS competition_id,
        running_competitions->>'code' AS competition_code,
        running_competitions->>'name' AS competition_name,
        running_competitions->>'type' AS competition_type,
        running_competitions->>'emblem' AS competition_emblem
    FROM
        {{ ref('stg_fb__teams') }},
        jsonb_array_elements(squad) AS running_competitions
)

SELECT * FROM running_competitions_data
