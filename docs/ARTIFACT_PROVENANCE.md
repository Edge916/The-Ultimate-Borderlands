# Read-only artifact provenance checks

From this trusted checkout, use a real Python interpreter:

```text
python -B scripts/verify_artifact_inventory.py
python -B scripts/verify_artifact_inventory.py --check-current
```

The [inventory](../evidence/verified_artifact_inventory.json) records actual bytes
from accepted integration 1720b62, whose current runtime/package is reviewed
v0.2.12 at e32cfb1. It is selected project evidence, not a complete repository
manifest or a claim that every retained design is implemented.

Immutable entries are the 44 originals in
[v031_preserved_baseline.json](../evidence/v031_preserved_baseline.json), original
v11 and v12 versioned ZIPs, five immutable v11 capture/snapshot files and two
accepted research files: 53 unique files. Preserve these byte for byte. Provenance records
refer to the accepted protected manifest and capture/research/build commits;
the verifier compares supplied fingerprints but does not authenticate manifest
origin, SDK identities or machine/game observations.

Four current-build entries separately record the e32cfb1 runtime, pyproject,
README and default ZIP. Default verification does not require their hashes:
later intentional changes must not rewrite old immutable fingerprints.
`--check-current` explicitly checks the recorded prepared build and reports
current drift separately. When a new build is accepted, update current records
only in a new claimed inventory scope with actual source/artifact evidence.
Do not silently replace historical hashes to make a check pass.

The verifier reads each listed file twice within a 64 MiB bound, checks exact
size/SHA256, validates ZIP CRC/exact three-file layout and compiles archived
runtime syntax in memory. Declared aggregate unpacked ZIP size is bounded before
decompression. It never executes packaged code, imports SDK/game
modules, rebuilds/recovers/extracts an archive or writes an input. Its JSON
stdout and exit 0/1 distinguish success/failure. Missing or changed bytes, invalid
ZIPs, duplicate JSON/path records, traversal and self-hashing inventories fail.

Explicit snapshot relationships compare the original v7/v8/v9/v10/v11 archives
with their actual three-file frozen snapshots. The v11 historical README is
different from current v12 README; no equality is assumed between versions.
With `--check-current`, a separate relationship compares current default ZIP
with the three current source files. New/unlisted artifact-area paths are
reported without assigning original hashes or automatically accepting them.
In particular, a future v12 game snapshot is not invented from prepared source.

Private backups/saves and unrelated paths are unsupported. No log content is
interpreted as a live result by this tool; engine behavior remains
NOT_ESTABLISHED and manifest origin remains NOT_CHECKED_BY_TOOL. A passing
fingerprint report does not establish new game tests, effects or save behavior.

## Validation record

Task 8521a5dc starts from accepted 1720b62. These four new files preserve all 133
baseline tracked files byte for byte. On Python 3.12.14, offline validation passed
319 unique tests (290 existing and 29 inventory regressions), with no failures,
errors, skips or expected failures. All 18 current Python files compiled; package
integrity, source equality and the existing isolated mock import passed.

The default verifier checked 53 immutable files, 12 versioned archives and five
snapshot relationships. The explicit current check also passed on four recorded
current files, one default archive and its source relationship. These checks ran
on repository bytes and inert fixtures. No game installation or live test ran.
