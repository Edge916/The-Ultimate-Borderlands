"""Adversarial catalog-text tests and output from inert project fixtures only."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import test_deathtrap_manager_relationship_metadata as implementation

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/review_deathtrap_manager_relationship_metadata_log.py'
spec = importlib.util.spec_from_file_location('relationship_text_reviewer', SCRIPT)
reviewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviewer)


def record(event, **values):
    return dict(event=event, epoch=1, **values)


def start():
    return record('START', version='0.2.19', target='ActivateSkill', phase='PRE', hooks=1, mode='STANDALONE_METADATA')


def row(root='MGR', ordinal=1, name='SyntheticSlot', **values):
    return record('ROW', root=root, ordinal=ordinal, name=name, owner=0, kind='SCALAR',
                  flags=0, offset=16, dim=1, size=4, decl='CTRL') | values


def summary(root='MGR', **values):
    return record('ROOT', root=root, coverage='COMPLETE_LINK', reason='NONE', visited=1,
                  objects=1, other=0, unsupported=0, rows=1, rechecked=1, ops=27) | values


def end(**values):
    return record('END', outcome='COMPLETE_SCOPED_METADATA', attempts=1, gate_ops=98,
        root_ops=68, mgr_ops=27, ctrl_ops=27, total_ops=220, rows=2, errors=0,
        refusals=0, reentry=0, reentry_saturated=False) | values


def stop(**values):
    return record('STOP', remaining=0, uncertain=0, attempts=1, cleanup_failures=0,
        removal_attempts=1, deferred=False, errors=0, refusals=0, reentry=0,
        reentry_saturated=False, ignored=0, ignored_saturated=False,
        outcome='COMPLETE_SCOPED_METADATA') | values


def complete():
    return [start(), record('BEGIN', attempt=1), row(), summary(), row('CTRL'), summary('CTRL'), end(), stop()]


def encode(records, framing=''):
    return ('\n'.join(framing + reviewer.PREFIX + json.dumps(r, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
                      for r in records) + '\n').encode('ascii')


class RelationshipLogReviewTests(unittest.TestCase):
    def assert_status(self, records, status='COMPLETE_LOG_TEXT'):
        result = reviewer.review_bytes(encode(records))
        self.assertEqual(result['status'], status, result.get('issues'))
        self.assertFalse(result['native_effect_ready'])
        self.assertFalse(result['native_owned_lifecycle_ready'])
        self.assertEqual(result['native_ownership'], 'NOT_ESTABLISHED')
        return result

    def invalid(self, records):
        r = self.assert_status(records, 'INVALID_LOG_TEXT')
        self.assertFalse(r['log_text_acceptable'])
        return r

    def test_complete_canonical_and_actual_sdk_header_frame(self):
        self.assert_status(complete())
        for prefix in ('[UVH-BOOST] ', '2026-10-12 12:00:00.000Z Synthetic INFO| [UVH-BOOST] '):
            self.assertEqual(reviewer.review_bytes(encode(complete(), prefix))['status'], 'COMPLETE_LOG_TEXT')

    def test_complete_other_and_unsupported_are_preserved_not_absence(self):
        records = complete()
        records[3] = summary(visited=4, objects=2, other=1, unsupported=1, rechecked=4, ops=102)
        records[6] = end(mgr_ops=102, total_ops=295)
        r = self.assert_status(records)
        self.assertEqual(r['sessions'][0]['roots']['MGR']['other'], 1)
        self.assertEqual(r['sessions'][0]['roots']['MGR']['unsupported'], 1)

    def test_maximum_rows_uint64_and_descriptor_ceiling(self):
        records = [start(), record('BEGIN', attempt=1)]
        for root in reviewer.ROOTS:
            records += [row(root, i + 1, 'N' * 125 + str(i).zfill(3), flags=(1 << 64) - 1, owner=2 if root == 'MGR' else 6)
                        for i in range(64)]
            records += [summary(root, visited=512, objects=512, other=448, rows=64, rechecked=512, ops=13824)]
        records += [end(mgr_ops=13824, ctrl_ops=13824, total_ops=27814, rows=128), stop()]
        self.assert_status(records)
        self.assertTrue(all(len(reviewer.PROJECT_PREFIX + line) <= 512 for line in encode(records).decode().splitlines()))

    def test_non_scalar_kind_and_maximum_layout(self):
        records = complete()
        records[2] |= dict(dim=1024, offset=1044480, kind='NON_SCALAR')
        self.assert_status(records)

    def test_partial_property_limit_is_honest(self):
        records = complete()
        records[3] = summary(coverage='PARTIAL', reason='PROPERTY_LIMIT', visited=512, objects=1,
                             rechecked=512, ops=12291)
        records[6] = end(outcome='PARTIAL_METADATA', mgr_ops=12291, total_ops=12484)
        records[7] = stop(outcome='PARTIAL_METADATA')
        r = self.assert_status(records, 'PARTIAL_LOG_TEXT')
        self.assertEqual(reviewer.exit_code(r), 1)

    def test_partial_row_limit_conservation(self):
        records = [start(), record('BEGIN', attempt=1)]
        records += [row(ordinal=i + 1, name='Synthetic' + str(i)) for i in range(64)]
        records += [summary(coverage='PARTIAL', reason='ROW_LIMIT', visited=65, objects=65,
            rows=64, rechecked=65, ops=1755), row('CTRL'), summary('CTRL'),
            end(outcome='PARTIAL_METADATA', mgr_ops=1755, total_ops=1948, rows=65), stop(outcome='PARTIAL_METADATA')]
        self.assert_status(records, 'PARTIAL_LOG_TEXT')

    def test_silent_no_attempt_is_distinct(self):
        records = [start(), end(outcome='NOT_OBSERVED', attempts=0, gate_ops=0, root_ops=0,
             mgr_ops=0, ctrl_ops=0, total_ops=0, rows=0), stop(attempts=0, outcome='NOT_OBSERVED')]
        self.assert_status(records, 'NOT_OBSERVED_LOG_TEXT')

    def test_no_markers_never_fabricates_silent_session(self):
        for data in (b'', b'ordinary startup\n'):
            r = reviewer.review_bytes(data)
            self.assertEqual(r['status'], 'NO_METADATA_RECORDS')
            self.assertFalse(r['log_text_acceptable'])

    def test_refusal_after_completed_mgr_keeps_valid_root_and_fault(self):
        records = complete()
        records[4:6] = [summary('CTRL', coverage='REFUSED', reason='CYCLE', visited=0,
            objects=0, rows=0, rechecked=0, ops=8), record('FAULT', kind='REFUSED', scope='CTRL', reason='CYCLE')]
        records[6] = end(outcome='REFUSED', ctrl_ops=8, total_ops=201, rows=1, refusals=1)
        records[7] = stop(outcome='REFUSED', refusals=1)
        self.assert_status(records, 'REFUSED_LOG_TEXT')

    def test_gate_failure_and_each_fixed_fault_reason(self):
        for reason in reviewer.REASONS:
            with self.subTest(reason=reason):
                records = [start(), record('BEGIN', attempt=1), record('FAULT', kind='REFUSED', scope='GATE', reason=reason),
                    end(outcome='REFUSED', gate_ops=1, root_ops=0, mgr_ops=0, ctrl_ops=0,
                        total_ops=1, rows=0, refusals=1), stop(outcome='REFUSED', refusals=1)]
                self.assert_status(records, 'REFUSED_LOG_TEXT')

    def test_error_history_survives_successful_cleanup(self):
        records = [start(), record('BEGIN', attempt=1), record('FAULT', kind='ERROR', scope='SESSION', reason='INTERNAL'),
            end(outcome='REFUSED', gate_ops=0, root_ops=0, mgr_ops=0, ctrl_ops=0, total_ops=0, rows=0, errors=1),
            stop(outcome='REFUSED', errors=1)]
        self.assert_status(records, 'REFUSED_LOG_TEXT')
        records[-1]['errors'] = 0
        self.invalid(records)

    def test_removal_retry_preserves_failures(self):
        records = complete()[:-1] + [stop(remaining=1, removal_attempts=4, cleanup_failures=4, outcome='REFUSED'),
                                   stop(removal_attempts=5, cleanup_failures=4, outcome='REFUSED')]
        self.assert_status(records, 'REFUSED_LOG_TEXT')
        records[-1] |= dict(cleanup_failures=0, outcome='COMPLETE_SCOPED_METADATA')
        self.invalid(records)

    def test_failed_registration_uncertainty_and_later_resolution(self):
        records = [record('NOT_STARTED', reason='REGISTRATION', remaining=1, uncertain=1),
            end(outcome='NOT_OBSERVED', attempts=0, gate_ops=0, root_ops=0, mgr_ops=0,
                ctrl_ops=0, total_ops=0, rows=0, refusals=1),
            stop(attempts=0, remaining=1, uncertain=1, cleanup_failures=4, removal_attempts=4, refusals=1, outcome='REFUSED'),
            stop(attempts=0, cleanup_failures=4, removal_attempts=5, refusals=1, outcome='REFUSED')]
        self.assert_status(records, 'REFUSED_LOG_TEXT')

    def test_identifier_refusal_no_own_hook(self):
        records = [record('NOT_STARTED', reason='IDENTIFIER', remaining=0, uncertain=0),
            end(outcome='NOT_OBSERVED', attempts=0, gate_ops=0, root_ops=0, mgr_ops=0,
                ctrl_ops=0, total_ops=0, rows=0, refusals=1),
            stop(attempts=0, removal_attempts=0, refusals=1, outcome='REFUSED')]
        self.assert_status(records, 'REFUSED_LOG_TEXT')

    def test_deferred_busy_stop_before_begin_requires_final_stop(self):
        records = [start(), stop(attempts=1, remaining=1, removal_attempts=0, deferred=True, outcome='REFUSED'),
            record('BEGIN', attempt=1), record('FAULT', kind='REFUSED', scope='SESSION', reason='STOPPED'),
            end(outcome='REFUSED', gate_ops=0, root_ops=0, mgr_ops=0, ctrl_ops=0, total_ops=0, rows=0, refusals=1),
            stop(outcome='REFUSED', refusals=1)]
        self.assert_status(records, 'REFUSED_LOG_TEXT')
        self.invalid(records[:-1])

    def test_reentry_and_ignored_saturation_monotonic(self):
        records = [start(), record('BEGIN', attempt=1), record('FAULT', kind='REFUSED', scope='SESSION', reason='REENTRY'),
            end(outcome='REFUSED', gate_ops=0, root_ops=0, mgr_ops=0, ctrl_ops=0, total_ops=0, rows=0,
                refusals=1, reentry=64, reentry_saturated=True),
            stop(outcome='REFUSED', refusals=1, reentry=64, reentry_saturated=True, ignored=64, ignored_saturated=True)]
        self.assert_status(records, 'REFUSED_LOG_TEXT')
        for key, value in (('reentry_saturated', False), ('reentry', 63), ('ignored', 63)):
            bad = copy.deepcopy(records) + [records[-1] | {key: value}]
            self.invalid(bad)

    def test_repeated_resolved_controls_and_multiple_epochs(self):
        records = complete() + [stop(), record('NOT_STARTED', reason='OVERLAP', remaining=0, uncertain=0)]
        records += [r | {'epoch': 2} for r in complete()]
        self.assert_status(records)
        records[-1]['epoch'] = 1
        self.invalid(records)

    def test_duplicate_extra_and_missing_keys(self):
        raw = encode(complete())
        for change in (raw.replace(b'"hooks":1', b'"hooks":1,"hooks":1', 1),
                       raw.replace(b'"hooks":1', b'"private":"SECRET","hooks":1', 1),
                       raw.replace(b'"hooks":1,', b'', 1)):
            r = reviewer.review_bytes(change)
            self.assertFalse(r['log_text_acceptable'])
            self.assertNotIn('SECRET', json.dumps(r))

    def test_canonical_json_numeric_and_type_rejection(self):
        raw = encode(complete())
        for value in (b'true', b'1.0', b'1e0', b'null', b'"1"', b'NaN', b'-0', b'01'):
            r = reviewer.review_bytes(raw.replace(b'"hooks":1', b'"hooks":' + value, 1))
            self.assertFalse(r['log_text_acceptable'], value)
        for change in (raw.replace(b'{', b'{ ', 1), raw.replace(b'"event":"START"', b'"event":"\\u0053TART"', 1)):
            self.assertFalse(reviewer.review_bytes(change)['log_text_acceptable'])

    def test_row_numeric_schema_and_token_mutations(self):
        for key, value in (('flags', 1 << 64), ('flags', -1), ('owner', 3), ('decl', 'OTHER'),
            ('name', 'private/path'), ('name', 'N' * 129), ('ordinal', 2), ('offset', 1048576),
            ('dim', 0), ('dim', 1025), ('size', 8), ('kind', 'NON_SCALAR'), ('root', 'FOREIGN')):
            with self.subTest(key=key, value=value):
                records = complete()
                records[2][key] = value
                self.invalid(records)

    def test_root_conservation_coverage_and_ops_mutations(self):
        for key, value in (('visited', 513), ('objects', 2), ('other', 2), ('unsupported', 1), ('rows', 0),
            ('rechecked', 0), ('ops', 26), ('coverage', 'PARTIAL'), ('reason', 'CYCLE')):
            records = complete()
            records[3][key] = value
            self.invalid(records)

    def test_end_conservation_and_caps_mutations(self):
        for key, value in (('rows', 1), ('total_ops', 221), ('gate_ops', 99), ('root_ops', 67),
            ('mgr_ops', 14001), ('ctrl_ops', 14001), ('attempts', 0), ('outcome', 'PARTIAL_METADATA'),
            ('errors', 1), ('reentry', 1), ('reentry_saturated', True)):
            records = complete()
            records[6][key] = value
            self.invalid(records)

    def test_missing_begin_root_end_stop_and_reordered_roots(self):
        for index in (0, 1, 3, 6, 7):
            records = complete()
            del records[index]
            self.invalid(records)
        records = complete()
        records[2:6] = records[4:6] + records[2:4]
        self.invalid(records)

    def test_duplicate_begin_row_root_and_end(self):
        for index in (1, 2, 3, 6):
            records = complete()
            records.insert(index, copy.deepcopy(records[index]))
            self.invalid(records)

    def test_shadowed_name_separate_declaring_owner(self):
        records = complete()
        records.insert(3, row(ordinal=2, owner=1))
        records[4] = summary(visited=2, objects=2, rows=2, rechecked=2, ops=54)
        records[7] = end(rows=3, mgr_ops=54, total_ops=247)
        self.assert_status(records)
        records[3]['owner'] = 0
        self.invalid(records)

    def test_unresolved_cleanup_and_counter_bounds(self):
        for values in (dict(remaining=1, cleanup_failures=4, removal_attempts=4, outcome='REFUSED'),
            dict(uncertain=1), dict(removal_attempts=5), dict(cleanup_failures=1),
            dict(removal_attempts=257), dict(ignored=65), dict(errors=257), dict(deferred=True)):
            records = complete()
            records[-1] |= values
            self.invalid(records)

    def test_mixed_clipped_unknown_version_and_private_text_suppression(self):
        raw = encode(complete())
        for tail in (b'[UVH-REL\n', b'[UVH-REL-META-V20] SECRET\n', b'[UVH-ACTIVATION] SECRET\n',
                     b'[UVH-CALLBACK] SECRET\n', b'UVH_RELATION_METADATA_V20_PRE SECRET\n'):
            report = reviewer.review_bytes(raw + tail)
            self.assertFalse(report['log_text_acceptable'])
            self.assertNotIn('SECRET', json.dumps(report))
        records = complete()
        records[0]['version'] = '0.2.18'
        self.invalid(records)

    def test_message_and_input_bounds_and_final_newline(self):
        for raw, code in ((b'\xff\n', 'UTF8'), (b'\0\n', 'NUL'), (b'x' * (reviewer.MAX_LINE_BYTES + 1), 'LINE_BYTES_BOUND'),
            (b'\n' * (reviewer.MAX_LINES + 1), 'LINE_BOUND'), (b'x' * (reviewer.MAX_BYTES + 1), 'BYTE_BOUND')):
            self.assertEqual(reviewer.review_bytes(raw)['input_error'], code)
        self.assertEqual(reviewer.review_bytes('not bytes')['input_error'], 'INPUT_TYPE')
        self.assertFalse(reviewer.review_bytes(encode(complete()).rstrip(b'\n'))['log_text_acceptable'])
        records = complete()
        records[2]['name'] = 'N' * 600
        self.invalid(records)

    def test_session_control_fault_and_global_record_limits(self):
        self.assert_status(complete() + [stop()] * 63)
        self.invalid(complete() + [stop()] * 64)
        raw = encode([r | {'epoch': i + 1} for i in range(129) for r in complete()])
        self.assertFalse(reviewer.review_bytes(raw)['log_text_acceptable'])
        raw = b'[UVH-REL\n' * (reviewer.MAX_RECORDS + 1)
        r = reviewer.review_bytes(raw)
        self.assertEqual(len(r['issues']), reviewer.MAX_ISSUES)
        self.assertTrue(r['issues_truncated'])
        self.assertLess(len(json.dumps(r)), 20000)
        records = [start(), record('BEGIN', attempt=1)]
        records += [record('FAULT', kind='REFUSED', scope='SESSION', reason='TIME')] * 9
        self.invalid(records)

    def test_exact_eight_fault_records_can_be_closed_without_erasure(self):
        records = [start(), record('BEGIN', attempt=1)]
        records += [record('FAULT', kind='REFUSED', scope='SESSION', reason='TIME')] * 8
        records += [end(outcome='REFUSED', gate_ops=0, root_ops=0, mgr_ops=0, ctrl_ops=0,
                        total_ops=0, rows=0, refusals=8), stop(outcome='REFUSED', refusals=8)]
        self.assert_status(records, 'REFUSED_LOG_TEXT')

    def test_cli_exit_readonly_and_read_error_does_not_echo_private_path(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'synthetic.log'
            raw = encode(complete())
            target.write_bytes(raw)
            run = subprocess.run([sys.executable, '-B', str(SCRIPT), str(target)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['status'], 'COMPLETE_LOG_TEXT')
            self.assertEqual(target.read_bytes(), raw)
            target.unlink()
            run = subprocess.run([sys.executable, '-B', str(SCRIPT), str(target)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertNotIn(str(target), run.stdout + run.stderr)

    def produced(self, action):
        fixture = implementation.RelationshipMetadataTests('test_complete_exact_operation_transcripts_and_known_other_fields')
        fixture.setUp()
        try:
            action(fixture)
            raw = ('\n'.join(fixture.h.logs) + '\n').encode('ascii')
            return reviewer.review_bytes(raw)
        finally:
            fixture.tearDown()

    def test_implementation_produced_complete_empty_partial_and_silent(self):
        def complete_run(f): f.start(); f.fire(); f.call('stop_relationship_metadata')
        def empty_run(f): f.link(0, []); f.link(1, []); complete_run(f)
        def silent_run(f): f.start(); f.call('stop_relationship_metadata')
        def partial_run(f):
            f.link(0, [f.prop('Synthetic' + str(i), 0, 1) for i in range(65)])
            complete_run(f)
        for action, status in ((complete_run, 'COMPLETE_LOG_TEXT'), (empty_run, 'COMPLETE_LOG_TEXT'),
                               (silent_run, 'NOT_OBSERVED_LOG_TEXT'), (partial_run, 'PARTIAL_LOG_TEXT')):
            with self.subTest(status=status):
                result = self.produced(action)
                self.assertEqual(result['status'], status, result.get('issues'))

    def test_implementation_produced_invalid_schema_and_cycle_refusal(self):
        def cycle(f):
            f.mgr[-1].PropertyLinkNext = f.mgr[0]
            f.start(); f.fire(); f.call('stop_relationship_metadata')
        def bad_schema(f):
            f.fn.NumParams = 7
            f.start(); f.fire(); f.call('stop_relationship_metadata')
        for action in (cycle, bad_schema):
            result = self.produced(action)
            self.assertEqual(result['status'], 'REFUSED_LOG_TEXT', result.get('issues'))

    def test_implementation_produced_failure_tails_and_refused_partial_rechecks(self):
        names = ('test_reentry_refuses_before_another_native_operation',
            'test_time_limit_after_last_native_get_refuses',
            'test_busy_stop_defers_and_requires_explicit_stop',
            'test_cleanup_failure_history_and_retry_are_preserved',
            'test_final_root_head_change_suppresses_every_staged_row',
            'test_private_sdk_exception_is_fixed_internal_error',
            'test_bool_integer_and_private_refusal_reason_never_leak')
        for name in names:
            with self.subTest(name=name):
                def action(f):
                    getattr(f, name)()
                    implementation.ON_OP = None
                    f.call('stop_relationship_metadata')
                result = self.produced(action)
                self.assertEqual(result['status'], 'REFUSED_LOG_TEXT', result.get('issues'))

    def test_implementation_unknown_registration_stays_unresolved(self):
        def action(f): f.test_unknown_add_outcome_never_removes_uncertain_foreign_handle()
        result = self.produced(action)
        self.assertEqual(result['status'], 'INVALID_LOG_TEXT')
        self.assertTrue(any(i['code'] == 'INCOMPLETE_CLOSURE' for i in result['issues']))

    def test_implementation_time_and_logging_missing_tail_never_pass(self):
        for name in ('test_session_timeout_on_callback_and_control_preserves_fault',
                     'test_logging_failure_stays_inert_and_cleanup_does_not_reread'):
            result = self.produced(lambda f: getattr(f, name)())
            self.assertFalse(result['log_text_acceptable'])

    def test_implementation_control_exhaustion_reports_only_recorded_evidence(self):
        result = self.produced(lambda f: f.test_control_log_cap_does_not_reopen_collector())
        # The actual unlogged 65th+ calls cannot be reconstructed from text.
        self.assertEqual(result['status'], 'NOT_OBSERVED_LOG_TEXT', result.get('issues'))
        self.assertEqual(result['sessions'][0]['controls'], 64)

    def test_implementation_expiry_on_repeated_resolved_stop_retains_failure(self):
        def action(f):
            f.start(); f.fire(); f.call('stop_relationship_metadata')
            f.clock += 120.0
            f.call('stop_relationship_metadata')
        result = self.produced(action)
        self.assertEqual(result['status'], 'REFUSED_LOG_TEXT', result.get('issues'))

    def test_refused_root_cannot_claim_unrelated_fault(self):
        records = [start(), record('BEGIN', attempt=1),
            summary(coverage='REFUSED', reason='LINK', visited=0, objects=0, rows=0, rechecked=0, ops=8),
            record('FAULT', kind='REFUSED', scope='MGR', reason='OWNER'),
            end(outcome='REFUSED', mgr_ops=8, ctrl_ops=0, total_ops=174, rows=0, refusals=1),
            stop(outcome='REFUSED', refusals=1)]
        self.invalid(records)

    def test_accepted_hook_never_becomes_uncertain_or_reenters_after_end(self):
        records = complete()[:-1] + [stop(remaining=1, uncertain=1, removal_attempts=4,
            cleanup_failures=4, outcome='REFUSED'), stop(removal_attempts=5, cleanup_failures=4, outcome='REFUSED')]
        self.invalid(records)
        records = complete()
        records[-1]['reentry'] = 1
        self.invalid(records)

    def test_input_exact_limit_and_privacy_nested_json(self):
        with patch.object(reviewer, 'MAX_BYTES', 64), patch.object(reviewer, 'MAX_LINE_BYTES', 64):
            self.assertEqual(reviewer.review_bytes(b'x' * 63 + b'\n')['status'], 'NO_METADATA_RECORDS')
            self.assertEqual(reviewer.review_bytes(b'x' * 64 + b'\n')['input_error'], 'BYTE_BOUND')
        raw = encode(complete()) + (reviewer.PREFIX + '{"event":' + '[' * 1100 + '"SECRET"' + ']' * 1100 + '}\n').encode()
        result = reviewer.review_bytes(raw)
        self.assertFalse(result['log_text_acceptable'])
        self.assertNotIn('SECRET', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
