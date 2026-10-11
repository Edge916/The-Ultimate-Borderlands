"""Direct text-read simulations; never proof of rendered or gameplay behavior."""
import types
import unittest

import test_presentations as presentation_tests
from test_runtime_mock import Obj, WrappedArray


class PresentationTextTests(unittest.TestCase):
    def setUp(self):
        fixture = presentation_tests.PresentationTests()
        fixture.setUp()
        self.h, self.node, self.tree = fixture.h, fixture.node, fixture.tree
        self.cls, self.array_prop = fixture.presentation_class, fixture.array_prop
        self.skill_class, self.inner = fixture.skill_class, fixture.inner
        self.reads, self.lookups, self.on_lookup = [], [], None
        self.fields = {'Description': 68, 'NoConstraintText': 80, 'Prefix': 104, 'Suffix': 92}
        self.props = {field: Obj(field, 'StrProperty', Outer=self.cls, PropertyFlags=4227075,
                                Offset_Internal=offset, ArrayDim=1) for field, offset in self.fields.items()}
        def lookup(field):
            self.lookups.append(field)
            if self.on_lookup:
                self.on_lookup(field)
            return self.props[field]
        self.cls._find_prop = lookup
        self.entries = []
        for definition, count in ((self.node, 0), (self.h.first, 4), (self.h.last, 2)):
            definition.SkillEffectPresentations = WrappedArray([self.entry(str(i)) for i in range(count)])
        self.h.logs.clear()

    def entry(self, label='one', path='GD_Test.Skill:Presentation'):
        fixture = self
        class Presentation(Obj):
            def __getattribute__(self, field):
                if field in fixture.fields:
                    fixture.reads.append((self.Name, field))
                    callback = self.callbacks.get(field)
                    if callback:
                        callback()
                    value = self.payload[field]
                    if isinstance(value, Exception):
                        raise value
                    return value
                if field in ('Attribute', 'BasePriority', 'bDontDisplayNumber', 'bEnableTextColor'):
                    raise AssertionError('unallowlisted instance value was read')
                return super().__getattribute__(field)
        entry = Presentation('Entry_' + label, Class=self.cls, Outer=Obj('SharedPackage'))
        entry.payload = {'Description': 'Bonus {value}', 'NoConstraintText': '', 'Prefix': '+', 'Suffix': '%'}
        entry.callbacks = {}
        entry._path_name = lambda: path
        self.entries.append(entry)
        return entry

    def one_entry(self):
        entry = self.entry()
        self.node.SkillEffectPresentations = WrappedArray([entry])
        self.h.first.SkillEffectPresentations = WrappedArray([])
        self.h.last.SkillEffectPresentations = WrappedArray([])
        return entry

    def snapshot(self):
        return self.h.call('inspect_overclock_presentation_text')

    def test_all_native_mock_strings_empty_candidate_and_no_writes_or_native_calls(self):
        def forbidden(*args, **kwargs):
            self.fail('native invocation, discovery, hooks, mutation or broad metadata scan')
        self.h.sdk.find_all = self.h.sdk.find_object = self.h.sdk.construct_object = self.h.sdk.load_package = forbidden
        self.h.sdk.hooks.add_hook = self.h.sdk.hooks.remove_hook = forbidden
        self.h.scope['_node_set_array'] = forbidden
        self.cls._properties = forbidden
        objects = [self.h.pc, self.tree, self.node, self.h.first, self.h.last, self.cls, *self.entries, *self.props.values()]
        before = [dict(obj.__dict__) for obj in objects]
        arrays = (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied))
        self.assertTrue(self.snapshot())
        self.assertEqual(before, [dict(obj.__dict__) for obj in objects])
        self.assertEqual(arrays, (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied)))
        self.assertEqual(len(self.reads), 24)
        self.assertEqual(set(field for _, field in self.reads), set(self.fields))
        self.assertEqual(len(self.lookups), 24)
        self.assertTrue(any('count=0 references=0/0 fields=0/0 text=NOT_APPLICABLE' in line for line in self.h.logs))
        self.assertTrue(any('complete_targets=3/3 fields=24/24 observers_added=0' in line for line in self.h.logs))
        self.assertTrue(any('FINAL points=(5, 0) ranks=(0, 0, 0) unchanged_from_start=True' in line for line in self.h.logs))
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.loads, [])

    def test_missing_text_metadata_is_unavailable_before_its_poisoned_payload(self):
        entry = self.one_entry()
        self.props.pop('Description')
        entry.callbacks['Description'] = lambda: self.fail('invalid descriptor allowed a payload read')
        self.assertFalse(self.snapshot())
        self.assertNotIn((entry.Name, 'Description'), self.reads)
        self.assertTrue(any('field=Description status=UNAVAILABLE' in line for line in self.h.logs))
        self.assertTrue(any('fields=3/4 text=PARTIAL' in line for line in self.h.logs))
        self.assertTrue(any('FINAL' in line and 'unchanged_from_start=True' in line for line in self.h.logs))

    def test_exact_descriptor_name_owner_type_flags_offset_and_dimension_before_payload(self):
        changes = [('Name', 'Prefix'), ('Outer', Obj('ForeignClass')),
                   ('Class', types.SimpleNamespace(Name='ObjectProperty')),
                   ('PropertyFlags', 3), ('PropertyFlags', True),
                   ('Offset_Internal', 80), ('Offset_Internal', True),
                   ('ArrayDim', 2), ('ArrayDim', True)]
        for field, value in changes:
            with self.subTest(field=field, value=value):
                self.setUp()
                entry = self.one_entry()
                setattr(self.props['Description'], field, value)
                self.assertFalse(self.snapshot())
                self.assertNotIn((entry.Name, 'Description'), self.reads)
                self.assertTrue(any('field=Description status=UNAVAILABLE' in line for line in self.h.logs))

    def test_non_string_payloads_are_unavailable_without_conversion_or_repr(self):
        class Poison:
            def __repr__(self):
                raise AssertionError('foreign payload repr')
        class Substring(str):
            pass
        for value in (None, False, 0, Poison(), Substring('subclass')):
            with self.subTest(kind=type(value)):
                self.setUp()
                entry = self.one_entry()
                entry.payload['Description'] = value
                self.assertFalse(self.snapshot())
                self.assertTrue(any('field=Description status=UNAVAILABLE' in line for line in self.h.logs))
                self.assertFalse(any('field=Description status=VERIFIED' in line for line in self.h.logs))

    def test_string_getter_failure_is_distinct_from_verified_empty(self):
        entry = self.one_entry()
        entry.payload['Description'] = RuntimeError('unavailable\nsecond line')
        self.assertFalse(self.snapshot())
        failure = next(line for line in self.h.logs if 'field=Description status=UNAVAILABLE' in line)
        self.assertIn('\\n', failure)
        self.assertNotIn('\n', failure)
        self.assertTrue(any("field=NoConstraintText status=VERIFIED length=0 clipped=False text=''" in line for line in self.h.logs))

    def test_strings_are_clipped_escaped_and_templates_not_evaluated(self):
        entry = self.one_entry()
        entry.payload['Description'] = '\n{value}<b>' + 'x' * 1000
        self.assertTrue(self.snapshot())
        line = next(line for line in self.h.logs if 'field=Description status=VERIFIED' in line)
        self.assertIn('length=1011 clipped=True', line)
        self.assertIn('\\n{value}<b>', line)
        self.assertNotIn('\n', line)
        self.assertNotIn('x' * 513, line)
        self.assertEqual(len(entry.payload['Description']), 1011)

    def test_sample_cap_never_indexes_fifth_entry_or_reads_more_than_four_fields(self):
        indices = []
        class Array(WrappedArray):
            def __getitem__(self, index):
                indices.append(index)
                if index >= 4:
                    raise AssertionError('sample cap exceeded')
                return super().__getitem__(index)
        self.node.SkillEffectPresentations = Array([self.entry(str(i)) for i in range(20)])
        self.h.first.SkillEffectPresentations = self.h.last.SkillEffectPresentations = WrappedArray([])
        self.assertTrue(self.snapshot())
        self.assertEqual(set(indices), {0, 1, 2, 3})
        self.assertEqual(len(self.reads), 16)
        self.assertTrue(any('count=20 references=4/20 fields=16/16' in line for line in self.h.logs))

    def test_invalid_session_or_rank_refuses_before_scalar_metadata(self):
        changes = [lambda: setattr(self.h.pc, 'PlayerSkillTree', Obj('Foreign')),
                   lambda: setattr(self.h.pc, 'Pawn', None),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', None),
                   lambda: setattr(self.tree.Skills[1], 'Grade', 1),
                   lambda: setattr(self.h.pc.WorldInfo, 'NetMode', 3),
                   lambda: setattr(self.h.pc.WorldInfo.GRI, 'PRIArray', WrappedArray([Obj('Peer')])),
                   lambda: self.node.SkillEffectDefinitions.append(Obj('Effect'))]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                change()
                self.assertFalse(self.snapshot())
                self.assertEqual(self.lookups, [])
                self.assertEqual(self.reads, [])

    def test_active_or_failed_observer_overlap_refuses_without_removing_hooks(self):
        for field in ('_init_hooks', '_trace_hooks', '_upgrade_hooks', '_ui_hooks', '_skillstate_hooks',
                      '_init_armed', '_upgrade_context', '_ui_context', '_skillstate_context'):
            with self.subTest(field=field):
                self.setUp()
                token = object() if field.endswith('context') else [('foreign', 'pre', 'foreign')]
                self.h.scope[field] = token
                self.assertFalse(self.snapshot())
                self.assertIs(self.h.scope[field], token)
                self.assertEqual(self.lookups, [])

    def test_points_change_during_scalar_metadata_aborts_before_any_text_read(self):
        self.one_entry()
        self.on_lookup = lambda field: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', 4)
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [])
        self.assertEqual(self.lookups, ['Description'])
        self.assertFalse(any('SUMMARY skill=MorePep' in line for line in self.h.logs))
        self.assertFalse(any('unchanged_from_start=True' in line for line in self.h.logs))
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 4)

    def test_rank_change_during_value_read_aborts_before_next_field_or_target(self):
        entry = self.one_entry()
        entry.callbacks['Description'] = lambda: setattr(self.tree.Skills[2], 'Grade', 1)
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [(entry.Name, 'Description')])
        self.assertFalse(any('field=Description status=VERIFIED' in line for line in self.h.logs))
        self.assertFalse(any('SUMMARY skill=MorePep' in line for line in self.h.logs))
        self.assertFalse(any('unchanged_from_start=True' in line for line in self.h.logs))
        self.assertEqual(self.tree.Skills[2].Grade, 1)

    def test_replaced_reference_during_metadata_refuses_stale_instance_before_payload(self):
        entry = self.one_entry()
        replacement = self.entry('new')
        self.on_lookup = lambda field: setattr(self.node, 'SkillEffectPresentations', WrappedArray([replacement]))
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [])
        self.assertFalse(any('SUMMARY skill=MorePep' in line for line in self.h.logs))
        self.assertNotIn((entry.Name, 'Description'), self.reads)

    def test_changed_descriptor_between_fields_skips_the_unverified_field(self):
        entry = self.one_entry()
        entry.callbacks['Description'] = lambda: setattr(self.props['NoConstraintText'].Class, 'Name', 'BoolProperty')
        self.assertFalse(self.snapshot())
        self.assertNotIn((entry.Name, 'NoConstraintText'), self.reads)
        self.assertTrue(any('fields=3/4 text=PARTIAL' in line for line in self.h.logs))

    def test_changed_reference_class_during_metadata_never_reads_instance_text(self):
        entry = self.one_entry()
        self.on_lookup = lambda field: setattr(entry, 'Class', Obj('ForeignClass'))
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [])
        self.assertFalse(any('SUMMARY skill=MorePep' in line for line in self.h.logs))

    def test_invalid_array_schema_wrapper_or_reference_class_refuses_before_text(self):
        changes = [lambda: setattr(self.array_prop, 'ArrayDim', 2),
                   lambda: setattr(self.node, 'SkillEffectPresentations', []),
                   lambda: setattr(self.node, 'SkillEffectPresentations', WrappedArray([Obj('Foreign')])),
                   lambda: setattr(self.inner, 'PropertyClass', types.SimpleNamespace(Name='AttributePresentationDefinition'))]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                self.one_entry()
                change()
                self.assertFalse(self.snapshot())
                self.assertEqual(self.lookups, [])
                self.assertEqual(self.reads, [])

    def test_oversized_and_unreadable_arrays_refuse_before_entry_access(self):
        class Huge(WrappedArray):
            def __len__(self):
                return 257
            def __getitem__(self, index):
                raise AssertionError('oversized array indexed')
        self.node.SkillEffectPresentations = Huge([])
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [])
        class Broken(Huge):
            def __len__(self):
                raise RuntimeError('unknown length')
        self.node.SkillEffectPresentations = Broken([])
        self.assertFalse(self.snapshot())
        self.assertEqual(self.lookups, [])

    def test_missing_oversized_or_non_string_identity_aborts_before_text(self):
        for path in ('', None, 4, 'x' * 385):
            with self.subTest(kind=type(path)):
                self.setUp()
                self.node.SkillEffectPresentations = WrappedArray([self.entry(path=path)])
                self.assertFalse(self.snapshot())
                self.assertEqual(self.lookups, [])
                self.assertEqual(self.reads, [])

    def test_array_length_change_during_text_aborts_before_next_field(self):
        entry = self.one_entry()
        entry.callbacks['Description'] = lambda: setattr(self.node, 'SkillEffectPresentations', WrappedArray([]))
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [(entry.Name, 'Description')])
        self.assertFalse(any('field=Description status=VERIFIED' in line for line in self.h.logs))
        self.assertFalse(any('unchanged_from_start=True' in line for line in self.h.logs))

    def test_scalar_allowlist_does_not_accept_a_guessed_field_and_cleanup_still_restores(self):
        with self.assertRaises(ValueError):
            self.h.call('_presentation_text_property', self.cls, 'Attribute')
        self.assertEqual(self.lookups, [])
        for method in ('cancel_init_node', 'shutdown'):
            with self.subTest(method=method):
                self.setUp()
                self.assertTrue(self.snapshot())
                self.h.call(method)
                self.assertEqual(self.h.names(), ['MorePep', 'Myelin'])
                self.assertEqual(self.h.ltier.bCellIsOccupied, [True, False, True])
                self.assertEqual(self.h.hooks, {})
                self.assertIsNone(self.h.scope['_uvh_node_state'])


if __name__ == '__main__':
    unittest.main()
