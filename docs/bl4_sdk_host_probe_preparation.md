# Offline BL4 SDK preparation and fixture rehearsal

This tool verifies the accepted [host-probe design](bl4_host_probe_design.md)
without installing anything. Its command reads the official archive as data and
creates a new JSON manifest. Its separate rehearsal functions copy only synthetic
bytes into a marked temporary fixture. They cannot install the official SDK.

**Decision: offline preparation is implemented; production installation and
rollback need separately reviewed work and exact owner approval.** Native
compatibility with Steam build 25372571 is still untested. See the
[actual check report](../evidence/bl4_sdk_host_probe_preparation_checks.json).

## Manifest command

Use an ordinary supported Python interpreter and an explicitly selected workspace
output. Paths below are arguments, not a game installation location:

```text
python -B scripts/prepare_bl4_sdk_host_probe.py <selected-oak2-sdk.zip> <new-workspace-manifest.json>
```

The command refuses an existing output. It checks exact archive size 14,752,091
and SHA-256 `602675446abed184169fa158be3c8bc81777a71203581e4a248eca8a3d00b5c7`,
the accepted design-check file's hash, CRC and all 63 individual file hashes.
It accepts this pinned [official v0.3 release](https://github.com/bl-sdk/oak2-mod-manager/releases/tag/v0.3),
not whichever release happens to be newest later. Changed inputs require a new
review, rather than updating the accepted historical fingerprints.

The JSON contains relative paths, sizes, SHA-256 hashes, prospective directories,
the loader path and expected Steam build. It excludes absolute installation and
workspace paths, usernames, account identifiers and raw source/log text. Which
directories would actually be introduced remains **undetermined** until a later
approved target preflight. Preparation does not inspect the game or declare an
installation safe from a manifest alone.

No SDK archive member is extracted, imported or executed. No DLL is loaded. ZIP
members are read for CRC/hash checks only; Python source/stubs remain inert data.
There is no command for installation, game launch or rollback of a game directory.

## Synthetic rehearsal

The library functions are exercised by
[filesystem tests](../tests/test_bl4_sdk_host_probe_preparation.py). A fixture
must begin as an existing empty temporary directory. `init_fixture` creates its
exclusive `UVH_SYNTHETIC_ONLY` marker. The fixture guard refuses an absent or
changed marker and any executable in the bounded tree. Every copied payload must
start with `UVH-INERT-FIXTURE`; native DLL/SDK bytes fail this gate.

Build and process arguments are **test inputs**, not queries of Steam or actual
processes. Tests verify mismatch refusal, but these functions do not establish
that a real game is closed. They must not be used as a production preflight.

Both ZIP and filesystem validation reject absolute/traversal paths, alternate
streams, backslashes, device names, trailing dots, noncanonical characters,
duplicate/case-colliding files and parent-file conflicts. Existing filesystem
ancestors and children are checked for symlinks and Windows reparse redirection.
One actual Windows directory junction was created and rejected in an owned
temporary fixture; its target was another directory in that same temporary root.
Injected symlink/reparse metadata tests are separately identified as simulations.

Staging refuses existing target files and unexpected SDK-directory contents
before opening its journal. It creates individual absent directories and opens
each file exclusively. It records and flushes intentions before writes, checks
copied bytes and introduces the synthetic loader **last**. An interruption leaves
the append-only journal and written fixture data; it does not manufacture a
completed installation. `recover_fixture_receipt` reads the initial write-ahead
receipt without mutating files. Truncated journals refuse.

Rollback first verifies every remaining manifest file and introduced directory.
An independent edit or unknown child causes refusal before removal. It
quarantines the unchanged synthetic loader **first**, then other matching files.
Quarantine is an explicitly selected, empty, disjoint temporary folder; writes
are exclusive and verified before unlinking the matching source. Only verified
empty introduced directories are removed with `rmdir`, never recursive removal.
Existing scaffolding and unrelated root files remain intact.

An independent change during rollback can leave a partial quarantine. The journal
records completed moves; no `ROLLBACK_COMPLETE` is emitted on failure. Preserve
both locations and investigate instead of blindly retrying. A partial copy with
different bytes is retained and refused, rather than discarded as though it were
known owned data. The tool does not automatically restore altered files or empty
a nonempty directory.

## Practical limits and next gate

These checks and exclusive writes handle tested deterministic failures. They are
not an atomic Windows security boundary against a hostile concurrent replacement
of directories or junctions. The journal is not signed or an authenticated record
of ownership. Crash durability across power failure, network filesystems, real
SDK-generated settings/logs, antivirus interference and Windows native dependency
loading are not established. Treat the fixture routines as rehearsals, not a
general installer or rollback utility.

The next production preparation must separately establish current selected-root
containment, live build/process checks, exact collisions, existing SDK configs,
environment overrides, extra mod folders, generated log/settings inventory and
owner-approved recovery paths. It needs an exact reviewed target manifest and
tested platform implementation before any installation request. No SDK/runtime
installer, game startup, profile/save/private-backup access or public raw-log
export is authorized by this offline task.

After those gates, the proposed owner test remains **DESKTOP / game closed →
STEAM / approved offline launch once → MAIN MENU only → built-in `mods -v` once →
normal quit → DESKTOP / confirmed full exit → preserve log before relaunch →
reviewed rollback**. Do not perform this future protocol yet. Do not select
Continue, New Game, Character Select, a campaign or matchmaking. The accepted
design retains its five-minute launch and one-minute menu bounds and no-retry
conditions. Normal startup may write game profile/settings; no zero-save-write
claim is made.

No campaign, map cooking/loading, playable hunter, movement, ownership/lifetime,
co-op or effect proof follows from archive equality or a synthetic round trip.
