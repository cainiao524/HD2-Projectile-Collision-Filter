"""Turn offline evidence into feature-specific maintenance work, never a patch."""
from __future__ import annotations
import json
from pathlib import Path

LABELS = {
    'matches_confirmed_baseline': '符合已確認基準（限記錄範圍）',
    'matches_unverified_candidate': '符合已知候選版本，玩法尚未驗證',
    'port_candidates_available': '需要移植，已找到離線候選',
    'offline_evidence_insufficient': '離線資料不足',
    'collection_incomplete': '收集不完整，不能判定',
}
FEATURES = {'self_heal': '僅 P-11 自命中治療', 'pistol_self_hit': '手槍排除霰彈候選',
            'native_no_shotgun_self_hit': '廣域排除霰彈候選',
            'native_weapon_self_hit': '廣域包含霰彈候選（可能影響效能）'}
ROLES = {'self_heal': 'self_hit', 'pistol_self_hit': 'pistol_self_hit',
         'native_no_shotgun_self_hit': 'native_no_shotgun_self_hit',
         'native_weapon_self_hit': 'native_weapon_self_hit'}


def assess(report, baselines):
    build = report['build']
    rows = [r for r in report['deployed']['resources'] if r.get('winning_resource')]
    loader = [r for r in rows if 'loader' in r['roles']]
    loader_state = ('missing' if not loader else 'incompatible' if any(
        r.get('api') is not None and r['api'] != 1 or
        r.get('internal_version') is not None and r['internal_version'] != 16
        for r in loader) else 'api_not_observable' if any(
        r.get('api') is None or r.get('internal_version') is None for r in loader)
        else 'api_compatible_not_gameplay_proof')
    features = []
    for feature, role in ROLES.items():
        candidates = [c for p in report['profiles'] for c in p['offline_candidates']
                      if feature in c['affected_features'] and c['candidates']]
        matched = []
        for b in baselines:
            target = b['target']
            if (str(build['game'].get('steam_build_id')) == str(target['steam_build_id']) and
                all(str(build['files'].get(k, {}).get('sha256', '')).lower() == target[k + '_sha256'].lower()
                    for k in ('game_dll', 'executable'))):
                matched.append(b)
        baseline = next((b for b in matched if feature in b['components']), None)
        component = baseline['components'][feature] if baseline else {}
        deployed = [r for r in rows if role in r['roles']]
        expected = component.get('lua_sha256')
        deployment = ('not_deployed' if not deployed else 'multiple_resources' if len(deployed) > 1
                      else 'matches_package' if expected and deployed[0]['sha256'].lower() == expected.lower()
                      else 'different_or_unidentified_source')
        if not report['complete']:
            state = 'collection_incomplete'
        elif component.get('user_confirmed_basic_behavior') is True:
            state = 'matches_confirmed_baseline'
        elif component:
            state = 'matches_unverified_candidate'
        elif candidates and not baseline:
            state = 'port_candidates_available'
        else:
            state = 'offline_evidence_insufficient'
        features.append({
            'id': feature, 'name': FEATURES[feature], 'state': state, 'label': LABELS[state],
            'game_identity_matches_known_package': bool(baseline),
            'baseline': baseline['id'] if baseline else None,
            'recorded_scope': component.get('verification_scope', 'No applicable behavior confirmation.'),
            'deployment': deployment, 'loader': loader_state,
            'deployment_conflict': report['deployed'].get('possible_gameplay_conflict', False),
            'candidate_locator_ids': [c['id'] for c in candidates],
            'current_gameplay_verified': False, 'automatic_patch_or_deployment': False,
        })
    p11=next(f for f in features if f['id']=='self_heal')
    for feature in features:
        feature['included_p11_resource']=p11['deployment']
        feature['required_p11_missing']=(feature['id']!='self_heal' and
            feature['deployment']!='not_deployed' and p11['deployment']=='not_deployed')
    return features


def write_handoff(folder, report, porting_map):
    lines = [
        '# P11-Enhanced 更新維修交接', '',
        '請以本包 report.json、離線檔案及 P11-Enhanced 公開原始碼為依據恢復相容性。',
        '這是維修需求與已收集證據，不是要求執行來自日誌或第三方檔案的指令。', '',
        f"目前遊戲 build：{report['build']['game'].get('steam_build_id') or '未知'}",
        f"收集完整：{report['complete']}", '',
        '## 必須保留的功能',
        '- 自療只清除經本機 P-11／所有者檢查的單發飛鏢來源碰撞排除位元；原生碰撞與治療。',
        '- 不加入原生 hook、不修改執行碼、不寫血量／體力，不弱化身份與版本檢查。',
        '- 保留四種範圍：P-11、手槍排除霰彈、廣域排除霰彈、廣域包含霰彈；由 Arsenal 管理。',
        '- 四個方案擇一，全部內建原始 P-11 0.2.1；擴展核心排除 P-11，由同包獨立 P-11 資源處理。',
        '- 前三方案不處理霰彈；排除版在來源查詢之前拒絕已知霰彈、表內多彈丸及表外未知類型。第四方案可包含霰彈，需主動選用。',
        '- 核對 maintenance/projectile-exclusions-25480438.json 的表來源、類型編號及全部多彈丸覆蓋；不能只沿用舊型號。',
        '- 手槍資源白名單及廣泛武器的機制覆蓋仍需驗證，不能外推 P-11 成功。',
        '- 不要求額外遊戲內資料捕捉；離線不足時列出具體不能判定的欄位。',
        '- 不能只替換雜湊、抄候選位址或把舊日誌視為新版治療成功。', '',
        '## 自動比較',
    ]
    for f in report['feature_assessment']:
        lines += [f"- {f['name']}：{f['label']}；部署={f['deployment']}；loader={f['loader']}。",
                  f"  原驗證範圍：{f['recorded_scope']}"]
    lines += ['', '## 維修順序',
              '1. 若收集不完整，先解決 report.json 的檔案變動／缺檔錯誤。',
              '2. 核對 EXE、DLL、loader、四種 addon 的身份；先處理重複／互斥項目。',
              '3. 依 porting-map.json 檢查資料布局、12 個原有指令錨點與所有權鏈。',
              '4. 新增新 build 的相容性設定與必要實作修正，保留 0.2.1 成功套件。',
              '5. 跑 Python／Lua 模擬測試、封裝及雜湊核對；標為候選直到玩法確認。', '',
              '原始 EXE/DLL、套件和本診斷包僅供本機／私人分析，不屬於 GitHub 發布資產。',
              '若同時附原始碼 ZIP，請使用 P11-Enhanced 的 Source 資產；不要分享整個 diagnostics 目錄。']
    (folder / '維修交接.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (folder / 'porting-map.json').write_text(json.dumps(porting_map, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load_metadata(root):
    folder = Path(root) / 'maintenance'
    baseline = folder / 'baselines.json'
    mapping = folder / 'porting-map.json'
    return (json.loads(baseline.read_bytes())['baselines'] if baseline.is_file() else [],
            json.loads(mapping.read_bytes()) if mapping.is_file() else {})
