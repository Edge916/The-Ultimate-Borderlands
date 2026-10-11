# v0.2.8 live run: visibility and restoration; inspection not run

Historical first-run record. The omitted inspection was subsequently completed
in a fresh process; see `v028_live_presentation_retry_result.md`. Keep this
first log/PNG and its recorded observations unchanged.

The user reported done and supplied a Skills screenshot. The installed
runtime, pyproject and README matched the original v0.2.8 ZIP byte for byte.
The complete log and original PNG were preserved before relaunch. No BL2
process was found at review. This run verifies the established insertion and
restoration in v0.2.8, but does not test the new presentation snapshot.

## Evidence

- `v028_user_test.log`: 20,009 bytes, SHA-256
  `2f3670fa1c50ced4864daf5fd8db9585b6ef5c6af36b7bded9fe8d16341d326d`.
- `v028_overclock_user_screenshot.png`: original 2,937,120-byte PNG, SHA-256
  `d1855e515d1135f449d1b0d3b7ae4e464a452cfa4809194995c3fa2d43992d15`.
- Installed runtime SHA-256:
  `4dae701cc263c3d4be1fb8b602f0f5d0987ad173b2cfd477bd784a7ddeb706a5`.
- Installed pyproject SHA-256:
  `0393dfc7317910731465da0a19aa62f5bb5b4bf777b5c8e8c4b6315de8cd12b1`.
- Installed/tested README SHA-256:
  `f33576f7ee07c57f0480a044a5d20db7154fdb516cdc123469f9846a98167811`.
- Original v0.2.8 ZIP: 30,016 bytes, SHA-256
  `93b2ae7f8cae8412d3af6637d1c6e0739cadf7b6b0cc07b3961c5758674940c2`.

Log timestamps below are UTC. SDK versions were unrealsdk3.2.0/b1852aa4 and
pyunrealsdk1.10.0/c72c5558.

| Time | Observed result |
|--|--|
| 08:43:43.009 | Initialization experiment armed. |
| 08:43:43.912 | Second ARM refused because already armed; no second insertion. |
| 08:43:50.330–.334 | Owned listen-host session, one local player/one owned roster player; inert node created and inserted before native initialization. |
| 08:43:50.333–.334 | One node among39 runtime skills, index14/tier7/grade0, both original skills present, tier indices13/14/15; initialization observers remaining0. |
| 08:45:29.855–.856 | Cancellation reported all owned observer families remaining0 and RESTORE result=True; original MorePep/Myelin and True/False/True cells restored. |
| 08:45:31.032 | Repeat cancellation found no patch to restore; observers still0. |

There are **zero `[UVH-PRESENT]` messages**: no BEGIN, BASELINE, SCHEMA,
ARRAY, REFERENCE, PROPERTY, SUMMARY, FINAL or END for the new snapshot.
The user explicitly answered **"I didn’t press 4"** when asked whether they
selected `4 - INSPECT OVERCLOCK PRESENTATIONS (READ ONLY)` in the mod options.
This is an omitted test step, not a schema rejection or evidence of a runtime
failure. The old observer STOP summaries with callbacks0 are cancellation
cleanup for traces that were not started; they are not failed trace tests.
No ERROR/Traceback appears; the existing legacy-import warning remains.

## Screenshot and limits

The screenshot confirms the visible native Little Big Trouble center node
with Deathtrap Overclock selected at0/1, one skill point available, the blue
title and inactive prototype description. The bottom of the screen displays
`[Enter] Spend Point`. The tooltip contains no orange bonus text.

That rendered input hint is distinct from orange grade-preview text. It does
not establish eligibility, cost, a successful purchase or the node effect.
The v0.2.7 observed empty grade-description return remains separate evidence;
no causal conclusion follows. This run has no presentation FINAL point/rank
comparison, so do not claim final sampled points/ranks were unchanged. The
initial grade0 and screenshot point1/grade0 are observations at those stages.
Native-array rollback cannot refund points, restore saved grades or clear
player caches. Full process exit was checked; restart before another test.

## Preservation and next action

All eight original v0.2.1–v0.2.8 ZIP hashes/integrity were checked unchanged.
The v0.2.7 log retains its recorded hash. An exact three-file tested v0.2.8
snapshot is preserved under `archive/tested_runtime/v0.2.8`; v0.2.7's snapshot
remains intact. Runtime and pyproject are frozen. No game/save/SDK files were
edited or saves parsed. Documentation changes may rebuild only the default ZIP.

Use the already verified installed v0.2.8 in a fresh process: Offline Gaige
alone, main menu select1 ARM then Continue, in map open the UVH mod options
and **select item4** once, then select3 CANCEL/RESTORE and fully exit.
The numbers label mod-option buttons; pressing keyboard4 in the map does not
select the inspector. No skill purchase, other traces, boost, respec or travel.
Preserve the next complete log under a **new evidence filename**, such as
`v028_presentation_retry.log`; never overwrite this first run or screenshot.
Review actual schema/count/reference/metadata coverage and FINAL state before
designing a next runtime. No v0.2.9 build is warranted by this omitted step.

After documentation updates, runtime syntax and the default ZIP's isolated
19-option import, integrity, exact three-file layout and source match passed.
Runtime/pyproject hashes, all eight original ZIP hashes, both tested-source
snapshots and preserved log/PNG hashes were checked unchanged. The default ZIP
alone was rebuilt with the updated README: 30,340 bytes, SHA-256
`5e26b909e0fce071b62fde7636d2a629ebe4d43282a00f30cb72409aa859c897`.
The established 108 mock results still apply to the unchanged runtime; this
review made no runtime change and did not rerun the mock suite.
