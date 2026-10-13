# Proposed owned-summon identity and cleanup contract

**Decision: NOT_READY for native implementation.** This is an offline policy
and a specification for an SDK-free model. No new hook path, signature, wrapper
lifetime, native invocation or gameplay permission is established here.

The accepted integration is db0adbe6379ae218146599a7069bd63c1ed05cc5. Its runtime
is prepared v0.2.12; the last captured game test remains v0.2.11. Read the
[accepted research](../evidence/overclock_effect_readiness_research.md), its
[recorded mock checks](../evidence/overclock_effect_readiness_checks.json), and
the [new design checks](../evidence/overclock_identity_cleanup_design_checks.json).
The old helper functions and grade-zero diagnostic guard remain untouched.

## Actual source findings

Current runtime line references are to
[the preserved source](../sdk_mods/UltimateVaultHunterDeathtrapBoost/__init__.py).
`signature` at 41 returns skill name, unchecked ActivatedTime and instigator
name. `find_live` at 46 invokes GetSkillManager and accepts the first name match
within 64 entries; its instigator check compares names. `apply` at 116 has no
Overclock-rank check. It checks Duration/base near 60 within absolute 0.05,
accessible empty modifiers, and the 180-second cap, writes Duration, then
records only after successful readback. Failed write verification attempts a
rollback before a successful record exists.

`restore` at 169 matches the scalar signature, checks Duration near the owned
after-value, and clears a stale or independently changed record. This avoids
overwriting an independent Duration but does not prove object identity. In
accepted inert probes, a same-name foreign owner was accepted, missing time
was accepted, two candidates selected the first, and a replacement reusing the
signature was restored instead of the original. These are code counterexamples
in mocks, not observed engine incidents.

`cancel_init_node` at 1379 removes observer families and rolls back owned native
arrays. `shutdown` at 3320 calls trace stop and node cancellation. Neither calls
manual `restore`; native array restoration does not restore a manual Duration.
`_upgrade_state` at 1636 requires candidate rank zero and freezes points/ranks.
Keep it unchanged. A future rank-one effect needs a separate gate, and must not
reinterpret active Deathtrap's Grade as the purchased Overclock rank.

## Required adapter evidence, before any effect

The future native adapter must provide freshly validated **exact** current SDK
controller, pawn, world, PRI, tree, manager, active skill and definition
references. A scalar name/path and Python id/address are insufficient. Validate
SDK wrapper/classes, exact instigator-to-controller ownership, uniquely owned
Overclock runtime entry/index/tier and exact Deathtrap definition, the current
Gaige session and both sole-owned-player rosters. Missing, foreign, replaced,
loading or ambiguous data refuses. More than one matching active instance
refuses, even if all names agree. Scan limits refuse incomplete membership.

The adapter must establish reference comparison and native liveness across the
whole read/write/readback interval, including destruction, wrapper recreation
and address reuse. Metadata descriptors alone establish none of this. A
revalidated natural lifecycle event must justify a new summon generation;
names or ActivatedTime alone cannot. Validate ActivatedTime as an exact int or
float, excluding bool, finite and nonnegative; it corroborates identity and is
never a replacement for it. Missing, boolean or nonfinite time refuses.

The SDK-free model will use opaque object tokens compared by Python `is`, plus
an exact session token and a monotonic positive generation supplied as a
**hypothetical verified fact**. This is an abstract contract, not a prescription
to compare native wrappers with `is`. Generations cannot be minted from time,
names, a guessed callback or a manager poll. Native policy remains NOT_READY
until lifecycle and lifetime evidence supplies these facts reliably.

## Eligibility and bounded state

A future separately authorized adapter validates the exact owned Overclock
entry each time: exact integer rank zero skips without writing; rank one alone
can continue; missing, bool, negative or other rank refuses. No points, rank,
save, cost, eligibility, purchase, activation or deactivation calls are made to
repair or manufacture eligibility. Cleanup of an existing owned Duration does
not require rank to remain one, but does require unchanged ownership/liveness.

Before proposing the single Duration assignment, recheck the entire adapter
proof, exact finite numeric Duration/base near 60 (absolute tolerance 0.05),
known exact integer modifier count zero, finite proposed Duration <=180 and
unchanged base/modifiers. Proposed delta is 15; do not write DurationBaseValue
or shared definitions. A nondefault Duration, inaccessible modifier stack,
nonempty stack, bool, NaN or infinity refuses. Recheck again at write and
readback; fresh facts cannot be inferred from an old metadata line.

There is at most one active ledger record and one active session. The record
holds exact tokens, generation, activation time, before/after values, phase,
attempt and cleanup facts. Keep a greatest-attempted-generation watermark even
after restoration or conflict so repeated events cannot add 15 again. Refuse
generation reuse/reversal; new generations require independent lifecycle proof.
Cap a session at 1024 attempts; exhaustion stops effects until explicitly
revalidated restart. A crash/lost ledger forbids adoption of an already changed
Duration or claims of successful cleanup. There is no persistent save ledger.

## State transitions and failures

The following are proposed actions, to be tested **as data** before any adapter
exists. State changes occur before offering a write action. No callback may
recursively start another write while pending, applied or cleaning.

| State/event | Required policy |
| --- | --- |
| IDLE + fresh rank-one eligible unique summon | Record PENDING_APPLY and watermark first; emit one proposed Duration assignment. |
| Repeated/reentrant event or reused generation | No second assignment, including after explicit restoration. |
| Apply acknowledgement with exact unchanged proof and verified after-value | APPLIED. Readback establishes a value, not longer lifespan. |
| Write raises, readback unavailable or mismatch | Stop effects; retain UNCERTAIN record before any cleanup. Never discard a possibly modified instance. |
| CANCEL/disable/limit/error | Clear accepting context first, mark disabled and remove observers; retain record for cleanup. |
| Same exact live record, known after-value and unchanged base/modifiers | PENDING_RESTORE; offer only the recorded before-value on that exact instance. |
| Fresh readback already equals before-value | Record clean, retire attempt, keep watermark; no redundant assignment. |
| Independent Duration or base/modifier change | Preserve it; terminal CONFLICT with no rollback assignment, retain finding and watermark. |
| Unknown ownership/liveness/readback | INERT_RETRY; no assignment until a fresh proof establishes the same original still live. |
| Original proved ended or replaced | Retire original record; never touch a replacement, even with reused names/time. |
| Restore raises or readback differs/unavailable | INERT_RETRY; failed cleanup remains a finding even if a later retry succeeds. |
| Failed observer removal | Context stays inert; retain failed handles for bounded retry, block all new effect contexts. |

A failed write's blind rollback is prohibited. If it demonstrably left before,
no restoration write is needed; if a fresh exact proof sees the owned after,
offer the before-value; any other or unknown value remains conflict/uncertain.
The abstract acknowledgement must describe both write outcome and fresh proof.
An adapter must not claim a thrown write made no change.

Cleanup never scans by name and then writes another object. Losing current
owner/session while the original might still live keeps an inert pending
record. A different session cannot start effects until the old record is safely
retired or explicitly diagnosed; unknown does not mean ended. No background
timer is promised. Retries are explicit/bounded, never automatic effect rearm.

Duration restoration is separate from hook removal and native-array rollback.
The future adapter must report all three outcomes and never claim complete
cleanup from a zero observer count alone. No point refund, rank repair, save
undo, UI/cache repair, shutdown ordering guarantee or no-save Alt+F4 guarantee
is supplied by this contract. A restart cannot retroactively prove restoration.

## Offline model acceptance and native prerequisites

The next claimed SDK-free model takes immutable abstract observations and
events and returns proposed actions as data. It must import no SDK, discover no
game objects and perform no native assignment. Exercise normal apply/restore,
rank zero, unknown rank, foreign same-name tokens, two candidates, replacement
with reused scalar signature, generation reuse, missing/bool/nonfinite time or
values, modifiers, reentrancy, readback/write failure, independent change,
uncertain liveness, cleanup failure/retry and hook removal failure. Failed
cleanup history remains visible through a successful retry. The model must not
turn its passing tests into an adapter-lifetime or game-behavior claim.

Before a native design, review the separately authorized v0.2.12 metadata
capture, then design and capture passive **natural** lifecycle evidence with
verified loaded function metadata/signature, phase, exact ownership and actual
native execution limitations. POST_UNCONDITIONAL alone does not prove native
execution. Resolve lifetime/reference semantics and safe timing with actual
evidence; neither invent a hook path nor invoke discovered functions. A later
effect requires a reviewed implementation contract and explicit authorization
for its exact gameplay writes and recovery protocol. This document authorizes
none of those actions.

## Actual checks for this design

The companion JSON records fresh AST/source checks and accepted mock findings
as historical inputs. All 137 baseline tracked files, prepared packages,
protected originals and captures remain byte-identical. No runtime code or
tests changed, so the already checked 319-test suite was not repeated for these
two design-only files. JSON decoding, local links, strict UTF-8, syntax of the
unchanged runtime and scoped whitespace were checked. No game/SDK/save access
or native lifecycle test ran. The native readiness decision remains NOT_READY.
