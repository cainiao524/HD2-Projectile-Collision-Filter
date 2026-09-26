-- Real FFI buffers with mocked Windows functions; no native process access.
local ffi=require('ffi'); local checks=0
local function check(ok,why) checks=checks+1; assert(ok,why) end
if not pcall(ffi.typeof,'P11ReadOnlyCaptureRegionV1') then ffi.cdef[[
typedef struct {void *base; void *allocation_base; uint32_t allocation_protection;
uint16_t partition; uint16_t reserved; size_t size; uint32_t state; uint32_t protection; uint32_t type;} P11ReadOnlyCaptureRegionV1;
]] end
local function ptr(n) return ffi.cast('void *',n) end
local function address(p) return tonumber(ffi.cast('uintptr_t',p)) end
local parent=getfenv(MakeData)
local function setup()
    local f=Fixture(); f.closed=0; f.native_writes=0; f.protection=4; f.module=f.base
    local kernel={}
    function kernel.GetModuleHandleA(name) assert(name=='game.dll'); return ptr(f.module) end
    function kernel.GetCurrentProcess() return ptr(-1) end
    function kernel.VirtualQuery(at,out,n)
        check(n==48,'region layout'); local a=address(at); local first=math.floor(a/4096)*4096
        local r=out[0]; r.base=ptr(first); r.allocation_base=ptr(a>=0x20000000 and 0x20000000 or f.base)
        r.size=f.region_size or 4096; r.state=f.memory_state or 0x1000
        r.protection=f.protection; r.type=f.memory_kind or (a>=0x20000000 and 0x20000 or 0x1000000)
        return f.query_fail and 0 or 48
    end
    function kernel.ReadProcessMemory(process,at,out,n,count)
        check(process==ptr(-1),'current process only'); check(n<=4096 and address(at)%4096+n<=4096,'bounded page read')
        local s=f.read(address(at),n)
        if not s or f.read_fail then count[0]=0; return 0 end
        local actual=f.short_read and n-1 or n
        ffi.copy(out,s,actual); count[0]=actual; return 1
    end
    function kernel.WriteProcessMemory(process,at,source,n,count)
        check(process==ptr(-1) and n==2,'two-byte current-process write only')
        check(address(at)==f.system+0x203c+14,'only expected slot flag touched')
        f.native_writes=f.native_writes+1
        if f.write_fail then count[0]=0; return 0 end
        local actual=f.short_write and 1 or n
        f.put(address(at),ffi.string(source,actual)); count[0]=actual
        if f.bad_readback then f.put(address(at),'\0\0') end
        return 1
    end
    local mock=setmetatable({load=function(name) assert(name=='kernel32'); return kernel end},{__index=ffi})
    setfenv(MakeData,setmetatable({require=function(name) if name=='ffi' then return mock end; return require(name) end},{__index=parent}))
    local api=MakeData({image_size=0x5000000},function()
        return {base_low=f.base,base_high=0,close=function() f.closed=f.closed+1 end}
    end)
    f.realapi=api
    function f.write()
        return api.clear_exclusion(f.system,7,0x22,{{at=f.system+0x3b040+36*7+8,bytes=f.u(1001)..f.u(201)}})
    end
    return f
end
do
    local f=setup(); local ok=f.write(); check(ok and f.native_writes==1,'valid owned-data write')
    check(f.peek(f.system+0x203c+14,2)=='\2\0','clear only source-exclusion')
    local n=f.native_writes; check(not f.write() and f.native_writes==n,'expected original required')
    f.realapi.close(); f.realapi.close(); check(f.closed==1,'idempotent close')
    check(not f.write() and f.native_writes==n,'no write after shutdown')
end
for _,p in ipairs({2,8,0x20,0x40,0x80,0x104}) do
    local f=setup(); f.protection=p; check(not f.write() and f.native_writes==0,'reject non-RW or executable page')
end
for _,m in ipairs({{memory_kind=0x1000000},{memory_kind=0x40000},{memory_state=0x2000},
    {query_fail=true},{read_fail=true},{short_read=true},{module=0x11000000}}) do
    local f=setup(); for k,v in pairs(m) do f[k]=v end
    check(not f.write() and f.native_writes==0,'reject changed or unavailable mapping')
end
do
    local f=setup(); f.put(f.system+0x3b040+36*7+8,f.u(9999))
    local ok,reason=f.write(); check(not ok and reason=='changed' and f.native_writes==0,'owner change rejected')
    f=setup(); f.put(f.base+0x347cea8,f.p(f.system+8))
    check(not f.write() and f.native_writes==0,'system changed rejected')
end
for _,key in ipairs({'write_fail','short_write','bad_readback'}) do
    local f=setup(); f[key]=true; local ok,reason=f.write()
    check(not ok and (reason=='write_failed' or reason=='write_readback_failed'),'native failure detected')
    check(f.native_writes==1,'no unsafe rollback')
end
do
    local f=setup(); f.api=f.realapi
    local n=Core.tick(f.api); check(n==1 and f.native_writes==1,'core plus real adapter with mocked native APIs')
end
setfenv(MakeData,parent)
return checks
