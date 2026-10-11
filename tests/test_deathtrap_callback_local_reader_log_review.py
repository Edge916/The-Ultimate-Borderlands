"""Synthetic mutations and real inert-v16 transcripts; never real SDK/game execution."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_deathtrap_callback_local_reader as inert

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('callback_log_review',
    ROOT / 'scripts/review_deathtrap_callback_local_reader_log.py')
reviewer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reviewer)
TAG = '[UVH-BOOST] [UVH-CALLBACK-READ] '


def start(epoch=1):
    return ('START version=0.2.16 epoch={} target=DeactivateSkill phase=PRE hooks=1 '
            'mode=STANDALONE_READER').format(epoch)


def event(epoch=1, ordinal=1, attempt=1, controller='SAME_WRAPPER', definition='DEATHTRAP_NAME'):
    stages = reviewer.EVENT_STAGES[(controller, definition)]
    return ('EVENT epoch={} ordinal={} attempt={} schema=VALID controller={} definition={} '
            'ownership=UNESTABLISHED ops={} stages={},{},{},{}').format(
                epoch, ordinal, attempt, controller, definition, sum(stages), *stages)


def stop(epoch=1, **overrides):
    values = dict(remaining=0, uncertain=0, attempts=0, classified=0, filtered=0,
                  nulls=0, refusals=0, errors=0, reentry=0, cleanup_failures=0, limit='NONE')
    values.update(overrides)
    return 'STOP epoch={} '.format(epoch) + ' '.join('{}={}'.format(k, v) for k, v in values.items())


def outcome(epoch=1, value='NOT_OBSERVED'):
    return 'OUTCOME epoch={} value={} ownership=UNESTABLISHED'.format(epoch, value)


def raw(records, prefix=TAG, ending='\n'):
    return (ending.join(prefix + record for record in records) + ending).encode()


def transcript(useful=False):
    return ([start(), event(), stop(attempts=1, classified=1), outcome(value='OBSERVED_PRIMITIVE')]
            if useful else [start(), stop(), outcome()])


class ReaderLogTests(unittest.TestCase):
    def assert_status(self, records, status='COMPLETE_LOG_TEXT'):
        report = reviewer.review_bytes(raw(records))
        self.assertEqual(report['status'], status, report.get('issues'))
        self.assertEqual(report['log_text_acceptable'], status == 'COMPLETE_LOG_TEXT')
        self.assertFalse(report['native_owned_lifecycle_ready'])
        self.assertFalse(report['native_effect_ready'])
        return report

    def invalid_mutation(self, before, after, records=None):
        records = transcript(True) if records is None else records
        blob = raw(records)
        self.assertIn(before.encode(), blob)
        report = reviewer.review_bytes(blob.replace(before.encode(), after.encode()))
        self.assertEqual(report['status'], 'INVALID_LOG_TEXT', report)
        return report

    def test_zero_observation_is_complete_text_only(self):
        r = self.assert_status(transcript())
        self.assertEqual(r['sessions'][0]['stops'][0]['outcome'], 'NOT_OBSERVED')
        self.assertEqual(r['native_ownership'], 'NOT_ESTABLISHED')
        self.assertEqual(r['cleanup']['process_exit'], 'NOT_ESTABLISHED')
        self.assertEqual(r['owner_protocol'], 'NOT_ESTABLISHED')

    def test_each_classification_branch_and_expected_budgets(self):
        for controller, definition in reviewer.EVENT_STAGES:
            with self.subTest(controller=controller, definition=definition):
                filtered = int(controller.startswith('OTHER') or definition == 'OTHER_NAME')
                nulls = int(controller == 'NULL_INSTIGATOR' or definition == 'NULL_DEFINITION')
                useful = int(definition == 'DEATHTRAP_NAME')
                r = self.assert_status([start(), event(controller=controller, definition=definition),
                    stop(attempts=1, classified=1, filtered=filtered, nulls=nulls),
                    outcome(value='OBSERVED_PRIMITIVE' if useful else 'OBSERVED_FILTERED')])
                self.assertEqual(r['sessions'][0]['useful'], useful)

    def test_mixed_branches_and_reentry_do_not_add_attempts(self):
        records = [start(), event(controller='NULL_INSTIGATOR', definition='NOT_READ'),
                   event(ordinal=2, attempt=2), stop(attempts=2, classified=2, nulls=1, reentry=7),
                   outcome(value='OBSERVED_PRIMITIVE')]
        self.assert_status(records)

    def test_twenty_four_classifications_and_event_limit(self):
        records = [start()] + [event(ordinal=i, attempt=i) for i in range(1, 25)]
        records += ['LIMIT reason=EVENTS', stop(attempts=24, classified=24, limit='EVENTS'),
                    outcome(value='OBSERVED_PRIMITIVE')]
        self.assert_status(records)

    def test_time_limit_zero_and_after_repeated_stop(self):
        self.assert_status([start(), 'LIMIT reason=TIME', stop(limit='TIME'), outcome()])
        self.assert_status(transcript() + ['LIMIT reason=TIME', stop(limit='TIME'), outcome()])

    def test_trailing_control_activity_needs_its_own_stop_and_outcome(self):
        for tail in ('LIMIT reason=TIME', 'ERROR reason=CLOCK', 'REMOVAL_ERROR remaining=1'):
            with self.subTest(tail=tail):
                records = transcript() + [tail]
                report = self.assert_status(records, 'PARTIAL_LOG_TEXT')
                self.assertFalse(report['reader_sections_complete'])
                self.assertTrue(report['sessions'][0]['awaiting_stop'])
                self.assert_status(records + [start(2), stop(2), outcome(2)], 'INVALID_LOG_TEXT')
        self.assert_status(transcript() + ['ERROR reason=CLOCK', stop(errors=1), outcome(value='REFUSED')],
                           'REFUSED_LOG_TEXT')
        records = [start(), 'REMOVAL_ERROR remaining=1', stop(remaining=1, cleanup_failures=1),
                   outcome(value='REFUSED'), 'REMOVAL_ERROR remaining=1']
        self.assert_status(records, 'PARTIAL_LOG_TEXT')
        self.assert_status(records + [stop(remaining=1, cleanup_failures=2), outcome(value='REFUSED')],
                           'REFUSED_LOG_TEXT')

    def test_all_refusal_reasons_preserved(self):
        for reason in ('SCHEMA', 'PLAYER', 'PARAMETER', 'CLOCK', 'TIME', 'BUDGET', 'STOPPED', 'INTERNAL'):
            with self.subTest(reason=reason):
                counts = 'ops=64 stages=64,0,0,0' if reason == 'BUDGET' else 'ops=0 stages=0,0,0,0'
                records = [start(), 'REFUSED epoch=1 reason={} {}'.format(reason, counts),
                    stop(attempts=1, refusals=1, limit='TIME' if reason == 'TIME' else 'NONE'),
                    outcome(value='REFUSED')]
                r = self.assert_status(records, 'REFUSED_LOG_TEXT')
                self.assertTrue(r['cleanup']['prior_refusal_preserved'])

    def test_errors_with_budget_and_internal_fallback(self):
        for record in ('ERROR epoch=1 reason=INTERNAL ops=7 stages=7,0,0,0',
                       'ERROR epoch=1 reason=LOGGING ops=196 stages=58,50,36,52',
                       'ERROR epoch=1 reason=INTERNAL'):
            self.assert_status([start(), record, stop(attempts=1, errors=1), outcome(value='REFUSED')],
                               'REFUSED_LOG_TEXT')

    def test_clock_errors_are_control_errors_not_attempts(self):
        records = [start(), 'ERROR reason=CLOCK', stop(errors=1), outcome(value='REFUSED'),
                   'ERROR reason=CLOCK', stop(errors=2), outcome(value='REFUSED')]
        self.assert_status(records, 'REFUSED_LOG_TEXT')

    def test_removal_retry_preserves_failure_and_cannot_be_clean(self):
        records = [start(), 'REMOVAL_ERROR remaining=1', stop(remaining=1, cleanup_failures=1),
                   outcome(value='REFUSED'), 'NOT_STARTED reason=OVERLAP',
                   stop(cleanup_failures=1), outcome(value='REFUSED')]
        r = self.assert_status(records, 'REFUSED_LOG_TEXT')
        self.assertTrue(r['cleanup']['reader_handles_resolved'])
        self.invalid_mutation('cleanup_failures=1', 'cleanup_failures=0', records)

    def test_failed_registration_with_uncertainty_and_retry(self):
        records = ['NOT_STARTED reason=REGISTRATION', stop(remaining=1, uncertain=1, refusals=1),
                   outcome(value='REFUSED'), stop(refusals=1), outcome(value='REFUSED')]
        self.assert_status(records, 'REFUSED_LOG_TEXT')

    def test_failed_identifier_and_registration_shapes(self):
        for reason in ('IDENTIFIER', 'REGISTRATION', 'CLOCK'):
            self.assert_status(['NOT_STARTED reason=' + reason, stop(refusals=1), outcome(value='REFUSED')],
                               'REFUSED_LOG_TEXT')

    def test_pre_start_refusal_is_partial_with_no_fabricated_epoch(self):
        for reason in ('CLOCK', 'EPOCH', 'REGISTRATION'):
            r = self.assert_status(['NOT_STARTED reason=' + reason], 'PARTIAL_LOG_TEXT')
            self.assertIsNone(r['sessions'][0]['epoch'])

    def test_overlap_controls_are_notes_and_alone_partial(self):
        self.assert_status(['NOT_STARTED reason=OVERLAP'], 'PARTIAL_LOG_TEXT')
        self.assert_status([start(), 'NOT_STARTED reason=OVERLAP', stop(), outcome()])

    def test_multiple_epochs_and_failed_history_not_laundered(self):
        self.assert_status(transcript() + [start(2), stop(2), outcome(2)])
        records = ['NOT_STARTED reason=IDENTIFIER', stop(refusals=1), outcome(value='REFUSED'),
                   start(2), stop(2), outcome(2)]
        self.assert_status(records, 'REFUSED_LOG_TEXT')

    def test_epoch_mismatch_replay_gap_and_zero(self):
        for before, after in (('START version=0.2.16 epoch=1', 'START version=0.2.16 epoch=0'),
                              ('EVENT epoch=1', 'EVENT epoch=2'), ('OUTCOME epoch=1', 'OUTCOME epoch=2')):
            self.invalid_mutation(before, after)
        for epoch in (1, 3):
            self.assert_status(transcript() + [start(epoch), stop(epoch), outcome(epoch)], 'INVALID_LOG_TEXT')
        self.assert_status([start(2), stop(2), outcome(2)], 'INVALID_LOG_TEXT')

    def test_missing_start_stop_outcome_or_clipped_record(self):
        for records in ([stop(), outcome()], [start()], [start(), stop()], [start(), outcome()]):
            report = reviewer.review_bytes(raw(records))
            self.assertFalse(report['log_text_acceptable'])
        for cut in (1, 8, 20):
            r = reviewer.review_bytes(raw(transcript())[:-cut])
            self.assertFalse(r['log_text_acceptable'])

    def test_duplicate_event_or_outcome_and_missing_event(self):
        records = transcript(True)
        self.assert_status(records[:2] + [records[1]] + records[2:], 'INVALID_LOG_TEXT')
        self.assert_status(records + [records[-1]], 'INVALID_LOG_TEXT')
        self.assert_status([records[0]] + records[2:], 'INVALID_LOG_TEXT')

    def test_repeated_stop_is_legal_but_each_needs_an_outcome(self):
        self.assert_status(transcript() + [stop(), outcome()])
        self.assert_status([start(), stop(), stop(), outcome()], 'INVALID_LOG_TEXT')
        self.assert_status([start(), stop(), 'NOT_STARTED reason=OVERLAP', outcome()], 'INVALID_LOG_TEXT')

    def test_event_after_terminal_or_stop_and_start_while_pending(self):
        self.assert_status(transcript() + [event()], 'INVALID_LOG_TEXT')
        self.assert_status([start(), 'LIMIT reason=TIME', event(), stop(attempts=1, classified=1, limit='TIME'),
                            outcome(value='OBSERVED_PRIMITIVE')], 'INVALID_LOG_TEXT')
        self.assert_status([start(), 'REMOVAL_ERROR remaining=1', stop(remaining=1, cleanup_failures=1),
                            outcome(value='REFUSED'), start(2), stop(2), outcome(2)], 'INVALID_LOG_TEXT')

    def test_version_target_phase_mode_and_schema_unknowns(self):
        for before, after in (('version=0.2.16', 'version=0.2.15'), ('target=DeactivateSkill', 'target=ActivateSkill'),
            ('version=0.2.16', 'version=0x2x16'),
            ('phase=PRE', 'phase=POST'), ('hooks=1', 'hooks=2'), ('mode=STANDALONE_READER', 'mode=ARMED'),
            ('schema=VALID', 'schema=OWNED'), ('schema=VALID', 'schema=UNKNOWN')):
            self.invalid_mutation(before, after)

    def test_unknown_labels_and_bogus_ownership_effect_fields(self):
        for before, after in (('controller=SAME_WRAPPER', 'controller=OWNED'),
            ('definition=DEATHTRAP_NAME', 'definition=PRIVATE_PAYLOAD'),
            ('ownership=UNESTABLISHED', 'ownership=ESTABLISHED'),
            ('ownership=UNESTABLISHED', 'ownership=UNESTABLISHED effect=READY')):
            r = self.invalid_mutation(before, after)
            self.assertNotIn('PRIVATE_PAYLOAD', json.dumps(r))

    def test_contradictory_classification_branches(self):
        for before, after in (('controller=SAME_WRAPPER', 'controller=NULL_INSTIGATOR'),
                              ('definition=DEATHTRAP_NAME', 'definition=NOT_READ')):
            self.invalid_mutation(before, after)

    def test_stage_sum_per_stage_total_and_branch_budget(self):
        for before, after in (('ops=196', 'ops=195'), ('stages=58,50,36,52', 'stages=65,50,36,45'),
                              ('stages=58,50,36,52', 'stages=57,51,36,52'), ('ops=196', 'ops=257')):
            self.invalid_mutation(before, after)

    def test_refusal_budget_exhaustion_and_logging_failure_branch_budget(self):
        self.assert_status([start(), 'REFUSED epoch=1 reason=BUDGET ops=0 stages=0,0,0,0',
                            stop(attempts=1, refusals=1), outcome(value='REFUSED')], 'INVALID_LOG_TEXT')
        self.assert_status([start(), 'ERROR epoch=1 reason=LOGGING ops=0 stages=0,0,0,0',
                            stop(attempts=1, errors=1), outcome(value='REFUSED')], 'INVALID_LOG_TEXT')

    def test_sequence_ordinal_attempt_and_integer_syntax(self):
        for before, after in (('ordinal=1', 'ordinal=2'), ('attempt=1', 'attempt=2'),
                              ('attempt=1', 'attempt=01'), ('epoch=1', 'epoch=-1'),
                              ('ordinal=1', 'ordinal=True'), ('ops=196', 'ops=1e2')):
            self.invalid_mutation(before, after)

    def test_stop_counts_each_counter_and_outcome_consistency(self):
        for field in ('attempts', 'classified', 'filtered', 'nulls', 'refusals', 'errors', 'cleanup_failures'):
            records = transcript()
            records[1] = stop(**{field: 1})
            self.assert_status(records, 'INVALID_LOG_TEXT')
        self.invalid_mutation('value=OBSERVED_PRIMITIVE', 'value=NOT_OBSERVED')
        self.invalid_mutation('value=NOT_OBSERVED', 'value=OBSERVED_FILTERED', transcript())

    def test_handle_uncertainty_reentry_and_history_contradictions(self):
        for changes in ({'remaining': 2}, {'uncertain': 1}, {'reentry': 1}, {'remaining': 1},
                        {'remaining': 1, 'uncertain': 1}):
            self.assert_status([start(), stop(**changes), outcome(value='REFUSED')], 'INVALID_LOG_TEXT')
        records = [start(), event(), stop(attempts=1, classified=1, reentry=2),
                   outcome(value='OBSERVED_PRIMITIVE'), stop(attempts=1, classified=1, reentry=1),
                   outcome(value='OBSERVED_PRIMITIVE')]
        self.assert_status(records, 'INVALID_LOG_TEXT')

    def test_bad_limits_and_missing_limit_marker(self):
        self.assert_status([start(), 'LIMIT reason=EVENTS', stop(limit='EVENTS'), outcome()], 'INVALID_LOG_TEXT')
        self.assert_status([start(), 'LIMIT reason=ATTEMPTS', stop(attempts=64, limit='ATTEMPTS'),
                            outcome(value='OBSERVED_FILTERED')], 'INVALID_LOG_TEXT')
        self.assert_status([start(), stop(limit='TIME'), outcome()], 'INVALID_LOG_TEXT')
        self.assert_status([start(), 'LIMIT reason=TIME', 'LIMIT reason=TIME', stop(limit='TIME'), outcome()],
                            'INVALID_LOG_TEXT')

    def test_removal_order_and_missing_error_history(self):
        records = [start(), 'REMOVAL_ERROR remaining=1', 'REMOVAL_ERROR remaining=1',
                   stop(remaining=1, cleanup_failures=2), outcome(value='REFUSED')]
        self.assert_status(records, 'INVALID_LOG_TEXT')
        self.assert_status([start(), 'REMOVAL_ERROR remaining=1', stop(cleanup_failures=1),
                            outcome(value='REFUSED')], 'INVALID_LOG_TEXT')

    def test_bare_project_and_sdk_frames_crlf_and_noise(self):
        for prefix in ('[UVH-CALLBACK-READ] ', TAG,
                       '2026-10-11 08:27:22.907Z   bbfc  log@59   INFO| ' + TAG):
            blob = b'other SDK startup text\r\n' + raw(transcript(), prefix, '\r\n') + b'other text\r\n'
            self.assertEqual(reviewer.review_bytes(blob)['status'], 'COMPLETE_LOG_TEXT')

    def test_fake_nested_clipped_or_unbounded_frames(self):
        for prefix in ('noise ' + TAG, '[OTHER] ' + TAG, TAG + TAG, '\ufeff' + TAG,
                       '2026-10-11 malformed INFO| ' + TAG):
            self.assertEqual(reviewer.review_bytes(raw(transcript(), prefix))['status'], 'INVALID_LOG_TEXT')
        self.assertEqual(reviewer.review_bytes(raw(transcript()).replace(b'UVH-CALLBACK-READ]',
            b'UVH-CALLBACK-REA'))['status'], 'INVALID_LOG_TEXT')
        self.assertEqual(reviewer.review_bytes(raw(['X' * 400]))['status'], 'INVALID_LOG_TEXT')

    def test_input_types_utf8_nul_and_line_byte_bounds(self):
        for blob, code in (('text', 'INPUT_TYPE'), (b'\xff', 'UTF8'), (b'\0', 'NUL'),
                           (b'X' * (reviewer.MAX_LINE_BYTES + 1), 'LINE_BOUND')):
            r = reviewer.review_bytes(blob)
            self.assertEqual(r['status'], 'INPUT_ERROR')
            self.assertEqual(r['input_error'], code)
        with patch.object(reviewer, 'MAX_BYTES', 8):
            self.assertEqual(reviewer.review_bytes(b'123456789')['input_error'], 'INPUT_BOUND')
        with patch.object(reviewer, 'MAX_LINES', 2):
            self.assertEqual(reviewer.review_bytes(b'1\n2\n3\n')['input_error'], 'INPUT_BOUND')
            self.assertEqual(reviewer.review_bytes(b'1\n2\n3')['input_error'], 'LINE_COUNT_BOUND')

    def test_integer_record_session_issue_and_output_bounds(self):
        r = reviewer.review_bytes(raw([start(2147483648)]))
        self.assertEqual(r['input_error'], 'INTEGER_BOUND')
        with patch.object(reviewer, 'MAX_RECORDS', 2):
            self.assertEqual(reviewer.review_bytes(raw(transcript()))['input_error'], 'RECORD_BOUND')
        with patch.object(reviewer, 'MAX_SESSIONS', 1):
            r = reviewer.review_bytes(raw(transcript() + [start(2), stop(2), outcome(2)]))
            self.assertEqual(r['input_error'], 'SESSION_BOUND')
        with patch.object(reviewer, 'MAX_ISSUES', 2):
            r = reviewer.review_bytes(raw(['UNKNOWN PRIVATE_PAYLOAD'] * 5))
            self.assertEqual(r['issue_count'], 5)
            self.assertEqual(len(r['issues']), 2)
            self.assertTrue(r['issues_truncated'])
            self.assertNotIn('PRIVATE_PAYLOAD', json.dumps(r))

    def test_empty_or_nonreader_log_has_no_reader_text(self):
        for blob in (b'', b'SDK startup\n', b'[UVH-DT-EVENT] STOP remaining=0\n'):
            self.assertEqual(reviewer.review_bytes(blob)['status'], 'NO_READER_TEXT')

    def test_cli_exit_codes_and_bounded_file_read(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'synthetic.log'
            for blob, expected in ((raw(transcript()), 0), (raw([start()]), 1), (b'\xff', 2)):
                path.write_bytes(blob)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(reviewer.main([str(path)]), expected)
                self.assertIsInstance(json.loads(output.getvalue()), dict)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(reviewer.main([str(path.with_name('absent'))]), 2)
            with patch.object(reviewer, 'MAX_BYTES', 1), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(reviewer.main([str(path)]), 2)

    def test_actual_inert_runtime_all_six_branch_transcripts(self):
        for kind in ('null_instigator', 'foreign_class', 'foreign_wrapper', 'null_definition', 'other_name', 'deathtrap'):
            with self.subTest(kind=kind):
                f = inert.CallbackLocalReaderTests(); f.setUp(); f.start()
                if kind == 'null_instigator': f.args.SkillInstigator = None
                if kind == 'foreign_class': f.args.SkillInstigator = inert.UObject(Class=inert.UClass(Name='Other'))
                if kind == 'foreign_wrapper': f.args.SkillInstigator = inert.UObject(Class=f.controller)
                if kind == 'null_definition': f.args.Definition = None
                if kind == 'other_name': f.definition.Name = 'OtherSkill'
                f.fire(); f.call('stop_callback_local_reader'); f.tearDown()
                r = reviewer.review_bytes(('\n'.join(f.h.logs) + '\n').encode())
                self.assertEqual(r['status'], 'COMPLETE_LOG_TEXT', r)
                self.assertEqual(r['sessions'][0]['useful'], int(kind == 'deathtrap'))

    def test_actual_inert_runtime_silence_cancel_and_repeated_stop(self):
        f = inert.CallbackLocalReaderTests(); f.setUp(); f.start()
        f.call('stop_callback_local_reader'); f.call('cancel_init_node'); f.tearDown()
        r = reviewer.review_bytes(('\n'.join(f.h.logs) + '\n').encode())
        self.assertEqual(r['status'], 'COMPLETE_LOG_TEXT', r)
        self.assertEqual(len(r['sessions'][0]['stops']), 2)

    def test_actual_inert_runtime_refusal_clock_and_removal_retry(self):
        for kind in ('schema', 'clock', 'removal', 'timeout'):
            with self.subTest(kind=kind):
                f = inert.CallbackLocalReaderTests(); f.setUp(); f.start()
                if kind == 'schema':
                    f.fn.NumParams = 2; f.fire()
                if kind == 'clock':
                    f.clock = 999.0; f.call('stop_callback_local_reader')
                if kind == 'removal':
                    f.h.fail_remove = True; f.call('stop_callback_local_reader')
                    f.h.fail_remove = False; f.call('stop_callback_local_reader')
                if kind == 'timeout':
                    f.clock = 1120.0; f.fire()
                f.tearDown()
                r = reviewer.review_bytes(('\n'.join(f.h.logs) + '\n').encode())
                self.assertEqual(r['status'], 'REFUSED_LOG_TEXT', r)

    def test_actual_inert_runtime_registration_uncertainty_and_existing_identifier(self):
        for existing in (True, False):
            with self.subTest(existing=existing):
                f = inert.CallbackLocalReaderTests(); f.setUp()
                foreign = lambda *values: None
                if existing:
                    f.h.hooks[f.key()] = foreign
                else:
                    def add(*values):
                        f.h.hooks[f.key()] = foreign
                        raise inert.PrivateError('PRIVATE')
                    f.sdk.hooks.add_hook = add
                self.assertFalse(f.call('start_callback_local_reader'))
                if not existing:
                    f.h.hooks.clear(); f.call('stop_callback_local_reader')
                f.tearDown()
                r = reviewer.review_bytes(('\n'.join(f.h.logs) + '\n').encode())
                self.assertEqual(r['status'], 'REFUSED_LOG_TEXT', r)

    def test_actual_inert_runtime_classification_limit_and_delayed_time_stop(self):
        f = inert.CallbackLocalReaderTests(); f.setUp(); f.start()
        for _ in range(24): f.fire()
        f.call('stop_callback_local_reader'); f.tearDown()
        r = reviewer.review_bytes(('\n'.join(f.h.logs) + '\n').encode())
        self.assertEqual(r['status'], 'COMPLETE_LOG_TEXT', r)
        self.assertEqual(r['sessions'][0]['classified'], 24)
        f = inert.CallbackLocalReaderTests(); f.setUp(); f.start(); f.call('stop_callback_local_reader')
        f.clock = 1120.0; f.call('stop_callback_local_reader'); f.tearDown()
        r = reviewer.review_bytes(('\n'.join(f.h.logs) + '\n').encode())
        self.assertEqual(r['status'], 'COMPLETE_LOG_TEXT', r)
        self.assertEqual(r['sessions'][0]['limit'], 'TIME')

    def test_actual_inert_runtime_error_logging_and_deferred_stop(self):
        for kind in ('exception', 'logging', 'deferred'):
            with self.subTest(kind=kind):
                f = inert.CallbackLocalReaderTests(); f.setUp(); f.start()
                if kind == 'exception':
                    def fail(obj, key):
                        if key == 'SkillInstigator': raise inert.PrivateError('PRIVATE_PAYLOAD')
                    f.args.on_read = fail
                if kind == 'logging':
                    emit = f.h.scope['_cr_emit']
                    f.h.scope['_cr_emit'] = lambda payload: False if payload.startswith('EVENT ') else emit(payload)
                if kind == 'deferred':
                    f.args.on_read = lambda obj, key: f.call('stop_callback_local_reader') if key == 'SkillInstigator' else None
                f.fire(); f.tearDown()
                r = reviewer.review_bytes(('\n'.join(f.h.logs) + '\n').encode())
                self.assertEqual(r['status'], 'REFUSED_LOG_TEXT', r)
                self.assertNotIn('PRIVATE_PAYLOAD', json.dumps(r))


if __name__ == '__main__':
    unittest.main()
