# v0.2.3: live enum/constraint diagnostics and restoration

The user completed the test and reported the hovered skill's title
**"Deathtrap Overclock"** in blue, followed by:

> Prototype:Extends Deathtrap duration by 15 seconds. (Not active in this node test.)

This matches the deliberately inactive prototype description (the source has a
space after the colon). The user previously reported rank 0/1 and clarified
that their orange-text observation concerned rank-upgrade text. This does not
establish the semantics of that UI text, purchase eligibility or an attempted
purchase. Separate More Pep/Myelin tooltip details have not been reported.

The complete game log is `v023_upgrade_metadata_and_restored.log`.
Unlike the previous intended test, this run really loaded v0.2.3: both the
snapshot headers and installed pyproject identify it, and the installed source
matches the workspace's v0.2.3 runtime hash.

On October 9, 2026 at 21:57–22:00 America/Los_Angeles
(October 10 04:57–05:00 UTC):

- Two button-4 attempts before loading Gaige refused inspection because no
  recorded active node existed. No metadata discovery occurred in those attempts.
- Insertion/native registration again produced one inert Overclock entry and
  both originals, with the one-player session checks passing. Observers were
  removed after initialization.
- Four snapshots completed, beginning at 04:57:50.324Z, 04:57:50.619Z,
  05:00:37.838Z and 05:00:38.455Z. Each reported PRI points 1 general / 0 specialist,
  Overclock grade 0 / maximum 1 / starting grade 0, index 14 / tier 7,
  unlocked True / requirement 0. Both original skills remained at grade 0.
- All three definitions have `ESkillType.SKILL_TYPE_Passive (value=0)`,
  `SkillClass=Skill`, grade rules enabled and `LockedSkillDetailStr='<Locked>'`.
  This rules out a differing observed SkillType as the explanation of this
  tooltip observation; it does not prove purchasing works.
- Overclock has zero constraints, effects and activation/deactivation actions.
  MorePep and Myelin each have one verified SkillConstraintData struct. Its
  activation/active/paused application flags are True, OnFailure is
  `ESkillState.SKILL_Paused (value=2)`, Evaluator is None, and EvaluatorDefinitions
  has one entry. The diagnostic did not traverse that array or evaluate/copy
  any constraint; its actual condition and purchase relevance remain unknown.
- Each metadata scan inspected 20120 objects, discovered 53 function paths,
  logged 32 paths and detailed 12 functions. The new upgrade-UI priorities and
  enum/constraint formatting worked without reported reflection errors.
- Cancellation at 05:00:39.267Z verified original skills MorePep/Myelin and cells
  True/False/True restored. The second cancellation found no remaining patch;
  all observers stayed zero. No ERROR or Traceback appears in the log.
- BL2 was not running when Codex checked after preserving the log.

## Useful metadata, not observed gameplay calls

`SkillTreeGFxObject:CanUpgradeSkill` has one parameter descriptor, a return byte
with enum **ESkillTreeFailureReason**, ParamsSize 1 / return offset 0. Its `retVal`
and `SkillState` descriptors have flags 0 and are locals. Do not assume a Boolean
return or a SkillDefinition argument. No return value was actually captured.

`Flash_SetSkillPointProperties` has zero parameters; its `_AS` variant has one
four-byte parameter. Other detailed functions include GetSkillUpgradeCost,
GetSkillState, GetSkillGradeByDef and GetSkillDescriptionForGrade. Discovery and
reflection do not invoke any of them or verify callable semantics.

The four sampled point/rank values stayed unchanged. The log does not prove
save-file equality, purchase cost/eligibility, refunds, persistence or the
node's +15-second effect. No saves were parsed, edited or restored by Codex.
The established manual +15-second feature remains separate and unchanged.

## Preserved baselines

All three tested versioned ZIPs are unchanged. Runtime code did not change
during this review; documentation-only updates may rebuild the default ZIP.
After the README status update, syntax compilation, isolated package import and
three-file ZIP/source verification passed again. Runtime, preserved log and all
three tested versioned-ZIP hashes were verified unchanged.

| Artifact | SHA256 |
|--|--|
| v0.2.3 tested ZIP | `4573834f5bfad6f8eb4bc8c34051c3edfa4e893ba22e358ce5761431d1e17de6` |
| v0.2.3 runtime | `1d2a62974b115b606a40d760da12996f7226c1e0a385282ef296248f06d6aef6` |
| Preserved v0.2.3 log | `d0dc15edca2e0b9d737bcbabfa87104c1f4fa792bb01829ec5a9390b07f82e77` |

The live read-only diagnostic milestone is complete. Do not repeat this snapshot
test merely to recover tooltip details. The next purchase work must establish
actual eligibility and a point/grade/save recovery plan before an explicitly
authorized purchase. A bounded, manually started observer of the UI's natural
CanUpgradeSkill/cost calls is a possible read-only next step; it must not invoke
or override them. Native-array cancellation cannot undo a purchased rank.
