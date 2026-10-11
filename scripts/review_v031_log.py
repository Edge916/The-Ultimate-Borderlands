"""Read a preserved v0.2.11 diagnostic log; emit evidence, never game commands."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

VERSION = '0.2.11'
PRESENTATION = 'GD_Tulip_Mechromancer_Skills.LittleBigTrouble.Myelin:AttributePresentationDefinition_0'
QUOTE = r"(?:'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\")"
EVENT = re.compile(r'^(?:\d{4}-\d{2}-\d{2} [^|\r\n]{1,512}INFO\| \[UVH-BOOST\] )?\[(UVH-[A-Z]+)\] (.*)$')
STATE = re.compile(r'^(BASELINE|FINAL) points=\((\d{1,10}), (\d{1,10})\) ranks=\((\d{1,10}), (\d{1,10}), (\d{1,10})\)( unchanged_from_start=True)?$')
BEGIN = re.compile(r'^BEGIN v(\d+\.\d+\.\d+) combined metadata snapshot \(READ ONLY; DO NOT BUY\)$')
REFERENCE = re.compile(r'^REFERENCE skill=Myelin index=1 count=(\d{1,3}) path=(' + QUOTE + r')$')
FIELD = re.compile(r'^FIELD wrapper=(KNOWN_ABSENT|UNKNOWN|SDK_UOBJECT) actual_class=(SDK_UCLASS|UNAVAILABLE) status=(VERIFIED_ABSENCE|VERIFIED_METADATA|PARTIAL_UNAVAILABLE)$')
LABEL = re.compile(r'^(CLASS role=(DECLARED|ACTUAL)|ANCESTOR depth=(\d{1,2})) name=(' + QUOTE + r') path=(' + QUOTE + r')$')
ANCESTRY = re.compile(r'^ANCESTRY coverage=(COMPLETE|CAPPED|CYCLE|UNAVAILABLE|NOT_APPLICABLE) classes=(\d{1,2}) declared_relation=(EXACT|DERIVED|NO|UNKNOWN)$')
END = 'END combined_checks=wrapper,class,ancestry observers_added=0; no writes/native queries.'
ADVICE = 'Metadata does not authorize gameplay use. DO NOT BUY; CANCEL and exit.'
CLEANUP_TAGS = {'UVH-STATE', 'UVH-UI', 'UVH-UPGRADE', 'UVH-INITNODE'}


def _quoted(value, limit):
    # Runtime writes repr of bounded strings. Never eval statements or objects.
    if len(value) > 4096:
        raise ValueError('quoted metadata exceeds bounds')
    decoded = ast.literal_eval(value)
    if type(decoded) is not str or not 0 < len(decoded) <= limit:
        raise ValueError('metadata is not a bounded nonempty string')
    return decoded


def _new_call(line, version):
    return dict(begin_line=line, terminal_line=None, version=version, baseline=None,
                final=None, reference=None, field=None, classes={}, ancestors=[],
                ancestry=None, observers_added=None, terminal=None, issues=[],
                records=[], outcome=None)


def _record(call, payload, line):
    """Accept only the exact current inspector's emitted structural records."""
    def single(key, value):
        if call[key] is not None:
            raise ValueError('duplicate ' + key)
        call[key] = value
    match = STATE.fullmatch(payload)
    if match:
        kind, *values = match.groups()
        numbers = [int(x) for x in values[:5]]
        suffix = values[5]
        if (kind == 'FINAL') != bool(suffix) or numbers[2] != 0:
            raise ValueError('state marker/grade is inconsistent with inert diagnostic')
        single(kind.lower(), dict(points=numbers[:2], ranks=numbers[2:]))
        return kind
    match = REFERENCE.fullmatch(payload)
    if match:
        count, path = match.groups()
        path = _quoted(path, 384)
        if not 2 <= int(count) <= 256 or path != PRESENTATION:
            raise ValueError('unexpected presentation reference/count')
        single('reference', dict(skill='Myelin', index=1, count=int(count), path=path))
        return 'REFERENCE'
    match = FIELD.fullmatch(payload)
    if match:
        single('field', dict(zip(('wrapper', 'actual_class', 'status'), match.groups())))
        return 'FIELD'
    match = LABEL.fullmatch(payload)
    if match:
        kind, role, depth, name, path = match.groups()
        value = dict(name=_quoted(name, 96), path=_quoted(path, 384))
        if role:
            if role in call['classes']:
                raise ValueError('duplicate class role')
            call['classes'][role] = value
            return 'CLASS'
        depth = int(depth)
        if depth != len(call['ancestors']) or depth >= 8:
            raise ValueError('noncontiguous/out-of-bounds ancestor depth')
        call['ancestors'].append(dict(depth=depth, **value))
        return 'ANCESTOR'
    match = ANCESTRY.fullmatch(payload)
    if match:
        coverage, count, relation = match.groups()
        single('ancestry', dict(coverage=coverage, classes=int(count), declared_relation=relation))
        return 'ANCESTRY'
    if payload == END:
        call['observers_added'] = 0
        return 'END'
    if re.fullmatch(r'FIELD status=UNAVAILABLE getter_error=[A-Za-z_][A-Za-z_0-9]{0,95}', payload):
        single('field', dict(status='UNAVAILABLE', getter_error=payload.split('getter_error=')[1]))
        return 'FIELD'
    raise ValueError('unrecognized/malformed diagnostic record')


def _finish(call):
    issues = call['issues']
    if call['version'] != VERSION:
        issues.append('unsupported diagnostic version')
    terminal = call['terminal']
    if terminal in ('ABORT', 'NOT_INSPECTED'):
        call['outcome'] = 'ABORTED' if terminal == 'ABORT' else 'NOT_INSPECTED'
        if issues:
            call['outcome'] = 'INVALID_OR_INCOMPLETE'
        return
    required = ('baseline', 'reference', 'field', 'ancestry', 'final')
    for key in required:
        if call[key] is None:
            issues.append('missing ' + key)
    if terminal != 'END':
        issues.append('missing END')
    if call['baseline'] != call['final']:
        issues.append('BASELINE/FINAL points or ranks differ')
    ranks = {'BASELINE': 1, 'REFERENCE': 2, 'FIELD': 3, 'CLASS': 4,
             'ANCESTOR': 5, 'ANCESTRY': 6, 'FINAL': 7, 'END': 8}
    order = [ranks[k] for k in call['records'] if k in ranks]
    if order != sorted(order):
        issues.append('diagnostic records out of order')
    field, ancestry = call['field'] or {}, call['ancestry'] or {}
    count, coverage, relation = (ancestry.get(k) for k in ('classes', 'coverage', 'declared_relation'))
    if count != len(call['ancestors']) or count is None or not 0 <= count <= 8:
        issues.append('ancestry count does not match bounded rows')
    if coverage == 'CAPPED' and count != 8:
        issues.append('CAPPED requires eight captured class rows')
    if coverage in ('COMPLETE', 'CYCLE') and not call['ancestors']:
        issues.append('coverage requires captured class rows')
    if coverage in ('UNAVAILABLE', 'CYCLE', 'NOT_APPLICABLE') and relation != 'UNKNOWN':
        issues.append('unverified coverage cannot establish declared relation')
    if relation == 'NO' and coverage != 'COMPLETE':
        issues.append('NO relation requires complete ancestry')
    labels = call['classes']
    if labels and set(labels) != {'DECLARED', 'ACTUAL'}:
        issues.append('missing declared/actual class labels')
    # Identity claims come from the runtime, never from these text labels.
    # Stable labels are necessary for the logged claim to be consistent, but
    # matching labels cannot establish identity or prove any parent link.
    if relation == 'EXACT' and ('DECLARED' not in labels or
            labels.get('DECLARED') != labels.get('ACTUAL')):
        issues.append('EXACT claim contradicts declared/actual class labels')
    if relation == 'DERIVED' and ('DECLARED' not in labels or not any(
            {k: row[k] for k in ('name', 'path')} == labels['DECLARED']
            for row in call['ancestors'])):
        issues.append('DERIVED claim lacks matching declared ancestor labels')
    if call['ancestors'] and ('ACTUAL' not in labels or
            {k: call['ancestors'][0][k] for k in ('name', 'path')} != labels['ACTUAL']):
        issues.append('first ancestry label differs from recorded actual class')
    if field.get('wrapper') == 'KNOWN_ABSENT':
        if (field != dict(wrapper='KNOWN_ABSENT', actual_class='UNAVAILABLE', status='VERIFIED_ABSENCE')
                or coverage != 'NOT_APPLICABLE' or count != 0 or labels):
            issues.append('known absence contains contradictory metadata')
        outcome = 'KNOWN_ABSENCE'
    else:
        complete = coverage == 'COMPLETE'
        if field.get('status') != ('VERIFIED_METADATA' if complete else 'PARTIAL_UNAVAILABLE'):
            issues.append('field status disagrees with coverage')
        if complete and (field.get('wrapper') != 'SDK_UOBJECT' or
                field.get('actual_class') != 'SDK_UCLASS' or len(labels) != 2 or relation == 'UNKNOWN'):
            issues.append('complete metadata lacks typed class/relationship records')
        if (labels or call['ancestors']) and field.get('actual_class') != 'SDK_UCLASS':
            issues.append('class rows emitted for unavailable actual class')
        if field.get('wrapper') == 'UNKNOWN' and (field.get('actual_class') != 'UNAVAILABLE' or
                coverage != 'UNAVAILABLE' or count != 0):
            issues.append('unknown wrapper contains contradictory class metadata')
        outcome = 'COMPLETE_METADATA' if complete else 'PARTIAL_METADATA'
    # Names and paths are reported/checked for consistency only. Never derive
    # EXACT/DERIVED/NO from them: SDK object identities are absent from text.
    call['outcome'] = 'INVALID_OR_INCOMPLETE' if issues else outcome


def review_bytes(raw):
    """Return a JSON-safe log report. No file writes, SDK imports, or callbacks."""
    report = dict(source=dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()),
                  calls=[], cleanup=dict(restoration_records=[], observer_records=[], error_records=[]), issues=[],
                  separate_checks=dict(process_exit='NOT_CHECKED', installed_archive_equality='NOT_CHECKED',
                                       capture_origin_authenticity='NOT_CHECKED'),
                  live_game_success='NOT_ESTABLISHED_BY_THIS_TOOL')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        report.update(status='INVALID_OR_INCOMPLETE', log_evidence_acceptable=False)
        report['issues'].append('input is not UTF-8 text')
        return report
    report['source']['lines'] = len(text.splitlines())
    report['source']['ends_with_newline'] = bool(text) and text.endswith('\n')
    if not report['source']['ends_with_newline']:
        report['issues'].append('missing final line terminator; capture may be truncated')
    call, versions = None, set()
    for line_number, line in enumerate(text.splitlines(), 1):
        event = EVENT.fullmatch(line)
        if not event:
            # Do not silently accept a clipped SDK line carrying a structural tag.
            if re.search(r'\[UVH-CLASS\] (?:BEGIN|BASELINE|REFERENCE|FIELD|CLASS|ANCESTOR|ANCESTRY|FINAL|END|ABORT)', line):
                report['issues'].append(f'line {line_number}: malformed diagnostic prefix')
            continue
        tag, payload = event.groups()
        if re.match(r'^(?:BEGIN|START) v\d', payload):
            versions.update(re.findall(r'\bv(\d+\.\d+\.\d+)\b', payload))
        if tag in CLEANUP_TAGS or tag == 'UVH-TRACE':
            pattern = (r'^Observers remaining=(\d{1,3})$' if tag == 'UVH-INITNODE' else
                       r'^STOP remaining=(\d{1,3}); events=\d{1,10}$' if tag == 'UVH-TRACE' else
                       r'^STOP remaining=(\d{1,3}) captured=\d{1,10} callbacks=\d{1,10} skipped=\d{1,10}$')
            match = re.fullmatch(pattern, payload)
            if match:
                report['cleanup']['observer_records'].append(dict(line=line_number, family=tag, remaining=int(match[1])))
            elif payload.startswith(('STOP remaining=', 'Observers remaining=', 'Hook removal ERROR',
                                     'Removal ERROR', 'Rollback failed;',
                                     'Native arrays changed independently;', 'Cannot verify rollback ownership;')):
                report['cleanup']['error_records'].append(dict(line=line_number, family=tag, reason='malformed or failed cleanup'))
            if report['calls'] and payload.startswith(('START ', 'Active observers=', 'ARMED.')):
                report['cleanup']['error_records'].append(dict(line=line_number, family=tag, reason='another experiment started after combined inspection'))
        if tag == 'UVH-NEWNODE' and payload.startswith('RESTORE result='):
            expected = re.fullmatch(r"RESTORE result=True skills=\['MorePep', 'Myelin'\] cells=\[True, False, True\] \(methods (?:assign|slice|clear\+extend), (?:assign|slice|clear\+extend)\)", payload)
            report['cleanup']['restoration_records'].append(dict(line=line_number, verified=bool(expected)))
        if tag == 'UVH-NEWNODE' and payload.startswith('Removal ERROR'):
            report['cleanup']['error_records'].append(dict(
                line=line_number, family=tag, reason='failed native node removal'))
        if tag != 'UVH-CLASS':
            continue  # SCHEMA rechecks and other diagnostic families are not snapshots.
        begin = BEGIN.fullmatch(payload)
        if begin:
            if call is not None:
                call['issues'].append('new BEGIN before prior terminal record')
            call = _new_call(line_number, begin[1])
            report['calls'].append(call)
            continue
        if payload == ADVICE:
            continue
        if call is None:
            report['issues'].append(f'line {line_number}: diagnostic record without current BEGIN')
            continue
        if re.fullmatch(r'ABORT [A-Za-z_][A-Za-z_0-9]{0,95}: metadata/current state unavailable or changed; no repair/refund\. CANCEL and exit\.', payload):
            call.update(terminal='ABORT', terminal_line=line_number)
            call = None
            continue
        if payload == 'NOT INSPECTED: initialization/other observers must be stopped.':
            call.update(terminal='NOT_INSPECTED', terminal_line=line_number)
            call = None
            continue
        try:
            kind = _record(call, payload, line_number)
            call['records'].append(kind)
            if kind == 'END':
                call.update(terminal='END', terminal_line=line_number)
                call = None
        except (ValueError, SyntaxError) as exc:
            call['issues'].append(f'line {line_number}: {exc}')
    for item in report['calls']:
        _finish(item)
    report['versions'] = sorted(versions)
    if versions != {VERSION}:
        report['issues'].append('missing/unsupported/mixed diagnostic versions')
    if not report['calls']:
        report['issues'].append('no combined v0.2.11 snapshot')
    baselines = [item['baseline'] for item in report['calls'] if item['baseline'] is not None]
    if baselines and any(state != baselines[0] for state in baselines):
        report['issues'].append('points/ranks differ between snapshots')
    last = max((item['terminal_line'] or item['begin_line'] for item in report['calls']), default=0)
    restorations = [r for r in report['cleanup']['restoration_records'] if r['line'] > last]
    observers = [r for r in report['cleanup']['observer_records'] if r['line'] > last]
    cleanup_errors = report['cleanup']['error_records']
    families = {r['family'] for r in observers}
    restored = bool(restorations) and all(r['verified'] for r in restorations)
    removed = CLEANUP_TAGS <= families and all(r['remaining'] == 0 for r in observers) and not cleanup_errors
    report['cleanup'].update(restoration_verified_after_last_call=restored,
                             required_observer_families=sorted(CLEANUP_TAGS),
                             observer_cleanup_verified_after_last_call=removed)
    if not restored:
        report['issues'].append('missing or failed native-array restoration after last call')
    if not removed:
        report['issues'].append('missing/nonzero observer cleanup after last call')
    outcomes = {item['outcome'] for item in report['calls']}
    if report['issues'] or 'INVALID_OR_INCOMPLETE' in outcomes:
        status = 'INVALID_OR_INCOMPLETE'
    elif 'ABORTED' in outcomes:
        status = 'ABORTED'
    elif 'NOT_INSPECTED' in outcomes:
        status = 'NOT_INSPECTED'
    elif 'PARTIAL_METADATA' in outcomes:
        status = 'PARTIAL'
    else:
        status = 'COMPLETE_LOG_EVIDENCE'
    report.update(status=status, log_evidence_acceptable=status == 'COMPLETE_LOG_EVIDENCE')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path, help='preserved UTF-8 log to read; output is JSON on stdout')
    args = parser.parse_args(argv)
    try:
        raw = args.log.read_bytes()
    except OSError as exc:
        print(json.dumps(dict(status='INPUT_ERROR', error=type(exc).__name__)))
        return 2
    report = review_bytes(raw)
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report['log_evidence_acceptable'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
