# GoM Extension: Guns of Tien — working notes

Everything needed to continue this project on another machine (written 2026-10-14). Engine notes for B42 in general
live in `~/Zomboid/Workshop/ZomboidFixesB42/CLAUDE.md` (read it too: load order, Kahlua pitfalls, networking, tooling);
GoM conversion research in `~/Zomboid/Workshop/VWP2GoM/docs/`. Open work: `TODO.md`. Designs: `docs/design.md` (main
mod), `docs/post93_design.md` (Post-93). Nothing in this repo has been run in game yet. It is a git repo (branch
master) and is listed in `~/Zomboid/Workshop/TienMods.code-workspace`. Work happens on the Mac and on a Windows PC
(Blender 5.2 at `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`, Python `py`, GoM under
`C:/Program Files (x86)/Steam/steamapps/workshop/content/108600`); `make_art.py` finds either install.

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
- **Loot: none** (user, 2026-10-17: "GoM doesn't allow you to loot specialized ammunition... do not add them, as well
  as our mod's"): GoM spawns only each calibre's standard box (plus the 12 ga slug beside buckshot and the 40 mm
  grenades); its 5.56 Hollow Point / Armor Piercing / Subsonic / Overpressured never spawn. All 12 of this mod's rounds
  are such special loads, so the main mod has no loot code (its old `server/GunsOfTien/Loot.lua`, boxes beside vanilla
  boxes plus GoM spawner bonus groups, was deleted); they come from Ammo Maker. Ammo Maker still spawns this mod's
  bullet / pellet parts itself, as it does every active part. No loot multiplier of our own (removed 2026-10-17,
  user: "if GoM has it, use their option"): the Post-93 loot follows GoM's `MarzGuns.LootMultiplier` ("GoM Loot
  Multiplier"; it scales GoM's spawner placements, and Loot.lua scales our own entries by it). Removing
  `GunsOfTien.AmmoLootMultiplier` only drops that key from servers' saved sandbox files. **Sandbox options left**:
  `RealisticPiercing`,
  `SubsonicRackRule` (1 always / 2 unless PBS-1 (default) / 3 never).
- **Art** (all generated, deterministic): rounds and boxes recoloured from GoM's renders / textures
  (`scripts/make_art.py`; real markings: US black tip + green band, SP grey lead tip, steel core silver, SS blue,
  HP green, +P / +P+ purple, SP-6 black, birdshot blue hull); Ammo Maker parts from Ammo Maker's art
  (`scripts/make_ammomaker_art.py`; SP silver "SP" code, birdshot heap of small pellets, shot size "8").
  Contact sheets in `docs/`.

## Decisions taken with the user (Post-93)

- **Guns**: H&K **MP7A1** (**held like a pistol** too (user, 2026-10-15), back slot, collapsible stock, integral folding front grip (user, 2026-10-18), integral top
  / left / right rails, 20 / 30 / 40 magazines in the grip, 950 rpm, damage 0.9-1.4, sound 114 / 33, reload = vanilla's
  pistol clips with the P90's magazine behaviour; shown as **"MP7A1 Submachine Gun"** (until the MP7A2, 2026-10-18: "MP7 Submachine Gun"), parts "MP7 ...", GoM's naming
  (user, 2026-10-15; item IDs keep `MP7A1`; the P90 likewise "P90 Submachine Gun", parts "P90 ...", ID `P90TR`)) and FN
  **Every display name follows GoM's conventions (user, 2026-10-15)**: mount devices "4.6x30mm / 5.7x28mm Family Muzzle
  Mounting Device" (GoM: "AR Family ..."), suppressors by their real model "Rotex-II Suppressor (4.6x30mm Weapons)"
  (B&T, made with H&K for the MP7) and "SP90 Suppressor (5.7x28mm Weapons)" (Gemtech, for FN; renamed "SP90
  Suppressor" 2026-10-16 when the Five-seveN got its own "SFN-57 Suppressor": the 5.7x28mm suppressors carry the model
  only, the MP7's keeps its bracket by the user's choice), stocks "(Folded)" /
  "(Deployed)"; ammunition "<calibre> <name> Round / Box", "Carton / Crate of ... Boxes", +P in square brackets, a real
  load name followed by its use in parentheses: "US Round (Subsonic)", "Steel Core / SP-6 Round (Armor Piercing)",
  "147gr / SB193 Round (Subsonic)", "SS197SR Round (Hollow Point)" (USAGE tables in gen_scripts.py /
  gen_post93_ammo.py).
  **P90 TR only** (1999, bullpup like the FAMAS, **held like a pistol** (user, 2026-10-14: SwingAnim Handgun, handgun
  reload mechanics, one hand, as GoM's MP5K / TEC9 / MAC10) but **never fits a holster** (AttachmentType Rifle: back slot; the MP7 the same), 50-round top magazine, integral top / side rails, 900 rpm, damage
  1.0-1.5, sound 118 / 34, downward ejection, **its own top-loading reload clips**). Standard rounds pierce 2 (in the
  gun scripts). **One suppressor each** with its own muzzle mount device (GoM's suppressor stats). Integrated rails
  are hidden required parts registered as parents of GoM's optics / lights / lasers. Spawns: GoM's
  `World_Anachronistic_Spawner` and `Zombie_Police_SMG_Spawner`. "You build everything": models in Blender by script.
- **Ammo**: 4.6x30 **DM11** (standard) and **Subsonic**; 5.7x28 **SS190** (standard), **SB193** subsonic, **SS197SR**
  (polymer tip, ×1.15, no pierce). Subsonic ×0.6 dmg, sound ×0.5, no pierce. Ammo Maker types `46x30` / `57x28`
  (existing) + `46x30SS`, `57x28SS`, `57x28SR`. 50-round boxes. Art: copper DM11 bullet (GoM's own is khaki; the user
  can switch it in `make_ammo_art.py`), real tip colours (SS190 black, SB193 violet, SS197SR blue).
- **FN Five-seveN** (user, 2026-10-16) as `MarzGuns.FIVESEVEN`, GoM's own unused name: GoM's pistol features, 20 /
  30-round magazines, its own "SFN-57 Suppressor" on the 5.7x28mm mount device it shares with the P90 (user: one
  suppressor per gun, the mount can be shared), under the rail GoM's two pistol lights (LP and TL; no lasers,
  user 2026-10-16; GoM's TL Tactical Light is pistol-only in its scripts though its model is a full-size flashlight in
  a clamp, the pre-rail way police lit pistols), spawns in
  GoM's police and SWAT handgun spawners and survivor / bandit bags, never civilian homes. See "FN Five-seveN" below.
- **H&K UCP Prototype** (user, 2026-10-17): `GunsOfTienPost93.UCP`, H&K's never-sold 4.6x30mm pistol (prototypes
  about 2004, cancelled 2009), shown as "UCP Prototype"; built like the Five-seveN (build_ucp.py, from a 550 px
  fan-wiki photo of the 2004 prototype traced with `trace_outline.py`, which now does the steps the Five-seveN's trace
  did by hand; the photo's rights are unclear, so it is not in the repo and make_ucp_art.py takes it as `--photo`);
  its own 20-round magazine and a small 40-round drum like the MP7's (user: realistically the UCP is only known with its
  own magazine, nothing shows it took the MP7's, so it keeps its own; a long 40, straight and then curved, was
  rejected); takes the
  MP7's mount device (drawn as `UCP_Muzzle_Mount_Device`) and Rotex-II, GoM's Beretta mount + pistol sights
  and both pistol lights, no lasers. Spawns (user, 2026-10-17): never in civilian homes, so neither pistol is in
  GoM's `World_Anachronistic_Spawner` (GoM inserts it in vanilla's `FirearmWeapons_Late` / `SafehouseBin_Late`, the
  `SafehouseLoot_Late` survivor-safehouse rooms in houses, and in `SurvivorBag_Late` / `BanditBag_Late`); the
  Five-seveN and the UCP alike in GoM's police and SWAT handgun spawners (user, 2026-10-17: the UCP is not rare,
  "treat it like any other gun"; it had been a very rare direct police entry with a required magazine), both pistols
  (+ magazine + box) by direct entries in the two late zombie bags at the 2/7 and 1/7 each Anachronistic gun gets there (Loot.lua `DIRECT`).
- **Loot matches GoM's** (user, 2026-10-17: "everything needs to be lootable the same as GoM"; traced in GoM's
  ItemInsertion.lua / VanillaReplacer*.lua / ItemSpawnerTable.lua): GoM spawns guns only through ~45 spawner items
  inserted in vanilla lists (each a gun + magazines + boxes; zombies carry them through AttachedWeaponDefinitions),
  high-capacity magazines loose through four `World_HighCap_*_Magazine_Spawner` (only with its sandbox
  SpawnHighCapMags), attachments through attachment spawners, boxes and cartons by replacing vanilla's
  (VanillaAmmoMap, sandbox VanillaAmmoReplacement) or `Distribution.Insert` beside them; its crates, its cartons of
  calibres vanilla lacks (7.62x39, 9x39, 5.45) and loose rounds never spawn. Ammo Maker spawns every active part and
  part box itself (ammomaker_itemDistribution.lua, at container fill). Ours follow the same routes; the special
  loads (main mod's 12, Post-93's 4.6x30 Subsonic and 5.7x28 SB193 / SS197SR) never spawn, as GoM's own do not. Its icons reuse the Five-seveN's Glock-fitted
  cameras. The Five-seveN and the UCP have no optic rail of their own: GoM's pistol sights need its Beretta mount.
- Other post-1993 ideas offered but not chosen: 5.56 Mk 262 / M855A1, 5.45 7N22, 7.62x51 M993, 9x39 PAB-9, modern
  9mm HST, 12 ga Flite Control; .300 Blackout would need a new gun.

## File map

- Main mod `Contents/mods/GoMExtensionGunsOfTien/42/media/`: `registries.lua` (ammo types, box tags),
  `sandbox-options.txt`, `scripts/GunsOfTien/` (`items_ammo.txt`, `models_ammo.txt`, `recipes_ammo.txt`,
  `recipes_ammomaker.txt`, `items_ammomaker_parts.txt`, `recipes_ammomaker_parts.txt`), `lua/shared/GunsOfTien/`
  (`Ammunition.lua`, `Sounds.lua`, `SoundTable.lua`, `AmmoMaker.lua`), `lua/server/GunsOfTien/HotBrass.lua` (no
  loot: see "Loot: none"), `lua/client/GunsOfTien/Tooltips.lua`, `lua/shared/Translate/EN/` (ItemName, Recipes, Tooltip,
  Sandbox), `textures/`.
- Post-93 `Contents/mods/GoMExtensionGunsOfTienPost93/42/media/`: `registries.lua`, `scripts/GunsOfTienPost93/`
  (ammo items / models / recipes / Ammo Maker placeholders; guns to come from `gen_post93_guns.py`),
  `lua/shared/GunsOfTienPost93/` (`Ammunition.lua`, `AmmoMaker.lua`, `Guns.lua`), `lua/server/GunsOfTienPost93/`
  (`Loot.lua`, `HotBrass.lua`), `lua/client/GunsOfTienPost93/Tooltips.lua`, `AnimSets/player(-vehicle)/actions/`
  (`Load/Unload/Rack/RackAim P90TR_GoT.xml`, `WeaponReloadType = P90TR`, clips `Bob_GunsOfTien_P90_Load / _Unload /
  _Rack / _AimRack` still to make), translations, textures.
- Workshop art: `scripts/render_ad_guns.py` (Blender: `ad_<gun>.png` of the four Post-93 guns fitted out, the MP7 /
  P90 at one scale and the two pistols at another; pistol renders are game-space-as-world, i.e. mirrored, and
  `make_workshop_art.py` flips them back, so their markings read right; the MP7 / P90 ad renders are **not** flipped
  yet) and `scripts/make_workshop_art.py [preview preview2 preview3 preview4 posters icons]`. preview4 (2026-10-18) is the
  MP7A2 alone, from render_ad_guns.py's `mp7a2` (fitted out without a light, so the handguard's side rail shows),
  mirrored to the game's view like the pistols; added on the Steam page by hand like preview2 / preview3.
- Generators (run with python3 from the repo root; never hand-edit their outputs): `scripts/gen_scripts.py` (main mod
  items / models / recipes / names), `scripts/sound_model.py` (→ SoundTable.lua), `scripts/make_art.py`,
  `scripts/make_ammomaker_art.py`, `scripts/post93/gen_post93_ammo.py`, `scripts/post93/make_ammo_art.py`,
  `scripts/post93/gen_post93_guns.py` (needs `scripts/post93/mp7_points.json` / `p90_points.json` /
  `fiveseven_points.json` / `ucp_points.json`),
  `scripts/check_refs.py` (every item / model / icon / mesh / texture / AnimSet clip name in both mods resolves
  against them, GoM, Gunworks, Ammo Maker, Hot Brass and vanilla, version and common folders), and the model
  builders `scripts/post93/build_mp7.py`, `build_p90.py`, `build_fiveseven.py`, `build_ucp.py` (the others import
  build_mp7 as their library), their review renders `render_mp7.py` / `render_p90.py` / `render_fiveseven.py` /
  `render_ucp.py` (Blender) and sheets + icons `make_mp7_art.py` / `make_p90_art.py` / `make_fiveseven_art.py` /
  `make_ucp_art.py` (Pillow); `trace_outline.py` traces a reference photo's outline.

## Status and how to continue

See `TODO.md`. In short: both mods' code is written and syntax-checked; nothing has been loaded in game. The Post-93
**MP7A1 and P90 TR assets are done**, both rebuilt from the user's photos (previews `docs/post93_mp7_preview.png`, `docs/post93_p90_preview.png` plus the
P90's `post93_p90_magazine.png`, `post93_p90_attachments.png`, `post93_p90_ammo.png`; the P90
was rebuilt from the user's photos and approved 2026-10-14). Each gun has: FBX `models_X/weapons/firearms/
GunsOfTienPost93_<GUN>.fbx` (nodes `<GUN>_BODY`, `<GUN>_BOLT`, MP7 also `MP7A1_STOCK` modelled deployed and `MP7A1_FOREGRIP` modelled folded),
magazines FBX `models_X/weapons/magazines/GunsOfTienPost93_<MP7|P90>_magazines.fbx` (nodes `46x30Magazine20/30/40_MP7`,
`57x28Magazine50_P90`), parts FBX `models_X/weapons/parts/GunsOfTienPost93_<MP7|P90>_parts.fbx` (`<MP7|P90>_Suppressor`,
`<MP7|P90>_Muzzle_Mount_Device`), textures `textures/weapons/GunsOfTienPost93/<node>.png` (gun 256 px atlas, others
128 px, RGB), icons `textures/item_GunsOfTienPost93_<name>.png` (32 px, GoM's icon cameras from
`mp7_icon_cameras.json`), points JSON (`<mp7|p90>_points.json`). Real sizes: MP7A1 415 / 638 mm, barrel 180 mm; P90 500
mm long, 181 mm tall with the TR rail; model = 0.72 × real. Rebuild order (Windows: `blender` = the path above):
`blender -b --factory-startup -P scripts/post93/build_p90.py` (~1 min), `blender -b --factory-startup -P
scripts/post93/render_p90.py -- DIR`, `py scripts/post93/make_p90_art.py --renders DIR`. Next: run `gen_post93_guns.py`,
check every reference resolves, make the P90 clips with TienInspectWeapon's pipeline, test.

## P90 reload animations (2026-10-15, approved from GIFs)

`scripts/post93/anim/p90_reload.py` (Blender; imports `~/Zomboid/Workshop/TienInspectWeapon/scripts/anim`, or
`$TIEN_ANIM`) builds `Bob_GunsOfTien_P90_{Unload,Load,Rack,AimRack}.x` (42 / 54 / 36 / 36 frames at 30 fps = the
Guns.lua durations 1.4 / 1.8 / 1.2 s), shipped in `42/media/anims_X/Bob/` and played by the `*P90TR_GoT.xml` AnimSets
(animId "P90TR"). Rebuild: `blender -b --factory-startup -P scripts/post93/anim/p90_reload.py -- "<game media>/anims_X/Bob"
"$(pwd -W)/tmp/anim/p90" [clips] --preview`, then TienInspectWeapon's `gif.py` / `sheet.py` on `tmp/anim/p90/prev_<clip>`
and its `xanim.py` on the `.x` before copying them in. Base pose vanilla `Bob_IdleHandgun`, second pose
`Bob_IdleAimHandgun`; the left hand's grips are vanilla's (`Bob_Reload_Handgun` frame 48 over the slide, frame 16's hand
orientation at the belt), anchored on contact points (`grip_on`: a template places the **wrist**, ~5 cm from the palm).
Staging: the gun across the chest, muzzle forward-left, top to the eyes, for the magazine (`MAG`); turned further left
so the charging handle faces the body, 5 cm closer, for the rack (`RACK`); hand reach 0.274 from the shoulder.
- Found on the way: a reload with an animId whose clips are missing never ends (the insert waits for `loadFinished`).
  Our unload AnimSet `x_extends` the load one, so its events override in order: `unloadFinished` (Gunworks takes the
  magazine off and the unload ends) inherits `End`. Tried at 0.74, as the hand starts away (`<m_Time>Percentage</m_Time>`
  + `<m_TimePc>` overrides an inherited time); the user preferred `End` (2026-10-15). With `m_EarlyTransitionOut`
  (ours, GoM's and vanilla's reload nodes) `End` events fire when the clip **starts fading out**, the node's blend-out
  time (0.2 s here, x the speed) before its last frame (42.21 `LiveAnimNode.addMainTrack` / `AnimationTrack`: debug
  option `AllowEarlyTransitionOut`, default on without `-debug`), so the magazine leaves ~frame 36 of 42 while the
  hand still moves: what the user saw on GoM's M16 (its unload is vanilla's rifle load clip reversed, `End` with a
  0.2 s blend). A longer blend-out on the unload node alone would take it off earlier and fade longer. The
  load click (`playReloadSound` "load") is at 0.66, the press. AimRack transitions to `IdleHandgun` via
  `Bob_AimToIdle_Handgun`.
- **The magazine leaves the gun with the hand (user, 2026-10-15).** The gun's model only changes when the unload
  action ends (`unloadFinished`, End), so with Gunworks' `style = "none"` the magazine stayed on the gun while the hand
  carried it away. The P90 now uses Gunworks' `"attachments"` style (Guns.lua: `magItem` + `attachments.magPart` =
  the magazine, partType Clip): an AnimSet event `changeWeaponPart` "mag" detaches the magazine **part** for looks only
  and attaches a magazine to the character's reload location (`Bip01_Prop2`, the left hand's prop bone) without ending
  anything (`Visuals.handleWeaponPartAnimEvent`); in the insert the same event puts the part back and removes the prop,
  and the insert's start shows the prop. Ours fire at 0.38 of the unload (frame 16, the hand has the magazine) and 0.66
  of the load (frame 36, pressed home, with the click). `p90_reload.py` keys `Bip01_Prop2` (`key_prop2`): at the swap
  frame exactly where the magazine sits on the gun (the `magazine` point), rigidly in the left hand on the hand's side
  of the swap. The hand-held magazine itself is turned off (user, 2026-10-15: the magazine only leaves the gun and
  comes back): Guns.lua wraps `ReloadAnim.attachReloadMagazine` (shared table, looked up at call time by the handler
  and by `handleWeaponPartAnimEvent`) to skip the P90's handler; the Prop2 keys stay, so dropping the wrapper brings
  it back. Rejected on the way: recutting the clips so the unload ends as the magazine comes off (the action ends
  there and the character snapped out of the reload between the two clips), a mid-clip `unloadFinished`, and held or
  near-still beats in the motion (they read as pauses).
- Preview meshes: an FBX's raw Z is negated from game space (the `.x` weapons and GoM's FBX models agree in game
  space: pistols' top -Z, rifles' +Z), so the gun is drawn with Z flipped back. `pose.from_clip(xa, tick)` takes
  ticks (160 a frame).
- Known and accepted: the left hand stops ~3 cm short of the magazine's rear end, the right wrist is past its natural
  range in some frames, the butt grazes the right hip while the gun is at the chest.

## MP7A1 reference and model (from the user's photos, 2026-10-14)

The first MP7A1 was built from published dimensions only and was off (user: "the handle seems off, the mags seem off
too, the mags of MP7 aren't really straight"); laid over a photo it overlapped 73%. Rebuilt from the user's photos
in `docs/`: `mp7_2.png` (H&K's product photo, left side, muzzle right, stock collapsed, front grip folded, 20-round
magazine; traced into `scripts/post93/mp7_reference_outline.json`, 415 mm = 888 px), `mp7_1.png` (left side, stock
extended, ghosted 40-round magazine), `mp7_3/4.png` (renders of an MP7A1 model, right side). A fifth photo was a Kel-Tec in an
MP7-style chassis, not an MP7, and was deleted. Photo coordinates as for the P90 (L back from the
muzzle tip, H up from the lowest point), 186 mm tall with the sights up:
- Grip almost upright: front edge L 227-234, back L 284-290 with a palm swell, bottom H 3, into the receiver at H 91.6;
  vertical-rib panel L 238-283, H 12-80. Origin = its rear-top, L 289 / H 91.5 (game y = (289 - L) × 0.00072,
  z = (H - 91.5) × 0.00072).
- Trigger guard: a shallow loop L 176-234, bar at H 71-74; trigger blade L 203-228, H 78-101.
- Folded front grip L 74-180, H 71.5-104.5, round nose, three grooves, release button at L 101.5 / H 89.5.
- Lower receiver H 103.5-135 (front) / 91.6-135 (behind the grip), half width 19; upper H 135-166.5, half 15.5;
  slanted metal nose plate from L 58 / H 160 down to a small hand stop at L 41 / H 92; bore H 120; barrel collar and
  flash hider L 0-52 (hider L 0-36.5, r 7). `canon` = L 47.7.
- Picatinny rail L 85-375, crossbars to H 169.6 every 10 mm; flip-up front sight L 89-136, rear drum L 320-370, both
  to H 186; short side rails L 78-140 at H 120 (both sides); T charging handle L 376-394, H 148-165.
- Stock collapsed: butt plate L 385-414, H 36-148 (front face slanting back toward the bottom, two holes at L 397,
  H 46.5 / 55.5), rods at H 140 x ±10; travel 223 mm. The rods run forward to L 360, 25 mm into the receiver
  (its back face is L 385): ending at L 395 left a visible gap with the stock extended (user, 2026-10-15).
- Magazines (`build_mp7.build_magazine`): swept from the feed lips (L 257 / H 104); the 20-round ends at its base
  plate under the grip (H 0.5-5.5), the 30 / 40-round go on 48 / 96 mm. Since 2026-10-17 (the user's photos of H&K's
  30 and 40: "they still look straight on the top", "those are curved") every box magazine curves along its whole
  length on one radius (`BOX_RADIUS` 560 mm: 20 ~10, 30 ~15, 40 ~20 degrees) and is tilted back about its top
  (`BOX_TILT`) so the chord of its part inside the grip lies on the grip's axis (it bows ~2 mm there, the grip has ~13
  to spare); `box_local()` maps texels back to (along, across) for painting. The 30 / 40 carry their lower part
  (`SLEEVE` 50 / 86 mm, a third / 44 % of their length) in a wider polymer sleeve (+1.1 mm a side across, +2 mm front
  to back, a raised rim at its top) with a witness slot, the capacity, "MADE IN GERMANY" / "4.6X30" moulded and, on
  the 40, a round mark; the base plate under it. The drum's tower stays straight (`mag_frame`). The `magazine` point
  has no rotation. Rebuilding on the Mac changes the bytes (not the shapes) of every MP7 asset against the
  Windows-built ones, so after a magazine-only change restore the gun, parts and their textures and part icons from git.
- **60-round drum** `46x30Magazine60_MP7` (user, 2026-10-15; H&K made only 20 / 30 / 40): `build_drum()`, a feed
  tower like the 20-round body up into the grip and a 92 mm drum **facing front and back** (axis along the barrel,
  user: the side-facing Glock-style layout was wrong; 40 mm front to back, centre 4 mm forward of the magazine axis,
  top 1.5 mm under the grip), hub caps, a winding key on the front face, "60" on both faces.
  Weight 0.22 (GoM's MP5 60, since 2026-10-17; was 0.30), "MP7 60Rds Drum 4.6x30mm Magazine", 2% on found MP7s and not in the
  spawner's magazine list. Its icon uses a camera fitted on GoM's `item_9x19Magazine100_MP5` (`make_mp7_art.py
  --fit-drum`, kind "drum"; the other kinds keep their stored cameras).
- **No GoM muzzle devices** (user, 2026-10-15): GoM's `LR2_Compensator`, `LX_Flashhider` and `Trix42_Muzzlebreak`
  are AR rifle parts that neither real gun can take, so they are not allowed on the MP7 or P90 ("if they don't fit
  it, then we shouldn't add them"). Only our own suppressors go on the guns' mount devices.
- `slab()` (the filled-curve profile extrusion) now lives in build_mp7.py and build_p90.py calls it.
- **Held like a pistol since 2026-10-15 (user: "MP7 also needs to be pistol wielded like P90")**: the item block is
  `GUN_HANDGUN` (SwingAnim Handgun, WeaponReloadType handgun, one hand, handgun muzzle flash), AttachmentType stays
  Rifle (back slot, never a holster), and the model is exported upside down exactly as the P90's (body, bolt and stock
  nodes turned; points through `handgun_points()`: upright parts and magazines `rotate -180 0 -180`, canon /
  bolt_fired / stock_folded `0 0 0` because those meshes are turned with the gun, `world` `-0.025 0 0`, `rifle_back` /
  `rifle_back_bag` turning it upright on the back). Textures, magazines, parts and icons came out byte-identical
  (render_mp7.py / make_mp7_art.py turn it back for display, `handgun_hold` in `mp7_points.json`); in vanilla's pistol
  reload the gun sits in the hand muzzle up with the magazine out of the grip's bottom, as it should.

## MP7A1 front grip (2026-10-18)

User: "can't the MP7 take a foregrip? I think it should". The real MP7A1's front grip is integral and folds up
under the receiver; GoM's three foregrips need `Picatinny_Rail_Down`, which the MP7 does not have, so they stay off
it (the "if they don't fit it" rule). `build_mp7.py` builds the grip as its own node `MP7A1_FOREGRIP` (was part of
the body), modelled folded and baked alone (the body is baked without it, so neither the recess nor the grip's top
face carries the other's shadow when it is down). Unfolded = point `foregrip_deployed`: 90 degrees about X through
the hinge (photo L 90.8 / H 88, the centre of the round nose, the release button beside it), its free end at H -1.6,
level with the pistol grip. The engine draws a part at `offset + rotateXYZ . vertex` (42.21
`ModelInstanceRenderData.makeAttachmentTransform`: `translation(offset).rotateXYZ(radians).scale`, JOML, game
space), so offset = hinge - R . hinge; upright the turn is +90, and in the turned (handgun) model -90 (a half turn
about Y flips a turn about X), written that way because `turned()` keeps a given rotate. Which end hinges is from
memory of photos of the unfolded gun (the grip hangs just behind the nose's hand stop), not from a photo in `docs/`.
Parts `MP7A1_Integrated_Foregrip_Folded / _Deployed` (part type `ForegripIntegrated`, `CannotBeRemoved`), folded
required at spawn. The fitted part is the state: `shared/GunsOfTienPost93/Foregrip.lua` swaps them with Gunworks'
`FoldingStock.SwapStockAttachment` (a plain part swap by part type) and `StatsFactory.ReapplyAllModifiers`; Gunworks'
`FoldingStock` itself cannot serve a second fold on one gun (one entry per gun type, state in
`modData.StockFolded`). Its timed action `ISFoldForegripGoT` copies `ISFoldStock` (swap in `complete`,
`CallSyncHandWeaponFields`); `client/GunsOfTienPost93/ForegripMenu.lua` offers "Fold / Unfold Foregrip" in the gun's
context menu and the firearm radial (icons `ui/GunsOfTienPost93_Radial_*Foregrip.png`,
`scripts/post93/make_foregrip_radial.py`, Gunworks' palette). Unfolded stats = GoM's Stub Foregrip (AimingTime x0.8,
Crit and Hit Chance x1.15 through CustomStatsAttachments, spread x0.85 through `RegisterSpreadPartModifier`). The
MP7 is held like a pistol, so the left hand stays at the pistol grip; the grip shows and gives its stats only.
The trigger guard was only its bottom bar, its open front end hidden by the folded grip (user: "it needs to
close"); `GUARD_OUT / GUARD_IN` now start with a front post up into the receiver, leaning forward ~12 degrees along
the grip's rear (user: "close with a slant and not a 90 degree angle"; measured on their muzzle-left side
photo). The trigger blade's top was traced ending at H 101.5, 2 mm under the receiver, so it floated (user: "trigger looks
detached"); `TRIGGER` now runs up to H 106.5, inside the receiver, on both MP7s.
A rebuild on Windows changed only the UV packing of the unchanged magazines and muzzle parts (same shapes and
triangle counts), so their FBX, textures and icons were restored from git, as after a magazine-only change.

## MP7A2 (2026-10-18)

User: "let's add MP7A2 as well". The real A2 (introduced about 2014) is the A1 with a rail handguard in place of the
folding grip: Picatinny rails at 3, 6 and 9 o'clock, the bottom one for a vertical grip or hand stop (Wikipedia,
Army Recognition on Lithuania's 2024 order; IMFDB refused the fetch). Choices (user): names "MP7A1 Submachine Gun" /
"MP7A2 Submachine Gun" (item IDs unchanged, parts and magazines stay "MP7 ..."), GoM's three foregrips on the
bottom rail, spawns as GoM does its MP5 series (one alternative whose gun slot lists `{ MP7A1, MP7A2 }`, picked at
random; same magazines and box). Built from the user's left-side render of an MP7A2 (muzzle left, stock extended;
not a photo, not kept in the repo), scaled 6.81 px/mm by the muzzle tip (L 0) and the receiver's rear face (L 385);
its hand stop (L 44 / H 91), bore and grip bottom land within 2-3 mm of the A1 photo's, so everything else stays the
A1's. `build_mp7.py` `build_body(a2=True)`: `A2_LOWER` (no grip lug), the handguard (`A2_HG_PLATE` side plates L
66.5-173, H 101-128.5, 1.5 mm proud of the receiver; `A2_HG_BOTTOM` under it to H 91.8, sloped front L 66.5 / H 100.5
to L 75 / H 91.8; "metal" material so it reads apart from the receiver, as on the render), side rails L 88-159 at H
118 (seven crossbars), bottom rail L 91-168 (teeth to H 89.5), cap screws painted at L 72.5 / 166.5, H 118; the A1's
short side rails left out; calibre marking moved behind the handguard (L 178.5), "MP7A2" on the right. Own FBX
`GunsOfTienPost93_MP7A2.fbx` (node `MP7A2_BODY`) and texture `MP7A2.png`; bolt and stock are the A1's models
(`MP7A1_BOLT` / `MP7A1_STOCK`, A1 atlas), so the A2 item names them in its ModelWeaponPart lines. Points
`mp7a2_points.json` (`points(bounds, a2=True)`): the A1's, side rails moved, plus `rail_down` (GoM's
Picatinny_Rail_Down spans z -0.0055..0.0011 from it) and `foregrip` (the MP5's sits 0.003 above its rail's bottom;
ours at L 118, the rail's forward third). Parts: it reuses the A1's integrated top / side rail parts, so GoM's optics,
lights and lasers need no new rule; `MP7A2_Integrated_Rail_Down` (PartType RailDown, like GoM's G36C's) is added to
the foregrips' any-of rule (`RequiredAttachment.RegisterRequired` merges into GoM's own) and their MountOn.
Spawn parts: the A1's minus the folding grip, plus GoM's foregrips at its MP5 chances (Stub / MKC 10, MK2 5). Reload
handler registered once per gun (animId "MP7A1" for both: `pointMagPart` rewrites each handler's spec). The two
icons differ only by the handguard at 32 px.

## MP7A1 reload (2026-10-15)

The MP7's magazine goes up into the pistol grip, so it reloads like vanilla's pistols: AnimSets `*MP7A1_GoT.xml`
(animId "MP7A1", player and player-vehicle) play vanilla `Bob_Reload_Handgun_Load` (46 frames, 1.5 s), for the unload
the same reversed but baked into a forward clip `anims_X/Bob/Bob_GunsOfTien_MP7_Unload.x`
(`scripts/post93/anim/mp7_reload.py`, plain Python: key times mirrored, everything else vanilla's), and vanilla
`Bob_Reload_Handgun_Rack` (40 frames) with GoM's / Hot Brass's rack events (`RackHandgun_HB.xml`: rack sound 0.18,
rackStart 0.37, ejectCasing 0.50, rackEnd 0.57; rackBullet made explicit at 0.50). Durations in Guns.lua = the clip
lengths (1.5 / 1.5 / 1.33).
- Chosen over GoM's `handgun2` clips (its MP5K / TEC9 reload, made for a magazine ahead of the grip): measured with the
  MP7 on Bip01_Prop1, vanilla's left palm gets to 0.047 from the magazine base, GoM's to 0.074. GoM's
  `Bob_Reload_Handgun2*.X` store **matrix keys** (AnimationKey type 4, 16 floats, row-major like FrameTransformMatrix)
  at 5555 ticks/s, which TienInspectWeapon's `xanim.read` skips (the clip reads as one frame); converting them is
  `mat4_to_srt(to_colmajor(m16))` per key, times x 4800 / 5555.
- Magazine behaviour as the P90's (attachments style, no magazine in the hand): `changeWeaponPart` "mag" at 0.15 of
  the unload (the left hand leaves the grip at frame ~7) and 0.85 of the load (it reaches the grip at frame ~38, with
  the load click). Baked forward rather than `m_AnimReverse` so those percentages count along the motion seen.
- Gunworks' magazine part spec has one item type, and `detachWeaponPartSpec` / `attachWeaponPartSpec` only take off
  / put on that type. The MP7 has three magazines, so Guns.lua wraps `ReloadAnim.handleWeaponPartAnimEvent` and
  `setWeaponAttachmentState` (looked up on the shared table at call time) to set the MP7 spec's `itemType` to
  `ReloadAnim.resolveReloadMagItem(action, handler)` first: the magazine being inserted (`action.magazine`), the one
  on the gun when the eject started (`_actualMagType`, Gunworks' AnimationsHooks), or the gun's saved MagazineType.

## P90 TR reference and model (from the user's photos, 2026-10-14)

The first P90 model (smooth, generic, one boxy opening) was rejected: "does not look like a P90 TR". The rebuild is
measured from the user's photos of a P90 TR (right side muzzle left, right side from ahead, left side from behind; a
licensed replica, serial 2509A0126 not reproduced). The right-side outline was traced on its white background (OpenCV,
Douglas-Peucker 1.5 px) into `scripts/post93/p90_reference_outline.json`, real mm with L = back from the muzzle tip and
H = up from the lowest point (500 mm = 1709 px). The gun is **181 mm tall** with the TR rail (an earlier eyeball
estimate said 214). Every profile in `build_p90.py` is written in those (L, H) coordinates:
- Muzzle: flash hider L 0-28.5 (r 10.4), knurled ring L 28.5-38.5 (r 11.7), collar to the receiver face at L 43; bore
  H 99.8. `canon` = L 43.
- Lower frame (polymer, one profile with two holes, half width 23.5, rounded edges): front hand stop L 43-63 down to H
  37, trigger loop to the bottom (H 0) with a finger tab at L 165-171, notch under the grip column at H 37 (L 173-188),
  belly flat at H 1 from L 255 to 300, slanting up to the butt. Trigger opening L 121-162, H 41-80 (trigger bar L
  148-169, H 46.5-53); thumbhole L 230-298, H 37-82. Seam under the receiver at H 93.
- Butt (half 27.5): L 352/369-500, H 22-140, butt plate seam L 489, mid seam H 93; FN monogram panel L 320-359, H 36-74
  on both sides; receiver band (polymer, half 25) L 205-356, H 84-118 with the raised "FN HERSTAL BELGIUM" panel L
  227-303, H 99-108 (right side only); magazine catch housing L 314-342, H 104-118; release tab L 344-360, H 119-134.
- TR metal upper (half 25.5, chamfered): receiver band L 42.5-205 from H 93, front column to L 78.5, rail block to H 176
  (front face slanting from L 42 at H 142 to L 60 at H 176), hoop arching down behind the magazine L 175-215; magazine
  window L 78.5-176 (H 118.5 up to the block's slanted underside H 142-155); slot L 164-197, H 163-171. Picatinny rail
  on top L 57-198, 14 crossbars from L 60.3 every 9.92 mm (photo; the standard is 10.0), top H 181. Side accessory
  bosses (T-shaped, hex screw) at L 71-95, H 150-172. Charging handles (bolt node, both sides) L 69-86.5, H 94.5-112,
  side tracks L 88-205, H 105.5-110.5.
- Magazine L 79.5-350.5, H 118.5-141.8, half 23: smoky brown body L 88-322 between grey end caps; rounds lie across it
  in two rows (H 124.5 / 135.5, pitch 9.6), tips seen on the right, case heads on the left.
- Origin = rear-top of the grip column, L 237 / H 80: game y = (237 - L) × 0.00072, z = (H - 80) × 0.00072 (bore z
  0.0143, muzzle y 0.1706, butt y -0.1894). The firing hand holds the column, thumb through the thumbhole.
- **Held like a pistol, so exported upside down.** Every GoM gun with `SwingAnim = Handgun` (pistols, MP5K, TEC9,
  MAC10; all `AttachmentType = Holster`, `WeaponReloadType = handgun`, `RunAnim = Run_Weapon2`, no TwoHandWeapon) is
  modelled turned 180° about the bore axis (game x → -x, z → -z: grip up, +X = the gun's right) around the same
  rear-top-of-grip origin; parts modelled upright sit at points with `rotate = -180 0 -180` (MP5K rail_up / scope),
  the muzzle keeps `-90 0 -180`, canon `0 0 0`, `world` = `-0.025 0 0` / `0 0 0` (MP5K, TEC9, MAC10). `build_p90.py`
  models and bakes upright and turns body + bolt at export (`turned()` for the points; `TURN`, `turned()` and
  `handgun_points()` live in build_mp7.py, which does the same for the MP7 since 2026-10-15); the magazine and part meshes
  stay upright. `render_p90.py` / `make_p90_art.py` turn everything back for display (`handgun_hold` in
  `p90_points.json` `_extras`). Its reload clips are made for the pistol stance (below). It stays
  `AttachmentType = Rifle` (vanilla's Back slot: locations "Rifle On Back" / "Rifle On Back with Bag", body points
  `rifle_back` / `rifle_back_bag`, shared/NPCs/AttachedLocations.lua); an attached item's own model attachment of the
  same name is applied too, so the P90's `rifle_back` / `rifle_back_bag` = `rotate -180 0 -180` hang it upright.
  Checked in game 2026-10-15 (MP7 and P90 hang upright and muzzle-down like a rifle). Engine (42.21
  `AnimatedModel$AnimatedModelInstanceRenderData.transformToParent`): parent bone · the body's attachment named by the
  location · the item model's attachment of that **same name** · mesh node transform; the item model is the weapon's
  `StaticModel`, else its `WeaponSprite` (`HandWeapon.getStaticModel`). So modded slots with their own location names
  (Plysken Attachments Reborn's per-bag `<Bag>_rifle` points) get no turn and show the upside-down model; left to
  Tien's Attachment Slots (user, 2026-10-15). An upright `StaticModel` would fix every slot but also changes the floor
  model (`WorldItemAtlas` uses it for weapons).
- Ejection port underneath L 262-296. Rails are cosmetic: optics / lights / lasers mount through the hidden
  `P90TR_Integrated_Rail_*` parts (Guns.lua), placed by `scope` / `rail_up` / `rail_*` / `light_left` / `laser_right`.
- GoM look: flat chamfered hard-surface parts (body 2,784 tris; GoM MP5 4,045, FAMAS 3,682), texture with flat
  panels, light AO and bright edges (GoM's black guns: texture median ~40 sRGB); the silhouette overlaps the traced
  outline by 98.7% (the preview's outline panel).
- Blender: a filled 2D curve with `extrude = half - bevel`, `bevel_depth = bevel`, `offset = -bevel` keeps the
  silhouette exactly on the drawn outline and cuts holes cleanly (how every profile with holes is built).
  `bmesh.from_mesh` appends to a non-empty bmesh but **not at the end of the index order**: find the new elements by
  set difference, never by index (doing it by index rotated earlier boxes into the wrong axes).

## FN Five-seveN (2026-10-16)

Guns of Marz names a Five-seveN (`"MarzGuns.FIVESEVEN": "5.7x28mm Five-SeveN"` in its ItemName.json) and ships
nothing else; the user chose to reuse that name ("let's reuse it, enable it in our mod and add missing stuff"), so the
Post-93 mod defines `item FIVESEVEN` in GoM's module (`scripts/GunsOfTienPost93/items_fiveseven.txt`, written by
`gen_post93_guns.py`) and GoM's translation names it; everything it uses is ours. If GoM ever ships its own
`item FIVESEVEN`, ours (loaded after GoM) replaces it whole, but GoM's Lua registrations for it would then meet our
parts. Features follow GoM's pistols ("match the features of what GoM has"); design table in docs/post93_design.md.
- **Reference**: a public-domain U.S. ATF side photo of an FNH USA Five-seveN, right side, muzzle right
  (commons.wikimedia.org/wiki/File:FN_Five_Seven.jpg, kept as docs/fiveseven_atf.jpg). Traced on its white background
  (flood fill from the border, Moore boundary, Douglas-Peucker 1.5 px; the scratch tracer was plain Python + numpy)
  into `scripts/post93/fiveseven_reference_outline.json`, scaled to FN's 208 mm (the photo's height then reads
  141 mm against FN's 137: lens or how FN measures). The trigger opening is cleaned by hand there (the trace ran round
  the trigger). Profiles in `build_fiveseven.py` are in that photo's (L, H) mm; silhouette overlap 96.0%.
- **GoM's pistol conventions** (measured on its Glock 17 / M92FS / USP, 2026-10-16): 0.72 scale (Glock 0.145 units
  = 202 mm), modelled upside down (+Z = bottom, +X = right), origin in the web of the grip under the beavertail
  (Glock: 12 mm behind its frame at that height, bore 47 mm above; ours L 197 / H 87, bore 45 above). Nodes
  `<GUN>_BODY` + `<GUN>_SLIDE`, the slide drawn through `MarzGuns.Slide_Lock` / `Slide_Fired` at points `slide_Lock`
  (absent: origin) / `slide_fired` (offset = slide travel: Glock 32 mm, ours 31) and swapped per shot by
  `Animations.RegisterWeaponWithAnimatedParts(gun, { SingleAttachment = { open = "MarzGuns.Slide_Fired", locked =
  "MarzGuns.Slide_Lock" }, cycleTicks = 5 })`. Magazine meshes sit in the gun's own space (the Glock has no
  `magazine` point, so `magazine magazine` draws them at the origin), floor pose `world` rotate 90 0 -90. Points:
  muzzle (-90 0 -180), world (-0.009 0.062 0, every pistol), rail_up (Beretta_Mount: 61 mm behind the muzzle, 11.4
  under the slide top), scope (pistol sights PL4 / PM2 / PS1: 13 mm behind and 24 mm above rail_up), underbarrel
  (lights / lasers PJ-3, PX1, TR-1, LP, TL: on the rail's underside), canon (= the muzzle, bore height); all rotate
  0 0 0, because GoM's pistol parts are modelled upside down too. Pistol sights need `Beretta_Mount` or `Colt_Mount`
  (GoM's AttachmentsRequiredParts.lua, per part, not per gun); spawn entries "part:chance:BM" fit the mount with the
  sight. No ReloadAnims entry (Gunworks' default handgun reload) and no RPM entry for GoM's semi-automatic pistols.
  Police pistols: `MarzGuns.Zombie_Police_Handgun_Spawner` (M92FS, Glock: gun, 4 magazines, 4 boxes),
  `Zombie_SWAT_Handgun_Spawner`.
- GoM's pistol `Muzzle_Mount_Device` model is about as big as its suppressors (r 0.0136 / 0.0157 x 0.082 units) and
  the M&P suppressor sits inside it. Ours: the P90's mount device (a 0.0089-radius sleeve, MountOn P90 + Five-seveN)
  is drawn at the Five-seveN's `canon` too (`ModelWeaponPart` picks the model per gun), with the Five-seveN's own
  `FIVESEVEN_Suppressor` (built by build_fiveseven.py in the gun's upside-down space, origin at `canon`; its collar,
  r 13.8 mm, covers the mount; CustomStats, RequiredAttachment on the shared mount, tooltip and suppressor spawner as
  the SP90's). Real world, as far as known: the SP90 fastens to the P90's own flash hider; Gemtech's can for the
  Five-seveN was a separate model (SFN-57) on a threaded barrel. Its size here (33 x 170 mm) is approximate.
  "Everything pistol-related" (user, 2026-10-16), matched by relation to GoM's items: on the Five-seveN the shared mount
  device item is drawn with the model `FIVESEVEN_Muzzle_Mount_Device` (the barrel's threaded end 15 mm out of the slide
  with a knurled adapter, inside the SFN-57's collar) instead of the P90's clamp; the SFN-57 weighs 0.8 (GoM's pistol
  cans 0.8-1.2 regardless of size; its P45, the same size, is 0.8) and its icon uses a camera fitted on GoM's
  M&P_Suppressor icon (`pistol_suppressor` in fiveseven_icon_cameras.json).
- **Weights follow GoM's (user, 2026-10-17: "use the GoM standard or values with our stuff too")**: suppressors
  0.8-1.2 whatever their size, matched by size (Rotex-II and SFN-57 0.8 as the P45, SP90 0.9 as the NDR), every mount
  device 0.5; magazines as GoM's (MP7 20 / 30 / 40 / 60 drum = 0.08 / 0.18 / 0.2 / 0.22 after the MP5's 20 / 30 / 60,
  P90 50 = 0.25 as GoM's 50-60 round pistol-calibre ones; pistol 20-round 0.05, the Five-seveN's extended 30 and the
  UCP's drum 0.2 as GoM's extended / drum pistol magazines); guns by GoM's weight against real (its SMGs ~0.78 of
  their kilograms: MP7 1.5, P90 2.0; its USP / M92FS ~1.0: Five-seveN 0.6, UCP 0.85).
- **Icons**: make_mp7_art.py's coarse camera grid fitted GoM's Glock icon to a twisted twin (error 110);
  `make_fiveseven_art.py` seeds the local search with side views (yaw 90 / 270, pitch 0 / 180, every 15 degrees of
  roll): Glock error 52, Glock magazine 29 (was 65). Cameras in `fiveseven_icon_cameras.json`.
- GoM bugs seen on the way (not ours to fix): its Glock magazine's script names icon `9x19Magazine17_GLOCK17` and
  texture `.../9x19Magazine17_GLOCK17`, but the files are `item_9x19Magazine17_GLOCK.png` and
  `9x19Magazine17_Glock.png`. The main mod's `sound_model.py` had no row for GoM's `GLOCK17`; added 2026-10-17 (4.49", 114 / 33).
- **Handedness of the review renders** (found 2026-10-16): the render scripts use game space as Blender world space,
  but game space is left-handed (+X = the gun's left with +Y forward and +Z up; Assimp MAKE_LEFT_HANDED), while
  Blender's own FBX import (world = raw x, -raw z, raw y: a mirror of game-as-world) shows the gun as authored and as
  the game shows it (vanilla text on world items is not mirrored in game). So every render_mp7 / render_p90 view is
  the mirror image of the game: a "right side" render has the muzzle on the left, and text painted to read right in
  those renders reads backwards in game. Seen directly: the P90 suppressor's "5.7X28" reads backwards in the
  Five-seveN sheet, which flips every render to the game's view. render_fiveseven.py / make_fiveseven_art.py do that
  flip; the Five-seveN's markings use the game's orientation (right side = -X upright, reads toward the muzzle,
  u = -L; left side u = +L). The MP7's and P90's painted text (`text_mask` with u = -L on the MP7's left, u = +L on
  the P90's right, the suppressors' calibre) read backwards in game: **fixed 2026-10-17** in build_mp7.py and
  build_p90.py (left side u = +L, right side u = -L, the suppressors' text along -y so it reads from the gun's left,
  the MP7 drum's "60" toward -X on its rear face), MP7 and P90 rebuilt. Which side each one-sided feature belongs on
  (the P90's "FN HERSTAL BELGIUM" panel, the MP7's markings) was not re-checked: the photos they were matched to are
  not in this repo and were labelled by the mirrored renders ("right side, muzzle left"); check in game against a
  photo before moving any. render_mp7 / render_p90 still do not flip their views (their sheets are mirrored).

## Gun tooltips (2026-10-18)

The user's screenshot showed raw keys in a gun's tooltip. 42.21 `HandWeapon.DoTooltip` adds one row per fitted part,
labelled `Tooltip_weapon_<PartType>`, then `WeaponPart.DoBatteryTooltip`: for a part tagged `base:usesbattery` (GoM's
weapon lights) a "Remaining:" row with a charge bar (`IGUI_invpanel_Remaining`, vanilla's): that row is the light's
battery, not a bug. GoM translates most part types; nobody translated `LaserRifle`, `LightRifle`,
`BayonetIntegrated`, `BayonetKnife`, `BoosterScope`, `Shellholder`, `UnderbarrelChamber`, `Animated1-9` (the M60's
visible belt rounds), so `gen_scripts.py` writes them into the main mod's Tooltip.json, and `gen_post93_guns.py`
writes `ForegripIntegrated` into Post-93's. GoM's own gun lines said only "Has Integrated Stock" / "Has Integrated
Bipod" (eight guns) and nothing for other guns with one; `scripts/gen_handling_tooltips.py` reads GoM's Stocks.lua,
Bipods.lua and AttachmentCustomStats.lua and writes `client/GunsOfTien/HandlingTooltips.lua`, one line per gun in the
wording of GoM's part tooltips ("Folding stock: deployed, Aiming Time reduced by 25%, Hit Chance increased by 15%.";
folding vs collapsible by the real gun), replacing the vague line or added after the others; the MP7s' lines in
Post-93's Tooltips.lua use the same wording. GoM registers no stats for the M4A1 and XM177 stocks or the M24 bipod, so
their lines say "no effect on handling".
Audit of every part with stats (user: "did we update tooltips that offer stats bonuses... but say nothing about
them?", 2026-10-18): sights, scopes, lasers, suppressors and muzzle devices matched their stats; missing were
Gunworks' spread modifiers (RPM.lua `RegisterSpreadPartModifier`: the AKS-74U / AS VAL / G36C stocks, GoM's three
foregrips, its bipod; our MP7A1 grip), the lights' script `AimingTimeModifier = 5` (vanilla adds a part's value to
the gun's), the foregrips' tool line, and the SPAS-12's pump / semi selector (a DA.RegisterPair of hidden Selector
parts: pump racks after every shot; semi Recoil Delay 15 from 30, Jam Chance 1.6 from 1). gen_handling_tooltips.py
now also writes those: spread in the stock / bipod lines, a "Mode selector" gun line, and PART_LINES added to a part's
own tooltip before its "Needs ..." line (stat lines without a full stop, as GoM's).
`scripts/check_gom_translations.py` (user: "scan all the tooltips GoM uses and add translation keys for EN") lists
every key GoM and Gunworks make the game look up (Lua getText literals, item names, item / recipe ToolTips,
IGUI_ItemCat_<DisplayCategory>, Tooltip_weapon_<PartType>, sandbox options) with no English anywhere (vanilla, GoM,
Gunworks, Ammo Maker, this repo) and exits 1 while any is missing; run it after a GoM / Gunworks update. Filled on
2026-10-18 (gen_scripts.py, main mod IG_UI.json): the break-action shotguns' barrel tooltips (only the
double-barrel's sawn-off barrels have stats), the Masterkey's (`Tooltip_Rail`), names for `Attack_Bayonet` (the
hidden weapon a fitted bayonet stabs with) and `frag_0-15` (explosion debris), `IGUI_ItemCat_Casings`, Gunworks'
`IGUI_ClickToRemove` and `IGUI_SelectAmmunition`. Deliberately left: GoM's ReloadAllMagazines_Compac.lua looks up
`ContextMenu_ReloadAllMagazines_*` only to remove another mod's options by their text. Fire mode labels are built
(`ContextMenu_FireMode_` .. mode) and all covered by vanilla (Auto / Burst / Single) and Gunworks (Real*).

## Lasers on a battery (2026-10-18)

User: "the laser attachments don't really emit lasers... put a battery in there to turn it on". Choices (user): dot
and a faint beam; the bonus only while on; 3x a weapon light's battery life; batteries changed the same way as GoM's
lights. Engine facts (42.21): GoM's lights are vanilla weapon lights (`ActivatedItem`, `TorchCone`, `UseDelta 0.001`,
tags `base:flashlight;base:usesbattery`); `HandWeapon.update` calls `update()` on every fitted part, and
`WeaponPart.update` spends one charge per 10 game minutes while the part is activated and switches it off at 0;
batteries go in and out only through vanilla's InsertBattery / RemoveBattery craft recipes on a loose part
(`RecipeCodeOnCreate.torchBatteryInsert` handles a WeaponPart), so a mounted light's battery cannot be changed and
neither can a laser's. `InventoryItem.save` writes the charge and the activated flag; `SyncHandWeaponFieldsPacket`
(server -> owner) replaces the client's fitted parts with the server's (full bytes) and its modData and sets aiming
time / hit chance / damage / range but **not** critical chance; client -> server it only carries ammo fields.
Design: `shared/GunsOfTien/Lasers.lua` (laser list, `DoParam` UseDelta 0.00033 + the lights' tags at
OnGameBoot / OnInitGlobalModData, GoM's laser modifiers in Gunworks' CustomStatsAttachments wrapped to apply only
while lit, `ISToggleLaserGoT` with the switch in the gun's modData `GunsOfTien_LaserOn`, set in `complete` and sent
with `CallSyncHandWeaponFields`; a laser still at the default single charge gets a full battery once, marked in its
modData); `server/GunsOfTien/Lasers.lua` drains every lit laser gun a player carries EveryTenMinutes (the part is
never activated, so the engine does not drain it too), switches it off at 0 and syncs it (re-equips a gun in hand
whose beam changed); `client/GunsOfTien/LaserMenu.lua` (Turn Laser On / Off in the gun's context menu and the firearm
radial, greyed with how to change the battery when empty; re-applies stats on the client when the lit state changes,
for the critical chance; a tooltip line on each laser part).
Look, second version (user's screenshot, 2026-10-18: "looks terrible. it's not even coming from the attachment
itself... fade into a certain short length... drop the red dot"): the first drew a dot and a beam to the first wall,
starting on the character's centre line; it ran parallel to the gun, so only the start was off. The engine knows
the muzzle (`IsoGameCharacter.getBallisticsController()`, public, returns a `BallisticsController` with public
`getMuzzlePosition()` / `getMuzzleDirection()` / `calculateMuzzlePosition`), but BallisticsController is not in
`LuaManager.Exposer`'s `setExposed` list (`@UsedFromLua` on its members is only a marker), so Lua cannot call it.
Now: a 0.3-tile glint, about the laser unit's own length (user: "really short"; 3 tiles first), in 4 segments
fading from alpha 0.8 to 0, no dot, stopped early by `isBlockedTo` or a character
within 0.3 tiles of the line, starting from `HOLDS[weapon:getSwingAnim()]` (tiles forward, tiles to the character's
right = (-dy, dx) of the facing, floor levels up). Rifle 0.49 / 0.12 / 0.47 was measured on that screenshot (the
beam's offset from the gun projected back with 1 level = 3 tile half-widths and the character ~0.75 level tall);
Handgun 0.58 / 0.05 / 0.5 is an estimate until a screenshot of a pistol-held gun. Then 0.3 tiles ("really short").
Third version (user: "how do you detect where the laser is?... so it can't be exact?"): no screen overlay can be
exact, so the beam became part of the gun. `scripts/make_laser_beam.py` (Blender) builds `GunsOfTien_LaserBeam.fbx`
(two crossed quads, 0.065 game units, about a laser unit's length; GoM's are 0.055-0.069) and `LaserBeam.png` (red,
premultiplied, alpha 1 to 0 along it: basicEffect.frag writes `Alpha * texture alpha`; no model shader is unlit, so it
is lit like the gun). `gen_scripts.py` `lasers()` writes one model per laser (`LaserBeam_<laser>`, its attachment named
like the gun's mount point, offset to the laser's lens: `LASER_LENS`, measured on front renders of GoM's
pointers.fbx with its textures) and one hidden part each (part type `LaserBeam`, FakeItem mount, CannotBeRemoved,
named "On": the gun tooltip shows "Laser Beam: On"). A part model's own attachment of the parent's name is applied
directly (`ModelInstanceRenderData.invertAttachmentSelfTransform` is a static flag, off). Lasers.lua fits / removes
the beam with the lit state (`UpdateBeam`), registers the beams with PreventRemovals, and adds each GoM gun in a
laser's MountOn a `ModelWeaponPart` line for its beam at load (`Item.DoParam("ModelWeaponPart = ...")` appends, even
for a part type already listed, so each script object is patched once); Post-93's guns list theirs in
items_guns.txt. GoM mounts its rifle lasers on `laser_right` (15 lines) and pistol lasers on `underbarrel` (7).
Checked: Blender renders of the M4A1 + AimRight, M92FS + PJ-3, MP7A1 + LRX-7 place the beam at the lens; Lua (lupa)
mocks: one line per GoM gun across two patch passes, beam on when lit, off when off / empty / the laser removed, a
slung gun drains and loses its beam without a re-equip. The overlay (`client/GunsOfTien/LaserDraw.lua`) and the lit
broadcast are gone.
Unlit (user: "our own light to the laser so that it's always [bright] without being affected by the lighting"): every
42.21 model shader is lit (`basicEffect.frag` multiplies by the lights + ambient; the vertex shaders do no lighting).
A model script's `shader = name` is any name (`ShaderManager.getOrCreateShader` creates it; file names are
case-sensitive), and `ShaderProgram` reads `media/shaders/<name>[_static][_instanced].vert` / `<name>[_instanced].frag`
through `ZomboidFileSystem.getString`, which finds mod files. `scripts/make_laser_shader.py` copies vanilla's
basicEffect shaders into the main mod as `gunsoftien_laser*` with the one lighting multiply removed from each
fragment shader (tint and alpha kept), and the beam models name it. Whether the engine finds it in the mod folder is
the first thing to check in game (a missing shader would leave the beam undrawn or logging errors; dropping the
`shader` line in gen_scripts.py goes back to the lit default).

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
- **Powder follows Ammo Maker's own pattern, for balance (user, 2026-10-15)**, not real charges (its "grains" are
  not real: 7.62x39 is 50): its 5.56 variants have subsonic `556x45SS` 35 (x0.7 of 50), overpressured `556x45OP` 70
  (x1.4), and HP / AP / TR the standard charge. Ours: subsonic x0.7 (7.62x39 US 35, 9x19 147gr 7, 4.6x30 10, 5.7
  SB193 8), +P+ x1.4 (9x19 14), .45 +P a milder x1.2 (19); hollow / soft points, steel core, SP-6, birdshot, SS197SR
  keep the standard charge.
- **Recipe books (checked 2026-10-15):** Ammo Maker gates only casings (`MakeCasings*` / `MakeHullsShotgun*`,
  `NeedToBeLearn = True`, taught by the "Ammo World" magazines May / April / March / February / January 93, one per
  casing shape, `magazineLearnedRecipes` in its recipeManager) and the reloading press parts (one manual). Round
  assembly (`Make<type>` / `Produce<type>`) and bullets / shot (`MakeBalls00`...) need no book; ours match
  (`NeedToBeLearn = False` everywhere), and each new type keeps its calibre's casing, so the casing gate applies.

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
  **Ours since 2026-10-15** (user: "MP7 and P90 just drop casings on the ground"): Hot Brass launches a casing from
  a point in front of the shooter (`doSpawnCasing`: forward / side in the facing, height above the feet; velocity
  from shellForce at `ejectAngle` off the facing, `heightSpread` / 200 up, plus `verticalForce`), never from the gun
  model. Pistol-held guns start where GoM's MP5K / TEC9 / MAC10 do (forward 0.55, side 0.06, height 0.53): the MP7
  uses those with shellForce 0.60 / sideSpread 50 / heightSpread {80, 100} / ejectAngle 80; the P90 falls from
  under the gun (forward 0.50, height 0.45, shellForce 0.15 forward, heightSpread {0, 10}, verticalForce -0.05,
  ~0.5 s) because -0.6 landed it almost at once. Flight at 60 fps (`stepCasing`: velZ -= 0.02, z += velZ x 0.05,
  xy += v x 0.1, drag 0.97 / 0.995): MP5K ~1.0 s and 1.8 tiles out.
- **GoM seems to plan 5.7 content** (ItemName keys `MarzGuns.57x28_Bullet/Box/Carton/Crate`, `MarzGuns.FIVESEVEN`;
  round, casing models and items for 4.6x30 and 5.7x28). Gunworks registers `swmg:bullet_57x28` with no item. Use our
  own module and ids, never `MarzGuns.` / `SWMG.` names.
