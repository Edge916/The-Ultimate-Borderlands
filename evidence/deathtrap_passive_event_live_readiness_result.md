# v0.2.15 passive event capture: readiness decision

**NOT_READY_FOR_NATIVE_EFFECT_DESIGN. READY_FOR_ADAPTER_EVIDENCE_RESEARCH.**
The completed run supports the observer's setup, explicit stop and cleanup
path in this one owner test. No accepting callback attempt was recorded.
Natural manager entry, owned Deathtrap lifecycle, native lifetime and the
purchased-node effect remain unverified. Keep the original effect task gated.

Accepted capture: `13b030b613753da8100bdd2494fc3a16ddeb82d7` /
[draft PR #26](https://github.com/Edge916/The-Ultimate-Borderlands/pull/26).
Runtime: `e197266ebb88e71f5cbf855289dcea283f8f93ea` /
[PR #24](https://github.com/Edge916/The-Ultimate-Borderlands/pull/24).
Strict reviewer: `c8dbb53b926326f904736dc81415d0ea5793cdd0` /
[PR #25](https://github.com/Edge916/The-Ultimate-Borderlands/pull/25).
These are accepted draft branches, not merged releases. The
[checks](deathtrap_passive_event_live_readiness_checks.json) pin the actual
inputs, source ranges and fresh artifact checks for this assessment.

## What was observed

The preserved [raw log](deathtrap_passive_event_user_test.log) contains
97 lines / 17,205 bytes, SHA-256
`3c1de714692827194df6881ebb01ecfcf3273a02e9cd825b420efc6210b3c402`.
Fresh strict CLI review is `COMPLETE_LOG_TEXT`, exit 0, with no issues; the
entire JSON result equals the [capture manifest](deathtrap_passive_event_capture_manifest.json).

| Log lines | Actual text evidence | Limit of the conclusion |
| --- | --- | --- |
| 24-28 | ARM succeeded; second ARM refused as already armed. | Reason for the second activation is unknown; exact operator clicks were not observed. |
| 29-36, 64 | Solo listen-host checks, inert grade-zero native insertion/runtime registration and initialization observers zero. | Data readback is not independent visible-node or save verification. |
| 65-66 | One START, DeactivateSkill PRE, hooks=1, attribution=NONE; BASELINE points=(1,0), ranks=(0,0,0). | Registration assertions do not demonstrate a natural callback delivery. |
| 67-70 | TIME; FINAL points=(1,0), ranks=(0,0,0) unchanged; STOP has remaining/captured/attempts/reentrant/uncertain/cleanup_failures all zero; NOT_OBSERVED. | This is valid silence, not proof that the native function or skill never ran. |
| 71-72 | Repeated STOP preserves the zero counters and NOT_OBSERVED result. | The log does not independently establish which UI control produced each STOP. |
| 73-94 | All four earlier observer families report zero after the accepting activity. | Hook cleanup is separate from a Duration or save restoration claim. |
| 95-97 | RESTORE result=True, MorePep/Myelin, cells=[True,False,True]; restart reminder. | Native-array restoration does not undo points, saves, cached trees or a prior manual Duration write. |

Unlike the earlier synchronous metadata captures, this run logs its starting
points/ranks as well as its final values. The reviewer can compare the two
text records directly. It still cannot independently reexecute the native
state checks or establish a save history.

The owner explicitly reported `STOP 21, CANCEL 3 and full exit completed`.
Read-only process queries at capture found BL2 absent before and after copying.
The raw log and all three installed project files were stable across double
reads and after copy, including hash, length and modification time. Installed
files, preserved snapshots, reviewed source and original v15 ZIP are byte
identical. The original ZIP passes CRC and its exact three-file layout.
These are retained capture provenance checks, not new game observations here.

## TIME and protocol deviations

The SDK log header timestamps from START65 to LIMIT67 differ by 44.228 seconds.
The protocol requested staying in place for about 20 seconds. This observation
is retained without treating it as an exact owner wait or an engine clock.
Menu navigation, the operator's timing and SDK logging latency were not
independently observed.

The actual runtime uses Python monotonic time and evaluates the 30-second
bound on callbacks or explicit controls. STOP checks the elapsed time and can
emit TIME. There is no background timer. With attempts=0 in this run, TIME at
STOP is consistent with that implementation; it does not demonstrate an
automatic stop at precisely 30 seconds, a lost callback or a timer defect.
No timer or runtime change follows from this result.

The refused second ARM remains a protocol deviation. The agent did not observe
the UI title, clicks, before-test state or the waiting interval. A separate
visible-failure report was not supplied; do not infer that none occurred.
The new capture manifest's initial START summary counter searched the wrong
header. It was corrected from the unchanged raw log and strict reviewer before
commit/publication, with its initial fingerprint and correction recorded.
Neither the raw log nor the installed snapshots was changed.

## What the actual source permits us to conclude

The [runtime](../sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py)
registers one verified void-return DeactivateSkill PRE path. START derives the
manager class from the loaded GetSkillManager return descriptor, without
calling that function or obtaining a manager instance. Metadata and session
guards revalidate the already captured controller/tree/definition context.
They do not identify the callback's manager, instigator or skill.

The callback's obj, args, ret and func parameters are unused: no loads of those
names occur in its AST. It returns exact None. A fresh AST check also confirms
that the observer functions have no GetSkillManager/ActivateSkill/
DeactivateSkill native method calls or Duration assignments. The unchanged
manual `find_live` does invoke GetSkillManager, but it is outside this observer
and supplies no accepted native adapter. Source inspection and poison fixtures
are not proof of real callback marshalling; this run exercised no accepting
callback body.

As described by the accepted [observer design](../docs/deathtrap_passive_event_observer_design.md),
PRE denotes an attempted entry before native execution. Even a future event
would remain unattributed and could be followed by another hook blocking the
call. This capture adds no argument, return, successful deactivation, skill
membership or summon identity information. It supplies no reason to add
activation/POST phases or read Boolean arguments from the existing class
metadata. Installed native-binary/source-commit matching remains unverified.

The diagnostic `_upgrade_state` still requires candidate rank zero and known
unchanged points/ranks/indices. A future purchased-node rank-one gate must be
separate. The application observer epoch prevents stale context reuse; it is
not a native summon generation. The
[SDK-free model](../design/overclock_effect_contract_model.py) receives
hypothetical verified identity, unique membership, generation, quiescence and
liveness facts. Its passing tests cannot manufacture those engine facts.

## Remaining gates and next bounded work

| Needed fact | Current evidence | Decision |
| --- | --- | --- |
| Natural manager entry during an accepting context | No accepting attempts/events in this run. | NOT_OBSERVED; not an absence claim. |
| Exact current manager/instigator/Deathtrap definition and unique active instance | Declared classes and current diagnostic context only; callback payloads deliberately ignored. | NOT_READY. |
| Wrapper comparison, native liveness and lifetime across reads | No live payload interval or verified destruction/recreation semantics. | NOT_READY. |
| Natural summon generation and successful lifecycle transition | No event pairing or native transition observation. | NOT_READY. |
| ActivatedTime units, Duration consumption and safe write/readback interval | Metadata only; monotonic observer timeout is not an engine skill clock. | NOT_READY. |
| Purchased Overclock rank-one eligibility | Current diagnostic is grade zero; earlier user purchase report is separate. | NOT_READY for native effect gate. |
| Duration cleanup on the same still-live original | Hook removal/array restore only; manual restore remains separate. | NOT_READY. |

The smallest useful next task is source/API research and an acceptance
specification for an actual native adapter boundary. It must resolve exact
wrapper comparison/liveness semantics, current manager ownership, bounded
unique skill membership, safe payload validation before any value read,
natural-generation evidence and the timing/cleanup interval. Match any source
reasoning to the installed API and explicitly retain unverified binary match.
If those facts cannot be established, record the blocker rather than treating
the hypothetical model or metadata paths as an adapter.

That work should produce a research result and check file only. It must not
add hooks, enumerate instance payloads, call discovered native functions,
mint generations from names/time, relax the grade-zero guard or write gameplay
state. No new game instructions or gameplay permission are supplied here.
A later diagnostic needs its own bounded design, claimed file scopes,
reviewed exact build and explicit owner approval of the new location-specific
protocol. Do not repeat this completed silent run to force events.

Keep the [identity/cleanup contract](../docs/overclock_identity_cleanup_contract.md)
and its unresolved native prerequisites intact. The legacy manual boost's
name/time/first-match discovery remains unchanged; CANCEL/shutdown still do
not invoke manual Duration restore. Neither that path nor zero hooks supplies
the automatic effect's ownership/recovery proof.

## Actual validation

This assessment reran the strict v15 CLI and compared its full report with the
manifest. Fresh checks verify the timeline/counters/cleanup, source AST and
syntax, source/snapshot/original-ZIP identity, all 187 accepted Git blobs and
15 versioned ZIP CRC/layouts, immutable inventory 53/12/5 and frozen complete
v12/v13/v14 reviewer JSON/manifests/snapshot-to-ZIP equality. Local links,
UTF-8/JSON, the exact two new file scopes and bounded known secret/savepath
scans are checked before publication.

No runtime, package, test, model, old log, snapshot or manifest is modified.
The accepted 596-test suite and hosted CI were not repeated for two evidence
files. No installed SDK/stub execution, game test, agent installation/control,
native invocation/payload read, purchase, respec, travel, summon, manual boost,
save/private-backup access, effect, co-op, merge or release occurred.
