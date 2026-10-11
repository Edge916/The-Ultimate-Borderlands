"""Combined class metadata checks; simulations are not live inheritance proof."""
import types
import unittest

import test_presentation_display as display_tests
from test_runtime_mock import Obj, WrappedArray


EXPECTED = 'GD_Tulip_Mechromancer_Skills.LittleBigTrouble.Myelin:AttributePresentationDefinition_0'


class Poison:
    def __repr__(self):
        raise AssertionError('unknown metadata/object repr')
    def __str__(self):
        raise AssertionError('unknown metadata/object coercion')
    def __bool__(self):
        raise AssertionError('unknown metadata/object truth conversion')
    def __eq__(self, other):
        raise AssertionError('unknown metadata/object equality')
    def __getattr__(self, field):
        raise AssertionError('unknown metadata/object traversal')


class MetaClass(Obj):
    def __init__(self, label, parent=None):
        super().__init__(label, 'Class', SuperField=parent)
        self.path_value = 'GD_Test.' + label
        self.on_path = self.on_parent = None
        self.metadata_reads = []

    def _path_name(self):
        self.metadata_reads.append('path')
        if self.on_path:
            self.on_path()
        return self.path_value

    def __getattribute__(self, field):
        if field == 'SuperField':
            self.metadata_reads.append('parent')
            if self.on_parent:
                self.on_parent()
        if field in ('_inherits', '_superfields', '_properties', '_find', 'ClassDefaultObject',
                     'Interfaces', '_implements', 'GetValue', 'Evaluate'):
            raise AssertionError('unallowlisted class metadata/API')
        return super().__getattribute__(field)


class AttributeClassTests(unittest.TestCase):
    def setUp(self):
        fixture = display_tests.PresentationDisplayTests()
        fixture.setUp()
        self.h, self.tree, self.node = fixture.h, fixture.tree, fixture.node
        self.reads, self.lookups, self.props = fixture.reads, fixture.lookups, fixture.props
        self.array_prop, self.inner = fixture.array_prop, fixture.inner
        self.entries, self.attributes = fixture.entries, fixture.attributes
        def convert(source):
            value = MetaClass(source.Name)
            value.__dict__.update(source.__dict__)
            return value
        self.cls, self.skill_class, self.declared = map(convert, (fixture.cls, fixture.skill_class, fixture.attribute_class))
        self.h.sdk.unreal.UClass = MetaClass  # Distinct from UObject; names cannot fake this type.
        self.array_prop.Outer = self.skill_class
        self.inner.PropertyClass = self.cls
        for prop in self.props.values():
            prop.Outer = self.cls
        self.props['Attribute'].PropertyClass = self.declared
        for definition in (self.node, self.h.first, self.h.last):
            definition.Class = self.skill_class
        for entry in self.entries:
            entry.Class = self.cls
        for attribute in self.attributes:
            attribute.Class = self.declared
        self.entry = self.h.last.SkillEffectPresentations[1]
        self.entry._path_name = lambda: EXPECTED
        self.value = self.entry.payload['Attribute']
        self.root = MetaClass('Object')
        self.declared.SuperField = self.root
        self.actual = MetaClass('ShieldAttributeSubclass', self.declared)
        self.value.Class = self.actual
        # Any access to Attribute object identity/values or other presentations fails.
        self.value._path_name = lambda: self.fail('Attribute object path is forbidden')
        for entry in self.entries:
            if entry is not self.entry:
                entry.callbacks['Attribute'] = lambda: self.fail('unrelated Attribute inspected')
        self.h.logs.clear()

    def snapshot(self):
        return self.h.call('inspect_overclock_attribute_class')

    def has(self, text):
        return any(text in line for line in self.h.logs)

    def assert_aborted(self):
        self.assertTrue(self.has('[UVH-CLASS] ABORT'))
        self.assertFalse(self.has('[UVH-CLASS] CLASS '))
        self.assertFalse(self.has('[UVH-CLASS] ANCESTOR '))
        self.assertFalse(self.has('unchanged_from_start=True'))

    def test_combined_wrapper_class_and_ancestry_without_calls_writes_or_other_payloads(self):
        def forbidden(*args, **kwargs):
            self.fail('discovery/hooks/native calls/loads/writes')
        self.h.sdk.find_all = self.h.sdk.find_object = self.h.sdk.construct_object = self.h.sdk.load_package = forbidden
        self.h.sdk.hooks.add_hook = self.h.sdk.hooks.remove_hook = forbidden
        self.h.scope['_node_set_array'] = forbidden
        objects = [self.h.pc, self.tree, self.node, self.h.first, self.h.last, self.cls, self.skill_class,
                   self.declared, self.actual, self.root, *self.entries, *self.attributes, *self.props.values()]
        # metadata_reads are fixture instrumentation; all other object state must stay equal.
        before = [{k: v for k, v in obj.__dict__.items() if k != 'metadata_reads'} for obj in objects]
        self.assertTrue(self.snapshot())
        self.assertEqual(before, [{k: v for k, v in obj.__dict__.items() if k != 'metadata_reads'} for obj in objects])
        self.assertEqual(set(self.reads), {(self.entry.Name, 'Attribute')})
        self.assertLessEqual(len(self.reads), 39)
        self.assertEqual(set(self.lookups), {'Attribute'})
        self.assertTrue(self.has('wrapper=SDK_UOBJECT actual_class=SDK_UCLASS status=VERIFIED_METADATA'))
        self.assertTrue(self.has('coverage=COMPLETE classes=3 declared_relation=DERIVED'))
        self.assertTrue(self.has('combined_checks=wrapper,class,ancestry observers_added=0'))
        self.assertTrue(self.has('FINAL points=(5, 0) ranks=(0, 0, 0) unchanged_from_start=True'))
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.h.loads, [])

    def test_exact_class_and_complete_non_subclass_are_separate_metadata_results(self):
        for actual, relation in ((self.declared, 'EXACT'), (self.root, 'NO')):
            with self.subTest(relation=relation):
                self.value.Class = actual
                self.h.logs.clear()
                self.assertTrue(self.snapshot())
                self.assertTrue(self.has('declared_relation=' + relation))

    def test_matching_name_without_declared_identity_does_not_establish_inheritance(self):
        self.value.Class = MetaClass('AttributeDefinition', self.root)
        self.assertTrue(self.snapshot())
        self.assertTrue(self.has('coverage=COMPLETE classes=2 declared_relation=NO'))

    def test_known_absence_is_distinct_from_metadata_unavailable(self):
        self.entry.payload['Attribute'] = None
        self.assertTrue(self.snapshot())
        self.assertTrue(self.has('wrapper=KNOWN_ABSENT'))
        self.assertTrue(self.has('status=VERIFIED_ABSENCE'))
        self.assertTrue(self.has('coverage=NOT_APPLICABLE classes=0'))
        self.assertEqual(self.actual.metadata_reads, [])

    def test_unknown_wrapper_is_not_repr_coerced_compared_or_traversed(self):
        self.entry.payload['Attribute'] = Poison()
        self.assertFalse(self.snapshot())
        self.assertTrue(self.has('wrapper=UNKNOWN'))
        self.assertTrue(self.has('coverage=UNAVAILABLE'))
        self.assertTrue(self.has('unchanged_from_start=True'))
        self.assertEqual(self.actual.metadata_reads, [])

    def test_actual_class_must_be_real_sdk_uclass_before_any_metadata_access(self):
        for actual in (None, Poison(), Obj('AttributeDefinition'), types.SimpleNamespace(Name='AttributeDefinition')):
            with self.subTest(kind=type(actual)):
                self.value.Class = actual
                self.h.logs.clear()
                self.assertFalse(self.snapshot())
                self.assertTrue(self.has('wrapper=SDK_UOBJECT actual_class=UNAVAILABLE'))
                self.assertFalse(self.has('[UVH-CLASS] CLASS '))
                self.assertTrue(self.has('unchanged_from_start=True'))

    def test_missing_or_wrong_attribute_schema_refuses_before_getter(self):
        changes = [('Name', 'Other'), ('Outer', Obj('Foreign')), ('Class', Obj('IntProperty')),
                   ('PropertyFlags', True), ('PropertyFlags', 4), ('Offset_Internal', 65),
                   ('ArrayDim', 2), ('PropertyClass', Obj('AttributeDefinition')),
                   ('PropertyClass', MetaClass('Other'))]
        for field, value in changes:
            with self.subTest(field=field):
                self.setUp()
                setattr(self.props['Attribute'], field, value)
                self.assertFalse(self.snapshot())
                self.assertEqual(self.reads, [])
                self.assert_aborted()
        self.setUp()
        self.props.pop('Attribute')
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [])

    def test_field_getter_error_is_unavailable_not_absent_and_exception_not_stringified(self):
        class GetterError(RuntimeError):
            def __str__(self):
                raise AssertionError('getter exception was stringified')
        self.entry.payload['Attribute'] = GetterError()
        self.assertFalse(self.snapshot())
        self.assertTrue(self.has('FIELD status=UNAVAILABLE getter_error=GetterError'))
        self.assertFalse(self.has('KNOWN_ABSENT'))
        self.assert_aborted()

    def test_initial_unknown_class_name_and_path_are_bounded_without_repr(self):
        for field, value in (('Name', Poison()), ('Name', ''), ('Name', 'x' * 97),
                             ('path_value', Poison()), ('path_value', ''), ('path_value', 'x' * 385)):
            with self.subTest(field=field, kind=type(value)):
                self.setUp()
                setattr(self.actual, field, value)
                self.assertFalse(self.snapshot())
                self.assertTrue(self.has('status=PARTIAL_UNAVAILABLE'))
                self.assertFalse(self.has('[UVH-CLASS] CLASS '))
                self.assertTrue(self.has('unchanged_from_start=True'))

    def test_class_paths_and_names_are_escaped_without_template_evaluation(self):
        self.actual.Name = 'Class\n{raw}<b>'
        self.actual.path_value = 'GD\n{value}<b>'
        self.assertTrue(self.snapshot())
        line = next(line for line in self.h.logs if 'CLASS role=ACTUAL' in line)
        self.assertIn('\\n{value}<b>', line)
        self.assertNotIn('\n', line)

    def test_parent_unknown_is_not_traversed_or_reported_as_root(self):
        self.actual.SuperField = Poison()
        self.assertFalse(self.snapshot())
        self.assertTrue(self.has('coverage=UNAVAILABLE classes=1 declared_relation=UNKNOWN'))
        self.assertTrue(self.has('unchanged_from_start=True'))

    def test_missing_parent_metadata_is_not_known_root(self):
        del self.actual.SuperField
        self.assertFalse(self.snapshot())
        self.assertTrue(self.has('coverage=UNAVAILABLE classes=0 declared_relation=UNKNOWN'))
        self.assertTrue(self.has('CLASS role=ACTUAL'))

    def test_unknown_ancestor_name_or_path_does_not_make_complete_chain(self):
        self.root.path_value = Poison()
        self.assertFalse(self.snapshot())
        self.assertTrue(self.has('coverage=UNAVAILABLE classes=2 declared_relation=UNKNOWN'))
        self.assertEqual(sum('ANCESTOR depth=' in line for line in self.h.logs), 2)

    def test_cycle_detection_is_bounded_and_does_not_claim_inheritance(self):
        for cyclic in (self.actual, self.declared):
            with self.subTest(target=cyclic.Name):
                self.setUp()
                self.declared.SuperField = self.actual if cyclic.Name == 'ShieldAttributeSubclass' else self.declared
                self.assertFalse(self.snapshot())
                self.assertTrue(self.has('coverage=CYCLE classes=2 declared_relation=UNKNOWN'))
                self.assertTrue(self.has('unchanged_from_start=True'))

    def test_eight_class_cap_never_reads_ninth_class_metadata(self):
        cursor, chain = None, []
        for i in reversed(range(9)):
            cursor = MetaClass('Ancestor' + str(i), cursor)
            chain.insert(0, cursor)
        self.value.Class = chain[0]
        chain[8].on_path = chain[8].on_parent = lambda: self.fail('ninth class metadata read')
        self.assertFalse(self.snapshot())
        self.assertEqual(chain[8].metadata_reads, [])
        self.assertTrue(self.has('coverage=CAPPED classes=8 declared_relation=UNKNOWN'))
        self.assertEqual(sum('ANCESTOR depth=' in line for line in self.h.logs), 8)
        self.assertLessEqual(len(self.reads), 39)

    def test_declared_identity_inside_capped_chain_proves_only_bounded_relationship(self):
        cursor = MetaClass('Tail')
        for i in range(7):
            cursor = MetaClass('Parent' + str(i), cursor)
        self.declared.SuperField = cursor
        self.assertFalse(self.snapshot())
        self.assertTrue(self.has('coverage=CAPPED classes=8 declared_relation=DERIVED'))
        self.assertTrue(self.has('status=PARTIAL_UNAVAILABLE'))

    def test_unknown_array_metadata_wrapper_count_or_reference_refuses_before_attribute(self):
        changes = [lambda: setattr(self.array_prop, 'Outer', Obj('Foreign')),
                   lambda: setattr(self.inner, 'PropertyClass', Obj('AttributePresentationDefinition')),
                   lambda: setattr(self.h.last, 'SkillEffectPresentations', []),
                   lambda: setattr(self.h.last, 'SkillEffectPresentations', WrappedArray([])),
                   lambda: setattr(self.h.last, 'SkillEffectPresentations', WrappedArray([self.entry] * 257)),
                   lambda: setattr(self.h.last, 'SkillEffectPresentations', WrappedArray([self.entry, Obj('Foreign')]))]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                change()
                self.assertFalse(self.snapshot())
                self.assertEqual(self.reads, [])
                self.assert_aborted()

    def test_only_observed_index_path_is_accepted_without_searching_other_entries(self):
        for path in (Poison(), 'Other.Path', '', EXPECTED + 'x'):
            with self.subTest(kind=type(path)):
                self.setUp()
                self.entry._path_name = lambda: path
                self.assertFalse(self.snapshot())
                self.assertEqual(self.reads, [])
                self.assert_aborted()

    def test_invalid_owned_session_points_rank_or_inertness_refuses_before_metadata(self):
        changes = [lambda: setattr(self.h.pc, 'Pawn', None),
                   lambda: setattr(self.h.pc, 'PlayerSkillTree', Obj('Foreign')),
                   lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', None),
                   lambda: setattr(self.tree.Skills[1], 'Grade', 1),
                   lambda: setattr(self.h.pc.WorldInfo.GRI, 'PRIArray', WrappedArray([Obj('Peer')])),
                   lambda: self.node.SkillEffectDefinitions.append(Obj('Effect'))]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                change()
                self.assertFalse(self.snapshot())
                self.assertEqual(self.lookups, [])
                self.assertEqual(self.reads, [])

    def test_overlapping_and_failed_observers_refuse_without_cleaning_up_or_reading(self):
        for field in ('_init_armed', '_init_hooks', '_trace_hooks', '_upgrade_context', '_upgrade_hooks',
                      '_ui_context', '_ui_hooks', '_skillstate_context', '_skillstate_hooks'):
            with self.subTest(field=field):
                self.setUp()
                token = object() if field.endswith('context') else [('foreign', 'pre', 'foreign')]
                self.h.scope[field] = token
                self.assertFalse(self.snapshot())
                self.assertIs(self.h.scope[field], token)
                self.assertEqual(self.reads, [])

    def test_state_change_at_class_path_or_parent_aborts_without_repair_or_stale_metadata(self):
        for field, change in (('on_path', lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', 4)),
                              ('on_parent', lambda: setattr(self.tree.Skills[2], 'Grade', 1))):
            with self.subTest(field=field):
                self.setUp()
                setattr(self.actual, field, change)
                self.assertFalse(self.snapshot())
                self.assert_aborted()

    def test_current_attribute_class_identity_or_declared_descriptor_change_aborts(self):
        changes = [lambda: setattr(self.value, 'Class', MetaClass('ShieldAttributeSubclass')),
                   lambda: self.entry.payload.update(Attribute=None),
                   lambda: self.entry.payload.update(Attribute=Obj('Replacement', Class=self.actual)),
                   lambda: setattr(self.props['Attribute'], 'PropertyClass', MetaClass('AttributeDefinition')),
                   lambda: setattr(self.props['Attribute'], 'Outer', Obj('Foreign'))]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                self.actual.on_path = change
                self.assertFalse(self.snapshot())
                self.assert_aborted()

    def test_current_presentation_count_reference_class_or_path_change_aborts(self):
        changes = [lambda: setattr(self.h.last, 'SkillEffectPresentations', WrappedArray([])),
                   lambda: setattr(self.h.last, 'SkillEffectPresentations', WrappedArray([self.entry, self.entries[0]])),
                   lambda: setattr(self.entry, 'Class', MetaClass('AttributePresentationDefinition')),
                   lambda: setattr(self.entry, '_path_name', lambda: 'Changed.Path')]
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                self.actual.on_path = change
                self.assertFalse(self.snapshot())
                self.assert_aborted()

    def test_absence_or_unknown_wrapper_changing_during_reread_aborts(self):
        for value in (None, Poison()):
            with self.subTest(kind=type(value)):
                self.setUp()
                self.entry.payload['Attribute'] = value
                attempts = []
                def change():
                    attempts.append(1)
                    if len(attempts) == 2:
                        self.entry.payload['Attribute'] = self.value
                self.entry.callbacks['Attribute'] = change
                self.assertFalse(self.snapshot())
                self.assert_aborted()

    def test_changed_parent_link_and_class_label_during_ancestry_are_rejected(self):
        for change in (lambda: setattr(self.actual, 'SuperField', self.root),
                       lambda: setattr(self.actual, 'Name', 'Changed')):
            with self.subTest(change=change):
                self.setUp()
                attempts = []
                def change_during_chain():
                    attempts.append(1)
                    if len(attempts) == 2:
                        change()
                self.declared.on_path = change_during_chain
                self.assertFalse(self.snapshot())
                self.assert_aborted()

    def test_schema_changed_during_attribute_getter_aborts_before_class_metadata(self):
        self.entry.callbacks['Attribute'] = lambda: setattr(self.props['Attribute'], 'PropertyClass', MetaClass('AttributeDefinition'))
        self.assertFalse(self.snapshot())
        self.assertEqual(self.actual.metadata_reads, [])
        self.assert_aborted()

    def test_points_changed_by_schema_lookup_abort_before_payload(self):
        old = self.cls._find_prop
        def lookup(field):
            self.h.pc.PlayerReplicationInfo.GeneralSkillPoints = 4
            return old(field)
        self.cls._find_prop = lookup
        self.assertFalse(self.snapshot())
        self.assertEqual(self.reads, [])
        self.assert_aborted()
        self.assertEqual(self.h.pc.PlayerReplicationInfo.GeneralSkillPoints, 4)

    def test_cancel_and_disable_still_restore_owned_arrays_and_all_hooks(self):
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
