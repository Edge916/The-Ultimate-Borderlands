"""Focused natural-call simulations; no engine/purchase/tooltip proof."""
import types
import unittest
from unittest.mock import patch

import test_upgrade_observers as upgrade_tests
from test_runtime_mock import MetadataFunction, Obj, WrappedArray


class FocusedStateTests(unittest.TestCase):
    def setUp(self):
        fixture = upgrade_tests.UpgradeObserverTests()
        fixture.setUp()
        self.h, self.tree, self.node, self.ui = fixture.h, fixture.tree, fixture.node, fixture.ui
        self.ui.NumSkillPoints = 5
        self.functions = {}
        struct = Obj('SkillTreeSkillStateData', 'ScriptStruct')
        struct._properties = lambda: iter([self.prop('Example', 'IntProperty', 0, 0)])
        specs = (
            ('PlayerSkillTree', 'GetSkillState', (3, 28, 24),
             [self.prop('SkillDef', 'ObjectProperty', 128, 0, PropertyClass=Obj('SkillDefinition')),
              self.prop('OutSkillState', 'StructProperty', 384, 4, Struct=struct),
              self.prop('ReturnValue', 'BoolProperty', 1408, 24)]),
            ('SkillTreeGFxObject', 'GetSkillDescriptionForGrade', (6, 32, 20),
             [self.prop('SkillDef', 'ObjectProperty', 128, 0, PropertyClass=Obj('SkillDefinition')),
              self.prop('Grade', 'IntProperty', 128, 4), self.prop('GradeModifier', 'IntProperty', 128, 8),
              self.prop('PlayerOwner', 'ObjectProperty', 128, 12, PropertyClass=Obj('WillowPlayerController')),
              self.prop('bIncludeHTML', 'BoolProperty', 128, 16),
              self.prop('ReturnValue', 'StrProperty', 4195712, 20)]),
            ('SkillTreeGFxObject', 'UpdateInfoBox', (0, 0, 65535),
             [self.prop('SkillDesc', 'StrProperty', 4194304, 0),
              self.prop('NextGradeText', 'StrProperty', 4194304, 24)]))
        for owner, method, signature, fields in specs:
            func = MetadataFunction(owner, method)
            func.NumParams, func.ParamsSize, func.ReturnValueOffset = signature
            func._properties = lambda fields=fields: iter(fields)
            self.functions[method] = func
        self.h.functions = list(self.functions.values())

    def prop(self, label, kind, flags, offset, **fields):
        return Obj(label, kind, PropertyFlags=flags, Offset_Internal=offset, ArrayDim=1, **fields)

    def start(self):
        self.assertTrue(self.h.call('start_skillstate_trace'))
        self.assertEqual(len(self.h.hooks), 3)
        self.assertEqual({key[1] for key in self.h.hooks}, {'post'})

    def args(self, method='GetSkillState', definition=None, **fields):
        class Inputs:
            @property
            def OutSkillState(self):
                raise AssertionError('copied out input must never be read as finished state')
            @property
            def ReturnValue(self):
                raise AssertionError('must use actual POST ret')
        args = Inputs()
        args.__dict__.update(_type=self.functions[method], SkillDef=definition or self.node,
                             PlayerOwner=self.h.pc, Grade=1, GradeModifier=0, bIncludeHTML=True)
        args.__dict__.update(fields)
        return args

    def fire(self, method='GetSkillState', obj=None, args=None, ret=True):
        key = next(key for key in self.h.hooks if key[0].endswith(':' + method))
        callback = self.h.hooks[key]
        def forbidden(*a, **kw):
            self.fail('callback invoked native function')
        with patch.dict('sys.modules', {'unrealsdk': self.h.sdk, 'mods_base': self.h.base}):
            return callback(obj if obj is not None else (self.tree if method == 'GetSkillState' else self.ui),
                            args if args is not None else self.args(method), ret, forbidden)

    def test_post_inputs_and_actual_returns_are_read_only_and_out_locals_are_never_read(self):
        self.start()
        before = [dict(obj.__dict__) for obj in (self.h.pc, self.node, self.tree, self.ui, *self.tree.Skills)]
        arrays = list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied)
        self.assertIsNone(self.fire(ret=False))
        self.assertIsNone(self.fire('GetSkillDescriptionForGrade', ret='<font color="orange">Rank 1</font>'))
        class Unreadable:
            def __getattr__(self, field):
                raise AssertionError('zero-param UI args/ret must not be read')
        self.assertIsNone(self.fire('UpdateInfoBox', args=Unreadable(), ret=Unreadable()))
        results = self.h.scope['_skillstate_results']
        self.assertEqual(results[0][2], ('QUERY_RETURN', False))
        self.assertEqual(results[1][2][:6], ('DESCRIPTION', 1, 0, True, 34, '<font color="orange">Rank 1</font>'))
        self.assertEqual(results[2][2][0], 'UI_VIEW')
        self.assertEqual(before, [dict(obj.__dict__) for obj in (self.h.pc, self.node, self.tree, self.ui, *self.tree.Skills)])
        self.assertEqual(arrays, (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied)))
        self.assertEqual(self.h.loads, [])
        self.assertTrue(self.h.call('stop_skillstate_trace'))
        self.assertEqual(self.h.hooks, {})

    def test_each_target_uses_input_identity_with_current_and_rollover_reported_separately(self):
        self.start()
        for definition in (self.node, self.h.first, self.h.last):
            self.fire(args=self.args(definition=definition))
            self.ui.CurrentSkill = self.node
            self.ui.CurrentSkill_Rollover = definition
            self.fire('GetSkillDescriptionForGrade', args=self.args('GetSkillDescriptionForGrade', definition), ret='preview')
            self.fire('UpdateInfoBox')
        self.assertEqual({row[1] for row in self.h.scope['_skillstate_results']}, {'UVH_DeathtrapOverclock', 'MorePep', 'Myelin'})
        last = self.h.scope['_skillstate_results'][-1][2]
        self.assertEqual(last[1:3], ('UVH_DeathtrapOverclock', 'Myelin'))

    def test_foreign_tree_ui_and_player_owner_are_rejected_before_value_reads(self):
        self.start()
        class Unreadable:
            def __getattr__(self, field):
                raise AssertionError('foreign args must not be read')
        self.fire(obj=Obj('OtherTree'), args=Unreadable(), ret=Unreadable())
        self.fire('GetSkillDescriptionForGrade', obj=Obj('OtherUI', 'SkillTreeGFxObject', WPCOwner=Obj('Other')), args=Unreadable(), ret=Unreadable())
        self.fire('UpdateInfoBox', obj=Obj('WrongClass', WPCOwner=self.h.pc), args=Unreadable())
        self.fire('GetSkillDescriptionForGrade', args=self.args('GetSkillDescriptionForGrade', PlayerOwner=Obj('Other')), ret=Unreadable())
        self.assertEqual(self.h.scope['_skillstate_results'], [])
        self.assertEqual(self.h.scope['_skillstate_callbacks'], 4)
        self.assertEqual(self.h.scope['_skillstate_skipped'], 4)

    def test_unrelated_skill_returns_and_ui_states_do_not_consume_capture_budget(self):
        self.start()
        other = Obj('OtherSkill', 'SkillDefinition')
        for _ in range(250):
            self.fire(args=self.args(definition=other), ret=object())
        self.ui.CurrentSkill = self.ui.CurrentSkill_Rollover = None
        self.fire('UpdateInfoBox')
        self.assertEqual(self.h.scope['_skillstate_results'], [])
        self.assertEqual(self.h.scope['_skillstate_callbacks'], 251)
        self.assertIsNotNone(self.h.scope['_skillstate_context'])

    def test_unknown_return_input_types_and_function_wrappers_abort_without_guessing(self):
        cases = [('GetSkillState', {}, 1), ('GetSkillState', {}, (True, object())),
                 ('GetSkillState', {'_type': object()}, True),
                 ('GetSkillDescriptionForGrade', {'Grade': True}, 'text'),
                 ('GetSkillDescriptionForGrade', {'Grade': -1}, 'text'),
                 ('GetSkillDescriptionForGrade', {'GradeModifier': 129}, 'text'),
                 ('GetSkillDescriptionForGrade', {'bIncludeHTML': 1}, 'text'),
                 ('GetSkillDescriptionForGrade', {}, object())]
        for method, fields, ret in cases:
            with self.subTest(method=method, fields=fields, ret=ret):
                self.setUp()
                self.start()
                self.fire(method, args=self.args(method, **fields), ret=ret)
                self.assertEqual(self.h.hooks, {})
                self.assertEqual(self.h.scope['_skillstate_results'], [])
                self.assertIsNone(self.h.scope['_skillstate_context'])

    def test_loaded_function_schema_struct_and_duplicate_errors_refuse_start(self):
        mutations = [lambda: self.h.functions.pop(), lambda: self.h.functions.append(self.h.functions[0]),
                     lambda: setattr(self.functions['GetSkillState'], 'NumParams', 2),
                     lambda: setattr(self.functions['GetSkillState'], 'Outer', Obj('Other')),
                     lambda: setattr(next(self.functions['GetSkillState']._properties()), 'PropertyClass', Obj('Pawn')),
                     lambda: setattr(list(self.functions['GetSkillState']._properties())[1].Struct, 'Name', 'WrongStruct'),
                     lambda: setattr(list(self.functions['GetSkillState']._properties())[1], 'PropertyFlags', 128),
                     lambda: setattr(list(self.functions['GetSkillDescriptionForGrade']._properties())[-1], 'PropertyFlags', 1408),
                     lambda: setattr(self.functions['UpdateInfoBox'], '_properties', lambda: iter([self.prop('InjectedParam', 'IntProperty', 128, 0)])),
                     lambda: setattr(self.functions['GetSkillState'], '_properties', lambda: iter([self.prop('SkillDef', 'ObjectProperty', 128, 0)] * 2))]
        for change in mutations:
            with self.subTest(change=change):
                self.setUp()
                change()
                self.assertFalse(self.h.call('start_skillstate_trace'))
                self.assertEqual(self.h.hooks, {})

    def test_metadata_scan_field_caps_reflection_and_dot_paths(self):
        self.h.functions = (MetadataFunction('Other', 'Other') for _ in range(30001))
        self.assertFalse(self.h.call('start_skillstate_trace'))
        self.setUp()
        self.functions['UpdateInfoBox']._properties = lambda: (self.prop('local' + str(i), 'IntProperty', 0, i * 4) for i in range(17))
        self.assertFalse(self.h.call('start_skillstate_trace'))
        self.setUp()
        def broken():
            raise RuntimeError('reflection unavailable')
        list(self.functions['GetSkillState']._properties())[1].Struct._properties = broken
        self.assertFalse(self.h.call('start_skillstate_trace'))
        self.setUp()
        list(self.functions['GetSkillState']._properties())[1].Struct._properties = lambda: (
            self.prop('field' + str(i), 'IntProperty', 0, i * 4) for i in range(20))
        self.functions['GetSkillState'].path = 'WillowGame.PlayerSkillTree.GetSkillState'
        self.start()
        self.assertEqual(sum('[UVH-STATE] STRUCT field' in line for line in self.h.logs), 12)
        self.assertTrue(any('STRUCT metadata capped at 12' in line for line in self.h.logs))

    def test_description_text_is_bounded_and_never_claimed_as_finished_out_state(self):
        self.start()
        self.fire('GetSkillDescriptionForGrade', ret='x' * 10000)
        detail = self.h.scope['_skillstate_results'][0][2]
        self.assertEqual(detail[4:6], (10000, 'x' * 512))
        self.assertLess(len(next(line for line in self.h.logs if '[UVH-STATE] RESULT ' in line)), 800)
        self.fire('GetSkillDescriptionForGrade', ret='')
        self.assertEqual(self.h.scope['_skillstate_results'][1][2][4:6], (0, ''))

    def test_capture_quotas_reserve_other_functions_and_other_skills(self):
        self.start()
        for definition in (self.h.first, self.node, self.h.last):
            self.ui.CurrentSkill = self.ui.CurrentSkill_Rollover = definition
            for grade in range(20):
                self.fire('GetSkillDescriptionForGrade', args=self.args('GetSkillDescriptionForGrade', definition, Grade=grade), ret=str(grade))
            for ret in (True, True, False, False, True):
                self.fire(args=self.args(definition=definition), ret=ret)
            for points in (5, 5, 6, 6, 7):
                self.ui.NumSkillPoints = points  # Simulated UI values; PRI stays unchanged.
                self.fire('UpdateInfoBox')
        self.assertEqual(len(self.h.scope['_skillstate_results']), 36)
        self.assertEqual(set(self.h.scope['_skillstate_counts'].values()), {4})
        self.assertEqual(len(self.h.scope['_skillstate_counts']), 9)
        self.assertIsNotNone(self.h.scope['_skillstate_context'])
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 5)

    def test_real_navigation_sequence_does_not_starve_node_or_myelin(self):
        self.start()
        extras = [Obj('Skill_DeathTrap', 'SkillDefinition'), Obj('CookingUpTrouble', 'SkillDefinition')]
        for definition in extras:
            self.tree.Skills.append(types.SimpleNamespace(Definition=definition, Owner=self.tree,
                Index=len(self.tree.Skills), ParentTierIndex=0, Grade=0))
        # Replay UpdateInfoBox POST pairs from v0.2.6, where broad capture hit
        # its limit as Overclock was reached. Inputs/nav aren't hooked here.
        states = [(extras[0], extras[0]), (extras[0], extras[0]), (extras[0], self.h.first),
                  (extras[1], extras[1]), (self.h.first, self.h.first), (self.node, self.node)]
        for current, rollover in states:
            self.ui.CurrentSkill, self.ui.CurrentSkill_Rollover = current, rollover
            self.fire('UpdateInfoBox')
        self.ui.CurrentSkill = self.ui.CurrentSkill_Rollover = self.h.last
        self.fire('UpdateInfoBox')
        self.fire(args=self.args(definition=self.h.last))
        self.fire('GetSkillDescriptionForGrade', args=self.args('GetSkillDescriptionForGrade', self.h.last), ret='Myelin preview')
        self.assertEqual({row[1] for row in self.h.scope['_skillstate_results']}, {'UVH_DeathtrapOverclock', 'MorePep', 'Myelin'})
        self.assertEqual(len(self.h.scope['_skillstate_results']), 6)
        self.assertEqual(len(self.h.hooks), 3)

    def test_changed_points_rank_pawn_tree_session_or_node_stops_without_repair(self):
        changes = [lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', 4),
                   lambda: setattr(self.tree.Skills[1], 'Grade', 1),
                   lambda: setattr(self.h.pc, 'Pawn', Obj('NewPawn')),
                   lambda: setattr(self.h.pc, 'PlayerSkillTree', Obj('OtherTree')),
                   lambda: setattr(self.h.pc.WorldInfo.GRI, 'PRIArray', WrappedArray([])),
                   lambda: self.node.SkillEffectDefinitions.append(Obj('Effect'))]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                self.start()
                change()
                before = self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, self.tree.Skills[1].Grade, list(self.h.btier.Skills)
                self.fire()
                self.assertEqual(self.h.hooks, {})
                self.assertEqual(before, (self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, self.tree.Skills[1].Grade, list(self.h.btier.Skills)))

    def test_start_refuses_unknown_state_or_any_other_trace_and_reverse_overlap(self):
        changes = [lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', None),
                   lambda: self.h.scope.update(_init_armed=True),
                   lambda: self.h.scope.update(_trace_hooks=[('other', 'pre', 'other')]),
                   lambda: self.h.scope.update(_ui_hooks=[('other', 'pre', 'other')]),
                   lambda: self.h.scope.update(_upgrade_context={})]
        for change in changes:
            self.setUp()
            change()
            self.assertFalse(self.h.call('start_skillstate_trace'))
            self.assertEqual(self.h.hooks, {})
        self.setUp()
        self.start()
        for function in ('start_ui_trace', 'start_upgrade_trace', 'start_tree_trace', 'start_skillstate_trace'):
            self.h.call(function)
            self.assertEqual(len(self.h.hooks), 3)

    def test_partial_registration_and_foreign_hook_identifiers_are_preserved(self):
        self.h.fail_add_at = self.h.add_calls + 2
        self.assertFalse(self.h.call('start_skillstate_trace'))
        self.assertEqual(self.h.hooks, {})
        self.setUp()
        key = ('WillowGame.SkillTreeGFxObject:GetSkillDescriptionForGrade', 'post', 'UVH_STATE_GetSkillDescriptionForGrade')
        foreign = lambda *args: None
        self.h.hooks[key] = foreign
        self.assertFalse(self.h.call('start_skillstate_trace'))
        self.assertEqual(self.h.hooks, {key: foreign})

    def test_failed_removal_keeps_only_inert_owned_hooks_for_retry(self):
        self.start()
        callback = next(iter(self.h.hooks.values()))
        self.h.fail_remove = True
        self.assertFalse(self.h.call('stop_skillstate_trace'))
        self.assertIsNone(self.h.scope['_skillstate_context'])
        self.assertIsNone(callback(None, None, None, None))
        self.assertFalse(self.h.call('start_skillstate_trace'))
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertFalse(self.h.call('start_upgrade_trace'))
        self.h.call('start_tree_trace')
        self.assertEqual(len(self.h.hooks), 3)
        self.h.fail_remove = False
        self.assertTrue(self.h.call('stop_skillstate_trace'))
        self.assertEqual(self.h.hooks, {})

    def test_duplicate_event_attempt_time_limits_and_zero_call_final_report(self):
        self.start()
        for _ in range(5): self.fire()
        self.assertEqual(len(self.h.scope['_skillstate_results']), 2)
        self.h.scope['_SKILLSTATE_EVENT_LIMIT'] = 3
        self.fire(ret=False)
        self.assertEqual(self.h.hooks, {})
        self.setUp()
        self.start()
        self.h.scope['_skillstate_callbacks'] = 2047
        self.fire(obj=Obj('Other'))
        self.assertEqual(self.h.hooks, {})
        self.setUp()
        self.start()
        self.h.scope['_skillstate_context']['started'] -= 100
        self.fire()
        self.assertEqual(self.h.hooks, {})
        self.setUp()
        self.start()
        self.h.call('stop_skillstate_trace')
        self.assertTrue(any('FINAL points=(5, 0) ranks=(0, 0, 0) unchanged_from_start=True' in line for line in self.h.logs))
        self.assertEqual(sum('NOT OBSERVED' in line for line in self.h.logs), 9)

    def test_reentrancy_read_errors_cancel_and_disable_remove_all_owned_hooks(self):
        self.start()
        self.h.scope['_skillstate_busy'] = True
        self.fire()
        self.assertEqual(self.h.scope['_skillstate_callbacks'], 0)
        self.h.scope['_skillstate_busy'] = False
        def broken(*args): raise RuntimeError('UI read failed')
        self.h.scope['_ui_view'] = broken
        self.fire('UpdateInfoBox')
        self.assertEqual(self.h.hooks, {})
        self.assertFalse(self.h.scope['_skillstate_busy'])
        for function in ('cancel_init_node', 'shutdown'):
            self.setUp()
            self.start()
            self.h.call(function)
            self.assertEqual(self.h.hooks, {})
            self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
            self.assertEqual(self.h.ltier.bCellIsOccupied, [True, False, True])


if __name__ == '__main__':
    unittest.main()
