# Competitions

## Workflow (Processor + API)
```mermaid
graph TD;
    A[Start Processing] --> B[CompetitionsProcessor Process];
    B --> C[CompetitionsAPI get_competitions];
    C --> D[Get Competitions Data];
    D --> E[Transform Data];
    E --> F[Add Metadata];
    A --> G[CompetitionDetailsProcessor Process];
    G --> C
    D --> I[Transform Details];
    I --> J[Add Metadata];
    F --> K[Write to Database]
    K --> L[End];

    subgraph API Calls
        C
    end

    subgraph Competitions Processing
        B --> E
        E --> F
    end

    subgraph CompetitionDetails Processing
        G --> I
        I --> J
    end

    subgraph Database Operations
        J --> K
    end

```

??? info "CompetitionsAPI Class"
    ::: src.utils.competitions_api.CompetitionsAPI
        options:
            filters: []
            group_by_category: true
            members_order: source

??? info "CompetitionsProcessor Class"
    ::: src.utils.competitions_api.CompetitionsProcessor
        options:
            filters: []
            group_by_category: true
            members_order: source

??? info "CompetitionsDetailsProcessor Class"
    ::: src.utils.competitions_api.CompetitionsProcessor
        options:
            filters: []
            group_by_category: true
            members_order: source

## Queries
??? info "Create Queries - Schema"
    ```sql
    --8<-- "src/utils/queries/create_queries.py"
    ```