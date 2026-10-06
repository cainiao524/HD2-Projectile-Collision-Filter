-- HD2-Addon: mods/pcf/bsl_four_scope_self_hit
local Core=(function()
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

end)()
local Version=(function()
-- Version checks only. The executable bytes below are read, never patched.
local V = {}
local RESEARCH_ANCHORS={
    {name='source_weapon_object_entity',rva=6382949,bytes_hex='8b4008'},
    {name='source_weapon_entity_store',rva=20620526,bytes_hex='8984964cb00300'},
    {name='first_source_entity_compare',rva=20629135,bytes_hex='433b9c874cb00300'},
    {name='first_source_entity_skip',rva=20629143,bytes_hex='0f84c1070000'},
    {name='accepted_hit_effect_flag',rva=20633688,bytes_hex='f680fc00000001'},
    {name='accepted_hit_stim_dispatch_flag',rva=20633866,bytes_hex='f680fc00000001'},
    {name='accepted_hit_effect_call_a',rva=20634039,bytes_hex='e8b4c3e1ff'},
    {name='accepted_hit_effect_call_b',rva=20634170,bytes_hex='e831c4e1ff'}
}
local function get(s, at, n)
    assert(type(s)=='string' and #s>=at+n, 'Short version read')
    local value=0; for i=n,1,-1 do value=value*256+s:byte(at+i) end
    return value
end
function V.files(api, p)
    assert(p.schema_version==1 and p.build_id==25480438, 'Unknown addon profile')
    assert((p.scope=='p11' or p.scope=='pistols' or p.scope=='native_no_shotguns' or p.scope=='native_weapons')
        and p.version=='0.3.2-bsl-four' and p.resource=='mods/pcf/bsl_four_scope_self_hit'
        and p.manager_guid=='f344360d-eb4a-4baa-b631-8e6982ecd9fb', 'Unknown BSL four-scope profile')
    local h=api.file_hashes()
    assert(h.game_sha256==p.game_sha256 and h.exe_sha256==p.exe_sha256, 'Unsupported game files')
end
function V.runtime(api,p)
    local b=assert(api.read(0,4096), 'Loaded image unreadable')
    local pe=p.pe_offset; local opt=pe+24
    assert(b:sub(1,2)=='MZ' and get(b,0x3c,4)==pe and b:sub(pe+1,pe+4)=='PE\0\0', 'Unexpected image header')
    assert(get(b,pe+4,2)==0x8664 and get(b,opt,2)==0x20b and get(b,opt+32,4)==4096, 'Unsupported image architecture')
    assert(get(b,pe+8,4)==p.timestamp and get(b,opt+56,4)==p.image_size, 'Unsupported loaded build')
    assert(get(b,pe+6,2)==p.section_count and get(b,pe+20,2)==p.optional_size and #p.sections==p.section_count, 'Unsupported sections')
    -- Raw sizes/offsets describe file layout, already pinned by both hashes.
    -- Validate the original virtual sections covering every used RVA/anchor.
    -- Additional packer sections are not used to locate gameplay data.
    assert(type(p.loaded_section_indices)=='table' and #p.loaded_section_indices==4,'Missing virtual-section policy')
    for order,i in ipairs(p.loaded_section_indices) do
        assert(i==order,'Unexpected virtual-section policy')
        local s=p.sections[i]
        local at=opt+p.optional_size+(i-1)*40
        for _,field in ipairs({{8,'virtual_size'},{12,'rva'},{36,'characteristics'}}) do
            local actual,expected=get(b,at+field[1],4),s[field[2]]
            assert(actual==expected,string.format('Loaded section %d %s differs: expected=%08X actual=%08X',i,field[2],expected,actual))
        end
    end
    V.anchors(api,p)
end
function V.check(api,p) V.files(api,p); V.runtime(api,p) end
function V.anchors(api,p)
    assert(#p.code_anchors==12, 'Missing code anchors')
    for _,a in ipairs(p.code_anchors) do
        local bytes=a.bytes_hex:gsub('..',function(x) return string.char(tonumber(x,16)) end)
        assert(api.read(a.rva,#bytes)==bytes, 'Code anchor differs: '..a.name)
    end
    assert(type(p.cursor_anchors)=='table' and #p.cursor_anchors==3,'Missing cursor anchors')
    for _,a in ipairs(p.cursor_anchors) do
        local bytes=a.bytes_hex:gsub('..',function(x) return string.char(tonumber(x,16)) end)
        assert(api.read(a.rva,#bytes)==bytes, 'Cursor anchor differs: '..a.name)
    end
    assert(type(p.research_anchors)=='table' and #p.research_anchors==8,'Missing research anchors')
    for i,expected in ipairs(RESEARCH_ANCHORS) do
        local a=p.research_anchors[i]
        assert(type(a)=='table' and a.name==expected.name and a.rva==expected.rva
            and a.bytes_hex==expected.bytes_hex,'Research anchor policy differs')
        local bytes=expected.bytes_hex:gsub('..',function(x) return string.char(tonumber(x,16)) end)
        assert(api.read(expected.rva,#bytes)==bytes,'Research anchor differs: '..expected.name)
    end
end
return V

end)()
local MakeImage=(function()
-- Read-only image/hash adapter reused for version checks; no capture output.
-- read() skip reasons: 1 bounds/closed, 2 module changed, 3 region query/layout,
--                     4 page identity/protection, 5 failed/short memory read.
-- Native handles used for hashing are opened and closed within file_hashes().
-- This module does not call native game functions or write to process memory.
return function(profile)
    local ffi = require('ffi')
    assert(ffi.os == 'Windows' and ffi.arch == 'x64' and ffi.abi('64bit'),
           'Windows x64 LuaJIT required')
    local image_size = type(profile) == 'table' and profile.image_size
    assert(type(image_size) == 'number' and image_size == math.floor(image_size)
           and image_size > 0 and image_size <= 0x7fffffff, 'Invalid image size')

    -- Use one uniquely named layout and reuse any compatible declarations already
    -- installed by the shared loader. All imported functions have the Windows ABI.
    if not pcall(ffi.typeof, 'P11ReadOnlyCaptureRegionV1') then
        ffi.cdef [[
            typedef struct {
                void *base; void *allocation_base; uint32_t allocation_protection;
                uint16_t partition; uint16_t reserved; size_t size;
                uint32_t state; uint32_t protection; uint32_t type;
            } P11ReadOnlyCaptureRegionV1;
        ]]
    end
    assert(ffi.sizeof('P11ReadOnlyCaptureRegionV1') == 48
           and ffi.offsetof('P11ReadOnlyCaptureRegionV1', 'size') == 24,
           'Unexpected Windows memory region layout')
    local kernel, bcrypt = ffi.load('kernel32'), ffi.load('bcrypt')
    local function declare(library, name, signature)
        if not pcall(function() return library[name] end) then ffi.cdef(signature) end
    end
    declare(kernel, 'GetModuleHandleA', 'void *GetModuleHandleA(const char *);')
    declare(kernel, 'GetModuleFileNameW', 'uint32_t GetModuleFileNameW(void *, uint16_t *, uint32_t);')
    declare(kernel, 'GetCurrentProcess', 'void *GetCurrentProcess(void);')
    declare(kernel, 'VirtualQuery', 'size_t VirtualQuery(const void *, void *, size_t);')
    declare(kernel, 'ReadProcessMemory', 'int ReadProcessMemory(void *, const void *, void *, size_t, size_t *);')
    declare(kernel, 'CreateFileW', 'void *CreateFileW(const uint16_t *, uint32_t, uint32_t, void *, uint32_t, uint32_t, void *);')
    declare(kernel, 'GetFileSizeEx', 'int GetFileSizeEx(void *, int64_t *);')
    declare(kernel, 'ReadFile', 'int ReadFile(void *, void *, uint32_t, uint32_t *, void *);')
    declare(kernel, 'CloseHandle', 'int CloseHandle(void *);')
    declare(bcrypt, 'BCryptOpenAlgorithmProvider', 'int32_t BCryptOpenAlgorithmProvider(void **, const uint16_t *, const uint16_t *, uint32_t);')
    declare(bcrypt, 'BCryptCloseAlgorithmProvider', 'int32_t BCryptCloseAlgorithmProvider(void *, uint32_t);')
    declare(bcrypt, 'BCryptCreateHash', 'int32_t BCryptCreateHash(void *, void **, void *, uint32_t, const void *, uint32_t, uint32_t);')
    declare(bcrypt, 'BCryptHashData', 'int32_t BCryptHashData(void *, const void *, uint32_t, uint32_t);')
    declare(bcrypt, 'BCryptFinishHash', 'int32_t BCryptFinishHash(void *, void *, uint32_t, uint32_t);')
    declare(bcrypt, 'BCryptDestroyHash', 'int32_t BCryptDestroyHash(void *);')

    local module = kernel.GetModuleHandleA('game.dll')
    assert(module ~= nil, 'game.dll is not loaded')
    local base = tonumber(ffi.cast('uintptr_t', module))
    assert(base >= 0x10000 and base + image_size < 0x800000000000,
           'Unexpected module address')
    local closed = false
    local process = kernel.GetCurrentProcess() -- A pseudo handle, never opened/closed.
    local region = ffi.new('P11ReadOnlyCaptureRegionV1[1]')
    local buffer, count = ffi.new('uint8_t[4096]'), ffi.new('size_t[1]')
    local readable = {[2]=true, [4]=true, [8]=true, [32]=true, [64]=true, [128]=true}
    local api = {base_low=base % 4294967296, base_high=math.floor(base / 4294967296)}
    local function same_module()
        return not closed and kernel.GetModuleHandleA('game.dll') == module
    end
    local function pointer(address) return ffi.cast('void *', address) end

    function api.read(rva, size)
        if closed or type(rva) ~= 'number' or rva ~= math.floor(rva) or rva < 0
           or type(size) ~= 'number' or size ~= math.floor(size) or size < 1 or size > 4096
           or rva > image_size - size then return nil, 1 end
        if not same_module() then return nil, 2 end
        local pieces, cursor, ending = {}, base + rva, base + rva + size
        while cursor < ending do
            if not same_module() then return nil, 2 end
            if tonumber(kernel.VirtualQuery(pointer(cursor), region, 48)) ~= 48 then
                return nil, 3
            end
            local r = region[0]
            local first = tonumber(ffi.cast('uintptr_t', r.base))
            local owner = tonumber(ffi.cast('uintptr_t', r.allocation_base))
            local span = tonumber(r.size)
            local last, protection = first + span, tonumber(r.protection)
            if first < 0x10000 or first > cursor or span <= 0
               or last <= cursor or last > 0x800000000000 then return nil, 3 end
            if tonumber(r.state) ~= 0x1000 or tonumber(r.type) ~= 0x1000000 or owner ~= base
               or math.floor(protection / 256) % 2 ~= 0
               or not readable[protection % 256] then return nil, 4 end
            local amount = math.min(ending - cursor, last - cursor, 4096 - cursor % 4096)
            count[0] = 0
            if not same_module() then return nil, 2 end
            if kernel.ReadProcessMemory(process, pointer(cursor), buffer, amount, count) == 0
               or tonumber(count[0]) ~= amount then return nil, 5 end
            pieces[#pieces + 1] = ffi.string(buffer, amount)
            cursor = cursor + amount
        end
        if not same_module() then return nil, 2 end
        return table.concat(pieces)
    end

    local function file_hash(target_module, label)
        local file, algorithm, hash
        local invalid = ffi.cast('void *', -1)
        local ok, result = pcall(function()
            local path = ffi.new('uint16_t[32768]')
            local length = tonumber(kernel.GetModuleFileNameW(target_module, path, 32768))
            assert(length > 0 and length < 32768, 'Cannot resolve ' .. label .. ' file')
            -- GENERIC_READ, FILE_SHARE_READ, OPEN_EXISTING, SEQUENTIAL_SCAN.
            -- Denying write/delete sharing prevents concurrent replacement while
            -- this handle is hashing. No path is included in the capture output.
            file = kernel.CreateFileW(path, 0x80000000, 1, nil, 3, 0x08000000, nil)
            assert(file ~= nil and file ~= invalid, 'Cannot open ' .. label .. ' read-only')
            local length64 = ffi.new('int64_t[1]')
            assert(kernel.GetFileSizeEx(file, length64) ~= 0, 'Cannot size ' .. label)
            local file_size = tonumber(length64[0])
            assert(file_size > 0 and file_size <= 67108864, label .. ' exceeds file size bounds')
            algorithm, hash = ffi.new('void *[1]'), ffi.new('void *[1]')
            local name = ffi.new('uint16_t[7]', {83,72,65,50,53,54,0})
            assert(bcrypt.BCryptOpenAlgorithmProvider(algorithm, name, nil, 0) == 0,
                   'SHA256 unavailable')
            assert(bcrypt.BCryptCreateHash(algorithm[0], hash, nil, 0, nil, 0, 0) == 0,
                   'SHA256 creation failed')
            local block, got = ffi.new('uint8_t[1048576]'), ffi.new('uint32_t[1]')
            local total = 0
            while total < file_size do
                local amount = math.min(1048576, file_size - total)
                got[0] = 0
                assert(kernel.ReadFile(file, block, amount, got, nil) ~= 0,
                       label .. ' file read failed')
                assert(tonumber(got[0]) == amount, label .. ' file read was shortened')
                assert(bcrypt.BCryptHashData(hash[0], block, amount, 0) == 0,
                       'SHA256 update failed')
                total = total + amount
            end
            assert(kernel.GetFileSizeEx(file, length64) ~= 0 and tonumber(length64[0]) == file_size,
                   label .. ' changed during hashing')
            local digest, hex = ffi.new('uint8_t[32]'), {}
            assert(bcrypt.BCryptFinishHash(hash[0], digest, 32, 0) == 0, 'SHA256 finish failed')
            for i = 0, 31 do hex[#hex + 1] = string.format('%02x', tonumber(digest[i])) end
            return table.concat(hex)
        end)
        -- Always attempt every applicable release, even if an earlier release
        -- reports an error. Never retain handles between game update frames.
        local cleanup_ok = true
        local function release(fn)
            local released, status = pcall(fn)
            if not released or not status then cleanup_ok = false end
        end
        if hash and hash[0] ~= nil then
            release(function() return bcrypt.BCryptDestroyHash(hash[0]) == 0 end)
        end
        if algorithm and algorithm[0] ~= nil then
            release(function() return bcrypt.BCryptCloseAlgorithmProvider(algorithm[0], 0) == 0 end)
        end
        if file ~= nil and file ~= invalid then
            release(function() return kernel.CloseHandle(file) ~= 0 end)
        end
        if not ok then error(result, 0) end
        assert(cleanup_ok, 'Hashing resource cleanup failed')
        return result
    end

    function api.file_hashes()
        assert(same_module(), 'Version adapter closed or game.dll changed')
        local game_hash = file_hash(module, 'game.dll')
        assert(same_module(), 'game.dll changed during hashing')
        local exe_hash = file_hash(nil, 'host EXE')
        assert(same_module(), 'game.dll changed during hashing')
        return {game_sha256=game_hash, exe_sha256=exe_hash}
    end
    function api.close() closed = true end
    return api
end

end)()
local MakeData=(function()
-- Narrow Windows adapter. Only clear_exclusion can write, only two bytes in
-- the current native projectile flag array, and only on non-executable heap pages.
return function(profile,MakeImage)
    local ffi,bit=require('ffi'),require('bit')
    local api=MakeImage(profile)
    local original_close=api.close; local closed=false
    local function close() if not closed then closed=true; original_close() end end
    local ok,result=pcall(function()
        local kernel=ffi.load('kernel32')
        if not pcall(function() return kernel.WriteProcessMemory end) then
            ffi.cdef('int WriteProcessMemory(void *, void *, const void *, size_t, size_t *);')
        end
        local function ptr(n) return ffi.cast('void *',n) end
        local function address(p) return tonumber(ffi.cast('uintptr_t',p)) end
        local base=api.base_low+api.base_high*4294967296
        local module=kernel.GetModuleHandleA('game.dll')
        assert(module~=nil and address(module)==base,'Module changed')
        local process=kernel.GetCurrentProcess()
        assert(process~=nil,'Current process unavailable')
        -- MakeImage has declared and validated this Windows x64 layout.
        local region=ffi.new('P11ReadOnlyCaptureRegionV1[1]')
        local buffer,got=ffi.new('uint8_t[4096]'),ffi.new('size_t[1]')
        local desired=ffi.new('uint16_t[1]')
        local function integer(n,lo,hi) return type(n)=='number' and n==math.floor(n) and n>=lo and n<=hi end
        local function same() return not closed and kernel.GetModuleHandleA('game.dll')==module end
        local function page(at,writing)
            if not same() or tonumber(kernel.VirtualQuery(ptr(at),region,48))~=48 then return nil end
            local r=region[0]; local first,owner=address(r.base),address(r.allocation_base)
            local last=first+tonumber(r.size); local prot,kind=tonumber(r.protection),tonumber(r.type)
            if not integer(first,65536,at) or not integer(last,at+1,0x800000000000)
                or not integer(owner,65536,first) or tonumber(r.state)~=0x1000 then return nil end
            if writing then
                if kind~=0x20000 or prot~=4 then return nil end
            else
                if prot~=2 and prot~=4 and prot~=8 then return nil end
                if kind==0x1000000 then
                    if owner~=base or first<base or last>base+profile.image_size then return nil end
                elseif kind~=0x20000 then return nil end
            end
            return last
        end
        function api.read_data(at,n)
            if not integer(at,65536,0x800000000000-1) or not integer(n,1,4096)
                or at+n>0x800000000000 or not same() then return nil end
            local first,chunks; local finish=at+n
            while at<finish do
                local last=page(at,false); if not last then return nil end
                local size=math.min(finish-at,last-at,4096-at%4096)
                got[0]=0
                if not same() or kernel.ReadProcessMemory(process,ptr(at),buffer,size,got)==0 or tonumber(got[0])~=size then return nil end
                local part=ffi.string(buffer,size)
                if not first then first=part
                elseif chunks then chunks[#chunks+1]=part
                else chunks={first,part} end
                at=at+size
            end
            if not same() then return nil end
            return chunks and table.concat(chunks) or first
        end
        function api.clear_exclusion(system,slot,expected,guards)
            if not integer(system,65536,0x800000000000-0xf0000) or system%8~=0
                or not integer(slot,0,2047) or not integer(expected,0,65535)
                or bit.band(expected,0x22)~=0x22 or type(guards)~='table' or #guards<1 or #guards>300 then
                return false,'invalid_write_request'
            end
            local at=system+0x203c+slot*2
            local last=page(at,true)
            if not last or at+2>last then return false,'write_page_rejected' end
            -- Recheck each pointer/owner dependency immediately before the write.
            for _,g in ipairs(guards) do
                if type(g.bytes)~='string' or #g.bytes>4096 or api.read_data(g.at,#g.bytes)~=g.bytes then return false,'changed' end
            end
            local p=api.read_data(base+0x347cea8,8)
            if not p then return false,'changed' end
            local system_now=ffi.new('uint64_t[1]'); ffi.copy(system_now,p,8)
            if tonumber(system_now[0])~=system then return false,'changed' end
            local before=string.char(expected%256,math.floor(expected/256)) -- short-lived original value
            if api.read_data(at,2)~=before then return false,'changed' end
            last=page(at,true)
            if not last or at+2>last or not same() then return false,'write_page_rejected' end
            desired[0]=bit.band(expected,0xffdf) -- The only gameplay data change.
            got[0]=0
            if kernel.WriteProcessMemory(process,ptr(at),desired,2,got)==0 or tonumber(got[0])~=2 then return false,'write_failed' end
            if api.read_data(at,2)~=ffi.string(desired,2) then return false,'write_readback_failed' end
            -- No rollback through a cached address: native lifecycle owns this dart.
            return true
        end
        api.base,api.close=base,close
        return api
    end)
    if not ok then pcall(close); error(result,0) end
    return result
end

end)()
local Entry=(function()
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

end)()
return Entry(Core,Version,MakeImage,MakeData,{["all_secondary_mechanisms_supported"]=false,["build_id"]=25480438,["code_anchors"]={{["bytes_hex"]="4885db0f843a090000",["name"]="gun_private_projectile_route",["rva"]=6380479},{["bytes_hex"]="c6453801",["name"]="gun_fixed_exclude_owner_option",["rva"]=6383042},{["bytes_hex"]="e81932d900",["name"]="gun_native_constructor_call",["rva"]=6383122},{["bytes_hex"]="8b0842898ca640500e00740c41385d187506440fb7c3eb0641b820000000",["name"]="constructor_option_flag",["rva"]=20618163},{["bytes_hex"]="498b46100f57c041b9000600000fb788f00000000fb7c10fb7d16683e0106683e22066c1e202660bd00fb7c16683e00c6603d2660bd00fb7c1664123c166c1e203660bd00fb7c16683e0026603d2660bd00fb7c166d1e86683ca016683e020664123cf4c6bff70660bc16603d266c1e802660bd066410bd066428994663c200000",["name"]="constructor_flag_composition",["rva"]=20618193},{["bytes_hex"]="433b9c874cb003000f84c1070000488b45a8",["name"]="collision_source_entity_gate",["rva"]=20629135},{["bytes_hex"]="41f684473c200000200f84e30000008b559485d20f84d8000000488b05469cf701488b4818488b81200700008bcaffd084c00f84ba000000428b8c25dc060000",["name"]="collision_source_unit_gate",["rva"]=20629153},{["bytes_hex"]="f680fc00000001",["name"]="stim_effect_definition_flag",["rva"]=20633866},{["bytes_hex"]="6641218c473c20000041",["name"]="reflection_owner_flag_clear",["rva"]=20637466},{["bytes_hex"]="e8cf35d600",["name"]="component196_native_constructor",["rva"]=6578780},{["bytes_hex"]="42c744a63cffffffff418bfc41399c378c3000000f8445010000498b4610",["name"]="optional_auxiliary_initial_sentinel",["rva"]=20619735},{["bytes_hex"]="3998900000000f8435010000418b4e18e836fbc2",["name"]="optional_auxiliary_definition_gate",["rva"]=20619765}},["cursor_anchors"]={{["bytes_hex"]="8b4130",["name"]="native_cursor_read",["rva"]=20617322},{["bytes_hex"]="4181e4ff070000",["name"]="native_cursor_slot_mask",["rva"]=20617371},{["bytes_hex"]="895130",["name"]="native_cursor_write",["rva"]=20617460}},["distinct_weapon_avatar_required"]=true,["exclude_shotguns"]=false,["excluded_projectile_types"]={},["exe_sha256"]="f5fee03dcfdb2e553a4752c283590950ac13316b376d8196aa556ff0400d5f06",["game_sha256"]="2e2c3b7c2500646dadd5f2b4c6e0504dbb7e7896139f64cddc0d1813c718f51e",["gameplay_verified"]=false,["generation_identity_verified"]=false,["id"]="pcf-bsl-four-25480438-native_weapons",["image_size"]=74727424,["loaded_section_indices"]={1,2,3,4},["loader"]={["api"]=1,["internal_max"]=17,["internal_min"]=16,["public_release_recommended"]="v18"},["manager_guid"]="f344360d-eb4a-4baa-b631-8e6982ecd9fb",["native_hook"]=false,["native_patch"]=false,["optional_size"]=240,["p11_runtime_version"]="0.3.2-bsl-four",["pe_offset"]=272,["per_projectile_processing"]=true,["performance_gameplay_verified"]=false,["performance_policy"]="bounded cursor/type-prefilter processing; hard per-update budget; no zero-overhead guarantee",["persistent_weapon_override"]=false,["pistol_mapping_source"]="Offline mod archive index, 2026-09-01; not current-build gameplay proof",["pistol_unit_hashes"]={"05e4e5c2db6e44a2","8d3d52a3b2f19402","3575aabc5f1f9326","c780bcd79547da0f","cf8934ff6567a42d","1a437158e1b8d2a1","dbb6c961c59fadc1","4d58c77087b774c5"},["pre_collision_timing_verified"]=false,["projectile_filter_source_sha256"]="50af7cccf03697a0ef96b7f9ddeb19279adc3b887bd95e0f972996844b7221ea",["projectile_type_max"]=350,["release_version"]="0.3.2-bsl-four",["research_anchors"]={{["bytes_hex"]="8b4008",["name"]="source_weapon_object_entity",["rva"]=6382949},{["bytes_hex"]="8984964cb00300",["name"]="source_weapon_entity_store",["rva"]=20620526},{["bytes_hex"]="433b9c874cb00300",["name"]="first_source_entity_compare",["rva"]=20629135},{["bytes_hex"]="0f84c1070000",["name"]="first_source_entity_skip",["rva"]=20629143},{["bytes_hex"]="f680fc00000001",["name"]="accepted_hit_effect_flag",["rva"]=20633688},{["bytes_hex"]="f680fc00000001",["name"]="accepted_hit_stim_dispatch_flag",["rva"]=20633866},{["bytes_hex"]="e8b4c3e1ff",["name"]="accepted_hit_effect_call_a",["rva"]=20634039},{["bytes_hex"]="e831c4e1ff",["name"]="accepted_hit_effect_call_b",["rva"]=20634170}},["resource"]="mods/pcf/bsl_four_scope_self_hit",["runtime_tested"]=false,["schema_version"]=1,["scope"]="native_weapons",["section_count"]=16,["sections"]={{["characteristics"]=1610612768,["raw_offset"]=1536,["raw_size"]=8718336,["rva"]=4096,["virtual_size"]=34667155},{["characteristics"]=1073741888,["raw_offset"]=8719872,["raw_size"]=825856,["rva"]=34672640,["virtual_size"]=5417484},{["characteristics"]=3221225536,["raw_offset"]=9545728,["raw_size"]=138240,["rva"]=40091648,["virtual_size"]=18462204},{["characteristics"]=1073741888,["raw_offset"]=9683968,["raw_size"]=550912,["rva"]=58556416,["virtual_size"]=1832304},{["characteristics"]=1073741888,["raw_offset"]=10234880,["raw_size"]=2048,["rva"]=60391424,["virtual_size"]=8968},{["characteristics"]=1073741888,["raw_offset"]=10236928,["raw_size"]=512,["rva"]=60403712,["virtual_size"]=1160},{["characteristics"]=1073741888,["raw_offset"]=10237440,["raw_size"]=10752,["rva"]=60407808,["virtual_size"]=222660},{["characteristics"]=1073741888,["raw_offset"]=10248192,["raw_size"]=1536,["rva"]=60633088,["virtual_size"]=4096},{["characteristics"]=1073741888,["raw_offset"]=10249728,["raw_size"]=512,["rva"]=60637184,["virtual_size"]=4096},{["characteristics"]=3221225536,["raw_offset"]=10250240,["raw_size"]=81920,["rva"]=60641280,["virtual_size"]=81920},{["characteristics"]=3221225536,["raw_offset"]=10332160,["raw_size"]=512,["rva"]=60723200,["virtual_size"]=4096},{["characteristics"]=3221225472,["raw_offset"]=10332672,["raw_size"]=4608,["rva"]=60727296,["virtual_size"]=8192},{["characteristics"]=1073741888,["raw_offset"]=10337280,["raw_size"]=1536,["rva"]=60735488,["virtual_size"]=4096},{["characteristics"]=3758096480,["raw_offset"]=10338816,["raw_size"]=0,["rva"]=60739584,["virtual_size"]=8806400},{["characteristics"]=1610612832,["raw_offset"]=10338816,["raw_size"]=4773888,["rva"]=69545984,["virtual_size"]=4773888},{["characteristics"]=1073741824,["raw_offset"]=15112704,["raw_size"]=399376,["rva"]=74321920,["virtual_size"]=405504}},["self_damage_verified"]=false,["startup_retry_updates"]=120,["startup_timeout_updates"]=600,["timestamp"]=1790161983,["unified_cursor_handler"]=true,["update_hook"]=true,["version"]="0.3.2-bsl-four"},_G)
