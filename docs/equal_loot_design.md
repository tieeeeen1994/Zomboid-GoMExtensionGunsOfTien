# GoM Extension: Guns of Tien - Loot Equalizer — design (parked 2026-11-15, not built; open questions at the end)

Sub-mod `GoMExtensionGunsOfTienLootEqualizer` ("Loot Equalizer") in the Guns of Tien Workshop item, like Post-93: players enable it themselves. Requires GoM (and so
Gunworks); the main mod, Post-93, Heavy Ordnance and the XM-556 minigun are optional and join the pools when
enabled. Only these mods' spawn routes are touched (user, 2026-11-15: "keep it simple and only care for GoM and
GoT"; Heavy Ordnance and the minigun added the same day).

## Rule

Where loot spawns and how often stay GoM's (and GoT's). Only **which** item a spawn gives changes: every gun,
explosive or ammo spawn picks evenly from one global pool, "regardless of lore" (a gun case can hold any gun).

## Pools

- **Guns**: every firearm item of GoM, GoT and Post-93, each item counted once (MP7A1 and MP7A2 are two guns),
  launchers included (M79, M16A2_M203...), minus the **excluded** items, by default: `GunsOfTien.UZI_2H`
  (debug item), `MarzGuns.M203_Weapon`, `MarzGuns.CAR15_M203_Weapon`, `GunsOfTienPost93.GROZAGL_GP25` (the
  under-barrel launchers' own items).
- **Zombie slots**: a holster draws from every pool gun that fits a holster, a back slot from every pool gun that
  fits a back slot (by the gun's attachment type).
- **Explosives**: any explosive (GoM's M67, M18, M14 incendiary; GoT has none).
- **Ammo boxes**: any standard box (each calibre's plain round, the three 40 mm boxes included). Special loads
  never spawn (GoM's Hollow Point / Armor Piercing / ..., GoT's 12, Post-93's).
- **Cartons**: any carton.

## Routes covered

- GoM's gun spawners (`ItemSpawnerMap`), every alternative replaced by the equal pick; the kits GoT and Post-93 add
  to them go into the pool instead.
- Guns put in loot lists directly (GoM's Desert Eagle in `PistolCase3`, GoT's late-bag pistols).
- GoM's vanilla replacer (sandbox VanillaWeaponReplacement / VanillaAmmoReplacement): a vanilla gun, box or carton
  becoming a GoM one draws from the pools too, so story and dead-survivor guns get it as well.
- GoM's zombie spawners (holster / back) with the slot filter above.
- `World_Ordnance_Spawner` (explosives).

## The kit (one setting for every gun)

GoM's most common kit (16 of its kits): **1-4 magazines + 1-4 boxes**.
- Magazine slot (user, 2026-11-15): each magazine picked evenly from every magazine that fits the gun (its Gunworks
  magazine profile, else its script `MagazineType`), minus the high-capacity ones (the magazines in GoM's four
  `World_HighCap_*_Magazine_Spawner`, which also hold the drums GoT adds there). So the M16A1 can get STANAG 20, 25
  or 30. The M1 Garand's en-bloc clip and the M60's belt box are those guns' magazines. Speedloader / stripper clip
  guns (Gunworks `SpeedLoader` registry: Python, Detective .38, Rhino, Mosin; no GoM gun has both a magazine and a
  loader) get their loader in this slot, 1-4 like any magazine (user, 2026-11-15). A gun with neither (tube shotguns, launchers, break
  actions) gets boxes only.
- Box: the gun's standard box. A gun with no box (the Double Deuce, 2-bore) gets loose rounds instead.

## Attachments and magazines (user, 2026-11-15)

- **Parts on a found gun**: unchanged. Each gun keeps its own table (GoM's `AttachmentPointsTable`, ours for GoT /
  Post-93): required parts, each optional part's own chance, the loaded magazine.
- **Loose attachments**: any attachment spawn (GoM's nine attachment spawners, GoM's vanilla attachment
  replacement) gives any attachment, evenly.
- **High-capacity magazines** (the magazines in GoM's four `World_HighCap_*_Magazine_Spawner`; still only while
  GoM's SpawnHighCapMags is on): a spawn gives 3-5 magazines from all high-capacity magazines, plus 1-2 boxes of
  those magazines' calibres.
- **Loose standard magazines** (GoM's direct entries, its vanilla magazine replacement): any standard magazine,
  evenly.
- **Loose rounds** (GoM's vanilla replacement of loose rounds): any standard round, evenly; special loads never.

- **Standard magazines** (loose pool) include speedloaders, stripper / en-bloc clips and the M60 belt box.

## Exclusions (user, 2026-11-15)

- Built-in skip list in the code for helper items that must never spawn (`GunsOfTien.UZI_2H` debug item,
  `MarzGuns.M203_Weapon`, `MarzGuns.CAR15_M203_Weapon`, `GunsOfTienPost93.GROZAGL_GP25`); updates add to it.
- One sandbox "never spawn" list (semicolons, empty default) for the admin's own choices, read as spawns happen.

## Other gun mods (added 2026-11-15)

- **Gunworks Heavy Ordnance** (workshop 3802070967, id `HeavyOrdnance`): one gun, `HeavyOrdnance.RPG7` (Firearm,
  back slot). Its only spawn route is `HeavyOrdnance.RPG7_Spawner` (resolved by its own
  `HeavyOrdnance_OnCreate.SelectItem`, placed in ArmyStorageGuns, DrugLabGuns, DrugShackWeapons, FirearmWeapons_Late
  and the three SafehouseBin lists, scaled by its own LootMultiplier): the RPG plus 0-6 loose `SWMG.Rocket_PG7V`. It
  has no magazine and no box, so it takes loose rounds. Its family also holds `HeavyOrdnance.Rocket_Gromit` (a joke
  mug-shaped rocket, never spawned). `HeavyOrdnance.HE_Explosion` (Explosives category) is the rockets' explosion
  helper: built-in skip list. No explosives of its own.
- **XM-556 Hurricane** (workshop 3781692448, id `BobrMinigun`): one gun, `BobrMinigun.Minigun` (Firearm, back
  slot), put bare straight into ArmyStorageGuns (0.5), FirearmWeapons_Late (0.1) and GunStoreRifles (0.1) when its
  file loads; nothing else of it spawns. Magazine `BobrMinigun.MinigunMagazine` (250, a weapon part its parts menu
  refuses to attach or detach; reloading inserts it), script `AmmoBox` `Base.556Box`. Gun and magazine have the
  vanilla `AmmoType` `base:bullets_556`, so GoM's `Hooks/ItemPatcher.lua` (`patchAllItemsAmmo`, OnInitGlobalModData,
  every item script of any mod with a vanilla AmmoType) registers both in GoM's `5.56x45mm` family: the minigun
  loads every GoM 5.56 (armor piercing included, seen in game) and fires each with its round's stats. Its kit box is
  GoM's standard `MarzGuns.556x45_Box`, as for any 5.56 gun (a vanilla `Base.556Box` would be converted by GoM's
  replacement anyway).

## Implementation idea: take over the spawner tables (user, 2026-11-15, parked)

Instead of code that re-picks at spawn time, rewrite the spawner tables once at world load and let GoM's own
resolver do the rest. GoM's spawners are data: `require("MarzWeapons/OnCreate/ItemSpawnerTable").ItemSpawnerMap`,
each spawner a list of alternatives picked evenly (`r:random(#entry)`), the first group the main item, each later
group rolling `minAmountChance`..`maxAmountChance` (defaults 1) items picked evenly from its `items`
(ItemSpawner.lua). GoT's and Post-93's Loot.lua already insert kits there.
- Every gun spawner's alternatives become the full pool, one alternative per gun: `{ items = { gun } }`,
  `{ items = <every standard magazine that fits>, min 1, max 4 }`, `{ items = { <standard box> }, min 1, max 4 }`
  (loose rounds or boxes only where the gun has no magazine / box). Even pick per gun and the kit rolls come from
  GoM's code, including the zombie spawners GoM resolves itself (Hooks/ZombieAttachmentSpawners.lua). Holster
  spawners take the holster-fitting guns, back spawners the back-fitting ones.
- Same treatment: `World_Ordnance_Spawner` (every explosive), the nine attachment spawners (every attachment), the
  four `World_HighCap_*` spawners (every high-capacity magazine + boxes of their calibres).
- GoM's `VanillaReplacerTable` (VanillaWeaponMap / MagazineMap / AmmoMap / AttachmentMap) has the same shape and is
  rewritten the same way. Heavy Ordnance's `HeavyOrdnance/OnCreate/ItemSpawnerTable` too (same shape, `amountChance`).
- Has to run after GoM's, GoT's and Post-93's inserts and after sandbox options load (OnInitGlobalModData or
  later); not traced yet.

Consequences raised, not answered yet:
1. **Exclusion list needs a restart**: the tables are built once at world load, so the sandbox "never spawn" list
   would apply from the next start (name ending " (Requires Restart)"), not as spawns happen (the earlier decision).
2. **Entries that are not spawners** stay outside the tables and keep extra chances on top of the equal pick: GoM's
   Desert Eagle + its magazines in `PistolCase3`, the M60 belt box in ArmyStorageAmmunition / ArmySurplusAmmoBoxes,
   ~35 loose-magazine entries (ItemInsertion.lua), the minigun's three entries, GoT's late-bag pistols (Loot.lua
   `DIRECT`). Recommended: swap each such list entry, at the same weight, for a spawner of its kind (gun entry ->
   a gun spawner, loose magazine -> a loose-magazine spawner) so everything goes through the rewritten tables.
3. **GoM's vanilla replacer rolls 0..`amountChance`** (VanillaReplacer.lua `rollOptionItems`, no minimum), so a
   replaced vanilla gun would get 0-4 magazines and boxes. Option: make its entries hand off to a rewritten gun
   spawner so the kit is 1-4 everywhere; whether a replacement that yields a spawner item resolves (ItemSpawnCore
   deferred queue) must be checked in game.

## Not decided yet

- Use the table takeover above, and answers to its three consequences.
- Loose-round amount for guns with no box (Double Deuce: GoM gives 1-20; RPG: Heavy Ordnance gives 0-6).
- `Rocket_Gromit`: special (never spawns) or standard.
