# Overclock effect readiness: independent research

The visible Overclock node remains inert. The manual +15-second prototype is a separate, explicitly invoked experiment; it is not ready to become a purchased-node effect. The next useful implementation is a bounded metadata-only Deathtrap diagnostic. No runtime change or additional game test is part of this research.

Reviewed baseline: `3af92a893cce1a4db6850e1270be3d2c78244497` ([PR #1](https://github.com/Edge916/The-Ultimate-Borderlands/pull/1)). All code line references below are in `sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py` at that commit. The two new research files preserve all 112 existing tracked files byte for byte. The JSON companion records hashes, source ranges, the complete reproducible inert probe program and its results.

## Evidence and limits

The retained [v0.1.1 log](v011_duration_write_verified.log), lines 28–35, records a live `Skill_DeathTrap` Duration write 60→75, base 60 and a refused repeated application. The user reported a longer lifespan, without stopwatch measurement. `Grade=1` on that active Deathtrap is not Overclock's runtime rank. This log contains no explicit successful restore record; explicit restoration is covered by the established mock, not established by this particular live log.

The independently accepted [v0.2.11 capture](https://github.com/Edge916/The-Ultimate-Borderlands/pull/3), commit `88a904e83babc1d85566d47f382cc32dfda89a8b`, contains two complete Attribute metadata calls with Overclock rank zero. The captured Myelin object has the runtime-verified derived UClass `ResourcePoolAttributeDefinition`. That resolves the previously refused wrapper's metadata; it does not validate a Deathtrap lifecycle, make the old exact-class Attribute guard interchangeable, or authorize gameplay writes. Justin's corrected offline reviewer is independently accepted at `44ad64cfde74807b01a20f17c0775c6122b75e15` ([PR #2](https://github.com/Edge916/The-Ultimate-Borderlands/pull/2)). Its text consistency checks do not establish SDK identity or machine exit/install proof.

The earlier user-reported Overclock purchase to 1/1 is UI evidence from another process. The retained restarted logs have one unspent point and rank zero. There is no captured first-run transaction, save audit, purchased effect or repeat-purchase requirement.

## Requirements and present gaps

| Requirement | Actual implementation/evidence | Remaining prerequisite |
| --- | --- | --- |
| Purchased-node rank | `_upgrade_state` lines 1636–1700 validates unique owned entries and explicitly requires Overclock grade **zero** at line 1695. Manual `apply` never reads the node. | A separately designed effect gate for the exact owned Overclock definition and rank. Preserve the existing grade-zero diagnostic guard. |
| Live Deathtrap identity | `find_live` lines 46–79 checks Gaige/action/definition names; line 60 invokes `pc.GetSkillManager()`. It scans at most 64 entries and accepts the first matching definition with an instigator name equal to the controller name. | Validate actual typed objects and exact current controller/world/definition ownership; reject ambiguous matches. Do not treat this helper as a passive metadata read. |
| Per-summon record | `signature` lines 41–43 stores skill name, unchecked ActivatedTime and instigator name; `apply` records that signature plus before/after values. | Exact validated identity and lifetime strategy. A missing time or reused signature must not identify another summon. SDK wrapper/lifetime behavior still requires evidence. |
| Anti-stacking | The current record stops a repeat, and nondefault Duration also refuses a second write if the record is lost. | Reentrant/later lifecycle callbacks need a separately verified once-per-owned-summon ledger. Lost state prevents undo even when it prevents stacking. |
| Timing | Current tree hooks concern tree initialization/UI/state queries. The 21 retained baseline logs contain only four matching ActivateSkill/DeactivateSkill/GetSkillManager **field inventory** lines, all in v0.1.9. | Loaded function metadata and actual natural summon timing/ownership. Inventory names provide no signature, hook phase or successful lifecycle callback proof. |
| Modifiers and values | `apply` lines 132–145 requires finite exact numeric Duration/base approximately 60, an accessible empty modifier stack, and the duration cap. | Retain these refusals. Define validation/rechecks for an automatic path without assuming the engine consumes late writes or recomputes duration. |
| Points, ranks and saves | The manual path only assigns live Duration; the newer diagnostic guard separately freezes points/ranks/indices/tier/session. No code can refund a transaction or undo a save. | Separate read-only rank verification from any future effect. No point/grade/save repair or save persistence claim. |
| Cancel/disable | `restore` lines 169–197 is a separate manual option. `cancel_init_node` lines 1379–1391 cleans observers/native arrays. `shutdown` lines 2974–2976 calls trace stop and node cancellation; factory line 3009 registers it for disable. Neither calls manual `restore`. | A future effect needs an explicit owned-duration cleanup policy. Node restoration does not promise duration restoration. Failed cleanup must remain visible/retryable without touching replacement objects. |
| Solo ownership | `_init_solo_session` lines 1167–1203 and `_upgrade_state` require the owned local-player/PRI rosters and unchanged session. `find_live` does not reuse those checks. | Independently validated effect ownership, session and multiplayer refusal. No co-op inference from the existing manual path. |
| Candidate behavior | Candidate construction keeps effects and activation/deactivation action arrays empty, assigns display/rank metadata and borrows the icon. It does not explicitly set SkillClass. | Do not infer an automatic effect from the candidate's default class or a grade-one description. |

## Actual inert checks

Eleven asserted probes ran against the repository's real `Harness`, with fake `mods_base` and `unrealsdk` modules and synthetic Python objects. The existing manual-duration unittest also passed (one test, zero failures/errors/skips). No installed SDK import, native game call or game state access occurred. The stub named GetSkillManager was called only inside the inert fixture.

The control produced 75 after two applications, preserved base 60 and explicitly restored 60. A distinct instigator with the same name still received 75; a missing ActivatedTime still received 75. Calling the registered shutdown handler's function after applying left Duration 75 and the record retained. This invokes the Python handler in a mock; it is not an observed real SDK disable transition.

A synthetic replacement object reusing the recorded names/time at Duration 75 was changed to 60 by `restore`, while the original remained 75. Two matching owned synthetic active skills selected the first (75) and left the second at 60. These counterexamples demonstrate missing identity/uniqueness checks in code; they do not show those conditions occurred in the real game.

A nonempty modifier stack and boolean Duration refused application. An independently changed Duration 76 was preserved and the record cleared. Losing the record did not stack on 75. Manual application succeeded with no Overclock node state, confirming the paths are independent.

These are readiness findings for a future implementation, not authorization to change the preserved manual prototype. No full-suite repeat was needed for two research-only artifacts; the collaborator's revised tool was separately peer-tested with all 236 unique tests.

Reproduce the contained checks from this branch's repository root using a real Python interpreter and `-B`; load `evidence/overclock_effect_readiness_checks.json` with `json.loads`, then execute its `probe_source` explicitly in an empty namespace. This runs only the repository's inert harness. Never substitute installed SDK modules or execute any SDK stub.

## SDK sources constrain the design

The pinned [unrealsdk hook header](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/hook_manager.h) distinguishes PRE, POST and POST_UNCONDITIONAL; the last can run for a blocked call, and callback order is unspecified. Copied argument changes do not alter the native call.

The pinned [Python hook binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/hook.cpp) exposes a callable bound function and permits blocking/return overrides. A passive observer must return None, avoid invoking it, and not interpret copied output slots as completed outputs. These APIs alone do not identify a BL2 Deathtrap lifecycle event.

The pinned [BoundFunction binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/bound_function.cpp) implements native invocation through its call operator. Therefore `GetSkillManager()` is a game function call, even when used to obtain data. Installed `.pyi` documentation was read as text only; local and public-source hashes are in the JSON. Logged installed SDK hashes resolve to these source commits, rather than an assumed latest API.

## One proposed follow-up: Deathtrap metadata readiness diagnostic

Implement a new explicit synchronous metadata-only option in a separately claimed runtime task after the reviewed capture/current-doc result. Keep the manual helpers, old exact-class Attribute guard and existing `_upgrade_state` unchanged. Use that existing current owned solo Gaige/tree/inert-grade-zero guard before and after the diagnostic. No purchase, summon, GetSkillManager invocation, Duration write, native query, observer, timer, package load or save operation belongs in this initial step.

Discover only already-loaded actual SDK UClass/UFunction descriptors. Revalidate each class/owner/path/type/schema/reference around reflection. Inspect allowlisted descriptor metadata for Definition, SkillInstigator, ActivatedTime, Duration, DurationBaseValue, DurationModifierStack and ActiveSkills, plus the observed GetSkillManager function descriptor. If a typed return descriptor exposes a loaded manager class, it can guide bounded metadata inspection; an unavailable class remains unavailable. Do not invent a WillowGame owner path from a name. Candidate activation/deactivation names from the old inventory are search suggestions only, with zero callable authorization.

Proposed hard bounds: at most four actually verified target classes, eight allowlisted fields, sixteen property descriptors plus one cap-detection read per selected function, four selected function descriptors and 30,000 scanned loaded functions. One user call produces one result, explicit COMPLETE/CAPPED/UNAVAILABLE/REFUSED outcomes and a final unchanged-state check; no unbounded iterator or persistent context. These are design bounds, not already implemented behavior. Capped data cannot validate a full signature.

Unknown typed metadata, conflicting class/owner/descriptor, overlong labels, cycles, schema/reference drift, an overlapping/failed observer or final session/points/rank change stops collection without fallback, invocation, repair or guessed zero values. Explicitly report observers_added=0 and no writes/calls. A test using poison callable wrappers must fail if the diagnostic invokes any native method.

This diagnostic supplies metadata only. A later independently reviewed design would still need passive **natural** lifecycle ownership/timing evidence, then a separate effect/cleanup proposal. The Attribute-class result does not remove those stages.

## Future acceptance matrix

| Offline case for the separately scoped follow-up | Required result |
| --- | --- |
| Valid current owned solo inert rank-zero state | Metadata-only result; no rank/points/Duration changes. |
| Rank one, unknown points, foreign/currently replaced tree/controller/pawn/world/PRI or extra local/roster player | Existing guard refuses; do not relax it for this diagnostic. |
| Unknown SDK wrapper/class, mismatched descriptor owner/name/schema, malformed flags/offset/dimension | Refuse before reading payload or calling methods. |
| Missing class/field/function, complete empty inventory, capped inventory, cycle or drift | Distinct outcomes; no inferred absence, signature or permission to call. |
| Poison GetSkillManager/bound functions/activation queries and package/construct/hook APIs | Zero calls; no hooks, object construction or loads. |
| Reference, native arrays, points/ranks/indices or session change during reflection | Abort before successful END; no repair. |
| Counts just at/above bounds, duplicate descriptors, cleanup exceptions | Bounded output and explicit refusal/error; import/disable remains inert. |

For a later effect proposal, add independent cases for rank-zero skip/rank-one verified gating, same-name foreign owners, multiple active matches, missing/bool/nonfinite activation time, replacement identity with a reused signature, reentrant callbacks, modifiers/unknown values, write/readback failure, independently changed duration and cancellation/disable failure. Each must specify an exact owned-object ledger and retry policy; none is implemented or game-verified here.

Only the two research artifacts change. Runtime, tests, current instructions, packages, captured logs/snapshots and private backups remain untouched. Publish this branch for independent peer review before treating the proposal as an accepted implementation specification.
