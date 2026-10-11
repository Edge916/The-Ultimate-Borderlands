# Codex instructions for the Ultimate Vault Hunter Collection

## Goals and priorities

1. Focus on a reliable **Borderlands 2 / Gaige skill-tree extension**, not the enormous cross-game vision yet.
2. Preserve the **actually game-tested** manual Deathtrap +15s prototype until an improved replacement has been verified.
3. Prototype a **new**, independently named `SkillDefinition` for "Deathtrap Overclock"; do not silently overwrite an existing Gaige skill or mutate the save.
4. Preserve v0.2.1 as the **first user-confirmed visible native node**. Its real log verifies pre-initialization insertion, runtime registration and native-array rollback. The original visibility objective is met for this solo test; a one-point purchase to1/1 is now user-reported (v0.2.10), while controlled transaction/save verification, persistence and the node's +15-second effect remain later milestones.

## Environment / packaging

- Windows PC, Borderlands 2 on Steam, SDK mods live under `Borderlands 2\sdk_mods`.
- `unrealsdk v3.2.0`, `pyunrealsdk v1.10.0`, Willow2 PythonSDK; Python in-game imports `mods_base`, `unrealsdk`.
- Install convention: build a ZIP with ONE `UltimateVaultHunterDeathtrapBoost/` folder containing `__init__.py`, `pyproject.toml`, README; user deletes/replaces the existing folder and restarts BL2. Keep one installed project mod, not many test mods.
- A mock test's success cannot establish real-engine behavior. Log fields may be SDK wrapper types (`WrappedArray`, `WrappedStruct`) and methods may behave differently in engine.

## Critical verified findings

- User reported Gaige Deathtrap lasted longer after setting **live active skill instance** `Skill_DeathTrap.Duration: 60.0 -> 75.0` while summoned; original `DurationBaseValue=60.0` remained unchanged. See `evidence/v011_duration_write_verified.log`. User's lifespan observation is conversational feedback, not stopwatch measurement.
- The action skill object `Pawn.MyActionSkill` is NOT where the working Duration field was found; actual active object lives in `pc.GetSkillManager().ActiveSkills` where `Definition.Name == 'Skill_DeathTrap'`.
- Gaige `PlayerClass.SkillTreePath = GD_Tulip_Mechro_Streaming.SkillTree.SkillTree_Mechromancer`. v0.1.8 found this top-level definition briefly at main menu, then it became inaccessible; in-map lookups found no top-level tree. Do not assume continuous asset availability or a confirmed garbage-collection cause.
- In-game Gaige branch object `GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble` and its `Layout_LittleBigTrouble` are accessible. Six tiers. Tier 0 original skills `MorePep`, `Myelin`, with occupancy `[True, False, True]`.
- v0.1.6 created a new `SkillDefinition` via `unrealsdk.construct_object`, reported the native Tier0 `[MorePep, DeathtrapOverclock, Myelin]` and layout `[True,True,True]`, but the user explicitly reported **NO visible skill-tree node**. Do not claim success based only on `INSERT VERIFIED` log.
- Tier 4 has two skills but occupancy `[False,True,False]` in one read; don't generalize that every tier's layout occupancy mirrors the skills array.
- v0.1.7 real log: three main-menu attempts returned no accessible branch/layout and aborted without insertion. See `evidence/v017_main_menu_assets_unavailable.log`. This does not test the UI caching hypothesis.
- v0.1.8 real snapshots found native assets briefly at menu, missing two seconds later, and branch/layout plus `pc.PlayerSkillTree` (class `PlayerSkillTree`) in Gaige's map. Trace found zero candidates, registered no observers and captured no calls. See `evidence/v018_assets_transient_playerskilltree_found.log`.
- v0.1.9 real trace registered 16 observers, captured 20 events and removed all observers. At `WillowGame.PlayerSkillTree:Initialize` PRE, Gaige's controller had no pawn, the native assets and exact `args.SkillTreeDef` were available, and `obj.Branches` was empty. POST had four branches. Later UI calls included `InitializeGFxHelper` and `SkillTreeGFxObject:extInitTree`. See `evidence/v019_live_tree_and_init_trace.log`. No node was inserted in that run.
- v0.2.0 real log: the Gaige PRE callback reported `NetMode=2` and aborted because the old guard required numeric 0. No candidate construction or insertion occurred; all observers were removed. The user reported no visible node. See `evidence/v020_netmode_guard_aborted_no_insertion.log`. This run did not test cache/UI insertion and does not establish whether any other player was connected.
- v0.2.1 real game: user reported **"done it worked!"** after the requested visibility test. PRE verified listen_host (`NetMode=2`), one owned local player and one owned roster player. One inert candidate entered the engine's 39-skill runtime tree at index 14/tier 7, grade 0; both original first-tier skills remained. All observers were removed. CANCEL verified original arrays restored. See `evidence/v021_native_node_visible_and_restored.log` and `evidence/v021_visibility_confirmation.md`. This confirms visible-node success in one solo run; it does not establish purchases, persistence, effects or co-op behavior.
- The v0.2.1 guard accepts SDK-named Standalone/ListenServer only when `ENGINE.GamePlayers` contains exactly one local player owning the current controller and `WorldInfo.GRI.PRIArray` contains exactly its owned PRI. Missing/loading data, extra players, clients and dedicated servers fail closed. Recheck after initialization; do not bypass failed evidence. Run Offline. Snapshot rollback restores native arrays, never manually rewrites player caches/indices; restart BL2 after every test. Preserve the tested versioned ZIP unchanged; documentation-only updates may rebuild the default ZIP without changing runtime code.
- v0.2.2 real diagnostic run: two menu attempts refused inspection; four in-map snapshots kept PRI points 1/0 and Overclock rank 0/1, with both originals present. Metadata reflection worked; cancellation restored original arrays and observers were zero. User then reported **"0/1, with no upgrade prompt"**. See `evidence/v022_purchase_diagnostic_result.md`. This does not prove a purchase defect; native skill prompts have not been compared. Raw fields include locals, and SkillType formatting did not expose the enum value. Keep both tested versioned ZIPs untouched.
- v0.2.3 tested baseline: improves only read-only button 4 with enum names/values, LockedSkillDetailStr, bounded SkillConstraintData fields and upgrade-UI metadata priority. All 48 established v0.2.1 functions remain unchanged, including constructor/insertion/rollback, solo guard and manual duration functions. No new hooks, native gameplay calls, loads or writes. **41 mocks plus a live diagnostic run:** four snapshots kept points 1/0 and Overclock rank 0/1; all three definitions have Passive/value0, SkillClass=Skill and locked detail '<Locked>'. Native constraint fields and UI metadata were read successfully, cancellation restored arrays and observers were zero. The user confirmed the blue title and inactive prototype description. See `evidence/v023_live_diagnostic_result.md`. Preserve the tested v0.2.3 ZIP too. Do not evaluate/copy constraints or infer purchase eligibility/callable signatures from metadata; CanUpgradeSkill's return descriptor is ESkillTreeFailureReason, not a Boolean.
- The intended v0.2.3 follow-up run actually used v0.2.2: both its log headers and installed pyproject/runtime hash confirm this. Four snapshots again kept points/ranks unchanged and cancellation restored native arrays with zero observers. The user clarified that Overclock looks like the other skills and they meant absent orange rank-upgrade text, which they attribute to its one-rank cap; that is not proof of purchase failure. See `evidence/v022_repeat_rank_preview_clarification.md`. The later v0.2.3 run resolved this mismatch without a runtime change; always verify the MODS title before arming.

## v0.2.4 baseline (live setup/cleanup; zero query calls)

v0.2.4's tested package: buttons 5/6 manually start/stop two bounded
POST observers of normal CanUpgradeSkill/GetSkillUpgradeCost calls. 57 local
mocks passed. The live run verified setup/stop/restoration, but callbacks=0.
The user confirmed highlighting all three skills; eligibility/cost are unanswered.
See evidence/v024_live_observer_result.md. Do not repeat the same trace or force
calls by buying. UI callback ownership/return handling remains mock-tested only. Require loaded function metadata
matching v0.2.3, current owned Gaige/tree/pawn, both sole-player rosters,
known unchanged PRI points/ranks/indices and an inert grade-zero candidate.
Require SkillTreeGFxObject.WPCOwner==pc and CurrentSkill among the three target
definitions. CurrentSkill_Rollover is reported separately, never substituted.
Use actual POST ret: SDK ESkillTreeFailureReason member for eligibility, exact
nonnegative int for cost. Unknown state refuses capture. Never invoke/override
the functions, edit arguments/returns or treat the failure enum as Boolean.
Limits: 24 captures, 2048 callback attempts, two copies per result; 90 seconds
checked on the next call. STOP/CANCEL/disable/error/session change/limits remove
observers. Failed removals retain inert hooks for retry. STOP checks final state.
Of the 48 v0.2.1 functions, only cancel_init_node changes, adding observer cleanup;
the snapshot's version header also changes from v0.2.3. Insertion, solo guard,
rollback, manual duration and other established functions remain unchanged.
See evidence/v024_observer_plan.md. Preserve all tested versioned ZIPs.

## v0.2.5 tested baseline (live UI selection/restoration passed)

Buttons 7/8 explicitly start/stop discovered SkillTreeGFxObject navigation and
refresh observers plus bounded direct owned-UI snapshots at start/stop. Use
loaded canonical function metadata only: no hardcoded undiscovered hook paths.
Up to 10 functions, PRE and POST_UNCONDITIONAL, 48 events, 2048 attempts, two
copies per state, 90-second expiry checked on the next call. POST_ANY labels
do not prove execution if another hook blocked the call. No args/ret reads,
native invocation, overrides, package loads or observer game-state writes.
Reuse the unchanged v0.2.4 current Gaige/tree/session/points/ranks/index/inert
guard. Require exact UI class and WPCOwner==pc before reading its selection.
Validate each selected/hovered definition's unique owned runtime entry/index;
unknown selection is labelled unavailable/unverified, never guessed. Report
UI points and target tier unlock state as direct reads, not eligibility.
Object inventory scans <=32 and prints <=4 owned UIs. Stop/cancel/disable/errors/
changes/limits clear capture before removal; failed hooks stay inert for retry.
Do not combine with upgrade/init traces. CANCEL gains UI cleanup, the snapshot
version header changes and legacy upgrade START gains a mutual-exclusion guard
plus version label. All other v0.2.4 functions stay AST-identical, including
_upgrade_state, insertion/rollback/manual duration. 71 mocks/package checks;
v0.2.5 has a live result: 14 events/16 callbacks, owned UI selection of Overclock,
MorePep and Myelin, UI point=1 and tier unlocked=True, final PRI points/ranks
unchanged, observers zero and native arrays restored. Inventories outside
Skills scanned one object but found zero owned views; callback data still
verified a live owned UI. See evidence/v025_live_ui_trace_result.md.
The ten-function selection included four artifact functions and omitted
discovered PostNav/input/info/point-display helpers. Do not treat their absence
as zero calls: they were not hooked. Next runtime should prioritize those
loaded core functions and exclude artifact/equip candidates, with a crowding
regression. Cost/eligibility/purchases/effects remain unverified.
Keep all five tested versioned ZIPs unchanged.

## v0.2.6 tested baseline (live core helpers, event limit and restoration passed)

v0.2.6 changes only _ui_candidates behavior: exclude artifact/equip names before
reflection and prioritize six loaded core helpers (PostNav, Navigate,
HandleInputKey, UpdateInfoBox and both Flash_SetSkillPointProperties variants)
plus Init and the proven Nav_Down/Left/Right anchors within the same ten-function
cap. extInitTree and other discovered methods are fallbacks when core paths are
absent; priority never invents a path. Log explicit SELECTED paths as well as
bounded candidates/metadata. Three functions change version labels only;
the other 59 v0.2.5 functions are AST-identical, including insertion/rollback,
solo/unchanged-state guards, UI callbacks/cleanup and manual duration.
All bounds/ownership/passive/no-args-ret-read requirements remain unchanged.
74 local mocks/package checks passed, including the actual 24-name live
crowding regression (failed before the fix), missing/foreign metadata, and
artifact/equip exclusion before reflection. Live result: all six core helpers
produced events; 48 events/51 callbacks reached the configured event bound.
MorePep and Overclock were selected; node UpdateInfoBox PRE/POST_ANY captured.
The trace stopped before Myelin; later highlights are unobserved, not failed.
UI point=1/tier unlocked=True; FINAL PRI points/ranks unchanged, all hooks
removed and native arrays restored. See evidence/v026_live_core_ui_result.md.
UpdateInfoBox metadata includes locals, not verified args; no prompt/cost/
eligibility data was read. Next useful design should target native skill-state/
info display and prevent incidental input traffic starving the event budget.
GetSkillState was discovered in v0.2.3; revalidate loaded metadata/SDK outputs
before passive reads, never invoke it. The v0.2.7 runtime below now provides
the focused observer for the next test.
See docs/NEXT_CODEX_TASK.md. Keep all six tested versioned ZIPs unchanged.

## v0.2.7 tested baseline (all targets captured; empty node grade description)

New buttons 9/10 opt in/out of three POST observers: PlayerSkillTree:GetSkillState
Boolean ret, SkillTreeGFxObject:GetSkillDescriptionForGrade input/actual string
ret, and UpdateInfoBox target UI view. Verify loaded canonical classes/outers/
paths and exact previously logged parameter/return metadata before registering.
Reflect <=16 function fields/<=12 raw native state struct descriptors, scan
<=30000 functions. SDK source confirms args are copied inputs; OutSkillState
is not a finished output and must never be read. No tuple reinterpretation or
args.ReturnValue/UpdateInfoBox-local reads. Ret can reflect another hook's override.
Do not equate a query Boolean with eligibility or preview text with rendered UI.

Reuse _upgrade_state unchanged. Require exact current owned tree before state
input/ret; exact UI/WPCOwner and validated current/rollover before description;
args._type matches verified function, input SkillDef is one of the three,
PlayerOwner==pc. Grade 0..128/modifier -128..128 exact ints, bIncludeHTML exact
bool, ret exact bool/string. Clip descriptions at 512 characters and log length.
UpdateInfoBox has no input/ret reads. Four captures per function/target, two
per distinct result, <=36 actual captures within the unchanged 48-event limit.
All callbacks count against 2048 attempts/90 seconds checked on calls.
Unrelated traffic uses no capture slots. No native invocation, overrides/blocks,
edits/loads/gameplay writes. Stop/cancel/disable/error/change/limits clear context
before removal; failed hooks stay inert/retryable and refuse other traces.
CANCEL adds focused cleanup; old UI/upgrade/loading STARTs gain mutual exclusion
and version labels; snapshot changes version label. 58 other prior functions
are AST-identical, including insertion/rollback, guards, old callbacks/manual.
Five new functions, 19 factory options; import remains inert.

90 local mocks/package checks passed, with poison copied-out/local reads,
actual bool/string returns, schema/reflection/bounds, replay of v0.2.6 nested
navigation, per-function/target quotas, foreign/stale/refusal and cleanup.
Live result: all nine function/skill buckets captured, 16 results/110 callbacks
and 94 aggregate skips. All target GetSkillState returns were True. Grade-one
description returns were empty for Overclock (two observations), length79 for
MorePep and length49 for Myelin, with modifier0/HTML=False. UI points=1 and
tier unlocked=True; sampled FINAL PRI points=(1,0)/ranks=(0,0,0) unchanged.
Explicit STOP removed all hooks; CANCEL restored original arrays/cells and
repeat cancellation found no patch. No abort/limit/error. See
evidence/v027_live_focused_state_result.md. Preview/query data still does not
prove rendered orange text, eligibility/cost or purchase failure.

All seven tested versioned ZIPs were recovered from the Recycle Bin after the
user confirmed deleting them. Every recovered original hash matched its prior
record; no versioned ZIP was rebuilt. Preserve all seven unchanged. A tested
three-file source snapshot also lives in archive/tested_runtime/v0.2.7.
Runtime code and installed files matched the tested ZIP at review; only docs
and the default ZIP change. v0.2.5/v0.2.6 logs remain unchanged.

## v0.2.8 tested baseline (live presentation counts and restoration passed)

Button 4 now routes to the focused synchronous presentation snapshot; total
options stays 19. No new observers/global capture state. Resolve only the loaded
SkillDefinition UClass SkillEffectPresentations property via SDK _find_prop.
Require exact target/shared class identity, array owner/name, ArrayProperty/
ObjectProperty inner, actual AttributePresentationDefinition UClass, dimension1,
bounded exact integer flags/offsets and no parameter/out/return bits.
Only then read SDK WrappedArray count (<=256) and <=4 actual UObject references
with exact declared class; log SDK path identity <=384, never object repr/graph.
Reflected presentation metadata is <=16 raw properties (one bounded lookahead),
once per common class/call, type names/labels <=96. No instance scalar/struct/
array/attribute/function values, copied presentations or native formatting calls.
Do not infer WrappedArray._type's semantics; it is not used.

Reuse _upgrade_state unchanged with a local baseline. Recheck before/after
target reads and reference access; refuse overlapping initialization/loading/
UI/upgrade/focused traces or failed hooks. Array/metadata unavailable is distinct
from verified zero; metadata COMPLETE/CAPPED/UNAVAILABLE is separate from
array/count/sample status. State change aborts before another target; FINAL
unchanged only after full state comparison. No repair/refund/writes/hooks/loads.

108 local mocks and syntax checks passed: existing 90 plus 18 meaningful new
presentation tests. 64 of 68 v0.2.7 functions are AST-identical; four change
version labels only, four new functions. Insertion/rollback/manual duration,
guards and observers/cleanup remain unchanged. Factory metadata/button4 route
change. See evidence/v028_presentation_snapshot_plan.md. The first live run's
installed three files matched the original ZIP. Its log confirms owned solo
insertion/runtime registration, zero observers and RESTORE result=True; the
screenshot confirms visible0/1, one point, inactive description and a rendered
[Enter] Spend Point hint. The hint is not proof of eligibility/purchase and is
distinct from orange grade-preview text. That first run had no [UVH-PRESENT]
messages; the user confirmed "I didn’t press 4". Presentation data and FINAL
comparison were unobserved in that run. See
evidence/v028_live_presentation_result.md. Preserve all eight original ZIPs,
logs/PNG and tested snapshots v0.2.7/v0.2.8 unchanged. Runtime is frozen.
Never install over SDK/core mods.

The subsequent fresh retry completed item4: two snapshots accepted the loaded
array/inner/class schema and verified presentation counts Overclock0, MorePep4
and Myelin2 with all six reference identities covered. Raw common-class
metadata was CAPPED after16 fields, not complete. Both calls sampled FINAL
PRI points=(1,0)/ranks=(0,0,0) unchanged, verified_arrays=3/3 and observers_added=0.
CANCEL restored original arrays/cells with all hooks0; repeat CANCEL found no
patch and the process was closed. No ERROR/Traceback, UNAVAILABLE or ABORT.
Installed files matched the original ZIP; workspace README differs for docs
only. See evidence/v028_live_presentation_retry_result.md and the separate
v028_presentation_retry.log. The empty array is now verified native data;
causation/eligibility/purchase/effect remain unproven. Runtime remains frozen.
Do not repeat this count test solely to reconfirm it. Next design is an explicit
bounded read-only string/display-field allowlist from the observed descriptors,
with loaded schema and unchanged-state checks before payload reads. No guessed
fields beyond the cap, Attribute traversal/evaluation, copies, formatter calls,
text overrides or gameplay writes. See docs/NEXT_CODEX_TASK.md.

## v0.2.9 tested baseline (presentation strings)

Button4 now routes to inspect_overclock_presentation_text, still19 options.
Explicit synchronous read-only comparison of Description, NoConstraintText,
Prefix and Suffix. Targeted SDK _find_prop checks exact field/owner, StrProperty,
flags4227075/dimension1 and observed offsets68/80/104/92 before each instance
read. Exact scalar owner was not printed in v0.2.8; the new check passed for
the six sampled native references in v0.2.9. Unknown metadata is evidence,
never bypass it. Exact str payload only, length/
clip status and repr-escaped output<=512 characters; unknown objects are never
converted/repr'd. No template/HTML evaluation or formatting invocation.

Reuse _upgrade_state unchanged with per-call baseline and overlap refusal.
Revalidate loaded array/inner/class and fresh current membership/count/class
around each read. Up to256 entries allowed, sample<=4 per skill, fixed4 fields
per entry (maximum48 values/call), SDK paths<=384. Field errors are UNAVAILABLE,
known empty strings VERIFIED, empty arrays NOT_APPLICABLE. Array/sample and
field coverage are separate. Field errors continue only after unchanged state/
reference checks; unknown/changing arrays/references abort before another target.
FINAL unchanged only after full comparison; no repair/refund.

No Boolean/float/Attribute values, arbitrary metadata/instance enumeration,
Attribute traversal/evaluation, copied effects/presentations/constraints,
native formatter/query calls, text/return overrides, gameplay writes, loads,
new hooks or automated effect. Reused _presentation_metadata emits
[UVH-PRESENT] SCHEMA during checks; new diagnostic uses [UVH-TEXT].

127 unique mocks plus syntax and AST scope checks passed:108 established plus
19 new text-read tests. Of72 prior functions67 are AST-identical and five
change version labels only; four new functions and fixed schema tuple.
Factory metadata/button4 route change. Two prior version assertions/one route
assertion updated; other established test behavior preserved. Insertion/
rollback/manual duration, state/session guards and observers/cleanup unchanged.
See evidence/v029_presentation_text_plan.md for the historical build checks.
The completed live run accepted every allowlisted scalar schema/owner and
verified24/24 fields in each of two snapshots: MorePep16/16, Myelin8/8;
Overclock count0/fields0/0 text=NOT_APPLICABLE. Native Description strings use
$NUMBER$ templates; all NoConstraintText/Prefix/Suffix values were verified
empty. No clipping/refusal/abort. Both calls sampled FINAL points=(1,0) and
ranks=(0,0,0) unchanged, observers_added=0. CANCEL restored original arrays/cells,
all hooks0; repeat CANCEL found no patch and BL2 process count0 at review.
See evidence/v029_live_presentation_text_result.md and v029_user_test.log.
Installed three files matched the original ZIP. Its tested runtime/pyproject
and all nine original ZIPs, tested snapshots v0.2.7/v0.2.8/v0.2.9 and prior
logs/PNG remain unchanged. At that review only docs/default ZIP changed;
the new v0.2.10 source below now supplies the next comparison.
Raw templates do not prove cause, eligibility, purchase or the node effect.

## v0.2.10 tested baseline (display comparison; one refused Attribute)

Button4 now routes to inspect_overclock_presentation_display, still19 options.
Read only three observed native flags bDontDisplayNumber,
bUseCustomNumberPlacement, bEnableTextColor and typed Attribute identity/absence.
Targeted scalar SDK _find_prop: exact name/declaring owner/type/flags3/dimension1,
offset116 for BoolProperty or64 for Attribute ObjectProperty. Actual declared
UClass/name AttributeDefinition required before getter; exact bool payloads,
no mask guesses. None Attribute is verified absence; otherwise actual SDK
UObject/Class identical to declared class before bounded escaped SDK path.
Unknown subclasses/same-name different classes/values refuse without repr/
conversion. Loaded descriptor owners and all 18 native bools passed in engine;
five of six Attribute identities passed. The second Myelin payload refused
the exact-class check; actual wrapper/class/ancestry/path remain unobserved.

Reuse _upgrade_state and _presentation_text_reference unchanged, per-call
baseline and overlap refusal. Fresh current array/count/membership/class and
state rechecked around reads. Accepted typed Attribute's descriptor/current
field/Class checked around path and outside field exceptions before logging;
changes abort before another field/target. Initial field metadata/getter/type/
path errors are UNAVAILABLE, never absence. Continue only while all state/
reference guards pass. Unknown/changing arrays/presentations abort. FINAL
unchanged only after full comparison; no point/rank repair/refund.
Up to256 array entries, sample<=4 per target, fixed4 field captures/reference,
maximum48 records; bounded Attribute rereads<=4/entry, paths<=384. Separate
flags/Attribute/present/absent/partial coverage; empty arrays NOT_APPLICABLE.
Fatal inspection gives snapshot=ABORTED/ABORT; no false array-zero inference.

No text reread, arbitrary enumeration, Attribute values/traversal/evaluation,
native formatters/queries, template evaluation, copies, overrides, loads,
new hooks or gameplay writes. Existing insertion/rollback/manual duration
and observer cleanup remain intact. New [UVH-DISPLAY] prefix; reused
[UVH-PRESENT] SCHEMA messages are metadata/membership rechecks.

151 unique mocks passed (127 established plus24 new), syntax and AST proof.
Of76 old functions70 remain AST-identical, six change only version labels;
four new functions and one fixed flag tuple. Factory/button4 route/version
change; only two prior version assertions and one route assertion updated.
New tests cover schema/owner/type/class refusal, strict bool/known absence,
bounded identity paths/samples, no attribute traversal or game writes/calls,
state/reference changes including typed Attribute schema/identity at path,
failed overlap and preserved CANCEL/disable restoration. The live run completed
four calls with23/24 fields each, all 18 flags and five identities. MorePep
flags12/12/Attributes4/4; Myelin flags6/6/Attributes1/2 PARTIAL. Overclock
count0 is NOT_APPLICABLE. Each BASELINE/FINAL points=(1,0)/ranks=(0,0,0)
unchanged, observers_added0. CANCEL restored arrays/cells with all hooks0;
repeated CANCEL found no patch and process count0 at review. No ABORT/ERROR.
See evidence/v030_live_presentation_display_result.md and v030_user_test.log.
Installed three files matched original ZIP. Exact tested files are under
archive/tested_runtime/v0.2.10; runtime/pyproject are frozen. Preserve all ten
original ZIPs and four tested snapshots/logs/PNG unchanged; docs/default ZIP
only in this review. Never install over SDK/core mods.

The user separately reports a one-point Overclock purchase to1/1 in an earlier
process, then Alt+F4/restart to follow the read-only steps. This is positive
user-observed UI purchase/rank evidence, not a purchase failure. The retained
restarted log has one unspent point/grade 0; no first-run transaction or grade 1
capture/save audit. Reset state after restart is observed; save behavior,
cost/transaction verification and duration effect remain unverified. No point
repair/backup restore/save writes. Do not repeat the purchase for missing data.
The report does not authorize further purchases or automatic effects/point/
grade/save writes; later controlled tests still need explicit scope/recovery.

## v0.2.11 tested baseline (combined class metadata and restoration passed)

Current runtime is v0.2.11 - OVERCLOCK ATTRIBUTE CLASS, now game-tested.
Read evidence/v031_live_attribute_class_result.md, v031_user_test.log and
v031_capture_manifest.json. Two complete calls 65-212/214-361 captured Myelin
index 1 SDK_UOBJECT/SDK_UCLASS and actual WillowGame.ResourcePoolAttributeDefinition.
Its five-class COMPLETE chain passes through declared Engine.AttributeDefinition;
logged DERIVED is actual runtime SDK identity/revalidated-link evidence, not
name inference. Sampled points=(1,0)/ranks=(0,0,0) stay unchanged, END observers0.
Solo listen-host sole-owned-player records30/35, one inert registered node36,
native RESTORE385-386 and four-family zero cleanup after the last call are
preserved. Separate capture machine queries found process count0 before/after.
One inspection was requested, two occurred; second ARM refused, CANCEL repeated.
Keep these deviations explicit. No repeat of this completed diagnostic needed.

The old exact-class Attribute guard, _upgrade_state and presentation reference
checks remain unchanged. Do not evaluate/traverse the derived Attribute or
infer gameplay authorization from the new class result. No new hooks/native
queries/writes in item4. Runtime/pyproject freeze at tested hashes 59f99db2 and
759a6892. Exact tested three files are in archive/tested_runtime/v0.2.11.
Keep all 44 prior protected files, original v0.2.11 ZIP and immutable capture/log/
manifest/snapshot unchanged. Current docs/default ZIP may differ only in README;
never rebuild any versioned ZIP or edit historical evidence to update status.

179 runtime mocks and syntax/AST proof apply to unchanged runtime. The corrected
standard-library offline reviewer at 44ad64c passed 236 unique tests (57+179) in
independent peer review, with no failures/errors/skips. It rejects contradictory
class labels and actual runtime removal/rollback failures, including retries.
Parser success does not verify SDK identity, machine exit/install equality or
log origin. Read actual capture/manifest and unchanged guards as separate inputs.

Readiness research PR#4 at f8aa2fe received independent acceptance (sequence71).
Read its actual findings, then separately scope a bounded metadata-only Deathtrap diagnostic. Do not
invoke GetSkillManager or activation/deactivation functions from inventory
names, install observers, change Duration or reuse grade-zero _upgrade_state
as a rank-one effect gate. Current manual duration path is independent: its
signature uses names/time; shutdown/cancel do not call manual restore. Research
counterexamples are inert mocks, not observed engine incidents. No automatic
effect, point/rank/save writes, guard relaxation, purchase/co-op/release here.
See docs/NEXT_CODEX_TASK.md for the concrete proposed scope and review gate.

## Guardrails

- Avoid modifying game save files, spending player skill points, adding persistent effects, enabling co-op or publishing a release until explicitly requested and separately tested.
- Use Gaige in solo mode on backed-up save for mutating experiments; make rollback explicit; fail closed on unexpected objects.
- Never enable automatically invasive hooks or modify shared definitions when no reliable revert is possible. Involve user in running game tests on their Windows installation.
- Keep docs honest about what's simulated and what's verified in-game; include precise log messages and expected behavior in release instructions.
- Before shipping: run Python syntax compilation, mock test(s), inspect ZIP layout and ensure the runtime remains usable without design scaffolding files.
- Do not include Borderlands game assets or any extracted proprietary binaries in the repo.

## First action

Read docs/NEXT_CODEX_TASK.md and evidence/v031_live_attribute_class_result.md.
The prepared v0.2.11 test and capture/reviewer peer reviews are complete; no
repeat game run is pending. Read shared updates and actual commits before
claiming new work. Research PR#4 is independently accepted; read its actual
findings before separately scoping the proposed diagnostic.
No lifecycle function signature/timing is established by old field inventories.
Preserve tested runtime, all originals and immutable capture. Keep the prior
user-reported purchase separate from transaction/save/effect proof. No purchases,
automatic effects, point/grade/save edits, co-op or release without separate scope.
Native-array rollback cannot refund points, undo saves or clear player/UI caches.
