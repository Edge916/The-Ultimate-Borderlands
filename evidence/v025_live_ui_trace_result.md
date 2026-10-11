# v0.2.5: owned UI selected Overclock and both originals; restoration passed

The user reported "done" after the requested v0.2.5 test. The preserved complete
log is v025_user_test.log (30099 bytes). Installed pyproject is v0.2.5 and the
installed runtime matches workspace/versioned-ZIP source byte for byte.
No runtime code changes during this review. Keep the v0.2.5 versioned ZIP
unchanged alongside all four earlier tested ZIPs.

## Observed on October 9, 2026, 23:16–23:17 Pacific

UTC timestamps below are October 10:

- 06:16:15.792: ARM accepted before Gaige loaded. Initialization again verified
  the solo session, inserted one inert candidate before native initialization,
  registered exactly one node plus both originals among 39 runtime skills,
  and removed initialization observers (remaining=0).
- 06:16:30.502: function discovery scanned 20120 objects, found 24 canonical
  SkillTreeGFxObject candidates and selected 10. Metadata reflection succeeded.
  START inventory scanned one UI object but found zero owned views; no live
  selection snapshot was printed. This does not prove no live UI existed.
- 06:16:30.510: START registered 20 PRE/POST_ANY observers with baseline
  points=(1,0), ranks=(0,0,0) in node/MorePep/Myelin order. Repeat start refused
  an active trace. The observed window lasted about 56.7 seconds, within limits.
- 06:16:36.868–.870: Init PRE had unavailable current/rollover; POST_ANY selected
  Skill_DeathTrap. Both phases verified exact UI class/WPCOwner and current
  Gaige/tree/session/point/rank guards. UI points=1 and target tier unlocked=True.
- extInitTree recorded four events, retaining Skill_DeathTrap selection.
- Navigation then selected the node and both originals, with matching hovered
  definitions, verified owned runtime registration/index, UI points=1 and
  target tier unlocked=True in every captured navigation event:

| UTC POST_ANY event | Function | Before -> after current/rollover |
|--|--|--|
| 06:16:38.805 | Nav_Down | Skill_DeathTrap -> UVH_DeathtrapOverclock |
| 06:16:40.143 | Nav_Left | UVH_DeathtrapOverclock -> MorePep |
| 06:16:44.691 | Nav_Right | MorePep -> UVH_DeathtrapOverclock |
| 06:16:50.919 | Nav_Right | UVH_DeathtrapOverclock -> Myelin |

- 06:17:27.201: FINAL points=(1,0), ranks=(0,0,0), unchanged_from_start=True.
  STOP inventory again scanned one UI object and printed zero owned views.
- 06:17:27.208: STOP remaining=0, captured=14, callbacks=16, skipped=2.
  Captured counts: Init 2, extInitTree 4, Nav_Down 2, Nav_Left 2, Nav_Right 4.
  No IGNORED owner/class entries appear; the two skips are duplicate suppression.
  There was no error or limit abort. Final UI/upgrade/init observer counts were zero.
- The same cancellation verified RESTORE result=True: native MorePep/Myelin
  skills and True/False/True occupancy restored, then NATIVE ARRAYS RESTORED.
  A repeat cancellation at 06:17:27.652 found no remaining patch and observers
  stayed zero. The log proves restoration; the user's "done" follows the
  instructions to exit. Process closure was not independently probed.
- No ERROR or Traceback appears. An unrelated SDK legacy-import deprecation
  warning remains present. No save files were read, edited or restored by Codex.

## What this establishes

The new observer callback path works in engine, and its guarded UI ownership/
selection reads accepted the real wrapper types. The owned native UI navigated
to Overclock and both originals with one available UI point and the target
tier unlocked. The custom definition participates in current and rollover
selection. Sampled PRI points and all three grades stayed unchanged; cleanup
and native-array rollback passed. This is useful evidence beyond visibility.

POST_ANY does not independently prove a native function executed if another
hook blocked it; the actual before/after selection fields are direct observations.
One UI point and an unlocked tier are not an eligibility result. Cost/purchase/
refund/save persistence and the node's +15-second effect remain unverified.
The start/stop inventories did not expose owned views outside Skills, so do
not infer that the live UI was missing from those counts. Save equality is not proven.

## Candidate-selection limitation and next useful change

The broad selection-name filter prioritized artifact-related functions before
the skill-navigation helpers, consuming four slots in the ten-function cap.
Selected paths were Init, extInitTree, ArtifactSelect, EquipSelectedArtifact,
Flash_UpdateArtifactSelection, Nav_Back, Nav_Down, Nav_DownArtifact, Nav_Left,
Nav_Right. No artifact function event was captured; these observers did not
invoke/equip anything. They nevertheless reduced relevant coverage.

Navigate, PostNav, HandleInputKey, UpdateInfoBox and both
Flash_SetSkillPointProperties variants were DISCOVERED but NOT HOOKED.
The log therefore says nothing about their call activity. Cost/eligibility
observers were not started in this run; their empty STOP summaries are not
an observation of those functions during this window.

Next useful work: explicitly prioritize these now-discovered core skill UI
paths, exclude artifact/equip functions and retain the proven navigation/Init
anchors inside a bounded observer set. Re-discover/verify loaded metadata each
run; never hook an undiscovered path or call a function to manufacture evidence.
Preserve ownership/solo/unchanged-point/rank guards, passive callbacks and cleanup.
Add a regression where unrelated artifact candidates would otherwise crowd out
PostNav/input/info/point-display coverage. No new runtime or test is ready yet.
Do not repeat unchanged v0.2.5 solely for selection confirmation or buy a point
to force a query. Any later purchase needs explicit scope and point/grade/save recovery.

## Preserved hashes

| Artifact | SHA256 |
|--|--|
| Preserved v0.2.5 log | `c476847b867b8919e97ca678d56032e09b7de4a717336969a1c389588d29ccef` |
| v0.2.5 runtime (installed/workspace) | `39effd4c589c8866beacadef9ea575c8886558dee8098aa0c77a0b8f5b8fc6cb` |
| Tested v0.2.5 ZIP | `6d592c187efe3c04ce9de7ba957a3a1b72489e02ce1cea7fb7cd797d4ae71ab3` |

71 existing mock tests remain applicable; runtime is unchanged. Documentation
updates rebuild the default ZIP only; syntax/isolated import/layout/source checks
are repeated and all five tested versioned ZIP hashes remain unchanged.
