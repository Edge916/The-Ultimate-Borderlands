# v0.2.18 activation-reader log reviewer

This standalone standard-library reviewer checks the bounded text emitted by
the [v18 runtime](../sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py) at
commit `30af0d1bb8abd94e06420689a04425e047ce82b8`. Read the
[accepted design](deathtrap_activation_reader_design.md),
[source audit](deathtrap_activation_reader_feasibility.md),
[implementation checks](../evidence/deathtrap_activation_reader_implementation_checks.json)
and [prepared instructions](deathtrap_activation_reader_instructions.md).
V18 has no live capture. This reviewer adds no runtime, package or game action.

From a checkout, run Python on
`scripts/review_deathtrap_activation_reader_log.py <log-path>`.
The script exposes `review_bytes(raw)` for an exact bytes object and `main(argv)`
for the command line. It reads at most 16 MiB plus one byte and prints a bounded
JSON report. It does not import the runtime, an earlier reviewer or any SDK.

| Exit | Meaning |
| --- | --- |
| 0 | COMPLETE_LOG_TEXT: reader sections are consistent, closed and resolved without recorded failure. |
| 1 | Invalid, partial, refused or absent reader text. |
| 2 | Bounded input, read, type or encoding error. |

Schema version 1 reports `reader_version=0.2.18`. Parser completion establishes
text consistency only. It does not authenticate a log or verify installation,
owner actions, process exit, actual hook handles or native engine behavior.
Native ownership, summon generation, engine clock, owner protocol and lifetime
remain unestablished; native lifecycle/effect readiness remains false. Preserve
the original effect dependencies.

## Exact activation and Name grammar

Accept only `[UVH-ACTIVATION]` with an exact START for version 0.2.18,
target ActivateSkill, phase PRE, hooks=1 and mode STANDALONE_READER. EVENT fields
are ordered: epoch, ordinal, attempt, schema, controller, definition, name,
ownership, ops and four stages. No missing, duplicate or extra field is accepted.

| Controller / definition | Name | Four stages / total |
| --- | --- | --- |
| NULL_INSTIGATOR / NOT_READ | `-` | 98,65,0,0 / 163 |
| OTHER_CONTROLLER_CLASS / NOT_READ | `-` | 98,66,0,0 / 164 |
| OTHER_WRAPPER / NOT_READ | `-` | 98,66,1,0 / 165 |
| SAME_WRAPPER / NULL_DEFINITION | `-` | 98,66,36,66 / 266 |
| SAME_WRAPPER / OTHER_NAME | Exact ASCII identifier unequal to Skill_DeathTrap | 98,66,36,68 / 268 |
| SAME_WRAPPER / DEATHTRAP_NAME | Exactly Skill_DeathTrap | 98,66,36,68 / 268 |

Identifiers contain 1..128 ASCII letters, digits or underscores. `-` is the
absence token, outside that alphabet. Words such as NOT_READ or NULL_DEFINITION
can be valid OTHER_NAME identifiers; they do not represent absence. No clipping,
coercion, case folding, suffix heuristic, alias or path inference is performed.
Reject old v17 counts even if the Name and labels otherwise look valid.

For partial REFUSED/ERROR budgets, each stage is at most its corresponding cap:
112, 80, 48 or 80. The total must equal their sum and be at most 320. A BUDGET
refusal must reach a documented stage or total cap; a LOGGING error uses a legal
completed EVENT count tuple. These counters describe reader-issued operations,
rather than SDK-internal copies, conversions, helper work or native timing.

Only a locally valid EVENT enters the report's ordered `events` list. Its fields
are line, epoch, ordinal, attempt, controller, definition and the validated Name;
an absence token becomes JSON null. An invalid local branch, budget, Name,
epoch/order or sequence cannot export that record's identifier. Earlier locally
valid events can remain visible in an overall invalid report; that visibility
does not make the whole log acceptable.

Issues contain fixed codes and line numbers, without malformed input, unrelated
SDK text, exception bodies, addresses or object paths. A valid simple identifier
can still contain personal text in a modded game. The alphabet is not a universal
privacy guarantee, and publishing any later raw log needs exact-content review
and separate approval.

## Framing, state and finite bounds

Accept bare reader records, project-prefixed records and the observed bounded
SDK INFO framing, using strict UTF-8 and LF or CRLF. Reject unknown, malformed,
nested or clipped activation frames and legacy `[UVH-CALL` reader markers,
including old v16/v17 text or mixed evidence. Old reader lines must not disappear
into a false zero-event activation result. A reader log needs its final newline.

All numeric fields use canonical nonnegative decimal integers at most
2147483647: no signs, leading zeros, alternative bases or oversized values.
Epochs must bind consistently and advance without replay or gaps. Events must
have the correct ordinal/attempt sequence. Enforce 64 accepting attempts and
24 classified events; filtered/null/useful counts and LIMIT/STOP/OUTCOME must
agree with the actual records. Reentry does not invent accepting attempts.
OVERLAP is a refused control note, rather than another accepting START or proof
of which option the owner clicked.

Refusal, error, failed registration, uncertainty and failed removal remain
visible after a successful cleanup retry. An accepting session needs a resolved
STOP/OUTCOME pair, with zero remaining and uncertain handles and no recorded
failure. Repeated resolved pairs are legal. TIME, CLOCK or removal activity after
an earlier pair needs a fresh pair; earlier closure cannot resolve a later tail.
Reject pending/unclosed restarts, incomplete STOP/OUTCOME pairs, contradictory
counters and an outcome that erases earlier failure history.

| Bound | Maximum |
| --- | ---: |
| Input bytes | 16 MiB |
| Input lines | 100000 |
| Bytes per input line | 16384 |
| Reader records | 4096 |
| Sessions | 128 |
| Retained issues | 128 |
| Locally valid events per session | 24 |
| Project record bytes, including the full project/reader prefixes | 384 |

SDK headers and newlines are handled separately from the project-record bound.
Issue count and the truncation flag retain overflow information. At most
24 events across each of 128 sessions yields 3072 retained identifiers, each
at most 128 ASCII bytes, also subject to the global record cap. A twenty-fifth
event cannot grow that session's identifier list. STOP history remains bounded
by the finite input and record limits. No background timer is introduced, and
SDK timestamps are not an engine clock or independently measured owner wait.

## Evidence limits and preserved captures

Zero accepting attempts is NOT_OBSERVED. Valid filtered/null classifications are
OBSERVED_FILTERED. An exact literal match can produce OBSERVED_PRIMITIVE, always
with ownership UNESTABLISHED. PRE describes attempted entry even when another
hook blocks or changes the original call; it proves no successful activation,
Deathtrap association, unique active instance, native generation, Duration or
safe write/readback/restoration interval. Silence never proves absence.

The runtime validates all six descriptors, including ReturnValue metadata, but
the Python reader does not read ret or AdditionalSkillTarget, SkillGrade or
StateChangeDelegate values. The SDK can process copied arguments and a prior
Boolean override before Python runs. Text validation cannot suppress or certify
that processing, native pointer validity, destruction exclusion, thread affinity
or installed binary/build equivalence.

The preserved [v17 capture](../evidence/deathtrap_callback_definition_name_user_test.log)
and [manifest](../evidence/deathtrap_callback_definition_name_capture_manifest.json)
remain one UpshotRobot/OTHER_NAME event, OBSERVED_FILTERED, under the unchanged
original v17 reviewer. The owner's natural Deathtrap end is separate evidence.
The activation reviewer rejects this old log as v18 evidence; it cannot infer an
alias or recover v16's omitted Name. Keep all raw logs, manifests, tested source
snapshots, historical reviewers and original versioned ZIPs unchanged.

## Verification and later gates

Actual targeted/full test results, source/CLI checks, emitted inert transcripts,
parser adversarial checks and preservation results are recorded in the
[companion checks](../evidence/deathtrap_activation_reader_log_review_checks.json).
This document states no uncompleted test count or hosted/native result. Inert
fixtures and parser success cannot establish a game run or native lifetime.

These new reviewer files need their own exact public approval and deliberate
acceptance review. That approval does not authorize gameplay or raw capture
export. A later owner diagnostic requires accepted implementation/reviewer,
the exact reviewed ZIP/commit and explicit approval of the meaningful protocol,
including any ordinary summon. Future instructions must distinguish main-menu
Offline/Gaige/title verification without ARM, Continue and full map loading,
in-map START22, only the separately approved action, in-map STOP23/CANCEL3 and
full desktop exit before private log preservation. No finalized gameplay action
or waiting interval is requested here. Refusal, unavailability, silence and
reached bounds are preserved without retry to manufacture coverage.

No real SDK/stub import, execution or compilation, native invocation/write,
installation, game/save/private-backup access, purchase, summon, effect, support
message, merge or release occurs in this offline reviewer task. Native effect
readiness remains NOT_READY.
