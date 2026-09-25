from __future__ import annotations

from typing import Any

from .utils import get_path


def evaluate_assertions(response, assertions: list[dict[str, Any]], elapsed_ms: float) -> list[dict[str, Any]]:
    results = []
    json_body = None
    for assertion in assertions:
        kind = assertion.get('type')
        passed = False
        actual: Any = None
        expected = assertion.get('value')
        detail = ''
        try:
            if kind == 'status':
                actual = response.status_code
                passed = actual == int(expected)
            elif kind == 'response_time_ms':
                actual = round(elapsed_ms, 3)
                passed = actual <= float(expected)
            elif kind in {'json_equals', 'json_exists', 'json_contains'}:
                if json_body is None:
                    json_body = response.json()
                actual = get_path(json_body, str(assertion.get('path', '')))
                if kind == 'json_equals':
                    passed = actual == expected
                elif kind == 'json_exists':
                    passed = actual is not None
                else:
                    passed = expected in actual if isinstance(actual, (list, str, dict)) else False
            elif kind == 'header_equals':
                actual = response.headers.get(str(assertion.get('header', '')))
                passed = actual == str(expected)
            elif kind == 'body_contains':
                actual = response.text
                passed = str(expected) in actual
            else:
                detail = f'Unsupported assertion type: {kind}'
        except Exception as exc:
            detail = str(exc)
        results.append({
            'type': kind,
            'passed': bool(passed),
            'actual': actual if not isinstance(actual, str) or len(actual) < 500 else actual[:500],
            'expected': expected,
            'detail': detail,
        })
    return results
