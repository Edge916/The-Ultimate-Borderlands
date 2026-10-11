"""Meaningful simulated transitions; no SDK fixtures or native adapter."""
from dataclasses import replace
import math
import importlib.util
import sys
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('sdk_free_effect_contract_model',
    Path(__file__).resolve().parents[1] / 'design/overclock_effect_contract_model.py')
model = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = model  # dataclasses resolve annotations via the registered module
SPEC.loader.exec_module(model)


class EffectContractModelTests(unittest.TestCase):
    def setUp(self):
        self.tokens = tuple(object() for _ in range(5))
        session, owner, world, definition, skill = self.tokens
        self.ledger = model.ContractModel(session, owner, world, definition)
        self.obs = model.Observation(session, owner, world, definition, skill,
                                     1, 12.0, 60.0, 60.0, 0, 1, (skill,))

    def applied(self):
        action = self.ledger.propose_apply(self.obs)
        after = replace(self.obs, duration=action.value)
        self.assertTrue(self.ledger.acknowledge(action, after, True))
        return after

    def test_apply_and_restore_return_data_without_changing_observation(self):
        action = self.ledger.propose_apply(self.obs)
        self.assertEqual(self.obs.duration, 60)
        self.assertIs(action.target, self.obs.skill)
        self.assertEqual(action.value, 75)
        self.assertEqual(self.ledger.record.phase, 'PENDING_APPLY')
        after = replace(self.obs, duration=75)
        self.assertTrue(self.ledger.acknowledge(action, after, True))
        restore = self.ledger.propose_cleanup(after)
        self.assertIs(restore.target, action.target)
        self.assertEqual(restore.value, 60)
        self.assertTrue(self.ledger.acknowledge(restore, self.obs, True))
        self.assertIsNone(self.ledger.record)
        self.assertFalse(self.ledger.enabled)
        self.assertEqual(self.ledger.watermark, 1)

    def test_rank_zero_skips_without_consuming_attempt(self):
        self.assertIsNone(self.ledger.propose_apply(replace(self.obs, rank=0)))
        self.assertEqual(self.ledger.attempts, 0)
        self.assertEqual(self.ledger.last, 'RANK_ZERO_SKIP')

    def test_unknown_bool_other_ranks_refuse(self):
        for rank in (None, True, False, -1, 2, 1.0):
            self.assertIsNone(self.ledger.propose_apply(replace(self.obs, rank=rank)))
        self.assertEqual(self.ledger.attempts, 0)

    def test_same_name_foreign_owner_token_is_not_equal_identity(self):
        class Named:
            name = 'Controller_0'
            def __eq__(self, other): raise AssertionError('token equality must never run')
        owner = Named(); other = Named()
        ledger = model.ContractModel(self.obs.session, owner, self.obs.world, self.obs.definition)
        self.assertIsNone(ledger.propose_apply(replace(self.obs, owner=other)))
        self.assertIsNotNone(ledger.propose_apply(replace(self.obs, owner=owner)))

    def test_changed_session_world_definition_or_missing_skill_refuses(self):
        for field in ('session', 'world', 'definition', 'owner', 'skill'):
            self.assertIsNone(self.ledger.propose_apply(replace(self.obs, **{field: None})))
        self.assertIsNone(self.ledger.record)

    def test_multiple_matches_empty_membership_foreign_match_refuse(self):
        for matches in ((), (self.obs.skill, object()), (object(),), [self.obs.skill]):
            self.assertIsNone(self.ledger.propose_apply(replace(self.obs, matches=matches)))

    def test_unknown_or_non_quiescent_proof_refuses(self):
        for kwargs in ({'verified':False}, {'verified':1}, {'quiescent':False}, {'quiescent':None}):
            self.assertIsNone(self.ledger.propose_apply(replace(self.obs, **kwargs)))

    def test_missing_bool_nonfinite_negative_activation_time_refuses(self):
        for value in (None, True, -1, math.nan, math.inf, -math.inf, '12'):
            self.assertIsNone(self.ledger.propose_apply(replace(self.obs, activated_time=value)))

    def test_invalid_generation_refuses(self):
        for value in (None, True, 0, -1, 1.0):
            self.assertIsNone(self.ledger.propose_apply(replace(self.obs, generation=value)))

    def test_nonfinite_bool_or_nondefault_duration_and_base_refuse(self):
        for field in ('duration','base'):
            for value in (None, True, math.nan, math.inf, -math.inf, 75, '60'):
                self.assertIsNone(self.ledger.propose_apply(replace(self.obs, **{field:value})))

    def test_unknown_bool_nonempty_modifiers_refuse(self):
        for value in (None, True, False, -1, 1, 0.0):
            self.assertIsNone(self.ledger.propose_apply(replace(self.obs, modifiers=value)))

    def test_near_default_uses_recorded_before_value(self):
        obs = replace(self.obs, duration=60.04)
        action = self.ledger.propose_apply(obs)
        self.assertAlmostEqual(action.value, 75.04, places=10)
        self.assertEqual(self.ledger.record.before, 60.04)

    def test_reentrant_pending_and_applied_events_do_not_stack(self):
        action = self.ledger.propose_apply(self.obs)
        self.assertIsNone(self.ledger.propose_apply(self.obs))
        self.ledger.acknowledge(action, replace(self.obs, duration=75), True)
        self.assertIsNone(self.ledger.propose_apply(self.obs))
        self.assertEqual(self.ledger.attempts, 1)

    def test_retired_generation_cannot_be_reused_even_with_replacement(self):
        action = self.ledger.propose_apply(self.obs)
        self.ledger.acknowledge(action, replace(self.obs,duration=75), True)
        self.assertTrue(self.ledger.retire_original(self.obs.skill, 1,
            verified_ended=True, write_interval_closed=True))
        skill = object(); obs = replace(self.obs, skill=skill, matches=(skill,))
        self.assertIsNone(self.ledger.propose_apply(obs))
        self.assertEqual(self.ledger.watermark, 1)

    def test_verified_natural_end_allows_a_new_generation_without_stacking(self):
        self.applied()
        self.assertTrue(self.ledger.retire_original(self.obs.skill,1,
            verified_ended=True,write_interval_closed=True))
        skill=object();new=replace(self.obs,skill=skill,matches=(skill,),generation=2)
        action=self.ledger.propose_apply(new)
        self.assertIs(action.target,skill)
        self.assertEqual(action.value,75)
        self.assertEqual(self.ledger.attempts,2)

    def test_foreign_unknown_or_inflight_end_does_not_retire_original(self):
        self.applied()
        for kwargs in ({'verified_ended':False,'write_interval_closed':True},
                       {'verified_ended':True,'write_interval_closed':False}):
            self.assertFalse(self.ledger.retire_original(self.obs.skill,1,**kwargs))
        self.assertFalse(self.ledger.retire_original(object(),1,verified_ended=True,write_interval_closed=True))
        self.assertIsNotNone(self.ledger.record)

    def test_enormous_int_values_fail_closed_instead_of_overflowing(self):
        for field in ('duration','base','activated_time'):
            self.assertIsNone(self.ledger.propose_apply(replace(self.obs,**{field:10**1000})))

    def test_session_attempt_cap_refuses_before_action(self):
        self.ledger.attempts = model.MAX_ATTEMPTS
        self.assertIsNone(self.ledger.propose_apply(self.obs))
        self.assertIsNone(self.ledger.record)

    def test_counterfeit_or_stale_action_ack_cannot_commit(self):
        action = self.ledger.propose_apply(self.obs)
        self.assertFalse(self.ledger.acknowledge(replace(action),replace(self.obs,duration=75),True))
        self.assertEqual(self.ledger.record.phase,'PENDING_APPLY')
        self.assertTrue(self.ledger.acknowledge(action,replace(self.obs,duration=75),True))
        self.assertFalse(self.ledger.acknowledge(action,replace(self.obs,duration=75),True))

    def test_failed_apply_keeps_record_before_cleanup(self):
        action = self.ledger.propose_apply(self.obs)
        self.assertFalse(self.ledger.acknowledge(action,replace(self.obs,duration=75),False))
        self.assertEqual(self.ledger.record.phase,'UNCERTAIN')
        self.assertFalse(self.ledger.enabled)
        restore = self.ledger.propose_cleanup(replace(self.obs,duration=75))
        self.assertEqual(restore.value,60)
        self.ledger.acknowledge(restore,self.obs,True)
        self.assertEqual(self.ledger.counts['apply_failed'],1)

    def test_failed_apply_already_before_retires_without_blind_rollback(self):
        action = self.ledger.propose_apply(self.obs)
        self.ledger.acknowledge(action,self.obs,False)
        self.assertIsNone(self.ledger.propose_cleanup(self.obs))
        self.assertIsNone(self.ledger.record)
        self.assertEqual(self.ledger.last,'ALREADY_CLEAN')

    def test_apply_unknown_readback_or_changed_rank_retains_uncertain(self):
        for kwargs in ({'duration':None}, {'duration':74}, {'rank':0}, {'base':61}, {'quiescent':False}):
            ledger = model.ContractModel(*self.tokens[:4]); action=ledger.propose_apply(self.obs)
            after=replace(replace(self.obs,duration=75),**kwargs)
            self.assertFalse(ledger.acknowledge(action,after,True))
            self.assertEqual(ledger.record.phase,'UNCERTAIN')

    def test_replacement_reuses_signature_but_cleanup_never_targets_it(self):
        after = self.applied(); skill=object()
        foreign=replace(after,skill=skill,matches=(skill,))
        self.assertIsNone(self.ledger.propose_cleanup(foreign))
        self.assertIs(self.ledger.record.observation.skill,self.obs.skill)
        self.assertEqual(self.ledger.record.phase,'INERT_RETRY')

    def test_session_or_activation_change_keeps_inert_original(self):
        after=self.applied()
        for kwargs in ({'session':object()},{'activated_time':13},{'generation':2},{'verified':False}):
            self.assertIsNone(self.ledger.propose_cleanup(replace(after,**kwargs)))
        self.assertIsNotNone(self.ledger.record)

    def test_independent_duration_change_is_terminal_conflict_even_if_later_reset(self):
        after=self.applied()
        self.assertIsNone(self.ledger.propose_cleanup(replace(after,duration=76)))
        self.assertEqual(self.ledger.record.phase,'CONFLICT')
        self.assertIsNone(self.ledger.propose_cleanup(after))
        self.assertEqual(self.ledger.counts['conflict'],1)

    def test_even_small_independent_change_is_preserved(self):
        after=self.applied()
        self.assertIsNone(self.ledger.propose_cleanup(replace(after,duration=75.001)))
        self.assertEqual(self.ledger.last,'CONFLICT')

    def test_changed_base_or_known_modifiers_preserved(self):
        for kwargs in ({'base':60.001},{'modifiers':1}):
            self.setUp();after=self.applied()
            self.assertIsNone(self.ledger.propose_cleanup(replace(after,**kwargs)))
            self.assertEqual(self.ledger.last,'CONFLICT')

    def test_unknown_cleanup_values_keep_inert_retry(self):
        after=self.applied()
        for kwargs in ({'duration':None},{'duration':True},{'base':math.nan},{'modifiers':None}):
            self.assertIsNone(self.ledger.propose_cleanup(replace(after,**kwargs)))
            self.assertEqual(self.ledger.record.phase,'INERT_RETRY')

    def test_cleanup_does_not_require_rank_one(self):
        after=self.applied();action=self.ledger.propose_cleanup(replace(after,rank=0))
        self.assertEqual(action.value,60)
        self.assertTrue(self.ledger.acknowledge(action,replace(self.obs,rank=0),True))

    def test_failed_cleanup_retry_and_history_survive_success(self):
        after=self.applied();action=self.ledger.propose_cleanup(after)
        self.assertFalse(self.ledger.acknowledge(action,after,False))
        self.assertEqual(self.ledger.record.phase,'INERT_RETRY')
        retry=self.ledger.propose_cleanup(after)
        self.assertNotEqual(retry.operation,action.operation)
        self.assertTrue(self.ledger.acknowledge(retry,self.obs,True))
        self.assertEqual(self.ledger.counts['cleanup_failed'],1)
        self.assertFalse(self.ledger.enabled)

    def test_restore_readback_mismatch_keeps_pending_original(self):
        after=self.applied();action=self.ledger.propose_cleanup(after)
        self.assertFalse(self.ledger.acknowledge(action,replace(after,duration=None),True))
        self.assertIs(self.ledger.record.observation.skill,self.obs.skill)
        self.assertEqual(self.ledger.counts['cleanup_failed'],1)

    def test_pending_restore_reentrancy_emits_no_second_write(self):
        after=self.applied();action=self.ledger.propose_cleanup(after)
        self.assertIsNone(self.ledger.propose_cleanup(after))
        self.assertIs(self.ledger.pending,action)

    def test_stop_during_pending_write_invalidates_ack_and_requires_fresh_cleanup(self):
        action=self.ledger.propose_apply(self.obs)
        self.assertEqual(self.ledger.stop(),('PROPOSE_REMOVE_OBSERVERS',))
        self.assertFalse(self.ledger.acknowledge(action,replace(self.obs,duration=75),True))
        self.assertIsNone(self.ledger.propose_apply(self.obs))
        self.assertIsNotNone(self.ledger.propose_cleanup(replace(self.obs,duration=75)))

    def test_failed_hook_removal_stays_inert_after_successful_retry(self):
        self.ledger.stop();self.assertFalse(self.ledger.acknowledge_hook_removal(False))
        self.assertIsNone(self.ledger.propose_apply(self.obs))
        self.assertTrue(self.ledger.acknowledge_hook_removal(True))
        self.assertFalse(self.ledger.enabled)
        self.assertEqual(self.ledger.counts['hook_failed'],1)

    def test_ended_original_requires_exact_true_not_unknown_or_integer(self):
        self.applied()
        self.ledger.propose_cleanup(original_ended=1)
        self.assertIsNotNone(self.ledger.record)
        self.ledger.propose_cleanup(original_ended=True)
        self.assertIsNone(self.ledger.record)
        self.assertEqual(self.ledger.counts['retired'],1)

    def test_missing_constructor_tokens_refuse(self):
        with self.assertRaises(ValueError):model.ContractModel(None,*self.tokens[1:4])
