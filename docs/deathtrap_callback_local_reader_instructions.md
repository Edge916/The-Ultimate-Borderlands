# Prepared v0.2.16 callback-local reader

This build adds **22 - START CALLBACK-LOCAL DEATHTRAP READER (NO ARM)** and
**23 - STOP / REPORT CALLBACK-LOCAL READER**. It is prepared for offline
review, with no game result or requested installation. The latest game-tested
diagnostic is v0.2.15; its preserved outcome is NOT_OBSERVED.

Read the [accepted design](deathtrap_callback_local_reader_design.md) and
[implementation checks](../evidence/deathtrap_callback_local_reader_implementation_checks.json).
The [runtime](../sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py) validates
fresh callback-local schema/controller/player facts and emits fixed primitive
labels. SAME_WRAPPER/DEATHTRAP_NAME are observations, not owned-manager,unique
summon,allocation generation or native write/restoration proofs.

No native engine function,active-skill scan,Boolean argument,ret,point/rank/
Duration/save field or native flag is used by the new reader. No native object,
descriptor,parameter buffer,bound function or exception/traceback is retained
in reader state or logging. The SDK's existing helper globals and pre-Python
conversions are disclosed; mock success does not establish native lifetime.

START checks only Python project state and the fixed hook-control API. It
refuses ARM/node/manual-record and other active or uncertain observers. The
first natural DeactivateSkill PRE callback performs schema validation. Import
starts nothing. The original21 controls retain their positions; they refuse
while this reader is active,except CANCEL3. STOP23 and disable remove only
the new reader's owned tuple,making it inert first and deferring removal when
busy. Unknown registration is not removed as owned. Failed cleanup remains
retryable and prevents a new START; retries retain failure history.

All reader output uses [UVH-CALLBACK-READ],fixed allowlisted labels and exact
primitive counters. One session has at most64 accepting attempts and24
classified records. Nested reentries do not inspect payloads or consume an
accepting attempt. The120-second bound is checked on operations/controls,not
by a background timer. Each callback counts at most256 reader-issued SDK
operations in four64-operation stages; SDK helper/conversion internals are not
counted. Entire project log lines stay within384UTF8 bytes.

Before any owner-run diagnostic:

1. Complete review of this exact source and original v0.2.16 ZIP.
2. Implement/review the separately scoped strict offline reader-log reviewer.
3. Obtain explicit owner approval of the exact build and meaningful natural
   gameplay protocol on already-backed-up solo Offline Gaige. Creating or
   publishing these files does not approve a game test.
4. Use clear location-based instructions: main menu for Offline/character/title
   verification,then Continue and fully load into the map. The reader requires
   no ARM/node insertion. Its START22 and STOP23 controls must be stated by
   name and location. Any ordinary Deathtrap use must be explicitly approved.
5. Include STOP23,CANCEL3 and full exit to the desktop before preserving the
   full log and installed files. Report refusals,deviations and visible failure.

No new owner steps are requested here. Repeating passive waiting is not a
meaningful event guarantee. Zero events is NOT_OBSERVED; filtered/refused
events differ from useful primitive observations. PRE is attempted entry even
when another hook blocks execution. No forced native call,purchase,respec,
travel,manual boost,effect or unauthorized retry may recover missing evidence.

Keep all raw captures,manifests,snapshots and15 original ZIPs unchanged.
Ownership/native adapter/effect remain NOT_READY,with existing dependencies
intact. The manual duration prototype and grade-zero diagnostic are unchanged;
CANCEL/disable still do not invoke manual Duration restore. No save/private-
backup access,SDK execution,installation,game test,merge or release occurs in
this implementation task.
