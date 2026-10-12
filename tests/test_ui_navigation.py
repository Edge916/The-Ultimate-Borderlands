"""Bounded UI navigation simulations, not engine execution/eligibility proof."""
import types
import unittest
from unittest.mock import patch

import test_upgrade_observers as upgrade_tests
from test_runtime_mock import MetadataFunction, Obj, WrappedArray


class UINavigationTests(unittest.TestCase):
    def setUp(self):
        fixture = upgrade_tests.UpgradeObserverTests()
        fixture.setUp()
        self.h, self.tree, self.node, self.ui = fixture.h, fixture.tree, fixture.node, fixture.ui
        self.ui.NumSkillPoints = 5
        self.h.objects['ui'] = self.ui
        self.h.functions = [self.function(method) for method in ('Init', 'extInitTree', 'PostNav', 'HandleInputKey', 'UpdateInfoBox')]

    def function(self, method, owner='SkillTreeGFxObject'):
        func = MetadataFunction(owner, method)
        func.NumParams, func.ParamsSize, func.ReturnValueOffset = 0, 0, 65535
        func._properties = lambda: iter([])
        return func

    def start(self):
        self.assertTrue(self.h.call('start_ui_trace'))
        self.assertEqual(len(self.h.hooks), 10)
        self.assertEqual({key[1] for key in self.h.hooks}, {'pre', 'post_always'})

    def fire(self, method='PostNav', phase='pre', obj=None):
        key = next(key for key in self.h.hooks if key[0].endswith(':' + method) and key[1] == phase)
        callback = self.h.hooks[key]
        class Unreadable:
            def __getattr__(self, field):
                raise AssertionError('args/return must not be read')
        def forbidden(*a, **kw):
            self.fail('native invocation is forbidden')
        with patch.dict('sys.modules', {'unrealsdk': self.h.sdk, 'mods_base': self.h.base}):
            return callback(obj or self.ui, Unreadable(), Unreadable(), forbidden)

    def test_pre_and_post_any_capture_selection_change_without_call_or_write(self):
        self.start()
        before = [dict(obj.__dict__) for obj in (self.h.pc, self.node, self.tree, *self.tree.Skills)]
        arrays = list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied)
        self.ui.CurrentSkill_Rollover = self.h.last
        self.assertIsNone(self.fire())
        self.ui.CurrentSkill = self.h.last  # Simulated engine navigation, never done by the observer.
        self.assertIsNone(self.fire(phase='post_always'))
        results = self.h.scope['_ui_results']
        self.assertEqual(results[0][1:4], ('PRE', 'UVH_DeathtrapOverclock', 'Myelin'))
        self.assertEqual(results[1][1:4], ('POST_ANY', 'Myelin', 'Myelin'))
        self.assertEqual(before, [dict(obj.__dict__) for obj in (self.h.pc, self.node, self.tree, *self.tree.Skills)])
        self.assertEqual(arrays, (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied)))
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 5)
        self.assertEqual(self.h.loads, [])
        self.assertTrue(self.h.call('stop_ui_trace'))
        self.assertEqual(self.h.hooks, {})

    def test_zero_calls_still_produce_owned_start_stop_inventory_and_final_state(self):
        self.start()
        self.ui.CurrentSkill = self.h.first
        self.ui.CurrentSkill_Rollover = self.node
        self.assertTrue(self.h.call('stop_ui_trace'))
        self.assertEqual(self.h.scope['_ui_callbacks'], 0)
        self.assertTrue(any('SNAPSHOT START' in line and 'current=UVH_DeathtrapOverclock' in line for line in self.h.logs))
        self.assertTrue(any('SNAPSHOT STOP' in line and 'current=MorePep' in line and 'rollover=UVH_DeathtrapOverclock' in line for line in self.h.logs))
        self.assertTrue(any('FINAL points=(5, 0) ranks=(0, 0, 0) unchanged_from_start=True' in line for line in self.h.logs))

    def test_unknown_or_foreign_selection_is_never_claimed_owned(self):
        self.start()
        for selected in (None, Obj('Foreign', 'SkillDefinition'), self.h.pc):
            self.ui.CurrentSkill = selected
            self.fire()
        self.assertEqual([row[2] for row in self.h.scope['_ui_results']], ['<none/unavailable>', '<unverified>', '<unverified>'])
        self.ui.CurrentSkill = self.h.first
        self.tree.Skills[0].Owner = Obj('OtherTree')
        self.assertIsNone(self.fire())
        self.assertEqual(self.h.hooks, {})

    def test_foreign_ui_never_reads_its_selection_and_all_callbacks_are_counted(self):
        class Foreign(Obj):
            @property
            def CurrentSkill(self):
                raise AssertionError('must not inspect foreign UI selection')
        other = Foreign('ForeignUI', 'SkillTreeGFxObject', WPCOwner=Obj('OtherPC'))
        self.h.objects['foreign'] = other
        self.start()
        self.fire(obj=other)
        self.fire(obj=Obj('WrongClass', WPCOwner=self.h.pc))
        self.assertEqual(self.h.scope['_ui_results'], [])
        self.assertEqual(self.h.scope['_ui_skipped'], 2)
        self.h.call('stop_ui_trace')
        self.assertTrue(any('INVENTORY STOP scanned=2 owned=1' in line for line in self.h.logs))

    def test_discovery_requires_exact_loaded_owner_class_and_canonical_path(self):
        good = self.function('PostNav')
        bad_path = self.function('PreNav')
        bad_path.path = 'WillowGame.SkillTreeGFxObject.SomeState:PreNav'
        wrong_kind = self.function('UpdateInfoBox')
        wrong_kind.Class.Name = 'Object'
        self.h.functions = [good, bad_path, wrong_kind, self.function('PostNav', 'Foreign'),
                            self.function('RequestSkillUpgrade'), self.function('CanUpgradeSkill'),
                            self.function('GetSkillUpgradeCost', 'WillowPlayerController')]
        paths = self.h.call('_ui_candidates')
        self.assertEqual(paths, ['WillowGame.SkillTreeGFxObject:PostNav'])
        self.h.functions = [bad_path, wrong_kind]
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertEqual(self.h.hooks, {})

    def test_discovery_priority_field_and_function_caps_and_duplicate_refusal(self):
        extra = [self.function('Refresh' + str(i)) for i in range(20)]
        self.h.functions = extra + self.h.functions
        self.h.functions[0]._properties = lambda: (Obj('field' + str(i), 'IntProperty', PropertyFlags=0) for i in range(20))
        paths = self.h.call('_ui_candidates')
        self.assertEqual(len(paths), 10)
        self.assertEqual([path.rsplit(':', 1)[-1] for path in paths[:5]],
                         ['PostNav', 'HandleInputKey', 'UpdateInfoBox', 'Init', 'extInitTree'])
        self.assertTrue(any('fields capped at 8' in line for line in self.h.logs))
        self.h.functions = [self.function('PostNav')] * 2
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertEqual(self.h.hooks, {})

    def test_metadata_scan_inventory_caps_and_reflection_errors_refuse_start(self):
        self.h.functions = (self.function('Other', 'Other') for _ in range(30001))
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertTrue(any('30000' in line for line in self.h.logs))
        self.setUp()
        def broken():
            raise RuntimeError('reflection failed')
        self.h.functions[0]._properties = broken
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertEqual(self.h.hooks, {})
        self.setUp()
        for i in range(32):
            self.h.objects[str(i)] = Obj('OtherUI' + str(i), 'SkillTreeGFxObject')
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertTrue(any('inventory exceeds 32' in line for line in self.h.logs))
        self.assertEqual(self.h.hooks, {})

    def test_live_candidate_crowding_keeps_core_helpers_and_navigation_anchors(self):
        # All 24 names discovered in the preserved v0.2.5 game log. Its old
        # selection spent four of ten slots on artifacts and missed all six helpers.
        methods = (
            'Init', 'extInitTree', 'ArtifactSelect', 'EquipSelectedArtifact',
            'Flash_UpdateArtifactSelection', 'Nav_Back', 'Nav_Down',
            'Nav_DownArtifact', 'Nav_Left', 'Nav_Right', 'Nav_Up', 'Nav_UpArtifact',
            'Navigate', 'PostNav', 'HandleInputKey', 'UpdateInfoBox',
            'Flash_SendInitialSkillData', 'Flash_SetSkillPointProperties',
            'Flash_SetSkillPointProperties_AS', 'GetSkillDescriptionForGrade',
            'SetSkillIconVisibility', 'UpdateAllSkillIcons',
            'UpdateAllSkillIcons_Branch', 'UpdateSkillIcon')
        helpers = {'PostNav', 'Navigate', 'HandleInputKey', 'UpdateInfoBox',
                   'Flash_SetSkillPointProperties', 'Flash_SetSkillPointProperties_AS'}
        expected = helpers | {'Init', 'Nav_Down', 'Nav_Left', 'Nav_Right'}
        self.h.functions = [self.function(method) for method in methods]
        # Unrelated selection/refresh names must not crowd out known core methods.
        self.h.functions.extend(self.function('Select' + str(i)) for i in range(30))
        paths = self.h.call('_ui_candidates')
        self.assertEqual(len(paths), 10)
        self.assertEqual({path.rsplit(':', 1)[-1] for path in paths}, expected)
        self.h.functions.reverse()
        self.assertEqual(self.h.call('_ui_candidates'), paths)
        self.assertTrue(self.h.call('start_ui_trace'))
        self.assertEqual(len(self.h.hooks), 20)
        for method in ('PostNav', 'UpdateInfoBox', 'Flash_SetSkillPointProperties'):
            self.assertIsNone(self.fire(method))
        self.assertEqual(len(self.h.scope['_ui_results']), 3)
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 5)
        self.assertTrue(self.h.call('stop_ui_trace'))
        self.assertEqual(self.h.hooks, {})

    def test_priority_never_invents_missing_helpers_or_accepts_foreign_metadata(self):
        good = self.function('Flash_SetSkillPointProperties')
        good.path = 'WillowGame.SkillTreeGFxObject.Flash_SetSkillPointProperties'
        nested = self.function('Navigate')
        nested.path = 'WillowGame.SkillTreeGFxObject.SomeState:Navigate'
        wrong_class = self.function('HandleInputKey')
        wrong_class.Class.Name = 'Object'
        self.h.functions = [good, self.function('UpdateInfoBox'), nested, wrong_class,
                            self.function('PostNav', 'Foreign'), self.function('Init')]
        paths = self.h.call('_ui_candidates')
        self.assertEqual({path.rsplit(':', 1)[-1] for path in paths},
                         {'Flash_SetSkillPointProperties', 'UpdateInfoBox', 'Init'})
        self.assertTrue(self.h.call('start_ui_trace'))
        self.assertEqual({key[0] for key in self.h.hooks}, set(paths))
        self.assertEqual(len(self.h.hooks), 6)

    def test_artifact_and_equip_descriptors_are_excluded_before_reflection(self):
        def forbidden():
            raise AssertionError('excluded descriptor must not be inspected')
        self.h.functions = [self.function('Init')]
        for method in ('ArtifactSelect', 'Nav_UpArtifact', 'RefreshArtifact',
                       'RolloverArtifact', 'EquipSelectedSkill', 'EquipInit'):
            func = self.function(method)
            func._properties = forbidden
            self.h.functions.append(func)
        self.assertTrue(self.h.call('start_ui_trace'))
        self.assertEqual(len(self.h.hooks), 2)
        self.assertEqual({key[0] for key in self.h.hooks}, {'WillowGame.SkillTreeGFxObject:Init'})
        self.assertFalse(any('CANDIDATE' in line and ('Artifact' in line or 'Equip' in line)
                             for line in self.h.logs))

    def test_inventory_has_four_owned_ui_print_limit_and_allows_none_loaded(self):
        for i in range(6):
            self.h.objects[str(i)] = Obj('UI' + str(i), 'SkillTreeGFxObject', WPCOwner=self.h.pc)
        self.start()
        self.assertEqual(sum('SNAPSHOT START' in line for line in self.h.logs), 4)
        self.h.call('stop_ui_trace')
        self.setUp()
        self.h.objects.pop('ui')
        self.start()
        self.assertTrue(any('INVENTORY START scanned=0 owned=0' in line for line in self.h.logs))

    def test_start_refuses_stale_tree_points_rank_session_and_other_traces(self):
        changes = [lambda: setattr(self.h.pc, 'PlayerSkillTree', Obj('OtherTree')),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', None),
                   lambda: setattr(self.tree.Skills[1], 'Grade', 1),
                   lambda: setattr(self.h.pc.WorldInfo.GRI, 'PRIArray', WrappedArray([])),
                   lambda: self.h.scope.update(_init_armed=True),
                   lambda: self.h.scope.update(_upgrade_hooks=[('foreign', 'post', 'foreign')]),
                   lambda: self.h.scope.update(_trace_hooks=[('foreign', 'pre', 'foreign')])]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                change()
                self.assertFalse(self.h.call('start_ui_trace'))
                self.assertEqual(self.h.hooks, {})
        self.setUp()
        self.start()
        self.assertFalse(self.h.call('start_upgrade_trace'))
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertEqual(len(self.h.hooks), 10)

    def test_changed_session_points_rank_node_or_tree_stops_without_repair(self):
        changes = [lambda: setattr(self.h.pc.WorldInfo.GRI, 'PRIArray', WrappedArray([self.h.pc.PlayerReplicationInfo, Obj('Peer')])),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', 4),
                   lambda: setattr(self.tree.Skills[1], 'Grade', 1),
                   lambda: setattr(self.h.pc, 'Pawn', Obj('Respawned')),
                   lambda: setattr(self.h.pc, 'PlayerSkillTree', Obj('Other')),
                   lambda: self.node.SkillActivationActions.append(Obj('Action'))]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                self.start()
                change()
                before = self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, self.tree.Skills[1].Grade, list(self.h.btier.Skills)
                self.fire()
                self.assertEqual(self.h.hooks, {})
                self.assertIsNone(self.h.scope['_ui_context'])
                self.assertEqual(before, (self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, self.tree.Skills[1].Grade, list(self.h.btier.Skills)))

    def test_duplicate_event_callback_and_time_bounds_remove_hooks(self):
        self.start()
        for _ in range(4):
            self.fire()
        self.assertEqual(len(self.h.scope['_ui_results']), 2)
        self.h.scope['_UI_EVENT_LIMIT'] = 3
        self.fire(phase='post_always')
        self.assertEqual(len(self.h.scope['_ui_results']), 3)
        self.assertEqual(self.h.hooks, {})
        self.setUp()
        self.start()
        self.h.scope['_ui_callbacks'] = self.h.scope['_UI_CALLBACK_LIMIT'] - 1
        self.fire(obj=Obj('Foreign'))
        self.assertEqual(self.h.hooks, {})
        self.setUp()
        self.start()
        self.h.scope['_ui_context']['started'] -= 100
        self.fire()
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.scope['_ui_results'], [])

    def test_partial_registration_and_preexisting_foreign_hooks_are_preserved(self):
        self.h.fail_add_at = self.h.add_calls + 3
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertEqual(self.h.hooks, {})
        self.setUp()
        key = ('WillowGame.SkillTreeGFxObject:extInitTree', 'pre', 'UVH_UI_PRE_extInitTree')
        foreign = lambda *args: None
        self.h.hooks[key] = foreign
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertEqual(self.h.hooks, {key: foreign})

    def test_failed_removal_leaves_inert_hooks_for_retry_and_blocks_restart(self):
        self.start()
        callback = next(iter(self.h.hooks.values()))
        self.h.fail_remove = True
        self.assertFalse(self.h.call('stop_ui_trace'))
        self.assertIsNone(self.h.scope['_ui_context'])
        self.assertEqual(len(self.h.scope['_ui_hooks']), 10)
        self.assertIsNone(callback(self.ui, None, None, None))
        self.assertFalse(self.h.call('start_ui_trace'))
        self.assertFalse(self.h.call('start_upgrade_trace'))
        self.h.fail_remove = False
        self.assertTrue(self.h.call('stop_ui_trace'))
        self.assertEqual(self.h.hooks, {})

    def test_reentrancy_errors_cancel_disable_and_final_point_check(self):
        self.start()
        self.h.scope['_ui_busy'] = True
        self.fire()
        self.assertEqual(self.h.scope['_ui_callbacks'], 0)
        self.h.scope['_ui_busy'] = False
        def broken(*args):
            raise RuntimeError('UI wrapper read error')
        self.h.scope['_ui_view'] = broken
        self.fire()
        self.assertEqual(self.h.hooks, {})
        self.assertFalse(self.h.scope['_ui_busy'])
        for action in ('cancel_init_node', 'shutdown'):
            with self.subTest(action=action):
                self.setUp()
                self.start()
                self.h.call(action)
                self.assertEqual(self.h.hooks, {})
                self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
                self.assertIsNone(self.h.scope['_ui_context'])
        self.setUp()
        self.start()
        self.h.pc.PlayerReplicationInfo.GeneralSkillPoints = 4
        self.h.call('stop_ui_trace')
        self.assertTrue(any('FINAL UNVERIFIED' in line for line in self.h.logs))
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 4)
        self.assertEqual(self.h.hooks, {})


if __name__ == '__main__':
    unittest.main()
