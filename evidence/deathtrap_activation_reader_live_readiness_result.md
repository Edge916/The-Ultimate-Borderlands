# Live v0.2.18 activation identifier assessment

**OBSERVED_PRIMITIVE. NOT_READY_FOR_NATIVE_EFFECT_DESIGN.** The completed
activation diagnostic reports the exact identifier `Skill_DeathTrap` with
SAME_WRAPPER/DEATHTRAP_NAME, followed by `UpshotRobot` with
SAME_WRAPPER/OTHER_NAME. This closes the narrower activation identifier coverage
gap. Native manager ownership, unique active membership, summon generation,
liveness, Duration and purchased-node effect prerequisites remain unresolved.
No repeat of this completed test is needed.

Accepted capture is `dffab187ffbf53d6d6b17ac9a6c2b12017b5994d` /
[draft PR 45](https://github.com/Edge916/The-Ultimate-Borderlands/pull/45).
Read the complete [raw log](deathtrap_activation_reader_user_test.log),
[manifest](deathtrap_activation_reader_capture_manifest.json),
[tested source](../archive/tested_runtime/v0.2.18/__init__.py),
[original ZIP](../dist/UltimateVaultHunterDeathtrapBoost_v0.2.18_folder_install.zip)
and [companion checks](deathtrap_activation_reader_live_readiness_checks.json).
Runtime/package is `30af0d1` / PR43; strict reviewer is `8c13d29` / PR44.
These are accepted draft branches, with no merged release.

## Actual recorded result

The complete log is 53 lines / 8,847 bytes, SHA256
`5e10b5e4c6687f3b6abad0175e0d6d5ff7348cac3c8a4ad225753e31838e3d2e`.
The current strict activation reviewer reproduces the entire frozen manifest
report: COMPLETE_LOG_TEXT / exit 0 / zero issues, seven reader records.

| Log line | Observation | Meaning |
| --- | --- | --- |
| 24 | One accepting START, version0.2.18, epoch1, ActivateSkill PRE, hooks1, standalone reader. | One registration assertion; no independent click count. |
| 25 | SAME_WRAPPER/DEATHTRAP_NAME, exact Name Skill_DeathTrap, ordinal1/attempt1, schemaVALID; ops268, stages98,66,36,68. | A supplied definition identifier after the reader's current local-controller checks. |
| 26 | SAME_WRAPPER/OTHER_NAME, exact Name UpshotRobot, ordinal2/attempt2, same valid counts. | A separate filtered identifier; no alias or second-summon inference. |
| 27-30 | Two STOP/OUTCOME pairs, both OBSERVED_PRIMITIVE; remaining0/uncertain0, attempts2/classified2/useful1/filtered1/nulls0, errors/refusals/cleanup failures/reentry0, limitNONE. | Recorded cleanup resolves this reader; repeated pairs are not assigned to individual manual clicks. |
| 31/42/44/52 | STATE/UI/UPGRADE/INIT remaining0. | Other runtime cleanup assertions, separate from independent handle inspection. |
| 53 | DISARMED; no initialization patch to restore. | No ARM/insertion markers; no purchased-rank, point/save or manual-Duration restoration proof. |
| 23 | Deprecated legacy import compatibility warning. | Retained SDK warning; no project ERROR or traceback in the capture. |

There are no reader OVERLAP, refusal, error, time-limit, uncertain-registration,
failed-removal, legacy-reader or unresolved-tail records. No null/foreign-wrapper
branch was observed in this run. One useful and one filtered classification
produce OBSERVED_PRIMITIVE while ownership remains UNESTABLISHED. Absence of an
error record is separate from the owner's visibility report.

SDK headers place the first event 5.173 seconds after START, the first STOP
76.746 seconds after START and the final STOP 82.168 seconds after START. The
two events are four milliseconds apart in those headers. These intervals are
text timestamps, including control and cleanup time. They do not measure
Deathtrap lifetime, engine clock, actual owner wait, summon count or compliance
with the proposed approximately90-second bound. The log does not record natural
deactivation in this activation-only reader.

The owner approved this exact build and one ordinary summon, then reported:
"Deathtrap ended naturally, confirm STOP23/CANCEL3/full exit." Natural end and
the completed controls/exit are explicit owner reports. UI/title verification,
START selection, exact summon count, waiting interval and pre-test state were
not independently observed. A separate visible-failure statement is NOT_REPORTED.
No additional run, replay or summon is authorized by this assessment.

## Source and provenance checks

The capture records stable double reads and source rereads, exclusive full-log
and three-file snapshot creation, and BL2 process count zero before and after
preservation. Those process checks occurred after the owner's run; this
assessment checks their preserved provenance without claiming another process
or installation observation now. The installed snapshot, accepted runtime,
current project source and original v18 ZIP members are byte-identical.
Original ZIP:45,939 bytes, SHA256
`1d7d2f24a45596e9a6faf36128474fd7184e524b692c8cb582bde4f5bf10c5ce`.
Its prepared-build README is frozen, including its original untested wording.

Actual source inspection confirms the fixed ActivateSkill PRE path, complete
six-property schema, five loaded classes and terminating membership probe.
Function/return-descriptor metadata is rechecked around each permitted parameter
getter; the return descriptor is metadata, not the return value. The successful
counts agree with accepted independent inert-access transcripts. Inert tests and
source equality establish the checked program, rather than native input safety.

Only SkillInstigator and the local-match Definition are parameter value getters;
Definition.Name is read once as an exact1..128 ASCII identifier. The matcher
uses only the literal Skill_DeathTrap. The reader does not obtain an asset path
or retain that definition wrapper. Fresh get_pc, controller/Pawn/player-class/
world/PRI and one-entry rosters support the SAME_WRAPPER classification within
the callback. They do not establish that the supplied manager belongs to that
controller or that a particular live active instance was uniquely created.

The callback returns exact non-tuple None, has an epoch-only closure and drops
obj/args/func/ret references before primitive logging. Its state and operation
budget remain bounded:112/80/48/80 stages,total320,64 attempts,24 events and a
120-second limit checked at callback/operation/control boundaries, with no timer.
It reads no Python ret, target, grade or delegate value, Delegate.Signature or
Bool.FieldMask, and makes no new engine UFunction/BoundFunction invocation or
flag/Duration/point/rank/save write. Historical manual functions, grade-zero
guards and CANCEL/disable cleanup are unchanged. CANCEL does not invoke the
separate manual Duration restore.

## SDK boundary remains conditional

The accepted [source audit](../docs/deathtrap_activation_reader_feasibility.md),
[design](../docs/deathtrap_activation_reader_design.md) and
[implementation checks](deathtrap_activation_reader_implementation_checks.json)
remain applicable. Their18 pinned SDK source fingerprints were verified as inert
UTF-8 text. No SDK/stub was imported, executed or compiled; no native binding
simulation is claimed.

The [pinned hook binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/hook.cpp)
can convert an earlier Boolean override before invoking Python. Exact None from
this callback adds no block or override and preserves an existing override.
Other hooks can block or change the original call; PRE entry does not establish
successful activation. Same-phase ordering supplies no outcome guarantee.

The [ProcessEvent argument copy](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/wrappers/wrapped_struct.cpp)
filters on PARAM; ReturnValue flags1408 contain PARAM0x80 and RETURN0x400. This
route can copy return/target/grade/delegate cells before Python guards. The
[CallFunction argument extractor](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/unreal/structs/fframe.cpp)
skips return properties but steps argument expressions before PRE. Wrapper
conversion and metadata/helper internals also fall outside the Python meter.
Ignoring Python fields cannot suppress or protect that earlier native work.

The full current [SDK97 discussion](https://github.com/bl-sdk/pyunrealsdk/issues/97)
was read through all API pages and remains closed/completed with one unchanged
[contributor reply](https://github.com/bl-sdk/pyunrealsdk/issues/97#issuecomment-6108546422).
Its hook-time VM/GC guidance does not make Python references preserve native
lifetime outside the hook, or certify already-invalid pointers, arbitrary
destruction, generation, game-thread affinity or installed binary/build/configuration
identity. The GIL is not an ownership or native lifetime lease. No outgoing
support message is proposed or sent. Startup version/hash prefixes agree with
the pinned context; source-to-installed-native-binary equivalence remains unchecked.

## Remaining prerequisites and next bounded question

| Requirement | V18 evidence | Decision |
| --- | --- | --- |
| Natural attempted activation and exact simple identifier | Skill_DeathTrap then UpshotRobot, source/grammar/provenance agree. | OBSERVED_PRIMITIVE within diagnostic limits. |
| Defined asset and successful owned Deathtrap lifecycle | No asset path, return outcome, live active instance or deactivation observation. | NOT_ESTABLISHED. |
| Controller-to-manager attribution and unique active membership | Manager class/function and supplied local-instigator wrapper assertions only. | NOT_READY. |
| Native allocation generation and later liveness | Observer epoch and Name are neither native serial nor lifetime lease. | NOT_READY. |
| Engine clock, Duration consumption and safe interval | No relevant engine timing or active Duration values read. | NOT_READY. |
| Purchased Overclock rank-one eligibility | No fresh point/rank/tree-entry gate in this reader. | NOT_READY. |
| Exact-original write/readback/restoration | Read-only reader hook cleanup; no new effect write or native cleanup proof. | NOT_READY. |
| Native adapter and purchased-node +15-second effect | Required native prerequisites remain incomplete. | NOT_READY_FOR_NATIVE_EFFECT_DESIGN. |

Preserve the [identity/cleanup contract](../docs/overclock_identity_cleanup_contract.md)
and all original effect-task dependencies. V17's sole UpshotRobot deactivation
observation and V16's omitted Name remain unchanged. V18 does not recover the old
identifier or show that UpshotRobot is an alias for Skill_DeathTrap.

The next supportable work is an **inert feasibility audit of callback-local
controller-to-manager attribution**, based on the now-observed literal activation
entry. Inventory only already-preserved reflected game metadata, installed text
stubs and versioned public SDK sources. Determine whether an actual declared
read-only relationship can connect the supplied manager to the validated local
instigator within this callback, with precise access, identity and lifetime limits.
Do not invent a new property/path or call GetSkillManager from a remembered name.
Class identity alone is insufficient.

If no evidenced relationship exists, report that metadata gap. Any proposed
additional sampling requires a separate bounded design, implementation/tests/
reviewer and exact owner approval. No ownership reader, additional field read,
ActiveSkills traversal, manager/skill native invocation, flag/Duration write,
retained wrapper or new owner test is authorized here. Even an attributed manager
would still require unique active membership, generation/liveness and every
remaining effect gate. This audit question is prospective work, not an adapter
design approval or a promise that such a route is available.

## Actual validation and publication

Fresh full v18 CLI/manifest equality, exact counters/Names/line/timestamp checks,
source AST/getter/closure/None/payload-drop and manual/grade-zero invariance,
244 accepted base Git blobs,18 original ZIP CRC/layouts, seven entire frozen
v12-v18 reports/snapshot relationships and immutable53/12/5 inventory pass.
Project syntax only, UTF-8/JSON, source fingerprints, local/primary links,
exact-two-file scope/whitespace and bounded credential/private-path scans are
recorded in the companion checks. The unchanged accepted877 tests and hosted CI
were not rerun for two evidence files.

No new raw game log, SDK source copy, runtime/package/current-document repair,
installation/game/save/private-backup access, purchase/summon, native invocation/
flag/Duration/effect, support message, merge or release occurs. These two new
assessment files require their own exact public approval and deliberate review;
the five-file capture approval was fulfilled by PR45.
