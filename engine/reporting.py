from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def write_junit(result: dict, path: Path) -> None:
    suite = ET.Element('testsuite', {
        'name': result['suite_name'],
        'tests': str(result['total']),
        'failures': str(result['failed']),
        'time': f"{result['duration_ms'] / 1000:.6f}",
    })
    for case in result['cases']:
        node = ET.SubElement(suite, 'testcase', {
            'name': case['name'],
            'classname': result['suite_name'],
            'time': f"{case['elapsed_ms'] / 1000:.6f}",
        })
        if not case['passed']:
            failure = ET.SubElement(node, 'failure', {'message': case.get('error') or 'Assertion failure'})
            failure.text = str(case['assertions'])
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suite).write(path, encoding='utf-8', xml_declaration=True)
