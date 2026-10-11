# Borderlands: Ultimate Vault Hunter Collection — Codex handoff

**Current game-tested build: v0.2.12 - DEATHTRAP METADATA. Result: PARTIAL.**
The owner completed the reviewed run and confirmed CANCEL/full exit. Both
logged inspections captured manager/skill/definition classes and all seven
selected fields; ActivateSkill/DeactivateSkill were UNAVAILABLE on the selected
controller. Points/ranks stayed unchanged by runtime assertion, arrays restored,
all observer families0 and independent capture process queries0. Actual installed
files matched original ZIP/source; the raw log, manifest and testedREADME are
frozen. Two calls instead of requestedone/secondARM refusal/repeatedCANCEL are
recorded in [the live result](evidence/v032_live_deathtrap_metadata_result.md)
and [manifest](evidence/v032_capture_manifest.json).

No repeat is needed to force full coverage. Next is a bounded metadata-owner
design using the actual returned SkillEffectManager class. No callable signature,
natural lifecycle timing, native lifetime or node duration effect is established.
Item4 makes no native function calls, active-skill payload reads, new hooks or
gameplay writes; established ARM/insertion is a separate operation. See
[the next task](docs/NEXT_CODEX_TASK.md). All84 pre-v12 functions/guards remain
AST-identical and19 options remain. Preserve all originals.

This project is a **Borderlands 2 PythonSDK gameplay-mod prototype**, with a separate early design-oriented codebase for a much larger multi-game Borderlands project.

**Previous game-tested build:** **v0.2.11 - OVERCLOCK ATTRIBUTE CLASS**.
Two complete read-only calls captured Myelin's previously refused Attribute as
SDK_UOBJECT with actual UClass ResourcePoolAttributeDefinition and a five-class
COMPLETE ancestry through declared AttributeDefinition. Runtime identity/link
checks report DERIVED; names alone do not establish that relationship.
Sampled points/ranks stayed unchanged, CANCEL restored arrays, observer families
reported zero and separate capture process queries found BL2 exited.

The previous v0.2.11 metadata test is complete. One call was requested; two were logged,
with a second ARM refusal and repeated CANCEL. These details are preserved in
[the reviewed live result](evidence/v031_live_attribute_class_result.md) and
[the immutable capture manifest](evidence/v031_capture_manifest.json).
No repeat of completed flags/text/classes is needed. The old exact-class guard
stays unchanged; this result does not authorize Attribute evaluation or effects.
179 unique runtime mocks remain relevant; the peer-reviewed offline reviewer
passed all 236 unique tests (57 reviewer+179 runtime).

The user separately reports spending one point in Overclock and seeing1/1,
then Alt+F4/restarting. The restarted log shows one unspent point and Overclock0.
This is positive user-observed purchase/rank evidence; the first transaction,
save behavior and node effect were not independently captured. Do not repeat
the purchase to recover missing evidence.

v0.2.9's completed live run verified all 24 native text fields in each of two
snapshots, including the scalar-owner guard. Overclock has no entries; native
Description strings use $NUMBER$ templates and the other strings are empty.
Points/ranks stayed unchanged in both calls, arrays restored, hooks0 and BL2
fully exited. v0.2.10 compared display flags and attribute identities.

The tested v0.2.8 retry verified presentation counts Overclock=0, MorePep=4
and Myelin=2, all six references, unchanged sampled FINAL state and restoration.
Its raw class metadata was capped at 16 properties; instance text was unread.
The empty candidate array and prior empty grade-preview return are consistent
with missing display data, but do not prove causation or eligibility.
The first screenshot's [Enter] Spend Point hint is separate evidence.

See [the live text result](evidence/v029_live_presentation_text_result.md),
[the next task](docs/NEXT_CODEX_TASK.md) and
[the live display result](evidence/v030_live_presentation_display_result.md).
Preserve all twelve original versioned ZIPs, six exact tested snapshots and
prior evidence unchanged. Current docs/default ZIP may differ in README only;
the exact v0.2.11/v0.2.12 tested READMEs are frozen in their snapshots/original ZIPs.

**Verified on user's real game (BL2): v0.2.1 now shows Deathtrap Overclock in Gaige's native tree.** The user reported "done it worked!" after the visibility test. The log verifies one inert runtime node at grade 0, both original first-tier skills present, all observers removed and original native arrays restored on cancellation. The separate manual v0.1.1 prototype changed active Deathtrap duration from **60.0 to 75.0**, and the user reported it stayed out longer. **The visible node does not apply that effect. A purchase to1/1 is now user-reported; captured transaction/save behavior and persistence remain unverified.** See [the visibility evidence](evidence/v021_visibility_confirmation.md).

Read `AGENTS.md` and `docs/STATE_AND_HISTORY.md` before changing any code. The initial visibility goal is met in one successful solo test. Preserve v0.2.1 as the first confirmed visibility baseline; current tested runtime is v0.2.12 with partial metadata coverage. The eventual goal is a safe **one-rank Deathtrap Overclock node** which, if purchased, grants +15 seconds to Deathtrap. Keep the user-reported purchase separate from log-verified state; do not claim captured transaction, persistence or duration-effect success without the relevant evidence.

## Run local tests

From project root (Python 3.10+):

```powershell
python -B scripts/run_offline_validation.py
python -B scripts/verify_artifact_inventory.py
python -B scripts/review_deathtrap_metadata_log.py evidence/v032_user_test.log
# PARTIAL / exit 1 is expected for this preserved v0.2.12 capture.
```

Run the generated ZIP's `UltimateVaultHunterDeathtrapBoost` folder inside `Borderlands 2\sdk_mods` only after backing up the save and reviewing the experiment's risk. **Local mock tests cannot run Borderlands 2 or confirm HUD/skill-tree behavior.**

## Layout

- `sdk_mods/UltimateVaultHunterDeathtrapBoost/` — current v0.2.12 runtime, with the bounded read-only Deathtrap metadata diagnostic, existing opt-in observers, established armed insertion and preserved manual duration prototype.
- `tests/` — isolated mock-based regressions for diagnostics, hook cleanup, missing assets, insertion rollback and the manual duration prototype.
- `scripts/package_mod.py` — package the SDK installable ZIP.
- `docs/` — handoff, next task, Windows installation notes.
- `evidence/` — selected real logs that prove specific engine behavior; no game assets or saves.
- `archive/early_design_source/` — **older independent data-model prototype** for the long-term cross-game vision. Not integrated into the current runtime; do not mistake it for playable gameplay functionality.

No game binaries, copyrighted game assets, save files, or PythonSDK loader are included.

The v0.2.2 diagnostic run is complete: four snapshots kept PRI points 1/0 and
Overclock rank 0/1, metadata reflection worked and CANCEL restored original
arrays with zero observers. See [the diagnostic evidence](evidence/v022_purchase_diagnostic_result.md).
v0.2.3 now has a completed live diagnostic run: enum/constraint/UI metadata reads
worked, all three definitions are Passive/value0, sampled points/ranks stayed
unchanged and cancellation restored arrays with zero observers. The user confirmed
the blue title and inactive prototype description. See [the live result](evidence/v023_live_diagnostic_result.md).
The current snapshot milestone is complete; no repeat is needed merely for
tooltip details. Restart before
normal play. **Do not buy any skill.** Native rollback does not rewrite the
engine-built player/UI cache, refund points or undo a purchased rank. A later
purchase test needs explicit scope and a point/grade/save recovery plan first.
See `docs/NEXT_CODEX_TASK.md` and the packaged README for reproduction and rollback.

The first intended v0.2.3 follow-up loaded v0.2.2, confirmed by its log and
installed hashes. That repeat again restored arrays and kept points/ranks unchanged.
The user clarified they meant absent orange rank-upgrade text and Overclock looks
like the other skills; purchase failure is not established. The later v0.2.3 run
resolved that mismatch. Always confirm the exact version in MODS before arming.
See [the earlier follow-up evidence](evidence/v022_repeat_rank_preview_clarification.md).

SDK interface checks used the installed pyunrealsdk v1.10.0 `.stubs` for
`find_all`, `_path_name`, PRE/POST callbacks, `add_hook`, `has_hook`, and
`remove_hook`, plus the installed `mods_base` factory's `on_disable` callback.
The upstream [pyunrealsdk usage overview](https://github.com/bl-sdk/pyunrealsdk#using-sdk-bindings)
documents the four-argument observer callback and hook path format. Function
discovery/PRE/POST callbacks were observed in the v0.1.9 engine log. v0.2.1's real
run verified PRE insertion, POST runtime registration, observer removal and
native-array restoration. Solo roster fields and enum lookup follow the installed
networking and mods_base sources; the one-player listen-host positive path passed
in engine. Other safety/refusal cases remain covered by local mocks.
No native save/grade/point APIs are invoked.

All three tested versioned ZIPs are preserved unchanged. v0.2.2 passed 37 local
simulated tests and isolated package checks, plus a real diagnostic/restore run.
Its bounded function metadata uses the SDK's `_properties()` reflection iterator,
documented in the [upstream bindings](https://github.com/bl-sdk/pyunrealsdk/blob/master/src/pyunrealsdk/unreal_bindings/uobject_children.cpp).
Raw fields/flags are not verified callable signatures or proof of actual cost.
The iterator includes local fields, and SkillType formatting did not expose its
enum value in the v0.2.2 run. v0.2.3 corrects that formatting and reads bounded
constraint metadata without evaluating or copying constraints. It passed 41
local mocks and its positive diagnostic path now has real engine evidence.
Historical failures remain in STATE_AND_HISTORY.

The completed test used **v0.2.4**: verify its MODS title, ARM before Continue as
backed-up Gaige Offline, press 5, highlight Overclock/More Pep/Myelin without
buying, press 6 then 3, and exit. Full steps are in docs/NEXT_CODEX_TASK.md and
the packaged README. STOP logs actual returned values and checks final state;
empty summaries mean no observed query. No purchase/effect conclusion follows.
Limits remove observers after 24 captures or 2048 attempts; a 90-second bound
is checked on the next call. Always press STOP even if no calls occur.
See [the implementation and evidence limits](evidence/v024_observer_plan.md).

The completed v0.2.4 observer run is preserved in evidence/v024_live_observer_result.md. Initial in-map ARM/start attempts refused; menu ARM then insertion and two-observer setup passed. The user confirmed highlighting all three skills, but STOP recorded callbacks=0 and no results, with sampled points/ranks unchanged. After clarification the user pressed 3 and exited; the final log verifies original native-array restoration and zero observers. All four versioned ZIPs and runtime are unchanged. Actual eligibility/cost remain unanswered; next useful work is a different bounded UI navigation/refresh observation, not point spending or repeating these same hooks.

The completed v0.2.5 test used **1 at MAIN MENU**, Continue as solo backed-up Gaige Offline, **7 START**, open Skills/hover/navigate all three, **8 STOP**, **3 CANCEL**, then exit. Do not buy. The direct UI snapshots supplement navigation events even if callbacks are zero. See docs/NEXT_CODEX_TASK.md and evidence/v025_ui_trace_plan.md. All four tested versioned ZIPs remain unchanged.

The v0.2.5 live UI trace is preserved in evidence/v025_live_ui_trace_result.md: 14 events/16 callbacks verified the owned UI selecting Overclock, MorePep and Myelin with UI point=1 and target tier unlocked=True. Final PRI points/ranks stayed unchanged; observers were removed and native arrays restored. The ten-function cap included four artifact paths and left discovered core PostNav/input/info/point-display helpers unhooked. v0.2.6 improves that priority and its live core-helper result is documented below. Eligibility/cost/purchases/effects remain unverified. At the v0.2.5 review its source was unchanged; all five tested versioned ZIPs stay unchanged.

The completed v0.2.6 test used **1 at MAIN MENU**, Continue as backed-up solo Gaige
Offline, **7 START**, navigate/hover Overclock, More Pep and Myelin without
clicking or buying, **8 STOP**, **3 CANCEL**, then fully exit. Confirm exact
title **UVH v0.2.6 - OVERCLOCK CORE UI TRACE** before arming. Leave BL2 closed
until the log is preserved. See docs/NEXT_CODEX_TASK.md and the packaged README.
74 local mocks include live-name crowding, loaded-only selection and exclusion
before reflection. The other 59 runtime functions remain AST-identical to
v0.2.5; only three version labels and candidate selection change. Keep the
six tested ZIPs. The live core-helper/cleanup result is documented below.

The v0.2.6 result is preserved in evidence/v026_live_core_ui_result.md:
48 events/51 callbacks captured all six core helpers, including Overclock's
UpdateInfoBox PRE/POST_ANY. MorePep/Overclock selection, one UI point and an
unlocked tier were observed. The event cap stopped before Myelin; no inference
about later highlights follows. Sampled FINAL PRI points/ranks stayed unchanged,
observers were removed and native arrays restored. Actual eligibility/cost/
upgrade text remain unknown in that run. v0.2.7 targets query/text/info and
protects target capture slots; its live result follows below. Do not repeat
unchanged v0.2.6 solely to reconfirm paths. The node stays inert.

The completed v0.2.7 test used **1 at MAIN MENU**, Continue as backed-up solo Gaige
Offline, **9 START**, highlight Overclock/More Pep/Myelin without clicking/
buying, **10 STOP**, **3 CANCEL**, then fully exit. Verify exact title
**UVH v0.2.7 - OVERCLOCK FOCUSED STATE TRACE**. Use 9/10 instead of older traces.
Hook inputs are copies: OutSkillState is not a final output. Observe actual
query Boolean and returned grade-description string, not copied outputs or
locals. Neither is proof of eligibility or the rendered prompt. The run captured
16 results/110 callbacks across all nine buckets, including empty Overclock
rank-preview returns and nonempty native-skill returns for the same inputs.
FINAL points/ranks were unchanged, hooks zero and restoration successful.
v0.2.8 below now supplies the bounded native presentation comparison.

All seven tested v0.2.1–v0.2.7 ZIPs were recovered from the Recycle Bin after
accidental deletion and verified against their original hashes. Keep `dist`:
it holds the project's tested baselines. A tested v0.2.7 source snapshot is
also preserved under `archive/tested_runtime/v0.2.7`. Only the default ZIP may
be rebuilt for documentation changes; versioned tested ZIPs remain unchanged.

The completed v0.2.8 test used the verified installed build in a fresh process:
**1 at MAIN MENU**, Continue as backed-up solo Gaige Offline, open the mod
options and **select item4 INSPECT** once, **3 CANCEL / RESTORE**, then fully exit.
The numbers label mod-option buttons, not keyboard keys in the map.
Verify **UVH v0.2.8 - OVERCLOCK PRESENTATION SNAPSHOT**. No skill highlighting
or trace START is needed; button4 reads all three targets. No point spending,
travel/respec/boost or other diagnostic buttons. Keep BL2 closed until its log
is preserved. Unknown/capped metadata is reported; the node remains inactive.
64 prior functions are AST-identical, four change version labels only and four
new functions implement the snapshot. Factory remains 19 options. Preserve the
eight original versioned ZIPs and tested-source snapshots v0.2.7/v0.2.8.
The first v0.2.8 log/PNG are preserved; collect the next log under a new name.
The first run verifies insertion/visibility/cleanup, with no [UVH-PRESENT]
messages. The separate retry log records two completed inspections and verified
empty Overclock data, compared with four MorePep and two Myelin presentations.
Do not repeat those counts merely to reconfirm them. The next design is a
bounded read-only comparison of observed presentation string/display fields.
At that review no next build was prepared; v0.2.9 below now supplies it.
Causation/purchases/effects remain unverified. The tested v0.2.8 runtime and
every original versioned ZIP are preserved unchanged.

The completed v0.2.9 test used its distinct ZIP (reproduction only): fully close BL2 and replace only the
project mod folder. Verify **UVH v0.2.9 - OVERCLOCK PRESENTATION TEXT** at
main menu, select1 ARM before Continue as backed-up solo Gaige Offline.
In map open mod options/select **4 - INSPECT PRESENTATION TEXT** once,
select3 CANCEL/RESTORE, fully exit and report done. Menu numbers are option
labels, not keyboard shortcuts. No highlighting, other traces or point spending.
Keep BL2 closed until its log is preserved under a new filename.

127 tests, syntax and AST proof passed. Of72 prior functions67 are unchanged,
five change version labels only and four new functions implement the inspector.
Factory retains19 options. The live run accepted exact scalar-owner matching,
verified24/24 fields per call and sampled unchanged FINAL points/ranks. Native
arrays/cells restored, all hooks0 and process exited. Partial/unknown data
still refuses reads; never bypass guards. Existing insertion/rollback, state/
session guards, observer cleanup and manual Deathtrap60->75 remain unchanged.
Preserve nine original ZIPs and three tested snapshots v0.2.7/v0.2.8/v0.2.9.
At that review the next design was observed display flags and a validated
Attribute reference identity; v0.2.10 below now supplies it. See the live result;
raw templates do not establish cause, eligibility/purchase or duration effects.


The completed v0.2.10 test used its distinct ZIP (reproduction only). Fully close BL2 and replace only the
project mod folder. At MAIN MENU verify **UVH v0.2.10 - OVERCLOCK PRESENTATION DISPLAY**,
select1 ARM before Continue as already backed-up Gaige alone Offline.
In map open mod options/select **4 - INSPECT PRESENTATION DISPLAY (READ ONLY)**
once, select3 CANCEL/RESTORE, fully exit and report done. Numbers label mod
options, not keyboard keys. No highlighting/other traces/points/respec/travel/
boost. Keep BL2 closed until the log is preserved under a distinct filename.

151 unique mocks, syntax and AST proof passed.70 old functions are unchanged,
six change version labels only, four new functions/fixed flag tuple,19 options.
The live run accepted scalar schemas/owners and five exact Attribute identities;
one Myelin field refused and remains unknown, never absence or a guessed subclass.
The next design can inspect only that field's wrapper/actual loaded class metadata;
no further game steps are needed for this review. Neither
flags nor reference names prove formatting semantics, eligibility or effects.
Preserve all ten tested ZIPs, snapshots/logs/PNG; each version has its own file.

## Completed v0.2.11 metadata milestone and proposed follow-up

Read [the live result](evidence/v031_live_attribute_class_result.md),
[the actual log](evidence/v031_user_test.log), [capture manifest](evidence/v031_capture_manifest.json)
and [offline reviewer](evidence/v031_log_review_tool.md). They distinguish raw
metadata/state/cleanup from separately checked installation and process exit.
Preserved v0.2.11 files remain identical to the original ZIP and snapshot.
Current v0.2.12 source adds only the bounded metadata diagnostic described above.

The node effect remains inactive; the separate manual +15s prototype is preserved.
[Readiness research PR#4](https://github.com/Edge916/The-Ultimate-Borderlands/pull/4)
passed independent peer review and proposes a bounded metadata-only Deathtrap
diagnostic for separately scoped implementation. No lifecycle implementation or game test has occurred; v0.2.12 prepares metadata only.
See [the next task](docs/NEXT_CODEX_TASK.md). Do not invoke native methods from
inventory names, relax diagnostic guards, spend points or add automatic effects.

The static artifact inventory pins the earlier prepared-e32 current files.
After this README-only documentation update, its immutable check still passes;
`--check-current` reports exactly the intentional README/defaultZIP drift.
Current package/source equality is checked separately by `verify_package.py`.
The versioned v12 ZIP and exact tested three-file snapshot remain untouched.
