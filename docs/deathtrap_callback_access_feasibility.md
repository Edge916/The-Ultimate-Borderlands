# Callback-confined Deathtrap ownership access: feasibility

**Decision: NOT_READY_FOR_CALLBACK_OWNERSHIP_READER.** The inspected SDK
provides synchronous hook dispatch and owned argument-copy storage. It does
not establish the native UObject lifetime interval required for a new reader
to dereference and compare manager, controller and definition references.
This is a bounded source finding, not evidence that ordinary SDK hooks are
broken or that a lifetime incident occurred in the owner's game.

Accepted input: `fecf7b5af901bfe0a474f8059d03ed17921609ca` /
[research PR #28](https://github.com/Edge916/The-Ultimate-Borderlands/pull/28).
Read the [native identity research](../evidence/deathtrap_native_adapter_evidence_research.md),
[v15 live assessment](../evidence/deathtrap_passive_event_live_readiness_result.md)
and [exact-original effect contract](overclock_identity_cleanup_contract.md).
The [companion checks](../evidence/deathtrap_callback_access_feasibility_checks.json)
pin primary source bytes, marker lines, installed text documentation and actual
repository checks. SDK sources remain local scratch, outside the project.

The accepted startup log reports unrealsdk 3.2.0 (`b1852aa4`) and pyunrealsdk
1.10.0 (`c72c5558`). Source pins agree with those prefixes; native binary/build
options and active locking configuration have not been independently matched.
The pybind11 revision below comes from the exact pyunrealsdk source-tree gitlink,
not from a currently installed version assertion.

## What occurs before and during a PRE callback

The pinned [BL2 dispatch implementation](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/game/bl2/hooks.cpp)
has two relevant entry paths:

1. ProcessEvent resolves matching hooks, creates a WrappedStruct view of the
   incoming parameter buffer, then calls `copy_params_only`. It constructs
   Details with the raw called-on object and bound function and runs PRE hooks
   inline, before invoking the selected original function when allowed.
2. CallFunction allocates argument storage and calls `extract_current_args`
   before PRE. The [FFrame helper](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/structs/fframe.cpp)
   steps the script argument expressions through the engine's fframe_step
   boundary. PRE therefore does not mean that no native processing happened
   earlier: argument evaluation precedes the selected function's PRE phase.
   This audit does not claim any particular expression caused a nested call.

The [hook runner](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/hook_manager.cpp)
iterates matching callback nodes and ORs their block decisions. Its shared
nodes retain callback-list structure; they are not strong references to the
called-on game object. The selected dispatch/runner code does not marshal
callbacks to a verified game thread or acquire an engine GC lifetime lease.
That bounded absence does not establish the threading or GC behavior of the
rest of BL2.

The [Python binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/hook.cpp)
acquires the GIL and invokes the Python callback on the dispatching thread.
It also performs return conversion before the callback when a value is set.
The GIL protects Python execution; no engine collector exclusion follows from
it. A Python exception handler is not a native dangling-pointer guard.

## Optional function lock is a separate boundary

The [lock implementation](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/locks.cpp)
uses a recursive mutex, conditional on `unrealsdk.locking_function_calls`, with
a source fallback of false. The BL2 detours choose locking or ordinary wrappers
when installed. The enabled value is cached on first lookup in this revision.
This report has not read or changed the owner's configuration and does not
assert whether that lock is enabled in the captured build.

When enabled, this lock serializes participating function-call paths. Its
recursive nature permits same-thread reentry. The inspected code does not
connect that mutex to engine garbage collection, UObject destruction or a
reference-root mechanism. Enabling a setting would not by itself supply those
facts and is not a proposed fix. The hook runner's log-stream mutex protects
logging, not game object lifetime. Python GC-related code in pybind11 concerns
Python objects, not Unreal's collector.

## Copied buffers do not own pointed-to game objects

[WrappedStruct](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/wrappers/wrapped_struct.cpp)
allocates its own storage for copied parameters. Its UnrealPointer control
block reference-counts that allocation. The
[object-property getter](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/properties/zobjectproperty.cpp)
returns a raw UObject pointer and ignores the parent-allocation argument.
The value type is UObject*. Copying a parameter copies its pointer value;
it does not clone or root the pointed-to controller/definition.

There is native pointer access even before a new Python reader's own guard:
ProcessEvent's generic parameter copy uses property setters, and this
object-property setter checks a non-null object's class. A later Python object
conversion uses the SDK polymorphic downcaster, whose
[cast helper](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/cast.h)
reads Class and walks class metadata. A type check after that conversion cannot
retroactively prove that the conversion's native access was safe. These are
source access points, not claims of observed invalid arguments.

WrappedStruct.__getattr__ resolves a field against its current type;
_get_field accepts a supplied descriptor without validating membership.
The installed documentation warns that a mismatched field is undefined
behavior. The property reader checks array index bounds, computes the
descriptor's offset and reads the value; these checks do not prove the base
object's lifetime. A future reader must validate the actual loaded args type,
declaring owner, property kind/flags/offset/dimension and current references
within a supported interval, before allowing field access.

## Wrapper caching explains identity, not generation

The pyunrealsdk gitlink selects pybind11
`f5fbe867d2d26e4a0a9177a51f6e568868ad3dc8`. Its
[caster lookup](https://github.com/pybind/pybind11/blob/f5fbe867d2d26e4a0a9177a51f6e568868ad3dc8/include/pybind11/detail/type_caster_base.h)
searches registered instances by the native pointer and matching C++ type,
then returns an existing Python wrapper if it can increment its reference.
The generic caster consults that map before creating a new wrapper.
[Registration and deallocation](https://github.com/pybind/pybind11/blob/f5fbe867d2d26e4a0a9177a51f6e568868ad3dc8/include/pybind11/detail/class.h)
add and remove Python instances in that map. The inspected lookup key has no
engine allocation serial.

This supplies a concrete source basis for wrapper reuse. It does not establish
every comparison/caching path in the installed binary. If a still-registered
non-owning wrapper and a new native lifetime have the same pointer and matched
type, the selected lookup predicate alone cannot distinguish the lifetimes.
This is a conditional source counterexample, not an observed replacement.
Python `is`, `==`, retained wrappers, names and debugger pointer integers must
not become a cross-callback exact-original generation test. Pointer equality
within an independently proved live interval is a narrower question; neither
this cache nor the emulated WeakPointer establishes that interval.

## The current metadata covers declarations only

Both preserved v14 descriptor blocks agree on void DeactivateSkill:
canonical WillowGame.SkillEffectManager owner, flags149506, parameters3,
size12, return offset65535 and no return property. Inputs are SkillInstigator
(ObjectProperty, Engine.Controller, flags128, offset0), Definition
(ObjectProperty, WillowGame.SkillDefinition, flags128, offset4), and
bIgnoreSkillInstigator (BoolProperty, flags144, offset8); each dimension1,
element size4. Boolean mask semantics were not captured and need not be read
to answer the proposed object-ownership question.

The unchanged v15 preflight revalidates those declarations and the known
GetSkillManager return descriptor. It does not call GetSkillManager. Its
callback never loads obj/args/ret/func and returns exact None. The completed
v15 run recorded zero accepting attempts/events; it supplies no delivered
manager, instigator or definition payload. A declared Controller class does
not establish current local Gaige ownership, and a declared SkillDefinition
class does not identify Deathtrap or a unique active skill instance.

## Concrete evidence request before another diagnostic

The following is a prepared question set, not a sent message. Source/API
maintainer evidence or documented engine capability must address the exact
BL2 SDK revision and the intended read operations:

1. Which thread executes DeactivateSkill PRE via ProcessEvent and CallFunction?
   What guarantees exclude GC/destruction/replacement while the called-on
   manager, copied controller/definition pointers and their Class metadata are
   converted, compared and read? Specify whether guarantees depend on a build
   option/setting and whether other engine threads participate in its lock.
2. What can happen while a callback waits for the GIL, during same-thread
   reentry, argument expression evaluation or a Python/native call? Which
   operations preserve the supported lifetime interval? Explain how unknown
   or expired intervals can be detected before the first native dereference.
3. What API compares two valid native UObject references within that interval
   without invoking user equality, requiring a native call or conflating reused
   lifetimes? What concrete generation/lifecycle mechanism supports later
   cleanup of the exact original, beyond WeakPointer's documented ambiguity?
4. How is the copied WrappedStruct argument buffer owned when converted to
   Python, and which loaded type/field membership checks are required before
   obtaining its two ObjectProperty values? Does any supported mechanism root
   their pointees for the read interval? A copy of the buffer is insufficient.
5. What bounded, natural observation can provide actual current manager-to-
   player ownership evidence without GetSkillManager invocation, object graph
   enumeration or a forced summon? What new fact would it collect that the
   completed silent run did not collect?

A sufficiently precise answer can support a separately reviewed, primitive-
only callback-reader design. That later design would retain no game wrappers,
perform no Duration write and distinguish attempted entry from successful
lifecycle. It would still need bounded guards/refusals, a meaningful capture
condition, implementation/reviewer checks and explicit exact-build owner
approval before a location-specific game protocol. No such protocol or build
is prepared here. Do not repeat the silent run to chase an event.

The owned effect remains NOT_READY until additional exact-original generation,
unique owned active instance, engine clock, Duration consumption, safe write/
readback/cleanup interval and separate purchased rank-one evidence are resolved.
The rank-zero diagnostic, SDK-free model and established manual prototype stay
unchanged. CANCEL/native-array restoration does not call manual Duration restore.

## Checks and limits

The companion file records fresh source text SHA256 and Git blob verification,
marker lines, installed documentation hashes, unchanged runtime syntax/AST,
both loaded v14 descriptor records, full v12/v13/v14/v15 offline report equality,
snapshot/original ZIP equality, all191 base blobs,15 original versioned ZIP CRC/
layout checks, immutable53/12/5 and two-file scope/UTF8/JSON/link/whitespace checks.

The accepted596-test suite and hosted CI were not repeated for this source-only
audit. No SDK/stub was executed, imported, compiled or packaged. No native
binary/source match, locking configuration, actual callback thread/GC/liveness/
reference comparison or ownership payload was tested. No new game test, hooks,
native invocation, runtime/package/model/test change, install/control, save/
private-backup, purchase/respec/travel/summon/manualboost, Duration write,
effect, co-op, outgoing message, merge or release occurred.
