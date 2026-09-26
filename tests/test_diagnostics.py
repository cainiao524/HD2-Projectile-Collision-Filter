"""Behavioral tests for offline diagnostics, using synthetic PE/Steam fixtures."""

import copy
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from collect_build_info import PEFormatError, _outside_game, collect_build_info, parse_pe, parse_steam_build_id
from compatibility_report import compare_manifest, create_report, load_manifest, validate_manifest
from log_parser import parse_log


def pe_fixture(with_version=True):
    data = bytearray(1024)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHI", data, 0x84, 0x8664, 1, 1700000000)
    struct.pack_into("<H", data, 0x94, 240)
    optional = 0x98
    struct.pack_into("<H", data, optional, 0x20B)
    struct.pack_into("<II", data, optional + 56, 0x2000, 0x200)
    struct.pack_into("<I", data, optional + 108, 16)
    section = optional + 240
    data[section:section + 8] = b".rsrc\0\0\0"
    struct.pack_into("<IIII", data, section + 8, 0x200, 0x1000, 0x200, 0x200)
    if with_version:
        struct.pack_into("<II", data, optional + 128, 0x1000, 0x200)
        for directory, name, target in ((0, 16, 0x80000020), (0x20, 1, 0x80000040), (0x40, 1033, 0x60)):
            struct.pack_into("<HH", data, 0x200 + directory + 12, 0, 1)
            struct.pack_into("<II", data, 0x200 + directory + 16, name, target)
        key = "VS_VERSION_INFO\0".encode("utf-16-le")
        block = bytearray(92)
        struct.pack_into("<HHH", block, 0, 92, 52, 0)
        block[6:6 + len(key)] = key
        struct.pack_into("<13I", block, 40, 0xFEEF04BD, 0x10000, (1 << 16) | 8, (46015 << 16), (1 << 16) | 8, (46015 << 16), 0, 0, 0, 0, 0, 0, 0)
        struct.pack_into("<IIII", data, 0x260, 0x1080, len(block), 0, 0)
        data[0x280:0x280 + len(block)] = block
    return data


def manifest_fixture():
    return {"schema_version": 1, "id": "test-build", "status": "unverified", "target": {"steam_build_id": "25480438", "game_dll_sha256": "A" * 64, "executable_sha256": "B" * 64}, "features": [{"id": "self_heal", "source": "mods/HealingPistolEnhanced/hooks/self_heal.lua", "status": "disabled"}]}


def build_fixture():
    return {"schema_version": 1, "game": {"steam_build_id": "25480438"}, "files": {"game_dll": {"sha256": "a" * 64}, "executable": {"sha256": "b" * 64}}}


class PETests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "example.dll"

    def test_extracts_version_and_image_metadata_without_loading(self):
        self.path.write_bytes(pe_fixture())
        info = parse_pe(self.path)
        self.assertEqual(info["file_version"], "1.8.46015.0")
        self.assertEqual(info["image_size"], 0x2000)
        self.assertEqual(info["machine"], "0x8664")

    def test_no_resource_keeps_version_unknown(self):
        self.path.write_bytes(pe_fixture(False))
        self.assertIsNone(parse_pe(self.path)["file_version"])

    def test_truncation_at_header_section_and_resource_boundaries(self):
        data = pe_fixture()
        for size in (0, 2, 63, 0x80, 0x97, 0x180, 0x1A0, 700):
            with self.subTest(size=size):
                self.path.write_bytes(data[:size])
                with self.assertRaises(PEFormatError):
                    parse_pe(self.path)

    def test_invalid_signatures_and_directories(self):
        for offset, value in ((0, b"XX"), (0x80, b"NOPE"), (0x98, b"\0\0"), (0x104, b"\xff\xff\xff\xff")):
            with self.subTest(offset=offset):
                data = pe_fixture()
                data[offset:offset + len(value)] = value
                self.path.write_bytes(data)
                with self.assertRaises(PEFormatError):
                    parse_pe(self.path)

    def test_bad_version_resource_retains_identity_with_error(self):
        data = pe_fixture()
        struct.pack_into("<I", data, 0x200 + 20, 0xFFFFFFFF)
        self.path.write_bytes(data)
        info = parse_pe(self.path)
        self.assertIn("version_error", info)
        self.assertIsNone(info["file_version"])


class SteamTests(unittest.TestCase):
    def test_only_appstate_build_id_is_returned(self):
        content = '// sample\n"AppState" { "appid" "553850" "LastOwner" "private-account" "nested" { "buildid" "999" } "buildid" "25480438" }'
        self.assertEqual(parse_steam_build_id(content), "25480438")

    def test_rejects_ambiguous_or_invalid_manifests(self):
        for content in ('"AppState" { "buildid" "123"', '"AppState" { "buildid" "1" "buildid" "2" }', '"AppState" { "buildid" "NaN" }', '"AppState" { "appid" "999" "buildid" "123" }'):
            with self.subTest(content=content):
                with self.assertRaises(ValueError):
                    parse_steam_build_id(content)

    def test_missing_build_id_is_unknown(self):
        self.assertIsNone(parse_steam_build_id('"AppState" { "LastOwner" "private-account" }'))

    def test_collector_retains_no_owner_and_never_creates_game_files(self):
        with tempfile.TemporaryDirectory() as directory:
            steamapps = Path(directory) / "steamapps"
            game = steamapps / "common" / "Helldivers 2"
            (game / "bin").mkdir(parents=True)
            (game / "data/game").mkdir(parents=True)
            (game / "bin/helldivers2.exe").write_bytes(pe_fixture())
            (game / "data/game/game.dll").write_bytes(pe_fixture())
            (steamapps / "appmanifest_553850.acf").write_text('"AppState" { "buildid" "25480438" "LastOwner" "private-account" }')
            before = {path.relative_to(game).as_posix(): path.read_bytes() for path in game.rglob("*") if path.is_file()}
            result = collect_build_info(game)
            after = {path.relative_to(game).as_posix(): path.read_bytes() for path in game.rglob("*") if path.is_file()}
            self.assertEqual(before, after)
            self.assertEqual(result["game"]["steam_build_id"], "25480438")
            self.assertNotIn("private-account", json.dumps(result))
            self.assertFalse(_outside_game(game / "report.json", game))
            self.assertTrue(_outside_game(Path(directory) / "report.json", game))


class CompatibilityTests(unittest.TestCase):
    def test_matching_hashes_do_not_enable_unverified_feature(self):
        result = compare_manifest(build_fixture(), manifest_fixture())
        self.assertEqual(result["status"], "disabled-unverified")
        self.assertEqual(result["features"][0]["status"], "disabled")
        self.assertFalse(result["runtime_verified"])

    def test_verified_metadata_still_requires_runtime_verification(self):
        manifest = manifest_fixture()
        manifest["status"] = "verified"
        manifest["features"][0]["status"] = "verified"
        result = compare_manifest(build_fixture(), manifest)
        self.assertEqual(result["status"], "match-requires-runtime-verification")
        self.assertEqual(result["features"][0]["status"], "disabled")

    def test_mismatch_missing_hash_or_collection_error_blocks(self):
        for change in ("wrong", "missing", "error"):
            with self.subTest(change=change):
                build = build_fixture()
                if change == "wrong":
                    build["files"]["game_dll"]["sha256"] = "C" * 64
                elif change == "missing":
                    build["files"]["game_dll"].pop("sha256")
                else:
                    build["files"]["game_dll"]["error"] = "file changed"
                self.assertEqual(compare_manifest(build, manifest_fixture())["status"], "disabled-build-mismatch")

    def test_invalid_manifest_is_disabled_in_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "build" / "manifest.json"
            path.parent.mkdir()
            path.write_text('{"schema_version": 1}')
            result = create_report(build_fixture(), directory)
            self.assertEqual(result["patches"][0]["status"], "disabled-invalid-manifest")

    def test_load_manifest_and_reject_unsafe_or_contradictory_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest_fixture()))
            self.assertEqual(load_manifest(path)["id"], "test-build")
        for field in ("hash", "source", "status"):
            manifest = copy.deepcopy(manifest_fixture())
            if field == "hash":
                manifest["target"]["game_dll_sha256"] = "not-a-hash"
            elif field == "source":
                manifest["features"][0]["source"] = "../outside.lua"
            else:
                manifest["features"][0]["status"] = "verified"
            with self.assertRaises(ValueError):
                validate_manifest(manifest)


class LogTests(unittest.TestCase):
    def test_loading_is_not_feature_verification(self):
        result = parse_log("[Loader] Loaded addon StimHoming\nmodule hash mismatch\n")
        self.assertEqual(result["events"][0]["event"], "addon_loading")
        self.assertFalse(result["events"][0]["proves_feature_compatibility"])
        self.assertIn("build_mismatch", {issue["code"] for issue in result["issues"]})

    def test_failure_to_source_mappings_and_guard_advice(self):
        cases = [("native publication signature mismatch", "signature_mismatch", "third-party/homing.json"), ("guided projectile callback changed", "callback_changed", "third-party/homing.json"), ("self-heal disabled: unverified", "self_heal_failed", "data_windows.lua"), ("P11_settings_mismatch", "target_selection", "third-party/homing.json"), ("Loaded section 2 rva differs", "self_hit_version_gate", "version.lua"), ("STOPPED write_readback_failed", "self_hit_data_guard", "data_windows.lua")]
        for line, code, source in cases:
            with self.subTest(line=line):
                result = parse_log(line)
                issue = next(item for item in result["issues"] if item["code"] == code)
                self.assertTrue(any(path.endswith(source) for path in issue["source_files"]))
                self.assertIn("never replace expected bytes blindly", result["advice"])

    def test_failures_do_not_become_positive_events_or_leak_lines(self):
        result = parse_log("verified callback failed owner=private-account\nUnexpected exception at C:\\private\\file.lua")
        self.assertEqual(result["events"], [])
        payload = json.dumps(result)
        self.assertNotIn("private-account", payload)
        self.assertNotIn("private", payload)
        self.assertIn("unclassified_failure", payload)

    def test_repeated_issues_preserve_line_numbers(self):
        result = parse_log("module hash mismatch\nnormal update\nmodule hash mismatch")
        self.assertEqual(result["issues"][0]["line_numbers"], [1, 3])


if __name__ == "__main__":
    unittest.main()
