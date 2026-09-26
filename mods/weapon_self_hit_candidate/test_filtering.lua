local checks=0
local function check(ok,why) checks=checks+1;assert(ok,why) end
local P2,OTHER='05e4e5c2db6e44a2','4a00000000000001'
local function setup(n,resource,owner)
    local f=Fixture()
    f.zero(f.system+0xe5040,8192);f.zero(f.system+0x203c,4096)
    f.put(f.weapon,f.raw(resource or P2))
    f.put(f.base+0x37c7670+22*8,f.p(f.definition));f.put(f.definition,f.u(22))
    for slot=0,n-1 do f.slot(slot,owner or 1001,22) end
    return f
end
local function tick(f,scope)
    return pcall(Core.tick,f.api,TestProfile(scope or 'pistols'))
end
local function reads(f)
    local n=0;for _,v in pairs(f.hits) do n=n+v end;return n
end
do
    local f=setup(0)
    f.slot(0,1001,22,0x20) -- source exclusion without an occupied slot
    f.slot(1,1001,22,0x2) -- occupied but already cleared
    local ok,n=tick(f)
    check(ok and n==0,'flag-only rejection does not write')
    check(not f.hits[f.system+0xe5040] and not f.hits[f.system+0xe6040],'no eligible flags means no type pages read')
end
do
    local f=setup(0)
    f.slot(1600,1001,22)
    local ok,n=tick(f)
    check(ok and n==1,'second type-page candidate is processed')
    check(not f.hits[f.system+0xe5040] and f.hits[f.system+0xe6040]==1,'only the needed type page is loaded')
end
do
    local f=setup(32,OTHER)
    local ok,n=tick(f)
    check(ok and n==0 and #f.writes==0,'non-pistol shot rejected')
    check(f.hits[f.weapon]==1,'one weapon identity discovery per update')
    check(not f.hits[f.base+0x3326dc0],'rejected weapon needs no attachment query')
    check(not f.hits[f.base+0x37c7670+22*8],'rejected weapon needs no definition query')
    check(reads(f)<=64,'32 rejected pellets have bounded discovery reads')
    -- Rejected identities are not remembered across updates or weapon reuse.
    f.put(f.weapon,f.raw(P2));f.hits={}
    ok,n=tick(f)
    check(ok and n==32,'new frame reclassifies previously rejected weapon')
end
do
    local f=setup(32,OTHER,9999)
    local ok,n=tick(f,'native_weapons')
    check(ok and n==0 and not f.hits[f.base+0x33266d8],'foreign owner skipped before weapon lookup')
end
do
    local f=setup(32)
    local ok,n=tick(f)
    check(ok and n==32 and #f.writes==32,'all selected pellets retain behavior')
    check(f.hits[f.weapon]==33,'one discovery plus fresh identity recheck per write')
    check(reads(f)<1100,'selected multi-pellet discovery reads reduced')
    f.hits={};ok,n=tick(f)
    check(ok and n==0 and not f.hits[f.weapon],'already-cleared slots do not repeat discovery')
end
do
    local f=setup(2)
    f.put(f.wm+0x38,f.u(2));f.put(f.wm+0x3c,f.u(2))
    local second=f.weapon+0x100
    f.put(f.ptrs+8,f.p(second));f.entity(second,f.raw(OTHER),202,2002,7)
    f.map(f.wm+0x50,0x36200000,{[201]=0,[202]=1})
    f.slot(1,1001,22,0x22,0xffffffff,202)
    local ok,n=tick(f)
    check(ok and n==1 and #f.writes==1,'same projectile type cannot authorize a different source weapon')
end
do
    local f=setup(2)
    f.slot(1,1001,23)
    f.put(f.base+0x37c7670+23*8,f.p(f.definition+0x400))
    f.put(f.definition+0x400,f.u(999))
    local ok,n=tick(f)
    check(ok and n==1,'definition cache is keyed by projectile type')
end
-- Capture all shared dependency guards, then mutate each after the first write.
-- This covers cache hits with recycled pointers, registry entries, weapon bytes,
-- attachment ownership, player identity and definition identity.
local shared={}
do
    local f=setup(1)
    local original=f.api.clear_exclusion
    f.api.clear_exclusion=function(system,slot,expected,guards)
        for _,g in ipairs(guards) do
            if g.at~=f.system+0x3b040+8 and g.at~=f.system+0xe5040 and g.at~=f.system+0x3c then
                shared[#shared+1]={at=g.at,bytes=g.bytes}
            end
        end
        return original(system,slot,expected,guards)
    end
    check(select(2,tick(f))==1 and #shared>=20,'capture complete shared guard chain')
end
for _,dependency in ipairs(shared) do
    local f=setup(2)
    local changed=false
    f.mutate=function(at)
        if not changed and at==f.system+0x3b040+36+8 then
            changed=true
            local byte=f.peek(dependency.at,1):byte()
            f.put(dependency.at,string.char((byte+1)%256))
        end
    end
    local ok,n=tick(f)
    check(changed and ok and n==1 and #f.writes==1,'cache hit still rejects changed dependency')
end
do
    local f=setup(2)
    f.mutate=function(at)
        if at==f.system+0x3b040+36+8 then f.put(f.system+0xe5040+4,f.u(318)) end
    end
    tick(f)
    check(#f.writes==1,'fresh slot type prevents reused P-11 slot write')
end
do
    local f=setup(2)
    f.mutate=function(at)
        if at==f.system+0x3b040+36+8 then f.put(at,f.u(9999)) end
    end
    local ok,n=tick(f)
    check(ok and n==1,'fresh source read prevents foreign slot write')
end
do
    local f=setup(1)
    check(select(2,tick(f))==1,'first tick accepts local weapon')
    f.put(f.weapon,f.raw(OTHER));f.slot(0,1001,22)
    local ok,n=tick(f)
    check(ok and n==0 and #f.writes==1,'accepted identities are not cached across updates')
end
return checks
