"""Read-only fingerprints, ZIP integrity and explicitly recorded source relationships."""
import argparse
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = 'evidence/verified_artifact_inventory.json'
FOLDER = 'UltimateVaultHunterDeathtrapBoost'
ENTRIES = {FOLDER + '/' + name for name in ('__init__.py', 'pyproject.toml', 'README.txt')}
MAX_FILE_BYTES = 64 * 1024 * 1024
AREAS = ('evidence/', 'dist/', 'archive/tested_runtime/', 'sdk_mods/' + FOLDER + '/')


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def relative_path(value):
    if (type(value) is not str or not value or '\\' in value or ':' in value
            or '\x00' in value or value.startswith('/')
            or any(part in ('', '.', '..') or part.endswith((' ', '.')) for part in value.split('/'))
            or not value.startswith(AREAS)):
        raise ValueError('noncanonical or unsupported artifact path')
    return value


def safe_path(root, value):
    path = (root / relative_path(value)).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('artifact path escapes repository')
    return path


def load_inventory(root, name=INVENTORY):
    with safe_path(root, name).open('rb') as stream:
        raw = stream.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError('inventory exceeds 1 MiB bound')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=strict_object)


def validate_inventory(manifest):
    required = {'schema_version', 'reference_commit', 'immutable_files', 'current_files',
                'snapshot_relationships', 'current_relationships', 'evidence_limits'}
    if type(manifest) is not dict or set(manifest) != required:
        raise ValueError('unexpected inventory schema')
    if type(manifest['schema_version']) is not int or manifest['schema_version'] != 1:
        raise ValueError('unsupported schema version')
    if type(manifest['reference_commit']) is not str or re.fullmatch('[0-9a-f]{40}', manifest['reference_commit']) is None:
        raise ValueError('invalid reference commit')
    if (type(manifest['evidence_limits']) is not list
            or not all(type(v) is str for v in manifest['evidence_limits'])):
        raise ValueError('invalid evidence limits')
    groups, seen = {}, set()
    for group in ('immutable_files', 'current_files'):
        entries = manifest[group]
        if type(entries) is not list or (group == 'immutable_files' and not entries):
            raise ValueError('missing artifact entries')
        groups[group] = {}
        for entry in entries:
            if type(entry) is not dict or set(entry) != {'path', 'bytes', 'sha256', 'provenance'}:
                raise ValueError('invalid file record')
            name = relative_path(entry['path'])
            if name.casefold() in seen:
                raise ValueError('duplicate artifact path')
            seen.add(name.casefold())
            if type(entry['bytes']) is not int or not 0 <= entry['bytes'] <= MAX_FILE_BYTES:
                raise ValueError('invalid artifact size')
            if type(entry['sha256']) is not str or re.fullmatch('[0-9a-f]{64}', entry['sha256']) is None:
                raise ValueError('invalid SHA256')
            if type(entry['provenance']) is not str or not entry['provenance']:
                raise ValueError('missing provenance')
            if name == INVENTORY:
                raise ValueError('inventory cannot fingerprint itself')
            groups[group][name] = entry
    for name, group in (('snapshot_relationships', 'immutable_files'), ('current_relationships', 'current_files')):
        if type(manifest[name]) is not list:
            raise ValueError('invalid relationships')
        zips = set()
        for relation in manifest[name]:
            if type(relation) is not dict or set(relation) != {'zip', 'entries_equal_files'}:
                raise ValueError('invalid relationship record')
            zip_path = relative_path(relation['zip'])
            mapping = relation['entries_equal_files']
            if zip_path in zips or zip_path not in groups[group] or not zip_path.endswith('.zip'):
                raise ValueError('unknown or duplicate relationship archive')
            zips.add(zip_path)
            if type(mapping) is not dict or set(mapping) != ENTRIES:
                raise ValueError('relationship must name the exact three entries')
            for file in mapping.values():
                if relative_path(file) not in groups[group]:
                    raise ValueError('relationship file not inventoried in its group')
    return groups


def read_verified(root, entry):
    path = safe_path(root, entry['path'])
    with path.open('rb') as stream:
        data = stream.read(entry['bytes'] + 1)
    if len(data) != entry['bytes']:
        raise ValueError('byte size differs')
    if hashlib.sha256(data).hexdigest() != entry['sha256']:
        raise ValueError('SHA256 differs')
    with path.open('rb') as stream:
        if stream.read(entry['bytes'] + 1) != data:
            raise ValueError('file changed during verification')
    return data


def check_zip(data):
    with ZipFile(io.BytesIO(data)) as z:
        if len(z.namelist()) != 3 or set(z.namelist()) != ENTRIES:
            raise ValueError('ZIP is not the exact three-file folder package')
        if sum(info.file_size for info in z.infolist()) > MAX_FILE_BYTES:
            raise ValueError('ZIP unpacked bytes exceed bound')
        if z.testzip() is not None:
            raise ValueError('ZIP CRC failed')
        payloads = {name: z.read(name) for name in ENTRIES}
        compile(payloads[FOLDER + '/__init__.py'], 'archived runtime (never executed)', 'exec')
        return payloads


def verify(root, manifest, check_current=False):
    root = Path(root).resolve()
    try:
        groups = validate_inventory(manifest)
    except (ValueError, TypeError) as exc:
        return {'status': 'FAIL', 'schema_error': str(exc), 'manifest_origin': 'NOT_CHECKED_BY_TOOL'}
    report = {'schema_version': 1, 'reference_commit': manifest['reference_commit'],
              'manifest_origin': 'NOT_CHECKED_BY_TOOL', 'game_behavior': 'NOT_ESTABLISHED',
              'immutable': {'verified_files': 0, 'verified_archives': 0, 'relationships': 0, 'errors': []},
              'current': {'status': 'NOT_CHECKED', 'verified_files': 0, 'verified_archives': 0,
                          'relationships': 0, 'errors': []}}
    for group, output, relations in (('immutable_files', 'immutable', 'snapshot_relationships'),
                                      ('current_files', 'current', 'current_relationships')):
        if output == 'current' and not check_current:
            continue
        section, verified, archives = report[output], {}, {}
        for name, entry in groups[group].items():
            try:
                data = read_verified(root, entry)
                verified[name] = data
                section['verified_files'] += 1
                if name.endswith('.zip'):
                    archives[name] = check_zip(data)
                    section['verified_archives'] += 1
            except Exception as exc:
                section['errors'].append({'path': name, 'error': str(exc)})
        for relation in manifest[relations]:
            try:
                payloads = archives[relation['zip']]
                for entry, name in relation['entries_equal_files'].items():
                    if payloads[entry] != verified[name]:
                        raise ValueError('archive entry differs from recorded file: ' + entry)
                section['relationships'] += 1
            except Exception as exc:
                section['errors'].append({'relationship': relation['zip'], 'error': str(exc)})
        section['status'] = 'FAIL' if section['errors'] else 'PASS'
    known = set(groups['immutable_files']) | set(groups['current_files']) | {INVENTORY}
    unlisted = []
    for directory in ('evidence', 'dist', 'archive/tested_runtime'):
        folder = root / directory
        if folder.exists():
            unlisted.extend(str(path.relative_to(root)).replace('\\', '/') for path in folder.rglob('*')
                            if path.is_file() and str(path.relative_to(root)).replace('\\', '/') not in known)
    report['unlisted_artifact_paths'] = sorted(unlisted)
    report['unlisted_policy'] = 'reported only; no original fingerprint or acceptance inferred'
    report['status'] = ('PASS' if report['immutable']['status'] == 'PASS'
                        and report['current']['status'] != 'FAIL' else 'FAIL')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', default=INVENTORY, help='repository-relative inventory JSON')
    parser.add_argument('--check-current', action='store_true', help='also require recorded prepared-build bytes')
    args = parser.parse_args(argv)
    try:
        report = verify(ROOT, load_inventory(ROOT, args.inventory), args.check_current)
    except (OSError, ValueError) as exc:
        report = {'status': 'FAIL', 'input_error': str(exc), 'manifest_origin': 'NOT_CHECKED_BY_TOOL'}
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
