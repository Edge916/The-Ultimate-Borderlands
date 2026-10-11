# v0.2.12 live metadata result: partial coverage, verified preservation

The owner completed the reviewed metadata protocol and explicitly confirmed
ARM1 / item4 / CANCEL3 / full exit, with no visible failure. The complete raw
[log](v032_user_test.log), [manifest](v032_capture_manifest.json) and exact
three-file snapshot under `archive/tested_runtime/v0.2.12` were preserved before
relaunch. Accepted capture: [PR13](https://github.com/Edge916/The-Ultimate-Borderlands/pull/13),
commit `65e3f5f5148d734bdd50e9d72e35fab4944de1ae`.

The result is **PARTIAL / UNAVAILABLE**, not COMPLETE or an effect-readiness
pass. Two calls at lines65–82 and83–100 each contain the same15 metadata rows,
FINAL points=(1,0), ranks=(0,0,0) and END coverage=UNAVAILABLE. ActivateSkill
and DeactivateSkill were unavailable in the selected controller-class lookup;
this does not establish absence elsewhere or identify a lifecycle event.

## Actual descriptor evidence

| Target | Recorded metadata | Limit |
| --- | --- | --- |
| Controller | WillowGame.WillowPlayerController, seven-node COMPLETE ancestry | Runtime SDK type/identity/link checks; offline parser only checks text consistency |
| GetSkillManager | WillowGame.WillowPlayerController:GetSkillManager; flags132097, NumParams1, ParmsSize4, ReturnValue offset0 / flags1408 / ZObjectProperty | Signature=NOT_ESTABLISHED; function was not invoked by item4 |
| Manager | Return descriptor declares WillowGame.SkillEffectManager; three-node COMPLETE ancestry | No manager instance read and no lifecycle owner established |
| ActiveSkills | Manager-owned ZArrayProperty offset408, size12, flags4194304, dimension1; ZObjectProperty inner declares WillowGame.Skill | No array payload, summon identity or lifetime observed |
| Skill | WillowGame.Skill, two-node COMPLETE ancestry | No active skill instance read |
| Duration / DurationBaseValue | ZFloatAttributeProperty, offsets120/124, size4, flags8192/2 | Descriptor metadata only; native values and Attribute semantics unread |
| ActivatedTime | ZFloatProperty offset164, size4, flags8192 | Clock semantics and lifecycle timing unestablished |
| SkillInstigator | ZObjectProperty offset180, size4, flags0, declared Engine.Controller | No live instigator payload or ownership proof for a summon |
| Definition | ZObjectProperty offset64, size4, flags0, declares WillowGame.SkillDefinition; three-node COMPLETE ancestry | Current owned definitions passed runtime class checks; no live summon association |
| DurationModifierStack | ZArrayProperty offset128, size12, flags4202498, ZObjectProperty inner | Payload, emptiness and modifier semantics unread |

All seven selected fields and four class roots had COMPLETE descriptor coverage.
The two unavailable function rows make each overall collection UNAVAILABLE.
There were no CAPPED or ABORT/REFUSED metadata calls, malformed rows, traceback
or recorded cleanup failure. Unknown function metadata remains a useful finding.

## State, cleanup and independent capture checks

Runtime lines30/35 reported listen_host with exactly one owned local player and
one owned PRI roster member. Lines32/36/45 reported one inert grade-zero node
among39 runtime skills and both originals present. The per-call initial comparison
baseline is internal, not logged: FINAL unchanged_from_start=True is a runtime
assertion, not an independently reconstructed before/after comparison.
Each END asserts observers_added=0 / native_calls=0 / writes=0 for item4.
The separate armed initialization performed its established native-array writes.

CANCEL lines123/124 verified skills=[MorePep,Myelin], cells=[True,False,True]
and NATIVE ARRAYS RESTORED. Post-last-call STATE/UI/UPGRADE/INITNODE cleanup
lines101/112/114/122 and126/137/139/147 all reported zero. The owner confirmed
CANCEL and full exit. Read-only process queries independently found zero BL2
processes immediately before and after preservation; no before-test observation
or agent observation of the UI title was made.

The complete log is32,788 bytes /148 lines, ends in a newline, SHA256
`8ddbb6aeae5d96be14879adf69fd21c6a7a1fcdbd3e55ec5f4199b2f943f520a`.
Source reads before/after copying were stable. Each installed file equals both
the accepted source and the original three-file ZIP (CRC/layout verified).
Original v12 ZIP SHA256 is
`4f49bad17d0e7d3e97b24f1dfdcb7f396eef2f8a8c6d93464054edf512aaefc6`.
Runtime SHA256 is `41fd2dd9e22bcfa64fbddfc19b881f6950362656e047b212b00eb86f33a01f73`;
pyproject SHA256 is `fa8acf733ef82a19371fc89b6d0cfb37e690ce2aca704ec1479cf01a9efae40e`.
The tested README remains frozen at `5e0b3441243818c4bf161c889f643ec09132ae1e6acbf2addb5162b8b8edec7f`.

Requested one item4 inspection; actual log contains two. Second ARM was refused
because already armed, and repeated CANCEL found no patch to restore. Preserve
these deviations. No test repetition is needed to force COMPLETE coverage.

## Reproduced offline checks and next decision

`python -B scripts/review_deathtrap_metadata_log.py evidence/v032_user_test.log`
returns **PARTIAL / exit1**, as expected. Its observable report matches the
capture manifest, including both unavailable rows and successful cleanup. Parser
success cannot reexecute SDK identity/link checks, authenticate origin or prove
installation/exit; the independent capture provides the latter machine evidence.
Runtime/pyproject/versioned ZIP/log/manifest/snapshots and all historical originals
stay unchanged. Only documentation and the default ZIP's README change here.

The accepted static inventory pins the prepared-e32 current fingerprints.
`verify_artifact_inventory.py` checks immutable originals; `--check-current`
should flag exactly the intentionally updated README/default ZIP. Their new
current equality is checked separately by `verify_package.py`; do not rewrite
the historical inventory or claim the explicit current check passed.

Next: design a bounded metadata-owner correction using the actual returned
SkillEffectManager class, then determine whether a new metadata-only diagnostic
is sufficiently specified. The v12 runtime queried all three selected functions
on the controller; no manager activation/deactivation descriptor was inspected.
Names are search candidates only. Require actual typed descriptor owner/path/
lookup/link/schema evidence before accepting another target; never guess a hook
path, call GetSkillManager/ActivateSkill/DeactivateSkill or add passive observers
on the basis of these rows. Natural lifecycle, native reference lifetime,
rank-one gating and +15-second effect readiness remain NOT_READY.

Actual checks: stable/exclusive capture, snapshot/package/source bytes, fresh CLI,
immutable fingerprints, exact documentation scope, UTF8/links, default package
CRC/layout/source/syntax and isolated import with inert SDK mocks. The unchanged
401-test suite was not repeated for documentation-only changes. No installed
SDK import, game launch/install, save/private-backup access, purchase, summon,
manual boost, native effect, co-op, merge or release was performed by the agent.
