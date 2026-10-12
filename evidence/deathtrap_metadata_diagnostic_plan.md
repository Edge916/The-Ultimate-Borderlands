# v0.2.12 Deathtrap metadata diagnostic plan

Task 659a5e78 is claimed by Jake on `codex/jake-deathtrap-metadata-v0212`.
Integration base `ced4ed2950611f1e9b9aaa64d8941b45a1f19681` combines accepted
documentation `cb1eac9` with accepted research `f8aa2fe`. The documentation
correction was deliberately reviewed after submission, under the updated
workflow; its self-review is recorded at shared sequence85. All dependencies
are complete. Existing originals and accepted research/capture remain immutable.

## Discovery and hard bounds

Use the current guarded controller's actual SDK `UObject.Class` as the first
loaded `UClass` root. Use documented `UStruct._find` for the three inventory
suggestions GetSkillManager, ActivateSkill and DeactivateSkill on that class.
Never access/call the controller's corresponding bound methods. A returned
descriptor must be an actual SDK `UFunction` with a declaring owner on the
validated controller class ancestry and a canonical owner/name path.

Inspect at most 16 properties per function, plus one uninspected lookahead.
Use `_find_return_param` for the descriptor reference; inspect its metadata
only if it is among those 16 captured properties. A capped function cannot
establish complete return coverage or a callable signature. Capture exact
bounded FunctionFlags, NumParams, ParamsSize and ReturnValueOffset; these
labels alone never validate parameter semantics or lifecycle behavior.

Only a typed ObjectProperty return descriptor of GetSkillManager may supply
the manager class. Inspect its ActiveSkills ArrayProperty and typed
ObjectProperty inner to obtain a loaded skill class. Inspect only Duration,
DurationBaseValue, ActivatedTime (FloatProperty), SkillInstigator and Definition
(ObjectProperty), and DurationModifierStack (ArrayProperty) descriptors there.
Definition's declared class is the optional fourth target class; no instance
values or further definition fields are inspected. Instigator's declared class
must be on the controller ancestry; this proves a descriptor relationship,
not a live summon owner. Do not find, summon or query an active skill.

Maximum four target roots, seven allowlisted fields, three function descriptors,
16 properties plus one cap read per function, and eight ancestry links per root.
Targeted lookup eliminates the proposed global scan: zero loaded functions
enumerated globally. Each target's ancestry must be typed, bounded and acyclic;
capped ancestry remains CAPPED. Descriptor owners must be actual captured
class/function references. Array-inner ownership must refer to its actual array
descriptor or declaring class; unknown ownership refuses. Numeric metadata is
exact int (never bool), with flags below 2**64, offsets/property sizes bounded
by 1 MiB, dimensions 1 for class fields (1..64 for raw function metadata),
element sizes 1..65536, and function sizes/counts bounded by their SDK ranges.
Class fields reject parameter/out/return flags. Labels are exact ASCII strings,
names at most96 and SDK paths at most384, with canonical class/function paths.

Revalidate every captured descriptor, lookup, identity, numeric/schema value,
class/parent/declared-class link and the guarded current state before emitting
the buffered metadata result. Missing lookup/getter is UNAVAILABLE, malformed
types/ownership/cycles/drift is REFUSED, truncated enumeration is CAPPED, and
only fully checked metadata is COMPLETE. None of these authorizes gameplay or
a callable signature. A successful final sample is required before END, even
for partial results. No unknown-as-zero, fallback path or inferred absence.

## Runtime and review boundaries

One explicit synchronous button4 call. Keep `_upgrade_state` and all84 existing
functions AST-identical, including historical labels, manual duration helpers,
exact-class Attribute guard, insertion/rollback and cleanup. Use its unchanged
owned solo Gaige/tree/pawn/world/PRI/inert-rank0/native-patch guard at entry,
during reflection and at final comparison. Refuse armed/pending/failed observers
both before and during collection. Context, captured rows and revalidation
ledger are local to the call; no persistent state, observer, timer or game write.

Factory title/version and button4 route/label advance to v0.2.12 - DEATHTRAP
METADATA. Total19 options remains. Preserve the historical inspector helper;
update only the two existing factory-version assertions and button4 assertion.
Add meaningful new cases in `tests/test_deathtrap_readiness.py`. Poison native
queries/bound wrappers, formatters, payload getters, constructors, package loads,
hook APIs and write operations. Test typed schema/owners, invalid numerics,
cycles/caps/missing descriptors, reference/session drift, rank/points/inertness,
foreign ownership/extra rosters and overlapping failed observers. Run all unique
existing236 tests plus new cases; syntax, AST and immutable-hash proofs; exact
three-file package/current-source/CRC/inert isolated import checks. Create the
new v0.2.12 ZIP exclusively. No installed files or game process will be touched.

Last game-tested version remains v0.2.11; v0.2.12 is an offline-verified prepared
diagnostic until a separately authorized manual test. Submit tested exact code
links and handoff, then perform a separate recorded review by an authorized
participant (including labeled self-review). No purchase, duration effect,
native invocation, save/private-backup operation, co-op, release or upstream merge.

## SDK evidence

Installed SDK stubs were read as text only. Pinned pyunrealsdk commit
`c72c5558473bfa1f1cbc9c9113efb2a02251e656` documents the reflection methods in
[uobject_children.cpp](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/uobject_children.cpp)
(27186bytes, SHA25628624b87860aec2b37af221ea5a54bf63eb1ca0d2e91d11d06a2f5c00d7a5ac1).
The [bound-function binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/unreal_bindings/bound_function.cpp)
separates descriptor references from the native call operator; no bound wrapper
is needed here. Generic SDK documentation does not prove any BL2 field schema,
loaded manager/skill class, lifecycle signature/timing or effect.
