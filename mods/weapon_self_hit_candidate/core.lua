-- Candidate only: local weapon-owned native projectile slots. This is not
-- proof that every weapon uses this subsystem or that a self-hit deals damage.
local ffi,bit=require('ffi'),require('bit')
local M={}
local function raw(h) return (h:gsub('..',function(x) return string.char(tonumber(x,16)) end)):reverse() end
local P11,AVATAR=raw('d6b1fb05b9109353'),raw('4d1c334d294dfa97')
local function value(s,at,kind)
    local v=ffi.new(kind..'[1]'); local n=ffi.sizeof(v)
    assert(type(s)=='string' and #s>=(at or 0)+n,'short_read')
    ffi.copy(v,s:sub((at or 0)+1,(at or 0)+n),n); return tonumber(v[0])
end
local function u(s,at)
    at=at or 0
    local a,b,c,d=s:byte(at+1,at+4)
    assert(d,'short_read'); return a+b*256+c*65536+d*16777216
end
local function short(s,at)
    local a,b=s:byte(at+1,at+2)
    assert(b,'short_read'); return a+b*256
end
function M.tick(api,profile)
    assert(profile and (profile.scope=='pistols' or profile.scope=='native_weapons'),'invalid_scope')
    local allowed={}
    for _,h in ipairs(profile.pistol_unit_hashes or {}) do
        assert(type(h)=='string' and h:match('^[0-9a-f]+$') and #h==16,'invalid_allowlist')
        allowed[raw(h)]=true
    end
    assert(profile.scope~='pistols' or next(allowed)~=nil,'empty_allowlist')
    local reads,bytes,changes,attempts=0,0,0,0
    local guards={}
    local function read(at,n,guard)
        reads,bytes=reads+1,bytes+n
        assert(reads<=12000 and bytes<=262144 and n<=4096,'read_budget')
        local s=assert(api.read_data(at,n),'data_unavailable')
        assert(#s==n,'short_read')
        if guard then guards[#guards+1]={at=at,bytes=s} end
        return s
    end
    local function pointer(at)
        local p=value(read(at,8,true),0,'uint64_t')
        assert(p>=65536 and p<0x800000000000 and p%1==0,'invalid_pointer'); return p
    end
    local function map(at,key,max)
        local h=read(at,20,true); local cap,empty,mult=u(h,8),u(h,12),u(h,16)
        assert(cap<=max and (cap==0 or bit.band(cap,cap-1)==0),'map_bounds')
        if cap==0 or key==empty then return nil end
        local p=value(h,0,'uint64_t'); assert(p>=65536 and p<0x800000000000,'map_pointer')
        local product=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',key)*ffi.new('uint64_t',mult)))
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
    local pm=pointer(base+0x3326468)
    local counts=read(pm+0x84,8,true)
    assert(u(counts)<=4 and u(counts,4)<=4,'player_bounds')
    if u(counts)==0 or u(counts,4)==0 then return 0,'waiting_player' end
    local net=u(read(pm+0x3a8,4,true)); local em=pointer(base+0x346bf98)
    local index=map(em+0xf22ec8,net,1048576)
    if not index then return 0,'waiting_player' end
    assert(index<262144,'avatar_bounds')
    local avatar,unit=entity(em+0xf32f18+24*index,AVATAR,nil,net)
    assert(avatar~=0xffffffff and unit~=0 and unit~=0xffffffff,'avatar_identity')
    local system=pointer(base+0x347cea8)
    local flags=read(system+0x203c,4096)
    -- Flags are only eligibility hints, not ownership. Read type pages lazily
    -- after finding an occupied slot with source exclusion still enabled.
    local types={}
    local function slot_type(slot)
        local page=math.floor(slot/1024)
        if not types[page] then types[page]=read(system+0xe5040+page*4096,4096) end
        return u(types[page],(slot%1024)*4)
    end
    local common=#guards
    -- These snapshots exist only for this tick. Reuse discovery work, never
    -- authorization: every accepted slot still supplies all original pointer,
    -- registry, weapon and owner guards to the writer for fresh readback.
    local weapons,definitions={},{}
    local function cached(cache,key,inspect)
        local saved=cache[key]
        if saved then
            if saved.accepted then
                for _,g in ipairs(saved.guards) do guards[#guards+1]=g end
            end
            return saved.accepted
        end
        local first=#guards+1
        local accepted=inspect()
        local dependencies={}
        if accepted then
            for i=first,#guards do dependencies[#dependencies+1]=guards[i] end
        end
        cache[key]={accepted=accepted,guards=dependencies}
        return accepted
    end
    local function weapon_allowed(weapon_id)
        return cached(weapons,weapon_id,function()
            local wm=pointer(base+0x33266d8)
            local wi=map(wm+0x50,weapon_id,8192)
            if not wi then return false end
            local cap=u(read(wm+0x2c,4,true))
            local counts=read(wm+0x38,8,true)
            local count,committed=u(counts),u(counts,4)
            assert(count<=cap and cap<=4096 and committed<=count and wi<committed,'weapon_bounds')
            local weapon=pointer(pointer(wm+0x68)+wi*8)
            local identity=read(weapon,24,true)
            local resource=identity:sub(1,8)
            assert(u(identity,8)==weapon_id and bit.band(u(identity,20),3)==1,'weapon_identity')
            -- Reject unrelated weapons before attachment or definition lookup.
            if resource==P11 or (profile.scope=='pistols' and not allowed[resource]) then return false end
            local am=pointer(base+0x3326dc0)
            local ai=map(am+0x20,weapon_id,32768)
            if not ai then return false end
            assert(ai<16384,'weapon_bounds')
            return u(read(pointer(am+0x40)+48*ai+4,4,true))==avatar
        end)
    end
    local function definition_matches(typ)
        return cached(definitions,typ,function()
            return u(read(pointer(base+0x37c7670+typ*8),4,true))==typ
        end)
    end
    for slot=0,2047 do
        local expected=short(flags,slot*2)
        if bit.band(expected,0x22)==0x22 then
          local typ=slot_type(slot)
          if typ>0 and typ<=4096 and typ~=318 then
            -- Never retain an address/identity from the previous Lua update.
            for i=#guards,common+1,-1 do guards[i]=nil end
            local source=read(system+0x3b040+36*slot+8,8,true)
            if u(source)==unit then
                local weapon_id=u(source,4)
                if weapon_allowed(weapon_id) and definition_matches(typ) then
                    assert(u(read(system+0xe5040+4*slot,4,true))==typ,'slot_reused')
                    read(system+0x3c+4*slot,4,true) -- FFFFFFFF is valid; not a generation ID.
                    assert(#guards<=300,'guard_budget')
                    attempts=attempts+1; assert(attempts<=64,'candidate_budget')
                    local ok,reason=api.clear_exclusion(system,slot,expected,guards)
                    if ok then changes=changes+1
                    elseif reason~='changed' then error({fatal=true,reason=reason or 'write_failed'},0) end
                end
            end
          end
        end
    end
    return changes,'ready'
end
return M
