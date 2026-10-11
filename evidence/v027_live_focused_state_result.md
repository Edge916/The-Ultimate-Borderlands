# v0.2.7: every target captured; Overclock's grade-description return is empty

The user reported "done" after the 1,9,10,3 test instructions. The complete
log was preserved as `v027_user_test.log` before relaunch: 31,364 bytes,
SHA-256 `3024e4692fa28f0ea17ec39b3f6131ce5db1329991c4285aae5169b837195452`.
Installed runtime, pyproject and README matched source and the tested v0.2.7
ZIP byte for byte before documentation edits. No runtime code changed in this
review. No Borderlands2 process was found at review; the user's reply also
follows explicit full-exit instructions.

## Observed October 10, 2026, 00:58–01:00 Pacific

UTC timestamps below are October 10:

- 07:58:43.938: ARM accepted. Repeat ARM at .48.646 refused.
- 07:58:57.325–.330: PRE verified listen_host, exactly one owned local player
  and one owned roster player. One inert node plus both original first-tier
  skills entered the engine's 39-skill runtime tree. Overclock grade=0,
  index=14, parent tier=7. Initialization observers removed, remaining=0.
  The early initialization read has tier bUnlocked=False; later UI reads have
  True. They are different observations at different stages, not eligibility.
- 07:59:24.128–.152: startup accepted all three exact loaded schemas:
  GetSkillState (3,28,24), GetSkillDescriptionForGrade (6,32,20), and
  UpdateInfoBox (0,0,65535). Native state metadata has five descriptors:
  SkillDefinition, ParentBranchDefinition, TierNumber, SkillGrade,
  bIsUnlocked, at offsets 0/4/8/12/16. These are metadata only; no finished
  OutSkillState or UpdateInfoBox locals were read.
- 07:59:24.174: START v0.2.7 registered three POST observers, baseline PRI
  points=(1,0), ranks=(0,0,0) in Overclock/MorePep/Myelin order. Repeat START
  at .24.854 refused without replacing the running trace.
- 07:59:32.211–.48.521: 16 results cover every one of the nine target/function
  buckets. All six captured GetSkillState returns were actual Boolean True.
  The query return is not CanUpgradeSkill or proof of purchase eligibility.

| Skill | Query results | Grade-description results | Info-view results | Observed grade-description return |
|--|--:|--:|--:|--|
| Overclock | 2 | 2 | 2 | Empty string, length 0 |
| More Pep | 2 | 2 | 2 | Length 79: electrocute +4%, ignite/corrode/slag +2% each |
| Myelin | 2 | 1 | 1 | Length 49: shock resistance +6%, shield capacity +3% |

Every captured description request had Grade=1, GradeModifier=0 and
bIncludeHTML=False. These are preview query inputs, not purchased ranks.
Overclock's two empty returns were at 07:59:36.471 and .41.391. Both retained
verified current/rollover=Overclock, UI points=1 and tier unlocked=True.
MorePep's first description/info view at .41.423/.425 had current=Overclock,
rollover=MorePep; later records at .43.648/.650 had both=MorePep. Myelin's
records at .48.520/.521 had both=Myelin. Current and rollover remain separate.

- 07:59:58.859: explicit STOP verified FINAL points=(1,0), ranks=(0,0,0),
  unchanged_from_start=True, then remaining=0, captured=16, callbacks=110,
  skipped=94. All nine SUMMARY buckets are OBSERVED. The 94 skips are an
  aggregate; the log does not distinguish unrelated calls from quota/duplicate
  skips. No event/attempt/time limit or ABORT occurred. Active time was about
  34.685 seconds, below 90 seconds; 16 results are below the 48-event bound.
- 08:00:00.373: repeat STOP retained the same totals and zero observers. It
  did not resample FINAL after capture context had already been cleared.
- 08:00:02.875–.876: CANCEL removed/confirmed zero focused/UI/upgrade/init
  observers, verified RESTORE result=True, original MorePep/Myelin arrays and
  True/False/True cells, and logged NATIVE ARRAYS RESTORED. At .03.373 repeat
  cancellation found no initialization patch remaining.
- No ERROR or Traceback occurs in the game log. The SDK's existing unrelated
  legacy-import DeprecationWarning remains present. No saves were parsed,
  edited or restored by Codex; sampled unchanged points/ranks do not prove
  save-byte equality. Native rollback does not clear the engine-built cache.

## Conclusions and limits

The focused observer works in this solo run: loaded metadata, actual Boolean
and string return representations, all three target identities, separate
selection/rollover, complete bucket coverage, final state checks, hook removal
and native-array restoration are now verified in engine.

The useful new difference is the empty rank-one description returned for
Overclock while both native comparison skills returned nonempty bonus text
for identical grade/modifier/HTML inputs. This supports investigating the
node's rank-preview presentation data. It does not prove the precise cause
of the missing orange prompt or establish eligibility/cost/purchase failure.
The rendered UI text itself was not captured. POST ret can reflect another
hook's override; exclusive final native semantics were not independently
established. Old eligibility/cost observers were not started; their empty
cancellation summaries are not a measure of query activity in this run.

The candidate constructor sets the static SkillDescription, rank limits and
icon, but does not populate SkillEffectPresentations. Its actual default array
was not inspected here. The older v0.1.5 log shows MorePep has four
AttributePresentationDefinition references and one-rank ExplosiveClap has one.
This is a concrete next comparison, not proof that presentation data alone
controls the prompt. Do not copy/evaluate gameplay effects or constraints,
invoke native queries, override returned text or buy to force evidence.
Purchase/refund/save persistence, automatic node +15 seconds and co-op remain
later milestones; the separately tested manual duration prototype is intact.

## Artifact recovery and hashes

The dist directory was empty at review. The user confirmed deleting its ZIPs,
thinking it was a download folder. All seven tested v0.2.1–v0.2.7 versioned
ZIPs were recovered by copying their original Recycle Bin payloads back into
dist, after verifying every payload against its previously recorded SHA-256.
Existing differing destinations would be refused; no versioned ZIP was rebuilt
or overwritten. The current default v0.2.7 ZIP was also recovered by its hash.
Recycle Bin records and game files were left unchanged.

| Artifact | SHA-256 |
|--|--|
| v0.2.7 complete log | 3024e4692fa28f0ea17ec39b3f6131ce5db1329991c4285aae5169b837195452 |
| Tested runtime | e8942b68dacbfe7fc841ff001ec1357eee7fea18a527c973fa4ea73ca829165e |
| Tested pyproject | fb0db55605a07a1e14e7abb89a3e91df558931a7bf69897f5c9b83492babff67 |
| Tested README | 9a0476c7c3c4ca3293554bffbe5c7175e04421d16d0ab2d5c8945e733a2e5037 |
| Tested v0.2.7 ZIP | 70687df8825949c07c550dda64e4ad101c4947a374c0dc6ceb9d69870192de87 |

An exclusive three-file tested-source snapshot is also preserved under
archive/tested_runtime/v0.2.7. Its files match the installed/tested ZIP.
The v0.2.5 and v0.2.6 log hashes were checked unchanged. Documentation-only
updates may rebuild the default ZIP; all seven tested versioned ZIPs must
remain unchanged. Existing 90 mocks remain applicable without runtime changes.
Syntax compilation and isolated 19-option package import, ZIP integrity,
exact three-file layout and source equality passed again for the updated
default ZIP. It is 28,652 bytes, SHA-256
`4f02efcc07d5453bbe8ca89fc9ad5dd42e95850ef61e7cc4795b763a9064ea0c`.
Final hash checks confirmed all seven recovered tested ZIPs, runtime,
tested-source snapshot and preserved v0.2.7 log unchanged. No new runtime or
game test was built during this review.
