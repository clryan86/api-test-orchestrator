from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path
    allowed_hosts: tuple[str, ...] = ()
    timeout_seconds: float = 10.0
    app_name: str = 'API Test Orchestrator'

    @classmethod
    def from_env(cls) -> 'Settings':
        root = Path(__file__).resolve().parents[1]
        hosts = tuple(item.strip().lower() for item in os.getenv('ALLOWED_HOSTS', '').split(',') if item.strip())
        return cls(
            database_path=Path(os.getenv('DATABASE_PATH', root / 'data' / 'runs.db')),
            allowed_hosts=hosts,
            timeout_seconds=float(os.getenv('TIMEOUT_SECONDS', '10')),
        )
