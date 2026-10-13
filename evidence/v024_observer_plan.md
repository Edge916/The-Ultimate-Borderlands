# v0.2.4: opt-in natural upgrade-call observers

The user's "next step" continues development after the completed v0.2.3
metadata diagnostic. This build obtains new evidence: actual normal UI query
results, without asking the user to spend points. It is not a purchase fix.
The initial live setup/cleanup result is now preserved, with zero callbacks;
see v024_live_observer_result.md. Actual query results remain unverified. The node remains inert and manual +15
seconds remains independent. All tested v0.2.1/v0.2.2/v0.2.3 ZIPs are preserved.

## Evidence used to select the observation

The preserved v0.2.3 log directly contains both loaded UFunction descriptors:

| Function | NumParams / ParamsSize / ReturnOffset | Parameter descriptors |
|--|--|--|
| SkillTreeGFxObject:CanUpgradeSkill | 1 / 1 / 0 | ReturnValue ByteProperty, flags 1408, offset 0, enum ESkillTreeFailureReason |
| WillowPlayerController:GetSkillUpgradeCost | 2 / 8 / 4 | Skill ObjectProperty flags 128 offset 0, class SkillDefinition; ReturnValue IntProperty flags 1408 offset 4 |

CanUpgradeSkill's other reflected fields have flags zero and are locals;
there is no skill-definition input descriptor. The eligibility observer reads
the UI's CurrentSkill and reports CurrentSkill_Rollover separately.
The [UnspecSkills author's source](https://github.com/ZetaDaemon/bl-sdk-mods/blob/main/UnspecSkills/__init__.py)
uses CurrentSkill, CurrentSkill_Rollover and WPCOwner in SkillTreeGFxObject
callbacks. That supports field names but does not verify this new observer's
live ownership/selection timing. No mutating code from that mod is used.

The installed pyunrealsdk v1.10.0 hooks stub documents POST as called after a
function is allowed to execute, with (obj,args,ret,func). Actual ret is used;
args.ReturnValue may differ. The observers return None and never invoke func.
SDK stubs are read as data only. Previous init traces establish hook support,
not these new query timings/results. No UFunction is invoked to check metadata.

## Implementation and bounds

New buttons 5/6 start/stop only the two POST hooks above. Import is inert.
Startup scans <=30000 loaded functions and <=16 fields each, requiring the
observed descriptors and known SDK enum type. Both registrations must succeed.
No PRE hooks, block/return/argument overrides or package loads.

Quiet bounded state reads verify exact current controller/Gaige/pawn/world/PRI,
recorded/current owned tree, sole local and roster players, SDK-named allowed
NetMode, exact native candidate/original arrays and empty gameplay effect/actions.
All three runtime entries must be unique and owned, with valid index/first tier.
Known nonnegative PRI general/specialist points and grades/indices are captured
at start and must remain unchanged. Candidate grade must be zero. STOP checks
final state too. Changed state is reported, never repaired/refunded.

UI callbacks require exact class SkillTreeGFxObject, WPCOwner==pc and CurrentSkill
among the three definitions. Cost callbacks require obj==pc and args.Skill among
them. Unknown ownership/selection refuses capture; bounded IGNORED logs assist
diagnosis. Eligibility ret must be a named member of the SDK's
ESkillTreeFailureReason type, including value-zero members; it is not Boolean.
Cost ret must be an exact nonnegative int. Unknown result types abort observation.

At most 24 captures, 2048 attempts including foreign calls, two copies of each
path/definition/result. Ninety seconds checked on the next call; no background
timer. Always manually STOP. Stop/cancel/disable/errors/session changes/limits
clear context before hook removal. Failed removals retain inert hooks for retry;
restart is refused while any remain. Summary [] means NOT OBSERVED.

Of 48 v0.2.1 functions, 47 remain AST-identical. Only cancel_init_node adds
stop_upgrade_trace before existing cleanup/rollback. The v0.2.3 snapshot changes
only its version header. Constructor, initialization, guards, rollback and
manual inspect/apply/restore remain unchanged. No save/point/grade/duration writes
are introduced by the observers. Existing explicitly armed insertion is still
mutating and still requires a backed-up solo Gaige, cancel and a fresh process.

## Local verification, not engine proof

57 unique mock tests passed (41 established, 16 new). They cover actual POST
ret versus mismatching args.ReturnValue; zero enum; selected versus rollover;
native comparisons; ownership/unknown types; exact metadata and bounds;
missing enum/points/rank/tree/concurrent trace; state/peer/point/rank/index/effect
changes; reentrancy/errors; capture/time/callback bounds; partial registration;
foreign hook ownership; removal failure/inert retry; cancel/disable cleanup;
final-point change without another UI call; import and preserved manual boost.
Observers never invoke the supplied native function, discovery or mutation APIs
in callbacks, and preserve the mocked game fields. Tests cannot establish engine
wrapper behavior, UI timing, query results, purchase or save-file equality.

Syntax compilation, exact-three-file ZIP/source/integrity inspection and isolated
packaged-runtime import pass. AST comparison verifies the exceptions above;
baseline ZIP hashes remain unchanged. New build hashes are recorded below after
packaging. Test steps/expected log tags are in docs/NEXT_CODEX_TASK.md.

## Review and later milestones

On "done", preserve/hash the log before another launch. Verify installed version,
START/RESULT/FINAL/STOP remaining=0 and native-array RESTORE result=True.
If there are no eligible calls, record that without claiming failure. Actual
returns describe UI checks at that moment; they do not prove successful point
spending/refunds, rank persistence or the +15-second node effect.
Only later, explicitly authorized purchase work may proceed after a concrete
point/grade/save recovery plan. Native-array rollback alone cannot undo a purchase.

## Build hashes

| Artifact | SHA256 |
|--|--|
| v0.2.4 install ZIP | `d1aa246adcca296cefb359d1ffc5c1a22fd46685eeaf77accca4468a6f85ca42` |
| v0.2.4 runtime | `dd51d0ac5f4b2bd0bad95067f681dde22675f9d219950230808c75f540f2c7ed` |
