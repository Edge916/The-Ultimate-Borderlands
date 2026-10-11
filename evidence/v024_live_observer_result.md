# v0.2.4: live setup/stop/restoration passed; zero observed calls

The user initially said "done" and described an unsuccessful in-map arm,
returning to main menu, arming and loading again, then button 5 working.
They subsequently confirmed that all three skills were highlighted after
button 5. They also clarified that BL2 was still open and button 3 had not
yet been pressed. After the follow-up they pressed 3 and closed BL2, confirming
"Done — restored and exited". Do not mistake the first report for a completed
restoration or rely on the initial process-name probe as proof of closure.

The initial snapshot is v024_user_test.log (16459 bytes). The completed log is
v024_upgrade_observers_zero_calls_and_restored.log (20349 bytes); it extends the
initial snapshot. Both are preserved byte for byte. Installed pyproject is
v0.2.4 and installed runtime SHA256 matches the workspace/versioned package.
No source code changed during this review. Keep all four versioned ZIPs intact.

## Observed sequence (October 10 UTC / October 9 Pacific)

- 05:38:03.692, 05:38:04.917 and 05:39:49.448: ARM refused because Gaige was
  already loaded; it required returning to main menu. Three early observer-start
  attempts also refused because there was no owned node record. No insertion
  or diagnostic hooks were started by these attempts. The user recalls button
  4 in the early sequence; the preserved log contains no button-4 snapshot
  headers, so do not infer a completed snapshot from that recollection.
- 05:40:46.690: ARM accepted at main menu. A repeat press reported already armed.
- 05:40:50.966–.973: PRE verified NetMode=2/listen_host, one owned local player
  and one owned roster player. It constructed the independent inert definition
  and verified insertion before the native initializer. Runtime readback had
  one candidate and both originals among 39 skills, node grade 0/index14/tier7,
  first-tier indices [13,14,15]. bUnlocked=False at this initialization snapshot;
  later tier unlock state was not sampled. This initial value also occurred in
  earlier successful runs and is not evidence of a persistent locked tier.
  Initialization observers were removed (remaining=0).
- 05:41:03.856: START v0.2.4 registered both POST observers. Preflight passed
  loaded function descriptors, SDK enum type, current owned tree, inert node,
  solo rosters and known points/ranks/indices. PRI points=(1,0), ranks=(0,0,0)
  in node/MorePep/Myelin order. A repeat start correctly refused an active trace.
- The user confirmed opening Skills and highlighting all three definitions.
  The log itself does not show UI navigation events or selected UI objects.
- 05:41:32.672: STOP verified final points=(1,0), ranks=(0,0,0), unchanged from
  start. remaining=0, captured=0, callbacks=0, skipped=0; all six summaries [].
  The observer window was about 28.8 seconds, below the 90-second bound.
  Another STOP at 05:41:33.767 remained zero. There was no timeout/error abort.
- 05:44:44.923–.924: after the clarification, CANCEL again verified observers
  zero, then RESTORE result=True: original skills MorePep/Myelin and cells
  True/False/True restored via assignment. NATIVE ARRAYS RESTORED was logged.
- 05:44:45.939: another cancellation had no remaining initialization patch
  and observers stayed zero. The user confirmed exiting the game afterward.
- No ERROR or Traceback appears in the completed log. The SDK's unrelated
  deprecated-legacy-import warning remains present.

## What passed and what remains unknown

v0.2.4's engine-tested paths now include in-map ARM/start refusal, accepted
menu ARM, insertion/runtime registration, observer preflight/registration,
duplicate-start refusal, final direct state check, observer removal, native
array restoration and repeated cancellation. The installed version is correct.
The user's "it worked" supports node visibility/setup, not an observed upgrade
result. Sampled points/ranks were unchanged; save-file equality is not proven.

Zero callbacks means neither installed observer received a call during the
window. It is not an ownership-filter rejection (skipped was also zero), a
returned failure reason, or proof that either function never runs elsewhere.
Cause remains unresolved: these query paths may not be reached by ordinary
highlighting, another UI path may be active, or dispatch/hook behavior may differ.
Do not choose between those hypotheses without evidence. The callbacks' actual
UI ownership/selection/return wrapper behavior remains mock-tested only.
Cost, eligibility, purchase, refund, persistence and the node effect are unverified.

Do not ask the user to repeat the same two-hook test or force a query by buying.
Next useful work is a bounded, opt-in trace of loaded UI navigation/refresh
functions plus direct owned-UI selection data, using exact discovered metadata
and all existing solo/tree/point/rank guards. Confirm observed functions and
ownership rather than guessing paths, invoking queries or bypassing rules.
Purchase work still requires explicit user scope and point/grade/save recovery.

## Preserved hashes

| Artifact | SHA256 |
|--|--|
| Initial in-progress log | `05fd15067c53b0553d6b71ae99ced9bef413170abaeceb8897d6522f1a0b5bdc` |
| Completed log | `f4c0e99d17ac743339eabb5381d31d3f78be80bf0b9fc328ec32f57518058c8b` |
| v0.2.4 runtime (installed/workspace) | `dd51d0ac5f4b2bd0bad95067f681dde22675f9d219950230808c75f540f2c7ed` |
| Preserved v0.2.4 install ZIP | `d1aa246adcca296cefb359d1ffc5c1a22fd46685eeaf77accca4468a6f85ca42` |

57 existing simulated tests remain applicable; runtime did not change.
Documentation-only updates rebuild the default ZIP while preserving the
versioned ZIP, with syntax/isolated import/layout/source checks repeated.
