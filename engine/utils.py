from __future__ import annotations

import re
from typing import Any


def get_path(value: Any, path: str) -> Any:
    current = value
    for piece in path.split('.'):
        if isinstance(current, dict) and piece in current:
            current = current[piece]
        elif isinstance(current, list) and piece.isdigit() and int(piece) < len(current):
            current = current[int(piece)]
        else:
            return None
    return current


def render(value: Any, variables: dict[str, Any]) -> Any:
    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            key = match.group(1).strip()
            return str(variables.get(key, ''))
        return re.sub(r'\{\{\s*([\w.-]+)\s*\}\}', replace, value)
    if isinstance(value, list):
        return [render(item, variables) for item in value]
    if isinstance(value, dict):
        return {key: render(item, variables) for key, item in value.items()}
    return value
