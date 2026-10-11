# v0.2.2: live read-only diagnostics and restoration

The user completed the requested diagnostic run and reported **"done"**.
The complete game log is preserved in `v022_purchase_rank_metadata_and_restored.log`.
This is engine evidence for button 4; it is not a purchase test. In a follow-up,
the user reported the tooltip showed **"0/1, with no upgrade prompt"**.
This confirms the displayed rank; it leaves upgrade behavior unresolved.
No native-skill tooltip comparison or purchase attempt was reported.

On October 9, 2026 at 21:12–21:13 America/Los_Angeles
(October 10 04:12–04:13 UTC):

- Two button-4 attempts at main menu refused inspection because there was no
  active recorded Gaige node. Neither attempt reached metadata discovery.
- At 04:12:12.105Z, PRE verified one owned local player and one owned PRI roster
  player in `listen_host` mode. Insertion and native initialization again produced
  one Overclock entry and both original first-tier skills among 39 runtime skills.
  Insertion observers were removed at 04:12:12.109Z.
- Four completed snapshots began at 04:12:27.379Z, 04:12:28.124Z,
  04:13:13.096Z and 04:13:13.732Z. Every snapshot passed the recorded/current
  tree, solo session, native patch, runtime entry and first-tier checks.
- Every snapshot reported `PRI.GeneralSkillPoints=1`,
  `PRI.SpecialistSkillPoints=0`, and Overclock rank 0 / max rank 1 / starting rank 0.
  The controller's equivalent point fields were unavailable (`<none>`);
  the diagnostic reported this rather than inventing values.
- The node remained index 14 / tier 7, with `unlocked=True` and
  `unlock_points=0`. Both MorePep and Myelin had one runtime entry at rank 0.
- Overclock's `SkillClass=Skill`, with grade rules enabled, matched the two
  original definitions. Its constraints, effects and activation/deactivation
  actions were empty. The originals each had one constraint; that difference
  alone does not establish a defect or purchase eligibility.
- `SkillType` printed as `<ESkillType len=0>` for all three definitions. This
  formatting does not expose the enum value; do not infer their types are equal.
- Each metadata scan inspected 20120 objects, discovered 53 function paths,
  logged 32 paths and detailed 12 functions. Reflection produced field
  descriptors without invoking the discovered functions.
- At 04:13:14.619Z, cancellation reported `RESTORE result=True` with
  skills `['MorePep', 'Myelin']` and cells `[True, False, True]`.
  A second cancellation had no remaining patch; observers remained zero.
  The preserved log contains no ERROR or Traceback entry.

The four snapshots show unchanged sampled points and ranks. Their timestamps
do not establish exactly when the user hovered the tooltip. The log cannot prove
save-file equality, a point refund, purchase eligibility/cost or persistence.
The mod's button-4 source performs reads and reflection only, with no native
purchase/grade/reset/save calls. No saves were parsed, edited or restored by Codex.
BL2 was not running when Codex checked processes after preserving the log.
Use a fresh game process before normal play; native-array restoration alone does
not rewrite the cached prototype tree.

## Metadata interpretation

Observed descriptors include `PlayerSkillTree:UpgradeSkill` (SkillDefinition
argument and Boolean return), `SetSkillGrade` (SkillDefinition, integer grade and
Boolean return), `WillowPlayerController:GetSkillUpgradeCost` (SkillDefinition and
integer return), and `PlayerSkillTree:GetSkillState` (SkillDefinition, out
SkillTreeSkillStateData struct and Boolean return). These are raw descriptors,
not verified callable signatures or permission to invoke these functions.

`_properties()` also returns local fields: `GetSkillGradeByDef.SkillState` has
flags 0 / offset 8 while ParamsSize is 8; `ApplySkillSaveGameData.SPD` has flags 0.
Do not treat every enumerated property as a function argument. Save/reset/grade
functions were inspected as metadata only and must remain uncalled in this scope.

## Preserved artifacts

The installed runtime and pyproject matched the workspace byte for byte at review.
Keep both versioned ZIPs unchanged. Documentation updates may rebuild only the
default ZIP, with the same runtime source and version.
After the status updates, syntax compilation, isolated package import and exact
three-file ZIP/source verification passed again. Runtime and both versioned-ZIP
hashes remained unchanged; only the default ZIP's README was updated.

| Artifact | SHA256 |
|--|--|
| v0.2.2 tested versioned ZIP | `a07442dfa33cfc1f2265f1618edd8cefe7f987a789f6cbf3f042d7075255a2cb` |
| v0.2.2 runtime `__init__.py` | `6b5e54e9e160453e24d2dd6c609b29f75e3252b4cf162afb44b2877ce4b2bb02` |
| v0.2.2 preserved game log | `78cfa63fd67c1f989e48c00d2da947a0fd75cbe6581970d436d7c1a8137b487a` |
| v0.2.1 tested versioned ZIP | `e04c6f4ab6ab5f472fe984996b0dcd375c671fd944aa0891663f2ab601b2f455` |

Next: investigate the absent upgrade prompt using a read-only comparison with
More Pep and Myelin. Current v0.2.3 improves enum formatting, reads bounded
constraint fields and prioritizes upgrade-UI metadata; it has no game result yet.
A later purchase experiment requires explicit scope and a point/grade/save
recovery plan; native-array restoration cannot undo a purchased rank.
The node remains inert, and manual +15 seconds remains separate.
