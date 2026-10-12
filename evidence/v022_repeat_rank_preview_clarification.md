# Intended v0.2.3 test actually ran v0.2.2

The user reported completion and clarified the visual observation:
Overclock looks like the other skills, with no orange text for upgrading its
rank. They interpret this as related to its single-rank `0/1` display, rather
than a demonstrated purchase failure. No purchase attempt or separate native
tooltip rank/prompt details were reported. Do not treat the earlier phrase
"no upgrade prompt" as proof that the skill cannot be purchased.

The new log is preserved as `v022_repeat_rank_preview_clarification.log`.
Its snapshots explicitly identify **v0.2.2**, and the installed pyproject also
reports v0.2.2. The installed `__init__.py` SHA256 is
`6b5e54e9e160453e24d2dd6c609b29f75e3252b4cf162afb44b2877ce4b2bb02`,
matching the tested v0.2.2 source. The workspace v0.2.3 source differs:
`1d2a62974b115b606a40d760da12996f7226c1e0a385282ef296248f06d6aef6`.
This establishes a version mismatch; it does not establish why replacement
did not occur. Only one project mod folder was found in the installed sdk_mods.

On October 9, 2026 at 21:45–21:47 America/Los_Angeles
(October 10 04:45–04:47 UTC):

- Native insertion/registration again succeeded with one inert Overclock and
  both original skills. The verified session had one owned local player and
  one owned roster entry in listen_host mode.
- Four completed snapshots began at 04:46:07.066Z, 04:46:07.834Z,
  04:47:54.030Z and 04:47:54.563Z. All reported PRI points 1 general / 0 specialist,
  Overclock grade 0 / maximum 1, index 14 / tier 7, unlocked True, requirement 0.
  Both original definitions had one runtime entry at grade 0.
- At 04:47:55.146Z, cancellation verified original skills MorePep/Myelin and
  cells True/False/True restored. The second cancellation had no remaining
  patch; observers stayed zero. No ERROR or Traceback appears in the log.
- The new enum/constraint/UI-priority details were absent because v0.2.3 was
  not loaded. This run cannot validate those changes.
- BL2 was not running when Codex checked after preserving the log.

Log SHA256:
`d684add928bc46cbf7a5a27356282a2df1b87bbdb9dca0724d49b6aed05c7482`.
The v0.2.3 ZIP remains unchanged with SHA256
`4573834f5bfad6f8eb4bc8c34051c3edfa4e893ba22e358ce5761431d1e17de6`.

No runtime change or new version is needed for this result. Replace the installed
project folder from the existing v0.2.3 ZIP with BL2 closed, then confirm the
MODS title says `UVH v0.2.3 - OVERCLOCK UPGRADE DIAGNOSTICS` before ARM/Continue.
If it still says v0.2.2, stop before arming. Use the existing read-only test,
CANCEL and exit; preserve the log before another launch. Do not spend points,
edit/restore saves, add effects or infer purchase eligibility from these reads.
