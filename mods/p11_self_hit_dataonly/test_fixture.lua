-- Synthetic memory only. No game or operating-system calls.
local ffi,bit=require('ffi'),require('bit')
local function scalar(kind,n) return ffi.string(ffi.new(kind..'[1]',n),ffi.sizeof(kind)) end
local function u(n) return scalar('uint32_t',n) end
local function p(n) return scalar('uint64_t',n) end
local function raw(h) return (h:gsub('..',function(x) return string.char(tonumber(x,16)) end)):reverse() end
return function()
    local f={base=0x10000000,pm=0x20000000,em=0x21000000,wm=0x24000000,am=0x25000000,system=0x30000000,
        weapon=0x35000000,ptrs=0x35100000,definition=0x34000000,attach=0x35200000,hits={},writes={},requests=0}
    local mem={}
    f.u,f.p,f.scalar,f.raw=u,p,scalar,raw
    function f.put(at,s) for i=1,#s do mem[at+i-1]=s:sub(i,i) end end
    function f.zero(at,n) f.put(at,string.rep('\0',n)) end
    function f.peek(at,n)
        local out={}; for i=0,n-1 do if not mem[at+i] then return nil end; out[i+1]=mem[at+i] end
        return table.concat(out)
    end
    function f.read(at,n)
        assert(n<=4096); f.hits[at]=(f.hits[at] or 0)+1
        if f.mutate then f.mutate(at,n,f.hits[at]) end
        return f.peek(at,n)
    end
    function f.entity(at,resource,id,unit,net,flags) f.put(at,resource..u(id)..u(unit)..u(net)..u(flags or 1)) end
    function f.map(at,data,entries)
        f.put(at,p(data)..u(8)..u(0xffffffff)..u(1)); f.put(data,string.rep(u(0xffffffff)..u(0xffffffff),8))
        for key,v in pairs(entries) do
            local idx=key%8
            while f.peek(data+idx*8,4)~=u(0xffffffff) do idx=(idx+1)%8 end
            f.put(data+idx*8,u(key)..u(v))
        end
    end
    function f.slot(slot,owner,typ,flags,aux,weapon)
        f.put(f.system+0xe5040+4*slot,u(typ or 318))
        f.put(f.system+0x203c+2*slot,scalar('uint16_t',flags or 0x22))
        f.put(f.system+0x3c+4*slot,u(aux or 0xffffffff))
        f.put(f.system+0x3b040+36*slot+8,u(owner)..u(weapon or 201))
    end
    f.api={base=f.base,read_data=f.read}
    function f.api.clear_exclusion(system,slot,expected,guards)
        f.requests=f.requests+1; f.last_guards=guards
        if f.write_error then return false,f.write_error end
        for _,g in ipairs(guards) do if f.read(g.at,#g.bytes)~=g.bytes then return false,'changed' end end
        local at=system+0x203c+slot*2
        if f.read(at,2)~=scalar('uint16_t',expected) then return false,'changed' end
        local desired=bit.band(expected,0xffdf)
        f.put(at,scalar('uint16_t',desired)); f.writes[#f.writes+1]={at=at,before=expected,after=desired}
        return true
    end
    f.put(f.base+0x3326468,p(f.pm)); f.put(f.base+0x346bf98,p(f.em))
    f.put(f.base+0x33266d8,p(f.wm)); f.put(f.base+0x3326dc0,p(f.am)); f.put(f.base+0x347cea8,p(f.system))
    f.put(f.pm+0x84,u(1)..u(1)); f.put(f.pm+0x3a8,u(5))
    f.map(f.em+0xf22ec8,0x36000000,{[5]=3})
    f.avatar=f.em+0xf32f18+24*3
    f.entity(f.avatar,raw('4d1c334d294dfa97'),101,1001,5,1)
    f.put(f.wm+0x2c,u(8)); f.put(f.wm+0x38,u(1)); f.put(f.wm+0x3c,u(1)); f.put(f.wm+0x68,p(f.ptrs))
    f.put(f.ptrs,p(f.weapon)); f.entity(f.weapon,raw('d6b1fb05b9109353'),201,2001,6,1)
    f.map(f.wm+0x50,0x36200000,{[201]=0}); f.map(f.am+0x20,0x36100000,{[201]=0})
    f.put(f.am+0x40,p(f.attach)); f.zero(f.attach,48); f.put(f.attach+4,u(101))
    f.put(f.base+0x37c7670+318*8,p(f.definition)); f.zero(f.definition,272)
    f.put(f.definition,u(318)); f.put(f.definition+0x80,raw('4431931242cbcd54')); f.put(f.definition+0xfc,'\1')
    f.zero(f.system+0xe5040,8192); f.zero(f.system+0x203c,4096)
    f.slot(7,1001)
    return f
end
