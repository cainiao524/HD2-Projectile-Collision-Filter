local checks=0
local function check(ok,why) checks=checks+1;assert(ok,why) end
local function setup(typ,n)
    local f=Fixture()
    f.zero(f.system+0xe5040,8192);f.zero(f.system+0x203c,4096)
    f.put(f.weapon,f.raw('05e4e5c2db6e44a2')) -- Allowed pistol: type filter must win.
    f.put(f.base+0x37c7670+typ*8,f.p(f.definition));f.put(f.definition,f.u(typ))
    for slot=0,n-1 do f.slot(slot,1001,typ) end
    return f
end
for typ in pairs(TestProfile('pistols').excluded_projectile_types) do
    for _,scope in ipairs({'pistols','native_no_shotguns'}) do
        local f=setup(typ,32)
        local ok,n=pcall(Core.tick,f.api,TestProfile(scope))
        check(ok and n==0 and #f.writes==0,'every excluded shotgun/multishot type is untouched')
        check(not f.hits[f.system+0x3b040+8],'excluded pellets do not read source records')
        check(not f.hits[f.base+0x33266d8],'excluded pellets do not query weapon manager')
        check(not f.hits[f.base+0x37c7670+typ*8],'excluded pellets do not query definitions')
        local reads=0;for _,count in pairs(f.hits) do reads=reads+count end
        check(reads==10,'32 excluded pellets cost only common reads plus one type page')
    end
    local f=setup(typ,2)
    local ok,n=pcall(Core.tick,f.api,TestProfile('native_weapons'))
    check(ok and n==2 and #f.writes==2,'fourth scope retains each excluded type when ownership passes')
end
for _,scope in ipairs({'pistols','native_no_shotguns','native_weapons'}) do
    local f=setup(22,1)
    check(select(2,pcall(Core.tick,f.api,TestProfile(scope)))==1,'ordinary projectile remains supported')
    f=setup(318,1)
    local ok,n=pcall(Core.tick,f.api,TestProfile(scope))
    check(ok and n==0 and #f.writes==0,'P-11 remains delegated to original addon')
end
for _,scope in ipairs({'pistols','native_no_shotguns'}) do
    local f=setup(351,1)
    local ok,n=pcall(Core.tick,f.api,TestProfile(scope))
    check(ok and n==0 and not f.hits[f.system+0x3b040+8],'unknown types fail closed before source reads')
    f=setup(179,1500)
    ok,n=pcall(Core.tick,f.api,TestProfile(scope))
    check(ok and n==0 and #f.writes==0,'large excluded bursts do not consume candidate write budget')
    f.slot(1700,1001,22)
    f.put(f.base+0x37c7670+22*8,f.p(f.definition));f.put(f.definition,f.u(22))
    ok,n=pcall(Core.tick,f.api,TestProfile(scope))
    check(ok and n==1,'ordinary projectile survives a large mixed shotgun burst')
    for _,field in ipairs({'exclude_shotguns','excluded_projectile_types','projectile_type_max'}) do
        f=setup(22,1);local p=TestProfile(scope);p[field]=nil
        check(not pcall(Core.tick,f.api,p) and #f.writes==0,'missing filter policy cannot silently enable shotguns')
    end
end
do
    local f=setup(351,1)
    check(select(2,pcall(Core.tick,f.api,TestProfile('native_weapons')))==1,'fourth scope retains previous broad type range')
end
return checks
