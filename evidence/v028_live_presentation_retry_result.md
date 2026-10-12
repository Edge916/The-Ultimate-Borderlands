# v0.2.8 live presentation snapshot: verified counts and restoration

The user reported done after selecting item4 in the mod options. The complete
new log was preserved separately from the first run before relaunch:
`v028_presentation_retry.log`, 38,263 bytes, SHA-256
`348d9ce354c6ec3853813de5eecba2c258d8fad72c8aab8280d26d4ec8a37229`.
No BL2 process was found at review. The installed runtime, pyproject and README
still matched the original v0.2.8 ZIP byte for byte. Current workspace README
has documentation changes only; runtime/pyproject matched workspace too.

This completes the presentation-count/reference diagnostic. Two snapshots
accepted the loaded schema and verified all three arrays. Presentation class
metadata was explicitly CAPPED after16 fields, so it was not fully enumerated.
No presentation instance values, attribute/effect data or formatter output
were read by this diagnostic. The existing node stays inert.

## Live results

Log times below are UTC, 2026-10-10. Fresh process startup was08:58:43.807.
Gaige initialization09:00:53.367–.371 verified listen_host, one owned local
player and one owned roster player, one grade0 node at index14/tier7 among39
skills, both original skills present and initialization observers remaining0.
A repeat ARM refused because already armed; it did not create another node.

| Snapshot | BEGIN | FINAL/END | Sampled baseline and final |
|--|--|--|--|
| 1 | 09:02:34.856 | 09:02:34.883 | PRI points=(1,0), ranks=(0,0,0), unchanged_from_start=True |
| 2 | 09:02:36.014 | 09:02:36.041 | PRI points=(1,0), ranks=(0,0,0), unchanged_from_start=True |

Each call samples its own baseline; the two identical observations do not
prove continuous monitoring between or after calls.

| Target | Verified presentation count | Verified references | Array sample capped? |
|--|--|--|--|
| UVH_DeathtrapOverclock | 0 | 0/0 | False |
| MorePep | 4 | 4/4 | False |
| Myelin | 2 | 2/2 | False |

All three SCHEMA lines in both snapshots reported ArrayProperty with
ObjectProperty inner and AttributePresentationDefinition element class,
flags71303179/offset156. Every SUMMARY reported array=VERIFIED and
metadata=CAPPED. Both END lines reported verified_arrays=3/3,
observers_added=0. There were no UNAVAILABLE or ABORT messages.

All six presentation object identities were verified each time. Paths share
the prefix `GD_Tulip_Mechromancer_Skills.LittleBigTrouble.`:

- MorePep: `MorePep:AttributePresentationDefinition_0`, `_1`, `_2`, `_3`.
- Myelin: `Myelin:AttributePresentationDefinition_45` and
  `Myelin:AttributePresentationDefinition_0`.

The four-reference sample bound covered every entry in these arrays. The
separate class-metadata bound did not cover every class property.

## Observed raw presentation metadata

Each snapshot reflected the same16 raw descriptors, once per common class.
Every observed ArrayDim was1. BoolProperty entries share offset116; no packed
Boolean masks were inferred and no instance values were read.

| Property | Raw type | Flags | Offset |
|--|--|--|--|
| BasePriority | FloatProperty | 3 | 60 |
| Attribute | ObjectProperty; declared AttributeDefinition | 3 | 64 |
| Description | StrProperty | 4227075 | 68 |
| NoConstraintText | StrProperty | 4227075 | 80 |
| Suffix | StrProperty | 4227075 | 92 |
| Prefix | StrProperty | 4227075 | 104 |
| bIncludeSuffixInTranslation | BoolProperty | 3 | 116 |
| bIncludePrefixInTranslation | BoolProperty | 3 | 116 |
| bBiggerIsBetter | BoolProperty | 3 | 116 |
| bDisplayAsPercentage | BoolProperty | 3 | 116 |
| bDisplayPercentAsFloat | BoolProperty | 3 | 116 |
| bDisplayAsInverse | BoolProperty | 3 | 116 |
| bDontDisplayNumber | BoolProperty | 3 | 116 |
| bDontDisplayPlusSign | BoolProperty | 3 | 116 |
| bUseCustomNumberPlacement | BoolProperty | 3 | 116 |
| bEnableTextColor | BoolProperty | 3 | 116 |

Fields after this cap remain unobserved. Names/types identify possible next
direct reads; they do not establish formatting semantics or attribute values.

## Cleanup, interpretation and preservation

CANCEL09:02:42.287 reported all owned observer families remaining0 and
RESTORE result=True, with MorePep/Myelin and True/False/True cells restored.
Repeat cancellation09:02:43.108 found no patch and observers remained0.
No ERROR/Traceback appears; the existing legacy-import warning remains.
Array rollback cannot refund points, restore grades/save data or clear caches;
full process exit was checked. No game/SDK/save files were edited by Codex and
no saves were parsed.

Overclock's empty presentation array is now a verified native observation,
rather than a constructor assumption. MorePep/Myelin's nonempty arrays give
a concrete comparison. Together with v0.2.7's empty Overclock grade-preview
return this is consistent with missing presentation data, but **does not prove
causation**, rendered orange-text behavior, eligibility/cost, purchase failure
or a functioning duration effect. The first-run screenshot's rendered
[Enter] Spend Point hint remains separate evidence.

All eight original v0.2.1–v0.2.8 ZIP hashes/integrity and exact tested snapshots
v0.2.7/v0.2.8 were verified unchanged. The previous v0.2.7 log, first v0.2.8
log and PNG retain their original hashes. Runtime/pyproject are frozen.
The existing108 mocks still apply to unchanged runtime; this review did not
repeat them. Documentation may rebuild only the default ZIP.

Next design: a bounded read-only comparison of exact observed presentation
string/display fields, with loaded metadata validated before every payload
read and the same unchanged current-state guards. Start with Description,
NoConstraintText, Prefix and Suffix; use an explicit small observed Boolean
allowlist if useful. No guessed unobserved fields, Attribute traversal/scalar
evaluation, copying presentations/effects/constraints, native formatter calls
or text overrides. Do not repeat v0.2.8 merely to reconfirm counts. A new runtime
needs meaningful refusal/bounds/state-change tests and package verification
before a new user game test. Purchases/effects/persistence/co-op remain separate
scoped milestones.

After the documentation review, runtime syntax and the rebuilt default ZIP's
isolated19-option import, integrity, exact three-file layout and source match
passed. Runtime/pyproject hashes, all eight original versioned ZIPs, both
tested snapshots and the checked logs/PNG remained unchanged. Only the default
ZIP received the updated README: 30,575 bytes, SHA-256
`c6ac6047f1962a54117c5d5a30f495a6c62ebd13c6ada4c284b8b994cfb9e6e8`.
No new runtime or game installation was performed during this review.
