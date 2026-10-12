"""Strict text and inert emitted-log cases, not natural callback evidence."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import test_deathtrap_passive_events as inert

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/review_deathtrap_passive_event_log.py'
spec = importlib.util.spec_from_file_location('passive_log_review', SCRIPT)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
T = '[UVH-DT-EVENT] '
START = T + review.START
BASE = T + 'BASELINE points=(1, 0) ranks=(0, 0, 0)'
FINAL = T + 'FINAL points=(1, 0) ranks=(0, 0, 0) unchanged=True'
STOP = T + 'STOP remaining=0 captured=0 attempts=0 reentrant=0 uncertain=0 cleanup_failures=0'
OUT = T + 'OUTCOME value=NOT_OBSERVED'
CLEANUP = ['['+tag+'] STOP remaining=0 captured=0 callbacks=0 skipped=0' for tag in review.FAMILIES[:3]] + [
    '[UVH-INITNODE] Observers remaining=0',
    "[UVH-NEWNODE] RESTORE result=True skills=['MorePep', 'Myelin'] cells=[True, False, True] (methods assign, assign)"]


def event(n=1):
    return T + 'EVENT ordinal={} target=DeactivateSkill phase=PRE attribution=NONE'.format(n)


def text(lines):
    return ('\n'.join(lines)+'\n').encode()


def silent():
    return [START, BASE, FINAL, STOP, OUT, *CLEANUP]


def observed(n=1):
    return [START, BASE, *(event(i) for i in range(1,n+1)),
        *([T+'LIMIT reason=EVENTS'] if n==24 else []), FINAL,
        STOP.replace('captured=0 attempts=0','captured={} attempts={}'.format(n,n)),
        T+'OUTCOME value=OBSERVED_UNATTRIBUTED', *CLEANUP]


class PassiveLogReviewTests(unittest.TestCase):
    def result(self, lines):
        return review.review_bytes(text(lines))

    def invalid(self, lines):
        result=self.result(lines)
        self.assertEqual(result['status'],'INVALID_LOG_TEXT')
        self.assertFalse(result['log_text_acceptable'])
        return result

    def generated(self, mode):
        fixture=inert.PassiveEventTests()
        fixture.setUp()
        try:
            fixture.start()
            if mode=='event':fixture.fire()
            if mode=='failure':
                fixture.h.fail_remove=True
                fixture.call('stop_deathtrap_events')
                fixture.h.fail_remove=False
            fixture.call('stop_deathtrap_events')
            fixture.call('cancel_init_node')
            return fixture.h.logs[:]
        finally:
            fixture.tearDown()

    def test_plain_silence_is_complete_without_absence_inference(self):
        r=self.result(silent());self.assertEqual(r['status'],'COMPLETE_LOG_TEXT')
        self.assertEqual(r['runs'][0]['stops'][0]['outcome'],'NOT_OBSERVED')
        self.assertEqual(r['engine_behavior'],'NOT_ESTABLISHED');self.assertFalse(r['native_effect_ready'])

    def test_observed_entry_remains_unattributed_attempt(self):
        r=self.result(observed());self.assertEqual(r['status'],'COMPLETE_LOG_TEXT')
        self.assertEqual(r['attribution'],'NONE');self.assertIn('attempted entry',r['event_meaning'])

    def test_actual_inert_v15_emitted_silence_and_cancel(self):
        self.assertEqual(self.result(self.generated('silence'))['status'],'COMPLETE_LOG_TEXT')

    def test_actual_inert_v15_emitted_entry_stop_and_cancel(self):
        self.assertEqual(self.result(self.generated('event'))['status'],'COMPLETE_LOG_TEXT')

    def test_actual_inert_v15_failed_cleanup_retry_history(self):
        r=self.result(self.generated('failure'));self.assertEqual(r['status'],'REFUSED_LOG_TEXT')
        self.assertTrue(r['log_text_consistent']);self.assertTrue(r['cleanup']['observer_handles_resolved'])
        self.assertTrue(r['cleanup']['prior_refusal_preserved'])

    def test_actual_sdk_wrapper_does_not_make_timestamp_engine_time(self):
        wrap='2026-10-11 06:43:18.836Z   7398    ~ UltimateVaultHunterDeathtrapBoost\\__init__.py@19   INFO| [UVH-BOOST] '
        r=self.result([wrap+x for x in silent()]);self.assertEqual(r['status'],'COMPLETE_LOG_TEXT')
        self.assertNotIn('timestamp',json.dumps(r))

    def test_boost_prefix_and_crlf_are_supported(self):
        raw=('\r\n'.join('[UVH-BOOST] '+x for x in silent())+'\r\n').encode()
        self.assertEqual(review.review_bytes(raw)['status'],'COMPLETE_LOG_TEXT')

    def test_wrong_version_refuses(self):self.invalid([x.replace('v0.2.15','v0.2.14') for x in silent()])
    def test_activation_path_refuses(self):self.invalid([x.replace('DeactivateSkill','ActivateSkill') for x in observed()])
    def test_post_phase_refuses(self):self.invalid([x.replace('phase=PRE','phase=POST') for x in observed()])
    def test_owned_attribution_refuses(self):self.invalid([x.replace('attribution=NONE','attribution=OWNED') for x in observed()])
    def test_unknown_target_fields_refuse(self):self.invalid([START+' object=private',*silent()[1:]])
    def test_unknown_reason_refuses(self):self.invalid([START,BASE,T+'ABORT reason=USER',*silent()[2:]])
    def test_unknown_outcome_refuses(self):self.invalid([*silent()[:4],T+'OUTCOME value=SUCCESS',*CLEANUP])
    def test_suffix_comment_refuses(self):self.invalid([START+' # okay',*silent()[1:]])
    def test_leading_space_frame_refuses(self):self.invalid([' '+START,*silent()[1:]])
    def test_hidden_tag_cannot_be_ignored(self):self.invalid(['[UVH-OTHER] '+START,*silent()[1:]])
    def test_embedded_cr_refuses(self):self.invalid([START.replace('DeactivateSkill','Deactivate\rSkill'),*silent()[1:]])
    def test_payload_eval_text_is_not_executed_or_echoed(self):
        marker='__import__("os").system("private-value")'
        r=self.invalid([T+'EVENT ordinal='+marker,*silent()])
        self.assertNotIn('private-value',json.dumps(r));self.assertNotIn('__import__',json.dumps(r))

    def test_negative_counter_refuses(self):self.invalid([x.replace('attempts=0','attempts=-1') for x in silent()])
    def test_boolean_counter_refuses(self):self.invalid([x.replace('attempts=0','attempts=True') for x in silent()])
    def test_nonfinite_counter_refuses(self):self.invalid([x.replace('attempts=0','attempts=nan') for x in silent()])
    def test_leading_zero_counter_refuses(self):self.invalid([x.replace('attempts=0','attempts=00') for x in silent()])
    def test_31bit_counter_bound_refuses(self):
        r=self.result([x.replace('attempts=0','attempts=2147483648') for x in silent()]);self.assertEqual(r['status'],'INPUT_ERROR')
    def test_31bit_points_allowed_without_native_claim(self):
        r=self.result([x.replace('points=(1, 0)','points=(2147483647, 0)') for x in silent()]);self.assertEqual(r['status'],'COMPLETE_LOG_TEXT')
    def test_rank_one_candidate_refuses(self):self.invalid([x.replace('ranks=(0, 0, 0)','ranks=(1, 0, 0)') for x in silent()])
    def test_nonzero_original_rank_is_allowed(self):
        self.assertEqual(self.result([x.replace('ranks=(0, 0, 0)','ranks=(0, 1, 2)') for x in silent()])['status'],'COMPLETE_LOG_TEXT')
    def test_final_points_mismatch_refuses(self):self.invalid([x.replace('FINAL points=(1, 0)','FINAL points=(0, 0)') for x in silent()])
    def test_final_ranks_mismatch_refuses(self):self.invalid([x.replace('FINAL points=(1, 0) ranks=(0, 0, 0)','FINAL points=(1, 0) ranks=(0, 1, 0)') for x in silent()])
    def test_duplicate_baseline_refuses(self):self.invalid([START,BASE,BASE,*silent()[2:]])
    def test_event_before_baseline_refuses(self):self.invalid([START,event(),*silent()[1:]])
    def test_missing_ordinal_refuses(self):self.invalid([x.replace('ordinal=1','ordinal=2') for x in observed()])
    def test_duplicate_event_refuses(self):self.invalid([*observed()[:3],event(),*observed()[3:]])
    def test_event_after_stop_refuses(self):self.invalid([*silent(),event()])
    def test_duplicate_final_refuses(self):self.invalid([*silent()[:3],FINAL,*silent()[3:]])
    def test_outcome_before_stop_refuses(self):self.invalid([START,BASE,OUT,*silent()[2:]])
    def test_duplicate_outcome_refuses(self):self.invalid([*silent(),OUT])
    def test_missing_final_is_partial(self):self.assertEqual(self.result([START,BASE,STOP,OUT,*CLEANUP])['status'],'PARTIAL_LOG_TEXT')
    def test_missing_outcome_is_partial(self):self.assertEqual(self.result([START,BASE,FINAL,STOP,*CLEANUP])['status'],'PARTIAL_LOG_TEXT')
    def test_missing_stop_is_partial(self):self.assertEqual(self.result([START,BASE,FINAL,*CLEANUP])['status'],'PARTIAL_LOG_TEXT')
    def test_orphan_stop_is_partial(self):self.assertEqual(self.result([STOP,OUT,*CLEANUP])['status'],'PARTIAL_LOG_TEXT')
    def test_restart_before_outcome_refuses(self):self.invalid([START,BASE,FINAL,STOP,*silent()])
    def test_two_complete_runs_remain_distinct(self):
        r=self.result(silent()+observed());self.assertEqual(r['status'],'COMPLETE_LOG_TEXT');self.assertEqual(len(r['runs']),2)
    def test_repeated_stop_cancel_does_not_invent_run(self):
        r=self.result([*silent()[:5],STOP,OUT,*CLEANUP]);self.assertEqual(r['status'],'COMPLETE_LOG_TEXT');self.assertEqual(len(r['runs']),1)
    def test_active_overlap_control_refusal_does_not_taint_observation(self):
        r=self.result([START,BASE,T+'NOT_STARTED reason=OVERLAP',*silent()[2:]])
        self.assertEqual(r['status'],'COMPLETE_LOG_TEXT');self.assertEqual(r['runs'][0]['overlap_refusals'],1)
    def test_registration_overlap_before_start_does_not_invent_run(self):
        r=self.result([T+'NOT_STARTED reason=OVERLAP',*silent()])
        self.assertEqual(r['status'],'COMPLETE_LOG_TEXT');self.assertEqual(len(r['runs']),1)
        self.assertEqual(r['unattached_control_refusals'],1)
    def test_standalone_overlap_is_partial_control_refusal(self):
        self.assertEqual(self.result([T+'NOT_STARTED reason=OVERLAP'])['status'],'PARTIAL_LOG_TEXT')
    def test_start_state_refusal_with_stop_is_consistent_refused(self):
        r=self.result([T+'NOT_STARTED reason=STATE',STOP,T+'OUTCOME value=REFUSED',*CLEANUP])
        self.assertEqual(r['status'],'REFUSED_LOG_TEXT');self.assertTrue(r['observer_sections_complete'])
    def test_registered_but_not_published_refusal_has_no_final(self):
        r=self.result([START,BASE,T+'NOT_STARTED reason=REGISTRATION',STOP,T+'OUTCOME value=REFUSED',*CLEANUP])
        self.assertEqual(r['status'],'REFUSED_LOG_TEXT');self.assertTrue(r['log_text_consistent'])
    def test_abort_state_unverified_final_is_refused(self):
        r=self.result([START,BASE,T+'ABORT reason=STATE',T+'FINAL UNVERIFIED reason=STATE',STOP.replace('attempts=0','attempts=1'),T+'OUTCOME value=REFUSED',*CLEANUP])
        self.assertEqual(r['status'],'REFUSED_LOG_TEXT');self.assertEqual(r['cleanup']['duration_restore'],'NOT_ESTABLISHED')
    def test_unverified_final_cannot_claim_not_observed(self):
        self.invalid([START,BASE,T+'FINAL UNVERIFIED reason=STATE',STOP,OUT,*CLEANUP])
    def test_24event_limit_is_consistent(self):self.assertEqual(self.result(observed(24))['status'],'COMPLETE_LOG_TEXT')
    def test_25th_event_refuses(self):self.invalid(observed(25))
    def test_missing_24event_limit_refuses(self):self.invalid([x for x in observed(24) if 'LIMIT' not in x])
    def test_wrong_event_limit_counter_refuses(self):self.invalid([START,BASE,T+'LIMIT reason=EVENTS',*silent()[2:]])
    def test_attempt_limit64_reentrant63_is_consistent(self):
        r=self.result([START,BASE,T+'LIMIT reason=ATTEMPTS',FINAL,STOP.replace('attempts=0 reentrant=0','attempts=64 reentrant=63'),OUT,*CLEANUP])
        self.assertEqual(r['status'],'COMPLETE_LOG_TEXT')
    def test_attempt_limit_without64_refuses(self):self.invalid([START,BASE,T+'LIMIT reason=ATTEMPTS',*silent()[2:]])
    def test_attempt65_refuses(self):self.invalid([x.replace('attempts=0','attempts=65') for x in silent()])
    def test_attempt64_requires_limit(self):self.invalid([x.replace('attempts=0','attempts=64') for x in silent()])
    def test_all_attempts_cannot_be_reentrant(self):
        self.invalid([x.replace('attempts=0 reentrant=0','attempts=1 reentrant=1') for x in silent()])
    def test_captures_plus_reentrant_cannot_exceed_attempts(self):self.invalid([x.replace('reentrant=0','reentrant=1') for x in observed()])
    def test_time_limit_during_silence_has_no_engine_clock_claim(self):
        r=self.result([START,BASE,T+'LIMIT reason=TIME',*silent()[2:]]);self.assertEqual(r['status'],'COMPLETE_LOG_TEXT')
        self.assertEqual(r['authenticity'],'NOT_ESTABLISHED')
    def test_pending_owned_cleanup_is_refused_even_with_old_arrays_restored(self):
        s=STOP.replace('remaining=0','remaining=1').replace('cleanup_failures=0','cleanup_failures=1')
        r=self.result([START,BASE,FINAL,T+'REMOVAL_ERROR remaining=1',s,T+'OUTCOME value=REFUSED',*CLEANUP])
        self.assertEqual(r['status'],'REFUSED_LOG_TEXT');self.assertFalse(r['cleanup']['observer_handles_resolved'])
    def test_pending_uncertain_registration_is_never_claimed_clean(self):
        s=STOP.replace('remaining=0','remaining=1').replace('uncertain=0','uncertain=1')
        r=self.result([T+'NOT_STARTED reason=REGISTRATION',s,T+'OUTCOME value=REFUSED',*CLEANUP])
        self.assertEqual(r['status'],'REFUSED_LOG_TEXT');self.assertTrue(r['log_text_consistent'])
    def test_cleanup_retry_cannot_erase_failure_history(self):
        s=STOP.replace('remaining=0','remaining=1').replace('cleanup_failures=0','cleanup_failures=1')
        self.invalid([START,BASE,FINAL,T+'REMOVAL_ERROR remaining=1',s,T+'OUTCOME value=REFUSED',STOP,OUT,*CLEANUP])
    def test_restart_while_pending_refuses(self):
        s=STOP.replace('remaining=0','remaining=1').replace('uncertain=0','uncertain=1')
        self.invalid([T+'NOT_STARTED reason=REGISTRATION',s,T+'OUTCOME value=REFUSED',*silent()])
    def test_retry_capture_counts_cannot_change(self):self.invalid([*observed()[:6],STOP,OUT,*CLEANUP])
    def test_uncertain_cannot_exceed_remaining(self):self.invalid([x.replace('uncertain=0','uncertain=1') for x in silent()])
    def test_old_family_nonzero_is_separate_partial_cleanup(self):
        r=self.result([*silent(), '[UVH-UI] STOP remaining=1 captured=0 callbacks=0 skipped=0'])
        self.assertEqual(r['status'],'PARTIAL_LOG_TEXT');self.assertTrue(r['cleanup']['observer_handles_resolved'])
    def test_malformed_later_old_stop_cannot_hide_behind_prior_zero(self):
        self.invalid([*silent(),'[UVH-UI] STOP remaining=-1 captured=0 callbacks=0 skipped=0'])
    def test_malformed_later_init_stop_cannot_hide_behind_prior_zero(self):
        self.invalid([*silent(),'[UVH-INITNODE] Observers remaining=0 extra'])
    def test_old_zero_before_activity_does_not_count(self):
        self.assertEqual(self.result([*CLEANUP,*silent()[:5]])['status'],'PARTIAL_LOG_TEXT')
    def test_restore_false_after_true_is_partial(self):
        self.assertEqual(self.result([*silent(),CLEANUP[-1].replace('result=True','result=False')])['status'],'PARTIAL_LOG_TEXT')
    def test_restore_wrong_original_arrays_is_partial(self):
        self.assertEqual(self.result([x.replace("['MorePep', 'Myelin']","['MorePep']") for x in silent()])['status'],'PARTIAL_LOG_TEXT')
    def test_restore_method_variants_are_supported(self):
        self.assertEqual(self.result([x.replace('methods assign, assign','methods slice, clear+extend') for x in silent()])['status'],'COMPLETE_LOG_TEXT')
    def test_valid_passive_without_old_cleanup_is_partial(self):self.assertEqual(self.result(silent()[:5])['status'],'PARTIAL_LOG_TEXT')
    def test_unrelated_sdk_log_is_no_observer_text_without_echo(self):
        r=self.result(['startup-private-value']);self.assertEqual(r['status'],'NO_OBSERVER_TEXT');self.assertNotIn('startup-private-value',json.dumps(r))
    def test_empty_input_is_no_observer_text(self):self.assertEqual(review.review_bytes(b'')['status'],'NO_OBSERVER_TEXT')
    def test_invalid_utf8_is_closed_input_error(self):self.assertEqual(review.review_bytes(b'\xff')['input_error'],'UTF8')
    def test_nonbytes_input_is_closed_input_error(self):self.assertEqual(review.review_bytes('private')['input_error'],'INPUT_TYPE')
    def test_byte_bound(self):
        with patch.object(review,'MAX_BYTES',16):self.assertEqual(review.review_bytes(b'x'*17)['input_error'],'INPUT_BOUND')
    def test_line_count_bound_before_split(self):
        with patch.object(review,'MAX_LINES',4):self.assertEqual(review.review_bytes(b'\n'*5)['input_error'],'INPUT_BOUND')
    def test_line_count_bound_without_final_newline(self):
        with patch.object(review,'MAX_LINES',4):self.assertEqual(review.review_bytes(b'x\nx\nx\nx\nx')['input_error'],'LINE_COUNT_BOUND')
    def test_unrelated_line_bound(self):
        with patch.object(review,'MAX_LINE_BYTES',16):self.assertEqual(review.review_bytes(b'x'*17)['input_error'],'LINE_BOUND')
    def test_event_256byte_bound(self):self.invalid([T+'x'*256,*silent()])
    def test_unknown_record_bound_cannot_skip_early_continue(self):
        with patch.object(review,'MAX_RECORDS',4):self.assertEqual(self.result([T+'bad']*5)['input_error'],'RECORD_BOUND')
    def test_run_bound(self):
        with patch.object(review,'MAX_RUNS',1):self.assertEqual(self.result(silent()+silent())['input_error'],'RUN_BOUND')
    def test_issue_output_is_bounded_and_closed(self):
        with patch.object(review,'MAX_ISSUES',2):
            r=self.result([T+'private-'+str(i) for i in range(4)])
        self.assertEqual(len(r['issues']),2);self.assertEqual(r['issue_count'],4);self.assertTrue(r['issues_truncated'])
        self.assertNotIn('private-',json.dumps(r))
    def test_cli_complete_exit0_matches_api(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path=Path(folder)/'synthetic.log';raw=text(silent());path.write_bytes(raw)
            p=subprocess.run([sys.executable,'-B',str(SCRIPT),str(path)],capture_output=True)
            self.assertEqual(p.returncode,0);self.assertEqual(json.loads(p.stdout),review.review_bytes(raw))
    def test_cli_partial_exit1_matches_api(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path=Path(folder)/'synthetic.log';raw=text([START,BASE]);path.write_bytes(raw)
            p=subprocess.run([sys.executable,'-B',str(SCRIPT),str(path)],capture_output=True)
            self.assertEqual(p.returncode,1);self.assertEqual(json.loads(p.stdout),review.review_bytes(raw))
    def test_cli_file_error_exit2_has_no_path_or_exception_text(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path=Path(folder)/'private-secret.log'
            p=subprocess.run([sys.executable,'-B',str(SCRIPT),str(path)],capture_output=True)
            self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stdout)['input_error'],'FILE_READ')
            self.assertNotIn('private-secret',p.stdout.decode());self.assertEqual(p.stderr,b'')
    def test_cli_refused_exit1_and_input_unchanged(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path=Path(folder)/'synthetic.log';raw=text([T+'NOT_STARTED reason=STATE',STOP,T+'OUTCOME value=REFUSED',*CLEANUP]);path.write_bytes(raw)
            p=subprocess.run([sys.executable,'-B',str(SCRIPT),str(path)],capture_output=True)
            self.assertEqual(p.returncode,1);self.assertEqual(json.loads(p.stdout)['status'],'REFUSED_LOG_TEXT');self.assertEqual(path.read_bytes(),raw)
    def test_import_and_cli_do_not_load_installed_sdk(self):
        p=subprocess.run([sys.executable,'-I','-B','-c',
            'import runpy,sys;runpy.run_path(sys.argv[1]);assert "unrealsdk" not in sys.modules and "mods_base" not in sys.modules',str(SCRIPT)],capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr.decode())
    def test_main_output_is_plain_JSON(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path=Path(folder)/'synthetic.log';path.write_bytes(text(silent()))
            stream=io.StringIO()
            with contextlib.redirect_stdout(stream):code=review.main([str(path)])
            self.assertEqual(code,0);self.assertEqual(json.loads(stream.getvalue())['status'],'COMPLETE_LOG_TEXT')
