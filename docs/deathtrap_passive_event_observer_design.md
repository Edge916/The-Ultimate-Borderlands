# Bounded manager-entry observer design

**Decision: READY_FOR_PASSIVE_EVENT_IMPLEMENTATION for one manually enabled
DeactivateSkill PRE observer only.** This design records an attempted entry
at a verified canonical path. All events are UNATTRIBUTED_MANAGER_EVENT.
It does not read callback payloads, identify a Deathtrap or prove native
execution, duration or successful deactivation. Activation and every POST
phase remain excluded. Implementation must pass the acceptance below before
review; a game test still needs explicit approval of the exact reviewed build.

Reviewed base `d69904a7c74b763d88326a40c0611cd6fc0c3ba9` /
[readiness PR #22](https://github.com/Edge916/The-Ultimate-Borderlands/pull/22).
Read the actual [assessment](../evidence/deathtrap_parameter_schema_readiness_result.md),
[capture](../evidence/deathtrap_parameter_metadata_capture_manifest.json) and
[design checks](../evidence/deathtrap_passive_event_observer_design_checks.json).
This change adds two design/check files; all runtime, tests and packages remain
unchanged. The SDK-free effect model remains a hypothetical ledger contract.

## Target and SDK boundary

Register exactly `WillowGame.SkillEffectManager:DeactivateSkill`, Type.PRE,
under the private identifier `UVH_DT_EVENT_V15_DEACTIVATE_PRE`. No discovery
token matching, global call logging, call injection, function recall, function
load or fallback owner is permitted. The actual descriptor is flags 149506,
NumParams 3, ParamsSize 12 and ReturnValueOffset 65535, with no selected return
property. Its complete property enumeration is:

| Property | SDK type | Flags / offset / dimension / element size | Declared class |
| --- | --- | --- | --- |
| SkillInstigator | ZObjectProperty | 128 / 0 / 1 / 4 | Engine.Controller |
| Definition | ZObjectProperty | 128 / 4 / 1 / 4 | WillowGame.SkillDefinition |
| bIgnoreSkillInstigator | ZBoolProperty | 144 / 8 / 1 / 4 | Not an object-property class |

Use the existing typed metadata helpers to resolve the manager class from the
controller's loaded GetSkillManager **return descriptor**, without calling
GetSkillManager or reading a manager instance. Require the exact canonical
controller and manager class paths, COMPLETE bounded ancestry, correct
declaring owner and the actual function/property metadata above. Inherited,
duplicate, unavailable, capped or changed metadata refuses registration.
Require `_find_return_param()` to remain None and no return-marked property;
the sentinel offset alone is insufficient. Retain only these verified loaded
class/function/property descriptors for bounded revalidation, using the
existing helpers' type/link checks. Do not read manager ActiveSkills or any
skill/target instance field.

Cap preflight at two class roots/eight ancestry entries per root, the two
selected function descriptors, four selected properties in total and 32
captured descriptor checks. The three-parameter target must enumerate exactly
three properties with complete links; no cap lookahead is accepted as coverage.
Revalidation repeats this bounded getter set; never expand it from an event.

The inspected SDK source converts a set return proxy before the Python
callback runs. ActivateSkill has a Boolean return and can have a prior
PRE-hook override; this design deliberately omits that target. For the
verified void DeactivateSkill, the inspected binding ignores attempts to
override a nonexistent return property. PRE starts with no native result.
This removes the return-value interpretation path from the chosen observer.
The Boolean *argument* is never read or interpreted, so this observer does
not need to infer FieldMask. A future payload reader would still require
separate actual field-mask/ownership evidence.

This is an inference from the inspected
[hook contract](https://github.com/bl-sdk/unrealsdk/blob/b1852aa440277afcce8a13566b5487aeae5a7ae9/src/unrealsdk/hook_manager.h)
and [Python binding](https://github.com/bl-sdk/pyunrealsdk/blob/c72c5558473bfa1f1cbc9c9113efb2a02251e656/src/pyunrealsdk/hook.cpp),
not an observed native callback. The installed stub API matches the inspected
interface, but installed native-binary/source-commit matching was not verified.
As with existing observers, execution depends on the SDK providing valid
callback wrappers and hook-registration/removal semantics. The framework
still constructs wrappers/copies; do not claim zero native reads or no
performance impact. The application callback must ignore all four supplied
values, return exact None, and never retain, compare, convert, format or call
obj, args, ret or func. It uses closed primitive labels from registration.
No tuple, Block sentinel or return override is permitted on any branch.

## Entry, current context and overlap

Append two options after the nineteen existing options: item 20 START PASSIVE
MANAGER ENTRY OBSERVER and item 21 STOP / REPORT PASSIVE MANAGER ENTRY
OBSERVER. Proposed version/title: v0.2.15 / UVH v0.2.15 - PASSIVE MANAGER
EVENTS. Enabling the mod registers no new observer. START is explicit and
requires initialization already complete, an owned inert node, loaded Gaige
in the map and no existing/failed observer handles or armed initialization.

Build the same typed current controller/tree/pawn/world/PRI/definition
context used by v14 metadata inspection. Reuse `_deathtrap_session` and
`_upgrade_state` unchanged: known sole local/roster ownership, approved SDK
net modes, exact current Gaige/pawn/tree, unique candidate/original entries,
inert arrays, candidate grade zero, known nonnegative points/ranks/indices
and an exact per-start baseline. Unknown/loading/rank-one/changed state
refuses. This is the existing diagnostic session guard, not new evidence of
callback manager or Deathtrap ownership.

Capture typed preflight metadata and revalidate the exact selected descriptor
getters around every callback's fresh `_deathtrap_session` checks. Compare
primitive points/ranks/indices to the start baseline before committing an
event. Any exception, metadata drift or session change disables observation;
never repair points/ranks or rediscover a replacement. The callback guard
reads only the already reviewed current diagnostic context and selected
loaded descriptors, never callback payloads or manager/skill instance values.
No relaxed `_upgrade_state` or purchased-node gate is introduced.

Make the overlap policy bidirectional through a new option-dispatch wrapper.
Wrap all existing option handlers except CANCEL item 3. While the new context
is active or any owned/uncertain handle remains, those handlers refuse before
calling their original function. This locks ARM, other traces, synchronous
diagnostics, legacy insertion and manual duration actions. In IDLE the
wrapper forwards the original option argument/result exactly. Existing helper
bodies and behavior remain unchanged. STOP item 21 and CANCEL item 3 remain
available. CANCEL invokes the new STOP first, then performs its existing
observer/array cleanup; an inert retained handle must not prevent native-array
restoration. Disable uses the existing shutdown-to-CANCEL path. No manual
duration restore is added or claimed.

The wrapper covers mod option dispatch, not arbitrary calls by other Python
code to old functions. Fresh `_deathtrap_session` checks still detect any
other active observer/initialization context before accepting a new event;
they disable this observer rather than removing another experiment's handles.

## Bounds and event contract

Fixed limits: one hook; 24 recorded events; 64 callback attempts, including
reentrant attempts while accepting; 30.0 seconds measured by finite Python
monotonic time; one event row per accepted attempt; at most 256 UTF-8 bytes
per new observer log line. These limits bound selected operations and memory,
not the wall time of an SDK getter. Time is checked at the next callback or
explicit START/STOP; there is no background timer and no guarantee of automatic
unregistration during silence. Always use STOP after the observation interval.

Store only primitive event counters and closed literals; no per-event native
objects, arbitrary strings, exception messages or timing arrays. Callback
count advances before busy/limit handling. A busy/reentrant callback records
no event and performs no second native guard. Reaching a bound immediately
clears accepting state. If already busy, defer removal to the outer callback's
finally block; it must then discard an uncommitted event. Late/stale callbacks
check a monotonically increasing bounded internal epoch and active context,
return None and perform no native reads/logging. Epoch is an application
context token, not an engine summon generation.

Emit only the following closed grammar (prefix `[UVH-DT-EVENT]`):

```text
START v0.2.15 target=DeactivateSkill phase=PRE attribution=NONE hooks=1
BASELINE points=(P1, P2) ranks=(R0, R1, R2)
EVENT ordinal=N target=DeactivateSkill phase=PRE attribution=NONE
LIMIT reason=EVENTS|ATTEMPTS|TIME
ABORT reason=STATE|METADATA|CLOCK|REGISTRATION|INTERNAL
NOT_STARTED reason=OVERLAP|STATE|METADATA|IDENTIFIER|REGISTRATION|CLOCK
FINAL points=(P1, P2) ranks=(R0, R1, R2) unchanged=True
FINAL UNVERIFIED reason=STATE
REMOVAL_ERROR remaining=1
STOP remaining=N captured=C attempts=A reentrant=S uncertain=U cleanup_failures=F
OUTCOME value=OBSERVED_UNATTRIBUTED|NOT_OBSERVED|REFUSED
```

Use exact nonnegative bounded integers, reject bool-as-int and nonfinite
clock values, and restrict numeric text so every line respects the byte cap.
Points/ranks and the primitive epoch must fit 0 through 2147483647; runtime
indices retain the existing tighter array bounds. An exhausted epoch refuses
START without wrapping. Failure/reentry counters saturate at 2147483647,
retaining the failure finding rather than growing an unbounded list. Require
an exact finite nonnegative float from the monotonic provider, no backward
movement and finite nonnegative elapsed subtraction; otherwise abort CLOCK.
Only primitive numeric values may be formatted; do not log `str(exc)`, names
or object paths from callbacks. The canonical path is fixed in code/checks,
and the event's target token comes from its registration closure. A FINAL
line reports a sampled diagnostic guard comparison, not that the whole
native call or game made no changes. STOP with zero events and successful
cleanup says NOT_OBSERVED. Any unresolved cleanup/abort makes REFUSED and
keeps its history after retries. An event is an attempted manager entry that
could be blocked by another PRE hook; intra-phase order is undefined.
No return value, native success, skill identity or lifespan is inferred.

## Registration and cleanup ledger

START uses a fresh primitive epoch with accepting state None during
registration. Preexisting private identifiers refuse without removal. Only
an exact True `add_hook` result establishes an owned handle. Verify its
presence, finish state/metadata revalidation and publish accepting context
last. A callback arriving during preflight/registration remains inert.

On exact False registration, do not claim/remove an identifier that might
belong to another registrant. If registration raises or returns a non-bool,
record an uncertain marker and keep the attempted closure inert. An ambiguous
present identifier is never removed as owned. STOP may clear that marker
only after exact `has_hook == False`; otherwise it blocks new observation
and reports unresolved uncertainty. Do not assume a thrown registration
made no change. A proven owned registration followed by verification failure
is cleaned using the owned ledger, even if accepting context was never set.

STOP first clears accepting context and increments/invalidates the epoch.
For an active context, attempt one final guard comparison; unavailable state
produces FINAL UNVERIFIED with no repair. Release current-session/metadata
references after that bounded final check; failed cleanup retains only
primitive handle/uncertainty records. Remove only proven owned handles and
verify absence. Return-value success alone is not absence proof. Exceptions,
non-bool results or a still-present hook retain an inert handle. Each explicit
STOP retries at most one owned removal/absence check; no loops or timers.

Failed-removal history survives later successful retry in STOP summaries.
New START is refused until all owned/uncertain handles are cleared. Neither
zero hooks nor native-array rollback proves Duration restoration, refunds,
save undo or cache cleanup. If the API cannot establish safe absence/ownership,
report the unresolved handle and stop; do not remove a foreign identifier or
silently relabel it clean. Full process exit may end the SDK session but is
not a substitute for a verified in-session cleanup claim.

## Implementation acceptance and exact scopes

The following are required meaningful SDK-free cases, not tests run by this
design-only task. Use inert SDK fixtures and objects poisoned for attribute,
equality, bool, str/repr, iteration, hashing and call access. Existing fixture
classes can be reused, but no actual SDK stub may be imported or executed.

| Case group | Required behavior |
| --- | --- |
| Nominal / silence | Valid sole Gaige preflight registers exactly one canonical PRE hook; event uses closed tokens and None return; silence reports NOT_OBSERVED. |
| Payload poison | All four poisonous values remain untouched and unretained for nominal, stale, refused, reentrant, exception and cleanup paths. |
| State refusal / drift | Missing pawn, non-Gaige, extra local/roster, loading/foreign current context, grade one, unknown/bool points, changed ranks/indices/session or inert arrays refuse/abort without repair. |
| Metadata refusal / drift | Foreign class/owner/path, unavailable/capped/duplicate/inherited function, changed flags/size/offset/types/classes/links, unexpected return descriptor or return-marked property refuse/abort. |
| Registration | Foreign identifier collision, exact False, throw-before/after simulated installation, non-bool result, callbacks during add/verify, presence failure and post-registration drift keep acceptance inert and ownership honest. |
| Bounds / reentry | Event 24, attempt 64, timeout/backward/nonfinite/bool clock, nested busy callbacks, limit while busy, stale epoch and queued callback after STOP produce bounded records, None, no repeated guard or commit after disabling. |
| Cleanup | Disable-before-removal, remove false/still present, throw, unknown presence, retry success/history, uncertain foreign handle never removed, repeated STOP and CANCEL/disable integration. |
| Controls / preservation | All nineteen original handlers dispatch identically when idle; active/pending locks block conflicting actions; STOP/CANCEL remain available; raw AST/function behavior preservation and all prior unique tests/package/source/ZIP/inventory checks. |
| Output / packaging | Closed grammar/256-byte rows, exact-int bounds, no raw exception/payload representation, accurate outcome/cleanup history, original v14 parser reports unchanged, inert import with21 options and no automatic new hooks. |

Future implementation scopes must be refined/claimed before any edit:

- `sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py`: append private event
  helpers/constants/option wrapper; add STOP to CANCEL; version/title/options
  factory changes. All other existing function AST and raw bodies, including
  manual duration, `_upgrade_state`, metadata helpers and existing observers,
  remain identical. No metadata item-4 behavior change.
- `sdk_mods/UltimateVaultHunterDeathtrapBoost/pyproject.toml` and `README.txt`:
  version/instructions only; explain unattributed PRE and explicit STOP.
- `tests/test_deathtrap_passive_events.py`: new mock cases above.
  `tests/test_runtime_mock.py`, `tests/test_presentations.py` and
  `tests/test_deathtrap_readiness.py`: only justified title/version/option
  expectations; preserve every established behavior case. Add a meaningful
  explicit idle-versus-locked dispatch and inert import check.
- `evidence/deathtrap_passive_event_implementation_checks.json` and
  `docs/NEXT_CODEX_TASK.md`: actual suite/AST/raw preservation/output/ZIP
  evidence, reviewed package fingerprints and exact future owner protocol.
- `dist/UltimateVaultHunterDeathtrapBoost_folder_install.zip` and a newly
  exclusive `dist/UltimateVaultHunterDeathtrapBoost_v0.2.15_folder_install.zip`:
  exactly the three project files, source-equal/CRC/inert import checked;
  preserve all fourteen original versioned ZIPs and all captured evidence.

No strict natural-event log reviewer or authentic capture is implemented in
this task. Scope those separately before relying on a future log's grammar,
cleanup history and source/install provenance. A future capture may find zero
callbacks; do not force native calls, purchase or summon to fill the log.

## Proposed later owner protocol and remaining gates

These are location-specific instructions for a future reviewed v0.2.15
build, not a request to run them now:

1. Install the exact reviewed project ZIP; start a fresh BL2 process and stay
   at the main menu. Set Offline and select already-backed-up Gaige.
2. At the main menu, verify the exact v0.2.15 MODS title and ARM item 1 once.
3. Select Continue and wait until Gaige is fully loaded into the map.
4. In the map, select START item 20 once. Stay in place, without opening other
   project controls, for about 20 seconds. Do not buy, respec, travel, summon,
   apply a manual boost or start another trace. Silence is acceptable.
5. Still in the map, select STOP / REPORT item 21, then CANCEL / RESTORE item 3.
6. Fully exit to desktop and report STOP, CANCEL and full exit, plus any visible
   failure, before relaunching. Preserve the full stable log/installed files
   and independently check process zero under a separately claimed capture.

Review the exact implemented build and its offline acceptance before asking
for that protocol approval. This observer's purpose is to verify bounded
registration/cleanup and whether the canonical manager entry is naturally
observed in that limited interval. One zero-callback run completes that
question; do not repeat it to chase a positive result. Progress to owned
Deathtrap activation/deactivation, payload reads, lifetime/clock measurement,
rank-one effects or summoning requires separately reviewed evidence and scope.

The original effect design remains NOT_READY. A positive coarse event cannot
supply callback ownership, wrapper lifetime, engine generation, clock units,
safe Duration write/readback, rank-one purchase or lifespan evidence. SDK
framework behavior and cleanup are still untested in game for this new target.

## Actual checks for this design

The companion JSON records fresh input fingerprints, selected source ranges,
typed metadata/source API checks, full parser-manifest equality, unchanged
runtime syntax, all173 base blobs/14 original ZIPs, source/snapshot/v14 package
CRC/layout and historical immutable inventory. Four installed stub/four pinned
source hashes are rechecked as text only. No new runtime/test code exists here,
so the accepted97 targeted tests and448 full suite were not repeated. New
acceptance cases above are specifications, not passing-test claims. No game,
SDK execution/import, hooks, callbacks, gameplay/save/private-backup writes,
purchase, summon, co-op, merge or release ran.
