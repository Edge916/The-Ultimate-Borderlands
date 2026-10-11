"""Display flag/reference simulations; no engine formatting or effect proof."""
import types
import unittest

import test_presentations as presentation_tests
from test_runtime_mock import Obj, WrappedArray


class PresentationDisplayTests(unittest.TestCase):
    def setUp(self):
        fixture = presentation_tests.PresentationTests()
        fixture.setUp()
        self.h, self.node, self.tree = fixture.h, fixture.node, fixture.tree
        self.cls, self.array_prop = fixture.presentation_class, fixture.array_prop
        self.inner, self.skill_class = fixture.inner, fixture.skill_class
        self.fields = ('bDontDisplayNumber', 'bUseCustomNumberPlacement', 'bEnableTextColor', 'Attribute')
        self.attribute_class = Obj('AttributeDefinition', 'Class')
        self.props = {field: Obj(field, 'BoolProperty', Outer=self.cls, PropertyFlags=3,
                                Offset_Internal=116, ArrayDim=1) for field in self.fields[:3]}
        self.props['Attribute'] = Obj('Attribute', 'ObjectProperty', Outer=self.cls,
                                      PropertyFlags=3, Offset_Internal=64, ArrayDim=1,
                                      PropertyClass=self.attribute_class)
        self.reads, self.lookups, self.paths, self.entries, self.attributes = [], [], [], [], []
        self.on_lookup = None
        def lookup(field):
            self.lookups.append(field)
            if self.on_lookup:
                self.on_lookup(field)
            return self.props[field]
        self.cls._find_prop = lookup
        for definition, count in ((self.node, 0), (self.h.first, 4), (self.h.last, 2)):
            definition.SkillEffectPresentations = WrappedArray([self.entry(str(i)) for i in range(count)])
        self.h.logs.clear()

    def attribute(self, label='one', path='GD_Test.Attributes:Bonus'):
        fixture = self
        class Attribute(Obj):
            def __repr__(self):
                raise AssertionError('Attribute repr is forbidden')
            def __getattribute__(self, field):
                if field in ('Value', 'BaseValue', 'Resolver', 'GetValue', 'Evaluate', 'GetAttributeValue',
                             '_properties', '_find_prop'):
                    raise AssertionError('Attribute was traversed or evaluated')
                return super().__getattribute__(field)
        value = Attribute('Attribute_' + label, Class=self.attribute_class, Outer=Obj('SharedPackage'))
        value.on_path = None
        def identity():
            fixture.paths.append(value.Name)
            if value.on_path:
                value.on_path()
            return path
        value._path_name = identity
        self.attributes.append(value)
        return value

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
                if field in ('Description', 'NoConstraintText', 'Prefix', 'Suffix', 'BasePriority',
                             'bBiggerIsBetter', 'bDontDisplayPlusSign', 'GetHumanReadableValue'):
                    raise AssertionError('unallowlisted field/method accessed')
                return super().__getattribute__(field)
        entry = Presentation('Entry_' + label, Class=self.cls, Outer=Obj('SharedPackage'))
        entry.payload = dict(zip(self.fields, (False, True, True, self.attribute(label))))
        entry.callbacks = {}
        entry.on_path = None
        def identity():
            if entry.on_path:
                entry.on_path()
            return path
        entry._path_name = identity
        self.entries.append(entry)
        return entry

    def one_entry(self):
        entry = self.entry()
        self.node.SkillEffectPresentations = WrappedArray([entry])
        self.h.first.SkillEffectPresentations = self.h.last.SkillEffectPresentations = WrappedArray([])
        return entry

    def snapshot(self):
        return self.h.call('inspect_overclock_presentation_display')

    def has(self, text):
        return any(text in line for line in self.h.logs)

    def test_all_native_flags_and_identities_without_writes_calls_or_attribute_evaluation(self):
        def forbidden(*args, **kwargs):
            self.fail('gameplay calls/discovery/hooks/mutation/broad metadata enumeration')
        self.h.sdk.find_all = self.h.sdk.find_object = self.h.sdk.construct_object = self.h.sdk.load_package = forbidden
        self.h.sdk.hooks.add_hook = self.h.sdk.hooks.remove_hook = forbidden
        self.h.scope['_node_set_array'] = forbidden
        self.cls._properties = forbidden
        objects = [self.h.pc, self.tree, self.node, self.h.first, self.h.last, self.cls,
                   self.attribute_class, *self.entries, *self.attributes, *self.props.values()]
        before = [dict(obj.__dict__) for obj in objects]
        arrays = (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied))
        self.assertTrue(self.snapshot())
        self.assertEqual(before, [dict(obj.__dict__) for obj in objects])
        self.assertEqual(arrays, (list(self.h.btier.Skills), list(self.h.ltier.bCellIsOccupied)))
        self.assertEqual(len([field for _, field in self.reads if field != 'Attribute']), 18)
        self.assertEqual(len([field for _, field in self.reads if field == 'Attribute']), 24)
        self.assertEqual(set(field for _, field in self.reads), set(self.fields))
        self.assertEqual(len(self.paths), 6)
        self.assertEqual(sum('[UVH-DISPLAY] VALUE' in line for line in self.h.logs), 24)
        self.assertTrue(self.has('count=0 references=0/0 flags=0/0 attributes=0/0 present=0 absent=0 display=NOT_APPLICABLE'))
        self.assertTrue(self.has('flags=12/12 attributes=4/4 present=4 absent=0 display=VERIFIED'))
        self.assertTrue(self.has('flags=6/6 attributes=2/2 present=2 absent=0 display=VERIFIED'))
        self.assertTrue(self.has('complete_targets=3/3 fields=24/24 observers_added=0'))
        self.assertTrue(self.has('FINAL points=(5, 0) ranks=(0, 0, 0) unchanged_from_start=True'))
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.loads, [])

    def test_known_absent_attribute_is_verified_and_false_bool_is_not_unavailable(self):
        entry = self.one_entry()
        entry.payload['Attribute'] = None
        self.assertTrue(self.snapshot())
        self.assertTrue(self.has('field=Attribute status=VERIFIED presence=ABSENT'))
        self.assertTrue(self.has('field=bDontDisplayNumber status=VERIFIED value=False'))
        self.assertTrue(self.has('attributes=1/1 present=0 absent=1 display=VERIFIED'))
        self.assertEqual(self.paths, [])

    def test_missing_metadata_refuses_before_poisoned_payload_and_records_partial(self):
        for field in self.fields:
            with self.subTest(field=field):
                self.setUp()
                entry = self.one_entry()
                self.props.pop(field)
                entry.callbacks[field] = lambda: self.fail('missing metadata allowed payload')
                self.assertFalse(self.snapshot())
                self.assertNotIn((entry.Name, field), self.reads)
                self.assertTrue(self.has('field=' + field + ' status=UNAVAILABLE'))
                self.assertTrue(self.has('display=PARTIAL'))
                self.assertTrue(self.has('unchanged_from_start=True'))

    def test_exact_descriptor_name_owner_type_flags_offset_and_dimension_before_payload(self):
        for target in ('bDontDisplayNumber', 'Attribute'):
            changes = [('Name', 'Other'), ('Outer', Obj('Foreign')),
                       ('Class', types.SimpleNamespace(Name='StrProperty')),
                       ('PropertyFlags', 0), ('PropertyFlags', True),
                       ('Offset_Internal', 5), ('Offset_Internal', True),
                       ('ArrayDim', 2), ('ArrayDim', True)]
            for field, value in changes:
                with self.subTest(target=target, field=field):
                    self.setUp()
                    entry = self.one_entry()
                    setattr(self.props[target], field, value)
                    self.assertFalse(self.snapshot())
                    self.assertNotIn((entry.Name, target), self.reads)
                    self.assertTrue(self.has('field=' + target + ' status=UNAVAILABLE'))

    def test_declared_attribute_class_must_be_real_sdk_class_with_expected_name_before_payload(self):
        for value in (None, object(), types.SimpleNamespace(Name='AttributeDefinition'), Obj('Other', 'Class')):
            with self.subTest(kind=type(value)):
                self.setUp()
                entry = self.one_entry()
                self.props['Attribute'].PropertyClass = value
                entry.callbacks['Attribute'] = lambda: self.fail('bad declared class allowed getter')
                self.assertFalse(self.snapshot())
                self.assertNotIn((entry.Name, 'Attribute'), self.reads)
                self.assertEqual(self.paths, [])

    def test_non_bool_payloads_refuse_without_bool_conversion_repr_or_coercion(self):
        class Poison:
            def __repr__(self):
                raise AssertionError('foreign payload repr')
            def __bool__(self):
                raise AssertionError('foreign payload conversion')
        for value in (None, 0, 1, 'True', Poison()):
            with self.subTest(kind=type(value)):
                self.setUp()
                entry = self.one_entry()
                entry.payload['bDontDisplayNumber'] = value
                self.assertFalse(self.snapshot())
                self.assertTrue(self.has('field=bDontDisplayNumber status=UNAVAILABLE'))
                self.assertFalse(self.has('field=bDontDisplayNumber status=VERIFIED'))

    def test_attribute_payload_class_is_checked_before_path_helper_without_repr(self):
        class Poison:
            def __repr__(self):
                raise AssertionError('foreign payload repr')
        for value in (False, 1, Poison(), Obj('Foreign', Class=Obj('OtherClass')),
                      Obj('SameName', Class=Obj('AttributeDefinition', 'Class'))):
            with self.subTest(kind=type(value)):
                self.setUp()
                entry = self.one_entry()
                if isinstance(value, Obj):
                    value._path_name = lambda: self.fail('invalid Attribute path helper')
                entry.payload['Attribute'] = value
                self.assertFalse(self.snapshot())
                self.assertTrue(self.has('field=Attribute status=UNAVAILABLE'))
                self.assertEqual(self.paths, [])

    def test_getter_failure_is_distinct_from_absence_and_escaped(self):
        entry = self.one_entry()
        entry.payload['Attribute'] = RuntimeError('not available\nsecond line')
        self.assertFalse(self.snapshot())
        failure = next(line for line in self.h.logs if 'field=Attribute status=UNAVAILABLE' in line)
        self.assertIn('\\n', failure)
        self.assertNotIn('\n', failure)
        self.assertFalse(self.has('presence=ABSENT'))
        self.assertTrue(self.has('flags=3/3 attributes=0/1 present=0 absent=0 display=PARTIAL'))

    def test_attribute_paths_are_bounded_exact_strings_and_escaped_without_conversion(self):
        class Poison:
            def __repr__(self):
                raise AssertionError('unknown path repr')
        class Substring(str):
            pass
        for path in (None, '', 'x' * 385, Poison(), Substring('x')):
            with self.subTest(kind=type(path)):
                self.setUp()
                entry = self.one_entry()
                entry.payload['Attribute'] = self.attribute(path=path)
                self.assertFalse(self.snapshot())
                self.assertTrue(self.has('field=Attribute status=UNAVAILABLE'))
                self.assertFalse(self.has('presence=PRESENT'))
        self.setUp()
        entry = self.one_entry()
        entry.payload['Attribute'] = self.attribute(path='GD_Test\n{value}<b>' + 'x' * 360)
        self.assertTrue(self.snapshot())
        line = next(line for line in self.h.logs if 'presence=PRESENT' in line)
        self.assertIn('\\n{value}<b>', line)
        self.assertNotIn('\n', line)

    def test_sample_cap_never_indexes_fifth_entry_and_captures_only_four_fields_per_reference(self):
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
        self.assertEqual(len(self.paths), 4)
        self.assertEqual(sum('[UVH-DISPLAY] VALUE' in line for line in self.h.logs), 16)
        self.assertEqual(len(self.reads), 28)
        self.assertTrue(self.has('count=20 references=4/20 flags=12/12 attributes=4/4'))

    def test_invalid_current_tree_session_rank_points_or_inertness_before_scalar_metadata(self):
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

    def test_overlapping_or_failed_observers_refuse_without_cleanup_or_reads(self):
        for field in ('_init_hooks', '_trace_hooks', '_upgrade_hooks', '_ui_hooks', '_skillstate_hooks',
                      '_init_armed', '_upgrade_context', '_ui_context', '_skillstate_context'):
            with self.subTest(field=field):
                self.setUp()
                token = object() if field.endswith('context') else [('foreign', 'pre', 'foreign')]
                self.h.scope[field] = token
                self.assertFalse(self.snapshot())
                self.assertIs(self.h.scope[field], token)
                self.assertEqual(self.lookups, [])
                self.assertEqual(self.reads, [])

    def test_points_changed_by_descriptor_lookup_abort_before_value_without_repair(self):
        self.one_entry()
        self.on_lookup = lambda field: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', 4)
        self.assertFalse(self.snapshot())
        self.assertEqual(self.lookups, ['bDontDisplayNumber'])
        self.assertEqual(self.reads, [])
        self.assertFalse(self.has('SUMMARY skill=MorePep'))
        self.assertFalse(self.has('unchanged_from_start=True'))
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 4)

    def test_rank_changed_during_bool_read_abort_before_logging_value_or_next_field(self):
        entry = self.one_entry()
        entry.callbacks['bDontDisplayNumber'] = lambda: setattr(self.tree.Skills[2], 'Grade', 1)
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [(entry.Name, 'bDontDisplayNumber')])
        self.assertFalse(self.has('field=bDontDisplayNumber status=VERIFIED'))
        self.assertFalse(self.has('SUMMARY skill=MorePep'))
        self.assertFalse(self.has('unchanged_from_start=True'))
        self.assertEqual(self.tree.Skills[2].Grade, 1)

    def test_replaced_presentation_during_metadata_refuses_stale_payload(self):
        entry = self.one_entry()
        replacement = self.entry('new')
        self.on_lookup = lambda field: setattr(self.node, 'SkillEffectPresentations', WrappedArray([replacement]))
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [])
        self.assertEqual(self.lookups, ['bDontDisplayNumber'])
        self.assertFalse(self.has('SUMMARY skill=MorePep'))
        self.assertFalse(self.has('unchanged_from_start=True'))

    def test_array_length_change_during_bool_read_aborts_without_verified_payload(self):
        entry = self.one_entry()
        entry.callbacks['bDontDisplayNumber'] = lambda: setattr(self.node, 'SkillEffectPresentations', WrappedArray([]))
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [(entry.Name, 'bDontDisplayNumber')])
        self.assertFalse(self.has('field=bDontDisplayNumber status=VERIFIED'))
        self.assertFalse(self.has('unchanged_from_start=True'))

    def test_attribute_replacement_or_absence_change_at_path_aborts_before_stale_identity(self):
        for replacement in ('new', None):
            with self.subTest(replacement=replacement):
                self.setUp()
                entry = self.one_entry()
                original = entry.payload['Attribute']
                value = self.attribute('new') if replacement == 'new' else None
                original.on_path = lambda: entry.payload.update(Attribute=value)
                self.assertFalse(self.snapshot())
                self.assertFalse(self.has('field=Attribute status=VERIFIED'))
                self.assertFalse(self.has('SUMMARY skill=MorePep'))
                self.assertFalse(self.has('unchanged_from_start=True'))
                self.assertEqual(self.paths, [original.Name])

    def test_known_absence_becoming_typed_reference_during_recheck_aborts(self):
        entry = self.one_entry()
        value = self.attribute('new')
        entry.payload['Attribute'] = None
        attempts = []
        def change():
            attempts.append(1)
            if len(attempts) == 2:
                entry.payload['Attribute'] = value
        entry.callbacks['Attribute'] = change
        self.assertFalse(self.snapshot())
        self.assertFalse(self.has('presence=ABSENT'))
        self.assertFalse(self.has('unchanged_from_start=True'))

    def test_attribute_class_or_descriptor_change_during_path_aborts_before_identity(self):
        changes = [lambda entry: setattr(entry.payload['Attribute'], 'Class', Obj('AttributeDefinition', 'Class')),
                   lambda entry: setattr(self.props['Attribute'], 'PropertyClass', Obj('AttributeDefinition', 'Class')),
                   lambda entry: setattr(self.props['Attribute'], 'Outer', Obj('Foreign'))]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                entry = self.one_entry()
                entry.payload['Attribute'].on_path = lambda: change(entry)
                self.assertFalse(self.snapshot())
                self.assertFalse(self.has('field=Attribute status=VERIFIED'))
                self.assertFalse(self.has('SUMMARY skill=MorePep'))
                self.assertFalse(self.has('unchanged_from_start=True'))

    def test_state_change_during_attribute_path_aborts_without_repair(self):
        entry = self.one_entry()
        entry.payload['Attribute'].on_path = lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', 4)
        self.assertFalse(self.snapshot())
        self.assertFalse(self.has('field=Attribute status=VERIFIED'))
        self.assertFalse(self.has('unchanged_from_start=True'))
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 4)

    def test_descriptor_change_between_flag_fields_refuses_unknown_second_payload(self):
        entry = self.one_entry()
        entry.callbacks['bDontDisplayNumber'] = lambda: setattr(self.props['bUseCustomNumberPlacement'], 'Class', Obj('IntProperty'))
        self.assertFalse(self.snapshot())
        self.assertNotIn((entry.Name, 'bUseCustomNumberPlacement'), self.reads)
        self.assertTrue(self.has('field=bUseCustomNumberPlacement status=UNAVAILABLE'))
        self.assertTrue(self.has('flags=2/3 attributes=1/1'))

    def test_invalid_array_metadata_wrapper_reference_class_or_size_before_display_reads(self):
        changes = [lambda: setattr(self.array_prop, 'Outer', Obj('ForeignClass')),
                   lambda: setattr(self.inner, 'PropertyClass', Obj('OtherClass', 'Class')),
                   lambda: setattr(self.node, 'SkillEffectPresentations', []),
                   lambda: setattr(self.node, 'SkillEffectPresentations', WrappedArray([Obj('Wrong', Class=Obj('Other'))])),
                   lambda: setattr(self.node, 'SkillEffectPresentations', WrappedArray([object()] * 257))]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                change()
                self.assertFalse(self.snapshot())
                self.assertEqual(self.reads, [])
                self.assertEqual(self.lookups, [])
                self.assertFalse(self.has('SUMMARY skill=MorePep'))

    def test_presentation_path_refusal_before_flags_or_attribute_reads(self):
        for path in (None, '', 'x' * 385, 1):
            with self.subTest(kind=type(path)):
                self.setUp()
                entry = self.entry(path=path)
                self.node.SkillEffectPresentations = WrappedArray([entry])
                self.assertFalse(self.snapshot())
                self.assertEqual(self.lookups, [])
                self.assertEqual(self.reads, [])

    def test_unallowlisted_field_refuses_lookup_and_cancel_disable_preserve_restoration(self):
        for field in ('Description', 'Value', 'bBiggerIsBetter', 'bDontDisplayPlusSign'):
            with self.assertRaises(ValueError):
                self.h.call('_presentation_display_property', self.cls, field)
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
