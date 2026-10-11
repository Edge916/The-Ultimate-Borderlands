# Review the prepared manager-metadata build before an owner test

Prepared version is **v0.2.13 - DEATHTRAP MANAGER METADATA**. Read the accepted
[design](../evidence/deathtrap_lifecycle_diagnostic_design.md), its
[checks](../evidence/deathtrap_lifecycle_design_checks.json) and the
[implementation checks](../evidence/deathtrap_manager_metadata_implementation_checks.json).
The design is accepted at fec90301 / PR15. This build is offline-tested only;
there is no v13 game log or installed-file confirmation yet.

Item4 keeps GetSkillManager's descriptor lookup on the current verified
controller. Its actual typed return PropertyClass supplies the manager root;
only then are ActivateSkill/DeactivateSkill queried on that exact class.
Actual owners must belong to its bounded verified ancestry. No guessed native
path, controller fallback, global discovery, manager instance, native call,
payload read, observer/timer or gameplay write is added. Missing manager
descriptors remain UNAVAILABLE. Complete descriptor coverage does not prove
callability, lifecycle order, native lifetime or effect readiness.

The unchanged owned solo Gaige/tree/session/points/ranks/inert-gradezero gate,
manual prototype, insertion/rollback and observer cleanup remain intact.
Four roots, three distinct function targets, seven fields,16+1 properties and
eight ancestry nodes bound a collection. Metadata getters are revalidated and
can repeat; finite loops cannot guarantee SDK getter latency. Invalid/foreign/
drifting data aborts, unavailable/capped branches stay explicit. Unattempted
manager descendants are never fabricated after unavailable primary discovery.
FINAL compares with an internal unlogged baseline; the parser reports that
limit and cannot reexecute SDK identity/link checks.

The offline reviewer supports separate strict v12/v13 row orders and owner
relations. Frozen [v12 raw log](../evidence/v032_user_test.log),
[manifest](../evidence/v032_capture_manifest.json),
[result](../evidence/v032_live_deathtrap_metadata_result.md) and tested snapshot
remain unchanged. Its reproduced PARTIAL / exit1 is expected, not a new failure.
The original v12 runtime/pyproject/versioned ZIP and all prior artifacts stay
frozen. Static inventory immutable checks pass; its explicit current check
continues to flag prepared-e32 fingerprint drift. Validate this new current
package/source/CRC/layout/syntax/inert import separately.

After deliberate implementation review, refine capture task8649d701 to the
metadata-only v13 protocol and preserve its dependency. Exact new paths are
`evidence/deathtrap_manager_metadata_user_test.log`,
`evidence/deathtrap_manager_metadata_capture_manifest.json` and
`archive/tested_runtime/v0.2.13`. This removes the queued natural-summon
assumption; no lifecycle observer exists in v13. Obtain explicit owner
authorization for the reviewed exact build/protocol before claiming a live
capture or starting installation/testing.

The proposed owner sequence is ARM1 at main menu before Continue, item4 once
in map, CANCEL3 and full exit on backed-up solo Offline Gaige. No purchase,
respec, travel, summon, manual boost or other trace. Capture authentic full
stable log and exact installed three-file equality before any relaunch;
UNAVAILABLE/REFUSED/CAPPED is honest evidence, not permission to expand a test.
The agent does not install the build, control the game or access saves/backups.

Lifecycle/lifetime/clock/write timing/rank-one gating and automatic +15-second
effect remain NOT_READY. A future effect needs new evidence, separate design
and explicit feature/test scope. Current owner work ends at a reviewed metadata
collection/restoration/exit; no co-op, persistence test, merge or release.
