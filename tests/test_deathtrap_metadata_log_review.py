"""Synthetic metadata text; none of these fixtures is a human/game capture."""
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('deathtrap_log_tool',
    Path(__file__).resolve().parents[1]/'scripts/review_deathtrap_metadata_log.py')
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


def root(target, name):
    return {'kind':'CLASS','target':target,'path':'Test.'+name,'coverage':'COMPLETE',
            'ancestry':[{'name':name,'path':'Test.'+name}]}


def prop(name, flags=3, offset=0):
    return {'name':name,'type':'ZObjectProperty','flags':flags,'offset':offset,'dimension':1,'element_size':8}


def synthetic_rows():
    rows = [root('controller','Controller')]
    for name in tool.METHODS:
        rows.append({'kind':'FUNCTION','name':name,'path':'Test.Controller:'+name,'coverage':'COMPLETE',
                     'flags':1024,'num_params':1 if name=='GetSkillManager' else 0,
                     'params_size':8 if name=='GetSkillManager' else 0,'return_offset':0 if name=='GetSkillManager' else 65535,
                     'signature':'NOT_ESTABLISHED','properties':[prop('ReturnValue',0x480)] if name=='GetSkillManager' else []})
    rows += [root('manager','Manager'),{'kind':'DISCOVERY','source_function':'GetSkillManager',
              'return_property':'ReturnValue','return_class':'Test.Manager'},root('active_skill_class','Skill'),
             {'kind':'FIELD','name':'ActiveSkills','type':'ZArrayProperty','flags':3,'offset':0,
              'dimension':1,'element_size':12,'inner_type':'ZObjectProperty','coverage':'COMPLETE',
              'owner':'Test.Manager','element_class':'Test.Skill'}]
    for name in tool.FIELDS:
        if name=='Definition':rows.append(root('definition_class','Definition'))
        rows.append({'kind':'FIELD','name':name,'type': 'ZObjectProperty' if name in ('Definition','SkillInstigator')
                        else 'ZArrayProperty' if name=='DurationModifierStack' else 'ZFloatProperty',
                     'flags':3,'offset':16,'dimension':1,'element_size':4,'coverage':'COMPLETE',
                     'inner_type':'ZFloatProperty' if name=='DurationModifierStack' else 'NOT_APPLICABLE',
                     'owner':'Test.Skill','declared_class':'Test.Definition' if name=='Definition'
                            else 'Test.Controller' if name=='SkillInstigator' else 'NOT_APPLICABLE'})
    return rows


def call(rows=None, coverage='COMPLETE', final='FINAL points=(1, 0) ranks=(0, 0, 0) unchanged_from_start=True'):
    rows = synthetic_rows() if rows is None else rows
    lines = ['[UVH-DEATHTRAP] BEGIN v0.2.12 metadata_only=True']
    lines += ['[UVH-DEATHTRAP] METADATA '+json.dumps(row,sort_keys=True) for row in rows]
    if final is not None:lines.append('[UVH-DEATHTRAP] '+final)
    lines.append('[UVH-DEATHTRAP] END coverage='+coverage+' observers_added=0 native_calls=0 writes=0 signature=NOT_ESTABLISHED')
    return lines


def cleanup():
    return ['[UVH-'+family+'] STOP remaining=0 captured=0 callbacks=0 skipped=0' for family in ('STATE','UI','UPGRADE')] + [
        '[UVH-INITNODE] Observers remaining=0',
        "[UVH-NEWNODE] RESTORE result=True skills=['MorePep', 'Myelin'] cells=[True, False, True] (methods assign, slice)",
        '[UVH-INITNODE] NATIVE ARRAYS RESTORED. Restart BL2 to clear any player/UI cache.']


def raw(lines):return ('\n'.join(lines)+'\n').encode()


class DeathtrapMetadataLogReviewTests(unittest.TestCase):
    def check(self, lines=None):return tool.review_bytes(raw(call()+cleanup() if lines is None else lines))

    def rejected(self, lines):
        report=self.check(lines);self.assertFalse(report['log_text_acceptable']);return report

    def test_complete_synthetic_text_is_acceptable_but_all_native_checks_remain_unknown(self):
        report=self.check();self.assertEqual(report['status'],'COMPLETE_LOG_TEXT')
        self.assertEqual(len(report['calls'][0]['rows']),15)
        self.assertTrue(all(v=='NOT_CHECKED' for v in report['separate_checks'].values()))
        self.assertNotIn('baseline',report['calls'][0])
        self.assertEqual(report['grammar']['runtime_sha256'],tool.RUNTIME_SHA256)

    def test_actual_sdk_prefix_format_and_bom_preserve_input_hash(self):
        data=b'\xef\xbb\xbf'+raw(['2026-10-11 01:22:51.987Z c728 ~ mod.py@19 INFO| [UVH-BOOST] '+line for line in call()+cleanup()])
        report=tool.review_bytes(data)
        self.assertTrue(report['log_text_acceptable'])
        self.assertEqual(report['source']['sha256'],hashlib.sha256(data).hexdigest())

    def test_multiple_calls_need_cleanup_after_the_last(self):
        report=self.check(call()+cleanup()+call()+cleanup())
        self.assertEqual(len(report['calls']),2);self.assertTrue(report['log_text_acceptable'])
        self.rejected(call()+cleanup()+call())

    def test_final_comparisons_between_calls_are_not_invented(self):
        final='FINAL points=(2, 0) ranks=(0, 1, 0) unchanged_from_start=True'
        self.assertTrue(self.check(call()+call(final=final)+cleanup())['log_text_acceptable'])

    def test_capped_function_requires_sixteen_properties_and_remains_partial(self):
        rows=synthetic_rows();f=rows[2];f['coverage']='CAPPED';f['properties']=[prop('P'+str(i),offset=8*i) for i in range(16)]
        report=self.check(call(rows,'CAPPED')+cleanup());self.assertEqual(report['calls'][0]['outcome'],'CAPPED')
        self.assertEqual(report['status'],'PARTIAL')
        f['properties'].pop();self.rejected(call(rows,'CAPPED')+cleanup())

    def test_seventeenth_function_property_refuses(self):
        rows=synthetic_rows();rows[2]['properties']=[prop('P'+str(i)) for i in range(17)]
        self.rejected(call(rows)+cleanup())

    def test_capped_ancestry_requires_eight_nodes(self):
        rows=synthetic_rows();rows[0]['coverage']='CAPPED'
        rows[0]['ancestry'] += [{'name':'Ancestor'+str(i),'path':'Test.Ancestor'+str(i)} for i in range(7)]
        self.assertEqual(self.check(call(rows,'CAPPED')+cleanup())['calls'][0]['outcome'],'CAPPED')
        rows[0]['ancestry'].pop();self.rejected(call(rows,'CAPPED')+cleanup())

    def test_ninth_ancestry_node_and_cycle_refuse(self):
        for cycle in (False,True):
            rows=synthetic_rows()
            rows[0]['ancestry'] = [copy.deepcopy(rows[0]['ancestry'][0]) for _ in range(2)] if cycle else [
                {'name':'A'+str(i),'path':'Test.A'+str(i)} for i in range(9)]
            self.rejected(call(rows)+cleanup())

    def test_unavailable_function_and_definition_are_honest_partial(self):
        rows=synthetic_rows();rows[2]={'kind':'FUNCTION','name':'ActivateSkill','coverage':'UNAVAILABLE'}
        rows=[r for r in rows if r.get('target')!='definition_class']
        i=next(i for i,r in enumerate(rows) if r.get('name')=='Definition')
        rows[i]={'kind':'FIELD','name':'Definition','coverage':'UNAVAILABLE'}
        report=self.check(call(rows,'UNAVAILABLE')+cleanup())
        self.assertEqual(report['calls'][0]['outcome'],'UNAVAILABLE');self.assertEqual(report['status'],'PARTIAL')

    def test_unavailable_manager_discovery_without_return_is_partial(self):
        rows=synthetic_rows()[:4];rows[1]['properties']=[];rows[1]['return_offset']=65535
        rows += [{'kind':'DISCOVERY','target':'manager','coverage':'UNAVAILABLE'}]
        self.assertEqual(self.check(call(rows,'UNAVAILABLE')+cleanup())['calls'][0]['outcome'],'UNAVAILABLE')

    def test_unavailable_active_array_has_no_invented_skill_or_fields(self):
        rows=synthetic_rows()[:6]+[{'kind':'FIELD','name':'ActiveSkills','coverage':'UNAVAILABLE'}]
        self.assertEqual(self.check(call(rows,'UNAVAILABLE')+cleanup())['calls'][0]['outcome'],'UNAVAILABLE')

    def test_cap_takes_precedence_over_unavailable_but_is_not_complete(self):
        rows=synthetic_rows();rows[2]['coverage']='CAPPED';rows[2]['properties']=[prop('P'+str(i)) for i in range(16)]
        rows[3]={'kind':'FUNCTION','name':'DeactivateSkill','coverage':'UNAVAILABLE'}
        self.assertEqual(self.check(call(rows,'CAPPED')+cleanup())['calls'][0]['outcome'],'CAPPED')
        self.rejected(call(rows,'UNAVAILABLE')+cleanup())

    def test_lone_unavailable_never_has_synthetic_final_or_end(self):
        lines=[call()[0],'[UVH-DEATHTRAP] '+tool.UNAVAILABLE]+cleanup()
        report=self.check(lines);self.assertEqual(report['calls'][0]['outcome'],'INCOMPLETE_UNAVAILABLE')
        self.assertIsNone(report['calls'][0]['final']);self.assertFalse(report['log_text_acceptable'])

    def test_abort_after_rows_or_final_is_refused(self):
        for lines in (call()[:4],call()[:-1]):
            report=self.rejected(lines+['[UVH-DEATHTRAP] '+tool.ABORT]+cleanup())
            self.assertEqual(report['calls'][0]['outcome'],'REFUSED')

    def test_missing_final_missing_end_and_no_newline_do_not_pass(self):
        self.rejected(call(final=None)+cleanup())
        self.rejected(call()[:-1]+cleanup())
        self.assertFalse(tool.review_bytes(raw(call()+cleanup()).rstrip(b'\n'))['log_text_acceptable'])

    def test_truncated_json_and_duplicate_json_keys_refuse(self):
        for text in ('{"kind":"CLASS"','{"kind":"CLASS","kind":"FIELD"}'):
            lines=call();lines[1]='[UVH-DEATHTRAP] METADATA '+text
            self.rejected(lines+cleanup())

    def test_deep_json_refuses_without_crashing(self):
        lines=call();lines[1]='[UVH-DEATHTRAP] METADATA '+'['*1500+'0'+']'*1500
        self.rejected(lines+cleanup())

    def test_array_inner_cannot_claim_not_applicable(self):
        for name in ('ActiveSkills','DurationModifierStack'):
            rows=synthetic_rows();next(r for r in rows if r.get('name')==name)['inner_type']='NOT_APPLICABLE'
            self.rejected(call(rows)+cleanup())

    def test_nonfinite_json_bool_numeric_and_unknown_schema_refuse(self):
        for change in ({'flags':True},{'offset':-1},{'dimension':0},{'element_size':65537},{'extra':1}):
            rows=synthetic_rows();rows[1]['properties'][0].update(change);self.rejected(call(rows)+cleanup())
        lines=call();lines[1]='[UVH-DEATHTRAP] METADATA {"kind":NaN}';self.rejected(lines+cleanup())

    def test_numeric_function_bounds_refuse(self):
        for field,value in (('flags',2**32),('num_params',256),('params_size',65536),('return_offset',65536)):
            rows=synthetic_rows();rows[2][field]=value;self.rejected(call(rows)+cleanup())

    def test_field_parameter_flags_dimension_and_aggregate_bound_refuse(self):
        for change in ({'flags':0x80},{'dimension':2},{'offset':1048576},{'element_size':0}):
            rows=synthetic_rows();rows[7].update(change);self.rejected(call(rows)+cleanup())

    def test_unknown_name_owner_and_noncanonical_path_refuse(self):
        for field,value in (('name','Foreign'),('owner','Test.Foreign'),('element_class','Test.Other')):
            rows=synthetic_rows();rows[7][field]=value;self.rejected(call(rows)+cleanup())
        rows=synthetic_rows();rows[0]['ancestry'][0]['path']='Test.Other';self.rejected(call(rows)+cleanup())

    def test_overlong_labels_and_paths_refuse(self):
        for field,value in (('type','A'*97),('owner','Test.'+'A'*380)):
            rows=synthetic_rows();rows[7][field]=value;self.rejected(call(rows)+cleanup())

    def test_function_path_and_signature_claim_refuse(self):
        for change in ({'path':'Test.Foreign:ActivateSkill'},{'signature':'VERIFIED'}):
            rows=synthetic_rows();rows[2].update(change);self.rejected(call(rows)+cleanup())

    def test_return_offset_duplicate_return_and_discovery_mismatch_refuse(self):
        for mode in ('offset','duplicate','discovery'):
            rows=synthetic_rows()
            if mode=='offset':rows[1]['return_offset']=4
            elif mode=='duplicate':rows[1]['properties'].append(prop('SecondReturn',0x480))
            else:rows[5]['return_property']='Wrong'
            self.rejected(call(rows)+cleanup())

    def test_declared_definition_and_instigator_class_mismatch_refuse(self):
        for name in ('Definition','SkillInstigator'):
            rows=synthetic_rows();next(r for r in rows if r.get('name')==name)['declared_class']='Test.Foreign'
            self.rejected(call(rows)+cleanup())

    def test_duplicate_property_and_extra_metadata_rows_refuse(self):
        rows=synthetic_rows();rows[1]['properties'].append(copy.deepcopy(rows[1]['properties'][0]))
        self.rejected(call(rows)+cleanup())
        rows=synthetic_rows();rows.append(copy.deepcopy(rows[-1]));self.rejected(call(rows)+cleanup())

    def test_row_reordering_missing_field_and_missing_root_refuse(self):
        for index in (6,8,12):
            rows=synthetic_rows();rows.pop(index);self.rejected(call(rows)+cleanup())
        rows=synthetic_rows();rows[2],rows[3]=rows[3],rows[2];self.rejected(call(rows)+cleanup())

    def test_false_complete_end_for_partial_metadata_refuses(self):
        rows=synthetic_rows();rows[2]={'kind':'FUNCTION','name':'ActivateSkill','coverage':'UNAVAILABLE'}
        self.rejected(call(rows,'COMPLETE')+cleanup())

    def test_nested_begin_or_orphan_record_refuses(self):
        self.rejected(call()[:3]+call()+cleanup())
        self.rejected(call()[1:]+cleanup())

    def test_duplicate_final_and_metadata_after_final_refuse(self):
        lines=call();lines.insert(-1,lines[-2]);self.rejected(lines+cleanup())
        lines=call();lines.insert(-1,lines[1]);self.rejected(lines+cleanup())

    def test_logged_baseline_is_rejected_because_runtime_never_emits_it(self):
        lines=call();lines.insert(1,'[UVH-DEATHTRAP] BASELINE points=(1, 0) ranks=(0, 0, 0)')
        self.rejected(lines+cleanup())

    def test_final_rank_one_unknown_or_bool_points_refuse(self):
        for final in ('FINAL points=(True, 0) ranks=(0, 0, 0) unchanged_from_start=True',
                      'FINAL points=(1, 0) ranks=(1, 0, 0) unchanged_from_start=True',
                      'FINAL points=(1, 0) ranks=(0, 0, 0) unchanged_from_start=False'):
            self.rejected(call(final=final)+cleanup())

    def test_end_observer_native_call_write_or_signature_claim_refuse(self):
        for old,new in (('observers_added=0','observers_added=1'),('native_calls=0','native_calls=1'),
                        ('writes=0','writes=1'),('signature=NOT_ESTABLISHED','signature=COMPLETE')):
            lines=call();lines[-1]=lines[-1].replace(old,new);self.rejected(lines+cleanup())

    def test_mixed_versions_and_malformed_prefix_refuse(self):
        self.rejected(['[UVH-CLASS] BEGIN v0.2.11 historical']+call()+cleanup())
        lines=call();lines[0]=lines[0].replace('0.2.12','0.2.13');self.rejected(lines+cleanup())
        self.rejected(['clipped [UVH-DEATHTRAP] FINAL broken']+call()+cleanup())

    def test_missing_cleanup_and_no_patch_alone_do_not_establish_restore(self):
        self.rejected(call())
        self.rejected(call()+cleanup()[:4]+['[UVH-INITNODE] DISARMED; no initialization patch to restore.'])
        self.rejected(cleanup()+call())

    def test_four_observer_families_required_after_last_call(self):
        for index in range(4):
            lines=cleanup();lines.pop(index);self.rejected(call()+lines)

    def test_cleanup_failure_then_successful_retry_still_refuses(self):
        for error in ('[UVH-INITNODE] Hook removal ERROR RuntimeError',
                      '[UVH-STATE] Removal ERROR path: RuntimeError',
                      '[UVH-INITNODE] Rollback failed; snapshot retained.',
                      '[UVH-NEWNODE] Removal ERROR RuntimeError: failed',
                      '[UVH-UI] STOP remaining=1 captured=0 callbacks=0 skipped=0',
                      "[UVH-NEWNODE] RESTORE result=False skills=[] cells=[] (methods assign, assign)"):
            report=self.rejected(call()+[error]+cleanup())
            self.assertTrue(report['cleanup']['errors'])

    def test_cleanup_failure_before_call_remains_a_finding(self):
        self.rejected(['[UVH-INITNODE] Cannot verify rollback ownership; retained']+call()+cleanup())

    def test_manual_duration_cleanup_failure_or_write_remains_a_finding(self):
        for payload in ('ERROR restore: RuntimeError', 'WARNING rollback failed: RuntimeError',
                        'RESTORE READBACK MISMATCH: got None', 'WRITE VERIFIED: live Duration 60 -> 75'):
            self.rejected(call()+['[UVH-BOOST] '+payload]+cleanup())

    def test_new_experiment_after_metadata_and_traceback_refuse(self):
        self.rejected(call()+['[UVH-UI] START v0.2.12 observers']+cleanup())
        self.rejected(call()+['Traceback (most recent call last):']+cleanup())

    def test_empty_old_log_and_invalid_utf8_are_not_new_capture(self):
        self.assertEqual(tool.review_bytes(b'old data\n')['status'],'NO_CALLS')
        self.assertEqual(tool.review_bytes(b'\xff')['status'],'INPUT_ERROR')

    def test_input_byte_line_and_call_bounds_refuse(self):
        self.assertEqual(tool.review_bytes(b'x'*(tool.MAX_BYTES+1))['status'],'INPUT_ERROR')
        self.assertEqual(tool.review_bytes(b'x'*(tool.MAX_LINE+1)+b'\n')['status'],'INPUT_ERROR')
        lines=[]
        for _ in range(129):lines.extend([call()[0],'[UVH-DEATHTRAP] '+tool.UNAVAILABLE])
        report=self.rejected(lines+cleanup());self.assertLessEqual(len(report['calls']),128)

    def test_no_literal_command_execution(self):
        final="FINAL points=(__import__('os').system('must_never_execute'), 0) ranks=(0, 0, 0) unchanged_from_start=True"
        self.rejected(call(final=final)+cleanup())

    def test_cli_exit_codes_stdout_json_and_inputs_unchanged(self):
        with tempfile.TemporaryDirectory(prefix='metadata_log_') as temp:
            path=Path(temp)/'input.log'
            for lines,code in ((call()+cleanup(),0),(call(),1)):
                data=raw(lines);path.write_bytes(data);output=io.StringIO()
                with patch('sys.stdout',output):self.assertEqual(tool.main([str(path)]),code)
                self.assertEqual(path.read_bytes(),data);json.loads(output.getvalue())
            with patch('sys.stdout',io.StringIO()):self.assertEqual(tool.main([str(path)+'missing']),2)

    def test_runtime_emitted_complete_and_capped_mock_records_match_parser(self):
        # Cross-check actual preserved runtime grammar using its existing inert harness.
        # Import the module, never alias its TestCase into this module/discovery.
        import test_deathtrap_readiness as fixtures
        fixture=fixtures.DeathtrapReadinessTests();fixture.setUp();fixture.run_diagnostic()
        report=self.check(fixture.h.logs+cleanup())
        self.assertEqual(report['calls'][0]['outcome'],'COMPLETE')
        fixture.setUp();func=fixture.controller.functions['ActivateSkill']
        func.props=[fixtures.ZProperty('P'+str(i),func,Offset_Internal=4*i) for i in range(17)]
        func.link();fixture.run_diagnostic()
        report=self.check(fixture.h.logs+cleanup())
        self.assertEqual(report['calls'][0]['outcome'],'CAPPED')
        self.assertFalse(report['log_text_acceptable'])
