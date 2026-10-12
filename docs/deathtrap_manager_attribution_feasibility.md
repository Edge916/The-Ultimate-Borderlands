# Callback-local manager attribution feasibility

**METADATA_GAP: no verified controller-to-manager field route in the inspected
inputs. Ownership reader and native effect remain NOT_READY.** The v18 capture
establishes a local-instigator primitive classification and the literal
`Skill_DeathTrap` identifier at ActivateSkill PRE. It does not connect that
instigator to the called-on manager. This audit finds generic SDK property
access support, but no captured game field descriptor that supplies the missing
relationship. It delivers two static files, with no new reader or game test.

Accepted parent is `132f3c628b0560d75f4aeff81ae1062d3f7a1255` /
[assessment PR 46](https://github.com/Edge916/The-Ultimate-Borderlands/pull/46).
Read the actual [assessment](../evidence/deathtrap_activation_reader_live_readiness_result.md),
complete [capture manifest](../evidence/deathtrap_activation_reader_capture_manifest.json),
[raw log](../evidence/deathtrap_activation_reader_user_test.log),
[tested source](../archive/tested_runtime/v0.2.18/__init__.py),
[original ZIP](../dist/UltimateVaultHunterDeathtrapBoost_v0.2.18_folder_install.zip)
and [audit checks](../evidence/deathtrap_manager_attribution_feasibility_checks.json).
Capture PR45, runtime PR43 and reviewer PR44 remain accepted draft branches.
No merge or release is implied.

## What the preserved game evidence declares

All 29 preserved evidence logs were read as bounded UTF-8 text. There are 42
relevant metadata rows across the v12, v13 and v14 logs, plus four older
controller field-name listings. The complete v14 records supply the strongest
typed schema; duplicate records agree. The listings contain GetSkillManager
among function/field names and are visibly clipped. They neither distinguish a
new ownership field nor supply its type, declaring class, flags, offset or link.

| Actual declaration | Available evidence | Attribution limit |
| --- | --- | --- |
| WillowPlayerController:GetSkillManager | v14 lines67/85: FUNCTION, flags132097, NumParams1, ParamsSize4; ReturnValue is dimension1 ZObjectProperty, offset0/size4/flags1408, declared SkillEffectManager. | A typed function return descriptor. Obtaining its value requires an engine function invocation, prohibited here. No backing property or current result was captured. |
| SkillEffectManager ancestry | v14 lines68/86: SkillEffectManager → Engine.Actor → Core.Object, COMPLETE. | Ancestry does not declare a manager-to-controller relationship or its instance value. |
| SkillEffectManager:ActivateSkill | v14 lines70/88: flags149506, six parameters, ParamsSize32, ReturnValueOffset28. SkillInstigator declares Engine.Controller; Definition declares SkillDefinition. | Copied arguments describe the attempted call. A controller argument can be validated without proving that it owns the called-on manager. |
| SkillEffectManager:DeactivateSkill | v14 lines71/89: three parameters, void return; instigator and definition types declared. | No additional ownership relationship or successful lifecycle result follows. |
| SkillEffectManager.ActiveSkills | v14 lines73/91: ZArrayProperty, offset408/size12/flags4194304, dimension1; inner ZObjectProperty declares WillowGame.Skill. | Array metadata only. No payload read or unique membership proof; traversal is prohibited in this audit. |
| WillowGame.Skill.SkillInstigator | v14 lines77/95: ZObjectProperty, offset180/size4/flags0, dimension1, declared Engine.Controller. | Belongs to a Skill, rather than the manager. Reaching a live Skill would require the separately unresolved active-instance route. |

These line references are to the preserved
[v14 metadata log](../evidence/deathtrap_parameter_metadata_user_test.log).
No inspected FIELD row owned by WillowPlayerController, SkillEffectManager or
its Actor ancestor declares a controller/manager link. The manager FIELD rows
are ActiveSkills. This is an absence from the sampled evidence, **not proof
that the game has no such property**. The diagnostic sampled selected names;
it did not exhaust every declared or inherited field.

In the actual v18 source, `obj.Class` is checked against the loaded manager
class; `func.object` connects the hook's bound function to `obj`. The fresh
SkillInstigator/current-controller comparison and sole-player checks connect
the argument to the local player. The `Owner` read is on that player's PRI.
It is not a manager Owner descriptor or value. Neither those checks nor the
literal definition Name provide the missing edge between manager and player.
The current reader has no manager ownership-field getter.

The frozen log remains COMPLETE_LOG_TEXT / exit0: one accepting START, two
SAME_WRAPPER events at lines25/26, Skill_DeathTrap then UpshotRobot, each
268 operations with stages98,66,36,68; one useful/one filtered, two resolved
STOP/OUTCOME pairs and no unresolved reader errors. The owner reported natural
end and STOP23/CANCEL3/full exit separately. PRE text, SDK timestamps and that
report do not supply manager attribution, activation success or engine lifespan.
V17's UpshotRobot and V16's omitted Name remain unchanged; no alias or repeat.

## Installed text is generic SDK support

All 16 installed `.stubs/**/*.pyi` files were read and hashed, never imported,
executed or compiled. None contains SkillEffectManager, WillowPlayerController,
SkillInstigator, GetSkillManager or ActiveSkills. They describe UObject,
UStruct, properties, functions, arrays and SDK facilities rather than generated
BL2 game-class declarations. A generic `Any` getter cannot certify a particular
game field's existence, declaring owner, offset, type or semantics.

The installed SDK launcher text and text members of eight SDK-mod archives were
also inspected without executing them. Controller mentions in compatibility,
networking and save-option hook code are unrelated to manager attribution.
No manager field declaration was found there. Settings, saves, private backups,
game binaries and live game logs were not accessed. The three installed project
files are represented by the immutable v18 capture snapshots; no new current
installation observation is claimed. Installed stub hashes are provenance for
text only, not an installed native binary/build/configuration match.

The generic FField `Owner` annotation describes a reflection descriptor owner.
UObject `Outer` describes object containment. Neither documents player ownership
of a BL2 SkillEffectManager. Actor ancestry alone does not justify guessing a
manager Owner field, invoking it, or giving its value a gameplay meaning.

## Property access and engine invocation are different boundaries

Seven additional official source files were fetched at the pinned revisions,
checked against pinned Git blob IDs, UTF-8 decoded and hashed. The 18 accepted
activation-design source fingerprints were independently rechecked. No SDK
source copies are included in the public payload.

At pyunrealsdk `c72c5558473bfa1f1cbc9c9113efb2a02251e656`,
[UObject binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/uobject.cpp)
routes an ordinary field getter through reflected field lookup and typed
access. Direct `_get_field` bypasses field-membership validation; it cannot be
used to turn a guessed descriptor into a safe access. Neither route confers
native lifetime or semantic ownership.

The [field dispatcher](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/property_access.cpp)
distinguishes properties from non-property fields. A UFunction produces a
BoundFunction. Merely inspecting a descriptor is different from calling it;
[BoundFunction invocation](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/bound_function.cpp)
releases the GIL and invokes engine code. GetSkillManager is in the latter
category. Its name and declared return class do not authorize a call or reveal
an equivalent data property. No UFunction, delegate, formatter, package loader
or other engine helper was invoked.

At unrealsdk `b1852aa440277afcce8a13566b5487aeae5a7ae9`,
[UStruct lookup](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/classes/ustruct.cpp)
searches reflected lists. Field iteration can move through superclass children;
the property-link implementation includes base properties. The compiled
iterator variant and actual descriptor links remain material. Generic inherited
lookup support does not establish any particular inherited game declaration.
SDK lookup/iteration executes native metadata code if used in-game, even when
it does not invoke a game UFunction. Python operation bounds would not bound
each helper's internal list traversal.

The [property getter](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/prop_traits.h)
uses descriptor offset and element size to locate a cell; the
[object-property trait](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/properties/zobjectproperty.cpp)
reads its stored UObject pointer. It does not validate that pointer against the
declared class on get, or establish the pointee's lifetime or relationship to
the caller. The setter has a separate class check, which does not justify
reading or writing a candidate here. A declared PropertyClass is type metadata,
not a native lease or ownership fact.

## Callback-local assumptions remain limited

The accepted [activation source audit](deathtrap_activation_reader_feasibility.md)
and [design](deathtrap_activation_reader_design.md) still apply. Exact non-tuple
None requests neither blocking nor a new return override; an earlier override
can be converted before Python and remains in place. Other hooks can block or
override, with no same-phase priority or execution-outcome guarantee.

ProcessEvent copies PARAM cells before PRE. ReturnValue flags1408 include
PARAM0x80 and RETURN0x400; return, target, grade and delegate processing can occur
before Python validation. CallFunction skips return during extraction but steps
argument expressions before PRE. Native casts, field lookup, pointer reads and
helper internals are outside the Python operation meter. Ignoring a Python
parameter does not prevent that SDK processing or protect an invalid input.

The complete current [SDK97 discussion](https://github.com/bl-sdk/pyunrealsdk/issues/97)
was read through all official API pages and remains closed/completed with one
unchanged [contributor reply](https://github.com/bl-sdk/pyunrealsdk/issues/97#issuecomment-6108546422).
Its hook-time VM/GC guidance does not provide a reference lease after return,
generation identity, arbitrary destruction exclusion, already-invalid-input
protection or a manager ownership relationship. The SDK acquires the GIL on
the calling thread; this is not a game-thread guarantee. Optional function
locking defaults false in source, and installed native configuration/build
equivalence remains unverified. No outgoing support message was sent.

Any later candidate would need an evidenced exact field name, declaring class,
property kind, dimension, flags, offset/size, declared object class, inheritance
and descriptor/member links, with explicit access semantics. A future design
would need fresh validation before and after a bounded getter, callback-local
reference comparisons, refusal on missing/null/foreign/replaced/ambiguous data,
reentry/stop/time/operation limits and primitive-only reporting. Such comparisons
remain conditional observations under valid ordinary SDK hook input. Python
`is`, addresses, names and observer epochs cannot become allocation generations
or post-return cleanup authority. References, exceptions, arrays, functions and
closures carrying native payload must not escape the callback.

No such candidate field route is established here, so this audit does **not**
support implementation of a manager ownership reader. No new field was read,
hook installed, array traversed or object enumerated in the engine.

## Remaining gap and next bounded work

The immediate blocker is **missing actual reflected controller/manager
relationship metadata and its semantic evidence**. A separately scoped
metadata-only discovery design is the next supportable question: whether a
bounded inspection of the already-evidenced controller and manager class
descriptors could obtain relevant declared fields and inherited declaring
owners without instance-value reads or engine invocation. This is a design
question, not approval to sample, install or run. It must accept incomplete or
absent coverage and avoid remembered property names, whole-object enumeration,
callable substitutes and automatic retries. If the data route is unsupported,
the result must remain a documented gap.

Even future attribution would not establish unique active Deathtrap membership,
native generation/liveness, successful activation/deactivation, engine clock,
Duration consumption, purchased Overclock rank-one eligibility or exact-original
write/readback/restoration. The [identity/cleanup contract](overclock_identity_cleanup_contract.md),
manual-duration separation, grade-zero guards and original effect dependencies
remain intact. Native adapter and +15-second effect stay NOT_READY.

## Actual checks and publication boundary

Fresh full v18 CLI output equals the entire frozen manifest report. All 246
accepted base blobs, 18 original versioned ZIPs, seven complete frozen v12-v18
reports and snapshot/ZIP relationships, and immutable inventory53/12/5 pass.
Source AST confirms the unchanged current getter boundaries, exact None,
epoch-only closure, payload drops and historical manual/grade-zero functions.
All 34 project Python files pass syntax checks; no SDK/stub compilation occurs.
Bounded installed text, 25 pinned source fingerprints/anchors, JSON, local and
primary links, exact two-file scope, whitespace and known export scans pass.
The unchanged accepted877 tests and hosted CI were not rerun for static files.

No new raw log, SDK/stub source copy, game asset, private file, runtime/package
change, live SDK execution, native binding simulation, gameplay, installation,
save/private-backup action, purchase/summon, flag/Duration/point/rank write,
support message, effect, merge or release occurs. Exactly this document and its
checks require a new scoped public-export approval, public-byte verification
and deliberate review. PR46 fulfilled the prior two-file assessment approval.
