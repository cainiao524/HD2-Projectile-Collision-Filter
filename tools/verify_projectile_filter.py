"""Verify the pinned exclusion facts against an explicitly supplied offline table.

No downloads, game launch, process reads, writes to game files or deployment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]


def verify(blob,profile):
    source=profile['table_source']
    assert hashlib.sha256(blob).hexdigest()==source['sha256'],'table fingerprint mismatch'
    offset,stride,count=source['record_offset'],source['record_size'],source['count']
    assert (offset,stride,count)==(44,272,350) and len(blob)==offset+stride*count,'table layout mismatch'
    rows={}
    for at in range(offset,len(blob),stride):
        typ=struct.unpack_from('<I',blob,at)[0]
        assert typ not in rows,'duplicate projectile type'
        rows[typ]=at
    assert set(rows)==set(range(1,profile['projectile_type_max']+1)),'unknown numeric type coverage'
    excluded={r['type']:r for r in profile['excluded']}
    assert len(excluded)==len(profile['excluded'])==38
    for typ,row in excluded.items():
        at=rows[typ]
        assert struct.unpack_from('<I',blob,at+28)[0]==row['num_projectiles']
        if row['reason']=='named_shotgun':
            assert list(struct.unpack_from('<III',blob,at+4))==row['name_hashes']
            assert struct.unpack_from('<f',blob,at+24)[0]==row['calibre']
            assert 'Shotgun' in row['legacy_name']
        else:
            assert row['reason']=='other_multishot' and row['num_projectiles']>1
    multi={typ for typ,at in rows.items() if struct.unpack_from('<I',blob,at+28)[0]>1}
    assert len(multi)==32 and multi<=set(excluded),'unfiltered multi-projectile record'
    assert profile['p11_type']==318 and 318 not in excluded
    assert struct.unpack_from('<Q',blob,rows[318]+128)[0]==int(profile['p11_unit_hash'],16)
    assert struct.unpack_from('<I',blob,rows[318]+28)[0]==1
    return {'excluded_types':len(excluded),'all_multishot_types':len(multi),
            'p11_excluded_from_filter':True,'offline_table_verified':True,'gameplay_verified':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--table',type=Path,required=True)
    args=parser.parse_args()
    metadata=json.loads((ROOT/'maintenance/projectile-exclusions-25480438.json').read_bytes())
    print(json.dumps(verify(args.table.read_bytes(),metadata),indent=2))
