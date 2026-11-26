-- Integration test of the Mod Options Menu addon against the real code mod DLL (no game needed).
--   luajit tests/test_options_addon.lua <path to p11_self_hit_fast.dll> hellforge/options-addon/p11_self_hit_options.lua
-- Loads the built DLL (so GetModuleHandleA finds it), mocks the BSL update chain and Mod Options Menu, runs the addon.
local ffi = require('ffi')
local dll = ffi.load(arg[1])
ffi.cdef[[ int p11_self_hit_get_scope(void); int p11_self_hit_set_scope(int); ]]
local registered, callbacks = {}, {}
local values = {}
local updates = 0
rawset(_G, 'update', function() updates = updates + 1 end)
local function run(n) for i = 1, n do update(0.016) end end
-- addon loads before MOM exists
dofile(arg[2])
run(5)
assert(P11SelfHitOptions.status == 'DLL found', P11SelfHitOptions.status)
rawset(_G, 'ModOptionsMenu', {api = 1,
  register_option = function(id, spec) registered[id] = spec; values[id] = values[id] or spec.default; return true end,
  on_change = function(id, cb) callbacks[id] = cb; return true end,
  get = function(id) return values[id] end})
values['local_p11_self_hit.scope'] = 3 -- a saved value
run(3)
local spec = registered['local_p11_self_hit.scope']
assert(spec and spec.type == 'choice' and #spec.choices == 4 and spec.mod_id == 'local.p11-self-hit-fast')
print('registered: default', spec.default, 'status:', P11SelfHitOptions.status)
assert(dll.p11_self_hit_get_scope() == 3, 'saved value not pushed')
callbacks['local_p11_self_hit.scope'](4, 'local_p11_self_hit.scope')
assert(dll.p11_self_hit_get_scope() == 4)
print('after APPLY 4:', dll.p11_self_hit_get_scope(), P11SelfHitOptions.status)
assert(dll.p11_self_hit_set_scope(0) == 0 and dll.p11_self_hit_set_scope(5) == 0)
assert(updates == 8, 'previous update not chained: ' .. updates)
-- loading twice is a no-op
dofile(arg[2]); run(1); assert(updates == 9)
for _, c in ipairs(spec.choices) do assert(#c > 0) end
print('description chars (utf8):', select(2, spec.description:gsub('[^\128-\191]', '')))
print('OK')
