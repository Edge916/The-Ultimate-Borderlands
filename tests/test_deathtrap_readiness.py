"""Typed inert metadata fixtures; passing tests do not establish engine behavior."""
import types
import unittest
import tomllib

import test_runtime_mock as runtime_tests


class UObject(runtime_tests.Obj):
    forbidden_reads = {'GetSkillManager', 'ActivateSkill', 'DeactivateSkill', 'Duration',
                       'DurationBaseValue', 'ActivatedTime', 'DurationModifierStack',
                       'ActiveSkills', 'SkillInstigator', 'GetSkillState', 'Evaluate'}
    def __getattribute__(self, key):
        if key in UObject.forbidden_reads:
            raise AssertionError('instance payload/native wrapper read: ' + key)
        return super().__getattribute__(key)
    def __setattr__(self, key, value):
        if key in UObject.forbidden_reads:
            raise AssertionError('gameplay field written: ' + key)
        return super().__setattr__(key, value)


class UField(UObject):
    pass


class UClass(UField):
    def __init__(self, label, parent=None):
        super().__init__(label, 'Class', SuperField=parent, PropertySize=256)
        self.props, self.functions = {}, {}
        self.on_path = self.on_lookup = None
    def _path_name(self):
        if self.on_path:
            self.on_path()
        return 'Test.' + self.Name
    def _find(self, field):
        if self.on_lookup:
            self.on_lookup(field)
        return self.functions[field]
    def _find_prop(self, field):
        if self.on_lookup:
            self.on_lookup(field)
        return self.props[field]


class ZProperty(UField):
    def __init__(self, label, owner, **values):
        super().__init__(label, 'Property', Outer=owner, PropertyFlags=3,
                         Offset_Internal=0, ArrayDim=1, ElementSize=4,
                         PropertyLinkNext=None)
        self.__dict__.update(values)


class ZFloatProperty(ZProperty):
    pass


class ZObjectProperty(ZProperty):
    pass


class ZArrayProperty(ZProperty):
    pass


class ZBoolProperty(ZProperty):
    pass


class ZIntProperty(ZProperty):
    pass


class ZDelegateProperty(ZProperty):
    pass


class ZClassProperty(ZObjectProperty):
    pass


class UFunction(UField):
    def __init__(self, owner, label, props=(), ret=None):
        super().__init__(label, 'Function', Outer=owner, FunctionFlags=1024,
                         NumParams=len(props), ParamsSize=8 if props else 0,
                         ReturnValueOffset=0 if ret else 65535, PropertySize=256,
                         SuperField=None, Children=None, PropertyLink=None)
        self.props, self.ret, self.read_count = list(props), ret, 0
    def _path_name(self):
        return self.Outer._path_name() + ':' + self.Name
    def _find_return_param(self):
        return self.ret
    def _properties(self):
        for prop in self.props:
            self.read_count += 1
            yield prop
    def link(self):
        self.Children = self.PropertyLink = self.props[0] if self.props else None
        for index, prop in enumerate(self.props):
            prop.PropertyLinkNext = self.props[index + 1] if index + 1 < len(self.props) else None
    def __call__(self, *args, **kwargs):
        raise AssertionError('native function invoked')


class Poison:
    calls = []
    def __getattr__(self, key):
        Poison.calls.append('getattr')
        raise AssertionError('unknown metadata traversed')
    def __str__(self):
        Poison.calls.append('str')
        raise AssertionError('unknown metadata converted')
    def __repr__(self):
        Poison.calls.append('repr')
        raise AssertionError('unknown metadata represented')
    def __eq__(self, other):
        Poison.calls.append('eq')
        raise AssertionError('unknown metadata compared')
    def __bool__(self):
        Poison.calls.append('bool')
        raise AssertionError('unknown metadata truth conversion')


class DeathtrapReadinessTests(unittest.TestCase):
    def setUp(self):
        Poison.calls = []
        fixture = runtime_tests.RuntimeTests()
        fixture.setUp()
        self.tree = fixture.purchase_fixture()
        self.h = fixture.h
        self.node = self.h.scope['_uvh_node_state']['node']
        for obj in (self.h.pc, self.tree, self.h.pc.Pawn, self.h.pc.WorldInfo,
                    self.h.pc.PlayerReplicationInfo, self.node, self.h.first, self.h.last):
            obj.__class__ = UObject
        self.controller = UClass('WillowPlayerController')
        self.manager, self.skill, self.definition = UClass('SkillManager'), UClass('Skill'), UClass('SkillDefinition')
        self.h.pc.Class = self.controller
        for obj in (self.node, self.h.first, self.h.last):
            obj.Class = self.definition
        self.primary = UFunction(self.controller, 'GetSkillManager')
        self.ret = ZObjectProperty('ReturnValue', self.primary, PropertyFlags=0x480,
                                  PropertyClass=self.manager, ElementSize=8)
        self.primary.props, self.primary.ret = [self.ret], self.ret
        self.primary.NumParams, self.primary.ParamsSize, self.primary.ReturnValueOffset = 1, 8, 0
        self.primary.link()
        self.controller.functions = {'GetSkillManager': self.primary}
        self.manager.functions = {
            'ActivateSkill': UFunction(self.manager, 'ActivateSkill'),
            'DeactivateSkill': UFunction(self.manager, 'DeactivateSkill'),
        }
        self.array = ZArrayProperty('ActiveSkills', self.manager, ElementSize=12)
        self.array.Inner = ZObjectProperty('ActiveSkills', self.array, PropertyClass=self.skill, ElementSize=8)
        self.manager.props['ActiveSkills'] = self.array
        for i, field in enumerate(('Duration', 'DurationBaseValue', 'ActivatedTime')):
            self.skill.props[field] = ZFloatProperty(field, self.skill, Offset_Internal=16 + 4*i)
        self.skill.props['SkillInstigator'] = ZObjectProperty('SkillInstigator', self.skill,
                                                           PropertyClass=self.controller, Offset_Internal=32, ElementSize=8)
        self.skill.props['Definition'] = ZObjectProperty('Definition', self.skill,
                                                       PropertyClass=self.definition, Offset_Internal=40, ElementSize=8)
        stack = ZArrayProperty('DurationModifierStack', self.skill, Offset_Internal=48, ElementSize=12)
        stack.Inner = ZFloatProperty('DurationModifierStack', stack)
        self.skill.props['DurationModifierStack'] = stack
        self.h.sdk.unreal = types.SimpleNamespace(UObject=UObject, UClass=UClass, UFunction=UFunction,
            UField=UField, ZProperty=ZProperty, ZFloatProperty=ZFloatProperty,
            ZObjectProperty=ZObjectProperty, ZArrayProperty=ZArrayProperty)
        self.forbidden_calls = []
        def forbidden(*args, **kwargs):
            self.forbidden_calls.append('forbidden')
            raise AssertionError('SDK native/discovery/mutation API called')
        self.h.sdk.find_all = self.h.sdk.find_object = self.h.sdk.load_package = self.h.sdk.construct_object = forbidden
        self.h.sdk.hooks.add_hook = self.h.sdk.hooks.remove_hook = forbidden
        self.h.logs.clear()
        self.baseline = (self.h.pc.PlayerReplicationInfo.GeneralSkillPoints,
                         tuple(entry.Grade for entry in self.tree.Skills), tuple(self.h.names()))

    def run_diagnostic(self):
        value = self.h.call('inspect_deathtrap_readiness')
        self.assertEqual(self.forbidden_calls, [])
        self.assertEqual(Poison.calls, [])
        return value

    def has(self, label):
        return any(label in line for line in self.h.logs)

    def refused(self):
        self.assertFalse(self.run_diagnostic())
        self.assertTrue(self.has('ABORT coverage=REFUSED'))
        self.assertFalse(self.has('END coverage=COMPLETE'))

    def test_complete_typed_metadata_preserves_state_and_reads_no_payload_or_native_wrappers(self):
        self.assertTrue(self.run_diagnostic())
        self.assertTrue(self.has('END coverage=COMPLETE'))
        self.assertTrue(self.has('observers_added=0 native_calls=0 writes=0 signature=NOT_ESTABLISHED'))
        self.assertEqual(self.baseline, (self.h.pc.PlayerReplicationInfo.GeneralSkillPoints,
                         tuple(entry.Grade for entry in self.tree.Skills), tuple(self.h.names())))
        self.assertEqual(self.primary.read_count, 1)
        self.assertEqual(self.h.hooks, {})

    def test_missing_primary_is_unavailable_not_absent_or_complete(self):
        del self.controller.functions['GetSkillManager']
        self.assertFalse(self.run_diagnostic())
        self.assertTrue(self.has('END coverage=UNAVAILABLE'))
        self.assertTrue(self.has('"target": "manager"'))

    def test_missing_field_remains_unavailable_while_other_fields_are_recorded(self):
        del self.skill.props['Duration']
        self.assertFalse(self.run_diagnostic())
        self.assertTrue(self.has('"name": "Duration"'))
        self.assertTrue(self.has('"name": "DurationBaseValue"'))
        self.assertTrue(self.has('END coverage=UNAVAILABLE'))

    def test_missing_optional_lifecycle_descriptor_is_not_a_zero_call_claim(self):
        del self.manager.functions['ActivateSkill']
        self.assertFalse(self.run_diagnostic())
        self.assertTrue(self.has('END coverage=UNAVAILABLE'))
        self.assertTrue(self.has('signature=NOT_ESTABLISHED'))

    def test_function_properties_cap_at_seventeen_reads(self):
        self.primary.props.extend(ZFloatProperty('Local' + str(i), self.primary, PropertyFlags=0,
                                               Offset_Internal=8+4*i) for i in range(20))
        self.primary.link()
        self.assertFalse(self.run_diagnostic())
        self.assertEqual(self.primary.read_count, 17)
        self.assertTrue(self.has('END coverage=CAPPED'))
        self.assertFalse(self.has('"name": "Local15"'))

    def test_class_ancestry_cap_is_explicit(self):
        parent = None
        for i in range(9):
            parent = UClass('Ancestor' + str(i), parent)
        self.controller.SuperField = parent
        self.assertFalse(self.run_diagnostic())
        self.assertTrue(self.has('END coverage=CAPPED'))

    def test_cyclic_class_ancestry_refuses(self):
        self.controller.SuperField = self.controller
        self.refused()

    def test_unknown_class_is_not_coerced(self):
        self.h.pc.Class = Poison()
        self.refused()

    def test_same_name_foreign_function_owner_refuses(self):
        self.primary.Outer = UClass('WillowPlayerController')
        self.refused()

    def test_same_name_foreign_field_owner_refuses(self):
        self.skill.props['Duration'].Outer = UClass('Skill')
        self.refused()

    def test_unknown_property_owner_is_not_compared(self):
        self.skill.props['Duration'].Outer = Poison()
        self.refused()

    def test_wrong_field_wrapper_refuses_before_inner_or_payload_access(self):
        self.manager.props['ActiveSkills'] = ZFloatProperty('ActiveSkills', self.manager)
        self.refused()

    def test_untyped_array_inner_refuses(self):
        self.array.Inner = Poison()
        self.refused()

    def test_foreign_array_inner_owner_refuses(self):
        self.array.Inner.Outer = UClass('SkillManager')
        self.refused()

    def test_untyped_return_class_refuses(self):
        self.ret.PropertyClass = Poison()
        self.refused()

    def test_instigator_class_must_be_on_controller_ancestry(self):
        self.skill.props['SkillInstigator'].PropertyClass = UClass('ForeignController')
        self.refused()

    def test_definition_class_must_equal_exact_owned_definition_classes(self):
        self.skill.props['Definition'].PropertyClass = UClass('SkillDefinition')
        self.refused()

    def test_invalid_field_numeric_and_parameter_metadata_refuses(self):
        for key, value in [('PropertyFlags', True), ('PropertyFlags', 2**64),
                           ('PropertyFlags', 128), ('Offset_Internal', -1),
                           ('Offset_Internal', 1048577), ('ArrayDim', 0),
                           ('ArrayDim', 2), ('ElementSize', 0), ('ElementSize', 65537)]:
            with self.subTest(key=key, value=value):
                self.setUp()
                setattr(self.skill.props['Duration'], key, value)
                self.refused()

    def test_invalid_function_numbers_refuse(self):
        for key, value in [('FunctionFlags', True), ('NumParams', 256), ('ParamsSize', -1),
                           ('ReturnValueOffset', 65536), ('PropertySize', 1048577)]:
            with self.subTest(key=key):
                self.setUp()
                setattr(self.primary, key, value)
                self.refused()

    def test_duplicate_function_descriptor_names_refuse(self):
        self.primary.props.append(ZFloatProperty('ReturnValue', self.primary, PropertyFlags=0, Offset_Internal=8))
        self.primary.link()
        self.refused()

    def test_property_chain_disagrees_with_enumeration_refuses(self):
        self.primary.PropertyLink = ZFloatProperty('Foreign', self.primary)
        self.refused()

    def test_return_reference_outside_complete_enumeration_refuses(self):
        self.primary.ret = ZObjectProperty('ReturnValue', self.primary, PropertyClass=self.manager)
        self.refused()

    def test_return_flag_and_offset_mismatch_refuse(self):
        for key, value in [('PropertyFlags', 128), ('Offset_Internal', 4)]:
            with self.subTest(key=key):
                self.setUp()
                setattr(self.ret, key, value)
                self.refused()

    def test_overlong_or_noncanonical_labels_refuse(self):
        for value in ['Duration' * 20, 'Bad Name', Poison()]:
            with self.subTest(value_type=type(value).__name__):
                self.setUp()
                self.skill.props['Duration'].Name = value
                self.refused()

    def test_rank_one_and_unknown_points_refuse(self):
        for change in ('rank', 'unknown_points', 'bool_points'):
            with self.subTest(change=change):
                self.setUp()
                if change == 'rank':
                    next(entry for entry in self.tree.Skills if entry.Definition == self.node).Grade = 1
                else:
                    self.h.pc.PlayerReplicationInfo.GeneralSkillPoints = None if change == 'unknown_points' else True
                self.refused()

    def test_foreign_replaced_session_objects_and_extra_rosters_refuse(self):
        for change in ('controller', 'tree', 'pawn', 'world', 'pri', 'tree_owner', 'locals', 'roster'):
            with self.subTest(change=change):
                self.setUp()
                if change == 'controller': self.h.scope['get_pc'] = lambda **kw: UObject('Foreign')
                elif change == 'tree': self.h.pc.PlayerSkillTree = UObject('Foreign')
                elif change == 'pawn': self.h.pc.Pawn = None
                elif change == 'world': self.h.pc.WorldInfo = UObject('Foreign')
                elif change == 'pri': self.h.pc.PlayerReplicationInfo = UObject('Foreign')
                elif change == 'tree_owner': self.tree.Outer = UObject('Foreign')
                elif change == 'locals': self.h.engine.GamePlayers = runtime_tests.WrappedArray([runtime_tests.Obj('L', Actor=self.h.pc)] * 2)
                else: self.h.pc.WorldInfo.GRI.PRIArray = runtime_tests.WrappedArray([self.h.pc.PlayerReplicationInfo] * 2)
                self.refused()

    def test_inertness_and_failed_observer_overlap_refuse(self):
        for change in ('effects', 'init', 'upgrade', 'ui', 'state', 'trace'):
            with self.subTest(change=change):
                self.setUp()
                if change == 'effects': self.node.SkillEffectDefinitions = [Poison()]
                else: self.h.scope[{'init':'_init_hooks','upgrade':'_upgrade_hooks','ui':'_ui_hooks','state':'_skillstate_hooks','trace':'_trace_hooks'}[change]] = [('failed',)]
                self.refused()

    def test_points_drift_during_reflection_aborts(self):
        def drift(field):
            self.h.pc.PlayerReplicationInfo.GeneralSkillPoints += 1
        self.manager.on_lookup = drift
        self.refused()

    def test_same_name_controller_class_replacement_is_detected(self):
        self.controller.on_path = lambda: setattr(self.h.pc, 'Class', UClass('WillowPlayerController'))
        self.refused()

    def test_return_class_reference_drift_is_detected(self):
        self.skill.on_lookup = lambda field: setattr(self.ret, 'PropertyClass', UClass('SkillManager'))
        self.refused()

    def test_property_list_growth_after_enumeration_is_detected(self):
        def grow(field):
            self.ret.PropertyLinkNext = ZFloatProperty('NewLocal', self.primary)
        self.manager.on_lookup = grow
        self.refused()

    def test_overlap_starting_during_reflection_is_detected(self):
        self.manager.on_lookup = lambda field: self.h.scope['_upgrade_hooks'].append(('late',))
        self.refused()

    def test_repeated_calls_do_not_retain_context_or_install_observers(self):
        self.assertTrue(self.run_diagnostic())
        self.assertTrue(self.run_diagnostic())
        self.assertEqual(self.h.hooks, {})
        self.assertEqual(self.primary.read_count, 2)

    def test_unknown_current_controller_is_not_compared_or_traversed(self):
        self.h.scope['get_pc'] = lambda **kw: Poison()
        self.refused()

    def test_unknown_cap_lookahead_is_not_compared_or_traversed(self):
        self.primary.props.extend(ZFloatProperty('Local' + str(i), self.primary, PropertyFlags=0,
                                               Offset_Internal=8+4*i) for i in range(15))
        extra = ZFloatProperty('Extra', self.primary)
        self.primary.props.append(extra)
        self.primary.link()
        self.primary.props[16] = Poison()
        self.refused()

    def test_cyclic_field_link_refuses(self):
        prop = self.skill.props['Duration']
        prop.PropertyLinkNext = prop
        self.refused()

    def test_cyclic_array_inner_refuses(self):
        prop = self.skill.props['DurationModifierStack']
        prop.Inner = prop
        self.refused()

    def test_invalid_class_size_refuses(self):
        for value in (True, -1, 1048577):
            with self.subTest(value=value):
                self.setUp()
                self.controller.PropertySize = value
                self.refused()

    def test_package_title_and_version_match_runtime_registration(self):
        config = tomllib.loads(runtime_tests.SOURCE.with_name('pyproject.toml').read_text(encoding='utf-8'))
        metadata = config['tool']['sdkmod']
        self.assertEqual(metadata['name'], self.h.mod_options['name'])
        self.assertEqual(metadata['version'], self.h.mod_options['version'])
        self.assertEqual(metadata['name'], 'UVH v0.2.19 - RELATIONSHIP CLASS METADATA')

    def metadata_rows(self):
        import json
        return [json.loads(line.split(' METADATA ',1)[1]) for line in self.h.logs if ' METADATA ' in line]

    def test_manager_candidates_use_return_class_and_never_controller_fallback(self):
        selected = {'controller':[], 'manager':[]}
        def controller_lookup(name):
            selected['controller'].append(name)
            if name != 'GetSkillManager': raise AssertionError('controller fallback attempted')
        self.controller.on_lookup = controller_lookup
        self.manager.on_lookup = lambda name: selected['manager'].append(name)
        self.controller.functions['ActivateSkill'] = Poison()
        self.controller.functions['DeactivateSkill'] = Poison()
        self.assertTrue(self.run_diagnostic())
        self.assertEqual(set(selected['controller']), {'GetSkillManager'})
        self.assertEqual(set(selected['manager']), {'ActivateSkill','DeactivateSkill','ActiveSkills'})
        rows = self.metadata_rows()
        self.assertEqual([r.get('name',r.get('target')) for r in rows[:6]],
                         ['controller','GetSkillManager','manager',None,'ActivateSkill','DeactivateSkill'])
        self.assertEqual(rows[4]['path'],'Test.SkillManager:ActivateSkill')
        self.assertEqual(rows[5]['path'],'Test.SkillManager:DeactivateSkill')

    def test_controller_candidates_cannot_substitute_for_missing_manager_candidates(self):
        self.manager.functions.clear()
        for name in ('ActivateSkill','DeactivateSkill'):
            self.controller.functions[name] = UFunction(self.controller,name)
        self.assertFalse(self.run_diagnostic())
        rows = self.metadata_rows()
        for name in ('ActivateSkill','DeactivateSkill'):
            self.assertEqual(next(r for r in rows if r.get('name')==name)['coverage'],'UNAVAILABLE')
        self.assertTrue(any(r.get('name')=='DurationModifierStack' for r in rows))
        self.assertTrue(self.has('END coverage=UNAVAILABLE'))

    def test_missing_primary_never_probes_manager_or_fabricates_candidate_rows(self):
        del self.controller.functions['GetSkillManager']
        accesses = []
        self.manager.on_lookup = lambda name: accesses.append(name)
        self.assertFalse(self.run_diagnostic())
        self.assertEqual(accesses,[])
        rows = self.metadata_rows()
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[-1],{'kind':'DISCOVERY','target':'manager','coverage':'UNAVAILABLE'})
        self.assertEqual([r['name'] for r in rows if r['kind']=='FUNCTION'],['GetSkillManager'])

    def test_manager_candidate_declaring_ancestor_requires_actual_captured_owner(self):
        parent = UClass('ManagerParent')
        self.manager.SuperField = parent
        self.manager.functions['ActivateSkill'] = UFunction(parent,'ActivateSkill')
        self.assertTrue(self.run_diagnostic())
        self.assertEqual(next(r for r in self.metadata_rows() if r.get('name')=='ActivateSkill')['path'],
                         'Test.ManagerParent:ActivateSkill')

    def test_same_name_foreign_manager_function_owner_refuses(self):
        self.manager.functions['ActivateSkill'].Outer = UClass('SkillManager')
        self.refused()

    def test_manager_header_and_return_class_drift_abort_before_output(self):
        for change in ('header','return_class'):
            with self.subTest(change=change):
                self.setUp()
                def drift(name):
                    if name == 'DeactivateSkill':
                        if change == 'header': self.manager.functions['ActivateSkill'].FunctionFlags += 1
                        else: self.ret.PropertyClass = UClass('SkillManager')
                self.manager.on_lookup = drift
                self.refused()
                self.assertEqual(self.metadata_rows(),[])

    def test_missing_active_array_has_no_invented_skill_root_or_fields(self):
        del self.manager.props['ActiveSkills']
        self.assertFalse(self.run_diagnostic())
        rows = self.metadata_rows()
        self.assertEqual(len(rows),7)
        self.assertEqual(rows[-1],{'kind':'FIELD','name':'ActiveSkills','coverage':'UNAVAILABLE'})
        self.assertFalse(any(r.get('target')=='active_skill_class' for r in rows))

    def test_unknown_manager_candidate_is_refused_without_unknown_conversion(self):
        self.manager.functions['ActivateSkill'] = Poison()
        self.refused()

    def parameter_fixture(self):
        self.argument_target = UClass('AdditionalTarget')
        activation = self.manager.functions['ActivateSkill']
        activation.props = [
            ZObjectProperty('SkillInstigator', activation, PropertyFlags=128, PropertyClass=self.controller, Offset_Internal=0, ElementSize=8),
            ZObjectProperty('Definition', activation, PropertyFlags=128, PropertyClass=self.definition, Offset_Internal=8, ElementSize=8),
            ZObjectProperty('AdditionalSkillTarget', activation, PropertyFlags=144, PropertyClass=self.argument_target, Offset_Internal=16, ElementSize=8),
            ZIntProperty('SkillGrade', activation, PropertyFlags=144, Offset_Internal=24),
            ZDelegateProperty('StateChangeDelegate', activation, PropertyFlags=4194448, Offset_Internal=28, ElementSize=12),
            ZBoolProperty('ReturnValue', activation, PropertyFlags=0x480, Offset_Internal=40),
        ]
        activation.ret = activation.props[-1]
        activation.NumParams, activation.ParamsSize, activation.ReturnValueOffset = 6, 44, 40
        activation.link()
        deactivation = self.manager.functions['DeactivateSkill']
        deactivation.props = [
            ZObjectProperty('SkillInstigator', deactivation, PropertyFlags=128, PropertyClass=self.controller, Offset_Internal=0, ElementSize=8),
            ZObjectProperty('Definition', deactivation, PropertyFlags=128, PropertyClass=self.definition, Offset_Internal=8, ElementSize=8),
            ZBoolProperty('bIgnoreSkillInstigator', deactivation, PropertyFlags=144, Offset_Internal=16),
        ]
        deactivation.NumParams, deactivation.ParamsSize = 3, 20
        deactivation.link()
        return activation, deactivation

    def test_parameter_class_paths_cover_primary_and_both_actual_candidates(self):
        self.parameter_fixture()
        self.assertTrue(self.run_diagnostic())
        rows = [row for row in self.metadata_rows() if row['kind'] == 'FUNCTION']
        self.assertEqual([r['parameter_classes_coverage'] for r in rows], ['COMPLETE'] * 3)
        paths = [[p['declared_class'] for p in r['properties'] if p['declared_class_coverage'] == 'COMPLETE'] for r in rows]
        self.assertEqual(paths, [['Test.SkillManager'], ['Test.WillowPlayerController', 'Test.SkillDefinition', 'Test.AdditionalTarget'], ['Test.WillowPlayerController', 'Test.SkillDefinition']])
        self.assertTrue(all(r['signature'] == 'NOT_ESTABLISHED' for r in rows))

    def test_parameter_boolean_delegate_scalar_fields_are_not_traversed(self):
        activation, deactivation = self.parameter_fixture()
        activation.props[4].Signature = Poison()
        activation.props[5].FieldMask = Poison()
        deactivation.props[-1].FieldMask = Poison()
        self.assertTrue(self.run_diagnostic())
        for row in self.metadata_rows():
            if row.get('name') in ('ActivateSkill', 'DeactivateSkill'):
                for prop in row['properties']:
                    if prop['type'] in ('ZIntProperty', 'ZBoolProperty', 'ZDelegateProperty'):
                        self.assertEqual((prop['declared_class'], prop['declared_class_coverage']), ('NOT_APPLICABLE', 'NOT_APPLICABLE'))

    def test_parameter_supported_object_subclass_uses_propertyclass_not_metaclass(self):
        activation, _ = self.parameter_fixture()
        prop = activation.props[2]
        prop.__class__ = ZClassProperty
        prop.MetaClass = Poison()
        self.assertTrue(self.run_diagnostic())
        value = next(row for row in self.metadata_rows() if row.get('name') == 'ActivateSkill')['properties'][2]
        self.assertEqual(value['type'], 'ZClassProperty')
        self.assertEqual(value['declared_class'], 'Test.AdditionalTarget')

    def test_parameter_unsupported_object_and_nonobject_tags_refuse(self):
        for base in (ZObjectProperty, ZProperty):
            with self.subTest(base=base.__name__):
                self.setUp()
                activation, _ = self.parameter_fixture()
                prop = activation.props[2] if base is ZObjectProperty else activation.props[3]
                prop.__class__ = type('UnlistedProperty', (base,), {})
                self.refused()

    def test_parameter_initial_class_getter_unavailable_is_explicit_partial(self):
        self.parameter_fixture()
        def unavailable(): raise RuntimeError('synthetic unavailable header')
        self.argument_target._path_name = unavailable
        self.assertFalse(self.run_diagnostic())
        row = next(row for row in self.metadata_rows() if row.get('name') == 'ActivateSkill')
        self.assertEqual(row['coverage'], 'COMPLETE')
        self.assertEqual(row['parameter_classes_coverage'], 'UNAVAILABLE')
        self.assertEqual(row['properties'][2]['declared_class'], 'UNAVAILABLE')
        self.assertTrue(self.has('END coverage=UNAVAILABLE'))

    def test_parameter_unavailable_header_becoming_available_aborts(self):
        self.parameter_fixture()
        calls = []
        def intermittent():
            calls.append(1)
            if len(calls) == 1: raise RuntimeError('synthetic first unavailable')
            return 'Test.AdditionalTarget'
        self.argument_target._path_name = intermittent
        self.refused()
        self.assertEqual(self.metadata_rows(), [])
        self.assertGreaterEqual(len(calls), 2)

    def test_parameter_invalid_class_metadata_refuses(self):
        for change in ('name', 'path', 'parent', 'size'):
            with self.subTest(change=change):
                self.setUp(); self.parameter_fixture()
                if change == 'name':
                    self.argument_target.Name = Poison()
                    self.argument_target._path_name = lambda: 'Test.AdditionalTarget'
                elif change == 'path': self.argument_target._path_name = lambda: 'Not canonical'
                elif change == 'parent': self.argument_target.SuperField = Poison()
                else: self.argument_target.PropertySize = True
                self.refused()

    def test_parameter_class_schema_drift_after_capture_aborts_before_output(self):
        self.parameter_fixture()
        calls = []
        def drift():
            calls.append(1)
            if len(calls) == 2: self.argument_target.PropertySize += 1
        self.argument_target.on_path = drift
        self.refused()
        self.assertEqual(self.metadata_rows(), [])

    def test_parameter_same_name_declared_class_replacement_aborts(self):
        activation, _ = self.parameter_fixture()
        def drift(name):
            if name == 'DeactivateSkill': activation.props[2].PropertyClass = UClass('AdditionalTarget')
        self.manager.on_lookup = drift
        self.refused()
        self.assertEqual(self.metadata_rows(), [])

    def test_parameter_class_change_during_emission_prevents_final_success(self):
        self.parameter_fixture()
        original = self.h.scope['log']
        def emit(line):
            original(line)
            if ' METADATA ' in line: self.argument_target.PropertySize += 1
        self.h.scope['log'] = emit
        self.refused()
        self.assertTrue(self.metadata_rows())
        self.assertFalse(self.has(' FINAL '))

    def test_parameter_capped_enumeration_precedes_unavailable_class(self):
        activation, _ = self.parameter_fixture()
        for i in range(11):
            activation.props.append(ZFloatProperty('Local' + str(i), activation, PropertyFlags=0, Offset_Internal=44 + 4*i))
        activation.link()
        def unavailable(): raise RuntimeError('synthetic unavailable header')
        self.argument_target._path_name = unavailable
        self.assertFalse(self.run_diagnostic())
        row = next(row for row in self.metadata_rows() if row.get('name') == 'ActivateSkill')
        self.assertEqual(len(row['properties']), 16)
        self.assertEqual((row['coverage'], row['parameter_classes_coverage']), ('CAPPED', 'CAPPED'))
        self.assertEqual(row['properties'][2]['declared_class_coverage'], 'UNAVAILABLE')
        self.assertTrue(self.has('END coverage=CAPPED'))

    def test_parameter_repeated_collections_do_not_retain_class_headers(self):
        self.parameter_fixture()
        self.assertTrue(self.run_diagnostic())
        self.argument_target.Name = 'UpdatedTarget'
        self.h.logs.clear()
        self.assertTrue(self.run_diagnostic())
        row = next(row for row in self.metadata_rows() if row.get('name') == 'ActivateSkill')
        self.assertEqual(row['properties'][2]['declared_class'], 'Test.UpdatedTarget')
        self.assertEqual(self.h.hooks, {})

    def test_parameter_rank_one_refuses_before_new_class_reads(self):
        self.parameter_fixture()
        calls = []
        self.argument_target.on_path = lambda: calls.append(1)
        next(entry for entry in self.tree.Skills if entry.Definition == self.node).Grade = 1
        self.refused()
        self.assertEqual(calls, [])

    def test_parameter_state_change_during_class_header_read_aborts(self):
        self.parameter_fixture()
        self.argument_target.on_path = lambda: setattr(self.h.pc.PlayerReplicationInfo, 'GeneralSkillPoints', 2)
        self.refused()
        self.assertEqual(self.metadata_rows(), [])
