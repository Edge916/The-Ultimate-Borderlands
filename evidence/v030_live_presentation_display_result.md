# v0.2.10 live display comparison and reported purchase

The restarted read-only run completed four snapshots with23/24 fields verified
each. All18 native Boolean fields were read; five of six Attribute identities
were verified. Myelin's second Attribute failed the exact declared-class check
and remained UNAVAILABLE. Points/ranks were unchanged across every captured
snapshot. Native arrays were restored, observers0 and process closed.
Runtime/pyproject and the original tested ZIP are unchanged in this review.

## Separate user-reported purchase

The user reported: "done i spent a point in the overclock skill and it went
to 1 of 1 i alt f4'd to not save restarted and did it your way just to give
you some extra data".

This is a user-observed one-point purchase and visible rank1/1 in an earlier
process, outside the requested read-only test. Record it as useful positive
UI purchase/rank evidence, not a demonstrated purchase defect. The retained
log starts with the restarted process and has no grade1 or purchase-event
capture. It cannot independently establish the transaction/cost, first-run
point decrement, save behavior or duration effect. No screenshot of that
purchase was provided. This report does not authorize further point spending,
automated purchases, grade/point repair, save edits or automatic node effects.

The restarted run independently verified points=(1,0), ranks=(0,0,0) at all
four BASELINE/FINAL pairs. Thus its captured session began with one unspent
point and Overclock grade0, and stayed there during the inspections. This is
evidence of the reset state after restart, not an audit of save files or proof
that Alt+F4 always prevents saving. No saves were parsed, copied or edited in
this review, and no backup restore/point refund was attempted. Do not repeat
the purchase to recover missing first-run evidence. A later controlled purchase
still requires explicit scope and a point/grade/save recovery plan.

## Installation and preserved evidence

- `evidence/v030_user_test.log`:259,457 bytes, SHA-256
  `88a79e741abb6b217f8f8a23c42e14578c11c75f2686abcfecc13d2c74e294fb`.
  Exclusively captured before relaunch, with a second source-byte stability check.
- Original `dist/UltimateVaultHunterDeathtrapBoost_v0.2.10_folder_install.zip`:
  32,742 bytes, SHA-256
  `962d5c11041b2d1db727d8ca130197a2a06e0fe3464b29cc64ac178ba0dc10fa`.
- Installed runtime/pyproject/README matched original ZIP and source before
  documentation edits. Exact tested files are retained under
  `archive/tested_runtime/v0.2.10`.

| Tested file | SHA-256 |
|--|--|
| __init__.py | 4f34082483c0d14715f708c9c8c61d42bcfe9bb262c23445ce9808489bc7bdbb |
| pyproject.toml | cd8a2e28c91e15b30bd8d5188f64864ed7c26cea3d9017cd3483862df558ba5f |
| README.txt | 4b6fb1f42297f76f737e9ebf87a517019d4b23db47c33fe1fc348752cbe82fa5 |

Fresh SDK initialization2026-10-10 20:45:58.416Z. ARM20:46:41.490;
repeat ARM20:46:42.716 refused an already armed experiment. PRE20:46:46.761
verified named listen_host, one matching local player and one matching roster
player. Native initialization registered one inert grade0 node index14/tier7
among39 skills, keeping both originals. Initialization observers were removed.

## Captured read-only data

Four calls:20:47:00.724-01.334,20:47:01.340-01.943,
20:47:01.997-02.577 and20:47:03.129-03.702Z. All arrays were known and
all six presentation references were sampled without a cap in each call.

| Target | Count/sample | Verified flags | Known Attributes | Present/absent | Display |
|--|--|--|--|--|--|
| UVH_DeathtrapOverclock | 0/0 | 0/0 | 0/0 | 0/0 | NOT_APPLICABLE |
| MorePep | 4/4 | 12/12 | 4/4 | 4/0 | VERIFIED |
| Myelin | 2/2 | 6/6 | 1/2 | 1/0 | PARTIAL |

The loaded scalar name/declaring owner/type/flags3/dimension1/recorded-offset
checks passed for the sampled fields, including the Attribute ObjectProperty
declared UClass named AttributeDefinition. Owner acceptance is enforced by the
runtime, not printed separately. Actual SDK BoolProperty reads returned this
same vector for every native presentation entry in every call:

| Field | Observed value |
|--|--|
| bDontDisplayNumber | False |
| bUseCustomNumberPlacement | True |
| bEnableTextColor | True |

These direct values do not prove native formatting/color/placement semantics.
No packed masks, templates, attribute values or formatter calls were used.

Five non-None SDK Attribute objects matched the exact declared Class and
passed descriptor/current-reference/Class rechecks around their bounded paths:

| Skill/index | Verified AttributeDefinition path |
|--|--|
| MorePep/0 | D_Attributes.StatusEffectModifiers.InstigatedShockStatusChanceModifier |
| MorePep/1 | D_Attributes.StatusEffectModifiers.InstigatedIncendiaryStatusChanceModifier |
| MorePep/2 | D_Attributes.StatusEffectModifiers.InstigatedCorrosiveStatusChanceModifier |
| MorePep/3 | D_Attributes.StatusEffectModifiers.InstigatedAmpStatusChanceModifier |
| Myelin/0 | D_Attributes.DamageTypeModifers.ShockImpactDamageModifier |

The spelling DamageTypeModifers is the logged game path. Myelin/1's
AttributePresentationDefinition_0 (the shield-capacity template in v0.2.9)
produced `status=UNAVAILABLE ValueError: 'Attribute payload is not the exact
declared SDK object class'` four times. No payload path was read or logged.
Its actual wrapper/class, inheritance and identity are unobserved. Do not
assume it is None, a specific subclass, a broken native skill or a safe
substitute for the declared class. Its three Boolean fields remain verified.

Each END reported complete_targets=2/3, fields=23/24, observers_added=0.
Across four calls:96 VALUE records,92 VERIFIED and4 identical UNAVAILABLE;
24 unique records. No ABORT or ERROR/Traceback.780 reused SCHEMA messages
are metadata/membership rechecks, not780 snapshots. No observer START calls.
All four FINAL comparisons matched points=(1,0)/ranks=(0,0,0),
unchanged_from_start=True. They cover the captured second-process inspections,
not the unlogged first purchase or every moment before exit.

## Cleanup, preservation and next direction

CANCEL20:47:31.762 verified RESTORE result=True with original MorePep/Myelin
and cells True/False/True. All observer families reported remaining0.
Repeated cancellations20:49:00.490 and20:49:02.973 found no patch and hooks0.
The existing legacy-import deprecation warning remains. The user reported
completion and review found Borderlands2 process count0.

All ten original v0.2.1-v0.2.10 ZIP hashes/integrity/layout and four exact
tested snapshots v0.2.7/v0.2.8/v0.2.9/v0.2.10 were checked unchanged.
Prior log/PNG preservation is checked alongside the current runtime hashes.
The151 prior mocks apply to unchanged code; this docs-only review does not
repeat them. Only documentation/default ZIP may change after preserving the
tested README. No game/SDK/save installation or writes by Codex.

The read-only data is useful despite one refused Attribute: native flags and
five identities are now verified. Do not repeat the same test to reconfirm
them or relax the exact-class guard. A next bounded metadata design can report
only the refused payload's SDK wrapper status and loaded actual UClass identity/
bounded class ancestry, after revalidating the property/current reference.
Unknown metadata refuses. No attribute values/evaluation, native formatters,
copies, overrides or gameplay writes. Its actual class/ancestry must be observed
before considering compatibility rules; names alone do not establish inheritance.
No next runtime or game test is prepared in this review. The user-reported
rank purchase is progress; persistence and the +15-second node effect remain
unverified. The node's effect remains intentionally inactive.


## Documentation package verification

After the review, runtime syntax and the rebuilt default ZIP's inert isolated
19-option import, integrity, exact three-file layout and source equality
passed. All46 protected runtime/original-ZIP/snapshot/log/PNG files remained
unchanged; the39 protection hashes recorded at build time were also rechecked.
The default ZIP alone received the updated README: 32841 bytes,
SHA-256 `4876e957b22be6510280c8d1eb5fe79c72a42358890eabf74b04940de409aac0`. Original v0.2.10 retains its tested README.
No runtime repair/new build or game/SDK/save write occurred.
