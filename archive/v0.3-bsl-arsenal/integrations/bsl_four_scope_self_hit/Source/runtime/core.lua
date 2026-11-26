-- Optimized four-scope research test; still processes individual owned projectiles. The native allocation cursor is a
-- discovery hint, never a generation ID or permission to write. Every candidate
-- gets fresh identity/ownership guards; no address or guard survives an update.
local bit=require('bit')
local M={
    -- P-11 uses a tighter per-update budget than the broad research scopes.
    -- Excess work is deferred instead of creating a frame spike.
    -- Broad scopes remain bounded; shotgun/multishot gets the tightest budget
    -- so bursts cannot turn the update hook into an unbounded scan.
    LIMITS={pending=128,inspect=64,retry_updates=8,minimum_inspections=2,writes=16,reads=6000,bytes=131072},
    P11_LIMITS={pending=64,inspect=32,retry_updates=4,minimum_inspections=2,writes=4,reads=1000,bytes=65536},
    SHOTGUN_LIMITS={pending=64,inspect=32,retry_updates=6,minimum_inspections=2,writes=8,reads=3000,bytes=98304}
}
local RING,UINT32,FAST_HEARTBEAT=2048,4294967296,30
local function raw(h) return (h:gsub('..',function(x) return string.char(tonumber(x,16)) end)):reverse() end
local P11,AVATAR,STIM=raw('d6b1fb05b9109353'),raw('4d1c334d294dfa97'),raw('4431931242cbcd54')
-- Build-time decoded constants from the pinned profile; no runtime identity or authorization.
-- Unknown valid policy hashes keep the original decoder fallback.
local DECODED_PISTOLS={
    ['05e4e5c2db6e44a2']='\162\068\110\219\194\229\228\005',
    ['0b882808c6f498e8']='\232\152\244\198\008\040\136\011',
    ['14d5d4506056c7a4']='\164\199\086\096\080\212\213\020',
    ['1a437158e1b8d2a1']='\161\210\184\225\088\113\067\026',
    ['3575aabc5f1f9326']='\038\147\031\095\188\170\117\053',
    ['416d053372c4e433']='\051\228\196\114\051\005\109\065',
    ['4d58c77087b774c5']='\197\116\183\135\112\199\088\077',
    ['52e4334e6a128caf']='\175\140\018\106\078\051\228\082',
    ['8d3d52a3b2f19402']='\002\148\241\178\163\082\061\141',
    ['9eb160830321bfd6']='\214\191\033\003\131\096\177\158',
    ['aa69a60d74a3ec54']='\084\236\163\116\013\166\105\170',
    ['bde1f2534280300d']='\013\048\128\066\083\242\225\189',
    ['c780bcd79547da0f']='\015\218\071\149\215\188\128\199',
    ['cf8934ff6567a42d']='\045\164\103\101\255\052\137\207',
    ['dbb6c961c59fadc1']='\193\173\159\197\097\201\182\219',
    ['e91f569c2ad8af01']='\001\175\216\042\156\086\031\233',
}
-- Accepted pointers are below 2^47, so LuaJIT numbers retain every bit.
-- Decode the two little-endian halves directly and avoid cdata in the hot path.
local function value(s,at)
    at=at or 0
    assert(type(s)=='string' and #s>=at+8,'short_read')
    local a,b,c,d,e,f,g,h=s:byte(at+1,at+8); assert(h,'short_read')
    return a+b*256+c*65536+d*16777216+(e+f*256+g*65536+h*16777216)*UINT32
end
local function mul_u32_low(a,b)
    local a0,a1=a%65536,math.floor(a/65536)
    local b0,b1=b%65536,math.floor(b/65536)
    local cross=(a0*b1+a1*b0)%65536
    return (a0*b0+cross*65536)%UINT32
end
local function u(s,at)
    at=at or 0
    local a,b,c,d=s:byte(at+1,at+4)
    assert(d,'short_read'); return a+b*256+c*65536+d*16777216
end
function M.reset() M.state=nil end

function M.tick(api,profile)
    local scope=profile and profile.scope
    assert(scope=='p11' or scope=='pistols' or scope=='native_no_shotguns' or scope=='native_weapons','invalid_scope')
    if scope=='p11' then
        assert(profile.exclude_shotguns==true,'invalid_projectile_policy')
    else
        assert(profile.exclude_shotguns==(scope~='native_weapons'),'invalid_projectile_policy')
        if profile.exclude_shotguns then
            assert(type(profile.excluded_projectile_types)=='table'
                and next(profile.excluded_projectile_types)~=nil
                and profile.projectile_type_max==350,'missing_projectile_filter')
            assert(not profile.excluded_projectile_types[318],'p11_filter_conflict')
        end
    end
    local allowed
    for _,h in ipairs(profile.pistol_unit_hashes or {}) do
        assert(type(h)=='string' and h:match('^[0-9a-f]+$') and #h==16,'invalid_allowlist')
        if scope=='pistols' then allowed=allowed or {};allowed[DECODED_PISTOLS[h] or raw(h)]=true end
    end
    assert(scope~='pistols' or (allowed and next(allowed)~=nil),'empty_allowlist')
    local limit=scope=='p11' and M.P11_LIMITS
        or scope=='native_weapons' and M.SHOTGUN_LIMITS
        or M.LIMITS
    local stats={reads=0,bytes=0,inspected=0,discovered=0,dropped=0,expired=0,retries=0,
        rejected_writes=0,invalid_candidates=0,pending=0,cursor_delta=0,p11_changes=0,other_changes=0,attempts=0}
    local changes=0
    local guards={}
    local function read(at,n,guard)
        stats.reads,stats.bytes=stats.reads+1,stats.bytes+n
        assert(stats.reads<=limit.reads and stats.bytes<=limit.bytes and n<=4096,'read_budget')
        local s=assert(api.read_data(at,n),'data_unavailable')
        assert(#s==n,'short_read')
        if guard then guards[#guards+1]={at=at,bytes=s} end
        return s
    end
    local function pointer(at)
        local p=value(read(at,8,true),0)
        assert(p>=65536 and p<0x800000000000 and p%1==0,'invalid_pointer'); return p
    end
    local function map(at,key,max)
        local h=read(at,20,true); local cap,empty,mult=u(h,8),u(h,12),u(h,16)
        assert(cap<=max and (cap==0 or bit.band(cap,cap-1)==0),'map_bounds')
        if cap==0 or key==empty then return nil end
        local p=value(h,0); assert(p>=65536 and p<0x800000000000,'map_pointer')
        local product=mul_u32_low(key,mult)
        for probe=0,math.min(cap,128)-1 do
            local row=read(p+8*bit.band(product+probe,cap-1),8,true)
            if u(row)==key then return u(row,4)~=0xffffffff and u(row,4) or nil end
            if u(row)==empty then return nil end
        end
        error('map_probe_limit')
    end
    local function entity(at,resource,id,net)
        local b=read(at,24,true)
        assert(b:sub(1,8)==resource and bit.band(u(b,20),3)==1,'entity_identity')
        assert((not id or u(b,8)==id) and (not net or u(b,16)==net),'entity_reused')
        return u(b,8),u(b,12)
    end
    local base=api.base
    -- When no slot is pending, a cursor-only read is safe: no write can occur
    -- until a cursor change forces the full player/avatar/owner validation
    -- below. This removes the repeated player-map walk from idle frames while
    -- preserving the owner and slot-reuse guards on every write.
    local function fast_read(at,n)
        stats.reads,stats.bytes=stats.reads+1,stats.bytes+n
        if stats.reads>limit.reads or stats.bytes>limit.bytes then return nil end
        local bytes=api.read_data(at,n)
        return bytes and #bytes==n and bytes or nil
    end
    local prior=M.state
    if prior and prior.scope==scope and prior.system and #prior.pending==0 then
        -- Re-read the global system pointer before using the cached cursor. This
        -- prevents a respawn/world rebuild from turning the idle shortcut into
        -- a stale owner path. Every 30 idle updates refreshes full identity.
        local system_bytes=fast_read(base+0x347cea8,8)
        if system_bytes then
            local system_now=value(system_bytes,0)
            -- Keep the idle shortcut fail-closed if the world rebuild leaves
            -- a transient or malformed system pointer in the data slot.
            if system_now>=65536 and system_now<0x800000000000 then
                local cursor_bytes=fast_read(system_now+0x30,4)
                if cursor_bytes then
                    local cursor_now=u(cursor_bytes)
                    local age=(prior.frame or 0)+1
                    if system_now==prior.system and cursor_now==prior.cursor and age%FAST_HEARTBEAT~=0 then
                        M.state={system=system_now,cursor=cursor_now,unit=prior.unit,avatar=prior.avatar,
                            scope=scope,frame=age,pending={}}
                        stats.fast_idle=true
                        return 0,'ready',stats
                    end
                end
            else
                M.reset()
            end
        end
    end
    local pm=pointer(base+0x3326468)
    local counts=read(pm+0x84,8,true)
    assert(u(counts)<=4 and u(counts,4)<=4,'player_bounds')
    if u(counts)==0 or u(counts,4)==0 then M.reset(); return 0,'waiting_player',stats end
    local net=u(read(pm+0x3a8,4,true)); local em=pointer(base+0x346bf98)
    local index=map(em+0xf22ec8,net,1048576)
    if not index then M.reset(); return 0,'waiting_player',stats end
    assert(index<262144,'avatar_bounds')
    local avatar,unit=entity(em+0xf32f18+24*index,AVATAR,nil,net)
    assert(avatar~=0xffffffff and unit~=0 and unit~=0xffffffff,'avatar_identity')
    local system=pointer(base+0x347cea8)
    -- Keep the cursor snapshot in the common guards: concurrent native
    -- construction invalidates a write and sends its slot back for rechecking.
    local cursor=u(read(system+0x30,4,true))
    local old=M.state
    if old and (old.system~=system or old.unit~=unit or old.avatar~=avatar or old.scope~=scope) then old=nil;stats.reset=true end
    local frame=old and old.frame+1 or 1
    local delta=old and (cursor-old.cursor)%UINT32 or 0
    stats.cursor_delta=delta
    -- Only scheduling storage is skipped: player, system and cursor identities
    -- were re-read above. Pending hints always keep their second opportunity.
    if old and delta==0 and #old.pending==0 then
        M.state={system=system,cursor=cursor,unit=unit,avatar=avatar,scope=scope,frame=frame,pending={}}
        return 0,'ready',stats
    end
    local queue,by_slot={},{}
    local function append(slot,expires,tries)
        local prior=by_slot[slot]
        if prior then prior.dead=true end
        local hint={slot=slot,expires=expires,tries=tries or 0}
        queue[#queue+1]=hint;by_slot[slot]=hint
    end
    if old and delta<=RING then
        for _,hint in ipairs(old.pending) do
            if hint.expires>=frame then append(hint.slot,hint.expires,hint.tries)
            else stats.expired=stats.expired+1 end
        end
    elseif old then
        -- More than one ring cannot identify which lifetime an old hint meant.
        -- Discard it and consider only the newest bounded window, with all
        -- identities re-read. Never replace uncertainty with a full-ring scan.
        stats.dropped=#old.pending;stats.overrun=true
    end
    if not old then
        append((cursor-1)%RING,frame+limit.retry_updates-1)
        stats.discovered=1
    elseif delta>0 then
        local take=math.min(delta,limit.pending)
        stats.dropped=stats.dropped+delta-take
        for step=take,1,-1 do append((cursor-step)%RING,frame+limit.retry_updates-1) end
        stats.discovered=take
    end
    -- At most 512 temporary hints (old 256 + new 256), compacted to 256.
    -- New allocations replace an older hint for the same slot; that is a fresh
    -- opportunity, not a cached identity or an extension of a failed write.
    local reverse={}
    for i=#queue,1,-1 do
        if not queue[i].dead then
            if #reverse<limit.pending then reverse[#reverse+1]=queue[i]
            else stats.dropped=stats.dropped+1 end
        end
    end
    queue={}
    for i=#reverse,1,-1 do queue[#queue+1]=reverse[i] end

    local common=#guards
    local function reset_guards() for i=#guards,common+1,-1 do guards[i]=nil end end
    local weapons,definitions={},{ }
    -- Cache only within this update and copy every accepted dependency into
    -- each write request; the Windows writer re-reads the complete guard chain.
    local function cached(cache,key,inspect)
        local saved=cache[key]
        if saved then
            if saved.result=='ok' then for _,g in ipairs(saved.guards) do guards[#guards+1]=g end end
            return saved.result
        end
        local first=#guards+1
        local result=inspect()
        local dependencies={}
        if result=='ok' then for i=first,#guards do dependencies[#dependencies+1]=guards[i] end end
        cache[key]={result=result,guards=dependencies}
        return result
    end
    local function weapon_allowed(weapon_id,p11)
        return cached(weapons,(p11 and 'p11:' or 'other:')..weapon_id,function()
            local wm=pointer(base+0x33266d8)
            local wi=map(wm+0x50,weapon_id,8192)
            if not wi then return 'retry' end
            local cap=u(read(wm+0x2c,4,true)); local counts=read(wm+0x38,8,true)
            local count,committed=u(counts),u(counts,4)
            assert(count<=cap and cap<=4096 and committed<=count and wi<committed,'weapon_bounds')
            local weapon=pointer(pointer(wm+0x68)+wi*8)
            local identity=read(weapon,24,true);local resource=identity:sub(1,8)
            assert(u(identity,8)==weapon_id and bit.band(u(identity,20),3)==1,'weapon_identity')
            if p11 then
                assert(resource==P11,'entity_identity')
            elseif resource==P11 or (scope=='pistols' and not allowed[resource]) then return 'reject' end
            local am=pointer(base+0x3326dc0)
            local ai=map(am+0x20,weapon_id,32768)
            if not ai then return 'retry' end
            assert(ai<16384,'weapon_bounds')
            return u(read(pointer(am+0x40)+48*ai+4,4,true))==avatar and 'ok' or 'reject'
        end)
    end
    local function definition_matches(typ)
        return cached(definitions,typ,function()
            local definition=pointer(base+0x37c7670+typ*8)
            assert(u(read(definition,4,true))==typ,'definition_identity')
            if typ==318 then
                assert(read(definition+0x80,8,true)==STIM
                    and bit.band(read(definition+0xfc,1,true):byte(),1)==1,'definition_identity')
            end
            return 'ok'
        end)
    end
    local waiting,deferred,p11_candidates,other_candidates={},{},{},{}
    -- On bursty maps, read contiguous source records in 32-slot chunks. The
    -- low-rate path keeps an 8-byte read so a single shot never pays for a
    -- large speculative block. These quick reads are only a prefilter; every
    -- local candidate is read again with guards immediately before writing.
    local source_blocks,type_blocks={},{ }
    local batch_sources=#queue>=8
    local batch_types=#queue>=8
    local function type_prefilter(slot)
        if not batch_types then return u(read(system+0xe5040+4*slot,4)) end
        local first=slot-slot%64
        local block=type_blocks[first]
        if not block then
            block=read(system+0xe5040+4*first,4*math.min(64,RING-first))
            type_blocks[first]=block
        end
        return u(block,4*(slot-first))
    end
    local function source_prefilter(slot)
        if not batch_sources then return read(system+0x3b040+36*slot+8,8) end
        local first=slot-slot%32
        local block=source_blocks[first]
        if not block then
            block=read(system+0x3b040+36*first+8,36*31+16)
            source_blocks[first]=block
        end
        local at=36*(slot-first)+1
        return block:sub(at,at+7)
    end
    local function retry(hint) waiting[#waiting+1]=hint end
    local function terminal(hint)
        -- The constructor publishes its cursor before filling the chosen slot.
        -- Its old contents may already look complete, foreign, or cleared. Give
        -- every fresh hint a second update opportunity, even after a successful
        -- write which a late constructor could overwrite. This is bounded
        -- polling, not proof of atomic constructor completion.
        if hint.tries<limit.minimum_inspections then retry(hint) end
    end
    local function invalid(reason,hint)
        stats.invalid_candidates=stats.invalid_candidates+1
        stats.last_rejection=tostring(reason)
        retry(hint)
    end
    local function discover(hint)
        local slot=hint.slot
        -- Type is the cheapest policy gate. P-11 rejects every non-318 slot
        -- here; no owner or weapon reads are spent on foreign/shotgun slots.
        local typ=type_prefilter(slot)
        if typ==0 then return 'retry' end
        if typ~=318 and (scope=='p11' or typ>4096 or
            (profile.exclude_shotguns and (typ>profile.projectile_type_max or profile.excluded_projectile_types[typ]))) then return 'reject' end
        -- Cheap ownership gate first. Foreign slots are rejected before the
        -- flags/weapon/definition reads used by local candidates.
        local source=source_prefilter(slot)
        local owner=u(source)
        if owner~=unit then
            return (owner==0 or owner==0xffffffff) and 'retry' or 'reject'
        end
        local lo,hi=read(system+0x203c+slot*2,2):byte(1,2)
        local expected=lo+hi*256
        if bit.band(expected,2)==0 then return 'retry' end -- constructor not committed
        if bit.band(expected,0x20)==0 then return 'reject' end -- already cleared
        return {hint=hint,slot=slot,expected=expected,typ=typ}
    end
    for i,hint in ipairs(queue) do
        if i>limit.inspect then deferred[#deferred+1]=hint
        else
            stats.inspected=stats.inspected+1
            if hint.tries>0 then stats.retries=stats.retries+1 end
            hint.tries=hint.tries+1
            local ok,result=pcall(discover,hint)
            if not ok then invalid(result,hint)
            elseif result=='retry' then retry(hint)
            elseif type(result)=='table' then
                local list=result.typ==318 and p11_candidates or other_candidates
                list[#list+1]=result
            else terminal(hint) end
        end
    end
    local function process(candidate)
        reset_guards()
        local source=read(system+0x3b040+36*candidate.slot+8,8,true)
        local owner,weapon_id=u(source),u(source,4)
        if owner~=unit then return (owner==0 or owner==0xffffffff) and 'retry' or 'reject' end
        if weapon_id==0 or weapon_id==0xffffffff then return 'retry' end
        -- Native source-entity comparison remains active. Never change IDs;
        -- refuse an ambiguous source equal to the local avatar entity.
        if weapon_id==avatar then
            stats.entity_alias_rejections=(stats.entity_alias_rejections or 0)+1
            stats.last_rejection='source_weapon_entity_matches_avatar'
            return 'reject'
        end
        local result=weapon_allowed(weapon_id,candidate.typ==318)
        if result~='ok' then return result end
        definition_matches(candidate.typ)
        assert(u(read(system+0xe5040+4*candidate.slot,4,true))==candidate.typ,'slot_reused')
        read(system+0x3c+4*candidate.slot,4,true) -- FFFFFFFF is valid; not a generation ID.
        assert(#guards<=300,'guard_budget')
        stats.attempts=stats.attempts+1
        local ok,reason=api.clear_exclusion(system,candidate.slot,candidate.expected,guards)
        if ok then
            changes=changes+1
            if candidate.typ==318 then stats.p11_changes=stats.p11_changes+1
            else stats.other_changes=stats.other_changes+1 end
            return 'done'
        elseif reason=='changed' then stats.rejected_writes=stats.rejected_writes+1;return 'retry'
        else error({fatal=true,reason=reason or 'write_failed'},0) end
    end
    -- Identify the bounded set first, then give all known P-11 candidates their
    -- opportunity before broad scopes consume writes. No per-shot event exists,
    -- so overload may still delay or expire an undiscovered slot.
    for _,list in ipairs({p11_candidates,other_candidates}) do
        for _,candidate in ipairs(list) do
            -- A maximal registry probe needs fewer than 600 reads / 16 KiB.
            -- Reserve that room before beginning another candidate so work is
            -- deferred intact rather than partially authorized at the budget.
            if stats.attempts>=limit.writes or stats.reads>limit.reads-600 or stats.bytes>limit.bytes-16384 then
                retry(candidate.hint);stats.budget_deferred=(stats.budget_deferred or 0)+1
            else
                local ok,result=pcall(process,candidate)
                if not ok then
                    if type(result)=='table' and result.fatal then error(result,0) end
                    invalid(result,candidate.hint)
                elseif result=='retry' then retry(candidate.hint)
                else terminal(candidate.hint) end
            end
        end
    end
    -- Retry candidates join after not-yet-inspected slots: a malformed or busy
    -- early hint cannot permanently starve the remaining bounded queue.
    for _,hint in ipairs(waiting) do deferred[#deferred+1]=hint end
    stats.pending=#deferred
    M.state={system=system,cursor=cursor,unit=unit,avatar=avatar,scope=scope,frame=frame,pending=deferred}
    local status=stats.overrun and 'cursor_overrun' or stats.dropped>0 and 'cursor_backlog'
        or stats.pending>0 and 'pending' or 'ready'
    return changes,status,stats
end
return M
