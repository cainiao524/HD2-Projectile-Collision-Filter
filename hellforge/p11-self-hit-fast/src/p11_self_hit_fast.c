/* Projectile self hit for Helldiver weapons, no hook and no per-shot work beyond a table lookup (build 25480438).
 *
 * The projectile constructor (spawn, game.dll+0x13a9830) composes each slot's flags word at pool+0x203c+2*slot
 * (stored at +0x13a9c49). Bit 0x20 is "exclude owner": the hit test at +0x13ac6a1 skips the shooter's own unit while
 * it is set. The constructor sets it unless the caller's options struct (r13) is non-NULL and its byte +0x18 is 0;
 * the gun route (+0x6165c2) always passes 1. Ricochets clear the bit in vanilla (+0x13ae71a).
 *
 * At +0x13a9bb3 ecx (zero-extended into rcx) holds the new projectile's type; the flags of `test r13, r13`
 * (+0x13a9a5b) are still live. The 20 bytes at +0x13a9bbd pick r8w (0 or 0x20) and fall into +0x13a9bd1; nothing
 * outside them jumps into them. They become a 14-byte absolute jump to this stub (r8 is the output, free to use):
 *
 *   +00 74 2A                je   L20               ; options NULL -> 0x20 (vanilla)
 *   +02 81 F9 00 04 00 00    cmp  ecx, 1024
 *   +08 73 11                jae  VAN
 *   +0A 49 B8 <table>        mov  r8, table         ; one byte per projectile type
 *   +14 41 80 3C 08 00       cmp  byte [r8+rcx], 0
 *   +19 75 0C                jne  SELF
 *   +1B 41 38 5D 18     VAN: cmp  byte [r13+18h], bl
 *   +1F 75 0B                jne  L20
 *   +21 44 0F B7 C3          movzx r8d, bx          ; vanilla: option 0
 *   +25 EB 0B                jmp  BACK
 *   +27 45 31 C0       SELF: xor  r8d, r8d          ; no "exclude owner"
 *   +2A EB 06                jmp  BACK
 *   +2C 41 B8 20 00 00 00 L20: mov r8d, 20h
 *   +32 FF 25 00 00 00 00 BACK: jmp [rip+0] -> game.dll+0x13a9bd1
 * The code after +0x13a9bd1 sets the flags (and ax,10h) before any branch reads them.
 *
 * The table is filled on the game thread, from the projectile types the armory weapons' records name (entities from
 * hellforge_content.h, see weapon_catalog.h), for the scope Mod Options Menu sets (through the Lua addon and
 * p11_self_hit_set_scope) or, without the menu, self-hit.ini's (re-read when the file changes).
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "hellforge_mod.h"
#include "hellforge_components.h"
#include <stdio.h>
#include <string.h>
#include "weapon_catalog.h"

#define VERSION "1.0.0"
#define SITE 0x13a9bb3u
#define PATCH_AT 0x13a9bbdu
#define RESUME 0x13a9bd1u
#define ROW_LOOKUP 0x616523u /* lea rcx,[projectile row pointers]; mov rcx,[rcx+rax*8] */
#define P11_TYPE 318u
#define TYPES 1024u

static const uint8_t kOriginal[30] = {
    0x8B, 0x08, 0x42, 0x89, 0x8C, 0xA6, 0x40, 0x50, 0x0E, 0x00,             /* kept */
    0x74, 0x0C, 0x41, 0x38, 0x5D, 0x18, 0x75, 0x06, 0x44, 0x0F, 0xB7, 0xC3, /* replaced */
    0xEB, 0x06, 0x41, 0xB8, 0x20, 0x00, 0x00, 0x00,
};
static const char kFlagStore[] = "66 42 89 94 66 3C 20 00 00"; /* +0x13a9c49 mov [rsi+r12*2+203Ch],dx */
static const char kOwnerGate[] = "41 F6 84 47 3C 20 00 00 20"; /* +0x13ac6a1 test byte [..+203Ch],20h */
static const char kNullTest[] = "4D 85 ED";                     /* +0x13a9a5b test r13,r13 */

static const char* const kScopeNames[5] = {
    "", "P-11 Only / 僅治療手槍", "All Sidearms / 手槍全部", "All Weapons (No Shotguns) / 全部武器不包括霰彈槍",
    "All Weapons (Including Shotguns) / 全部武器包括霰彈槍",
};

static struct {
    volatile uint8_t* table;  /* read by the stub */
    uintptr_t game;
    int patched, entities_ready, scope;
    wchar_t ini[MAX_PATH];
    FILETIME ini_time;
    uint32_t frames;
} g;

static void AbsJump(uint8_t* out, uintptr_t target)
{
    static const uint8_t jmp[6] = {0xFF, 0x25, 0, 0, 0, 0};
    memcpy(out, jmp, sizeof jmp);
    memcpy(out + 6, &target, 8);
}

/* ---- config ---------------------------------------------------------------------------------------------------- */

static const char kDefaultIni[] =
    "; Projectile Self Hit / 子彈能擊中自己 (local.p11-self-hit-fast)\r\n"
    "; With Mod Options Menu, choose in game under ESC > MODS; this file then follows the menu.\r\n"
    "; 有 Mod Options Menu 時在遊戲內 ESC > MODS 選，本檔會跟著選單更新。\r\n"
    "; Without it, saved changes apply in game within about 2 seconds. / 沒有選單時，存檔後約 2 秒內生效。\r\n"
    ";\r\n"
    "; Effect Scope / 生效範圍 (pick one / 四選一):\r\n"
    ";   1 = P-11 Only / 僅治療手槍 (recommended, default / 推薦，預設)\r\n"
    ";   2 = All Sidearms / 手槍全部 (no shotguns or multi-pellet / 排除霰彈／多彈丸)\r\n"
    ";   3 = All Weapons (No Shotguns) / 全部武器不包括霰彈槍\r\n"
    ";   4 = All Weapons (Including Shotguns) / 全部武器包括霰彈槍\r\n"
    ";       This mod's cost does not grow with pellets; shotgun pellets can hit you at the muzzle.\r\n"
    ";       本模組的開銷不隨彈丸數增加；但霰彈彈丸可能在槍口就打到自己。\r\n"
    "scope=1\r\n";

static int ReadScope(void)
{
    FILE* f = _wfopen(g.ini, L"rb");
    if (f == NULL) {
        f = _wfopen(g.ini, L"wb");
        if (f != NULL) { fwrite(kDefaultIni, 1, sizeof kDefaultIni - 1, f); fclose(f); }
        return 1;
    }
    char line[256];
    int scope = 1;
    while (fgets(line, sizeof line, f) != NULL) {
        const char* p = line;
        while (*p == ' ' || *p == '\t') p++;
        if (_strnicmp(p, "scope", 5) != 0) continue;
        p += 5;
        while (*p == ' ' || *p == '\t' || *p == '=') p++;
        if (*p >= '1' && *p <= '4') scope = *p - '0';
    }
    fclose(f);
    return scope;
}

/* Mod Options Menu (ESC > MODS) sets the scope through the companion Lua addon (options-addon/), which finds this
 * DLL among the loaded modules and calls these exports from the game's Lua thread. set only records the request;
 * the game-thread tick rebuilds the table and writes self-hit.ini, so the next session starts with the same scope
 * before the menu has registered. Returns the scope taken, or 0 for a value outside 1..4. */
static volatile LONG g_requested; /* 0: none pending */

HF_MOD_EXPORT int p11_self_hit_set_scope(int scope)
{
    if (scope < 1 || scope > 4) return 0;
    InterlockedExchange(&g_requested, scope);
    return scope;
}

HF_MOD_EXPORT int p11_self_hit_get_scope(void)
{
    LONG pending = g_requested;
    return pending != 0 ? (int)pending : g.scope;
}

static void WriteScope(int scope)
{
    char text[sizeof kDefaultIni + 8];
    memcpy(text, kDefaultIni, sizeof kDefaultIni);
    char* s = strstr(text, "scope=1");
    if (s != NULL) s[6] = (char)('0' + scope);
    FILE* f = _wfopen(g.ini, L"wb");
    if (f != NULL) { fwrite(text, 1, strlen(text), f); fclose(f); }
}

static int IniChanged(void)
{
    WIN32_FILE_ATTRIBUTE_DATA a;
    FILETIME t = {0, 0};
    if (GetFileAttributesExW(g.ini, GetFileExInfoStandard, &a)) t = a.ftLastWriteTime;
    if (CompareFileTime(&t, &g.ini_time) == 0) return 0;
    g.ini_time = t;
    return 1;
}

/* ---- table ----------------------------------------------------------------------------------------------------- */

static uint32_t Pellets(const HfApi* hf, uint32_t type)
{
    uint8_t ins[11];
    if (hf->read(g.game + ROW_LOOKUP, ins, sizeof ins) != 0 || ins[0] != 0x48 || ins[1] != 0x8D || ins[2] != 0x0D ||
        ins[7] != 0x48 || ins[8] != 0x8B || ins[9] != 0x0C || ins[10] != 0xC1) return 0;
    int32_t disp;
    memcpy(&disp, ins + 3, 4);
    uintptr_t rows = (uintptr_t)((intptr_t)(g.game + ROW_LOOKUP + 7) + disp), row = 0;
    uint32_t got = 0, pellets = 0;
    if (hf->read(rows + 8ull * type, &row, 8) != 0 || row < 0x10000 || hf->read(row, &got, 4) != 0 || got != type ||
        hf->read(row + 0x1C, &pellets, 4) != 0) return 0;
    return pellets;
}

static uint32_t LiveU32(HfMod* mod, uint64_t entity, HfField field)
{
    HfLiveValue v;
    if (!HF_API(mod)->get_live(mod, (HfRef)entity, &field, &v)) return 0;
    double n = v.now.number;
    return n > 0 && n < TYPES ? (uint32_t)n : 0;
}

static int WeaponTypes(HfMod* mod, uint64_t e, uint32_t* out)
{
    int n = 0;
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(ProjectileWeapon, projectile));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(ProjectileWeapon, weapon_function_projectile_type));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(WeaponMagazine, first_projectile));
    for (int i = 0; i < 32; i++) out[n++] = LiveU32(mod, e, (HfField)HF_FIELD_AT(WeaponMagazine, pattern, i));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(WeaponHeat, level_1_projectile));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(WeaponHeat, level_2_projectile));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(WeaponHeat, level_3_projectile));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(WeaponCharge, level_1_projectile));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(WeaponCharge, level_2_projectile));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(WeaponCharge, level_3_projectile));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(WeaponRounds, primary_projectile));
    out[n++] = LiveU32(mod, e, (HfField)HF_FIELD(WeaponRounds, alternate_projectile));
    return n;
}

static void BuildTable(HfMod* mod, int scope)
{
    const HfApi* hf = HF_API(mod);
    static uint8_t want[TYPES];
    memset(want, 0, sizeof want);
    want[P11_TYPE] = 1;
    uint32_t weapons = 0, skipped_shotgun = 0;
    if (scope >= 2 && g.entities_ready) {
        for (size_t w = 0; w < sizeof kWeapons / sizeof kWeapons[0]; w++) {
            const WeaponEntry* e = &kWeapons[w];
            if (e->slot != 3 && scope < 3) continue;
            if (e->shotgun && scope < 4) { skipped_shotgun++; continue; }
            uint32_t types[64];
            int n = WeaponTypes(mod, e->entity, types), any = 0;
            for (int i = 0; i < n; i++) {
                uint32_t t = types[i];
                if (t == 0 || t >= TYPES) continue;
                if (scope < 4 && Pellets(hf, t) > 1) { skipped_shotgun++; continue; }
                want[t] = 1; any = 1;
            }
            weapons += (uint32_t)any;
        }
    }
    uint32_t count = 0;
    char list[TYPES * 5] = "";
    size_t len = 0;
    for (uint32_t t = 0; t < TYPES; t++) {
        g.table[t] = want[t];
        if (want[t]) {
            count++;
            if (len + 6 < sizeof list) len += (size_t)snprintf(list + len, sizeof list - len, " %u", t);
        }
    }
    hf->log(mod, "scope %d = %s: %u projectile types self-hit (%u weapons, %u shotgun/multi-pellet skips):%s",
            scope, kScopeNames[scope], count, weapons, skipped_shotgun, list);
    if (scope >= 2 && !g.entities_ready) hf->log(mod, "weapon records not loaded yet; P-11 only until they are");
}

static void Tick(HfMod* mod, float dt, void* user)
{
    (void)dt; (void)user;
    if (!g.patched) return;
    LONG requested = InterlockedExchange(&g_requested, 0);
    if (requested != 0) {
        g.scope = (int)requested;
        WriteScope(g.scope);
        IniChanged(); /* take our own write's time, so the ini check below does not rebuild again */
        HF_API(mod)->log(mod, "Mod Options Menu: scope %d = %s", g.scope, kScopeNames[g.scope]);
        BuildTable(mod, g.scope);
        return;
    }
    if ((g.frames++ % 120) != 0) return;
    if (!IniChanged()) return;
    g.scope = ReadScope();
    BuildTable(mod, g.scope);
}

static void EntitiesReady(HfMod* mod, HfEvent event, void* user)
{
    (void)event; (void)user;
    g.entities_ready = 1;
    g.ini_time.dwLowDateTime = g.ini_time.dwHighDateTime = 0xFFFFFFFFu; /* rebuild on the next tick */
}

/* ---- patch ----------------------------------------------------------------------------------------------------- */

static void Patch(HfMod* mod, HfEvent event, void* user)
{
    (void)event; (void)user;
    const HfApi* hf = HF_API(mod);
    uintptr_t game = hf->module_base("game.dll", NULL);
    if (game == 0 || strcmp(hf->build_id(), "25480438") != 0) {
        hf->log(mod, "self hit: not game build 25480438; left as it is");
        return;
    }
    if (!hf->code_matches(game + 0x13a9c49u, kFlagStore) || !hf->code_matches(game + 0x13ac6a1u, kOwnerGate) ||
        !hf->code_matches(game + 0x13a9a5bu, kNullTest)) {
        hf->log(mod, "self hit: the flag store, owner gate or options test is not the reviewed code; left as it is");
        return;
    }
    uint8_t now[sizeof kOriginal];
    if (hf->read(game + SITE, now, sizeof now) != 0 || memcmp(now, kOriginal, sizeof kOriginal) != 0) {
        hf->log(mod, "self hit: game.dll+0x%x is not the reviewed code (another self-hit mod, or HellForge changed it?); left as it is", SITE);
        return;
    }

    /* page 0: stub (made RX), page 1: type table (RW) */
    uint8_t* mem = (uint8_t*)VirtualAlloc(NULL, 8192, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (mem == NULL) { hf->log(mod, "self hit: no memory for the stub; left as it is"); return; }
    uint8_t* table = mem + 4096;
    table[P11_TYPE] = 1;
    uintptr_t t = (uintptr_t)table;
    uint8_t stub[64] = {
        0x74, 0x2A,
        0x81, 0xF9, 0x00, 0x04, 0x00, 0x00,
        0x73, 0x11,
        0x49, 0xB8, 0, 0, 0, 0, 0, 0, 0, 0,
        0x41, 0x80, 0x3C, 0x08, 0x00,
        0x75, 0x0C,
        0x41, 0x38, 0x5D, 0x18,
        0x75, 0x0B,
        0x44, 0x0F, 0xB7, 0xC3,
        0xEB, 0x0B,
        0x45, 0x31, 0xC0,
        0xEB, 0x06,
        0x41, 0xB8, 0x20, 0x00, 0x00, 0x00,
    };
    memcpy(stub + 12, &t, 8);
    AbsJump(stub + 50, game + RESUME);
    memcpy(mem, stub, sizeof stub);
    DWORD old = 0;
    if (!VirtualProtect(mem, 4096, PAGE_EXECUTE_READ, &old)) {
        VirtualFree(mem, 0, MEM_RELEASE);
        hf->log(mod, "self hit: the stub could not be made executable; left as it is");
        return;
    }
    FlushInstructionCache(GetCurrentProcess(), mem, 4096);

    uint8_t site[20];
    AbsJump(site, (uintptr_t)mem);
    memset(site + 14, 0xCC, sizeof site - 14);
    if (hf->write(game + PATCH_AT, site, sizeof site) != 0) {
        hf->log(mod, "self hit: write to game.dll+0x%x refused; left as it is", PATCH_AT);
        return;
    }
    if (hf->read(game + PATCH_AT, now, sizeof site) != 0 || memcmp(now, site, sizeof site) != 0) {
        hf->log(mod, "self hit: read-back after the write does not match");
        return;
    }
    g.game = game;
    g.table = table;
    g.patched = 1;
    hf->log(mod, "self hit: game.dll+0x%x -> stub %p, type table %p (no hook, no per-frame work on shots)",
            PATCH_AT, (void*)mem, (void*)table);
}

HF_MOD_EXPORT int hellforge_mod_init(const HfApi* hf, HfMod* mod)
{
    if (hf->version < 13 || hf->size < offsetof(HfApi, code_matches) + sizeof hf->code_matches) return 1;
    hf->log(mod, "Projectile self hit " VERSION " for game build %s", hf->build_id());
    const char* folder = hf->mod_folder(mod);
    wchar_t wfolder[MAX_PATH];
    if (folder == NULL || !MultiByteToWideChar(CP_UTF8, 0, folder, -1, wfolder, MAX_PATH)) wfolder[0] = 0;
    _snwprintf(g.ini, MAX_PATH - 1, L"%ls\\self-hit.ini", wfolder);
    g.scope = ReadScope();
    hf->log(mod, "config %ls: scope %d = %s", g.ini, g.scope, kScopeNames[g.scope]);
    if (hf->on(mod, HF_EVENT_GAME_LOADED, Patch, NULL) != 0) return 1;
    hf->on(mod, HF_EVENT_ENTITIES_READY, EntitiesReady, NULL);
    if (!hf->on_game_thread(mod, Tick, NULL)) hf->log(mod, "no game-thread callback: scope stays P-11 only");
    return 0;
}
