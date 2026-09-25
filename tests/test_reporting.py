from pathlib import Path

from engine.reporting import write_junit


def test_write_junit(tmp_path: Path):
    result = {'suite_name': 'Demo', 'total': 1, 'failed': 0, 'duration_ms': 12, 'cases': [{'name': 'Case', 'passed': True, 'elapsed_ms': 10, 'assertions': [], 'error': None}]}
    target = tmp_path / 'report.xml'
    write_junit(result, target)
    text = target.read_text()
    assert '<testsuite' in text
    assert 'Demo' in text
