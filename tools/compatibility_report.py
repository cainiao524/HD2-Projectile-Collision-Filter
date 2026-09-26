#!/usr/bin/env python3
"""Compare collected file identities with patch manifests; never enable features.

A matching disk hash does not verify decrypted runtime addresses, instructions,
calling conventions, loader callbacks, or behavior. Those require separate proof.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SHA256 = re.compile(r"[0-9a-fA-F]{64}")


def validate_manifest(value: object) -> dict:
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError("patch manifest must use schema_version 1")
    if not isinstance(value.get("id"), str) or not value["id"].strip():
        raise ValueError("patch manifest requires a nonempty id")
    if value.get("status") not in ("unverified", "verified"):
        raise ValueError("patch status must be unverified or verified")
    target = value.get("target")
    if not isinstance(target, dict):
        raise ValueError("patch manifest requires a target object")
    if not isinstance(target.get("steam_build_id"), str) or not re.fullmatch(r"[0-9]+", target["steam_build_id"]):
        raise ValueError("target.steam_build_id must be a numeric string")
    for key in ("game_dll_sha256", "executable_sha256"):
        digest = target.get(key)
        if digest is not None and (not isinstance(digest, str) or not SHA256.fullmatch(digest)):
            raise ValueError(f"target.{key} must be a 64-character hexadecimal hash or null")
    if value["status"] == "verified" and not all(target.get(key) for key in ("game_dll_sha256", "executable_sha256")):
        raise ValueError("verified manifests require both executable and game DLL hashes")
    features = value.get("features")
    if not isinstance(features, list) or not features:
        raise ValueError("patch manifest requires a nonempty features list")
    ids = set()
    for feature in features:
        if not isinstance(feature, dict) or not isinstance(feature.get("id"), str) or not feature["id"].strip():
            raise ValueError("each feature requires an id")
        if feature["id"] in ids:
            raise ValueError("feature IDs must be unique")
        ids.add(feature["id"])
        if feature.get("status") not in ("disabled", "verified"):
            raise ValueError("feature status must be disabled or verified")
        source = feature.get("source")
        if not isinstance(source, str) or not source.strip() or source.startswith(("/", "\\")) or ":" in source or ".." in source.replace("\\", "/").split("/"):
            raise ValueError("feature source must be a repository-relative path")
        if value["status"] == "unverified" and feature["status"] == "verified":
            raise ValueError("an unverified patch cannot declare verified features")
    return value


def load_manifest(path: Path | str) -> dict:
    return validate_manifest(json.loads(Path(path).read_text(encoding="utf-8-sig")))


def compare_manifest(build: dict, manifest: dict) -> dict:
    validate_manifest(manifest)
    target = manifest["target"]
    checks = []
    values = (
        ("steam_build_id", target["steam_build_id"], build.get("game", {}).get("steam_build_id")),
        ("game_dll_sha256", target.get("game_dll_sha256"), build.get("files", {}).get("game_dll", {}).get("sha256")),
        ("executable_sha256", target.get("executable_sha256"), build.get("files", {}).get("executable", {}).get("sha256")),
    )
    for name, expected, actual in values:
        if expected is None:
            status = "unspecified"
        elif actual is None:
            status = "missing"
        else:
            status = "match" if str(expected).casefold() == str(actual).casefold() else "mismatch"
        checks.append({"field": name, "expected": expected, "actual": actual, "status": status})
    errors = [name for name, item in build.get("files", {}).items() if item.get("error") or item.get("pe_error")]
    all_match = all(check["status"] == "match" for check in checks) and not errors
    matching_declared = all(check["status"] in ("match", "unspecified") for check in checks) and not errors
    if not matching_declared:
        status = "disabled-build-mismatch"
    elif manifest["status"] != "verified" or not all_match:
        status = "disabled-unverified"
    else:
        status = "match-requires-runtime-verification"
    return {
        "patch_id": manifest["id"],
        "status": status,
        "disk_identity_matches_declared_fields": matching_declared,
        "runtime_verified": False,
        "checks": checks,
        "collection_errors": errors,
        "features": [{
            "id": feature["id"],
            "source": feature["source"],
            "status": "disabled",
            "reason": feature.get("reason") or (
                "runtime verification is required; offline comparison cannot enable this feature"
                if status == "match-requires-runtime-verification" and feature["status"] == "verified"
                else "build or feature evidence is incomplete or incompatible"
            ),
        } for feature in manifest["features"]],
        "advice": "Keep affected features disabled. Re-derive and independently verify addresses and signatures; never replace expected bytes blindly or copy observed bytes merely to pass a guard.",
    }


def create_report(build: dict, patches: Path | str) -> dict:
    if not isinstance(build, dict) or build.get("schema_version") != 1 or not isinstance(build.get("game"), dict) or not isinstance(build.get("files"), dict):
        raise ValueError("build report must contain schema_version 1, game and files objects")
    for item in build["files"].values():
        if not isinstance(item, dict):
            raise ValueError("each collected file must be an object")
    results = []
    for path in sorted(Path(patches).glob("*/manifest.json")):
        try:
            result = compare_manifest(build, load_manifest(path))
        except (ValueError, OSError) as exc:
            result = {"status": "disabled-invalid-manifest", "error": str(exc), "runtime_verified": False, "features": []}
        result["manifest"] = path.relative_to(patches).as_posix()
        results.append(result)
    return {
        "schema_version": 1,
        "steam_build_id": build["game"].get("steam_build_id"),
        "scope": "read-only disk identity comparison; runtime offsets and loader compatibility are not verified",
        "status": "disabled" if not results or not any(item["status"] == "match-requires-runtime-verification" for item in results) else "runtime-verification-required",
        "patches": results,
        "warnings": [] if results else ["no patches/*/manifest.json files found"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_info", type=Path)
    parser.add_argument("--patches", type=Path, default=Path(__file__).resolve().parents[1] / "patches")
    parser.add_argument("--output", type=Path, help="optional JSON output; otherwise prints JSON")
    args = parser.parse_args()
    try:
        report = create_report(json.loads(args.build_info.read_text(encoding="utf-8-sig")), args.patches)
        payload = json.dumps(report, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
            print(f"Wrote compatibility report: {args.output}")
        else:
            print(payload, end="")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Compatibility report failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
