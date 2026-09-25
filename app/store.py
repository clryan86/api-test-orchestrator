from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


class RunStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS runs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suite_name TEXT NOT NULL,
                passed INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                total INTEGER NOT NULL,
                success INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )''')

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def save(self, result: dict[str, Any]) -> int:
        with self.connection() as conn:
            cur = conn.execute(
                'INSERT INTO runs(suite_name,passed,failed,total,success,duration_ms,result_json,created_at) VALUES(?,?,?,?,?,?,?,?)',
                (result['suite_name'], result['passed'], result['failed'], result['total'], int(result['success']), result['duration_ms'], json.dumps(result), datetime.now(timezone.utc).isoformat()),
            )
            return int(cur.lastrowid)

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute('SELECT * FROM runs ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        return [self._row(row) for row in rows]

    def get(self, run_id: int) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute('SELECT * FROM runs WHERE id=?', (run_id,)).fetchone()
        return self._row(row) if row else None

    @staticmethod
    def _row(row):
        item = dict(row)
        item['result'] = json.loads(item.pop('result_json'))
        item['success'] = bool(item['success'])
        return item
