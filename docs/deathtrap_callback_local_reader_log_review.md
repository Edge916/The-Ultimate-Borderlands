# Offline review of callback-local reader text

The standard-library [reviewer](../scripts/review_deathtrap_callback_local_reader_log.py)
checks the fixed `[UVH-CALLBACK-READ]` grammar in the accepted v0.2.16
[runtime](../sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py), commit
`b51f91ff28ece47fc28ca91eef6f12cc305f8c8b` / [draft PR 32](https://github.com/Edge916/The-Ultimate-Borderlands/pull/32).
It reads bytes and produces JSON. It imports no SDK, runs no game code and
changes no input file. The [tests](../tests/test_deathtrap_callback_local_reader_log_review.py)
use synthetic mutations and the existing inert runtime harness. The
[checks](../evidence/deathtrap_callback_local_reader_log_review_checks.json)
record actual offline validation and preserved historical evidence.

Run on a preserved copy of the complete log, after separately approved owner
steps and full exit, using an available Python interpreter:

```powershell
python -B scripts/review_deathtrap_callback_local_reader_log.py path/to/preserved.log
```

Exit 0 means COMPLETE_LOG_TEXT for the reader section; exit 1 means missing,
partial, invalid or refused reader text; exit 2 means an input/read/bound error.
The JSON status is authoritative about this parser's text assessment. It is
not an installation check or authorization for a game test/public log export.

| Status | Meaning |
|---|---|
| COMPLETE_LOG_TEXT | Every reader session has consistent ordered records, paired STOP/OUTCOME and resolved reader handles, with no refused/error/cleanup-failure history. |
| REFUSED_LOG_TEXT | Structurally complete but a refusal, error, failed registration, unresolved handle or removal failure occurred. A successful retry retains this result. |
| PARTIAL_LOG_TEXT | Reader-related text exists but an accepting/failed session cannot be reconstructed and closed. No accepting session is invented. |
| INVALID_LOG_TEXT | Fixed grammar, epoch, order, label, budget, counter or outcome contradiction. |
| NO_READER_TEXT | No reader marker was found. This is not zero accepting attempts. |
| INPUT_ERROR | Wrong input type, unreadable file, invalid UTF8/NUL or a size/count bound was exceeded. |

## Records and order

An accepting session starts with this exact shape:

```text
START version=0.2.16 epoch=1 target=DeactivateSkill phase=PRE hooks=1 mode=STANDALONE_READER
```

Epochs begin at 1 and increase consecutively in the complete transcript;
duplicates, replay, gaps and cross-session records are rejected. A failed
START can consume an epoch. Its unnumbered NOT_STARTED record is associated
only with the following bounded STOP carrying that epoch; unmatched failures
remain partial. Early EPOCH/CLOCK refusals need not produce a STOP at all.
OVERLAP is a refused control action, not a fabricated accepting START.

EVENT records assert `schema=VALID`, positive consecutive ordinal and attempt,
fixed controller/definition labels, `ownership=UNESTABLISHED`, operation total
and four stage counts. There is no separate successful SCHEMA record.
The parser verifies this assertion's grammar and consistency; it cannot
independently verify SDK descriptors or identity from log text.

The fixed normal-event operation counts were checked against actual inert
runtime transcripts and the independently counted reader fixture:

| Controller | Definition | Four stages | Total | Classification |
|---|---|---|---:|---|
| NULL_INSTIGATOR | NOT_READ | 58,49,0,0 | 107 | null |
| OTHER_CONTROLLER_CLASS | NOT_READ | 58,50,0,0 | 108 | filtered |
| OTHER_WRAPPER | NOT_READ | 58,50,1,0 | 109 | filtered |
| SAME_WRAPPER | NULL_DEFINITION | 58,50,36,50 | 194 | null |
| SAME_WRAPPER | OTHER_NAME | 58,50,36,52 | 196 | filtered |
| SAME_WRAPPER | DEATHTRAP_NAME | 58,50,36,52 | 196 | useful primitive observation |

Only these six combinations are accepted. A budget total must equal its four
stages, every stage is at most 64 and the total is at most 256. Counts are
reader-issued operations; SDK conversion/helper internals are excluded.
Refusal/error records may contain partial counts; BUDGET refusal requires a
stage exhaustion and a LOGGING error requires a normal-event budget.
These rules deliberately bind to v16. A later source/grammar change needs a
separately reviewed parser correction.

Every EVENT, callback REFUSED or callback ERROR accounts for one accepting
attempt. A callback refusal/error is terminal; records cannot conceal missing
attempts or keep classifying afterward. The bound is 64 attempts and 24
classifications. With v16's terminal first refusal and 24-event cap, an
ordinary complete session cannot reach the defensive 64-attempt cap; a
synthetic attempt-64 assertion with missing earlier records is rejected.
Reentry is a separate primitive counter, requires an accepting attempt and
does not add attempts or classifications. Its exact value is asserted by STOP,
not independently observed by the parser.

LIMIT accepts only TIME, EVENTS or ATTEMPTS. EVENTS requires 24 classified
records; ATTEMPTS requires 64 accounted attempts. A TIME callback refusal
sets the limit without a separate LIMIT line. The 120-second bound is checked
by the runtime on operations/controls, with no background timer. A later idle
STOP can add TIME after an earlier clean STOP; this does not prove an engine
clock or the owner's waiting interval.

STOP reports the session epoch, remaining/uncertain handles, every counter
and limit. It must be followed by OUTCOME before another reader record.
Later reader activity, including an idle TIME limit, clock error or removal
retry, requires a fresh STOP/OUTCOME. An earlier completed pair cannot certify
a truncated later control sequence or allow a new START while it is pending.
Intervening unrelated SDK lines are allowed. Repeated STOP/OUTCOME pairs are
legal: event/attempt/filter/null/refusal/reentry totals stay fixed, remaining
and uncertainty cannot increase, and clock/removal errors stay in history.
Removal errors require a pending handle and an exact retained failure count.
An accepting START has known hook ownership; later uncertain=1 contradicts
that accepting record. Registration without an accepting START can instead
retain unknown registration uncertainty. Unknown hooks are never treated as
owned just because a later STOP resolves them.

OUTCOME is recomputed from the reported, checked counters: REFUSED for any
remaining handle, refusal, error or cleanup failure; otherwise NOT_OBSERVED
for zero attempts; otherwise OBSERVED_PRIMITIVE if a useful classification
occurred, or OBSERVED_FILTERED for only filtered/null records. A refused
session remains part of the overall result after a later clean session.

## Bounds and separate evidence

Input limits are 16 MiB, 100,000 lines, 16,384 bytes per input line, 4,096 reader
records, 128 sessions and 128 retained issue details. Issue totals continue
after the detail cap. Every project reader line, including `[UVH-BOOST]`, is
at most 384 UTF8 bytes. Integers use canonical nonnegative decimal syntax
and are at most 2,147,483,647. Input is strict UTF8; CRLF/LF are supported;
reader input must end with a newline so an unterminated capture cannot pass.
Bare reader, project-prefixed and the observed bounded SDK INFO frames are
accepted. Nested, unknown, clipped or malformed reader markers are rejected.
JSON emits fixed issue codes and allowlisted labels, never unknown payload
text, exception bodies or object paths.

COMPLETE_LOG_TEXT checks only reader transcript consistency. It cannot
detect an entirely omitted session, fabricated text or a relaunch spliced
into a carefully edited transcript. Other observer cleanup, node insertion,
point/rank state, native arrays/manual Duration restore, exact installed
files, owner clicks/protocol, process exit and log authenticity are separate
capture/provenance evidence. This standalone reader needs no ARM and does
not log a point baseline or array restoration; older v15 parser requirements
are not substituted for its actual interface. All frozen v12-v15 parser
outputs and files remain unchanged.

PRE records attempted entry even if another hook blocks native execution.
SAME_WRAPPER and DEATHTRAP_NAME do not establish manager ownership, exact
summon/allocation generation, successful deactivation, lifespan, rank-one
effect eligibility or native write/restoration safety. Schema facts are
asserted in the log. Zero attempts remains NOT_OBSERVED; silence is not a
reason to repeat a diagnostic. Every report leaves native ownership, engine
behavior and effect readiness unestablished.

No new raw game capture, SDK-source import/execution/stub compilation,
installation, game action, outgoing support request, save/private-backup
operation, merge or release occurs in this task. The new game protocol and
exact build still require separate explicit owner approval after review.
