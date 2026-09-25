# API Guide

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/healthz` | Service health |
| POST | `/api/run` | Execute one suite |
| POST | `/api/run-many` | Execute suites concurrently |
| GET | `/api/runs` | Test-run history |
| GET | `/api/runs/{id}` | Detailed result |
| GET | `/api/metrics` | Aggregate QA metrics |

Use `/docs` for interactive OpenAPI documentation.
