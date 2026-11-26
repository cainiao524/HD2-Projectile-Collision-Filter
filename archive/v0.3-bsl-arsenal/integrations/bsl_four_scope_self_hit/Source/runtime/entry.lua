-- Optimized four-scope research test, API 1; individual projectile processing.
return function(Core,Version,MakeImage,MakeData,Profile,env)
    local marker='PCFFourScopeScript032'
    -- The shared legacy marker rejects old/new handlers in either load order.
    -- A repeated loader evaluation must not install another callback.
    local existing=rawget(env,marker)
    local loader=rawget(env,'CowboyBingusModLoader')
    if existing then
        if type(existing)=='table' and existing.integrated_cursor==true
            and existing.scope==Profile.scope and existing.version==Profile.version then return existing end
        local conflict={status='stopped',reason='Existing self-hit addon or different scope is already loaded; restart after selecting one package.',
            changes=0,gameplay_verified=false,native_hook=false,scope=Profile.scope,version=Profile.version}
        if type(loader)=='table' and type(loader.open_log)=='function' then
            pcall(function()
                local duplicate_log=loader.open_log('PCFFourScopeScriptConflict.log')
                if duplicate_log then duplicate_log:write('STOPPED: '..conflict.reason..'\n'); duplicate_log:flush(); duplicate_log:close() end
            end)
        end
        return conflict
    end
    if type(loader)~='table' or type(loader.open_log)~='function' then return nil end
    local opened,log=pcall(loader.open_log,'PCFFourScopeScript.log')
    if not opened or not log then return nil end
    local state={status='initializing',changes=0,gameplay_verified=false,native_hook=false,
        scope=Profile.scope,version=Profile.version,integrated_cursor=true}
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
        pcall(note,'STOPPED: '..reason..'; data writes='..state.changes..'; this package gameplay remains unverified')
        if api then pcall(api.close) end
        pcall(function() log:close() end)
        if wrapper and rawget(env,'update')==wrapper then rawset(env,'update',previous) end
        if shutdown_wrapper and rawget(env,'shutdown')==shutdown_wrapper then rawset(env,'shutdown',previous_shutdown) end
    end
    local function conflicts()
        assert(rawget(env,marker)==state,'Self-hit addon marker changed')
        for _,name in ipairs({'StimSelfHitExperimental01','StimSelfHitDataOnly','StimSelfHitDataOnly01',
            'P11StimSelfHitDataOnly11','P11OwnedProjectileObserver25480438','P11ReadOnlyCapture25480438',
            'WeaponSelfHitPistolsCandidate010','WeaponSelfHitNativeNoShotgunsCandidate012',
            'WeaponSelfHitNativeCandidate010','P11SelfHitDataOnly020','PCFNativeLocalSelfHit030','PCFP11ScriptSelfHit030','PCFP11ScriptSelfHit031','PCFFourScopeScript031'}) do
            assert(not rawget(env,name),'Disable other self-hit/research addon: '..name)
        end
    end
    local ok,err=pcall(function()
        note('Projectile Collision Filter Optimized Test '..tostring(Profile.version)..' / scope='..tostring(Profile.scope)..' / build 25480438')
        note('BSL Lua only: no game.dll code patch, no scanner, no native hook. Only local owner-checked runtime flag 0x20.')
        note('Type-first policy gate and hard per-update budget are enabled; P-11 type 318 is always covered. Shotgun/multishot are excluded only in the no-shotgun scopes.')
        note('LOADER: API='..tostring(loader.api)..'; internal='..tostring(loader.version)
            ..'; supported v17/v18 (internal 16/17).')
        assert(Profile.loader.api==1 and Profile.loader.internal_min==16
            and Profile.loader.internal_max==17,'Unsupported loader policy')
        assert(loader.api==Profile.loader.api and type(loader.version)=='number'
            and (loader.version==16 or loader.version==17),
            'Unsupported loader: API='..tostring(loader.api)..'; internal='..tostring(loader.version)
            ..'; supported API 1, internal 16/17 (v17/v18)')
        assert(type(previous)=='function','Existing update unavailable')
        assert(Profile.scope=='p11' or Profile.scope=='pistols' or Profile.scope=='native_no_shotguns'
            or Profile.scope=='native_weapons','Unsupported scope')
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
            Version.files(api,Profile)
            enabled=true; state.status='enabled'
            note('ENABLED: virtual sections and all 12 base + 3 cursor + 8 research anchors match; startup updates='..startup_frames..'. Arsenal controls this addon.')
        else
            state.last_error=tostring(reason)
            if startup_frames==1 then note('WAITING IMAGE: '..state.last_error) end
            if startup_frames>=Profile.startup_timeout_updates then stop(state.last_error) end
        end
    end
    wrapper=function(...)
        if not stopped and enabled then
            local worked,failure=pcall(function()
                frames=frames+1
                if frames==1 or frames%120==0 then conflicts() end
                if frames%120==0 then Version.anchors(api,Profile) end
                local ticked,count,status,stats=pcall(Core.tick,api,Profile)
                if not ticked then
                    if type(count)=='table' and count.fatal then error(count.reason,0) end
                    state.status,state.last_error='waiting_data',tostring(count)
                    if not state.reported_skip then state.reported_skip=true; note('SKIPPING unstable/unavailable data: '..state.last_error) end
                    return
                end
                state.status=status
                state.changes=state.changes+count
                if type(stats)=='table' then
                    state.cursor_stats=stats
                    if (stats.entity_alias_rejections or 0)>0 and not state.reported_entity_alias then
                        state.reported_entity_alias=true
                        note('SKIP SOURCE ENTITY: weapon entity equals local avatar entity; no write for that candidate.')
                    end
                    local overruns=status=='cursor_overrun' and 1 or 0
                    local drops=tonumber(stats.dropped) or 0
                    local expired=tonumber(stats.expired) or 0
                    state.cursor_overruns=(state.cursor_overruns or 0)+overruns
                    state.cursor_dropped=(state.cursor_dropped or 0)+drops
                    state.cursor_expired=(state.cursor_expired or 0)+expired
                    if (overruns>0 or drops>0 or expired>0)
                        and (not state.last_overrun_log or frames-state.last_overrun_log>=600) then
                        state.last_overrun_log=frames
                        note('CURSOR BUDGET: overruns='..state.cursor_overruns..'; dropped='..state.cursor_dropped
                            ..'; expired='..state.cursor_expired..'; bounded work can miss a projectile; not gameplay proof.')
                    end
                end
                if status=='ready' and not state.first_ready then
                    state.first_ready=true; note('READY: local player/definition checks passed; data writes='..state.changes)
                end
                if count>0 and not state.first_write then
                    state.first_write=true; note('FIRST DATA WRITE READ BACK: not proof of collision, healing or self-damage')
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
