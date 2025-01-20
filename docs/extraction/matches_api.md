# Matches

## Workflow (Processor + API)
```mermaid
graph TD
    A[Start] --> K[Processor]
    K --> B[MatchesProcessor]
    B --> C[Matches API]
    C --> D[API Request: Get Matches Today]
    D --> E[Matches Data Retrieved]
    E --> F[Convert to DataFrame]
    F --> G[Transform Data -JSON Columns-]
    G --> H[Add Load Timestamp]
    H --> I[Load Data to DB]
    I --> J[Database Write]
    
    C --> Q[Logging]

```

??? info "MatchesAPI Class"
    ::: src.utils.matches_api.MatchesAPI
        options:
            filters: []
            group_by_category: true
            members_order: source

??? info "MatchesProcessor Class"
    ::: src.utils.matches_api.MatchesProcessor
        options:
            filters: []
            group_by_category: true
            members_order: source

## Queries
??? info "Create Queries - Schema"
    ```sql
    --8<-- "src/utils/queries/create_queries.py"
    ```