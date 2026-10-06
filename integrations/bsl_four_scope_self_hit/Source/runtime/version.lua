-- Version checks only. The executable bytes below are read, never patched.
local V = {}
local RESEARCH_ANCHORS={
    {name='source_weapon_object_entity',rva=6382949,bytes_hex='8b4008'},
    {name='source_weapon_entity_store',rva=20620526,bytes_hex='8984964cb00300'},
    {name='first_source_entity_compare',rva=20629135,bytes_hex='433b9c874cb00300'},
    {name='first_source_entity_skip',rva=20629143,bytes_hex='0f84c1070000'},
    {name='accepted_hit_effect_flag',rva=20633688,bytes_hex='f680fc00000001'},
    {name='accepted_hit_stim_dispatch_flag',rva=20633866,bytes_hex='f680fc00000001'},
    {name='accepted_hit_effect_call_a',rva=20634039,bytes_hex='e8b4c3e1ff'},
    {name='accepted_hit_effect_call_b',rva=20634170,bytes_hex='e831c4e1ff'}
}
local function get(s, at, n)
    assert(type(s)=='string' and #s>=at+n, 'Short version read')
    local value=0; for i=n,1,-1 do value=value*256+s:byte(at+i) end
    return value
end
function V.files(api, p)
    assert(p.schema_version==1 and p.build_id==25480438, 'Unknown addon profile')
    assert((p.scope=='p11' or p.scope=='pistols' or p.scope=='native_no_shotguns' or p.scope=='native_weapons')
        and p.version=='0.3.2-bsl-four' and p.resource=='mods/pcf/bsl_four_scope_self_hit'
        and p.manager_guid=='f344360d-eb4a-4baa-b631-8e6982ecd9fb', 'Unknown BSL four-scope profile')
    local h=api.file_hashes()
    assert(h.game_sha256==p.game_sha256 and h.exe_sha256==p.exe_sha256, 'Unsupported game files')
end
function V.runtime(api,p)
    local b=assert(api.read(0,4096), 'Loaded image unreadable')
    local pe=p.pe_offset; local opt=pe+24
    assert(b:sub(1,2)=='MZ' and get(b,0x3c,4)==pe and b:sub(pe+1,pe+4)=='PE\0\0', 'Unexpected image header')
    assert(get(b,pe+4,2)==0x8664 and get(b,opt,2)==0x20b and get(b,opt+32,4)==4096, 'Unsupported image architecture')
    assert(get(b,pe+8,4)==p.timestamp and get(b,opt+56,4)==p.image_size, 'Unsupported loaded build')
    assert(get(b,pe+6,2)==p.section_count and get(b,pe+20,2)==p.optional_size and #p.sections==p.section_count, 'Unsupported sections')
    -- Raw sizes/offsets describe file layout, already pinned by both hashes.
    -- Validate the original virtual sections covering every used RVA/anchor.
    -- Additional packer sections are not used to locate gameplay data.
    assert(type(p.loaded_section_indices)=='table' and #p.loaded_section_indices==4,'Missing virtual-section policy')
    for order,i in ipairs(p.loaded_section_indices) do
        assert(i==order,'Unexpected virtual-section policy')
        local s=p.sections[i]
        local at=opt+p.optional_size+(i-1)*40
        for _,field in ipairs({{8,'virtual_size'},{12,'rva'},{36,'characteristics'}}) do
            local actual,expected=get(b,at+field[1],4),s[field[2]]
            assert(actual==expected,string.format('Loaded section %d %s differs: expected=%08X actual=%08X',i,field[2],expected,actual))
        end
    end
    V.anchors(api,p)
end
function V.check(api,p) V.files(api,p); V.runtime(api,p) end
function V.anchors(api,p)
    assert(#p.code_anchors==12, 'Missing code anchors')
    for _,a in ipairs(p.code_anchors) do
        local bytes=a.bytes_hex:gsub('..',function(x) return string.char(tonumber(x,16)) end)
        assert(api.read(a.rva,#bytes)==bytes, 'Code anchor differs: '..a.name)
    end
    assert(type(p.cursor_anchors)=='table' and #p.cursor_anchors==3,'Missing cursor anchors')
    for _,a in ipairs(p.cursor_anchors) do
        local bytes=a.bytes_hex:gsub('..',function(x) return string.char(tonumber(x,16)) end)
        assert(api.read(a.rva,#bytes)==bytes, 'Cursor anchor differs: '..a.name)
    end
    assert(type(p.research_anchors)=='table' and #p.research_anchors==8,'Missing research anchors')
    for i,expected in ipairs(RESEARCH_ANCHORS) do
        local a=p.research_anchors[i]
        assert(type(a)=='table' and a.name==expected.name and a.rva==expected.rva
            and a.bytes_hex==expected.bytes_hex,'Research anchor policy differs')
        local bytes=expected.bytes_hex:gsub('..',function(x) return string.char(tonumber(x,16)) end)
        assert(api.read(expected.rva,#bytes)==bytes,'Research anchor differs: '..expected.name)
    end
end
return V
