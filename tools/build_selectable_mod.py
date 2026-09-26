"""Wrap four scope payloads in one Arsenal exclusive-suboption mod."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import zipfile
from build_self_hit_release import NAME as SELF_NAME, zip_files

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'v0.3.0-preview.4'
NAME = f'P11-Enhanced-Selectable-{VERSION}-build25480438.zip'
GUID = 'ad4dbb99-b77a-48ad-b56c-b75b50d66ca6'
ARCHIVE = '9ba626afa44a3aa3.patch_0'
CHOICES = (
    ('P11', SELF_NAME, '僅 P-11 / P-11 only',
     '僅治療槍；其他彈丸一律不處理，包括霰彈。保留 P-11 0.2.1。'),
    ('Pistols', 'weapon_self_hit_pistols-0.1.2-build25480438-CANDIDATE.zip',
     '手槍排除霰彈 + P-11 / Pistols, no shotguns',
     '候選手槍範圍；先排除已知霰彈、所有表內多彈丸種類與未知種類。內建原 P-11。'),
    ('NativeNoShotguns', 'weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip',
     '廣域排除霰彈 + P-11 / Broad, no shotguns',
     '本機原生武器投射物；先排除已知霰彈、所有表內多彈丸種類與未知種類。內建原 P-11。'),
    ('NativeWeapons', 'weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip',
     '全部含霰彈 + P-11 / Include shotguns [Heavy]',
     '主動選用：包含霰彈及多彈丸的廣域原生投射物候選，可能造成卡頓。不是所有傷害系統的支援保證。'),
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
    manifest = {'Version': 1, 'Guid': GUID, 'Name': f'P11-Enhanced {VERSION} — 四選一',
                'Description': '四選一：前三項排除霰彈；第四項包含霰彈與多彈丸，可能影響效能。'
                               '每個方案均內建同一份 P-11。build 25480438；需 Bingus Shared Loader v17 / API 1。',
                'Options': [{'Name': '啟用自命中，選擇一個範圍 / Self-hit scope',
                             'Description': '下方四選一。預選僅 P-11；切換前關閉遊戲，選好後重新部署。升級後重新確認範圍。',
                             'SubOptions': choices}]}
    for name, value in [('manifest.json', manifest), ('Source/payloads.json', payloads)]:
        files[name] = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    files['README.md'] = (ROOT/'docs/release/SELECTABLE.md').read_bytes()
    path = ROOT/'dist'/NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    zip_files(path, files)
    return NAME, path.read_bytes()
