# v0.2.5: bounded read-only UI navigation/refresh trace

The user authorized continuing with "lets start" after v0.2.4 setup/stop/
restoration passed with zero callbacks despite all three skills being highlighted.
This is a different observation: discovered navigation/refresh functions and
owned UI selection snapshots, not another run of the same cost/eligibility hooks.
Source/package is v0.2.5; the later live selection/restoration result is now
recorded in v025_live_ui_trace_result.md. Actual eligibility/cost are unverified. Purchase/effect/persistence
remain out of scope. Preserve all five tested versioned ZIPs unchanged.

## Why these observations

The v0.1.9 game log captured SkillTreeGFxObject.Init and extInitTree when Skills
opened, so loaded versions of those functions are preferred anchors. The
[UnspecSkills author's source](https://github.com/ZetaDaemon/bl-sdk-mods/blob/main/UnspecSkills/__init__.py)
uses HandleInputKey, PostNav, UpdateInfoBox and other UI refresh methods, plus
CurrentSkill, CurrentSkill_Rollover, WPCOwner and NumSkillPoints. This supports
names only; current loaded metadata must still supply every hook path.
No mutating code or native calls from that mod are copied. UI field semantics
and navigation timing must be verified in our engine run, not assumed from it.

Installed pyunrealsdk v1.10.0 hooks documentation supports PRE and
POST_UNCONDITIONAL (used as POST_ANY in logs). PRE returns None; POST_ANY runs
even if another hook blocks the function. Neither phase invokes func, reads or
edits args/ret, blocks or overrides. Events report phase/selected state and do
not establish that a blocked function executed or returned an eligibility result.
SDK stubs were read as data only, never executed.

## Discovery and scope

Explicit button 7 only. Scan <=30000 loaded Function objects, accepting exact
Class Function / Outer SkillTreeGFxObject / canonical WillowGame.Class:Method
metadata; reject nested/state/foreign and duplicate paths. Method-name filters
cover navigation, rollover, selection, input, info, initialization and refresh.
Cost/CanUpgradeSkill/RequestSkillUpgrade are not selected by those filters.
Prioritize observed Init/extInitTree anchors, then navigation, input and info.
Log <=24 candidates and <=8 raw field descriptors for each of <=10 hooked
functions. Raw fields include locals and are not callable signatures. No args
are accessed, and no native function is invoked to verify them. Reflection or
registration failure aborts and cleans up all owned partial registrations.

Reuse the unchanged v0.2.4 _upgrade_state guard at start and every callback:
same Gaige/controller/pawn/world/PRI/current recorded tree, inert grade-zero
node, exact native candidate/original arrays, unique owned runtime entries,
valid indices/first tier, SDK-named solo mode and exactly one owned local and
roster player. Both PRI point fields and all three grades/indices stay unchanged.
Changed/unknown state removes observers without refund, repair or native-array edits.

Read CurrentSkill/CurrentSkill_Rollover only on exact SkillTreeGFxObject whose
WPCOwner equals the guarded controller. Each non-null definition must have the
exact SkillDefinition class, one runtime registration owned by this tree and
a valid index resolving to that definition. Foreign/unknown selection receives
an unverified/unavailable label, not an inferred skill identity. Verified other
skills may be logged to show where navigation starts. NumSkillPoints must be
an exact nonnegative int; target first-tier bUnlocked must be Boolean. These
are direct UI/tier fields, not proof of eligibility or cost.

Start/stop also scan <=32 SkillTreeGFxObject instances and print <=4 owned views.
No owned UI at start is allowed because first opening Skills may create it.
These snapshots can supply selected/hovered state even with zero hook callbacks;
the selection at STOP may differ after leaving Skills. No selection is forced.

## Limits and cleanup

<=10 functions / 20 hooks, 48 captured events, 2048 callback attempts (including
foreign UI), two copies of each path/phase/view, 90 seconds checked on the next
call. There is no background timer; always press STOP. Reentrancy is ignored.
Context is cleared before stop/cancel/disable/error/state-change/limit cleanup.
Failed removal retains inert hooks for retry and prevents another trace start.
New UI and old upgrade traces refuse overlapping starts. Existing loading/legacy
buttons remain for history; use only 1,7,8,3 in this test.

Among the v0.2.4 functions, only three change: cancel_init_node adds UI cleanup;
inspect_overclock_purchase updates its version header; start_upgrade_trace adds
UI mutual exclusion and a version label. All other established functions remain
AST-identical, including _upgrade_state, manual duration and native insertion/
rollback. Of the original v0.2.1 functions, only cancellation adds cleanup.
No observer-driven game writes, game-console commands, save edits or effects.

## Local checks and evidence limits

71 unique mock tests pass: 57 established plus 14 UI cases. New cases cover
PRE/POST_ANY selection changes without args/ret/native calls/writes; direct
zero-call inventories; unknown/foreign selection/ownership; exact metadata,
priority and scan/field/function/object/output bounds; no UI yet; missing state;
mutual exclusion; peer/point/rank/tree/effect changes; duplicate/event/time/
callback limits; partial registration and foreign hook preservation; inert
failed-removal retry; reentrancy/errors; cancel/disable and final-point changes.
Syntax, exact-three-file ZIP/source/integrity and isolated import checks pass.
Mocks cannot establish UI events, real wrappers, eligibility, cost or save equality.

## Test and review

Close BL2, replace one mod folder from v0.2.5 ZIP. Offline/backed-up solo Gaige.
Verify MODS title v0.2.5; press 1 at MAIN MENU before Continue. In map press 7,
then open Skills and hover/highlight Overclock/More Pep/Myelin, also using arrow
keys/controller navigation if available, about five seconds each. Do not press
purchase controls, respec or travel. Finish within 90 seconds. Press 8, then 3,
fully exit and tell Codex done. An abort/empty result is evidence, not a reason
to buy or invoke a function. See docs/NEXT_CODEX_TASK.md for expected tags.

On done, preserve the final log before relaunch and confirm restoration/closure.
Review discovered paths and PRE/POST_ANY events plus owned start/stop snapshots;
distinguish callbacks=0 from foreign-owner skips or unverified selections.
Require final points/ranks unchanged, both trace types/init observers removed
and native-array RESTORE result=True. Purchase work still needs actual
eligibility evidence plus explicit authorization and point/grade/save recovery.

## Build hashes

| Artifact | SHA256 |
|--|--|
| v0.2.5 install ZIP | `6d592c187efe3c04ce9de7ba957a3a1b72489e02ce1cea7fb7cd797d4ae71ab3` |
| v0.2.5 runtime | `39effd4c589c8866beacadef9ea575c8886558dee8098aa0c77a0b8f5b8fc6cb` |
