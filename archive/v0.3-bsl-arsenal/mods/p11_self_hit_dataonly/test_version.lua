-- Header and instruction fixtures were read from the existing offline capture.
local checks=0
local function check(ok,why) checks=checks+1; assert(ok,why) end
local function fixture()
    local s={header=Header,game=Profile.game_sha256,exe=Profile.exe_sha256}
    s.api={file_hashes=function() return {game_sha256=s.game,exe_sha256=s.exe} end,
        read=function(rva,n)
            if rva==0 then return s.header end
            local bytes=AnchorFixture[rva]
            if s.bad_anchor and bytes then return string.rep('\0',n) end
            return bytes
        end}
    return s
end
do local f=fixture(); check(pcall(Version.check,f.api,Profile),'current capture layout and hashes') end
for _,kind in ipairs({'game','exe','header','anchor'}) do
    local f=fixture()
    if kind=='header' then f.header='NZ'..f.header:sub(3)
    elseif kind=='anchor' then f.bad_anchor=true else f[kind]=string.rep('0',64) end
    check(not pcall(Version.check,f.api,Profile),'reject '..kind..' mismatch')
end
do local f=fixture(); f.header=f.header:sub(1,400); check(not pcall(Version.check,f.api,Profile),'truncated header') end
local function set_u32(s,at,n)
    local bytes={}; for i=1,4 do bytes[i]=string.char(n%256); n=math.floor(n/256) end
    return s:sub(1,at)..table.concat(bytes)..s:sub(at+5)
end
local section_start=Profile.pe_offset+24+Profile.optional_size
for section=1,4 do
    for _,field in ipairs({{8,'virtual_size'},{12,'rva'},{36,'characteristics'}}) do
        local f=fixture(); local at=section_start+(section-1)*40+field[1]
        f.header=set_u32(f.header,at,0)
        local ok,err=pcall(Version.check,f.api,Profile)
        check(not ok and tostring(err):find('section '..section..' '..field[2],1,true),'required virtual field still rejected')
        check(tostring(err):find('expected=',1,true) and tostring(err):find('actual=',1,true),'actual/expected diagnostic')
    end
end
do
    local f=fixture()
    for section=1,Profile.section_count do
        local at=section_start+(section-1)*40
        f.header=set_u32(f.header,at+16,0); f.header=set_u32(f.header,at+20,0)
    end
    check(pcall(Version.check,f.api,Profile),'disk raw sizes/offsets are validated by hashes, not loaded metadata')
    f.game=string.rep('0',64)
    check(not pcall(Version.check,f.api,Profile),'raw metadata policy does not bypass file hash')
end
do
    local f=fixture(); f.header=set_u32(f.header,section_start+4*40+8,0)
    check(pcall(Version.check,f.api,Profile),'unused packer section not used for gameplay addressing')
    f.bad_anchor=true; check(not pcall(Version.check,f.api,Profile),'all code anchors still required')
end
return checks
