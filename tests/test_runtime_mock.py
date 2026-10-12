"""Simulated SDK regression tests, never proof of engine/UI behavior."""
import sys
import types
import unittest
from enum import IntEnum, IntFlag
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sdk_mods' / 'UltimateVaultHunterDeathtrapBoost' / '__init__.py'
BRANCH = 'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble'
LAYOUT = 'GD_Tulip_Mechromancer_Skills.SkillTrees.Layout_LittleBigTrouble'
TEMPLATE = 'GD_Tulip_Mechromancer_Skills.LittleBigTrouble.MorePep'


class NetMode(IntEnum):
    NM_Standalone = 0
    NM_DedicatedServer = 1
    NM_ListenServer = 2
    NM_Client = 3


class Obj:
    def __init__(self, name, kind='Object', **fields):
        self.Name = name
        self.Class = types.SimpleNamespace(Name=kind)
        self.__dict__.update(fields)


class MetadataFunction(Obj):
    def __init__(self, owner, method, separator=':'):
        super().__init__(method, 'Function', Outer=Obj(owner))
        self.path = 'WillowGame.' + owner + separator + method

    def _path_name(self):
        return self.path


class WrappedArray:
    """Sequence protocol without Python list identity or slicing."""
    def __init__(self, values):
        self.values = tuple(values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        return self.values[index]


class Harness:
    def __init__(self, source=None):
        self.logs, self.loads, self.constructed = [], [], []
        self.first = Obj('MorePep', 'SkillDefinition', SkillIcon='icon')
        self.last = Obj('Myelin', 'SkillDefinition')
        self.btier = types.SimpleNamespace(Skills=[self.first, self.last])
        self.ltier = types.SimpleNamespace(bCellIsOccupied=[True, False, True])
        self.branch = Obj('Branch_LittleBigTrouble', 'SkillTreeBranchDefinition', Tiers=[self.btier])
        self.layout = Obj('Layout_LittleBigTrouble', 'SkillTreeBranchLayoutDefinition', Tiers=[self.ltier])
        self.pc = Obj('Controller_0', PlayerClass=Obj('CharClass_Mechromancer'), Pawn=None)
        self.pc.WorldInfo = Obj('WorldInfo_0', NetMode=0)
        self.pc.PlayerReplicationInfo = Obj('PRI_0', Owner=self.pc)
        self.pc.WorldInfo.GRI = Obj('GRI_0', PRIArray=WrappedArray([self.pc.PlayerReplicationInfo]))
        self.engine = Obj('Engine_0', GamePlayers=WrappedArray([Obj('LocalPlayer_0', Actor=self.pc)]))
        self.objects = {BRANCH: self.branch, LAYOUT: self.layout, TEMPLATE: self.first}
        self.functions = [MetadataFunction('WillowPlayerController', 'InitializeSkillTree')]
        self.hooks = {}
        self.fail_add_at = None
        self.fail_remove = False
        self.add_calls = 0
        self.sdk = types.ModuleType('unrealsdk')
        self.sdk.logging = types.SimpleNamespace(info=self.logs.append)
        self.sdk.find_object = lambda kind, path: self.objects.get(path)
        self.sdk.load_package = self.loads.append
        self.sdk.construct_object = self.construct
        self.sdk.find_all = self.find_all
        self.sdk.find_enum = lambda enum_name: NetMode if enum_name == 'ENetMode' else None
        self.sdk.hooks = types.SimpleNamespace(
            Type=types.SimpleNamespace(PRE='pre', POST='post', POST_UNCONDITIONAL='post_always'),
            add_hook=self.add_hook, remove_hook=self.remove_hook,
            has_hook=lambda path, phase, ident: (path, phase, ident) in self.hooks)
        base = types.ModuleType('mods_base')
        base.ButtonOption = lambda *args, **kwargs: kwargs
        base.CoopSupport = types.SimpleNamespace(ClientSide='client')
        base.Game = types.SimpleNamespace(BL2='bl2')
        base.get_pc = lambda **kwargs: self.pc
        base.build_mod = self.build_mod
        base.ENGINE = self.engine
        self.base = base
        self.scope = {}
        with patch.dict(sys.modules, {'unrealsdk': self.sdk, 'mods_base': base}):
            exec(compile(source or SOURCE.read_text(encoding='utf-8'), str(SOURCE), 'exec'), self.scope)

    def build_mod(self, **kwargs):
        self.mod_options = kwargs

    def call(self, function, *args):
        with patch.dict(sys.modules, {'unrealsdk': self.sdk, 'mods_base': self.base}):
            return self.scope[function](*args)

    def find_all(self, kind, exact=False):
        if kind == 'Function':
            return iter(self.functions)
        return (obj for obj in self.objects.values() if obj.Class.Name == kind)

    def construct(self, kind, outer, name):
        node = Obj(name, kind, SkillEffectDefinitions=[], SkillActivationActions=[],
                   SkillDeactivationActions=[])
        self.constructed.append(node)
        self.objects[BRANCH + '.' + name] = node
        return node

    def add_hook(self, path, phase, ident, callback):
        self.add_calls += 1
        if self.add_calls == self.fail_add_at:
            raise RuntimeError('simulated registration failure')
        key = (path, phase, ident)
        if key in self.hooks:
            return False
        self.hooks[key] = callback
        return True

    def remove_hook(self, path, phase, ident):
        if self.fail_remove:
            raise RuntimeError('simulated removal failure')
        return self.hooks.pop((path, phase, ident), None) is not None

    def fire(self, key, obj=None, args=None):
        with patch.dict(sys.modules, {'unrealsdk': self.sdk, 'mods_base': self.base}):
            return self.hooks[key](obj or self.pc, args or types.SimpleNamespace(),
                                   123, lambda: (_ for _ in ()).throw(AssertionError('native call forbidden')))

    def names(self):
        return [obj.Name for obj in self.btier.Skills]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def test_import_never_installs_observers_or_mutates(self):
        self.assertEqual(self.h.loads, [])
        self.assertEqual(self.h.constructed, [])
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertEqual(self.h.mod_options['version'], '0.2.18')

    def init_fixture(self):
        self.h.branch.Tiers.extend(types.SimpleNamespace(Skills=[]) for _ in range(5))
        self.h.layout.Tiers.extend(types.SimpleNamespace(bCellIsOccupied=[]) for _ in range(5))
        self.h.branch.Layout = self.h.layout
        tree = Obj('PlayerSkillTree_0', 'PlayerSkillTree', Outer=self.h.pc,
                   Branches=[], Skills=[], Tiers=[])
        definition = Obj('SkillTree_Mechromancer', 'SkillTreeDefinition',
                         _path_name=lambda: 'GD_Tulip_Mechro_Streaming.SkillTree.SkillTree_Mechromancer')
        return tree, types.SimpleNamespace(SkillTreeDef=definition)

    def run_pre(self, tree, args):
        def forbidden():
            self.fail('hook invoked native function')
        return self.h.call('_init_pre', tree, args, None, forbidden)

    def simulate_native_initialize(self, tree):
        tree.Skills = [types.SimpleNamespace(Definition=skill, Grade=0, Index=i)
                       for i, skill in enumerate(self.h.btier.Skills)]
        tree.Branches = [types.SimpleNamespace(Definition=self.h.branch, TierIndices=[0])]
        tree.Tiers = [types.SimpleNamespace(SkillIndices=list(range(len(tree.Skills))))]

    def purchase_fixture(self):
        tree, args = self.init_fixture()
        self.h.call('arm_init_node')
        self.run_pre(tree, args)
        self.simulate_native_initialize(tree)
        self.h.call('_init_post', tree, args, None, None)
        self.h.pc.Pawn = Obj('GaigePawn')
        self.h.pc.PlayerSkillTree = tree
        self.h.pc.PlayerReplicationInfo.GeneralSkillPoints = 5
        self.h.pc.PlayerReplicationInfo.SpecialistSkillPoints = 0
        for entry in tree.Skills:
            entry.Owner = tree
            entry.ParentTierIndex = 0
        tree.Tiers[0].TierNumber = 0
        tree.Tiers[0].bUnlocked = True
        tree.Tiers[0].BranchPointsToUnlockTier = 0
        return tree

    def test_purchase_snapshot_reads_ranks_points_and_metadata_without_gameplay_calls(self):
        tree = self.purchase_fixture()
        def forbidden(*args, **kwargs):
            self.fail('purchase diagnostic invoked a game function or mutation API')
        for owner in (self.h.pc, tree):
            for method in ('UpgradeSkill', 'SetSkillGrade', 'GetSkillUpgradeCost',
                           'GetSkillState', 'GetSkillGradeByDef', 'ResetSkillTree', 'SaveSkillSaveGameData'):
                setattr(owner, method, forbidden)
        self.h.sdk.construct_object = self.h.sdk.load_package = forbidden
        self.h.sdk.hooks.add_hook = forbidden
        func = MetadataFunction('PlayerSkillTree', 'UpgradeSkill')
        func.FunctionFlags, func.NumParams, func.ParamsSize, func.ReturnValueOffset = 1024, 2, 8, 4
        param = Obj('SkillDef', 'ObjectProperty', PropertyFlags=128, Offset_Internal=0,
                    ArrayDim=1, PropertyClass=Obj('SkillDefinition'))
        result = Obj('ReturnValue', 'BoolProperty', PropertyFlags=1024, Offset_Internal=4, ArrayDim=1)
        func._properties = lambda: iter((param, result))
        self.h.functions = [func]
        self.h.logs.clear()
        before_skills, before_cells = list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied)
        self.assertTrue(self.h.call('inspect_overclock_purchase'))
        self.assertTrue(any('PRI.GeneralSkillPoints=5' in x for x in self.h.logs))
        self.assertTrue(any('NODE rank=0 max_rank=1' in x for x in self.h.logs))
        self.assertTrue(any('FUNCTION WillowGame.PlayerSkillTree:UpgradeSkill' in x for x in self.h.logs))
        self.assertTrue(any('SkillDef type=ObjectProperty flags=128' in x for x in self.h.logs))
        self.assertTrue(any('object_class=SkillDefinition' in x for x in self.h.logs))
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 5)
        self.assertEqual([entry.Grade for entry in tree.Skills], [0, 0, 0])
        self.assertEqual(list(self.h.btier.Skills), before_skills)
        self.assertEqual(list(self.h.ltier.bCellIsOccupied), before_cells)
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(len(self.h.constructed), 1)

    def test_purchase_snapshot_exposes_zero_enum_and_constraint_fields_without_evaluation(self):
        tree = self.purchase_fixture()
        class SkillType(IntFlag):
            SKILL_Passive = 0
            SKILL_Active = 1
        constraint_type = Obj('SkillConstraintData', 'ScriptStruct')
        constraint_type._properties = lambda: iter((
            Obj('Constraint', 'ObjectProperty'), Obj('MinGrade', 'IntProperty'),
            Obj('Evaluate', 'DelegateProperty')))
        def forbidden(*args, **kwargs):
            self.fail('read-only comparison evaluated a constraint or invoked gameplay')
        constraint = types.SimpleNamespace(_type=constraint_type, MinGrade=1,
            Constraint=Obj('NativeRequirement', 'SkillConstraintDefinition'), Evaluate=forbidden)
        self.h.first.SkillConstraints = WrappedArray([constraint])
        self.h.first.LockedSkillDetailStr = 'Native locked detail'
        self.h.last.SkillConstraints = []
        node = tree.Skills[1].Definition
        node.SkillConstraints = []
        for definition in (node, self.h.first, self.h.last):
            definition.SkillType = SkillType.SKILL_Passive
        for owner in (self.h.pc, tree):
            for method in ('UpgradeSkill', 'SetSkillGrade', 'GetSkillUpgradeCost',
                           'GetSkillState', 'ResetSkillTree', 'SaveSkillSaveGameData'):
                setattr(owner, method, forbidden)
        self.h.sdk.construct_object = self.h.sdk.load_package = self.h.sdk.hooks.add_hook = forbidden
        self.h.logs.clear()
        self.assertTrue(self.h.call('inspect_overclock_purchase'))
        self.assertEqual(sum('skill_type=SkillType.SKILL_Passive (value=0)' in x for x in self.h.logs), 3)
        self.assertTrue(any('CONSTRAINT MorePep[0].MinGrade type=IntProperty value=1' in x for x in self.h.logs))
        self.assertTrue(any('NativeRequirement [SkillConstraintDefinition]' in x for x in self.h.logs))
        self.assertTrue(any("LockedSkillDetailStr='Native locked detail'" in x for x in self.h.logs))
        self.assertFalse(any('CONSTRAINT MorePep[0].Evaluate' in x for x in self.h.logs))
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 5)
        self.assertEqual([entry.Grade for entry in tree.Skills], [0, 0, 0])
        self.assertEqual(constraint.MinGrade, 1)
        self.assertEqual(len(self.h.first.SkillConstraints), 1)
        self.assertEqual(len(node.SkillConstraints), 0)
        self.assertEqual(self.h.hooks, {})

    def test_constraint_comparison_bounds_fields_and_constraints(self):
        struct_type = Obj('SkillConstraintData', 'ScriptStruct')
        struct_type._properties = lambda: (Obj('Field' + str(i), 'IntProperty') for i in range(100))
        constraint = types.SimpleNamespace(_type=struct_type, **{'Field' + str(i): i for i in range(100)})
        self.h.first.SkillConstraints = WrappedArray([constraint] * 100)
        self.h.call('_purchase_constraint_details', self.h.first)
        self.assertEqual(sum(' CONSTRAINT ' in x for x in self.h.logs), 4 * 8)
        self.assertTrue(any('Constraints capped at 4' in x for x in self.h.logs))
        self.assertTrue(any('Constraint fields capped at 8' in x for x in self.h.logs))
        self.assertEqual(len(self.h.first.SkillConstraints), 100)
        self.assertEqual(self.h.hooks, {})

    def test_constraint_comparison_refuses_unknown_struct_and_contains_reflection_errors(self):
        unknown = Obj('OtherStruct', 'ScriptStruct')
        unknown._properties = lambda: self.fail('unknown struct traversed')
        broken = Obj('SkillConstraintData', 'ScriptStruct')
        def unavailable(): raise RuntimeError('reflection unavailable')
        broken._properties = unavailable
        self.h.first.SkillConstraints = WrappedArray([
            types.SimpleNamespace(_type=unknown), types.SimpleNamespace(_type=broken),
            types.SimpleNamespace()])
        self.h.call('_purchase_constraint_details', self.h.first)
        self.assertEqual(sum('not traversed' in x for x in self.h.logs), 2)
        self.assertTrue(any('Constraint fields unavailable MorePep[1]: RuntimeError' in x for x in self.h.logs))
        self.h.first.SkillConstraints = None
        self.h.call('_purchase_constraint_details', self.h.first)
        self.assertTrue(any('constraint details unavailable' in x for x in self.h.logs))
        self.assertEqual(self.h.hooks, {})

    def test_purchase_metadata_details_prioritize_upgrade_ui_checks(self):
        methods = ('CanUpgradeSkill', 'Flash_SetSkillPointProperties', 'Flash_SetSkillPointProperties_AS')
        funcs = [MetadataFunction('PlayerSkillTree', 'UpgradeSkill' + str(i)) for i in range(40)]
        funcs += [MetadataFunction('SkillTreeGFxObject', method) for method in methods]
        for func in funcs:
            func._properties = lambda: iter(())
        self.h.functions = funcs
        self.h.call('_purchase_function_metadata')
        details = [x for x in self.h.logs if ' FUNCTION ' in x]
        self.assertEqual(len(details), 12)
        for method in methods:
            self.assertTrue(any('SkillTreeGFxObject:' + method + ' flags=' in x for x in details))
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.constructed, [])

    def test_purchase_snapshot_refuses_missing_foreign_or_stale_state(self):
        for failure in ('record', 'menu', 'class', 'owner', 'current_tree', 'peer',
                        'patch', 'duplicate', 'entry_owner', 'entry_index', 'entry_tier',
                        'first_tier', 'tier_number', 'large_tiers'):
            with self.subTest(failure=failure):
                self.h = Harness()
                tree = self.purchase_fixture()
                if failure == 'record': self.h.scope['_uvh_node_state'] = None
                elif failure == 'menu': self.h.pc.Pawn = None
                elif failure == 'class': self.h.pc.PlayerClass.Name = 'CharClass_Siren'
                elif failure == 'owner': tree.Outer = Obj('OtherController')
                elif failure == 'current_tree': self.h.pc.PlayerSkillTree = Obj('OtherTree')
                elif failure == 'peer': self.h.pc.WorldInfo.GRI.PRIArray = [self.h.pc.PlayerReplicationInfo, Obj('Peer')]
                elif failure == 'patch': self.h.ltier.bCellIsOccupied = [True, False, True]
                elif failure == 'duplicate': tree.Skills.append(tree.Skills[1])
                elif failure == 'entry_owner': tree.Skills[1].Owner = Obj('OtherTree')
                elif failure == 'entry_index': tree.Skills[1].Index = -1
                elif failure == 'entry_tier': tree.Skills[1].ParentTierIndex = -1
                elif failure == 'first_tier': tree.Branches[0].TierIndices = [1]
                elif failure == 'tier_number': tree.Tiers[0].TierNumber = 1
                elif failure == 'large_tiers': tree.Tiers *= 65
                self.h.logs.clear()
                def forbidden(*args, **kwargs): self.fail('refused snapshot still scanned or mutated')
                self.h.sdk.find_all = self.h.sdk.construct_object = self.h.sdk.load_package = forbidden
                before = list(self.h.btier.Skills)
                self.assertFalse(self.h.call('inspect_overclock_purchase'))
                self.assertEqual(list(self.h.btier.Skills), before)
                self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 5)
                self.assertTrue(any('NOT INSPECTED:' in x for x in self.h.logs))

    def test_purchase_snapshot_missing_points_and_nonzero_grade_are_logged_never_repaired(self):
        tree = self.purchase_fixture()
        del self.h.pc.PlayerReplicationInfo.GeneralSkillPoints
        tree.Skills[1].Grade = 1
        self.h.logs.clear()
        self.assertTrue(self.h.call('inspect_overclock_purchase'))
        self.assertTrue(any('PRI.GeneralSkillPoints=<none>' in x for x in self.h.logs))
        self.assertTrue(any('UNEXPECTED RANK:' in x for x in self.h.logs))
        self.assertEqual(tree.Skills[1].Grade, 1)
        self.assertFalse(hasattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints'))
        self.assertEqual(self.h.hooks, {})

    def test_purchase_metadata_is_bounded_filters_paths_and_handles_reflection_errors(self):
        self.h.functions = [MetadataFunction('PlayerSkillTree', 'GetSkillState' + str(i)) for i in range(40)]
        for func in self.h.functions:
            func._properties = lambda: (Obj('Field' + str(i), 'IntProperty') for i in range(100))
        invalid = MetadataFunction('Unrelated', 'UpgradeSkill')
        foreign = MetadataFunction('PlayerSkillTree', 'UpgradeSkill')
        foreign.path = 'OtherGame.PlayerSkillTree:UpgradeSkill'
        nested = MetadataFunction('PlayerSkillTree', 'UpgradeSkill')
        nested.path = 'WillowGame.PlayerSkillTree:State.UpgradeSkill'
        broken = MetadataFunction('WillowPlayerController', 'GetSkillUpgradeCost')
        def unavailable(): raise RuntimeError('unsupported reflection')
        broken._properties = unavailable
        self.h.functions += [invalid, foreign, nested, broken]
        self.h.call('_purchase_function_metadata')
        self.assertEqual(sum(' FUNCTION ' in x for x in self.h.logs), 12)
        self.assertLessEqual(sum(' FIELD ' in x for x in self.h.logs), 12 * 16)
        self.assertTrue(any('Metadata fields unavailable' in x for x in self.h.logs))
        self.assertFalse(any('DISCOVERED OtherGame' in x or 'DISCOVERED WillowGame.Unrelated' in x for x in self.h.logs))
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.constructed, [])

    def test_purchase_metadata_scan_cap_and_no_discovery_are_explicit(self):
        calls = [0]
        def endless(kind, exact=False):
            while True:
                calls[0] += 1
                yield Obj('OtherFunction', 'Function', Outer=Obj('OtherOwner'))
        self.h.sdk.find_all = endless
        self.h.call('_purchase_function_metadata')
        self.assertLessEqual(calls[0], 30001)
        self.assertTrue(any('scan capped' in x for x in self.h.logs))
        self.assertTrue(any('discovered=0' in x for x in self.h.logs))
        self.assertEqual(self.h.hooks, {})

    def test_purchase_metadata_scan_failure_keeps_node_state_and_all_points_unchanged(self):
        tree = self.purchase_fixture()
        record = self.h.scope['_uvh_node_state']
        def unavailable(*args, **kwargs): raise RuntimeError('metadata unavailable')
        self.h.sdk.find_all = unavailable
        self.assertFalse(self.h.call('inspect_overclock_purchase'))
        self.assertIs(self.h.scope['_uvh_node_state'], record)
        self.assertEqual([entry.Grade for entry in tree.Skills], [0, 0, 0])
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 5)
        self.h.call('cancel_init_node')
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])

    def test_init_arm_is_explicit_no_loads_or_writes_and_cancel_removes_hooks(self):
        self.h.call('arm_init_node')
        self.assertTrue(self.h.scope['_init_armed'])
        self.assertEqual(len(self.h.hooks), 2)
        self.assertEqual(self.h.loads, [])
        self.assertEqual(self.h.constructed, [])
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.h.call('add_overclock_node')
        self.assertEqual(self.h.loads, [])
        self.assertEqual(self.h.constructed, [])
        self.h.call('cancel_init_node')
        self.assertEqual(self.h.hooks, {})
        self.assertFalse(self.h.scope['_init_armed'])

    def test_pre_init_inserts_before_native_copy_and_verifies_then_restores(self):
        tree, args = self.init_fixture()
        definition_before = args.SkillTreeDef
        self.h.call('arm_init_node')
        self.assertIsNone(self.run_pre(tree, args))
        self.assertEqual(tree.Skills, [])  # Only the engine populates its cache.
        self.assertEqual(self.h.names(), ['MorePep', 'UVH_DeathtrapOverclock', 'Myelin'])
        self.assertEqual(self.h.loads, [])  # Assets already available; never force-load.
        self.assertIs(args.SkillTreeDef, definition_before)
        self.simulate_native_initialize(tree)
        self.assertIsNone(self.h.call('_init_post', tree, args, None, lambda: self.fail('native call')))
        self.assertEqual(self.h.hooks, {})
        self.assertTrue(self.h.call('inspect_init_node'))
        self.assertFalse(self.h.scope['_init_armed'])
        self.h.call('cancel_init_node')
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertEqual(self.h.ltier.bCellIsOccupied, [True, False, True])
        self.assertEqual(len(tree.Skills), 3)  # No manual cache/index edits; restart is explicit.
        self.assertTrue(all(entry.Grade == 0 for entry in tree.Skills))
        self.assertIsNone(self.h.scope['_uvh_node_state'])
        self.h.call('arm_init_node')
        self.assertFalse(self.h.scope['_init_armed'])  # One consumed experiment per restart.

    def test_pre_init_fails_closed_on_network_ownership_assets_and_shape(self):
        for failure in ('network', 'unknown_network', 'owner', 'pawn', 'tree_class',
                        'tree_path', 'existing_cache', 'layout_pointer', 'tiers', 'foreign_skills'):
            with self.subTest(failure=failure):
                self.h = Harness()
                tree, args = self.init_fixture()
                self.h.call('arm_init_node')
                if failure == 'network': self.h.pc.WorldInfo.NetMode = 1
                elif failure == 'unknown_network': self.h.pc.WorldInfo = None
                elif failure == 'owner': tree.Outer = Obj('OtherController')
                elif failure == 'pawn': self.h.pc.Pawn = Obj('Pawn')
                elif failure == 'tree_class': tree.Class.Name = 'OtherTree'
                elif failure == 'tree_path': args.SkillTreeDef._path_name = lambda: 'GD_Other.Tree'
                elif failure == 'existing_cache': tree.Branches = [object()]
                elif failure == 'layout_pointer': self.h.branch.Layout = Obj('OtherLayout')
                elif failure == 'tiers': self.h.branch.Tiers = self.h.branch.Tiers[:1]
                elif failure == 'foreign_skills': self.h.btier.Skills = [self.h.last, self.h.first]
                before = list(self.h.btier.Skills)
                self.assertIsNone(self.run_pre(tree, args))
                self.assertEqual(list(self.h.btier.Skills), before)
                self.assertEqual(self.h.constructed, [])
                self.h.call('_init_post', tree, args, None, None)
                self.assertEqual(self.h.hooks, {})

    def test_solo_host_mode_two_reaches_insertion_with_both_rosters_verified(self):
        tree, args = self.init_fixture()
        self.h.pc.WorldInfo.NetMode = NetMode.NM_ListenServer
        self.h.call('arm_init_node')
        self.assertIsNone(self.run_pre(tree, args))
        self.assertEqual(self.h.names(), ['MorePep', 'UVH_DeathtrapOverclock', 'Myelin'])
        self.simulate_native_initialize(tree)
        self.h.call('_init_post', tree, args, None, None)
        self.assertTrue(self.h.call('inspect_init_node'))
        self.assertTrue(any('SESSION role=listen_host local_players=1 roster_players=1' in x for x in self.h.logs))
        self.assertEqual(self.h.hooks, {})
        self.h.call('cancel_init_node')
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])

    def test_session_gate_rejects_peers_missing_rosters_wrong_identity_and_unknown_enum(self):
        for failure in ('client', 'dedicated', 'bool', 'float', 'unknown_mode', 'enum_missing',
                        'local_missing', 'local_empty', 'local_peer', 'local_wrong',
                        'gri_missing', 'roster_missing', 'roster_empty', 'roster_peer',
                        'roster_wrong', 'own_pri_missing', 'pri_wrong_owner', 'roster_read_error'):
            with self.subTest(failure=failure):
                self.h = Harness()
                tree, args = self.init_fixture()
                self.h.pc.WorldInfo.NetMode = NetMode.NM_ListenServer
                if failure == 'client': self.h.pc.WorldInfo.NetMode = NetMode.NM_Client
                elif failure == 'dedicated': self.h.pc.WorldInfo.NetMode = NetMode.NM_DedicatedServer
                elif failure == 'bool': self.h.pc.WorldInfo.NetMode = False
                elif failure == 'float': self.h.pc.WorldInfo.NetMode = 2.0
                elif failure == 'unknown_mode': self.h.pc.WorldInfo.NetMode = 99
                elif failure == 'enum_missing': self.h.sdk.find_enum = lambda _: None
                elif failure == 'local_missing': del self.h.engine.GamePlayers
                elif failure == 'local_empty': self.h.engine.GamePlayers = []
                elif failure == 'local_peer': self.h.engine.GamePlayers = [Obj('Local', Actor=self.h.pc), Obj('Peer')]
                elif failure == 'local_wrong': self.h.engine.GamePlayers = [Obj('Local', Actor=Obj('Other'))]
                elif failure == 'gri_missing': self.h.pc.WorldInfo.GRI = None
                elif failure == 'roster_missing': del self.h.pc.WorldInfo.GRI.PRIArray
                elif failure == 'roster_empty': self.h.pc.WorldInfo.GRI.PRIArray = []
                elif failure == 'roster_peer': self.h.pc.WorldInfo.GRI.PRIArray = [self.h.pc.PlayerReplicationInfo, Obj('PeerPRI')]
                elif failure == 'roster_wrong': self.h.pc.WorldInfo.GRI.PRIArray = [Obj('OtherPRI', Owner=self.h.pc)]
                elif failure == 'own_pri_missing': self.h.pc.PlayerReplicationInfo = None
                elif failure == 'pri_wrong_owner': self.h.pc.PlayerReplicationInfo.Owner = Obj('OtherPC')
                elif failure == 'roster_read_error':
                    class Unreadable:
                        def __len__(self): raise RuntimeError('loading roster unavailable')
                    self.h.pc.WorldInfo.GRI.PRIArray = Unreadable()
                self.h.call('arm_init_node')
                self.assertIsNone(self.run_pre(tree, args))
                self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
                self.assertEqual(self.h.constructed, [])
                self.assertEqual(self.h.loads, [])
                self.assertTrue(any('ABORT:' in line for line in self.h.logs))
                self.h.call('_init_post', tree, args, None, None)
                self.assertEqual(self.h.hooks, {})

    def test_session_enum_values_are_resolved_from_sdk_metadata(self):
        # Do not silently rely on the numeric value from the previous failing guard.
        self.h.sdk.find_enum = lambda _: types.SimpleNamespace(NM_Standalone=7, NM_ListenServer=9)
        self.h.pc.WorldInfo.NetMode = 9
        self.assertTrue(self.h.call('_init_solo_session', self.h.pc))
        self.h.pc.WorldInfo.NetMode = 2
        self.assertFalse(self.h.call('_init_solo_session', self.h.pc))
        self.assertEqual(self.h.constructed, [])

    def test_new_peer_before_post_causes_owned_native_rollback_and_hook_cleanup(self):
        tree, args = self.init_fixture()
        self.h.pc.WorldInfo.NetMode = NetMode.NM_ListenServer
        self.h.call('arm_init_node')
        self.run_pre(tree, args)
        self.simulate_native_initialize(tree)
        self.h.pc.WorldInfo.GRI.PRIArray = [self.h.pc.PlayerReplicationInfo, Obj('PeerPRI')]
        self.h.call('_init_post', tree, args, None, None)
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertIsNone(self.h.scope['_uvh_node_state'])
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(len(tree.Skills), 3)  # Cache still requires restart.

    def test_check_after_loading_roster_abort_reports_current_session_without_inserting(self):
        tree, args = self.init_fixture()
        self.h.pc.WorldInfo.NetMode = NetMode.NM_ListenServer
        own_pri = self.h.pc.PlayerReplicationInfo
        self.h.pc.WorldInfo.GRI.PRIArray = []
        self.h.call('arm_init_node')
        self.run_pre(tree, args)
        self.h.call('_init_post', tree, args, None, None)
        self.h.pc.WorldInfo.GRI.PRIArray = WrappedArray([own_pri])
        self.h.logs.clear()
        self.assertFalse(self.h.call('inspect_init_node'))
        self.assertTrue(any('No initialization insertion recorded' in x for x in self.h.logs))
        self.assertTrue(any('roster_players=1 local_matches=True roster_matches=True' in x for x in self.h.logs))
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertEqual(self.h.constructed, [])
        self.assertEqual(self.h.hooks, {})

    def test_pre_init_ignores_other_class_and_arm_refuses_loaded_player_tree(self):
        tree, args = self.init_fixture()
        self.h.call('arm_init_node')
        self.h.pc.PlayerClass.Name = 'CharClass_Siren'
        self.run_pre(tree, args)
        self.assertTrue(self.h.scope['_init_armed'])
        self.assertEqual(self.h.constructed, [])
        self.h.call('cancel_init_node')
        self.h.pc.PlayerSkillTree = tree
        self.h.call('arm_init_node')
        self.assertEqual(self.h.hooks, {})

    def test_init_setup_failure_removes_partial_hook_registration(self):
        self.h.fail_add_at = 2
        self.h.call('arm_init_node')
        self.assertFalse(self.h.scope['_init_armed'])
        self.assertEqual(self.h.hooks, {})

    def test_init_runtime_missing_node_rolls_native_arrays_back(self):
        tree, args = self.init_fixture()
        self.h.call('arm_init_node')
        self.run_pre(tree, args)
        tree.Skills = [types.SimpleNamespace(Definition=self.h.first),
                       types.SimpleNamespace(Definition=self.h.last)]
        self.h.call('_init_post', tree, args, None, None)
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertIsNone(self.h.scope['_uvh_node_state'])
        self.assertEqual(self.h.hooks, {})

    def test_init_partial_write_failure_retains_snapshot_when_restore_fails(self):
        tree, args = self.init_fixture()
        real_set = self.h.scope['_node_set_array']
        def fail_layout(owner, prop, values):
            if prop == 'bCellIsOccupied':
                return False, 'simulated write and rollback failure'
            return real_set(owner, prop, values)
        self.h.scope['_node_set_array'] = fail_layout
        self.h.call('arm_init_node')
        self.run_pre(tree, args)
        record = self.h.scope['_uvh_node_state']
        self.assertIsNotNone(record)
        self.assertTrue(record['restore_failed'])
        self.h.scope['_node_set_array'] = real_set
        self.h.call('cancel_init_node')
        self.assertIsNone(self.h.scope['_uvh_node_state'])
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])

    def test_init_rollback_preserves_independent_edits(self):
        tree, args = self.init_fixture()
        self.h.call('arm_init_node')
        self.run_pre(tree, args)
        self.h.btier.Skills = [self.h.last, self.h.first]
        self.h.call('cancel_init_node')
        self.assertEqual(self.h.names(), ['Myelin', 'MorePep'])
        self.assertIsNotNone(self.h.scope['_uvh_node_state'])

    def test_candidate_existing_name_or_unreadable_effects_never_overwritten(self):
        existing = Obj('UVH_DeathtrapOverclock', 'SkillDefinition', SkillName='foreign')
        self.h.objects['GD_Tulip_Mechromancer_Skills.LittleBigTrouble.UVH_DeathtrapOverclock'] = existing
        self.assertIsNone(self.h.call('_node_make_candidate', self.h.branch))
        self.assertEqual(existing.SkillName, 'foreign')
        self.h.objects.pop('GD_Tulip_Mechromancer_Skills.LittleBigTrouble.UVH_DeathtrapOverclock')
        self.h.sdk.construct_object = lambda *args: Obj('UVH_DeathtrapOverclock', 'SkillDefinition')
        self.assertIsNone(self.h.call('_node_make_candidate', self.h.branch))

    def test_live_dump_does_not_follow_controller_listeners(self):
        tree = Obj('PlayerSkillTree_0', 'PlayerSkillTree', SkillTreeListeners=WrappedArray([self.h.pc]))
        self.h.call('_diag_dump_live', 'Tree', tree)
        self.assertFalse(any('SkillTreeListeners[0]' in line for line in self.h.logs))

    def test_trace_accepts_colon_and_dot_paths_and_rejects_nested_or_foreign(self):
        colon = MetadataFunction('PlayerSkillTree', 'Initialize')
        dotted = MetadataFunction('PlayerSkillTree', 'Initialize', separator='.')
        self.h.functions = [colon, dotted]
        self.assertEqual(self.h.call('_trace_candidates'), ['WillowGame.PlayerSkillTree:Initialize'])
        for path in ('OtherGame.PlayerSkillTree:Initialize',
                     'WillowGame.PlayerSkillTree:SomeState.Initialize',
                     'WillowGame.PlayerSkillTree.SomeState.Initialize'):
            colon.path = path
            self.assertIsNone(self.h.call('_trace_hook_path', colon))

    def test_live_tree_reads_nested_wrappers_without_calling_native_methods(self):
        node = types.SimpleNamespace(SkillDefinition=self.h.first, Grade=0)
        tier = types.SimpleNamespace(Skills=WrappedArray([node]))
        tree = Obj('PlayerSkillTree_0', 'PlayerSkillTree',
                   Branches=WrappedArray([types.SimpleNamespace(Tiers=WrappedArray([tier]),
                                                              Definition=self.h.branch)]))
        tree.Owner = self.h.pc
        tree.Initialize = lambda: self.fail('native call forbidden')
        self.h.pc.PlayerSkillTree = tree
        self.h.call('inspect_tree_loading')
        self.assertTrue(any('PlayerSkillTree.Branches[0].Tiers[0]' in line for line in self.h.logs))
        self.assertTrue(any('PlayerSkillTree.Branches[0].Tiers[0].Skills[0].Grade = 0' in line
                            for line in self.h.logs))
        self.assertEqual(node.Grade, 0)
        self.assertEqual(self.h.loads, [])
        self.assertEqual(self.h.constructed, [])
        self.assertEqual(self.h.hooks, {})

    def test_live_tree_budget_cycles_and_unexpected_class_fail_closed(self):
        tree = Obj('PlayerSkillTree_0', 'PlayerSkillTree')
        tree.SelfReference = tree
        tree.Skills = WrappedArray([types.SimpleNamespace(Grade=i) for i in range(100)])
        self.h.pc.PlayerSkillTree = tree
        self.h.call('_diag_dump_live', 'Tree', tree, 10, [8])
        self.assertLess(len(self.h.logs), 25)
        tree.Class = types.SimpleNamespace(Name='OtherTree')
        self.h.logs.clear()
        self.h.call('_diag_player_tree', self.h.pc)
        self.assertTrue(any('Unexpected player tree class' in line for line in self.h.logs))
        self.assertFalse(any('fields=' in line for line in self.h.logs))

    def test_snapshots_work_with_missing_assets_and_no_controller(self):
        self.h.objects.clear()
        self.h.pc = None
        self.h.call('inspect_tree_loading')
        self.assertTrue(any('TroubleBranch found=False' in x for x in self.h.logs))
        self.assertEqual(self.h.loads, [])
        self.assertEqual(self.h.constructed, [])
        self.assertEqual(self.h.hooks, {})

    def test_snapshot_reads_wrapped_arrays_and_never_invokes_game_functions(self):
        entry = Obj('UIEntry', Branch=self.h.branch, Layout=self.h.layout)
        self.h.pc.SkillTreeBranches = WrappedArray([entry])
        self.h.pc.InitializeSkillTree = lambda: self.fail('native call forbidden')
        self.h.btier.Skills = WrappedArray([self.h.first, self.h.last])
        self.h.ltier.bCellIsOccupied = WrappedArray([True, False, True])
        self.h.call('inspect_tree_loading')
        self.assertTrue(any('SkillTreeBranches[0].Branch' in x for x in self.h.logs))
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertEqual(list(self.h.ltier.bCellIsOccupied), [True, False, True])
        self.assertEqual(self.h.loads, [])
        self.assertEqual(self.h.constructed, [])

    def test_observers_are_explicit_discovered_bounded_and_removable(self):
        self.h.functions.extend([MetadataFunction('WillowPlayerController', 'BuySkill'),
                                 MetadataFunction('Unrelated', 'Initialize')])
        self.h.call('start_tree_trace')
        self.assertEqual(len(self.h.hooks), 2)
        for key in self.h.hooks:
            self.assertIn('InitializeSkillTree', key[0])
        self.h.call('start_tree_trace')
        self.assertEqual(len(self.h.hooks), 2)
        for key in list(self.h.hooks):
            for _ in range(5):
                self.assertIsNone(self.h.fire(key))
        self.assertEqual(self.h.scope['_trace_events'], 4)
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertEqual(self.h.loads, [])
        self.assertEqual(self.h.constructed, [])
        self.h.call('stop_tree_trace')
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.scope['_trace_hooks'], [])

    def test_trace_has_global_cap_and_no_args_or_return_override(self):
        self.h.functions = [MetadataFunction('WillowPlayerController', 'InitializeSkillTree' + str(i))
                            for i in range(20)]
        self.h.call('start_tree_trace')
        self.assertEqual(len(self.h.hooks), 16)
        args = types.SimpleNamespace(SkillTree=self.h.branch, ReturnValue=123)
        for key in list(self.h.hooks):
            for _ in range(3):
                self.assertIsNone(self.h.fire(key, args=args))
        self.assertEqual(self.h.scope['_trace_events'], 24)
        self.assertIs(args.SkillTree, self.h.branch)
        self.assertEqual(args.ReturnValue, 123)
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])

    def test_trace_setup_failure_cleans_partial_registration(self):
        self.h.fail_add_at = 2
        self.h.call('start_tree_trace')
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.scope['_trace_hooks'], [])

    def test_removal_failure_is_retained_for_retry_and_disable_cleanup(self):
        self.h.call('start_tree_trace')
        self.h.fail_remove = True
        self.h.call('stop_tree_trace')
        self.assertEqual(len(self.h.scope['_trace_hooks']), 2)
        self.h.fail_remove = False
        with patch.dict(sys.modules, {'unrealsdk': self.h.sdk}):
            self.h.mod_options['on_disable']()
        self.assertEqual(self.h.hooks, {})

    def test_no_candidates_is_a_diagnostic_result(self):
        self.h.functions.clear()
        self.h.call('start_tree_trace')
        self.assertEqual(self.h.hooks, {})
        self.assertTrue(any('No usable initialization functions' in x for x in self.h.logs))

    def test_legacy_missing_assets_fail_closed_with_specific_reason(self):
        self.h.objects.pop(LAYOUT)
        self.h.call('add_overclock_node')
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertEqual(self.h.constructed, [])
        self.assertTrue(any('Missing assets: branch=' in x and 'layout=<missing>' in x
                            for x in self.h.logs))

    def test_legacy_insertion_duplicate_check_and_rollback(self):
        self.h.call('add_overclock_node')
        self.assertEqual(self.h.names(), ['MorePep', 'UVH_DeathtrapOverclock', 'Myelin'])
        self.assertEqual(self.h.ltier.bCellIsOccupied, [True, True, True])
        self.assertEqual(self.h.constructed[0].SkillEffectDefinitions, [])
        self.h.call('add_overclock_node')
        self.assertEqual(len(self.h.constructed), 1)
        self.h.pc.Pawn = Obj('Pawn_0')
        self.h.call('check_overclock_preload')
        self.h.call('remove_overclock_node')
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertEqual(self.h.ltier.bCellIsOccupied, [True, False, True])
        self.assertIsNone(self.h.scope['_uvh_node_state'])

    def test_legacy_refuses_loaded_character_and_foreign_tree(self):
        self.h.pc.Pawn = Obj('Pawn_0')
        self.h.call('add_overclock_node')
        self.assertEqual(self.h.loads, [])
        self.h.pc.Pawn = None
        self.h.btier.Skills = [self.h.last, self.h.first]
        self.h.call('add_overclock_node')
        self.assertEqual(self.h.names(), ['Myelin', 'MorePep'])
        self.assertEqual(self.h.constructed, [])

    def test_legacy_rollback_after_partial_layout_write_failure(self):
        real_set = self.h.scope['_node_set_array']
        def fail_new_layout(owner, prop, values):
            if prop == 'bCellIsOccupied' and values == [True, True, True]:
                return False, 'simulated failure'
            return real_set(owner, prop, values)
        self.h.scope['_node_set_array'] = fail_new_layout
        self.h.call('add_overclock_node')
        self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
        self.assertEqual(self.h.ltier.bCellIsOccupied, [True, False, True])

    def test_manual_duration_boost_remains_75_nonstacking_and_restorable(self):
        self.h.pc.Pawn = Obj('Pawn_0', MyActionSkill=Obj('Action', 'DeathtrapActionSkill'))
        skill = Obj('LiveDeathtrap', Definition=Obj('Skill_DeathTrap'),
                    SkillInstigator=self.h.pc, Duration=60.0, DurationBaseValue=60.0,
                    ActivatedTime=12.0, DurationModifierStack=[])
        self.h.pc.GetSkillManager = lambda: types.SimpleNamespace(ActiveSkills=WrappedArray([skill]))
        self.h.call('apply')
        self.assertEqual(skill.Duration, 75.0)
        self.assertEqual(skill.DurationBaseValue, 60.0)
        self.h.call('apply')
        self.assertEqual(skill.Duration, 75.0)
        self.h.call('restore')
        self.assertEqual(skill.Duration, 60.0)


if __name__ == '__main__':
    unittest.main()
