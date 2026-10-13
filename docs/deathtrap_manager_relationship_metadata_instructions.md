# Prepared v0.2.19 relationship class metadata collector

**Offline implementation only; not tested in game. No owner test is approved.**
This implements the accepted [design](deathtrap_manager_relationship_metadata_design.md)
from `24026ad43a26f5e32eaf534073080a836e89ecd1` /
[PR48](https://github.com/Edge916/The-Ultimate-Borderlands/pull/48).
Read the [metadata-gap audit](deathtrap_manager_attribution_feasibility.md),
[v18 assessment](../evidence/deathtrap_activation_reader_live_readiness_result.md)
and [implementation checks](../evidence/deathtrap_manager_relationship_metadata_implementation_checks.json).
V18's exact Skill_DeathTrap and filtered UpshotRobot observations remain frozen.

The title is **UVH v0.2.19 - RELATIONSHIP CLASS METADATA**. New item24 starts a
separate class-descriptor catalog; item25 stops/reports it. The existing item3
CANCEL also stops this family before the historical array cleanup. Import and
START perform no game/class/player field lookup. The one-attempt collector
runs only inside a naturally delivered ActivateSkill PRE callback, returns
exact None, and never invokes the hooked function.

The accepted98-operation schema gate validates all six descriptors without
reading their values. Eight fixed class lookups/ancestry and two root heads
are checked before and after the bounded PropertyLink walks. Each root permits
512 descriptors and64 rows. Descriptor guards reject invalid binding shape,
owner, link, integer/layout, duplicate/cycle or changed data. Exact object
properties record only known declared-class tokens. OTHER class declarations
and unsupported subtypes remain explicit; no class-path synthesis or value read.

Meter caps are112/96/14000/14000,total28208. Collector2 seconds/session120
seconds are checked at issued-operation/callback/control boundaries, with no
background timer. The entire maximum planned walk is27814 issued operations.
Native SDK copy/conversion/traversal/getter internals are outside that count
and a single native operation can overrun a time limit. SDK input validity,
installed native binary/build/configuration and thread/lifetime/destruction
guarantees remain conditional/unestablished as described in the design.

An inner frame returns primitive rows/summaries/counters only. Payload/native
references and exceptions are released before JSON logging. One attempt makes
the collector inert but leaves its handle until explicit STOP. A busy STOP
defers cleanup; another explicit STOP is required when collection has ended.
Failed owned removal and unknown registration remain blockers for restart.
Logging/control exhaustion cannot establish clean closure through silence.
Old option/start surfaces refuse overlap, while CANCEL/disable remove the new
owned handle without invoking manual Duration restore. The historical manual,
grade-zero and old reader functions retain their behavior outside the new guard.

The prefix `[UVH-REL-META]` carries canonical bounded JSON. COMPLETE_LINK is
scoped linked-list metadata, not an exhaustive game field inventory or an
ownership relationship. Partial/refused/no-event/OTHER findings must be retained.
No instance values, GetSkillManager/BoundFunction/UFunction/delegate call,
ActiveSkills payload, flag/Duration/point/rank/save write or automatic effect
occurs in this collector. Manager attribution, unique active membership,
generation/liveness, clock/Duration consumption, rank-one and exact-original
write/readback/restoration remain NOT_READY.

## Gates before any later owner action

1. Publish and deliberately accept the exact tested runtime/package payload.
2. Complete the separately scoped strict metadata-log reviewer and its tests.
3. Prepare a new owner request naming the exact original ZIP/hash, title and
   location-specific protocol, then receive explicit approval.
4. Only that later request may authorize installation or an ordinary summon.
   Capture follows explicit STOP25/CANCEL3/full desktop exit and preserves the
   complete log/snapshots without replaying a partial or refused result.

The later protocol must clearly locate every step: with BL2 closed install the
approved build; at the **MAIN MENU** verify Offline/Gaige/exact title without ARM;
select Continue and fully load the **MAP**; select **START24** once; close options
and use only the separately approved ordinary action needed for a natural
callback; select **STOP25**, then **CANCEL3** in the map; fully exit to the
**DESKTOP** and wait for log preservation before relaunching. That is a future
protocol outline, not a runnable approved test. No buying/respec/travel/manual
boost/item4/other trace or automatic retry. Time/refusal/skill-availability and
missing-control stop/skip rules must be specified in the later exact request.

All old raw captures, manifests, snapshots and original ZIPs remain immutable.
The current ZIP has only three project files; it adds no SDK/stub source, game
asset or private file. Runtime/package publication, game use and raw-log export
are separate approvals. Hosted CI, installed SDK/native behavior, gameplay,
save/private-backup changes, merge and release are not performed here.
