"""Read-only presentation snapshots with SDK metadata mocks, not engine proof."""
import types
import unittest
from unittest.mock import patch

import test_upgrade_observers as upgrade_tests
from test_runtime_mock import Obj, WrappedArray


class PresentationTests(unittest.TestCase):
    def setUp(self):
        fixture = upgrade_tests.UpgradeObserverTests()
        fixture.setUp()
        self.h, self.tree, self.node = fixture.h, fixture.tree, fixture.node
        self.h.sdk.unreal = types.SimpleNamespace(UClass=Obj, UObject=Obj, WrappedArray=WrappedArray)
        self.presentation_class = Obj('AttributePresentationDefinition', 'Class')
        self.skill_class = Obj('SkillDefinition', 'Class')
        self.inner = self.prop('Inner', 'ObjectProperty', 0, PropertyClass=self.presentation_class)
        self.array_prop = self.prop('SkillEffectPresentations', 'ArrayProperty', 120,
                                   Inner=self.inner, Outer=self.skill_class)
        self.lookup_count = 0
        def lookup(field):
            self.lookup_count += 1
            self.assertEqual(field, 'SkillEffectPresentations')
            return self.array_prop
        self.skill_class._find_prop = lookup
        self.fields = [self.prop('Description', 'StrProperty', 0),
                       self.prop('Attribute', 'ObjectProperty', 4, PropertyClass=Obj('AttributeDefinition'))]
        self.presentation_class._properties = lambda: iter(self.fields)
        for definition, count in ((self.node, 0), (self.h.first, 4), (self.h.last, 2)):
            definition.Class = self.skill_class
            definition.SkillEffectPresentations = WrappedArray([self.entry(str(i)) for i in range(count)])
        self.h.logs.clear()

    def prop(self, label, kind, offset, **fields):
        metadata = dict(PropertyFlags=0, Offset_Internal=offset, ArrayDim=1)
        metadata.update(fields)
        return Obj(label, kind, **metadata)

    def entry(self, label='0', path=None):
        class Presentation(Obj):
            @property
            def Description(self):
                raise AssertionError('presentation instance values were read')
            @property
            def Attribute(self):
                raise AssertionError('gameplay attribute was traversed')
        entry = Presentation('Presentation_' + label, Class=self.presentation_class)
        entry._path_name = lambda: path if path is not None else 'GD_Test.Skill:Presentation_' + label
        return entry

    def snapshot(self):
        return self.h.call('inspect_overclock_presentations')

    def test_three_arrays_metadata_and_actual_empty_count_are_observed_without_writes(self):
        arrays = (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied))
        def forbidden(*args, **kwargs):
            self.fail('snapshot invoked a native function, discovery or mutation')
        self.h.sdk.find_object = self.h.sdk.find_all = self.h.sdk.construct_object = self.h.sdk.load_package = forbidden
        self.h.sdk.hooks.add_hook = self.h.sdk.hooks.remove_hook = forbidden
        self.h.scope['_node_set_array'] = forbidden
        for owner in (self.h.pc, self.tree, self.node, self.h.first, self.h.last):
            for method in ('GetSkillState', 'UpgradeSkill', 'GetSkillUpgradeCost', 'SetSkillGrade',
                           'SaveSkillSaveGameData', 'GetSkillEffectPresentations', 'GetHumanReadableSkillEffects'):
                setattr(owner, method, forbidden)
        # Native methods above are poison fixture additions, not snapshot changes.
        before = [dict(obj.__dict__) for obj in (self.h.pc, self.tree, self.node, self.h.first, self.h.last,
                                                self.array_prop, self.inner, self.presentation_class)]
        self.assertTrue(self.snapshot())
        self.assertEqual(before, [dict(obj.__dict__) for obj in (self.h.pc, self.tree, self.node, self.h.first, self.h.last,
                                                              self.array_prop, self.inner, self.presentation_class)])
        self.assertEqual(arrays, (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied)))
        self.assertEqual(self.lookup_count, 3)
        self.assertEqual(sum('[UVH-PRESENT] REFERENCE' in line for line in self.h.logs), 6)
        self.assertEqual(sum('[UVH-PRESENT] PROPERTY' in line for line in self.h.logs), 2)
        self.assertTrue(any('skill=UVH_DeathtrapOverclock array=VERIFIED count=0 references=0/0' in line for line in self.h.logs))
        self.assertTrue(any('FINAL points=(5, 0) ranks=(0, 0, 0) unchanged_from_start=True' in line for line in self.h.logs))
        self.assertTrue(any('verified_arrays=3/3 observers_added=0' in line for line in self.h.logs))
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.loads, [])

    def test_factory_routes_button_four_to_focused_snapshot_and_keeps_nineteen_options(self):
        options = self.h.mod_options['options']
        option = next(option for option in options if option['display_name'].startswith('4 -'))
        self.assertIs(option['on_press'], self.h.scope['inspect_deathtrap_readiness'])
        self.assertEqual(len(options), 19)
        self.assertEqual(self.h.mod_options['version'], '0.2.14')

    def test_unverified_session_tree_rank_points_or_inertness_refuses_before_metadata(self):
        changes = [lambda: setattr(self.h.pc, 'PlayerSkillTree', Obj('ForeignTree')),
                   lambda: setattr(self.tree, 'Outer', Obj('ForeignController')),
                   lambda: setattr(self.h.pc, 'Pawn', None),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', None),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'SpecialistSkillPoints', True),
                   lambda: setattr(self.tree.Skills[1], 'Grade', 1),
                   lambda: setattr(self.tree.Skills[0], 'Owner', Obj('ForeignTree')),
                   lambda: setattr(self.tree.Skills[2], 'Index', 0),
                   lambda: setattr(self.h.pc.WorldInfo, 'NetMode', 3),
                   lambda: setattr(self.h.pc.WorldInfo.GRI, 'PRIArray', WrappedArray([self.h.pc.PlayerReplicationInfo, Obj('Peer')])),
                   lambda: setattr(self.h.engine, 'GamePlayers', WrappedArray([])),
                   lambda: self.node.SkillEffectDefinitions.append(Obj('Effect')),
                   lambda: self.h.scope.update(_uvh_node_state=None),
                   lambda: setattr(self.h.sdk, 'find_enum', lambda _: None)]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                change()
                self.assertFalse(self.snapshot())
                self.assertEqual(self.lookup_count, 0)
                self.assertFalse(any('[UVH-PRESENT] ARRAY ' in line for line in self.h.logs))
                self.assertEqual(self.h.hooks, {})

    def test_active_or_failed_observers_refuse_without_changing_them(self):
        for field in ('_init_hooks', '_trace_hooks', '_upgrade_hooks', '_ui_hooks', '_skillstate_hooks',
                      '_init_armed', '_upgrade_context', '_ui_context', '_skillstate_context'):
            with self.subTest(field=field):
                self.setUp()
                token = object() if field.endswith('context') else [('other', 'pre', 'other')]
                self.h.scope[field] = token
                self.assertFalse(self.snapshot())
                self.assertIs(self.h.scope[field], token)
                self.assertEqual(self.lookup_count, 0)

    def test_invalid_array_metadata_never_reads_payloads_or_reports_empty(self):
        changes = [lambda: setattr(self.array_prop.Class, 'Name', 'StructProperty'),
                   lambda: setattr(self.inner.Class, 'Name', 'StructProperty'),
                   lambda: setattr(self.array_prop, 'Outer', Obj('OtherClass')),
                   lambda: setattr(self.array_prop, 'Name', 'OtherArray'),
                   lambda: setattr(self.array_prop, 'ArrayDim', True),
                   lambda: setattr(self.inner, 'ArrayDim', 2),
                   lambda: setattr(self.array_prop, 'PropertyFlags', 128),
                   lambda: setattr(self.inner, 'PropertyFlags', True),
                   lambda: setattr(self.inner, 'Offset_Internal', -1),
                   lambda: setattr(self.array_prop, 'Offset_Internal', True),
                   lambda: setattr(self.presentation_class, 'Name', 'OtherDefinition'),
                   lambda: setattr(self.inner, 'PropertyClass', None),
                   lambda: setattr(self.skill_class, '_find_prop', lambda _: None)]
        def poison(_):
            self.fail('payload was read before validating metadata')
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                change()
                with patch.object(Obj, 'SkillEffectPresentations', property(poison), create=True):
                    self.assertFalse(self.snapshot())
                self.assertEqual(sum('array=UNAVAILABLE' in line for line in self.h.logs), 3)
                self.assertFalse(any('[UVH-PRESENT] ARRAY ' in line for line in self.h.logs))
                self.assertTrue(any('FINAL' in line and 'unchanged_from_start=True' in line for line in self.h.logs))

    def test_missing_property_or_array_wrapper_is_unavailable_not_zero(self):
        for value in (None, [], [self.entry()], object()):
            with self.subTest(value=type(value)):
                self.setUp()
                self.node.SkillEffectPresentations = value
                self.assertFalse(self.snapshot())
                self.assertTrue(any('skill=UVH_DeathtrapOverclock array=UNAVAILABLE' in line for line in self.h.logs))
                self.assertFalse(any('ARRAY skill=UVH_DeathtrapOverclock count=0' in line for line in self.h.logs))
                self.assertTrue(any('verified_arrays=2/3' in line for line in self.h.logs))
        self.setUp()
        del self.node.SkillEffectPresentations
        self.assertFalse(self.snapshot())

    def test_reference_class_is_checked_before_sdk_path_helper(self):
        for entry in (None, object(), Obj('Wrong', Class=Obj('OtherClass')),
                      Obj('WrongIdentity', Class=Obj('AttributePresentationDefinition', 'Class'))):
            with self.subTest(entry=type(entry)):
                self.setUp()
                if isinstance(entry, Obj):
                    entry._path_name = lambda: self.fail('unverified object identity helper called')
                self.node.SkillEffectPresentations = WrappedArray([entry])
                self.assertFalse(self.snapshot())
                self.assertFalse(any('REFERENCE skill=UVH_DeathtrapOverclock' in line for line in self.h.logs))

    def test_shared_presentation_reference_is_allowed_without_owner_graph_traversal(self):
        entry = self.entry()
        entry.Outer = Obj('SharedPackage')
        self.node.SkillEffectPresentations = WrappedArray([entry])
        self.assertTrue(self.snapshot())
        self.assertTrue(any('REFERENCE skill=UVH_DeathtrapOverclock' in line for line in self.h.logs))

    def test_paths_are_bounded_typed_and_not_formatted_as_object_graphs(self):
        for path in ('', None, 4, 'x' * 385):
            with self.subTest(path=type(path)):
                self.setUp()
                entry = self.entry()
                entry._path_name = lambda path=path: path
                self.node.SkillEffectPresentations = WrappedArray([entry])
                self.assertFalse(self.snapshot())
        self.setUp()
        self.node.SkillEffectPresentations = WrappedArray([self.entry(path='Native.Path\nExtra')])
        self.assertTrue(self.snapshot())
        line = next(line for line in self.h.logs if 'REFERENCE skill=UVH_DeathtrapOverclock' in line)
        self.assertIn('\\n', line)
        self.assertNotIn('\n', line)

    def test_reference_and_metadata_caps_do_not_read_extra_entries_or_values(self):
        reads, fields = [], []
        class CountedArray(WrappedArray):
            def __getitem__(this, index):
                reads.append(index)
                return super().__getitem__(index)
        self.node.SkillEffectPresentations = CountedArray([self.entry(str(i)) for i in range(20)])
        def reflected():
            for i in range(1000):
                fields.append(i)
                yield self.prop('Field' + str(i), 'ObjectProperty', i * 4)
        self.presentation_class._properties = reflected
        self.assertTrue(self.snapshot())
        self.assertEqual(reads, [0, 1, 2, 3])
        self.assertEqual(fields, list(range(17)))  # one bounded lookahead, no descriptor reads past 16
        self.assertEqual(sum('[UVH-PRESENT] PROPERTY' in line for line in self.h.logs), 16)
        self.assertTrue(any('count=20 references=4/20 metadata=CAPPED' in line for line in self.h.logs))

    def test_oversized_or_unreadable_array_refuses_before_reference_sampling(self):
        class HugeArray(WrappedArray):
            def __len__(self):
                return 257
            def __getitem__(self, index):
                raise AssertionError('oversized array entries were read')
        self.node.SkillEffectPresentations = HugeArray([])
        self.assertFalse(self.snapshot())
        self.assertTrue(any('size exceeds 256' in line for line in self.h.logs))
        class UnreadableArray(HugeArray):
            def __len__(self):
                raise RuntimeError('unavailable array')
        self.node.SkillEffectPresentations = UnreadableArray([])
        self.assertFalse(self.snapshot())

    def test_metadata_failure_does_not_guess_fields_or_invalidate_verified_counts(self):
        def broken():
            raise RuntimeError('reflection unavailable')
        for fields in (None, [self.prop('Duplicate', 'StrProperty', 0)] * 2,
                       [self.prop('BadOffset', 'StrProperty', -1)],
                       [self.prop('BadFlags', 'StrProperty', 0, PropertyFlags=True)]):
            with self.subTest(fields=fields):
                self.setUp()
                self.presentation_class._properties = broken if fields is None else lambda: iter(fields)
                self.assertTrue(self.snapshot())
                self.assertTrue(any('METADATA UNAVAILABLE' in line for line in self.h.logs))
                self.assertEqual(sum('metadata=UNAVAILABLE' in line for line in self.h.logs), 3)
                self.assertTrue(any('verified_arrays=3/3' in line for line in self.h.logs))

    def test_changed_state_during_metadata_aborts_before_first_array_read(self):
        original = self.skill_class._find_prop
        def change(field):
            self.h.pc.PlayerReplicationInfo.GeneralSkillPoints -= 1
            return original(field)
        self.skill_class._find_prop = change
        def poison(_):
            self.fail('array read after points changed')
        with patch.object(Obj, 'SkillEffectPresentations', property(poison), create=True):
            self.assertFalse(self.snapshot())
        self.assertEqual(self.lookup_count, 1)
        self.assertFalse(any('[UVH-PRESENT] ARRAY ' in line for line in self.h.logs))
        self.assertFalse(any('FINAL' in line and 'unchanged_from_start=True' in line for line in self.h.logs))
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 4)  # never repaired

    def test_changed_state_during_reference_sampling_aborts_before_next_entry(self):
        reads = []
        class ChangingArray(WrappedArray):
            def __getitem__(this, index):
                reads.append(index)
                self.tree.Skills[2].Grade = 1
                return super().__getitem__(index)
        self.node.SkillEffectPresentations = ChangingArray([self.entry(str(i)) for i in range(4)])
        self.assertFalse(self.snapshot())
        self.assertEqual(reads, [0])
        self.assertEqual(self.tree.Skills[2].Grade, 1)
        self.assertFalse(any('SCHEMA skill=MorePep' in line for line in self.h.logs))
        self.assertFalse(any('REFERENCE skill=UVH_DeathtrapOverclock' in line for line in self.h.logs))
        self.assertFalse(any('unchanged_from_start=True' in line for line in self.h.logs))

    def test_changed_array_length_is_partial_not_a_verified_sample(self):
        class ChangingArray(WrappedArray):
            def __getitem__(this, index):
                value = super().__getitem__(index)
                this.values += (self.entry('extra'),)
                return value
        self.node.SkillEffectPresentations = ChangingArray([self.entry()])
        self.assertFalse(self.snapshot())
        self.assertTrue(any('array length/definition class changed' in line for line in self.h.logs))
        self.assertTrue(any('verified_arrays=2/3' in line for line in self.h.logs))

    def test_cancel_and_disable_still_restore_the_native_patch_without_extra_hooks(self):
        for method in ('cancel_init_node', 'shutdown'):
            with self.subTest(method=method):
                self.setUp()
                self.assertTrue(self.snapshot())
                self.h.call(method)
                self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
                self.assertEqual(self.h.ltier.bCellIsOccupied, [True, False, True])
                self.assertEqual(self.h.hooks, {})
                self.assertIsNone(self.h.scope['_uvh_node_state'])

    def test_non_sdk_class_metadata_refuses_before_array_lookup(self):
        foreign = types.SimpleNamespace(Name='SkillDefinition')
        for definition in (self.node, self.h.first, self.h.last):
            definition.Class = foreign
        self.assertFalse(self.snapshot())
        self.assertEqual(self.lookup_count, 0)
        self.assertEqual(sum('array=UNAVAILABLE' in line for line in self.h.logs), 3)

    def test_changed_element_class_metadata_refuses_before_next_target_payload(self):
        original = self.skill_class._find_prop
        foreign = Obj('AttributePresentationDefinition', 'Class')
        def lookup(field):
            prop = original(field)
            if self.lookup_count > 1:
                prop.Inner.PropertyClass = foreign
            return prop
        self.skill_class._find_prop = lookup
        reads = []
        class PoisonArray(WrappedArray):
            def __len__(self):
                reads.append('len')
                raise AssertionError('changed element class payload was read')
        self.h.first.SkillEffectPresentations = PoisonArray([])
        self.h.last.SkillEffectPresentations = PoisonArray([])
        self.assertFalse(self.snapshot())
        self.assertEqual(reads, [])
        self.assertEqual(sum('element class differs between targets' in line for line in self.h.logs), 2)
        self.assertTrue(any('verified_arrays=1/3' in line for line in self.h.logs))


if __name__ == '__main__':
    unittest.main()
