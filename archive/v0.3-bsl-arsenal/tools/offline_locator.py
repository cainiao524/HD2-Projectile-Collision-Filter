"""Exact on-disk signature candidates only; never authorize runtime addresses."""
from pathlib import Path

def locate(data,sections,pattern,limit=32):
    needle=bytes.fromhex(pattern)
    if len(needle)<16:raise ValueError('signature is too short for a useful candidate')
    matches=[];start=0;truncated=False
    while True:
        at=data.find(needle,start)
        if at<0:break
        start=at+1
        for section in sections:
            delta=at-section['raw_offset']
            if section['characteristics'] & 0x20000000 and 0<=delta and delta+len(needle)<=section['raw_size']:
                if len(matches)==limit:truncated=True;break
                matches.append({'file_offset':at,'rva':section['rva']+delta,'section':section['name']})
                break
        if truncated:break
    return {'candidates':matches,'truncated':truncated,'runtime_verified':False,'can_enable_feature':False,
        'status':'offline_bytes_absent' if not matches else 'unique_unverified_candidate' if len(matches)==1 and not truncated else 'ambiguous_candidates'}

def scan(binary,pe,locators):
    p=Path(binary)
    if p.stat().st_size>256*1024*1024:raise ValueError('binary exceeds bounded offline scan size')
    data=p.read_bytes();results=[]
    for locator in locators:
        results.append({'id':locator['id'],'affected_features':locator['affected_features'],
            'purpose':locator['purpose'],**locate(data,pe.get('sections',[]),locator['bytes_hex'])})
    return results
