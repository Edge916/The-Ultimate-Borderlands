# Offline v0.2.11 log reviewer

This tool reads an explicitly supplied preserved UTF-8 log and prints JSON to
stdout. It does not import the SDK/runtime, invoke native functions, alter the
log, install a mod, or write a report file. Use an actual Python 3.9+ executable;
the Windows `python` alias may not be an installed interpreter.

```powershell
& 'C:/path/to/python.exe' -I -B scripts/review_v031_log.py evidence/v031_user_test.log
```

The capture file remains pending. Run against it only after the owner has
performed the prepared diagnostic and exclusively preserved the complete log.
An old log, mock output or manually constructed fixture cannot establish a new
game session. The tool does not authenticate a log's origin.

## Evidence reported

The source section records the exact original byte count, SHA256, line count
and final line terminator, before UTF-8 BOM/CRLF handling. Each actual
`[UVH-CLASS] BEGIN` starts a separate call. SDK timestamp/source prefixes and
bare diagnostic tags are supported. Reused `[UVH-PRESENT] SCHEMA` messages do
not create calls. Diagnostic version headers from other UVH families are
checked for conflicting versions.

Each call preserves its version, BASELINE/FINAL points and ranks, Myelin
presentation reference, wrapper/class status, declared/actual class labels,
bounded ancestry rows, coverage, logged declared relation and observers added.
Records must be ordered, unique where applicable, within the runtime's bounds,
and consistent. FINAL's `unchanged_from_start=True` does not substitute for
comparing the actual point/rank tuples. State differences between calls also
prevent complete-log acceptance.

Metadata names/paths are compared only for consistency; they never establish
SDK object identity, parent links, eligibility or an effect. `declared_relation`
is the diagnostic's recorded claim, not a relationship independently computed
from those labels. Even complete metadata with relation `NO` means only that
the log reports a complete observed ancestry; it is not approval for gameplay
use or guard changes.

Calls retain separate outcomes:

- `COMPLETE_METADATA`: well-formed complete typed metadata records.
- `KNOWN_ABSENCE`: explicit verified None, with not-applicable ancestry.
- `PARTIAL_METADATA`: stable CAPPED, CYCLE or UNAVAILABLE observations.
- `ABORTED` and `NOT_INSPECTED`: explicit terminal refusal outcomes.
- `INVALID_OR_INCOMPLETE`: malformed, contradictory or missing records.

For complete-log acceptance, the last call must be followed by the exact
successful original-array readback and zero remaining INITNODE/STATE/UI/UPGRADE
observers. Missing or failed restoration, malformed/nonzero cleanup, rollback
refusal or a subsequent experiment prevents acceptance. Evidence before the
last call does not prove cleanup afterward. A failed removal followed by a
retry remains conservatively flagged for manual review.

## Exit codes and limits

- `0`: `COMPLETE_LOG_EVIDENCE`; every call is complete metadata/known absence,
  state is stable, versions agree and cleanup is recorded.
- `1`: partial, refused, aborted, malformed, incomplete or historical evidence.
- `2`: command-line/input read error.

Exit 0 is **not a successful live-game-session verdict**. Every report leaves
process exit, installed/archive equality and capture-origin authenticity as
`NOT_CHECKED`, and live game success as `NOT_ESTABLISHED_BY_THIS_TOOL`. Review
the actual raw records, capture manifest, installed-file hashes, ARM/native
registration/solo ownership, user observations and independent process query
separately. Text parsing cannot verify runtime identities or reconstruct
missing engine data. Partial/refused results are useful findings.

## Validation

The implementation starts from independently reviewed PR #1 commit
`3af92a893cce1a4db6850e1270be3d2c78244497`. Only the three claimed paths are added:
`scripts/review_v031_log.py`, `tests/test_log_review.py`, and this document.
Original runtime, tests, snapshots, logs, source handoff, PNG and ZIP bytes stay
unchanged.

Fifty targeted tests cover actual SDK prefixes, complete/known absence/unknown
wrapper/stable partial/capped/cyclic data, literal metadata handling, record
order/duplicates/bounds, changed state within and between calls, mixed versions,
truncation including clipped CRLF, missing/failed/malformed cleanup, later
experiment activation, CLI exit codes and input preservation. Fixtures are
synthetic and never presented as engine results. The retained v0.2.10 log is
also explicitly rejected as new v0.2.11 proof. The combined suite includes the
179 existing SDK mocks; shared task results record the actual full-suite run.

The v0.2.11 live capture and its review remain separate dependent tasks.
