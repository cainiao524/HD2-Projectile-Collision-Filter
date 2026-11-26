-- Isolated synthetic memory regression. Passing this is not gameplay evidence.
local checks=0
local function check(ok,why) checks=checks+1; assert(ok,why) end
local SCOPES={'p11','pistols','native_no_shotguns','native_weapons'}
local P2,P11,PRIMARY='05e4e5c2db6e44a2','d6b1fb05b9109353','a6a735accb4a327f'
local function run(f,scope,core)
    return pcall((core or f.core).tick,f.api,TestProfiles[scope or 'p11'])
end
local function setup(typ,resource)
    local f=Fixture(); f.core=NewCore()
    if typ then f.slot(7,1001,typ); f.source_weapon(resource or P2,typ) end
    return f
end
local function prime(scope)
    local f=setup(); f.blank()
    check(run(f,scope),'empty initial update is valid')
    return f
end
for _,scope in ipairs(SCOPES) do
    local f=setup()
    local ok,n=run(f,scope)
    check(ok and n==1 and #f.writes==1,'P-11 is included exactly once in '..scope)
    check(f.writes[1].before==0x22 and f.writes[1].after==2,'only exclusion bit changes')
    check(not f.hits[f.system+0x203c] and not f.hits[f.system+0xe5040], 'unrelated slots are not swept')
    check(f.max_read<4096,'no whole flags/type page read')
    ok,n=run(f,scope)
    check(ok and n==0 and #f.writes==1,'same dart is idempotent')
    local _,_,_,idle=run(f,scope)
    check(idle.inspected==0,'idle update does not re-scan a retired hint')
    f.slot(7,9999)
    ok,n=run(f,scope)
    check(ok and n==0 and #f.writes==1,'reused latest slot with foreign owner is rejected')
    f=setup(); f.slot(7,9999)
    ok,n=run(f,scope)
    check(ok and n==0 and #f.writes==0 and not f.hits[f.base+0x33266d8],
          'foreign source rejected before weapon discovery in '..scope)
end

for _,scope in ipairs(SCOPES) do
    for _,mutate in ipairs({
        function(f) f.put(f.pm+0x84,f.u(0)..f.u(0)) end,
        function(f) f.put(f.avatar+16,f.u(9)) end,
        function(f) f.put(f.avatar+20,f.u(0)) end,
        function(f) f.put(f.weapon,f.raw('0000000000000000')) end,
        function(f) f.put(f.weapon+8,f.u(202)) end,
        function(f) f.put(f.weapon+20,f.u(0)) end,
        function(f) f.put(f.attach+4,f.u(999)) end,
        function(f) f.put(f.definition,f.u(317)) end,
        function(f) f.put(f.definition+0x80,f.raw('0000000000000000')) end,
        function(f) f.put(f.definition+0xfc,'\0') end,
        function(f) f.put(f.wm+0x3c,f.u(0)) end,
        function(f) f.put(f.wm+0x2c,f.u(4097)) end,
        function(f) f.slot(7,1001,318,0x22,0xffffffff,101) end,
    }) do
        local f=setup(); mutate(f); run(f,scope)
        check(#f.writes==0,'invalid P-11 identity/ownership is rejected in '..scope)
    end
end

for typ in pairs(TestProfiles.pistols.excluded_projectile_types) do
    for _,scope in ipairs(SCOPES) do
        local f=setup(typ)
        local ok,n=run(f,scope)
        if scope=='native_weapons' then
            check(ok and n==1,'fourth scope allows known excluded type '..typ)
        else
            check(ok and n==0 and #f.writes==0,'first three reject shotgun/multishot type '..typ)
            check(not f.hits[f.system+0x3b040+36*7+8] and not f.hits[f.base+0x33266d8],
                'excluded type rejected before source and weapon lookups')
        end
    end
end

for _,resource in ipairs(TestProfiles.pistols.pistol_unit_hashes) do
    local f=setup(22,resource)
    local ok,n=run(f,'pistols')
    check(ok and n==1,'catalog source recognized: '..resource)
    f=setup(22,resource); f.put(f.attach+4,f.u(9999)); run(f,'pistols')
    check(#f.writes==0,'catalog membership does not replace attachment ownership')
    f=setup(22,resource); f.slot(7,9999,22); run(f,'pistols')
    check(#f.writes==0,'catalog membership does not replace local source unit')
end
for _,scope in ipairs(SCOPES) do
    local f=setup(22,PRIMARY)
    local ok,n=run(f,scope)
    check(ok and n==((scope=='native_no_shotguns' or scope=='native_weapons') and 1 or 0),
          'sidearm scope uses actual source identity, not shared type or AI category')
end
for _,scope in ipairs({'p11','pistols','native_no_shotguns'}) do
    local f=setup(351)
    local ok,n=run(f,scope)
    check(ok and n==0 and not f.hits[f.system+0x3b040+36*7+8], 'unknown type excluded before owner lookup')
end
do
    local f=setup(351)
    check(select(2,run(f,'native_weapons'))==1,'fourth scope preserves broader bounded native type range')
end

-- One shared work queue must not lose an entire 65-projectile update.
for _,scope in ipairs(SCOPES) do
    local f=prime(scope)
    for slot=0,64 do f.slot(slot,1001) end
    f.cursor(65)
    for i=1,3 do
        local before=#f.writes
        local ok,n,status,stats=run(f,scope)
        check(ok and n<=64 and #f.writes-before<=64,'per-update write budget holds')
        check(stats and stats.inspected<=128 and stats.pending<=256,'inspection and pending budgets hold')
    end
    check(#f.writes==65,'all 65 eligible hints are eventually processed in '..scope)
end
do
    local f=prime('native_weapons')
    f.source_weapon(P11,22) -- Add a generic definition without changing P-11 identity.
    local second=f.weapon+0x100
    f.put(f.wm+0x38,f.u(2)); f.put(f.wm+0x3c,f.u(2))
    f.put(f.ptrs+8,f.p(second)); f.entity(second,f.raw(P2),202,2002,7)
    f.map(f.wm+0x50,0x36200000,{[201]=0,[202]=1})
    f.map(f.am+0x20,0x36100000,{[201]=0,[202]=1})
    f.zero(f.attach+48,48); f.put(f.attach+52,f.u(101))
    for slot=0,64 do f.slot(slot,1001,22,0x22,0xffffffff,202) end
    f.slot(65,1001); f.cursor(66)
    local ok,n,status,stats=run(f,'native_weapons')
    check(ok and n==64 and stats.p11_changes==1 and stats.other_changes==63,
          'P-11 receives shared write budget before other known candidates')
    check(f.writes[1].at==f.system+0x203c+130,'P-11 is handled once by the common priority flow')
    for _=1,3 do run(f,'native_weapons') end
    check(#f.writes==66,'deferred expanded candidates finish without duplicate P-11 writes')
end
do
    local f=setup(); check(select(2,run(f))==1,'baseline local P-11 accepted')
    f.cursor(11); f.slot(9,1001); f.slot(10,1001)
    check(select(2,run(f))==2,'completed slots around earlier incomplete slot proceed')
    f.slot(8,1001)
    check(select(2,run(f))==1 and f.writes[#f.writes].at==f.system+0x203c+16,
          'earlier incomplete slot is retried after cursor has moved past it')
end
do
    local f=prime('p11')
    f.slot(0,1001,318,2) -- cursor moved, but old cleared lifetime still visible
    f.slot(1,9999) -- old foreign lifetime
    f.slot(2,1001,22) -- old out-of-scope lifetime
    f.cursor(3)
    local ok,n=run(f)
    check(ok and n==0,'valid-looking old occupants are not modified')
    for slot=0,2 do f.slot(slot,1001) end
    ok,n=run(f)
    check(ok and n==3,'fresh hints recheck terminal observations on a later update')
end
do
    local f=setup(); run(f)
    f.cursor(10); f.slot(8,1001); f.slot(9,1001)
    local writer=f.api.clear_exclusion; local rejected=false
    f.api.clear_exclusion=function(system,slot,expected,guards)
        if slot==8 and not rejected then rejected=true; return false,'changed' end
        return writer(system,slot,expected,guards)
    end
    local ok,n,status,stats=run(f)
    check(ok and rejected and n==1 and stats.rejected_writes==1,'write recheck rejection does not abort other slots')
    ok,n=run(f)
    check(ok and n==1 and f.writes[#f.writes].at==f.system+0x203c+16,'changed writer result remains pending')
end
do
    local f=setup(); run(f)
    f.cursor(10); f.slot(9,1001); run(f)
    f.slot(8,9999); local ok,n=run(f)
    check(ok and n==0 and #f.writes==2,'pending slot reused by foreign shooter is never written')
end
do
    local f=prime('p11'); f.cursor(3)
    run(f)
    for i=1,16 do run(f) end
    f.slot(0,1001)
    check(select(2,run(f))==0,'expired earlier hint does not stay pending indefinitely')
end
do
    local f=prime('p11'); f.cursor(4096)
    local ok,n,status,stats=run(f)
    check(ok and n==0 and stats.dropped>0 and stats.pending<=256 and stats.inspected<=128,
          'ring overrun reports dropped hints with bounded work')
    check(status=='cursor_overrun' or stats.overrun or stats.overruns,'overrun is explicit')
end
do
    local f=setup(); f.cursor(0xffffffff); f.slot(2046,1001); run(f)
    f.cursor(0); f.slot(2047,1001)
    check(select(2,run(f))==1 and f.writes[#f.writes].at==f.system+0x203c+4094,
          'unsigned 32-bit cursor wrap reaches final ring slot')
end

-- Each dependency handed to the writer is mutated independently after lookup.
for _,scope in ipairs({'p11','pistols'}) do
    local f=scope=='p11' and setup() or setup(22)
    check(select(2,run(f,scope))==1 and #f.last_guards>=20,'full guard chain recorded')
    local dependencies=f.last_guards
    for _,dependency in ipairs(dependencies) do
        local t=scope=='p11' and setup() or setup(22)
        local writer=t.api.clear_exclusion
        t.api.clear_exclusion=function(system,slot,expected,guards)
            local original=t.peek(dependency.at,1)
            assert(original,'fixture guard byte missing')
            t.put(dependency.at,string.char((original:byte()+1)%256))
            return writer(system,slot,expected,guards)
        end
        run(t,scope)
        check(#t.writes==0,'fresh guarded writer rejects changed dependency')
    end
    for _,dependency in ipairs(dependencies) do
        if dependency.at~=f.system+0x3b040+36*7+8 and dependency.at~=f.system+0xe5040+28
            and dependency.at~=f.system+0x3c+28 then
            local t=prime(scope)
            if scope~='p11' then t.source_weapon(P2,22) end
            t.slot(0,1001,scope=='p11' and 318 or 22)
            t.slot(1,1001,scope=='p11' and 318 or 22); t.cursor(2)
            local writer=t.api.clear_exclusion
            t.api.clear_exclusion=function(system,slot,expected,guards)
                if slot==1 then
                    local original=t.peek(dependency.at,1)
                    assert(original,'fixture shared guard byte missing')
                    t.put(dependency.at,string.char((original:byte()+1)%256))
                end
                return writer(system,slot,expected,guards)
            end
            local ok,n=run(t,scope)
            check(ok and n==1 and #t.writes==1,'same-update cache hit preserves every shared writer guard')
        end
    end
end
do
    local f=setup(); f.write_error='write_readback_failed'
    local ok,e=run(f)
    check(not ok and type(e)=='table' and e.fatal and e.reason=='write_readback_failed','readback failure is fatal')
end
do
    local f=setup(); f.slot(7,1001,318,0xf7ff)
    check(select(2,run(f))==1 and f.writes[1].after==0xf7df,'unrelated runtime flags preserved')
end
for _,scope in ipairs({'pistols','native_no_shotguns'}) do
    for _,field in ipairs({'exclude_shotguns','excluded_projectile_types','projectile_type_max'}) do
        local f=setup(22)
        local p={}; for k,v in pairs(TestProfiles[scope]) do p[k]=v end; p[field]=nil
        check(not pcall(f.core.tick,f.api,p) and #f.writes==0,'missing exclusion policy never enables a broader scope')
    end
end
do
    local f=setup(); local p={scope='unknown'}
    check(not pcall(f.core.tick,f.api,p) and f.reads==0,'unknown scope rejected before data access')
    f=setup(22); p={}; for k,v in pairs(TestProfiles.pistols) do p[k]=v end
    p.pistol_unit_hashes={}
    check(not pcall(f.core.tick,f.api,p) and f.reads==0,'empty sidearm catalog rejected before data access')
    p.pistol_unit_hashes={'not-a-weapon-id'}
    check(not pcall(f.core.tick,f.api,p) and f.reads==0,'malformed sidearm identity rejected before data access')
end
return checks
