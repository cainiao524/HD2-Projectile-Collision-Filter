"""Bounded read-only Stingray resource inspection; never execute resources."""
import io
import re
import struct
from pathlib import Path

LUA_TYPE = 0xA14E8DFA2CD117E2

def resource_hash(name):
    data=name.encode('utf-8'); mask=(1<<64)-1; mix=0xC6A4A7935BD1E995
    value=len(data)*mix & mask; end=len(data)//8*8
    for (word,) in struct.iter_unpack('<Q',data[:end]):
        word=word*mix & mask; word ^= word>>47
        value=(value ^ (word*mix & mask))*mix & mask
    if data[end:]: value=(value ^ int.from_bytes(data[end:],'little'))*mix & mask
    value ^= value>>47; value=value*mix & mask
    return value ^ (value>>47)

def lua_resources(stream, size):
    def read(at,n):
        if at<0 or n<0 or at+n>size: raise ValueError('resource range outside archive')
        stream.seek(at); data=stream.read(n)
        if len(data)!=n: raise ValueError('truncated resource archive')
        return data
    magic,types,count=struct.unpack('<III',read(0,12))
    if magic!=0xF0000011 or types>4096 or count>100000: raise ValueError('unsupported archive header')
    table=72+types*32; data_start=table+count*80
    if data_start>size: raise ValueError('truncated resource table')
    entries=read(table,count*80)
    for index in range(count):
        e=struct.unpack_from('<7Q6I',entries,index*80)
        if e[1]!=LUA_TYPE: continue
        if e[2]<data_start: raise ValueError('Lua overlaps resource table')
        if e[7]>8*1024*1024: raise ValueError('Lua resource exceeds collection limit')
        raw=read(e[2],e[7])
        if len(raw)<8: raise ValueError('truncated Lua envelope')
        length,version=struct.unpack_from('<II',raw)
        if version!=2 or length+8!=len(raw): raise ValueError('unsupported Lua envelope')
        body=raw[8:]; marker=re.match(rb'-- HD2-Addon: (mods/[A-Za-z0-9_/]+)\r?\n',body[:256])
        declared=marker[1].decode('ascii') if marker else None
        if declared and resource_hash(declared)!=e[0]: raise ValueError('addon declaration/resource hash mismatch')
        yield {'resource_hash':f'{e[0]:016x}','declaration':declared,'body':body}

def inspect_file(path):
    path=Path(path)
    with path.open('rb') as stream: return list(lua_resources(stream,path.stat().st_size))

def make_archive(name, source):
    body=source.encode('utf-8') if isinstance(source,str) else source
    payload=struct.pack('<II',len(body),2)+body
    offset=192; end=(offset+len(payload)+15)&~15
    header=struct.pack('<III20sQQ24s',0xF0000011,1,1,b'',end,0,b'')
    types=struct.pack('<IIQIIII',0,0,LUA_TYPE,1,0,16,16)
    entry=struct.pack('<7Q6I',resource_hash(name),LUA_TYPE,offset,0,0,0,0,len(payload),0,0,16,16,0)
    return (header+types+entry).ljust(offset,b'\0')+payload+b'\0'*(end-offset-len(payload))

def make_lua_archive(resources):
    """Pack independent Lua resources in one native archive, without merging code."""
    if not resources: raise ValueError('empty Lua resource archive')
    items=sorted(resources.items(),key=lambda item:resource_hash(item[0]))
    if len(items)==1: return make_archive(*items[0])
    hashes=[resource_hash(name) for name,_ in items]
    if len(set(hashes))!=len(hashes): raise ValueError('duplicate Lua resource identity')
    offset=(72+32+80*len(items)+15)&~15
    payloads=bytearray();entries=[]
    for index,((name,source),identity) in enumerate(zip(items,hashes)):
        body=source.encode('utf-8') if isinstance(source,str) else source
        payload=struct.pack('<II',len(body),2)+body
        start=offset+len(payloads)
        entries.append(struct.pack('<7Q6I',identity,LUA_TYPE,start,0,0,0,0,len(payload),0,0,16,16,index))
        payloads.extend(payload);payloads.extend(b'\0'*(-len(payloads)%16))
    end=offset+len(payloads)
    header=struct.pack('<III20sQQ24s',0xF0000011,1,len(items),b'',end,0,b'')
    types=struct.pack('<IIQIIII',0,0,LUA_TYPE,len(items),0,16,16)
    return (header+types+b''.join(entries)).ljust(offset,b'\0')+payloads
