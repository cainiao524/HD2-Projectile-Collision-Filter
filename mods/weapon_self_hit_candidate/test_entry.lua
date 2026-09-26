local checks=0
local function check(ok,why) checks=checks+1; assert(ok,why) end
local lines={}
local env={unpack=unpack,update=function() return 'original' end,
    CowboyBingusModLoader={api=1,version=16,open_log=function()
        return {write=function(_,...) for i=1,select('#',...) do lines[#lines+1]=select(i,...) end; return true end,
            flush=function() return true end,close=function() return true end}
    end}}
env.P11SelfHitDataOnly020={} -- Proven P-11 addon may coexist.
local api={close=function() end}
local version={files=function() end,runtime=function() end,anchors=function() end}
local calls=0
local core={tick=function(_,p) calls=calls+1; check(p.scope=='pistols','selected profile propagated'); return 1,'ready' end}
local make=function() return api end
local state=Entry(core,version,make,make,Profile,env)
check(state.status=='waiting_image','wait for loaded image')
env.update(); check(state.status=='enabled' and state.changes==0,'no early write')
env.update(); check(state.changes==1 and calls==1,'candidate update active')
check(state.native_hook==false and state.gameplay_verified==false,'no success claim')
local old=env.update
local all={}
for k,v in pairs(Profile) do all[k]=v end
all.scope='native_weapons'
local second=Entry(core,version,make,make,all,env)
check(second.status=='stopped' and second.reason:find('one weapon self-hit',1,true),'mutual exclusion')
check(env.update==old,'second scope does not replace active callback')
return checks
