# Prepared v0.2.12 metadata test protocol

This is a reviewed-build test plan, not authorization to install or run it.
The owner must explicitly authorize this exact manual test before the capture
task begins. v0.2.12 is offline-verified only; v0.2.11 is the last game-tested
build. The [v0.2.11 result](../evidence/v031_live_attribute_class_result.md)
is complete and needs no repeat.

## Exact build

Use the original [versioned v0.2.12 ZIP](../dist/UltimateVaultHunterDeathtrapBoost_v0.2.12_folder_install.zip)
from accepted commit `e32cfb16914ee1fe6e55519f5526494100a1fd0e`
([PR #6](https://github.com/Edge916/The-Ultimate-Borderlands/pull/6)).
It is 36,736 bytes and must not be rebuilt or overwritten for this test.

| Input | SHA256 |
| --- | --- |
| Versioned ZIP | `4f49bad17d0e7d3e97b24f1dfdcb7f396eef2f8a8c6d93464054edf512aaefc6` |
| __init__.py | `41fd2dd9e22bcfa64fbddfc19b881f6950362656e047b212b00eb86f33a01f73` |
| pyproject.toml | `fa8acf733ef82a19371fc89b6d0cfb37e690ce2aca704ec1479cf01a9efae40e` |
| README.txt | `5e0b3441243818c4bf161c889f643ec09132ae1e6acbf2addb5162b8b8edec7f` |

Title: **UVH v0.2.12 - DEATHTRAP METADATA**. The ZIP has one
`UltimateVaultHunterDeathtrapBoost/` folder with exactly those three files.
Confirm all three installed bytes equal this ZIP, not merely its title.
Keep SDK/core mods and all original project archives. Installation, if
authorized, is performed manually by the owner while BL2 is fully closed;
Codex does not write game, SDK or save files.

## Owner steps after explicit test authorization

Use an already backed-up Gaige alone, Offline, in a fresh process. This plan
does not authorize creating, inspecting or restoring private backups.
Overclock must remain inert and rank zero. If it is already purchased, do not
respec or repair points/ranks to make the test pass; stop and report that state.

1. With BL2 fully closed, manually install the exact project folder and have
   its three-file equality recorded. Start BL2 and check the exact MODS title
   above at the main menu. A wrong title/build means stop before ARM.
2. Select **1 - ARM ONE GAIGE INIT NODE TEST (SOLO / INERT)** once at the
   main menu, then Continue into the existing solo Gaige session. ARM uses the
   established temporary native-array insertion; item4 itself only reads
   metadata. Do not repeat ARM or enable another trace.
3. In the map, open this mod's options and select
   **4 - INSPECT DEATHTRAP METADATA (READ ONLY)** exactly once. No hovering,
   buying, respec, travel, summon, manual boost or other observer is needed.
   A refusal or partial result is useful evidence; do not force another call.
4. Select **3 - CANCEL / RESTORE NATIVE ARRAYS (THEN RESTART)**. Record any
   restoration or hook-removal failure without hiding it behind a retry.
   A refusal before insertion can legitimately leave no patch to restore.
5. Fully exit BL2. Do not relaunch until the complete log and installed
   snapshot have been preserved. Confirm explicitly that CANCEL was selected
   and the game fully exited; also record whether a failure was shown.

Numbers are mod-option labels, not keyboard hotkeys. A short "done" without
that context does not establish installation, restoration or exit.

## Expected records and honest outcomes

Read the [actual implementation plan](../evidence/deathtrap_metadata_diagnostic_plan.md)
and [offline checks](../evidence/deathtrap_metadata_diagnostic_checks.json).
The current source emits one BEGIN and buffered JSON METADATA rows per call.
Its comparison baseline is internal: it does **not** emit a BASELINE line.
FINAL reports sampled points/ranks and the runtime's unchanged-from-start
check. Do not reconstruct an unseen baseline from FINAL or from the old v11 log.

```text
[UVH-DEATHTRAP] BEGIN v0.2.12 metadata_only=True
[UVH-DEATHTRAP] METADATA {...}
[UVH-DEATHTRAP] FINAL points=(...) ranks=(...) unchanged_from_start=True
[UVH-DEATHTRAP] END coverage=... observers_added=0 native_calls=0 writes=0 signature=NOT_ESTABLISHED
```

| Actual outcome | Meaning and next action |
| --- | --- |
| END coverage=COMPLETE | Selected metadata coverage and final guard passed. Preserve evidence; no callable signature, natural timing or effect is established. |
| END coverage=CAPPED | At least one ancestry/property bound stopped collection. Preserve the observed prefix; it is not a full signature. |
| END coverage=UNAVAILABLE | Some selected lookup/metadata was unavailable. Preserve other records; unavailable does not mean zero or absence. |
| UNAVAILABLE without FINAL/END | Collection ended early. Preserve as incomplete, not a completed unchanged-state comparison. |
| ABORT coverage=REFUSED | State/schema/reference was invalid, unavailable or changed. Stop; no repair, guard relaxation or successful comparison is implied. |
| Missing/truncated/conflicting records | Preserve the entire log and report the gap. Do not splice successful records from another call or version. |

Bounds are four target class roots, seven allowlisted fields, three function
descriptors, 16 properties plus one unreported cap read per function and eight
ancestry nodes per target. There is no global function scan. Printed labels
alone do not prove SDK identity; actual runtime checks and immutable source
must be reviewed separately. COMPLETE never authorizes calling a function.

## Capture and cleanup evidence

The separately claimed capture task preserves these new paths exclusively:

- `evidence/v032_user_test.log`: complete raw
  `Binaries/Win32/Plugins/unrealsdk.log`, stable reads before/after copying,
  byte size, SHA256, timestamp and actual call count/deviations.
- `evidence/v032_capture_manifest.json`: exact reviewed commit/package hashes,
  installed three-file equality, explicit human confirmation, raw-record
  references and independent process-count observations before/after capture.
- `archive/tested_runtime/v0.2.12/`: exact installed `__init__.py`,
  `pyproject.toml` and `README.txt`, each created exclusively and hash-checked.

No new capture is inferred from old logs, mocks or this plan. Preserve every
original v11/v12 archive and earlier snapshot/log/manifest byte. If a target
capture path already exists, stop and coordinate a new scope; never overwrite.

For a successful armed insertion, review the actual original-array RESTORE
record and NATIVE ARRAYS RESTORED message plus zero remaining owned observer
families after the last inspection. A no-patch message alone cannot prove an
earlier insertion was restored. Any actual removal/rollback failure remains a
finding even if a later attempt succeeds. The [v11 manifest](../evidence/v031_capture_manifest.json)
is a historical example, not fresh v12 evidence. A log ending or process silence
is not independent exit proof: record read-only Borderlands2 process counts.

If restoration fails, fully exit and preserve the failure; do not start normal
play or another experiment before review. Native-array rollback does not refund
points, undo grades/saves or clear engine/UI caches. Full restart is required
before normal play after an armed experiment. This plan makes no guarantee
about when BL2 saves; Alt+F4 is not proof of prevented saves. Manual duration
restore is separate from node CANCEL/disable, and no duration boost belongs here.

No effect, purchase/transaction, persistence, co-op or release claim follows from
this test. Review actual captures using the submitted offline tool when available,
then perform a separate recorded acceptance review; any authorized participant
may review, including a labeled self-review.
