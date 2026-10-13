# BL4 SDK host compatibility probe design

Design only — October 12, 2026. No installation or game run is approved by this
document. Accepted parent: BL4 feasibility audit
`40f663eca0353db713833f30e6e6c5351018009b` / [PR52](https://github.com/Edge916/The-Ultimate-Borderlands/pull/52).
Read the [audit](bl4_unified_collection_feasibility.md) and
[actual design checks](../evidence/bl4_host_probe_design_checks.json).

**Decision: ready to prepare a bounded staging/rollback tool and an owner request;
installed-build compatibility remains untested.** The proposed proof is one SDK
startup at the main menu, not a map, mission or legacy-character test.

## Exact candidate and provenance

The [official BL4 installation page](https://bl-sdk.github.io/oak2-mod-db/)
links to the oak2-mod-manager release channel. Its resolved latest stable release
is [v0.3: Whiskey Foxtrot](https://github.com/bl-sdk/oak2-mod-manager/releases/tag/v0.3),
published June 26, 2026, tag commit
`77ec7de7471c76958842f321b12a54ebf896b36c`.

The candidate is **oak2-sdk.zip**, asset ID 458756674, **14,752,091 bytes**.
Observed SHA-256:
`602675446abed184169fa158be3c8bc81777a71203581e4a248eca8a3d00b5c7`.
The downloaded bytes match GitHub's published asset digest. CRC checks pass.
The ZIP was inspected as data in workspace scratch; native code was not loaded,
SDK source/stubs were not imported or compiled, and no content was installed.

The release declares Base 1.12, Console Mod Menu 1.6, Keybinds 1.1,
pyunrealsdk 1.10.0 / c72c5558 and unrealsdk 3.2.0 / b1852aa4.
Bundled text constants corroborate the first three component versions. Manager
configuration declares `0.3 (77ec7de7)` and `Whiskey Foxtrot`; its bundled startup
source matches the pinned manager source after line-ending normalization.
These are archive/source declarations, not observed running component versions.
The same SDK source revision used by another game does not establish BL4 binary
compatibility: the game backend and native build still matter.

The release claims support for both previous signature sets. It does not name
Steam build 25372571 as a tested build in the inspected release text. Do not turn
that general claim into a compatibility result for this installation.

## Local preflight observed

Fresh sanitized metadata still identifies Steam AppID1285190/build25372571,
with the executable present. BL4 process count was zero at the check. The x64
VC runtime registry reports Installed1, version v14.51.36247.00; no redistributable
installer was run and this is not a loaded-dependency test.

All **63 SDK archive target files** were checked against the actual game root;
none existed. Expected Plugins and root sdk_mods directories remain absent.
These checks are a point-in-time snapshot and must be repeated before staging.
Existing files, a new game build, extra mods/configuration or a running process
would require reassessment, not an automatic overwrite or continued test.

## Installation layout and preparation requirements

The ZIP is rooted at the game directory. Its loader is
`OakGame/Binaries/Win64/dsound.dll`; native SDK/Python files and the default
configuration live under `OakGame/Binaries/Win64/Plugins`.
Mod manager and bundled libraries live in the game-root `sdk_mods` directory.
The default init-script path goes four parent directories from Plugins to that
root. Do not place the root sdk_mods folder inside Win64 or create nested copies.

A later, separately claimed preparation task must build and test a staging and
rollback tool using inert temporary directories only. Before requesting owner
installation permission it must produce a concrete 63-file manifest containing
every exact archive path/hash, proposed target and introduced directory. It must:

- Verify the exact publisher/archive hash and CRC; reject path traversal, absolute
  paths, alternate streams, symlinks/reparse redirection, Windows device names,
  duplicate paths and case-insensitive collisions.
- Resolve and verify all targets remain inside the explicitly selected BL4 root.
  Check the exact Steam build and process absence before any copy or rollback.
- Refuse any existing target file or unexpected SDK/mod/configuration. No blind
  overwrite, game-file replacement or recursive removal of a shared directory.
- Review default configuration and any environment/config override that can
  redirect SDK startup, logging or extra mod folders. Refuse unexpected overrides;
  do not launch debug servers or add third-party/gameplay mods.
- Stage the unmodified official files only after exact owner permission, then
  compare installed bytes to the manifest. No custom probe/runtime code is needed.

The SDK's pinned startup code creates a native initialization thread when loaded;
installation followed by launching the game therefore executes native code.
Archive inspection and approval to publish this design do not authorize that.

## Proposed owner protocol — not approved yet

The later request must name the exact SDK archive/hash, reviewed staging tool,
Steam build and rollback manifest. The owner must have a suitable existing
backup arrangement before the run; this design neither reads nor creates saves
or private backups. Normal game startup may write its own profile/settings;
remaining at the main menu does not prove zero save/profile writes.

1. **DESKTOP / BL4 CLOSED:** verify the approved build and process absence. Stage
   only the exact reviewed SDK manifest after installation permission. Preserve
   any existing log before launch; abort on build/path/config/file differences.
2. **STEAM:** use the approved offline startup condition and launch BL4 once.
   No account sign-in, new network mode or additional settings are part of this
   protocol. If offline startup cannot reach the main menu, record that result.
3. **MAIN MENU:** stay here. Do not select Continue, New Game, Character Select,
   a campaign or matchmaking. Confirm normal menu loading, then press the
   console key twice as described by the official installation guide.
4. **MAIN MENU / CONSOLE:** look for the built-in console-menu loaded message.
   Enter **`mods -v` once** to obtain Console Mod Menu's version. The inspected
   bundled source explicitly registers this version option. Do not enter Python,
   object queries, cheats or other commands; do not enable any extra mod.
5. **MAIN MENU:** return through normal UI and quit the game normally. The future
   test is bounded to five minutes from launch and one minute of menu inspection.
   If the menu/console/command is unavailable, initialization reports an error or
   the bound is reached, stop and report; no retry to force a successful result.
6. **DESKTOP:** report what appeared and confirm full exit. Wait for preservation
   of the complete SDK log and installed-file checks before relaunching.
   If normal exit fails, report that the process may still be running; do not
   claim full exit, preserve an incomplete run as complete or perform rollback.

Exact UI wording and the approved offline launch condition must be confirmed in
the final owner request. This outline is a future protocol, not instructions to
install or run the game now.

## Log preservation and result meaning

Pinned SDK initialization chooses `unrealsdk.log` beside its DLL unless a config
override changes it. With the unchanged release layout, the expected relative
path is `OakGame/Binaries/Win64/Plugins/unrealsdk.log`.
The pinned logger opens this file with truncation, so another launch can overwrite
the run. Preserve the complete file only after owner full-exit confirmation and
an independent absent-process check, then hash it with the installed-file manifest.
Local preservation does not authorize posting raw startup logs publicly.

Required evidence is separated into: archive/provenance equality; installed-file
equality and exact build; owner-reported menu/console observations; SDK version
and error text; full exit; and resolved rollback. Missing logs, refused startup,
crash, timeout, absent console, version mismatch and uncertain exit are legitimate
results. No parser should manufacture a success from a missing error line.

At most this run establishes a bounded startup/text observation for that build.
It does not establish package cooking/loading, a custom map, gameplay correctness,
new character registration, co-op, native ownership/lifetime or legacy skills.

## Rollback design

After log preservation and verified full exit, disable the introduced loader
first by moving only its manifest-matched file to a reviewed workspace quarantine.
Then quarantine the other unchanged introduced files and startup-generated SDK
logs/settings under the explicitly approved paths. Keep a rollback journal.
Unexpected changes, unknown files, shared directories or a running process cause
refusal and a precise report; preserve evidence rather than deleting unknown data.

Confirm original target-file absence and remove only verified empty directories
introduced by this installation. Never recursively delete the game, Win64,
Plugins or sdk_mods simply because their names appear in the archive. Restoration
claims concern checked introduced paths and bytes; they do not claim undoing
normal game/profile updates or native activity during startup.

## Validation and next gates

Actual checks: stable release/tag/asset provenance, downloaded publisher-digest
match, all63 file hashes/CRC/layout/native PE metadata, five bundled text files,
five pinned source files, normalized startup-source equality, sanitized current
build/runtime/process metadata, all63 target collisions absent, link/JSON/scope/
whitespace/privacy checks,35 project syntax files, all256 accepted base blobs,
19 original ZIPs/seven complete frozen reports/inventory53,12,5 preservation.
Existing914 tests/hostedCI were not rerun for static additions.

Next gates: publish and deliberately accept the exact two design files; separately
claim/test the staging/rollback preparation; obtain exact owner installation and
startup-protocol approval; preserve and assess the owner-run result. No SDK or
redistributable installation, game launch, save work, native execution, raw-log
export, map/character implementation, merge or release occurred here.
