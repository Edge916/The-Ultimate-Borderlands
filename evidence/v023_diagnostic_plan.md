# v0.2.3: investigate the absent upgrade prompt

After v0.2.2, the user reported Overclock's tooltip showed
**"0/1, with no upgrade prompt"**. The engine log shows one unspent general point,
an unlocked first tier and grade 0. This is enough to investigate the UI path;
it does not prove an incorrect SkillType, missing constraint or purchase defect.
The user has not compared the native first-row skills' prompts in the same UI.

Two limitations in v0.2.2's diagnostics are addressed:

- `_tree_info` uses `len()` on values it cannot classify. SDK enum members are
  IntFlag values, so `<ESkillType len=0>` does not print their actual name/value.
  v0.2.3's purchase-only formatter explicitly reads Python Enum name/value.
  The general formatter and all established v0.2.1 functions stay unchanged.
- v0.2.2 logged only constraint counts and prioritized purchase/reset/save
  function metadata. v0.2.3 reads up to four SkillConstraintData structs per
  definition, up to eight reflected property values per struct, and the
  LockedSkillDetailStr. Unknown struct types are not traversed. It does not
  evaluate constraints, follow their object graphs or copy them into Overclock.
  Metadata detail now prioritizes CanUpgradeSkill, Flash_SetSkillPointProperties
  and its _AS variant alongside cost/state/grade/description query metadata.
  The existing limits remain 30000 scanned objects, 32 paths, 12 detailed
  functions and 16 fields per function. No discovered function is invoked.

Primary SDK reference: [pyunrealsdk enum bindings](https://github.com/bl-sdk/pyunrealsdk/blob/master/src/pyunrealsdk/unreal_bindings/uenum.cpp).
The installed v1.10.0 `_uenum.pyi` independently describes IntFlag enums.
The installed WrappedStruct stub documents `_type`; its UStruct metadata
supports `_properties()`. These are read as data, never executed as scripts.

Only the two existing v0.2.2 diagnostic functions changed, plus two new helpers
and version/description metadata. No new hooks, gameplay calls, loads or writes.
The node constructor, solo guards, insertion/rollback and manual duration
functions remain unchanged. Test source models enum values and constraint
descriptors, but it cannot establish real-engine UI behavior.

Local validation: 41 simulated tests passed, including zero-valued enum display,
constraint field output without evaluation, bounds, unknown struct refusal,
reflection failures and upgrade-UI metadata priority. Syntax compilation,
isolated packaged-runtime import and exact three-file ZIP/source verification
also passed. AST comparison verified all 48 v0.2.1 function bodies unchanged;
against v0.2.2, only the two diagnostic functions changed. Both tested ZIP hashes
and the v0.2.2 log hash were verified unchanged. At build time there was no live
result; the later v0.2.3 run is documented in v023_live_diagnostic_result.md.

Install ZIP: `dist/UltimateVaultHunterDeathtrapBoost_v0.2.3_folder_install.zip`
(21349 bytes). SHA256:
`4573834f5bfad6f8eb4bc8c34051c3edfa4e893ba22e358ce5761431d1e17de6`.

Run the documented backed-up Gaige Offline test: ARM, Continue, button 4, compare
Overclock/More Pep/Myelin tooltips without purchasing, button 4 again, CANCEL,
exit. Record whether each skill shows an upgrade prompt or locked message using
the same input method. Do not respec, travel, buy any skill or use manual boost.
Preserve the log before restarting; use a fresh process before normal play.

Follow-up: the next user run still loaded v0.2.2, confirmed by log headers and
installed hashes. See v022_repeat_rank_preview_clarification.md. The user meant
missing orange rank-upgrade text; do not infer a purchase failure. A subsequent
run correctly loaded v0.2.3 and verified its diagnostic reads and restoration.
The user confirmed the blue title and inactive prototype description. The current
snapshot milestone is complete; see v023_live_diagnostic_result.md. Preserve the
tested v0.2.3 ZIP alongside earlier baselines; no runtime change was needed.
