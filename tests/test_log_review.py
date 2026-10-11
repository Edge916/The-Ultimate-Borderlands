"""Synthetic protocol fixtures; these tests are not live engine evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/review_v031_log.py'
spec = importlib.util.spec_from_file_location('uvh_offline_log_review', SCRIPT)
reviewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviewer)


def event(tag, value):
    return f'[{tag}] {value}\n'


def cleanup():
    return ''.join(event(tag, 'Observers remaining=0' if tag == 'UVH-INITNODE'
                         else 'STOP remaining=0 captured=0 callbacks=0 skipped=0')
                   for tag in sorted(reviewer.CLEANUP_TAGS)) + event(
        'UVH-NEWNODE', "RESTORE result=True skills=['MorePep', 'Myelin'] cells=[True, False, True] (methods assign, slice)")


def snapshot(coverage='COMPLETE', relation='DERIVED', absent=False, unknown=False,
             points=(1, 0), final_points=None, version='0.2.11'):
    final_points = points if final_points is None else final_points
    rows = {'COMPLETE': 2, 'CAPPED': 8, 'CYCLE': 2, 'UNAVAILABLE': 0}.get(coverage, 0)
    lines = [f'BEGIN v{version} combined metadata snapshot (READ ONLY; DO NOT BUY)',
             f'BASELINE points={points} ranks=(0, 0, 0)',
             f'REFERENCE skill=Myelin index=1 count=2 path={reviewer.PRESENTATION!r}']
    if absent:
        coverage, relation, rows = 'NOT_APPLICABLE', 'UNKNOWN', 0
        lines.append('FIELD wrapper=KNOWN_ABSENT actual_class=UNAVAILABLE status=VERIFIED_ABSENCE')
    elif unknown:
        coverage, relation, rows = 'UNAVAILABLE', 'UNKNOWN', 0
        lines.append('FIELD wrapper=UNKNOWN actual_class=UNAVAILABLE status=PARTIAL_UNAVAILABLE')
    else:
        status = 'VERIFIED_METADATA' if coverage == 'COMPLETE' else 'PARTIAL_UNAVAILABLE'
        lines.extend([f'FIELD wrapper=SDK_UOBJECT actual_class=SDK_UCLASS status={status}',
                      "CLASS role=DECLARED name='AttributeDefinition' path='Core.AttributeDefinition'",
                      "CLASS role=ACTUAL name='DerivedAttribute' path='Core.DerivedAttribute'"])
        for depth in range(rows):
            name = 'DerivedAttribute' if depth == 0 else ('AttributeDefinition' if depth == 1 else f'Parent{depth}')
            lines.append(f'ANCESTOR depth={depth} name={name!r} path={"Core." + name!r}')
    lines.extend([f'ANCESTRY coverage={coverage} classes={rows} declared_relation={relation}',
                  f'FINAL points={final_points} ranks=(0, 0, 0) unchanged_from_start=True', reviewer.END, reviewer.ADVICE])
    return ''.join(event('UVH-CLASS', line) for line in lines)


def report(text):
    return reviewer.review_bytes(text.encode('utf-8'))


class LogReviewTests(unittest.TestCase):
    def assert_invalid(self, text):
        result = report(text)
        self.assertEqual(result['status'], 'INVALID_OR_INCOMPLETE')
        self.assertFalse(result['log_evidence_acceptable'])
        return result

    def test_complete_metadata_requires_separate_install_exit_checks(self):
        result = report(snapshot() + cleanup())
        self.assertEqual(result['status'], 'COMPLETE_LOG_EVIDENCE')
        self.assertEqual(result['calls'][0]['outcome'], 'COMPLETE_METADATA')
        self.assertEqual(result['separate_checks']['process_exit'], 'NOT_CHECKED')
        self.assertEqual(result['separate_checks']['installed_archive_equality'], 'NOT_CHECKED')
        self.assertEqual(result['live_game_success'], 'NOT_ESTABLISHED_BY_THIS_TOOL')

    def test_sdk_prefix_from_preserved_log_format(self):
        text = snapshot() + cleanup()
        sdk = ''.join('2026-10-11 00:00:00.000Z   679c    ~ UltimateVaultHunterDeathtrapBoost\\__init__.py@19   INFO| [UVH-BOOST] ' + line + '\n'
                      for line in text.splitlines())
        self.assertEqual(report(sdk)['status'], 'COMPLETE_LOG_EVIDENCE')

    def test_known_absence_is_separate_from_class_coverage(self):
        result = report(snapshot(absent=True) + cleanup())
        self.assertTrue(result['log_evidence_acceptable'])
        self.assertEqual(result['calls'][0]['outcome'], 'KNOWN_ABSENCE')
        self.assertEqual(result['calls'][0]['ancestry']['coverage'], 'NOT_APPLICABLE')

    def test_unknown_wrapper_is_partial_not_absence(self):
        result = report(snapshot(unknown=True) + cleanup())
        self.assertEqual(result['status'], 'PARTIAL')
        self.assertEqual(result['calls'][0]['field']['wrapper'], 'UNKNOWN')
        self.assertFalse(result['log_evidence_acceptable'])

    def test_unavailable_ancestry_is_stable_partial(self):
        result = report(snapshot('UNAVAILABLE', 'UNKNOWN') + cleanup())
        self.assertEqual(result['status'], 'PARTIAL')
        self.assertEqual(result['calls'][0]['baseline'], result['calls'][0]['final'])

    def test_capped_eight_rows_is_partial(self):
        result = report(snapshot('CAPPED', 'DERIVED') + cleanup())
        self.assertEqual(result['status'], 'PARTIAL')
        self.assertEqual(result['calls'][0]['ancestry']['declared_relation'], 'DERIVED')
        self.assertEqual(len(result['calls'][0]['ancestors']), 8)

    def test_cycle_does_not_become_complete(self):
        result = report(snapshot('CYCLE', 'UNKNOWN') + cleanup())
        self.assertEqual(result['status'], 'PARTIAL')
        self.assertEqual(result['calls'][0]['ancestry']['coverage'], 'CYCLE')

    def test_matching_names_do_not_infer_exact_relation(self):
        text = snapshot(relation='NO').replace('DerivedAttribute', 'AttributeDefinition')
        result = report(text + cleanup())
        self.assertEqual(result['calls'][0]['ancestry']['declared_relation'], 'NO')
        self.assertEqual(result['calls'][0]['outcome'], 'COMPLETE_METADATA')

    def test_exact_claim_rejects_different_declared_actual_labels(self):
        consistent = snapshot(relation='EXACT').replace('DerivedAttribute', 'AttributeDefinition')
        for changed in (
                consistent.replace("CLASS role=DECLARED name='AttributeDefinition'",
                                   "CLASS role=DECLARED name='OtherName'"),
                consistent.replace("CLASS role=DECLARED name='AttributeDefinition' path='Core.AttributeDefinition'",
                                   "CLASS role=DECLARED name='AttributeDefinition' path='Other.AttributeDefinition'"),
                snapshot(relation='EXACT')):
            with self.subTest(record=changed):
                self.assert_invalid(changed + cleanup())

    def test_exact_consistent_labels_preserve_logged_claim(self):
        text = snapshot(relation='EXACT').replace('DerivedAttribute', 'AttributeDefinition')
        result = report(text + cleanup())
        self.assertTrue(result['log_evidence_acceptable'])
        self.assertEqual(result['calls'][0]['ancestry']['declared_relation'], 'EXACT')
        self.assertEqual(result['separate_checks']['capture_origin_authenticity'], 'NOT_CHECKED')

    def test_derived_claim_requires_matching_declared_ancestor_labels(self):
        for coverage in ('COMPLETE', 'CAPPED'):
            for name, path in (('Other', 'Core.AttributeDefinition'),
                               ('AttributeDefinition', 'Other.AttributeDefinition'),
                               ('Other', 'Other.AttributeDefinition')):
                text = snapshot(coverage, 'DERIVED').replace(
                    "ANCESTOR depth=1 name='AttributeDefinition' path='Core.AttributeDefinition'",
                    f'ANCESTOR depth=1 name={name!r} path={path!r}')
                with self.subTest(coverage=coverage, name=name, path=path):
                    self.assert_invalid(text + cleanup())

    def test_runtime_observer_removal_errors_survive_zero_retry(self):
        for family, path in (('UVH-STATE', 'WillowGame.PlayerSkillTree.GetSkillState'),
                             ('UVH-UI', 'WillowGame.SkillTreeGFxObject.UpdateInfoBox'),
                             ('UVH-UPGRADE', 'WillowGame.SkillTreeSkill.Upgrade'),
                             ('UVH-TRACE', 'WillowGame.PlayerSkillTree.Initialize')):
            with self.subTest(family=family):
                result = self.assert_invalid(snapshot() + event(
                    family, f'Removal ERROR {path}: RuntimeError') + cleanup())
                self.assertEqual(result['cleanup']['error_records'][0]['family'], family)

    def test_runtime_rollback_failure_invalidates_successful_restore(self):
        result = self.assert_invalid(snapshot() + cleanup() + event(
            'UVH-INITNODE', 'Rollback failed; snapshot retained. Do not continue playing; restart BL2.'))
        self.assertEqual(result['cleanup']['error_records'][0]['family'], 'UVH-INITNODE')

    def test_runtime_native_node_removal_failure_invalidates_restore(self):
        result = self.assert_invalid(snapshot() + event(
            'UVH-NEWNODE', 'Removal ERROR RuntimeError: failed') + cleanup())
        self.assertEqual(result['cleanup']['error_records'][0]['family'], 'UVH-NEWNODE')

    def test_runtime_init_hook_failure_survives_zero_retry(self):
        result = self.assert_invalid(snapshot() + event(
            'UVH-INITNODE', 'Hook removal ERROR RuntimeError') + cleanup())
        self.assertEqual(result['cleanup']['error_records'][0]['family'], 'UVH-INITNODE')

    def test_getter_abort_is_reported_without_fabricated_final(self):
        text = event('UVH-CLASS', 'BEGIN v0.2.11 combined metadata snapshot (READ ONLY; DO NOT BUY)')
        text += event('UVH-CLASS', 'BASELINE points=(1, 0) ranks=(0, 0, 0)')
        text += event('UVH-CLASS', 'FIELD status=UNAVAILABLE getter_error=RuntimeError')
        text += event('UVH-CLASS', 'ABORT ValueError: metadata/current state unavailable or changed; no repair/refund. CANCEL and exit.')
        result = report(text + cleanup())
        self.assertEqual(result['status'], 'ABORTED')
        self.assertIsNone(result['calls'][0]['final'])
        self.assertFalse(result['log_evidence_acceptable'])

    def test_not_inspected_is_refusal(self):
        text = event('UVH-CLASS', 'BEGIN v0.2.11 combined metadata snapshot (READ ONLY; DO NOT BUY)')
        text += event('UVH-CLASS', 'NOT INSPECTED: initialization/other observers must be stopped.')
        self.assertEqual(report(text + cleanup())['status'], 'NOT_INSPECTED')

    def test_missing_required_records(self):
        for kind in ('BASELINE', 'REFERENCE', 'FIELD', 'ANCESTRY', 'FINAL', 'END'):
            with self.subTest(kind=kind):
                text = ''.join(line for line in snapshot().splitlines(True) if not line.startswith('[UVH-CLASS] ' + kind + ' '))
                self.assert_invalid(text + cleanup())

    def test_changed_points_even_with_unchanged_true(self):
        self.assert_invalid(snapshot(final_points=(0, 0)) + cleanup())

    def test_changed_original_skill_ranks(self):
        text = snapshot().replace('FINAL points=(1, 0) ranks=(0, 0, 0)', 'FINAL points=(1, 0) ranks=(0, 1, 0)')
        self.assert_invalid(text + cleanup())

    def test_inert_candidate_grade_must_be_zero(self):
        self.assert_invalid(snapshot().replace('ranks=(0, 0, 0)', 'ranks=(1, 0, 0)') + cleanup())

    def test_negative_points_are_malformed(self):
        self.assert_invalid(snapshot().replace('points=(1, 0)', 'points=(-1, 0)') + cleanup())

    def test_false_unchanged_flag_is_not_accepted(self):
        self.assert_invalid(snapshot().replace('unchanged_from_start=True', 'unchanged_from_start=False') + cleanup())

    def test_duplicate_field(self):
        line = next(line for line in snapshot().splitlines(True) if 'FIELD wrapper=' in line)
        self.assert_invalid(snapshot().replace(line, line + line) + cleanup())

    def test_reordered_final_is_invalid(self):
        lines = snapshot().splitlines(True)
        final = next(line for line in lines if '[UVH-CLASS] FINAL ' in line)
        lines.remove(final)
        lines.insert(1, final)
        self.assert_invalid(''.join(lines) + cleanup())

    def test_old_version_is_rejected(self):
        self.assert_invalid(snapshot(version='0.2.10') + cleanup())

    def test_mixed_diagnostic_versions_are_rejected(self):
        text = event('UVH-DISPLAY', 'BEGIN v0.2.10 display snapshot') + snapshot() + cleanup()
        self.assert_invalid(text)

    def test_new_begin_cannot_close_prior_incomplete_call(self):
        text = event('UVH-CLASS', 'BEGIN v0.2.11 combined metadata snapshot (READ ONLY; DO NOT BUY)')
        self.assert_invalid(text + snapshot() + cleanup())

    def test_multiple_snapshots_are_counted_separately(self):
        result = report(snapshot() + snapshot(absent=True) + cleanup())
        self.assertEqual(len(result['calls']), 2)
        self.assertTrue(result['log_evidence_acceptable'])

    def test_changed_points_between_individually_stable_snapshots(self):
        self.assert_invalid(snapshot() + snapshot(points=(2, 0)) + cleanup())

    def test_schema_rechecks_are_not_snapshots(self):
        schema = event('UVH-PRESENT', "SCHEMA owner='AttributePresentationDefinition' coverage=CAPPED")
        result = report(schema * 15 + snapshot() + cleanup())
        self.assertEqual(len(result['calls']), 1)

    def test_restoration_before_snapshot_is_insufficient(self):
        self.assert_invalid(cleanup() + snapshot())

    def test_missing_restoration(self):
        text = ''.join(line for line in cleanup().splitlines(True) if 'RESTORE result=' not in line)
        self.assert_invalid(snapshot() + text)

    def test_failed_restoration(self):
        self.assert_invalid(snapshot() + cleanup().replace('result=True', 'result=False'))

    def test_wrong_restored_native_arrays(self):
        self.assert_invalid(snapshot() + cleanup().replace("['MorePep', 'Myelin']", "['MorePep', 'UVH_DeathtrapOverclock', 'Myelin']"))

    def test_missing_observer_family(self):
        self.assert_invalid(snapshot() + cleanup().replace(event('UVH-INITNODE', 'Observers remaining=0'), ''))

    def test_nonzero_observer_cleanup_is_not_hidden_by_later_zero(self):
        text = snapshot() + event('UVH-INITNODE', 'Observers remaining=1') + cleanup()
        self.assert_invalid(text)

    def test_nonzero_added_observers_is_not_accepted(self):
        self.assert_invalid(snapshot().replace('observers_added=0', 'observers_added=1') + cleanup())

    def test_capped_count_must_equal_eight(self):
        self.assert_invalid(snapshot('CAPPED', 'UNKNOWN').replace('classes=8', 'classes=7') + cleanup())

    def test_relation_requires_appropriate_coverage(self):
        for coverage in ('UNAVAILABLE', 'CYCLE', 'CAPPED'):
            with self.subTest(coverage=coverage):
                self.assert_invalid(snapshot(coverage, 'NO') + cleanup())

    def test_missing_class_role(self):
        text = ''.join(line for line in snapshot().splitlines(True) if 'CLASS role=DECLARED ' not in line)
        self.assert_invalid(text + cleanup())

    def test_noncontiguous_ancestor_depth(self):
        self.assert_invalid(snapshot().replace('ANCESTOR depth=1', 'ANCESTOR depth=3') + cleanup())

    def test_metadata_bounds(self):
        for text in (snapshot().replace("name='DerivedAttribute'", 'name=' + repr('a' * 97)),
                     snapshot().replace('count=2', 'count=257'),
                     snapshot().replace("path='Core.DerivedAttribute'", 'path=' + repr('a' * 385))):
            with self.subTest(text=text[:100]):
                self.assert_invalid(text + cleanup())

    def test_quoted_metadata_is_data_not_code(self):
        hostile = "__import__('os').system('never-run')"
        text = snapshot().replace("name='DerivedAttribute'", 'name=' + repr(hostile))
        result = report(text + cleanup())
        self.assertEqual(result['calls'][0]['classes']['ACTUAL']['name'], hostile)
        self.assertTrue(result['log_evidence_acceptable'])

    def test_unquoted_expression_is_not_evaluated(self):
        text = snapshot().replace("name='DerivedAttribute'", "name=__import__('os').system('never-run')")
        self.assert_invalid(text + cleanup())

    def test_known_absence_cannot_contain_class_metadata(self):
        text = snapshot(absent=True).replace('[UVH-CLASS] ANCESTRY', event('UVH-CLASS', "CLASS role=ACTUAL name='A' path='A'") + '[UVH-CLASS] ANCESTRY')
        self.assert_invalid(text + cleanup())

    def test_clipped_prefix_is_not_silently_ignored(self):
        text = snapshot() + 'clipped INFO| [UVH-BOOST] [UVH-CLASS] FINAL points=(1, 0) ranks=(0, 0, 0) unchanged_from_start=True\n' + cleanup()
        self.assert_invalid(text)

    def test_missing_eof_newline_is_reported(self):
        self.assert_invalid((snapshot() + cleanup()).rstrip('\n'))

    def test_clipped_windows_final_crlf_is_reported(self):
        self.assert_invalid((snapshot() + cleanup()).rstrip('\n') + '\r')

    def test_malformed_cleanup_cannot_reuse_an_earlier_zero(self):
        self.assert_invalid(snapshot() + cleanup() + event('UVH-UI', 'STOP remaining=unknown'))

    def test_other_trace_start_cannot_reuse_earlier_cleanup(self):
        self.assert_invalid(snapshot() + cleanup() + event('UVH-UI', 'START v0.2.11 functions=4 observers=8 points=(1, 0) ranks=(0, 0, 0) READ ONLY; DO NOT BUY.'))

    def test_rollback_refusal_invalidates_prior_restore(self):
        self.assert_invalid(snapshot() + cleanup() + event('UVH-INITNODE', 'Native arrays changed independently; refusing rollback overwrite. Restart BL2.'))

    def test_bom_crlf_hashes_original_bytes(self):
        raw = b'\xef\xbb\xbf' + (snapshot() + cleanup()).replace('\n', '\r\n').encode()
        result = reviewer.review_bytes(raw)
        self.assertTrue(result['log_evidence_acceptable'])
        self.assertEqual(result['source']['sha256'], hashlib.sha256(raw).hexdigest())

    def test_non_utf8_keeps_hash_and_refuses(self):
        raw = b'\xffbroken'
        result = reviewer.review_bytes(raw)
        self.assertEqual(result['status'], 'INVALID_OR_INCOMPLETE')
        self.assertEqual(result['source']['sha256'], hashlib.sha256(raw).hexdigest())

    def test_historical_v030_is_not_v031_proof(self):
        path = ROOT / 'evidence/v030_user_test.log'
        raw = path.read_bytes()
        result = reviewer.review_bytes(raw)
        self.assertFalse(result['log_evidence_acceptable'])
        self.assertEqual(result['calls'], [])
        self.assertEqual(raw, path.read_bytes())

    def test_cli_exit_codes_and_source_preservation(self):
        with tempfile.TemporaryDirectory(prefix='uvh_review_fixture_') as directory:
            path = Path(directory) / 'fixture.log'
            for text, expected in ((snapshot() + cleanup(), 0),
                                   (snapshot(unknown=True) + cleanup(), 1),
                                   (snapshot(), 1)):
                raw = text.encode()
                path.write_bytes(raw)
                done = subprocess.run([sys.executable, '-I', '-B', str(SCRIPT), str(path)], capture_output=True)
                self.assertEqual(done.returncode, expected, done.stderr)
                result = json.loads(done.stdout)
                self.assertEqual(result['source']['sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(path.read_bytes(), raw)
                self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_cli_missing_file_is_input_error(self):
        with tempfile.TemporaryDirectory(prefix='uvh_review_missing_') as directory:
            done = subprocess.run([sys.executable, '-I', '-B', str(SCRIPT), str(Path(directory) / 'absent')], capture_output=True)
            self.assertEqual(done.returncode, 2)
            self.assertEqual(json.loads(done.stdout)['status'], 'INPUT_ERROR')


if __name__ == '__main__':
    unittest.main()
