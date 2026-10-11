# Review the prepared v0.2.12 metadata diagnostic

Current prepared build is v0.2.12 - DEATHTRAP METADATA. Last game-tested build
remains v0.2.11. The new diagnostic has not been installed or run in the game.
Read the [implementation plan](../evidence/deathtrap_metadata_diagnostic_plan.md)
and [actual checks](../evidence/deathtrap_metadata_diagnostic_checks.json), actual
runtime/tests and shared review notes before accepting the submitted task.

Button4 performs one synchronous collection of loaded metadata. The guarded
controller's actual UClass supplies typed GetSkillManager/ActivateSkill/
DeactivateSkill descriptors. A typed return class and ActiveSkills array-inner
descriptor can supply manager and skill class roots; Definition's declared
class is compared with the owned definitions. No manager/active-skill instance
or payload is read. All84 old functions and their guards remain AST-identical.

Hard bounds: four target class roots, seven allowlisted fields, three selected
functions, 16 property descriptors plus one cap read per function and eight
ancestry nodes per target; zero global function enumeration. Capture/recheck
real SDK types, owner/class/parent/property links, lookup identity, bounded
numeric metadata, canonical names/paths and unchanged current state before END.
COMPLETE means selected metadata coverage only. CAPPED/UNAVAILABLE remain
partial; REFUSED reports invalid or drifting state/schema. No callable
signature, parameter semantics, natural lifecycle timing or effect is proven.

Review task659a5e78 using actual code and checks after submission. Any authorized
participant may review, including a separately labeled self-review. Every
completion needs a current version and review note; dependencies and scope
reservations remain intact. Review is separate from writing/testing the patch.

Only after review and separate manual-test authorization should a new bounded
test/capture task be claimed. Prepare an exact build/title/protocol and preserve
the actual complete log and installed snapshot under new exclusive paths.
Do not install or launch the game in this implementation task. Unknown engine
metadata should guide the next bounded investigation; do not guess classes or
loosen guards to make the diagnostic complete. Lifecycle observation/effects
still require their own evidence and design.

The [v0.2.11 result](../evidence/v031_live_attribute_class_result.md),
[log](../evidence/v031_user_test.log) and
[manifest](../evidence/v031_capture_manifest.json) remain immutable. Two calls,
second ARM refusal and repeated CANCEL are documented honestly. SDK identity
comes from runtime class/link checks; parser success supplies text consistency.
Machine installation/exit observations are separate. No repeat is needed.

The accepted [readiness research](../evidence/overclock_effect_readiness_research.md)
and its checks remain unchanged. Manual duration helpers remain independent;
cancel/disable does not call manual restore. Earlier reported purchase1/1 is
separate UI evidence, not a transaction/save/effect audit. Preserve44 prior
protected files, original v0.2.11 ZIP, capture5files and research2files. No
private-backup operations, purchases, points/grades/saves, automatic effects,
co-op, release or upstream merge.
