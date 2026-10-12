# Callback-local DeactivateSkill parameter reader

**READY_FOR_BOUNDED_PRIMITIVE_READER_IMPLEMENTATION_REVIEW.** This design uses
the new hook-time GC guidance to specify a limited diagnostic. It does not
provide an ownership reader, native adapter or purchased-node duration effect.
Those gates remain NOT_READY and their existing dependencies remain intact.
No runtime, package or new game protocol is delivered by this task.

Accepted base: 1f3e9c4628c834d24913f59ef8d6960c3e56e186, documentation PR30.
Read the [v14 schema](../evidence/deathtrap_parameter_metadata_user_test.log),
[v15 capture](../evidence/deathtrap_passive_event_capture_manifest.json),
[callback audit](deathtrap_callback_access_feasibility.md),
[native identity research](../evidence/deathtrap_native_adapter_evidence_research.md)
and [exact-original cleanup contract](overclock_identity_cleanup_contract.md).
The [companion checks](../evidence/deathtrap_callback_local_reader_design_checks.json)
record the actual source/evidence checks and untested boundaries.

## Useful question and evidence boundary

In a naturally delivered, validated DeactivateSkill PRE callback, can we observe
that the supplied instigator shares the fresh local-controller Python wrapper
and that the supplied definition's Name is exactly Skill_DeathTrap? Record only
fixed primitive classifications. SAME_WRAPPER and DEATHTRAP_NAME do not establish
manager ownership, an exact definition asset, unique active-skill membership,
successful deactivation, summon generation or a write/restoration interval.

[Contributor guidance](https://github.com/bl-sdk/pyunrealsdk/issues/97#issuecomment-6108546422)
states that hook execution blocks the UnrealScript VM and prevents GC; Python
references retained beyond that interval do not preserve native objects. This
resolves the hook-time GC question. It does not certify arbitrary destruction,
already-invalid incoming pointers or this installed binary's build options.
The reader relies on the SDK's ordinary valid hook-input contract and confines
its own reads to the callback. Python guards cannot retroactively protect the
SDK conversions that happen before Python, or catch a native dangling-pointer
fault. Do not describe this design as a general liveness test.

The selected sources match captured SDK startup prefixes: unrealsdk
b1852aa440277afcce8a13566b5487aeae5a7ae9 and pyunrealsdk
c72c5558473bfa1f1cbc9c9113efb2a02251e656. Source/binary equivalence remains
unverified. The contributor requested avoiding LLM question dumps; no further
issue or comment is proposed here.

## One callback, fresh locals

START owns only an epoch, flags, monotonic times, counters, fixed strings and
one hook-registration tuple. It checks project control state without accessing
saved native objects. Refuse armed/injected-node, manual-duration-record and
other active/uncertain observer contexts. This diagnostic runs without ARM or
node insertion; it neither changes nor calls the grade-zero _upgrade_state.
The existing manual prototype and restoration separation remain unchanged.

START registers the already observed canonical
WillowGame.SkillEffectManager:DeactivateSkill path at PRE with a distinct fixed
identifier. Do not perform UObject metadata/player reads from the option
handler: that handler's hook interval has not been established. Registration
uses the preserved path evidence and SDK hook-control API. The first natural
callback performs its own complete schema check. Registration alone supplies
no schema/payload observation; zero callbacks remains NOT_OBSERVED.

Every accepting callback obtains current loaded classes with the SDK's
find_class API, using only the observed manager, controller and definition
class paths. Resolve the function and properties anew. SDK lookup internals
are outside the reader's explicit traversal budget; never load a package,
enumerate instance objects or invent a Deathtrap asset path. No native engine
UFunction is invoked: GetSkillManager/ActivateSkill/DeactivateSkill calls and
BoundFunction.__call__ are prohibited. Read-only SDK metadata/field bindings
and the documented get_pc helper are the proposed access routes.

Use fresh callback-local helpers. Do not reuse _DTEventChecks,
_deathtrap_check/_chain/_function or _dt_event_metadata contexts: they capture
wrappers/descriptors in lambda defaults and retained snapshots. No cache of
native metadata, captured baseline controller, node state or old manager may
become the new reader's proof of present liveness.

## Schema before either parameter

Use the exact SDK binding types: UObject for the manager/parameter/controller,
UClass for classes, UFunction, BoundFunction and WrappedStruct. Reject Python
subclasses/proxies and unobserved native wrapper variants rather than invoking
their conversion/equality methods. Preserve all four callback positional
parameters; never read ret and return exact None on every path.

Require obj.Class to share the fresh loaded SkillEffectManager class wrapper;
func.object must share obj's wrapper. Obtain the current manager-class
DeactivateSkill function and require func.func and args._type to share that
same fresh UFunction wrapper. These are conservative wrapper-identity guards,
not allocation-serial or cross-callback identity claims. A wrapper mismatch
refuses; do not substitute ==, pointer integers, names or WeakPointer.

Check the function's declaring Outer, exact Name, FunctionFlags=149506,
NumParams=3, ParamsSize=12, ReturnValueOffset=65535, no return descriptor and
no inherited SuperField. Validate PropertySize as an exact bounded integer
at least12; the raw capture does not establish its exact value. Resolve at
most four properties to prove exactly these three ordered members, unique
names, direct declaring owner and no extra property:

| Member | SDK property | Flags | Offset | Dimension | Element size | Declared class |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| SkillInstigator | ZObjectProperty | 128 | 0 | 1 | 4 | Engine.Controller |
| Definition | ZObjectProperty | 128 | 4 | 1 | 4 | WillowGame.SkillDefinition |
| bIgnoreSkillInstigator | ZBoolProperty | 144 | 8 | 1 | 4 | Not applicable |

Require exact primitive integer values, excluding bool, for numeric metadata;
verify bounds against the current parameter storage and loaded owner/type.
For each object property require its fresh PropertyClass wrapper to match the
corresponding loaded class. The Boolean descriptor is checked for shape only:
never obtain its value, infer FieldMask or use bIgnoreSkillInstigator semantics.

Immediately before each parameter getter, recheck args._type, function/owner
and that member's lookup/membership/schema. Use fixed-name getattr on the
validated WrappedStruct; its binding resolves the field against the actual
current _type. Do not pass unchecked descriptors to _get_field. Recheck those
links after the getter and before another getter or output. A detected change
refuses; a post-read check is not pre-dereference native immunity.

## Fresh player and fixed classifications

Read SkillInstigator first. None produces NULL_INSTIGATOR without reading
Definition. An unexpected Python/SDK type or class refuses. For the local
comparison require its actual Class to share the fresh WillowPlayerController
class wrapper; other typed classes produce OTHER_CONTROLLER_CLASS with no
Definition read. This is deliberately narrower than accepting every subclass
of the declared Engine.Controller.

Obtain get_pc(possibly_loading=True) inside this callback. Installed
mods_base1.12 documents it as the main local-controller API; its Willow
implementation reads GamePlayers.Actor. It owns persistent ENGINE and
descriptor globals. Disclose that dependency: the reader retains no additional
native references and does not claim the SDK stores none. None/loading,
unexpected controller type/class or helper failure refuses.

For a candidate local match, quietly re-express the source-established solo
checks with fresh locals: loaded pawn, PlayerClass.Name=CharClass_Mechromancer,
SDK-named Standalone/ListenServer NetMode excluding bool, exactly one
ENGINE.GamePlayers entry with Actor sharing pc, and one world.GRI.PRIArray
entry sharing pc.PlayerReplicationInfo with Owner sharing pc. Use only these
fixed field paths; no broad graph search, array copying or arbitrary traversal.
Require typed current object/array/scalar values, verify exact one-entry lengths
before index0, and refuse any unavailable/ambiguous/loading/client state.
Do not call _init_solo_session: its exception formatting can stringify native
objects. These checks are new callback-local observations, not cached START
facts or an Overclock rank/purchase gate.

Compare instigator is pc only while both fresh local wrappers remain in this
callback. A mismatch records OTHER_WRAPPER and stops parameter inspection.
The pinned pybind11 pointer/type instance cache supports interpreting is as a
same-wrapper observation; it supplies neither general native equality nor a
generation across callbacks. Distinct wrappers for a semantically identical
native object are conservatively refused, not repaired with addresses.

Only after SAME_WRAPPER and the fresh solo checks may Definition be obtained.
None produces NULL_DEFINITION. Require the exact UObject binding type and
fresh loaded SkillDefinition Class wrapper; unknown/derived classes refuse.
Read Name once, require exact Python str, 1..128 characters and bounded
identifier characters. The inspected UObject binding/FName caster returns a
Python string; do not call str/repr/path helpers on objects. Emit only
DEATHTRAP_NAME or OTHER_NAME; never retain/log the supplied name. The SDK
converts the native name before Python can enforce the output length bound.

Reacquire get_pc and the narrow solo facts before emission; require the same
callback-local wrappers and known fields. Refuse changed state. This provides
one bounded observation, not stable ownership beyond return. Do not read
ActiveSkills, Grade, ActivatedTime, Duration, modifiers, point/rank/save state
or a definition asset path. No instance/payload is stored for later cleanup.

## State, bounds and results

Proposed reader-owned state contains no game wrappers, metadata descriptors,
argument buffers, bound functions, callbacks that close over such values,
exceptions/tracebacks or queued log arguments. The observer closes over only
the exact positive31-bit epoch; its other locals die with the callback.
SDK modules/binding types and hook-phase enum constants are library controls,
not game-reference ledger entries. Callback arguments necessarily exist in
the SDK/Python call frame; the reader must not export that frame.

| Bound | Contract |
| --- | --- |
| Hook scope | One fixed PRE path/identifier; no activation or POST expansion. |
| Session | At most64 accepting attempts,24 classified records,120 seconds. |
| Callback | At most256 reader-issued SDK lookup/getter/iterator operations: four stages capped64 each; at most8 class validation links, two parameter getter calls, one definition Name read and two get_pc acquisitions. |
| Rosters | Two known arrays, length exactly1, one element each per fresh validation; no active-skill scan. |
| Output | Fixed schema/version/prefix and allowlisted primitive values; each encoded record at most384 UTF8 bytes. |
| Clock | Finite monotonic times; regressions/errors refuse. Limit checked on entry, bounded stages and STOP; no background timer. |

The four operation budgets cover schema validation, instigator validation,
fresh player/session probes, and definition/final schema validation. The first
stage includes up to4 class lookups, one function lookup, up to4 property
iterator probes, header/link checks and all three property shapes. The two
parameter stages reserve before/after member rechecks as well as the getters;
the session budget includes both probes of the two fixed rosters. Count each
reader-issued SDK lookup, getter, array length/index and iterator operation
before performing it. Stop before exceeding a stage or total budget. A draft
32-call budget was insufficient for the schema plus both rechecks and was
replaced before acceptance. SDK internal conversions/helper reads are disclosed
separately; this bounds reader-issued operations, not every native instruction.

Busy/reentry and accepting/epoch/count/time gates precede any payload access.
Nested callbacks increment only a primitive counter and return None. A stop
request first clears accepting. If a callback is busy, defer owned hook removal
until its finally; no concurrent callback is allowed to rearm. REFUSED or ERROR
stops inspection and requests cleanup. Drop native local values before reporting
fixed reasons; never log exception objects, exc_info, traceback, args or funcs.
Do not persist an exception in state or capture it in a closure.

STOP/CANCEL/disable/error/time/count controls remove only this owned tuple.
Failed removal retains a fixed tuple for bounded retry and blocks a new START;
no claim of zero hooks until absence is verified. STOP requires no saved game
object access or _upgrade_state/Duration restore. Existing CANCEL must retain
its established array/other-observer cleanup order with this new stop operation
added separately under a later implementation review. No timer/rearm/write is
hidden in cleanup.

Use a new prefix [UVH-CALLBACK-READ]. Distinguish attempts, classified records,
filtered/null cases, refusals, errors, reentry and cleanup failures. Example
primitive record: EVENT ordinal=1 schema=VALID controller=SAME_WRAPPER
definition=DEATHTRAP_NAME ownership=UNESTABLISHED. This is a proposed format,
not a captured live result. Zero accepting attempts is NOT_OBSERVED; nonzero
attempts with only filtered/refused outcomes must remain separately labeled.
PRE records attempted entry even if another hook blocks native execution.

## Later implementation and capture acceptance

Implementation is a separate claimed task. Add independent helpers/state and
START/STOP controls, with AST proof that historical insertion, grade-zero
diagnostic and manual Duration functions remain intact. Its prospective scopes
are runtime __init__.py/pyproject.toml/README.txt, new
tests/test_deathtrap_callback_local_reader.py, necessary existing factory/control
tests, package verifier, a unique versioned/default package and its own runtime
checks/instructions. Refine the exact existing test/package filenames first;
do not reserve those files through this two-file design task.

Required meaningful tests include wrong callback/args._type/function/owner,
extra or changed descriptors, bool/offset/dimension/class mismatches before
getters, poison ret/Boolean/foreign Definition access, null/local/foreign/name
classifications, fresh-pc replacement/loading/roster changes, cached-wrapper
and exception/logging/closure escape, reentry/stop/limits, failed removal/retry,
clock errors and exactNone on all paths. Model tests verify fixture behavior,
not native lifetime or ownership. A strict primitive-log reviewer needs its
own task and synthetic adversarial cases before a real capture.

A useful live capture must receive a natural event and classify its parameters.
Repeating the old stay-still run does not guarantee such an event. An owner-run
test involving ordinary Deathtrap use would require separately approved exact
code/build and explicit gameplay scope; none is requested or approved here.
Future instructions must specify main-menu/map locations and control labels.
No forced native call, purchase, respec, travel, manual boost or effect test is
authorized by this design. Silence remains a valid outcome, with no repeat to
manufacture missing facts.

Even a positive SAME_WRAPPER/DEATHTRAP_NAME result does not satisfy the effect
contract. Manager ownership, unique active summon, native generation, clock/
Duration consumption, purchased rank-one eligibility and safe exact-original
write/readback/restoration remain separate evidence requirements. Preserve all
raw captures, tested snapshots, original ZIPs and recorded deviations.

## Actual design validation

The companion JSON records fresh full SDK97 discussion/fingerprint, pinned
primary helper/binding/dispatch/comparison byte checks, the two identical v14
DeactivateSkill descriptor blocks and current v15 parser/manifest equality.
All193 accepted base files remain byte-identical, including runtime/tests,
evidence and packages; the exact two new files are checked for scope, syntax/
UTF8/JSON/local links/known-secret-private-path markers and whitespace. Original
ZIP CRC/layout and immutable inventory checks remain applicable.

The596-suite/hostedCI and native behavior are not tested by design prose.
No SDK/stub import/execution/compilation, game test, installation/control,
native function/flag/Duration write, save/private-backup access, purchase,
summon, effect, outgoing support message, merge or release occurs here.
