# GoM Extension: Guns of Tien — working notes

Everything needed to continue this project on another machine (written 2026-10-14). Engine notes for B42 in general
live in `~/Zomboid/Workshop/ZomboidFixesB42/CLAUDE.md` (read it too: load order, Kahlua pitfalls, networking, tooling);
GoM conversion research in `~/Zomboid/Workshop/VWP2GoM/docs/`. Open work: `TODO.md`. Designs: `docs/design.md` (main
mod), `docs/post93_design.md` (Post-93). Nothing in this repo has been run in game yet. The folder is not a git repo
yet (`git init` was offered, not answered). It is listed in `~/Zomboid/Workshop/TienMods.code-workspace`.

## What this is

One Workshop item, two mods in `Contents/mods/`:
- **`GoMExtensionGunsOfTien`** (folder `42/`, empty `common/`): an extension of Guns of Marz (GoM, workshop 3722134990,
  id `GunsOfMarz`) on the Gunworks gang framework (workshop 3722064198, id `SWMG`). `mod.info`:
  `require=SWMG,GunsOfMarz,ammomaker`, `loadModAfter=HBVCEFb42,SWMG,GunsOfMarz,ammomaker`. Item module `GunsOfTien`,
  ammo type namespace `gunsoftien:`, sandbox page `GunsOfTien`.
- **`GoMExtensionGunsOfTienPost93`**: add-on for things that did not exist in July 1993 (the MP7A1, the P90 TR, their
  4.6x30 / 5.7x28 ammo). Requires the main mod too. Module `GunsOfTienPost93`, namespace `gunsoftienpost93:`.
  (The user typed "GoMExtensionGunsOfTIenPost93"; the id was written with a lowercase i, flagged to the user.)

The user (Tien, author of the other `~/Zomboid/Workshop/Tien*` mods) wants **realism, set in Kentucky, July 1993**,
and rich, consistent designs; decisions are taken with them, step by step. Hard dependencies are fine: "our mod
fully depends on GoM and Ammo Maker and will not load without them". Before building a feature, check
`~/Zomboid/Workshop/*` for one of the user's own mods that already does it (e.g. `RakeFeathersToo` already rakes
feathers and eggs; a duplicate was built into Zomboid Fixes by mistake and removed).

## Decisions taken with the user (main mod)

- **Rounds** (12, all real 1993 loads; profiles in `shared/GunsOfTien/Ammunition.lua`, numbers in docs/design.md):
  7.62x39 **US Subsonic** (×0.5 dmg, sound ×0.5; must rack after every shot **unless a PBS-1 is fitted**: low powder
  short-strokes the AK's gas system, the PBS-1's back pressure pushes enough gas into the port — the user wanted this
  behaviour), 7.62x39 **Soft Point**, 7.62x39 **Steel Core** (Norinco, pierces 3), 9mm **147gr Subsonic**, 9mm
  **Hollow Point**, 9mm **+P+**, .45 **Hollow Point**, .45 **+P**, 9x39 **SP-6** (pierces 3), .30-06 and .308 **Soft
  Point** (×1.2 dmg, never pierce), 12 ga **Birdshot** (9 pellets = the engine's cap, ×0.3 dmg per pellet, spread ×2,
  range ×0.5, crits cut). Dropped by the user: PBS-1 wipe wear, extra wear when suppressed, an MP5SD subsonic rule,
  hollow points jamming M1911s, a separate .30-30 soft point. Left alone: GoM's .223 as a weaker "civilian" 5.56.
- **GoM's plain rounds renamed** (translation override only): `SWMG.9x39_Bullet` → 9x39mm SP-5, `SWMG.545x39_Bullet`
  → 5.45x39mm 7N6 (and its boxes). 7N6 also pierces 3 and tumbles (crit chance ×1.1).
- **Realistic piercing** (sandbox `RealisticPiercing`, default on): plain .30-06 / 7.62x51 / .308 pierce 2; plain
  .30-30 is what real .30-30 almost always is, a flat-nosed soft point (keeps the name ".30-30 Round", never pierces).
  Done as a StatsFactory layer keyed by the gun's current round (Gunworks never profiles a gun's own script round).
- **Realistic gun sounds, always on** (the user removed the sandbox option): every GoM gun except the M79 / M203 gets
  SoundRadius / SoundVolume = M16 (175 / 50) × f, f = 2^(ΔdB/10), ΔdB from powder burnt (10·log10(grains/25)),
  barrel (+3 dB per halving vs the calibre's usual barrel), no supersonic crack −5 dB, integral suppressor −17 dB
  (= GoM's ×0.3). AS VAL and MP5SD → 33 / 9; .45 guns quiet; short carbines louder; bolt / lever / shotgun volume
  180-250 → ~50-60. `scripts/sound_model.py` writes `shared/GunsOfTien/SoundTable.lua`; `Sounds.lua` applies it with
  the script setters at every `OnInitGlobalModData`. **Changed from Lua, not by redefining items**: a mod's `item X`
  block replaces GoM's whole item (user's correction), and Lua stays flexible with GoM updates. Call them "realistic",
  not "corrected". SoundGain (what players hear) is untouched.
- **Ammo Maker** (required): every round craftable. Steel Core → Ammo Maker's `762x39AP`, SP-6 → `9x39AP`; the others
  get new types (copies of the calibre's base type) with Make / Produce placeholder recipes. New parts in Ammo Maker
  style: **soft point bullets** `GunsOfTien.BulletRifleSSP` / `BulletRifleMSP` ("Make Soft Point Bullet": standard
  Ammo Maker rifle bullet + Small File Set kept — the dum-dum method of filing the jacket off the nose) and
  **Birdshot Pellets** `GunsOfTien.Birdshot` (a 100-use pouch like Balls 00, 10 per shell; "Pour Birdshot Pellets" /
  "(Furnace)": same metal / crucible / tongs / charcoal as Ammo Maker's buckshot plus the unused vanilla
  `Base.Strainer` (kept) and 0.5 water — the shot-pan method; the user chose this over a mold). Each part has a box.
  Item display names follow Ammo Maker ("Bullet Rifle S SP", "Box Birdshot Pellets").
- **Loot**: boxes next to vanilla boxes of the same calibre (no army / police / SWAT for hunting loads and Chinese
  steel core), plus bonus groups in GoM's spawners; sandbox `AmmoLootMultiplier`. **Sandbox options left**:
  `AmmoLootMultiplier`, `RealisticPiercing`, `SubsonicRackRule` (1 always / 2 unless PBS-1 (default) / 3 never).
- **Art** (all generated, deterministic): rounds and boxes recoloured from GoM's renders / textures
  (`scripts/make_art.py`; real markings: US black tip + green band, SP grey lead tip, steel core silver, SS blue,
  HP green, +P / +P+ purple, SP-6 black, birdshot blue hull); Ammo Maker parts from Ammo Maker's art
  (`scripts/make_ammomaker_art.py`; SP silver "SP" code, birdshot heap of small pellets, shot size "8").
  Contact sheets in `docs/`.

## Decisions taken with the user (Post-93)

- **Guns**: H&K **MP7A1** (two-handed, Rifle hold, back slot, collapsible stock, integral top / left / right rails,
  20 / 30 / 40 magazines in the grip, 950 rpm, damage 0.9-1.4, sound 114 / 33, reload = GoM's "MP5" clips) and FN
  **P90 TR only** (1999, bullpup like the FAMAS, 50-round top magazine, integral top / side rails, 900 rpm, damage
  1.0-1.5, sound 118 / 34, downward ejection, **its own top-loading reload clips**). Standard rounds pierce 2 (in the
  gun scripts). **One suppressor each** with its own muzzle mount device (GoM's suppressor stats). Integrated rails
  are hidden required parts registered as parents of GoM's optics / lights / lasers. Spawns: GoM's
  `World_Anachronistic_Spawner` and `Zombie_Police_SMG_Spawner`. "You build everything": models in Blender by script.
- **Ammo**: 4.6x30 **DM11** (standard) and **Subsonic**; 5.7x28 **SS190** (standard), **SB193** subsonic, **SS197SR**
  (polymer tip, ×1.15, no pierce). Subsonic ×0.6 dmg, sound ×0.5, no pierce. Ammo Maker types `46x30` / `57x28`
  (existing) + `46x30SS`, `57x28SS`, `57x28SR`. 50-round boxes. Art: copper DM11 bullet (GoM's own is khaki; the user
  can switch it in `make_ammo_art.py`), real tip colours (SS190 black, SB193 violet, SS197SR blue).
- Other post-1993 ideas offered but not chosen: 5.56 Mk 262 / M855A1, 5.45 7N22, 7.62x51 M993, 9x39 PAB-9, modern
  9mm HST, 12 ga Flite Control; .300 Blackout would need a new gun.

## File map

- Main mod `Contents/mods/GoMExtensionGunsOfTien/42/media/`: `registries.lua` (ammo types, box tags),
  `sandbox-options.txt`, `scripts/GunsOfTien/` (`items_ammo.txt`, `models_ammo.txt`, `recipes_ammo.txt`,
  `recipes_ammomaker.txt`, `items_ammomaker_parts.txt`, `recipes_ammomaker_parts.txt`), `lua/shared/GunsOfTien/`
  (`Ammunition.lua`, `Sounds.lua`, `SoundTable.lua`, `AmmoMaker.lua`), `lua/server/GunsOfTien/` (`Loot.lua`,
  `HotBrass.lua`), `lua/client/GunsOfTien/Tooltips.lua`, `lua/shared/Translate/EN/` (ItemName, Recipes, Tooltip,
  Sandbox), `textures/`.
- Post-93 `Contents/mods/GoMExtensionGunsOfTienPost93/42/media/`: `registries.lua`, `scripts/GunsOfTienPost93/`
  (ammo items / models / recipes / Ammo Maker placeholders; guns to come from `gen_post93_guns.py`),
  `lua/shared/GunsOfTienPost93/` (`Ammunition.lua`, `AmmoMaker.lua`, `Guns.lua`), `lua/server/GunsOfTienPost93/`
  (`Loot.lua`, `HotBrass.lua`), `lua/client/GunsOfTienPost93/Tooltips.lua`, `AnimSets/player(-vehicle)/actions/`
  (`Load/Unload/Rack/RackAim P90TR_GoT.xml`, `WeaponReloadType = P90TR`, clips `Bob_GunsOfTien_P90_Load / _Unload /
  _Rack / _AimRack` still to make), translations, textures.
- Generators (run with python3 from the repo root; never hand-edit their outputs): `scripts/gen_scripts.py` (main mod
  items / models / recipes / names), `scripts/sound_model.py` (→ SoundTable.lua), `scripts/make_art.py`,
  `scripts/make_ammomaker_art.py`, `scripts/post93/gen_post93_ammo.py`, `scripts/post93/make_ammo_art.py`,
  `scripts/post93/gen_post93_guns.py` (needs `scripts/post93/mp7_points.json` / `p90_points.json`), and the model
  builders `scripts/post93/build_mp7.py`, `build_p90.py` (+ `p90_geometry.py`, `p90_meshio.py`, `p90_decals.py`).

## Status and how to continue

See `TODO.md`. In short: both mods' code is written and syntax-checked; nothing has been loaded in game. The Post-93
**MP7A1 assets are done** (preview `docs/post93_mp7_preview.png`); the **P90 TR model was rejected** by the user and
must be rebuilt to "P90 TR reference" below (the files on disk are the rejected version). Each gun needs: FBX `models_X/weapons/firearms/
GunsOfTienPost93_<GUN>.fbx` (nodes `<GUN>_BODY`, `<GUN>_BOLT`, MP7 also `MP7A1_STOCK` modelled deployed),
magazines FBX `models_X/weapons/magazines/GunsOfTienPost93_<MP7|P90>_magazines.fbx` (nodes `46x30Magazine20/30/40_MP7`,
`57x28Magazine50_P90`), parts FBX `models_X/weapons/parts/GunsOfTienPost93_<MP7|P90>_parts.fbx` (`<MP7|P90>_Suppressor`,
`<MP7|P90>_Muzzle_Mount_Device`), textures `textures/weapons/GunsOfTienPost93/<node>.png` (gun 256 px atlas, others
128 px, RGB), icons `textures/item_GunsOfTienPost93_<name>.png` (32 px, framed like GoM's via make_art.py), points
JSON (muzzle, world, magazine, scope, rail_up / left / right, laser_right, light_left, canon, bolt_fired, MP7
stock_folded, P90 ejection port), preview `docs/post93_<mp7|p90>_preview.png` (with an overlay on GoM's MP5 / FAMAS).
Real sizes: MP7A1 415 / 638 mm, barrel 180 mm; P90 500 mm, barrel 263 mm; model = 0.72 × real. Then run
`gen_post93_guns.py`, check every reference resolves, make the P90 clips with TienInspectWeapon's pipeline, test.

## P90 TR reference (from the user's photo, 2026-10-14)

The first P90 model was rejected. The user supplied a photo of a P90 TR (right side, muzzle left); measured from it,
in real mm, L = back from the muzzle tip, H = above the gun's lowest point (500 mm long, 214 mm tall with the rail):
- Muzzle device (flash hider with two side ports, knurled ring at its base): L 0-42 at bore height H ≈ 122, ~22 mm wide.
- Front face vertical at L ≈ 42 from the rail block top down to H ≈ 70; below it the **front hand-stop hook**, a
  rounded hook reaching the bottom (H ≈ 2) at L 90-135, with a small step on its front edge at H 60-80.
- **Front opening** (rounded oval): L 141-175, H 41-87; the **trigger** a short blade at its rear-lower edge, L 169-183,
  H 45-52.
- **Grip column** between the openings: L 175-246, flowing into the belly.
- **Rear opening / thumbhole** (larger rounded rectangle): L 246-306, H 48-92.
- **Belly**: one smooth U under both openings: up to H ≈ 25-30 under the front opening (L ~150), down to H ≈ 0 at
  L 215-275, back up to the butt's flat bottom (H ≈ 32) near L ~345. Thick rounded polymer, the lower frame one smooth
  closed shape with the two openings through it.
- **Butt**: tall slab L 316-500, top H ≈ 159, flat bottom H ≈ 32, vertical rear face with soft corners, small slot at
  the bottom rear; large flat sides with the FN logo panel near its front.
- **Receiver band** H ≈ 92-133 from the front face to the butt: "FN HERSTAL BELGIUM" engraving around L 260-325, a
  side track L 70-215 at H 105-118, the **charging handle** levers on both sides at L 100-120, H 105-118.
- **Magazine** (translucent smoky brown, red-tinted rounds visible) flat on top from L ≈ 103 to 366, H 133-165
  (~32 mm tall, 50-55 mm wide), release tab at its rear L 366-390, H 145-160, just in front of the butt top.
- **TR rail block**: tall block on top at the front, L 42-225, H 133-207, Picatinny rail on top (H 207-214,
  L 65-215), side cut-outs, short side rails at its front; the magazine passes under it. A curved **hoop** arching over
  the magazine at L 205-225 from the block down to the receiver band.
- Ejection port underneath at the rear (L ~300-340). Width ~55 mm; black matte polymer, metal muzzle, rails, handles.
- Origin = rear-top of the pistol grip = top-rear of the grip column, L 246 / H 92: game y = (246 - L) × 0.00072,
  z = (H - 92) × 0.00072 (bore z ≈ 0.0216, muzzle y ≈ 0.177, butt y ≈ -0.183). The firing hand holds the column,
  thumb through the thumbhole; the support hand on the front hook.

## Research reference

Paths below: W = `~/Library/Application Support/Steam/steamapps/workshop/content/108600`,
F = `W/3722064198/mods/Gunworks_gang_framework/42.13/media`, G = `W/3722134990/mods/GunsOfMarz/42.16/media`,
V = `W/3773834525/mods/MarzVanillaGuns/42.18/media` (Vanilla Weapons Plus Gunworks Edition, a worked example of an
outside mod adding ammo), H = `W/3802070967/mods/HeavyOrdnance/42.19/media` (another),
HB = `W/3610677934/mods/Hot_Brass_Visible_Casing_Ejection_Framework/42.15/media` (mod id `HBVCEFb42`). Traced
2026-10-14 from the files, nothing run in game yet.

## How a round works in Gunworks + GoM

- **AmmoType**: `AmmoType.register("ns:name", "Module.Item")` in a mod's own `media/registries.lua` (F, V and H each
  ship one; the namespace need not be the mod id). The second argument is the item key: vanilla reload code finds
  bullets by `getAmmoType():getItemKey()` (`ISLoadBulletsInMagazine` ~14/58/127), so it must equal the round's full
  type. Each round needs its own enum (`Ammo.AmmoProfileSetter` skips when `weapon:getAmmoType() == enum`, Ammo.lua
  ~297). Do not touch `SWMG_AmmoTypes` inside registries.lua (load order); later shared Lua can.
- **The real rounds are `SWMG.*`** (F/scripts/AmmunitionLibrary/ammo.txt, placeholder look); GoM restyles them at load
  with `GunworksUtils/itemAdjustments` `AdjustAmmunitionStats` (G/lua/shared/MarzWeapons/Hooks/AmmoPatch.lua).
  GoM's `MarzGuns.*_Bullet` scripts are orphans. A new mod's rounds can live in its own module, final values written
  in the script (DisplayCategory Ammo, ItemType base:normal, Weight 0.0085 / 0.009 / 0.012, count 5, MetalValue 1,
  Tags base:ammo). **Every round needs `AmmoType = ns:name`** (its own id, never `base:...`): tracer settings are
  loaded only for AmmoTypes some item script names (`Item.resolveItemTypes` ~3147), and
  `IsoBulletTracerEffects.createEffect` (~95) reads them for the gun's current AmmoType with no null check, so a
  round without it most likely throws on every shot. GoM's ItemPatcher adds any item with a vanilla AmmoType to a
  family.
- **Families** (F/lua/shared/WeaponSystems/Utils/Ammo.lua): `RegisterMultipleAmmoFamilies` **appends** to an existing
  family (same `type` replaces in place, ~237-250); family order is the default reload priority
  (`GetOrderedBulletTypesForFamily` ~143-167), so register after GoM. `RegisterAmmoStats` overwrites by profile name
  (use unique names). `RegisterRestoreStats` is a set; GoM's list covers MaxDamage, MinDamage, MaxRange, MinRange,
  CritDmgMultiplier, ProjectileCount, MaxHitCount, CriticalChance, PiercingBullets, SoundRadius, SoundVolume,
  RackAfterShot, ConditionLowerChanceOneIn, MuzzleFlashModelKey.
- GoM profiles `762x39mmAmmo`, `9x19mmAmmo`, `9x39mmAmmo`, `45ACPAmmo`, `545x39mmAmmo` are named in the families but
  **defined nowhere** (no stats = base stats). Defined: the 5.56 set (G/.../Registries/Ammunition.lua 257-299),
  7.62x51 civilian, 12ga slug, 40mm, `38SpecialAmmo`.
- **Family members** (Ammunition.lua 27-156): 7.62x39 = `762x39Magazine30/75`, `SKS` (AK47 feeds from the
  magazines); 9x19 = the M92FS / M93R / HIPOWER / P226 / MP5 (all MP5s) / TEC9 / VP70M magazines; 9x39 =
  `9x39Magazine30` (ASVAL); .45 ACP = `COLT_SINGLE` + M1911 / USP / THOMPSON / MAC10 magazines.
- **Which round loads**: per-player order `GunworksAmmoPref[family]` (AmmoLoaderUI drag), `GetAutomaticReloadAmmoType`
  (R reload, `Magazine.reloadMagazine`); context menu, radial and AmmoLoaderUI list family members by the item's
  display name and texture. `MagazineAmmoProfileSetter` / `AmmoProfileSetter` set the AmmoType (MP: `SWMG`
  `magazineAmmoProfile` / `ammoProfile` commands). modData `AmmoList` (saved) holds one full type per round, last =
  next; the attack hook (CustomSystemHooks.lua ~722-762) applies that round's profile on every shot. A gun's /
  magazine's `ammoType` is not saved (rebuilt from the script).
- **Stat layers** (StatsFactory.lua ~257-309): base = shadow item with all attachments, then each active layer's
  modifiers; `Multiply` multiplies, `Set` overwrites. Ammo and suppressor (`AttachmentCustomStats`, ×0.3 radius and
  volume) multipliers stack (subsonic 5.56 + suppressor = ×0.15). Layer order between Ammo and CustomStatsAttachments
  is UNCONFIRMED (matters only for `Set` conflicts).
- **Boxes / cartons / crates** (G/scripts/MarzWeapons/items/ammunition/ammo_boxes.txt): every calibre and every
  5.56 variant has all three. Box sizes: 7.62x39 and 9x39 = 20 (`OpenBoxOf20Bullets`, tag
  `marzguns:ammobox20`), 9x19 and .45 = 50 (`OpenBoxOf50Bullets`, `marzguns:ammobox50`), 12 gauge = 25
  (`OpenBoxOf25Bullets`, `OpenShellsBox` action; packing = `place25BulletsInBox`); carton = 12 boxes, crate = 4
  cartons. GoM's recipes (G/scripts/MarzWeapons/recipes/ammunition.txt) use closed `itemMapper` lists, so an
  outside mod cannot join them: own tags (`ItemTag.register` in registries.lua) and own recipe names, as V does
  (`OpenBoxOfBullets20_mvgi` etc., V/scripts/MarzVanillaWeapons/items/recipes.txt).
- **Loot**: GoM gives the 5.56 variants **no loot at all**. Its ammo comes from `ItemInsertion.lua`
  (`Distribution.Insert(baseItem, chance, tables, newItem)` relative to vanilla boxes on `OnPostDistributionMerge`,
  F/lua/server/Distribution/Functions.lua), spawner items (`require("MarzWeapons/OnCreate/ItemSpawnerTable")
  .ItemSpawnerMap`, positional bonus groups; adding to an `items` list dilutes the base box) and
  `VanillaReplacerTable.VanillaAmmoMap` (alternatives = random choice). `9x39_Box` is in one spawner only (~1265).
  Sandbox `MarzGuns.LootMultiplier`, `VanillaAmmoReplacement`.
- **Tooltips**: `require("MarzWeapons/ItemTooltipsTable").tooltipsPergun[fullType] = { lines }` (client, hard-coded
  English in GoM; looked up at render time).
- **Hot Brass** (guarded by `getActivatedMods():contains("HBVCEFb42")`, `require("SpentCasingPhysics/Init")`):
  `RegisterCasingToAmmo` keyed by item key (no entry = no casing on fire), `RegisterPressureProfiles` keyed by
  **profile name** (GoM: subsonic 0.25, AP/HP 1.1, +P 1.7, civilian 0.7), `RegisterItemSound` by ejected item type.
  Example: G/lua/server/MarzWeapons/HotBrass/CustomParams.lua.
- **Art**: GoM icons are G/textures/`item_<Name>.png`, 32×32 (`Icon = <Name>`); round models are submeshes of
  `models_X/worlditems/Ammunition/Rounds.fbx` (`mesh = Worlditems/Ammunition/Rounds|762x39_Round`, scale 0.015) with
  128×128 textures in G/textures/worlditems/Ammunition/Rounds/; boxes use vanilla meshes (`WorldItems/RifleAmmoBox`
  0.6, `HandGunAmmoBox` 0.4) with 64×128 textures in .../Ammunition/Boxes/; cartons use vanilla parcel icons.
  Our art: `scripts/make_art.py` (Python 3 + Pillow, reads GoM's PNGs/meshes, writes every icon and texture;
  `--sheet P` contact sheet, `--fit` re-fits icon cameras). Found while making it (2026-10-14): round textures are
  shared per family (762x39 / 9x39 / 7.62x54 = `Russian_Steel_Round_Base`, 9x19 / .38 / .30-30 =
  `Pistol_Standard`, .45 = `Pistol_Medium`, 5.56 / .30-06 / 7.62x51 = `Nato_Round_Base`, .308 / .223 =
  `Nato_Round_CIV`) and every round submesh uses one UV layout: bullet island = texels x 30-100, y 3-30 (point at
  the top). GoM's variant paint covers f >= 0.28 of the bullet (f 0 = case mouth, 1 = point, along the mesh's
  Y axis). Icons are renders: rounds ≈ yaw 269.5 / roll 45 views of the submesh, every rifle box the same
  RifleAmmoBox view, but GoM's .30-30 icon shows Nato colours while its model uses Pistol_Standard. GoM's 5.56
  boxes: accent band (green L in 556x45_Box) → light variant colour, fine-print panel (x 31-46, y 6-73) → label
  ("subsonic rounds", "FULL METAL JACKET" on AP, "HOLLOW POINT", "[P+]"). Shells: buckshot = red hull / green
  box, slug = green hull / red box; the yellow shell texture is only the unused .410 model.
  Post-93 4.6x30 / 5.7x28 art: `scripts/post93/make_ammo_art.py` (imports make_art). GoM has their round meshes
  (`46x30_Round`, `57x28_Round`, same 206-triangle family and UV layout as `556x45_Round`) but no icons, so icons are
  rendered: GoM's 5.56 icon camera, colour/shading learned from item_556x45_Round_Base vs Nato_Round_Base (hue kept,
  saturation ×0.86, value ratio by screen-space normal; GoM icons ≈ texture slightly desaturated, edge pixels alpha =
  coverage and colour × ~coverage). GoM's handgun box icon: only the 9x19_Box panel (eagle, calibre text), the side
  print and the tray show; the lid flap sticker barely does.
- **Other keys by full type**: `RateOfFire.RegisterSpreadAmmoModifier` (item key; GoM's own one uses
  `MarzGuns.556x45_Bullet_Overpressured`, which never matches: a GoM bug), Ammo Maker `ammoMakerAddAmmoTypesMap0..9`
  (GoM and V both write Map0), ItemArrange `IA.arrangables`.

## Ammo Maker (workshop 2788256295, mod id `ammomaker`, a hard requirement of this mod)

- API (its server/ammomaker_apiFunctions.lua, OnPreDistributionMerge): global tables `ammoMakerAddAmmoTypesMap0..9`
  of `{ modId, itemType, ammoType }` are appended to `ammoMakerAmmoTypes[itemType]` (GoM and Vanilla Weapons Plus both
  write Map0, so one overwrites the other; this mod takes the first free slot from 9 down).
- Recipes (shared/ammomaker_recipeManager.lua, OnInitGlobalModData): for each active item, `Make<ammoType>` /
  `Produce<ammoType>` craftRecipes (placeholders in a script, module Base, empty inputs / outputs) are filled with
  `recipe:Load` from `ammoMakerAmmoData[ammoType]` (`grainsAmount`, `bulletType` / `bulletCount`, `casingType`,
  casing models / icons, `bulkCrafting`, `dropExtraData`). **One recipe per ammo type**: two items on the same type
  overwrite each other (`pairs` order), so every round needs its own type. Unused types' recipes are hidden by
  `updateRecipesInactive`.
- `ammoMakerAmmoData` is a plain global table: new types are copies of a calibre's base type with another bullet part
  (parts in shared/ammomaker_ammoParts.lua: `BulletRifleS/M/L`, `BulletHandgunS/M/L`, each with `AP` / `HP` / `TR`,
  `Balls00`, `Slug12`...). Existing types used here: `762x39AP`, `9x39AP`. Added (shared/GunsOfTien/AmmoMaker.lua):
  762x39SS, 762x39SP, 9x19ParaSS / HP / PPP, 45ACPHP, 45ACPP, 3006SpringSP, 308WinSP, 12Bird.
- Ammo Maker makes projectiles two ways: **cast** in a part mold at a furnace (standard bullets, one mold per size
  class Rifle / Handgun S, M, L; AP bullets from the same mold in steel; Balls 00; slugs), where the casting uses the
  mold up and gives a blank Mold back that `MakeMoldBullets` re-imprints from a kept sample (the recipe is generated
  from every active part's `moldType`); or **converted** from a standard bullet (hollow point = standard bullet +
  Small File Set kept; tracer = + pyro paste). Everything is cast from iron / steel scrap, not lead. `Balls00` is a
  drainable pouch (UseDelta 0.01, 100 uses; a 00 shell takes 10); `MakeBalls00` gives 3 pouches.
- This mod's parts (scripts/GunsOfTien/items_ammomaker_parts.txt, entries in `ammoMakerAmmoParts` from
  shared/GunsOfTien/AmmoMaker.lua): `BulletRifleSSP` / `BulletRifleMSP` (soft points, converted: standard rifle
  bullet + Small File Set, "dum-dum" filing) and `Birdshot` (a pouch like Balls 00, poured with vanilla's unused
  `Base.Strainer` + water at a furnace, no mold), each with a box for Ammo Maker's generated pack / unpack recipes
  (its loot code inserts every "Shotgun" part's `boxType` unchecked). Fluid input at a furnace (entity) recipe is
  written like vanilla's pottery wheel: `item 1 [*] mode:keep flags[ItemIsFluid;HandcraftOnly]` +
  `-fluid 0.5 categories[Water] mode:mixture`.

## Combat mechanics that matter here (42.21 Java, traced 2026-10-14; decompiles in the session scratchpad)

- **Piercing** (`CombatManager.calculateHitInfoList` ~2296-2396): candidates within MaxRange, within 2.75 tiles of the
  aim line, in line of sight, and listed by the native ballistics code; nearest first; the loop stops at
  `MaxHitCount` (script default 1000). `PiercingBullets` only filters later targets to within 1° of the first (seen
  from the shooter); without it the N nearest candidates are hit with no line test (GoM's Thompson, MaxHitCount 2).
  Vanilla bug: the "no reference yet" marker is −1, but `atan2` is negative for targets south of the shooter, so
  shooting S / SE / SW never filters (hits the MaxHitCount nearest). No damage split for firearms; a ÷5
  `PIERCING_BULLET_DAMAGE_REDUCTION` (~790-809) applies only when a later target sits on exactly the first one's
  offset. **GoM gives every rifle `MaxHitcount = 1`** (lower-case `c`; DoParam is case-insensitive), so its
  `PiercingBullets = true` (bolt rifles, M60, BAR, SKS, PSG-1, lever rifles) does nothing. In MP the server's copy
  must agree (extra hits past its MaxHitCount re-fire `OnWeaponSwingHitPoint`; anticheat allows ProjectileCount ×
  MaxHitCount hits).
- **Pellets** only on `RangeFalloff` guns (every GoM shotgun: `Projectilecount = 9`, `MaxHitcount = 9`): the native
  code returns at most 9 pellet records, each zombie hit by N pellets gets N independent hits (own hit roll, own
  damage); RangeFalloff guns get ×2 damage. Damage chain: head ×3, limbs ×0.05, × (1 − clothing defence), ×1.5 not
  facing, ×1.5 non-player, ×0.3, crit × max(2, CritDmgMultiplier). No distance falloff in Java; MaxRange limits
  candidates and pellet ray length. Zombie health (Normal) 1.8-2.1.
- **StatsFactory layers**: `SF.RegisterModifierLayer(id, getModifiers(w), restoreStats, isApplicable(w))`, run in
  registration order (Gunworks' Ammo first, a later mod's last). A modifier is any `function(weapon, base)`.
  `ReapplyAllModifiers` runs on equip, game start (player 0), attach / detach (`complete`, server in MP), fire-mode /
  stock / bipod changes and round-type changes; the attack hook calls `Ammo.AmmoProfileSetter` per shot, which
  returns early when the round's enum equals the gun's AmmoType, so a gun firing only its script's own round never
  gets an ammo profile (hence a layer for plain-round piercing). The client is not re-applied after a server-side
  attach.
- **Item definitions**: an `item X` block in another mod's scripts (same module) replaces GoM's whole item, by mod
  load order (user, 2026-10-14). This mod changes GoM's guns from Lua instead (script setters at
  OnInitGlobalModData), so GoM's other stats and later GoM updates are kept.
- **Item sound**: `Item.DoParam("SoundRadius = n")` / `SoundVolume` (integers) and the script setters
  `setSoundRadius` / `setSoundVolume` work; copied into the gun at creation (`Item.java` ~1657), not saved, so
  loaded guns take the script value. The world sound comes from the shooting client's copy.

## Gun sound stats in GoM (item scripts, G/scripts/MarzWeapons/items/weapons/*.txt)

`SoundRadius` (tiles zombies hear it), `SoundVolume` (how strongly it draws them), `SoundGain` (playback loudness for
players). GoM is inconsistent: bolt rifles 250 volume, shotguns 200, lever rifles 180-230, but assault and battle
rifles 30-50; short-barrel carbines quieter than the M16 (real: louder). Suppressors (`AttachmentCustomStats`) ×0.3
radius and volume, ×0.9 damage, swing sound `CapGunRevolverShoot` (rifles) / `CapGunRifleShoot` (pistols); 5.56
subsonic ×0.5. Integral: MP5SD 50 / 15, ASVAL 50 / 25.

## Gun assets in GoM (for the Post-93 sub-mod's MP7 / P90; traced 2026-10-14 on the MP5 family)

Scratch tools of that trace (inspect_fbx.py, bounds.py, gripzoom.py, rt.py, synth.py) were in the session scratchpad.
- **Model scripts** (G/scripts/MarzWeapons/models/weapons/smgs.txt): `mesh = weapons/firearms/MP5|MP5_BODY` = file
  `models_X/weapons/firearms/MP5.fbx`, node `MP5_BODY` (node world transform = mesh transform); texture relative to
  `media/textures`; no `scale` line (1), `cullFace = None`. Attachment points: `muzzle` (engine: flash, shot origin,
  tracers; rotate -90 0 -180), `world` (floor pose, 0.02 0.13 0 / 180 0 180 on every rifle), `magazine`, `scope`,
  `rail_up/down/left/right`, `foregrip`, `laser_right`, `light_left`, `canon` (suppressors / muzzle devices; MP5 has
  none), `bayonet`, `stock` / `stock_folded`, `bolt_lock` / `bolt_fired` (offset = bolt travel; GoM
  AnimationsFiring.lua swaps Bolt_Fired / Bolt_Lock each shot). No `Bip01_Prop1`: the model origin is the right-hand
  prop bone.
- **ModelWeaponPart** = `partType modelName attachmentSelf attachmentParent`: an installed part whose full type equals
  partType draws modelName at the gun's `attachmentParent` point (gun origin if missing), then its own
  `attachmentSelf` (GoM parts define only `world`, so part meshes are modelled with the origin at their mount point).
  Bolts, integrated stocks and magazines are all parts (hidden part items, `MountOn = MarzGuns.FakeItem`). Guns have
  no StaticModel / WorldStaticModel: `WeaponSprite` is used in hand, on the back / holster and on the floor.
- **Mesh files**: Blender 5.1 binary FBX 7400, Geometry + Model only (no material, bones, deformers), Lcl rotation 0,
  scaling 1, UnitScaleFactor 1, Up Y / Front Z. game = (raw x, raw y, -raw z) (Assimp MAKE_LEFT_HANDED). Game space:
  +Y muzzle, +Z top (rifle-held; handgun-held guns MP5K / TEC9 / MAC10 are modelled upside down), +X the gun's left.
  Origin at the rear-top of the pistol grip (MP5 handle y ~0.02, z -0.025..-0.07; bore z 0.041). Drawn at about 0.72
  of real length (MP5 family; GoM 0.62-0.74). FAMAS (bullpup): grip at the origin, body and magazine behind it.
  One magazine FBX per gun class (`models_X/weapons/magazines/smgs.fbx`), origin at the feed lips, hanging along -Z.
- **Blender**: import with defaults gives objects at rotation (90,0,0), scale 0.01, data = raw FBX coordinates;
  `export_scene.fbx` with defaults (apply_scale_options FBX_SCALE_NONE, object_types MESH) round-trips MP5.fbx
  bit-identically except normal order. To build new: object name = node name, data = (game x, game y, -game z),
  rotation_euler (90°,0,0), scale 0.01, export defaults. (FBX_SCALE_ALL / UNITS write UnitScale 100: wrong.)
- **Textures**: gun 256x256 RGB atlas shared by its nodes (baked / painted detail: AO, wear, engraving); magazines and
  parts 128x128 RGB each. Icons `item_<Icon>.png` 32x32 RGBA: diagonal render, muzzle top right.
- **Reload animations** are chosen by a string: Gunworks sets the `WeaponReloadType` anim variable (and
  `GunworksReloadAnim`) to the `animId` registered per gun full type in GoM's `Registries/ReloadAnims.lua`
  (`ReloadAnim.RegisterMultipleWeapons({ [fullType] = { animId, style = "none", durations } })`; MP5 / G3 / PSG1 =
  "MP5", MP5K / TEC9 = "handgun2", FAMAS = "BullpupReload"). AnimSet XMLs (both `AnimSets/player/actions/` and
  `player-vehicle/actions/`): Load / Unload / Rack / RackAim per animId, conditions `PerformingAction=Reload`,
  `WeaponReloadType=<animId>`, `isLoading` / `isUnloading` / `isRacking`, events loadFinished, rackBullet,
  ejectCasing... MP5 load = vanilla `Bob_Reload_Rifle_Load`, unload = the same reversed, rack = `MP5_Rack.X`.
  Bullpup clips are FBX (`Bob_BullpupMagIn/Out/Rack.fbx`; two files carry the stack name `Bob_BullpupRack`). Firing
  and holding: no per-gun clips (Gunworks FirearmReal*/HandgunReal* by `Weapon` = SwingAnim Rifle / Handgun).
- **Sounds**: GoM ships no gun sounds; guns name vanilla FMOD events (MP5: M9Shoot, M16Rack, M1911Equip...). A mod
  file sound: `sound X { category = Item, clip { file = media/sound/X.ogg, volume = ... } }` (GoM's M1Ping).
- **Hot Brass** ejection per gun: `RegisterWeaponParams` in G/lua/server/MarzWeapons/HotBrass/CustomParams.lua (MP5
  forwardOffset 0.36, sideOffset 0.08, heightOffset 0.48, ejectAngle 80; FAMAS forward 0.10).

## Gun data and registries in GoM (MP5 family as the template; traced 2026-10-14)

Full report kept in the session; the essentials, all `require`-able public Gunworks modules (call after GoM's file):
- **Item**: copy `MarzGuns.MP5` (G/scripts/MarzWeapons/items/weapons/smgs.txt 102-233): `AmmoType` = the round's id,
  `MagazineType` (default mag, overwritten at run time), `WeaponReloadType = boltaction` (engine mechanics; the
  animation comes from ReloadAnim), `SwingAnim = Rifle` (= anim `Weapon` = firearm; Handgun for one-handed),
  `AttachmentType` Rifle (back) / Holster, `OnCreate = MarzGuns_OnCreate.AttachParts`, a `ModelWeaponPart` line per
  possible part (bolt states with the gun's own bolt model, stock states, every magazine, rails, each accessory).
  Magazines: `ItemType = base:weaponpart`, `PartType = Clip`, `MountOn = <guns>`, `CanAttach / CanDetach =
  MarzGuns_AttachAndDetach.IsMagazine`, `DisplayCategory = WeaponMagazine`, `AmmoType` = the round. Repair:
  `fixing Fix X { Require = <gun>, Fixer = MarzGuns.RepairPack; Aiming=3, }`.
- **Guns are not in ammo families, their magazines are** (`Ammo.RegisterItemWithFamily(family, mags)`), except guns
  loaded directly (bolt rifles, shotguns, SKS, revolvers).
- **Registries** (GoM file → Gunworks API): Magazines.lua → `Magazine.RegisterMagazineProfile(name, mags)` (appends) +
  `RegisterWeaponWithProfile(name, gun)`; RPM.lua → `RateOfFire.RegisterWeapon(gun, { rpm, burstCount, enableSpread,
  sustainedSpread, maxSpread })` (**required** for RealAuto / RealBurst; RecoilDelay forced to 1 in those);
  AnimationsFiring.lua → `Animations.RegisterWeaponWithAnimatedParts(gun, { SingleAttachment = { open =
  "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" }, cycleTicks = 3 })` (**not** the API_DOCS `attachments =`
  form, which Animations.lua never reads); ReloadAnims.lua → `require("WeaponSystems/ReloadAnim/HandlerFactory")
  .RegisterWeapon(gun, { animId = "MP5", style = "none", durations = { unload = 1.2, load = 1.5, rack = 1.2 } })`;
  Stocks.lua → `FoldingStock.RegisterWeapon(gun, { attachments = { partType = "StockIntegrated", folded, deployed },
  initialState = "folded" })` + CustomStatsAttachments stats for the deployed part (MP5: HitChance ×1.15,
  AimingTime ×0.75); UniversalAttachments.lua → `UniversalAttachment.RegisterWeapon(gun, { ["MarzGuns.Picatinny_Rail"]
  = { Up, Down, Left, Right } })`; PermanentAttachments.lua → `PreventRemovals.Register({ mags })`;
  `require("MarzWeapons/OnCreate/AttachmentPointsTable").weaponAttachmentTablesAndChances[gun] = { required = {
  "MarzGuns.Bolt_Lock", <folded stock> }, optionals = { "mag:chance", "part:chance:PRU|PRD|PRL|PRR" } }` (spawn parts,
  ammo filled with the gun's script round).
- **Attachments**: MountOn lists are in the part scripts; `DoParam("MountOn = ...")` replaces; Gunworks
  `GSU.AddWeaponsToMountOn(part, guns)` appends (writes `"; "`, untested). Optics need `Picatinny_Rail_Up`, foregrips
  rail down, lights rail left, lasers rail right. Pistol suppressors (M&P, Shh9) need `Pistol_Muzzle_Mount_Device`.
- **Spawns**: `require("MarzWeapons/OnCreate/ItemSpawnerTable").ItemSpawnerMap`: insert a new alternative (gun + its
  magazines + box) into `MarzGuns.Zombie_Police_SMG_Spawner` (SWAT zombies, police bags, prison riot, SWAT trucks),
  `World_Short_SMG_Spawner` (gun stores, bandits) or `World_Anachronistic_Spawner` (post-1993 guns: G36, Benelli M4,
  AA-12...; in FirearmWeapons_Late, SafehouseBin_Late). GoM's `addItem` is local.
- **Tooltips**: `require("MarzWeapons/ItemTooltipsTable").tooltipsPergun[gun] = { "Uses ...", "Available Picatinny
  Slots: ..." }`. Hot Brass `RegisterWeaponParams` by gun full type; Hot Brass already ships `HBVCEF.46x30_Casing`
  and `57x28_Casing` and P90 (downward: forward 0.35, side 0.10, height 0.50, shellForce 0.10, sideSpread 10,
  ejectAngle 0, verticalForce -0.6) / MP7 (forward 0.40, side 0, height 0.45, shellForce 0.60, sideSpread 30)
  values for another mod's guns. Ammo Maker already has types `46x30` and `57x28`.
- **GoM seems to plan 5.7 content** (ItemName keys `MarzGuns.57x28_Bullet/Box/Carton/Crate`, `MarzGuns.FIVESEVEN`;
  round, casing models and items for 4.6x30 and 5.7x28). Gunworks registers `swmg:bullet_57x28` with no item. Use our
  own module and ids, never `MarzGuns.` / `SWMG.` names.
