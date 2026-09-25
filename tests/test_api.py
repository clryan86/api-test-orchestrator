from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={'ok': True, 'value': 7})


def test_api_executes_and_persists_run(tmp_path: Path):
    settings = Settings(database_path=tmp_path / 'runs.db', allowed_hosts=('api.example.test',))
    client = TestClient(create_app(settings, transport=httpx.MockTransport(handler)))
    suite = {'name': 'Health contract', 'base_url': 'https://api.example.test', 'cases': [{'name': 'Health', 'path': '/health', 'assertions': [{'type': 'status', 'value': 200}, {'type': 'json_equals', 'path': 'ok', 'value': True}]}]}
    response = client.post('/api/run', json={'suite': suite})
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert response.json()['run_id'] == 1
    assert client.get('/api/runs').json()[0]['suite_name'] == 'Health contract'
    metrics = client.get('/api/metrics').json()
    assert metrics['run_count'] == 1
    assert metrics['passed_runs'] == 1


def test_api_rejects_non_allowlisted_target(tmp_path: Path):
    settings = Settings(database_path=tmp_path / 'runs.db', allowed_hosts=('allowed.test',))
    client = TestClient(create_app(settings, transport=httpx.MockTransport(handler)))
    response = client.post('/api/run', json={'suite': {'name': 'Bad', 'base_url': 'https://blocked.test', 'cases': []}})
    assert response.status_code == 422
