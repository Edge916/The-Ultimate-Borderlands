# v0.2.17 callback definition names: prepared implementation

**OFFLINE VALIDATION ONLY. NOT TESTED IN GAME.** Implements the accepted
[Definition.Name design](deathtrap_callback_definition_name_design.md),
commit `306c2453aecd1b5a59f379cca512e46e9f05b1b1` /
[draft PR 36](https://github.com/Edge916/The-Ultimate-Borderlands/pull/36).
The [checks](../evidence/deathtrap_callback_definition_name_implementation_checks.json)
record actual validation, fingerprints and preserved evidence.

The [v16 assessment](../evidence/deathtrap_callback_local_reader_live_readiness_result.md)
reported one SAME_WRAPPER/OTHER_NAME PRE event without the supplied name.
The owner's natural Deathtrap end remains a separate observation. This
implementation makes that existing Name read visible as a bounded primitive;
it cannot recover the old identifier or resolve native ownership/effect gates.
Do not repeat v16 or change the matcher from its filtered result.

## Runtime change

The prepared title is `UVH v0.2.17 - CALLBACK DEFINITION NAMES`.
Controls22/23 start and stop the same standalone one-hook DeactivateSkill PRE
reader, without ARM or node insertion. The new fixed registration identifier
is `UVH_CALLBACK_NAME_V17_DEACTIVATE_PRE`; the path and phase are unchanged.
All23 options remain, with updated labels for those two reader controls.

The new `[UVH-CALLBACK-NAME]` prefix and START version0.2.17 distinguish this
format. EVENT inserts `name=<token>` between definition and ownership.
For a validated non-null SAME_WRAPPER definition, the token is the existing
single Name getter's exact ASCII string of1..128 letters/digits/underscore.
The other four null/foreign/unread branches use `-`, which is not an identifier.
Invalid values refuse without clipping, repr, path or exception output.
Only exact case-sensitive Skill_DeathTrap still gives DEATHTRAP_NAME; every
other valid string remains OTHER_NAME. No alias, suffix or case heuristic.

Inspection carries that string only after the current final guards pass.
Its frame dies, the callback's obj/args/func/ret locals are dropped, and only
then is a primitive EVENT assembled. Stops/clock refusals clear the token;
failure/control records have no Name field. There is no Name history cache,
native reference ledger or added SDK getter. The observer closes over epoch
only and returns exact None. Existing SDK helper/conversion limitations remain.

Schema checks, instigator-first access, foreign/null unread Definition,
fresh solo Gaige/controller/rosters and final-session checks are unchanged.
The same operation, reentry, overlap, time, registration ownership/uncertainty,
busy-stop deferral and failed-removal history rules remain. Historical
insertion/rollback, grade-zero diagnostic guard and manual Duration functions
are unchanged; CANCEL/disable do not invoke manual Duration restore.

| Branch | Stages | Total |
| --- | --- | ---: |
| Null instigator | 58,49,0,0 | 107 |
| Other controller class | 58,50,0,0 | 108 |
| Other controller wrapper | 58,50,1,0 | 109 |
| Same wrapper, null definition | 58,50,36,50 | 194 |
| Same wrapper, other name | 58,50,36,52 | 196 |
| Same wrapper, exact Deathtrap name | 58,50,36,52 | 196 |

Actual inert transcripts verify these reader-issued counts, one Definition
Name read on each accepted non-null local callback and no foreign Definition
read. SDK internals are outside this counter. The existing384-byte encoded
project-line guard remains; the longest actual EVENT is320 bytes, including
the complete project prefix and a128-character Name. A real24-event inert
session reaches that bound and cleans up at the event limit. There is still
one PRE hook,64-attempt/24-classification/120-second bounds and four64-operation
stages, with no background timer.

## Tests and preservation

Nineteen new independent tests exercise all six actual branches/counts, every
allowed ASCII character,1/128 boundaries, invalid lengths/types/subclasses/
Unicode/path/line injection, sentinel collisions, exact literal/case/suffix
behavior, stop/time/session changes during or just after the Name read,
exception lifetime, primitive-only emission after native locals drop, distinct
successive Names without a state cache, cleanup retry/history, logging failure,
the longest record/event limit and the unchanged getter/closure/None boundaries.
These are fixture properties, not a native lifetime or owner test.

The accepted681 unique tests remain in the full run, with current version and
EVENT-format expectations updated where necessary. The seven v16 reviewer
fixture sites now explicitly run the unchanged tested
[v16 runtime snapshot](../archive/tested_runtime/v0.2.16/__init__.py), using the
existing inert harness. Their expected transcripts, adversarial assertions
and corrected parser are unchanged. This prevents a version change from
silently reinterpreting accepted v16 evidence. The new independent tests do
not inherit or duplicate the43 established reader tests.

The companion checks record the full offline run, source syntax/AST boundary
comparison, frozen fullv12-v16 report/manifest equality, snapshot/original-ZIP
relationships, immutable53/12/5 inventory and all accepted files outside the
confirmed scope. All16 prior original versionedZIPs remain byte identical.
No raw capture, manifest, tested snapshot or historical fingerprint is edited.
Hosted CI and native behavior remain unverified.

The default package is byte identical to the exclusively created new
[v17 original ZIP](../dist/UltimateVaultHunterDeathtrapBoost_v0.2.17_folder_install.zip),
which contains exactly one folder with __init__.py,pyproject.toml,README.txt.
CRC/source/layout checks and a separate isolated inert import verify title,
version,23 options, prefix/registration identifier and no import-time game
access or new hook. Freeze this versioned ZIP; never rebuild an original ZIP.

## Next review and owner instructions

First publish the exact implementation payload after scoped owner approval,
then record deliberate acceptance review. A **separate strict v17 log reviewer**
must implement the accepted name/classification grammar, bounded identifier
JSON and corrected trailing-control/cleanup history rules before any owner
diagnostic. The unchanged v16 parser rejects this new format and is not a
substitute. There is no owner test approval for this new build yet.

Later instructions must identify locations and exact reviewed ZIP/commit.
With BL2 fully closed, the owner would install only after approval. At the
main menu, verify Offline, Gaige and the exact v17 title, without ARM. Select
Continue and fully load into the map. In-map select START22 once. A single
ordinary Deathtrap use and natural end within an explicit bound would require
separate gameplay approval; then STOP23 and CANCEL3 in-map, followed by full
exit to desktop before preservation/relaunch. This is a prospective layout,
not a request to run now. Refusal/unavailable skill/time bound/silence is
preserved without retry. No buying, respec, travel, manual boost or other trace.

Names are simple game identifiers, not asset paths, pointer identities or
summon generations. The allowed alphabet prevents path and line injection;
it cannot universally exclude personal text in a modded identifier. Future
raw SDK logs may still include installation/object paths and startup details;
preserve and review exact files before separate public export approval.

All native manager ownership, unique active instance, generation/later
liveness, engine clock/Duration consumption, purchased rank-one and
exact-original write/readback/cleanup gates remain NOT_READY. Keep original
effect dependencies intact. PRE is attempted entry, including when another
hook blocks execution; a Name match cannot establish deactivation or lifespan.
No real SDK/stub execution/compilation, native engine invocation/flag/write,
installation/game/save/private-backup/purchase/summon/effect/support message,
merge or release occurs in this implementation task.
