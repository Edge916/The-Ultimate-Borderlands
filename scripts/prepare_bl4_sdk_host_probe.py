"""Offline SDK manifest preparation; synthetic fixture rehearsal, never an installer.

The CLI only reads the selected ZIP and creates one JSON manifest. Rehearsal
functions accept visibly inert bytes in an explicitly marked empty fixture.
They do not query Steam, execute SDK code, launch a game or access saves.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import zipfile

ARCHIVE_SHA256 = "602675446abed184169fa158be3c8bc81777a71203581e4a248eca8a3d00b5c7"
ARCHIVE_BYTES = 14752091
DESIGN_CHECK_SHA256 = "ebb983c4a12f2d892440dde18a83c95d0961c6920eda7801dc4ab2d50b29111a"
BUILD = "25372571"
LOADER = "OakGame/Binaries/Win64/dsound.dll"
MARKER = ".uvh-inert-fixture.json"
MARKER_BYTES = b'{"kind":"UVH_SYNTHETIC_ONLY","schema":1}\n'
INERT = b"UVH-INERT-FIXTURE\n"
DEVICE = re.compile(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", re.I)
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_EXPANDED = 128 * 1024 * 1024


class Refusal(ValueError):
    """No inference of success or permission from a refused operation."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative_path(name):
    if type(name) is not str or not re.fullmatch(r"[A-Za-z0-9._/-]+", name):
        raise Refusal("noncanonical archive path")
    parts = name.split("/")
    if any(p in ("", ".", "..") or p.endswith(".") or DEVICE.match(p) for p in parts):
        raise Refusal("unsafe Windows path")
    return name


def paths_checked(names):
    files, components = set(), {}
    for name in names:
        relative_path(name)
        folded = name.casefold()
        if folded in files:
            raise Refusal("duplicate case-insensitive file")
        files.add(folded)
        for i in range(1, len(name.split("/")) + 1):
            part = "/".join(name.split("/")[:i])
            previous = components.setdefault(part.casefold(), part)
            if previous != part:
                raise Refusal("case-insensitive component collision")
    for name in names:
        if any("/".join(name.split("/")[:i]).casefold() in files
               for i in range(1, len(name.split("/")))):
            raise Refusal("file is also a parent directory")


def archive_manifest(data):
    """Inspect a ZIP as data, including CRC; never extract or import its members."""
    if type(data) is not bytes or len(data) > MAX_ARCHIVE:
        raise Refusal("archive size/type")
    rows, explicit_dirs, expanded = [], [], 0
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 512:
                raise Refusal("too many archive entries")
            for entry in entries:
                name = entry.filename[:-1] if entry.is_dir() else entry.filename
                relative_path(name)
                mode = stat.S_IFMT(entry.external_attr >> 16)
                allowed = (0, stat.S_IFDIR) if entry.is_dir() else (0, stat.S_IFREG)
                if mode not in allowed or entry.flag_bits & 1:
                    raise Refusal("link/special/encrypted archive entry")
                if entry.is_dir():
                    explicit_dirs.append(name)
                    continue
                expanded += entry.file_size
                if entry.file_size > 32 * 1024 * 1024 or expanded > MAX_EXPANDED:
                    raise Refusal("expanded archive bound")
                raw = archive.read(entry)  # ZipFile checks this entry's CRC.
                rows.append({"path": name, "bytes": len(raw), "sha256": digest(raw)})
    except (zipfile.BadZipFile, RuntimeError, OSError, NotImplementedError) as exc:
        raise Refusal("invalid archive or CRC") from exc
    paths_checked([r["path"] for r in rows])
    if len(set(d.casefold() for d in explicit_dirs)) != len(explicit_dirs):
        raise Refusal("duplicate archive directory")
    paths_checked([r["path"] for r in rows] + [d + "/directory-marker" for d in explicit_dirs])
    return sorted(rows, key=lambda r: r["path"])


def directories(rows):
    return sorted({"/".join(r["path"].split("/")[:i]) for r in rows
                   for i in range(1, len(r["path"].split("/")))},
                  key=lambda p: (len(p.split("/")), p))


def prepare_manifest(data, design_bytes):
    if len(data) != ARCHIVE_BYTES or digest(data) != ARCHIVE_SHA256:
        raise Refusal("not the approved v0.3 archive")
    if digest(design_bytes) != DESIGN_CHECK_SHA256:
        raise Refusal("accepted design checks differ")
    accepted = json.loads(design_bytes)["official_archive"]["files"]
    rows = archive_manifest(data)
    expected = sorted(({k: r[k] for k in ("path", "bytes", "sha256")} for r in accepted),
                      key=lambda r: r["path"])
    if rows != expected or len(rows) != 63:
        raise Refusal("archive manifest differs")
    return {"schema": 1, "kind": "OFFLINE_PREPARATION_ONLY", "release": "v0.3",
            "archive_sha256": ARCHIVE_SHA256, "archive_bytes": ARCHIVE_BYTES,
            "expected_steam_build": BUILD, "loader": LOADER, "files": rows,
            "prospective_directories": directories(rows),
            "introduced_directories": "UNDETERMINED_UNTIL_APPROVED_TARGET_PREFLIGHT",
            "native_compatibility": "NOT_TESTED", "installation_authorized": False}


def no_redirect(path):
    """Reject every existing symlink/reparse ancestor before resolving containment."""
    path = Path(os.path.abspath(path))
    for part in reversed((path, *path.parents)):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise Refusal("symlink/reparse redirection")
    return path


def target(root, name):
    relative_path(name)
    root = no_redirect(root)
    path = no_redirect(root.joinpath(*name.split("/")))
    if not path.resolve().is_relative_to(root.resolve()):
        raise Refusal("target escapes fixture")
    current = root
    for part in name.split("/"):
        if current.exists():
            if not current.is_dir():
                raise Refusal("parent is not directory")
            if any(p.name.casefold() == part.casefold() and p.name != part for p in current.iterdir()):
                raise Refusal("existing case collision")
        current = current / part
    return path


def scan_fixture(root):
    """Bounded scan without following redirecting children."""
    seen = []
    def visit(folder):
        for child in folder.iterdir():
            no_redirect(child)
            seen.append(child)
            if len(seen) > 1024:
                raise Refusal("fixture tree bound")
            if child.suffix.casefold() == ".exe":
                raise Refusal("real executable in fixture")
            if child.is_dir():
                visit(child)
            elif not child.is_file():
                raise Refusal("special fixture entry")
    visit(root)
    return seen


def init_fixture(root):
    root = no_redirect(root)
    if not root.is_dir() or any(root.iterdir()):
        raise Refusal("fixture must be existing and empty")
    with (root / MARKER).open("xb") as stream:
        stream.write(MARKER_BYTES)


def fixture_guard(root, build, process_count):
    root = no_redirect(root)
    if type(build) is not str or build != BUILD or type(process_count) is not int or process_count != 0:
        raise Refusal("fixture build/process input")
    marker = target(root, MARKER)
    if not marker.is_file() or marker.read_bytes() != MARKER_BYTES:
        raise Refusal("not a synthetic fixture")
    scan_fixture(root)
    return root


def synthetic_payload(payload):
    if type(payload) is not dict or not 1 <= len(payload) <= 100 or LOADER not in payload:
        raise Refusal("synthetic payload shape/loader")
    paths_checked(list(payload))
    for raw in payload.values():
        if type(raw) is not bytes or not raw.startswith(INERT) or len(raw) > 262144:
            raise Refusal("only marked inert bytes may be copied")
    if MARKER in payload or any(p.startswith(".uvh-") for p in payload):
        raise Refusal("reserved fixture metadata")
    return [{"path": p, "bytes": len(raw), "sha256": digest(raw)} for p, raw in sorted(payload.items())]


class Journal:
    """Exclusive append-only JSONL intents/completions; fsync before fixture writes."""
    def __init__(self, path, root):
        self.path = no_redirect(path)
        if self.path.is_relative_to(Path(root).absolute()) or self.path.exists():
            raise Refusal("journal must be new and outside fixture")
        self.stream = self.path.open("xb")

    def record(self, event, **fields):
        self.stream.write((json.dumps({"event": event, **fields}, sort_keys=True) + "\n").encode())
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def close(self):
        self.stream.close()


def stage_fixture(root, payload, journal_path, *, build=BUILD, process_count=0, fault=None):
    """Fixture-only simulation; return receipt or retain journal after interruption."""
    root = fixture_guard(root, build, process_count)
    rows = synthetic_payload(payload)
    for row in rows:
        if target(root, row["path"]).exists():
            raise Refusal("existing fixture target")
    dirs = directories(rows)
    for name in dirs:
        path = target(root, name)
        if path.exists() and not path.is_dir():
            raise Refusal("fixture parent type")
    # A nonempty SDK-specific directory is an unexpected previous install.
    for name in ("sdk_mods", "OakGame/Binaries/Win64/Plugins"):
        path = target(root, name)
        if path.exists() and any(path.iterdir()):
            raise Refusal("unexpected SDK fixture contents")
    receipt = {"schema": 1, "kind": "SYNTHETIC_FIXTURE_RECEIPT", "files": rows,
               "introduced_directories": [d for d in dirs if not target(root, d).exists()]}
    journal = Journal(journal_path, root)
    try:
        journal.record("STAGE_BEGIN", receipt=receipt)
        for name in receipt["introduced_directories"]:
            path = target(root, name)
            journal.record("MKDIR_INTENT", path=name)
            path.mkdir()  # no exist_ok and no recursive creation
            journal.record("MKDIR_DONE", path=name)
        # Introduce loader last, so incomplete staging cannot enable this fixture.
        for row in sorted(rows, key=lambda r: (r["path"] == LOADER, r["path"])):
            path = target(root, row["path"])
            journal.record("COPY_INTENT", **row)
            if fault:
                fault("before_copy", row["path"])
            with path.open("xb") as stream:
                stream.write(payload[row["path"]])
                stream.flush()
                os.fsync(stream.fileno())
            if digest(path.read_bytes()) != row["sha256"]:
                raise Refusal("fixture copy mismatch")
            journal.record("COPY_DONE", **row)
        journal.record("STAGE_COMPLETE")
        return receipt
    finally:
        journal.close()


def recover_fixture_receipt(journal_path):
    """Read the write-ahead receipt, including interrupted staging; no mutation."""
    raw = no_redirect(journal_path).read_bytes()
    if len(raw) > 1048576 or not raw.endswith(b"\n"):
        raise Refusal("incomplete/bounded journal")
    entries = [json.loads(line) for line in raw.splitlines()]
    if not entries or entries[0].get("event") != "STAGE_BEGIN":
        raise Refusal("missing stage receipt")
    return entries[0]["receipt"]


def rollback_fixture(root, receipt, quarantine, journal_path, *, build=BUILD, process_count=0, fault=None):
    """Quarantine unchanged introduced fixture files; no recursive deletion."""
    root = fixture_guard(root, build, process_count)
    if type(receipt) is not dict or receipt.get("kind") != "SYNTHETIC_FIXTURE_RECEIPT" or receipt.get("schema") != 1:
        raise Refusal("invalid fixture receipt")
    rows, dirs = receipt["files"], receipt["introduced_directories"]
    paths_checked([r["path"] for r in rows])
    if LOADER not in [r["path"] for r in rows] or len(rows) > 100:
        raise Refusal("receipt loader/bound")
    prospective = directories(rows)
    if len(set(dirs)) != len(dirs) or any(d not in prospective for d in dirs):
        raise Refusal("receipt directory scope")
    allowed = {r["path"]: r for r in rows}
    existing = []
    for row in rows:
        path = target(root, row["path"])
        if path.exists():
            if not path.is_file() or path.stat().st_size != row["bytes"] or digest(path.read_bytes()) != row["sha256"]:
                raise Refusal("independently changed fixture file")
            if not path.read_bytes().startswith(INERT):
                raise Refusal("non-synthetic file")
            existing.append(row)
    for path in scan_fixture(root):
        relative = path.relative_to(root).as_posix()
        managed = any(relative == d or relative.startswith(d + "/") for d in
                      [*dirs, "sdk_mods", "OakGame/Binaries/Win64/Plugins"])
        if managed and relative not in allowed and relative not in prospective:
            raise Refusal("unknown introduced-directory child")
    quarantine = no_redirect(quarantine)
    if quarantine.is_relative_to(root) or root.is_relative_to(quarantine):
        raise Refusal("quarantine overlaps fixture")
    if not quarantine.is_dir() or any(quarantine.iterdir()):
        raise Refusal("quarantine must be empty")
    no_redirect(journal_path)
    if Path(os.path.abspath(journal_path)).is_relative_to(quarantine):
        raise Refusal("journal overlaps quarantine")
    journal = Journal(journal_path, root)
    try:
        journal.record("ROLLBACK_BEGIN")
        for row in sorted(existing, key=lambda r: (r["path"] != LOADER, r["path"])):
            source = target(root, row["path"])
            # Recheck after any injected/concurrent independent edit.
            if fault:
                fault("before_quarantine", row["path"])
            if digest(source.read_bytes()) != row["sha256"]:
                raise Refusal("fixture changed during rollback")
            destination = target(quarantine, row["path"])
            for name in directories([row]):
                folder = target(quarantine, name)
                if not folder.exists():
                    folder.mkdir()
            journal.record("QUARANTINE_INTENT", **row)
            with destination.open("xb") as stream:
                stream.write(source.read_bytes())
                stream.flush()
                os.fsync(stream.fileno())
            if digest(destination.read_bytes()) != row["sha256"] or digest(source.read_bytes()) != row["sha256"]:
                raise Refusal("quarantine verification failed")
            source.unlink()
            journal.record("QUARANTINE_DONE", **row)
        for name in sorted(dirs, key=lambda d: (-len(d.split("/")), d)):
            folder = target(root, name)
            if folder.exists():
                journal.record("RMDIR_INTENT", path=name)
                folder.rmdir()  # only empty introduced directories; never recursive
                journal.record("RMDIR_DONE", path=name)
        journal.record("ROLLBACK_COMPLETE")
        return {"status": "FIXTURE_RESTORED", "quarantined_files": len(existing)}
    finally:
        journal.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path, help="new JSON manifest outside the selected archive")
    args = parser.parse_args(argv)
    try:
        source = no_redirect(args.archive)
        if source.stat().st_size != ARCHIVE_BYTES:
            raise Refusal("archive size differs")
        checks = Path(__file__).resolve().parents[1] / "evidence/bl4_host_probe_design_checks.json"
        manifest = prepare_manifest(source.read_bytes(), checks.read_bytes())
        output = no_redirect(args.output)
        if output == source:
            raise Refusal("output equals archive")
        with output.open("xb") as stream:
            stream.write((json.dumps(manifest, indent=2) + "\n").encode())
        print(json.dumps({"status": "PREPARED_ONLY", "files": len(manifest["files"]),
                          "archive_sha256": ARCHIVE_SHA256, "native_compatibility": "NOT_TESTED"}))
        return 0
    except (Refusal, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": type(exc).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
