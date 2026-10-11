# v0.2.7: passive target query/description observation

This is the pre-test design record. The run is now complete; see
v027_live_focused_state_result.md and the later result section below.

v0.2.6 verified all six core helpers, including node UpdateInfoBox, but broad
input/navigation traffic consumed 48 events before Myelin. Preserve that log
and the six tested versioned ZIPs. This build observes only three natural calls
with capture quotas per function/target. At build time no v0.2.7 game result existed.

## SDK finding that changes the design

Installed unrealsdk v3.2.0 / pyunrealsdk v1.10.0 stubs were read as documentation
only, never executed. hooks.add_hook documents a separate actual ret argument;
args.ReturnValue may be incorrect. POST runs only for an allowed function.
BoundFunction.__call__'s output tuple is a different API and is not a hook return.
The Python hook binding converts only the return property before dispatching
the callback. See the [primary binding implementation](https://github.com/bl-sdk/pyunrealsdk/blob/master/src/pyunrealsdk/hook.cpp).

The BL2 implementation copies/extracts args before native execution and passes
that same copy to post hooks; it updates the separate return proxy, not copied
out fields. Therefore reading args.OutSkillState as the final native output
would be unsound. v0.2.7 never reads that field. This interpretation follows
the [primary BL2 hook implementation](https://github.com/bl-sdk/unrealsdk/blob/master/src/unrealsdk/game/bl2/hooks.cpp).
The [installed-commit hook contract](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/hook_manager.h)
also distinguishes args from actual return proxy. Exact installed-commit
implementation pages were unavailable through browsing; reviewed master
implementation and installed stub agree on copy/return semantics. The design
avoids output-struct reads entirely and does not infer their final values.

## Loaded schemas required each run

Metadata comes from v0.2.3's live diagnostic log and v0.2.6's UpdateInfoBox log.
Startup scans <=30000 loaded Function objects, accepts only exact canonical
class/outer/path and rejects missing/duplicate/changed descriptors. No guessed
path is hooked. Each function has <=16 reflected fields; unknown additional
parameter/out/return flags refuse startup. Raw locals are logged, never read.

| Function | NumParams / ParamsSize / ReturnValueOffset | Required inputs/return |
|--|--|--|
| PlayerSkillTree:GetSkillState | 3 / 28 / 24 | SkillDef ObjectProperty flags128 offset0 (SkillDefinition); OutSkillState StructProperty flags384 offset4 (SkillTreeSkillStateData); ReturnValue BoolProperty flags1408 offset24 |
| SkillTreeGFxObject:GetSkillDescriptionForGrade | 6 / 32 / 20 | SkillDef ObjectProperty flags128 offset0; Grade IntProperty flags128 offset4; GradeModifier IntProperty flags128 offset8; PlayerOwner ObjectProperty flags128 offset12 (WillowPlayerController); bIncludeHTML BoolProperty flags128 offset16; ReturnValue StrProperty flags4195712 offset20 |
| SkillTreeGFxObject:UpdateInfoBox | 0 / 0 / 65535 | No parameters/return; reflected strings/SkillState are locals |

Required array dimensions are one; SkillDef PropertyClass must be SkillDefinition.
OutSkillState's descriptor must have exact ScriptStruct class/name. Reflect at
most 12 raw struct property descriptors (class/flags/offset/dimension) for future
design; no struct instance reads or evaluation. No constraints are followed.

## Passive reads and guard order

Three POST observers, returning None. Actual ret can reflect another hook's
override; the observation is not an exclusive native-semantic claim.

- Every callback first counts toward attempt/time limits, then runs unchanged
  _upgrade_state: same current Gaige/controller/pawn/world/PRI/tree, both
  sole-player rosters, exact owned inert patch, unique runtime registrations/
  indices/tier and known unchanged PRI points/ranks. Node grade stays zero.
- GetSkillState requires obj==the guarded current tree before any args reads,
  args._type==the verified function, and SkillDef identity among the three
  targets. Actual ret must be exact bool. Record QUERY_RETURN only. Never
  read OutSkillState, args.ReturnValue or reinterpret a tuple. A Boolean
  means the observed query returned that value, not an eligibility result.
- Descriptions require exact SkillTreeGFxObject/WPCOwner==pc before args/text;
  reuse validated separate current/rollover runtime identities. Matching
  args._type, target SkillDef and PlayerOwner==pc are required. Grade is exact
  int 0..128, modifier exact int -128..128, bIncludeHTML exact bool, actual
  ret exact str. Requested definition must appear in verified current/rollover.
  Record inputs, original text length, first 512 characters and separate UI
  view. Preserve empty strings. Returned preview is not the rendered prompt.
- UpdateInfoBox reads only guarded target current/rollover/UI points/tier;
  choose a target rollover identity, otherwise target current identity, while
  retaining both values. UI_VIEW describes that UI observation only. Never
  inspect args, ret, NextGradeText or other locals. Foreign/other selection
  consumes no capture slot. No substitution for query identity.

No invocation, writes, overrides/blocks, args/ret edits, package loads, point/
grade/save/effect/constraint changes. Unknown relevant representations abort
and clean up. Foreign owners/targets skip before reading their payloads.

## Budget and cleanup

Four captures per function/skill, two copies per distinct result. Nine buckets
reserve coverage: <=36 results within the unchanged 48-event cap. Other skill
activity and duplicate/quota skips consume no events but count against 2048
attempts and 90 seconds checked on the next callback. No background timer;
always STOP. Retain only bounded scalar records, not argument/output wrappers.

STOP clears context first, verifies FINAL PRI points/ranks, removes only owned
hooks, and reports all nine buckets as OBSERVED/NOT OBSERVED. Failed removals
retain inert hooks for retry; prevent other traces. CANCEL invokes new cleanup
before existing cleanup/rollback; disable reaches it through unchanged shutdown.
Old UI/upgrade/loading STARTs refuse overlap in reverse too. Partial registration
cleans up own hooks; preexisting foreign identifiers are preserved.

58 existing v0.2.6 functions are AST-identical. Existing changes are:
cancel_init_node (focused cleanup), start_tree_trace (mutual exclusion),
start_ui_trace/start_upgrade_trace (mutual exclusion/version labels) and
inspect_overclock_purchase (version label only). Five new focused functions.
Factory metadata/version changes and adds buttons 9/10, total 19 options.
Import remains inert. Constructor/insertion/rollback, solo/current-state guards,
old callbacks, old candidate selection and verified manual duration stay intact.

## Local checks / game procedure

90 unique local mocks passed. New cases cover actual bool/string returns and
poison copied-out/ReturnValue/local reads; no writes/native invocation; all
three identities; foreign ownership; absent/invalid metadata and reflection
bounds; wrong input wrapper and scalar types; text clipping/empty values;
capture quotas and replay of the v0.2.6 nested navigation; unchanged-state
aborts; mutual exclusion both ways; partial/failed hook removal and retry;
zero calls, duplicate/attempt/time/event bounds, reentrancy/errors and cancel/
disable rollback. This does not establish engine behavior or rendered UI.

Before shipping: syntax compile, exact one-folder/three-file ZIP source/integrity
checks and isolated 19-option import without game access/scaffolding. Preserve
all six tested ZIPs and v0.2.6 log unchanged; create a new v0.2.7 versioned ZIP.

Use docs/NEXT_CODEX_TASK.md: close BL2, replace only this mod, verify exact
v0.2.7 title, 1 ARM at main menu before Continue as backed-up Gaige Offline,
9 START in map, highlight all three without clicking/buying, 10 STOP,
3 CANCEL, fully exit. Use only 1,9,10,3. Preserve/hash final log before relaunch;
verify metadata, target records, final points/ranks, zero observers and native
RESTORE result=True. Clarify final steps if cleanup evidence is missing.

Any empty/partial result is evidence, never a reason to buy or invoke a query.
Purchase/refund/save persistence, automatic node effect, constraints, co-op and
release remain later milestones requiring scope/recovery. Native arrays cannot
refund a point or undo a saved grade. Manual +15 seconds remains independent.

## Completed artifact checks

Final local verification: 90 tests passed, runtime syntax compilation passed,
and the default package passed isolated import with 19 options and no game
access. ZIP integrity, exactly one mod folder containing the three required
files, and byte equality to current source all passed.

Created `dist/UltimateVaultHunterDeathtrapBoost_v0.2.7_folder_install.zip`
exclusively, without overwriting any versioned artifact. It is 28,884 bytes,
matches the checked default ZIP, and passed its own layout/integrity/source
and syntax checks. SHA-256:
`70687df8825949c07c550dda64e4ad101c4947a374c0dc6ceb9d69870192de87`.

Current runtime SHA-256:
`e8942b68dacbfe7fc841ff001ec1357eee7fea18a527c973fa4ea73ca829165e`.
All six tested v0.2.1–v0.2.6 ZIP hashes and the preserved v0.2.6 log hash
were checked unchanged. No files were installed into the game and no live
v0.2.7 behavior was established at this build-time checkpoint. User installation
and the 1,9,10,3 test were pending; their later result is recorded below.

## Later live result

The planned run is complete; see v027_live_focused_state_result.md. All nine
buckets were captured, 16 results/110 callbacks. Overclock returned an empty
Grade1/modifier0/HTML=False description; both native skills returned bonus text.
Sampled final points/ranks stayed unchanged, all hooks were removed and native
restoration passed. The game log is preserved with SHA-256
3024e4692fa28f0ea17ec39b3f6131ce5db1329991c4285aae5169b837195452.
No runtime changes during review. All seven tested versioned ZIPs were recovered
after the user confirmed deleting them, with original hashes verified. No
versioned ZIP was rebuilt; a tested-source snapshot is also archived. The next
task is bounded native presentation-data investigation, not an identical rerun.
