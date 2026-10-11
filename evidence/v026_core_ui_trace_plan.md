# v0.2.6: prioritize discovered core skill UI functions

Later live result: v026_live_core_ui_result.md verifies all six helpers,
event-limit cleanup and restoration. This document records the build design.

This build follows the preserved v0.2.5 live result, not a purchase attempt.
See v025_live_ui_trace_result.md: native owned selection/restoration passed,
but the ten-function cap selected four artifact paths and omitted six helpers.
Those helpers were discovered, not hooked; no call conclusion follows.
At build time no v0.2.6 game result existed.

## Runtime change

Only _ui_candidates changes behavior. Exclude method names containing artifact
or equip (case-insensitive) before descriptor reflection. Prioritize this exact
order among the canonical loaded descriptors actually found:

1. PostNav
2. Navigate
3. HandleInputKey
4. UpdateInfoBox
5. Flash_SetSkillPointProperties
6. Flash_SetSkillPointProperties_AS
7. Init
8. Nav_Down
9. Nav_Left
10. Nav_Right

All ten names were discovered in the preserved game log. Init and the three
navigation methods produced useful owned selection events. extInitTree,
Nav_Up, Nav_Back and Flash_SendInitialSkillData are lower-priority fallbacks,
followed by the other discovered matching methods in deterministic path order.
The priority list never creates a hook path. Each run revalidates exact Function
class, SkillTreeGFxObject outer and canonical WillowGame.SkillTreeGFxObject path.
Nested/foreign/duplicate metadata is rejected as before.

The cap stays ten functions/twenty hooks. CANDIDATE remains discovery only;
new SELECTED entries identify the actual chosen set alongside raw METADATA.
Reflection stays <=8 fields per selected function, discovery <=30000 objects,
candidate logging <=24. Raw properties may include locals; no signature inference.

Among the other existing functions, inspect_overclock_purchase,
start_upgrade_trace and start_ui_trace change version labels only.
The other 59 functions remain AST-identical to the v0.2.5 ZIP. Insertion,
native rollback, solo/current-state guard, UI callbacks/cleanup and verified
manual +15-second duration prototype are unchanged. Factory metadata/title
and button 7's display label identify v0.2.6. The same 17 buttons remain.

## Preserved observation requirements

PRE and POST_UNCONDITIONAL callbacks return None. POST_ANY can fire for a
call another mod blocked; it does not establish execution. No args/ret reads,
native invocation, overriding/blocking, package loads or observer game-state
writes. Normal UI activity is the sole source of events.

Reuse the unchanged current Gaige/controller/pawn/world/PRI/tree, exact owned
inert patch/runtime registration/index, both sole-player rosters and known
unchanged point/rank guard. Candidate grade remains zero. Require exact UI
class and WPCOwner==pc before reading its selection. Current and rollover
are separate; each definition must have a unique owned runtime entry/index.
Unknown data is unavailable/unverified, never guessed.

Direct UI points/tier-unlock/selection observations are not actual eligibility
or cost. Merely observing a point-display function still does not read its
arguments. Inventories remain <=32 objects/<=4 printed owned views; zero owned
views outside Skills does not establish that a live UI is missing.

Bounds stay 48 events, 2048 attempts including foreign UI, two copies per
state, 90 seconds checked on the next callback. No background timer: STOP
is required. Stop/cancel/disable/error/state change/limits clear capture first.
Failed hook removals stay inert and retained for retry; refuse overlapping
UI/upgrade/init/loading traces. Do not widen or bypass guards to get events.

## Local validation and game test

74 unique mocks pass. Three new regressions cover:

- All 24 names from the v0.2.5 live discovery plus 30 unrelated selection
  candidates. The six missed helpers and four proven anchors fit ten slots,
  independent of discovery order. Selected helpers register passive callbacks,
  capture owned state and remove cleanly without point changes.
- Missing/foreign/nested/wrong-class priority methods cannot manufacture
  paths. Loaded dot-form paths normalize to the existing canonical form.
- Artifact/equip descriptors are excluded before reflection, using poison
  descriptors to detect accidental inspection.

Before the fix, the UI suite ran 17 cases with two failures: the live crowding
case omitted all six core helpers and the poison artifact case refused startup.
The missing/foreign metadata case already passed. After the fix, all 74 tests
passed. Syntax and isolated package import/layout/source checks are required
before shipping. All five tested v0.2.1-v0.2.5 ZIPs and the v0.2.5 log stay intact.

Follow docs/NEXT_CODEX_TASK.md: close BL2, install only this project folder,
verify exact v0.2.6 title at main menu, 1 ARM before Continue as backed-up Gaige
Offline, 7 START in map, open Skills/navigate all three without clicking/buying,
8 STOP, 3 CANCEL, fully exit. Use only 1,7,8,3; no point spending/respec/travel.
Preserve/hash the final log before relaunch. Partial/empty/limit results are
evidence, not a reason to buy or force a native query.

Verify installed version/hash, actual SELECTED paths, owned events per method,
sampled final points/ranks, zero observers and RESTORE result=True with original
MorePep/Myelin and True/False/True occupancy. Clarify completion if final
cleanup/exit evidence is missing. No node effect, refund/save persistence,
co-op or release claim. Any later purchase needs explicit authorization and
point/grade/save recovery; native-array rollback cannot undo a purchase.

## Completed package checks and artifact hashes

Syntax compilation and verify_package.py passed: inert isolated import,
ZIP integrity, exactly three files in one folder and byte-for-byte source match.
The new versioned ZIP is 26629 bytes and equals the checked default ZIP.
The regression fixture was compared to the preserved live log: all 24 names match.
All five tested ZIP hashes and the v0.2.5 log were rechecked unchanged.
At build time no v0.2.6 game result existed.

| Artifact | SHA256 |
|--|--|
| v0.2.6 runtime | 8134f90a3ce54b9b88ab964eb2cb187ecc385e1d241f69633fc2d5b1b79894a1 |
| v0.2.6 versioned ZIP | cf09a3f4fbfb0847409f4fcd78595d4e97be0548bd743350c7322990d525e2b5 |
