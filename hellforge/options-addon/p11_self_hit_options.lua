-- HD2-Addon: mods/local/p11_self_hit_options
-- Projectile Self Hit / 子彈能擊中自己: the scope choice in Mod Options Menu (ESC > MODS).
-- Needs the HellForge code mod local.p11-self-hit-fast (its DLL, p11_self_hit_fast.dll, already in the game) and
-- Mod Options Menu. This addon only finds that DLL among the loaded modules (never loads one from disk), registers one
-- choice, and passes the applied value to the DLL's p11_self_hit_set_scope. Changes apply at once (APPLY / Tab).
if rawget(_G, 'P11SelfHitOptions') then return end

local pcall, type, tostring, rawget, rawset, select = pcall, type, tostring, rawget, rawset, select
local unpack = unpack or table.unpack

local OPTION_ID = 'local_p11_self_hit.scope'
local MOD_ID = 'local.p11-self-hit-fast'
local DLL = 'p11_self_hit_fast.dll'
local WAIT_TICKS = 1800 -- give up looking for the DLL / the menu after about 30 s of updates

local state = {version = '1.0.0', status = 'WAITING', ticks = 0}
rawset(_G, 'P11SelfHitOptions', state)

local loader = rawget(_G, 'CowboyBingusModLoader')
local log_file
if loader and type(loader.open_log) == 'function' then
    pcall(function() log_file = loader.open_log('P11SelfHitOptions.log') end)
end
local function note(message)
    state.status = message
    if log_file then pcall(function() log_file:write(message .. '\n'); log_file:flush() end) end
end

-- The DLL's exports, found through the loaded module only. Private FFI names (with __asm__ labels for the real
-- exports) so another mod's prototypes for GetModuleHandleA / GetProcAddress cannot clash with ours.
local set_scope, get_scope
local function find_dll()
    local ok, err = pcall(function()
        local ffi = require('ffi')
        if not pcall(ffi.typeof, 'p11sho_marker') then
            ffi.cdef [[
                typedef struct p11sho_marker { int unused; } p11sho_marker;
                void *p11sho_GetModuleHandleA(const char *name) __asm__("GetModuleHandleA");
                void *p11sho_GetProcAddress(void *module, const char *name) __asm__("GetProcAddress");
            ]]
        end
        local kernel32 = ffi.load('kernel32')
        local module = kernel32.p11sho_GetModuleHandleA(DLL)
        if module == nil then return end
        local set = kernel32.p11sho_GetProcAddress(module, 'p11_self_hit_set_scope')
        local get = kernel32.p11sho_GetProcAddress(module, 'p11_self_hit_get_scope')
        if set == nil or get == nil then error('the DLL has no p11_self_hit_set_scope / get_scope (older version?)', 0) end
        set_scope = ffi.cast('int (*)(int)', set)
        get_scope = ffi.cast('int (*)(void)', get)
    end)
    if not ok then return false, tostring(err) end
    return set_scope ~= nil
end

local CHOICES = {
    'P-11 Only / 僅治療手槍',
    'All Sidearms / 手槍全部',
    'All Weapons (No Shotguns) / 全部武器不包括霰彈槍',
    'All Weapons (Including Shotguns) / 全部武器包括霰彈槍',
}
local DESCRIPTION = 'Which of your own projectiles can hit you. P-11: self-heal with the stim pistol (recommended). '
    .. 'Sidearms / all weapons skip shotguns and multi-pellet rounds unless you include them; pellets can hit you at '
    .. 'the muzzle. Applies at once.\n哪些自己射出的子彈能擊中自己。P-11：治療手槍自我治療（推薦）。'
    .. '手槍／全部武器預設排除霰彈與多彈丸；包括霰彈時彈丸可能在槍口打到自己。立即生效。'

local function push(value, why)
    if type(value) ~= 'number' or value < 1 or value > 4 then return end
    local ok, result = pcall(set_scope, value)
    if ok and result == value then
        note('scope ' .. value .. ' (' .. CHOICES[value] .. ') sent to ' .. DLL .. ' (' .. why .. ')')
    else
        note('scope ' .. value .. ' refused by ' .. DLL .. ': ' .. tostring(result))
    end
end

local registered = false
local function register(menu)
    local default = 1
    local ok, current = pcall(get_scope)
    if ok and type(current) == 'number' and current >= 1 and current <= 4 then default = current end
    local done, why = menu.register_option(OPTION_ID, {
        type = 'choice', mod = 'Projectile Self Hit', mod_id = MOD_ID,
        label = 'Effect Scope / 生效範圍', choices = CHOICES, default = default, description = DESCRIPTION,
    })
    if not done then note('MENU_REFUSED ' .. tostring(why)); return end
    menu.on_change(OPTION_ID, function(value) push(value, 'applied in the menu') end)
    registered = true
    push(menu.get(OPTION_ID), 'saved value')
end

local function step()
    state.ticks = state.ticks + 1
    if registered or state.gave_up then return end
    if set_scope == nil then
        local found, why = find_dll()
        if why then state.gave_up = true; note('DLL_ERROR ' .. why); return end
        if not found then
            if state.ticks >= WAIT_TICKS then state.gave_up = true; note('NO_DLL ' .. DLL .. ' is not loaded (enable local.p11-self-hit-fast)') end
            return
        end
        note('DLL found')
    end
    local menu = rawget(_G, 'ModOptionsMenu')
    if type(menu) ~= 'table' or type(menu.register_option) ~= 'function' or type(menu.on_change) ~= 'function' then
        if state.ticks >= WAIT_TICKS then state.gave_up = true; note('NO_MENU Mod Options Menu is not installed') end
        return
    end
    local ok, err = pcall(register, menu)
    if not ok then state.gave_up = true; note('REGISTER_FAILED ' .. tostring(err)) end
end

local previous_update = rawget(_G, 'update')
local function pack(...) return {n = select('#', ...), ...} end
if type(previous_update) == 'function' then
    rawset(_G, 'update', function(...)
        local result = pack(previous_update(...))
        pcall(step)
        return unpack(result, 1, result.n)
    end)
    note('WAITING')
else
    note('HALTED no_update_callback')
end
