# Borderlands: Ultimate Vault Hunter Collection — development source

**STATUS: NOT PLAYABLE, NOT READY FOR MELTY.** This is the first code milestone: data-driven roster/skill/progression groundwork and a read-only Borderlands 2 SDK diagnostic. It does **not** port playable characters or include their original abilities yet. There is no fake executable, footage, replacement character models, copied game asset, or published release.

## What we are building
- Borderlands 1 GOTY Enhanced → The Pre-Sequel → Borderlands 2 → Borderlands 3 → Borderlands 4.
- Campaign level milestones 60 / 120 / 180 / 240 / 300.
- All **26** known main-game and DLC Vault Hunters (including BL4 C4SH and Loveless), selected from original installations only.
- Every character preserves signature action skills and original trees. Add new character-specific branches, with level-60/120/240 tiers as **design placeholders**, not gameplay-ready skill trees.
- Co-op with a friend; authoritative state and save consistency are future engine integrations.
- Eventually unified progression, money, eridium, inventory, Oz kits on every Vault Hunter, unlocked fast travel, replay and loot levels capped at 300.

## Repository layout
- `sheets/`: the source-of-truth JSON records of games, Vault Hunters, proposed new branches, and engine systems.
- `ultimate_vh/preflight.py`: verifies every sheet cell, campaign range and cross-sheet reference.
- `ultimate_vh/generate.py`: translates every JSON row into an immutable Python record in `generated/sheet_records.py`.
- `ultimate_vh/progression.py`: isolated, tested level, skill-effect, co-op-manifest and fast-travel rules; **not game hooks**.
- `ultimate_vh/save.py`: checksum-protected atomic sidecar save, never overwrites a game's original saves.
- `adapters/bl2_sdk_probe/`: *experimental, read-only* mod-menu diagnostic for BL2 PythonSDK; no new Vault Hunters yet.
- `tests/`: automated tests of the source-only domain model.
- `docs/RUNTIME_GATES.md`: exact unmet in-game and Melty release prerequisites.

## Development commands
Run from the project root with Python 3.10+ (no third-party Python libraries):

```bash
python -m ultimate_vh.preflight
python -m ultimate_vh.generate
python -m unittest discover -s tests -v
```

## Distribution/credits
Design by project requester; programming prototype created with ChatGPT. This original prototype's code is offered under MIT (see LICENSE). Game titles, names, content and characters are owned by their respective rights holders; no rights to those assets are claimed or distributed. Upstream Borderlands SDK loaders are **not included**; review their licenses before bundling. The user has NOT specified whether a final Melty release should permit remixing.

Current blocker: the execution sandbox has no access to the user's Windows game installations or live gameplay and cannot connect to Melty's publishing API. See `docs/RUNTIME_GATES.md`.
