# Interview Guide

## 30-second explanation

> API Test Orchestrator is a declarative QA framework I built around httpx. Test cases can assert status codes, nested JSON, headers, body content, and response times. One response can extract a variable that is templated into a later request, so it supports realistic API workflows. It also supports retries, parallel suite runs, JUnit output, history, and a target-host allowlist.

## Design decisions

**Why JSON suites?** They are language-neutral, easy to version in Git, API-friendly, and can be generated from other systems.

**Why keep the engine separate from FastAPI?** The runner is the product; the web service is only one adapter. Separation makes CLI/CI integration and testing straightforward.

**Why MockTransport in tests?** The orchestration logic can be tested deterministically without depending on external APIs or network conditions.

**Why an allowlist?** A service that sends user-defined HTTP requests can become an SSRF primitive. Restricting hosts is an important production boundary.

## Resume bullets

- Built a declarative Python API-testing framework supporting multi-step request workflows, nested assertions, variable extraction, request templating, retries, and parallel suite execution.
- Added CI-friendly exit codes and JUnit XML generation plus persisted execution history and a FastAPI operations dashboard.
- Implemented target-host allowlisting and deterministic httpx MockTransport integration tests.
