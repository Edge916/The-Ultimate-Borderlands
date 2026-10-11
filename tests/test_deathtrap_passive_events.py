"""Inert manager-entry acceptance; no installed SDK/game behavior is tested."""
import ast
import gc
import sys
import types
import unittest
import weakref
from unittest.mock import patch
import test_deathtrap_readiness as meta
import test_runtime_mock as runtime


class CanonicalClass(meta.UClass):
    def _path_name(self):
        if self.on_path:
            self.on_path()
        return self.package + '.' + self.Name


class PayloadPoison:
    touched = []
    def __getattribute__(self, key):
        PayloadPoison.touched.append('attribute')
        raise AssertionError('callback payload attribute')
    def __eq__(self, other):
        PayloadPoison.touched.append('equality')
        raise AssertionError('callback payload equality')
    def __bool__(self):
        PayloadPoison.touched.append('bool')
        raise AssertionError('callback payload bool')
    def __str__(self):
        PayloadPoison.touched.append('str')
        raise AssertionError('callback payload str')
    def __repr__(self):
        PayloadPoison.touched.append('repr')
        raise AssertionError('callback payload repr')
    def __iter__(self):
        PayloadPoison.touched.append('iteration')
        raise AssertionError('callback payload iteration')
    def __hash__(self):
        PayloadPoison.touched.append('hash')
        raise AssertionError('callback payload hash')
    def __call__(self, *args, **kwargs):
        PayloadPoison.touched.append('call')
        raise AssertionError('callback payload native call')


class PrivateError(Exception):
    def __str__(self):
        raise AssertionError('exception message was formatted')


class PassiveEventTests(unittest.TestCase):
    def setUp(self):
        PayloadPoison.touched=[]
        fixture=meta.DeathtrapReadinessTests()
        fixture.setUp()
        self.h,self.tree,self.node=fixture.h,fixture.tree,fixture.node
        self.controller,self.manager,self.definition=fixture.controller,fixture.manager,fixture.definition
        for cls in (self.controller,self.manager,self.definition):
            cls.__class__=CanonicalClass
            cls.package='WillowGame'
        self.manager.Name='SkillEffectManager'
        self.root=CanonicalClass('Object');self.root.package='Core'
        self.engine_controller=CanonicalClass('Controller',self.root);self.engine_controller.package='Engine'
        self.controller.SuperField=self.engine_controller
        self.manager.SuperField=self.root
        self.definition.SuperField=self.root
        self.primary,self.ret=fixture.primary,fixture.ret
        self.primary.FunctionFlags=132097
        self.primary.ParamsSize=4
        self.ret.PropertyFlags,self.ret.ElementSize=1408,4
        self.deact=meta.UFunction(self.manager,'DeactivateSkill')
        self.deact.FunctionFlags,self.deact.NumParams,self.deact.ParamsSize=149506,3,12
        self.deact.props=[meta.ZObjectProperty('SkillInstigator',self.deact,PropertyFlags=128,PropertyClass=self.engine_controller),
            meta.ZObjectProperty('Definition',self.deact,PropertyFlags=128,Offset_Internal=4,PropertyClass=self.definition),
            meta.ZBoolProperty('bIgnoreSkillInstigator',self.deact,PropertyFlags=144,Offset_Internal=8)]
        self.deact.link()
        self.manager.functions['DeactivateSkill']=self.deact
        self.h.sdk.hooks.add_hook=self.h.add_hook
        self.h.sdk.hooks.remove_hook=self.h.remove_hook
        self.clock=1000.0
        self.native_calls=fixture.forbidden_calls
        self.removed=[]
        original_remove=self.h.remove_hook
        def remove(*args):
            self.removed.append(args)
            return original_remove(*args)
        self.h.sdk.hooks.remove_hook=remove
        self.h.logs.clear()

    def tearDown(self):
        self.assertEqual(PayloadPoison.touched,[])
        self.assertEqual(self.native_calls,[])

    def call(self,name,*args):
        with patch('time.monotonic',lambda:self.clock):
            return self.h.call(name,*args)

    def key(self):
        return (self.h.scope['_DT_EVENT_PATH'],'pre',self.h.scope['_DT_EVENT_IDENT'])

    def start(self):
        self.assertTrue(self.call('start_deathtrap_events'))
        return self.h.hooks[self.key()]

    def fire(self,callback=None,payloads=None):
        callback=self.h.hooks[self.key()] if callback is None else callback
        values=tuple(PayloadPoison() for _ in range(4)) if payloads is None else payloads
        with patch.dict(sys.modules,{'unrealsdk':self.h.sdk,'mods_base':self.h.base}),patch('time.monotonic',lambda:self.clock):
            value=callback(*values)
        self.assertIsNone(value)

    def has(self,token):
        return any('[UVH-DT-EVENT] '+token in line for line in self.h.logs)

    def test_import_is_inert_with_twenty_one_options(self):
        self.assertIsNone(self.h.scope['_dt_event_context'])
        self.assertEqual(self.h.scope['_dt_event_handles'],[])
        self.assertEqual(len(self.h.mod_options['options']),21)
        self.assertFalse(any(self.key()==k for k in self.h.hooks))

    def test_nominal_one_void_pre_target_and_no_callback_payload_reads(self):
        self.start();self.fire()
        self.assertEqual(list(self.h.hooks),[self.key()])
        self.assertEqual(self.h.scope['_dt_event_stats']['captured'],1)
        self.assertTrue(self.has('EVENT ordinal=1 target=DeactivateSkill phase=PRE attribution=NONE'))
        self.assertTrue(self.call('stop_deathtrap_events'))
        self.assertTrue(self.has('OUTCOME value=OBSERVED_UNATTRIBUTED'))

    def test_silence_reports_not_observed_not_failure_or_zero_skills(self):
        self.start();self.assertTrue(self.call('stop_deathtrap_events'))
        self.assertTrue(self.has('OUTCOME value=NOT_OBSERVED'))
        self.assertEqual(self.h.hooks,{})

    def test_all_four_payloads_are_not_retained(self):
        self.start()
        values=tuple(PayloadPoison() for _ in range(4))
        refs=[weakref.ref(v) for v in values]
        self.fire(payloads=values)
        del values
        gc.collect()
        self.assertTrue(all(ref() is None for ref in refs))

    def test_stale_callback_has_no_guard_reads_or_output(self):
        callback=self.start();self.call('stop_deathtrap_events')
        self.h.scope['_dt_event_guard']=lambda ctx:(_ for _ in ()).throw(AssertionError('stale guard'))
        before=list(self.h.logs);self.fire(callback)
        self.assertEqual(self.h.logs,before)

    def test_prior_epoch_stays_inert_after_new_start(self):
        old=self.start();self.call('stop_deathtrap_events');self.start()
        self.fire(old)
        self.assertEqual(self.h.scope['_dt_event_stats']['attempts'],0)

    def test_controller_pawn_roster_and_rank_start_refusals(self):
        changes=[lambda:setattr(self.h.pc,'Pawn',None),lambda:setattr(self.h.pc.PlayerClass,'Name','Other'),
            lambda:setattr(self.h.pc.WorldInfo.GRI,'PRIArray',runtime.WrappedArray([])),
            lambda:setattr(next(s for s in self.tree.Skills if s.Definition is self.node),'Grade',1),
            lambda:setattr(self.h.pc.PlayerReplicationInfo,'GeneralSkillPoints',None),
            lambda:setattr(self.h.pc.PlayerReplicationInfo,'GeneralSkillPoints',True)]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                self.setUp();change()
                self.assertFalse(self.call('start_deathtrap_events'))
                self.assertTrue(self.has('NOT_STARTED reason=STATE'))
                self.assertEqual(self.h.hooks,{})

    def test_rank_one_candidate_refuses(self):
        target=next(s for s in self.tree.Skills if s.Definition is self.node)
        target.Grade=1
        self.assertFalse(self.call('start_deathtrap_events'))

    def test_original_skill_rank_is_allowed_with_candidate_still_zero(self):
        original=next(s for s in self.tree.Skills if s.Definition is self.h.first)
        original.Grade=1
        self.start();self.fire()
        self.assertEqual(self.h.scope['_dt_event_context']['baseline'][1],(0,1,0))

    def test_extra_local_player_refuses(self):
        self.h.engine.GamePlayers=runtime.WrappedArray([types.SimpleNamespace(Actor=self.h.pc),types.SimpleNamespace(Actor=self.h.pc)])
        self.assertFalse(self.call('start_deathtrap_events'))

    def test_inert_candidate_array_change_refuses(self):
        self.node.SkillEffectDefinitions=[types.SimpleNamespace()]
        self.assertFalse(self.call('start_deathtrap_events'))

    def test_points_and_ranks_above_output_bound_refuse_without_formatting(self):
        self.h.pc.PlayerReplicationInfo.GeneralSkillPoints=2147483648
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertTrue(self.has('NOT_STARTED reason=STATE'))

    def test_session_change_aborts_and_cleans_without_payload_read(self):
        callback=self.start();self.h.pc.Pawn=meta.UObject('ReplacementPawn')
        self.fire(callback)
        self.assertIsNone(self.h.scope['_dt_event_context'])
        self.assertEqual(self.h.hooks,{})
        self.assertTrue(self.has('ABORT reason=STATE'))

    def test_points_drift_preserved_without_refund(self):
        self.start();self.h.pc.PlayerReplicationInfo.GeneralSkillPoints=3
        self.fire();self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints,3)
        self.assertTrue(self.has('OUTCOME value=REFUSED'))

    def test_existing_observer_context_prevents_start(self):
        self.h.scope['_upgrade_context']={}
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertEqual(self.h.hooks,{})

    def test_foreign_canonical_class_path_refuses(self):
        self.manager.package='Foreign'
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertTrue(self.has('NOT_STARTED reason=METADATA'))

    def test_wrong_declared_instigator_or_definition_class_refuses(self):
        for index in (0,1):
            with self.subTest(index=index):
                self.setUp();foreign=CanonicalClass('Controller' if index==0 else 'SkillDefinition');foreign.package='Foreign'
                self.deact.props[index].PropertyClass=foreign
                self.assertFalse(self.call('start_deathtrap_events'))

    def test_function_header_and_property_schema_mutations_refuse(self):
        changes=[lambda:setattr(self.deact,'FunctionFlags',1024),lambda:setattr(self.deact,'NumParams',4),
            lambda:setattr(self.deact,'ParamsSize',16),lambda:setattr(self.deact,'ReturnValueOffset',0),
            lambda:setattr(self.deact.props[2],'PropertyFlags',True),lambda:setattr(self.deact.props[2],'Offset_Internal',4),
            lambda:setattr(self.deact.props[1],'ElementSize',8),lambda:setattr(self.deact,'PropertyLink',None)]
        for index,change in enumerate(changes):
            with self.subTest(index=index):
                self.setUp();change();self.assertFalse(self.call('start_deathtrap_events'))
                self.assertTrue(self.has('NOT_STARTED reason=METADATA'))

    def test_unexpected_return_descriptor_refuses_even_with_void_offset(self):
        self.deact.ret=self.deact.props[2]
        self.assertFalse(self.call('start_deathtrap_events'))

    def test_unavailable_inherited_and_extra_property_metadata_refuse(self):
        for kind in ('missing','inherited','extra'):
            with self.subTest(kind=kind):
                self.setUp()
                if kind=='missing':del self.manager.functions['DeactivateSkill']
                elif kind=='inherited':self.deact.SuperField=self.deact
                else:self.deact.props.append(meta.ZIntProperty('Local',self.deact,PropertyFlags=0,Offset_Internal=16));self.deact.link()
                self.assertFalse(self.call('start_deathtrap_events'))

    def test_metadata_drift_after_start_aborts_before_event(self):
        self.start();self.deact.props[2].Offset_Internal=4;self.fire()
        self.assertTrue(self.has('ABORT reason=METADATA'))
        self.assertEqual(self.h.scope['_dt_event_stats']['captured'],0)

    def test_controller_class_reference_drift_with_same_path_aborts(self):
        self.start()
        foreign=CanonicalClass('WillowPlayerController',self.engine_controller);foreign.package='WillowGame'
        self.h.pc.Class=foreign
        self.fire();self.assertTrue(self.has('ABORT reason=METADATA'))

    def test_activation_target_and_boolean_mask_are_never_traversed(self):
        self.manager.functions['ActivateSkill']=PayloadPoison()
        self.deact.props[2].FieldMask=PayloadPoison()
        self.start();self.fire()
        self.assertEqual(list(self.h.hooks),[self.key()])

    def test_selected_definition_class_drift_aborts(self):
        self.start();foreign=CanonicalClass('SkillDefinition');foreign.package='WillowGame';self.node.Class=foreign
        self.fire();self.assertTrue(self.has('ABORT reason=METADATA'))

    def test_descriptor_checks_cannot_grow_past_thirty_two(self):
        checks=self.h.scope['_DTEventChecks']()
        for n in range(32):checks.append(n)
        with self.assertRaises(self.h.scope['_DTEventRefusal']):checks.append(33)
        self.assertEqual(len(checks),32)

    def test_identifier_collision_never_removes_foreign_hook(self):
        foreign=lambda *args:None;self.h.hooks[self.key()]=foreign
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertIs(self.h.hooks[self.key()],foreign)
        self.assertEqual(self.removed,[])

    def test_registration_false_never_claims_or_removes_foreign_identifier(self):
        foreign=lambda *args:None
        def add(*args):self.h.hooks[self.key()]=foreign;return False
        self.h.sdk.hooks.add_hook=add
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertIs(self.h.hooks[self.key()],foreign)
        self.assertEqual(self.removed,[])

    def test_registration_exception_before_install_clears_uncertain_by_absence(self):
        self.h.sdk.hooks.add_hook=lambda *args:(_ for _ in ()).throw(PrivateError())
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertEqual(self.h.scope['_dt_event_uncertain'],[])
        self.assertEqual(self.removed,[])

    def test_registration_exception_after_install_retains_inert_uncertain_not_owned(self):
        def add(path,phase,ident,callback):self.h.hooks[(path,phase,ident)]=callback;raise PrivateError()
        self.h.sdk.hooks.add_hook=add
        self.assertFalse(self.call('start_deathtrap_events'))
        self.fire();self.assertEqual(self.h.scope['_dt_event_stats']['captured'],0)
        self.assertEqual(self.removed,[])
        self.assertFalse(self.call('start_deathtrap_events'))
        self.h.hooks.clear();self.assertTrue(self.call('stop_deathtrap_events'))
        self.assertTrue(self.has('OUTCOME value=REFUSED'))

    def test_non_boolean_registration_result_is_uncertain_and_inert(self):
        def add(path,phase,ident,callback):self.h.hooks[(path,phase,ident)]=callback;return 1
        self.h.sdk.hooks.add_hook=add
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertEqual(self.h.scope['_dt_event_handles'],[])
        self.assertTrue(self.h.scope['_dt_event_uncertain'])
        self.fire();self.assertEqual(self.removed,[])

    def test_callback_during_registration_is_inert(self):
        def add(path,phase,ident,callback):self.fire(callback);return self.h.add_hook(path,phase,ident,callback)
        self.h.sdk.hooks.add_hook=add
        self.start();self.assertEqual(self.h.scope['_dt_event_stats']['attempts'],0)

    def test_original_dispatch_is_locked_during_registration_before_ownership_result(self):
        seen=[]
        self.h.scope['probe']=self.h.scope['_dt_event_option_gate'](lambda arg:seen.append(arg))
        def add(*args):
            self.assertFalse(self.call('probe',object()))
            return self.h.add_hook(*args)
        self.h.sdk.hooks.add_hook=add
        self.start();self.assertEqual(seen,[])

    def test_stop_during_registration_invalidates_pending_start_and_removes_proven_handle(self):
        def add(*args):
            result=self.h.add_hook(*args)
            self.call('stop_deathtrap_events')
            return result
        self.h.sdk.hooks.add_hook=add
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertIsNone(self.h.scope['_dt_event_context'])
        self.assertEqual(self.h.hooks,{})
        self.assertFalse(self.h.scope['_dt_event_starting'])

    def test_unknown_post_registration_presence_retains_owned_inert_until_retry(self):
        seen=[]
        def presence(*args):
            seen.append(1)
            return False if len(seen)==1 else 1
        self.h.sdk.hooks.has_hook=presence
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertIsNone(self.h.scope['_dt_event_context'])
        self.assertTrue(self.h.scope['_dt_event_handles'])
        self.h.sdk.hooks.has_hook=lambda *args:args in self.h.hooks
        self.assertTrue(self.call('stop_deathtrap_events'))
        self.assertTrue(self.has('OUTCOME value=REFUSED'))

    def test_post_registration_state_drift_cleans_owned_handle(self):
        def add(*args):result=self.h.add_hook(*args);self.h.pc.Pawn=None;return result
        self.h.sdk.hooks.add_hook=add
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertEqual(self.h.hooks,{})
        self.assertEqual(len(self.removed),1)

    def test_event_limit_cleans_on_twenty_fourth_and_stale_call_is_inert(self):
        callback=self.start()
        for _ in range(24):self.fire(callback)
        self.assertEqual(self.h.scope['_dt_event_stats']['captured'],24)
        self.assertTrue(self.has('LIMIT reason=EVENTS'))
        self.assertEqual(self.h.hooks,{})
        self.fire(callback);self.assertEqual(self.h.scope['_dt_event_stats']['captured'],24)

    def test_attempt_limit_before_guard_cleans(self):
        self.start();self.h.scope['_dt_event_stats']['attempts']=63
        self.fire();self.assertTrue(self.has('LIMIT reason=ATTEMPTS'))
        self.assertEqual(self.h.scope['_dt_event_stats']['captured'],0)

    def test_reentrant_callback_has_no_second_guard_or_event(self):
        callback=self.start();original=self.h.scope['_dt_event_guard'];called=[]
        def guard(context):
            if not called:called.append(1);self.fire(callback)
            return original(context)
        self.h.scope['_dt_event_guard']=guard
        self.fire(callback)
        self.assertEqual(self.h.scope['_dt_event_stats']['attempts'],2)
        self.assertEqual(self.h.scope['_dt_event_stats']['captured'],1)
        self.assertEqual(self.h.scope['_dt_event_stats']['reentrant'],1)

    def test_busy_attempt_limit_invalidates_before_outer_commit_and_defers_removal(self):
        callback=self.start();original=self.h.scope['_dt_event_guard'];called=[]
        def guard(context):
            if not called:
                called.append(1)
                self.h.scope['_dt_event_stats']['attempts']=63
                self.fire(callback)
                self.assertEqual(self.removed,[])
                self.assertIsNone(self.h.scope['_dt_event_context'])
            return original(context)
        self.h.scope['_dt_event_guard']=guard
        self.fire(callback)
        self.assertEqual(self.h.scope['_dt_event_stats']['captured'],0)
        self.assertEqual(self.h.hooks,{})

    def test_timeout_and_stop_during_silence_are_explicit(self):
        callback=self.start();self.clock=1030.0;self.fire(callback)
        self.assertTrue(self.has('LIMIT reason=TIME'))
        self.assertEqual(self.h.hooks,{})
        self.setUp();self.start();self.clock=1030.0;self.call('stop_deathtrap_events')
        self.assertTrue(self.has('LIMIT reason=TIME'))

    def test_nonfinite_boolean_integer_and_negative_clock_refuse_start(self):
        for value in (float('nan'),float('inf'),True,1000,-1.0):
            with self.subTest(value_type=type(value).__name__):
                self.setUp();self.clock=value;self.assertFalse(self.call('start_deathtrap_events'))
                self.assertTrue(self.has('NOT_STARTED reason=CLOCK'))

    def test_backward_clock_aborts_without_callback_payload_read(self):
        self.start();self.clock=999.0;self.fire()
        self.assertTrue(self.has('ABORT reason=CLOCK'))
        self.assertEqual(self.h.hooks,{})

    def test_epoch_exhaustion_refuses_without_wrap_or_hooks(self):
        self.h.scope['_dt_event_epoch']=2147483647
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertEqual(self.h.scope['_dt_event_epoch'],2147483647)
        self.assertEqual(self.h.hooks,{})

    def test_cleanup_failure_retains_inert_handle_and_history_after_retry(self):
        callback=self.start();self.h.fail_remove=True
        self.assertFalse(self.call('stop_deathtrap_events'))
        self.fire(callback)
        self.assertFalse(self.call('start_deathtrap_events'))
        self.assertEqual(self.h.scope['_dt_event_stats']['failures'],1)
        self.h.fail_remove=False
        self.assertTrue(self.call('stop_deathtrap_events'))
        self.assertEqual(self.h.scope['_dt_event_stats']['failures'],1)
        self.assertTrue(self.has('OUTCOME value=REFUSED'))
        self.assertIsNone(self.h.scope['_dt_event_context'])
        self.assertIsNone(self.h.scope['_dt_event_closing_context'])

    def test_false_removal_with_hook_still_present_is_not_clean(self):
        self.start();self.h.sdk.hooks.remove_hook=lambda *args:False
        self.assertFalse(self.call('stop_deathtrap_events'))
        self.assertTrue(self.h.scope['_dt_event_handles'])

    def test_unknown_presence_or_non_boolean_removal_retains_handle(self):
        for kind in ('presence','removal'):
            with self.subTest(kind=kind):
                self.setUp();self.start()
                if kind=='presence':self.h.sdk.hooks.has_hook=lambda *args:1
                else:self.h.sdk.hooks.remove_hook=lambda *args:1
                self.assertFalse(self.call('stop_deathtrap_events'))
                self.assertTrue(self.h.scope['_dt_event_handles'])

    def test_final_unknown_state_is_refused_without_blocking_owned_removal(self):
        self.start();self.h.pc.Pawn=None
        self.assertTrue(self.call('stop_deathtrap_events'))
        self.assertEqual(self.h.hooks,{})
        self.assertTrue(self.has('FINAL UNVERIFIED reason=STATE'))
        self.assertTrue(self.has('OUTCOME value=REFUSED'))

    def test_cancel_clears_accepting_state_before_array_restore_even_with_failed_removal(self):
        callback=self.start();self.h.fail_remove=True
        self.call('cancel_init_node')
        self.assertIsNone(self.h.scope['_dt_event_context'])
        self.assertEqual(self.h.names(),['MorePep','Myelin'])
        self.fire(callback)
        self.assertEqual(self.h.scope['_dt_event_stats']['captured'],0)

    def test_disable_cleans_and_restores_with_original_shutdown(self):
        self.start();self.call('shutdown')
        self.assertEqual(self.h.hooks,{})
        self.assertEqual(self.h.names(),['MorePep','Myelin'])

    def test_option_gate_forwards_exact_idle_argument_and_result_then_locks(self):
        argument=object();result=object();seen=[]
        def handler(value):seen.append(value);return result
        wrapped=self.h.scope['_dt_event_option_gate'](handler)
        self.h.scope['probe']=wrapped
        self.assertIs(self.call('probe',argument),result)
        self.assertIs(seen[0],argument)
        self.start();self.assertFalse(self.call('probe',argument));self.assertEqual(len(seen),1)
        self.h.fail_remove=True;self.call('stop_deathtrap_events')
        self.assertFalse(self.call('probe',argument));self.assertEqual(len(seen),1)

    def test_original_controls_except_cancel_are_wrapped_and_new_stop_available(self):
        options=self.h.mod_options['options']
        self.assertIs(options[2]['on_press'],self.h.scope['cancel_init_node'])
        for index,option in enumerate(options[:19]):
            if index!=2:self.assertIn(option['on_press'].__wrapped__,self.h.scope.values())
        self.assertIs(options[19]['on_press'],self.h.scope['start_deathtrap_events'])
        self.assertIs(options[20]['on_press'],self.h.scope['stop_deathtrap_events'])
        self.start();before=self.h.scope['_init_armed']
        self.h.scope['locked_arm']=options[0]['on_press']
        self.assertFalse(self.call('locked_arm'));self.assertEqual(self.h.scope['_init_armed'],before)

    def test_closed_log_bounds_and_no_payload_or_exception_text(self):
        self.start();self.fire();self.call('stop_deathtrap_events')
        lines=[x for x in self.h.logs if x.startswith('[UVH-DT-EVENT]')]
        self.assertTrue(all(len(x.encode('utf-8'))<=256 for x in lines))
        self.assertTrue(all('PayloadPoison' not in x and 'PrivateError' not in x for x in lines))

    def test_logger_exception_aborts_inertly_without_formatting_exception(self):
        callback=self.start()
        self.h.sdk.logging.info=lambda *args:(_ for _ in ()).throw(PrivateError())
        self.fire(callback)
        self.assertIsNone(self.h.scope['_dt_event_context'])
        self.assertEqual(self.h.hooks,{})

    def test_callback_source_never_loads_the_four_payload_parameters(self):
        tree=ast.parse(runtime.SOURCE.read_bytes())
        outer=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_dt_event_callback')
        observe=next(n for n in outer.body if isinstance(n,ast.FunctionDef))
        loads={n.id for n in ast.walk(observe) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}
        self.assertEqual(loads & {'obj','args','ret','func'},set())


if __name__=='__main__':
    unittest.main()
