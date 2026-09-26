"""Wrap four scope payloads in one Arsenal exclusive-suboption mod."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import zipfile
from build_self_hit_release import NAME as SELF_NAME, zip_files

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'v0.3.0-preview.6'
MOD_NAME = 'Projectile Collision Filter'
NAME = f'Projectile-Collision-Filter-{VERSION}-build25480438.zip'
GUID = 'ad4dbb99-b77a-48ad-b56c-b75b50d66ca6'
ARCHIVE = '9ba626afa44a3aa3.patch_0'
CHOICES = (
    ('P11', SELF_NAME, '僅治療手槍',
     '僅讓 P-11 治療飛鏢對自己生效。推薦，首次預選。 / P-11 only: self-hit healing. Recommended and preselected.'),
    ('Pistols', 'weapon_self_hit_pistols-0.1.3-build25480438-CANDIDATE.zip',
     '手槍全部',
     '擴展副武器原生投射物候選，包含電漿與榴彈；排除霰彈及多彈丸。雷射、火焰尚未支援，實體彈藥分支待驗證。 / All sidearms: expanded native-projectile candidates, including plasma and grenade sources. Shotguns/multishot excluded. Beam/spray unsupported; entity paths unverified.'),
    ('NativeNoShotguns', 'weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip',
     '全部武器不包括霰彈槍',
     '包含 P-11 與支援的武器投射物；排除霰彈及多彈丸類型。 / All weapons except shotguns: P-11 plus supported native-projectile candidates; shotguns and multishot types excluded.'),
    ('NativeWeapons', 'weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip',
     '全部武器包括霰彈槍',
     '包含霰彈及多彈丸類型，可能造成嚴重性能影響。 / All weapons including shotguns: includes multishot types and may cause severe performance impact.'),
)


def build_selectable(packages: dict[str, bytes]) -> tuple[str, bytes]:
    files = {}
    choices = []
    payloads = {}
    for folder, package, label, description in CHOICES:
        include = f'Variants/{folder}'
        choices.append({'Name': label, 'Description': description, 'Include': [include]})
        with zipfile.ZipFile(io.BytesIO(packages[package])) as z:
            for suffix in ('', '.stream', '.gpu_resources'):
                # Preserve the complete original archive, including resource order.
                files[f'{include}/{ARCHIVE}{suffix}'] = z.read(f'Addon/{ARCHIVE}{suffix}')
            for entry in z.namelist():
                if entry.startswith('Source/') and not entry.endswith('/'):
                    files[f'Source/{folder}/{entry[7:]}'] = z.read(entry)
        payloads[folder] = {'source_package': package,
                            'source_package_sha256': hashlib.sha256(packages[package]).hexdigest(),
                            'archive_sha256': hashlib.sha256(files[f'{include}/{ARCHIVE}']).hexdigest()}
    manifest = {'Version': 1, 'Guid': GUID, 'Name': f'{MOD_NAME} {VERSION} — 四選一',
                'Description': '四選一：前三項排除霰彈；第四項包含霰彈與多彈丸，可能造成嚴重性能影響。'
                               '每個方案均內建同一份 P-11。build 25480438；需 Bingus Shared Loader v17 / API 1。 '
                               'Choose one scope. All include unchanged P-11 healing. First three exclude shotguns; the fourth may severely affect performance. Expanded mechanisms remain preview candidates.',
                'Options': [{'Name': '生效範圍',
                             'Description': '下方四選一。預選僅 P-11；切換前關閉遊戲，選好後重新部署。升級後重新確認範圍。 / Scope: choose one. P-11 is preselected. Close the game before changing selection, then redeploy. Recheck your scope after an upgrade.',
                             'SubOptions': choices}]}
    for name, value in [('manifest.json', manifest), ('Source/payloads.json', payloads)]:
        files[name] = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    files['README.md'] = (ROOT/'docs/release/SELECTABLE.md').read_bytes()
    path = ROOT/'dist'/NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    zip_files(path, files)
    return NAME, path.read_bytes()
