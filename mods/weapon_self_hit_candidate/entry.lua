-- Standard API 1 callback composition; Arsenal selects one candidate scope.
return function(Core,Version,MakeImage,MakeData,Profile,env)
    local markers={pistols='WeaponSelfHitPistolsCandidate010',
        native_no_shotguns='WeaponSelfHitNativeNoShotgunsCandidate012',
        native_weapons='WeaponSelfHitNativeCandidate010'}
    local marker=assert(markers[Profile.scope],'invalid_scope')
    if rawget(env,marker) then return rawget(env,marker) end
    local loader=rawget(env,'CowboyBingusModLoader')
    if type(loader)~='table' or type(loader.open_log)~='function' then return nil end
    local opened,log=pcall(loader.open_log,'WeaponSelfHitCandidate.log')
    if not opened or not log then return nil end
    local state={status='initializing',changes=0,gameplay_verified=false,native_hook=false}
    rawset(env,marker,state)
    local previous,previous_shutdown=rawget(env,'update'),rawget(env,'shutdown')
    local wrapper,shutdown_wrapper,api; local stopped=false; local frames=0
    local enabled=false; local startup_frames=0
    local unpack_values=env.unpack or unpack
    local function pack(...) return {n=select('#',...),...} end
    local function note(s) assert(log:write(s,'\n')); assert(log:flush()) end
    local function stop(reason)
        if stopped then return end
        stopped=true; state.status,state.reason='stopped',reason
        pcall(note,'STOPPED: '..reason..'; data writes='..state.changes..'; self-damage remains unverified')
        if api then pcall(api.close) end
        pcall(function() log:close() end)
        if wrapper and rawget(env,'update')==wrapper then rawset(env,'update',previous) end
        if shutdown_wrapper and rawget(env,'shutdown')==shutdown_wrapper then rawset(env,'shutdown',previous_shutdown) end
    end
    local function conflicts()
        for _,other in pairs(markers) do
            assert(other==marker or not rawget(env,other),'Enable only one weapon self-hit candidate scope')
        end
    end
    local ok,err=pcall(function()
        note('Weapon Self-Hit '..Profile.scope..' '..tostring(Profile.version or 'candidate')..' DATA-ONLY CANDIDATE / build 25480438')
        note('Only local owner-checked native projectile flag 0x20; P-11 excluded. No native hook. Self-damage is NOT verified.')
        note(Profile.exclude_shotguns and 'Projectile policy: skip known shotguns, all pinned multi-projectile types and unknown types before source lookup.'
            or 'Projectile policy: include shotgun and multi-projectile types; increased per-pellet work is possible.')
        assert(loader.api==Profile.loader.api and type(loader.version)=='number'
            and loader.version>=Profile.loader.internal_min and loader.version<=Profile.loader.internal_max,'Unsupported loader')
        assert(type(previous)=='function','Existing update unavailable')
        conflicts()
        assert(Profile.startup_retry_updates==120 and Profile.startup_timeout_updates==600,'Invalid startup schedule')
        api=MakeData(Profile,MakeImage); Version.files(api,Profile)
        note('WAITING IMAGE: file hashes match; loaded-layout validation begins after the existing update callback. No data writes yet.')
    end)
    if not ok then stop(tostring(err)); return state end
    state.status='waiting_image'
    local function initialize_after_update()
        startup_frames=startup_frames+1
        if startup_frames~=1 and startup_frames%Profile.startup_retry_updates~=0 then return end
        local ready,reason=pcall(Version.runtime,api,Profile)
        if ready then
            Version.files(api,Profile) -- Recheck files at the point of activation.
            enabled=true; state.status='enabled'
            note('ENABLED: virtual sections and all 12 anchors match; startup updates='..startup_frames..'. Arsenal controls this candidate.')
        else
            state.last_error=tostring(reason)
            if startup_frames==1 then note('WAITING IMAGE: '..state.last_error) end
            if startup_frames>=Profile.startup_timeout_updates then stop(state.last_error) end
        end
    end
    wrapper=function(...)
        if not stopped and enabled then
            local worked,failure=pcall(function()
                conflicts(); frames=frames+1
                if frames%120==0 then Version.anchors(api,Profile) end
                local ticked,count,status=pcall(Core.tick,api,Profile)
                if not ticked then
                    if type(count)=='table' and count.fatal then error(count.reason,0) end
                    state.status,state.last_error='waiting_data',tostring(count)
                    if not state.reported_skip then state.reported_skip=true; note('SKIPPING unstable/unavailable data: '..state.last_error) end
                    return
                end
                state.status=status
                state.changes=state.changes+count
                if status=='ready' and not state.first_ready then
                    state.first_ready=true; note('READY: local player/definition checks passed; data writes='..state.changes)
                end
                if count>0 and not state.first_write then
                    state.first_write=true; note('FIRST DATA WRITE READ BACK: not proof of collision or self-damage')
                end
            end)
            if not worked then stop(tostring(failure)) end
        end
        local result=pack(pcall(previous,...))
        if not result[1] then stop('Previous update failed'); error(result[2],0) end
        if not stopped and not enabled then
            local ready,reason=pcall(initialize_after_update)
            if not ready then stop(tostring(reason)) end
        end
        return unpack_values(result,2,result.n)
    end
    shutdown_wrapper=function(...)
        stop('Shutdown')
        if type(previous_shutdown)=='function' then return previous_shutdown(...) end
    end
    rawset(env,'update',wrapper); rawset(env,'shutdown',shutdown_wrapper)
    return state
end
