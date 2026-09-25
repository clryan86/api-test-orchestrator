from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

from .assertions import evaluate_assertions
from .utils import get_path, render


@dataclass
class RunnerConfig:
    timeout_seconds: float = 10.0
    max_workers: int = 4
    allowed_hosts: tuple[str, ...] = ()


class SuiteRunner:
    def __init__(self, config: RunnerConfig | None = None, transport=None):
        self.config = config or RunnerConfig()
        self.transport = transport

    def run_suite(self, suite: dict[str, Any], base_url: str | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        variables = deepcopy(suite.get('variables', {}))
        resolved_base = base_url or suite.get('base_url', '')
        self._validate_base_url(resolved_base)
        cases = suite.get('cases', [])
        results: list[dict[str, Any]] = []
        for case in cases:
            result = self._run_case(case, resolved_base, variables)
            results.append(result)
            for key, path in case.get('extract', {}).items():
                if result.get('response_json') is not None:
                    value = get_path(result['response_json'], path)
                    if value is not None:
                        variables[key] = value
            if not result['passed'] and suite.get('stop_on_failure'):
                break
        passed = sum(1 for item in results if item['passed'])
        return {
            'suite_name': suite.get('name', 'Unnamed Suite'),
            'passed': passed,
            'failed': len(results) - passed,
            'total': len(results),
            'success': len(results) == passed,
            'duration_ms': round((time.perf_counter() - started) * 1000, 3),
            'variables': variables,
            'cases': results,
        }

    def run_many(self, suites: list[dict[str, Any]], base_url: str | None = None) -> list[dict[str, Any]]:
        workers = min(max(1, self.config.max_workers), max(1, len(suites)))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self.run_suite, suite, base_url) for suite in suites]
            return [future.result() for future in as_completed(futures)]

    def _run_case(self, case: dict[str, Any], base_url: str, variables: dict[str, Any]) -> dict[str, Any]:
        method = str(case.get('method', 'GET')).upper()
        path = str(render(case.get('path', '/'), variables))
        url = urljoin(base_url.rstrip('/') + '/', path.lstrip('/'))
        headers = render(case.get('headers', {}), variables)
        params = render(case.get('params', {}), variables)
        json_body = render(case.get('json'), variables)
        retries = max(0, min(int(case.get('retries', 0)), 3))
        last_error = None
        response = None
        elapsed_ms = 0.0
        attempts = 0
        for attempts in range(1, retries + 2):
            try:
                started = time.perf_counter()
                with httpx.Client(timeout=self.config.timeout_seconds, transport=self.transport) as client:
                    response = client.request(method, url, headers=headers, params=params, json=json_body)
                elapsed_ms = (time.perf_counter() - started) * 1000
                last_error = None
                break
            except Exception as exc:
                last_error = str(exc)
                if attempts <= retries:
                    time.sleep(0.05 * attempts)
        if response is None:
            return {
                'name': case.get('name', path), 'method': method, 'url': url, 'passed': False,
                'attempts': attempts, 'status_code': None, 'elapsed_ms': elapsed_ms,
                'assertions': [], 'error': last_error, 'response_json': None,
            }
        assertions = evaluate_assertions(response, case.get('assertions', []), elapsed_ms)
        passed = all(item['passed'] for item in assertions)
        try:
            response_json = response.json()
        except Exception:
            response_json = None
        return {
            'name': case.get('name', path), 'method': method, 'url': url, 'passed': passed,
            'attempts': attempts, 'status_code': response.status_code, 'elapsed_ms': round(elapsed_ms, 3),
            'assertions': assertions, 'error': None, 'response_json': response_json,
        }

    def _validate_base_url(self, base_url: str) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme not in {'http', 'https'} or not parsed.hostname:
            raise ValueError('base_url must be an http/https URL')
        if self.config.allowed_hosts and parsed.hostname.lower() not in self.config.allowed_hosts:
            raise ValueError('base_url host is not allowlisted')
