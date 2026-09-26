"""Wrap the three existing payloads in one Arsenal exclusive-suboption mod."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import zipfile
from build_self_hit_release import NAME as SELF_NAME, zip_files

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'v0.3.0-preview.3'
NAME = f'P11-Enhanced-Selectable-{VERSION}-build25480438.zip'
GUID = 'ad4dbb99-b77a-48ad-b56c-b75b50d66ca6'
ARCHIVE = '9ba626afa44a3aa3.patch_0'
CHOICES = (
    ('P11', SELF_NAME, '僅 P-11 / P-11 only',
     '僅治療槍；保留 P-11 0.2.1 原始程式。建議先選此項。'),
    ('Pistols', 'weapon_self_hit_pistols-0.1.1-build25480438-CANDIDATE.zip',
     '手槍系列 + P-11 / Pistols [Candidate]',
     '內建相同 P-11，另啟用八個候選手槍資源 ID。擴展玩法未實測。'),
    ('NativeWeapons', 'weapon_self_hit_native-0.1.1-build25480438-CANDIDATE.zip',
     '廣域武器 + P-11 / Broad weapons [Candidate]',
     '內建相同 P-11，另處理本機武器的原生投射物；不代表所有傷害機制。擴展玩法未實測。'),
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
    manifest = {'Version': 1, 'Guid': GUID, 'Name': f'P11-Enhanced {VERSION} — 三選一',
                'Description': '武器自命中：僅 P-11／手槍系列／廣域原生投射物，三選一。'
                               '每個方案均內建同一份 P-11。build 25480438；需 Bingus Shared Loader v17 / API 1。',
                'Options': [{'Name': '啟用自命中，選擇一個範圍 / Self-hit scope',
                             'Description': '下方三選一。切換前關閉遊戲，選好後重新部署；不要同開舊獨立版本。',
                             'SubOptions': choices}]}
    for name, value in [('manifest.json', manifest), ('Source/payloads.json', payloads)]:
        files[name] = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    files['README.md'] = (ROOT/'docs/release/SELECTABLE.md').read_bytes()
    path = ROOT/'dist'/NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    zip_files(path, files)
    return NAME, path.read_bytes()
