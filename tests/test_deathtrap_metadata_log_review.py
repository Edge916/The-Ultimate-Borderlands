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
        fixture.setUp();func=fixture.manager.functions['ActivateSkill']
        func.props=[fixtures.ZProperty('P'+str(i),func,Offset_Internal=4*i) for i in range(17)]
        func.link();fixture.run_diagnostic()
        report=self.check(fixture.h.logs+cleanup())
        self.assertEqual(report['calls'][0]['outcome'],'CAPPED')
        self.assertFalse(report['log_text_acceptable'])


def manager_rows():
    rows = synthetic_rows()
    rows[2]['path'] = 'Test.Manager:ActivateSkill'
    rows[3]['path'] = 'Test.Manager:DeactivateSkill'
    return rows[:2]+rows[4:6]+rows[2:4]+rows[6:]


def manager_call(rows=None,coverage='COMPLETE'):
    lines = call(manager_rows() if rows is None else rows,coverage)
    lines[0] = '[UVH-DEATHTRAP] BEGIN v0.2.13 metadata_only=True'
    return lines


class ManagerMetadataLogReviewTests(unittest.TestCase):
    def review(self,rows=None,coverage='COMPLETE'):
        return tool.review_bytes(raw(manager_call(rows,coverage)+cleanup()))

    def test_manager_version_contract_and_runtime_hash_are_explicit(self):
        report = self.review()
        self.assertEqual(report['status'],'COMPLETE_LOG_TEXT')
        self.assertEqual(report['grammar'],{'version':'0.2.13','runtime_sha256':tool.RUNTIME_HASHES['0.2.13']})
        self.assertTrue(all(v=='NOT_CHECKED' for v in report['separate_checks'].values()))

    def test_controller_or_foreign_candidates_cannot_pass_manager_owner_contract(self):
        for owner in ('Controller','Foreign'):
            for index in (4,5):
                rows = manager_rows();rows[index]['path']='Test.'+owner+':'+rows[index]['name']
                self.assertEqual(self.review(rows)['status'],'REFUSED')

    def test_v12_order_or_v13_order_with_wrong_version_refuses(self):
        self.assertEqual(self.review(synthetic_rows())['status'],'REFUSED')
        self.assertEqual(tool.review_bytes(raw(call(manager_rows())+cleanup()))['status'],'REFUSED')

    def test_mixed_v12_v13_calls_refuse_even_if_each_sequence_is_valid(self):
        report = tool.review_bytes(raw(call()+manager_call()+cleanup()))
        self.assertEqual(report['status'],'REFUSED')
        self.assertIn('mixed/unsupported versions',report['issues'])

    def test_missing_primary_discovery_has_no_unattempted_candidate_rows(self):
        rows = manager_rows()[:2]
        rows[1] = {'kind':'FUNCTION','name':'GetSkillManager','coverage':'UNAVAILABLE'}
        rows.append({'kind':'DISCOVERY','target':'manager','coverage':'UNAVAILABLE'})
        self.assertEqual(self.review(rows,'UNAVAILABLE')['status'],'PARTIAL')
        rows.append({'kind':'FUNCTION','name':'ActivateSkill','coverage':'UNAVAILABLE'})
        self.assertEqual(self.review(rows,'UNAVAILABLE')['status'],'REFUSED')

    def test_missing_manager_candidate_keeps_fields_partial(self):
        rows = manager_rows();rows[4]={'kind':'FUNCTION','name':'ActivateSkill','coverage':'UNAVAILABLE'}
        self.assertEqual(self.review(rows,'UNAVAILABLE')['calls'][0]['outcome'],'UNAVAILABLE')
        self.assertEqual(self.review(rows,'COMPLETE')['status'],'REFUSED')

    def test_manager_ancestor_owner_is_accepted_only_in_declared_chain(self):
        rows = manager_rows();rows[2]['ancestry'].append({'name':'Parent','path':'Test.Parent'})
        rows[4]['path']='Test.Parent:ActivateSkill'
        self.assertEqual(self.review(rows)['status'],'COMPLETE_LOG_TEXT')
        rows[2]['ancestry'].pop()
        self.assertEqual(self.review(rows)['status'],'REFUSED')

    def test_manager_return_discovery_mismatch_and_unavailable_contradiction_refuse(self):
        for change in ('class','unavailable'):
            rows = manager_rows()
            if change == 'class': rows[3]['return_class']='Test.Foreign'
            else: rows[3]={'kind':'DISCOVERY','target':'manager','coverage':'UNAVAILABLE'}
            self.assertEqual(self.review(rows)['status'],'REFUSED')

    def test_manager_properties_cap_and_missing_array_remain_partial(self):
        rows=manager_rows();rows[4]['coverage']='CAPPED'
        rows[4]['properties']=[prop('P'+str(i),offset=8*i) for i in range(16)]
        self.assertEqual(self.review(rows,'CAPPED')['status'],'PARTIAL')
        rows=manager_rows()[:6]+[{'kind':'FIELD','name':'ActiveSkills','coverage':'UNAVAILABLE'}]
        self.assertEqual(self.review(rows,'UNAVAILABLE')['status'],'PARTIAL')

    def test_manager_cleanup_failure_history_is_not_erased_by_successful_retry(self):
        lines=manager_call()+['[UVH-STATE] STOP remaining=1 captured=0 callbacks=0 skipped=0']+cleanup()
        report=tool.review_bytes(raw(lines))
        self.assertEqual(report['status'],'REFUSED')
        self.assertTrue(report['cleanup']['errors'])

    def test_manager_abort_and_unknown_output_do_not_claim_complete(self):
        lines=manager_call()[:3]+['[UVH-DEATHTRAP] '+tool.ABORT]+cleanup()
        self.assertEqual(tool.review_bytes(raw(lines))['status'],'REFUSED')
        lines=manager_call();lines.insert(-1,'[UVH-DEATHTRAP] BASELINE points=(1, 0) ranks=(0, 0, 0)')
        self.assertEqual(tool.review_bytes(raw(lines+cleanup()))['status'],'REFUSED')


def parameter_rows():
    rows = manager_rows()
    for row in rows:
        if row['kind'] == 'FUNCTION':
            for p in row['properties']:
                p.update(declared_class='Test.Manager', declared_class_coverage='COMPLETE')
            row['parameter_classes_coverage'] = 'COMPLETE' if row['properties'] else 'NOT_APPLICABLE'
    def object_prop(name, path, offset):
        return dict(prop(name,128,offset), declared_class=path, declared_class_coverage='COMPLETE')
    def nonobject_prop(name, kind, offset, flags=144, size=4):
        return dict(prop(name,flags,offset), type=kind, element_size=size,
                    declared_class='NOT_APPLICABLE', declared_class_coverage='NOT_APPLICABLE')
    rows[4].update(num_params=6, params_size=44, return_offset=40, parameter_classes_coverage='COMPLETE', properties=[
        object_prop('SkillInstigator','Test.Controller',0), object_prop('Definition','Test.Definition',8),
        object_prop('AdditionalSkillTarget','Test.Actor',16), nonobject_prop('SkillGrade','ZIntProperty',24),
        nonobject_prop('StateChangeDelegate','ZDelegateProperty',28,4194448,12),
        nonobject_prop('ReturnValue','ZBoolProperty',40,0x480)])
    rows[5].update(num_params=3, params_size=20, parameter_classes_coverage='COMPLETE', properties=[
        object_prop('SkillInstigator','Test.Controller',0), object_prop('Definition','Test.Definition',8),
        nonobject_prop('bIgnoreSkillInstigator','ZBoolProperty',16)])
    return rows


def parameter_call(rows=None, coverage='COMPLETE'):
    lines = call(parameter_rows() if rows is None else rows, coverage)
    lines[0] = '[UVH-DEATHTRAP] BEGIN v0.2.14 metadata_only=True'
    return lines


class ParameterMetadataLogReviewTests(unittest.TestCase):
    def review(self, rows=None, coverage='COMPLETE'):
        return tool.review_bytes(raw(parameter_call(rows, coverage) + cleanup()))

    def test_parameter_version_hash_and_native_unknowns_remain_explicit(self):
        result = self.review()
        self.assertEqual(result['status'], 'COMPLETE_LOG_TEXT')
        self.assertEqual(result['grammar'], {'version':'0.2.14','runtime_sha256':tool.RUNTIME_HASHES['0.2.14']})
        self.assertTrue(all(v == 'NOT_CHECKED' for v in result['separate_checks'].values()))
        self.assertEqual(result['game_behavior'], 'NOT_ESTABLISHED_BY_TOOL')

    def test_parameter_old_versions_reject_new_keys_and_new_version_requires_them(self):
        for version in ('0.2.12', '0.2.13'):
            lines = parameter_call(); lines[0] = lines[0].replace('0.2.14', version)
            self.assertEqual(tool.review_bytes(raw(lines + cleanup()))['status'], 'REFUSED')
        self.assertEqual(self.review(manager_rows())['status'], 'REFUSED')

    def test_parameter_mixed_versions_refuse(self):
        result = tool.review_bytes(raw(manager_call() + parameter_call() + cleanup()))
        self.assertEqual(result['status'], 'REFUSED')
        self.assertIn('mixed/unsupported versions', result['issues'])

    def test_parameter_object_sentinel_path_and_coverage_contradictions_refuse(self):
        for values in ({'declared_class':'NOT_APPLICABLE'}, {'declared_class':'UNAVAILABLE'},
                       {'declared_class':'Bad Path'}, {'declared_class_coverage':'NOT_APPLICABLE'},
                       {'declared_class_coverage':'UNAVAILABLE'}, {'declared_class_coverage':True}):
            rows = parameter_rows(); rows[4]['properties'][0].update(values)
            self.assertEqual(self.review(rows)['status'], 'REFUSED')

    def test_parameter_nonobject_types_cannot_claim_object_class(self):
        for index in (3, 4, 5):
            rows = parameter_rows()
            rows[4]['properties'][index].update(declared_class='Test.Actor', declared_class_coverage='COMPLETE')
            self.assertEqual(self.review(rows)['status'], 'REFUSED')

    def test_parameter_supported_subclasses_and_unsupported_tags(self):
        for kind in tool.OBJECT_PROPERTY_TYPES:
            rows = parameter_rows(); rows[4]['properties'][0]['type'] = kind
            self.assertEqual(self.review(rows)['status'], 'COMPLETE_LOG_TEXT')
        rows = parameter_rows(); rows[4]['properties'][0]['type'] = 'UnlistedProperty'
        self.assertEqual(self.review(rows)['status'], 'REFUSED')

    def test_parameter_aggregate_coverage_cannot_hide_partial_class(self):
        rows = parameter_rows()
        rows[4]['properties'][2].update(declared_class='UNAVAILABLE', declared_class_coverage='UNAVAILABLE')
        self.assertEqual(self.review(rows, 'UNAVAILABLE')['status'], 'REFUSED')
        rows[4]['parameter_classes_coverage'] = 'UNAVAILABLE'
        self.assertEqual(self.review(rows, 'UNAVAILABLE')['status'], 'PARTIAL')
        self.assertEqual(self.review(rows, 'COMPLETE')['status'], 'REFUSED')

    def test_parameter_partial_preserves_descriptor_completeness(self):
        rows = parameter_rows()
        rows[4]['properties'][2].update(declared_class='UNAVAILABLE', declared_class_coverage='UNAVAILABLE')
        rows[4]['parameter_classes_coverage'] = 'UNAVAILABLE'
        result = self.review(rows, 'UNAVAILABLE')
        self.assertEqual(result['calls'][0]['rows'][4]['coverage'], 'COMPLETE')
        self.assertEqual(result['calls'][0]['outcome'], 'UNAVAILABLE')

    def test_parameter_capped_enumeration_requires_capped_class_coverage(self):
        rows = parameter_rows(); f = rows[4]
        f['coverage'] = 'CAPPED'; f['parameter_classes_coverage'] = 'CAPPED'
        f['return_offset'] = 65535
        f['properties'] = [dict(prop('P'+str(i),offset=8*i),declared_class='Test.Actor',declared_class_coverage='COMPLETE') for i in range(16)]
        self.assertEqual(self.review(rows,'CAPPED')['status'], 'PARTIAL')
        f['parameter_classes_coverage'] = 'COMPLETE'
        self.assertEqual(self.review(rows,'CAPPED')['status'], 'REFUSED')

    def test_parameter_primary_return_class_must_match_discovery(self):
        for path, coverage in (('Test.Foreign','COMPLETE'), ('UNAVAILABLE','UNAVAILABLE')):
            rows = parameter_rows()
            rows[1]['properties'][0].update(declared_class=path,declared_class_coverage=coverage)
            rows[1]['parameter_classes_coverage'] = coverage
            self.assertEqual(self.review(rows,'UNAVAILABLE' if coverage=='UNAVAILABLE' else 'COMPLETE')['status'], 'REFUSED')

    def test_parameter_cap_precedes_unavailable_sample_without_complete_claim(self):
        rows = parameter_rows(); f = rows[4]
        f.update(coverage='CAPPED', parameter_classes_coverage='CAPPED', return_offset=65535,
                 properties=[dict(prop('P'+str(i),offset=8*i),declared_class='Test.Actor',declared_class_coverage='COMPLETE') for i in range(16)])
        f['properties'][0].update(declared_class='UNAVAILABLE',declared_class_coverage='UNAVAILABLE')
        self.assertEqual(self.review(rows,'CAPPED')['calls'][0]['outcome'], 'CAPPED')
        self.assertEqual(self.review(rows,'UNAVAILABLE')['status'], 'REFUSED')

    def test_parameter_cleanup_failure_history_survives_retry(self):
        lines = parameter_call() + ['[UVH-INITNODE] Observers remaining=1'] + cleanup()
        self.assertEqual(tool.review_bytes(raw(lines))['status'], 'REFUSED')

    def test_parameter_runtime_emitted_complete_and_partial_match_parser(self):
        import test_deathtrap_readiness as fixtures
        fixture = fixtures.DeathtrapReadinessTests(); fixture.setUp(); fixture.parameter_fixture()
        self.assertTrue(fixture.run_diagnostic())
        self.assertEqual(tool.review_bytes(raw(fixture.h.logs + cleanup()))['status'], 'COMPLETE_LOG_TEXT')
        fixture.setUp(); fixture.parameter_fixture()
        def unavailable(): raise RuntimeError('synthetic header unavailable')
        fixture.argument_target._path_name = unavailable
        self.assertFalse(fixture.run_diagnostic())
        self.assertEqual(tool.review_bytes(raw(fixture.h.logs + cleanup()))['status'], 'PARTIAL')

    def test_parameter_missing_keys_and_overlong_declared_paths_refuse(self):
        for change in ('class', 'coverage', 'function', 'length'):
            rows = parameter_rows()
            if change == 'class': del rows[4]['properties'][0]['declared_class']
            elif change == 'coverage': del rows[4]['properties'][0]['declared_class_coverage']
            elif change == 'function': del rows[4]['parameter_classes_coverage']
            else: rows[4]['properties'][0]['declared_class'] = 'A'*385
            self.assertEqual(self.review(rows)['status'], 'REFUSED')
