from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from engine.runner import RunnerConfig, SuiteRunner

from .config import Settings
from .schemas import MultiSuiteRunRequest, SuiteRunRequest
from .store import RunStore

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = Jinja2Templates(directory=str(ROOT / 'templates'))


def create_app(settings: Settings | None = None, transport=None) -> FastAPI:
    settings = settings or Settings.from_env()
    runner = SuiteRunner(RunnerConfig(timeout_seconds=settings.timeout_seconds, allowed_hosts=settings.allowed_hosts), transport=transport)
    store = RunStore(settings.database_path)
    app = FastAPI(title=settings.app_name, version='1.0.0', description='Declarative API test suites, assertions, extraction, retries, parallel execution and run history.')
    app.state.runner = runner
    app.state.store = store
    app.mount('/static', StaticFiles(directory=str(ROOT / 'static')), name='static')

    @app.get('/healthz')
    def healthz():
        return {'ok': True, 'service': settings.app_name}

    @app.get('/', response_class=HTMLResponse)
    def dashboard(request: Request):
        runs = store.list(20)
        total = len(store.list(1000))
        passing = sum(1 for item in runs if item['success'])
        pass_rate = round(passing / len(runs) * 100, 1) if runs else 0
        return TEMPLATES.TemplateResponse(request=request, name='index.html', context={'app_name': settings.app_name, 'runs': runs, 'metrics': {'total': total, 'recent_pass_rate': pass_rate}})

    @app.get('/runs/{run_id}', response_class=HTMLResponse)
    def run_page(run_id: int, request: Request):
        run = store.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail='Run not found')
        return TEMPLATES.TemplateResponse(request=request, name='run.html', context={'app_name': settings.app_name, 'run': run})

    @app.post('/api/run')
    def run_suite(payload: SuiteRunRequest):
        try:
            result = runner.run_suite(payload.suite, payload.base_url)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        run_id = store.save(result)
        return {'run_id': run_id, **result}

    @app.post('/api/run-many')
    def run_many(payload: MultiSuiteRunRequest):
        try:
            results = runner.run_many(payload.suites, payload.base_url)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        return [{'run_id': store.save(result), **result} for result in results]

    @app.get('/api/runs')
    def runs(limit: int = 50):
        return store.list(max(1, min(limit, 200)))

    @app.get('/api/runs/{run_id}')
    def run_detail(run_id: int):
        run = store.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail='Run not found')
        return run

    @app.get('/api/metrics')
    def metrics():
        runs = store.list(1000)
        return {
            'run_count': len(runs),
            'passed_runs': sum(1 for item in runs if item['success']),
            'failed_runs': sum(1 for item in runs if not item['success']),
            'total_cases': sum(item['total'] for item in runs),
            'failed_cases': sum(item['failed'] for item in runs),
        }

    return app


app = create_app()
