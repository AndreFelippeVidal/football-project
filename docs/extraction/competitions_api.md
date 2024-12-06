# Competitions

## API
```mermaid
graph TD
    A[CompetitionsAPI] --> B[Get Competitions by Plan]
    A --> C[Get Competition by ID]
    A --> D[Get Matches by Competition ID]
    B --> E[API Request to Competitions Endpoint]
    C --> F[API Request to Competitions by ID Endpoint]
    D --> G[Paginated API Request to Matches Endpoint]

```

??? info "CompetitionsAPI Class"
    ::: src.utils.competitions_api.CompetitionsAPI
        options:
            filters: []
            group_by_category: true
            members_order: source

## Processor
```mermaid
graph TD
    A[CompetitionsProcessor] --> B[Process Data]
    B --> C[Fetch Competitions Data]
    C --> D[Transform to DataFrame]
    D --> E[Add Metadata Columns]
    E --> F[Write Data to Database]
    F --> G[Check if Table Exists]
    F --> H[Insert Data into Table]

```
??? info "CompetitionsProcessor Class"
    ::: src.utils.competitions_api.CompetitionsProcessor
        options:
            filters: []
            group_by_category: true
            members_order: source

<!-- ## Queries
??? info "Create Queries"
    ```sql
    --8<-- "src/data_sources/vendors/hgi/queries/hgi_create_queries.py"
    ``` -->