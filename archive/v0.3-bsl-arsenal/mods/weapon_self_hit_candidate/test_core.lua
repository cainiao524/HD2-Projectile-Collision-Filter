local checks=0
local function check(ok,why) checks=checks+1; assert(ok,why) end
local P2='05e4e5c2db6e44a2'
local OTHER='4a00000000000001'
local function setup(resource,owner)
    local f=Fixture()
    f.put(f.weapon, f.raw(resource))
    f.put(f.base+0x37c7670+22*8,f.p(f.definition))
    f.put(f.definition,f.u(22))
    f.slot(7,owner or 1001,22)
    return f
end
local function tick(f,scope)
    return pcall(Core.tick,f.api,TestProfile(scope))
end
do
    local f=setup(P2)
    local ok,n,status=tick(f,'pistols')
    check(ok and n==1 and status=='ready','pistol projectile selected')
    check(#f.writes==1 and f.writes[1].before==0x22 and f.writes[1].after==0x2,'only source bit cleared')
    ok,n=tick(f,'pistols'); check(ok and n==0,'idempotent')
end
do
    local f=setup(OTHER)
    local ok,n=tick(f,'pistols'); check(ok and n==0 and #f.writes==0,'non-pistol rejected in pistol mode')
    ok,n=tick(f,'native_weapons'); check(ok and n==1,'local registered weapon accepted in broad mode')
end
do
    local f=Fixture()
    local ok,n=tick(f,'native_weapons')
    check(ok and n==0 and #f.writes==0,'P-11 remains untouched')
end
for _,mutate in ipairs({
    function(f) f.slot(7,9999,22) end,
    function(f) f.put(f.attach+4,f.u(999)) end,
    function(f) f.put(f.weapon+8,f.u(999)) end,
    function(f) f.put(f.weapon+20,f.u(0)) end,
    function(f) f.put(f.definition,f.u(23)) end,
    function(f) f.slot(7,1001,22,0x20) end,
    function(f) f.slot(7,1001,22,0x2) end,
    function(f) f.slot(7,1001,318) end,
}) do
    local f=setup(P2); mutate(f); tick(f,'native_weapons')
    check(#f.writes==0,'invalid candidate rejected')
end
do
    local f=setup(P2)
    f.write_error='changed'
    local ok,n=tick(f,'pistols'); check(ok and n==0 and #f.writes==0,'identity change skips write')
    f.write_error='write_failed'
    local success,err=tick(f,'pistols')
    check(not success and type(err)=='table' and err.fatal,'write failure is fatal')
end
do
    local f=setup(P2)
    local profile=TestProfile('pistols');profile.pistol_unit_hashes={}
    local success=pcall(Core.tick,f.api,profile)
    check(not success and #f.writes==0,'empty pistol mapping fails closed')
end
return checks
