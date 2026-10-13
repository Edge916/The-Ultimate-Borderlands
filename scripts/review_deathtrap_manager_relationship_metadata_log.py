"""Bounded v19 catalog log consistency, never native safety or ownership proof."""
import argparse
import hashlib
import json
from pathlib import Path
import re

MAX_BYTES = 16 * 1024 * 1024
MAX_LINES = 100000
MAX_LINE_BYTES = 16384
MAX_RECORDS = 4096
MAX_SESSIONS = MAX_ISSUES = 128
PREFIX = '[UVH-REL-META] '
PROJECT_PREFIX = '[UVH-BOOST] '
MARKERS = ('[UVH-REL', '[UVH-ACT', '[UVH-CALL', 'UVH_RELATION_METADATA_')
FRAME = re.compile(
    r'^(?:(?:[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}'
    r'\.[0-9]{3}Z [^|\r\n]{1,512}INFO\| )?\[UVH-BOOST\] )?'
    r'\[UVH-REL-META\] (?P<payload>[ -~]+)$')
CAPS = (112, 96, 14000, 14000)
ROOTS = ('MGR', 'CTRL')
DECLS = ('MGR', 'CTRL', 'GEARBOX_PC', 'GAME_PC', 'ENGINE_PC', 'CONTROLLER', 'ACTOR', 'OBJECT')
REASONS = ('SCHEMA', 'TYPE', 'OWNER', 'LINK', 'CYCLE', 'DUPLICATE', 'RANGE', 'ABI',
           'BUDGET', 'CLOCK', 'TIME', 'STOPPED', 'REENTRY', 'INTERNAL', 'LOGGING')
OUTCOMES = ('NOT_OBSERVED', 'COMPLETE_SCOPED_METADATA', 'PARTIAL_METADATA', 'REFUSED')
KEYS = {k: frozenset(v.split()) for k, v in {
    'START': 'event epoch version target phase hooks mode',
    'BEGIN': 'event epoch attempt',
    'ROW': 'event epoch root ordinal name owner kind flags offset dim size decl',
    'ROOT': 'event epoch root coverage reason visited objects other unsupported rows rechecked ops',
    'END': 'event epoch outcome attempts gate_ops root_ops mgr_ops ctrl_ops total_ops rows errors refusals reentry reentry_saturated',
    'STOP': 'event epoch remaining uncertain attempts cleanup_failures removal_attempts deferred errors refusals reentry reentry_saturated ignored ignored_saturated outcome',
    'FAULT': 'event epoch kind scope reason',
    'NOT_STARTED': 'event epoch reason remaining uncertain',
}.items()}
BOOLEANS = frozenset(('deferred', 'reentry_saturated', 'ignored_saturated'))
NUMBERS = frozenset(('epoch', 'hooks', 'attempt', 'ordinal', 'owner', 'flags', 'offset', 'dim', 'size',
    'visited', 'objects', 'other', 'unsupported', 'rows', 'rechecked', 'ops', 'attempts',
    'gate_ops', 'root_ops', 'mgr_ops', 'ctrl_ops', 'total_ops', 'errors', 'refusals',
    'reentry', 'remaining', 'uncertain', 'cleanup_failures', 'removal_attempts', 'ignored'))


def baseline():
    return dict(schema_version=1, reader_version='0.2.19', scope='scoped catalog text consistency',
        authenticity='NOT_ESTABLISHED', installation='NOT_ESTABLISHED', owner_protocol='NOT_ESTABLISHED',
        native_ownership='NOT_ESTABLISHED', engine_behavior='NOT_ESTABLISHED',
        native_generation='NOT_ESTABLISHED', native_liveness='NOT_ESTABLISHED',
        native_clock_duration='NOT_ESTABLISHED', purchased_rank_one='NOT_ESTABLISHED',
        native_owned_lifecycle_ready=False, native_effect_ready=False)


def input_error(code):
    return dict(baseline(), status='INPUT_ERROR', input_error=code, log_text_acceptable=False)


def require(ok, code):
    if not ok:
        raise ValueError(code)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def decode_record(payload):
    # Canonical serialization rejects whitespace, floats, exponents, escapes of
    # ordinary ASCII and negative zero. No parsed invalid value enters reports.
    r = json.loads(payload, object_pairs_hook=unique_pairs,
                   parse_constant=lambda _: (_ for _ in ()).throw(ValueError('JSON_CONSTANT')))
    require(type(r) is dict and type(r.get('event')) is str and r['event'] in KEYS, 'EVENT')
    require(r.keys() == KEYS[r['event']], 'KEYS')
    for key, value in r.items():
        expected = bool if key in BOOLEANS else int if key in NUMBERS else str
        require(type(value) is expected, 'VALUE_TYPE')
    require(json.dumps(r, sort_keys=True, separators=(',', ':'), ensure_ascii=True) == payload, 'CANONICAL_JSON')
    require(len((PROJECT_PREFIX + PREFIX + payload).encode('ascii')) <= 512, 'MESSAGE_BOUND')
    for key in NUMBERS & r.keys():
        high = 18446744073709551615 if key == 'flags' else 2147483647
        require(0 <= r[key] <= high, 'INTEGER_BOUND')
    event = r['event']
    require(r['epoch'] > 0 or event in ('NOT_STARTED', 'FAULT', 'STOP'), 'EPOCH')
    if event == 'START':
        require((r['version'], r['target'], r['phase'], r['hooks'], r['mode']) ==
                ('0.2.19', 'ActivateSkill', 'PRE', 1, 'STANDALONE_METADATA'), 'START_SCHEMA')
    elif event == 'BEGIN':
        require(r['attempt'] == 1, 'ATTEMPT')
    elif event == 'ROW':
        require(r['root'] in ROOTS and r['decl'] in DECLS, 'TOKEN')
        require(1 <= r['ordinal'] <= 64 and r['owner'] <= (2 if r['root'] == 'MGR' else 6), 'ROW_INDEX')
        require(re.fullmatch(r'[A-Za-z0-9_]{1,128}', r['name']) is not None, 'NAME')
        require(r['offset'] <= 1048576 and 1 <= r['dim'] <= 1024 and r['size'] == 4
                and r['offset'] + r['dim'] * r['size'] <= 1048576, 'ROW_LAYOUT')
        require(r['kind'] == ('SCALAR' if r['dim'] == 1 else 'NON_SCALAR'), 'ROW_KIND')
    elif event == 'ROOT':
        require(r['root'] in ROOTS and r['coverage'] in ('COMPLETE_LINK', 'PARTIAL', 'REFUSED'), 'ROOT_TOKEN')
        v, o, other, unsupported, rows, checked = (r[k] for k in ('visited', 'objects', 'other', 'unsupported', 'rows', 'rechecked'))
        require(v <= 512 and o <= v and other <= o and unsupported <= v - o
                and rows <= min(64, o - other) and checked <= v and r['ops'] <= 14000, 'ROOT_COUNTS')
        if r['coverage'] != 'REFUSED':
            require(checked == v and r['ops'] == 24 * (v - o) + 27 * o, 'ROOT_OPERATIONS')
            if r['coverage'] == 'COMPLETE_LINK':
                require(r['reason'] == 'NONE' and rows == o - other, 'COMPLETE_COVERAGE')
            else:
                require((r['reason'] == 'PROPERTY_LIMIT' and v == 512 and rows == o - other)
                        or (r['reason'] == 'ROW_LIMIT' and rows == 64 and o - other == 65), 'PARTIAL_COVERAGE')
        else:
            require(r['reason'] in REASONS and rows == 0, 'REFUSED_COVERAGE')
            require(r['ops'] >= 16 * v + 2 * o + 8 * checked, 'REFUSED_OPERATIONS')
    elif event in ('END', 'STOP'):
        require(r['outcome'] in OUTCOMES and r['attempts'] <= 1, 'OUTCOME')
        require(r['errors'] <= 256 and r['refusals'] <= 256 and r['reentry'] <= 64
                and (not r['reentry_saturated'] or r['reentry'] == 64), 'COUNTER_BOUND')
        if event == 'END':
            stages = tuple(r[k] for k in ('gate_ops', 'root_ops', 'mgr_ops', 'ctrl_ops'))
            require(all(v <= cap for v, cap in zip(stages, CAPS)) and sum(stages) == r['total_ops']
                    and r['total_ops'] <= 28208 and r['rows'] <= 128, 'END_OPERATIONS')
            require((r['outcome'] == 'NOT_OBSERVED') == (r['attempts'] == 0), 'SILENT_ATTEMPTS')
        else:
            require(r['remaining'] <= 1 and r['uncertain'] <= r['remaining'] and r['ignored'] <= 64
                    and (not r['ignored_saturated'] or r['ignored'] == 64)
                    and r['cleanup_failures'] <= r['removal_attempts'] <= 256, 'STOP_COUNTS')
    elif event == 'FAULT':
        require(r['kind'] in ('ERROR', 'REFUSED') and r['scope'] in ('SESSION', 'GATE', 'ROOTS', *ROOTS)
                and r['reason'] in REASONS, 'FAULT_SCHEMA')
    else:
        require(r['reason'] in ('OVERLAP', 'EPOCH', 'CLOCK', 'IDENTIFIER', 'REGISTRATION')
                and r['remaining'] <= 1 and r['uncertain'] <= r['remaining'], 'NOT_STARTED_SCHEMA')
    return r


class Session:
    def __init__(self, epoch, line, started=False, failed_start=False):
        self.epoch, self.line, self.started, self.failed_start = epoch, line, started, failed_start
        self.begun = False
        self.roots, self.rows, self.faults = {}, {root: [] for root in ROOTS}, []
        self.end, self.stop = None, None
        self.records = self.controls = 0
        self.closed = False
        self.errors = 0
        self.refusals = int(failed_start)
        self.reentry = self.ignored = self.cleanup = self.removals = 0
        self.reentry_sat = self.ignored_sat = False

    def record(self, r):
        event = r['event']
        self.records += 1
        self.controls += int(event in ('STOP', 'NOT_STARTED'))
        require(self.records <= 205 and self.controls <= 64 and len(self.faults) + int(event == 'FAULT') <= 8, 'SESSION_RECORD_BOUND')
        require(r['epoch'] == self.epoch, 'EPOCH_ORDER')
        if event == 'BEGIN':
            require(self.started and not self.begun and self.end is None and not self.closed, 'BEGIN_ORDER')
            self.begun = True
        elif event in ('ROW', 'ROOT'):
            root = r['root']
            require(self.begun and self.end is None and not self.closed and root not in self.roots, 'CATALOG_ORDER')
            require(root == 'MGR' or 'MGR' in self.roots, 'ROOT_ORDER')
            if event == 'ROW':
                rows = self.rows[root]
                require(r['ordinal'] == len(rows) + 1 and not any((v['owner'], v['name']) == (r['owner'], r['name']) for v in rows), 'ROW_ORDER_DUPLICATE')
                rows.append({k: v for k, v in r.items() if k not in ('epoch', 'event', 'root')})
            else:
                require(r['rows'] == len(self.rows[root]), 'ROW_CONSERVATION')
                self.roots[root] = {k: v for k, v in r.items() if k not in ('epoch', 'event', 'root')}
        elif event == 'FAULT':
            # A later explicit STOP may discover session expiry/clock failure
            # after a prior resolved STOP. That fault needs its own final STOP.
            self.closed = False
            self.faults.append({k: v for k, v in r.items() if k not in ('epoch', 'event')})
            if r['kind'] == 'ERROR': self.errors += 1
            else: self.refusals += 1
        elif event == 'END':
            require(self.end is None and not self.closed and r['attempts'] == int(self.begun), 'END_ORDER')
            self.counters(r)
            stages = tuple(r[k] for k in ('gate_ops', 'root_ops', 'mgr_ops', 'ctrl_ops'))
            require(r['rows'] == sum(len(v) for v in self.rows.values()), 'END_ROW_CONSERVATION')
            for root, key in zip(ROOTS, ('mgr_ops', 'ctrl_ops')):
                require(r[key] == (self.roots[root]['ops'] if root in self.roots else 0), 'STAGE_CONSERVATION')
            if not self.begun:
                require(stages == (0, 0, 0, 0) and not self.roots and not any(self.rows.values()), 'SILENT_DATA')
            elif r['outcome'] in ('COMPLETE_SCOPED_METADATA', 'PARTIAL_METADATA'):
                require(self.started and len(self.roots) == 2 and stages[:2] == (98, 68)
                        and not self.errors and not self.refusals and not self.reentry, 'SUCCESS_FAILURE_HISTORY')
                coverages = {v['coverage'] for v in self.roots.values()}
                require('REFUSED' not in coverages and r['outcome'] ==
                        ('PARTIAL_METADATA' if 'PARTIAL' in coverages else 'COMPLETE_SCOPED_METADATA'), 'END_COVERAGE')
            else:
                require(self.errors or self.refusals, 'REFUSAL_HISTORY')
                # A catalog refusal stops that loop. A later root recheck or
                # callback boundary can retrospectively refuse both catalogs.
                if 'CTRL' in self.roots and self.roots['MGR']['coverage'] == 'REFUSED':
                    require(self.roots['CTRL']['coverage'] == 'REFUSED' and
                            any(f['scope'] in ('ROOTS', 'SESSION') for f in self.faults), 'REFUSAL_ROOT_ORDER')
                for root, summary in self.roots.items():
                    if summary['coverage'] == 'REFUSED':
                        require(any(f['reason'] == summary['reason'] and f['scope'] in (root, 'ROOTS', 'SESSION')
                                    for f in self.faults), 'ROOT_FAULT_CONSERVATION')
            self.end = {k: v for k, v in r.items() if k not in ('event', 'epoch')}
        elif event == 'STOP':
            require(r['attempts'] == int(self.begun) or (r['deferred'] and r['attempts'] == 1 and self.started), 'STOP_ATTEMPT')
            require(not self.started or not r['uncertain'], 'ACCEPTED_HANDLE_UNCERTAIN')
            if self.end is not None:
                require(r['reentry'] == self.end['reentry'] and r['reentry_saturated'] == self.end['reentry_saturated'], 'POST_END_REENTRY')
            self.counters(r)
            require(self.ignored <= r['ignored'] and (not self.ignored_sat or r['ignored_saturated']), 'IGNORED_REGRESSION')
            require(self.cleanup <= r['cleanup_failures'] and self.removals <= r['removal_attempts'], 'CLEANUP_REGRESSION')
            delta = r['removal_attempts'] - self.removals
            failures = r['cleanup_failures'] - self.cleanup
            require(delta <= 4 and failures <= delta and (not r['deferred'] or delta == 0), 'CLEANUP_ATTEMPTS')
            if self.stop is not None and self.stop['remaining'] == 0:
                require(delta == 0 and r['remaining'] == 0 and not r['uncertain'], 'RESOLVED_HANDLE_REGRESSION')
            if self.started and not r['deferred'] and self.stop is None:
                require(delta >= 1, 'MISSING_REMOVAL')
            if r['remaining'] and not r['deferred'] and r['removal_attempts'] < 256:
                require(delta == 4 and failures == 4, 'UNRESOLVED_REMOVAL')
            self.ignored, self.ignored_sat = r['ignored'], r['ignored_saturated']
            self.cleanup, self.removals = r['cleanup_failures'], r['removal_attempts']
            require(r['outcome'] == ('REFUSED' if self.errors or self.refusals or self.cleanup or r['remaining']
                    else self.end['outcome'] if self.end is not None else 'NOT_OBSERVED'), 'STOP_OUTCOME_HISTORY')
            require(r['deferred'] or self.end is not None, 'MISSING_END_BEFORE_STOP')
            self.closed = not r['remaining'] and not r['deferred']
            self.stop = {k: v for k, v in r.items() if k not in ('event', 'epoch')}
        elif event == 'NOT_STARTED':
            require(r['reason'] == 'OVERLAP' or self.failed_start, 'NOT_STARTED_ORDER')
            require(not self.started or not r['uncertain'], 'ACCEPTED_HANDLE_UNCERTAIN')
            if self.stop is not None and self.stop['remaining'] == 0:
                require(r['remaining'] == 0 and r['uncertain'] == 0, 'NOT_STARTED_HANDLE')
        else:
            require(event == 'START', 'RECORD_ORDER')

    def counters(self, r):
        require(r['errors'] == self.errors and r['refusals'] == self.refusals, 'FAULT_CONSERVATION')
        require(self.reentry <= r['reentry'] and (not self.reentry_sat or r['reentry_saturated']), 'REENTRY_REGRESSION')
        self.reentry, self.reentry_sat = r['reentry'], r['reentry_saturated']

    def report(self):
        return dict(epoch=self.epoch, line=self.line, started=self.started, failed_start=self.failed_start,
            closed=self.closed, records=self.records, controls=self.controls, roots=self.roots,
            rows=self.rows, faults=self.faults, end=self.end, stop=self.stop)


def review_bytes(raw):
    if type(raw) is not bytes:
        return input_error('INPUT_TYPE')
    if len(raw) > MAX_BYTES:
        return input_error('BYTE_BOUND')
    try:
        text = raw.decode('utf-8', errors='strict')
    except UnicodeError:
        return input_error('UTF8')
    if '\x00' in text:
        return input_error('NUL')
    lines = text.split('\n')
    if len(lines) - int(lines[-1] == '') > MAX_LINES:
        return input_error('LINE_BOUND')
    if any(len(line.encode('utf-8')) > MAX_LINE_BYTES for line in lines):
        return input_error('LINE_BYTES_BOUND')
    issues, sessions, current = [], [], None
    issue_count = records = idle_controls = 0
    last_epoch = 0

    def issue(line, code):
        nonlocal issue_count
        issue_count += 1
        if len(issues) < MAX_ISSUES:
            issues.append(dict(line=line, code=code))

    def new_session(r, line, started=False, failed_start=False):
        nonlocal current, last_epoch
        require(len(sessions) < MAX_SESSIONS, 'SESSION_BOUND')
        require(r['epoch'] > last_epoch and (current is None or current.closed), 'SESSION_ORDER')
        current = Session(r['epoch'], line, started, failed_start)
        sessions.append(current)
        last_epoch = r['epoch']

    if raw and not raw.endswith(b'\n'):
        issue(len(lines), 'FINAL_NEWLINE')
    try:
        for number, line in enumerate(lines, 1):
            line = line.removesuffix('\r')
            if not any(marker in line for marker in MARKERS):
                continue
            records += 1
            require(records <= MAX_RECORDS, 'RECORD_BOUND')
            match = FRAME.fullmatch(line)
            if match is None:
                issue(number, 'MIXED_CLIPPED_UNKNOWN_MARKER')
                continue
            try:
                r = decode_record(match['payload'])
            except (ValueError, TypeError, RecursionError, OverflowError):
                issue(number, 'INVALID_RECORD')
                continue
            if r['event'] == 'START':
                new_session(r, number, started=True)
            elif r['event'] == 'NOT_STARTED' and (current is None or r['epoch'] != current.epoch):
                if r['reason'] in ('REGISTRATION', 'IDENTIFIER') and r['epoch'] > last_epoch:
                    new_session(r, number, failed_start=True)
                else:
                    require(r['remaining'] == 0 and r['uncertain'] == 0 and r['epoch'] == last_epoch, 'ORPHAN_CONTROL')
                    idle_controls += 1
                    require(idle_controls <= 64, 'IDLE_CONTROL_BOUND')
                    continue
            if current is None:
                issue(number, 'ORPHAN_RECORD')
                continue
            try:
                current.record(r)
            except ValueError as exc:
                issue(number, exc.args[0])
        for run in sessions:
            if run.end is None or run.stop is None or not run.closed:
                issue(run.line, 'INCOMPLETE_CLOSURE')
            if run.begun and any(run.rows[root] and root not in run.roots for root in ROOTS):
                issue(run.line, 'MISSING_ROOT')
    except ValueError as exc:
        issue(len(lines), exc.args[0])
    failure = any(s.errors or s.refusals or s.cleanup or s.failed_start for s in sessions)
    partial = any(s.end and s.end['outcome'] == 'PARTIAL_METADATA' for s in sessions)
    silent = any(s.end and s.end['outcome'] == 'NOT_OBSERVED' for s in sessions)
    status = ('INVALID_LOG_TEXT' if issue_count else 'NO_METADATA_RECORDS' if not sessions
              else 'REFUSED_LOG_TEXT' if failure else 'PARTIAL_LOG_TEXT' if partial
              else 'NOT_OBSERVED_LOG_TEXT' if silent else 'COMPLETE_LOG_TEXT')
    return dict(baseline(), status=status, log_text_acceptable=bool(sessions) and not issue_count,
        byte_length=len(raw), sha256=hashlib.sha256(raw).hexdigest(), line_count=len(lines) - int(lines[-1] == ''),
        records=records, idle_controls=idle_controls, sessions=[s.report() for s in sessions],
        issues=issues, issue_count=issue_count, issues_truncated=issue_count > len(issues),
        coverage_limit='PropertyLink scope only; OTHER and unsupported descriptors are not semantic absence')


def exit_code(report):
    return 0 if report['status'] == 'COMPLETE_LOG_TEXT' else 1 if report['log_text_acceptable'] else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path, help='preserved UTF-8 log; read only')
    args = parser.parse_args(argv)
    try:
        # Bound before decoding, including files whose stat grows after opening.
        with args.log.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        report = review_bytes(raw)
    except OSError:
        report = input_error('READ_ERROR')
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    return exit_code(report)


if __name__ == '__main__':
    raise SystemExit(main())
