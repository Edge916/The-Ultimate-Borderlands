# Native Deathtrap adapter: identity and lifetime evidence

**Decision: NOT_READY_FOR_NATIVE_ADAPTER_IMPLEMENTATION.** The inspected SDK
offers an emulated weak reference, not the exact generation and lifetime
guarantee required by the accepted effect contract. No native adapter, new
observer or game test is authorized by this research.

Accepted repository: `f1c9021c5948805dfad7ac05228af4692e2752be` /
[readiness PR #27](https://github.com/Edge916/The-Ultimate-Borderlands/pull/27).
The [v15 assessment](deathtrap_passive_event_live_readiness_result.md),
[capture manifest](deathtrap_passive_event_capture_manifest.json) and
[identity/cleanup contract](../docs/overclock_identity_cleanup_contract.md)
were inspected against the actual source. The
[companion checks](deathtrap_native_adapter_evidence_checks.json) pin source
URLs, hashes, relevant ranges, installed API text and actual repository checks.

## Installed API and source provenance

The accepted v15 log self-reports unrealsdk v3.2.0 (`b1852aa4`) on line 2 and
pyunrealsdk v1.10.0 (`c72c5558`) on line 20. Those short identifiers agree with
the previously pinned full source commits. This is useful startup evidence;
it does not independently verify the installed native binaries or their build
options against those commits.

Installed `.pyi` files were read and hashed as text only. The unreal module
exports `WeakPointer`; its supplied documentation explicitly describes
emulation and an occasional replacement-object ambiguity. This is actual
installed API documentation, not a guessed missing function. No stub was
executed, imported, compiled or placed in the repository/package.

Nine additional files were fetched from the two pinned primary source trees
into local scratch and read as inert text. Existing hook contract/binding and
BoundFunction sources were freshly hash-checked. The source below describes
those inspected revisions; it does not establish all SDK versions or every
engine object's runtime behavior.

## WeakPointer is useful, but not an exact generation proof

The pinned [weak-pointer header](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/wrappers/weak_pointer.h)
documents an emulated Unreal 3 path and a distinct native-weak-pointer path.
The emulated path stores an object index, address, outer address, virtual-table
address, class address and FName. It deliberately avoids retaining a raw
pointer that would later be dereferenced without first resolving GObjects.

The [implementation](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/wrappers/weak_pointer.cpp)
checks the index bounds, resolves the current GObjects entry, then compares
those stored fields. A null or mismatched result refuses. A mutable lookup
that returns null permanently clears that pointer, reducing later reuse risk.
These are meaningful checks, not an absence of liveness support.

They still contain no emulated allocation serial or unique lifetime token.
If two hypothetical object lifetimes reuse every checked field, this predicate
cannot distinguish them. That is a source-logic counterexample, not an
observed incident or a measured probability. The header and installed
documentation explicitly acknowledge that a rare near-identical replacement
may be returned. The alternative native FWeakObjectPtr branch is not proof
that this installed BL2 build provides a serial-backed native lifetime token.

The [Python binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/weak_pointer.cpp)
constructs the reference from the supplied UObject, returns a mutable
dereference on `__call__`, and exposes `replace`. Construction reads the
current object's fields; it is not a magic validity test for an already stale
raw wrapper. The documentation says no strong native reference is available
and describes hook-time GC safety conditionally. That condition is not an
established lifetime guarantee across future callbacks, explicit STOP,
destruction/replacement or a write/readback interval.

Consequently, do not use WeakPointer success, repeated matching scalar fields
or a Python reference as permission to restore Duration on the purported
original. They can corroborate bounded observations but do not satisfy the
accepted exact-original cleanup contract by themselves.

## UObject references and field access

The pinned [binding helper](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/bindings.h)
uses a `std::unique_ptr` holder with `py::nodelete` for PyUEClass. Python
therefore does not own deletion of the wrapped native object through that
holder. Keeping the Python wrapper is not a native GC root or an exact
lifetime lease. The inspected UObject/PyUEClass definitions add no explicit
custom equality, hash, allocation-generation or liveness-check API. This
bounded source finding does not settle generic pybind11 wrapper caching or
every SDK comparison behavior. The model's opaque Python `is` tokens remain
hypothetical adapter facts, not a recommendation for native wrappers.

In the [UObject binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/uobject.cpp),
`_get_address` returns the native pointer as an integer and is documented for
debugging. It supplies no allocation generation. `__getattr__` reads through
the current native Class and property accessor. Repr/path formatting also
reads native class/name/outer information; avoid it on an unvalidated or
retained callback wrapper.

Installed UObject and WrappedStruct documentation warns that `_get_field` and
`_set_field` do not validate descriptor membership; a wrong descriptor is
undefined behavior. Caching a descriptor from a different owner and adding a
Python exception handler is not a validated adapter. A future payload reader
must establish its loaded owner/class/field links, current references and
read interval before access. The existing v14 declared classes alone do not
provide that instance proof.

## Manager ownership and callback boundaries

The [hook contract](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/hook_manager.h)
supplies the called-on object, copied arguments, return proxy and bound
function. PRE precedes native execution; POST follows an allowed call;
POST_UNCONDITIONAL can follow a blocked call. Same-phase order is unspecified.
Even a delivered PRE event does not prove successful skill deactivation.

The [Python hook binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/hook.cpp)
converts an already-set return before invoking the callback. Ignoring callback
payloads does not eliminate the SDK's own wrapper/conversion work. The
accepted v15 observer deliberately selects the verified void DeactivateSkill
PRE path and ignores all four supplied values; it has no manager instance or
payload ownership proof. This completed run recorded no accepting attempts.

The [BoundFunction binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/bound_function.cpp)
releases the GIL and calls the native function for `__call__`. Looking up the
GetSkillManager return descriptor, as v15 does, is different from calling
`pc.GetSkillManager()`. A future native getter call would cross that execution
boundary and require its own reviewed scope; a known descriptor is not
authorization to invoke it. No such call ran in this research.

Engine.Controller / WillowGame.SkillDefinition declarations do not establish
that an actual callback instigator owns the current Gaige or that the
definition is the exact Deathtrap definition. Core.Object for the activation
target proves no summon type. ActivatedTime metadata proves neither units nor
generation. Boolean FieldMask/return/delegate semantics remain separate from
object-property class coverage. No payload value was obtained here.

## Effect readiness and the next useful boundary

| Requirement | Research result | Remaining evidence |
| --- | --- | --- |
| Detect null or many ordinary replacement cases | Emulated WeakPointer supports checked GObjects lookup. | Actual tested native behavior and exact-original guarantee are not established. |
| Prove exact object generation across callbacks | Emulated predicate has no unique allocation serial; scalar reuse can collide. | A verified native generation/lifecycle mechanism that meets the contract. |
| Keep the original alive through access/cleanup | Non-owning holder and conditional hook-time GC guidance. | A validated lifetime/read interval, including destruction, reentrancy and replacement. |
| Prove current manager/instigator/unique Deathtrap membership | Function/field class metadata, no actual instance proof. | Bounded freshly validated ownership and complete unique membership evidence. |
| Prove clock and Duration write/readback/cleanup interval | No actual skill timing or consumption observation. | Native timing and safe interval evidence, separate from observer monotonic time. |
| Verify a purchased rank-one Overclock gate | Current diagnostic remains grade zero; model facts are hypothetical. | A separate reviewed eligibility gate and later explicit gameplay authorization. |

The SDK-free model and current grade-zero diagnostic must remain unchanged.
The manual name/time/first-match boost is still separate, and CANCEL/shutdown
do not call its Duration restore. Hook removal/native-array rollback cannot
be used as the effect's cleanup proof.

The next useful design question is whether a bounded observation confined to
one natural callback can safely obtain **primitive ownership evidence** while
retaining no native wrappers or proposing any Duration write. Such a design
must first resolve the actual hook-time lifetime and comparison boundary,
loaded callback/field types, unknown/reentrant behavior and useful capture
conditions. WeakPointer cannot silently become the persistent effect ledger.
If that proof cannot be supplied, the concrete blocker is missing native
generation/lifetime capability; source/API or SDK maintainer evidence is
needed before extending the adapter. Do not relax the accepted contract to
turn a rare documented ambiguity into an exact-original guarantee.

This report neither specifies nor approves a new runtime/payload observer,
activation/POST expansion, native manager call or summon test. Any later
diagnostic needs separate bounded design/implementation review and explicit
exact-build, location-specific owner approval. Do not repeat the completed
silent run to chase a positive event. Its second ARM refusal, TIME,
44.228-second wrapper interval, unknown UI/visible-failure facts and recorded
manifest-counter correction remain in the unchanged capture.

## Actual checks and limits

Fresh source/stub byte hashes and source-marker/range checks, unchanged runtime
syntax/AST, full v15 CLI/manifest equality, all 189 accepted Git blobs,
15 original ZIP CRC/layouts, immutable53/12/5, frozen fullv12/v13/v14
reports/manifests/snapshot-originalZIP equality, current source/snapshot/v15ZIP
identity, UTF-8/JSON/local links/exact two-file scopes/whitespace and bounded
known secret/savepath scans are verified in the companion checks.

The accepted596-test suite and hostedCI were not repeated for research files.
No native binary was loaded or matched to source, no WeakPointer was created
or called, and no SDK/stub was executed/imported/compiled. No game test,
instance enumeration, hook registration, native invocation, gameplay write,
agent install/control, save/private-backup access, purchase/respec/travel/
summon/manualboost/effect/co-op/merge/release occurred. The source-logic
collision is hypothetical; no engine lifetime incident is claimed.
