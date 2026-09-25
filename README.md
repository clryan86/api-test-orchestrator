# API Test Orchestrator

[![CI](https://github.com/clryan86/api-test-orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/clryan86/api-test-orchestrator/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![QA](https://img.shields.io/badge/QA-API%20automation-48B0F1)
![httpx](https://img.shields.io/badge/httpx-client-7C4DFF)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)

A declarative API QA platform for building repeatable multi-step test suites with assertions, variable extraction, request templating, retries, parallel suite execution, JUnit reporting, and persisted run history.

## Why this exists

Professional API testing is more than checking one status code. Integration tests often need to create a resource, extract an identifier, call a second endpoint, validate nested JSON, enforce response-time expectations, retry transient network errors, and publish CI-readable reports. This project models that workflow directly.

## Capabilities

- JSON-defined suites
- GET/POST/PUT/PATCH/DELETE support through httpx
- status-code assertions
- response-time assertions
- nested JSON equality/existence/containment assertions
- header and body assertions
- value extraction from one response into later requests
- `{{variable}}` templating
- bounded retries
- stop-on-failure mode
- parallel execution of independent suites
- JUnit XML reports
- SQLite run history
- operations dashboard
- destination hostname allowlist
- CLI and REST interfaces

## Example suite

```json
{
  "name": "Users API Contract",
  "base_url": "https://api.example.test",
  "cases": [
    {
      "name": "Create user",
      "method": "POST",
      "path": "/users",
      "assertions": [
        {"type": "status", "value": 201},
        {"type": "json_exists", "path": "id"}
      ],
      "extract": {"user_id": "id"}
    },
    {
      "name": "Read user",
      "path": "/users/{{user_id}}",
      "assertions": [
        {"type": "status", "value": 200}
      ]
    }
  ]
}
```

## CLI

```bash
python -m app.cli suites/demo.json --allow-host api.example.test --junit reports/demo.xml
```

Exit code is `0` for a passing suite and `1` for a failing suite, making the CLI CI-friendly.

## API

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `/docs` for the generated OpenAPI interface.

## Tests

```bash
pytest
ruff check .
```

The test suite uses `httpx.MockTransport`, so API orchestration behavior is exercised deterministically without reaching external services.

## Security

The runner validates HTTP(S) base URLs and supports a hostname allowlist. Production deployments should always configure an allowlist to reduce SSRF risk when users can submit suites.

## Roadmap

- OpenAPI contract import
- JSON Schema assertions
- OAuth/API-key secret references
- HTML report export
- flaky-test quarantine
- baseline performance thresholds
- environment profiles
- WebSocket testing
- Playwright browser/API hybrid suites
- GitHub PR annotations

## Author

**Christopher Ryan**  
Python • QA Automation • Backend • CI/CD

## License

MIT
