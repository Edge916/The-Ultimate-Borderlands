# Passive manager-event log review

The read-only reviewer checks text emitted by the accepted v0.2.15 runtime at
`e197266ebb88e71f5cbf855289dcea283f8f93ea` /
[draft PR24](https://github.com/Edge916/The-Ultimate-Borderlands/pull/24).
Read the [implementation checks](../evidence/deathtrap_passive_event_implementation_checks.json)
and [reviewer checks](../evidence/deathtrap_passive_event_log_review_checks.json).
The runtime,15 versioned ZIPs and previous captures remain unchanged. There is
no actual v15 game capture or native callback result in this task.

Use a verified Python interpreter from the repository root:

```text
python -B scripts/review_deathtrap_passive_event_log.py preserved_log.log
```

The CLI reads at most16MiB, writes only a JSON report to stdout, and never
modifies the input. It imports only standard-library modules. It does not
import the runtime/SDK, execute log content, reconstruct objects or retain
arbitrary startup messages, wrapper paths or exception text in the report.
File errors report a fixed FILE_READ code without the input path.

| Status | Meaning | CLI exit |
| --- | --- | ---: |
| COMPLETE_LOG_TEXT | Closed consistent observation text, new handles resolved, old cleanup assertions present | 0 |
| REFUSED_LOG_TEXT | Closed refusal or cleanup failure history; retained even after a successful retry | 1 |
| PARTIAL_LOG_TEXT | Missing start/final/stop/outcome, orphan records or missing old cleanup assertions | 1 |
| INVALID_LOG_TEXT | Malformed framing/grammar, contradictory ordering/state/counters or invalid selected old cleanup records | 1 |
| NO_OBSERVER_TEXT | No passive observation section; unrelated or historical SDK text is not a v15 result | 1 |
| INPUT_ERROR | Wrong type, unreadable file, invalid UTF8 or exceeded input bounds | 2 |

COMPLETE_LOG_TEXT is text consistency. Authenticity, installed package/source
identity, actual game callbacks, native identity/liveness, native cleanup,
process exit, duration restoration and effect readiness remain unestablished
by this script. A matching input hash identifies bytes, not their origin.
Do not fabricate a capture from synthetic fixtures or use a complete report
as evidence that missing calls did not happen.

Recognized passive records have exact version15, DeactivateSkill, PRE and NONE
labels. Whole lines may be plain, prefixed by `[UVH-BOOST]`, or use the observed
bounded timestamp/INFO wrapper plus that prefix. Timestamp text is discarded;
it cannot measure engine time or lifespan. Unknown/suffixed/embedded records
are rejected. Each emitted passive line is at most256UTF8bytes excluding the
SDK wrapper. Exact integer grammar rejects Boolean, negative, nonfinite,
leading-zero and over31bit fields. Baseline/final points have two entries and
ranks have three; the candidate rank is0, while original skill ranks may vary.

Ordering checks require a baseline before sequential event ordinals1through24,
and forbid events after limit, abort, final or STOP. STOP counts must match
events, captured plus reentrant must not exceed attempts, and attempts cannot
exceed64. Events24 require EVENTS limit; attempts64 require ATTEMPTS limit.
TIME is only a runtime assertion of a Python observation bound. Verified FINAL
must match the logged baseline; UNVERIFIED FINAL preserves refusal. No FINAL
is required for a setup that explicitly reports NOT_STARTED and never accepts
observation. The START line is logged before final publication of accepting
state, so START followed by NOT_STARTED is a setup refusal, not a live session.

NOT_STARTED OVERLAP is a conflicting-control refusal. It does not invent a new
active run or erase an existing run; an unattached refusal before registration
is counted separately. A STOP without prior observation/setup context remains
partial, including a stop that may have interrupted registration. Repeated
STOP/CANCEL after a closed report stays in that run. Capture/attempt/reentrant
counts cannot change on cleanup retries. Owned removal errors must match the
cumulative cleanup-failure counter; counters cannot decrease, and unresolved
remaining/uncertain handles cannot be called clean. REFUSED history cannot be
replaced by NOT_OBSERVED or OBSERVED_UNATTRIBUTED after a successful retry.
Starting another run with pending handles is inconsistent.

Silence is NOT_OBSERVED. A recorded entry is OBSERVED_UNATTRIBUTED and remains
an attempted canonical manager-function entry. Another PRE hook may block the
native call. No Deathtrap ownership, successful deactivation, generation,
reference lifetime, summon, engine clock, rank-one effect or measured duration
is inferred. No payload or native invocation adapter is provided.

The cleanup report separately checks the last strict STOP/zero assertion for
the existing state/UI/upgrade/init observer families and the exact original
MorePep/Myelin arrays and occupancy RESTORE assertion. These must follow the
last passive START/baseline/event/setup-refusal activity. A later malformed or
nonzero family report, or a failed/unknown RESTORE, cannot hide behind an
earlier clean assertion. Repeated STOP/CANCEL without new accepting activity
does not erase an earlier restoration assertion. These are log assertions;
they cannot refund points, undo saves, clear player/UI caches or establish
manual Duration restoration or desktop exit.

Input bounds are16MiB/100000lines/16384bytes per raw line/4096selected records/
128runs/128reported issues. The total issue count and a truncation flag preserve
the existence of further issues. Reports contain closed codes, line numbers,
bounded primitives and a SHA256 rather than arbitrary raw text. The accepted
v12/v13/v14 metadata reviewer remains byte-identical and is still used for
those frozen captures. This separate reviewer does not alter that grammar.

The acceptance suite includes94 meaningful new cases, including actual
accepted-runtime transcripts generated under inert SDK fixtures, malicious
input, strict UTF8/tuple/counter/wrapper/order/bounds, registration/control
refusal, cleanup retry history, old cleanup and CLI exit/output behavior.
These are synthetic test cases. Actual fresh full-suite and provenance results
are recorded in the companion checks; no raw game log is added here.

After the reviewer is published and deliberately reviewed, separately scope
an owner-run capture against the exact originalv15 ZIP and installed files.
The location-specific proposed protocol remains main-menu Offline Gaige,
title verification and ARM1; Continue until fully loaded into the map;
START20 once and stay about20seconds; STOP21 then CANCEL3 in the map; fully
exit to desktop before relaunching. Obtain explicit exact-build/protocol
approval first. This document does not request a new test or installation.
No purchase,respec,travel,summon,manual boost,other trace,game/nativeSDK
execution,save/private-backup access,co-op,merge or release in this task.
