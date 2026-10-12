# ActivateSkill PRE source feasibility audit

**Conditional support for a separate bounded primitive-reader design review.
Native adapter/effect NOT_READY.** Pinned SDK sources support a callback that
returns exact non-tuple None without requesting a block or changing an existing
return override. They do not establish Deathtrap activation coverage, native
generation, installed-binary equivalence or general input/lifetime safety.
No new hook, runtime, package or owner test is delivered here.

Accepted parent is assessment `ce83fcffaa12502be0ce8bdb4b97bb5df2747169` /
[PR 40](https://github.com/Edge916/The-Ultimate-Borderlands/pull/40).
Read its [v17 result](../evidence/deathtrap_callback_definition_name_live_readiness_result.md),
the complete [capture](../evidence/deathtrap_callback_definition_name_capture_manifest.json)
and [this audit's checks](../evidence/deathtrap_activation_reader_feasibility_checks.json).
V17 observed one UpshotRobot/OTHER_NAME event, with no Skill_DeathTrap match. Its owner
reported a natural Deathtrap end; neither fact supplies a new activation event.
Keep the literal matcher, all frozen inputs and original effect dependencies.

## Existing candidate metadata

Both preserved v14 descriptor rows agree on the actual loaded
WillowGame.SkillEffectManager:ActivateSkill path: flags 149506, 6 parameters,
ParamsSize 32 and ReturnValueOffset 28. This is metadata, not permission to call
or register that function and not an established lifecycle signature.

| Property | Kind / declared class | Flags | Offset / size |
| --- | --- | ---: | --- |
| SkillInstigator | ZObjectProperty / Engine.Controller | 128 | 0 / 4 |
| Definition | ZObjectProperty / WillowGame.SkillDefinition | 128 | 4 / 4 |
| AdditionalSkillTarget | ZObjectProperty / Core.Object | 144 | 8 / 4 |
| SkillGrade | ZIntProperty | 144 | 12 / 4 |
| StateChangeDelegate | ZDelegateProperty | 4194448 | 16 / 12 |
| ReturnValue | ZBoolProperty | 1408 | 28 / 4 |

All dimensions are 1. The complete schema must be validated, even when a proposed
reader would access only the instigator, definition and bounded Name. Core.Object
does not identify a summon. SkillGrade is not purchased Overclock rank; the
delegate is not an allocation-generation or liveness contract. No payload
values for these fields were obtained in this audit.

## Python return and SDK processing

At pyunrealsdk pin c72c5558, the
[Python hook binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/hook.cpp)
calls Python in obj,args,ret,func order; the v17 callback and inert fixtures
match it. Exact non-tuple None takes the non-block path and never reaches
tuple override processing. It leaves a previous override unchanged, including
one provided by another hook. A tuple is a different contract and is prohibited
for the proposed reader, even if its first element is None.

Before invoking Python, the binding checks the
[return proxy](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/wrappers/property_proxy.cpp).
Initially it has no stored value, so Python receives the Unset class sentinel.
If an earlier hook supplied an override, the binding converts that stored value
first. The [property accessor](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/property_access.cpp)
dispatches it through its actual property traits. For
[BoolProperty](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/properties/zboolproperty.cpp),
the getter reads a bitfield through FieldMask and produces a Boolean.
Ignoring ret inside Python cannot suppress this earlier conversion.

| Source case, not a native test | Exact None from our proposed callback |
| --- | --- |
| No previous override or block | Requests neither block nor override. |
| Previous override exists | SDK conversion already occurred; the override remains. |
| Another hook requests blocking | Our callback cannot make execution happen. |
| A later hook changes the override | Our callback supplies no priority or outcome guarantee. |

The [core hook contract](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/hook_manager.h)
leaves same-phase order unspecified. Its
[dispatcher](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/hook_manager.cpp)
runs the collection and accumulates block requests. PRE remains attempted
entry, including blocked calls. Neither an event nor a preserved return
override establishes successful activation or a live summon.

## Work before Python cannot be bounded by Python guards

The pinned [BL2 hooks](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/game/bl2/hooks.cpp)
construct copied arguments before PRE. ProcessEvent uses
[copy_params_only](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/wrappers/wrapped_struct.cpp),
which filters on the parameter bit only. ReturnValue flags 1408 contain that
bit as well as the return bit. Consequently this source route can copy the
return cell and the target/grade/delegate cells before the reader validates
anything. Do not claim those values are wholly unread by the SDK.

CallFunction instead uses
[argument extraction](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/structs/fframe.cpp):
it skips return properties and steps argument expressions before PRE. If the
original call is allowed, the hook resets its code position before calling it.
This SDK route's evaluation and copying cannot be described as zero native
work or counted solely by a future Python operation budget.

Native object/type conversion also precedes the callback, as shown by the
[casters](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/type_casters.cpp).
Python validation can reject the objects it receives; it cannot retroactively
protect an invalid native pointer or unsupported conversion. Source typing,
metadata flags and Python exceptions are not a general liveness guarantee.

## Thread, lifetime and invocation limits

The Python hook registration wrapper acquires the GIL on the invoking thread.
It does not establish game-thread affinity. BL2 selects its locking wrapper
conditionally; the [lock source](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/locks.cpp)
reads a configuration option whose default is false. Installed build/configuration
equivalence and all caller-thread behavior were not checked here. The GIL is
not an owned-manager, native lifetime or reentry proof.

The complete current [SDK97 discussion](https://github.com/bl-sdk/pyunrealsdk/issues/97)
still has one unchanged contributor reply. It supplies hook-time VM/GC guidance;
it does not make Python references keep native objects alive after return or
establish arbitrary destruction/generation/ABI guarantees. No support message
is proposed or sent. The independent audit cache preserves its read time/hash.

[BoundFunction.__call__](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/bound_function.cpp)
releases the GIL and invokes a native function. A future primitive design must
forbid that route, delegate calls, package loading, broad object enumeration,
extra phases, engine calls, flag/Duration/point/rank/save writes and native
references escaping the callback. No SDK source or stub was executed/compiled.

## Conditional next design and precise gaps

A **separate activation primitive-reader design review** is supportable under
the same limited ordinary-valid-SDK-hook-input assumption used by the accepted
v17 diagnostic. The return source supports an exact None callback; it does not
support promises of zero SDK return/argument processing, actual activation
success or arbitrary native input safety. If the intended requirement is that
the SDK never touches ignored/return cells before Python, this standard binding
cannot meet it; do not propose a game test under that requirement.

The design must spell out this assumption and source/binary/thread/ABI limits,
validate all six descriptors and current function/owner links, retain fresh
instigator-first solo/current-player/roster checks, and allow only the two
parameter getters plus one bounded Definition.Name. AdditionalSkillTarget,
SkillGrade, StateChangeDelegate and ret stay unread by the Python reader; their
SDK preprocessing remains explicitly separate. Preserve the exact literal,
primitive-only state/epoch closure/None return, native-payload dropping,
overlap/reentry/time/event bounds and owned/uncertain cleanup behavior.

Derive new exact stage counts and finite operation bounds for the six-property
schema, including the terminating membership probe. Do not assume the three-
property reader's 58/50/36/52 counts or four 64-operation stage budgets carry over. New version,
identifier/prefix/strict grammar, Name privacy, error output and cleanup must
be separately specified and tested with inert fixtures before any package/run.
Reader-issued bounds cannot constrain SDK allocation/conversion/expression work.

Activation coverage is still **NOT_OBSERVED**. There is no captured activation
identifier or authoritative native path-to-owned-Deathtrap association. A later
explicitly approved primitive activation observation could test that narrower
identifier question, while accepting silence/refusal/OTHER_NAME. It would not
prove manager ownership, unique active membership, summon generation/liveness,
engine clock/Duration consumption, purchased rank-one or exact-original restore.
All effect gates remain NOT_READY and original dependencies remain intact.

Prospective next design scopes are `docs/deathtrap_activation_reader_design.md`
and `evidence/deathtrap_activation_reader_design_checks.json`, dependent on this
audit's publication and deliberate acceptance. They do not authorize runtime,
hook installation or gameplay. No owner test is proposed for execution now.

## Actual checks and publication

Sixteen pinned primary sources were fetched/UTF8-decoded/hashed as inert text,
with source-line/control-flow fingerprints and comparison to prior checked
caches. The actual two identical v14 descriptor rows, parameter/return flag
arithmetic, callback order, None/tuple separation, return conversion, pre-Python
copy/extraction, block aggregation and GIL/lock/invocation paths were checked.
This is static source analysis; no simulated binding or native test is claimed.

Fresh full v17 CLI/manifest equality, runtime/source/snapshot/original ZIP,
all 227 accepted base files, 17 original archives, six frozen full v12-v17 reports/
snapshot relationships and immutable 53/12/5 inventory pass. Local/primary links,
UTF8/JSON/exact two-file scope/whitespace/known secret-private-path scans are
recorded. Unchanged 760 tests and hosted CI are not rerun for documentation-only
work. No new raw log, SDK source copy, runtime/package, private file, installation,
game/save/purchase/summon/effect/support/merge/release action occurs.
These two new audit files need their own exact public approval; PR 40 fulfilled
the previous assessment approval.
