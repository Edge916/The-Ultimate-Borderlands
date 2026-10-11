# Next development step: resolve the native access contract

The latest game-tested diagnostic is **v0.2.15 - PASSIVE MANAGER EVENTS**.
Its [preserved capture](../evidence/deathtrap_passive_event_capture_manifest.json)
and [raw log](../evidence/deathtrap_passive_event_user_test.log) pass the strict
reviewer as COMPLETE_LOG_TEXT / exit 0. One START registered DeactivateSkill
PRE; attempts=0, events=0 and outcome=NOT_OBSERVED. Setup and explicit
stop/cleanup are documented. No natural owned manager entry was observed.
Read the [readiness result](../evidence/deathtrap_passive_event_live_readiness_result.md)
for the separate process/package checks, protocol deviations and limits.

The owner confirmed STOP21, CANCEL3 and full exit. A separate visible-failure
report was NOT_REPORTED. Both logged baseline/final points=(1,0), ranks=(0,0,0)
match; zero owned handles/uncertainty/cleanup failures and earlier observer
families follow. Arrays restore independently of Duration or save recovery.
Retain the refused second ARM, repeated STOP and TIME at explicit control.
SDK header times span 44.228 seconds versus about 20 requested; the 30-second
limit is checked on calls/controls, not by a background timer or engine clock.

No repeat of the silent run is requested. v13/v14 metadata is complete but
does not supply callable signatures or object lifetime. v15 ignores callback
obj/args/ret/func and returns exact None; the SDK still converts wrappers.
The original effect-design task remains gated on actual READY_FOR_EFFECT_DESIGN,
and implementation/capture dependencies remain intact.

## Evidence to read

- [v13 owner metadata assessment](../evidence/deathtrap_lifecycle_readiness_result.md).
- [v14 parameter-class assessment](../evidence/deathtrap_parameter_schema_readiness_result.md).
- [v15 readiness](../evidence/deathtrap_passive_event_live_readiness_result.md).
- [Native identity/lifetime research](../evidence/deathtrap_native_adapter_evidence_research.md).
- [Callback access audit](deathtrap_callback_access_feasibility.md) and its
  [checks](../evidence/deathtrap_callback_access_feasibility_checks.json).
- [Exact-original cleanup contract](overclock_identity_cleanup_contract.md).
- The complete [SDK documentation request #97](https://github.com/bl-sdk/pyunrealsdk/issues/97)
  and any actual response. Submission alone is not an answer.

Installed mods_base 1.12 documents
[Willow KEEP_ALIVE=0x4000](https://github.com/bl-sdk/mods_base/blob/a8c0e36ec902e6e5841c8cf3d4845aa5da352ae6/__init__.py#L134)
as preventing collection. This is a retention capability, not automatic
retention by copied hook arguments; setting it writes a native object.
Safe initial access, explicit destruction, other flag owners, bit restoration
and exact-original cleanup remain unresolved. Selected installed init/hook
files match the v1.12 pin after line-ending normalization, with different raw
bytes. The startup prefixes agree with selected native source pins; binary
build options and active function-lock configuration remain unmatched.

## Bounded next result

When real SDK guidance is available, read the full reply and cited exact
revision/source. Record what it establishes and what remains unsupported:

1. Object validity during native conversion and reads, including dispatch
   thread, GC, explicit destruction and the optional function-call lock.
2. GIL wait, prior script argument evaluation, reentry/nested hooks and native
   calls that release the GIL; validation before the first dereference.
3. Supported comparison within a callback and exact-original generation or
   lifecycle evidence for later cleanup, including address reuse.
4. Copied argument storage versus pointee retention and any supported flag
   ownership/restoration contract; no flag writes in a read-only review.
5. A supported manager-to-local-controller relationship and a meaningful
   natural observation that could provide unique owned-instance evidence.

If unresolved, retain NOT_READY_FOR_CALLBACK_OWNERSHIP_READER and the native
adapter/effect gates. Source absence is bounded, not an observed crash or
universal SDK limitation. Emulated WeakPointer/model epochs/names/time cannot
manufacture exact native generation. Python mocks prove fixture behavior only.

After sufficient evidence, refine and claim a separate diagnostic design
with exact file scopes and useful acceptance. A runtime change, installation
and owner game protocol require their own review and explicit applicable
authorization. No lifecycle reader, native call, summon, flag/Duration write,
purchase, save/private-backup operation, co-op, merge or release is proposed
by this continuation document. Keep grade-zero guards unchanged. Node
CANCEL/disable do not invoke manual Duration restore; array rollback cannot
refund points, undo saves or clear cached player/UI trees.

Preserve raw captures, manifests, source snapshots and all original versioned
ZIPs. The tested/package READMEs are frozen historical preparation text; use
current evidence for completed status. This repair changes six current
documents only, with no package rebuild. Read current Pair Project results
between tasks and record actual checks, tests not run and deliberate review.
