# v0.2.6: all six core helpers observed; trace limit and restoration passed

The user reported "done" after the v0.2.6 instructions. The complete log was
preserved as v026_user_test.log (49774 bytes) before any relaunch. Installed
runtime and pyproject match workspace and the tested versioned ZIP byte for
byte. No runtime code changes during this review. Preserve all six tested
v0.2.1-v0.2.6 versioned ZIPs unchanged.

## Observed October 9, 2026, 23:53–23:55 Pacific

UTC timestamps below are October 10:

- 06:53:57.790: main-menu ARM accepted; repeated ARM refused as already armed.
- 06:54:12.219–.224: PRE verified listen_host with exactly one owned local
  player and one owned roster player. One inert candidate entered the native
  initializer, and the engine registered one node plus both originals among
  39 runtime skills. Initialization observers removed (remaining=0).
- 06:54:58.705–.706: discovery scanned 20120 functions, accepted 19 candidates
  after artifact/equip exclusion, and SELECTED/METADATA listed exactly the
  intended ten canonical loaded methods. All six previously missed helpers
  fit the unchanged cap alongside Init, Nav_Down, Nav_Left and Nav_Right.
- START inventory scanned two objects, found zero owned views; callbacks later
  verified a live owned UI. START registered 20 observers with baseline PRI
  points=(1,0), ranks=(0,0,0) in node/MorePep/Myelin order. Repeat START refused.
- 06:55:04.234–06:55:10.181: captured 48 events from 51 callback attempts,
  with three duplicate skips. Every event verified the same live owned UI:
  Transient.StatusMenuExGFxMovie_1:SkillTreeGFxObject_1. UI point=1 and target
  tier unlocked=True in every event. No foreign-owner/class skip appeared.

| Selected method | Captured events | Observed role/limit |
|--|--:|--|
| PostNav | 7 | Current/rollover transitions; final node PRE captured |
| Navigate | 6 | Deathtrap -> CookingUpTrouble -> MorePep -> Overclock |
| HandleInputKey | 12 | Normal UI input path; no input arguments read |
| UpdateInfoBox | 12 | Native skill-info update including node PRE/POST_ANY |
| Flash_SetSkillPointProperties | 2 | Initialization with selection unavailable |
| Flash_SetSkillPointProperties_AS | 2 | Initialization with selection unavailable |
| Init | 2 | Screen initialization and Deathtrap selection |
| Nav_Down | 0 | Hooked, no captured event before the limit |
| Nav_Left | 2 | Deathtrap -> CookingUpTrouble |
| Nav_Right | 3 | MorePep reached; node navigation truncated by limit |

- All six targeted helpers produced events. The point-display methods appeared
  during initialization with no verified selected skill; do not attribute
  their events to Overclock or infer an upgrade prompt from them.
- MorePep was first observed as rollover while current was Deathtrap, then as
  both current and rollover. Their distinct values were retained correctly.
- At 06:55:10.177 Navigate POST_ANY selected UVH_DeathtrapOverclock while
  rollover was still MorePep. PostNav PRE retained that state. UpdateInfoBox
  PRE at .180 and POST_ANY at .181 verified both current and rollover as
  Overclock. All definitions passed unique owned runtime-entry/index checks.
- Event 48 triggered the configured event limit at .181; capture was cleared
  and observers removed immediately. This is an expected bounded stop, not
  an error or a 90-second expiry. The active window was about 11.47 seconds;
  captured screen activity lasted about 5.95 seconds.
- FINAL at .182 verified PRI points=(1,0), all three ranks=(0,0,0),
  unchanged_from_start=True. STOP inventory at .189 scanned three objects,
  found one owned view, and printed the node's current/rollover selection.
  STOP reported remaining=0, captured=48, callbacks=51, skipped=3.
- Manual STOP repeats at 06:55:23.350/.24.656 retained zero hooks. Because the
  trace had already stopped, those repeats did not perform another FINAL
  point/rank check. The last verified point/rank sample is .10.182.
- CANCEL at 06:55:25.835 verified RESTORE result=True: MorePep/Myelin and
  True/False/True occupancy restored; NATIVE ARRAYS RESTORED. UI/upgrade/init
  observers were zero. Repeat cancellation at .27.656 found no patch left.
- No ERROR or Traceback appears. The unrelated SDK legacy-import deprecation
  warning remains present. The user's "done" follows full-exit instructions;
  process closure was not independently probed. No saves were read/edited/
  restored by Codex during this review.

## What passed and what remains unknown

The priority fix is verified in engine: all six previously missed core helpers
were selected and captured, excluding artifact/equip candidates. The owned
native UI reached MorePep and Overclock and updated the node's info box.
The direct STOP inventory also worked while the UI was alive. Sampled points/
ranks stayed unchanged, the event bound removed all observers and native-array
rollback passed.

The cap cut the trace before any Myelin selection event, and before the final
node PostNav/Nav_Right POST_ANY phases. This does not establish that the user
failed to highlight Myelin later; subsequent UI activity was unobserved.
The v0.2.5 run separately verified Myelin selection. No unchanged v0.2.6 rerun
is needed simply to reconfirm the six helper call paths.

POST_ANY does not independently prove execution if another mod blocked a
call. Current/rollover fields are direct observations. Neither UI point/tier
fields nor UpdateInfoBox activity reveals actual eligibility/cost/upgrade text.
UpdateInfoBox has zero parameters; reflected SkillDesc, GradeDesc,
NextGradeText and SkillState are raw locals, not verified hook arguments.
Do not read them as args or invoke a function to manufacture evidence.
The old upgrade observers were not started in this run; their empty cancellation
summaries do not measure eligibility/cost call activity. Purchase, refund,
save persistence and the automatic +15-second node effect remain unverified.

## Next useful diagnostic

Focus the next bounded passive design on the three target definitions and
their native skill state/info display, rather than capturing all input traffic
or merely widening the 48-event bound. Filter irrelevant captures before they
consume the event budget while still counting every callback against the
attempt/time limits. Preserve all ownership/current-tree/solo/unchanged-state
guards and cleanup. Add budget regressions with the observed nested navigation
sequence so incidental input/other-skill traffic cannot starve target coverage.

PlayerSkillTree:GetSkillState was discovered in v0.2.3 with SkillDef input,
OutSkillState (SkillTreeSkillStateData) output and Boolean return metadata.
This is a concrete candidate for normal-call observation, not permission to
invoke it. Revalidate loaded function/struct metadata and SDK output handling
before designing any args/ret reads. Unknown representations must fail closed.
Do not infer its actual activity from this trace: it was not hooked.
No new runtime or game procedure is ready yet. No points, saves, constraints,
effects, co-op or release work; later purchase still needs explicit scope and
point/grade/save recovery. Native-array restoration cannot undo a purchase.

## Preserved hashes

| Artifact | SHA256 |
|--|--|
| v0.2.6 complete log | 8509efded92cb6787964bbfe178821a5cd1ff2d1b3c4bccf7d2304e2cbc61281 |
| v0.2.6 installed/workspace runtime | 8134f90a3ce54b9b88ab964eb2cb187ecc385e1d241f69633fc2d5b1b79894a1 |
| Tested v0.2.6 ZIP | cf09a3f4fbfb0847409f4fcd78595d4e97be0548bd743350c7322990d525e2b5 |

74 existing mocks remain applicable with no runtime changes this review.
Documentation updates rebuild the default ZIP only. Syntax and isolated
package/import/layout/source checks are repeated; all six versioned ZIPs
and runtime/log hashes are verified unchanged.
