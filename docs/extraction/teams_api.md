# Teams

## Workflow (Processor + API)
```mermaid
graph TD
    A[Start]  --> C[TeamsProcessor]
    C --> C1[process]
    C1 --> C2[Fetch teams data from API]
    C2 --> B[TeamsAPI]
    B --> B1[get_teams]
    B --> B2[get_team_by_id]
    B --> B3[get_team_upcoming_matches]
    B1 --> C3[Transform data using TeamsResponse]
    B2 --> C3
    B3 --> C3
    C3 --> C4[Load data into database]
    
    A --> D[TeamUpcomingMatchesProcessor]
    D --> D1[process]
    D1 --> D2[Fetch upcoming matches from API]
    D2 --> B
    B1 --> D3[Transform match data using MatchesTodayResponse]
    B2 --> D3
    B3 --> D3
    D3 --> D4[Load matches into database]

```

??? info "TeamsAPI Class"
    ::: src.utils.teams_api.TeamsAPI
        options:
            filters: []
            group_by_category: true
            members_order: source

??? info "TeamsProcessor Class"
    ::: src.utils.teams_api.TeamsProcessor
        options:
            filters: []
            group_by_category: true
            members_order: source

??? info "TeamsUpcomingMatchesProcessor Class"
    ::: src.utils.teams_api.TeamUpcomingMatchesProcessor
        options:
            filters: []
            group_by_category: true
            members_order: source

## Queries
??? info "Create Queries - Schema"
    ```sql
    --8<-- "src/utils/queries/create_queries.py"
    ```