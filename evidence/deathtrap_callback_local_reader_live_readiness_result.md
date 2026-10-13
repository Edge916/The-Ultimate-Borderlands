# v0.2.16 callback-local reader: live assessment

**OBSERVED_FILTERED. NOT_READY_FOR_NATIVE_EFFECT_DESIGN.** The capture adds
one schema-valid PRE event with `SAME_WRAPPER/OTHER_NAME`. This is a live
primitive classification where the v15 passive capture had zero attempts.
No `DEATHTRAP_NAME` event was recorded. The owner reports that Deathtrap ended
naturally; the captured event cannot yet be attributed to that summon.

Accepted capture: `27ca755086ef705a0ac0baa954213af394c9037e` /
[draft PR #34](https://github.com/Edge916/The-Ultimate-Borderlands/pull/34).
Runtime: `b51f91ff28ece47fc28ca91eef6f12cc305f8c8b` /
[PR #32](https://github.com/Edge916/The-Ultimate-Borderlands/pull/32).
Corrected strict reviewer: `9f5646d8bd5f37661a94cb6d94a0f96660dc006c` /
[PR #33](https://github.com/Edge916/The-Ultimate-Borderlands/pull/33).
These accepted draft branches are unmerged. Read the
[checks](deathtrap_callback_local_reader_live_readiness_checks.json),
[full raw log](deathtrap_callback_local_reader_user_test.log) and
[capture manifest](deathtrap_callback_local_reader_capture_manifest.json).

## Evidence and its limits

The preserved log has 80 lines / 13,802 bytes, SHA-256
`0c16ddf9dd0c46459fec53599b9685f4f2e3f6e5c263977be99cfaddb13b5fdc`.
Fresh strict review returns `COMPLETE_LOG_TEXT`, exit 0, with zero issues;
the entire result equals the manifest's report. This checks transcript
consistency. Process exit, installation and owner actions require the
separate provenance below.

| Log lines | Recorded evidence | Limit |
| --- | --- | --- |
| 24 | One accepting START, version 0.2.16, epoch 1, DeactivateSkill PRE, one hook. | Registration text does not identify a Deathtrap instance. |
| 25 | `NOT_STARTED reason=OVERLAP`. | START and several guarded controls emit this label; the triggering control and operator clicks are unknown. |
| 26 | One event: `schema=VALID`, `SAME_WRAPPER/OTHER_NAME`, ownership unestablished, 196 operations, stages 58/50/36/52. | Schema and counters are runtime assertions. The supplied definition's actual Name is not logged. |
| 27-32, 56-57 | Four STOP/OUTCOME pairs: one attempt/classification/filter, zero unresolved or uncertain handles, errors, refusals, reentry and cleanup failures; `OBSERVED_FILTERED`, limit NONE. | CANCEL and disable also call STOP; four pairs do not prove four manual STOP clicks. The overlap refusal remains separately recorded. |
| 33, 44, 46, 54; 58, 69, 71, 79 | STATE, UI, UPGRADE and INITNODE cleanup report remaining zero. | These are runtime handle assertions, not native-object or Duration restoration. |
| 55, 80 | DISARMED, no initialization patch to restore. | No ARM or insertion marker appears. This standalone protocol requires no node insertion, point/rank baseline or array rollback. |

There are no project ERROR or traceback markers in this log. Line 23 contains
a deprecated legacy-import compatibility warning. The owner supplied no
separate visible-failure statement, so an absence of visible errors is not
asserted. No passive-observer or metadata-inspection markers appear.

The owner explicitly approved this exact build and the location-specific
protocol, then reported: `deathtrap ended naturally and i stop 23 and cancel 3
and full exit`. The agent did not observe the menu title, map, action-skill
presses, summon count, natural end, waiting interval or before-test process.
Those details must not be manufactured from the event timestamp.

SDK header intervals are 64.640 seconds from START to EVENT, 76.070 seconds
to the first STOP and 84.229 seconds to the final STOP. They lie within the
proposed approximately 90-second bound, but they are not an independently
measured owner wait, an engine clock or Deathtrap lifespan. The runtime's
120-second limit uses monotonic time checked on operations and controls;
it has no background timer. No TIME or count limit occurred in this transcript.

Capture-time process queries found BL2 absent before and after preservation.
The complete log and three installed project files were stable across double
reads and rereads after exclusive copying. Installed files, frozen
[v16 snapshots](../archive/tested_runtime/v0.2.16/__init__.py), accepted runtime
source and the original v16 ZIP are byte identical. The ZIP is 44,901 bytes,
SHA-256 `f80114f0b395edc6b5a35edbfa000c5573337359fe44a477be20b88f83a29d85`,
with clean CRC and exactly three files in one folder. These are preserved
provenance checks; this assessment performs no new game run or installation.

## What OTHER_NAME means in the actual source

The accepted [runtime](../sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py)
uses fresh loaded class/function/property checks in `_cr_inspect`. It obtains
SkillInstigator first. Definition is not read for null, foreign-class or
foreign-wrapper cases. For `SAME_WRAPPER`, `_cr_solo` checks typed player
objects, Mechromancer class, named Standalone/ListenServer mode and both
one-entry owned rosters, then rechecks the current player/session.

For a non-null, exact-class SkillDefinition, the reader obtains Name once,
requires an exact Python string of 1..128 identifier characters and compares
it to the literal `Skill_DeathTrap`. Equality gives `DEATHTRAP_NAME`; every
other accepted string gives `OTHER_NAME`. Only this fixed label leaves the
inspection frame. The supplied string, asset path and native definition are
absent from the log and reader state.

The live event therefore exercises the nominal classification path according
to the runtime's assertions. It does not establish which other identifier
was supplied, why the event happened, whether it belonged to Deathtrap or
whether the native deactivation completed. The log cannot distinguish an
unrelated skill event from a different identifier used by the relevant
definition. These possibilities are unresolved; neither justifies changing
the literal or declaring the guard defective. No additional event is claimed
to have been lost, blocked or suppressed.

Fresh source/AST checks confirm that this reader does not access ret,
bIgnoreSkillInstigator payload, ActiveSkills, Grade, ActivatedTime, Duration,
point/rank/save state or a definition asset path. Native function metadata
inspection and hook registration/removal are separate from calling the
engine's GetSkillManager/ActivateSkill/DeactivateSkill methods; the reader
makes no such method call or gameplay/flag assignment. Inspection returns
primitive labels/counts; the callback drops payload locals before reporting
and returns exact None. Its closure captures epoch only. These source checks
and the earlier inert tests are not a native lifetime proof.

The full current [SDK discussion](https://github.com/bl-sdk/pyunrealsdk/issues/97#issuecomment-6108546422)
still contains one contributor reply: hook execution blocks the UnrealScript
VM and prevents GC during that interval, while Python references do not
preserve native objects afterward. That guidance does not certify already
invalid inputs, explicit destruction, installed binary equivalence or
later exact-original access. Existing SDK helper globals are still disclosed
in the accepted [reader design](../docs/deathtrap_callback_local_reader_design.md).
No SDK source, stub or binary was executed in this assessment.

## Remaining native prerequisites

| Required fact | Current evidence | Decision |
| --- | --- | --- |
| Natural attempted PRE entry and nominal parameter classification | One accepted SAME_WRAPPER/OTHER_NAME event in the transcript. | Observed text assertion; no successful native deactivation proof. |
| Definition identifier and association with the owner's Deathtrap use | Actual Name is intentionally suppressed; owner natural-end report is separate. | NOT_READY for Deathtrap attribution. |
| Exact manager ownership and unique active instance | Manager type/link and current instigator wrapper only; no owned-manager relationship or active-instance membership. | NOT_READY. |
| Allocation/summon generation and later liveness | Callback epoch controls observer reuse; no native generation, address-reuse or post-return retention contract. | NOT_READY. |
| Skill clock, Duration consumption and safe write/readback phase | No ActivatedTime, Duration or modifiers read. SDK header and monotonic limits are separate. | NOT_READY. |
| Purchased Overclock rank-one gate | No rank/point reads in this diagnostic; historical purchase report remains separate. | NOT_READY; preserve the existing grade-zero guard. |
| Cleanup on the exact still-live original after a Duration write | Hook cleanup only. Manual restore is an independent prototype. | NOT_READY. |
| Complete native adapter and purchased-node effect | The prerequisites above are unresolved. | NOT_READY_FOR_NATIVE_EFFECT_DESIGN. |

PRE means attempted entry even if another hook blocks native execution.
Neither SAME_WRAPPER, a definition name, an observer epoch nor a passing mock
token substitutes for owned-manager, unique instance or native generation
evidence. Keep the [exact-original cleanup contract](../docs/overclock_identity_cleanup_contract.md)
and original effect-task dependencies intact. CANCEL/disable do not invoke
manual Duration restore, and hook cleanup cannot refund points or restore saves.

## Next bounded task

Design a callback-local **Definition.Name diagnostic**, limited to resolving
the identifier hidden by OTHER_NAME. Prospective design files are
`docs/deathtrap_callback_definition_name_design.md` and
`evidence/deathtrap_callback_definition_name_design_checks.json`, on a separate
claimed branch after this assessment is accepted. They are a proposal, not
new implementation or gameplay authorization.

The design must retain the existing schema, instigator, solo-session,
class, reentry, operation/time/output limits and no-native-reference-escape
checks. Evaluate whether the already read Name can be emitted as one bounded,
validated primitive identifier after native locals are released. Specify an
exact versioned grammar, privacy/export treatment and strict reviewer cases
for long, malformed, missing, null, foreign, changing and truncated records.
Do not add another payload getter, asset path traversal, arbitrary enumeration,
activation/POST observer, engine invocation, active-skill scan or gameplay write
to answer this narrower question. Do not replace the current fixed matcher
until actual identifier evidence has been separately reviewed.

A later implementation and reviewer need their own scopes, meaningful tests,
immutable versioned package and deliberate review. Any new owner test needs
explicit approval of its exact build and location-specific bounded protocol.
Another capture with the same fixed labels cannot resolve the omitted Name;
do not repeat v16 to chase a preferred event. Even an eventual Deathtrap-name
match would leave the manager, unique instance, generation, clock, rank-one
and exact-original cleanup gates unresolved. No additional SDK support message
is proposed or sent.

## Actual checks

The companion JSON records the fresh full v16 CLI/manifest comparison,
independent raw counters/timestamps, source AST/ranges and fingerprints,
source/snapshot/original-ZIP equality, all 208 accepted Git blobs, all 16
original ZIP layouts/CRCs, immutable inventory 53/12/5 and frozen full v12-v15
reports/snapshot relationships. UTF-8, JSON, local links, exact two-file scope
and known secret/private-path checks are included.

The accepted 681-test suite and hosted CI are not repeated for two evidence
files with unchanged code. No native SDK import/execution/stub compilation,
agent game action/installation, native engine call/flag write, save/private
backup access, purchase/respec/travel/summon/boost/effect, outgoing support
message, merge or release occurs. Public export of these two new assessment
files requires its own scoped approval; the five-file capture approval is
already fulfilled by PR34.
