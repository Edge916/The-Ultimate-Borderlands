# Offline v0.2.19 relationship metadata log review

This standard-library reader checks the bounded `[UVH-REL-META]` text emitted
by the accepted [v19 implementation](deathtrap_manager_relationship_metadata_instructions.md)
at `7a23c583a0d81507b7c01e1edc82171c7c50a97f` / [PR49](https://github.com/Edge916/The-Ultimate-Borderlands/pull/49).
Its grammar follows the [design](deathtrap_manager_relationship_metadata_design.md)
and the actual callback/control source, including late refusal of both roots.
It reads a selected preserved log without modifying it, importing the SDK,
starting the game, or calling any engine function.

```powershell
python -B scripts/review_deathtrap_manager_relationship_metadata_log.py PATH_TO_PRESERVED_LOG
```

Use an actual Python interpreter if `python` is a Windows Store alias.
The command prints bounded JSON to stdout and returns:

| Exit | Status | Meaning |
| --- | --- | --- |
| 0 | COMPLETE_LOG_TEXT | All recorded sessions have complete scoped catalog text and resolved final STOP. |
| 1 | PARTIAL_LOG_TEXT | A valid recorded descriptor or known-row bound kept coverage partial. |
| 1 | NOT_OBSERVED_LOG_TEXT | Valid START/END/STOP recorded no attempt; no catalog is invented. |
| 1 | REFUSED_LOG_TEXT | Text is coherent and closed, with preserved refusal/error/cleanup failure history. |
| 2 | INVALID_LOG_TEXT | Malformed, inconsistent, mixed, clipped, bounded-out or unclosed evidence. |
| 2 | NO_METADATA_RECORDS | No recorded metadata session; ordinary startup/idle refusal is not a silent run. |
| 2 | INPUT_ERROR | Invalid UTF-8, NUL, read failure or input size/line bound. |

Exit 0 verifies recorded text consistency only. It never establishes source
authenticity, installed build, owner protocol, native pointer safety, ownership,
allocation generation, liveness, engine execution, clock/Duration behavior,
purchased rank-one or an effect. All corresponding readiness flags remain false
or NOT_ESTABLISHED, even for complete catalogs. A coherent refusal is a useful
finding; exit 1 is not a request to repeat an owner diagnostic.

## Checks and limits

The reader requires compact sorted-key canonical JSON, exact record key/type
sets and fixed tokens; duplicate/extra keys, bool integers, escaped ordinary
ASCII, floats/exponents, unknown versions and invalid names are rejected.
It accepts bare project records and the actual SDK INFO header framing, while
checking the entire project message against its 512-ASCII-byte limit.
New-family partial/unknown markers and legacy activation/callback reader
markers make a combined log invalid. Unrelated startup text is ignored.

Each positive epoch has one START or a faithfully recorded registration refusal,
at most one BEGIN/attempt, MGR then CTRL, consecutive row ordinals and no repeated
declaring-owner/name pair. A shadowed name under a different owner stays distinct.
ROW owners are ancestry indexes (MGR0..2, CTRL0..6), not player ownership.
Known declared tokens, uint64 flags, element size4, dimension/kind and maximum
layout are checked. The log omits class PropertySize, so the reader cannot
independently re-prove the runtime's exact per-class layout guard from text.

ROOT category counts and emitted rows conserve; complete or partial prefixes
require all recorded descriptor rechecks and exact `24*(visited-objects)+27*objects`
issued catalog operations. Complete gate/root setup is exactly98/68.
PROPERTY_LIMIT requires512 visited descriptors; ROW_LIMIT requires65 known
object declarations and64 emitted rows. REFUSED preserves counters and a matching
fault; late ROOTS/SESSION failures can refuse both already-inspected catalogs.
END totals conserve the four stages and128 rows, with caps112/96/14000/14000
and28208 total. Those are issued Python-side counts, excluding native getter,
copy, conversion and SDK helper internals.

COMPLETE_LINK means only the recorded null-terminated PropertyLink scope.
OTHER class declarations and unsupported subtypes remain explicit. It does not
mean all fields are inventoried or that an instance relationship exists.

Every session needs END and a final non-deferred STOP with remaining/uncertain0.
Busy/deferred STOP may precede BEGIN, but cannot close the session. Errors and
refusals conserve FAULT history; cleanup/removal attempts never decrease and
each explicit control allows at most4 attempts,256 total. Later success cannot
erase earlier cleanup failures. Reentry and ignored counters are monotone,
bounded64, and retain saturation flags. Repeated resolved STOP performs no
extra recorded removal; a later expiry fault requires another resolved STOP.
Uncertain registration cannot authorize takeover or restart.

Input limits are16MiB,100000 lines,16384 bytes/line,4096 recognized project
records and128 sessions. Session limits are205 records,64 control records and8
faults. Reports retain at most128 fixed-code issue summaries; invalid raw text,
exception strings and input paths are not echoed. Valid descriptor names are
intentional metadata output. A saturated logger may suppress later calls: this
reader can report only recorded evidence, not reconstruct omitted records or
assert that the last recorded state remained final in the actual process.
Missing recorded closure never passes through silence.

## Verification and handoff

Meaningful synthetic cases cover exact maxima, category/counter conservation,
canonical grammar, partial/refused/silent/complete runs, registration uncertainty,
repeated/deferred controls, cleanup failure retries, mixed/clipped markers,
privacy and bounded outputs. Existing inert project collector fixtures also
produce the exact implementation's complete, empty, partial, refused, timeout,
reentry, changed-root, failed-log and cleanup tails. These exercise project
Python behavior; no real SDK binding or SDK stub is simulated or executed.
Actual check results and preservation fingerprints are in the
[reviewer checks](../evidence/deathtrap_manager_relationship_metadata_log_review_checks.json).

Only the new reader, its tests, this guide and its check report belong to this
task. Historical parsers, raw logs, manifests, snapshots, runtime and all original
ZIP bytes remain unchanged. The complete original imported handoff was read in
34 contiguous100000-byte pages (final shorter page), ending3348046/has_more=false.
Both kickoff reviews were already complete. Jake's active BL4 feasibility work
uses disjoint paths and remains his claim.

The v19 capture task still needs its separately approved exact original ZIP,
owner protocol and game actions after this reader is reviewed. This documentation
does not install, launch, summon, repeat a diagnostic, merge a PR or publish a
release. Do not rebuild a versioned ZIP. Review the exact four-file diff and
actual checks before recording task acceptance.
