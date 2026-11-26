#!/usr/bin/env python3
"""Read game build fingerprints without loading binaries or changing game files.

Only the Steam build ID is retained from appmanifest_553850.acf. PE version
resources are read directly with the Python standard library; no DLL is loaded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO


class PEFormatError(ValueError):
    """An input is not a supported, structurally valid PE file."""


class _Reader:
    def __init__(self, stream: BinaryIO, size: int):
        self.stream, self.size = stream, size

    def read(self, offset: int, size: int) -> bytes:
        if offset < 0 or size < 0 or offset + size > self.size:
            raise PEFormatError("truncated or out-of-range PE data")
        self.stream.seek(offset)
        data = self.stream.read(size)
        if len(data) != size:
            raise PEFormatError("file changed or was truncated during inspection")
        return data


def _fixed_version(data: bytes) -> tuple[str, str]:
    if len(data) < 6:
        raise PEFormatError("truncated version resource")
    length, value_length, value_type = struct.unpack_from("<HHH", data)
    if length > len(data) or length < 6 or value_type != 0:
        raise PEFormatError("invalid version resource header")
    key = "VS_VERSION_INFO\0".encode("utf-16-le")
    if data[6:6 + len(key)] != key:
        raise PEFormatError("unexpected version resource key")
    value_offset = (6 + len(key) + 3) & ~3
    if value_length < 52 or value_offset + value_length > length:
        raise PEFormatError("truncated fixed version information")
    values = struct.unpack_from("<13I", data, value_offset)
    if values[0] != 0xFEEF04BD:
        raise PEFormatError("invalid fixed version signature")

    def version(ms: int, ls: int) -> str:
        return f"{ms >> 16}.{ms & 65535}.{ls >> 16}.{ls & 65535}"

    return version(values[2], values[3]), version(values[4], values[5])


def _resource_versions(reader: _Reader, rva_to_offset, rva: int, size: int):
    base = rva_to_offset(rva, size)

    def resource_read(offset: int, count: int) -> bytes:
        if offset < 0 or offset + count > size:
            raise PEFormatError("resource directory exceeds its declared size")
        return reader.read(base + offset, count)

    def entries(offset: int):
        header = resource_read(offset, 16)
        named, numbered = struct.unpack_from("<HH", header, 12)
        count = named + numbered
        if count > 4096:
            raise PEFormatError("unreasonable resource directory entry count")
        data = resource_read(offset + 16, count * 8)
        return [struct.unpack_from("<II", data, n * 8) for n in range(count)]

    version_dirs = [target for name, target in entries(0) if name == 16]
    if not version_dirs:
        return None, None
    target = version_dirs[0]
    if not target & 0x80000000:
        raise PEFormatError("version resource type is not a directory")
    # Resource tree: type -> name -> language -> data. Never follow arbitrary
    # recursion, which also bounds traversal of malformed cyclic resources.
    for _, name_target in entries(target & 0x7FFFFFFF):
        if not name_target & 0x80000000:
            continue
        for _, language_target in entries(name_target & 0x7FFFFFFF):
            if language_target & 0x80000000:
                continue
            data_rva, data_size, _, _ = struct.unpack(
                "<IIII", resource_read(language_target, 16)
            )
            if data_size > 1024 * 1024:
                raise PEFormatError("version resource is unexpectedly large")
            return _fixed_version(reader.read(rva_to_offset(data_rva, data_size), data_size))
    raise PEFormatError("version resource has no supported data entry")


def parse_pe(path: Path | str) -> dict:
    """Return PE metadata, raising PEFormatError for invalid/truncated headers."""
    path = Path(path)
    with path.open("rb") as stream:
        reader = _Reader(stream, path.stat().st_size)
        dos = reader.read(0, 64)
        if dos[:2] != b"MZ":
            raise PEFormatError("missing DOS MZ signature")
        pe_offset = struct.unpack_from("<I", dos, 0x3C)[0]
        if pe_offset < 64:
            raise PEFormatError("PE header overlaps the DOS header")
        header = reader.read(pe_offset, 24)
        if header[:4] != b"PE\0\0":
            raise PEFormatError("missing PE signature")
        machine, section_count, timestamp = struct.unpack_from("<HHI", header, 4)
        optional_size = struct.unpack_from("<H", header, 20)[0]
        if not 1 <= section_count <= 96:
            raise PEFormatError("invalid PE section count")
        optional = reader.read(pe_offset + 24, optional_size)
        if len(optional) < 2:
            raise PEFormatError("missing optional header")
        magic = struct.unpack_from("<H", optional)[0]
        if magic not in (0x10B, 0x20B):
            raise PEFormatError("unsupported optional-header format")
        directory_start, directory_count_offset = (96, 92) if magic == 0x10B else (112, 108)
        if len(optional) < directory_start:
            raise PEFormatError("truncated optional header")
        image_size, header_size = struct.unpack_from("<II", optional, 56)
        if not image_size or not header_size or header_size > reader.size:
            raise PEFormatError("invalid image or header size")
        directory_count = struct.unpack_from("<I", optional, directory_count_offset)[0]
        if directory_count > (len(optional) - directory_start) // 8:
            raise PEFormatError("truncated data-directory table")
        section_table = reader.read(pe_offset + 24 + optional_size, section_count * 40)
        sections = []
        section_info = []
        for index in range(section_count):
            section = section_table[index * 40:(index + 1) * 40]
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", section, 8)
            if raw_size and (raw_offset < header_size or raw_offset + raw_size > reader.size):
                raise PEFormatError("truncated or overlapping section data")
            sections.append((virtual_address, virtual_size, raw_offset, raw_size))
            section_info.append({'name':section[:8].split(b'\0',1)[0].decode('ascii',errors='replace'),
                'rva':virtual_address,'virtual_size':virtual_size,'raw_offset':raw_offset,'raw_size':raw_size,
                'characteristics':struct.unpack_from('<I',section,36)[0]})

        def rva_to_offset(rva: int, count: int) -> int:
            if rva < header_size and rva + count <= header_size:
                return rva
            for address, virtual_size, raw_offset, raw_size in sections:
                delta = rva - address
                if 0 <= delta < max(virtual_size, raw_size) and delta + count <= raw_size:
                    return raw_offset + delta
            raise PEFormatError("RVA does not map to complete on-disk data")

        result = {
            "format": "PE32+" if magic == 0x20B else "PE32",
            "machine": f"0x{machine:04X}",
            "timestamp": timestamp,
            "timestamp_utc": datetime.fromtimestamp(timestamp, timezone.utc).isoformat(),
            "image_size": image_size,
            "section_count": section_count,
            "sections": section_info,
            "file_version": None,
            "product_version": None,
        }
        if directory_count > 2:
            resource_rva, resource_size = struct.unpack_from("<II", optional, directory_start + 16)
            if resource_rva and resource_size:
                try:
                    result["file_version"], result["product_version"] = _resource_versions(
                        reader, rva_to_offset, resource_rva, resource_size
                    )
                except PEFormatError as exc:
                    result["version_error"] = str(exc)
        return result


def parse_steam_build_id(content: str) -> str | None:
    """Parse Valve KeyValues but return only the AppState build ID."""
    pattern = re.compile(r'\s+|//[^\n]*|"((?:\\.|[^"\\])*)"|([{}])|([^\s{}"]+)')
    tokens = []
    position = 0
    while position < len(content):
        match = pattern.match(content, position)
        if not match:
            raise ValueError("malformed Steam manifest token")
        position = match.end()
        if match.group(1) is not None:
            tokens.append(re.sub(r'\\(["\\])', r'\1', match.group(1)))
        elif match.group(2):
            tokens.append(match.group(2))
        elif match.group(3):
            tokens.append(match.group(3))

    index = 0

    def object_values(nested: bool, depth: int = 0) -> dict:
        nonlocal index
        if depth > 32:
            raise ValueError("Steam manifest nesting exceeds limit")
        result = {}
        while index < len(tokens):
            key = tokens[index]
            index += 1
            if key == "}":
                if nested:
                    return result
                raise ValueError("unmatched manifest closing brace")
            if key == "{" or index >= len(tokens):
                raise ValueError("manifest key has no value")
            value = tokens[index]
            index += 1
            if value == "{":
                value = object_values(True, depth + 1)
            elif value == "}":
                raise ValueError("manifest key has no value")
            normalized_key = key.lower()
            if normalized_key in result:
                raise ValueError("duplicate manifest key")
            result[normalized_key] = value
        if nested:
            raise ValueError("unclosed manifest object")
        return result

    values = object_values(False)
    app_state = values.get("appstate")
    if not isinstance(app_state, dict):
        return None
    if app_state.get("appid", "553850") != "553850":
        raise ValueError("manifest is for a different application")
    build_id = app_state.get("buildid")
    if build_id is None:
        return None
    if not isinstance(build_id, str) or not re.fullmatch(r"[0-9]+", build_id):
        raise ValueError("Steam build ID must contain digits only")
    return build_id


def inspect_binary(path: Path, relative_path: str) -> dict:
    result = {"relative_path": relative_path, "exists": path.is_file()}
    if not result["exists"]:
        return result
    try:
        before = path.stat()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        result.update(size_bytes=before.st_size, sha256=digest.hexdigest().upper())
        try:
            result["pe"] = parse_pe(path)
        except PEFormatError as exc:
            result["pe_error"] = str(exc)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            result["error"] = "file changed during collection; close the game/updater and collect again"
            result.pop("sha256", None)
    except OSError as exc:
        result["error"] = f"unable to read file ({type(exc).__name__})"
    return result


def collect_build_info(game_root: Path | str) -> dict:
    root = Path(game_root).resolve()
    if not root.is_dir():
        raise ValueError("game root is not a directory")
    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "game": {"app_id": "553850", "steam_build_id": None},
        "files": {},
        "warnings": [],
        "scope": "on-disk identity only; no runtime address or feature verification",
    }
    for key, relative in (("executable", "bin/helldivers2.exe"), ("game_dll", "data/game/game.dll")):
        report["files"][key] = inspect_binary(root / relative, relative)
        if not report["files"][key]["exists"]:
            report["warnings"].append(f"missing expected file: {relative}")
    candidates = [root.parent.parent / "appmanifest_553850.acf", root.parent / "appmanifest_553850.acf", root / "appmanifest_553850.acf"]
    manifest = next((path for path in candidates if path.is_file()), None)
    if manifest:
        try:
            if manifest.stat().st_size > 4 * 1024 * 1024:
                raise ValueError("Steam manifest exceeds the size limit")
            report["game"]["steam_build_id"] = parse_steam_build_id(manifest.read_text(encoding="utf-8-sig"))
            if report["game"]["steam_build_id"] is None:
                report["warnings"].append("Steam manifest has no AppState build ID")
        except (OSError, UnicodeError, ValueError) as exc:
            report["warnings"].append(f"unable to parse Steam build ID ({type(exc).__name__})")
    else:
        report["warnings"].append("appmanifest_553850.acf was not found beside the Steam common directory")
    return report


def _outside_game(output: Path, game_root: Path) -> bool:
    try:
        output.resolve().relative_to(game_root.resolve())
    except ValueError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_root", type=Path, help="Helldivers 2 installation directory")
    parser.add_argument("--output", type=Path, required=True, help="JSON output outside the game directory")
    args = parser.parse_args()
    if not _outside_game(args.output, args.game_root):
        parser.error("--output must be outside the game directory; the collector never writes game files")
    try:
        report = collect_build_info(args.game_root)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Collection failed: {type(exc).__name__}: {exc}\n")
    print(f"Wrote build identity report: {args.output}")
    print(f"Steam build ID: {report['game']['steam_build_id'] or 'unknown'}")
    for warning in report["warnings"]:
        print(f"Warning: {warning}")
    return 0 if all(item.get("sha256") for item in report["files"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
