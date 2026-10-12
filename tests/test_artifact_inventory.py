"""Temporary byte/ZIP fixtures; no runtime or SDK code is executed."""
import copy
import hashlib
import importlib.util
import io
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('artifact_verifier', ROOT / 'scripts/verify_artifact_inventory.py')
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


class ArtifactInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='artifact_fixture_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = {'schema_version': 1, 'reference_commit': 'a'*40, 'immutable_files': [],
                         'current_files': [], 'snapshot_relationships': [], 'current_relationships': [],
                         'evidence_limits': ['synthetic fixture; no game evidence']}
        self.add_file('evidence/original.log', b'preserved\n')

    def add_file(self, name, data, current=False):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        record = {'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                  'provenance': 'synthetic test fixture'}
        self.manifest['current_files' if current else 'immutable_files'].append(record)
        return record

    def package(self, name='dist/original.zip', runtime=b'raise RuntimeError("must never execute")\n', current=False):
        values = {'__init__.py': runtime, 'pyproject.toml': b'[tool.sdkmod]\nversion="test"\n',
                  'README.txt': b'frozen readme\n'}
        buf = io.BytesIO()
        with ZipFile(buf, 'w') as z:
            for key, value in values.items():
                z.writestr(tool.FOLDER + '/' + key, value)
        record = self.add_file(name, buf.getvalue(), current)
        return values, record

    def check(self, current=False):
        return tool.verify(self.root, self.manifest, current)

    def test_valid_bytes_pass_without_inventing_game_or_origin_evidence(self):
        result = self.check()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['immutable']['verified_files'], 1)
        self.assertEqual(result['manifest_origin'], 'NOT_CHECKED_BY_TOOL')
        self.assertEqual(result['game_behavior'], 'NOT_ESTABLISHED')

    def test_missing_original_fails_without_rebuilding_it(self):
        (self.root / 'evidence/original.log').unlink()
        self.assertEqual(self.check()['status'], 'FAIL')
        self.assertFalse((self.root / 'evidence/original.log').exists())

    def test_same_size_corruption_fails_sha(self):
        (self.root / 'evidence/original.log').write_bytes(b'corrupted\n')
        self.assertEqual(self.check()['status'], 'FAIL')
        self.assertIn('SHA256', self.check()['immutable']['errors'][0]['error'])

    def test_changed_size_fails_before_zip_or_source_relationships(self):
        (self.root / 'evidence/original.log').write_bytes(b'x')
        self.assertIn('byte size', self.check()['immutable']['errors'][0]['error'])

    def test_duplicate_path_refuses(self):
        self.manifest['immutable_files'].append(copy.deepcopy(self.manifest['immutable_files'][0]))
        self.assertIn('duplicate artifact path', self.check()['schema_error'])

    def test_case_variant_path_refuses_for_windows_compatibility(self):
        extra = copy.deepcopy(self.manifest['immutable_files'][0]); extra['path'] = 'evidence/Original.log'
        self.manifest['immutable_files'].append(extra)
        self.assertIn('duplicate artifact path', self.check()['schema_error'])

    def test_overlap_of_immutable_and_current_refuses(self):
        self.manifest['current_files'].append(copy.deepcopy(self.manifest['immutable_files'][0]))
        self.assertIn('duplicate artifact path', self.check()['schema_error'])

    def test_traversal_absolute_backslash_and_private_area_refuse(self):
        for name in ('../private_backups/x', '/absolute', 'C:/outside', 'evidence/../x',
                     'evidence\\x', 'private_backups/x', 'evidence//x', 'evidence/x.'):
            with self.subTest(name=name):
                bad = copy.deepcopy(self.manifest); bad['immutable_files'][0]['path'] = name
                self.assertEqual(tool.verify(self.root, bad)['status'], 'FAIL')

    def test_invalid_size_or_sha_refuses(self):
        for key, value in (('bytes', True), ('bytes', -1), ('bytes', tool.MAX_FILE_BYTES+1),
                           ('sha256', 'a'*63), ('sha256', 'Z'*64)):
            with self.subTest(key=key, value=value):
                bad = copy.deepcopy(self.manifest); bad['immutable_files'][0][key] = value
                self.assertEqual(tool.verify(self.root, bad)['status'], 'FAIL')

    def test_empty_immutable_inventory_cannot_pass(self):
        self.manifest['immutable_files'] = []
        self.assertEqual(self.check()['status'], 'FAIL')

    def test_bool_schema_and_unknown_fields_refuse(self):
        for bad in ({**self.manifest, 'schema_version': True}, {**self.manifest, 'unexpected': 1}):
            self.assertEqual(tool.verify(self.root, bad)['status'], 'FAIL')

    def test_inventory_self_fingerprint_refuses(self):
        self.manifest['immutable_files'][0]['path'] = tool.INVENTORY
        self.assertIn('itself', self.check()['schema_error'])

    def test_duplicate_json_key_refuses_before_verification(self):
        path = self.root / tool.INVENTORY; path.write_text('{"schema_version":1,"schema_version":2}')
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            tool.load_inventory(self.root)

    def test_non_utf8_inventory_refuses(self):
        path = self.root / tool.INVENTORY; path.write_bytes(b'\xff')
        with self.assertRaises(ValueError):
            tool.load_inventory(self.root)

    def test_valid_zip_compiles_but_never_executes_runtime(self):
        self.package()
        result = self.check()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['immutable']['verified_archives'], 1)

    def test_invalid_zip_fails_even_if_its_recorded_hash_matches(self):
        self.add_file('dist/bad.zip', b'not a ZIP')
        self.assertEqual(self.check()['status'], 'FAIL')

    def test_extra_or_duplicate_zip_entry_refuses(self):
        baseline = copy.deepcopy(self.manifest)
        for duplicate in (False, True):
            with self.subTest(duplicate=duplicate):
                self.manifest = copy.deepcopy(baseline)
                buf = io.BytesIO()
                with ZipFile(buf, 'w') as z:
                    for name in tool.ENTRIES: z.writestr(name, b'# inert\n')
                    z.writestr(tool.FOLDER+'/README.txt' if duplicate else 'extra.txt', b'extra')
                name = 'dist/extra'+str(duplicate)+'.zip'; self.add_file(name, buf.getvalue())
                self.assertEqual(self.check()['status'], 'FAIL')

    def test_bad_crc_fails_after_matching_whole_archive_hash(self):
        values, record = self.package()
        path = self.root/record['path']
        data = bytearray(path.read_bytes())
        offset = data.find(values['__init__.py'])
        self.assertGreaterEqual(offset, 0)
        data[offset] ^= 1
        path.write_bytes(data)
        record['sha256'] = hashlib.sha256(data).hexdigest()
        result = self.check()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('CRC', result['immutable']['errors'][-1]['error'])

    def test_archive_syntax_error_refuses_without_execution(self):
        self.package(runtime=b'def broken(\n')
        self.assertEqual(self.check()['status'], 'FAIL')

    def test_unpacked_size_bound_refuses_before_decompression(self):
        _, record = self.package()
        path = self.root/record['path']; data = bytearray(path.read_bytes())
        central = data.find(b'PK\x01\x02')
        self.assertGreaterEqual(central, 0)
        struct.pack_into('<I', data, central+24, tool.MAX_FILE_BYTES+1)
        path.write_bytes(data); record['sha256'] = hashlib.sha256(data).hexdigest()
        result = self.check()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('unpacked bytes', result['immutable']['errors'][-1]['error'])

    def relationship(self, values, current=False):
        prefix = 'sdk_mods/'+tool.FOLDER+'/' if current else 'archive/tested_runtime/probe/'
        mapping = {}
        for name, data in values.items():
            path = prefix+name; self.add_file(path, data, current)
            mapping[tool.FOLDER+'/'+name] = path
        relation = {'zip': 'dist/current.zip' if current else 'dist/original.zip', 'entries_equal_files': mapping}
        self.manifest['current_relationships' if current else 'snapshot_relationships'].append(relation)

    def test_exact_historical_snapshot_relationship_passes(self):
        values, _ = self.package(); self.relationship(values)
        self.assertEqual(self.check()['immutable']['relationships'], 1)

    def test_historical_readme_must_not_equal_a_current_readme(self):
        values, _ = self.package(); self.relationship(values)
        self.add_file('sdk_mods/'+tool.FOLDER+'/README.txt', b'new current docs\n', True)
        self.assertEqual(self.check(True)['status'], 'PASS')

    def test_mismatched_snapshot_refuses_even_when_both_hashes_are_valid(self):
        values, _ = self.package(); values['README.txt'] = b'different historical bytes\n'; self.relationship(values)
        self.assertEqual(self.check()['status'], 'FAIL')
        self.assertIn('archive entry differs', self.check()['immutable']['errors'][-1]['error'])

    def test_unknown_relationship_target_refuses(self):
        values, _ = self.package(); self.relationship(values)
        self.manifest['snapshot_relationships'][0]['entries_equal_files'][tool.FOLDER+'/README.txt'] = 'evidence/not_inventoried'
        self.assertEqual(self.check()['status'], 'FAIL')

    def test_current_drift_is_separate_and_explicit_check_fails(self):
        self.add_file('sdk_mods/'+tool.FOLDER+'/README.txt', b'old\n', True)
        (self.root/'sdk_mods'/tool.FOLDER/'README.txt').write_bytes(b'new\n')
        self.assertEqual(self.check()['status'], 'PASS')
        self.assertEqual(self.check()['current']['status'], 'NOT_CHECKED')
        result = self.check(True)
        self.assertEqual(result['immutable']['status'], 'PASS')
        self.assertEqual(result['current']['status'], 'FAIL')

    def test_current_zip_and_sources_can_be_checked_explicitly(self):
        values, _ = self.package('dist/current.zip', current=True); self.relationship(values, True)
        self.assertEqual(self.check(True)['current']['relationships'], 1)

    def test_unlisted_new_file_is_reported_without_original_hash(self):
        path = self.root/'evidence/new_capture.log'; path.write_bytes(b'new unknown data')
        result = self.check()
        self.assertEqual(result['status'], 'PASS')
        self.assertIn('evidence/new_capture.log', result['unlisted_artifact_paths'])
        self.assertEqual(result['immutable']['verified_files'], 1)

    def test_changed_double_read_fails(self):
        real_open = Path.open; calls = 0
        def changing_open(path, *args, **kwargs):
            nonlocal calls
            if path == self.root/'evidence/original.log':
                calls += 1
                if calls == 2: return io.BytesIO(b'changed!')
            return real_open(path, *args, **kwargs)
        with patch.object(Path, 'open', changing_open):
            self.assertEqual(self.check()['status'], 'FAIL')

    def test_cli_failed_input_returns_nonzero_and_json(self):
        output = io.StringIO()
        with patch.object(tool, 'ROOT', self.root), patch('sys.stdout', output):
            self.assertEqual(tool.main([]), 1)
        self.assertEqual(json.loads(output.getvalue())['status'], 'FAIL')
