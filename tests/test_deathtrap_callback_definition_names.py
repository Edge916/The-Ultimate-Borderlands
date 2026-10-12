"""Name export boundary tests using inert bindings, never a native lifetime proof."""
import ast
import gc
import hashlib
import inspect
import json
import re
import unittest
import weakref
from pathlib import Path
from unittest.mock import patch
import test_deathtrap_callback_local_reader as inert
import test_deathtrap_callback_local_reader_log_review as old_log
import test_runtime_mock as runtime

PREFIX = '[UVH-CALLBACK-NAME] '
ROOT = Path(__file__).resolve().parents[1]


class DefinitionNameTests(unittest.TestCase):
    def setUp(self):
        self.f = inert.CallbackLocalReaderTests()
        self.f.setUp()

    def tearDown(self):
        self.f.tearDown()

    def records(self):
        return [line.split(PREFIX, 1)[1] for line in self.f.h.logs if PREFIX in line]

    def events(self):
        return [line for line in self.records() if line.startswith('EVENT ')]

    def token(self, event):
        return re.search(r' name=([^ ]+) ownership=', event).group(1)

    def fresh(self):
        self.f.tearDown()
        self.f.setUp()

    def test_all_six_branches_keep_actual_sdk_counts_and_required_token(self):
        cases = [('NULL_INSTIGATOR','NOT_READ','-',(58,49,0,0)),
                 ('OTHER_CONTROLLER_CLASS','NOT_READ','-',(58,50,0,0)),
                 ('OTHER_WRAPPER','NOT_READ','-',(58,50,1,0)),
                 ('SAME_WRAPPER','NULL_DEFINITION','-',(58,50,36,50)),
                 ('SAME_WRAPPER','OTHER_NAME','Different_Skill',(58,50,36,52)),
                 ('SAME_WRAPPER','DEATHTRAP_NAME','Skill_DeathTrap',(58,50,36,52))]
        for controller, definition, name, stages in cases:
            with self.subTest(controller=controller, definition=definition):
                self.fresh()
                if controller == 'NULL_INSTIGATOR': self.f.args.SkillInstigator = None
                if controller == 'OTHER_CONTROLLER_CLASS': self.f.args.SkillInstigator = inert.UObject(Class=self.f.declared)
                if controller == 'OTHER_WRAPPER': self.f.args.SkillInstigator = inert.UObject(Class=self.f.controller)
                if definition == 'NULL_DEFINITION': self.f.args.Definition = None
                if definition == 'OTHER_NAME': self.f.definition.Name = name
                if definition == 'NOT_READ': self.f.args.Definition = inert.Poison()
                self.f.start(); self.f.fire()
                event = self.events()[0]
                self.assertIn('controller={} definition={}'.format(controller, definition), event)
                self.assertEqual(self.token(event), name)
                actual = tuple(map(int, event.split('stages=')[1].split(',')))
                self.assertEqual(actual, stages)
                self.assertEqual(len(inert.NATIVE_OPS), sum(stages))
                self.assertEqual(self.f.args.reads.count('Definition'), int(definition != 'NOT_READ'))
                self.assertEqual(self.f.definition.reads.count('Name'), int(definition in ('OTHER_NAME','DEATHTRAP_NAME')))

    def test_one_and_128_character_names_are_exact_without_clipping(self):
        for name in ('Z','Z'*128):
            with self.subTest(length=len(name)):
                self.fresh(); self.f.definition.Name = name
                self.f.start(); self.f.fire()
                self.assertEqual(self.token(self.events()[0]), name)
                self.assertEqual(self.f.definition.reads.count('Name'), 1)
                self.assertTrue(all(len(line.encode('utf-8')) <= 384 for line in self.f.h.logs))

    def test_every_allowed_ascii_character_is_a_literal_primitive(self):
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_':
            with self.subTest(char=char):
                self.fresh(); self.f.definition.Name = char
                self.f.start(); self.f.fire()
                self.assertEqual(self.token(self.events()[0]), char)

    def test_literal_match_is_case_sensitive_and_no_alias_is_added(self):
        for name in ('Skill_DeathTrap','skill_deathtrap','SKILL_DEATHTRAP','Skill_DeathTrap_0','DeathTrap'):
            with self.subTest(name=name):
                self.fresh(); self.f.definition.Name = name
                self.f.start(); self.f.fire(); self.f.call('stop_callback_local_reader')
                event = self.events()[0]
                self.assertEqual(self.token(event), name)
                self.assertIn('definition='+('DEATHTRAP_NAME' if name=='Skill_DeathTrap' else 'OTHER_NAME'), event)
                self.assertEqual(self.f.h.scope['_cr_stats']['filtered'], int(name!='Skill_DeathTrap'))

    def test_sentinel_like_valid_names_do_not_become_absence(self):
        for name in ('NOT_READ','NULL_DEFINITION','NONE'):
            with self.subTest(name=name):
                self.fresh(); self.f.definition.Name = name
                self.f.start(); self.f.fire()
                self.assertEqual(self.token(self.events()[0]), name)
                self.assertIn('definition=OTHER_NAME', self.events()[0])

    def test_invalid_name_values_never_escape_in_event_or_error(self):
        class StrSubclass(str):
            def __str__(self): raise AssertionError('subclass conversion')
            def __repr__(self): raise AssertionError('subclass representation')
        values = ('','-','Z'*129,'invalid path','invalid/path','invalid\\path','invalid.path',
                  'invalid:name','invalid=name','invalid|name','invalid\nname','invalid\rname',
                  'invalid\tname','invalid\x00name','é','☃',True,123,None,inert.Poison(),StrSubclass('Invalid_Name'))
        for index, value in enumerate(values):
            with self.subTest(index=index):
                self.fresh(); self.f.definition.Name = value
                self.f.start(); self.f.fire()
                self.assertFalse(self.events())
                self.assertTrue(self.f.has('REFUSED epoch=1 reason=PARAMETER'))
                self.assertTrue(all(' name=' not in record for record in self.records()))
                self.assertEqual(self.f.h.scope['_cr_stats']['classified'], 0)

    def test_stop_inside_name_getter_prevents_export_and_defers_owned_removal(self):
        self.f.definition.Name = 'Never_Export_Stopped_Name'
        self.f.start()
        def stop_at_name(obj, key):
            if key == 'Name':
                self.assertFalse(self.f.call('stop_callback_local_reader'))
                self.assertTrue(self.f.h.hooks)
        self.f.definition.on_read = stop_at_name
        self.f.fire()
        self.assertFalse(self.events()); self.assertFalse(self.f.h.hooks)
        self.assertTrue(self.f.has('REFUSED epoch=1 reason=STOPPED'))
        self.assertNotIn('Never_Export_Stopped_Name', '\n'.join(self.f.h.logs))

    def test_timeout_inside_name_read_does_not_export_identifier(self):
        self.f.definition.Name = 'Never_Export_Timeout_Name'
        self.f.start()
        self.f.definition.on_read = lambda obj,key: setattr(self.f,'clock',1120.0) if key=='Name' else None
        self.f.fire()
        self.assertFalse(self.events()); self.assertFalse(self.f.h.hooks)
        self.assertTrue(self.f.has('REFUSED epoch=1 reason=TIME'))
        self.assertNotIn('Never_Export_Timeout_Name', '\n'.join(self.f.h.logs))

    def test_final_session_change_keeps_read_name_private(self):
        self.f.definition.Name = 'Never_Export_Changed_Session'
        self.f.start()
        self.f.definition.on_read = lambda obj,key: setattr(self.f.pri,'Owner',object()) if key=='Name' else None
        self.f.fire()
        self.assertFalse(self.events()); self.assertTrue(self.f.has('REFUSED epoch=1 reason=PLAYER'))
        self.assertNotIn('Never_Export_Changed_Session', '\n'.join(self.f.h.logs))

    def test_name_exception_is_not_formatted_or_retained(self):
        error = inert.PrivateError('Never_Export_Exception_Text')
        error_ref = weakref.ref(error)
        def fail(obj, key, error=error):
            if key == 'Name': raise error
        self.f.definition.on_read = fail
        self.f.start(); self.f.fire()
        self.assertFalse(self.events()); self.assertTrue(self.f.has('ERROR epoch=1 reason=INTERNAL'))
        self.assertNotIn('Never_Export_Exception_Text', '\n'.join(self.f.h.logs))
        self.f.definition.on_read = None
        del fail, error
        gc.collect()
        self.assertIsNone(error_ref())

    def test_emitter_sees_only_primitive_result_after_native_locals_drop(self):
        emit = self.f.h.scope['_cr_emit']
        observed = []
        def check(payload):
            if payload.startswith('EVENT '):
                frame = inspect.currentframe().f_back
                try:
                    self.assertEqual(frame.f_code.co_name, 'observe')
                    for key in ('obj','args','func','ret'):
                        self.assertIsNone(frame.f_locals[key])
                    self.assertIs(type(frame.f_locals['name']), str)
                    cursor = frame
                    while cursor is not None:
                        self.assertNotEqual(cursor.f_code.co_name, '_cr_inspect')
                        cursor = cursor.f_back
                    observed.append(payload)
                finally:
                    del frame
            return emit(payload)
        self.f.h.scope['_cr_emit'] = check
        self.f.start(); self.f.fire()
        self.assertEqual(len(observed), 1)

    def test_two_different_names_are_separate_observations_with_no_cache(self):
        self.f.start()
        for name in ('Observed_Name_One','Observed_Name_Two'):
            self.f.definition.Name = name; self.f.fire()
        self.assertEqual([self.token(e) for e in self.events()], ['Observed_Name_One','Observed_Name_Two'])
        self.assertEqual(self.f.definition.reads.count('Name'), 2)
        self.assertEqual(self.f.h.scope['_cr_stats']['filtered'], 2)
        state = {key:value for key,value in self.f.h.scope.items()
                 if key.startswith('_cr_') and not callable(value)}
        self.assertNotIn('Observed_Name_', json.dumps(state))

    def test_longest_actual_event_and_24_record_limit_fit_384_bytes(self):
        self.f.h.scope['_cr_epoch'] = 2147483646
        self.f.definition.Name = 'Z'*128
        callback = self.f.start()
        for _ in range(24): self.f.fire(callback)
        event_lines = [line for line in self.f.h.logs if PREFIX+'EVENT ' in line]
        self.assertEqual(len(event_lines), 24)
        self.assertEqual(max(len(line.encode('utf-8')) for line in event_lines), 320)
        self.assertIn('ordinal=24 attempt=24', event_lines[-1])
        self.assertFalse(self.f.h.hooks)
        self.assertTrue(self.f.has('LIMIT reason=EVENTS'))
        self.assertEqual(self.f.definition.reads.count('Name'), 24)
        self.f.fire(callback, (inert.Poison(),inert.Poison(),inert.Poison(),inert.Poison()))
        self.assertEqual(len(self.events()), 24)

    def test_reader_format_and_identifier_are_separate_from_v16(self):
        self.assertEqual(self.f.h.mod_options['name'],'UVH v0.2.17 - CALLBACK DEFINITION NAMES')
        self.assertEqual(self.f.h.scope['_CR_IDENT'],'UVH_CALLBACK_NAME_V17_DEACTIVATE_PRE')
        self.assertEqual(len(self.f.h.mod_options['options']), 23)
        self.f.start(); self.f.fire(); self.f.call('stop_callback_local_reader')
        self.assertTrue(self.f.has('START version=0.2.17'))
        self.assertNotIn('[UVH-CALLBACK-READ]', '\n'.join(self.f.h.logs))
        report = old_log.reviewer.review_bytes(('\n'.join(self.f.h.logs)+'\n').encode())
        self.assertFalse(report['log_text_acceptable'])

    def test_v16_reviewer_fixture_remains_its_immutable_tested_source(self):
        path = ROOT/'archive/tested_runtime/v0.2.16/__init__.py'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         '1d6524fa483705384951d60a6e48fc92209f21cfb62e5390c65db295924c2548')
        fixture = old_log.frozen_reader_fixture(); fixture.setUp()
        try:
            self.assertEqual(fixture.h.mod_options['version'], '0.2.16')
            fixture.start(); fixture.fire(); fixture.call('stop_callback_local_reader')
            self.assertNotIn(' name=', fixture.event())
            report = old_log.reviewer.review_bytes(('\n'.join(fixture.h.logs)+'\n').encode())
            self.assertEqual(report['status'], 'COMPLETE_LOG_TEXT')
        finally:
            fixture.tearDown()

    def test_late_stop_after_inspection_suppresses_primitive_name(self):
        original = self.f.h.scope['_cr_inspect']
        def stop_after_inspection(*args):
            result = original(*args)
            self.f.call('stop_callback_local_reader')
            return result
        self.f.h.scope['_cr_inspect'] = stop_after_inspection
        self.f.definition.Name = 'Never_Export_Late_Stop'
        self.f.start(); self.f.fire()
        self.assertFalse(self.events()); self.assertFalse(self.f.h.hooks)
        self.assertNotIn('Never_Export_Late_Stop', '\n'.join(self.f.h.logs))

    def test_failed_cleanup_preserves_history_without_retaining_name_in_state(self):
        self.f.definition.Name = 'Observed_Once_Only'
        self.f.start(); self.f.fire()
        self.f.h.fail_remove = True
        self.assertFalse(self.f.call('stop_callback_local_reader'))
        self.assertFalse(self.f.call('start_callback_local_reader'))
        self.f.h.fail_remove = False
        self.assertTrue(self.f.call('stop_callback_local_reader'))
        self.assertTrue(self.f.has('OUTCOME epoch=1 value=REFUSED'))
        self.assertEqual(len(self.events()), 1)
        self.assertTrue(all(' name=' not in r for r in self.records() if not r.startswith('EVENT ')))
        self.assertNotIn('Observed_Once_Only', json.dumps(self.f.h.scope['_cr_stats']))

    def test_logging_failure_does_not_claim_export_or_leak_exception_text(self):
        self.f.start()
        self.f.h.scope['log'] = lambda message: (_ for _ in ()).throw(inert.PrivateError('Never_Export_Log_Error'))
        self.f.fire()
        self.assertFalse(self.f.h.hooks)
        self.assertEqual(self.f.h.scope['_cr_stats']['classified'], 0)
        self.assertGreater(self.f.h.scope['_cr_stats']['errors'], 0)
        self.assertNotIn('Never_Export_Log_Error', '\n'.join(self.f.h.logs))

    def test_source_keeps_exact_parameter_and_name_getter_boundaries(self):
        tree = ast.parse(runtime.SOURCE.read_bytes())
        reader = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_cr_inspect')
        getters = [n for n in ast.walk(reader) if isinstance(n,ast.Call)
                   and isinstance(n.func,ast.Attribute) and n.func.attr=='get' and len(n.args)>1]
        fields = [(n.args[0].id,n.args[1].value) for n in getters
                  if isinstance(n.args[0],ast.Name) and isinstance(n.args[1],ast.Constant)]
        self.assertEqual([f for f in fields if f[0]=='args'], [('args','SkillInstigator'),('args','Definition')])
        self.assertEqual(fields.count(('definition','Name')), 1)
        callback = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_cr_callback')
        observe = next(n for n in callback.body if isinstance(n,ast.FunctionDef))
        self.assertTrue(all(isinstance(n.value,ast.Constant) and n.value.value is None
                            for n in ast.walk(observe) if isinstance(n,ast.Return)))
        closure = self.f.start().__closure__
        self.assertEqual(tuple(c.cell_contents for c in closure), (1,))


if __name__ == '__main__':
    unittest.main()
