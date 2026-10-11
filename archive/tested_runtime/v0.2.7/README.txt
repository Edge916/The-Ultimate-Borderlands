Ultimate Vault Hunters v0.2.7 - OVERCLOCK FOCUSED STATE TRACE.

NEXT TEST: observe normal native query returns and grade-description text for
Overclock, More Pep and Myelin. The node is still INACTIVE. DO NOT BUY ANY SKILL.
90 local mocks pass. NO v0.2.7 game result yet.

v0.2.6 proved core-helper calls but its 48-event cap stopped before Myelin.
This trace uses only three POST observers and four captures per function/skill,
so input/other-skill traffic does not consume the event budget.
Hook args are copied inputs: OutSkillState is NOT a finished output. It and
UpdateInfoBox locals are never read. Query Boolean does not mean eligibility.

INSTALL:
Close BL2. Replace only sdk_mods/UltimateVaultHunterDeathtrapBoost with this
ZIP's folder; keep one project mod and all SDK/core mods. The folder directly
contains __init__.py, pyproject.toml, README.txt; no nested mod folder.
Use the already backed-up Gaige alone, Offline, in a fresh BL2 process.

ONE TEST:
1. At MAIN MENU before Continue, confirm the exact MODS title:
   UVH v0.2.7 - OVERCLOCK FOCUSED STATE TRACE
   Press 1 - ARM ONE GAIGE INIT NODE TEST, then Continue.
   ARM after Continue refuses; it must precede tree initialization.
2. In the map choose 9 - START FOCUSED STATE TRACE.
   Use 9/10 for this test, not 5/6 or 7/8.
3. Open Skills. Highlight/hover Deathtrap Overclock, More Pep, then Myelin,
   about three seconds each. Use navigation keys/controller if needed.
   Do not click a skill, right-click or press purchase/upgrade controls.
   Finish promptly within 90 seconds.
4. Choose 10 - STOP / REPORT FOCUSED STATE TRACE.
5. Choose 3 - CANCEL / RESTORE NATIVE ARRAYS, then fully exit BL2.
6. Tell Codex "done" and leave BL2 closed until the final log is preserved.
   Restart before normal play to discard the engine-built prototype cache.

Use only 1,9,10,3. No legacy insertion, old traces, manual boost, travel,
respec, co-op or point spending. On abort/limit/error, stop, cancel, exit and
report. Empty/partial results are evidence; never force a query.

WHAT IS OBSERVED:
Startup validates loaded canonical function metadata against the previously
logged signatures for PlayerSkillTree:GetSkillState, and SkillTreeGFxObject:
GetSkillDescriptionForGrade/UpdateInfoBox. Requires all three exact Function
classes/outers/paths; rejects missing/duplicate/changed metadata.
Scan <=30000 functions, reflect <=16 fields per function and <=12 raw native
skill-state struct descriptors. Metadata is not permission to invoke a call.

POST only, for functions allowed to execute. Current Gaige/controller/pawn/
world/PRI/tree, both sole-player rosters, owned inert patch/runtime indices
and known unchanged PRI points/ranks are checked every callback. Node grade=0.
GetSkillState requires exact current tree, matching input wrapper type and
target SkillDef before reading actual Boolean ret. No OutSkillState/ReturnValue
args read, tuple reinterpretation or native invocation.
Descriptions require exact UI class/WPCOwner, verified owned selection,
matching input wrapper/target SkillDef/PlayerOwner, bounded integer Grade/
GradeModifier, Boolean bIncludeHTML and actual string ret. Log the requested
grade, modifier, HTML flag, original text length, first 512 characters and
separate validated current/rollover. Text is a returned preview, not proof of
the rendered orange prompt or eligibility. UpdateInfoBox observes owned
target UI fields only; never args, ret or locals.

Bounds: four results per function/skill, two copies per distinct result,
maximum 36 captures across the nine buckets within the unchanged 48-event cap.
2048 callback attempts (including skips), 90 seconds checked on the NEXT call.
No background timer: always STOP. No args/ret edits, overrides/blocks, loads,
observer game-state writes, point/grade/save/effect/constraint changes.
Unknown/mismatched data stops and cleans up; import installs no hooks/writes.

Stop/cancel/disable/error/changes/limits clear capture before removing only
owned hooks. Failed removals stay inert for retry and block all other traces.
STOP verifies final PRI points/ranks and reports nine observed/missing buckets.
Old UI/upgrade/loading traces refuse overlap in either direction.

EXPECTED LOG:
[UVH-INITNODE] one inert runtime node/both originals, observers remaining=0.
[UVH-STATE] STRUCT/METADATA; START v0.2.7 POST observers=3;
RESULT skill=... detail=QUERY_RETURN / DESCRIPTION / UI_VIEW;
FINAL unchanged_from_start=True; STOP remaining=0; nine SUMMARY buckets.
[UVH-NEWNODE] RESTORE result=True: MorePep/Myelin, True/False/True restored.
No result is NOT OBSERVED; it does not establish query/eligibility failure.

ROLLBACK:
CANCEL restores only matching owned native arrays; independent changes are
not overwritten and failed restores retain snapshots. It cannot clear player
caches, refund points, restore grades or undo a save. Restart after every test.
If restoration fails, fully exit without saving and report/restart.

PRESERVED:
All six tested v0.2.1-v0.2.6 ZIPs stay unchanged. 58 existing functions remain
AST-identical to v0.2.6, including insertion/rollback, solo/current-state guard,
old observer callbacks and verified manual Deathtrap 60 -> 75 prototype.
Five new diagnostic functions; CANCEL adds cleanup; old trace STARTs add
mutual exclusion/version labels; read-only snapshot changes version label.
Factory has 19 options; no automatic node effect/purchase/persistence/co-op.
