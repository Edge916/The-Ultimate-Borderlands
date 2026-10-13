# v0.2.17 definition-name log reviewer

This standard-library reviewer checks the bounded text emitted by the accepted
[v17 implementation](deathtrap_callback_definition_name_implementation.md),
commit `db0a3f9e2ee267debdb164514d5b100dc5a78521` /
[draft PR 37](https://github.com/Edge916/The-Ultimate-Borderlands/pull/37).
It implements the separately reviewed
[Name design](deathtrap_callback_definition_name_design.md). V17 has no live
capture yet. The checks below are offline fixtures, not a new game run.

From a checkout, run Python on
`scripts/review_deathtrap_callback_definition_name_log.py <log-path>`.
It reads at most 16 MiB plus one byte, prints a bounded JSON report and returns:

| Exit | Meaning |
| --- | --- |
| 0 | COMPLETE_LOG_TEXT: all reader sections are consistent, closed and resolved without recorded failure. |
| 1 | Partial, refused, invalid or absent reader text. |
| 2 | Bounded input/read/type/encoding error. |

Schema version 1 reports `reader_version=0.2.17`. COMPLETE_LOG_TEXT establishes
transcript consistency only. It cannot verify log origin, owner actions,
installation, process exit, actual native handles, lifetime or duration effect.
Native ownership, summon generation, engine clock, installation, owner protocol,
authenticity and engine behavior remain NOT_ESTABLISHED; both native readiness
booleans remain false. All original effect gates and dependencies remain intact.

## Name grammar

Only the new `[UVH-CALLBACK-NAME]` prefix and exact START version 0.2.17 are
accepted. EVENT requires one `name` field immediately after `definition`.
The script preserves the corrected v16 control, counter and cleanup rules in
its own standalone file; the original v16 parser is neither changed nor imported.

| Controller / definition | Name | Four stages / total |
| --- | --- | --- |
| NULL_INSTIGATOR / NOT_READ | `-` | 58,49,0,0 / 107 |
| OTHER_CONTROLLER_CLASS / NOT_READ | `-` | 58,50,0,0 / 108 |
| OTHER_WRAPPER / NOT_READ | `-` | 58,50,1,0 / 109 |
| SAME_WRAPPER / NULL_DEFINITION | `-` | 58,50,36,50 / 194 |
| SAME_WRAPPER / OTHER_NAME | Exact ASCII identifier unequal to Skill_DeathTrap | 58,50,36,52 / 196 |
| SAME_WRAPPER / DEATHTRAP_NAME | Exactly Skill_DeathTrap | 58,50,36,52 / 196 |

An identifier contains 1..128 letters, digits or underscores. No clipping,
Unicode/case conversion, suffix alias or path inference. Names such as NOT_READ
and NULL_DEFINITION are valid OTHER_NAME identifiers, distinct from the absence
token. A Name match is a primitive observation at attempted PRE entry, including
when another hook blocks execution. It establishes no summon association,
unique native instance, ownership, successful deactivation or lifespan.

Each session's ordered `events` list contains only line, epoch, ordinal, attempt,
the two fixed classifications and a locally validated Name. Absence becomes JSON
null. Contradictory branch/name labels, invalid budgets, local epoch/order or
sequence errors never export that record's identifier. Issues retain only fixed
codes and line numbers, without malformed input, unrelated SDK text, exception
bodies or object paths. A valid identifier may still contain personal text in a
modded game; the alphabet is not a universal privacy guarantee. Public export of
any later raw capture still requires review of its exact contents and approval.

## Closure and limits

Bare reader records, project records and the observed bounded SDK INFO frame
are accepted with strict UTF8 and LF/CRLF. Old/mixed/nested/unknown/clipped
`[UVH-CALL` frames, malformed or extra fields, noncanonical/out-of-range numbers,
branch/stage/counter contradictions, duplicate/out-of-order events, bad restarts
and a missing final newline are rejected.

The existing 64-attempt/24-classification limit and exact six operation branches
are checked. OVERLAP remains a refused control note, not another accepting START
or an identified operator click. Reentry does not invent attempts. Refusal,
error, failed registration, uncertainty and failed removal history remain visible
after a successful cleanup retry. Repeated resolved STOP/OUTCOME pairs are legal.
TIME, CLOCK or removal activity after an earlier pair needs its own fresh pair;
an earlier closure cannot certify a truncated tail or permit a pending restart.

Bounds are 16 MiB input, 100,000 lines, 16,384 bytes per input line, 4,096 reader
records, 128 sessions and 128 retained issues. Issue count and truncation flag
retain overflow information. A project record is at most 384 UTF8 bytes including
the full project prefix; the SDK header and newline are checked separately.
No background timer or native-clock conclusion is added by the reviewer.

At most 24 locally valid events per session bound identifier JSON to at most
3,072 events across 128 sessions, with at most 128 ASCII bytes per Name, and also
subject to the global record cap. An invalid twenty-fifth event cannot grow the
identifier list. The maximum-session fixture contains 3,584 records and 3,072
128-byte identifiers; its entire JSON report remains below 1.5 MB. STOP history
and classifications also remain bounded by input records and fixed labels.

## Actual verification and preserved evidence

Sixty independent tests run the new parser: 42 adapted control tests exercise
this new format, including six actual inert runtime branch transcripts and
registration/removal/reentry/stop/time/error paths; 18 additional tests cover
Name fields, privacy, exact boundaries, contradictory labels, mixed/clipped
frames, maximum identifier output and frozen capture relationships. No tests
inherit another suite or duplicate its IDs. All previous 700 unique tests remain
unchanged. The full run, syntax, package and preservation results are recorded in
[the companion checks](../evidence/deathtrap_callback_definition_name_log_review_checks.json).

The initial direct targeted run had one Windows sandbox temporary-folder error;
workspace-confined fixtures resolve it without skipping any check. A subsequent
targeted run found a test referencing the wrong manifest key; corrected it to
the actual diagnostic/offline_review field. The final 60-test run has no failures,
errors or skips. The prior parser, transcripts and manifest were not edited.

The immutable real
[v16 log](../evidence/deathtrap_callback_local_reader_user_test.log) still returns
its entire frozen manifest report under the original corrected reviewer:
COMPLETE_LOG_TEXT, one SAME_WRAPPER/OTHER_NAME event and OBSERVED_FILTERED, with
the original OVERLAP and four resolved STOP pairs retained. The new parser
rejects that log as v17 evidence; it cannot recover the omitted old Name.
Owner natural end, trigger attribution and SDK header intervals remain separate
from reader assertions. No repeat v16 test is requested.

All 216 accepted base files, 17 original versioned ZIPs, prior logs/manifests/
tested snapshots, complete frozen v12-v16 reports and immutable inventory
relationships are preserved. The v17 ZIP remains the accepted original; this
task has no runtime/version/package changes. Source syntax compilation and inert
project mocks do not import, execute or compile a real SDK or SDK stub.

Hosted CI, native SDK/binary behavior, game installation, owner protocol, save/
private-backup access, purchase, summon, effect, support messages, merge and release
are not run. These four new files require their own exact public approval and
deliberate acceptance review. After acceptance, a later capture task still needs
separate approval for the exact ZIP/commit and location-specific owner protocol:
main menu Offline Gaige/title without ARM, Continue fully into the map, START 22,
a separately approved ordinary Deathtrap use, STOP 23/CANCEL 3 in-map and full
desktop exit before preservation. This is a prospective layout, not a request
to run it now. Refusal/unavailable skill/time bound/silence is preserved without
retry. No new owner run is authorized here.
