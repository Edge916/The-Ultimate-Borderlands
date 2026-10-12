# v0.2.10: native presentation flags and attribute identities

## Evidence and scope before implementation

v0.2.9's two live snapshots verified24/24 native presentation strings each,
Overclock's empty array and unchanged sampled points/ranks. Native descriptions
contain $NUMBER$ templates; other inspected strings are empty. The log and
exact tested source/ZIP are preserved. Missing presentation data is a supported
hypothesis for absent orange bonus text, not proof of causation or eligibility.

The next explicit button4 comparison reads only these previously observed
AttributePresentationDefinition fields (v028_presentation_retry.log lines70,
81,83,84; repeated107,118,120,121):

| Field | Type | Flags | Offset | Dimension |
|--|--|--:|--:|--:|
| bDontDisplayNumber | BoolProperty | 3 | 116 | 1 |
| bUseCustomNumberPlacement | BoolProperty | 3 | 116 | 1 |
| bEnableTextColor | BoolProperty | 3 | 116 | 1 |
| Attribute | ObjectProperty, declared AttributeDefinition | 3 | 64 | 1 |

Validate targeted loaded descriptors via SDK _find_prop: exact field/owner,
type/flags/offset/dimension, actual declared UClass/name for Attribute. No
packed masks inferred from the shared Boolean offset; let SDK getattr read
an exact bool. Bool-like integers and unknown payloads are UNAVAILABLE.
Read only typed SDK Attribute reference identity: None is VERIFIED absence;
actual UObject with Class identical to declared AttributeDefinition is eligible
for bounded escaped SDK _path_name. Subclasses or same-name different classes
are unverified and refuse. Do not traverse or evaluate attributes, enumerate
their fields, read their values or invoke native methods/formatters.

## Guards, finite coverage and changed references

Reuse _upgrade_state and _presentation_text_reference unchanged. Validate exact
owned current Gaige/tree/pawn/world/PRI, named solo roles/both sole-player
rosters, known unchanged points/ranks/indices/tier, unique registrations and
owned inert grade0 patch. Refuse overlapping/failed loading/init/upgrade/UI/
focused observers. Per-call baseline; no repair/refund after a state change.

Up to256 array entries accepted, up to4 references sampled per skill. Fixed
three flags and one Attribute field per reference: maximum36 Boolean fields
and12 attribute identity/absence records,48 total distinct captures per call.
Attribute getters have at most four reads per sampled entry (initial plus
identity rechecks); total named instance reads<=84/call. No text reread.
Bound and escape presentation/attribute paths<=384 characters. Metadata and
array/current membership/count/classes revalidated around each payload read.
When a typed Attribute value has been accepted, keep a local expected reference
and revalidate its loaded descriptor/current field/Class around the path read
and again outside field exception handling, before logging. A changed typed
reference or its schema aborts before another field/target; no stale VERIFIED
record. Invalid initial field schema/type/getter/path is UNAVAILABLE, not empty;
other allowlisted fields continue only if all state/reference guards still pass.
Unknown/changing presentation arrays/references abort before another target.

Separate known array count/sample, verified flag count, known Attribute fields,
present/absent references and partial display coverage. Empty array is
NOT_APPLICABLE. FINAL unchanged only after full guarded comparison. New log
prefix [UVH-DISPLAY]; reused [UVH-PRESENT] SCHEMA are membership rechecks.
No new global capture state, hooks, loads, native calls, copies, overrides,
constructor/effect/point/save writes. Existing insertion/rollback/manual duration
and observer cleanup remain unchanged. Button4 route/factory metadata change;
19 options retained. New runtime uses v0.2.10; v0.2.9 artifacts remain intact.

## Validation to complete before shipping

Meaningful new mocks must cover valid native comparison/known absence without
writes/native calls; exact descriptor/type/owner/class refusal before poisoned
payload; strict bool and UObject/class checks without conversion/repr; getter
failure versus known absence; path bounds/escaping; fixed sample/field bounds;
overlap/failed hooks; stale state before metadata and changes during metadata,
payload/path; replaced array/presentation/typed Attribute and schema changes;
no Attribute traversal/evaluation; preserved cancellation/disable cleanup.
Keep all127 established cases, changing only necessary version/route assertions.

Prove old function ASTs unchanged except version labels. Run meaningful full
mocks and runtime syntax. Build/verify default ZIP with inert isolated19-option
import, exact single mod folder/three files, integrity and source match, then
create distinct v0.2.10 ZIP exclusively. Preserve all39 protected original
ZIP/snapshot/log/PNG hashes. No game/SDK/save installation or writes by Codex.
SDK stubs were read as documentation only, never imported/executed/packaged.

## Proposed game test after those checks pass

Fresh BL2 process, replace only project mod. Verify exact title
UVH v0.2.10 - OVERCLOCK PRESENTATION DISPLAY at main menu; item1 ARM before
Continue as already backed-up Gaige alone Offline. In map open mod options,
select item4 INSPECT PRESENTATION DISPLAY (READ ONLY) once, item3 CANCEL /
RESTORE, fully exit and report done. Numbers label menu options, not keys.
No highlighting, trace START/STOP, points/respec/travel/boost or other diagnostics.
On unknown/partial/refusal cancel/exit and preserve evidence; never bypass guards.
Preserve/hash the next log under a distinct filename before any relaunch.
Verify installed bytes, coverage/refusal/path evidence, sampled FINAL state,
all hooks0, native RESTORE result=True and exit. Node effect remains inactive.
No v0.2.10 engine result is available at design time. Purchases/persistence/
automatic effects/co-op/release remain separately scoped later milestones.


## Completed local validation

24 new display tests passed on the first targeted run in3.081 seconds.
The full suite passed151 unique tests in13.378 seconds, preserving127 prior
cases and adding24. Tests cover the planned schema/class/type/owner guard
before poisoned payload; exact Boolean and typed UObject without repr/
conversion; known absence/getter failure; path bounds/escaping; fixed sample/
field limits, overlap/refusal; stale array/presentation/Attribute/schema,
state changes during metadata/getters/paths, and unchanged cleanup. Poisoned
Attribute value/evaluation/metadata methods prove no traversal in the mock.
All six native mock refs yield18 flag and6 identity records; identity rechecks
read the Attribute field a bounded four times per present reference.

Runtime syntax and AST proof passed:76 old functions,70 AST-identical and
six version labels only (old purchase, upgrade/UI/focused START, old count/
text inspectors). Four new functions plus one fixed flag tuple. Factory/
metadata/button4 route changes. Two prior version and one route assertion
updates only. Established insertion/rollback/manual duration, state/session
guards, old observer callbacks and cleanup remain unchanged.
All39 protected original ZIP/snapshot/log/PNG hashes remain unchanged.
No v0.2.10 game result or direct game/SDK/save installation/write.
Package checks and artifact hashes are recorded below after final packaging.


## Final packaged artifact

Default package generation and verify_package.py passed: inert isolated
19-option import with no game-state access/scaffolding, exact single mod
folder/three files, ZIP integrity/runtime compilation and source equality.
Factory title/version/button4 route and current handoff status were checked.
The new versioned ZIP was created exclusively, byte-identical to the verified
default, then rechecked. No source changes followed the full151-test pass
apart from documentation; runtime/pyproject stayed byte-identical through
packaging. All39 protected original artifacts retain their hashes.

- Versioned/default ZIP: 32,742 bytes, SHA-256
  962d5c11041b2d1db727d8ca130197a2a06e0fe3464b29cc64ac178ba0dc10fa.
- Runtime SHA-256:
  4f34082483c0d14715f708c9c8c61d42bcfe9bb262c23445ce9808489bc7bdbb.
- pyproject.toml SHA-256:
  cd8a2e28c91e15b30bd8d5188f64864ed7c26cea3d9017cd3483862df558ba5f.
- Packaged README SHA-256:
  4b6fb1f42297f76f737e9ebf87a517019d4b23db47c33fe1fc348752cbe82fa5.

Current ZIP: dist/UltimateVaultHunterDeathtrapBoost_v0.2.10_folder_install.zip.
No v0.2.10 game result yet. Next is the documented fresh solo Offline1,4,3
test; preserve its new log before relaunch. No direct install/game/SDK/save
write was performed. The node remains inactive.


## Completed game review

The subsequent restarted run is preserved in v030_user_test.log and reviewed
in v030_live_presentation_display_result.md. Four calls verified23/24 fields
each: all18 flags and five of six typed Attribute identities. Myelin's second
Attribute refused the exact declared-class guard; actual class/ancestry/path
remain unobserved. All BASELINE/FINAL points=(1,0)/ranks=(0,0,0) unchanged,
arrays restored, hooks0 and process count0 checked. No ABORT/ERROR/Traceback.
The user separately reports a prior purchase to Overclock1/1 then Alt+F4/
restart; that transaction/grade1/save behavior is not in this retained log.
Keep the report separate from captured reset state, and do not repeat purchases
to recover evidence. No save parsing/edit/backup restore/point repair occurred.
Above no-live statements describe build-time status. Exact tested files are
under archive/tested_runtime/v0.2.10; original ZIP/runtime/pyproject unchanged.
Only documentation/default ZIP may change at review; no next runtime/test.
