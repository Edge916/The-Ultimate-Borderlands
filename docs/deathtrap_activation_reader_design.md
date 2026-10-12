# Bounded callback-local ActivateSkill primitive reader

**READY_FOR_BOUNDED_ACTIVATION_READER_IMPLEMENTATION_REVIEW, under the
ordinary-valid SDK hook-input assumption. Native adapter/effect NOT_READY.**
This is a design for a narrower identifier observation. No reader, hook,
package or owner game protocol is delivered or authorized by these two files.

Accepted parent is `37b53d93fd9f7fb08446b88b55ca223f270b4325` /
[audit PR 41](https://github.com/Edge916/The-Ultimate-Borderlands/pull/41).
Read the actual [audit](deathtrap_activation_reader_feasibility.md),
[v17 assessment](../evidence/deathtrap_callback_definition_name_live_readiness_result.md),
[full capture manifest](../evidence/deathtrap_callback_definition_name_capture_manifest.json),
[current source](../sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py) and
[companion design checks](../evidence/deathtrap_activation_reader_design_checks.json).
The accepted v17 observation is UpshotRobot/OTHER_NAME, with no Skill_DeathTrap
match. Its owner separately reported a natural Deathtrap end. Keep both facts
and the old v16 Name omission unchanged; no alias or retrospective recovery.

## Question and source limits

In a naturally delivered ActivateSkill PRE callback, does the supplied
instigator share the fresh solo Gaige controller wrapper, and what bounded
simple Definition.Name is supplied? Exact Skill_DeathTrap is a primitive match;
another valid identifier is filtered. Neither classification establishes a
definition asset, owned manager, successful activation, live summon, unique
active instance, allocation generation, engine clock, Duration, purchased
rank-one eligibility or exact-original write/readback/restoration interval.
Activation coverage is currently NOT_OBSERVED. Silence and refusal are valid.

The pinned [Python hook binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/hook.cpp)
calls obj,args,ret,func. Return exact non-tuple None on every callback path;
never return a tuple, Block, Unset, a Boolean override or another value. None
adds no block or override and preserves a prior override. A prior Boolean
override may already be converted before Python. Another hook can block the
original or replace its result; same-phase order is unspecified. PRE reports
attempted entry and never establishes successful activation.

ProcessEvent copies all PARAM fields, including this ReturnValue; CallFunction
steps argument expressions before PRE. Native wrapping/downcast also precedes
Python guards. These routes and the corresponding exact source fingerprints
are in the audit. Ignoring ret or other Python fields cannot suppress that
earlier work. This design cannot meet a zero-prior-SDK-processing requirement.
Do not propose a game test under such a requirement.

The complete current [SDK97 discussion](https://github.com/bl-sdk/pyunrealsdk/issues/97)
still contains one unchanged contributor reply. Its hook-time VM/GC guidance
does not certify already-invalid inputs, arbitrary destruction, game-thread
affinity, native generation or installed binary/build/configuration equivalence.
The registration wrapper acquires the GIL on its calling thread; configuration
locking is not presumed. Python exceptions do not contain native pointer faults.
No SDK/stub is imported, executed or compiled; no further support message.

## Complete metadata before parameter values

Use the observed fixed path WillowGame.SkillEffectManager:ActivateSkill at PRE.
START may register through the existing hook-control API, but must perform no
UObject, function, property or player read in its option handler. First natural
accepting callback validates the entire schema from fresh locals. Registration
alone establishes neither schema nor payload coverage.

Require exact SDK UObject/WrappedStruct/BoundFunction binding types for obj,
args and func. Load and name-check the five observed classes anew:
WillowGame.SkillEffectManager, WillowGame.WillowPlayerController,
Engine.Controller, WillowGame.SkillDefinition and Core.Object. Names must be
exact primitive strings SkillEffectManager, WillowPlayerController, Controller,
SkillDefinition and Object. Each lookup is a callback-local SDK metadata route;
no package load, broad object enumeration, asset-path guess or native engine call.

Require obj.Class to share the fresh manager-class wrapper. Resolve its current
ActivateSkill UFunction; func.object is obj, func.func and args._type are that
function, and its Outer is the manager. Check exact Name ActivateSkill,
FunctionFlags 149506, NumParams 6, ParamsSize 32, ReturnValueOffset 28 and
SuperField None. PropertySize is an exact integer in 32..1048576, excluding
bool; its exact loaded value is not established by the capture.

Both preserved v14 rows specify exactly these six ordered direct properties:

| Property | Exact SDK binding / declared class | Flags | Offset | Dimension | Element size |
| --- | --- | ---: | ---: | ---: | ---: |
| SkillInstigator | ZObjectProperty / Engine.Controller | 128 | 0 | 1 | 4 |
| Definition | ZObjectProperty / WillowGame.SkillDefinition | 128 | 4 | 1 | 4 |
| AdditionalSkillTarget | ZObjectProperty / Core.Object | 144 | 8 | 1 | 4 |
| SkillGrade | ZIntProperty / not applicable | 144 | 12 | 1 | 4 |
| StateChangeDelegate | ZDelegateProperty / not applicable | 4194448 | 16 | 1 | 12 |
| ReturnValue | ZBoolProperty / not applicable | 1408 | 28 | 1 | 4 |

For every descriptor require exact binding type, Outer identity, exact Name,
PropertyFlags/Offset_Internal/ArrayDim/ElementSize as exact integers and a
current fixed-name _find_prop lookup sharing its wrapper. For the three object
properties, PropertyClass must share the corresponding loaded class. Bounds
must fit ParamsSize and current PropertySize. Obtain six properties and one
terminating iterator probe; reject absent, reordered, duplicate or extra members.

The pinned [module registration](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/bindings.cpp)
and [metadata type registrations](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/uobject_children.cpp)
expose these property types and _properties/_find_prop/_find_return_param.
Exact ZIntProperty/ZDelegateProperty types replace the old Boolean/object
shortcut; ElementSize is explicitly per descriptor, including delegate size 12.
Do not read Delegate.Signature, a delegate value, Bool.FieldMask or return value.
Metadata shape alone supplies no delegate semantics or Boolean-mask assumption.

The new function-link helper must obtain _find_return_param and validate its
complete ReturnValue descriptor through the same eight-operation scalar
property check. It returns that descriptor only to callback-local code. Initial
iteration must share it at index 5; a final fresh _find_return_param check must
still share it. Every later function-link recheck requires that originally
validated callback-local return descriptor and revalidates its full shape.
No descriptor or function enters reader state or an observer closure.

Before and after each parameter getter, repeat this function/return link check,
that parameter's full property/membership check and PropertySize bound. This
checks the particular member about to be read, alongside current function/return
metadata; it is not continuous validation of every unrelated descriptor or
protection against already-invalid native inputs. Any observed link/schema
change refuses before a further getter. Return descriptor lookup is metadata;
the Python ret argument and all its value semantics remain unread.

## Instigator first, primitive transfer

Read only args.SkillInstigator first. None is NULL_INSTIGATOR. A typed foreign
controller class is OTHER_CONTROLLER_CLASS. Neither branch may read Definition
or its Name. Unexpected Python/SDK types refuse without coercion or repr.

Inside the callback obtain current get_pc(possibly_loading=True); a different
wrapper is OTHER_WRAPPER, with no Definition read. For a local match preserve
the current narrow solo checks: loaded Pawn, CharClass_Mechromancer PlayerClass,
SDK-named Standalone/ListenServer excluding bool, exactly one GamePlayers Actor
sharing pc, and one world.GRI.PRIArray entry sharing pc.PlayerReplicationInfo,
whose Owner shares pc. Type/length/index checks precede reads. No cache or broad
graph traversal. SDK-owned ENGINE/helper globals and internal reads remain
disclosed dependencies; this reader adds no retained native reference.

Only SAME_WRAPPER with those fresh facts may obtain args.Definition. None is
NULL_DEFINITION. Otherwise require exact UObject and Class sharing the fresh
SkillDefinition class, then read Name once. Accept only exact Python str of
1..128 characters from ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.
Do not call str/repr/path/formatter helpers or clip, sanitize, hash or coerce a
bad value. Invalid type/length/character/getter failure yields fixed refusal
without the identifier. SDK string conversion occurs before this Python bound.

The case-sensitive literal Skill_DeathTrap produces DEATHTRAP_NAME; every
other valid identifier produces OTHER_NAME. No case folding, suffix stripping,
UpshotRobot alias, role inference, native route or effect follows a Name.
After current manager-class and final fresh pc/solo comparison plus epoch/
accepting/stop/clock gates, return only primitive labels/counts and that string.
The four absence branches return `-`, outside the identifier alphabet.

The inspection frame and its exception/traceback locals must finish before
emission. Drop obj/args/ret/func in the outer callback before constructing an
EVENT; clear name to `-` on refusal, stop, clock failure and finally. Observer
closure contains only the primitive epoch. No wrappers, properties, function,
ret, exceptions, inspection frame, name history or queued native log arguments
escape. Every callback path returns exact None, including busy, stale and failed
paths. Do not invoke BoundFunction, delegate, GetSkillManager or engine functions;
no ActiveSkills/Duration/ActivatedTime/Grade/points/rank/save reads or writes.
Keep historical/manual/grade-zero functions and separate manual restore intact.

## New finite budget derived from the proposed access sequence

Keep four stages, but replace the old uniform64/total256 meter with stage caps
**112,80,48,80 and total320**. One fixed metadata getter, lookup, iterator probe,
array length/index or explicit get_pc tick costs1; a metadata method costs2
(method getter and call tick). Check accepting/epoch/stop/monotonic time and both
budgets before each metered operation. A failed operation still consumes its
reserved tick; an exhausted meter refuses before the next operation.

These bounds count the explicit reader meter, not all native work. SDK copies,
conversions, metadata lookup/iterator internals, helper/global access and engine
expression processing are separate and unbounded by this meter. They neither
prove native timing nor protect pointers. New implementation must instrument
its actual operation transcript and demonstrate the counts below.

## Operation ledger

| Component | Metered operations | Derivation |
| --- | ---: | --- |
| Object property check | 9 | Outer+Name+four numeric fields+PropertyClass+two lookup ticks. |
| Scalar/delegate property check | 8 | Outer+Name+four numeric fields+two lookup ticks. |
| Base function-link check | 14 | Three wrapper links, current manager lookup2, Outer+Name, four numbers, SuperField, return lookup2. |
| Proposed function/return link | 22 | Base14 plus complete scalar ReturnValue check8. |
| Parameter member recheck | 32 | Function/return22+object property9+PropertySize1. |
| One pc/solo probe | 18 | Explicit get_pc1 plus unchanged narrow solo17. |
| Initial six-property schema stage | 98 | Five class lookup/Name pairs10+manager Class1+function lookup2+link22+PropertySize1+iterator method2+six next probes6+three object checks27+three scalar checks24+terminator1+final return lookup2. |
| Instigator stage, null / typed | 65 / 66 | Two member rechecks64+getter1, then Class1 if non-null. |
| Local session stage, complete | 36 | Two fresh pc/solo probes of18. |
| Definition/final stage, null / named | 66 / 68 | Two member rechecks64+getter1+manager Class1, plus definition Class+Name2 if non-null. |

| Controller / definition | Name | Stage counts | Total |
| --- | --- | --- | ---: |
| NULL_INSTIGATOR / NOT_READ | `-` | 98,65,0,0 | 163 |
| OTHER_CONTROLLER_CLASS / NOT_READ | `-` | 98,66,0,0 | 164 |
| OTHER_WRAPPER / NOT_READ | `-` | 98,66,1,0 | 165 |
| SAME_WRAPPER / NULL_DEFINITION | `-` | 98,66,36,66 | 266 |
| SAME_WRAPPER / OTHER_NAME | Valid identifier unequal to Skill_DeathTrap | 98,66,36,68 | 268 |
| SAME_WRAPPER / DEATHTRAP_NAME | Exactly Skill_DeathTrap | 98,66,36,68 | 268 |

Only these six successful branch combinations are legal EVENTs. Refusal/error
counts are partial prefixes of the interrupted sequence and never exceed the
stage caps or total320; they include attempted failed operations. An exhausted
meter does not silently broaden traversal or emit a normal EVENT. Name/solo/
schema/control failure prevents any subsequent value getter and retains no name.
Return rechecks apply even to null instigator; no definition value is read there.

Keep one fixed PRE hook, 64 accepting attempts, 24 classified events and 120 seconds
checked at operations/entry/control boundaries. No background timer, forced call
or automatic rearm. Busy/reentry counts only a primitive counter without payload
inspection. A busy START refuses; STOP first clears accepting and defers owned
removal until finally. Stale epochs and callbacks after closure return None.

## Wire format, cleanup and separate strict reviewer

Reserve prospective **0.2.18**, title `UVH v0.2.18 - CALLBACK ACTIVATION READER`,
prefix `[UVH-ACTIVATION]` and identifier `UVH_ACTIVATION_READER_V18_PRE`.
Use existing controls22/23 for this replacement reader with explicit activation
START/STOP labels. Other controls remain. These are design constants, not an
installed or game-tested build. ARM/node/manual-duration/other active or uncertain
observer contexts must refuse START using project control state alone.

Keep the accepted v17 ordered primitive grammar and field meanings, changing
prefix, START version/target=ActivateSkill and the stage/cap tables above.
For example, this is a **synthetic design illustration**, not a captured event:

```text
[UVH-BOOST] [UVH-ACTIVATION] EVENT epoch=1 ordinal=1 attempt=1 schema=VALID controller=SAME_WRAPPER definition=OTHER_NAME name=Example_Identifier ownership=UNESTABLISHED ops=268 stages=98,66,36,68
```

Every project record is at most384 UTF8 bytes including project prefix and new
reader prefix, excluding SDK timestamp/source header/newline. The longest normal
EVENT is 317 bytes with a 128-character OTHER_NAME and maximum allowed decimal
widths; a conservative STOP ceiling is 221 bytes. Static checks measure all six
branches/decimal-width boundaries and fixed control forms. Keep the runtime byte
guard and Name limit unchanged, and require full emitted transcripts in the later
inert implementation tests. No name on REFUSED/ERROR/STOP/other controls.

STOP removes only the tuple it positively owns. An uncertain registration is
checked for absence without deleting a foreign tuple. Non-bool results/exceptions/
present-after-removal retain pending identity, block restart and record failure;
a later verified cleanup does not erase failure history. Repeated resolved
STOP/OUTCOME pairs remain legal. CANCEL/disable retain established other-observer/
array cleanup order; no manual Duration restore, refund, save repair or engine
write is added by this reader. No game wrappers are needed for cleanup.

A new separately scoped stdlib reviewer must recognize activation markers and
older `[UVH-CALL` reader markers, including clipped/nested forms. It must reject
old v16/v17 or mixed evidence rather than silently ignoring old prefixes and
reporting zero events. Preserve existing reviewers and all frozen reports.
Require version 0.2.18/ActivateSkill/PRE, strict UTF8/final newline/known bounded
SDK INFO framing, canonical31-bit integers, ordered fields and no extras.
Input limits remain 16 MiB, 100000 lines, 16384 bytes per input line, 4096 records,
128 sessions and 128 retained issues. Fixed partial stage caps are 112/80/48/80 and
sum <= 320; valid EVENTs require the exact six branch counts, Name relation,
epoch/ordinal/attempt sequence and final counters/outcome.

## Reviewer evidence limits

Preserve the corrected trailing-activity rule: TIME/CLOCK/removal activity after
an earlier STOP requires a fresh STOP/OUTCOME. Earlier closure cannot resolve a
later failure; unresolved pending/history blocks restart. Zero attempts is
NOT_OBSERVED, valid filtered names are OBSERVED_FILTERED, and an exact literal
match is OBSERVED_PRIMITIVE, all with ownership UNESTABLISHED. Parser completion
establishes text consistency, not authenticity, protocol, installed bytes,
process exit or native lifetime. The bounded report exports only locally valid
primitive event tokens; at most24 events per session/128sessions gives3072 names.
Do not include malformed input, unrelated lines, exception text or object paths
in issues. Duplicate names establish no generation and distinct names are legal.

## Meaningful later tests and privacy

## Implementation verification

Implementation must prove the proposed meter with actual inert transcripts,
not merely mirror constants: all six success branches; individual interruption
points; six-property order/count/types/flags/owner/class/offset/size/dimension and
return-descriptor changes; poisoned ret/target/grade/delegate values never read;
no engine/delegate/BoundFunction call; one valid Name getter; foreign/null paths
stop before Definition; pc/class/roster/loading/client changes and two fresh
probes; exactNone/epoch-only closure/payload/exception/frame drops before emit;
bad Name type/subclass/empty/129/Unicode/path/line separators/getter failure;
stop during Name read prevents identifier output; separate valid different names.
Check operation cap-before-access, one extra iterator probe, reentry, busy stop,
stale callbacks,64/24/120 limits, clock/log failures, uncertain registration,
foreign identifier, removal failure/retry, restart and CANCEL/disable cleanup.
Run new meaningful tests alongside the accepted 760 unique tests, without
compiling/importing SDK or modifying immutable original packages/captures.

The separate reviewer must accept actual new inert transcripts and reject
adversarial missing/duplicate/extra Name fields, incorrect absence token or
classification, old v17 counts, cap/sum/decimal/epoch/counter/ordering errors,
truncation, mixed/version/prefix/nested frames and unresolved trailing activity.
Prove the old real v17 capture still returns its entire frozen report under its
original reviewer and fails the new one. Do not equate a synthetic transcript
with native input/lifetime proof.

The identifier alphabet excludes paths and line injection but cannot universally
exclude personal text in modded identifiers. No definition asset paths, addresses,
reprs, arbitrary field values, SDK copies or extracted game assets. Surrounding
raw SDK logs may contain startup/object/installation details. Any later capture
needs private preservation and exact-content review plus separate public approval.
Name is transient primitive output only, never a retained history or effect gate.

After this design's public approval and deliberate acceptance, separately refine/
claim implementation scopes, then strict reviewer scopes. Require their actual
tests/package/source provenance/public review before proposing any owner-run
diagnostic. Future instructions must state main menu, fully loaded map, named
controls and desktop exit; a new build and any ordinary summon require exact
owner approval. No request to install, launch, summon or run now. Silence/refusal
is preserved without replay to manufacture coverage. Keep original effect task
dependencies and the [identity/cleanup contract](overclock_identity_cleanup_contract.md)
intact; all owned-manager/unique-active/generation/liveness/clock/Duration/
rank-one/exact-original cleanup and native effect requirements remain NOT_READY.

## Actual design checks

The companion records source AST/static operation arithmetic, both actual v14
schema rows, accepted audit hashes and 18 pinned source fingerprints, current full
SDK97 read/fingerprint, synthetic grammar/Name/size/budget probes and their limits.
All 229 accepted baseline blobs, 17 original ZIPs, six full frozen v12-v17 reports/
snapshot relationships and immutable 53/12/5 inventory remain unchanged. Source
syntax only, UTF8/JSON/links/exactscope/whitespace/known scans are checked.
Static design arithmetic is not an implemented reader or native binding test.

Unchanged 760 tests and hosted CI are not rerun for two design files. No new payload
reader, SDK/stub import/execution/compilation, hook/runtime/package, native call/
flag/Duration/gameplay write, installation/game/save/private-backup/purchase/
summon/effect, outgoing support, merge or release. Exact public export of these
two new design files requires its own owner approval and deliberate review;
PR 41 fulfilled the previous audit approval.
