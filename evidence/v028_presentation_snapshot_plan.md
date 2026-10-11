# v0.2.8: bounded read-only presentation comparison

## Evidence driving the change

v0.2.7's live trace captured all nine skill/function buckets. Overclock's
GetSkillDescriptionForGrade return was empty for Grade1/modifier0/HTML=False;
MorePep and Myelin returned bonus text for the same inputs. Sampled FINAL
points/ranks remained unchanged, observers were removed and native rollback
passed. See v027_live_focused_state_result.md. This difference does not prove
the cause of the rendered orange prompt's absence or a purchase failure.

At design time the inert constructor did not populate SkillEffectPresentations
and its actual default array remained unobserved. v0.1.5's real log shows four MorePep and one
one-rank ExplosiveClap AttributePresentationDefinition references. v0.2.8
compares the three current owned target arrays and inspects bounded raw class
property metadata to identify a next safe display-data investigation.
No presentation instances are copied, evaluated or changed.

## Deliberate scope

Button 4 now routes to inspect_overclock_presentations, instead of the older
general purchase snapshot. It remains a synchronous explicit diagnostic with
no observers. Other options remain in place; total stays 19. The old purchase
function remains in source and regressions, with only its version label changed.

Four new functions: _presentation_metadata, _presentation_class_fields,
_presentation_details and inspect_overclock_presentations. Of 68 v0.2.7
functions, 64 are AST-identical, including constructor/insertion/rollback,
_upgrade_state, UI/current-session guards, observer callbacks/cleanup and the
verified manual duration prototype. The other four change version labels only:
inspect_overclock_purchase, start_upgrade_trace, start_ui_trace,
start_skillstate_trace. Factory metadata and button 4's route/label change.
No new global capture state, import-time game access or automated gameplay.

## Reflection and payload checks

Installed SDK stubs were read as documentation only. UClass._find_prop is SDK
property reflection; _properties iterates raw descriptors; UObject._path_name
is an SDK identity helper. WrappedArray is the documented SDK array type.
The [primary Python array binding](https://github.com/bl-sdk/pyunrealsdk/blob/master/src/pyunrealsdk/unreal_bindings/wrapped_array.cpp)
also exports that wrapper. Its _type attribute's array/inner semantics were
not established for the installed commit; this design never reads or changes
_type or relies on a guessed interpretation. Exact installed-commit source
was unavailable through browsing. No stubs were executed or packaged.

Reuse unchanged _upgrade_state with a local baseline: current owned Gaige/
controller/pawn/world/PRI/tree, both sole-player rosters, exact inert patch,
unique registrations/indices/tier, grade-zero node and known nonnegative PRI
points/ranks. Refuse while initialization/loading/UI/upgrade/focused traces
are active or failed hooks remain. No observer cleanup is performed by button
4; existing CANCEL/disable remain the restoration path.

Require each target's exact shared SkillDefinition UClass identity. Resolve
only SkillEffectPresentations via _find_prop; do not scan the skill class.
Require property Name, Outer==that class, ArrayProperty with ObjectProperty
Inner, actual UClass named AttributePresentationDefinition. Both descriptors
need dimension1, exact integer flags in [0,2^64), no parameter/out/return bits
(mask0x580), exact integer offset0..1048576. These structural checks are not
a previously game-verified fixed offset/flag schema; actual native matches
remain a live-test question. Unknown metadata refuses payload reads.

Recheck current state after metadata and before array access. Require an actual
SDK WrappedArray. Read length; refuse >256 before entries. Log count, sample
size and explicit cap. Inspect at most four references per target, each an
actual SDK UObject with Class identical to the declared presentation class.
Shared references need not be child objects of the skill. Only call SDK path
identity after class/state checks; path must be nonempty exact string <=384,
logged with repr escaping. No object repr/owner graph or instance display/
attribute/struct/array/function values are read. Recheck state before/after
reference access and array length/definition class after sampling.

Reflect the common presentation UClass once per button invocation, at most
16 property descriptors with one bounded lookahead. Reject duplicate/absent/
oversized field names, missing/non-property kinds or untyped/out-of-bound
flags/offset/dimensions. Log raw name/type/flags/offset/dimension and bounded
metadata type names for referenced class/struct/enum/inner; never their payloads.
Metadata names/skill labels <=96, error detail <=180, object paths <=384.
No scalar presentation values are guessed; decide any value allowlist from
the actual native metadata after this run.

## Reporting and refusal

Each of three target summaries distinguishes VERIFIED array count/reference
sample from UNAVAILABLE data. Empty is count0, never a substitute for a failed
read. Metadata has separate COMPLETE/CAPPED/UNAVAILABLE status; an unavailable
class metadata iterator does not turn a verified count into zero. The function
returns True only if all three arrays/reference samples verified; this is not
proof that all metadata or all references beyond the four-entry cap were read.

Current-state failures abort before proceeding to another target. Each call
samples its own baseline; no cross-call point/rank claim. FINAL compares the
complete state, prints points/ranks unchanged_from_start=True only on success,
then END verified_arrays=N/3 observers_added=0. Metadata/payload errors report
partial data; state changes cause ABORT, never repair/refund. The snapshot
does not buy/save/load/evaluate/copy effects/constraints, register/remove hooks,
invoke native query/formatting functions or override any return/text.

## Local verification and one game test

108 unique local mocks passed, including 18 new presentation tests. New cases
cover empty/nonempty verified arrays, missing/invalid metadata, wrong SDK/
native classes, wrong wrappers/references, absent/oversized paths, shared refs,
four-reference/16-property bounds, oversized/unreadable arrays, metadata errors,
changed points/ranks/class/array lengths, observer overlap, no mutation/native
invocation, and preserved cancel/disable rollback. They do not establish
engine behavior or the cause of missing text. Runtime syntax compilation passed.

Before shipping: exact three-file single-folder ZIP integrity/source match and
isolated 19-option import without game access. Preserve seven tested ZIPs,
v0.2.7 log and tested source snapshot unchanged. New v0.2.8 ZIP gets its own
filename; no game installation is performed by Codex.

Test: close BL2, install only this mod from v0.2.8 ZIP, verify exact title
UVH v0.2.8 - OVERCLOCK PRESENTATION SNAPSHOT. Main menu 1 ARM, Continue as
backed-up Gaige alone Offline, in map 4 INSPECT once, 3 CANCEL/RESTORE, fully
exit and report done. No Skills highlighting or observer START needed for this
snapshot. Do not spend points or use any other diagnostic/boost/respec/travel.
On partial/error: cancel and exit; never force a native function/purchase.
Preserve/hash the final log before relaunch. Verify three summaries/raw metadata,
sampled final unchanged state, zero owned observers and RESTORE result=True.
No v0.2.8 game result yet. The node remains inert; later purchase/refund/
persistence/automatic effects/co-op/release need separate scope and recovery.

## Completed artifact checks

108 tests passed, including all 90 prior tests. Runtime syntax compilation,
isolated packaged import with 19 options and no game access, exact single-mod
folder/three-file layout, ZIP integrity and byte equality to current source
all passed. No additional runtime changes after these tests.

Created dist/UltimateVaultHunterDeathtrapBoost_v0.2.8_folder_install.zip
exclusively, without overwriting any versioned artifact. It is 30,016 bytes,
matches the checked default ZIP byte for byte, and passed separate integrity,
layout/source and packaged syntax checks. SHA-256:
`93b2ae7f8cae8412d3af6637d1c6e0739cadf7b6b0cc07b3961c5758674940c2`.

Runtime SHA-256:
`4dae701cc263c3d4be1fb8b602f0f5d0987ad173b2cfd477bd784a7ddeb706a5`.
pyproject SHA-256:
`0393dfc7317910731465da0a19aa62f5bb5b4bf777b5c8e8c4b6315de8cd12b1`.

Final AST checks confirmed 64 prior functions unchanged and the other four
changed only version strings, plus four new functions. All seven tested ZIP
hashes, the v0.2.7 preserved log and tested-runtime snapshot were checked
unchanged. No game files were installed/edited and no v0.2.8 engine behavior
was established at build time. User installation and the 1,4,3 test were pending.

## First live run review

See v028_live_presentation_result.md. Installed three files matched the
original v0.2.8 ZIP. Live insertion/visibility and native-array restoration
passed, with zero observers. The screenshot shows0/1, one skill point and
[Enter] Spend Point; that rendered input hint is not orange bonus text or
proof of eligibility/purchase. The user confirmed they did not select item4.
Zero [UVH-PRESENT] messages means the presentation diagnostic was not run;
schema/counts/references/metadata and snapshot FINAL comparison remain unknown.
Collect this omitted step using the already verified v0.2.8 in a fresh process,
selecting item4 in mod options. Preserve the retry log under a distinct name.
All eight original versioned ZIP hashes/integrity were checked unchanged;
exact tested files are archived in archive/tested_runtime/v0.2.8. The previous
v0.2.7 snapshot/log remain intact. Runtime/pyproject are frozen. Documentation
updates rebuild only the default ZIP; a new runtime/version is unnecessary.

## Completed live presentation inspection

The fresh retry is preserved as v028_presentation_retry.log, with review in
v028_live_presentation_retry_result.md. Two completed calls verified arrays
Overclock0/0, MorePep4/4 and Myelin2/2; all reference samples covered their
arrays, while class metadata was explicitly CAPPED after16 properties.
All three loaded array/inner/class schemas were accepted. Both calls sampled
PRI points=(1,0)/ranks=(0,0,0) unchanged at FINAL, verified_arrays=3/3 and
observers_added=0. Cancellation restored original arrays/cells with observers0;
repeat cancellation found no patch and the process was closed. No ERROR/
Traceback, UNAVAILABLE or ABORT. Installed files matched the original ZIP.
The empty candidate array is now verified, but causation/eligibility/effects
remain unproven. Next design uses the observed string/display field metadata,
not another identical count test. Runtime/all eight original ZIPs remain frozen.
