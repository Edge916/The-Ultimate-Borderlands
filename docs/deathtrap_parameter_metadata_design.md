# Bounded function parameter class metadata

Decision: **READY_FOR_PARAMETER_METADATA** in a separately claimed v0.2.14
implementation. Native lifecycle and effect remain **NOT_READY**. This is a
synchronous descriptor design: it adds no observer, manager instance, summon
payload, native invocation or gameplay write.

Accepted base: `71962c87d7475b369dc926ae259bdee974c9ac84`
([readiness PR #18](https://github.com/Edge916/The-Ultimate-Borderlands/pull/18)).
Read the actual [readiness decision](../evidence/deathtrap_lifecycle_readiness_result.md),
[v13 log](../evidence/deathtrap_manager_metadata_user_test.log),
[manifest](../evidence/deathtrap_manager_metadata_capture_manifest.json) and
[runtime](../sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py).
[Design checks](../evidence/deathtrap_parameter_metadata_design_checks.json)
pin these inputs and the actual checks performed.

## Concrete gap and available API

V13 has two complete 15-row collections. The manager owns ActivateSkill and
DeactivateSkill; their object properties are typed SDK descriptors. The current
`_deathtrap_property` captures each ZObjectProperty's actual PropertyClass and
revalidates that reference, but the FUNCTION output omits its declared class
path. Consequently the log supplies argument names/types/flags/offsets without
the controller/definition/target type relationships needed by a later design.

Use only those already selected descriptors. The installed SDK declarations and
pinned reflection bindings expose ZObjectProperty.PropertyClass, UClass.Name,
UClass._path_name(), SuperField and PropertySize. The existing `_deathtrap_class`
validates their typed metadata and canonical bounded labels. There is no need
for a new native lookup API, guessed owner, BoundFunction call or object scan.

ZBoolProperty.FieldMask and ZDelegateProperty.Signature exist in the inspected
SDK text. They are deliberately outside this class-path extension; do not
invent values or traverse their signatures. A later observer design still needs
its own sufficient schema and callback contract. Object-parameter declared
classes do not establish instance ownership, Python argument compatibility,
delegate behavior or return meaning.

## Versioned emitted schema

Proposed name: `UVH v0.2.14 - DEATHTRAP PARAMETER CLASSES`, version `0.2.14`.
Keep 19 options and item4's callback. Keep v13's 15-row order, four root targets,
three selected functions and seven fields. BEGIN uses v0.2.14; FINAL and END
retain the existing grammar and `signature=NOT_ESTABLISHED`.

For an available v14 FUNCTION row, add exactly one key:
`parameter_classes_coverage`. Each enumerated property retains its six existing
keys and adds exactly `declared_class` and `declared_class_coverage`.

| Actual property result | declared_class | declared_class_coverage |
| --- | --- | --- |
| SDK ZObjectProperty (including supported SDK subclasses), typed class header accepted | Actual canonical path, at most 384 characters | COMPLETE |
| Typed object class exists, initial permitted class-header getter unavailable | UNAVAILABLE | UNAVAILABLE |
| Supported SDK property outside the ZObjectProperty hierarchy | NOT_APPLICABLE | NOT_APPLICABLE |

An untyped PropertyClass remains a refusal under the unchanged helper. Invalid
class/name/path/parent/size is ABORT, rather than UNAVAILABLE. Nonobject status
does not assert a callable primitive signature. Only declared object classes
are described; no array-inner/delegate/Boolean metadata or instance values are
added. A missing function retains exactly the old three-key UNAVAILABLE row,
without fabricated property or parameter-class coverage.

Function `coverage` retains its descriptor-enumeration COMPLETE/CAPPED meaning.
`parameter_classes_coverage` is CAPPED whenever enumeration is CAPPED; otherwise
UNAVAILABLE if any sampled object class is unavailable, COMPLETE if at least
one sampled object class is accepted and all applicable classes are accepted,
or NOT_APPLICABLE for a complete enumeration with no object properties. Overall
END retains CAPPED precedence over UNAVAILABLE, now including the additional
class coverage. No false COMPLETE when a class path is unavailable.

For text validation, use an explicit property-tag table derived from the
inspected SDK declarations. Object-derived tags are ZObjectProperty,
ZClassProperty, ZComponentProperty, ZLazyObjectProperty, ZSoftObjectProperty,
ZSoftClassProperty and ZWeakObjectProperty. Known nonobject tags require
NOT_APPLICABLE. Unsupported tags refuse instead of guessing inheritance from
their names. Runtime output must likewise refuse an SDK type tag outside this
fixed supported table. The parser checks consistent text; it cannot reproduce
the runtime isinstance checks or native reference comparisons.

When the primary GetSkillManager return class is COMPLETE, its declared path
must equal manager DISCOVERY.return_class and the manager CLASS root. This
checks the actually selected return property's relation, not a guessed path.
Do not impose guessed Engine.Controller or SkillDefinition classes on candidate
arguments: report their actual accepted metadata. A foreign function owner still
refuses under the existing bounded ancestry checks.

## Revalidation and bounds

Refactor only `inspect_deathtrap_readiness`; keep all ten `_deathtrap_*` helpers,
the field tuple and every other established function unchanged. A nested class
snapshot helper may wrap `_deathtrap_class` as `(COMPLETE, actual_header)` or
`(UNAVAILABLE, None)` for initial LookupError only. Add one captured getter/check
per sampled object property. Rechecking an unavailable snapshot is mandatory:
becoming available, becoming invalid or changing reference/schema aborts before
successful output. Do not discard unavailable checks or silently retry until
successful. Other exceptions follow existing refusal handling.

The property snapshot already retains actual descriptor/PropertyClass identity.
The new class snapshot retains the exact class header/reference and supplies
its actual path; each remains guarded by the unchanged `_deathtrap_session`
and `_deathtrap_check` before/after reflection, output and FINAL/END. Retain
grade-zero ownership/session/point/rank/indices/inert-node checks and overlap
refusal. This is no native wrapper-lifetime policy and no future rank-one gate.

Per collection, keep at most four distinct root classes, eight ancestry nodes
per root, three function targets, seven field targets, sixteen accepted
properties plus one cap lookahead per function, and fifteen metadata rows.
At most 48 new class-header checks increase the captured-check upper bound
from 94 to **142**. No new class ancestry traversal or descriptor enumeration
is introduced. Getter revalidation can repeat calls; these are finite selected
bounds, not a promise of 142 total raw getters or a hard time deadline.

Names remain bounded at 96 characters and paths at 384. The design checks
serialize a conservative size bound using per-field maxima and verify it fits
the existing 16,384-character parser line bound. No unbounded log aggregation, unknown repr,
pointer/address conversion, arbitrary subclass walk, package load, construction,
instance ActiveSkills read, payload field, native function or hook API is allowed.

Missing primary discovery stops dependent lookups. Initial supported metadata
unavailability remains honest; CAPPED does not validate unsampled properties.
Buffered rows are emitted only after all required rechecks. Changing points,
ranks, tree, session or descriptors aborts without repair. Cleanup families,
context-before-removal behavior and retained inert failed handles stay unchanged.

## Offline reviewer and meaningful checks

Extend the reviewer with a separate strict v14 contract and actual runtime hash
pin. Keep v12 and v13 schemas/results unchanged; they reject the new keys. V14
requires them on every available FUNCTION/property, checks the fixed tag table,
coverage/sentinel/path relations, primary return/discovery agreement and overall
END status. Preserve duplicate-key, malformed number, size/line/input, row-order,
owner, return-offset and cleanup-failure history checks. Mixed versions refuse.
Do not upgrade text consistency to signature, SDK identity, log origin, install,
exit, lifecycle, rank-one gate or effect proof.

Preserve the existing 420 unique offline tests. Add cases for all three actual
object-parameter groups; scalar/Boolean/delegate NOT_APPLICABLE; supported SDK
object subclasses; unsupported tags; unavailable/invalid class headers;
same-name changed class reference and class schema/path drift during collection,
rechecks and output; capped enumeration; missing primary; preserved rank-zero
and overlap refusals. Poison payload/native function/discovery/construct/load/
hook/write APIs must remain unused. Class-header getter unavailability later
changing to available must abort, rather than convert a partial result to COMPLETE.

Add strict v14 parser fixtures for complete/partial/capped/refused, missing new
keys, sentinel/coverage/tag contradictions, fake return/discovery classes,
mixed versions and actual cleanup failure even after retry. Reproduce the frozen
v12 PARTIAL/exit1 and v13 COMPLETE_LOG_TEXT/exit0 reports byte-equivalent as JSON.
Passing mocks do not establish real SDK behavior.

Before an owner test: full unique suite, syntax, limited AST/raw-byte proof
(94 of the 95 old top-level functions unchanged), exact three-file package
CRC/layout/source and isolated inert 19-option import. Factory/version/item4
label and pyproject are permitted integration changes. Preserve all 13 original
versioned ZIPs, immutable capture/snapshots/designs and the static inventory;
create v14's ZIP exclusively. Historical current fingerprints may drift; check
new source/package explicitly rather than rewriting them.

## Exact follow-up scopes and user protocol

Implementation task `78df9fea-d295-4ba1-b4b4-38508b990e28` has these twelve paths:

- sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py
- sdk_mods/UltimateVaultHunterDeathtrapBoost/pyproject.toml
- sdk_mods/UltimateVaultHunterDeathtrapBoost/README.txt
- tests/test_deathtrap_readiness.py
- tests/test_runtime_mock.py
- tests/test_presentations.py
- scripts/review_deathtrap_metadata_log.py
- tests/test_deathtrap_metadata_log_review.py
- evidence/deathtrap_parameter_metadata_implementation_checks.json
- docs/NEXT_CODEX_TASK.md
- dist/UltimateVaultHunterDeathtrapBoost_folder_install.zip
- dist/UltimateVaultHunterDeathtrapBoost_v0.2.14_folder_install.zip

Refine its acceptance to this reviewed design and preserve its dependency before
claiming. Capture task `cc1ccb8a-e594-4294-9fa3-512ad8d139c2` reserves only the
new parameter-metadata raw log/manifest and three v0.2.14 installed snapshots.
Pin exact reviewed commit/package/hash/title before explicit owner approval.
The proposed later owner instructions must say where each action occurs:

1. Start a fresh BL2 process and remain at the main menu.
2. At the main menu, set Offline and select the already backed-up Gaige.
3. In MODS, verify the exact approved v0.2.14 title before proceeding.
4. While still at the main menu, select ARM (item 1) once.
5. Select Continue; wait until Gaige is fully loaded into the map.
6. While in the map, open the mod options and inspect item 4 once.
7. While still in the map, select CANCEL / RESTORE (item 3).
8. Fully exit BL2 to the desktop, then report completion before any relaunch.

These are a future proposal, **not a request to run a new test now**. No purchase,
respec, travel, summon, manual boost or other trace belongs in it. Preserve the
authentic log and exact installed snapshot only after completion; refusal or
partial coverage is a valid finding. No repeat to force COMPLETE.

Schema review task `c76fb125-2eb5-4d3a-804d-75b165b0db3c` must inspect actual
new evidence before deciding readiness for a passive observer **design**.
Natural events, native equality/liveness/generation, clock/write interval,
rank-one gate, duration cleanup and lifespan remain later prerequisites.
Existing effect tasks keep their dependencies and actual readiness/authorization
gates. No SDK stub execution/import/package, game install/control, save/private
backup access, gameplay writing, co-op, merge or release is authorized here.

This task changes only this design and its checks JSON. Full 420-suite/hosted CI
and native checks are not rerun for two design files; the companion records
fresh parser/hash/bounds/scope checks and distinguishes prior 83-test evidence.
