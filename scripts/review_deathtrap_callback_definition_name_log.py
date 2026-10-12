"""Strict bounded v17 reader text consistency; never native ownership or authenticity."""
import argparse
import hashlib
import json
from pathlib import Path
import re

MAX_BYTES = 16 * 1024 * 1024
MAX_LINES = 100000
MAX_LINE_BYTES = 16384
MAX_RECORDS = 4096
MAX_SESSIONS = 128
MAX_ISSUES = 128
INTEGER_MAX = 2147483647
TAG = '[UVH-CALLBACK-NAME] '
FRAME = re.compile(
    r'^(?:(?:[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}'
    r'\.[0-9]{3}Z [^|\r\n]{1,512}INFO\| )?\[UVH-BOOST\] )?'
    r'\[UVH-CALLBACK-NAME\] (?P<payload>[ -~]+)$')
N = r'(?:0|[1-9][0-9]{0,9})'


def integer(name):
    return '(?P<' + name + '>' + N + ')'


EPOCH = 'epoch=' + integer('epoch')
BUDGET = ('ops=' + integer('ops') + ' stages=' + integer('s0') + ','
          + integer('s1') + ',' + integer('s2') + ',' + integer('s3'))
PATTERNS = {
    'START': re.compile(r'START version=0\.2\.17 ' + EPOCH
                        + ' target=DeactivateSkill phase=PRE hooks=1 mode=STANDALONE_READER'),
    'EVENT': re.compile('EVENT ' + EPOCH + ' ordinal=' + integer('ordinal')
                        + ' attempt=' + integer('attempt') + ' schema=VALID '
                        + 'controller=(?P<controller>NULL_INSTIGATOR|OTHER_CONTROLLER_CLASS|OTHER_WRAPPER|SAME_WRAPPER) '
                        + 'definition=(?P<definition>NOT_READ|NULL_DEFINITION|OTHER_NAME|DEATHTRAP_NAME) '
                        + 'name=(?P<name>-|[A-Za-z0-9_]{1,128}) ownership=UNESTABLISHED ' + BUDGET),
    'REFUSED': re.compile('REFUSED ' + EPOCH
                          + ' reason=(?P<reason>SCHEMA|PLAYER|PARAMETER|CLOCK|TIME|BUDGET|STOPPED|INTERNAL) '
                          + BUDGET),
    'ERROR': re.compile('ERROR ' + EPOCH + ' reason=(?P<reason>INTERNAL|LOGGING) ' + BUDGET),
    'INTERNAL_ERROR': re.compile('ERROR ' + EPOCH + ' reason=INTERNAL'),
    'CLOCK_ERROR': re.compile('ERROR reason=CLOCK'),
    'LIMIT': re.compile('LIMIT reason=(?P<reason>TIME|ATTEMPTS|EVENTS)'),
    'NOT_STARTED': re.compile('NOT_STARTED reason=(?P<reason>OVERLAP|EPOCH|CLOCK|IDENTIFIER|REGISTRATION)'),
    'REMOVAL_ERROR': re.compile('REMOVAL_ERROR remaining=1'),
    'STOP': re.compile('STOP ' + EPOCH + ' remaining=' + integer('remaining')
                       + ' uncertain=' + integer('uncertain') + ' attempts=' + integer('attempts')
                       + ' classified=' + integer('classified') + ' filtered=' + integer('filtered')
                       + ' nulls=' + integer('nulls') + ' refusals=' + integer('refusals')
                       + ' errors=' + integer('errors') + ' reentry=' + integer('reentry')
                       + ' cleanup_failures=' + integer('cleanup_failures')
                       + ' limit=(?P<limit>NONE|TIME|ATTEMPTS|EVENTS)'),
    'OUTCOME': re.compile('OUTCOME ' + EPOCH
                          + ' value=(?P<value>NOT_OBSERVED|OBSERVED_PRIMITIVE|OBSERVED_FILTERED|REFUSED) '
                          + 'ownership=UNESTABLISHED'),
}
# Counts are fixed reader-issued operations in the accepted v17 source. They
# exclude SDK helper/conversion internals, and do not establish native safety.
EVENT_STAGES = {
    ('NULL_INSTIGATOR', 'NOT_READ'): (58, 49, 0, 0),
    ('OTHER_CONTROLLER_CLASS', 'NOT_READ'): (58, 50, 0, 0),
    ('OTHER_WRAPPER', 'NOT_READ'): (58, 50, 1, 0),
    ('SAME_WRAPPER', 'NULL_DEFINITION'): (58, 50, 36, 50),
    ('SAME_WRAPPER', 'OTHER_NAME'): (58, 50, 36, 52),
    ('SAME_WRAPPER', 'DEATHTRAP_NAME'): (58, 50, 36, 52),
}
NUMERIC = {'epoch', 'ordinal', 'attempt', 'ops', 's0', 's1', 's2', 's3',
           'remaining', 'uncertain', 'attempts', 'classified', 'filtered', 'nulls',
           'refusals', 'errors', 'reentry', 'cleanup_failures'}
COUNTERS = ('attempts', 'classified', 'filtered', 'nulls', 'refusals', 'errors',
            'reentry', 'cleanup_failures')


def input_error(code):
    return dict(schema_version=1, reader_version='0.2.17', status='INPUT_ERROR', input_error=code,
                log_text_acceptable=False, authenticity='NOT_ESTABLISHED',
                native_ownership='NOT_ESTABLISHED', engine_behavior='NOT_ESTABLISHED',
                native_owned_lifecycle_ready=False, native_effect_ready=False)


def decode_record(payload):
    for kind, pattern in PATTERNS.items():
        match = pattern.fullmatch(payload)
        if match is not None:
            values = match.groupdict()
            for name in NUMERIC & values.keys():
                values[name] = int(values[name])
                if values[name] > INTEGER_MAX:
                    raise ValueError('INTEGER_BOUND')
            return kind, values
    return None, {}


def review_bytes(raw):
    if type(raw) is not bytes:
        return input_error('INPUT_TYPE')
    if len(raw) > MAX_BYTES or raw.count(b'\n') > MAX_LINES:
        return input_error('INPUT_BOUND')
    try:
        text = raw.decode('utf-8', errors='strict')
    except UnicodeError:
        return input_error('UTF8')
    lines = text.split('\n')
    if len(lines) - int(lines[-1] == '') > MAX_LINES:
        return input_error('LINE_COUNT_BOUND')
    if any(len(line.encode('utf-8')) > MAX_LINE_BYTES for line in lines):
        return input_error('LINE_BOUND')
    if '\x00' in text:
        return input_error('NUL')
    issues, sessions = [], []
    current = None
    records = issue_count = overlap_refusals = 0
    seen_epochs = set()
    last_epoch = 0

    def issue(line, code):
        nonlocal issue_count
        issue_count += 1
        if len(issues) < MAX_ISSUES:
            issues.append(dict(line=line, code=code))

    def session(line, epoch=None, started=False, failed_start=None, orphan=False):
        if len(sessions) >= MAX_SESSIONS:
            raise ValueError('SESSION_BOUND')
        run = dict(line=line, epoch=epoch, started=started, failed_start=failed_start,
                   orphan=orphan, attempts=0, classified=0, filtered=0, nulls=0,
                   useful=0, refusals=int(failed_start is not None), errors=0,
                   cleanup_failures=0, overlap_refusals=0, limit='NONE', terminal=False,
                   removal_pending=False, awaiting_stop=True, stops=[], classifications={}, events=[])
        sessions.append(run)
        return run

    def bind_epoch(run, epoch, line):
        nonlocal last_epoch
        if epoch < 1:
            issue(line, 'EPOCH_BOUND')
        if run['epoch'] is None:
            if epoch in seen_epochs or epoch <= last_epoch:
                issue(line, 'EPOCH_REPLAY')
            elif epoch != last_epoch + 1:
                issue(line, 'EPOCH_GAP')
            seen_epochs.add(epoch)
            last_epoch = max(last_epoch, epoch)
            run['epoch'] = epoch
        elif epoch != run['epoch']:
            issue(line, 'EPOCH_MISMATCH')

    def paired(run):
        return bool(run['stops']) and run['stops'][-1]['outcome'] is not None

    try:
        for lineno, original in enumerate(lines, 1):
            line = original[:-1] if original.endswith('\r') else original
            if '[UVH-CALL' not in line:
                continue
            records += 1
            if records > MAX_RECORDS:
                raise ValueError('RECORD_BOUND')
            frame = FRAME.fullmatch(line)
            if frame is None or line.count('[UVH-CALLBACK') != 1:
                issue(lineno, 'FRAME')
                continue
            payload = frame['payload']
            if len(('[UVH-BOOST] ' + TAG + payload).encode('utf-8')) > 384:
                issue(lineno, 'PROJECT_LINE_BOUND')
                continue
            kind, values = decode_record(payload)
            if kind is None:
                issue(lineno, 'GRAMMAR')
                continue
            record_issue_count = issue_count
            if (current is not None and current['stops']
                    and current['stops'][-1]['outcome'] is None and kind != 'OUTCOME'):
                issue(lineno, 'MISSING_OUTCOME')
            if kind == 'START':
                if current is not None and (not paired(current)
                        or current['awaiting_stop'] or current['stops'][-1]['remaining']):
                    issue(lineno, 'UNCLOSED_BEFORE_START')
                current = session(lineno, started=True)
                bind_epoch(current, values['epoch'], lineno)
                continue
            if kind == 'NOT_STARTED':
                if values['reason'] == 'OVERLAP':
                    overlap_refusals += 1
                    if current is not None:
                        current['overlap_refusals'] += 1
                else:
                    if current is not None and (not paired(current)
                            or current['awaiting_stop'] or current['stops'][-1]['remaining']):
                        issue(lineno, 'NOT_STARTED_ORDER')
                    current = session(lineno, failed_start=values['reason'])
                    current['terminal'] = True
                continue
            if current is None:
                current = session(lineno, orphan=True)
            run = current
            if 'epoch' in values:
                bind_epoch(run, values['epoch'], lineno)
            if kind in ('EVENT', 'REFUSED', 'ERROR', 'INTERNAL_ERROR',
                        'CLOCK_ERROR', 'LIMIT', 'REMOVAL_ERROR'):
                run['awaiting_stop'] = True
            if 'ops' in values:
                stages = tuple(values['s' + str(i)] for i in range(4))
                if any(n > 64 for n in stages) or values['ops'] != sum(stages) or values['ops'] > 256:
                    issue(lineno, 'BUDGET')
                if kind == 'REFUSED' and values['reason'] == 'BUDGET' and max(stages) < 64:
                    issue(lineno, 'BUDGET_REFUSAL_WITHOUT_EXHAUSTION')
                if kind == 'ERROR' and values['reason'] == 'LOGGING' and stages not in EVENT_STAGES.values():
                    issue(lineno, 'LOGGING_ERROR_BUDGET')
            if kind in ('EVENT', 'REFUSED', 'ERROR', 'INTERNAL_ERROR'):
                if not run['started'] or run['terminal'] or run['stops']:
                    issue(lineno, 'ATTEMPT_ORDER')
                run['attempts'] += 1
                if run['attempts'] > 64 or run['classified'] >= 24:
                    issue(lineno, 'ATTEMPT_BOUND')
                if kind == 'EVENT':
                    pair = (values['controller'], values['definition'])
                    expected = EVENT_STAGES.get(pair)
                    if expected is None:
                        issue(lineno, 'CLASSIFICATION_BRANCH')
                    elif stages != expected:
                        issue(lineno, 'CLASSIFICATION_BUDGET')
                    name = values['name']
                    absent = pair in (('NULL_INSTIGATOR', 'NOT_READ'),
                                      ('OTHER_CONTROLLER_CLASS', 'NOT_READ'),
                                      ('OTHER_WRAPPER', 'NOT_READ'),
                                      ('SAME_WRAPPER', 'NULL_DEFINITION'))
                    valid_name = (name == '-' if absent else
                                  name == 'Skill_DeathTrap' if pair == ('SAME_WRAPPER', 'DEATHTRAP_NAME') else
                                  name not in ('-', 'Skill_DeathTrap') if pair == ('SAME_WRAPPER', 'OTHER_NAME') else False)
                    if not valid_name:
                        issue(lineno, 'NAME_CLASSIFICATION')
                    if values['ordinal'] != run['classified'] + 1 or values['attempt'] != run['attempts']:
                        issue(lineno, 'EVENT_SEQUENCE')
                    # Export only a locally valid EVENT; never retain malformed tokens.
                    # The 24-event/session and global record/session bounds cap JSON too.
                    if issue_count == record_issue_count and len(run['events']) < 24:
                        run['events'].append(dict(line=lineno, epoch=values['epoch'],
                            ordinal=values['ordinal'], attempt=values['attempt'],
                            controller=values['controller'], definition=values['definition'],
                            name=None if name == '-' else name))
                    run['classified'] += 1
                    if pair in (('OTHER_CONTROLLER_CLASS', 'NOT_READ'), ('OTHER_WRAPPER', 'NOT_READ'),
                                ('SAME_WRAPPER', 'OTHER_NAME')):
                        run['filtered'] += 1
                    elif pair in (('NULL_INSTIGATOR', 'NOT_READ'), ('SAME_WRAPPER', 'NULL_DEFINITION')):
                        run['nulls'] += 1
                    elif pair == ('SAME_WRAPPER', 'DEATHTRAP_NAME'):
                        run['useful'] += 1
                    label = values['controller'] + '/' + values['definition']
                    run['classifications'][label] = run['classifications'].get(label, 0) + 1
                else:
                    key = 'refusals' if kind == 'REFUSED' else 'errors'
                    run[key] += 1
                    run['terminal'] = True
                    if values.get('reason') == 'TIME':
                        run['limit'] = 'TIME'
            elif kind == 'CLOCK_ERROR':
                run['errors'] += 1
                run['terminal'] = True
            elif kind == 'LIMIT':
                if run['limit'] != 'NONE' or run['removal_pending']:
                    issue(lineno, 'LIMIT_ORDER')
                reason = values['reason']
                if (reason == 'EVENTS' and run['classified'] != 24
                        or reason == 'ATTEMPTS' and run['attempts'] != 64):
                    issue(lineno, 'LIMIT_COUNT')
                run['limit'] = reason
                run['terminal'] = True
            elif kind == 'REMOVAL_ERROR':
                if run['removal_pending']:
                    issue(lineno, 'REMOVAL_ORDER')
                run['cleanup_failures'] += 1
                run['removal_pending'] = True
                run['terminal'] = True
            elif kind == 'STOP':
                if values['remaining'] > 1 or values['uncertain'] > values['remaining']:
                    issue(lineno, 'STOP_HANDLE_BOUND')
                if run['started'] and values['uncertain']:
                    issue(lineno, 'STARTED_UNCERTAINTY')
                if run['started'] and values['remaining'] and not run['removal_pending']:
                    issue(lineno, 'MISSING_REMOVAL_ERROR')
                if run['removal_pending'] and values['remaining'] != 1:
                    issue(lineno, 'REMOVAL_REMAINING')
                run['removal_pending'] = False
                if (values['attempts'] > 64 or values['classified'] > 24
                        or values['filtered'] + values['nulls'] > values['classified']):
                    issue(lineno, 'STOP_COUNT_BOUND')
                if not values['attempts'] and values['reentry']:
                    issue(lineno, 'REENTRY_WITHOUT_ATTEMPT')
                for name in COUNTERS:
                    if name != 'reentry' and values[name] != run[name]:
                        issue(lineno, 'COUNT_' + name.upper())
                if values['limit'] != run['limit']:
                    issue(lineno, 'LIMIT_MISMATCH')
                if values['classified'] == 24 and values['limit'] != 'EVENTS':
                    issue(lineno, 'MISSING_EVENT_LIMIT')
                if values['attempts'] == 64 and values['limit'] != 'ATTEMPTS':
                    issue(lineno, 'MISSING_ATTEMPT_LIMIT')
                if run['stops']:
                    previous = run['stops'][-1]
                    stable = ('attempts', 'classified', 'filtered', 'nulls', 'refusals', 'reentry')
                    if (any(values[k] != previous[k] for k in stable)
                            or values['remaining'] > previous['remaining']
                            or values['uncertain'] > previous['uncertain']):
                        issue(lineno, 'RETRY_COUNTS')
                run['terminal'] = True
                run['stops'].append(dict(line=lineno, **values, outcome=None))
                run['awaiting_stop'] = False
            elif kind == 'OUTCOME':
                if not run['stops'] or run['stops'][-1]['outcome'] is not None:
                    issue(lineno, 'OUTCOME_ORDER')
                else:
                    stop = run['stops'][-1]
                    expected = ('REFUSED' if stop['remaining'] or stop['refusals'] or stop['errors']
                                or stop['cleanup_failures'] else 'NOT_OBSERVED' if not stop['attempts']
                                else 'OBSERVED_PRIMITIVE' if stop['classified'] > stop['filtered'] + stop['nulls']
                                else 'OBSERVED_FILTERED')
                    if values['value'] != expected:
                        issue(lineno, 'OUTCOME_CONTRADICTION')
                    stop['outcome'] = values['value']
        if records and not raw.endswith(b'\n'):
            issue(len(lines), 'UNTERMINATED_INPUT')
    except ValueError as exc:
        code = exc.args[0]
        return input_error(code if code in ('INTEGER_BOUND', 'SESSION_BOUND', 'RECORD_BOUND') else 'BOUND')
    complete = bool(sessions) and all(
        not r['orphan'] and (r['started'] or r['failed_start'] is not None)
        and r['epoch'] is not None and bool(r['stops']) and not r['awaiting_stop']
        and all(s['outcome'] is not None for s in r['stops'])
        for r in sessions)
    resolved = bool(sessions) and all(r['stops'] and r['stops'][-1]['remaining'] == 0
                                     and r['stops'][-1]['uncertain'] == 0 for r in sessions)
    refused = any(r['failed_start'] or r['refusals'] or r['errors'] or r['cleanup_failures']
                  or r['stops'] and any(s['remaining'] or s['uncertain'] for s in r['stops'])
                  for r in sessions)
    if issue_count:
        status = 'INVALID_LOG_TEXT'
    elif not sessions:
        status = 'PARTIAL_LOG_TEXT' if overlap_refusals else 'NO_READER_TEXT'
    elif not complete:
        status = 'PARTIAL_LOG_TEXT'
    elif refused or not resolved:
        status = 'REFUSED_LOG_TEXT'
    else:
        status = 'COMPLETE_LOG_TEXT'
    return dict(schema_version=1, reader_version='0.2.17', status=status, log_text_acceptable=status == 'COMPLETE_LOG_TEXT',
                log_text_consistent=issue_count == 0, reader_sections_complete=complete,
                input=dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()),
                records=records, sessions=sessions, overlap_refusals=overlap_refusals,
                issues=issues, issue_count=issue_count, issues_truncated=issue_count > MAX_ISSUES,
                cleanup=dict(reader_handles_resolved=resolved, prior_refusal_preserved=bool(refused),
                             other_observers='NOT_ESTABLISHED', arrays_or_manual_duration='NOT_ESTABLISHED',
                             process_exit='NOT_ESTABLISHED'),
                event_meaning='PRE attempted entry; validated primitive definition name only; no association or lifespan',
                schema_evidence='ASSERTED_IN_LOG_TEXT', native_ownership='NOT_ESTABLISHED',
                summon_generation='NOT_ESTABLISHED', native_clock='NOT_ESTABLISHED',
                installation='NOT_ESTABLISHED', owner_protocol='NOT_ESTABLISHED',
                authenticity='NOT_ESTABLISHED', engine_behavior='NOT_ESTABLISHED',
                native_owned_lifecycle_ready=False, native_effect_ready=False,
                silence='NOT_OBSERVED never proves absence, deactivation, ownership or lifespan')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    args = parser.parse_args(argv)
    try:
        with args.log.open('rb') as stream:
            report = review_bytes(stream.read(MAX_BYTES + 1))
    except OSError:
        report = input_error('FILE_READ')
    print(json.dumps(report, indent=2))
    return 2 if report['status'] == 'INPUT_ERROR' else 0 if report['log_text_acceptable'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
