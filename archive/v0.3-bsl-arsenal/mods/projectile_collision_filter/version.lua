-- Version checks only. The executable bytes below are read, never patched.
local V = {}
local function get(s, at, n)
    assert(type(s)=='string' and #s>=at+n, 'Short version read')
    local value=0; for i=n,1,-1 do value=value*256+s:byte(at+i) end
    return value
end
function V.files(api, p)
    assert(p.schema_version==1 and p.build_id==25480438, 'Unknown addon profile')
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
end
return V
