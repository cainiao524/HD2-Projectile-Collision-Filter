local checks=0
local function check(ok,why) checks=checks+1; assert(ok,why) end
local function fixture(options)
    options=options or {}; local calls,closes,verifies,anchors,runtimes,old_calls=0,0,0,0,0,0; local lines={}; local mode='ready'
    local old=function(a,b) old_calls=old_calls+1; if options.previous_error then error('upstream broke') end; return a,nil,b end
    local shutdown=function(...) return 'shutdown',... end
    local env={update=old,shutdown=shutdown,unpack=unpack,
        CowboyBingusModLoader={api=options.api or 1,version=options.version or 16,open_log=function()
            return {write=function(self,...) for i=1,select('#',...) do lines[#lines+1]=select(i,...) end; return self end,
                flush=function() return true end,close=function() return true end}
        end}}
    if options.conflict then env.StimSelfHitExperimental01={} end
    local api={close=function() closes=closes+1 end}
    local core={tick=function()
        calls=calls+1
        if mode=='missing' then error('data_unavailable') end
        if mode=='write_error' then error({fatal=true,reason='write_readback_failed'},0) end
        return 1,'ready'
    end}
    local version={files=function()
            verifies=verifies+1
            assert(not options.hash_error and not (options.activation_hash_error and verifies>1),'wrong game files')
        end,
        runtime=function()
            runtimes=runtimes+1; assert(old_calls>0,'runtime validation must follow existing update')
            assert(not options.layout_error and runtimes>(options.delay_checks or 0),'Loaded section 3 rva differs')
        end,
        anchors=function() anchors=anchors+1; assert(not options.anchor_error,'code changed') end}
    local make=function() return api end
    local state=Entry(core,version,make,make,Profile,env)
    return {env=env,state=state,old=old,shutdown=shutdown,core=core,version=version,make=make,
        mode=function(s) mode=s end,counts=function() return calls,closes,verifies,anchors,runtimes end,
        lines=function() return table.concat(lines) end}
end
do
    local f=fixture(); check(f.state.status=='waiting_image','no gameplay work during loader discovery')
    local a,b,c=f.env.update('a','b'); check(a=='a' and b==nil and c=='b','nil returns preserved')
    check(f.state.status=='enabled' and f.state.changes==0,'first update validates without writes')
    f.env.update()
    check(f.state.changes==1 and f.lines():find('FIRST DATA WRITE READ BACK',1,true),'write counted without healing claim')
    check(f.state.gameplay_verified==false and f.state.native_hook==false,'candidate remains unverified')
    local count=f.counts(); check(count==1,'one scan per update')
    local again=Entry(f.core,f.version,f.make,f.make,Profile,f.env); check(again==f.state,'duplicate initialization suppressed')
    f.env.shutdown('x'); local _,closes=f.counts(); check(closes==1,'adapter closed')
    check(f.env.update==f.old and f.env.shutdown==f.shutdown,'restore own callbacks only')
end
for _,o in ipairs({{api=2},{version=15},{version=17},{conflict=true},{hash_error=true}}) do
    local f=fixture(o); check(f.state.status=='stopped' and f.env.update==f.old,'unsupported or conflict rejected')
    check(f.counts()==0,'no writes before enabled')
end
do
    local f=fixture(); f.env.update(); f.mode('missing'); f.env.update()
    check(f.state.status=='waiting_data','menu/unready data does not permanently disable')
    f.mode('ready'); f.env.update(); check(f.state.changes==1,'recovers when player data becomes available')
    f.mode('write_error'); f.env.update(); check(f.state.status=='stopped','write fault disables further writes')
    local n=f.counts(); f.env.update(); check(f.counts()==n,'no work after stop')
end
do
    local f=fixture({previous_error=true}); local ok,err=pcall(f.env.update)
    check(not ok and tostring(err):find('upstream broke',1,true),'upstream error propagated')
    check(f.state.status=='stopped','stops after upstream failure')
end
do
    local f=fixture(); f.env.update(); local own=f.env.update
    local later=function(...) return own(...) end; f.env.update=later
    f.mode('write_error'); later()
    check(f.env.update==later,'later addon wrapper retained')
end
do
    local f=fixture({anchor_error=true}); f.env.update(); for i=1,120 do f.env.update() end
    check(f.state.status=='stopped' and f.state.changes==119,'changed anchor prevents next write')
end
do
    local f=fixture({delay_checks=1})
    for i=1,119 do f.env.update() end
    check(f.state.status=='waiting_image' and f.counts()==0,'layout still unready: no writes')
    f.env.update(); check(f.state.status=='enabled' and f.counts()==0,'deferred validation can recover')
    f.env.update(); check(f.state.changes==1,'writes only after complete validation')
    local _,_,hashes,_,runtime=f.counts(); check(hashes==2 and runtime==2,'files checked again before activation')
end
do
    local f=fixture({layout_error=true}); for i=1,600 do f.env.update() end
    check(f.state.status=='stopped' and f.counts()==0,'persistent wrong layout never bypassed')
    check(f.state.reason:find('section 3 rva',1,true),'specific field failure retained')
    local _,closes,_,_,runtime=f.counts(); check(closes==1 and runtime==6,'bounded startup attempts')
end
do
    local f=fixture({activation_hash_error=true}); f.env.update()
    check(f.state.status=='stopped' and f.counts()==0,'disk identity changed before activation')
end
return checks
