# BL4 unified collection: initial feasibility audit

Audit date: October 12, 2026. Baseline: accepted PR49 commit
`7a23c583a0d81507b7c01e1edc82171c7c50a97f`.
See the [actual checks and source fingerprints](../evidence/bl4_unified_collection_feasibility_checks.json).

**Decision: continue bounded BL4 tooling research; campaign and legacy-character
implementation are not ready to start.** BL4 is installed and a community SDK
exists. A compatible custom-content authoring, cooking and loading route, and
a new playable-character integration route, have not been demonstrated.
This is an evidence gap, not a finding that the collection is impossible.

## Confirmed product scope

One collection using the Borderlands 4 engine foundation. Any playable Vault
Hunter from BL1, BL2, The Pre-Sequel, BL3 or BL4, including DLC characters, can
play every included campaign and campaign DLC. Modern movement includes double
jump, sliding and ground slam. Wonderlands is excluded. Character fidelity,
equipment pools, progression, balancing and co-op remain design decisions.

The following proofs support the full collection vision; they do not replace
it with a smaller final product.

## Local installation and repository evidence

The actual checkout is the accepted 254-file PR49 baseline. Its existing code
is a BL2 diagnostic, not a BL4 character framework. The collaborator's active
repository-navigation scopes are separate from these two new audit files.

Steam metadata and the executable's presence confirm a local BL4 installation:
AppID 1285190, installed and target build 25372571. No executable file/product
version was supplied by its version resource. These checks do not verify depot
integrity, exact engine minor version, SDK compatibility or gameplay.

The expected Win64 Plugins directory, dsound SDK loader and two checked sdk_mods
locations were absent. No editable game project or engine Build.version was
found at the checked game-relative paths. The content directory contains 345
PAK files, 346 UCAS files and 346 UTOC files. Only names/counts/metadata were read;
no archive was opened or extracted. Presence does not establish encryption,
mapping compatibility, mount order or that added content would load.

No UE5 editor or selected asset tools were found in the bounded default/tool-root
search. The editor registry contained a 4.0 entry, not evidence of a usable UE5
cooker. Other locations and source-built tools remain possible. The restricted
shell initially could not see the D: library; an authorized read-only host check
resolved access. Do not interpret the initial negative result as absence.

Private account identifiers, unrelated installed games, saves, installation
paths and raw manifests are not included in this payload. No game, editor,
SDK, importer or packaging executable was run.

## What the primary sources establish

| Source | Verified source capability | Boundary for this project |
| --- | --- | --- |
| [BL4 mod manager](https://github.com/bl-sdk/oak2-mod-manager/blob/d606e796733eced318e2a44e51b871a7becae55e/Readme.md) | A BL4 Python mod manager exists; its source metadata declares version 0.3. Changelog discusses custom game-data types and two signature sets. | Not installed here; no match to installed build 25372571 has been tested. |
| [SDK game selector](https://github.com/bl-sdk/unrealsdk/blob/ac31716b2b462e78f0a841b6d352aa2fa56c7f92/src/unrealsdk/game/selector.cpp) and [BL4 interface](https://github.com/bl-sdk/unrealsdk/blob/ac31716b2b462e78f0a841b6d352aa2fa56c7f92/src/unrealsdk/game/bl4/bl4.h) | Separate OAK2 BL4 backend, hooks, reflected object access and package/object interfaces are implemented or declared. | A package-loading interface is not proof of compatible authored maps, mission systems or character registration. |
| [Movement mod source](https://github.com/Squ1ggs/Bl4SDKmods/blob/54d81c030378d1fcd12585cd679ee00d14132aa5/bl4_player_movement/__init__.py) | Code reads existing movement components and writes tuning fields, including movement-cost paths. | This demonstrates an implementation approach in source, not a tested legacy Vault Hunter or our build compatibility. |
| [World travel description](https://github.com/Squ1ggs/Bl4SDKmods/blob/54d81c030378d1fcd12585cd679ee00d14132aa5/world_travel/README.md) | Author describes bookmarks and travel to existing locations. | Travel commands do not establish import or creation of a new map. |
| [FModel](https://github.com/4sval/FModel/blob/d61549776a0ca9411903804640c7a61de721c4e6/README.md) | Archive exploration, preview and conversion/export facilities, backed by CUE4Parse. Export implementation inspected as text. | Viewing or exporting assets does not provide an editable BL4 project or recreate mission logic. No local/build-specific parser test. |
| [UAssetGUI](https://github.com/atenfyr/UAssetGUI/blob/6b9dcf3daa128cd84a29006ccb29aec72b191939/README.md) | Low-level asset examination/modification and JSON round trips using engine versions/mappings. | Editing an existing package is not a demonstrated map authoring pipeline; mappings and game-specific types are unverified. |
| [retoc](https://github.com/trumank/retoc/blob/885a8dae740cb1ce1e41ff2e74f67f9f0c118237/README.md) and [CLI](https://github.com/trumank/retoc/blob/885a8dae740cb1ce1e41ff2e74f67f9f0c118237/retoc_cli/src/main.rs) | IoStore/legacy-container conversion and versioned packing interfaces. Source uses legacy and Zen asset conversions. | Its word "legacy" refers to container/package representation; it does not mean converting UE3 Borderlands gameplay to UE5. No BL4 cook/mount proof was run. |

The current SDK README labels BL4's engine minor version with uncertainty.
Do not select an editor/cooker merely from that guess or assume the latest
stock UE5 build matches Gearbox's serialization, native types or shaders.
Current BL4 source pins are distinct from the earlier installed BL2 SDK pins.
The legacy SDK97 discussion was reread as historical context, not as a BL4
thread/lifetime or asset-loading guarantee.

Epic's [UE5.5 cooked-content documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-cooked-content-in-the-unreal-engine?application_version=5.5)
describes read-only cooked assets, preserved dependency paths and known Blueprint
limitations. Its [build pipeline documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/build-operations-cooking-packaging-deploying-and-running-projects-in-unreal-engine?application_version=5.5)
describes project-based build/cook/stage/package steps. These explain why installed
packages and an SDK are insufficient evidence of an authoring pipeline. They are
generic engine documentation, not a supported BL4 map-import recipe.

## Related UE5 reimplementation research

[BL2 ReBased](https://github.com/zuhuHix/BL2_ReBased/blob/664b5fddf6ed0e5fe8150b32b2945e4431a23bce/README.md)
is a relevant research lead. Its author reports frozen BL2 scenery and a bounded
Maya/mission developer slice with stand-ins, and explicitly says the full game
is not playable. These are author reports, not independently reproduced results.
The inspected [OpenWillow project](https://github.com/zuhuHix/BL2_ReBased/blob/664b5fddf6ed0e5fe8150b32b2945e4431a23bce/host/ue5/OpenWillow/OpenWillow.uproject)
and [level importer](https://github.com/zuhuHix/BL2_ReBased/blob/664b5fddf6ed0e5fe8150b32b2945e4431a23bce/host/ue5/import_level.py)
use their own UE5 project/editor workflow. That architecture supplies research
ideas, but is not a BL4-hosted port or a replacement for the confirmed foundation.
No code, proprietary assets or claimed runtime results were adopted.

## Next bounded proofs and acceptance gates

1. **BL4 host/tooling compatibility design.** Identify an exact official SDK
   release, its provenance and a reversible install/owner diagnostic plan for
   build 25372571. Define minimal read-only startup/version observations and
   refusal/cleanup conditions before requesting permission to install or run.
   Candidate separate scopes: `docs/bl4_host_probe_design.md` and
   `evidence/bl4_host_probe_design_checks.json`.
2. **Custom-content route research.** Find a reproducible BL4-specific tiny
   authored-map example or construct a justified cook/mount design from verified
   compatibility evidence. Record exact project/engine assumptions, dependency
   paths, game types, registry/container handling and rollback. Before a live
   proof, require a concrete reviewed artifact and owner protocol. The proof
   must load a new tiny area with movement and collision, not teleport to an
   existing BL4 location. Candidate separate scopes: `docs/bl4_content_route.md`
   and `evidence/bl4_content_route_checks.json`.
3. **Legacy character integration design.** Establish the host's selectable
   character definition, pawn/animation rig, skills/UI, equipment and progression
   interfaces. A cosmetic replacement alone does not pass. First runnable proof:
   one legacy character and its characteristic action skill in an existing BL4
   area, with modern movement and bounded unload/restore evidence. Gaige remains
   a candidate, not an implementation selected by this audit. Candidate separate
   scopes: `docs/bl4_legacy_hunter_design.md` and
   `evidence/bl4_legacy_hunter_design_checks.json`.
4. **First campaign slice.** Only after content and character proofs pass,
   combine one legacy area, one mission and combat; verify completion, collision,
   equipment and save/reload behavior. Add a second character/campaign slice to
   test the shared framework before expansion across the collection.

These are proposed follow-ups, not newly claimed implementation or live tests.
The concrete current blockers are missing installed/tested BL4 SDK tooling,
unconfirmed engine/cooker compatibility, no accessible BL4 editable project or
verified custom-map template, and unproved legacy-character/mission interfaces.
Read-only research can continue without those; native or content implementation
cannot honestly be declared ready from this audit.

## Actual validation and limits

All 254 baseline blobs remain byte-identical. The two additions pass UTF-8,
JSON, source fingerprints/Git blob checks, link/scope/whitespace/privacy checks,
35 project syntax checks, all 19 original ZIP CRC/layout checks, seven complete
frozen report/manifest equalities and immutable inventory 53/12/5 checks.
Downloaded source was read as inert text only and excluded from project syntax
compilation. Existing 914 offline tests and hosted CI were not rerun for static
files. No live game/SDK/editor/content conversion, character/mission execution,
asset extraction, save/private-backup work, game test, install, merge or release.
No live native or gameplay proof is claimed. Findings are ready for review;
public export of these two files requires a separate scoped approval.
