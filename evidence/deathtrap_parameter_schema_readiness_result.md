# v0.2.14 parameter schema: passive design readiness

**Decision: READY_FOR_PASSIVE_OBSERVER_DESIGN, limited to bounded,
unattributed function-path and hook-phase events.** The actual canonical
function owners and argument classes now support writing that design. This is
not readiness to implement hooks, read callback payloads, identify an owned
Deathtrap lifecycle or design the duration effect. Those gates remain open.
No further game test is requested by this assessment.

Accepted cumulative base: `d441147a0311acb12c4ac7a44ffa79874810afad`
([capture PR #21](https://github.com/Edge916/The-Ultimate-Borderlands/pull/21)).
Unchanged runtime: `a707779914ee9fe092dca8e72800c015f5b26e61`
([implementation PR #20](https://github.com/Edge916/The-Ultimate-Borderlands/pull/20)).
These remain draft branches, not merged releases. The
[companion checks](deathtrap_parameter_schema_readiness_checks.json) pin
inputs, actual descriptors, SDK text hashes, source ranges and fresh checks.

## What the capture adds

Fresh strict review of the [preserved log](deathtrap_parameter_metadata_user_test.log)
returns `COMPLETE_LOG_TEXT`, exit 0, and equals the entire report in the
[manifest](deathtrap_parameter_metadata_capture_manifest.json). Lines 65-82
and 83-100 contain identical fifteen-row collections. Four class roots, three
functions and seven fields have COMPLETE descriptor coverage. All function
rows still explicitly say `signature=NOT_ESTABLISHED`.

| Descriptor | Actual declared class or selected type |
| --- | --- |
| WillowPlayerController:GetSkillManager ReturnValue | WillowGame.SkillEffectManager |
| SkillEffectManager:ActivateSkill SkillInstigator | Engine.Controller |
| SkillEffectManager:ActivateSkill Definition | WillowGame.SkillDefinition |
| SkillEffectManager:ActivateSkill AdditionalSkillTarget | Core.Object |
| SkillEffectManager:ActivateSkill SkillGrade | ZIntProperty |
| SkillEffectManager:ActivateSkill StateChangeDelegate | ZDelegateProperty |
| SkillEffectManager:ActivateSkill ReturnValue | ZBoolProperty |
| SkillEffectManager:DeactivateSkill SkillInstigator / Definition | Engine.Controller / WillowGame.SkillDefinition |
| SkillEffectManager:DeactivateSkill bIgnoreSkillInstigator | ZBoolProperty |

GetSkillManager has one parameter/four bytes/return offset 0. ActivateSkill has
six parameters/32 bytes/return offset 28. DeactivateSkill has three
parameters/12 bytes/return offset 65535. Actual full canonical paths, flags,
offsets, sizes and property-class coverage are copied into the checks.
AdditionalSkillTarget's broad Core.Object declaration does not establish an
actor, a summon or the intended target's native class.

Class coverage is NOT_APPLICABLE for the integer, Boolean and delegate
descriptors. This is a class-metadata result, not verification of Boolean
FieldMask, delegate Signature, payload values or return meaning. Those fields
were not emitted by this diagnostic. Their APIs exist in the inspected SDK;
their omission is not a claim that they are unavailable.

The seven field descriptors remain unchanged from v13: manager ActiveSkills,
Skill Duration, DurationBaseValue, ActivatedTime, SkillInstigator, Definition
and DurationModifierStack. No current manager was invoked or skill/target
payload captured. The rank-zero FINAL assertion compares against an unlogged
internal starting state; the parser cannot independently reconstruct it.

## Actual SDK contract and its limits

The installed `.pyi` files were read as text and freshly hash-checked. They
were never executed, imported or packaged. Four previously pinned public
source files were inspected locally and freshly matched to their accepted
hashes. This verifies those source texts, not that the installed native binary
was built from the pinned commits.

The [hook manager contract](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/hook_manager.h)
defines PRE before execution, POST only after an allowed call, and
POST_UNCONDITIONAL even after a blocked call. Ordering within a phase is
unspecified. PRE is an attempted call; POST is not proof of successful skill
activation. Neither phase identifies a Deathtrap or proves a lifetime.

The callback receives obj, args, ret and func. Arguments are a mutable copy;
changing that copy does not edit the original call's arguments. The return
proxy can include another PRE observer's override. `args.ReturnValue` is not
the authoritative return. In the
[Python hook binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/hook.cpp),
a set return is converted before the Python callback runs. Ignoring ret in
the callback therefore does not remove the SDK's own conversion work. This
also matters for PRE if another hook has already supplied a return override.
The design must review this path before choosing phases; it cannot advertise
zero native reads or a verified safe adapter from these descriptors alone.

An exact None callback result does not block execution or supply a return
override in that binding. Block sentinels and tuples are excluded from the
proposed scope. The
[BoundFunction binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/bound_function.cpp)
executes native code through `__call__`; even its representation reads native
function/object information. The callback must neither call nor format it.
Object address, InternalIndex, name, path and class do not supply a verified
generation or native lifetime. No payload wrapper may be retained to fill
that gap.

## Exact next design scope

The smallest useful next task is a design document and SDK-free acceptance
specification for manually enabled, bounded canonical manager-call events.
It must satisfy all of the following before implementation can be considered:

1. Use only the two verified SkillEffectManager canonical function paths.
   Capture a closed literal path/phase label selected at registration and
   bounded primitive counters. Ignore all four callback payloads: no attribute
   access, identity comparison, repr, conversion, retention or native calls.
2. Label each event `UNATTRIBUTED_MANAGER_EVENT`. Such an event could relate
   to another skill or controller. Do not pair PRE/POST into a summon
   generation, claim owned-manager membership, infer successful activation,
   calculate lifespan or infer engine-clock units.
3. Decide phase eligibility from the SDK's actual automatic marshalling and
   return-override behavior. Prefer PRE-only initially; justify any POST
   separately. POST_UNCONDITIONAL cannot supply an execution-success claim.
   Missing conversion/lifetime evidence may still block implementation.
4. Specify manual opt-in, preserved grade-zero/sole-player guards and unchanged
   points/ranks, exact current-context/session policy, overlap refusal,
   finite limits and unique hook identifiers. Resolve how fresh session
   checks work without reading unverified callback payloads. Set accepting
   state inert before removing hooks. Retain failed removals for bounded
   retry; report cleanup failures even after a successful retry.
5. Specify poisonous-payload mocks, repeated/reentrant callbacks, limits,
   context changes, partial registration, exception/removal failure and
   retry acceptance. Confirm exact implementation/test file scopes and
   preservation of all prior behavior, evidence and versioned packages.
   Implementation and a subsequent exact-build owner test require separate
   claims, review and the applicable explicit test authorization.

This scope records coarse activity while preserving the unresolved ownership
boundary. If that activity would not answer a useful question, the design
should refuse a runtime change and identify the missing adapter evidence.
Readiness to write the design is not a promise that implementation will pass
its gates. The [identity/cleanup contract](../docs/overclock_identity_cleanup_contract.md)
still requires exact native ownership and lifetime evidence before an effect.

## What remains NOT_READY

Natural activation/deactivation callbacks, exact current manager ownership,
instigator/definition/target payload interpretation, return/delegate semantics,
native wrapper lifetime, liveness and generation are unobserved. So are
ActivatedTime clock units, live Duration/base/modifier values and a safe
effect consumption/write/readback interval. The separate purchased-node
rank-one gate, native duration cleanup adapter and measured extended lifespan
remain unverified. The SDK-free model accepts hypothetical opaque facts; its
passing tests do not establish an engine adapter.

The existing manual duration path still uses names/time and first-match
discovery. CANCEL/disable cleanup does not invoke its manual restoration.
Those functions and the grade-zero diagnostic guard were inspected and remain
unchanged. This report supplies no reason to reuse that path for an automatic
effect or infer duration cleanup from array restoration or zero hooks.

## Actual validation and provenance

97 fresh SDK-free tests passed with no failures, errors or skips: 36 contract
model cases and 61 metadata guard cases. These exercise hypothetical ledger
inputs and inert schema/refusal/drift fixtures, not engine callbacks. Fresh
parser/full-manifest equality, unchanged runtime syntax, all 171 base Git
blobs, all 14 original versioned ZIPs, ZIP CRC/three-file layout and exact
reviewed-source/tested-snapshot/v14 ZIP equality passed. Immutable inventory
53 files/12 archives/5 relationships passed; its older baseline is preserved,
and later packages are checked separately. Four installed stub and four
pinned source hashes matched their accepted inputs.

The preserved capture's stable double-read and process-zero checks are prior
capture provenance, not new observations of the game process in this task.
The literal owner statement is `cancel 3 completed, fully exited`. Two
inspections occurred despite one requested; a second ARM refused and CANCEL
was repeated. The agent did not independently observe the UI/title or
pre-test state, and no separate visible-failure statement was given. These
limits remain in the original manifest without revision.

The unchanged full 448-test suite and hosted CI were not repeated for these
two evidence files. No native SDK execution, new game test, hook registration,
payload read, native invocation, gameplay write, purchase, save/private-backup
access, co-op, merge or release ran. Only these two new evidence files change.
