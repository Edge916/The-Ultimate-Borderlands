"""Run repository syntax, unique inert tests and the unchanged package verifier."""
import argparse
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTAX_DIRS = ('sdk_mods/UltimateVaultHunterDeathtrapBoost', 'scripts', 'tests', 'design')


def contained(root, path):
    # Windows managed workspaces can read files but deny strict handle resolution.
    # Normal resolution still resolves accessible symlinks and normalizes .. .
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError('repository path escapes root: ' + str(path))
    return resolved


def syntax_check(root):
    count, errors = 0, []
    for directory in SYNTAX_DIRS:
        folder = root / directory
        if not folder.exists():
            continue
        for path in sorted(folder.rglob('*.py')):
            try:
                contained(root, path)
                compile(path.read_bytes(), str(path), 'exec')
                count += 1
            except (OSError, SyntaxError, ValueError) as exc:
                errors.append(str(path.relative_to(root)) + ': ' + str(exc))
    return {'compiled_files': count, 'errors': errors, 'status': 'FAIL' if errors else 'PASS'}


def unique_cases(suite):
    cases = []
    def visit(item):
        if isinstance(item, unittest.TestSuite):
            for child in item:
                visit(child)
        else:
            cases.append(item)
    visit(suite)
    seen = set()
    for case in cases:
        ident = case.id()
        if ident in seen:
            raise ValueError('duplicate test ID: ' + ident)
        seen.add(ident)
    if not cases:
        raise ValueError('no tests discovered')
    return cases


def test_check(root, stream, verbosity=1):
    loader = unittest.TestLoader()
    original_path = sys.path[:]
    try:
        directory = contained(root, root / 'tests')
        suite = loader.discover(str(directory), pattern='test_*.py', top_level_dir=str(directory))
        if loader.errors:
            raise ValueError('test discovery failed: ' + '\n'.join(loader.errors))
        cases = unique_cases(suite)
        result = unittest.TextTestRunner(stream=stream, verbosity=verbosity).run(suite)
        complete = result.testsRun == len(cases)
        passed = result.wasSuccessful() and not result.skipped and not result.expectedFailures and complete
        return {'status': 'PASS' if passed else 'FAIL', 'unique_tests': len(cases),
                'tests_run': result.testsRun, 'failures': len(result.failures),
                'errors': len(result.errors), 'skips': len(result.skipped),
                'unexpected_successes': len(result.unexpectedSuccesses),
                'expected_failures': len(result.expectedFailures), 'all_discovered_run': complete}
    except (OSError, ValueError, ImportError) as exc:
        return {'status': 'FAIL', 'discovery_error': str(exc), 'tests_run': 0}
    finally:
        sys.path[:] = original_path


def package_check(root):
    try:
        verifier = contained(root, root / 'scripts/verify_package.py')
        result = subprocess.run([sys.executable, '-B', str(verifier)], cwd=root,
                                capture_output=True, text=True, timeout=60)
        return {'status': 'PASS' if result.returncode == 0 else 'FAIL',
                'exit_code': result.returncode, 'stdout': result.stdout[-4000:],
                'stderr': result.stderr[-4000:]}
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return {'status': 'FAIL', 'error': str(exc)}


def run_validation(root=ROOT, stream=None, verbosity=1):
    """Only trusted repository tests execute; SDK stubs/archives are not discovered."""
    root = Path(root).resolve()
    stream = sys.stderr if stream is None else stream
    start = time.monotonic()
    report = {'schema_version': 1, 'python': sys.version.split()[0],
              'interpreter': sys.executable, 'scope': 'offline repository checks',
              'engine_behavior': 'NOT_ESTABLISHED', 'hosted_CI': 'NOT_CHECKED'}
    old_temp, old_bytecode = tempfile.tempdir, sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        report['syntax'] = syntax_check(root)
        if report['syntax']['status'] == 'FAIL':
            report['tests'] = {'status': 'NOT_RUN', 'reason': 'syntax failed before discovery'}
        else:
            with tempfile.TemporaryDirectory(prefix='uvh_offline_', dir=root) as workspace_temp:
                tempfile.tempdir = workspace_temp
                report['tests'] = test_check(root, stream, verbosity)
        report['package'] = package_check(root)
    finally:
        tempfile.tempdir = old_temp
        sys.dont_write_bytecode = old_bytecode
    report['seconds'] = round(time.monotonic() - start, 3)
    report['status'] = ('PASS' if all(report[section]['status'] == 'PASS'
                                    for section in ('syntax', 'tests', 'package')) else 'FAIL')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verbose', action='store_true', help='show each unique unittest ID')
    args = parser.parse_args(argv)
    try:
        report = run_validation(verbosity=2 if args.verbose else 1)
    except (OSError, ValueError) as exc:
        report = {'status': 'FAIL', 'error': str(exc), 'engine_behavior': 'NOT_ESTABLISHED'}
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
