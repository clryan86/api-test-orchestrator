import httpx

from engine.runner import RunnerConfig, SuiteRunner


def handler(request: httpx.Request) -> httpx.Response:
    if request.method == 'POST' and request.url.path == '/users':
        return httpx.Response(201, json={'id': 42, 'name': 'Aisha'}, headers={'x-service': 'demo'})
    if request.method == 'GET' and request.url.path == '/users/42':
        return httpx.Response(200, json={'id': 42, 'name': 'Aisha', 'roles': ['admin', 'user']})
    return httpx.Response(404, json={'error': 'not found'})


def test_runner_executes_multistep_suite_with_extraction():
    runner = SuiteRunner(RunnerConfig(allowed_hosts=('api.example.test',)), transport=httpx.MockTransport(handler))
    result = runner.run_suite({
        'name': 'User flow',
        'base_url': 'https://api.example.test',
        'cases': [
            {'name': 'Create', 'method': 'POST', 'path': '/users', 'assertions': [{'type': 'status', 'value': 201}, {'type': 'json_exists', 'path': 'id'}], 'extract': {'user_id': 'id'}},
            {'name': 'Read', 'path': '/users/{{user_id}}', 'assertions': [{'type': 'status', 'value': 200}, {'type': 'json_contains', 'path': 'roles', 'value': 'admin'}]},
        ],
    })
    assert result['success'] is True
    assert result['variables']['user_id'] == 42
    assert result['passed'] == 2


def test_runner_surfaces_failed_assertion():
    runner = SuiteRunner(transport=httpx.MockTransport(handler))
    result = runner.run_suite({'name': 'Failure', 'base_url': 'https://api.example.test', 'cases': [{'name': 'Wrong status', 'path': '/users/42', 'assertions': [{'type': 'status', 'value': 201}]}]})
    assert result['success'] is False
    assert result['failed'] == 1
