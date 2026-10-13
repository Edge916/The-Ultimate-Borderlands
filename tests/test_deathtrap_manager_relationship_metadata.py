"""Inert metadata access/cleanup transcripts; never SDK binding or native lifetime proof."""
import ast
import gc
import inspect
import json
import sys
import types
import unittest
import weakref
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import test_runtime_mock as runtime

SOURCE = Path(__file__).resolve().parents[1] / 'sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py'
OPS = []
ON_OP = None
FORBIDDEN = {'SkillInstigator','Definition','AdditionalSkillTarget','SkillGrade','StateChangeDelegate',
    'ReturnValue','Pawn','PlayerClass','WorldInfo','PlayerReplicationInfo','ActiveSkills','Duration',
    'GetSkillManager','FieldMask','Signature','ClassDefaultObject','_path_name','_get_address'}
FIELDS = {'Class','Name','Outer','SuperField','PropertySize','PropertyLink','PropertyLinkNext',
    'PropertyFlags','Offset_Internal','ArrayDim','ElementSize','PropertyClass',
    'FunctionFlags','NumParams','ParamsSize','ReturnValueOffset','_type','func','object',
    '_find','_properties','_find_prop','_find_return_param'}

def record(kind, label, field=''):
    frame = inspect.currentframe()
    stage = None
    try:
        while frame is not None:
            if frame.f_code.co_name == '_rm_collect':
                stage = frame.f_locals['budget'].stage
                break
            frame = frame.f_back
    finally:
        del frame
    item = (stage,kind,label,field)
    OPS.append(item)
    if ON_OP is not None:
        ON_OP(item)

class Node:
    def __init__(self, label, **fields):
        self.__dict__.update(fields, _label=label)
    def __getattribute__(self, field):
        if field in FORBIDDEN:
            raise AssertionError('forbidden payload getter')
        if field in FIELDS:
            record('get',object.__getattribute__(self,'_label'),field)
        return object.__getattribute__(self,field)
    def __bool__(self): raise AssertionError('native truth')
    def __eq__(self, other): raise AssertionError('native equality')
    def __repr__(self): raise AssertionError('native repr')
    def __str__(self): raise AssertionError('native str')

class UObject(Node): pass
class UClass(UObject):
    def _find(self, name):
        record('method',self._label,'_find')
        return self._functions[name]
class UField(UObject): pass
class ZProperty(UField): pass
class ZObjectProperty(ZProperty): pass
class ZBoolProperty(ZProperty): pass
class ZIntProperty(ZProperty): pass
class ZDelegateProperty(ZProperty): pass
class ObjectSubtype(ZObjectProperty): pass
class Iterator:
    def __init__(self, values): self.values=iter(values)
    def __next__(self):
        record('next','function')
        return next(self.values)
class UFunction(UField):
    def _find_prop(self, name):
        record('method',self._label,'_find_prop')
        return self._props[name]
    def _properties(self):
        record('method',self._label,'_properties')
        return Iterator(self._ordered)
    def _find_return_param(self):
        record('method',self._label,'_find_return_param')
        return self._ordered[-1]
    def __call__(self,*args): raise AssertionError('engine invocation')
class WrappedStruct(Node): pass
class BoundFunction(Node):
    def __call__(self,*args): raise AssertionError('bound invocation')
class Poison:
    def __getattribute__(self,key): raise AssertionError('ignored payload accessed')
    def __repr__(self): raise AssertionError('ignored repr')
    def __str__(self): raise AssertionError('ignored str')
class PrivateError(Exception):
    def __str__(self): raise AssertionError('private exception formatted')

class RelationshipMetadataTests(unittest.TestCase):
    def setUp(self):
        global ON_OP
        ON_OP=None
        self.h=runtime.Harness(source=SOURCE.read_bytes())
        self.sdk=self.h.sdk
        self.sdk.unreal=types.SimpleNamespace(UObject=UObject,UClass=UClass,UField=UField,
            ZProperty=ZProperty,ZObjectProperty=ZObjectProperty,ZBoolProperty=ZBoolProperty,
            ZIntProperty=ZIntProperty,ZDelegateProperty=ZDelegateProperty,UFunction=UFunction,
            WrappedStruct=WrappedStruct,BoundFunction=BoundFunction)
        paths=self.h.scope['_RM_CLASS_PATHS']
        sizes=(940,1600,1500,1400,1300,1100,600,64)
        self.classes=[UClass(str(i),Name=p.rsplit('.',1)[-1],PropertySize=sizes[i],PropertyLink=None,
            _functions={}) for i,p in enumerate(paths)]
        for i,parent in enumerate((6,2,3,4,5,6,7,None)):
            self.classes[i].SuperField=None if parent is None else self.classes[parent]
        self.lookup=dict(zip(paths,self.classes))
        self.definition=UClass('definition_class',Name='SkillDefinition')
        self.lookup['WillowGame.SkillDefinition']=self.definition
        def find_class(path):
            record('lookup','class',path)
            return self.lookup[path]
        self.sdk.find_class=find_class
        self.fn=UFunction('function',Name='ActivateSkill',Outer=self.classes[0],FunctionFlags=149506,
            NumParams=6,ParamsSize=32,ReturnValueOffset=28,PropertySize=32,SuperField=None)
        self.classes[0]._functions['ActivateSkill']=self.fn
        props=[]
        for name,kind,flags,offset,size,decl in (
            ('SkillInstigator',ZObjectProperty,128,0,4,self.classes[5]),
            ('Definition',ZObjectProperty,128,4,4,self.definition),
            ('AdditionalSkillTarget',ZObjectProperty,144,8,4,self.classes[7]),
            ('SkillGrade',ZIntProperty,144,12,4,None),
            ('StateChangeDelegate',ZDelegateProperty,4194448,16,12,None),
            ('ReturnValue',ZBoolProperty,1408,28,4,None)):
            props.append(kind(name,Name=name,Outer=self.fn,PropertyFlags=flags,Offset_Internal=offset,
                ArrayDim=1,ElementSize=size,PropertyClass=decl))
        self.fn._ordered=props
        self.fn._props={object.__getattribute__(p,'Name'):p for p in props}
        self.obj=UObject('manager',Class=self.classes[0])
        self.args=WrappedStruct('args',_type=self.fn)
        self.bound=BoundFunction('bound',object=self.obj,func=self.fn)
        self.other=UClass('other',Name='SyntheticOther')
        self.mgr=[self.prop('SyntheticControllerSlot',0,5),self.prop('SyntheticOtherSlot',0,None)]
        self.ctrl=[self.prop('SyntheticManagerSlot',1,0),self.prop('SyntheticScalar',1,kind=ZIntProperty)]
        self.link(0,self.mgr)
        self.link(1,self.ctrl)
        self.clock=1000.0
        self.h.scope['get_pc']=lambda **kw: (_ for _ in ()).throw(AssertionError('player value helper'))
        self.h.logs.clear()
        OPS.clear()
    def tearDown(self):
        global ON_OP
        ON_OP=None
        self.assertEqual(self.h.loads,[])
        self.assertEqual(self.h.constructed,[])
    def prop(self,name,owner,decl=None,kind=ZObjectProperty,**values):
        fields=dict(Name=name,Outer=self.classes[owner],PropertyFlags=0,Offset_Internal=16,
            ArrayDim=1,ElementSize=4,PropertyLinkNext=None,PropertyClass=self.other if decl is None else self.classes[decl])
        fields.update(values)
        return kind(name,**fields)
    def link(self,root,props):
        self.classes[root].PropertyLink=props[0] if props else None
        for i,prop in enumerate(props): prop.PropertyLinkNext=props[i+1] if i+1<len(props) else None
    def call(self,name,*args):
        with patch('time.monotonic',lambda:self.clock): return self.h.call(name,*args)
    def key(self): return (self.h.scope['_RM_PATH'],'pre',self.h.scope['_RM_IDENT'])
    def start(self):
        self.assertTrue(self.call('start_relationship_metadata'))
        return self.h.hooks[self.key()]
    def fire(self,cb=None,values=None):
        if cb is None: cb=self.h.hooks[self.key()]
        if values is None: values=(self.obj,self.args,Poison(),self.bound)
        with patch.dict(sys.modules,{'unrealsdk':self.sdk,'mods_base':self.h.base}),patch('time.monotonic',lambda:self.clock):
            self.assertIsNone(cb(*values))
    def records(self,event=None):
        rows=[json.loads(line.split('[UVH-REL-META] ',1)[1]) for line in self.h.logs if '[UVH-REL-META] ' in line]
        return rows if event is None else [r for r in rows if r['event']==event]
    def refused(self):
        self.start();self.fire()
        self.assertEqual(self.records('END')[-1]['outcome'],'REFUSED')
    def test_import_start_no_native_access_and_version_options(self):
        self.assertEqual(self.h.mod_options['version'],'0.2.19')
        self.assertEqual(len(self.h.mod_options['options']),25)
        self.assertEqual(self.h.mod_options['name'],'UVH v0.2.19 - RELATIONSHIP CLASS METADATA')
        self.start()
        self.assertEqual(OPS,[])
        self.assertEqual(self.records('START')[0]['hooks'],1)
    def test_complete_exact_operation_transcripts_and_known_other_fields(self):
        self.start();self.fire()
        end=self.records('END')[0]
        self.assertEqual([end[k] for k in ('gate_ops','root_ops','mgr_ops','ctrl_ops')],[98,68,54,51])
        self.assertEqual(Counter(x[0] for x in OPS),{0:98,1:68,2:54,3:51})
        self.assertEqual(end['outcome'],'COMPLETE_SCOPED_METADATA')
        self.assertEqual([r['decl'] for r in self.records('ROW')],['CONTROLLER','MGR'])
        self.assertEqual(self.records('ROOT')[0]['other'],1)
        self.assertEqual(len(self.h.hooks),1)
        self.assertTrue(self.call('stop_relationship_metadata'))
        self.assertFalse(self.h.hooks)
        self.assertEqual(self.records('STOP')[-1]['remaining'],0)
    def test_empty_links_and_no_payload_reads(self):
        self.link(0,[]);self.link(1,[])
        self.start();self.fire()
        self.assertFalse(self.records('ROW'))
        self.assertEqual(self.records('END')[0]['total_ops'],166)
        self.assertFalse(any(op[3] in FORBIDDEN for op in OPS))
    def test_single_attempt_later_and_stale_callbacks_ignore_everything(self):
        cb=self.start();self.fire(cb)
        OPS.clear();self.fire(cb, (Poison(),Poison(),Poison(),Poison()))
        self.assertEqual(OPS,[])
        self.assertEqual(len(self.records('BEGIN')),1)
        self.call('stop_relationship_metadata');self.start()
        self.fire(cb,(Poison(),Poison(),Poison(),Poison()))
        self.assertEqual(OPS,[])
    def test_cycle_rejected(self):
        self.mgr[-1].PropertyLinkNext=self.mgr[0]
        self.refused()
        self.assertEqual(self.records('ROOT')[0]['reason'],'CYCLE')
    def test_duplicate_owner_name_rejected(self):
        self.mgr[1].Name='SyntheticControllerSlot'
        self.refused()
        self.assertEqual(self.records('ROOT')[0]['reason'],'DUPLICATE')
    def test_foreign_owner_rejected(self):
        self.mgr[0].Outer=self.classes[1]
        self.refused()
        self.assertEqual(self.records('ROOT')[0]['reason'],'OWNER')
    def test_changed_link_rejected(self):
        global ON_OP
        calls=0
        def mutate(op):
            nonlocal calls
            if op[2]=='SyntheticControllerSlot' and op[3]=='PropertyLinkNext':
                calls+=1
                if calls==2: object.__setattr__(self.mgr[0],'PropertyLinkNext',None)
        ON_OP=mutate
        self.refused()
        self.assertEqual(self.records('ROOT')[0]['reason'],'LINK')
    def test_invalid_numeric_and_name_variants_refuse_without_private_output(self):
        for field,value in [('PropertyFlags',True),('PropertyFlags',-1),('PropertyFlags',2**64),
            ('Offset_Internal',False),('ArrayDim',0),('ArrayDim',1025),('ElementSize',0),
            ('ElementSize',8),('Offset_Internal',940),('Name','private/path'),('Name','Z'*129)]:
            with self.subTest(field=field,value=value):
                self.setUp()
                setattr(self.mgr[0],field,value)
                self.refused()
                self.assertNotIn('private/path','\n'.join(self.h.logs))
    def test_inherited_owner_and_non_scalar_metadata(self):
        self.link(0,[self.prop('SyntheticInherited',6,5,ArrayDim=2)])
        self.start();self.fire()
        row=self.records('ROW')[0]
        self.assertEqual((row['owner'],row['kind'],row['dim']),(1,'NON_SCALAR',2))
    def test_unsupported_object_subtype_is_counted_not_followed(self):
        self.link(0,[self.prop('SyntheticSubtype',0,kind=ObjectSubtype)])
        self.start();self.fire()
        self.assertEqual(self.records('ROOT')[0]['unsupported'],1)
        self.assertFalse(any(op[2]=='SyntheticSubtype' and op[3]=='PropertyClass' for op in OPS))
    def test_max_flag_and_name_message_bound(self):
        self.mgr[0].Name='Z'*128;self.mgr[0].PropertyFlags=2**64-1
        self.start();self.fire()
        row=self.records('ROW')[0]
        self.assertEqual(row['flags'],2**64-1)
        self.assertTrue(all(len(line.encode('ascii'))<=512 for line in self.h.logs if '[UVH-REL-META]' in line))
    def test_property_limit_is_partial_with_complete_prefix_rechecks(self):
        self.link(0,[self.prop('P'+str(i),0,kind=ZIntProperty) for i in range(513)])
        self.start();self.fire()
        root=self.records('ROOT')[0]
        self.assertEqual((root['coverage'],root['reason'],root['visited'],root['rechecked'],root['ops']),
            ('PARTIAL','PROPERTY_LIMIT',512,512,512*24))
        self.assertEqual(self.records('END')[0]['outcome'],'PARTIAL_METADATA')
    def test_row_limit_and_maximum_rows(self):
        self.link(0,[self.prop('P'+str(i),0,5) for i in range(65)])
        self.start();self.fire()
        root=self.records('ROOT')[0]
        self.assertEqual((root['coverage'],root['reason'],root['rows']),('PARTIAL','ROW_LIMIT',64))
        self.assertEqual(len(self.records('ROW')),65)
    def test_reentry_refuses_before_another_native_operation(self):
        global ON_OP
        cb=self.start()
        triggered=False
        def nested(op):
            nonlocal triggered
            if not triggered:
                triggered=True
                self.fire(cb,(Poison(),Poison(),Poison(),Poison()))
        ON_OP=nested
        self.fire(cb)
        self.assertEqual(len(OPS),1)
        self.assertEqual(self.records('END')[0]['outcome'],'REFUSED')
        self.assertEqual(self.records('END')[0]['reentry'],1)
    def test_time_limit_after_last_native_get_refuses(self):
        global ON_OP
        self.start()
        def advance(op):
            if len(OPS)==271: self.clock+=2.0
        ON_OP=advance
        self.fire()
        self.assertEqual(self.records('END')[0]['outcome'],'REFUSED')
        self.assertFalse(self.records('ROW'))
    def test_busy_stop_defers_and_requires_explicit_stop(self):
        global ON_OP
        self.start()
        done=False
        def stop(op):
            nonlocal done
            if not done:
                done=True
                self.assertFalse(self.call('stop_relationship_metadata'))
        ON_OP=stop
        self.fire()
        self.assertTrue(self.records('STOP')[0]['deferred'])
        self.assertEqual(self.records('END')[0]['outcome'],'REFUSED')
        self.assertTrue(self.h.hooks)
        ON_OP=None
        self.assertTrue(self.call('stop_relationship_metadata'))
        self.assertFalse(self.h.hooks)
    def test_cleanup_failure_history_and_retry_are_preserved(self):
        self.start();self.fire()
        self.h.fail_remove=True
        self.assertFalse(self.call('stop_relationship_metadata'))
        self.assertEqual(self.records('STOP')[-1]['removal_attempts'],4)
        self.assertEqual(self.records('STOP')[-1]['cleanup_failures'],4)
        self.h.fail_remove=False
        self.assertTrue(self.call('stop_relationship_metadata'))
        self.assertEqual(self.records('STOP')[-1]['cleanup_failures'],4)
        self.assertEqual(self.records('STOP')[-1]['outcome'],'REFUSED')
    def test_unowned_identifier_never_removed_or_adopted(self):
        self.h.hooks[self.key()]=lambda *args:None
        self.assertFalse(self.call('start_relationship_metadata'))
        self.assertTrue(self.h.hooks)
        self.assertEqual(self.h.scope['_rm_stats']['removal_attempts'],0)
    def test_silence_and_repeated_stop(self):
        self.start();self.call('stop_relationship_metadata');self.call('stop_relationship_metadata')
        self.assertEqual(len(self.records('END')),1)
        self.assertEqual(self.records('END')[0]['outcome'],'NOT_OBSERVED')
        self.assertEqual(len(self.records('STOP')),2)
    def test_all_old_options_and_direct_start_surfaces_refuse_overlap(self):
        self.start();OPS.clear()
        for option in self.h.mod_options['options'][:23]:
            if option['display_name'].startswith('3 -'): continue
            self.assertFalse(option['on_press']())
        for name in ('arm_init_node','start_tree_trace','start_upgrade_trace','start_ui_trace',
            'start_skillstate_trace','start_deathtrap_events','start_callback_local_reader'):
            self.assertFalse(self.call(name))
        self.assertEqual(OPS,[])
        self.assertEqual(len(self.h.hooks),1)
    def test_cancel_and_disable_stop_new_handles_without_manual_restore(self):
        for name in ('cancel_init_node','shutdown'):
            self.setUp();self.start()
            self.h.scope['restore']=lambda *a: (_ for _ in ()).throw(AssertionError('manual restore'))
            self.call(name)
            self.assertFalse(self.h.hooks)
            self.assertEqual(self.records('STOP')[-1]['remaining'],0)
    def test_clock_failure_does_not_register(self):
        for value in (float('nan'),-1.0,True):
            self.setUp();self.clock=value
            self.assertFalse(self.call('start_relationship_metadata'))
            self.assertFalse(self.h.hooks)
            self.assertEqual(OPS,[])
    def test_unknown_add_outcome_never_removes_uncertain_foreign_handle(self):
        def add(path,phase,ident,cb):
            self.h.hooks[(path,phase,ident)]=cb
            raise PrivateError()
        self.sdk.hooks.add_hook=add
        self.assertFalse(self.call('start_relationship_metadata'))
        self.assertTrue(self.h.hooks)
        self.assertEqual(self.records('STOP')[-1]['uncertain'],1)
        self.assertFalse(self.call('start_relationship_metadata'))
    def test_primitive_stats_epoch_closure_and_no_native_cell_assignments(self):
        cb=self.start();self.fire(cb)
        self.assertEqual(cb.__code__.co_freevars,('epoch',))
        def primitive(value):
            if type(value) in (str,int,bool,float,type(None)): return True
            if type(value) in (list,tuple): return all(primitive(v) for v in value)
            if type(value) is dict: return all(type(k)is str and primitive(v) for k,v in value.items())
            return False
        self.assertTrue(primitive(self.h.scope['_rm_stats']))
        nodes={n.name:n for n in ast.parse(SOURCE.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
        for name,node in nodes.items():
            if name.startswith('_rm_') or name=='_RMBudget':
                self.assertFalse(any(isinstance(n,(ast.Assign,ast.AugAssign,ast.AnnAssign)) and
                    any(isinstance(t,ast.Attribute) and not (isinstance(t.value,ast.Name) and t.value.id=='budget' and t.attr=='stage')
                        for t in (n.targets if isinstance(n,ast.Assign) else [n.target]))
                    and name!='_RMBudget' for n in ast.walk(node)))
    def test_final_root_head_change_suppresses_every_staged_row(self):
        global ON_OP
        self.start()
        def change(op):
            if len(OPS)==270: object.__setattr__(self.classes[0],'PropertyLink',None)
        ON_OP=change;self.fire()
        self.assertEqual(self.records('END')[0]['outcome'],'REFUSED')
        self.assertFalse(self.records('ROW'))
    def test_class_chain_changes_and_invalid_binding_shape_refuse(self):
        for mutation in ('name','super','size','shape','function'):
            self.setUp()
            if mutation=='name': self.classes[2].Name='Unexpected'
            elif mutation=='super': self.classes[2].SuperField=None
            elif mutation=='size': self.classes[0].PropertySize=419
            elif mutation=='shape': self.sdk.unreal.UField=str
            else: self.fn.NumParams=5
            self.refused()
            self.assertFalse(self.records('ROW'))
    def test_bool_integer_and_private_refusal_reason_never_leak(self):
        global ON_OP
        self.start()
        def fail(op): raise self.h.scope['_RMRefusal']('private/path/token')
        ON_OP=fail;self.fire()
        self.assertEqual(self.records('FAULT')[0]['reason'],'INTERNAL')
        self.assertNotIn('private/path/token','\n'.join(self.h.logs))
    def test_private_sdk_exception_is_fixed_internal_error(self):
        global ON_OP
        self.start()
        def fail(op): raise PrivateError(Poison())
        ON_OP=fail;self.fire()
        self.assertEqual(self.records('FAULT')[0]['reason'],'INTERNAL')
    def test_budget_checks_before_lookup_and_native_getter(self):
        self.start()
        scope=self.h.scope
        scope['_rm_busy']=True
        scope['_rm_stats']['collector_started']=self.clock
        with patch('time.monotonic',lambda:self.clock):
            budget=scope['_RMBudget'](scope['_rm_epoch'])
            budget.counts[0]=112
            with self.assertRaises(scope['_RMRefusal']): budget.lookup(self.sdk.find_class,'Core.Object')
            self.assertEqual(OPS,[])
        scope['_rm_busy']=False
    def test_ignored_and_reentry_counter_saturation_are_explicit(self):
        cb=self.start();self.fire(cb)
        for _ in range(66): self.fire(cb,(Poison(),Poison(),Poison(),Poison()))
        self.call('stop_relationship_metadata')
        self.assertEqual(self.records('STOP')[-1]['ignored'],64)
        self.assertTrue(self.records('STOP')[-1]['ignored_saturated'])
    def test_control_log_cap_does_not_reopen_collector(self):
        self.start();self.call('stop_relationship_metadata')
        for _ in range(70): self.call('stop_relationship_metadata')
        self.assertEqual(len(self.records('STOP')),64)
        self.assertTrue(self.h.scope['_rm_stats']['truncated'])
        self.assertFalse(self.call('start_relationship_metadata'))
        self.assertFalse(self.h.hooks)
    def test_logging_failure_stays_inert_and_cleanup_does_not_reread(self):
        cb=self.start()
        self.sdk.logging.info=lambda text: (_ for _ in ()).throw(PrivateError())
        self.fire(cb)
        self.assertTrue(self.h.scope['_rm_stats']['truncated'])
        OPS.clear();self.fire(cb,(Poison(),Poison(),Poison(),Poison()))
        self.assertEqual(OPS,[])
        self.call('stop_relationship_metadata')
        self.assertFalse(self.h.hooks)
        self.assertFalse(self.call('start_relationship_metadata'))
    def test_session_timeout_on_callback_and_control_preserves_fault(self):
        self.start();self.clock+=120.0;self.fire()
        self.assertEqual(OPS,[])
        self.call('stop_relationship_metadata')
        self.assertFalse(self.h.hooks)
        self.assertEqual(self.records('STOP')[-1]['outcome'],'REFUSED')
        self.assertTrue(any(r['reason']=='TIME' for r in self.records('FAULT')))
    def test_payload_reference_dropped_before_logging(self):
        cb=self.start()
        sentinel=UObject('unused')
        weak=weakref.ref(sentinel)
        self.args=WrappedStruct('args',_type=self.fn)
        self.bound=BoundFunction('bound',object=self.obj,func=self.fn)
        # The unused ret is not held in collector globals or output.
        self.fire(cb, (self.obj,self.args,sentinel,self.bound))
        del sentinel;gc.collect()
        self.assertIsNone(weak())
    def test_maximum_full_object_walk_with_other_declarations(self):
        self.link(0,[self.prop('P'+str(i),0,None) for i in range(512)])
        self.link(1,[self.prop('Q'+str(i),1,None) for i in range(512)])
        self.start();self.fire()
        end=self.records('END')[0]
        self.assertEqual((end['total_ops'],end['mgr_ops'],end['ctrl_ops']),(27814,13824,13824))
        self.assertEqual(end['outcome'],'COMPLETE_SCOPED_METADATA')
        self.assertFalse(self.records('ROW'))
    def test_two_roots_maximum_known_rows_are_bounded(self):
        self.link(0,[self.prop('P'+str(i),0,5) for i in range(64)])
        self.link(1,[self.prop('Q'+str(i),1,0) for i in range(64)])
        self.start();self.fire()
        self.assertEqual(len(self.records('ROW')),128)
        self.assertEqual(self.records('END')[0]['outcome'],'COMPLETE_SCOPED_METADATA')

if __name__=='__main__': unittest.main()
