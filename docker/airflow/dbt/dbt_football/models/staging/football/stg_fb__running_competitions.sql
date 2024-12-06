WITH running_competitions_data AS (
    SELECT
        team_id,
        comp_data->>'id' AS competition_id,
        comp_data->>'code' AS competition_code,
        comp_data->>'name' AS competition_name,
        comp_data->>'type' AS competition_type,
        comp_data->>'emblem' AS competition_emblem
    FROM
        {{ ref('stg_fb__teams') }},
        jsonb_array_elements(running_competitions) AS comp_data
)

SELECT distinct team_id,
       competition_id,
       competition_code,
       competition_name,
       competition_type,
       competition_emblem
FROM running_competitions_data
