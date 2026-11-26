local checks=0
local function check(ok,why) checks=checks+1;assert(ok,why) end
for _,scope in ipairs({'pistols','native_no_shotguns','native_weapons'}) do
 for _,reverse in ipairs({false,true}) do
  for _,fail in ipairs({false,true}) do
   local calls,p11_calls,expanded_calls,closed=0,0,0,0
   local env={unpack=unpack}
   local base=function(a,b,c) calls=calls+1;check(a=='first' and b==nil and c=='last','arguments preserved');return 'return',nil,3 end
   env.update=base
   env.CowboyBingusModLoader={api=1,version=16,open_log=function()
    return {write=function() return true end,flush=function() return true end,close=function() return true end}
   end}
   local version={files=function() end,runtime=function() end,anchors=function() end}
   local make=function() return {close=function() closed=closed+1 end} end
   local p11={tick=function() p11_calls=p11_calls+1;return 1,'ready' end}
   local expanded={tick=function() expanded_calls=expanded_calls+1;if fail then error({fatal=true,reason='fixture_failure'}) end;return 1,'ready' end}
   local profile={loader={api=1,internal_min=16,internal_max=16},startup_retry_updates=120,startup_timeout_updates=600,scope=scope}
   local a,b
   if reverse then
    b=Entry(expanded,version,make,make,profile,env);a=P11Entry(p11,version,make,make,profile,env)
   else
    a=P11Entry(p11,version,make,make,profile,env);b=Entry(expanded,version,make,make,profile,env)
   end
   for frame=1,3 do
    local x,y,z=env.update('first',nil,'last')
    check(x=='return' and y==nil and z==3,'return values preserved')
   end
   check(calls==3 and p11_calls==2,'P-11 and original callback kept running')
   check(a.changes==2,'P-11 unaffected by expanded failure or load order')
   check(expanded_calls==(fail and 1 or 2),'expanded scope lifecycle')
   if fail then check(b.status=='stopped','expanded fatal failure remains stopped') end
   env.shutdown()
   check(closed==2 and a.status=='stopped' and b.status=='stopped','both resources close on shutdown')
  end
 end
end
return checks
