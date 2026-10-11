"""Read-only v0.2.12 log text consistency; never SDK identity or game proof."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

VERSION = '0.2.12'
RUNTIME_SHA256 = '41fd2dd9e22bcfa64fbddfc19b881f6950362656e047b212b00eb86f33a01f73'
MAX_BYTES = 16 * 1024 * 1024
MAX_LINE = 16384
TAG = 'UVH-DEATHTRAP'
EVENT = re.compile(r'^(?:(?:\d{4}-\d{2}-\d{2} [^|\r\n]{1,512}INFO\| )?\[UVH-BOOST\] )?\[(UVH-[A-Z]+)\] (.*)$')
METHODS = ('GetSkillManager', 'ActivateSkill', 'DeactivateSkill')
FIELDS = ('Duration', 'DurationBaseValue', 'ActivatedTime', 'SkillInstigator', 'Definition', 'DurationModifierStack')
FAMILIES = {'UVH-STATE', 'UVH-UI', 'UVH-UPGRADE', 'UVH-INITNODE'}
END = re.compile(r'^END coverage=(COMPLETE|CAPPED|UNAVAILABLE) observers_added=0 native_calls=0 writes=0 signature=NOT_ESTABLISHED$')
FINAL = re.compile(r'^FINAL points=(\([^\r\n]{1,128}\)) ranks=(\([^\r\n]{1,128}\)) unchanged_from_start=True$')
ABORT = 'ABORT coverage=REFUSED; invalid/unavailable/drifting state or metadata; no repair'
UNAVAILABLE = 'UNAVAILABLE metadata collection incomplete; no signature or absence inferred'
RESTORE = re.compile(r"^RESTORE result=True skills=\['MorePep', 'Myelin'\] cells=\[True, False, True\] \(methods (?:assign|slice|clear\+extend), (?:assign|slice|clear\+extend)\)$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, names):
    require(type(value) is dict and set(value) == set(names.split()), 'unexpected metadata schema')


def label(value, path=False):
    require(type(value) is str and 0 < len(value) <= (384 if path else 96)
            and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.:]*' if path else r'[A-Za-z_][A-Za-z0-9_]*', value) is not None,
            'invalid canonical label/path')


def integer(value, maximum, minimum=0):
    require(type(value) is int and minimum <= value <= maximum, 'invalid numeric metadata')


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('nonfinite JSON scalar: ' + value)


def row_schema(row):
    require(type(row) is dict, 'metadata row is not an object')
    kind = row.get('kind')
    if kind == 'CLASS':
        keys(row, 'kind target path coverage ancestry')
        require(row['target'] in ('controller', 'manager', 'active_skill_class', 'definition_class'), 'unknown root')
        label(row['path'], True)
        require(row['coverage'] in ('COMPLETE', 'CAPPED'), 'invalid class coverage')
        nodes = row['ancestry']
        require(type(nodes) is list and 1 <= len(nodes) <= 8, 'ancestry bound')
        require(row['coverage'] != 'CAPPED' or len(nodes) == 8, 'capped ancestry must have eight nodes')
        paths = []
        for node in nodes:
            keys(node, 'name path'); label(node['name']); label(node['path'], True)
            require(node['path'].endswith('.'+node['name']), 'class name/path disagreement')
            paths.append(node['path'])
        require(len(set(paths)) == len(paths) and paths[0] == row['path'], 'duplicate ancestry or root mismatch')
    elif kind in ('FUNCTION', 'FIELD') and row.get('coverage') == 'UNAVAILABLE':
        keys(row, 'kind name coverage')
        require(row['name'] in (METHODS if kind == 'FUNCTION' else ('ActiveSkills', *FIELDS)), 'unknown unavailable row')
    elif kind == 'FUNCTION':
        keys(row, 'kind name path coverage flags num_params params_size return_offset signature properties')
        require(row['name'] in METHODS and row['coverage'] in ('COMPLETE','CAPPED'), 'invalid function')
        require(row['signature'] == 'NOT_ESTABLISHED', 'signature cannot be established')
        label(row['path'], True)
        for field, bound in (('flags',2**32-1),('num_params',255),('params_size',65535),('return_offset',65535)):
            integer(row[field], bound)
        props = row['properties']
        require(type(props) is list and len(props) <= 16, 'function property bound')
        require(row['coverage'] != 'CAPPED' or len(props) == 16, 'capped function must have sixteen properties')
        names, returns = [], []
        for prop in props:
            keys(prop, 'name type flags offset dimension element_size')
            scalar_schema(prop, class_field=False)
            names.append(prop['name'])
            if prop['flags'] & 0x400:
                returns.append(prop)
        require(len(set(names)) == len(names) and len(returns) <= 1, 'duplicate property or ambiguous return')
        if returns:
            require(returns[0]['offset'] == row['return_offset'], 'return offset disagreement')
    elif kind == 'FIELD':
        common = 'kind name type flags offset dimension element_size coverage inner_type owner '
        keys(row, common + ('element_class' if row.get('name') == 'ActiveSkills' else 'declared_class'))
        require(row['name'] in ('ActiveSkills', *FIELDS) and row['coverage'] == 'COMPLETE', 'invalid field')
        scalar_schema(row, class_field=True); label(row['owner'], True)
        label(row['inner_type'])
        declared = row.get('element_class',row.get('declared_class'))
        if declared != 'NOT_APPLICABLE': label(declared, True)
    elif kind == 'DISCOVERY':
        if row.get('coverage') == 'UNAVAILABLE':
            keys(row, 'kind target coverage'); require(row['target'] == 'manager','invalid discovery')
        else:
            keys(row, 'kind source_function return_property return_class')
            require(row['source_function'] == 'GetSkillManager', 'invalid discovery source')
            label(row['return_property']); label(row['return_class'], True)
    else:
        raise ValueError('unknown metadata kind')


def scalar_schema(row, class_field):
    label(row['name']); label(row['type'])
    integer(row['flags'],2**64-1); integer(row['offset'],1048576)
    integer(row['dimension'],1 if class_field else 64,1); integer(row['element_size'],65536,1)
    require(row['offset']+row['dimension']*row['element_size'] <= 1048576, 'property aggregate bound')
    require(not class_field or not row['flags'] & 0x580, 'class field has parameter flags')


def validate_rows(rows):
    """Exact emitted sequence/observable relations; no native subtype inference."""
    require(len(rows) <= 15, 'metadata row bound')
    for row in rows: row_schema(row)
    index = 0
    def take(kind, name=None):
        nonlocal index
        require(index < len(rows), 'missing metadata row')
        row = rows[index]; index += 1
        require(row['kind'] == kind and (name is None or row.get('name',row.get('target')) == name),
                'unexpected metadata row order')
        return row
    controller = take('CLASS','controller')
    owners = {n['path'] for n in controller['ancestry']}
    functions = [take('FUNCTION',name) for name in METHODS]
    for function in functions:
        if function['coverage'] != 'UNAVAILABLE':
            require(any(function['path'] in (owner+':'+function['name'],owner+'.'+function['name']) for owner in owners),
                    'function path is outside controller ancestry')
    marked = [p for p in functions[0].get('properties',[]) if p['flags'] & 0x400]
    if index < len(rows) and rows[index]['kind'] == 'DISCOVERY':
        discovery = take('DISCOVERY')
        require(discovery.get('coverage') == 'UNAVAILABLE' and not marked, 'contradictory unavailable discovery')
    else:
        manager = take('CLASS','manager'); discovery = take('DISCOVERY')
        require(discovery.get('return_class') == manager['path'] and len(marked) == 1
                and discovery.get('return_property') == marked[0]['name'], 'return/manager discovery mismatch')
        manager_owners = {n['path'] for n in manager['ancestry']}
        if index < len(rows) and rows[index]['kind'] == 'FIELD':
            array = take('FIELD','ActiveSkills')
            require(array['coverage'] == 'UNAVAILABLE', 'missing active skill root')
        else:
            skill = take('CLASS','active_skill_class'); array = take('FIELD','ActiveSkills')
            require(array.get('element_class') == skill['path'] and array.get('owner') in manager_owners,
                    'ActiveSkills owner/element class mismatch')
            require(array['inner_type'] != 'NOT_APPLICABLE', 'ActiveSkills must have an inner descriptor')
            skill_owners = {n['path'] for n in skill['ancestry']}
            for name in FIELDS:
                definition = None
                if name == 'Definition' and index < len(rows) and rows[index]['kind'] == 'CLASS':
                    definition = take('CLASS','definition_class')
                field = take('FIELD',name)
                if field['coverage'] == 'UNAVAILABLE':
                    require(definition is None, 'unavailable definition has a discovered root')
                    continue
                require(field['owner'] in skill_owners, 'field owner is outside skill ancestry')
                if name == 'Definition':
                    require(definition is not None and field['declared_class'] == definition['path'], 'definition class mismatch')
                elif name == 'SkillInstigator':
                    require(field['declared_class'] in owners, 'instigator class outside controller ancestry')
                else:
                    require(field['declared_class'] == 'NOT_APPLICABLE', 'unexpected declared scalar/array class')
                if name != 'DurationModifierStack':
                    require(field['inner_type'] == 'NOT_APPLICABLE', 'unexpected scalar/object inner')
                else:
                    require(field['inner_type'] != 'NOT_APPLICABLE', 'modifier array must have an inner descriptor')
    require(index == len(rows), 'extra metadata rows')
    roots = [r['path'] for r in rows if r['kind'] == 'CLASS']
    require(len(roots) <= 4 and len(set(roots)) == len(roots), 'duplicate/excessive roots')
    statuses = {r.get('coverage') for r in rows}
    return 'CAPPED' if 'CAPPED' in statuses else 'UNAVAILABLE' if 'UNAVAILABLE' in statuses else 'COMPLETE'


def state_tuple(text, count):
    value = ast.literal_eval(text)  # bounded scalar tuples only; never eval commands
    require(type(value) is tuple and len(value) == count and str(value) == text
            and all(type(v) is int and v >= 0 for v in value), 'invalid canonical FINAL state')
    return value


def review_bytes(raw):
    report = {'source':{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},
              'grammar':{'version':VERSION,'runtime_sha256':RUNTIME_SHA256},'calls':[], 'issues':[],
              'cleanup':{'restorations':[],'native_restored_lines':[],'observers':[],'errors':[]},
              'separate_checks':dict.fromkeys(('installed_archive_equality','process_exit','capture_origin',
                    'SDK_identity','internal_start_state','native_property_links_and_sizes','native_subtype_compatibility',
                    'unlogged_cap_lookahead'),'NOT_CHECKED'),
              'game_behavior':'NOT_ESTABLISHED_BY_TOOL'}
    try:
        require(len(raw) <= MAX_BYTES, 'input exceeds sixteen MiB')
        text = raw.decode('utf-8-sig')
        lines = text.splitlines()
        require(len(lines) <= 100000 and all(len(line) <= MAX_LINE for line in lines), 'input line bound')
    except (ValueError,UnicodeError) as exc:
        report.update(status='INPUT_ERROR',log_text_acceptable=False,input_error=str(exc)); return report
    if not text.endswith('\n'): report['issues'].append('missing final newline; possible truncation')
    current, versions = None, set()
    for number, line in enumerate(lines,1):
        event = EVENT.fullmatch(line)
        if not event:
            if '[UVH-DEATHTRAP]' in line or 'Traceback (most recent call last):' in line:
                report['issues'].append(f'line {number}: malformed diagnostic prefix or traceback')
            continue
        tag,payload = event.groups()
        if re.match(r'^(?:BEGIN|START) v\d',payload): versions.update(re.findall(r'\bv(\d+\.\d+\.\d+)\b',payload))
        cleanup = report['cleanup']
        if tag in FAMILIES or tag == 'UVH-TRACE':
            pattern = (r'Observers remaining=(\d{1,3})' if tag == 'UVH-INITNODE' else
                       r'STOP remaining=(\d{1,3}); events=\d{1,10}' if tag == 'UVH-TRACE' else
                       r'STOP remaining=(\d{1,3}) captured=\d{1,10} callbacks=\d{1,10} skipped=\d{1,10}')
            match = re.fullmatch(pattern,payload)
            if match:
                cleanup['observers'].append({'line':number,'family':tag,'remaining':int(match[1])})
                if int(match[1]): cleanup['errors'].append({'line':number,'reason':'nonzero observer cleanup'})
            elif payload.startswith(('STOP remaining=','Observers remaining=','Hook removal ERROR','Removal ERROR',
                         'Rollback failed;','Native arrays changed independently;','Cannot verify rollback ownership;')):
                cleanup['errors'].append({'line':number,'reason':'failed/malformed cleanup'})
            if report['calls'] and payload.startswith(('START ','Active observers=','ARMED.')):
                cleanup['errors'].append({'line':number,'reason':'another experiment started after metadata call'})
        if tag == 'UVH-NEWNODE' and payload.startswith('RESTORE result='):
            cleanup['restorations'].append({'line':number,'verified':RESTORE.fullmatch(payload) is not None})
            if RESTORE.fullmatch(payload) is None: cleanup['errors'].append({'line':number,'reason':'failed/malformed restoration'})
        if tag == 'UVH-NEWNODE' and payload.startswith('Removal ERROR'):
            cleanup['errors'].append({'line':number,'reason':'failed node removal'})
        if tag == 'UVH-BOOST' and payload.startswith(('ERROR restore:', 'WARNING rollback failed:',
                       'RESTORE READBACK MISMATCH:', 'BEGIN experimental +15 seconds', 'WRITE VERIFIED:')):
            cleanup['errors'].append({'line':number,'reason':'manual duration activity/failure outside metadata protocol'})
        if tag == 'UVH-INITNODE' and payload == 'NATIVE ARRAYS RESTORED. Restart BL2 to clear any player/UI cache.':
            cleanup['native_restored_lines'].append(number)
        if tag != TAG: continue
        if payload.startswith('BEGIN '):
            if current is not None: current['issues'].append('new BEGIN before terminal record')
            if len(report['calls']) >= 128:
                report['issues'].append('call bound exceeded'); break
            current = {'begin_line':number,'last_line':number,'rows':[],'final':None,'coverage':None,
                       'terminal':None,'issues':[]}
            report['calls'].append(current)
            if payload != 'BEGIN v0.2.12 metadata_only=True': current['issues'].append('unsupported/malformed BEGIN')
            continue
        if current is None:
            report['issues'].append(f'line {number}: diagnostic record without BEGIN'); continue
        current['last_line'] = number
        try:
            if payload.startswith('METADATA '):
                require(current['final'] is None and len(current['rows']) < 15,'metadata after FINAL or row bound')
                row = json.loads(payload[9:],object_pairs_hook=strict_object,parse_constant=reject_constant)
                row_schema(row);current['rows'].append(row)
            elif payload.startswith('FINAL '):
                match = FINAL.fullmatch(payload); require(match is not None and current['final'] is None,'malformed/duplicate FINAL')
                points,ranks = state_tuple(match[1],2),state_tuple(match[2],3)
                require(ranks[0] == 0,'diagnostic candidate rank is not zero')
                current['final'] = {'points':points,'ranks':ranks,'unchanged_assertion':True,
                                    'comparison_to_start':'NOT_CHECKED; start state not logged'}
            elif payload.startswith('END '):
                match = END.fullmatch(payload);require(match is not None and current['final'] is not None,'malformed END or missing FINAL')
                current['coverage'] = match[1]
                require(validate_rows(current['rows']) == match[1],'END coverage contradicts metadata')
                current['terminal'] = 'END'; current = None
            elif payload == ABORT:
                current.update(terminal='ABORT',coverage='REFUSED');current = None
            elif payload == UNAVAILABLE:
                current.update(terminal='UNAVAILABLE',coverage='UNAVAILABLE');current = None
            else:
                raise ValueError('unrecognized diagnostic record; BASELINE is not emitted')
        except (ValueError,SyntaxError,TypeError,KeyError,RecursionError,OverflowError) as exc:
            current['issues'].append(f'line {number}: {exc}')
    for call in report['calls']:
        call['outcome'] = ('INVALID' if call['issues'] else 'REFUSED' if call['terminal'] == 'ABORT'
                           else 'INCOMPLETE_UNAVAILABLE' if call['terminal'] == 'UNAVAILABLE'
                           else 'INCOMPLETE' if call['terminal'] is None else call['coverage'])
    report['versions'] = sorted(versions)
    if versions and versions != {VERSION}: report['issues'].append('mixed/unsupported versions')
    last = max((call['last_line'] for call in report['calls']),default=0)
    cleanup = report['cleanup']
    restorations = [r for r in cleanup['restorations'] if r['line'] > last]
    cleanup['restoration_asserted_after_last_call'] = (bool(restorations) and all(r['verified'] for r in restorations)
        and any(n > restorations[-1]['line'] for n in cleanup['native_restored_lines']))
    observations = [r for r in cleanup['observers'] if r['line'] > last]
    cleanup['four_families_zero_after_last_call'] = (FAMILIES <= {r['family'] for r in observations}
        and all(r['remaining'] == 0 for r in observations))
    outcomes = {c['outcome'] for c in report['calls']}
    status = ('NO_CALLS' if not outcomes else 'REFUSED' if report['issues'] or cleanup['errors'] or outcomes & {'INVALID','REFUSED'}
              else 'PARTIAL' if outcomes != {'COMPLETE'} or not cleanup['restoration_asserted_after_last_call']
                    or not cleanup['four_families_zero_after_last_call'] else 'COMPLETE_LOG_TEXT')
    report.update(status=status,log_text_acceptable=status == 'COMPLETE_LOG_TEXT')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path,help='preserved UTF-8 input; JSON report goes to stdout')
    args = parser.parse_args(argv)
    try:
        with args.log.open('rb') as stream: raw = stream.read(MAX_BYTES+1)
        report = review_bytes(raw)
    except OSError as exc:
        report = {'status':'INPUT_ERROR','input_error':type(exc).__name__,'log_text_acceptable':False}
    print(json.dumps(report,indent=2))
    return 2 if report['status'] == 'INPUT_ERROR' else 0 if report['log_text_acceptable'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
