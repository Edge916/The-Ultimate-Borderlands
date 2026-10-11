"""Validation failures are exercised in inert temporary repositories."""
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('offline_runner', ROOT / 'scripts/run_offline_validation.py')
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class OfflineValidationRunnerTests(unittest.TestCase):
    def fixture(self, body):
        temporary = tempfile.TemporaryDirectory(prefix='validation_fixture_')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / 'tests').mkdir()
        (root / 'scripts').mkdir()
        (root / 'dist').mkdir()
        module_name = 'test_probe_' + uuid.uuid4().hex
        (root / 'tests' / (module_name + '.py')).write_text(body, encoding='utf-8')
        self.addCleanup(sys.modules.pop, module_name, None)
        (root / 'scripts/verify_package.py').write_text(
            "from pathlib import Path\nfrom zipfile import ZipFile\n"
            "with ZipFile(Path(__file__).parents[1] / 'dist/probe.zip') as z:\n"
            "    assert z.testzip() is None\n"
            "    assert z.namelist() == ['payload.txt']\n"
            "    assert z.read('payload.txt') == b'inert'\n", encoding='utf-8')
        with ZipFile(root / 'dist/probe.zip', 'w') as z:
            z.writestr('payload.txt', b'inert')
        return root

    def check(self, root):
        return runner.run_validation(root, stream=io.StringIO())

    def test_pass_counts_actual_discovery_and_validates_package(self):
        root = self.fixture('import unittest\nclass Checks(unittest.TestCase):\n'
                            ' def test_one(self): self.assertEqual(1, 1)\n'
                            ' def test_two(self): self.assertTrue(True)\n')
        report = self.check(root)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['tests']['unique_tests'], 2)
        self.assertEqual(report['tests']['tests_run'], 2)
        self.assertEqual(report['package']['exit_code'], 0)
        self.assertEqual(report['hosted_CI'], 'NOT_CHECKED')
        self.assertEqual(report['engine_behavior'], 'NOT_ESTABLISHED')

    def test_empty_suite_fails_instead_of_green_zero_tests(self):
        report = self.check(self.fixture('VALUE = 1\n'))
        self.assertEqual(report['status'], 'FAIL')
        self.assertIn('no tests discovered', report['tests']['discovery_error'])

    def test_failed_test_produces_failed_validation(self):
        root = self.fixture('import unittest\nclass Checks(unittest.TestCase):\n'
                            ' def test_one(self): self.fail("intended failure")\n')
        report = self.check(root)
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['tests']['failures'], 1)

    def test_skipped_test_cannot_make_validation_pass(self):
        root = self.fixture('import unittest\nclass Checks(unittest.TestCase):\n'
                            ' @unittest.skip("intended gap")\n'
                            ' def test_one(self): pass\n')
        report = self.check(root)
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['tests']['skips'], 1)

    def test_discovery_import_error_prevents_any_test_execution(self):
        root = self.fixture('raise RuntimeError("intended import failure")\n')
        report = self.check(root)
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['tests']['tests_run'], 0)
        self.assertIn('test discovery failed', report['tests']['discovery_error'])

    def test_expected_failure_is_still_unverified_coverage(self):
        root = self.fixture('import unittest\nclass Checks(unittest.TestCase):\n'
                            ' @unittest.expectedFailure\n'
                            ' def test_one(self): self.fail("known gap")\n')
        report = self.check(root)
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['tests']['expected_failures'], 1)

    def test_duplicate_test_ids_refuse_before_execution(self):
        root = self.fixture('import unittest\nclass Checks(unittest.TestCase):\n'
                            ' def test_one(self): raise AssertionError("must not run")\n'
                            'Alias = Checks\n')
        report = self.check(root)
        self.assertEqual(report['status'], 'FAIL')
        self.assertIn('duplicate test ID', report['tests']['discovery_error'])
        self.assertEqual(report['tests']['tests_run'], 0)

    def test_invalid_syntax_is_not_executed_and_fails(self):
        report = self.check(self.fixture('def broken(\n'))
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['syntax']['status'], 'FAIL')
        self.assertEqual(report['tests']['status'], 'NOT_RUN')

    def test_corrupt_zip_fails_even_with_passing_tests(self):
        root = self.fixture('import unittest\nclass Checks(unittest.TestCase):\n'
                            ' def test_one(self): pass\n')
        (root / 'dist/probe.zip').write_bytes(b'not a ZIP')
        report = self.check(root)
        self.assertEqual(report['tests']['status'], 'PASS')
        self.assertEqual(report['package']['status'], 'FAIL')
        self.assertEqual(report['status'], 'FAIL')

    def test_unexpected_package_contents_fail(self):
        root = self.fixture('import unittest\nclass Checks(unittest.TestCase):\n'
                            ' def test_one(self): pass\n')
        with ZipFile(root / 'dist/probe.zip', 'a') as z:
            z.writestr('extra.txt', b'wrong')
        self.assertEqual(self.check(root)['package']['status'], 'FAIL')

    def test_temporary_directory_and_bytecode_settings_are_restored(self):
        root = self.fixture('import tempfile, unittest\nfrom pathlib import Path\n'
                            'class Checks(unittest.TestCase):\n'
                            ' def test_one(self):\n'
                            '  with tempfile.TemporaryDirectory() as t:\n'
                            '   self.assertTrue(Path(t).is_relative_to(Path(__file__).parents[1]))\n')
        old_temp, old_bytecode = tempfile.tempdir, sys.dont_write_bytecode
        self.assertEqual(self.check(root)['status'], 'PASS')
        self.assertEqual(tempfile.tempdir, old_temp)
        self.assertEqual(sys.dont_write_bytecode, old_bytecode)
        self.assertFalse(list(root.glob('uvh_offline_*')))

    def test_temp_settings_restore_even_if_checker_raises(self):
        root = self.fixture('import unittest\n')
        old_temp, old_bytecode = tempfile.tempdir, sys.dont_write_bytecode
        with patch.object(runner, 'test_check', side_effect=ValueError('intended')):
            with self.assertRaises(ValueError):
                self.check(root)
        self.assertEqual(tempfile.tempdir, old_temp)
        self.assertEqual(sys.dont_write_bytecode, old_bytecode)
        self.assertFalse(list(root.glob('uvh_offline_*')))

    def test_path_outside_repository_refuses(self):
        root = self.fixture('import unittest\n')
        with self.assertRaisesRegex(ValueError, 'escapes root'):
            runner.contained(root, root.parent)

    def test_missing_package_verifier_fails(self):
        root = self.fixture('import unittest\nclass Checks(unittest.TestCase):\n'
                            ' def test_one(self): pass\n')
        (root / 'scripts/verify_package.py').unlink()
        self.assertEqual(self.check(root)['package']['status'], 'FAIL')

    def test_cli_exit_status_tracks_failed_report(self):
        output = io.StringIO()
        with patch.object(runner, 'run_validation', return_value={'status': 'FAIL'}), patch('sys.stdout', output):
            self.assertEqual(runner.main([]), 1)
        self.assertEqual(json.loads(output.getvalue())['status'], 'FAIL')
