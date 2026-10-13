"""Filesystem refusal/recovery tests using harmless bytes, never the SDK runtime."""
import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_bl4_sdk_host_probe.py"
spec = importlib.util.spec_from_file_location("bl4_host_preparation", SCRIPT)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def zip_bytes(entries):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_STORED) as z:
        for name, raw in entries:
            z.writestr(name, raw)
    return output.getvalue()


class ArchiveTests(unittest.TestCase):
    def test_inert_archive_rows_and_directories(self):
        raw = zip_bytes([("sdk_mods/.stubs/example.pyi", b"never executed"), (p.LOADER, b"data")])
        rows = p.archive_manifest(raw)
        self.assertEqual(2, len(rows))
        self.assertEqual(p.digest(b"data"), rows[0]["sha256"])
        self.assertIn("sdk_mods/.stubs", p.directories(rows))

    def test_wrong_official_archive_refuses(self):
        with self.assertRaises(p.Refusal):
            p.prepare_manifest(zip_bytes([(p.LOADER, b"fake")]), b"{}")

    def test_invalid_zip(self):
        with self.assertRaises(p.Refusal):
            p.archive_manifest(b"not a zip")

    def test_archive_bound(self):
        with patch.object(p, "MAX_ARCHIVE", 5), self.assertRaises(p.Refusal):
            p.archive_manifest(b"123456")

    def test_expansion_bound(self):
        with patch.object(p, "MAX_EXPANDED", 5), self.assertRaises(p.Refusal):
            p.archive_manifest(zip_bytes([("file", b"123456")]))

    def test_member_crc_corruption(self):
        raw = zip_bytes([("file", b"original-payload")]).replace(b"original-payload", b"modified-payload")
        with self.assertRaises(p.Refusal):
            p.archive_manifest(raw)

    def test_symlink_zip(self):
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaises(p.Refusal):
            p.archive_manifest(zip_bytes([(info, b"outside")]))

    def test_special_zip(self):
        info = zipfile.ZipInfo("pipe")
        info.external_attr = (stat.S_IFIFO | 0o600) << 16
        with self.assertRaises(p.Refusal):
            p.archive_manifest(zip_bytes([(info, b"")]))

    def test_empty_directory_supported(self):
        self.assertEqual([], p.archive_manifest(zip_bytes([("folder/", b"")])))

    def test_directory_case_collision(self):
        with self.assertRaises(p.Refusal):
            p.archive_manifest(zip_bytes([("Parent/", b""), ("parent/file", b"data")]))

    def test_duplicate_directory(self):
        with self.assertRaises(p.Refusal):
            p.archive_manifest(zip_bytes([("Folder/", b""), ("folder/", b"")]))


class PathTests(unittest.TestCase):
    def test_unsafe_windows_names(self):
        for name in ("../escape", "/absolute", "C:/file", "folder\\file", "file:ads",
                     "file ", "file.", "a//b", "a/./b", "NUL.txt", "COM1", "x/LPT9.log",
                     "//server/share", "a/..", "a\x00b", "COM¹", "a\nb", "CONIN$"):
            with self.subTest(name=name), self.assertRaises(p.Refusal):
                p.relative_path(name)

    def test_case_duplicate(self):
        with self.assertRaises(p.Refusal):
            p.paths_checked(["a/File", "a/file"])

    def test_component_case_collision(self):
        with self.assertRaises(p.Refusal):
            p.paths_checked(["A/one", "a/two"])

    def test_file_parent_conflict(self):
        with self.assertRaises(p.Refusal):
            p.paths_checked(["folder", "folder/child"])

    def test_dot_files_allowed(self):
        self.assertEqual("sdk_mods/.stubs/.gitignore", p.relative_path("sdk_mods/.stubs/.gitignore"))

    def test_reparse_attribute_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = type("Stat", (), {"st_mode": stat.S_IFDIR, "st_file_attributes": 0x400})()
            original = Path.lstat
            def lstat(path, *args, **kwargs):
                return fake if path == root else original(path, *args, **kwargs)
            with patch.object(Path, "lstat", lstat), self.assertRaises(p.Refusal):
                p.no_redirect(root / "child")

    def test_symlink_mode_rejected(self):
        fake = type("Stat", (), {"st_mode": stat.S_IFLNK, "st_file_attributes": 0})()
        with patch.object(Path, "lstat", return_value=fake), self.assertRaises(p.Refusal):
            p.no_redirect(Path("anywhere"))

    def test_actual_redirecting_directory_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).absolute()
            outside, link = base / "outside", base / "link"
            outside.mkdir()
            if os.name == "nt":
                environment = dict(os.environ, UVH_TEST_LINK=str(link), UVH_TEST_TARGET=str(outside))
                subprocess.run(["powershell", "-NoProfile", "-Command",
                                "New-Item -ItemType Junction -Path $env:UVH_TEST_LINK -Target $env:UVH_TEST_TARGET | Out-Null"],
                               env=environment, check=True, capture_output=True, timeout=15)
            else:
                link.symlink_to(outside, target_is_directory=True)
            try:
                with self.assertRaises(p.Refusal):
                    p.no_redirect(link / "child")
            finally:
                # Remove only the tested link within this exact temporary root.
                self.assertTrue(link.absolute().is_relative_to(base))
                if os.name == "nt":
                    link.rmdir()
                else:
                    link.unlink()


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "fixture"
        self.root.mkdir()
        p.init_fixture(self.root)
        self.quarantine = self.base / "quarantine"
        self.quarantine.mkdir()
        self.payload = {p.LOADER: p.INERT + b"fake-loader", "sdk_mods/library.txt": p.INERT + b"fake-library",
                        "OakGame/Binaries/Win64/Plugins/config.txt": p.INERT + b"fake-config"}
        self.stage_log = self.base / "stage.jsonl"
        self.rollback_log = self.base / "rollback.jsonl"

    def tearDown(self):
        # Only the test framework's own resolved temporary tree is cleaned up.
        self.temp.cleanup()

    def stage(self, **kwargs):
        return p.stage_fixture(self.root, self.payload, self.stage_log, **kwargs)

    def rollback(self, receipt, **kwargs):
        return p.rollback_fixture(self.root, receipt, self.quarantine, self.rollback_log, **kwargs)

    def snapshot(self):
        return {f.relative_to(self.root).as_posix(): f.read_bytes() for f in self.root.rglob("*") if f.is_file()}

    def test_round_trip_preserves_unrelated_root_file(self):
        (self.root / "unrelated.txt").write_bytes(b"independent")
        before = self.snapshot()
        receipt = self.stage()
        self.assertEqual("FIXTURE_RESTORED", self.rollback(receipt)["status"])
        self.assertEqual(before, self.snapshot())
        for name, raw in self.payload.items():
            self.assertEqual(raw, (self.quarantine / name).read_bytes())

    def test_loader_last_stage_first_rollback(self):
        receipt = self.stage()
        stage = [json.loads(line) for line in self.stage_log.read_text().splitlines()]
        self.assertEqual(p.LOADER, [e["path"] for e in stage if e["event"] == "COPY_DONE"][-1])
        self.rollback(receipt)
        rollback = [json.loads(line) for line in self.rollback_log.read_text().splitlines()]
        self.assertEqual(p.LOADER, [e["path"] for e in rollback if e["event"] == "QUARANTINE_DONE"][0])

    def test_existing_target_refuses_before_journal(self):
        destination = self.root / p.LOADER
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"existing")
        before = self.snapshot()
        with self.assertRaises(p.Refusal):
            self.stage()
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.stage_log.exists())

    def test_existing_empty_scaffold_preserved(self):
        scaffold = self.root / "OakGame/Binaries/Win64"
        scaffold.mkdir(parents=True)
        receipt = self.stage()
        self.rollback(receipt)
        self.assertTrue(scaffold.is_dir())
        self.assertFalse((scaffold / "Plugins").exists())

    def test_unknown_child_in_preexisting_sdk_directory_refuses(self):
        (self.root / "sdk_mods").mkdir()
        receipt = self.stage()
        (self.root / "sdk_mods/unknown").write_bytes(b"independent")
        with self.assertRaises(p.Refusal):
            self.rollback(receipt)
        self.assertTrue((self.root / p.LOADER).exists())

    def test_unknown_sdk_directory_refused(self):
        sdk = self.root / "sdk_mods"
        sdk.mkdir()
        (sdk / "unrelated.txt").write_text("keep")
        with self.assertRaises(p.Refusal):
            self.stage()
        self.assertFalse(self.stage_log.exists())

    def test_marker_missing_refused(self):
        (self.root / p.MARKER).unlink()
        with self.assertRaises(p.Refusal):
            self.stage()

    def test_marker_changed_refused(self):
        (self.root / p.MARKER).write_bytes(b"different")
        with self.assertRaises(p.Refusal):
            self.stage()

    def test_real_executable_refused(self):
        (self.root / "Borderlands4.exe").write_bytes(b"MZ")
        with self.assertRaises(p.Refusal):
            self.stage()

    def test_wrong_build_and_process_inputs(self):
        for kwargs in ({"build": "different"}, {"process_count": 1}, {"process_count": False}, {"process_count": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(p.Refusal):
                self.stage(**kwargs)
        self.assertFalse(self.stage_log.exists())

    def test_rollback_requires_absent_process_input(self):
        receipt = self.stage()
        before = self.snapshot()
        with self.assertRaises(p.Refusal):
            self.rollback(receipt, process_count=1)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.rollback_log.exists())

    def test_real_bytes_refused(self):
        self.payload[p.LOADER] = b"MZnative-library"
        with self.assertRaises(p.Refusal):
            self.stage()

    def test_missing_loader_refused(self):
        del self.payload[p.LOADER]
        with self.assertRaises(p.Refusal):
            self.stage()

    def test_payload_traversal_refused(self):
        self.payload["../escaped"] = p.INERT
        with self.assertRaises(p.Refusal):
            self.stage()
        self.assertFalse((self.base / "escaped").exists())

    def test_case_collision_existing_parent(self):
        (self.root / "SDK_MODS").mkdir()
        with self.assertRaises(p.Refusal):
            self.stage()

    def test_parent_file_conflict(self):
        (self.root / "sdk_mods").write_text("not a directory")
        with self.assertRaises(p.Refusal):
            self.stage()

    def test_journal_inside_fixture_refused_before_copy(self):
        with self.assertRaises(p.Refusal):
            p.stage_fixture(self.root, self.payload, self.root / "journal")
        self.assertEqual({p.MARKER: p.MARKER_BYTES}, self.snapshot())

    def test_existing_journal_not_overwritten(self):
        self.stage_log.write_text("keep")
        with self.assertRaises(p.Refusal):
            self.stage()
        self.assertEqual("keep", self.stage_log.read_text())

    def test_interrupted_stage_recover_receipt_and_rollback(self):
        def fail(event, name):
            if name == p.LOADER:
                raise OSError("simulated interruption")
        with self.assertRaises(OSError):
            self.stage(fault=fail)
        self.assertFalse((self.root / p.LOADER).exists())
        receipt = p.recover_fixture_receipt(self.stage_log)
        self.assertEqual(2, self.rollback(receipt)["quarantined_files"])
        self.assertEqual({p.MARKER: p.MARKER_BYTES}, self.snapshot())

    def test_interrupted_partial_write_retained_and_refused(self):
        def partial(event, name):
            (self.root / name).write_bytes(b"partial")
            raise OSError("simulated partial copy")
        with self.assertRaises(OSError):
            self.stage(fault=partial)
        receipt = p.recover_fixture_receipt(self.stage_log)
        before = self.snapshot()
        with self.assertRaises(p.Refusal):
            self.rollback(receipt)
        self.assertEqual(before, self.snapshot())

    def test_changed_file_refuses_entire_rollback(self):
        receipt = self.stage()
        changed = self.root / "sdk_mods/library.txt"
        changed.write_bytes(b"independent edit")
        before = self.snapshot()
        with self.assertRaises(p.Refusal):
            self.rollback(receipt)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.rollback_log.exists())

    def test_unknown_child_refuses_entire_rollback(self):
        receipt = self.stage()
        unknown = self.root / "sdk_mods/unknown.txt"
        unknown.write_text("keep")
        before = self.snapshot()
        with self.assertRaises(p.Refusal):
            self.rollback(receipt)
        self.assertEqual(before, self.snapshot())

    def test_unknown_empty_directory_refuses(self):
        receipt = self.stage()
        (self.root / "sdk_mods/unexpected").mkdir()
        with self.assertRaises(p.Refusal):
            self.rollback(receipt)

    def test_quarantine_collision_refused_before_mutation(self):
        receipt = self.stage()
        (self.quarantine / "keep").write_text("keep")
        before = self.snapshot()
        with self.assertRaises(p.Refusal):
            self.rollback(receipt)
        self.assertEqual(before, self.snapshot())

    def test_quarantine_overlap_refused(self):
        receipt = self.stage()
        with self.assertRaises(p.Refusal):
            p.rollback_fixture(self.root, receipt, self.root, self.rollback_log)

    def test_rollback_journal_inside_quarantine_refused(self):
        receipt = self.stage()
        with self.assertRaises(p.Refusal):
            p.rollback_fixture(self.root, receipt, self.quarantine, self.quarantine / "log")

    def test_mid_rollback_edit_retains_evidence_and_reports_partial(self):
        receipt = self.stage()
        def edit(event, name):
            if name != p.LOADER:
                (self.root / name).write_bytes(b"independent change")
        with self.assertRaises(p.Refusal):
            self.rollback(receipt, fault=edit)
        self.assertFalse((self.root / p.LOADER).exists())
        self.assertTrue((self.quarantine / p.LOADER).exists())
        events = [json.loads(line)["event"] for line in self.rollback_log.read_text().splitlines()]
        self.assertNotIn("ROLLBACK_COMPLETE", events)

    def test_truncated_journal_refused(self):
        self.stage()
        self.stage_log.write_bytes(self.stage_log.read_bytes()[:-1])
        with self.assertRaises(p.Refusal):
            p.recover_fixture_receipt(self.stage_log)

    def test_forged_directory_scope_refused(self):
        receipt = self.stage()
        receipt["introduced_directories"].append("unrelated")
        with self.assertRaises(p.Refusal):
            self.rollback(receipt)

    def test_init_refuses_nonempty_directory(self):
        with self.assertRaises(p.Refusal):
            p.init_fixture(self.root)


class CommandTests(unittest.TestCase):
    def test_output_exclusive_and_sanitized_with_mock_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, output = root / "archive.zip", root / "manifest.json"
            source.write_bytes(b"inert")
            result = {"files": [{"path": p.LOADER}], "kind": "OFFLINE_PREPARATION_ONLY"}
            with patch.object(p, "ARCHIVE_BYTES", 5), patch.object(p, "prepare_manifest", return_value=result), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, p.main([str(source), str(output)]))
                first = output.read_bytes()
                self.assertEqual(1, p.main([str(source), str(output)]))
                self.assertEqual(first, output.read_bytes())
            self.assertNotIn(str(root).encode(), first)

    def test_bad_archive_creates_no_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, output = root / "archive.zip", root / "manifest.json"
            source.write_bytes(b"fake")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, p.main([str(source), str(output)]))
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
