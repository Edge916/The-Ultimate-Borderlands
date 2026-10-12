# v0.2.1: first confirmed native node visibility

The user completed the requested visibility test and reported: **"done it worked!"**
This is the visual confirmation; Codex did not independently inspect the game screen.
The real game log is preserved in `v021_native_node_visible_and_restored.log`.

On October 9, 2026 at 18:12:56 America/Los_Angeles (October 10 01:12:56 UTC):

- PRE verified `NetMode=2`, SDK role `listen_host`, one local player and one roster
  player, both matching the current controller/PRI.
- A separate `SkillDefinition` named `UVH_DeathtrapOverclock` was constructed in
  `GD_Tulip_Mechromancer_Skills.LittleBigTrouble`, max rank 1, effects empty.
- PRE insertion succeeded before the native player-tree initializer.
- POST and two later CHECK calls verified one candidate plus both original
  first-tier skills, with 39 total runtime skills.
- The candidate's runtime index was 14, parent tier 7, grade 0. Little Big Trouble's
  first tier contained indices `[13,14,15]`. Its `bUnlocked` changed from False
  immediately after initialization to True at the later checks.
- All insertion observers were removed. At 01:13:42.159Z, cancellation verified
  original skills `[MorePep,Myelin]` and layout `[True,False,True]` were restored.
  A second cancellation found no remaining patch; observers remained zero.

Visibility, runtime registration and native-array restoration passed in this run.
The log does not independently prove restart/cache clearing or unchanged saves.
There is no evidence of a purchase or +15-second effect from the new node; its
logged grade stayed 0. The established manual duration button remains separate.
This is one successful solo test, not broad regression coverage or co-op support.
The earlier invisible node's exact cause is still not proven; pre-initialization
insertion is now a demonstrated working approach.

The versioned ZIP is preserved unchanged as the tested baseline:
`dist/UltimateVaultHunterDeathtrapBoost_v0.2.1_folder_install.zip`.
At confirmation, its runtime source matched the installed mod and workspace byte for byte.
Subsequent README status updates change documentation only; the default rebuilt
ZIP included those updates. The later v0.2.2 diagnostic build adds read-only
inspection while preserving all pre-existing v0.2.1 functions. The versioned
v0.2.1 ZIP and the preserved game log remain unchanged.

SHA256:

| Artifact | SHA256 |
|--|--|
| Tested versioned ZIP | `e04c6f4ab6ab5f472fe984996b0dcd375c671fd944aa0891663f2ab601b2f455` |
| Runtime `__init__.py` | `17116510f2bf6ef64d9e4c56cf7f61d1334fded834d17b224611c598ca4fea4a` |
| Preserved game log | `bb42d31110462749ad21f90885a911d9f92cb22a50a1cff74660b91eb68544ca` |
