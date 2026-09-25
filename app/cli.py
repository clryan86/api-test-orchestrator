from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.reporting import write_junit
from engine.runner import RunnerConfig, SuiteRunner


def main() -> None:
    parser = argparse.ArgumentParser(description='Run declarative API test suites.')
    parser.add_argument('suite')
    parser.add_argument('--base-url')
    parser.add_argument('--junit')
    parser.add_argument('--allow-host', action='append', default=[])
    args = parser.parse_args()
    suite = json.loads(Path(args.suite).read_text(encoding='utf-8'))
    runner = SuiteRunner(RunnerConfig(allowed_hosts=tuple(args.allow_host)))
    result = runner.run_suite(suite, args.base_url)
    print(json.dumps(result, indent=2, default=str))
    if args.junit:
        write_junit(result, Path(args.junit))
    raise SystemExit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
