# Project state and development history

## Reviewed v0.2.12 - DEATHTRAP METADATA: partial live result

Last game-tested runtime is v0.2.12. Read
evidence/v032_live_deathtrap_metadata_result.md, v032_user_test.log and
v032_capture_manifest.json. The owner confirmed the full protocol, CANCEL3
and full exit. Two calls65-82/83-100 captured identical15 rows: four class roots
and seven fields COMPLETE; controller ActivateSkill/DeactivateSkill UNAVAILABLE.
FINAL points=(1,0)/ranks=(0,0,0) unchanged is a runtime assertion; the internal
start baseline is not logged. END is UNAVAILABLE, not full coverage or effect
readiness. No manager instance, active-skill payload or native invocation in item4.
Runtime restore123/124 and all four observer families0 after the last call;
independent process queries0 before/after capture and installed/source/original
ZIP equality. Two inspections vs requestedone, refused secondARM and repeated
CANCEL are documented. No repeat to force COMPLETE.

Next: design a bounded metadata-owner correction using the actual typed return
class WillowGame.SkillEffectManager. v12 only queried activation/deactivation
names on the controller. A missing lookup does not prove absence elsewhere;
no guessed function/hook path or callable signature. Native lifecycle, lifetime,
timing and effect remain NOT_READY. Keep _upgrade_state at gradezero and preserve
all historical/manual functions. Manual restore remains separate from CANCEL.

Freeze runtime41fd2dd9, pyprojectfa8acf73, originalv12ZIP4f49bad1, immutable
capture/snapshot/testedREADME and all earlier evidence/research. Only current
documentation/default ZIP README may differ. Static artifact inventory records
prepared-e32 current hashes: immutable check must pass; explicit --check-current
reports intentional README/defaultZIP drift, checked separately by package
source/CRC/layout/syntax/inert-import verification. Do not rewrite old hashes.
Recorded review is required after submission, including labeled self-review;
resolve shared findings before completion. No new game/nativeSDK/install/save/
private-backup/purchase/summon/boost/co-op/merge/release action in this review.

## What the user wants

Long-term ambition: a Borderlands Ultimate Vault Hunter Collection spanning main Borderlands games with persistent progression, a broad roster, expanded skill systems and co-op. Immediate priority is to establish reliably working BL2 mod systems; selected feature is a real **new Gaige skill-tree node** called **Deathtrap Overclock**, ultimately allowing a skill-point purchase that adds 15 seconds to summoned Deathtrap. They prefer incremental downloadable ZIPs and short install instructions. They requested a move to Codex for direct ongoing code development.

## Runtime

- Platform: Windows, Steam Borderlands 2.
- SDK versions observed in logs: `unrealsdk v3.2.0`, `pyunrealsdk v1.10.0`.
- `sdk_mods/UltimateVaultHunterDeathtrapBoost` is the sole current installed project mod folder (after replacing previous test mods).

## Chronological evidence (user real game vs simulated)

| Version | Result | Reliability |
|--|--|--|
| v0.0.9 | Failed to find duration on `DeathtrapActionSkill` | Real game log |
| v0.1.0 | Found active `Skill_DeathTrap.Duration = 60` in `SkillEffectManager.ActiveSkills` | Real game log |
| **v0.1.1** | Wrote live `Duration 60 -> 75`; user reported summon lasted longer | **Real game log and user observation** |
| v0.1.2 | `PlayerClass.SkillTreePath` found; non-default `SkillTreeDefinition` missing | Real game log |
| v0.1.3 / v0.1.4 | Found branch and layout objects for Gaige, including six tiers | Real game logs |
| v0.1.5 | Confirmed `SkillDefinition` metadata and availability of `unrealsdk.construct_object` | Real game log |
| **v0.1.6** | Inserted separate inert node into `LittleBigTrouble` tier 0 data; `INSERT VERIFIED` | **Real game log, but user confirmed node NOT visible in Skills UI** |
| **v0.1.7** | Three main-menu attempts aborted: branch/layout unavailable or unexpected; no insertion | **Real game log; no UI visibility test reached** |
| **v0.1.8** | Assets briefly accessible at menu, then missing; Gaige's map has branch/layout and `PlayerSkillTree_0`; trace registered zero observers | **Real game log; no native calls traced, no insertion tested** |
| **v0.1.9** | Trace captured native Initialize PRE/POST with available assets, then UI initialization; 20 events, all 16 observers removed | **Real game log; no insertion or visibility test** |
| **v0.2.0** | Reached Gaige Initialize PRE, but the numeric-only solo guard aborted on `NetMode=2`; no construction/insertion, all observers removed | **Real game log; user reported no visible node; insertion/UI experiment not reached** |
| **v0.2.1** | PRE inserted one inert node; engine built its runtime entry; all observers removed; CANCEL restored original arrays | **Real game log and user-confirmed visibility: "done it worked!"** |
| **v0.2.2** | Two menu refusals, four completed read-only snapshots with PRI points 1/0 and node rank 0/1, metadata reflection, observer cleanup and native-array restoration | **Real game log plus 37 local mocks; user reports tooltip 0/1 with no upgrade prompt; purchase behavior unverified** |
| **v0.2.3** | Four live snapshots verified matching Passive enum values, native constraint and upgrade-UI metadata; points/ranks unchanged, native arrays restored | **Real game log, user-confirmed title/prototype description and 41 mocks; purchase/effect untested** |
| Intended v0.2.3 follow-up | Installed v0.2.2 actually ran; four snapshots kept points/ranks unchanged and restored native arrays with zero observers | **Real repeat v0.2.2 log and installed hashes; does not test v0.2.3** |
| **v0.2.4** | Opt-in bounded POST observers for normal UI eligibility/cost; unchanged points/ranks/indices, current tree/UI/session guards; stop/cancel/disable cleanup | **57 mocks plus live setup/stop/restoration, unchanged sampled points/ranks; callbacks=0, eligibility/cost unanswered** |
| **v0.2.5** | Opt-in discovered UI navigation/refresh PRE/POST_ANY trace and bounded owned selection snapshots; unchanged state/session guard and cleanup | **71 mocks plus 14 live events verifying owned node/original selection, unchanged sampled points/ranks, hook cleanup and native-array restoration; eligibility/cost unverified** |
| **v0.2.6** | Core UI priority verified: all six helpers captured; MorePep/Overclock and node info update observed, cap stopped before Myelin | **74 mocks plus live 48 events/51 callbacks, unchanged sampled FINAL points/ranks, event-limit cleanup and native-array restoration** |
| **v0.2.7 (focused trace baseline)** | All nine function/skill buckets observed; Overclock grade-one description empty while native skills returned text; final points/ranks unchanged, hooks removed and arrays restored | **90 mocks plus live 16 results/110 callbacks, exact installed/source/ZIP match and verified cleanup; eligibility/rendered prompt/effect unverified** |
| **v0.2.8 (presentation baseline)** | Fresh retry verified presentation counts Overclock0/MorePep4/Myelin2, all six references, capped raw metadata, unchanged sampled FINAL state and restoration | **108 mocks plus two live snapshots, installed/ZIP byte match, arrays 3/3 and cleanup; cause/eligibility/effect unverified** |
| **v0.2.9 (text baseline)** | Two snapshots accepted scalar schemas/owners and verified all 24 native text fields; Overclock has no entries, native descriptions use $NUMBER$ templates | **127 mocks plus live24/24 fields per call, installed/ZIP byte match, sampled FINAL state unchanged, hooks0, arrays restored and process closed; cause/eligibility/effect unverified** |
| **v0.2.10 (previous tested source)** | Four live snapshots verified18 native flags and five of six Attribute identities each; second Myelin Attribute refused exact-class validation | **151 mocks plus live23/24 fields/call, sampled FINAL state unchanged, restored/hooks0/exited; separate user report of first-run one-point purchase to1/1, transaction/save/effect unverified** |
| **v0.2.11 (previous game-tested baseline)** | Two combined Myelin wrapper/UClass/ancestry calls | **SDK_UOBJECT; ResourcePoolAttributeDefinition; five-class COMPLETE/DERIVED; sampled state unchanged; restoration/hooks0/independent exit checks; runtime frozen** |
| **v0.2.12 (current game-tested source)** | Two bounded Deathtrap metadata calls; four roots/seven fields COMPLETE, controller lifecycle names UNAVAILABLE | **Partial coverage; FINAL unchanged assertion, restoration/four-family cleanup, independent exit and installed/ZIP equality; no summon payload/lifecycle/effect proof** |

## Relevant exact data

- Branch: `SkillTreeBranchDefinition'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble'`
- Layout: `SkillTreeBranchLayoutDefinition'GD_Tulip_Mechromancer_Skills.SkillTrees.Layout_LittleBigTrouble'`
- First tier before insertion: `Skills=[MorePep,Myelin]`, `bCellIsOccupied=[True,False,True]`.
- First tier after v0.1.6 insertion: `Skills=[MorePep,UVH_DeathtrapOverclock,Myelin]`, `bCellIsOccupied=[True,True,True]`.
- Current custom `SkillDefinition` prototype is intentionally inert: max rank1, effects empty. The user now reports a one-point UI purchase to1/1 in an earlier v0.2.10 test process; the retained restarted log is grade 0/one point. No captured purchase transaction, save audit/persistence or node effect verification. Manual +15s is an independent button.
- User said the v0.1.6 node was not present visually following in-world insertion. v0.2.1 pre-initialization insertion is now a demonstrated working approach; UI caching as the exact earlier failure cause remains an inference, not proven.
- `GD_Tulip_Mechro_Streaming.SkillTree.SkillTree_Mechromancer` was inaccessible from previous lookups; could be streaming/another lookup behavior.

## Logs included

- `v011_duration_write_verified.log`: active skill write acceptance.
- `v014_native_branches_and_layout.log`: real branch definitions, tier layout.
- `v015_skill_definitions_and_construct_api.log`: creation API and sample metadata.
- `v016_node_insertion_verified_but_NOT_VISIBLE.log`: node data insertion.

- `v017_main_menu_assets_unavailable.log`: three real main-menu aborts on October 9, 2026 local time. No `INSERT VERIFIED` or candidate construction entry. Missing assets are the leading inference because no pristine-tier mismatch entry appears; `load_package` returning None alone is not proof of failure.

- `v018_assets_transient_playerskilltree_found.log`: menu snapshots at 00:23:42.691Z and 00:23:44.474Z change all four exact asset lookups from found to missing. Cause is unknown. In-map snapshots show branch/layout pristine, no loaded streaming definition, and `PlayerSkillTree'Loader.TheWorld:PersistentLevel.WillowPlayerController_2.PlayerSkillTree_0'`. Trace at 00:23:47Z registered zero observers. The log contains no node insertion or observer events.

v0.1.8's discovery parser required dot-form UFunction paths and would reject `WillowGame.Class:Method`. A colon-form mock reproduced the defect before the v0.1.9 fix. Since the old trace did not log raw metadata, its empty result could have other causes too; no actual call order is established. The existence of a live player tree suggests a separate runtime representation to inspect, not a proven explanation of v0.1.6 visibility failure.

- `v019_live_tree_and_init_trace.log`: 11 discovered candidates, 16 active observers, 20 captured events, `STOP remaining=0`. At 00:36:12.596Z (October 9 17:36:12 local), PlayerSkillTree.Initialize PRE has Gaige/no pawn, all exact native assets present, empty Branches and exact `args.SkillTreeDef`. POST has four branches. Little Big Trouble is runtime branch 2 with `TierIndices=[7,8,9,10,11,12]`; runtime lists are flat rather than nested tiers inside branches. Subsequent UI calls include InitializeGFxHelper and extInitTree. No node insertion occurred. These observations support pre-initialization insertion but do not prove why v0.1.6 was invisible.

The generic v0.1.9 dump consumed its budget following SkillTreeListeners into the controller before reaching runtime Skills/Tiers. v0.2.0 fixes that traversal and reads the targeted candidate/runtime tier directly. Reading SkillDefinitionToIndex raised RuntimeError (likely unsupported map access); v0.2.0 never reads or writes this map and lets the native initializer construct cache/index state.

- `v020_netmode_guard_aborted_no_insertion.log`: armed at 00:51:52.276Z, then Gaige Initialize PRE at 00:52:04.826Z reported `NetMode=2` and no pawn. The guard required `NM_Standalone=0` and aborted before construction or shared writes. Observer removal reported zero remaining. CHECK recorded no insertion; CANCEL had no patch to restore. User reported the node did not appear. This does not test pre-initialization insertion, prove a UI failure, or establish the session's player count/network setting.

v0.2.1 replaces that unsupported solo assumption. The installed SDK networking source documents `WorldInfo.GRI.PRIArray` as the roster updated on player joins/leaves, and uses `unrealsdk.find_enum('ENetMode')` for network roles. Installed mods_base obtains the local controller through `ENGINE.GamePlayers[0].Actor`. The new gate reads those same properties without invoking native gameplay functions: allow named Standalone/ListenServer only with exactly one local player matching pc and exactly one roster entry matching pc.PlayerReplicationInfo with Owner==pc. Clients/dedicated servers, extra players, missing/loading data and identity mismatches refuse insertion. Numeric 2 alone never authorizes mutation. These field semantics are supported by installed SDK code, and the one-player listen-host positive path was verified at PRE in the successful v0.2.1 run. Refusal/peer-arrival cases remain mock-tested only. CHECK reports current session evidence even after an abort, without constructing/inserting a node. Test Offline; do not enable co-op.

- `v021_native_node_visible_and_restored.log`: at 01:12:56.828Z (October 9 18:12:56 America/Los_Angeles), Gaige PRE verified listen_host (`NetMode=2`), one local player and one roster player with both identity matches True. It constructed an independent inert SkillDefinition and verified insertion before native Initialize. POST and two later CHECK calls found exactly one candidate and both original skills among 39 runtime skills. The candidate was index 14, parent tier 7, grade 0; first-tier SkillIndices were `[13,14,15]`. Tier bUnlocked was initially False and later True. All observers were removed. CANCEL at 01:13:42.159Z verified original skills `[MorePep,Myelin]` and cells `[True,False,True]` restored. The user reported **"done it worked!"**, confirming visible-node success for the requested test. See `v021_visibility_confirmation.md` for evidence limits and baseline hashes.

The current v0.2.1 experiment must be explicitly armed at main menu, runs once for Gaige only, and inserts before the native initializer builds player caches. It also guards exact class/tree path/ownership, an empty player tree, and the known pristine six-tier branch/layout. A snapshot precedes writes. POST_UNCONDITIONAL rechecks solo evidence, inspects the runtime Skills array for the new candidate and both original skills, and removes observers. Failed session/runtime verification restores owned native arrays. Cancellation/disable restores owned native writes; independent changes are not overwritten. Failed restores retain their snapshots. Restoring shared definitions does not clear the engine-built cache; **restart BL2 after every test**. No save/grade/point APIs are called and the new node is inert; never buy it. Local mocks are not proof of engine visibility.

v0.2.1 local validation: 31 simulated tests, syntax compile, exact three-file ZIP integrity/source comparison and isolated packaged-runtime import. Includes solo listen-host insertion, refusal of 18 invalid session cases, SDK enum lookup, peer arrival before POST rollback, read-only session check after PRE abort and preservation of the manual duration prototype. The real game log and user's visual confirmation now add a successful solo visibility/registration/restore result.

The visibility objective is complete for this test. Keep `dist/UltimateVaultHunterDeathtrapBoost_v0.2.1_folder_install.zip` unchanged as the tested baseline. At confirmation, runtime source matched that ZIP and the installed mod byte for byte. Do not infer point purchase, persistence, the new node's +15-second effect, every other skill's UI integrity, or co-op support. Those require later scope and separate evidence.

v0.2.2 added `inspect_overclock_purchase` and bounded UFunction discovery/reflection. It reads only after the recorded Gaige tree, current controller, solo roster, native patch and runtime entry indices/first tier are verified. It logs direct PRI/controller point fields, candidate and original ranks, grade rules, skill type/class, effect/action counts and tier state. It does not call native eligibility/cost/grade/purchase/save functions, manually edit ranks/points, register observers or load packages. SDK `_properties()` returns metadata fields (up to 16 per function); raw flags, offsets, class/struct/enum references, NumParams and return offsets are logged without interpreting them as a callable signature. Discovery is capped at 30000 scanned objects, 32 paths and 12 detailed functions. Unknown fields/errors are reported rather than guessed. Existing v0.2.1 functions remain AST-identical. The inert insertion still requires explicit ARM, CANCEL and a fresh game process after testing.

v0.2.2 local validation: 37 tests, syntax compilation, isolated three-file ZIP import/layout/source checks. New cases cover non-mutation, missing/foreign/stale ownership, duplicate or invalid runtime entries, unavailable point data, unexpected nonzero grade, reflection failure and scan/output bounds.

- `v022_purchase_rank_metadata_and_restored.log`: the user reported "done" after the diagnostic instructions. Two menu attempts refused inspection. At 04:12:12.105Z (October 9 21:12:12 America/Los_Angeles), Gaige PRE verified one owned local player and roster player in listen_host mode; insertion/native registration again found one candidate and both originals among 39 runtime skills. Four in-map snapshots completed at 04:12:27.379Z, 04:12:28.124Z, 04:13:13.096Z and 04:13:13.732Z. Every snapshot reported PRI points 1 general / 0 specialist, Overclock rank 0 / max 1 / starting 0, index 14 / tier 7, unlocked True / unlock requirement 0, and both originals at rank 0. Controller point fields were unavailable. Overclock SkillClass=Skill and grade rules=True matched the originals; constraints/effects/actions were empty. SkillType formatting (`<ESkillType len=0>`) did not expose the enum value. Each scan inspected 20120 objects, found 53 functions, logged 32 paths and detailed 12 functions. `_properties()` includes locals as well as parameters; raw descriptors do not establish callable signatures or eligibility. At 04:13:14.619Z, CANCEL verified original skills and cells restored; all observers were zero. The log contains no ERROR or Traceback. At the initial review, the tooltip observation was unreported; snapshot timestamps alone do not prove hover timing. See `v022_purchase_diagnostic_result.md` for limits and hashes.

The live v0.2.2 diagnostic milestone is complete; purchases, cost, persistence and the node's effect remain unverified. Installed v0.2.2 runtime/pyproject matched the workspace at review. Preserve both tested versioned ZIPs; documentation-only changes may rebuild the default ZIP. No runtime code changed during the initial result review. A later one-point purchase experiment requires explicit scope and a point/grade/save recovery plan first, since native-array restoration cannot undo a purchased rank.

The user subsequently reported **"0/1, with no upgrade prompt"**. The tooltip's rank is confirmed; there is no native-skill prompt comparison and no purchase attempt. This does not establish the cause or prove that purchasing fails. v0.2.3 addresses concrete diagnostic gaps: a purchase-only Enum formatter exposes SDK IntFlag names/values, constraint inspection reads exact SkillConstraintData metadata with four-entry/eight-field caps plus LockedSkillDetailStr, and detailed function metadata prioritizes CanUpgradeSkill and Flash_SetSkillPointProperties instead of mutation APIs. No constraints are evaluated or copied, no object graph is traversed, and no native gameplay calls/hooks/loads/writes are added. All 48 established v0.2.1 functions remain unchanged. Only the two v0.2.2 diagnostic functions, two new helpers and mod metadata differ. 41 local mocks passed, including zero enum output, comparison without evaluation, reflection errors/unknown type refusal/bounds and UI metadata priority. At build time there was no v0.2.3 game result. The planned test compared Overclock, More Pep and Myelin tooltips with the same input method, snapshot before/after, then CANCEL and exit. See `v023_diagnostic_plan.md`.

The intended v0.2.3 follow-up test instead loaded v0.2.2, confirmed by snapshot headers, installed pyproject and the installed runtime SHA256 matching the v0.2.2 baseline. The preserved `v022_repeat_rank_preview_clarification.log` has four completed snapshots at 04:46:07.066Z, 04:46:07.834Z, 04:47:54.030Z and 04:47:54.563Z. Points remained 1/0, Overclock grade 0/max1, originals grade 0; at 04:47:55.146Z original arrays restored with zero observers. The user clarified that Overclock looks like other skills and they meant no orange rank-upgrade text, which they attribute to the one-rank cap. That interpretation is not verified UI semantics and does not demonstrate purchase failure. See `v022_repeat_rank_preview_clarification.md` for hashes and exact limits. Only one installed project folder was found; why replacement did not happen is unknown. At that review there was no v0.2.3 live result. The next step was to use the existing v0.2.3 ZIP, check its exact MODS title before ARM/Continue, then run the documented read-only test. No runtime change is needed merely to correct installation.

The next run correctly loaded v0.2.3, with log headers and installed runtime/pyproject matching the workspace. `v023_upgrade_metadata_and_restored.log` shows two menu refusals and four completed snapshots at 04:57:50.324Z, 04:57:50.619Z, 05:00:37.838Z and 05:00:38.455Z (October 9 21:57–22:00 America/Los_Angeles). PRI points remained 1/0, Overclock grade 0/max1 and both originals grade 0. All three definitions have ESkillType.SKILL_TYPE_Passive/value0, SkillClass=Skill, grade rules True and LockedSkillDetailStr '<Locked>'. Native constraint structs were read without evaluation: all three application flags True, OnFailure SKILL_Paused/value2, Evaluator None and one EvaluatorDefinitions entry; that array's contents and purchase relevance remain unknown. Upgrade-UI metadata reflection worked; CanUpgradeSkill returns a descriptor with ESkillTreeFailureReason, not Boolean, with no explicit skill input. It was never invoked and no actual failure reason/cost was captured. CANCEL at 05:00:39.267Z restored MorePep/Myelin and original cells, observers zero. The user confirmed the blue title and exact inactive prototype description. No ERROR or Traceback appears. See `v023_live_diagnostic_result.md` for hashes and limits. The live diagnostic milestone is complete; no source code changed during review, all three tested ZIPs are preserved, and no repeat snapshot is needed merely for tooltip details. Next purchase work needs actual eligibility evidence and explicit recovery/scope before point spending; manual +15 seconds remains independent.

The verified manual +15s duration functions are preserved. No saves were parsed or edited. Byte-verified save-directory copies are outside the project in the handoff's `private_backups/2026-10-09_v017` and `private_backups/2026-10-09_pre_v020`. These are current-state snapshots when copied, not proof of a pre-project historical backup; never package them or restore them automatically.

The completed v0.2.4 observer run is preserved in evidence/v024_live_observer_result.md. Initial in-map ARM/start attempts refused; menu ARM then insertion and two-observer setup passed. The user confirmed highlighting all three skills, but STOP recorded callbacks=0 and no results, with sampled points/ranks unchanged. After clarification the user pressed 3 and exited; the final log verifies original native-array restoration and zero observers. All four versioned ZIPs and runtime are unchanged. Actual eligibility/cost remain unanswered; next useful work is a different bounded UI navigation/refresh observation, not point spending or repeating these same hooks.

v0.2.5 adds button 7/8 UI navigation/refresh observation and direct owned-UI start/stop snapshots after v0.2.4 captured zero calls. Up to 10 loaded functions/20 PRE/POST_ANY hooks, 48 events, 2048 attempts, two copies per state, 90 seconds checked on calls. No args/ret reads, native invocation, overrides or observer game writes. It reuses _upgrade_state unchanged. Only cancellation/UI mutual-exclusion/version labels change among v0.2.4 functions; native insertion/rollback/manual duration stay unchanged. 71 local mocks plus syntax/isolated package checks pass. The later live result below verifies UI selection and restoration. See evidence/v025_ui_trace_plan.md. All four tested versioned ZIPs remain unchanged.

The v0.2.5 live UI trace is preserved in evidence/v025_live_ui_trace_result.md: 14 events/16 callbacks verified the owned UI selecting Overclock, MorePep and Myelin with UI point=1 and target tier unlocked=True. Final PRI points/ranks stayed unchanged; observers were removed and native arrays restored. The ten-function cap included four artifact paths and left discovered core PostNav/input/info/point-display helpers unhooked. At that review the next useful work was candidate priority and a crowding regression; v0.2.6 below implements them. Eligibility/cost/purchases/effects remain unverified. At that review the v0.2.5 runtime was unchanged; all five tested versioned ZIPs stay unchanged.

v0.2.6 addresses the v0.2.5 candidate crowding limitation: exclude artifact/equip
names before reflection, prioritize six discovered core helpers plus Init and
Nav_Down/Left/Right within ten slots, use loaded fallbacks only, and log explicit
SELECTED paths. The actual 24-name live regression failed on the old priority
before passing with the fix. 74 local mocks, syntax and isolated ZIP checks
passed at build time; the live result follows below. Only _ui_candidates changes behavior, three
functions change version labels and the other 59 are AST-identical to v0.2.5.
Guards, callback/cleanup bounds, inert insertion/rollback and manual duration
remain unchanged. All five tested versioned ZIPs and the v0.2.5 log are intact.
See evidence/v026_core_ui_trace_plan.md and docs/NEXT_CODEX_TASK.md for the new
test. Eligibility/cost/purchases/persistence/node effects remain unverified.

The v0.2.6 live result is preserved in evidence/v026_live_core_ui_result.md.
Installed runtime/pyproject matched workspace/tested ZIP. Discovery selected
the intended ten methods from 19 candidates; all six core helpers produced
events. 48 events/51 callbacks (three duplicate skips) reached the configured
event bound after about 11.47 seconds. MorePep/Overclock selection and node
UpdateInfoBox PRE/POST_ANY were verified with UI point=1 and tier unlocked.
The cap cut off before Myelin; later UI activity was unobserved. The live STOP
inventory printed the owned node UI. FINAL PRI points=(1,0)/ranks=(0,0,0) stayed
unchanged at limit stop; later repeated STOP calls did not resample them.
All hooks removed; CANCEL restored native MorePep/Myelin and True/False/True,
then repeat cancellation found no patch. No ERROR/Traceback. Cost/eligibility/
prompt text remain unknown; point-display events were at initialization and
cannot be attributed to the node. Runtime/all six tested ZIPs remain unchanged.
At that review the next design was native skill-state/info with verified loaded
metadata/SDK output handling and capture-budget regression; v0.2.7 below supplies it.
Never read UpdateInfoBox locals as args or invoke GetSkillState to force evidence.

v0.2.7 adds focused buttons 9/10 after v0.2.6 proved helper activity but broad
input traffic exhausted its cap. Three POST observers validate loaded native
schemas before reading target input/actual bool/string returns or an owned UI
view. SDK hook args are copied inputs, so OutSkillState cannot be treated as
a finished state output; UpdateInfoBox locals and args.ReturnValue are never
read. Four records per function/target and two per distinct result permit <=36
captures in nine buckets within the 48-event cap, preserving other skill/function
slots. Every callback counts against 2048 attempts/90 seconds checked on calls.
No native invocation/override/edit/load/observer gameplay writes. 58 existing
functions are AST-identical; five scoped cleanup/START/version edits and five
new diagnostic functions. 90 local mocks, syntax and isolated 19-option
three-file package checks passed before the live test below. Preserve the
tested ZIPs and the v0.2.6 log. See evidence/v027_focused_state_plan.md and
docs/NEXT_CODEX_TASK.md. Query Boolean/preview text are not proof of eligibility/
cost/rendered prompt; purchase/persistence/automatic node effect remain untested.

The v0.2.7 live result is preserved in evidence/v027_live_focused_state_result.md.
All three installed files matched source and the tested ZIP before doc edits.
Loaded schemas were accepted and three POST hooks observed all nine function/
skill buckets: 16 results/110 callbacks/94 aggregate skips without an abort or
limit. GetSkillState returned True for every target. All description inputs
were Grade1/modifier0/HTML=False; Overclock returned an empty string twice,
MorePep length79 twice and Myelin length49 once. Every target info view showed
UI point1/tier unlocked=True, with current/rollover retained separately.
FINAL sampled points=(1,0)/ranks=(0,0,0) unchanged, all hooks removed and CANCEL
restored MorePep/Myelin plus True/False/True. Repeat CANCEL found no patch.
No ERROR/Traceback; the user reported done and no BL2 process was found at review.
No saves were read/edited. Runtime code remains unchanged. Neither the query
Boolean nor preview text proves eligibility/cost/rendered prompt behavior.

The concrete next comparison is definition presentation data, beginning with
SkillEffectPresentations: the older v0.1.5 log shows MorePep has four
AttributePresentationDefinition references and one-rank ExplosiveClap has one.
The inert constructor does not populate this array, but its actual defaults
and causal relevance to the missing prompt remain unknown. Plan bounded
read-only metadata/target comparison before changing any presentation/effect.
At that review no next runtime existed; v0.2.8 below now supplies it.
Do not repeat the completed trace merely to reconfirm its result.

The user confirmed accidentally deleting dist's ZIPs. All seven tested
v0.2.1–v0.2.7 original ZIPs were recovered by copying Recycle Bin payloads
whose hashes matched the prior records; no versioned archive was rebuilt.
The current default ZIP was recovered too, then may be rebuilt for docs only.
Recycle Bin/game files were unchanged. All tested ZIPs must remain unchanged.
The three tested v0.2.7 files also have a byte-identical snapshot under
archive/tested_runtime/v0.2.7; current log hash is
3024e4692fa28f0ea17ec39b3f6131ce5db1329991c4285aae5169b837195452.

v0.2.8 replaces button4's route with a focused synchronous presentation
snapshot. Target/shared SDK class identities and the loaded SkillEffectPresentations
ArrayProperty/ObjectProperty-inner descriptors are checked before SDK array
reads. Count<=256, sample<=4 references per skill, exact declared UObject class
and SDK paths<=384; common presentation class metadata<=16 properties with one
bounded lookahead. No guessed instance display/scalar/attribute/struct/array/
function reads, native formatting/query calls, new hooks, writes or loads.
Unchanged _upgrade_state is reused around reads, with a per-call baseline.
Separate VERIFIED/UNAVAILABLE array summaries and COMPLETE/CAPPED/UNAVAILABLE
metadata; FINAL unchanged state only on success, no repair on abort.
108 mocks (90 existing + 18 new), syntax and AST scope checks passed. Of 68 prior
functions, 64 are identical; four change version labels only, four are added.
Insertion/rollback/guards/observers/manual duration stay intact; factory 19 options.
Preserve all seven tested ZIPs/log/source snapshot; create v0.2.8 separately.
At build time there was no game result. See evidence/v028_presentation_snapshot_plan.md and
docs/NEXT_CODEX_TASK.md for the short 1,4,3 test. Purchases/effects/saves/co-op/
release remain outside this diagnostic milestone.

The first v0.2.8 live run is preserved in evidence/v028_user_test.log and
v028_overclock_user_screenshot.png; review is in v028_live_presentation_result.md.
All three installed files matched the original ZIP. Owned listen-host solo
insertion built one inert grade 0 node at index 14/tier 7 among 39 skills and kept
both originals. The screenshot confirms Overclock0/1, one skill point, inactive
prototype description and a rendered [Enter] Spend Point hint, without orange
bonus text. That hint is not proof of eligibility/cost/purchase and differs
from grade-preview text. Cancellation restored MorePep/Myelin and original
cells with zero observers; repeat cancellation found no patch. No ERROR/
Traceback and no BL2 process at review. No saves were parsed or edited.

There are zero [UVH-PRESENT] messages and no snapshot FINAL point/rank
comparison. The user explicitly answered "I didn’t press 4". Do not infer
zero presentation counts, a schema refusal, unchanged final points/ranks or
a runtime defect. Next is the omitted item4 step in a fresh v0.2.8 process:
menu1 before Continue, in-map mod options item4, item3, full exit. Mod-option
numbers are not keyboard shortcuts. Preserve the next log under a new name.
All eight original versioned ZIP hashes/integrity were verified unchanged,
plus the previous v0.2.7 log. Exact tested snapshots v0.2.7/v0.2.8 are retained.
Runtime/pyproject remain frozen; only docs/default ZIP may change.

The fresh v0.2.8 retry completed the omitted inspection and is preserved in
evidence/v028_presentation_retry.log, SHA-256
348d9ce354c6ec3853813de5eecba2c258d8fad72c8aab8280d26d4ec8a37229.
Review: evidence/v028_live_presentation_retry_result.md. Installed runtime,
pyproject and README matched the original ZIP. Both synchronous calls accepted
loaded ArrayProperty/ObjectProperty-inner/AttributePresentationDefinition
metadata and verified counts Overclock0, MorePep4 and Myelin2, covering all
six references. Raw class metadata was capped after16 properties, with later
fields unobserved; no instance scalar/text values or Attribute traversal.
Each call sampled FINAL points=(1,0)/ranks=(0,0,0) unchanged and arrays 3/3,
observers_added=0. CANCEL restored original arrays/cells with all hooks0;
repeat cancellation found no patch, process closed. No ERROR/Traceback,
UNAVAILABLE or ABORT. The empty candidate array is now verified, not assumed.
It is consistent with the prior empty preview return, but does not prove
causation/rendered orange text, eligibility/cost, purchase failure or effect.
Keep both runs/PNG and all eight original ZIPs/snapshots unchanged. Next design
is a bounded read-only comparison of exact observed presentation string/display
fields; at that review no next build/test existed. v0.2.9 below supplies it.

v0.2.9 now implements the next four-string comparison: Description,
NoConstraintText, Prefix and Suffix, targeted exact loaded StrProperty
name/owner/flags/dimension/observed offsets before named SDK getattr. Scalar
owner was not printed in v0.2.8 and is a new fail-closed check. Exact str,
output<=512 characters with length/clipping/escaping; no formatting/template
evaluation, unknown-value repr, Boolean/float values or Attribute traversal.
Fresh current array/count/reference/class and unchanged _upgrade_state are
checked around reads; reference/array changes abort before another target,
field unavailable is distinct from empty and complete array/sample coverage.
Maximum4 refs/4 fields per target,48 values; no new hooks/writes/loads/calls.
Per-call FINAL only after full baseline comparison. Old insertion/rollback,
solo/session guard, observers/cleanup and manual duration stay intact.
67 prior functions are AST-identical, five change version labels only; four
new functions/fixed field tuple and factory metadata/button4 route change,
still19 options. Two prior version assertions and one route assertion update.
127 mocks (108 prior plus19 new), runtime syntax and AST proof passed.
See evidence/v029_presentation_text_plan.md for the historical build checks.
At build time no v0.2.9 game result existed; the completed live result follows.
Purchases/persistence/effects/co-op/release remain unverified.

The v0.2.9 live result is preserved in evidence/v029_live_presentation_text_result.md
and v029_user_test.log (94,218 bytes, SHA-256
9f73970ca42390bf96904b0af174ebaec93faf77b40db6baf5a9ab3979bb3279).
All three installed files matched workspace/original ZIP before doc edits;
exact tested files are under archive/tested_runtime/v0.2.9. The fresh solo
listen-host initialization retained both originals and registered one inert
grade 0 node index 14/tier 7 among 39 skills. Two synchronous inspections accepted
all allowlisted scalar schemas including the newly checked declaring owner.
Each verified MorePep16/16 and Myelin8/8 fields, all six references; Overclock
count0/fields0/0 text=NOT_APPLICABLE. Native Description strings contain
$NUMBER$ templates; all NoConstraintText/Prefix/Suffix values were verified
empty. Both calls had complete_targets3/3, fields24/24, no clipping and
observers_added0; no UNAVAILABLE/ABORT/ERROR/Traceback. 222 reused SCHEMA
messages are metadata/membership checks, not additional snapshots.
FINAL sampled points=(1,0)/ranks=(0,0,0) stayed unchanged. CANCEL restored
original MorePep/Myelin and True/False/True cells with all hooks0; repeat
CANCEL found no patch and the review found BL2 process count0. No saves were
parsed/edited. Runtime/pyproject and all nine original ZIPs remain unchanged;
tested snapshots v0.2.7/v0.2.8/v0.2.9 and prior evidence retain their hashes.
Only docs/default ZIP may change. The127 previous mocks apply to frozen code.

The next useful read-only design is a small observed native display-flag
comparison and validated Attribute descriptor/typed reference identity. Actual
display flags, attribute identities/values and formatter semantics were not
read in v0.2.9. Never guess masks, evaluate/traverse Attributes, invoke native
formatters or copy effects/presentations/constraints based on template text.
At that review no next build/test existed; v0.2.10 below now supplies it. Do not repeat the completed strings
solely to reconfirm them; later gameplay milestones still need separate scope.


v0.2.10 implements the next native display comparison: exact bool values for
bDontDisplayNumber, bUseCustomNumberPlacement, bEnableTextColor, and only a
typed Attribute reference identity/known absence. Targeted loaded descriptors
must match name/declaring owner/type/flags3/dimension1/observed offsets116 or64;
Attribute declared UClass/name AttributeDefinition required before payload.
Actual non-None Attribute must be SDK UObject/Class identical to declared
class; unknown subclasses/same-name different classes refuse before path.
None is verified absence, not unknown. No Attribute traversal/evaluation or
native formatter calls. Boolean packing is left to the SDK, never guessed.
These schema/owner/payload checks are newly simulated, not engine verified.

Reuse unchanged _upgrade_state/_presentation_text_reference and per-call
baseline, current session/tree/ownership/points/ranks/inert patch plus fresh
array/count/membership/class checks. Accepted typed Attribute descriptor/
current field/Class is rechecked around bounded escaped SDK path and outside
field exception handling before logging; changes abort before another field/
target. Field unknowns are UNAVAILABLE while unchanged-state guards hold,
not empty/absent. Unknown/changing arrays/presentations abort; FINAL only after
full guarded comparison, no repair/refund. Maximum4 sampled refs/target,
fixed4 field captures/ref,48 records/call; bounded Attribute rereads<=4/entry,
paths<=384. Separate array/sample/flag/Attribute/present/absent/partial coverage.
No strings reread, copies, overrides, loads, new hooks or gameplay writes.

151 unique mocks passed in13.378 seconds (127 established plus24 new);
runtime syntax/AST scope proof passed.70 of76 old functions AST-identical,
six version-label-only changes, four new functions/fixed flag tuple and
factory metadata/button4 route change. Two prior version assertions/one route
assertion updated; insertion/rollback/manual duration/old cleanup preserved.
See evidence/v030_presentation_display_plan.md and docs/NEXT_CODEX_TASK.md
for the historical fresh solo Offline1,4,3 test. At build time no v0.2.10
game result existed; the completed result follows. No direct install/save
writes or automated purchases/effects were performed.

v0.2.10's live result is preserved in v030_user_test.log (259,457 bytes,
SHA-256 88a79e741abb6b217f8f8a23c42e14578c11c75f2686abcfecc13d2c74e294fb)
and reviewed in evidence/v030_live_presentation_display_result.md. Installed
three files matched the original ZIP/source before doc edits; exact tested
files are under archive/tested_runtime/v0.2.10. Fresh solo listen-host
initialization registered one inert grade 0 node14/tier 7 among 39 skills,
keeping originals and removing observers. Four synchronous calls verified
all 18 native flags (False/True/True) and five AttributeDefinition identities
each. Myelin's second presentation Attribute refused exact declared-class
validation: actual wrapper/class/ancestry/path unobserved, not None or a
known subclass. MorePep flags12/12/Attributes4/4; Myelin flags6/6/Attributes1/2
PARTIAL; Overclock count0 NOT_APPLICABLE. Each END fields23/24, targets2/3,
observers_added0. No ABORT/ERROR/Traceback. All BASELINE/FINAL points=(1,0)/
ranks=(0,0,0) unchanged. CANCEL restored arrays/cells with all hooks0;
two repeated cancellations found no patch, process count0 at review.
All ten original ZIPs and four tested snapshots checked intact; runtime/
pyproject remain frozen. Only docs/default ZIP may change in this review.
Existing151 mock results apply to unchanged code; no repeat suite needed.

The user reports spending a point in Overclock and seeing1/1 in an earlier
process, then Alt+F4/restarting for the documented read-only run. Record this
as positive user-observed UI purchase/rank evidence. The retained restarted
log has no transaction or grade 1 capture; one unspent point and node grade 0
were sampled in every comparison. Reset state after restart is observed,
not a save audit or proof Alt+F4 prevents saves. No save parsing/edit/backup
restore/point repair in this review. Do not repeat purchasing for missing
evidence. Further purchases/automatic effects/point-grade-save writes need
separate scope/recovery. Persistence and the node +15-second effect remain
unverified; the effect is still intentionally inactive.

Next useful design can classify the refused Myelin Attribute using SDK
wrapper/loaded actual UClass/bounded ancestry metadata only. Do not relax
exact-class checks, guess a subclass or evaluate/traverse Attribute values.
No next build/test exists in this review; no repeat of completed flags/
identities merely to reconfirm them.

## v0.2.11 build and completed metadata diagnostic

The user requested the next step, then asked to do more tests at once. One new
item4 combines the refused Myelin Attribute's wrapper, actual loaded UClass
identity and bounded metadata ancestry in one game session. No repeated native
flags/text/identities, combined old observers, purchases or effects. The current
source advances to11 for this authorized diagnostic; frozen v0.2.10 original
ZIP/tested snapshot remain unchanged. At build time the live result was pending;
the completed capture is recorded below.

Inspect only current Myelin index 1's exact observed shield-capacity presentation
path, actual SDK WrappedArray count2..256, loaded array/member/class and exact
Attribute descriptor owner/name/ObjectProperty/flags3/offset64/dimension1/
declared SDK UClass. None is known absence. Unknown wrapper/class never coerced/
repr'd/traversed. Actual class must be real SDK UClass before bounded Name/path/
SuperField metadata reads. Never read Attribute object's path or values.
SDK docs read only before choosing explicit SuperField reads; no iterator or
_inherits/native calls. Names<=96, paths<=384, eight classes/cycle detection,
COMPLETE/CAPPED/CYCLE/UNAVAILABLE separate. Relationship uses verified loaded
parent identities, not names. At most39 Attribute getter reads of one field.
Captured class labels/links and current schema/field/Class/presentation path/
state revalidated. Changes or unknown state abort without repair/refund.

179 unique local mocks passed in18.428 seconds (151 established plus28 new).
The first targeted run failed two timing assertions because fixture mutation
occurred before metadata capture. Corrected the fixture to change at the second
declared-class path read, during captured ancestry; full suite then passed.
Runtime syntax and AST proof passed:73 of80 old functions AST-identical, seven
version labels only, four new helpers/inspector, factory19 options. Old state/
reference/compatibility guards, insertion/rollback/manual duration and cleanup
unchanged. New mock checks cover schema/type/unknown metadata, bounds/cycles,
loaded identity relationships, no unrelated payload/attribute traversal/calls/
writes, changing field/descriptor/class/presentation/path/state and restoration.

## Completed v0.2.11 live result and its historical follow-up

The user performed the prepared diagnostic and answered done to CANCEL/full exit.
The raw v031_user_test.log is 93,722 bytes/410 lines, SHA7339178b278e7e4c63a8ec4272a692c199840c82c99017be2198901f1a1f3b00.
Capture manifest and exact three tested files are immutable at 88a904e, reviewed
independently by Justin. Two calls 65-212/214-361, rather than requested one,
verify SDK_UOBJECT/SDK_UCLASS actual WillowGame.ResourcePoolAttributeDefinition.
Both five-class COMPLETE chains include declared Engine.AttributeDefinition,
followed by Engine.AttributeDefinitionBase, Engine.GBXDefinition and Core.Object.
DERIVED comes from the unchanged SDK identity/link guards, not string names.
BASELINE/FINAL points=(1,0)/ranks=(0,0,0) match; END observers_added0.

ARM25; repeated ARM refused28. Owned solo listen-host rosters30/35 and one inert
registered node36 keep originals; grade 0/index 14/tier 7 logged. CANCEL restores
original MorePep/Myelin and cells385, confirmed386. Four observer families zero
after last call363/374/376/384; repeated CANCEL410 finds no patch after zero
cleanup388/399/401/409. Capture machine checks independently find process0
before/after preservation, not inferred from log silence. No repeat test needed.

The corrected standard-library reviewer 44ad64c is also independently accepted:
236 unique tests 0failure/error/skip. It rejects contradictory relation labels
and actual removal/rollback failures even after a retry. Parser success cannot
establish SDK identity, process exit/install equality or log authenticity.
See evidence/v031_live_attribute_class_result.md for exact provenance/hashes,
raw records, package checks and limits. Runtime/pyproject and all 45 original
protected artifacts remain frozen; fifth exact snapshot includes historical
README. Current docs/default ZIP may update README only.

Earlier user-reported purchase1/1 remains separate UI evidence; captured restarted
state has one point/grade 0. No captured cost/transaction/save/persistence/effect
proof, no purchase failure claim and no repeat purchase to recover missing data.
Node +15s remains inactive; manual prototype remains independent and unchanged.

Independent readiness research PR#4 at f8aa2fe passed peer review (sequence71),
including independent reproduction of eleven inert probes and the manual test. It
identifies synthetic ownership/signature/lifecycle/cleanup gaps and proposes
one bounded metadata-only Deathtrap diagnostic, without native GetSkillManager
calls, hooks/writes/purchases or grade-zero guard relaxation. It is a proposal,
not an implemented diagnostic or observed engine failure. Read it before
separately scoping runtime work; docs/NEXT_CODEX_TASK.md carries the next design.

## Completed v0.2.12 live metadata capture

See [the reviewed result](../evidence/v032_live_deathtrap_metadata_result.md),
[manifest](../evidence/v032_capture_manifest.json) and immutable log/snapshot.
Original versionedZIP and testedREADME remain unchanged; current defaultZIP
README reflects the reviewed partial result. The next task is metadata-owner
design; no lifecycle observer or effect readiness is established by this run.
