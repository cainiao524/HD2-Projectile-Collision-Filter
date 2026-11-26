# Archive / 舊版留檔

## `v0.3-bsl-arsenal/`

The Arsenal / Bingus Shared Loader line, moved here unchanged when HellForge v1 became the main version (2026-11-26): Projectile Collision Filter v0.2.1 – v0.3.0-preview.8 (formerly P11-Enhanced), the Update Toolkit, the BSL four-scope candidate (`integrations/bsl_four_scope_self_hit/`), their docs, maintenance data and user-report evidence.

Those builds clear the "exclude owner" flag `0x20` shot by shot after each projectile spawns, with ownership and identity checks on every write. That is why they cost more with shotguns and heavy fire; v1 decides at the source instead (see [../docs/HOW-IT-WORKS.md](../docs/HOW-IT-WORKS.md)).

Their releases and tags stay on GitHub for rollback. Paths inside the archive are relative to `v0.3-bsl-arsenal/`: run its tools from that folder. Its `AGENTS.md` and rules apply to that line only.

---

Arsenal／BSL 線在 HellForge v1 成為主版本時（2026-11-26）原樣移到這裡：Projectile Collision Filter v0.2.1 到 v0.3.0-preview.8（前身 P11-Enhanced）、Update Toolkit、BSL 四選一候選，以及它們的文件、維護資料與使用者回報紀錄。

這些版本是在射彈生成後逐發清除 `0x20`，每次寫入都做所有權與身份核對，所以霰彈槍和大量射彈時開銷較大；v1 改在旗標產生的源頭判斷。舊 Release 與標籤保留可回退。archive 內的路徑以 `v0.3-bsl-arsenal/` 為根，工具請在該資料夾內執行；其中的 `AGENTS.md` 與規則只適用於那條線。
