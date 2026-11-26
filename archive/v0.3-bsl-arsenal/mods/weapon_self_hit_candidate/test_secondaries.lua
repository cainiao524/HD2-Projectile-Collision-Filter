-- Real build-profile regression using synthetic memory only. An invented
-- native slot checks filtering/guards, not that a weapon actually creates one.
local checks=0
local function check(ok,why) checks=checks+1;assert(ok,why) end
local profile=assert(TestProfiles.pistols)
local P2,P11,OTHER='05e4e5c2db6e44a2','d6b1fb05b9109353','4a00000000000001'
-- Offline reference EquipmentType labels this primary as Pistol. Family
-- selection must not therefore admit it, even with a shared projectile type.
local STALWART='a6a735accb4a327f'
local legacy={
    '05e4e5c2db6e44a2','8d3d52a3b2f19402','3575aabc5f1f9326','c780bcd79547da0f',
    'cf8934ff6567a42d','1a437158e1b8d2a1','dbb6c961c59fadc1','4d58c77087b774c5',
}
local function setup(n,resource,typ)
    local f=Fixture();typ=typ or 22
    f.zero(f.system+0xe5040,8192);f.zero(f.system+0x203c,4096)
    f.put(f.weapon,f.raw(resource))
    f.put(f.base+0x37c7670+typ*8,f.p(f.definition));f.put(f.definition,f.u(typ))
    for slot=0,n-1 do f.slot(slot,1001,typ) end
    return f
end
local function tick(f,p) return pcall(Core.tick,f.api,p or profile) end
local function reads(f)
    local total=0;for _,n in pairs(f.hits) do total=total+n end;return total
end
local old_profile={};for k,v in pairs(profile) do old_profile[k]=v end
old_profile.pistol_unit_hashes=legacy
local read_counts={}
for _,count in ipairs({0,1,32,64}) do
    local old=setup(count,P2);local old_ok,old_n=tick(old,old_profile)
    local current=setup(count,P2);local ok,n=tick(current)
    check(old_ok and ok and old_n==count and n==count,'original P-2 behavior survives catalog expansion')
    check(reads(old)==reads(current),'larger catalog adds no game-memory reads for original P-2')
    read_counts[count]=reads(current)
end

for _,resource in ipairs(profile.pistol_unit_hashes) do
    local f=setup(32,resource);local ok,n=tick(f)
    check(ok and n==32 and #f.writes==32,'real profile source identity is recognized: '..resource)
    check(reads(f)==read_counts[32],'each catalog source has the same bounded memory-read cost as P-2')
    check(f.hits[f.weapon]==33,'one identity discovery plus a fresh check for every write')
    for _,write in ipairs(f.writes) do
        check(write.before==0x22 and write.after==0x2,'catalog expansion changes only the exclusion bit')
    end
    f=setup(2,resource);f.slot(1,9999,22)
    ok,n=tick(f)
    check(ok and n==1 and #f.writes==1 and f.writes[1].at==f.system+0x203c,
          'only the local source unit is modified for each catalog identity')
    f=setup(1,resource);f.put(f.attach+4,f.u(9999))
    ok,n=tick(f)
    check(ok and n==0 and #f.writes==0,'catalog identity cannot replace attachment ownership')
    f=setup(1,resource);f.put(f.weapon+8,f.u(9999));tick(f)
    check(#f.writes==0,'catalog identity cannot replace weapon-entity identity')
end

for _,resource in ipairs({OTHER,STALWART,P11}) do
    local f=setup(32,resource);local ok,n=tick(f)
    check(ok and n==0 and #f.writes==0,'nonsecondary/P-11 resource is rejected even with accepted type 22')
    check(not f.hits[f.base+0x3326dc0],'rejected resource does not query attachment ownership')
end

-- Source-weapon identity is authoritative even when two weapons emit the same
-- projectile type; there is no currently-equipped-weapon shortcut.
do
    local selected=profile.pistol_unit_hashes[#profile.pistol_unit_hashes]
    local f=setup(2,selected);local second=f.weapon+0x100
    f.put(f.wm+0x38,f.u(2));f.put(f.wm+0x3c,f.u(2))
    f.put(f.ptrs+8,f.p(second));f.entity(second,f.raw(STALWART),202,2002,7)
    f.map(f.wm+0x50,0x36200000,{[201]=0,[202]=1})
    f.slot(1,1001,22,0x22,0xffffffff,202)
    local ok,n=tick(f)
    check(ok and n==1 and #f.writes==1 and f.writes[1].at==f.system+0x203c,
          'shared projectile type does not authorize the primary source weapon')
end

-- Every current excluded type must win before source ownership or resource
-- lookup, regardless of which real catalog identity would otherwise match.
local filter_sources={OTHER,STALWART}
for _,resource in ipairs(profile.pistol_unit_hashes) do filter_sources[#filter_sources+1]=resource end
for typ in pairs(profile.excluded_projectile_types) do
    for _,resource in ipairs(filter_sources) do
        local f=setup(1,resource,typ);local ok,n=tick(f)
        check(ok and n==0 and #f.writes==0,'shotgun/multishot exclusion remains prior to family matching')
        check(not f.hits[f.system+0x3b040+8] and not f.hits[f.base+0x33266d8]
              and not f.hits[f.base+0x37c7670+typ*8],
              'excluded type performs no source, weapon or definition lookup')
        check(reads(f)==10,'excluded type keeps its fixed common-read cost')
    end
end

local selected=profile.pistol_unit_hashes[#profile.pistol_unit_hashes]
-- Reuse or ownership changes between discovery and the mock writer must be
-- detected by the same fresh dependency checks used for legacy identities.
for _,mutate in ipairs({
    function(f) f.put(f.weapon,f.raw(STALWART)) end,
    function(f) f.put(f.weapon+8,f.u(202)) end,
    function(f) f.put(f.ptrs,f.p(f.weapon+0x100)) end,
    function(f) f.put(f.attach+4,f.u(9999)) end,
    function(f) f.put(f.system+0x3b040+8,f.u(9999)) end,
    function(f) f.put(f.system+0x3b040+12,f.u(202)) end,
    function(f) f.put(f.system+0xe5040,f.u(318)) end,
}) do
    local f=setup(1,selected);local writer=f.api.clear_exclusion
    f.api.clear_exclusion=function(system,slot,expected,guards)
        mutate(f);return writer(system,slot,expected,guards)
    end
    local ok,n=tick(f)
    check(ok and n==0 and #f.writes==0,'fresh guards reject recycled source/weapon/owner before writing')
end
do
    local f=setup(1,selected);local ok,n=tick(f)
    check(ok and n==1,'real profile source initially accepted')
    f.put(f.weapon,f.raw(STALWART));f.slot(0,1001,22);f.hits={}
    ok,n=tick(f)
    check(ok and n==0 and #f.writes==1,'accepted identity does not authorize a reused weapon next tick')
end
return checks
