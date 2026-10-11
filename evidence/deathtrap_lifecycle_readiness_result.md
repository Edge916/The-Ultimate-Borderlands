# v0.2.13 metadata capture: lifecycle and effect readiness

**Decision: NOT_READY for passive lifecycle implementation or native effect
design.** The accepted capture resolves the function-owner lookup. It does not
supply natural activation events, live Deathtrap values, instance lifetime or a
safe duration-write interval. The next bounded work is a metadata parameter
schema design. No repeat of this completed test is needed.

Reviewed cumulative base: `9a2ed31064b0a8873e1a21551e3c4d8a6df689cf`
([capture PR #17](https://github.com/Edge916/The-Ultimate-Borderlands/pull/17)).
The reviewed runtime is `ea70391413a06ef33fd2deb16a030fccd01734e0`
([implementation PR #16](https://github.com/Edge916/The-Ultimate-Borderlands/pull/16)).
These are shared draft branches, not merged releases. The
[checks](deathtrap_lifecycle_readiness_checks.json) pin actual inputs, source
ranges, function descriptors, SDK source hashes and checks performed.

## What the actual capture establishes

The [raw log](deathtrap_manager_metadata_user_test.log), lines 65–82 and 83–100,
contains two identical COMPLETE collections, each with four class roots, three
function descriptors, seven fields and one discovery row. Fresh offline review
returns `COMPLETE_LOG_TEXT`, exit 0, and equals the report in the
[capture manifest](deathtrap_manager_metadata_capture_manifest.json).

GetSkillManager is declared on WillowGame.WillowPlayerController. Its typed
return descriptor supplies WillowGame.SkillEffectManager. ActivateSkill and
DeactivateSkill are found on that manager class, resolving the v12 controller
lookup gap. Actual descriptor numbers are:

| Function | NumParams / ParamsSize | Return metadata |
| --- | --- | --- |
| GetSkillManager | 1 / 4 | ZObjectProperty, offset 0; declared manager class |
| ActivateSkill | 6 / 32 | ZBoolProperty ReturnValue, offset 28 |
| DeactivateSkill | 3 / 12 | No selected return; ReturnValueOffset 65535 |

ActivateSkill lists SkillInstigator, Definition, AdditionalSkillTarget,
SkillGrade, StateChangeDelegate and ReturnValue. DeactivateSkill lists
SkillInstigator, Definition and bIgnoreSkillInstigator. Those counts include
the return property where present; they are not an invocation recipe. All
three rows explicitly say `signature=NOT_ESTABLISHED`. Object-parameter
PropertyClass paths and Boolean masks are not emitted. A metadata Boolean
return does not prove a successful natural activation or its gameplay meaning.

ActiveSkills declares Skill as its object-array element class. The Skill fields
are Duration, DurationBaseValue, ActivatedTime, SkillInstigator, Definition and
DurationModifierStack. Duration/base descriptors are ZFloatAttributeProperty;
their compatible descriptor type does not establish live numeric payloads.
SkillInstigator declares Engine.Controller; Definition declares SkillDefinition
and matches the three owned tree definitions' classes. No manager instance or
active-skill payload is acquired by this inspector.

Lines 30/35 record sole-owned local/roster players in a named listen-host
session. Lines 32/36/45 record inert insertion, one registered node among 39
skills, both originals present and node grade zero. FINAL points `(1,0)` and
ranks `(0,0,0)` assert equality to an internal start state that is not logged;
the parser cannot reconstruct that comparison independently.

Lines 123–124 record native arrays restored to MorePep/Myelin and cells
`[True, False, True]`. All four observer families report zero after the last
collection, with no cleanup error. The manifest records independent process
count zero before and after preservation and stable log/installed-file reads.
The three installed snapshot files exactly match reviewed source and the
original v13 ZIP. These checks establish preservation and this test's cleanup;
they do not establish a future owned-duration rollback.

The owner reported completion of the explicit eight-step main-menu → Continue
→ in-map inspection → CANCEL → full-exit protocol. The agent did not observe
the UI title or the machine before the test, and no separate visible-failure
report was supplied. Two inspections instead of one, a second ARM refused as
already armed, and repeated CANCEL are retained without a causal guess.

## Compare with the actual model and runtime

The [SDK-free model](../design/overclock_effect_contract_model.py) consumes
immutable observations and emits proposed actions as data. Its exact tokens,
verified unique membership, quiescence and monotonic generation are hypothetical
adapter facts. Python `is` in this model is not a native-wrapper identity policy.
The [identity/cleanup contract](../docs/overclock_identity_cleanup_contract.md)
requires independent native evidence for each of those facts.

The current runtime's `_upgrade_state` still requires Overclock rank **zero**.
It is preserved as the diagnostic guard and cannot serve as a rank-one effect
gate. The old manual `find_live` calls GetSkillManager and selects the first
name match; `signature` stores names and unchecked ActivatedTime. `apply` does
not check Overclock rank. Manual `restore` is separate: CANCEL/shutdown remove
observers and restore node arrays without calling it. Prior research's
same-name, replacement and missing-time counterexamples are inert code probes,
not observed engine incidents. The new capture does not resolve them.

The four pinned SDK sources were inspected as text with fresh hash checks.
POST is limited to calls allowed to run; POST_UNCONDITIONAL may also follow a
blocked call. Callback order is unspecified. Copied argument ReturnValue is
not native return proof, and callback ret can reflect another hook's override.
BoundFunction's call operator invokes native code. These API facts constrain
later design; no hook or native invocation was performed here.

| Missing prerequisite | Bounded next result needed |
| --- | --- |
| Parameter type relationships | Design a metadata-only extension to report revalidated declared classes for the observed object parameters, with strict versioned parser/mocks and explicit unavailable coverage. Do not read callback payloads or guess a Boolean mask/signature. |
| Natural lifecycle and ownership | After sufficient schema evidence, separately design a passive observation protocol using discovered canonical owners, actual phase/return limits and exact current manager/controller/definition membership. New runtime/test authorization remains separate. |
| Native identity and lifetime | Establish supported reference comparison, liveness, replacement/address reuse and a verified generation source; names/time/array absence are insufficient. |
| Clock and write phase | Establish ActivatedTime units, fresh Duration/base/modifier payloads and when the engine consumes them. Metadata offsets prove no safe write window. |
| Purchased-node gate | Separately validate a unique owned Overclock entry and exact rank one, without relaxing the grade-zero inspector or confusing Deathtrap Grade with Overclock rank. No repeat purchase is requested. |
| Duration cleanup and behavior | Design pending-before-write, exact original-instance cleanup, conflict preservation and inert retries; later separately approved native checks and lifespan evidence are required. |

Existing effect implementation/capture tasks must remain unclaimed while these
prerequisites are unresolved. Completing this review is a documented NOT_READY
decision, not approval for gameplay writes. Preserve existing dependencies and
record narrower prerequisite tasks rather than bypassing the effect gate.

## Actual checks and limits

Fresh targeted suites passed **83 tests**: 36 SDK-free model transitions and
47 inert metadata guards, zero failures/errors/skips. The fake SDK fixtures
poison instance payloads, native wrappers, gameplay writes and hook APIs. Their
success verifies Python behavior in those fixtures only.

All 160 accepted base files remain byte-identical to their Git blobs. Fresh
parser/manifest comparison, original v13 ZIP CRC/three-file layout/source/
snapshot equality, runtime syntax, model import AST, preserved rank-zero gate
and separate manual cleanup checks passed. Immutable inventory verified 53
files, 12 prior archives and five relationships; v13 is checked separately.
The static inventory's old current fingerprints remain historical and are not
rewritten to conceal intentional version drift.

Only this result and its JSON checks are added. The unchanged full 420-test
suite and hosted CI were not repeated. No SDK stub was executed, imported or
packaged. No new game test, installation, summon, observer, native invocation,
duration write, purchase/respec, save/private-backup access, persistence,
co-op, merge or release occurred.
