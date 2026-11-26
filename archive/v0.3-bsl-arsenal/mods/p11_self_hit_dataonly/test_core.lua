local checks=0
local function check(ok,why) checks=checks+1; assert(ok,why) end
local function run(f) return pcall(Core.tick,f.api) end
do
    local f=Fixture(); f.slot(8,9999); f.slot(9,1001,317); f.slot(10,1001,318,2); f.slot(11,1001,318,0x20)
    local ok,n,status=run(f)
    check(ok and n==1 and status=='ready','one local active P11')
    check(#f.writes==1 and f.writes[1].before==0x22 and f.writes[1].after==2,'only 0x20 changed')
    check(f.writes[1].at==f.system+0x203c+14,'exact flag address')
    check(f.peek(f.system+0x203c+16,2)==f.scalar('uint16_t',0x22),'foreign projectile unchanged')
    ok,n=run(f); check(ok and n==0 and #f.writes==1,'idempotent across updates')
    f.slot(7,9999); ok,n=run(f); check(ok and n==0 and #f.writes==1,'reused slot with foreign owner untouched')
    f.slot(7,1001); ok,n=run(f); check(ok and n==1 and #f.writes==2,'new eligible data revalidated')
end
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
    local f=Fixture(); mutate(f); run(f); check(#f.writes==0,'reject invalid identity/ownership')
end
for _,loc in ipairs({'avatar','weapon','source','system','aux','type','flags'}) do
    local f=Fixture()
    local at=({avatar=f.avatar,weapon=f.weapon,source=f.system+0x3b040+36*7+8,
        system=f.base+0x347cea8,aux=f.system+0x3c+28,type=f.system+0xe5040+28,flags=f.system+0x203c+14})[loc]
    f.mutate=function(a,n,hit)
        if a==at and hit==(loc=='flags' and 1 or 2) then f.put(a,string.rep('\0',n)) end
    end
    run(f); check(#f.writes==0,'changed '..loc..' rejected')
end
do
    local f=Fixture(); f.write_error='write_readback_failed'
    local ok,e=run(f); check(not ok and type(e)=='table' and e.fatal and e.reason=='write_readback_failed','write faults are fatal')
    f=Fixture(); f.write_error='changed'; local ok,n=run(f); check(ok and n==0,'changed data skips')
end
do
    local f=Fixture(); f.slot(7,1001,318,0xf7ff)
    local ok,n=run(f); check(ok and n==1 and f.writes[1].after==0xf7df,'all other bits retained')
    check(#f.last_guards<300,'bounded guards')
end
return checks
