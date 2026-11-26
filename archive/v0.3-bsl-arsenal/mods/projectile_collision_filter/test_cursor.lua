-- Synthetic cursor scheduling regressions. No live process or game access.
local checks=0
local profile={scope='p11'}
local function check(ok,message) checks=checks+1;assert(ok,message) end
local function fixture()
    Core.reset()
    local f=Fixture()
    f.put(f.system+0x30,f.u(8))
    return f
end
local function tick(f) return Core.tick(f.api,profile) end
local function foreign(f,first,last)
    for cursor=first,last do f.slot(cursor%2048,9999,22) end
end
local function guard_at(f,at)
    for _,g in ipairs(f.last_guards or {}) do if g.at==at then return true end end
    return false
end

do
    local f=fixture()
    local n,status,stats=tick(f)
    check(n==1 and status=='pending' and stats.p11_changes==1,'first update handles latest slot')
    check(guard_at(f,f.system+0x30),'cursor remains a pre-write guard')
    local count=f.hits[f.system+0x203c+14]
    n,status,stats=tick(f)
    check(n==0 and stats.inspected==1 and stats.pending==0,'successful slot gets a second constructor-completion opportunity')
    check(f.hits[f.system+0x203c+14]==count+1,'second opportunity only reads the cleared flag')
    n,status,stats=tick(f)
    check(n==0 and stats.inspected==0,'retired slot is not repeatedly inspected')
end
for _,delta in ipairs({1,63,64,65}) do
    local f=fixture();tick(f);tick(f)
    foreign(f,8,8+delta-1);f.slot(8,1001)
    f.put(f.system+0x30,f.u(8+delta))
    local n,status,stats=tick(f)
    check(n==1 and stats.p11_changes==1,'delta '..delta..' retains earlier P-11 opportunity')
    check(stats.inspected==delta and stats.dropped==0,'delta '..delta..' is processed without silent loss')
end
do
    local f=fixture();tick(f);tick(f)
    foreign(f,8,207);f.slot(207,1001)
    f.put(f.system+0x30,f.u(208))
    local n,status,stats=tick(f)
    check(n==0 and stats.inspected==128 and stats.pending==200,'200-slot interval is continued, not swept')
    n,status,stats=tick(f)
    check(n==1 and stats.inspected==128 and stats.pending<=200,'remaining interval gets first inspection before prefix retries')
    check(stats.dropped==0,'bounded continuation loses no hints below cap')
end
do
    local f=fixture();tick(f);tick(f)
    f.put(f.system+0x30,f.u(11))
    local n,status,stats=tick(f)
    check(n==0 and stats.pending==3,'multiple incomplete constructor slots retained')
    f.slot(8,1001);foreign(f,9,10)
    n,status,stats=tick(f)
    check(n==1 and stats.pending==0 and stats.retries==3,'earlier incomplete slot gets a retry, not only newest')
end
do
    local f=fixture()
    f.mutate=function(at,n,hit)
        if at==f.system+0x30 and hit==2 then f.put(at,f.u(9)) end
    end
    local n,status,stats=tick(f)
    check(n==0 and stats.rejected_writes==1 and stats.pending==1,'cursor mutation refuses write and retains hint')
    f.mutate=nil;foreign(f,8,8)
    n,status,stats=tick(f)
    check(n==1 and stats.pending==1,'guard-rejected earlier slot receives fresh guards next update')
end
do
    local f=fixture();f.zero(f.system+0x203c+14,2)
    local n,status,stats
    for i=1,Core.LIMITS.retry_updates do
        n,status,stats=tick(f)
        check(stats.pending==1,'incomplete hint remains within update TTL '..i)
    end
    n,status,stats=tick(f)
    check(stats.pending==0 and stats.expired==1,'expired hint is explicitly retired')
    f.slot(7,1001)
    n,status,stats=tick(f)
    check(n==0 and stats.inspected==0,'same cursor does not renew expired identity-free hints forever')
end
do
    local f=fixture();tick(f);tick(f)
    foreign(f,8,407);f.slot(8,1001);f.slot(407,1001)
    f.put(f.system+0x30,f.u(408))
    local n,status,stats=tick(f)
    check(status=='cursor_backlog' and stats.dropped==144,'overflow is explicit, not a silent delta>64 drop')
    check(stats.inspected==128 and stats.pending==256,'overflow work remains bounded')
    n,status,stats=tick(f)
    check(n==1 and f.writes[#f.writes].at==f.system+0x203c+2*407,'newest retained window is continued')
    check(f.peek(f.system+0x203c+16,2)==f.scalar('uint16_t',0x22),'discarded older opportunity is not secretly full-scanned')
end
do
    local f=fixture();tick(f);tick(f)
    foreign(f,2040,2047);foreign(f,0,7)
    f.put(f.system+0x30,f.u(0xfffffff8))
    local n,status,stats=tick(f)
    check(status=='cursor_overrun' and stats.overrun and stats.inspected<=128,'ambiguous reset/jump reports overrun with bounded work')
    -- Establish the wrapped frontier in the same fixture; all previous pending
    -- hints are safe to revalidate and cannot carry a cached write permission.
    foreign(f,2040,2047);f.slot(2047,1001)
    f.put(f.system+0x30,f.u(0))
    n,status,stats=tick(f)
    if n==0 then n,status,stats=tick(f) end
    check(n==1 and f.writes[#f.writes].at==f.system+0x203c+4094,'uint32 and 2048-slot ring wrap retain new P-11')
end
do
    local f=fixture();f.zero(f.system+0x203c+14,2)
    tick(f)
    f.slot(7,9999) -- pending slot was recycled to a different owner
    local n,status,stats=tick(f)
    check(n==0 and stats.pending==0 and #f.writes==0,'pending hint rechecks ownership after reuse')
end
for _,before in ipairs({'foreign','cleared','written'}) do
    local f=fixture()
    if before=='foreign' then f.slot(7,9999,318)
    elseif before=='cleared' then f.slot(7,1001,318,2) end
    local n,status,stats=tick(f)
    check(n==(before=='written' and 1 or 0) and stats.pending==1,'pre-fill '..before..' content retains a second opportunity')
    -- Native constructor now fills the slot after having exposed its cursor.
    -- It may replace a foreign/cleared occupant, or overwrite our first clear.
    f.slot(7,1001)
    n,status,stats=tick(f)
    check(n==1 and stats.pending==0,'post-fill P-11 is processed after '..before..' content')
end
do
    local f=fixture();tick(f);tick(f)
    f.put(f.system+0x30,f.u(10));f.slot(8,1001);f.slot(9,1001)
    -- One malformed candidate must not suppress the later valid P-11.
    f.slot(8,1001,318,0x22,0xffffffff,999)
    f.map(f.wm+0x50,0x36200000,{[201]=0,[999]=7})
    local n,status,stats=tick(f)
    check(n==1 and stats.invalid_candidates==1,'one corrupt candidate fails closed while later P-11 is handled')
    check(stats.pending==2,'malformed retry and successful second opportunity are bounded')
end
do
    local f=fixture();tick(f);tick(f)
    f.zero(f.system+0x203c,4096)
    f.put(f.system+0x30,f.u(264)) -- 256 incomplete hints
    local n,status,stats=tick(f)
    check(stats.inspected==128 and stats.pending==256,'incomplete busy prefix is capped')
    f.slot(263,1001)
    n,status,stats=tick(f)
    check(n==1 and stats.inspected==128,'uninspected suffix takes priority over repeatedly incomplete prefix')
end
do
    local f=fixture();f.zero(f.system+0x203c+14,2);tick(f)
    f.put(f.pm+0x84,f.u(0)..f.u(0))
    local n,status,stats=tick(f)
    check(status=='waiting_player' and Core.state==nil,'no local player clears all pending hints')
end

return checks
