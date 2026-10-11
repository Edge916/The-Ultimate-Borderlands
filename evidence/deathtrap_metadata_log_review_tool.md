# Offline v0.2.12 Deathtrap metadata log reviewer

The [standard-library CLI](../scripts/review_deathtrap_metadata_log.py) reads a
preserved UTF-8 log and prints JSON to stdout. It does not modify inputs, import
SDK modules, invoke game functions, install anything or write a capture.

```text
python -B scripts/review_deathtrap_metadata_log.py path/to/preserved.log
```

Use a real Python interpreter. Exit 0 means `COMPLETE_LOG_TEXT`: every parsed
call claims COMPLETE metadata coverage, valid observable rows/FINAL/END, and
post-last-call cleanup text is present with no failures. Exit 1 means partial,
unavailable, refused, invalid, incomplete or absent v12 calls/cleanup. Exit 2
means missing/unreadable/invalid UTF-8 or oversized input. JSON reports call
outcomes separately from restoration, observer counts and retained error history.

The exact grammar comes from prepared v0.2.12 runtime SHA256
`41fd2dd9e22bcfa64fbddfc19b881f6950362656e047b212b00eb86f33a01f73`
at accepted e32cfb1, unchanged through this task's parent aa632a9. Earlier v11
[reviewer](../scripts/review_v031_log.py), logs, captures, snapshots and all
packages remain unchanged. The new tool intentionally does not accept a v11
class log as a v12 metadata capture. No human v12 log has been captured yet.

## What the text can establish

BEGIN must name v0.2.12 with metadata_only=True. JSON METADATA schemas and their
emitted order are checked: controller class; three allowlisted functions;
typed-return manager discovery or UNAVAILABLE; ActiveSkills discovery or
UNAVAILABLE; the six allowlisted skill fields, with Definition's class root
only when actually reported. This gives at most four distinct roots, three
function rows, seven field rows and 15 total rows. No extra inferred roots,
fields, return properties or signatures are added.

Class ancestry is 1–8 reported nodes; CAPPED requires eight. A function reports
0–16 properties; CAPPED requires sixteen. The seventeenth cap-detection read
and native links are not logged and remain NOT_CHECKED. Property/function
numbers have the runtime's exact integer bounds, excluding bool. Class-field
dimension is one and parameter/out/return flags refuse. Aggregate property
size is bounded, but unlogged native PropertySize equality is NOT_CHECKED.
Names and paths are canonical bounded strings; owner/declared/discovered
paths agree with the reported ancestry. Duplicate JSON keys/properties/roots,
cycles by repeated ancestry path, impossible schemas, malformed prefixes,
unknown records and mixed versions do not pass. SDK subclass compatibility is
not derived from a wrapper type's printed name; native identity is NOT_CHECKED.

CAPPED takes precedence over UNAVAILABLE when both occur, as in the actual
runtime. Either remains PARTIAL. A lone UNAVAILABLE can finish no metadata
call; it has no fabricated FINAL/END. ABORT is REFUSED, including after partial
rows or a FINAL. Missing FINAL/END remains incomplete. Full cleanup text is
required after the last call: original MorePep/Myelin arrays/cells restoration,
the separate native-restored assertion, and zero remaining observers for all
four init/upgrade/UI/state families. Failed removals/rollback, malformed or
nonzero cleanup, or manual Duration activity/failure remain findings even if a
later retry prints success. DISARMED/no patch alone never proves restoration.

FINAL has known nonnegative points/ranks, candidate rank zero and the logged
unchanged_from_start=True assertion. **The runtime emits no BASELINE line.**
The tool does not independently compare FINAL to an unseen starting state and
does not enforce equality across separate calls. Different later-call points
or original-skill grades are reported; their cause is not inferred. A supplied
BASELINE line is rejected as an unsupported record, not treated as engine proof.

## Limits and checks

Source byte size/SHA256 refer to the supplied raw log, including an optional
UTF-8 BOM. File input is bounded at 16 MiB, 100000 lines, 16384 characters per
line, 128 calls and 15 metadata rows per call. JSON duplicate keys, excessive
nesting and nonfinite numeric data refuse. Scalar FINAL tuples use bounded
literal parsing only; no commands, arbitrary objects or code are evaluated.
Bare synthetic rows, raw runtime messages with UVH-BOOST, and the known SDK
timestamp/INFO envelope can be parsed; none authenticates the origin.

Installed-file/archive equality, process exit, origin, actual SDK object/class
identity, native links/sizes/subtypes, internal baseline and unlogged lookahead
remain explicit NOT_CHECKED. Game behavior is NOT_ESTABLISHED_BY_TOOL. Even a
passing text report requires independent owner capture evidence and review;
it cannot verify lifespan, purchases, save behavior or effect readiness.

The [46 new tests](../tests/test_deathtrap_metadata_log_review.py) use synthetic
fixtures, including caps/unknowns/partial calls, schema/coverage contradictions,
truncation, multiple calls, cleanup failure then retry, no-patch and input
bounds. One regression cross-checks COMPLETE and CAPPED messages emitted by
the actual preserved runtime in its existing poison/inert SDK harness. That is
mock execution, not a native SDK/game session. The full offline runner passed
401 unique tests (355 existing + 46 new), zero failures/errors/skips/expected
failures; 22 current Python files compiled and package integrity/source equality
and isolated mock import passed. The first harness comparison exposed an
unsupported bare UVH-BOOST envelope; that grammar support was corrected and
the full suite rerun. All 142 parent tracked files remain byte-identical.

Actual CLI runs also returned exit 0/COMPLETE_LOG_TEXT on a labeled synthetic
complete fixture, exit 1/PARTIAL on a synthetic lone UNAVAILABLE, and exit
1/REFUSED on synthetic failed cleanup followed by success. The preserved v11
capture returned exit 1/NO_CALLS and retained its original SHA256
`7339178b278e7e4c63a8ec4272a692c199840c82c99017be2198901f1a1f3b00`.
These checks create no new human evidence. The immutable/current artifact
verifier passed on the prepared build and originals as separate inputs.
