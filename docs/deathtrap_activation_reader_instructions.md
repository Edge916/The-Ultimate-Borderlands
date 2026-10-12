# Prepared v0.2.18 callback activation reader

**Prepared for offline review. No v0.2.18 game result or owner-run diagnostic is
authorized by these instructions.** The exact title is
`UVH v0.2.18 - CALLBACK ACTIVATION READER`. Read the
[accepted design](deathtrap_activation_reader_design.md),
[source audit](deathtrap_activation_reader_feasibility.md) and
[v17 assessment](../evidence/deathtrap_callback_definition_name_live_readiness_result.md)
before relying on this build.

The replacement reader observes one fixed
`WillowGame.SkillEffectManager:ActivateSkill` PRE hook and emits
`[UVH-ACTIVATION]` records. It requires no ARM or node insertion. Its controls are:

| Item | Label | Purpose |
| --- | --- | --- |
| 22 | START CALLBACK ACTIVATION READER (NO ARM) | Opt into one bounded reader session. |
| 23 | STOP / REPORT CALLBACK ACTIVATION READER | Make capture inert, resolve the owned hook and report its counters and cleanup. |
| 3 | CANCEL / RESTORE NATIVE ARRAYS (THEN RESTART) | Use the established project cancellation and array cleanup. |

Import starts no reader. START checks project control state and the fixed hook
API, without a player, function, property or UObject read in its option handler.
It refuses ARM/node/manual-duration records and active or uncertain observers.
The first naturally delivered accepting callback performs the fresh checks;
registration alone proves neither schema nor event coverage.

## What this reader can establish

Inside the callback, validate the complete six-property ActivateSkill schema,
including the Boolean ReturnValue **descriptor**. Then read only
`args.SkillInstigator`, followed by `args.Definition` only for a freshly validated
local solo Gaige controller. Read that definition's Name once. Accept only an
exact Python string of 1..128 ASCII letters, digits or underscores. The literal
`Skill_DeathTrap` produces DEATHTRAP_NAME; another valid identifier produces
OTHER_NAME. Null or foreign instigators never read Definition. A local null
Definition is observed through its getter and leaves Name unread. All four
absence branches use `-`. Invalid values refuse without conversion, clipping
or object formatting.

The Python reader does not inspect the ret argument or the values of
AdditionalSkillTarget, SkillGrade or StateChangeDelegate. Descriptor checks are
metadata reads. It invokes no engine function or delegate and writes no native
argument, return, flag, Duration, rank, point or save value. The inspection frame
finishes and obj/args/ret/func are dropped before primitive emission. No native
wrapper, descriptor, exception, traceback or Name history enters reader state;
the observer closes over only a primitive epoch and returns exact non-tuple None.

These Python restrictions do not prevent SDK processing before the callback.
ProcessEvent copies PARAM fields, including ReturnValue, and CallFunction steps
argument expressions. Native wrapping and a prior Boolean return-override
conversion can also precede Python guards. The operation meter excludes these
internals. Hook-time VM/GC guidance does not establish protection against already
invalid inputs, arbitrary destruction, native generation, thread affinity or
installed binary/configuration equivalence. Exact None adds no block or return
override; another hook can still block or alter the original call. PRE observes
attempted entry, rather than successful activation.

The accepted v17 capture remains one UpshotRobot/OTHER_NAME observation. The
owner separately reported that Deathtrap ended naturally. Those facts do not
establish a Deathtrap association, and v16's omitted Name cannot be recovered.
No alias or new effect follows a primitive identifier. Native manager ownership,
unique summon, generation/later liveness, engine timing, Duration, rank-one
eligibility and exact-original write/readback/restoration remain NOT_READY.

## Bounds and cleanup

One session allows at most 64 accepting attempts and 24 classified events. The
120-second limit is checked at callback, metered operation and control boundaries;
there is no background timer. It is a reader bound, not an instruction to wait
120 seconds or proof of an owner waiting interval.

The four reader-issued operation caps are 112, 80, 48 and 80, with a total cap of
320. Each reserved operation counts even if it fails. A cap refuses before the
next access. SDK conversions, copied inputs, iterator/helper internals and engine
processing are outside this counter. Each activation-reader record, including
the project prefix, remains bounded to 384 UTF-8 bytes. Busy reentry uses a
primitive counter without payload inspection;
stale callbacks return None.

STOP clears accepting before removing only the hook tuple the reader positively
owns. Removal is deferred while busy. Uncertain registration is checked without
deleting a foreign tuple; failed cleanup remains pending, prevents restart and
retains failure history even after later resolution. CANCEL and disable retain
the established cleanup order. They do not invoke manual Duration restore. The
manual prototype and grade-zero diagnostic remain separate.

## Gates before any owner-run diagnostic

Review the exact implementation, source hashes and original v0.2.18 ZIP first.
The package must contain exactly one `UltimateVaultHunterDeathtrapBoost/` folder
with `__init__.py`, `pyproject.toml` and `README.txt`, matching the reviewed source.
The final commit, ZIP hash and source/package checks must accompany any later
owner instructions; no unverified hash is supplied here. Preserve every previous
raw log, manifest, tested snapshot and original versioned ZIP.

A separately scoped **strict activation-log reviewer** must be implemented,
tested and accepted before a new diagnostic is proposed. The old v16/v17 reviewers
do not validate this prefix, ActivateSkill target or new operation counts. The
new reviewer must reject old/mixed evidence and retain cleanup failure history.
Parser completion establishes text consistency, rather than log authenticity,
installed bytes, process exit or native lifetime.

The owner must explicitly approve the exact reviewed build/ZIP and meaningful
gameplay protocol, including any ordinary Deathtrap summon. Publishing the build
or this document does not authorize installation, launching, a summon or a game
test. No finalized summon count or owner waiting cutoff is specified here.

## Location-based layout for later approved instructions

This is the required layout for a future protocol, **not a request to run now**.
The final approved protocol must supply the exact build and permitted action and
time bound before these steps are actionable.

1. **Before launch, with Borderlands 2 fully closed:** verify the reviewed ZIP
   and follow its approved installation instructions. Replace only the project
   mod folder, leaving SDK/core mods alone. Use the already-backed-up solo
   Offline Gaige setup specified in the approved protocol; no agent accesses
   saves or private backups.
2. **At the MAIN MENU:** verify Offline mode, Gaige and the exact title
   `UVH v0.2.18 - CALLBACK ACTIVATION READER`. Do not select ARM item 1.
3. **Move from the main menu into the MAP:** select Continue and wait until the
   map is fully loaded before opening the project mod options.
4. **In the fully loaded MAP:** select **22 - START CALLBACK ACTIVATION READER
   (NO ARM)** once. If it refuses, report the refusal and proceed to the approved
   stop/exit steps without another START or a forced event. If it accepts, close
   options and perform only the ordinary action explicitly approved in the final
   protocol, within its stated owner time bound. No action is approved here.
5. **Still in the MAP:** select **23 - STOP / REPORT CALLBACK ACTIVATION READER**,
   then **3 - CANCEL / RESTORE NATIVE ARRAYS (THEN RESTART)**. Report any refusal,
   pending cleanup, visible failure or deviation. Do not rearm or repeat a test
   to manufacture an event or identifier match.
6. **Exit to the DESKTOP:** fully close Borderlands 2. Report completion of STOP,
   CANCEL and full exit, plus what happened during the approved action. Keep the
   game closed until the complete log and installed files have been preserved;
   relaunching can replace the live log.

Zero attempts is NOT_OBSERVED. A valid different identifier is OBSERVED_FILTERED;
an exact literal match is OBSERVED_PRIMITIVE, with ownership still UNESTABLISHED.
Silence, an unavailable skill, refusal or a reached bound is preserved without
retry. No purchase, respec, travel, manual boost, metadata inspection or other
trace belongs in a future protocol unless separately authorized.

Future raw SDK logs may contain startup information, addresses and installation
or object paths. Even a bounded simple identifier can contain personal text in
a modded game. Preserve the exact log privately after full exit, verify installed
snapshots against the approved ZIP, and review the actual contents before seeking
separate approval for any public raw-log export. This document authorizes no
game/save/private-backup access, support message, merge, release or capture export.
