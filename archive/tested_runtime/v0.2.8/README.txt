Ultimate Vault Hunters v0.2.8 - OVERCLOCK PRESENTATION SNAPSHOT.

NEXT TEST: compare Overclock, More Pep and Myelin presentation data with
button4. 108 local mocks/syntax checks pass; NO v0.2.8 game result yet.
The prior v0.2.7 trace captured empty Overclock rank-preview text and nonempty
native-skill bonus text, with unchanged sampled points/ranks and restoration.
This snapshot investigates a difference; it does not fix or activate the node.
DO NOT BUY ANY SKILL. The Overclock +15-second node effect is still INACTIVE.

INSTALL:
Close BL2. Replace only sdk_mods/UltimateVaultHunterDeathtrapBoost with this
ZIP's folder; keep one project mod and all SDK/core mods. Its folder directly
contains __init__.py, pyproject.toml, README.txt; no nested mod folder.
Use the already backed-up Gaige alone, Offline, in a fresh BL2 process.

ONE TEST (use only 1, 4, 3):
1. At MAIN MENU before Continue, verify the exact MODS title:
   UVH v0.2.8 - OVERCLOCK PRESENTATION SNAPSHOT
   Choose 1 - ARM ONE GAIGE INIT NODE TEST, then Continue.
2. In map choose 4 - INSPECT OVERCLOCK PRESENTATIONS once.
   It reads all three target definitions. No Skills highlighting or trace
   START needed. No points, respec, travel, boost or other diagnostic buttons.
3. Choose 3 - CANCEL / RESTORE, fully exit BL2 and tell Codex done.
   Leave BL2 closed until the final log is preserved. Restart before normal
   play to discard the engine-built prototype cache.
On partial/error/refusal, cancel and exit; unknown data is evidence.
Never buy or invoke a query/formatter to force a result.

OBSERVATION:
Loaded SkillDefinition property metadata must describe SkillEffectPresentations
as an owned ArrayProperty with ObjectProperty inner and an actual
AttributePresentationDefinition UClass. Exact target/shared class identities,
typed/bounded flags/offsets and dimension1 are checked before array reads.
SDK WrappedArray count<=256, <=4 typed UObject references per target with exact
declared class and SDK path<=384. Common class raw metadata<=16 properties with
one bounded lookahead; type names/skill labels<=96. Actual native matches for
this new property schema are unverified until this run.

Read-only counts, references and property descriptors only. No presentation
instance scalar/display/struct/array/attribute/function values, arbitrary
object repr/graph, guessed WrappedArray._type semantics, effect/constraint
evaluation/copying, native game query/formatting calls, text overrides, loads
or writes. SDK reflection/identity helpers are used, not gameplay functions.
No observers are added by button4.

Reuse unchanged current Gaige/controller/pawn/world/PRI/tree, both sole-player
rosters, exact inert patch/runtime registrations/indices/tier and known PRI
points/ranks guard around reads. Node grade0; snapshot has a local baseline.
Unknown/changed state refuses/aborts. Failed observers or active other traces
refuse inspection. No point/grade/save repair is attempted.

EXPECTED LOG:
[UVH-PRESENT] BEGIN v0.2.8, BASELINE, SCHEMA, ARRAY count/sample/capped,
REFERENCE identities, PROPERTY raw metadata, three SUMMARY lines,
FINAL unchanged_from_start=True, END verified_arrays=N/3 observers_added=0.
VERIFIED empty count is different from UNAVAILABLE data. Metadata status
COMPLETE/CAPPED/UNAVAILABLE is separate from verified array/reference samples.
[UVH-NEWNODE] RESTORE result=True: MorePep/Myelin and True/False/True restored.
Counts/metadata do not prove rendered orange text or purchase eligibility.

ROLLBACK / PRESERVATION:
CANCEL restores only matching owned native arrays; independent changes are
preserved, failed restores retain snapshots. It cannot reset player caches,
refund points, restore grades or undo a save. Restart after every test.
If restoration fails, fully exit without saving and report before resuming.

All seven tested v0.2.1-v0.2.7 ZIPs stay unchanged; keep dist as project evidence.
64 prior functions are AST-identical, four change version labels only and four
are added. Factory 19 options; button4 now runs this focused snapshot instead
of the older general purchase snapshot. Insertion/rollback/guards, existing
observers/cleanup and verified manual Deathtrap 60->75 prototype are unchanged.
Import is inert. No purchases/persistence/automatic effects/co-op/release.
