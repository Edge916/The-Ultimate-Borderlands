# Design the bounded metadata-owner correction

Reviewed game-tested source is v0.2.12 - DEATHTRAP METADATA. Its
[live result](../evidence/v032_live_deathtrap_metadata_result.md),
[raw log](../evidence/v032_user_test.log), [manifest](../evidence/v032_capture_manifest.json)
and exact tested three-file snapshot remain immutable. Accepted capture is
65e3f5f / PR13. Reproduce the offline parser: PARTIAL / exit1 is expected.

Two identical15-row calls captured all four class roots and seven selected
fields. GetSkillManager on WillowPlayerController has a typed return descriptor
declaring SkillEffectManager; ActiveSkills' object-array inner declares Skill.
ActivateSkill and DeactivateSkill were unavailable on the controller. The
current implementation queries all three selected names on that controller;
the manager's activation/deactivation descriptors have not been inspected.
This is a lookup-scope limitation, not proof of absent methods or hook ownership.

Design task26f23ca8 should inspect actual SDK source/documentation and the runtime
typed metadata helpers. Decide whether it can specify a bounded synchronous
lookup of those two candidate names on the already-observed manager class,
without obtaining a manager instance, global function discovery, guessed native
paths, native invocation, payload reads, hooks, timers or writes. Require actual
UClass/UFunction owner/path/lookup/property identity and bounded flags/offsets/
schema/link rechecks. Missing/refused/capped data stays explicit; no fallback
to controller behaviors or same-name functions on unrelated objects.

Keep the owned solo Gaige/tree/session/points/ranks/inert-gradezero guard,
manual prototype, insertion/rollback/cleanup and all original evidence intact.
At most four roots, three selected function lookups, seven fields,16 properties
plus one cap read per function and eight ancestry nodes per root; final state
comparison and overlap refusal remain required. Complete metadata supplies no
callable signature or permission to install lifecycle observers.

Before coding: reviewed design must state exact new version, runtime/test/parser/
documentation/defaultZIP and exclusively created versionedZIP scopes. Refine
the ready implementation task accordingly; preserve dependencies and claim a
separate branch. A NOT_READY design is valid and leaves coding unclaimed until
named prerequisites exist. No future owner test starts solely from queued status.

The completed owner run had two inspections instead of requestedone, a refused
secondARM and repeatedCANCEL. FINAL1/0 and0/0/0 unchanged assertion, native
RESTORE123/124 and all four zero-observer families passed. Independent process
queries0 and installed/originalZIP/source equality are separate capture checks.
Internal start baseline/native SDK checks are not reconstructed by the parser.

Preserve all twelve versioned ZIPs, six tested snapshots, logs/manifest/PNG and
accepted research/model/reviewer artifacts. Current docs/default ZIP README may
change only after exact testedREADME preservation. The accepted static inventory
pins prepared-e32 current bytes; immutable checks pass and explicit current check
flags intentional README/defaultZIP drift. Verify current package/source/CRC/
syntax/inert import separately rather than replacing old hashes to force pass.

Any participant may deliberately review submitted actual work, including labeled
self-review; every completion requires findings and resolved shared defects.
Native lifecycle/lifetime/clock/write timing and a rankone effect gate remain
NOT_READY. No game launch/install/nativeSDK import, private-backup/save access,
purchase/respec/travel/summon/manualboost/othertrace, effect, co-op, merge or release.
