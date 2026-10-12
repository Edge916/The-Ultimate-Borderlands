"""Adversarial inert bindings: fixture behavior, never native lifetime proof."""
import ast
import gc
import sys
import types
import unittest
import weakref
from unittest.mock import patch
import test_runtime_mock as runtime

NATIVE_OPS = []
SDK_FIELDS = {'Class','Name','Outer','FunctionFlags','NumParams','ParamsSize','ReturnValueOffset',
    'PropertySize','SuperField','PropertyFlags','Offset_Internal','ArrayDim','ElementSize',
    'PropertyClass','Pawn','PlayerClass','WorldInfo','PlayerReplicationInfo','NetMode',
    'GamePlayers','GRI','PRIArray','Actor','Owner','_type','SkillInstigator','Definition',
    '_find','_find_prop','_properties','_find_return_param','func','object'}


class PropertyIterator:
    def __init__(self, values):self.iterator=iter(values)
    def __next__(self):
        NATIVE_OPS.append('next')
        return next(self.iterator)


class PrivateError(Exception):
    def __str__(self):
        raise AssertionError('private exception formatted')


class Poison:
    touched = []
    def __getattribute__(self, key):
        Poison.touched.append(key)
        raise AssertionError('poison payload accessed')
    def __repr__(self):
        Poison.touched.append('repr'); raise AssertionError('repr')
    def __str__(self):
        Poison.touched.append('str'); raise AssertionError('str')
    def __eq__(self, other):
        Poison.touched.append('eq'); raise AssertionError('eq')
    def __bool__(self):
        Poison.touched.append('bool'); raise AssertionError('bool')


class UObject:
    def __init__(self, **fields):
        self.__dict__.update(fields)
        self.reads = []
        self.on_read = None
    def __getattribute__(self, key):
        if key not in ('__dict__', 'reads', 'on_read', '__class__'):
            if key in SDK_FIELDS:NATIVE_OPS.append('get')
            reads = object.__getattribute__(self, 'reads')
            reads.append(key)
            on_read = object.__getattribute__(self, 'on_read')
            if on_read is not None:
                on_read(self, key)
            if key in ('Duration', 'Grade', 'ActiveSkills', 'ActivatedTime', 'GetSkillManager',
                       'ActivateSkill', 'bIgnoreSkillInstigator', '_path_name'):
                raise AssertionError('forbidden native field: ' + key)
        return object.__getattribute__(self, key)
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
        NATIVE_OPS.append('method')
        return self.functions[field]


class ZObjectProperty(UObject):
    pass


class ZBoolProperty(UObject):
    pass


class UFunction(UObject):
    def _find_prop(self, field):
        NATIVE_OPS.append('method')
        return self.properties[field]
    def _properties(self):
        NATIVE_OPS.append('method')
        return PropertyIterator(self.ordered)
    def _find_return_param(self):
        NATIVE_OPS.append('method')
        return self.return_prop
    def __call__(self, *args):
        raise AssertionError('engine function invoked')


class WrappedStruct(UObject):
    pass


class BoundFunction(UObject):
    def __call__(self, *args):
        raise AssertionError('bound engine function invoked')


class WrappedArray:
    def __init__(self, *values):
        self.values = values
        self.indices = []
        self.on_len = None
    def __len__(self):
        NATIVE_OPS.append('len')
        if self.on_len is not None:
            self.on_len()
        return len(self.values)
    def __getitem__(self, index):
        NATIVE_OPS.append('index')
        self.indices.append(index)
        if index != 0:
            raise AssertionError('unbounded array access')
        return self.values[index]
    def __iter__(self):
        raise AssertionError('roster copied/traversed')


class CallbackLocalReaderTests(unittest.TestCase):
    # Preserve the accepted v17 reader scenarios as historical regressions.
    # Current activation behavior has independent tests and an explicit source.
    fixture_source = (runtime.ROOT / 'archive/tested_runtime/v0.2.17/__init__.py').read_bytes()
    reader_prefix = '[UVH-CALLBACK-NAME] '

    def setUp(self):
        Poison.touched = []
        self.h = runtime.Harness(source=self.fixture_source)
        self.sdk = self.h.sdk
        self.sdk.unreal = types.SimpleNamespace(UObject=UObject, UClass=UClass,
            UFunction=UFunction, ZObjectProperty=ZObjectProperty, ZBoolProperty=ZBoolProperty,
            BoundFunction=BoundFunction, WrappedStruct=WrappedStruct, WrappedArray=WrappedArray)
        self.manager = UClass(Name='SkillEffectManager', functions={})
        self.controller = UClass(Name='WillowPlayerController', functions={})
        self.declared = UClass(Name='Controller', functions={})
        self.definition_class = UClass(Name='SkillDefinition', functions={})
        self.classes = {'WillowGame.SkillEffectManager': self.manager,
            'WillowGame.WillowPlayerController': self.controller,
            'Engine.Controller': self.declared, 'WillowGame.SkillDefinition': self.definition_class}
        self.lookups = []
        def find_class(label):
            NATIVE_OPS.append('lookup')
            self.lookups.append(label)
            return self.classes[label]
        self.sdk.find_class = find_class
        self.fn = UFunction(Name='DeactivateSkill', Outer=self.manager, FunctionFlags=149506,
            NumParams=3, ParamsSize=12, ReturnValueOffset=65535, PropertySize=12,
            SuperField=None, return_prop=None)
        self.manager.functions['DeactivateSkill'] = self.fn
        self.props = []
        for label, flags, offset, declared in (('SkillInstigator',128,0,self.declared),
                ('Definition',128,4,self.definition_class),('bIgnoreSkillInstigator',144,8,None)):
            kind = ZBoolProperty if declared is None else ZObjectProperty
            prop = kind(Name=label, Outer=self.fn, PropertyFlags=flags, Offset_Internal=offset,
                        ArrayDim=1, ElementSize=4, PropertyClass=declared)
            self.props.append(prop)
        self.fn.properties = {p.Name: p for p in self.props}
        self.fn.ordered = self.props
        self.pri = UObject()
        self.pawn = UObject()
        self.player_class = UObject(Name='CharClass_Mechromancer')
        self.roster = WrappedArray(self.pri)
        self.gri = UObject(PRIArray=self.roster)
        self.world = UObject(NetMode=runtime.NetMode.NM_Standalone, GRI=self.gri)
        self.pc = UObject(Class=self.controller, Pawn=self.pawn, PlayerClass=self.player_class,
                          WorldInfo=self.world, PlayerReplicationInfo=self.pri)
        self.pri.Owner = self.pc
        self.local = UObject(Actor=self.pc)
        self.players = WrappedArray(self.local)
        self.engine = UObject(GamePlayers=self.players)
        self.h.pc = self.pc
        self.h.base.ENGINE = self.engine
        self.definition = UObject(Name='Skill_DeathTrap', Class=self.definition_class)
        self.obj = UObject(Class=self.manager)
        self.args = WrappedStruct(_type=self.fn, SkillInstigator=self.pc, Definition=self.definition)
        self.bound = BoundFunction(object=self.obj, func=self.fn)
        self.clock = 1000.0
        self.h.logs.clear()
        def find_enum(label):
            NATIVE_OPS.append('lookup')
            return runtime.NetMode
        self.sdk.find_enum=find_enum
        def current_pc(**kwargs):
            NATIVE_OPS.append('helper')
            return self.pc
        self.h.scope['get_pc']=current_pc
        NATIVE_OPS.clear()

    def tearDown(self):
        self.assertEqual(Poison.touched, [])
        self.assertEqual(self.h.loads, [])
        self.assertEqual(self.h.constructed, [])

    def call(self, name, *values):
        with patch('time.monotonic', lambda: self.clock):
            return self.h.call(name, *values)

    def key(self):
        return (self.h.scope['_CR_PATH'], 'pre', self.h.scope['_CR_IDENT'])

    def start(self):
        self.assertTrue(self.call('start_callback_local_reader'))
        return self.h.hooks[self.key()]

    def fire(self, callback=None, values=None):
        if callback is None:
            callback = self.h.hooks[self.key()]
        if values is None:
            values = (self.obj, self.args, Poison(), self.bound)
        with patch.dict(sys.modules, {'unrealsdk':self.sdk,'mods_base':self.h.base}), \
                patch('time.monotonic', lambda:self.clock):
            self.assertIsNone(callback(*values))

    def has(self, text):
        return any(self.reader_prefix + text in line for line in self.h.logs)

    def event(self):
        return next(line for line in self.h.logs if self.reader_prefix + 'EVENT ' in line)

    def test_import_inert_standalone_options_and_no_start_native_reads(self):
        self.assertEqual(self.h.mod_options['version'],'0.2.17')
        self.assertEqual(len(self.h.mod_options['options']),23)
        self.h.base.get_pc = lambda **kw: (_ for _ in ()).throw(AssertionError('START player read'))
        self.h.scope['get_pc'] = self.h.base.get_pc
        self.sdk.find_class = lambda _: (_ for _ in ()).throw(AssertionError('START metadata read'))
        self.start()
        self.assertEqual(self.lookups,[])
        self.assertEqual(self.args.reads,[])
        self.assertFalse(self.h.scope['_init_armed'])
        self.assertIsNone(self.h.scope['_uvh_node_state'])

    def test_useful_event_fits_every_stage_and_reports_narrow_classification(self):
        self.start(); self.fire()
        event = self.event()
        self.assertIn('controller=SAME_WRAPPER definition=DEATHTRAP_NAME name=Skill_DeathTrap ownership=UNESTABLISHED',event)
        stages = tuple(map(int,event.split('stages=')[1].split(',')))
        self.assertTrue(all(0 < n <= 64 for n in stages))
        self.assertLessEqual(sum(stages),256)
        self.assertEqual(sum(stages),len(NATIVE_OPS))
        self.assertEqual(self.args.reads.count('SkillInstigator'),1)
        self.assertEqual(self.args.reads.count('Definition'),1)
        self.assertEqual(self.definition.reads.count('Name'),1)
        self.assertEqual(self.players.indices,[0,0]); self.assertEqual(self.roster.indices,[0,0])
        self.assertTrue(self.call('stop_callback_local_reader'))
        self.assertTrue(self.has('OUTCOME epoch=1 value=OBSERVED_PRIMITIVE ownership=UNESTABLISHED'))

    def test_silence_is_not_observed_and_no_sdk_getters_on_stop(self):
        self.start()
        self.sdk.find_class = lambda _: (_ for _ in ()).throw(AssertionError('STOP metadata'))
        self.h.scope['get_pc'] = lambda **kw: (_ for _ in ()).throw(AssertionError('STOP pc'))
        self.assertTrue(self.call('stop_callback_local_reader'))
        self.assertTrue(self.has('OUTCOME epoch=1 value=NOT_OBSERVED'))

    def test_wrong_callback_types_and_poison_return_never_read(self):
        for index in (0,1,3):
            with self.subTest(index=index):
                self.setUp(); self.start()
                values = [self.obj,self.args,Poison(),self.bound]; values[index] = Poison()
                self.fire(values=values)
                self.assertTrue(self.has('REFUSED epoch=1 reason=SCHEMA'))
                self.assertNotIn('SkillInstigator',self.args.reads)

    def test_wrong_links_refuse_before_parameters(self):
        changes = [('args','_type',object()),('bound','object',object()),('bound','func',object()),
                   ('obj','Class',object()),('fn','Outer',object())]
        for holder, field, value in changes:
            with self.subTest(holder=holder,field=field):
                self.setUp(); setattr(getattr(self,holder),field,value); self.start(); self.fire()
                self.assertFalse(self.has('EVENT ')); self.assertNotIn('SkillInstigator',self.args.reads)

    def test_header_numeric_bool_and_bounds_refuse_before_getter(self):
        for field,value in (('FunctionFlags',True),('NumParams',4),('ParamsSize',13),
                ('ReturnValueOffset',0),('PropertySize',11),('PropertySize',1048577),
                ('SuperField',object()),('return_prop',object()),('Name','Wrong')):
            with self.subTest(field=field,value=value):
                self.setUp(); setattr(self.fn,field,value); self.start(); self.fire()
                self.assertFalse(self.has('EVENT ')); self.assertNotIn('SkillInstigator',self.args.reads)

    def test_all_property_shapes_refuse_before_values(self):
        for index in range(3):
            for field,value in (('PropertyFlags',True),('Offset_Internal',99),('ArrayDim',2),
                                ('ElementSize',8),('Outer',object()),('Name','Unexpected')):
                with self.subTest(index=index,field=field):
                    self.setUp(); setattr(self.props[index],field,value); self.start(); self.fire()
                    self.assertNotIn('SkillInstigator',self.args.reads)
                    self.assertFalse(self.has('EVENT '))

    def test_descriptor_membership_classes_extra_and_order_refuse(self):
        for change in ('lookup','class','extra','order','kind'):
            with self.subTest(change=change):
                self.setUp()
                if change=='lookup': self.fn.properties['Definition']=object()
                if change=='class': self.props[0].PropertyClass=self.controller
                if change=='extra': self.fn.ordered=self.props+[self.props[0]]
                if change=='order': self.fn.ordered=list(reversed(self.props))
                if change=='kind': self.fn.ordered=[Poison()]+self.props[1:]
                self.start();self.fire();self.assertNotIn('SkillInstigator',self.args.reads)

    def test_parameter_recheck_detects_change_before_second_getter(self):
        self.start()
        def drift(obj,key):
            if key=='SkillInstigator': self.props[0].PropertyFlags=129
        self.args.on_read=drift; self.fire()
        self.assertTrue(self.has('REFUSED epoch=1 reason=SCHEMA'))
        self.assertNotIn('Definition',self.args.reads)

    def test_null_instigator_foreign_class_and_foreign_wrapper_do_not_read_definition(self):
        for case in ('null','class','wrapper'):
            with self.subTest(case=case):
                self.setUp()
                self.args.Definition=Poison()
                self.args.SkillInstigator = (None if case=='null' else UObject(Class=self.declared)
                    if case=='class' else UObject(Class=self.controller))
                self.start();self.fire()
                expected={'null':'NULL_INSTIGATOR','class':'OTHER_CONTROLLER_CLASS','wrapper':'OTHER_WRAPPER'}[case]
                self.assertIn('controller='+expected+' definition=NOT_READ',self.event())
                self.assertNotIn('Definition',self.args.reads)

    def test_null_definition_and_other_name(self):
        for value,expected in ((None,'NULL_DEFINITION'),('Another_Skill','OTHER_NAME')):
            with self.subTest(expected=expected):
                self.setUp()
                if value is None:self.args.Definition=None
                else:self.definition.Name=value
                self.start();self.fire();self.assertIn('definition='+expected,self.event())
                self.assertTrue(self.call('stop_callback_local_reader'))
                self.assertTrue(self.has('OUTCOME epoch=1 value=OBSERVED_FILTERED'))

    def test_bad_definition_name_type_length_and_characters_never_logged(self):
        for value in (Poison(),'','A'*129,'private/path','bad\nname',True):
            with self.subTest(kind=type(value).__name__):
                self.setUp();self.definition.Name=value;self.start();self.fire()
                self.assertTrue(self.has('REFUSED epoch=1 reason=PARAMETER'))
                self.assertFalse(self.has('EVENT '))

    def test_unknown_subclasses_are_rejected_without_getters(self):
        class Unknown(WrappedStruct):pass
        self.args.__class__=Unknown;self.start();self.fire()
        self.assertEqual(self.args.reads,[])

    def test_player_loading_class_pawn_character_client_and_rosters_refuse(self):
        for case in ('loading','class','pawn','character','client','mode_bool','players','roster','owner','actor'):
            with self.subTest(case=case):
                self.setUp()
                if case=='loading':self.h.scope['get_pc']=lambda **kw:None
                if case=='class':self.pc.Class=self.declared
                if case=='pawn':self.pc.Pawn=None
                if case=='character':self.player_class.Name='OtherCharacter'
                if case=='client':self.world.NetMode=runtime.NetMode.NM_Client
                if case=='mode_bool':self.world.NetMode=True
                if case=='players':self.players.values=(self.local,self.local)
                if case=='roster':self.roster.values=()
                if case=='owner':self.pri.Owner=object()
                if case=='actor':self.local.Actor=object()
                self.start();self.fire()
                self.assertNotIn('Definition',self.args.reads)
                self.assertFalse(self.has('EVENT ') and case not in ('class',))

    def test_final_player_replacement_and_session_change_refuse(self):
        for case in ('pc','pawn','roster','owner','world','class'):
            with self.subTest(case=case):
                self.setUp();self.start()
                def drift(obj,key):
                    if key!='Name':return
                    if case=='pc':self.h.scope['get_pc']=lambda **kw:None
                    if case=='pawn':self.pc.Pawn=UObject()
                    if case=='roster':self.roster.values=()
                    if case=='owner':self.pri.Owner=object()
                    if case=='world':self.pc.WorldInfo=UObject(NetMode=runtime.NetMode.NM_Standalone,GRI=self.gri)
                    if case=='class':self.pc.Class=self.declared
                self.definition.on_read=drift;self.fire()
                self.assertTrue(self.has('REFUSED epoch=1 reason=PLAYER'))
                self.assertFalse(self.has('EVENT '))

    def test_return_and_boolean_arguments_poison_and_no_native_calls(self):
        self.args.bIgnoreSkillInstigator=Poison()
        self.start();self.fire();self.assertNotIn('bIgnoreSkillInstigator',self.args.reads)
        self.assertNotIn('__call__',self.bound.reads)

    def test_exception_is_not_formatted_or_retained(self):
        self.start()
        def error(obj,key):
            if key=='SkillInstigator':raise PrivateError('PRIVATE_PAYLOAD')
        self.args.on_read=error;self.fire()
        self.assertTrue(self.has('ERROR epoch=1 reason=INTERNAL'))
        self.assertFalse(any('PRIVATE_PAYLOAD' in x for x in self.h.logs))
        self.assertFalse(self.h.hooks)

    def test_nested_callback_reads_no_nested_payload(self):
        callback=self.start();once=[]
        def nested(obj,key):
            if key=='SkillInstigator' and not once:
                once.append(True);self.fire(callback,(Poison(),Poison(),Poison(),Poison()))
        self.args.on_read=nested;self.fire()
        self.assertEqual(self.h.scope['_cr_stats']['reentry'],1)
        self.assertEqual(self.h.scope['_cr_stats']['attempts'],1)
        self.assertEqual(self.h.scope['_cr_stats']['classified'],1)

    def test_stop_inside_getter_defers_removal_and_prevents_emission(self):
        self.start();seen=[]
        def stop(obj,key):
            if key=='SkillInstigator':
                seen.append(self.call('stop_callback_local_reader'))
                self.assertIn(self.key(),self.h.hooks)
        self.args.on_read=stop;self.fire()
        self.assertEqual(seen,[False]);self.assertFalse(self.h.hooks)
        self.assertFalse(self.has('EVENT '))

    def test_count_limit_and_stale_epoch_cannot_rearm(self):
        old=self.start()
        for _ in range(24):self.fire(old)
        self.assertFalse(self.h.hooks);self.assertFalse(self.h.scope['_cr_accepting'])
        self.assertTrue(self.has('LIMIT reason=EVENTS'))
        self.start();self.fire(old,(Poison(),Poison(),Poison(),Poison()))
        self.assertEqual(self.h.scope['_cr_stats']['attempts'],0)

    def test_attempt_limit_includes_last_valid_attempt(self):
        self.start();self.h.scope['_cr_stats']['attempts']=63;self.fire()
        self.assertEqual(self.h.scope['_cr_stats']['attempts'],64)
        self.assertTrue(self.has('LIMIT reason=ATTEMPTS'));self.assertFalse(self.h.hooks)

    def test_time_clock_regression_and_end_of_getter_timeout(self):
        for case in ('time','regress','nan','end'):
            with self.subTest(case=case):
                self.setUp();self.start()
                if case=='time':self.clock=1120.0
                if case=='regress':self.clock=999.0
                if case=='nan':self.clock=float('nan')
                if case=='end':
                    self.props[0].on_read=lambda obj,key:setattr(self,'clock',1120.0) if key=='ElementSize' else None
                self.fire();self.assertFalse(self.has('EVENT '));self.assertFalse(self.h.hooks)

    def test_failed_removal_is_inert_retained_and_retryable(self):
        old=self.start();self.h.fail_remove=True
        self.assertFalse(self.call('stop_callback_local_reader'))
        self.assertIsNotNone(self.h.scope['_cr_pending'])
        self.assertFalse(self.call('start_callback_local_reader'))
        self.fire(old,(Poison(),Poison(),Poison(),Poison()))
        self.h.fail_remove=False;self.assertTrue(self.call('stop_callback_local_reader'))
        self.assertEqual(self.h.scope['_cr_stats']['cleanup_failures'],1)
        self.assertTrue(self.has('OUTCOME epoch=1 value=REFUSED'))

    def test_registration_uncertainty_never_removes_unknown_hook(self):
        foreign=lambda *args:None
        def broken_add(*values):
            self.h.hooks[self.key()]=foreign
            raise PrivateError('PRIVATE')
        self.sdk.hooks.add_hook=broken_add
        self.assertFalse(self.call('start_callback_local_reader'))
        self.assertIs(self.h.hooks[self.key()],foreign)
        self.assertFalse(self.call('start_callback_local_reader'))
        self.h.hooks.clear();self.assertTrue(self.call('stop_callback_local_reader'))

    def test_existing_identifier_is_not_removed(self):
        foreign=lambda *args:None;self.h.hooks[self.key()]=foreign
        self.assertFalse(self.call('start_callback_local_reader'))
        self.assertIs(self.h.hooks[self.key()],foreign)

    def test_controls_mutually_exclude_and_cancel_disable_remove_reader(self):
        self.start()
        for index in list(range(2))+list(range(3,21)):
            self.h.scope['option']=self.h.mod_options['options'][index]['on_press']
            self.assertFalse(self.call('option'))
        self.assertTrue(self.h.hooks)
        self.call('cancel_init_node');self.assertFalse(self.h.hooks)
        self.start();self.call('shutdown');self.assertFalse(self.h.hooks)

    def test_old_contexts_and_manual_record_block_start_without_native_reads(self):
        for key,value in (('_init_armed',True),('_init_hooks',[object()]),('_uvh_node_state',object()),
                ('_record',object()),('_trace_hooks',[object()]),('_upgrade_context',object()),
                ('_ui_context',object()),('_skillstate_context',object()),('_dt_event_uncertain',[object()])):
            with self.subTest(key=key):
                self.setUp();self.h.scope[key]=value
                self.assertFalse(self.call('start_callback_local_reader'));self.assertEqual(self.lookups,[])

    def test_epoch_clock_and_registration_boolean_guards(self):
        for case in ('epoch','clock','addtype','has_type','missing'):
            with self.subTest(case=case):
                self.setUp()
                if case=='epoch':self.h.scope['_cr_epoch']=2147483647
                if case=='clock':self.clock=float('nan')
                if case=='addtype':self.sdk.hooks.add_hook=lambda *v:None
                if case=='has_type':self.sdk.hooks.has_hook=lambda *v:None
                if case=='missing':self.sdk.hooks.add_hook=lambda *v:True
                self.assertFalse(self.call('start_callback_local_reader'))

    def test_state_closure_and_log_do_not_escape_native_values(self):
        callback=self.start();self.fire()
        self.assertEqual(tuple(c.cell_contents for c in callback.__closure__),(1,))
        def primitive(value):
            if type(value) in (type(None),bool,int,float,str):return True
            if type(value) in (tuple,list):return all(primitive(v) for v in value)
            if type(value) is dict:return all(type(k)is str and primitive(v) for k,v in value.items())
            return False
        for key,value in self.h.scope.items():
            if key.startswith('_cr_') and not callable(value):self.assertTrue(primitive(value),key)
        self.assertTrue(all(type(x)is str and len(x.encode('utf-8'))<=384 for x in self.h.logs))
        obj_ref,args_ref,bound_ref=map(weakref.ref,(self.obj,self.args,self.bound))
        self.obj=self.args=self.bound=None;gc.collect()
        self.assertIsNone(obj_ref());self.assertIsNone(args_ref());self.assertIsNone(bound_ref())

    def test_callback_ret_unused_and_exact_none_on_all_returns_ast(self):
        tree=ast.parse(runtime.SOURCE.read_text(encoding='utf-8'))
        outer=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_cr_callback')
        observe=next(n for n in outer.body if isinstance(n,ast.FunctionDef))
        self.assertFalse(any(isinstance(n,ast.Name) and n.id=='ret' and isinstance(n.ctx,ast.Load)
                             for n in ast.walk(observe)))
        self.assertTrue(all(isinstance(n.value,ast.Constant) and n.value.value is None
                            for n in ast.walk(observe) if isinstance(n,ast.Return)))

    def test_operation_budget_counts_before_access_and_caps_stage_and_total(self):
        self.start()
        budget=self.h.scope['_CRBudget'](1)
        self.h.scope['budget']=budget
        with patch('time.monotonic',lambda:self.clock):
            for stage in range(4):
                budget.stage=stage
                for _ in range(64):budget.tick()
                with self.assertRaises(self.h.scope['_CRRefusal']):budget.get(Poison(),'Name')
        self.assertEqual(budget.counts,[64]*4)

    def test_return_descriptor_and_superfield_drift_refuse_before_parameter(self):
        for case in ('return','super'):
            with self.subTest(case=case):
                self.setUp();self.start()
                def drift(obj,key):
                    if key=='SkillInstigator':
                        if case=='return':self.fn.return_prop=object()
                        else:self.fn.SuperField=object()
                self.args.on_read=drift;self.fire()
                self.assertFalse(self.has('EVENT '));self.assertNotIn('Definition',self.args.reads)

    def test_second_parameter_schema_is_checked_again_after_player_probe(self):
        self.start()
        self.player_class.on_read=lambda obj,key:setattr(self.props[1],'ElementSize',8) if key=='Name' else None
        self.fire();self.assertNotIn('Definition',self.args.reads)
        self.assertTrue(self.has('REFUSED epoch=1 reason=SCHEMA'))

    def test_definition_type_class_and_post_getter_schema_refusals(self):
        for case in ('type','class','post'):
            with self.subTest(case=case):
                self.setUp();self.start()
                if case=='type':self.args.Definition=Poison()
                if case=='class':self.definition.Class=self.controller
                if case=='post':
                    self.args.on_read=lambda obj,key:setattr(self.props[1],'ArrayDim',2) if key=='Definition' else None
                self.fire();self.assertFalse(self.has('EVENT '))
                self.assertNotIn('Name',self.definition.reads)

    def test_logging_failure_stops_and_never_claims_classification(self):
        self.start()
        self.h.scope['log']=lambda message:(_ for _ in ()).throw(PrivateError('SECRET'))
        self.fire();self.assertFalse(self.h.hooks)
        self.assertEqual(self.h.scope['_cr_stats']['classified'],0)
        self.assertGreater(self.h.scope['_cr_stats']['errors'],0)

    def test_start_cancellation_and_registration_reentry_never_accept_payload(self):
        for case in ('cancel','reentry'):
            with self.subTest(case=case):
                self.setUp();original=self.sdk.hooks.add_hook
                def add(path,phase,ident,callback):
                    result=original(path,phase,ident,callback)
                    if case=='cancel':self.assertFalse(self.call('stop_callback_local_reader'))
                    else:self.fire(callback,(Poison(),Poison(),Poison(),Poison()))
                    return result
                self.sdk.hooks.add_hook=add
                result=self.call('start_callback_local_reader')
                self.assertEqual(result,case=='reentry')
                self.assertEqual(self.h.scope['_cr_stats']['attempts'],0)
                if case=='cancel':self.assertFalse(self.h.hooks)

    def test_removal_unknown_return_is_failure_even_when_hook_disappears(self):
        self.start();original=self.sdk.hooks.remove_hook
        def remove(*values):original(*values);return None
        self.sdk.hooks.remove_hook=remove
        self.assertFalse(self.call('stop_callback_local_reader'))
        self.assertIsNotNone(self.h.scope['_cr_pending'])
        self.sdk.hooks.remove_hook=original
        self.assertTrue(self.call('stop_callback_local_reader'))
        self.assertTrue(self.has('OUTCOME epoch=1 value=REFUSED'))

    def test_manager_class_change_at_definition_is_refused_before_log(self):
        self.start()
        self.definition.on_read=lambda obj,key:setattr(self.obj,'Class',self.controller) if key=='Name' else None
        self.fire();self.assertFalse(self.has('EVENT '))

    def test_fresh_array_view_wrappers_with_same_members_are_accepted(self):
        self.start()
        self.engine.on_read=lambda obj,key:setattr(obj,'GamePlayers',WrappedArray(self.local)) if key=='GamePlayers' else None
        self.gri.on_read=lambda obj,key:setattr(obj,'PRIArray',WrappedArray(self.pri)) if key=='PRIArray' else None
        self.fire();self.assertIn('controller=SAME_WRAPPER definition=DEATHTRAP_NAME',self.event())

    def test_malformed_array_and_missing_player_field_are_not_false_zero(self):
        for case in ('array','field'):
            with self.subTest(case=case):
                self.setUp()
                if case=='array':self.engine.GamePlayers=Poison()
                else:del self.pc.Pawn
                self.start();self.fire();self.assertFalse(self.has('EVENT '))
                self.assertNotIn('Definition',self.args.reads)

    def test_stale_global_epoch_blocks_all_payload_access(self):
        callback=self.start();self.h.scope['_cr_epoch']=2
        self.fire(callback,(Poison(),Poison(),Poison(),Poison()))
        self.assertEqual(self.h.scope['_cr_stats']['attempts'],0)

    def test_primitive_emit_length_and_fixed_label_contract(self):
        self.assertFalse(self.h.scope['_cr_emit'](Poison()))
        self.assertFalse(self.h.scope['_cr_emit']('A'*385))
        self.assertTrue(self.h.scope['_cr_emit']('CONTROL reason=TEST'))
        self.start();self.fire();self.call('stop_callback_local_reader')
        self.assertTrue(all(len(x.encode('utf-8'))<=384 for x in self.h.logs))

    def test_malformed_internal_refusal_stays_in_inspection_frame(self):
        self.start()
        self.args.on_read=lambda obj,key:(_ for _ in ()).throw(self.h.scope['_CRRefusal']()) if key=='SkillInstigator' else None
        self.fire();self.assertTrue(self.has('REFUSED epoch=1 reason=INTERNAL'))
        self.assertFalse(self.has('EVENT '));self.assertFalse(self.h.hooks)


if __name__=='__main__':unittest.main()
