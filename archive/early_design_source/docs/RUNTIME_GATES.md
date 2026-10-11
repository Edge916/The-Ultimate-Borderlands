# Runtime gates — hard blockers before gameplay/publishing

These are **not** feature checkmarks. Source builds and unit tests are not game tests.

1. Installations and game licenses: verify the five game directories on a Windows test machine, including the two BL4 DLC Vault Hunters (separate paid entitlements may be required). The chat sandbox cannot inspect the user's PC.
2. Loader: get a supported BL2/TPS/BL1 PythonSDK loader in a way compatible with Melty one-click packaging and its distribution license; Melty's game_info/one_click_check must confirm.
3. Native gameplay: inspect the character select and actor templates, action skills, skill trees, cosmetics, animations and voice assets in the user's owned installs. Record exact resource IDs, then implement in-game hooks. Current JSON names are human references only.
4. Cross-engine: implement on-demand content extraction or bridging from UE3/UE4/UE5 legally, with no game files uploaded. Test each one in the actual host game. Existing engines cannot load the other engines' native game packages directly.
5. Co-op: host and join in TWO running installations, verify that each player uses the same transformed actors and original skills; never claim tested from model-only simulations.
6. Saves: back up native saves, build adapters and test reloading real inventory/skills across restarts and co-op. Sidecar save proof does NOT migrate native inventory.
7. Real capture: screenshot the mod working in the game; don't use fabricated art/mockups.
8. Melty: connect an authorized publisher, confirm game_info for each game, search_mashups, inspect_package, validate_recipe, one_click_check, upload, media, user authorization and publish verification. No release or listing exists.

The toolkit from github.com/rehan-remade/universal-modder was researched via its public documentation. Git clone failed because this container cannot resolve github.com. No toolkit or SDK dependency was installed, and no game was launched.
