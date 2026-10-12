"""Bounded v15 passive-event text consistency, never authenticity or engine proof."""
import argparse
import hashlib
import json
from pathlib import Path
import re

MAX_BYTES = 16 * 1024 * 1024
MAX_LINES = 100000
MAX_LINE_BYTES = 16384
MAX_RECORDS = 4096
MAX_RUNS = 128
MAX_ISSUES = 128
INTEGER_MAX = 2147483647
TAG = '[UVH-DT-EVENT] '
FRAME = re.compile(r'^(?:(?:[0-9]{4}-[0-9]{2}-[0-9]{2} [^|\r\n]{1,512}INFO\| )?\[UVH-BOOST\] )?\[(UVH-[A-Z-]+)\] (.*)$')
N = r'(?:0|[1-9][0-9]{0,9})'
TWO = r'\((' + N + r'), (' + N + r')\)'
THREE = r'\((' + N + r'), (' + N + r'), (' + N + r')\)'
START = 'START v0.2.15 target=DeactivateSkill phase=PRE attribution=NONE hooks=1'
BASELINE = re.compile('BASELINE points=' + TWO + ' ranks=' + THREE)
EVENT = re.compile('EVENT ordinal=(' + N + ') target=DeactivateSkill phase=PRE attribution=NONE')
LIMIT = re.compile(r'LIMIT reason=(EVENTS|ATTEMPTS|TIME)')
ABORT = re.compile(r'ABORT reason=(STATE|METADATA|CLOCK|REGISTRATION|INTERNAL)')
NOT_STARTED = re.compile(r'NOT_STARTED reason=(OVERLAP|STATE|METADATA|IDENTIFIER|REGISTRATION|CLOCK)')
FINAL = re.compile('FINAL points=' + TWO + ' ranks=' + THREE + ' unchanged=True')
STOP = re.compile('STOP remaining=(' + N + ') captured=(' + N + ') attempts=(' + N +
                  ') reentrant=(' + N + ') uncertain=(' + N + ') cleanup_failures=(' + N + ')')
OUTCOME = re.compile(r'OUTCOME value=(OBSERVED_UNATTRIBUTED|NOT_OBSERVED|REFUSED)')
OLD_STOP = re.compile('STOP remaining=(' + N + ') captured=(' + N + ') callbacks=(' + N + ') skipped=(' + N + ')')
OLD_INIT = re.compile('Observers remaining=(' + N + ')')
RESTORE = re.compile(r"RESTORE result=True skills=\['MorePep', 'Myelin'\] cells=\[True, False, True\] \(methods (?:assign|slice|clear\+extend), (?:assign|slice|clear\+extend)\)")
FAMILIES = ('UVH-STATE', 'UVH-UI', 'UVH-UPGRADE', 'UVH-INITNODE')


def input_error(code):
    return dict(schema_version=1, status='INPUT_ERROR', input_error=code,
                log_text_acceptable=False, engine_behavior='NOT_ESTABLISHED')


def numbers(match):
    values = tuple(int(x) for x in match.groups())
    if any(x > INTEGER_MAX for x in values):
        raise ValueError('INTEGER_BOUND')
    return values


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
    issues, runs, old = [], [], {k: [] for k in FAMILIES}
    restore, record_count, cutoff = None, 0, 0
    unattached_control_refusals = 0
    current = None
    issue_total = 0

    def issue(line, code):
        nonlocal issue_total
        issue_total += 1
        if len(issues) < MAX_ISSUES:
            issues.append(dict(line=line, code=code))

    def new_run(line, started=False, orphan=False):
        if len(runs) >= MAX_RUNS:
            raise ValueError('RUN_BOUND')
        run = dict(line=line, started=started, orphan=orphan, baseline=None,
                   events=0, limit=None, abort=None, not_started=None, final=None,
                   stops=[], overlap_refusals=0, removal_errors=0, refused=False,
                   ended=False)
        runs.append(run)
        return run

    try:
        for lineno, original in enumerate(lines, 1):
            line = original[:-1] if original.endswith('\r') else original
            match = FRAME.fullmatch(line)
            if match is None:
                if '[UVH-DT-EVENT]' in line:
                    issue(lineno, 'FRAME')
                continue
            tag, payload = match.groups()
            if tag != 'UVH-DT-EVENT' and '[UVH-DT-EVENT]' in payload:
                issue(lineno, 'FRAME')
            if tag in FAMILIES:
                stop = (OLD_INIT if tag == 'UVH-INITNODE' else OLD_STOP).fullmatch(payload)
                if stop:
                    vals = numbers(stop)
                    old[tag].append((lineno, vals[0]))
                    record_count += 1
                elif payload.startswith('STOP ') or payload.startswith('Observers remaining='):
                    issue(lineno, 'OLD_CLEANUP_GRAMMAR')
            elif tag == 'UVH-NEWNODE' and payload.startswith('RESTORE '):
                restore = (lineno, RESTORE.fullmatch(payload) is not None)
                record_count += 1
            elif tag == 'UVH-DT-EVENT':
                record_count += 1
                if record_count > MAX_RECORDS:
                    raise ValueError('RECORD_BOUND')
                if len((TAG + payload).encode('utf-8')) > 256 or '\r' in payload:
                    issue(lineno, 'EVENT_LINE_BOUND')
                    continue
                start = payload == START
                baseline = BASELINE.fullmatch(payload)
                event = EVENT.fullmatch(payload)
                limit = LIMIT.fullmatch(payload)
                abort = ABORT.fullmatch(payload)
                refused = NOT_STARTED.fullmatch(payload)
                final = FINAL.fullmatch(payload)
                unverified = payload == 'FINAL UNVERIFIED reason=STATE'
                removal = payload == 'REMOVAL_ERROR remaining=1'
                stop = STOP.fullmatch(payload)
                outcome = OUTCOME.fullmatch(payload)
                if not any((start, baseline, event, limit, abort, refused, final, unverified, removal, stop, outcome)):
                    issue(lineno, 'GRAMMAR')
                    continue
                if start:
                    if current is not None and (not current['stops'] or current['stops'][-1]['outcome'] is None):
                        issue(lineno, 'UNCLOSED_BEFORE_START')
                    if current is not None and current['stops'] and current['stops'][-1]['remaining']:
                        issue(lineno, 'START_WHILE_PENDING')
                    current = new_run(lineno, started=True)
                    cutoff = lineno
                    continue
                if refused and refused[1] != 'OVERLAP':
                    if current is None or current['ended']:
                        current = new_run(lineno)
                    if current['events'] or current['not_started'] is not None:
                        issue(lineno, 'NOT_STARTED_ORDER')
                    current['not_started'] = refused[1]
                    current['refused'] = current['ended'] = True
                    cutoff = lineno
                    continue
                if refused:
                    if current is None:
                        unattached_control_refusals += 1
                    else:
                        current['overlap_refusals'] += 1
                    continue
                if current is None:
                    current = new_run(lineno, orphan=True)
                if baseline:
                    values = numbers(baseline)
                    if current['baseline'] is not None or current['events'] or current['ended']:
                        issue(lineno, 'BASELINE_ORDER')
                    if values[2] != 0:
                        issue(lineno, 'CANDIDATE_RANK')
                    current['baseline'] = dict(points=list(values[:2]), ranks=list(values[2:]))
                    cutoff = lineno
                elif event:
                    ordinal = numbers(event)[0]
                    if current['baseline'] is None or current['ended'] or current['final'] is not None:
                        issue(lineno, 'EVENT_ORDER')
                    if ordinal != current['events'] + 1 or not 1 <= ordinal <= 24:
                        issue(lineno, 'EVENT_ORDINAL')
                    current['events'] += 1
                    cutoff = lineno
                elif limit or abort:
                    if current['limit'] is not None or current['abort'] is not None or current['stops'] or current['baseline'] is None:
                        issue(lineno, 'TERMINAL_ORDER')
                    current['ended'] = True
                    if limit:
                        current['limit'] = limit[1]
                    else:
                        current['abort'] = abort[1]
                        current['refused'] = True
                elif final or unverified:
                    if current['final'] is not None or current['stops']:
                        issue(lineno, 'FINAL_ORDER')
                    if final:
                        values = numbers(final)
                        state = dict(points=list(values[:2]), ranks=list(values[2:]))
                        if current['baseline'] != state:
                            issue(lineno, 'FINAL_STATE_MISMATCH')
                        current['final'] = 'VERIFIED'
                    else:
                        current['final'] = 'UNVERIFIED'
                        current['refused'] = True
                    current['ended'] = True
                elif removal:
                    current['removal_errors'] += 1
                    current['refused'] = True
                    current['ended'] = True
                elif stop:
                    remaining, captured, attempts, reentrant, uncertain, failures = numbers(stop)
                    if remaining > 1 or uncertain > remaining or captured > 24 or attempts > 64 or captured + reentrant > attempts or (attempts > 0 and reentrant >= attempts):
                        issue(lineno, 'STOP_BOUND_OR_COUNTS')
                    if captured != current['events']:
                        issue(lineno, 'CAPTURE_COUNT')
                    if not current['orphan'] and failures != current['removal_errors']:
                        issue(lineno, 'FAILURE_HISTORY')
                    if current['limit'] == 'EVENTS' and captured != 24:
                        issue(lineno, 'EVENT_LIMIT_COUNT')
                    if current['limit'] == 'ATTEMPTS' and attempts != 64:
                        issue(lineno, 'ATTEMPT_LIMIT_COUNT')
                    if attempts == 64 and current['limit'] != 'ATTEMPTS':
                        issue(lineno, 'MISSING_ATTEMPT_LIMIT')
                    if captured == 24 and current['limit'] != 'EVENTS':
                        issue(lineno, 'MISSING_EVENT_LIMIT')
                    if current['stops']:
                        prev = current['stops'][-1]
                        if prev['outcome'] is None:
                            issue(lineno, 'MISSING_OUTCOME_BEFORE_STOP')
                        if (captured, attempts, reentrant) != (prev['captured'], prev['attempts'], prev['reentrant']) or failures < prev['cleanup_failures'] or remaining > prev['remaining']:
                            issue(lineno, 'RETRY_COUNTS')
                    current['refused'] |= bool(remaining or uncertain or failures)
                    current['ended'] = True
                    current['stops'].append(dict(line=lineno, remaining=remaining, captured=captured,
                        attempts=attempts, reentrant=reentrant, uncertain=uncertain,
                        cleanup_failures=failures, outcome=None))
                elif outcome:
                    if not current['stops'] or current['stops'][-1]['outcome'] is not None:
                        issue(lineno, 'OUTCOME_ORDER')
                    else:
                        expected = ('REFUSED' if current['refused'] else
                                    'OBSERVED_UNATTRIBUTED' if current['events'] else 'NOT_OBSERVED')
                        if outcome[1] != expected:
                            issue(lineno, 'OUTCOME_CONTRADICTION')
                        current['stops'][-1]['outcome'] = outcome[1]
            if record_count > MAX_RECORDS:
                raise ValueError('RECORD_BOUND')
    except ValueError as exc:
        # Only literal internally generated bound codes; no arbitrary input text.
        code = exc.args[0]
        return input_error(code if code in ('INTEGER_BOUND', 'RUN_BOUND', 'RECORD_BOUND') else 'BOUND')
    complete = bool(runs) and all(
        not r['orphan'] and bool(r['stops']) and all(s['outcome'] is not None for s in r['stops'])
        and (r['not_started'] is not None or (r['started'] and r['baseline'] is not None and r['final'] is not None))
        for r in runs)
    resolved = bool(runs) and all(r['stops'] and r['stops'][-1]['remaining'] == 0 for r in runs)
    history_refused = any(r['refused'] for r in runs)
    old_zero = {k: bool(v) and v[-1][0] > cutoff and v[-1][1] == 0 for k, v in old.items()}
    restored = restore is not None and restore[0] > cutoff and restore[1]
    cleanup = dict(observer_handles_resolved=bool(resolved), prior_refusal_preserved=history_refused,
                   old_families_zero_after_last_activity=old_zero,
                   native_arrays_restored_after_last_activity=bool(restored),
                   process_exit='NOT_ESTABLISHED', duration_restore='NOT_ESTABLISHED')
    if issue_total:
        status = 'INVALID_LOG_TEXT'
    elif not runs:
        status = 'PARTIAL_LOG_TEXT' if unattached_control_refusals else 'NO_OBSERVER_TEXT'
    elif not complete:
        status = 'PARTIAL_LOG_TEXT'
    elif history_refused or not resolved:
        status = 'REFUSED_LOG_TEXT'
    elif not all(old_zero.values()) or not restored:
        status = 'PARTIAL_LOG_TEXT'
    else:
        status = 'COMPLETE_LOG_TEXT'
    return dict(schema_version=1, status=status, log_text_acceptable=status == 'COMPLETE_LOG_TEXT',
                log_text_consistent=issue_total == 0, observer_sections_complete=bool(complete),
                input=dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()),
                records=record_count, runs=runs, unattached_control_refusals=unattached_control_refusals,
                issues=issues, issue_count=issue_total,
                issues_truncated=issue_total > MAX_ISSUES, cleanup=cleanup,
                event_meaning='UNATTRIBUTED_MANAGER_EVENT; attempted entry only',
                attribution='NONE', authenticity='NOT_ESTABLISHED', engine_behavior='NOT_ESTABLISHED',
                native_owned_lifecycle_ready=False, native_effect_ready=False,
                missing_calls_or_silence='No absence, deactivation, ownership, timing or lifespan inference')


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
