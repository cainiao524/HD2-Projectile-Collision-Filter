#!/usr/bin/env python3
"""Summarize loader/mod log failures and relevant source files.

Output excludes raw log lines, absolute paths and account identifiers. A load or
callback message is evidence of that event only, not proof that a feature works.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SOURCE_MAP = {
    'main.lua': ['mods/p11_self_hit_dataonly/entry.lua', 'mods/p11_self_hit_dataonly/version.lua'],
    'hooks/self_heal.lua': ['mods/p11_self_hit_dataonly/core.lua', 'mods/p11_self_hit_dataonly/data_windows.lua'],
    'hooks/projectile.lua': ['third-party/homing.json'],
    'hooks/aim.lua': ['third-party/homing.json'],
    'menu/settings.lua': [], 'config.lua': [],
    'candidate.lua': ['mods/weapon_self_hit_candidate/entry.lua', 'mods/weapon_self_hit_candidate/core.lua', 'mods/weapon_self_hit_candidate/data_windows.lua'],
    'unified.lua': ['mods/projectile_collision_filter/entry.lua', 'mods/projectile_collision_filter/core.lua', 'mods/projectile_collision_filter/data_windows.lua', 'mods/projectile_collision_filter/version.lua'],
}
SELF_HIT_FEATURES = ['self_heal', 'pistol_self_hit', 'native_no_shotgun_self_hit', 'native_weapon_self_hit']
GUARD_ADVICE = "Keep the feature disabled. Re-derive and verify the address, original instructions, structure layout and calling convention; never replace expected bytes blindly or copy observed bytes just to pass a guard."
RULES = (
    ('unified_scope_conflict', r'Existing P-11 addon or different scope is already loaded|Disable other self-hit/research addon|Self-hit addon marker changed', SELF_HIT_FEATURES, ['unified.lua'], 'Close the game, disable other self-hit/research addons, choose one Arsenal scope and redeploy. The collector never deploys changes.'),
    ('candidate_scope_conflict', r'Enable only one weapon self-hit candidate scope', ['pistol_self_hit', 'native_no_shotgun_self_hit', 'native_weapon_self_hit'], ['candidate.lua'], 'Close the game and select only one of the four self-hit variants in Arsenal, then redeploy.'),
    ('unsupported_shared_loader', r'Unsupported loader', ['addon_loading','self_heal','pistol_self_hit','native_weapon_self_hit'], ['main.lua','candidate.lua'], 'These addons require API 1 and internal version 16; a newer internal version is not automatically compatible.'),
    ("self_hit_version_gate", r"Unsupported game files|Unsupported loaded build|Loaded section.*differs|Code anchor differs|STARTUP TIMEOUT", ["self_heal"], ["main.lua"], "Compare both file hashes, virtual sections and instruction anchors. Deferred startup rejection is not a loader-discovery failure. " + GUARD_ADVICE),
    ("self_hit_data_guard", r"write_failed|write_readback_failed|write_page_rejected|invalid_write_request", ["self_heal"], ["hooks/self_heal.lua"], "Inspect the narrow data adapter and identity guards; do not bypass a failed write/readback check."),
    ("restoration_failed", r"rollback.failed|restoration.failed|restoration_not_confirmed|settings.restore.failed|stop mutations", ["teammate_lock", "projectile_homing", "self_heal"], ["hooks/projectile.lua", "hooks/self_heal.lua"], "Stop the addon and restart the game to clear uncertain runtime changes. Inspect ownership checks and rollback before any retry."),
    ("build_mismatch", r"(?:build|version|module.hash|game.hash|executable.hash).{0,40}(?:mismatch|unsupported|changed|rejected)|(?:unsupported|unverified).{0,25}build|hash mismatch", ["teammate_lock", "projectile_homing", "self_heal"], ["main.lua"], "Collect fresh build identities and inspect patches/<build>/manifest.json. A loader that discovered the addon may already be working. " + GUARD_ADVICE),
    ("signature_mismatch", r"(?:signature|expected.bytes|byte.verification|native publication).{0,60}(?:mismatch|failed|changed)|(?:mismatch|failed).{0,40}(?:signature|expected.bytes)", ["teammate_lock", "projectile_homing", "self_heal"], ["hooks/projectile.lua", "hooks/self_heal.lua"], GUARD_ADVICE),
    ("callback_changed", r"callback.{0,40}(?:changed|mismatch|unavailable|missing|failed)|(?:missing|unavailable).{0,25}callback", ["projectile_homing", "self_heal"], ["main.lua", "hooks/projectile.lua", "hooks/self_heal.lua"], "Check the loader API and the addon callback contract, then verify build-specific callback locations. " + GUARD_ADVICE),
    ("missing_module", r"module.{0,100}not found|cannot (?:open|load)|file not found|no such file|missing (?:file|module|dependency)", ["addon_loading"], ["main.lua"], "Check archive contents, Lua module names, addon discovery and the loader dependency. Restore missing source files before investigating memory offsets."),
    ("loader_api", r"(?:loader|api).{0,35}(?:unsupported|incompatible|mismatch|too old)|(?:requires?|missing).{0,30}(?:loader|api ?1)", ["addon_loading"], ["main.lua"], "Check the supported Bingus Shared Loader version and API 1 contract. A game-build rejection alone does not establish that the loader needs updating."),
    ("target_selection", r"P11_settings_mismatch|P11 not held|muzzle mismatch|roster_read_failed|roster_recheck_failed|diver_resource_mismatch|snapshot_changed_or_unreadable", ["teammate_lock"], ["hooks/aim.lua"], "Keep targeting disabled until P-11 identity, local-player exclusion, teammate identity and snapshot guards have been checked for the current build."),
    ("self_heal_failed", r"self[_ -]?heal.{0,60}(?:error|failed|unverified|disabled|reject)|self[_ -]?hit.{0,60}(?:error|failed|unverified|disabled|reject)", ["self_heal"], ["hooks/self_heal.lua"], "Check the real loaded-shot event and native self-hit evidence. An offline hash match does not verify effect behavior or replication scope."),
    ("menu_failed", r"(?:menu|settings ui|config ui).{0,40}(?:error|failed|missing|unavailable)", ["configuration_menu"], ["menu/settings.lua", "config.lua"], "Check the loader's documented UI capability and configuration adapter. Do not infer a menu API from the loader version alone."),
)
COMPILED_RULES = [(code, re.compile(pattern, re.I), features, sources, advice) for code, pattern, features, sources, advice in RULES]


def parse_log(content: str) -> dict:
    issues = {}
    events = []
    scopes = set()
    unified = 'Projectile Collision Filter' in content or 'CURSOR BUDGET:' in content
    for number, line in enumerate(content.splitlines(), 1):
        scope = re.search(r'\bscope=(p11|pistols|native_no_shotguns|native_weapons)\b', line)
        if scope: scopes.add(scope[1])
        budget = re.search(r'CURSOR BUDGET: overruns=(\d+); dropped=(\d+); expired=(\d+)', line)
        if budget:
            counts = dict(zip(('overruns', 'dropped', 'expired'), map(int, budget.groups())))
            events.append({'line': number, 'event': 'bounded_cursor_work', **counts,
                           'proves_feature_compatibility': False})
            if any(counts.values()):
                issue = issues.setdefault('cursor_budget_limited', {'code': 'cursor_budget_limited',
                    'severity': 'warning', 'line_numbers': [], 'affected_features': SELF_HIT_FEATURES,
                    'source_files': SOURCE_MAP['unified.lua'],
                    'advice': 'Bounded discovery/retry limits skipped or expired hints. Inspect the 15 anchors, allocation cursor/probe semantics and pending limits. Do not remove budgets or write guards, infer missed-hit counts, or treat this log as gameplay proof.'})
                issue['line_numbers'].append(number)
        matched = False
        for code, pattern, features, sources, advice in COMPILED_RULES:
            if pattern.search(line):
                matched = True
                issue = issues.setdefault(code, {"code": code, "severity": "error", "line_numbers": [], "affected_features": features, "source_files": sorted({p for path in sources for p in SOURCE_MAP[path]}), "advice": advice})
                issue["line_numbers"].append(number)
                if unified and 'self_heal' in features:
                    issue['source_files'] = sorted(set(issue['source_files']) | set(SOURCE_MAP['unified.lua']))
                    issue['affected_features'] = sorted(set(issue['affected_features']) | set(SELF_HIT_FEATURES))
        # Explicit negative states suppress misleading positive event labels.
        if line.startswith('FIRST DATA WRITE READ BACK:') and not re.search(r'\b(?:failed|failure|error|mismatch|rejected)\b', line, re.I):
            events.append({'line':number,'event':'data_write_readback','proves_feature_compatibility':False})
        negative = matched or re.search(r"\b(?:failed|failure|error|mismatch|rejected|unavailable|unsupported|not|false)\b", line, re.I)
        if not negative:
            if line.startswith('ENABLED:'):
                events.append({'line':number,'event':'addon_activation','proves_feature_compatibility':False})
            if re.search(r"\b(?:loaded|loading|discovered|registered)\b.*\b(?:addon|stim|homing|healing)|\b(?:addon|stim|homing|healing)\b.*\b(?:loaded|loading|discovered|registered)\b", line, re.I):
                events.append({"line": number, "event": "addon_loading", "proves_feature_compatibility": False})
            if re.search(r"\b(?:verified|verification passed|verification succeeded)\b", line, re.I):
                events.append({"line": number, "event": "verification_message", "proves_feature_compatibility": False})
            if re.search(r"\bcallback\b.*\b(?:registered|invoked|executed|completed)\b", line, re.I):
                events.append({"line": number, "event": "callback_message", "proves_feature_compatibility": False})
        if not matched and re.search(r"\b(?:error|exception|failed|failure|mismatch)\b|startup_failed", line, re.I):
            issue = issues.setdefault("unclassified_failure", {"code": "unclassified_failure", "severity": "error", "line_numbers": [], "affected_features": ["unknown"], "source_files": [], "advice": "Inspect these lines locally and identify the failing addon. Do not assume the failure is a loader problem or an offset mismatch without evidence."})
            issue["line_numbers"].append(number)
    return {"schema_version": 1, "line_count": len(content.splitlines()), "issues": list(issues.values()), "events": events,
            "observed_scopes": sorted(scopes), "scope_verified_by_log": False,
            "runtime_verified": False, "scope": "heuristic log triage; source mappings are inspection candidates, not verified root causes", "advice": GUARD_ADVICE}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = parse_log(args.log_file.read_text(encoding="utf-8-sig", errors="replace"))
        payload = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
            print(f"Wrote log triage report: {args.output}")
        else:
            print(payload, end="")
    except OSError as exc:
        parser.exit(2, f"Unable to read/write diagnostic file: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
