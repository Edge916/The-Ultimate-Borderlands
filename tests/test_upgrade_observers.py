"""Natural POST-call observer simulations; these do not establish engine behavior."""
import types
import unittest
from enum import IntFlag
from unittest.mock import patch

import test_runtime_mock as runtime_tests
from test_runtime_mock import Harness, MetadataFunction, Obj, WrappedArray


class ESkillTreeFailureReason(IntFlag):
    # Test-only representative names/values; actual SDK members are read at runtime.
    NO_FAILURE = 0
    LOCKED = 1
    MAX_GRADE = 2


class UpgradeObserverTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        fixture = runtime_tests.RuntimeTests()
        fixture.h = self.h
        self.tree = fixture.purchase_fixture()
        self.h.pc.Class.Name = 'WillowPlayerController'
        self.node = self.h.scope['_uvh_node_state']['node']
        self.ui = Obj('GaigeTreeUI', 'SkillTreeGFxObject', WPCOwner=self.h.pc,
                      CurrentSkill=self.node, CurrentSkill_Rollover=self.node)
        old_enum = self.h.sdk.find_enum
        self.h.sdk.find_enum = lambda kind: ESkillTreeFailureReason if kind == 'ESkillTreeFailureReason' else old_enum(kind)
        eligibility = MetadataFunction('SkillTreeGFxObject', 'CanUpgradeSkill')
        eligibility.NumParams, eligibility.ParamsSize, eligibility.ReturnValueOffset = 1, 1, 0
        return_reason = Obj('ReturnValue', 'ByteProperty', PropertyFlags=1408,
                            Offset_Internal=0, ArrayDim=1, Enum=Obj('ESkillTreeFailureReason'))
        local = Obj('retVal', 'ByteProperty', PropertyFlags=0)
        eligibility._properties = lambda: iter([return_reason, local])
        cost = MetadataFunction('WillowPlayerController', 'GetSkillUpgradeCost')
        cost.NumParams, cost.ParamsSize, cost.ReturnValueOffset = 2, 8, 4
        skill_arg = Obj('Skill', 'ObjectProperty', PropertyFlags=128, Offset_Internal=0,
                        ArrayDim=1, PropertyClass=Obj('SkillDefinition'))
        return_cost = Obj('ReturnValue', 'IntProperty', PropertyFlags=1408, Offset_Internal=4, ArrayDim=1)
        cost._properties = lambda: iter([skill_arg, return_cost])
        self.h.functions = [eligibility, cost]

    def start(self):
        self.assertTrue(self.h.call('start_upgrade_trace'))
        self.assertEqual(len(self.h.hooks), 2)
        self.assertTrue(all(key[1] == 'post' for key in self.h.hooks))

    def fire(self, kind='CanUpgradeSkill', obj=None, args=None, ret=None):
        key = next(key for key in self.h.hooks if key[0].endswith(':' + kind))
        callback = self.h.hooks[key]
        if obj is None:
            obj = self.ui if kind == 'CanUpgradeSkill' else self.h.pc
        if args is None:
            args = types.SimpleNamespace(Skill=self.node, ReturnValue=999)
        if ret is None:
            ret = ESkillTreeFailureReason.NO_FAILURE if kind == 'CanUpgradeSkill' else 1
        def forbidden(*a, **kw):
            self.fail('observer invoked a native function')
        with patch.dict('sys.modules', {'unrealsdk': self.h.sdk, 'mods_base': self.h.base}):
            return callback(obj, args, ret, forbidden)

    def test_post_uses_actual_return_enum_zero_and_cost_never_invokes_or_writes(self):
        self.start()
        before = [dict(obj.__dict__) for obj in (self.h.pc, self.ui, self.node, self.tree, *self.tree.Skills)]
        arrays = (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied))
        def forbidden(*a, **kw):
            self.fail('callback called SDK discovery/construction/load/write helper')
        self.h.sdk.find_all = self.h.sdk.find_enum = self.h.sdk.construct_object = self.h.sdk.load_package = forbidden
        self.h.scope['_node_set_array'] = forbidden
        self.assertIsNone(self.fire())
        self.assertIsNone(self.fire('GetSkillUpgradeCost'))
        results = self.h.scope['_upgrade_results']
        self.assertIn('ESkillTreeFailureReason.NO_FAILURE (value=0)', results[0][2])
        self.assertEqual(results[1][2], '1')
        self.assertEqual(before, [dict(obj.__dict__) for obj in (self.h.pc, self.ui, self.node, self.tree, *self.tree.Skills)])
        self.assertEqual(arrays, (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied)))
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 5)
        self.assertEqual(self.h.loads, [])
        self.assertTrue(self.h.call('stop_upgrade_trace'))
        self.assertEqual(self.h.hooks, {})
        self.assertTrue(any('FINAL points=(5, 0) ranks=(0, 0, 0) unchanged_from_start=True' in line for line in self.h.logs))

    def test_selection_and_rollover_are_distinct_and_originals_are_comparable(self):
        self.start()
        self.ui.CurrentSkill = self.h.first
        self.ui.CurrentSkill_Rollover = self.node
        self.fire(ret=ESkillTreeFailureReason.LOCKED)
        self.fire('GetSkillUpgradeCost', args=types.SimpleNamespace(Skill=self.h.last), ret=2)
        self.assertEqual([row[1] for row in self.h.scope['_upgrade_results']], ['MorePep', 'Myelin'])
        self.assertTrue(any('skill=MorePep' in line and 'rollover=UVH_DeathtrapOverclock' in line for line in self.h.logs))
        self.h.call('stop_upgrade_trace')
        self.assertTrue(any('CanUpgradeSkill UVH_DeathtrapOverclock results=[]' in line for line in self.h.logs))

    def test_foreign_ui_controller_class_and_unknown_selection_never_capture(self):
        self.start()
        self.fire(obj=Obj('Foreign', 'SkillTreeGFxObject', WPCOwner=Obj('Other'), CurrentSkill=self.node))
        self.fire(obj=Obj('WrongClass', WPCOwner=self.h.pc, CurrentSkill=self.node))
        self.fire('GetSkillUpgradeCost', obj=Obj('OtherPC'), ret=1)
        self.fire('GetSkillUpgradeCost', args=types.SimpleNamespace(), ret=1)
        self.ui.CurrentSkill = None
        self.fire()
        self.ui.CurrentSkill = Obj('OtherSkill', 'SkillDefinition')
        self.fire()
        self.assertEqual(self.h.scope['_upgrade_results'], [])
        self.assertEqual(self.h.scope['_upgrade_skipped'], 6)
        self.assertIsNotNone(self.h.scope['_upgrade_context'])

    def test_unverified_returns_abort_without_guessing_boolean_or_raw_enum(self):
        for kind, value in [('CanUpgradeSkill', True), ('CanUpgradeSkill', 0),
                            ('CanUpgradeSkill', ESkillTreeFailureReason(8)),
                            ('GetSkillUpgradeCost', True), ('GetSkillUpgradeCost', -1),
                            ('GetSkillUpgradeCost', '1')]:
            with self.subTest(kind=kind, value=value):
                self.setUp()
                self.start()
                self.assertIsNone(self.fire(kind, ret=value))
                self.assertEqual(self.h.scope['_upgrade_results'], [])
                self.assertIsNone(self.h.scope['_upgrade_context'])
                self.assertEqual(self.h.hooks, {})

    def test_start_requires_exact_loaded_metadata_and_never_hooks_on_refusal(self):
        mutations = [lambda: self.h.functions.pop(),
                     lambda: self.h.functions.append(self.h.functions[0]),
                     lambda: setattr(self.h.functions[0], 'NumParams', 2),
                     lambda: setattr(self.h.functions[0], 'Outer', Obj('Foreign')),
                     lambda: setattr(self.h.functions[0]._properties().__next__(), 'Enum', Obj('WrongEnum')),
                     lambda: setattr(self.h.functions[1]._properties().__next__(), 'PropertyClass', Obj('Pawn')),
                     lambda: setattr(self.h.functions[1], '_properties', lambda: iter([Obj('Skill')]))]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                self.setUp()
                mutate()
                self.assertFalse(self.h.call('start_upgrade_trace'))
                self.assertEqual(self.h.hooks, {})

    def test_metadata_discovery_and_field_iteration_are_bounded(self):
        self.h.functions = (MetadataFunction('Other', 'Other') for _ in range(30001))
        self.assertFalse(self.h.call('start_upgrade_trace'))
        self.assertTrue(any('30000 objects' in line for line in self.h.logs))
        self.setUp()
        self.h.functions[0]._properties = lambda: (Obj('field' + str(i), PropertyFlags=0) for i in range(17))
        self.assertFalse(self.h.call('start_upgrade_trace'))
        self.assertTrue(any('fields exceed 16' in line for line in self.h.logs))
        self.assertEqual(self.h.hooks, {})

    def test_metadata_reflection_exception_is_contained(self):
        def broken():
            raise RuntimeError('unsupported reflection')
        self.h.functions[0]._properties = broken
        self.assertFalse(self.h.call('start_upgrade_trace'))
        self.assertEqual(self.h.hooks, {})

    def test_start_refuses_missing_enum_points_rank_and_concurrent_observers(self):
        changes = [lambda: setattr(self.h.sdk, 'find_enum', lambda kind: None),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', None),
                   lambda: setattr(self.tree.Skills[1], 'Grade', 1),
                   lambda: self.h.scope.update(_init_armed=True),
                   lambda: self.h.scope.update(_trace_hooks=[('other', 'pre', 'other')]),
                   lambda: setattr(self.h.pc, 'PlayerSkillTree', Obj('OtherTree')),
                   lambda: setattr(self.h.pc, 'Pawn', None)]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                change()
                self.assertFalse(self.h.call('start_upgrade_trace'))
                self.assertEqual(self.h.hooks, {})

    def test_each_session_tree_rank_point_and_inertness_change_stops_without_repair(self):
        changes = [lambda: setattr(self.h.pc.WorldInfo.GRI, 'PRIArray', WrappedArray([self.h.pc.PlayerReplicationInfo, Obj('Peer')])),
                   lambda: setattr(self.h.engine, 'GamePlayers', WrappedArray([])),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'Owner', Obj('Other')),
                   lambda: setattr(self.h.pc.WorldInfo, 'NetMode', 3),
                   lambda: setattr(self.h.pc.WorldInfo, 'NetMode', True),
                   lambda: setattr(self.h.pc, 'Pawn', Obj('Respawned')),
                   lambda: setattr(self.h.pc, 'PlayerSkillTree', Obj('OtherTree')),
                   lambda: setattr(self.tree, 'Outer', Obj('Other')),
                   lambda: setattr(self.tree.Skills[0], 'Grade', 1),
                   lambda: setattr(self.tree.Skills[1], 'Grade', 1),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', 4),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'SpecialistSkillPoints', 1),
                   lambda: setattr(self.tree.Skills[1], 'Index', 0),
                   lambda: setattr(self.tree.Skills[1], 'Owner', Obj('OtherTree')),
                   lambda: setattr(self.tree.Tiers[0], 'TierNumber', 1),
                   lambda: self.tree.Skills.append(self.tree.Skills[1]),
                   lambda: self.node.SkillEffectDefinitions.append(Obj('Effect')),
                   lambda: self.h.btier.Skills.reverse()]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                self.start()
                change()
                grades = [entry.Grade for entry in self.tree.Skills]
                points = (self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, self.h.pc.PlayerReplicationInfo.SpecialistSkillPoints)
                native = list(self.h.btier.Skills)
                self.assertIsNone(self.fire())
                self.assertEqual(self.h.hooks, {})
                self.assertIsNone(self.h.scope['_upgrade_context'])
                self.assertEqual(self.h.scope['_upgrade_results'], [])
                self.assertEqual(grades, [entry.Grade for entry in self.tree.Skills])
                self.assertEqual(points, (self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, self.h.pc.PlayerReplicationInfo.SpecialistSkillPoints))
                self.assertEqual(native, list(self.h.btier.Skills))

    def test_duplicate_suppression_and_all_callback_limit_include_foreign_calls(self):
        self.start()
        for _ in range(5):
            self.fire()
        self.assertEqual(len(self.h.scope['_upgrade_results']), 2)
        self.assertEqual(self.h.scope['_upgrade_skipped'], 3)
        self.h.scope['_upgrade_callbacks'] = self.h.scope['_UPGRADE_CALLBACK_LIMIT'] - 1
        self.fire(obj=Obj('Foreign'))
        self.assertEqual(self.h.hooks, {})

    def test_captured_event_limit_and_elapsed_time_cleanup(self):
        self.start()
        for cost in range(self.h.scope['_UPGRADE_EVENT_LIMIT']):
            self.fire('GetSkillUpgradeCost', ret=cost)
        self.assertEqual(len(self.h.scope['_upgrade_results']), 24)
        self.assertEqual(self.h.hooks, {})
        self.setUp()
        self.start()
        self.h.scope['_upgrade_context']['started'] -= 100
        self.fire()
        self.assertEqual(self.h.scope['_upgrade_results'], [])
        self.assertEqual(self.h.hooks, {})

    def test_reentrancy_is_inert_and_callback_errors_remove_observers(self):
        self.start()
        self.h.scope['_upgrade_busy'] = True
        self.assertIsNone(self.fire())
        self.assertEqual(self.h.scope['_upgrade_callbacks'], 0)
        self.h.scope['_upgrade_busy'] = False
        def broken(context):
            raise RuntimeError('wrapper read failed')
        self.h.scope['_upgrade_state'] = broken
        self.assertIsNone(self.fire())
        self.assertFalse(self.h.scope['_upgrade_busy'])
        self.assertEqual(self.h.hooks, {})

    def test_partial_registration_failure_removes_only_owned_hooks(self):
        self.h.fail_add_at = self.h.add_calls + 2
        self.assertFalse(self.h.call('start_upgrade_trace'))
        self.assertEqual(self.h.hooks, {})
        self.assertIsNone(self.h.scope['_upgrade_context'])
        self.setUp()
        path = self.h.scope['_UPGRADE_PATHS'][1]
        key = (path, 'post', 'UVH_UPGRADE_GetSkillUpgradeCost')
        foreign = lambda *args: None
        self.h.hooks[key] = foreign
        self.assertFalse(self.h.call('start_upgrade_trace'))
        self.assertEqual(self.h.hooks, {key: foreign})

    def test_removal_failure_retains_inert_hooks_for_retry_and_blocks_restart(self):
        self.start()
        callback = next(iter(self.h.hooks.values()))
        self.h.fail_remove = True
        self.assertFalse(self.h.call('stop_upgrade_trace'))
        self.assertIsNone(self.h.scope['_upgrade_context'])
        self.assertEqual(len(self.h.scope['_upgrade_hooks']), 2)
        self.assertIsNone(callback(self.ui, None, True, None))
        self.assertEqual(self.h.scope['_upgrade_callbacks'], 0)
        self.assertFalse(self.h.call('start_upgrade_trace'))
        self.h.fail_remove = False
        self.assertTrue(self.h.call('stop_upgrade_trace'))
        self.assertEqual(self.h.hooks, {})

    def test_cancel_and_disable_remove_observers_before_native_rollback(self):
        for action in ('cancel_init_node', 'shutdown'):
            with self.subTest(action=action):
                self.setUp()
                self.start()
                self.fire()
                self.h.call(action)
                self.assertEqual(self.h.hooks, {})
                self.assertIsNone(self.h.scope['_upgrade_context'])
                self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
                self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 5)
                self.assertTrue(all(entry.Grade == 0 for entry in self.tree.Skills))

    def test_stop_checks_final_points_even_without_a_further_ui_call(self):
        self.start()
        self.h.pc.PlayerReplicationInfo.GeneralSkillPoints = 4
        self.assertTrue(self.h.call('stop_upgrade_trace'))
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 4)
        self.assertTrue(any('FINAL UNVERIFIED' in line and 'points/ranks/runtime indices changed' in line for line in self.h.logs))


if __name__ == '__main__':
    unittest.main()
