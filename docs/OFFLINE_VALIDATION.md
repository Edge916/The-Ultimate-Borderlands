# One command for offline validation

From a trusted repository checkout with a real Python 3.11 or 3.12 interpreter:

```text
python -B scripts/run_offline_validation.py --verbose
```

On the owner's Windows PC, the plain python command is an alias. Use:

```powershell
& 'C:/Users/jakec/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B scripts/run_offline_validation.py --verbose
```

The runner compiles current project Python under the shipped mod, scripts,
tests and any future design folder without executing it. It then discovers
all current `tests/test_*.py`, refuses duplicate IDs, zero tests or discovery
errors before test execution, and fails on errors, failures, expected failures
or skipped tests.
The count is dynamic; adding a test does not require updating a magic total.
Repository tests execute only in the established inert SDK harnesses. Archives,
SDK stubs, installed mods, game assets and saves are not test-discovery inputs.

Temporary test directories stay under a fresh workspace-contained directory,
which is removed after testing. Previous tempfile and bytecode settings are
restored even on failure. The runner uses its own interpreter to invoke the
unchanged [package verifier](../scripts/verify_package.py), which checks CRC,
exact three-file layout/source/syntax and an isolated inert import. It never
rebuilds an archive. This supports the actual Windows temporary-directory
restriction without changing any established test or game code.

Unittest progress goes to stderr. A JSON report goes to stdout; exit0 means all
three stages passed, exit1 means failure. The report includes actual discovered/
run/failed/errored/skipped counts, package output and elapsed time. Native engine
behavior is always NOT_ESTABLISHED. The local runner marks hostedCI NOT_CHECKED;
use actual hosted job results to verify hosted execution separately.

## CI configuration

The [workflow](../.github/workflows/offline-validation.yml) runs this same command
on Ubuntu and Windows with Python3.11 and3.12. These four hosted configurations
are proposed coverage until their actual jobs finish successfully. Only contents
read permission is requested; checkout credentials are not persisted. No SDK,
game assets, third-party Python packages, secrets, release or installation step.

Official release commits checked when preparing this workflow:

- [actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1):
  `3d3c42e5aac5ba805825da76410c181273ba90b1`.
- [actions/setup-python v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0):
  `5fda3b95a4ea91299a34e894583c3862153e4b97`.

Both are pinned to exact commits. Updating a pin requires reviewing the official
release and rerunning actual checks. This is ordinary push/pull_request CI,
without a privileged pull_request_target or workflow_run execution path.

## Validation record

Task32e4173b starts from accepted protocol6331b35 with runtime/package e32cfb1.
Only runner, meaningful runner regressions, workflow and this document change.
Record actual local counts/results below before submission. Full mock success
does not establish engine schemas, signatures, effects, save behavior or install
and process-exit evidence. Last game-tested build remains v0.2.11.

Actual local run: Windows/Python3.12.14, exit0, 290 unique tests (275 existing
plus15 new runner regressions), zero failures/errors/skips/expected failures,
all discovered tests run; 24.710seconds for the suite and25.718seconds overall.
Sixteen current Python files compile. The unchanged package verifier passes
CRC/layout/current-source/syntax and isolated inert import. All129 accepted
baseline files are preserved byte for byte; only the four claimed paths are new.

The first attempt refused before discovery because strict Windows handle
resolution denied readable workspace paths. Normal canonical resolution fixes
that compatibility issue; an outside-root path still refuses. Temporary test
directories work inside the workspace and their settings are restored.
Hosted jobs have not been run as part of this local result; inspect actual
job status for this exact published commit before claiming hosted success.
