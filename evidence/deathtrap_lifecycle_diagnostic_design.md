# Bounded manager-owner metadata correction

Decision: **READY_FOR_METADATA_OWNER_CORRECTION** in a separately claimed
v0.2.13 implementation. **NOT_READY_FOR_PASSIVE_LIFECYCLE_OR_EFFECT**.
This historical lifecycle-design filename contains a synchronous metadata
design only. No lifecycle observer, manager instance or active summon is part
of the proposed build. [Actual design checks](deathtrap_lifecycle_design_checks.json)
record the source hashes and checks performed for this decision.

## Inputs and established facts

The accepted cumulative base is `8813aef6a0a0d1f5759dcab10c582d20d081b307`
([PR14](https://github.com/Edge916/The-Ultimate-Borderlands/pull/14)).
Read the actual [v12 result](v032_live_deathtrap_metadata_result.md),
[raw log](v032_user_test.log), [capture manifest](v032_capture_manifest.json)
and [tested runtime](../archive/tested_runtime/v0.2.12/__init__.py).
The raw log SHA256 is
`8ddbb6aeae5d96be14879adf69fd21c6a7a1fcdbd3e55ec5f4199b2f943f520a`;
runtime SHA256 is
`41fd2dd9e22bcfa64fbddfc19b881f6950362656e047b212b00eb86f33a01f73`;
capture-manifest SHA256 is
`6121c698c1beb85884c69468262c131d27017e885cb8729250c3c5344190db01`.

Two v12 calls at lines 65–82 and 83–100 contain identical 15 metadata rows.
GetSkillManager was found on the current controller class; its typed return
descriptor declares WillowGame.SkillEffectManager. ActiveSkills on that class
has a typed object-property inner declaring WillowGame.Skill. Four class roots
and all seven selected fields had COMPLETE coverage. ActivateSkill and
DeactivateSkill were UNAVAILABLE in the controller lookup. The current
runtime queries all three names on the controller; it never queries those two
names on the returned manager class. Their presence, owner and schema there
remain unknown. A missing lookup is not proof of absence elsewhere.

FINAL points=(1,0), ranks=(0,0,0) asserts equality to an internal, unlogged
initial baseline. It is not an independently reconstructed state comparison.
Metadata END reports zero added observers/native calls/writes. Separate armed
initialization inserted the inert node. CANCEL restored native arrays, all
four observer families reached zero, and the capture recorded independent
process-exit and installed/original-package equality checks. Two inspections
occurred despite the requested one; preserve that deviation and the refused
second ARM/repeated CANCEL.

## SDK evidence and its limits

Installed SDK stubs were read as text only and hashed; they were never executed,
imported or packaged. Their API declares UClass as a UStruct subclass,
`UStruct._find(name)` for a child descriptor, `_find_prop(name)` for properties,
`UFunction._find_return_param()`, `ZObjectProperty.PropertyClass` and
`ZArrayProperty.Inner`. The actual size member is `ParamsSize`.
There is no `_find_func` API in the inspected declarations.

Pinned [reflection bindings](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/uobject_children.cpp)
expose `_find` through the native structure's field search, including typed
result wrapping and a missing-field exception; they also expose the property
and function metadata members used by the existing helpers. This supports
bounded descriptor lookup on an already verified manager UClass. It does not
establish a BL2 lifecycle owner, callable signature or instance lifetime.

Pinned [bound-function bindings](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/bound_function.cpp)
implement native invocation through the callable wrapper. Lookup is not
invocation; this design permits no BoundFunction call.
The [hook contract](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/hook_manager.h)
and [Python hook bindings](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/hook.cpp)
distinguish POST from POST_UNCONDITIONAL: the latter may run for a blocked call.
Copied arguments are not the native argument storage, an args ReturnValue
need not be correct, and callback `ret` may include another hook's override.
Callback order is not guaranteed. No hook is proposed here.

## Selected lookup and data contract

Reuse the existing ten `_deathtrap_*` helpers and `_DEATHTRAP_FIELDS`
unchanged. Refactor only `inspect_deathtrap_readiness` to collect:

1. The current verified controller class/ancestry and GetSkillManager descriptor
   selected with `_find` on that class.
2. The actual typed ZObjectProperty return descriptor's PropertyClass as the
   manager root, after the existing function header/property/link/return checks.
3. ActivateSkill and DeactivateSkill, selected with `_find` on that exact
   manager root and validated against its bounded ancestry. These are search
   candidates, not assumed methods or native hook paths.
4. ActiveSkills, its actual typed inner class, and the existing six Skill fields;
   Definition supplies the fourth root and must equal the classes of the three
   current owned definitions.

For a valid descriptor, retain actual SDK type, exact label, canonical bounded
path, exact declaring owner in the selected root's captured ancestry, header
numbers, property ownership, links, offset/size/dimension bounds and return
flag/offset agreement. A same-name descriptor outside that ancestry refuses.
A descriptor inherited from a verified ancestor is permitted only with its
actual matching owner/path; an unsupported function SuperField remains
UNAVAILABLE. Do not hardcode WillowGame.SkillEffectManager:ActivateSkill or
any other unobserved native path. Do not fall back to controller behavior
functions, unrelated same-name classes, global find_object/find_all, loads,
construction, manager instance acquisition or `pc.GetSkillManager()`.

Permitted payload consists of metadata and the existing owned session/state
reads. No manager/ActiveSkills/Duration/ActivatedTime/instigator/modifier payload,
native formatter/query, pointer conversion, unknown repr/string/equality,
copied effects, argument/return overrides or gameplay write is added.

## Guard, bounds and failure handling

Preserve `_upgrade_state` as the grade-zero diagnostic gate: exact current
owned controller/Gaige/tree/pawn/world/PRI/definition references, supported
named solo mode and both sole-player rosters, inert owned initialization,
bounded runtime arrays, unchanged points/ranks/indices/tier baseline.
Rank one or unavailable state refuses; this guard is not a future effect gate.
Preserve the manual duration prototype, insertion/rollback and shutdown/CANCEL.

Reuse `_deathtrap_session` and `_deathtrap_check`: revalidate before/after
captured getters, after enumeration, around output and before FINAL/END.
Refuse armed initialization, all live observer contexts, registered hooks or
failed-removal hooks retained for retry. New diagnostics retain no context and
register no hooks/timers. Existing observer cleanup still clears its context
before removing hooks and retains failed removals inert for explicit retry;
this metadata correction needs no new cleanup family or changes to that code.

Per collection: at most four distinct roots, eight ancestry nodes per root,
three distinct selected function targets, seven field targets, sixteen accepted
properties plus one cap lookahead per function, and fifteen metadata rows.
Names have at most 96 characters and paths 384. Existing exact-integer metadata
bounds remain unchanged. Captured revalidation entries have an upper bound of
94: 32 ancestry entries + controller-Class entry + 3 headers + 48 properties
+ 7 fields + 3 owned-definition-Class entries. This is a bound on selected
targets and captured checks, not a claim of only three raw `_find` calls:
revalidation repeats bounded getter calls. There are zero observer callback
attempts/events, zero timers and no retained collection state. SDK getter
latency is outside Python's control; finite loops do not promise a hard wall
clock deadline. No timeout thread or forced native call is introduced.

Initial supported lookup/getter failure produces UNAVAILABLE while guards
still pass. Malformed, untyped, foreign, cyclic or changing metadata/state
produces ABORT coverage=REFUSED before another target/output. CAPPED ancestry
or properties is explicit and never complete; retain the existing overall
CAPPED precedence over UNAVAILABLE. A metadata failure never repairs points,
ranks, arrays, saves or native references.

If GetSkillManager has no accepted typed return, emit unavailable manager
DISCOVERY and stop dependent discovery. Do not fabricate manager function
rows for lookups that were never attempted. A wrongly typed accepted return
refuses. If either manager function is unavailable, continue existing field
discovery under all guards. If ActiveSkills is unavailable, no Skill/Definition
root or their fields are fabricated. Missing individual fields remain explicit;
a missing Definition has no Definition class row. FINAL/END still require
successful full state/metadata revalidation.

## Versioned output and offline reviewer

Proposed title: `UVH v0.2.13 - DEATHTRAP MANAGER METADATA`; version `0.2.13`.
Keep nineteen options and item4 callback; its label states manager metadata.
Keep the existing JSON row schemas and UVH-DEATHTRAP prefix, using a v0.2.13
BEGIN. The complete row order becomes:

| Position | Row | Verified root for lookup/ownership |
| --- | --- | --- |
| 1 | controller CLASS | Current controller Class |
| 2 | GetSkillManager FUNCTION | Controller ancestry |
| 3–4 | manager CLASS, DISCOVERY | Accepted return PropertyClass |
| 5–6 | ActivateSkill, DeactivateSkill FUNCTION | Manager ancestry |
| 7–8 | active_skill_class CLASS, ActiveSkills FIELD | Manager array's inner class |
| 9–12 | Duration, DurationBaseValue, ActivatedTime, SkillInstigator FIELD | Skill ancestry; instigator declared class in controller ancestry |
| 13–14 | definition_class CLASS, Definition FIELD | Exact classes of the three owned definitions |
| 15 | DurationModifierStack FIELD | Skill ancestry |

Optional unavailable branches omit unattempted descendants as above. Both
versions must enforce their actual sequence and relations; v12's controller
function order/owner rule cannot be silently reused for v13.
Extend `review_deathtrap_metadata_log.py` with separate v12/v13 contracts and
actual runtime hash pins after the new runtime is built. Preserve v12 behavior
and its 46 existing tests, including the actual frozen v12 PARTIAL/exit1 result.
Validate v13's controller primary and manager candidate ownership separately.
Reject mixed-version/mismatched-order/foreign-owner rows and contradictory
discovery. Preserve strict keys/numbers/duplicate-key/input bounds, CAPPED and
UNAVAILABLE outcomes, cleanup failure history, unlogged initial baseline and
separate NOT_CHECKED claims. Never upgrade parser text consistency to SDK
identity, native signature, log origin, install or process-exit proof.

## Exact later implementation scopes and acceptance

Refine implementation task `6c2e567d-28fa-4541-82b1-8f6a73e8b2b6` before
claiming; retain its design dependency. Use a separate branch based on the
accepted design commit. Proposed exact changed paths:

- `sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py`
- `sdk_mods/UltimateVaultHunterDeathtrapBoost/pyproject.toml`
- `sdk_mods/UltimateVaultHunterDeathtrapBoost/README.txt`
- `tests/test_deathtrap_readiness.py`
- `tests/test_runtime_mock.py`
- `tests/test_presentations.py`
- `scripts/review_deathtrap_metadata_log.py`
- `tests/test_deathtrap_metadata_log_review.py`
- `evidence/deathtrap_manager_metadata_implementation_checks.json`
- `docs/NEXT_CODEX_TASK.md`
- `dist/UltimateVaultHunterDeathtrapBoost_folder_install.zip`
- `dist/UltimateVaultHunterDeathtrapBoost_v0.2.13_folder_install.zip`

Update the existing metadata fixture/tests rather than the nonexistent queued
lifecycle test. Preserve assertions for all existing failure guards, add
manager-only availability with a poisoned controller fallback, exact manager
ancestor/foreign owner, manager identity/header drift, missing primary without
dependent lookups, and missing manager function with valid field continuation.
Use inert fake SDK types and invocation/payload/discovery/write/hook poison.
Add v13 reviewer fixtures for complete/partial/refused/capped and malformed
owner/order/return relations, unavailable discovery without unattempted rows,
mixed versions and cleanup failure after retry. Existing v12 fixtures remain
valid and the actual v12 report remains unchanged.

Run the full unique offline suite, syntax, exact limited AST proof and package
CRC/layout/source/inert import. Preserve all 95 existing function ASTs except
the diagnostic orchestration; all ten helpers and every manual/insertion/
rollback/observer/cleanup/state function stay identical. Factory/title/version/
item4 label and pyproject are the other permitted runtime integrations.
Create the new versioned three-file ZIP exclusively. Preserve all twelve
original versioned ZIPs, all historical captures/snapshots/designs/reviewers and
the static inventory. Its explicit current check will report intended current
fingerprint drift; check new current package equality separately. Do not alter
historical hashes to force a pass.

After implementation review, refine capture task
`8649d701-5626-4dc3-8025-d538c1f7a99b` to a v13 metadata capture with the same
dependency, exact title/package and new exclusive paths
`evidence/deathtrap_manager_metadata_user_test.log`,
`evidence/deathtrap_manager_metadata_capture_manifest.json` and
`archive/tested_runtime/v0.2.13`. Remove natural-summon assumptions from that
task's description/acceptance. A separately approved owner protocol may use
ARM1, item4 once, CANCEL3 and full exit; this design starts no game test.
Any approved publication must expose only the prepared scoped project result.

## Remaining readiness and checks not performed

Even complete manager descriptor metadata establishes no natural event order,
native instance ownership/lifetime, clock semantics, payload values, stable
summon identity, cleanup write timing, rank-one gate or automatic +15-second
effect. Passive lifecycle investigation needs a new reviewed contract and
actual function schema/owner evidence; effects need separately authorized
design and gameplay-writing scope. Missing descriptors are a valid next result.

This task changes exactly this design and its JSON checks. It builds no v13
runtime/package, installs nothing and performs no game/native-SDK run,
save/private-backup access, purchase/respec/travel/summon/manual boost, observer
experiment, effect, co-op, merge or release. The unchanged full 401-test suite
and hosted matrix were not repeated for this design. Fresh targeted v12 mocks,
actual frozen-log CLI, text/hash/AST/base-scope checks and immutable provenance
verification are reported as offline evidence only.
