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
            local chunks={}; local finish=at+n
            while at<finish do
                local last=page(at,false); if not last then return nil end
                local size=math.min(finish-at,last-at,4096-at%4096)
                got[0]=0
                if not same() or kernel.ReadProcessMemory(process,ptr(at),buffer,size,got)==0 or tonumber(got[0])~=size then return nil end
                chunks[#chunks+1]=ffi.string(buffer,size); at=at+size
            end
            if not same() then return nil end
            return table.concat(chunks)
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
