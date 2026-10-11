# Callback-local Definition.Name diagnostic design

**READY_FOR_BOUNDED_NAME_DIAGNOSTIC_IMPLEMENTATION_REVIEW.** Resolve the
identifier omitted by the accepted v0.2.16 reader using its existing one
Definition.Name read. Native ownership, generation and the purchased-node
duration effect remain **NOT_READY_FOR_NATIVE_EFFECT_DESIGN**. This task
delivers design and checks, with no runtime, package or game action.

Accepted base: `73704f2b00658764beef6d26853a544d39944068` /
[assessment PR 35](https://github.com/Edge916/The-Ultimate-Borderlands/pull/35).
Read the actual [assessment](../evidence/deathtrap_callback_local_reader_live_readiness_result.md),
[80-line capture](../evidence/deathtrap_callback_local_reader_user_test.log),
[manifest](../evidence/deathtrap_callback_local_reader_capture_manifest.json),
[runtime](../sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py),
[original reader design](deathtrap_callback_local_reader_design.md) and
[corrected strict reviewer](../scripts/review_deathtrap_callback_local_reader_log.py).
The [companion checks](../evidence/deathtrap_callback_definition_name_design_checks.json)
record actual design validation and its limits.

## Question and evidence boundary

The approved owner reports that Deathtrap ended naturally, followed by STOP23,
CANCEL3 and full exit. The preserved transcript contains one schema-valid
SAME_WRAPPER/OTHER_NAME PRE event, with no DEATHTRAP_NAME event. The actual
supplied Name is intentionally absent. It cannot distinguish an unrelated
skill definition from a different relevant identifier. Neither explanation
is established; do not change the literal or declare the guard defective.

Retain the overlap refusal with unknown triggering control, four resolved
STOP/OUTCOME pairs and SDK header intervals 64.640/76.070/84.229 seconds.
They do not prove four manual clicks, engine time, summon association or
lifespan. The raw capture and every original manifest, tested snapshot and
versioned ZIP stay immutable. Another v16 capture cannot recover the omitted
identifier; do not repeat that build to chase a preferred observation.

The full current [SDK discussion](https://github.com/bl-sdk/pyunrealsdk/issues/97#issuecomment-6108546422)
still has one contributor reply: hook execution prevents GC during its
interval, while Python references outside it do not retain native objects.
Its fingerprint and source revisions are recorded in the accepted assessment.
This design adds no lifetime guarantee: already-invalid inputs, explicit
destruction, installed binary equivalence and post-return access remain
unestablished. No additional issue/comment/support message is proposed.

## Exactly one existing read, primitive transfer

Keep the standalone reader's current guarded access route. No ARM, node
insertion, cached manager/player/definition or manual-duration record is
required or accepted. START checks only project control state and registers
one fixed DeactivateSkill PRE path through the hook-control API. No player or
UObject metadata read occurs in its option handler. Zero natural accepting
callbacks remains NOT_OBSERVED.

Inside each accepting callback preserve the complete fresh manager/function/
args._type/property schema checks; exact SDK binding types and wrapper links;
SkillInstigator-first access; and current solo Gaige/controller/roster checks.
Null instigator, other controller class and other wrapper must not read
Definition or its Name. SAME_WRAPPER is a callback-local wrapper observation,
with manager ownership UNESTABLISHED.

For SAME_WRAPPER, keep the current Definition getter and exact loaded
SkillDefinition class guard. None remains NULL_DEFINITION. For a non-null
validated definition, use the already obtained Name exactly once: exact Python
str, length 1..128, every character in
`ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_`.
Do not call str/repr/path/formatter helpers, truncate, sanitize, hash an
invalid identifier or substitute a placeholder for a failed read. Invalid
type, character, length or getter failure produces the existing fixed
refusal/error route, with no identifier output. SDK conversion happens
before Python applies this bound; this is not a native allocation bound.

The exact case-sensitive literal `Skill_DeathTrap` still produces
DEATHTRAP_NAME; every other valid identifier produces OTHER_NAME. Do not
replace this matcher, add aliases, strip suffixes, fold case or route an
effect from the identifier. The value is one observed simple Name, not a
definition asset path, native instance identity or summon generation.

Extend the inspection return tuple with one primitive name token. Return the
validated string only on the final accepting SAME_WRAPPER/non-null path,
after the existing manager and fresh session rechecks and accepting/epoch/
clock checks. All earlier branches and failures return the single sentinel
`-`. This sentinel is outside the permitted identifier alphabet. No second
Name getter or new descriptor, payload field, revalidation traversal,
activation/POST observer, active-skill scan or native engine call is added.

The inspection frame must finish before logging. Then drop the callback's
obj/args/func/ret locals before assembling the primitive EVENT, as in the
accepted reader. A pending stop, epoch/session change or clock refusal must
clear the returned name token to `-` and take the fixed refusal route, never
emit a successful name record. SDK exceptions and their tracebacks die inside
the inspection frame; no exception/repr/exc_info or native object enters log
arguments, reader state, closures, queues or deferred reporting. All callback
paths return exact None. The observer's sole captured free variable remains
the primitive epoch. SDK helper globals and conversions retain their
previously disclosed limitations; this promises no absence of SDK references.

Only a callback-local exact string and primitive labels/counts cross the
inspection boundary. No name is retained in stats, global state or a history
cache. Subsequent valid callbacks may legitimately report different names;
each is a separate bounded observation. No cross-callback native identity or
stable-name assumption is introduced.

## Fresh wire format and unchanged budgets

Reserve implementation version **0.2.17**, title
`UVH v0.2.17 - CALLBACK DEFINITION NAMES`, prefix `[UVH-CALLBACK-NAME]`, and
distinct fixed hook identifier `UVH_CALLBACK_NAME_V17_DEACTIVATE_PRE`.
Keep the observed path `WillowGame.SkillEffectManager:DeactivateSkill` and PRE.
Reuse controls22/23 for this replacement reader; preserve the other options
and historical/manual behavior. These are prospective constants, not an
installed or game-tested build.

Every record keeps the corrected v16 grammar, field order and meaning, with
only the new prefix, START version0.2.17 and one required EVENT field
`name=<token>` immediately after `definition=<classification>`. The new
reviewer must never silently reinterpret an old v16 record. For example,
the following **synthetic** line is a design illustration, not a captured Name:

```text
[UVH-BOOST] [UVH-CALLBACK-NAME] EVENT epoch=1 ordinal=1 attempt=1 schema=VALID controller=SAME_WRAPPER definition=OTHER_NAME name=Example_Identifier ownership=UNESTABLISHED ops=196 stages=58,50,36,52
```

| Controller / definition | Required name token | Four stages / total | Meaning |
| --- | --- | --- | --- |
| NULL_INSTIGATOR / NOT_READ | `-` | 58,49,0,0 / 107 | Null instigator; no definition getter. |
| OTHER_CONTROLLER_CLASS / NOT_READ | `-` | 58,50,0,0 / 108 | Filtered; no definition getter. |
| OTHER_WRAPPER / NOT_READ | `-` | 58,50,1,0 / 109 | Filtered; no definition getter. |
| SAME_WRAPPER / NULL_DEFINITION | `-` | 58,50,36,50 / 194 | Known null; no Name getter. |
| SAME_WRAPPER / OTHER_NAME | Valid identifier unequal to `Skill_DeathTrap` | 58,50,36,52 / 196 | Filtered, actual simple Name observed. |
| SAME_WRAPPER / DEATHTRAP_NAME | Exactly `Skill_DeathTrap` | 58,50,36,52 / 196 | Useful primitive match; ownership unestablished. |

Only these six triples are legal. Strings such as NOT_READ, NULL_DEFINITION
or Skill_DeathTrap_0 are valid OTHER_NAME identifiers when actually supplied;
they cannot collide with the `-` absence sentinel. No name field is allowed
on REFUSED, ERROR, STOP or other controls. Only a structurally valid EVENT
increments classified/filter/null counters. A logging failure takes the
existing fixed ERROR/cleanup route and cannot certify successful emission.

| Bound | Contract |
| --- | --- |
| Hook and session | One PRE hook; 64 attempts,24 classified events,120 seconds checked on entry/operations/controls; no background timer. |
| Reader-issued SDK work | At most256 operations, four stages capped64; exactly the existing two parameter getters, at most one definition Name read and two current-player acquisitions. Fixed normal branch counts above must be re-proven by new inert implementation transcripts. |
| Name | One exact ASCII string of 1..128 characters, or `-` only for the four absence branches; no clipping. |
| Project record | At most384 UTF8 bytes including `[UVH-BOOST] ` and the full new prefix, excluding SDK timestamp/source header and newline, exactly as the current emitter measures. |
| State and cleanup | Primitive state only; existing registration ownership/uncertainty, overlap/reentry, time/error/limit cleanup, busy-stop deferral and failed-removal retry semantics stay intact. |

The longest proposed normal EVENT is **320 bytes** using a128-character
OTHER_NAME, epoch2147483647, ordinal24 and attempt64. A conservative STOP
ceiling is **224 bytes**, including maximum31-bit defensive counters; some
such counter combinations are unreachable and not legal transcript evidence.
Other forms also fit384. The design checks exhaustively measure six branches
over name-length and relevant decimal-width boundaries and every fixed control
form. Keep the emitter's actual encoded-byte guard; do not raise it or reduce
the Name bound just to fit. SDK header limits are separately enforced by
the strict reviewer.

## Strict reviewer and meaningful verification

Create a separately scoped stdlib-only v17 reviewer; retain the corrected
v16 script and all its existing fixtures unchanged. Accept bare/new-project/
observed bounded SDK INFO framing, strict UTF8 and CRLF/LF, canonical31-bit
integers, exactly ordered fields and a final newline. Reject mixed old/new,
unknown/nested/clipped prefixes and extra fields, even if some earlier
session was complete. Input bounds remain16MiB/100000lines/16384bytes per
input line/4096records/128sessions/128retained issues. Preserve the corrected
trailing-activity rule: TIME, CLOCK or removal activity after an earlier STOP
needs a fresh STOP/OUTCOME; unresolved history blocks restart and cannot
borrow earlier closure. Repeated resolved STOPs remain legal.

Verify each name token against the exact six-branch table, stage totals,
ordinal/attempt sequence, epoch and all final counters/outcomes. Zero attempts
is NOT_OBSERVED; actual valid names with no literal match remain
OBSERVED_FILTERED; a literal match is OBSERVED_PRIMITIVE. Refusal, error,
registration uncertainty and cleanup failure history remain visible after a
successful retry. OVERLAP stays a refused control, not a fabricated START or
identified operator click. Parser completion establishes transcript consistency
only, never actual protocol, installed files, process exit or native identity.

The JSON report may include a bounded ordered event list containing only line,
epoch, ordinal, attempt, fixed classifications and the validated definition
name (JSON null for `-`). At most24 events per session and4096reader records
overall bound this list; names are at most128 ASCII bytes each. Do not export
malformed input, raw unrelated lines, exception bodies or object paths in
issue details. Preserve fixed native readiness/authenticity fields as
NOT_ESTABLISHED/false. Identical names across events establish no association
or generation; different valid names are not a grammar failure.

Implementation tests must prove poison ret/Boolean/foreign Definition remains
unread; one Name getter on a valid non-null local branch; original counts and
no extra native calls; exact None and epoch-only closure; no wrapper/exception/
name retention; and payload locals dropped before the emitter. Cover1/128/129,
empty/non-str/subclass/Unicode/space/newline/path/separator values, exact match/
case/suffix/sentinel-like names, getter exception, fresh session/schema/control
changes, busy/reentry/stops/limits/failed removal and logging failures. A
stop triggered during Name access must prevent EVENT/name output. Two valid
callbacks with different identifiers must emit separate observations without
changing the matcher. These are inert fixture properties, not native lifetime
proofs. New tests must run alongside the accepted681 unique tests.

Reviewer tests must use actual new inert-runtime transcripts plus adversarial
mutations: missing/duplicate/extra name fields, wrong sentinel, label/name
contradiction, oversize and non-ASCII name, integer/budget/counter mismatch,
truncated EVENT/STOP/OUTCOME, final newline absence, epoch/restart/order errors,
trailing TIME/CLOCK/removal tails and later retry history. Demonstrate that
the immutable real v16 capture still returns its full frozen report under
the original reviewer and is rejected as v17 evidence by the new one.

## Privacy and later task boundaries

A validated Name is a game-supplied simple identifier. It excludes spaces,
slashes, dots, quotes and separators, which prevents path and line injection;
that alphabet is not a universal assurance that a modded identifier contains
no personal text. Do not collect definition paths, addresses, object repr,
arbitrary fields, SDK source copies or extracted game assets. The surrounding
raw SDK log may still contain startup details and installation/object paths.
Any future full capture must be privately preserved, reviewed against its
exact contents and separately approved before public export, as before.

Later bounded tasks, after this design's publication and required review:

1. Implement v17 on its own branch: current runtime/version/package README,
   new name-reader tests, necessary existing control/factory/package tests,
   package verifier, new instructions/checks and one uniquely versioned ZIP
   plus default ZIP. Refine actual filenames before claim. Preserve all210
   accepted base files outside confirmed scope and all16 original ZIPs; never
   rebuild a versioned ZIP. Verify source/ZIP/CRC/layout/AST and meaningful
   inert tests before concrete exact-file publication approval and review.
2. Implement the separate strict v17 reviewer/test/doc/check files on its own
   dependent branch, preserving v16 parser and all frozen capture reports.
   Reproduce new runtime transcript behavior and adversarial closures before
   publication approval and review.
3. Prepare an exact-build owner diagnostic only after both are accepted.
   Instructions must name main-menu/map locations, verify Offline/Gaige/title,
   use no ARM, enter the map, START22 once, a separately approved ordinary
   Deathtrap use once/natural end within a bounded interval, STOP23/CANCEL3
   in-map and full desktop exit before preservation. This is a prospective
   shape, not a request to run now. A refusal/unavailable skill/time bound or
   silence is preserved without retry. No buying/respec/travel/manual boost/
   other trace. Explicit approval of the new ZIP/version and exact gameplay
   protocol is still required. Then preserve unique raw log/manifest/three
   installed snapshots and request approval of that exact public payload.
4. Assess actual new identifier records against source and package provenance,
   keeping owner natural-end/actions/timing separate. Do not change routing
   or call an effect ready from a Name match. Any later matcher or additional
   access proposal needs actual evidence and its own task/review.

All original effect task dependencies stay intact. Manager ownership, unique
active instance, allocation/summon generation and later liveness, engine clock/
Duration consumption, purchased rank-one eligibility and exact-original
write/readback/cleanup remain NOT_READY. PRE reports attempted entry even if
another hook blocks native execution. Keep the
[identity/cleanup contract](overclock_identity_cleanup_contract.md), existing
grade-zero diagnostic guard and separate manual Duration restoration. CANCEL/
disable do not invoke that manual restore or repair points/saves.

## Actual design checks

The companion JSON records actual source AST and frozen fingerprints, the
existing one Name/two parameter getter route, corrected v16 full-report/
manifest equality, raw observed event and timing/provenance limits, all210
accepted Git blobs and16original ZIPs unchanged, immutable53/12/5 inventory
and all frozen fullv12-v16 report/snapshot relationships. A scratch stdlib
grammar probe measures proposed line sizes and positive/adversarial name
branches; it is design validation, not a delivered v17 runtime/reviewer.
UTF8/JSON/links/exactscope/whitespace and known secret/private-path scans pass.

The accepted681 suite and hosted CI are not repeated for two design files.
No real SDK/stub import/execution/compilation, new payload reader execution,
native invocation/flag or gameplay write, installation/game/save/private-backup
access, purchase/summon/effect, outgoing support message, merge or release
occurs. Public export of these two new files requires its own exact owner
approval; the accepted assessment publication approval is fulfilled by PR35.
