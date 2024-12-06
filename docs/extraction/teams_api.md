# Teams

## API
```mermaid
graph TD
    A[TeamsAPI] --> B[get_teams]
    A --> C[get_team_by_id]
    B -->|Input: competition_id| D[Fetch Teams API Endpoint]
    C -->|Input: team_id| E[Fetch Team Details API Endpoint]

```

??? info "TeamsAPI Class"
    ::: src.utils.teams_api.TeamsAPI
        options:
            filters: []
            group_by_category: true
            members_order: source

## Processor
```mermaid
graph TD
    F[TeamsProcessor]
    F --> G[__init__]
    G -->|Input: api_connection, competition_ids, schema, table| H[Set Attributes]
    F --> I[process]
    I --> J[Log Start Processing]
    I --> K[Fetch Competition IDs from DB]
    K --> L[Loop For Each Competition ID]
    L --> M[Fetch Teams from API]
    M --> N[Transform API Response to DataFrame]
    N --> O[Add Metadata Columns]
    O --> P[Write to Database]
    F --> Q[_write_to_db]
    Q --> R[Validate or Create Table]
    R --> S[Truncate Table]
    S --> T[Bulk Insert DataFrame into DB]


```
??? info "TeamsProcessor Class"
    ::: src.utils.teams_api.TeamsProcessor
        options:
            filters: []
            group_by_category: true
            members_order: source

<!-- ## Queries
??? info "Create Queries"
    ```sql
    --8<-- "src/data_sources/vendors/hgi/queries/hgi_create_queries.py"
    ``` -->