# Architecture

```mermaid
flowchart TD
    J[JSON Test Suite] --> R[Suite Runner]
    R --> T[Template Engine]
    R --> H[httpx Client]
    H --> API[Target API]
    API --> A[Assertion Engine]
    A --> X[Variable Extraction]
    X --> R
    R --> S[(SQLite Run Store)]
    R --> JUNIT[JUnit XML]
    S --> UI[FastAPI Dashboard]
```

The orchestration engine is independent of FastAPI. That allows the same runner to be used by the CLI, REST service, unit tests, or a future CI plugin.

Independent suites can execute concurrently while cases within a suite remain ordered so extracted variables are deterministic.
