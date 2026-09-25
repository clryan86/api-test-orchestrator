from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SuiteRunRequest(BaseModel):
    suite: dict[str, Any]
    base_url: str | None = None


class MultiSuiteRunRequest(BaseModel):
    suites: list[dict[str, Any]] = Field(min_length=1, max_length=50)
    base_url: str | None = None
