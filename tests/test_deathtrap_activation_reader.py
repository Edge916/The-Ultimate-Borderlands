"""Independent inert activation transcripts; no SDK/native lifetime proof."""
import ast
import gc
import inspect
import json
import re
import sys
import types
import unittest
import weakref
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import test_runtime_mock as runtime


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py'
PREFIX = '[UVH-ACTIVATION] '
NATIVE_OPS = []
NATIVE_WRITES = []
ON_OPERATION = None
TRACE_WRITES = False
SDK_FIELDS = {'Class', 'Name', 'Outer', 'FunctionFlags', 'NumParams', 'ParamsSize',
    'ReturnValueOffset', 'PropertySize', 'SuperField', 'PropertyFlags',
    'Offset_Internal', 'ArrayDim', 'ElementSize', 'PropertyClass', 'Pawn',
    'PlayerClass', 'WorldInfo', 'PlayerReplicationInfo', 'NetMode', 'GamePlayers',
    'GRI', 'PRIArray', 'Actor', 'Owner', '_type', 'SkillInstigator', 'Definition',
    '_find', '_find_prop', '_properties', '_find_return_param', 'func', 'object'}
FORBIDDEN_FIELDS = {'AdditionalSkillTarget', 'SkillGrade', 'StateChangeDelegate',
    'Signature', 'FieldMask', 'ReturnValue', 'Duration', 'Grade', 'ActiveSkills',
    'ActivatedTime', 'GetSkillManager', 'ActivateSkill', '_path_name'}


def record(kind, label, field=''):
    """Record actual fixture accesses, with primitive stage only, never frames."""
    cursor = inspect.currentframe()
    stage = None
    try:
        while cursor is not None:
            if cursor.f_code.co_name == '_cr_inspect':
                stage = cursor.f_locals['budget'].stage
                break
            cursor = cursor.f_back
    finally:
        del cursor
    entry = (stage, kind, label, field)
    NATIVE_OPS.append(entry)
    if ON_OPERATION is not None:
        ON_OPERATION(entry)


class PrivateError(Exception):
    def __str__(self):
        raise AssertionError('private exception formatted')


class Poison:
    touched = []
    def __getattribute__(self, key):
        Poison.touched.append(key)
        raise AssertionError('poison accessed')
    def __repr__(self):
        Poison.touched.append('repr')
        raise AssertionError('poison repr')
    def __str__(self):
        Poison.touched.append('str')
        raise AssertionError('poison str')
    def __bool__(self):
        Poison.touched.append('bool')
        raise AssertionError('poison truth')
    def __eq__(self, other):
        Poison.touched.append('eq')
        raise AssertionError('poison equality')


class UObject:
    def __init__(self, label='object', **fields):
        self.__dict__.update(fields)
        self.__dict__.update(_label=label, reads=[], on_read=None)
    def __getattribute__(self, key):
        if key in SDK_FIELDS or key in FORBIDDEN_FIELDS:
            label = object.__getattribute__(self, '_label')
            object.__getattribute__(self, 'reads').append(key)
            record('get', label, key)
            hook = object.__getattribute__(self, 'on_read')
            if hook is not None:
                hook(self, key)
            if key in FORBIDDEN_FIELDS:
                raise AssertionError('forbidden getter: ' + key)
        return object.__getattribute__(self, key)
    def __setattr__(self, key, value):
        if TRACE_WRITES and (key in SDK_FIELDS or key in FORBIDDEN_FIELDS):
            NATIVE_WRITES.append((object.__getattribute__(self, '_label'), key))
        object.__setattr__(self, key, value)
    def __eq__(self, other):
        raise AssertionError('native equality')
    def __bool__(self):
        raise AssertionError('native truth')
    def __repr__(self):
        raise AssertionError('native repr')
    def __str__(self):
        raise AssertionError('native str')


class UClass(UObject):
    def _find(self, field):
        record('method', self._label, '_find:' + field)
        return self.functions[field]


class ZObjectProperty(UObject):
    pass


class ZBoolProperty(UObject):
    pass


class ZIntProperty(UObject):
    pass


class ZDelegateProperty(UObject):
    pass


class PropertyIterator:
    def __init__(self, values):
        self.iterator = iter(values)
    def __next__(self):
        record('next', 'function', 'property')
        return next(self.iterator)


class UFunction(UObject):
    def _find_prop(self, name):
        record('method', 'function', '_find_prop:' + name)
        return self.properties[name]
    def _properties(self):
        record('method', 'function', '_properties')
        return PropertyIterator(self.ordered)
    def _find_return_param(self):
        record('method', 'function', '_find_return_param')
        return self.return_prop
    def __call__(self, *args):
        raise AssertionError('engine invocation')


class WrappedStruct(UObject):
    pass


class BoundFunction(UObject):
    def __call__(self, *args):
        raise AssertionError('bound engine invocation')


class WrappedArray:
    def __init__(self, label, *values):
        self.label, self.values, self.indices = label, values, []
    def __len__(self):
        record('len', self.label)
        return len(self.values)
    def __getitem__(self, index):
        record('index', self.label, str(index))
        self.indices.append(index)
        if index != 0:
            raise AssertionError('unbounded array index')
        return self.values[index]
    def __iter__(self):
        raise AssertionError('roster traversal')


class ActivationReaderTests(unittest.TestCase):
    def setUp(self):
        global ON_OPERATION, TRACE_WRITES
        ON_OPERATION, TRACE_WRITES = None, False
        Poison.touched = []
        # Explicit current bytes: old fixtures remain frozen to their own versions.
        self.h = runtime.Harness(source=SOURCE.read_bytes())
        self.sdk = self.h.sdk
        self.sdk.unreal = types.SimpleNamespace(UObject=UObject, UClass=UClass,
            UFunction=UFunction, ZObjectProperty=ZObjectProperty,
            ZBoolProperty=ZBoolProperty, ZIntProperty=ZIntProperty,
            ZDelegateProperty=ZDelegateProperty, BoundFunction=BoundFunction,
            WrappedStruct=WrappedStruct, WrappedArray=WrappedArray)
        self.manager = UClass('manager_class', Name='SkillEffectManager', functions={})
        self.controller = UClass('controller_class', Name='WillowPlayerController', functions={})
        self.declared = UClass('declared_controller', Name='Controller', functions={})
        self.definition_class = UClass('definition_class', Name='SkillDefinition', functions={})
        self.core = UClass('core_class', Name='Object', functions={})
        self.classes = {'WillowGame.SkillEffectManager': self.manager,
            'WillowGame.WillowPlayerController': self.controller,
            'Engine.Controller': self.declared, 'WillowGame.SkillDefinition': self.definition_class,
            'Core.Object': self.core}
        self.lookups = []
        def find_class(path):
            record('lookup', 'class', path)
            self.lookups.append(path)
            return self.classes[path]
        self.sdk.find_class = find_class
        self.fn = UFunction('function', Name='ActivateSkill', Outer=self.manager,
            FunctionFlags=149506, NumParams=6, ParamsSize=32, ReturnValueOffset=28,
            PropertySize=32, SuperField=None)
        self.manager.functions['ActivateSkill'] = self.fn
        self.props = []
        for name, kind, flags, offset, size, declared in (
            ('SkillInstigator', ZObjectProperty, 128, 0, 4, self.declared),
            ('Definition', ZObjectProperty, 128, 4, 4, self.definition_class),
            ('AdditionalSkillTarget', ZObjectProperty, 144, 8, 4, self.core),
            ('SkillGrade', ZIntProperty, 144, 12, 4, None),
            ('StateChangeDelegate', ZDelegateProperty, 4194448, 16, 12, None),
            ('ReturnValue', ZBoolProperty, 1408, 28, 4, None)):
            self.props.append(kind(name + '_prop', Name=name, Outer=self.fn,
                PropertyFlags=flags, Offset_Internal=offset, ArrayDim=1,
                ElementSize=size, PropertyClass=declared, Signature=Poison(), FieldMask=Poison()))
        self.fn.properties = {object.__getattribute__(p, 'Name'): p for p in self.props}
        self.fn.ordered, self.fn.return_prop = self.props, self.props[5]
        self.pri, self.pawn = UObject('pri'), UObject('pawn')
        self.player_class = UObject('player_class', Name='CharClass_Mechromancer')
        self.roster = WrappedArray('roster', self.pri)
        self.gri = UObject('gri', PRIArray=self.roster)
        self.world = UObject('world', NetMode=runtime.NetMode.NM_Standalone, GRI=self.gri)
        self.pc = UObject('pc', Class=self.controller, Pawn=self.pawn,
            PlayerClass=self.player_class, WorldInfo=self.world, PlayerReplicationInfo=self.pri)
        self.pri.Owner = self.pc
        self.local = UObject('local', Actor=self.pc)
        self.players = WrappedArray('players', self.local)
        self.engine = UObject('engine', GamePlayers=self.players)
        self.h.pc, self.h.base.ENGINE = self.pc, self.engine
        self.definition = UObject('definition', Name='Skill_DeathTrap', Class=self.definition_class)
        self.obj = UObject('manager', Class=self.manager)
        self.args = WrappedStruct('args', _type=self.fn, SkillInstigator=self.pc,
            Definition=self.definition, AdditionalSkillTarget=Poison(), SkillGrade=Poison(),
            StateChangeDelegate=Poison(), ReturnValue=Poison())
        self.bound = BoundFunction('bound', object=self.obj, func=self.fn)
        def find_enum(name):
            record('lookup', 'enum', name)
            return runtime.NetMode
        self.sdk.find_enum = find_enum
        def current_pc(**kwargs):
            self.assertEqual(kwargs, {'possibly_loading': True})
            record('helper', 'current_pc')
            return self.pc
        self.h.scope['get_pc'] = current_pc
        self.clock = 1000.0
        self.h.logs.clear()
        NATIVE_OPS.clear()
        NATIVE_WRITES.clear()

    def tearDown(self):
        global ON_OPERATION, TRACE_WRITES
        ON_OPERATION, TRACE_WRITES = None, False
        self.assertEqual(Poison.touched, [])
        self.assertEqual(self.h.loads, [])
        self.assertEqual(self.h.constructed, [])

    def fresh(self):
        self.tearDown()
        self.setUp()

    def call(self, name, *args):
        with patch('time.monotonic', lambda: self.clock):
            return self.h.call(name, *args)

    def key(self):
        return (self.h.scope['_CR_PATH'], 'pre', self.h.scope['_CR_IDENT'])

    def start(self):
        self.assertTrue(self.call('start_callback_local_reader'))
        return self.h.hooks[self.key()]

    def fire(self, callback=None, values=None):
        global TRACE_WRITES
        if callback is None:
            callback = self.h.hooks[self.key()]
        if values is None:
            values = (self.obj, self.args, Poison(), self.bound)
        TRACE_WRITES = True
        try:
            with patch.dict(sys.modules, {'unrealsdk': self.sdk, 'mods_base': self.h.base}), \
                    patch('time.monotonic', lambda: self.clock):
                self.assertIsNone(callback(*values))
        finally:
            TRACE_WRITES = False

    def records(self):
        return [line.split(PREFIX, 1)[1] for line in self.h.logs if PREFIX in line]

    def events(self):
        return [line for line in self.records() if line.startswith('EVENT ')]

    def has(self, text):
        return any(line.startswith(text) for line in self.records())

    def refuse_before_instigator(self):
        self.start()
        self.fire()
        self.assertFalse(self.events())
        self.assertNotIn('SkillInstigator', self.args.reads)

    def test_factory_activation_identity_and_start_has_no_native_access(self):
        self.assertEqual(self.h.mod_options['name'], 'UVH v0.2.19 - RELATIONSHIP CLASS METADATA')
        self.assertEqual(self.h.mod_options['version'], '0.2.19')
        self.assertEqual(self.h.scope['_CR_PATH'], 'WillowGame.SkillEffectManager:ActivateSkill')
        self.assertEqual(self.h.scope['_CR_IDENT'], 'UVH_ACTIVATION_READER_V18_PRE')
        self.assertEqual(len(self.h.mod_options['options']), 25)
        self.assertIn('22', self.h.mod_options['options'][21]['display_name'])
        self.assertIn('ACTIVATION', self.h.mod_options['options'][21]['display_name'])
        self.assertIn('23', self.h.mod_options['options'][22]['display_name'])
        self.assertFalse(self.h.hooks)
        self.start()
        self.assertEqual(NATIVE_OPS, [])
        self.assertTrue(self.has('START version=0.2.18 epoch=1 target=ActivateSkill phase=PRE'))

    def test_six_success_branches_have_independent_actual_access_transcripts(self):
        cases = [('NULL_INSTIGATOR', 'NOT_READ', '-', (98, 65, 0, 0)),
            ('OTHER_CONTROLLER_CLASS', 'NOT_READ', '-', (98, 66, 0, 0)),
            ('OTHER_WRAPPER', 'NOT_READ', '-', (98, 66, 1, 0)),
            ('SAME_WRAPPER', 'NULL_DEFINITION', '-', (98, 66, 36, 66)),
            ('SAME_WRAPPER', 'OTHER_NAME', 'UpshotRobot', (98, 66, 36, 68)),
            ('SAME_WRAPPER', 'DEATHTRAP_NAME', 'Skill_DeathTrap', (98, 66, 36, 68))]
        for controller, definition, name, expected in cases:
            with self.subTest(controller=controller, definition=definition):
                self.fresh()
                if controller == 'NULL_INSTIGATOR': self.args.SkillInstigator = None
                if controller == 'OTHER_CONTROLLER_CLASS': self.args.SkillInstigator = UObject('foreign', Class=self.declared)
                if controller == 'OTHER_WRAPPER': self.args.SkillInstigator = UObject('foreign', Class=self.controller)
                if definition == 'NOT_READ': self.args.Definition = Poison()
                if definition == 'NULL_DEFINITION': self.args.Definition = None
                if definition == 'OTHER_NAME': self.definition.Name = name
                self.start(); self.fire()
                event, = self.events()
                reported = tuple(map(int, event.split('stages=')[1].split(',')))
                self.assertEqual(reported, expected)
                actual = Counter(entry[0] for entry in NATIVE_OPS)
                self.assertEqual(tuple(actual[i] for i in range(4)), expected)
                self.assertEqual(len(NATIVE_OPS), sum(expected))
                self.assertIn('ops=' + str(sum(expected)), event)
                self.assertIn('controller={} definition={} name={}'.format(controller, definition, name), event)
                self.assertEqual(self.args.reads.count('SkillInstigator'), 1)
                self.assertEqual(self.args.reads.count('Definition'), int(definition != 'NOT_READ'))
                self.assertEqual(self.definition.reads.count('Name'), int(definition in ('OTHER_NAME', 'DEATHTRAP_NAME')))
                self.assertEqual(sum(x[1] == 'next' for x in NATIVE_OPS), 7)
                self.assertEqual(NATIVE_WRITES, [])

    def test_schema_has_every_exact_type_and_no_poisoned_value_reads(self):
        self.start(); self.fire()
        self.assertEqual(self.lookups[:5], ['WillowGame.SkillEffectManager',
            'WillowGame.WillowPlayerController', 'Engine.Controller',
            'WillowGame.SkillDefinition', 'Core.Object'])
        self.assertEqual(self.props[4].reads.count('ElementSize'), 1)
        self.assertNotIn('Signature', self.props[4].reads)
        self.assertNotIn('FieldMask', self.props[5].reads)
        for name in FORBIDDEN_FIELDS:
            self.assertNotIn(name, self.args.reads)
        self.assertEqual(self.players.indices, [0, 0])
        self.assertEqual(self.roster.indices, [0, 0])
        self.assertTrue(self.call('stop_callback_local_reader'))
        self.assertTrue(self.has('OUTCOME epoch=1 value=OBSERVED_PRIMITIVE ownership=UNESTABLISHED'))

    def test_every_descriptor_numeric_owner_name_and_size_shape_refuses(self):
        for index in range(6):
            for field, bad in (('PropertyFlags', True), ('PropertyFlags', -1),
                ('Offset_Internal', 99), ('ArrayDim', 2), ('ArrayDim', True),
                ('ElementSize', 8), ('ElementSize', True), ('Outer', object()), ('Name', 'Wrong')):
                with self.subTest(index=index, field=field, badtype=type(bad).__name__):
                    self.fresh(); setattr(self.props[index], field, bad)
                    self.refuse_before_instigator()

    def test_complete_kind_class_membership_order_count_and_terminator_guards(self):
        for change in ('wrong_kind', 'subclass', 'declared', 'lookup', 'missing', 'extra', 'reordered', 'duplicate'):
            for index in range(6):
                with self.subTest(change=change, index=index):
                    self.fresh()
                    if change == 'wrong_kind': self.props[index].__class__ = UObject
                    if change == 'subclass':
                        self.props[index].__class__ = type('Unknown', (type(self.props[index]),), {})
                    if change == 'declared':
                        if index >= 3: continue
                        self.props[index].PropertyClass = self.controller
                    if change == 'lookup': self.fn.properties[object.__getattribute__(self.props[index], 'Name')] = object()
                    if change == 'missing': self.fn.ordered = self.props[:index] + self.props[index+1:]
                    if change == 'extra': self.fn.ordered = self.props + [self.props[index]]
                    if change == 'reordered': self.fn.ordered = list(reversed(self.props))
                    if change == 'duplicate': self.fn.ordered = self.props[:index] + [self.props[0]] + self.props[index+1:]
                    if change == 'duplicate' and index == 0: continue
                    self.refuse_before_instigator()

    def test_function_wrapper_owner_names_numbers_and_bounds_refuse(self):
        for holder, field, bad in [('args', '_type', object()), ('bound', 'object', object()),
            ('bound', 'func', object()), ('obj', 'Class', object()), ('fn', 'Outer', object()),
            ('fn', 'Name', 'DeactivateSkill'), ('fn', 'FunctionFlags', True),
            ('fn', 'NumParams', 3), ('fn', 'ParamsSize', 31), ('fn', 'ReturnValueOffset', 65535),
            ('fn', 'PropertySize', 31), ('fn', 'PropertySize', True),
            ('fn', 'PropertySize', 1048577), ('fn', 'SuperField', object())]:
            with self.subTest(holder=holder, field=field):
                self.fresh(); setattr(getattr(self, holder), field, bad)
                self.refuse_before_instigator()

    def test_missing_wrong_or_alternate_return_descriptor_refuses_initial_schema(self):
        for bad in (None, object(), self.props[0]):
            with self.subTest(kind=type(bad).__name__):
                self.fresh(); self.fn.return_prop = bad; self.refuse_before_instigator()
        self.fresh()
        old = self.props[5]
        self.fn.return_prop = ZBoolProperty('alternate_return', **old.__dict__)
        self.refuse_before_instigator()

    def test_fresh_return_lookup_identity_is_checked_after_schema_iteration(self):
        self.start()
        def change(obj, key):
            if key == 'Name': self.fn.return_prop = object()
        self.props[4].on_read = change
        self.fire()
        self.assertFalse(self.events()); self.assertNotIn('SkillInstigator', self.args.reads)

    def test_return_flags_and_shape_are_revalidated_before_first_getter(self):
        for field, bad in (('PropertyFlags', 128), ('ElementSize', 8), ('Outer', object()),
            ('Offset_Internal', 0), ('ArrayDim', True), ('Name', 'BadReturn')):
            with self.subTest(field=field):
                self.fresh(); self.start()
                def change(obj, key):
                    if key == 'object': setattr(self.props[5], field, bad)
                self.bound.on_read = change
                self.fire(); self.assertNotIn('SkillInstigator', self.args.reads)
                self.assertFalse(self.events())

    def test_return_pointer_and_full_shape_drift_after_instigator_blocks_definition(self):
        for field, bad in (('return_prop', object()), ('PropertyFlags', 128),
            ('ElementSize', 8), ('Offset_Internal', 0), ('ArrayDim', 2), ('Outer', object())):
            with self.subTest(field=field):
                self.fresh(); self.start()
                def change(obj, key):
                    if key == 'SkillInstigator':
                        setattr(self.fn if field == 'return_prop' else self.props[5], field, bad)
                self.args.on_read = change; self.fire()
                self.assertEqual(self.args.reads.count('SkillInstigator'), 1)
                self.assertNotIn('Definition', self.args.reads); self.assertFalse(self.events())

    def test_return_and_member_drift_during_player_probe_blocks_definition_getter(self):
        for target in ('return', 'definition'):
            with self.subTest(target=target):
                self.fresh(); self.start()
                prop = self.props[5 if target == 'return' else 1]
                self.player_class.on_read = lambda obj, key: setattr(prop, 'ElementSize', 8) if key == 'Name' else None
                self.fire(); self.assertNotIn('Definition', self.args.reads)
                self.assertTrue(self.has('REFUSED epoch=1 reason=SCHEMA'))

    def test_return_and_definition_drift_after_definition_prevents_name_getter(self):
        for target in ('return_pointer', 'return_shape', 'definition_shape', 'function'):
            with self.subTest(target=target):
                self.fresh(); self.start()
                def change(obj, key):
                    if key != 'Definition': return
                    if target == 'return_pointer': self.fn.return_prop = object()
                    if target == 'return_shape': self.props[5].PropertyFlags = 128
                    if target == 'definition_shape': self.props[1].ArrayDim = 2
                    if target == 'function': self.fn.NumParams = 7
                self.args.on_read = change; self.fire()
                self.assertNotIn('Name', self.definition.reads); self.assertFalse(self.events())

    def test_instigator_member_recheck_after_getter_refuses_before_definition(self):
        self.start()
        self.args.on_read = lambda obj, key: setattr(self.props[0], 'ElementSize', 8) if key == 'SkillInstigator' else None
        self.fire(); self.assertNotIn('Definition', self.args.reads)
        self.assertTrue(self.has('REFUSED epoch=1 reason=SCHEMA'))

    def test_unknown_callback_types_refuse_without_payload_conversion(self):
        for index in (0, 1, 3):
            with self.subTest(index=index):
                self.fresh(); self.start()
                values = [self.obj, self.args, Poison(), self.bound]; values[index] = Poison()
                self.fire(values=values); self.assertFalse(self.events())
                self.assertNotIn('SkillInstigator', self.args.reads)

    def test_typed_unknown_parameter_and_definition_class_refuse_without_name(self):
        for target in ('instigator', 'definition_type', 'definition_class'):
            with self.subTest(target=target):
                self.fresh(); self.start()
                if target == 'instigator': self.args.SkillInstigator = Poison()
                if target == 'definition_type': self.args.Definition = Poison()
                if target == 'definition_class': self.definition.Class = self.controller
                self.fire(); self.assertFalse(self.events())
                self.assertNotIn('Name', self.definition.reads)

    def test_one_and_128_character_names_fit_without_clipping_or_coercion(self):
        for name in ('A', 'Z'*128):
            with self.subTest(length=len(name)):
                self.fresh(); self.definition.Name = name; self.start(); self.fire()
                self.assertIn(' name=' + name + ' ownership=', self.events()[0])
                self.assertEqual(self.definition.reads.count('Name'), 1)
                self.assertTrue(all(len(line.encode('utf-8')) <= 384 for line in self.h.logs))

    def test_literal_names_case_suffix_and_no_upshotrobot_alias(self):
        for name in ('Skill_DeathTrap', 'UpshotRobot', 'skill_deathtrap', 'SKILL_DEATHTRAP',
            'Skill_DeathTrap_0', 'NOT_READ', 'NULL_DEFINITION'):
            with self.subTest(name=name):
                self.fresh(); self.definition.Name = name; self.start(); self.fire()
                self.assertIn('definition=' + ('DEATHTRAP_NAME' if name == 'Skill_DeathTrap' else 'OTHER_NAME'), self.events()[0])
                self.assertIn(' name=' + name + ' ownership=', self.events()[0])

    def test_invalid_name_values_stay_private_in_all_error_records(self):
        class StrSubclass(str):
            def __str__(self): raise AssertionError('str coercion')
            def __repr__(self): raise AssertionError('repr coercion')
        for index, bad in enumerate((None, True, 1, b'Name', Poison(), StrSubclass('Private_Name'),
            '', '-', 'A'*129, 'Private/Path', 'Private\\Path', 'Private.Path',
            'Private:Path', 'Private=Name', 'Private|Name', 'Private Name',
            'Private\nName', 'Private\rName', 'Private\tName', 'Private\x00Name', 'é', '☃')):
            with self.subTest(index=index):
                self.fresh(); self.definition.Name = bad; self.start(); self.fire()
                self.assertFalse(self.events()); self.assertTrue(self.has('REFUSED epoch=1 reason=PARAMETER'))
                self.assertFalse(any(' name=' in line for line in self.records()))
                self.assertNotIn('Private', '\n'.join(self.h.logs))

    def test_name_getter_exception_dies_without_text_or_traceback_escape(self):
        error = PrivateError('PRIVATE_EXCEPTION')
        reference = weakref.ref(error)
        def fail(obj, key, error=error):
            if key == 'Name': raise error
        self.definition.on_read = fail; self.start(); self.fire()
        self.assertFalse(self.events()); self.assertTrue(self.has('ERROR epoch=1 reason=INTERNAL'))
        self.assertNotIn('PRIVATE_EXCEPTION', '\n'.join(self.h.logs))
        self.definition.on_read = None; del error, fail; gc.collect()
        self.assertIsNone(reference())

    def test_stop_at_name_read_defers_cleanup_and_discards_identifier(self):
        self.definition.Name = 'Never_Export_Stop'; self.start()
        def stop(obj, key):
            if key == 'Name':
                self.assertFalse(self.call('stop_callback_local_reader'))
                self.assertIn(self.key(), self.h.hooks)
        self.definition.on_read = stop; self.fire()
        self.assertFalse(self.events()); self.assertFalse(self.h.hooks)
        self.assertNotIn('Never_Export_Stop', '\n'.join(self.h.logs))

    def test_timeout_clock_regression_and_invalid_clock_suppress_name(self):
        for change in ('entry_time', 'regress', 'nan', 'name_time'):
            with self.subTest(change=change):
                self.fresh(); self.definition.Name = 'Never_Export_Time'; self.start()
                if change == 'entry_time': self.clock = 1120.0
                if change == 'regress': self.clock = 999.0
                if change == 'nan': self.clock = float('nan')
                if change == 'name_time':
                    self.definition.on_read = lambda obj, key: setattr(self, 'clock', 1120.0) if key == 'Name' else None
                self.fire(); self.assertFalse(self.events()); self.assertFalse(self.h.hooks)
                self.assertNotIn('Never_Export_Time', '\n'.join(self.h.logs))

    def test_initial_player_loading_class_pawn_character_mode_rosters_and_links(self):
        for change in ('loading', 'class', 'pawn', 'character', 'client', 'bool_mode',
            'players', 'roster', 'owner', 'actor', 'array', 'missing'):
            with self.subTest(change=change):
                self.fresh()
                if change == 'loading': self.h.scope['get_pc'] = lambda **kw: None
                if change == 'class':
                    # Drift after the instigator class read, at the fresh local
                    # solo check; changing it earlier is a valid filtered event.
                    def drift_class(obj, key):
                        if key == 'Class' and obj.reads.count('Class') == 2:
                            obj.Class = self.declared
                    self.pc.on_read = drift_class
                if change == 'pawn': self.pc.Pawn = None
                if change == 'character': self.player_class.Name = 'Other_Character'
                if change == 'client': self.world.NetMode = runtime.NetMode.NM_Client
                if change == 'bool_mode': self.world.NetMode = True
                if change == 'players': self.players.values = (self.local, self.local)
                if change == 'roster': self.roster.values = ()
                if change == 'owner': self.pri.Owner = object()
                if change == 'actor': self.local.Actor = object()
                if change == 'array': self.engine.GamePlayers = Poison()
                if change == 'missing': del self.pc.Pawn
                self.start(); self.fire(); self.assertFalse(self.events())
                self.assertNotIn('Definition', self.args.reads)

    def test_final_player_session_and_manager_drift_keep_read_name_private(self):
        for change in ('pc', 'pawn', 'roster', 'owner', 'world', 'class', 'manager'):
            with self.subTest(change=change):
                self.fresh(); self.definition.Name = 'Never_Export_Drift'; self.start()
                def drift(obj, key):
                    if key != 'Name': return
                    if change == 'pc': self.h.scope['get_pc'] = lambda **kw: None
                    if change == 'pawn': self.pc.Pawn = UObject('replacement_pawn')
                    if change == 'roster': self.roster.values = ()
                    if change == 'owner': self.pri.Owner = object()
                    if change == 'world': self.pc.WorldInfo = UObject('replacement_world', NetMode=runtime.NetMode.NM_Standalone, GRI=self.gri)
                    if change == 'class': self.pc.Class = self.declared
                    if change == 'manager': self.obj.Class = self.controller
                self.definition.on_read = drift; self.fire(); self.assertFalse(self.events())
                self.assertNotIn('Never_Export_Drift', '\n'.join(self.h.logs))

    def test_emitter_follows_finished_inspection_and_dropped_four_native_locals(self):
        original, seen = self.h.scope['_cr_emit'], []
        def check(payload):
            if payload.startswith('EVENT '):
                frame = inspect.currentframe().f_back
                cursor = frame
                try:
                    self.assertEqual(frame.f_code.co_name, 'observe')
                    for key in ('obj', 'args', 'ret', 'func'): self.assertIsNone(frame.f_locals[key])
                    while cursor is not None:
                        self.assertNotEqual(cursor.f_code.co_name, '_cr_inspect')
                        cursor = cursor.f_back
                    seen.append(payload)
                finally:
                    del frame, cursor
            return original(payload)
        self.h.scope['_cr_emit'] = check; self.start(); self.fire()
        self.assertEqual(len(seen), 1)

    def test_epoch_only_closure_and_state_are_primitive_without_native_or_name_history(self):
        callback = self.start()
        self.assertEqual(tuple(cell.cell_contents for cell in callback.__closure__), (1,))
        for name in ('First_Identifier', 'Second_Identifier'):
            self.definition.Name = name; self.fire()
        def primitive(value):
            if type(value) in (type(None), bool, int, float, str): return True
            if type(value) in (tuple, list): return all(primitive(v) for v in value)
            if type(value) is dict: return all(type(k) is str and primitive(v) for k, v in value.items())
            return False
        state = {key: value for key, value in self.h.scope.items() if key.startswith('_cr_') and not callable(value)}
        self.assertTrue(all(primitive(v) for v in state.values()))
        self.assertNotIn('Identifier', json.dumps(state))
        refs = [weakref.ref(x) for x in (self.obj, self.args, self.bound)]
        self.obj = self.args = self.bound = None; gc.collect()
        self.assertTrue(all(r() is None for r in refs))

    def test_busy_reentry_reads_no_nested_payload_and_only_counts_primitive(self):
        callback, once = self.start(), []
        def nested(obj, key):
            if key == 'SkillInstigator' and not once:
                once.append(True); self.fire(callback, (Poison(), Poison(), Poison(), Poison()))
        self.args.on_read = nested; self.fire()
        self.assertEqual(self.h.scope['_cr_stats']['reentry'], 1)
        self.assertEqual(self.h.scope['_cr_stats']['attempts'], 1)
        self.assertEqual(self.h.scope['_cr_stats']['classified'], 1)

    def test_old_and_closed_callbacks_are_exact_none_without_payload_access(self):
        callback = self.start(); self.call('stop_callback_local_reader')
        before = len(NATIVE_OPS); self.fire(callback, (Poison(), Poison(), Poison(), Poison()))
        self.assertEqual(len(NATIVE_OPS), before)
        self.start(); self.fire(callback, (Poison(), Poison(), Poison(), Poison()))
        self.assertEqual(self.h.scope['_cr_stats']['attempts'], 0)

    def test_stale_global_epoch_is_inert(self):
        callback = self.start(); self.h.scope['_cr_epoch'] = 2
        self.fire(callback, (Poison(), Poison(), Poison(), Poison()))
        self.assertEqual(self.h.scope['_cr_stats']['attempts'], 0)
        self.assertEqual(NATIVE_OPS, [])

    def test_actual_longest_event_and_24_events_bound_names_without_restart(self):
        self.h.scope['_cr_epoch'] = 2147483646
        self.definition.Name = 'A'*128; callback = self.start()
        for _ in range(24): self.fire(callback)
        lines = [line for line in self.h.logs if PREFIX + 'EVENT ' in line]
        self.assertEqual(len(lines), 24)
        self.assertEqual(max(len(line.encode('utf-8')) for line in lines), 317)
        self.assertEqual(self.definition.reads.count('Name'), 24)
        self.assertTrue(self.has('LIMIT reason=EVENTS')); self.assertFalse(self.h.hooks)
        self.fire(callback, (Poison(), Poison(), Poison(), Poison()))
        self.assertEqual(len(self.events()), 24)

    def test_64th_attempt_counts_before_automatic_owned_cleanup(self):
        self.start(); self.h.scope['_cr_stats']['attempts'] = 63; self.fire()
        self.assertEqual(self.h.scope['_cr_stats']['attempts'], 64)
        self.assertTrue(self.has('LIMIT reason=ATTEMPTS')); self.assertFalse(self.h.hooks)

    def test_stage_and_total_meter_refuse_before_one_extra_getter(self):
        self.start(); budget = self.h.scope['_CRBudget'](1)
        with patch('time.monotonic', lambda: self.clock):
            for stage, cap in enumerate((112, 80, 48, 80)):
                budget.stage = stage
                for _ in range(cap): budget.tick()
                with self.assertRaises(self.h.scope['_CRRefusal']): budget.get(Poison(), 'Name')
        self.assertEqual(budget.counts, [112, 80, 48, 80])
        self.assertEqual(NATIVE_OPS, [])

    def test_every_successful_access_prefix_can_stop_before_another_native_operation(self):
        global ON_OPERATION
        for interrupted in range(1, 269):
            with self.subTest(access=interrupted):
                self.fresh(); self.start()
                def stop(entry):
                    if len(NATIVE_OPS) == interrupted: self.h.scope['_cr_stop_requested'] = True
                ON_OPERATION = stop
                self.fire()
                self.assertLessEqual(len(NATIVE_OPS), interrupted)
                self.assertFalse(self.events()); self.assertFalse(self.h.hooks)
                self.assertNotIn(' name=', '\n'.join(self.records()))
        ON_OPERATION = None

    def test_failed_getter_consumes_reserved_tick_without_private_error_text(self):
        self.start()
        def fail(obj, key):
            if key == 'SkillInstigator': raise PrivateError('PRIVATE_GETTER')
        self.args.on_read = fail; self.fire()
        record_line = next(line for line in self.records() if line.startswith('ERROR epoch=1 reason=INTERNAL ops='))
        stages = tuple(map(int, record_line.split('stages=')[1].split(',')))
        self.assertEqual(stages, (98, 33, 0, 0))
        self.assertEqual(len(NATIVE_OPS), sum(stages))
        self.assertNotIn('PRIVATE_GETTER', '\n'.join(self.h.logs))

    def test_logging_failure_stops_without_counting_export_or_leaking_name(self):
        self.start(); self.h.scope['log'] = lambda message: (_ for _ in ()).throw(PrivateError('PRIVATE_LOG'))
        self.fire(); self.assertFalse(self.h.hooks)
        self.assertEqual(self.h.scope['_cr_stats']['classified'], 0)
        self.assertGreater(self.h.scope['_cr_stats']['errors'], 0)
        self.assertNotIn('PRIVATE_LOG', '\n'.join(self.h.logs))

    def test_late_stop_after_finished_inspection_prevents_name_export(self):
        original = self.h.scope['_cr_inspect']
        def stop(*values):
            result = original(*values); self.call('stop_callback_local_reader'); return result
        self.h.scope['_cr_inspect'] = stop
        self.definition.Name = 'Never_Export_Late'; self.start(); self.fire()
        self.assertFalse(self.events()); self.assertFalse(self.h.hooks)
        self.assertNotIn('Never_Export_Late', '\n'.join(self.h.logs))

    def test_silence_stop_needs_no_player_metadata_and_repeated_pairs_are_legal(self):
        self.start()
        self.sdk.find_class = lambda _: (_ for _ in ()).throw(AssertionError('STOP metadata'))
        self.h.scope['get_pc'] = lambda **kw: (_ for _ in ()).throw(AssertionError('STOP player'))
        for _ in range(3): self.assertTrue(self.call('stop_callback_local_reader'))
        self.assertTrue(self.has('OUTCOME epoch=1 value=NOT_OBSERVED'))
        self.assertEqual(NATIVE_OPS, [])

    def test_failed_removal_retains_identity_refuses_restart_and_preserves_history(self):
        callback = self.start(); self.fire(); self.h.fail_remove = True
        self.assertFalse(self.call('stop_callback_local_reader'))
        self.assertIsNotNone(self.h.scope['_cr_pending'])
        self.assertFalse(self.call('start_callback_local_reader'))
        self.fire(callback, (Poison(), Poison(), Poison(), Poison()))
        self.h.fail_remove = False; self.assertTrue(self.call('stop_callback_local_reader'))
        self.assertEqual(self.h.scope['_cr_stats']['cleanup_failures'], 1)
        self.assertTrue(self.has('OUTCOME epoch=1 value=REFUSED'))

    def test_uncertain_registration_never_deletes_foreign_tuple(self):
        foreign = lambda *values: None
        def broken_add(*values):
            self.h.hooks[self.key()] = foreign; raise PrivateError('PRIVATE_ADD')
        self.sdk.hooks.add_hook = broken_add
        self.assertFalse(self.call('start_callback_local_reader'))
        self.assertIs(self.h.hooks[self.key()], foreign)
        self.assertFalse(self.call('start_callback_local_reader'))
        self.h.hooks.clear(); self.assertTrue(self.call('stop_callback_local_reader'))
        self.assertNotIn('PRIVATE_ADD', '\n'.join(self.h.logs))

    def test_preexisting_identifier_refuses_without_deleting_foreign_hook(self):
        foreign = lambda *values: None; self.h.hooks[self.key()] = foreign
        self.assertFalse(self.call('start_callback_local_reader'))
        self.assertIs(self.h.hooks[self.key()], foreign)

    def test_registration_epoch_clock_nonbool_and_absence_checks(self):
        for change in ('epoch', 'clock', 'add_type', 'has_type', 'missing'):
            with self.subTest(change=change):
                self.fresh()
                if change == 'epoch': self.h.scope['_cr_epoch'] = 2147483647
                if change == 'clock': self.clock = float('nan')
                if change == 'add_type': self.sdk.hooks.add_hook = lambda *v: None
                if change == 'has_type': self.sdk.hooks.has_hook = lambda *v: None
                if change == 'missing': self.sdk.hooks.add_hook = lambda *v: True
                self.assertFalse(self.call('start_callback_local_reader')); self.assertEqual(NATIVE_OPS, [])

    def test_registration_reentry_and_stop_never_accept_starting_payload(self):
        for change in ('reentry', 'stop'):
            with self.subTest(change=change):
                self.fresh(); original = self.sdk.hooks.add_hook
                def add(path, phase, ident, callback):
                    result = original(path, phase, ident, callback)
                    if change == 'reentry': self.fire(callback, (Poison(), Poison(), Poison(), Poison()))
                    else: self.assertFalse(self.call('stop_callback_local_reader'))
                    return result
                self.sdk.hooks.add_hook = add
                self.assertEqual(self.call('start_callback_local_reader'), change == 'reentry')
                self.assertEqual(self.h.scope['_cr_stats']['attempts'], 0)
                if change == 'stop': self.assertFalse(self.h.hooks)

    def test_nonbool_removal_result_retains_failure_after_absence_retry(self):
        self.start(); original = self.sdk.hooks.remove_hook
        def remove(*values): original(*values); return None
        self.sdk.hooks.remove_hook = remove
        self.assertFalse(self.call('stop_callback_local_reader'))
        self.assertIsNotNone(self.h.scope['_cr_pending'])
        self.sdk.hooks.remove_hook = original
        self.assertTrue(self.call('stop_callback_local_reader'))
        self.assertTrue(self.has('OUTCOME epoch=1 value=REFUSED'))

    def test_old_contexts_and_manual_record_refuse_before_native_lookup(self):
        for key, value in (('_init_armed', True), ('_init_hooks', [object()]),
            ('_uvh_node_state', object()), ('_record', object()), ('_trace_hooks', [object()]),
            ('_upgrade_context', object()), ('_ui_context', object()),
            ('_skillstate_context', object()), ('_dt_event_uncertain', [object()])):
            with self.subTest(key=key):
                self.fresh(); self.h.scope[key] = value
                self.assertFalse(self.call('start_callback_local_reader'))
                self.assertEqual(NATIVE_OPS, [])

    def test_active_reader_blocks_other_controls_and_cancel_disable_clean_own_hook(self):
        self.start()
        for index in list(range(2)) + list(range(3, 21)):
            self.h.scope['option'] = self.h.mod_options['options'][index]['on_press']
            self.assertFalse(self.call('option'))
        self.call('cancel_init_node'); self.assertFalse(self.h.hooks)
        self.start(); self.call('shutdown'); self.assertFalse(self.h.hooks)

    def test_emit_refuses_nonprimitive_and_oversize_without_coercing(self):
        self.assertFalse(self.h.scope['_cr_emit'](Poison()))
        self.assertFalse(self.h.scope['_cr_emit']('A'*385))
        self.assertTrue(self.h.scope['_cr_emit']('CONTROL reason=TEST'))

    def test_ast_preserves_three_value_getters_none_ret_drop_and_no_engine_call(self):
        tree = ast.parse(SOURCE.read_bytes())
        nodes = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        getter_fields = [(n.args[0].id, n.args[1].value) for n in ast.walk(nodes['_cr_inspect'])
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'get'
            and len(n.args) > 1 and isinstance(n.args[0], ast.Name) and isinstance(n.args[1], ast.Constant)]
        self.assertEqual([x for x in getter_fields if x[0] == 'args'], [('args', 'SkillInstigator'), ('args', 'Definition')])
        self.assertEqual(getter_fields.count(('definition', 'Name')), 1)
        observe = next(n for n in nodes['_cr_callback'].body if isinstance(n, ast.FunctionDef))
        self.assertEqual([a.arg for a in observe.args.args], ['obj', 'args', 'ret', 'func'])
        self.assertFalse(any(isinstance(n, ast.Name) and n.id == 'ret' and isinstance(n.ctx, ast.Load) for n in ast.walk(observe)))
        self.assertTrue(all(isinstance(n.value, ast.Constant) and n.value.value is None for n in ast.walk(observe) if isinstance(n, ast.Return)))
        self.assertEqual(sum(isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant) and n.value.value is None
            and {t.id for t in n.targets if isinstance(t, ast.Name)} == {'obj', 'args', 'ret', 'func'} for n in ast.walk(observe)), 3)
        for name, node in nodes.items():
            if not name.startswith('_cr_') and name != '_CRBudget': continue
            for n in ast.walk(node):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                    self.assertNotIn(n.func.attr, ('GetSkillManager', 'ActivateSkill', 'load_package', 'construct_object', '_path_name'))
                if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
                    self.assertNotIn(n.attr, FORBIDDEN_FIELDS)
        old = ast.parse((ROOT/'archive/tested_runtime/v0.2.17/__init__.py').read_bytes())
        old_nodes = {n.name: n for n in old.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        for name in ('signature', 'find_live', 'apply', 'restore', '_upgrade_state', 'cancel_init_node', 'shutdown'):
            self.assertEqual(ast.dump(nodes[name]), ast.dump(old_nodes[name]), name)


if __name__ == '__main__':
    unittest.main()
