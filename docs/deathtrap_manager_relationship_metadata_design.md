# Bounded relationship class metadata discovery

**READY_FOR_BOUNDED_METADATA_IMPLEMENTATION_REVIEW under ordinary-valid SDK
hook-input assumptions. Native attribution and effect NOT_READY.** This design
addresses the accepted audit's METADATA_GAP by cataloguing a limited reflected
property-link scope. It delivers two static design files. No implementation,
package, hook registration, installation or game test occurs here.

Accepted parent `ca901f940f043db901f61191be24d9c3fcb5bda4` /
[audit PR47](https://github.com/Edge916/The-Ultimate-Borderlands/pull/47).
Read the actual [audit](deathtrap_manager_attribution_feasibility.md),
[audit checks](../evidence/deathtrap_manager_attribution_feasibility_checks.json),
[v18 assessment](../evidence/deathtrap_activation_reader_live_readiness_result.md),
complete [raw log](../evidence/deathtrap_activation_reader_user_test.log),
[manifest](../evidence/deathtrap_activation_reader_capture_manifest.json),
[tested source](../archive/tested_runtime/v0.2.18/__init__.py),
[original ZIP](../dist/UltimateVaultHunterDeathtrapBoost_v0.2.18_folder_install.zip)
and [design checks](../evidence/deathtrap_manager_relationship_metadata_design_checks.json).
V18 observed Skill_DeathTrap and filtered UpshotRobot at PRE, with clean recorded
cleanup. That does not establish manager ownership. No repeat of v18 is needed.

## Narrow question and access interval

Do the property links of the already-evidenced controller and manager classes
contain scalar object-property descriptors whose declared class is one of their
known class roots or ancestors? Record descriptor facts and scoped coverage,
rather than evaluating any discovered field on a controller, manager or skill.
A discovered declaration would require later semantic research and a separately
reviewed access design; it would not establish current player ownership.

For a future separately approved build, sample at most once inside a naturally
delivered WillowGame.SkillEffectManager:ActivateSkill PRE callback. This is the
observed v14/v18 entry, not a guessed path. Do not sample in START, a menu handler,
a worker thread, a timer or after hook return. START performs only Python-state
checks and hook-control API operations. This avoids assuming an outside-hook
lease for descriptors retained from a menu observation.

The accepted ordinary-valid-SDK-input assumption remains explicit. The complete
current [SDK97 discussion](https://github.com/bl-sdk/pyunrealsdk/issues/97) has one
unchanged [contributor reply](https://github.com/bl-sdk/pyunrealsdk/issues/97#issuecomment-6108546422).
Hook-time VM/GC guidance does not certify already-invalid pointers, arbitrary
destruction, allocation generations, game-thread affinity or installed native
binary/build/configuration equivalence. Python exceptions and a GIL do not
contain native pointer faults. If arbitrary-input safety or zero prior native
processing is required, this standard binding does not satisfy that requirement.

Return exact non-tuple None on every callback path. Read no Python ret,
SkillInstigator, Definition, Name of a skill definition, AdditionalSkillTarget,
SkillGrade or StateChangeDelegate value. None requests no block or new override;
an earlier override can be converted before Python and remains in effect.
Other hooks may block or alter the call; PRE does not establish execution.
ProcessEvent's PARAM copy includes this ReturnValue; CallFunction steps argument
expressions before PRE. Wrapping, casts and metadata getter internals remain
outside the Python operation meter. These are the accepted
[activation source boundaries](deathtrap_activation_reader_feasibility.md).

## Fixed roots and inherited declaring owners

The complete duplicate [v14 class rows](../evidence/deathtrap_parameter_metadata_user_test.log)
at lines66/84 and68/86 supply these exact chains:

| Root token | Fixed class paths in order |
| --- | --- |
| MGR | WillowGame.SkillEffectManager → Engine.Actor → Core.Object |
| CTRL | WillowGame.WillowPlayerController → GearboxFramework.GearboxPlayerController → GameFramework.GamePlayerController → Engine.PlayerController → Engine.Controller → Engine.Actor → Core.Object |

There are eight distinct classes. Load all eight fresh inside the callback using
only these fixed paths. Require exact SDK UClass wrappers, exact primitive Name
labels, the indicated SuperField identity links and terminal None on Core.Object.
PropertySize must be an exact integer0..1048576; child sizes cannot be smaller
than their validated bases. SkillEffectManager requires at least420 bytes from
its captured ActiveSkills offset408/size12. Unknown layouts refuse; no guessed
new property name, package loading or broad object/function enumeration.

Repeat these eight lookups/Name/SuperField/PropertySize checks at the end and
require unchanged callback-local wrappers and scalars. Pointer/wrapper identity
is an observation during this access interval, not a native generation or lease.
No fixed path is synthesized from a discovered field Name.

Before the catalog walk, require exact obj/args/func SDK binding types and the
accepted v18 metadata-only preflight: manager Class, bound object/function and
args._type links, ActivateSkill Name/owner/flags149506/NumParams6/ParamsSize32/
return-offset28/SuperFieldNone, all six ordered parameter descriptors with their
declared classes, and a terminating seventh probe. Reuse the verified stage0
access plan, not `_cr_inspect` or its parameter-value/player reads. Its complete
successful count is98 issued operations, including its existing function/return
descriptor checks; no additional uncounted recheck or return-value read is added.
Existing v18 code remains frozen in
this design. The future implementation must independently measure its gate.

## Walk only the bounded PropertyLink scope

The pinned [binding declarations](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/uobject_children.cpp)
expose PropertyLink, PropertyLinkNext, SuperField, descriptor scalars and
ZObjectProperty.PropertyClass. The pinned
[UStruct source](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/classes/ustruct.cpp)
describes a property-link iterator containing inherited properties, alongside
other build variants. Use explicit bounded PropertyLink/PropertyLinkNext getters
instead of `_properties`, `_fields`, `_find_prop`, `_inherits` or an unbounded
SDK search over a discovered name. This bounds issued link steps, without
claiming to bound casts or a single native getter internally.
That catalog restriction is separate from the fixed schema gate: the accepted
98-operation gate uses `_find`, `_properties`, `_find_prop` and
`_find_return_param` for its already-known function/parameter names. Their native
internals are not bounded by the Python meter. They are metadata helpers, never
engine UFunction invocation or a search over a newly discovered property name.

Require the observed BL2 UField-based property binding shape, rather than
silently translating an FField Owner variant. For each root, save its head and
walk at most512 distinct descriptors. The predecessor edge is root.PropertyLink
for index1 and previous.PropertyLinkNext thereafter. Require SDK ZProperty
instances, reject cycles and duplicate (declaring-owner, Name) pairs, and require
Outer to share one of that root's freshly validated UClass ancestors. Name is an
exact1..128 ASCII letters/digits/underscore string. A shadowed name with a
different declaring owner is a separate declaration, not an ownership alias.

For each descriptor validate exact integer PropertyFlags0..2^64-1,
Offset_Internal0..1048576, ArrayDim1..1024 and ElementSize1..1048576; exclude bool.
Require offset + dimension*element-size within both declaring-class and root
PropertySize. Do not dereference the instance cell at that offset. Snapshot
Name, Outer, flags, offset, dimension, size and PropertyLinkNext. Re-read these
seven fields and the incoming edge after inspection; require unchanged values
and callback-local identities. A null next link is a legitimate terminal probe;
a non-null link beyond512 is PROPERTY_LIMIT, never a complete inventory.

Only exact SDK ZObjectProperty enters the direct-object category. Its
PropertyClass must be an exact UClass; re-read it with the header. Use identity
against the eight already-loaded classes to assign one fixed declaration token:
MGR, CTRL, GEARBOX_PC, GAME_PC, ENGINE_PC, CONTROLLER, ACTOR or OBJECT. OTHER is
counted but its class Name/Outer/path is not followed or published. Other
ZObjectProperty subtypes are counted as unsupported; no subclass fallback,
array Inner, delegate Signature, Bool FieldMask, ClassDefaultObject or instance
value read. Therefore this plan does not exhaust every possible relationship
type, even if the linked list reaches null.

Record at most64 known-token direct-object rows per root. Exact object properties
require element size4 for the observed32-bit schema; a different size refuses.
Dimension1 is SCALAR metadata; larger dimensions are NON_SCALAR metadata and
cannot be a proposed scalar route. No cell or array element is read in either
case. The65th qualifying row produces ROW_LIMIT before buffering it, preserving
partial coverage. Do not guess names to bypass an inventory bound.

Keep the descriptors/edge references and headers callback-local for one final
bounded revalidation pass. Recheck the incoming edge, seven header fields and,
for exact objects, PropertyClass for every visited descriptor. Recheck root
heads and all eight class headers before releasing metadata references. Changed
links/scalars, unknown owners/types, invalid integers, cycles or ambiguous
membership refuse the affected catalog. An unvalidated staged row is discarded;
valid completed-root findings may remain primitive observations with their own
coverage. No record may claim an atomic game-wide schema snapshot.

COMPLETE_LINK means the inspected root's linked list reached null and all
visited descriptors were rechecked within this callback. It does not certify
all Children fields, every property category, game semantics or a data route.
Unknown class declarations, skipped subtypes and limits stay visible. No
relationship, absence of relationship or current manager ownership is inferred
from COMPLETE_LINK or a known declared-class token.

## Finite operation, time, memory and output ceilings

Count each SDK lookup/getter before issuing it. Pure primitive comparisons and
formatting do not consume native-read operations. Use independent new-family
budget/clock state; do not use v18's320-operation budget for this larger walk.

| Stage | Derivation | Ceiling |
| --- | --- | ---: |
| Hook schema gate | Accepted stage0 plan98; reserved cap includes refusal paths. | 112 |
| Root setup/recheck | 8 classes ×4 operations ×2 passes +2 heads ×2 passes =68. | 96 |
| MGR catalog | Non-object: edge+7-header, repeat edge+7-header, final edge+7-header =24; exact object adds three PropertyClass getters =27;512 ×27 =13824. | 14000 |
| CTRL catalog | Same independent bound. | 14000 |
| Total | 112+96+14000+14000. Full planned worst path98+68+2×512×27 =27814. | 28208 |

Terminal None tests are primitive checks of already-metered head/next getters;
there is no unmetered extra descriptor read. Stop before the next operation if
its stage or total ceiling is exhausted. Counters may equal their cap but never
exceed it. Actual future implementation access transcripts must justify exact
branch counts; these are derived design bounds, not observed runtime counts.

Use one metadata attempt per accepting session, two roots, at most1024 visited
descriptor references plus finite eight-class/function-schema locals,128
primitive row dictionaries and two root summaries. Retain no native reference,
iterator, exception, callable or bound method in global state, options, closures
or asynchronous work. The callback closure captures only its primitive epoch.
An inner collecting frame returns validated primitives; it releases all native
locals and SDK exceptions before the outer callback drops obj/args/func/ret and
logs. No arbitrary exception text, repr, address or installation path is output.

Use a2.0-second collector interval and120-second session limit, checked before
each issued operation and at control/callback/output boundaries. Reject clock
regression/nonfinite/negative readings. No background timer is promised. A
single blocking native operation can overrun the interval; the next check
refuses further work. A timeout, reentry or explicit stop abandons unvalidated
rows and preserves the failure. Do not resume a partial walk in another callback
or replay it to obtain completeness.

Set sampling eligibility false before the first attempt, while allowing that
active collector's bounded operations until stop/epoch/time checks fail.
Later callbacks return None without any new payload or metadata access.
Nested callbacks set a bounded reentry finding and return None; any reentry
refuses catalog completion. The new callback must not call v18's value reader.

Limit every project message, including UVH/project prefixes, to512 ASCII bytes.
Compact canonical JSON uses the exact row keys in the checks specification;
maximum128-character Name,64-bit flags and all fixed tokens fit that bound.
Up to128 ROW records, one START, one BEGIN, two ROOT summaries, one END,
eight bounded error/refusal records and64 control records give205 project
records /104960 bytes per session, excluding SDK headers and unrelated startup
text. Further control/error calls cannot append unbounded records or reopen the
collector. A logging failure remains a fixed-code finding; no row retry or
native reread. Message-length refusal must not leak the offending text.
The64 control slots include NOT_STARTED and STOP records. Once those slots or
fault slots are exhausted, keep the collector inert and prohibit another START.
Explicit cleanup still runs without further records. A resolved state that
cannot be logged remains unverified by the offline reviewer; silence cannot
replace the required final resolved STOP. Saturated counters carry explicit
Boolean saturation flags, rather than implying no further callbacks occurred.

## New family and strict review contract

Proposed future version0.2.19, title `UVH v0.2.19 - RELATIONSHIP CLASS METADATA`,
identifier `UVH_RELATION_METADATA_V19_PRE`, prefix `[UVH-REL-META]`.
New START item24 and STOP/REPORT item25 are separate from v18 items22/23 and
passive20/21; item3 remains CANCEL. Preserve every historical option/function
and package. All project families must reject overlap with this new active,
busy, owned or uncertain session; this is later scoped implementation work.
No ARM, manual boost or metadata item4 is part of a prospective run.

Use compact sorted-key JSON after the fixed prefix, canonical nonnegative
decimal integers and exact enums, rejecting duplicate/extra keys or unknown
types. Each record carries a primitive epoch1..2147483647. The companion checks
define the complete key sets for START, BEGIN, ROW, ROOT, END and STOP, allowed
root/class/coverage/reason/outcome tokens, operation caps and counter relations.
ROW ordinal is consecutive per root; owner is an index in that root's fixed
chain, not an instance owner. ROOT records preserve scanned/direct-object/
other-declaration/unsupported-subtype/emitted counts, rechecked count, exact
issued operations and complete/partial/refused coverage. No ROOT can claim
COMPLETE_LINK after a bound or failed recheck. END summarizes every root and
prior failure; a later STOP may resolve handles without erasing those findings.

START registers one fixed PRE hook with Python-only overlap checks and a
pending-registration record set before add_hook. Reject an existing identifier;
never adopt or remove another participant's hook. Failed/uncertain registration
blocks new START until explicit bounded cleanup resolves it. Sample completion
sets the collector inert but does not claim hook removal. Explicit STOP/CANCEL/
disable remove owned handles; busy STOP sets an inert deferred finding and needs
another explicit STOP after the collecting frame ends. At most four removal
attempts per control call; failed cleanup history and uncertain handles remain
visible, including after later success. No automatic rearm or scheduled retry.
Hook removal is separate from native arrays, manual Duration and save recovery.

The later stdlib-only offline reviewer must recognize clipped/current/unknown
new-family markers and reject mixed legacy reader sections. Require final
newline, UTF-8/ASCII project records, exact grammar/order/caps/conservation,
single attempt, coherent per-root coverage, valid row ranges, known declaring
owner/target tokens, no duplicate row identities, and resolved final STOP with
prior failures preserved. Incomplete/refused/limit/silence is a faithful result,
not grounds to repeat a game run. The reviewed scope is text consistency only.
Installation, authenticity, owner protocol, native ownership/lifecycle/generation,
clock/Duration/rank-one and effect readiness are always unestablished/false.

Later reviewer limits:16MiB input,100000 lines,16384 bytes/line,4096 project
records,128 sessions and128 issue summaries. Reject limit excess without a
partial-success verdict. Keep bounded primitive reports and suppress arbitrary
invalid text. Tests must cover exact maximum rows/flags/bounds, null/changed/
cyclic/foreign-owner metadata, subclass/OTHER coverage, terminal/limit distinction,
operation transcripts, mid-operation/time/reentry/stop/logging failures,
registration/removal uncertainty and retries, closure/payload lifetime, mixed/
clipped prefixes and old full frozen reports. Use inert project fixtures only;
never execute or simulate the actual SDK binding or compile its stubs.

## Later file scopes and publication gates

After this design's publication and deliberate acceptance, separately claim a
bounded runtime/package task, including current runtime/version/README, new
metadata collector tests, affected shared overlap tests, package verifier,
instructions/checks and a new original ZIP/default ZIP. Determine the exact
affected tests from actual source before refining scopes. Preserve v18 originals
and manual/grade-zero functions. A separate reviewer task can own a new parser,
its synthetic tests, review instructions and checks. Capture depends on both
reviewed build and reviewer; it needs a new owner approval naming exact ZIP/hash,
title and detailed MAIN MENU → fully loaded MAP → controls → DESKTOP protocol.
One ordinary summon, if needed to deliver the callback, is a separately approved
game action. This design does not authorize that protocol or installation now.

Future schema assessment must accept silence, partial/refused coverage or no
candidate. A known declared class and field Name still need actual relationship
semantics before any instance-value reader. Keep the
[identity/cleanup contract](overclock_identity_cleanup_contract.md) and all
original effect dependencies. Manager ownership, unique active generation/
liveness, clock/Duration consumption, purchased rank-one and exact-original
write/readback/restoration remain NOT_READY. No +15-second effect is delivered.

## Actual static checks

All248 accepted base files,18 original ZIPs,seven entire frozen v12-v18 reports
and snapshot relationships,inventory53/12/5 and34 project syntax files pass.
The actual source/schema,25 pinned inert primary fingerprints/binding anchors,
current full SDK97 context, finite operation/output arithmetic and maximum
primitive row encoding, JSON/local/primary links/exact scopes/whitespace/export
scans are checked in the companion file. The unchanged accepted877 tests and
hosted CI are not rerun for these static design files. Arithmetic/schema checks
are not a native diagnostic or SDK simulation.

No current SDK/stub import/execution/compilation, new raw log or SDK source copy,
runtime/package change, field-value read, engine call, game/install/save/private-
backup/purchase/summon/write/effect/support/merge/release occurs. These two design
files require their own scoped publication approval, complete public-byte
verification and deliberate acceptance. PR47 fulfilled the audit approval.
