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
  `require=SWMG,GunsOfMarz`, `loadModAfter=HBVCEFb42,SWMG,GunsOfMarz,ammomaker` (Ammo Maker optional, see "Ammo
  Maker" below). Item module `GunsOfTien`,
  ammo type namespace `gunsoftien:`, sandbox page `GunsOfTien`.
- **`GoMExtensionGunsOfTienPost93`**: add-on for things that did not exist in July 1993 (the MP7A1, the P90 TR, their
  4.6x30 / 5.7x28 ammo). Requires the main mod too. Module `GunsOfTienPost93`, namespace `gunsoftienpost93:`.
  (The user typed "GoMExtensionGunsOfTIenPost93"; the id was written with a lowercase i, flagged to the user.)

The user (Tien, author of the other `~/Zomboid/Workshop/Tien*` mods) wants **realism, set in Kentucky, July 1993**,
and rich, consistent designs; decisions are taken with them, step by step. Hard dependencies on GoM and Gunworks
are fine; Ammo Maker became optional on 2026-10-24 (user: "Marz specifically requested to make Ammo Maker
optional... follow GoM's footsteps"), so treat it as GoM does: used when present, nothing breaks without it. Follow
the vision of GoM. Before building a feature, check
`~/Zomboid/Workshop/*` for one of the user's own mods that already does it (e.g. `RakeFeathersToo` already rakes
feathers and eggs; a duplicate was built into Zomboid Fixes by mistake and removed).

## Animations are generic, never per gun (rule, user, 2026-10-28)

Per-gun sets (the short SMG stance as Uzi / UziT / MP5K / MP7: 255 nodes and ~29 MB each) took 2-3 days of fixes
and multiply the work for every other mod that modifies animations. So:

- **No animation is made for one gun.** Before adding a stance, reload or rack animation, justify it with other real
  guns that move and handle nearly the same; otherwise fit the gun to an existing animation (model placement,
  orientation), not the animation to the gun. Small imperfections are accepted: some clipping, a hand a little off
  its place. No per-gun hold sets, no per-gun hand places.
- **Three kinds, chosen separately per gun:** a stance (the hold: idle, movement and everything else that is not
  aiming, reloading or racking), a magazine family and a rack family. A gun may take its magazine change from one
  family and its rack from another (the MP7: the pistol magazine change, the rear T-handle rack). Reload nodes are
  XML, so mixing families needs no new clips.
- Stances: vanilla's rifle; **short SMG** (one set: Uzi, Mini Uzi, MP7A1 / A2, GoM's MP5K; its aim is the approved
  aim with one shared left-hand place, the Uzi's); the H&K rifle-hand hold (UMP45, UMP9, GoM's MP5A3 / A2 / SD);
  **bullpup** (AUG, FAMAS; built 2026-10-28 as a tucked carry, section "Bullpup stance (built)": vanilla's rifle
  hold with the palm moved back "looked weird", the gun hanging back past the hip). Short SMG = held by the grip, no stock to the
  shoulder, about half a metre or less as carried: the MP5K is in, the MP5A3 / A2 / SD (550-680 mm, stocks
  shouldered) stay with the UMPs.
- A family has one clip set per stance it is used in: the pistol family is the Uzi's old stance reload on the short
  SMG stance (magazine into the grip, knob racked overhand, played from the stance, so no blend from a pistol pose)
  and `UziGrip` (vanilla's pistol clips) on the pistol stance (Micro Uzi; Mini Uzi and MP7s in one hand).
- Families decided: pistol magazine + pistol rack (Uzi, Mini Uzi: the top knob is racked like a slide; later the
  Micro Uzi and MAC-10 type guns); pistol magazine + rear T-handle rack (MP7; real kin: Steyr TMP 1992, B&T MP9
  2004, every AR's rack); H&K (MP5s, MP5K, UMPs); bullpup (AUG and FAMAS, one family); belt-fed (M249; M60, PKM, MG3
  handle alike). The P90's top-magazine reload is the one kept as is ("one of the weird guns"); a future M4 with
  that kind of magazine (an AR-57 type upper) would use it.
- **Built 2026-10-28 (not loaded in game yet): the short SMG stance holds its gun in the pistol orientation.** The
  stance's gun bone is the rifle relation turned half a turn about the gun's Y at its origin (`compact_pack.py`
  `turn_gun_bone` for `compact_animsets.PISTOL_SETS`), so a gun modelled for the pistol clips is drawn upright with
  its grip in the hand and no model point, the muzzle the game shoots from is the drawn muzzle, whatever its muzzle
  height, and one model serves both hands. This is exactly what the old upright turn plus per-set gun shift drew
  (checked: 2e-6 against UziT), with no per-gun numbers. Gone: `TURNED_SETS`, `turnUpright`, the UziT / MP5K / MP7
  sets (1,020 nodes, 28 packs), OneHand.lua's model swap (the `*_1H` model scripts stay for guns saved with them,
  identical now), Post-93's `MP7A1` one-hand reload (the MP7 uses the Micro's identical `UziGrip`).
  - Packs: `GunsOfTien_CompactShortSMG_Pack1-7.x` (main mod, 277 clips, 28.5 MB), made once by
    `scripts/anim/shortsmg_from_packs.py` from the 2026-10-27 packs (the per-gun builds lived in tmp/ on the Mac):
    the Uzi set's clips, and the reloads taken out under family names, each set's gun-bone move measured against
    vanilla's Bob_IdleAimRifle (MP5K 0.0890, MP7 0.0344) and undone first. Nodes: `compact_animsets.py ...
    ShortSMG` (255, reproduced the shipped Uzi nodes byte for byte before the rename) and `write_reload_nodes`
    (24: ids `ShortSMGPistol`, `ShortSMGHK`, `ShortSMGPistolRearT` with `clip_sets`). Grip animId
    `GunsOfTien_CompactShortSMG`; reload ids `GunsOfTienCompactShortSMG<Pistol|HK|PistolRearT>`.
  - The full Uzi re-exported in pistol orientation (`UZI_ONLY=1 blender ... build_uzi.py`: Uzi alone, a new UV
    layout and texture from this machine's bake; points turned, its rifle floor pose turned, MP7-style `rifle_back`
    / `rifle_back_bag` points turning it back upright on the back). Other mods' rifle locations (Plysken's) have no
    such point and would draw it upside down. smg_reload's `uzi_spec` keeps upright places and draws the mesh with
    `model_turn`; hold_preview turns it for rifle clips.
  - Outside the stance's nodes (climbing, hit reactions, actions...) vanilla's generic clips hold the gun in a third
    relation, matching neither rifles nor pistols (Bob_ClimbWindowStart, Bob_FallIdle): the short SMGs now look
    there as GoM's MP5K / MAC-10 do.
  "Compact SMG stance" below describes the per-gun build this replaced.
- Entering a reload: reload nodes live in `AnimSets/player/actions` (a sub-state layer over idle / aim, blended in
  over the node's `m_BlendTime`, ours 0.20 s), so there is no hard snap, but hands and gun cross-fade separately
  (the gun bone hangs from Bip01) and can part for a moment when the reload's first pose is far from the stance.
  A transition clip (`m_Transitions` with `m_AnimName`) cannot cover it: the engine (42.21
  `AdvancedAnimator.FindTransitionsFromProxy`) only plays one from a node going out to a node coming in, and the root
  idle node stays active under the reload layer. If the cross-fade looks bad, the fix is a lead-in and lead-out
  built into the clips of that (stance, family) pair, generic for every gun using them.

## Decisions taken with the user (main mod)

- **Writing in game texts** (user, 2026-10-19, both mods): tooltips, Information lines, sandbox and UI strings never
  join sentences with a semicolon (a full stop and a new sentence instead), and a colon only introduces a list
  ("Takes: ..."; "Does not pierce", not "Expands: never pierces"). A "Subject: Detail" line never ends with a full
  stop ("Compatible Muzzle Device: AR Muzzle Mount"; user, 2026-10-19), while a text that is a sentence always
  does, recipe tooltips included ("Assemble ... with reloading press.", "File the jacket off ... so the lead
  shows."; Ammo Maker writes its own without one); labels (recipe and menu names, part names, sandbox names and
  choices) and Information stat lines never do; GoM's own such lines lose theirs at run time (`dropAllSubjectStops` in client
  `GunsOfTien/Tooltips.lua`, at file load and on the first tick, so Post-93's count too). **Gun lines in GoM's attachment style** (user:
  "the way GoM lists the buffs and debuffs is better"): a heading per state ("Folding stock deployed:", "Folded:",
  "Pump action:", "Sawn-off stock:") and one effect per line ("Aiming Time reduced by 15%"), never one packed
  sentence; gen_handling_tooltips.py `line()` writes the stock / bipod / selector lines that way. **Compact, in
  GoM's own form** (user: "do not overexplain... stay true to GoM's format. we just needed to put the numbers there
  and fix some spellings and grammar"): one fact per line, stat lines without a full stop, GoM's own lines kept but
  spelt right; no explanations ("Does not pierce", not "Expands, so it never pierces"; "Needs racking every shot";
  bayonets "Attachable on compatible guns.", guns "Can attach a bayonet.", no stat lists where the game shows them).
  The break-action barrels' item tooltips (Tooltip.json) are one sentence ("Sawn-off barrels for the TOZ-34."); the
  sawn-off barrels' stats are Information lines in the attachment format, one effect per line (client
  `GunsOfTien/Tooltips.lua` `SAWN_BARRELS`; user, 2026-10-19, replacing the earlier one-sentence stat list). Long Information
  lines are wrapped by ZomboidFixesB42's GoM tooltip fix (`*_GoMTooltips.lua`), not by breaking them up here.

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
  (= GoM's ×0.3), and for the MP5SD no crack either (its ported barrel slows standard rounds below the speed of
  sound; added 2026-10-22 so it beats a plain MP5 with the Mk9, user). AS VAL 22 / 6 and MP5SD 25 / 6 (user, 2026-10-24, set over the model's 33 / 9 and 23 / 7: `OVERRIDE` in
  sound_model.py; the SD's so that the 147gr's ×0.7 gives 17 / 4); .45 guns quiet; short carbines louder; bolt / lever / shotgun volume
  180-250 → ~50-60. `scripts/sound_model.py` writes `shared/GunsOfTien/SoundTable.lua`; `Sounds.lua` applies it with
  the script setters at every `OnInitGlobalModData`. **Changed from Lua, not by redefining items**: a mod's `item X`
  block replaces GoM's whole item (user's correction), and Lua stays flexible with GoM updates. Call them "realistic",
  not "corrected". SoundGain (what players hear) is untouched.
- **Ammo Maker** (optional since 2026-10-24, as in GoM; the rounds then come from nowhere, like GoM's own special
  loads, see "Ammo Maker" below): every round craftable. Steel Core → Ammo Maker's `762x39AP`, SP-6 → `9x39AP`; the others
  get new types (copies of the calibre's base type) with Make / Produce placeholder recipes. New parts in Ammo Maker
  style: **soft point bullets** `GunsOfTien.BulletRifleSSP` / `BulletRifleMSP` ("Make Soft Point Bullet": standard
  Ammo Maker rifle bullet + Small File Set kept — the dum-dum method of filing the jacket off the nose) and
  **Birdshot Pellets** `GunsOfTien.Birdshot` (a 100-use pouch like Balls 00, 10 per shell; "Pour Birdshot Pellets" /
  "(Furnace)": same metal / crucible / tongs / charcoal as Ammo Maker's buckshot plus the unused vanilla
  `Base.Strainer` (kept) and 0.5 water — the shot-pan method; the user chose this over a mold). Each part has a box.
  Item display names follow Ammo Maker ("Bullet Rifle S SP", "Box Birdshot Pellets").
- **AWC Mk9 SMG suppressor** (user, 2026-10-22): GoM's 9mm cans (M&P, Shh9 on its Pistol mount) fit its pistols only,
  so 9mm SMGs got one: SMG cans only (user: "no pistol"), one 9x19mm SMG mount device for every gun, and only guns whose
  real barrel takes a can: GoM's MP5 and MP5A2 (three lugs) and Post-93's UMP9 (threaded); not the plain MP5K (flush end
  cap, only the MP5K-N had lugs / threads), the MP5SD (integral) or the TEC-9 (its pre-1994 threaded barrel would
  take one; the user left it out). The can is AWC's Mk9, 12" x 2", kept after the user found it huge (no shorter SMG
  can fitting both mounts is both documented and from before July 1993). Build notes: "AWC Mk9 SMG suppressor" below.
- **M249 Light Machine Gun** (user, 2026-10-22; building): the main mod's first gun (adopted 1982, so it is 1993
  material). The PIP gun ("M249E2", the user's word for it), its own 200-round box plus every GoM STANAG in one
  profile (STANAG jam x2), two Auto rates 750 / 1000 (the original gas regulator, the user's choice over the PIP's one
  rate), custom belt reload clips, no links, loot where GoM's M60 spawns, named "M249 Light Machine Gun". Design:
  docs/design.md 4d; build notes: "M249 Light Machine Gun" below.
- **Uzi, Mini Uzi, Micro Uzi** (user, 2026-10-23; building): IMI's 9mm family, main mod (1954 / 1980 / 1986). The Uzi
  held as a rifle, the Mini and Micro **like a pistol and holstered** (GoM's MP5K / MAC-10 way, the user's choice
  over a rifle-held Mini), the Micro also in an ankle holster (user, 2026-10-23: AttachmentType HolsterSmall as GoM's
  Detective .38; every vanilla slot that takes Holster takes HolsterSmall too); a Micro Uzi, not the Uzi Pistol of the user's sixth photo (that photo serves its
  receiver); 20 / 25 / 32 plus 40 / 50 magazines shared by all three; the AWC Mk9 on its SMG mount device on all three.
  Design: docs/design.md 4f; build notes: "Uzi family" below.
- **Steyr AUG A1** (user, 2026-10-27; built): main mod (1977; the AUG/SA was imported to the US until 1989). Steyr
  green, held as a rifle like GoM's FAMAS, its own 30 / 42 magazines (no STANAG), the integral 1.5x scope as a hidden
  required part, the folding front grip as Post-93's MP7A1's (the fold code moved to the main mod for both), no
  muzzle parts, rails or bayonet (user's choice), the bullpup animation set it shares with GoM's FAMAS (hold and
  reloads, section "Bullpup set"), loot in GoM's import rifle spawner.
  Design: docs/design.md 4g; build notes: "Steyr AUG A1" below.
- **Loot: none** (user, 2026-10-17: "GoM doesn't allow you to loot specialized ammunition... do not add them, as well
  as our mod's"): GoM spawns only each calibre's standard box (plus the 12 ga slug beside buckshot and the 40 mm
  grenades); its 5.56 Hollow Point / Armor Piercing / Subsonic / Overpressured never spawn. All 12 of this mod's rounds
  are such special loads, so the main mod has no ammunition loot (its old `server/GunsOfTien/Loot.lua`, boxes beside
  vanilla boxes plus GoM spawner bonus groups, was deleted); they come from Ammo Maker. The Mk9 and its mount device
  are parts, not ammunition, and join GoM's suppressor and muzzle device spawners (a new `server/GunsOfTien/Loot.lua`,
  2026-10-22, as Post-93's parts). GoM also spawns its mount devices in place of vanilla's Improved Choke Tube
  (`VanillaReplacerTable.VanillaAttachmentMap["Base.ChokeTubeImproved"]`, read by `VanillaReplacer.lua` while its
  sandbox `VanillaAttachmentReplacement` is on; "Base.ChokeTubeFull" gives its compensator / flash hider / brake),
  so every mount device of ours joins that list too (main mod's SMG mount, Post-93's MP7 / P90 / SCAR-H mounts, the
  latter missed until 2026-10-22). Ammo Maker still spawns this mod's
  bullet / pellet parts itself, as it does every active part. No loot multiplier of our own (removed 2026-10-17,
  user: "if GoM has it, use their option"): the Post-93 loot follows GoM's `MarzGuns.LootMultiplier` ("GoM Loot
  Multiplier"; it scales GoM's spawner placements, and Loot.lua scales our own entries by it). Removing
  `GunsOfTien.AmmoLootMultiplier` only drops that key from servers' saved sandbox files. **Sandbox options left**:
  `RealisticPiercing`,
  `SubsonicRackRule` (1 always / 2 unless PBS-1 (default) / 3 never). `RescaleGuns` ("[BETA] Resize Guns of Marz",
  `GunScale.lua`) was removed on 2026-10-26 (user: "remove that option for now"); a server that had it keeps no
  value (its data and where the code is kept: `docs/gom_gun_scale.md`).
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
  (polymer tip, ×1.15, no pierce). Subsonic: 4.6x30 ×0.6 dmg, SB193 ×0.7, both sound ×0.7 (the 147gr 9mm's; ×0.5 until
  2026-10-24, user: a suppressed MP7 was quieter than the MP5SD), no pierce. Ammo Maker types `46x30` / `57x28`
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
  (+ magazine + box) by direct entries in the two late zombie bags at the 2/n and 1/n each Anachronistic gun gets there
  (Loot.lua `DIRECT`; n counted at run time, 7 = GoM's 5 + MP7 + P90).
- **SCAR loot** (2026-10-20): military, the MP7's way: an alternative each in GoM's `World_Army_Rifle_Spawner` and
  `Zombie_Army_Rifle_Spawner` (see docs/post93_design.md). GoM spawners resolve through Gunworks' `ItemSpawnCore`: an
  alternative picked evenly, each later group rolls 0..amountChance items. GoM's spawners also arm zombies
  (`AttachedWeaponDefinitions.lua`: police / SWAT holsters, SWAT and army back slots), so a gun inside one reaches
  zombies too; a spawner item of our own (any `item` with `OnCreate = MarzGuns_OnCreate.SelectItem` plus an entry in
  GoM's `ItemSpawnerMap`) would have to be wired into those lists as well.
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
- **FN SCAR-L and SCAR-H** (user, 2026-10-20): Mk 16 STD and Mk 17 LB (20" barrel, chosen over the TPRS of the
  user's photo) in FDE, select fire, standard side-folding stock; the SCAR-L on GoM's 5.56 family and STANAG
  magazines, the SCAR-H on its 7.62x51 family with its own 20 / 10-round magazines and its own SOCOM762-RC suppressor +
  mount device (GoM has no 7.62x51 can). Design: docs/post93_design.md; build notes: "FN SCAR-L and SCAR-H" below.
- **H&K UMP45 and UMP9** (user, 2026-10-22; built): two guns on one shared model, no calibre conversion recipe and no
  UMP40 (no .40 S&W round in GoM / Gunworks, and the user chose not to add one); the .45 hits harder than GoM's MP5,
  UMP45 magazines 10 / 20 / 25, Auto / two-round Burst / Single, GoM's MP5 reload clips (replaced 2026-10-26 by
  their own, after the resize: smg_reload.py `ump`, packed with rifle_hand.py's UMP set, nodes
  *GunsOfTienCompactUMP_GoT.xml, "attachments" style with the magazine in the hand), the UMP45 GoM's .45 mount device
  + P45 suppressor as its MAC-10 (user, same day, replacing "no suppressor"), the UMP9 the main mod's 9x19mm SMG mount
  device + AWC Mk9 (GoM's 9mm cans fit its pistols only),
  loot the MP7 / P90 route, magazines on found guns by GoM's MP5 rule. Design: docs/post93_design.md; build notes:
  "H&K UMP45 and UMP9" below.
- Other post-1993 ideas offered but not chosen: 5.56 Mk 262 / M855A1, 5.45 7N22, 7.62x51 M993, 9x39 PAB-9, modern
  9mm HST, 12 ga Flite Control; .300 Blackout would need a new gun.

## File map

- **No `x_extends` in AnimSets** (2026-10-24, Linux report): the game lower-cases an `x_extends` path and fails to
  open it on a case-sensitive file system (ZomboidFixesB42 CLAUDE.md, "Item and recipe scripts"). Every node that
  extended another (Uzi grip unload / rack, M249 aim rack; Post-93 MP7A1 / P90TR unload / rack, P90TR aim rack) is
  written out in full, merged as `PZXmlUtil.resolve` does (an empty `<m_Conditions />` keeps the parent's n-th, an
  extra one is appended after the parent's children), with a header comment saying so; `compact_animsets.py`
  already flattens the same way. Write new nodes in full. "Marz Mods Animsets for Linux" (workshop 3774316897,
  id `Linux_Animsets_Marz_Mods`, no `loadModAfter`) covers only GoM's own `_HB` files, as lowercase copies dated
  2026-08-17, i.e. from before GoM's 2026-10-23 id renames (its `loadfal_hb.xml` answers `"FAL"`, plays
  `Bob_Reload_Rifle_Load`, no InsertMag). The game keys AnimSet files by lowercased path (`resolveFileOrGUID` →
  `activeFileMap`, last mod loaded wins, logged `mod "X" overrides media/animsets/...`), so on a server listing it
  after GunsOfMarz it replaces GoM's current nodes, GoM's own guns included. So never borrow GoM's animId for a gun
  of ours: copy its nodes under an id of our own (the SCAR-H, 2026-10-27).
- Descriptions (2026-10-24, as in ZomboidFixesB42): `README.md`, `forum.txt` (the pinned Discussions thread, one
  post: every feature and the sandbox options) and the `mod.info` descriptions list the features; keep them in
  step. `workshop.txt` only has the requirements, a short intro and a pointer to that thread (Steam caps the
  Workshop description at 8000 characters; a longer one fails the in-game upload).
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
  yet) and `scripts/make_workshop_art.py [preview preview2 preview3 preview4 preview5 posters icons]`. preview4
  (2026-10-18) is the MP7A2 alone, from render_ad_guns.py's `mp7a2` (fitted out without a light, so the handguard's side
  rail shows), mirrored to the game's view like the pistols. preview2-5 are added on the Steam page by hand (all four
  there since 2026-10-19); only preview.png goes up with the in-game upload.
  preview5 (2026-10-19, user: "I want the three to be included but the main features would just use the double barrel
  model") is the sawn-off shotguns: GoM's Double Barrel whole and sawn off (render_ad_guns.py `db_full` / `db_sawn`,
  one scale, lined up on the receiver, mirrored back), then one slot row of the six offcuts under the three guns'
  names. Only what this mod adds is shown, and the captions carry no pronouns (user: "remove the pronouns. just add
  the what we add"; GoM's gun and sawn-off barrel icons were dropped). DIN Alternate Bold (the Mac's stand-in for Bahnschrift) has no "·": `text_layer`
  draws a dot by hand where the font lacks the glyph.
  preview6 (2026-10-20) is the SCAR-L and SCAR-H: render_ad_guns.py `scarl` / `scarh` (rifles, upright: spec
  `rifle`, nothing turned; a side-on view so the two stack with their names above them), no big title (user: only
  the add-on line on top, the guns' names carry the page), one scale, lined up on the
  butt, fitted out with GoM's sights, foregrip, bipod and muzzle parts, then one slot row of what the add-on adds
  besides the guns (the SCAR-H's magazines, drum, suppressor, mount device) and two text lines; added on the Steam
  page by hand like preview2-5.
  preview7 (2026-10-22) is the UMP45 and UMP9, laid out like preview6: render_ad_guns.py `ump45` / `ump9` (one body
  file, each gun's texture; the view shows the right side after the mirror, so the UMP45 carries GoM's laser rather
  than a light on the hidden left rail), one scale, staggered, each under its name and calibre, then one slot row (each
  gun and its magazines) and one line (the rails line was removed, user 2026-10-22). Added on the Steam page by hand like the others.
  preview8 (2026-10-22, user: "introduce the two suppressors we added") is "NEW SUPPRESSORS": the AWC Mk9 on GoM's MP5
  and on the UMP9, GoM's P45 on the UMP45 (render_ad_guns.py `mp5_mk9` (spec `gom_smg`: GoM's own MP5 meshes, its
  30-round magazine, our mount and can at the measured `canon`; `mp5a2_mk9` is there too, unused), `ump9_mk9` (spec
  key `main_parts`), `ump45_p45`), one view and scale, staggered, each under its name and its can, then a slot row
  (Mk9, our mount, GoM's P45 and .45 mount); the can is named "P45" alone and the two lines under the row were
  removed (user, 2026-10-22). Added on the Steam page by hand.
  preview9 (2026-10-22) is the M249 and belt links: render_ad_guns.py `m249` (body, closed cover, deployed bipod,
  box and belt, seen from its left after the mirror), title "M249 LIGHT MACHINE GUN", then one slot row (the gun,
  its box, the M27 and M13 links and their boxes), then two lines at the bottom: "LMG BELTS NOW NEED LINKS" and what
  that means (M249 and GoM's M60, one link per round loaded, fired links eject; user 2026-10-22). Not yet on the Steam page.
  preview10 (2026-10-23) is the Uzi, Mini Uzi and Micro Uzi: render_ad_guns.py `uzi` / `miniuzi` / `microuzi` (one
  view and scale, so their real sizes show; the Uzi and Micro stock folded, the Mini deployed; standard magazines;
  the M249's view, the gun's left after the mirror), title "UZI · MINI UZI · MICRO UZI", staggered with name and rate
  of fire, then a slot row (the three guns, the five magazines) and one line (the Mk9 fits all three). Rebuild:
  `blender -b --factory-startup -P scripts/render_ad_guns.py -- <absolute path>/tmp/ad uzi miniuzi microuzi` (a
  relative OUT_DIR lands under C:\ on Windows), then `py scripts/make_workshop_art.py preview10`. Not yet on the Steam page.
- Generators (run with python3 from the repo root; never hand-edit their outputs): `scripts/gen_scripts.py` (main mod
  items / models / recipes / names), `scripts/sound_model.py` (→ SoundTable.lua), `scripts/gen_handling_tooltips.py`
  (→ HandlingTooltips.lua: GoM's stock / bipod / selector / part / gun line fixes), `scripts/gen_round_tooltips.py`
  (→ RoundTooltips.lua: every round's lines from the profiles), `scripts/make_art.py`,
  `scripts/make_ammomaker_art.py`, `scripts/post93/gen_post93_ammo.py`, `scripts/post93/make_ammo_art.py`,
  `scripts/post93/gen_post93_guns.py` (needs `scripts/post93/mp7_points.json` / `p90_points.json` /
  `fiveseven_points.json` / `ucp_points.json` / `scarl_points.json` / `scarh_points.json` / `ump_points.json`),
  `scripts/check_refs.py` (every item / model / icon / mesh / texture / AnimSet clip name in both mods resolves
  against them, GoM, Gunworks, Ammo Maker, Hot Brass and vanilla, version and common folders),
  `scripts/scale_audit.py` + `scale_audit_report.py` (every gun's drawn size against its real one, "Gun scale"), and the model
  builders `scripts/post93/build_mp7.py`, `build_p90.py`, `build_fiveseven.py`, `build_ucp.py` (the others import
  build_mp7 as their library), their review renders `render_mp7.py` / `render_p90.py` / `render_fiveseven.py` /
  `render_ucp.py` (Blender) and sheets + icons `make_mp7_art.py` / `make_p90_art.py` / `make_fiveseven_art.py` /
  `make_ucp_art.py` (Pillow), and the same three for the SCARs (`build_scar.py`...) and the UMPs (`build_ump.py`,
  `render_ump.py`, `make_ump_art.py`); `trace_outline.py` traces a reference photo's outline. Main mod meshes:
  `scripts/build_sawn_stocks.py` (Blender: the stockless break-action bodies and the stock / barrel offcuts, from
  GoM's own FBX files; writes `scripts/sawn_offcuts.json`, read by gen_scripts.py), then `scripts/make_offcut_art.py`
  (Pillow: the offcut icons, cameras in `offcut_icon_cameras.json`, sheet `docs/sawn_offcuts_preview.png`);
  `scripts/build_mk9.py` (Blender: the Mk9 and its mount device with the Post-93 kit, and GoM's MP5 / MP5A2 `canon`
  measured into `scripts/smg9_points.json`), then `scripts/make_mk9_art.py` (their icons); `scripts/build_m249.py`,
  `render_m249.py`, `make_m249_art.py` (the M249, section "M249 Light Machine Gun"); `scripts/build_uzi.py`,
  `render_uzi.py`, `make_uzi_art.py` (the Uzis, section "Uzi family"); `scripts/build_aug.py`, `render_aug.py`,
  `make_aug_art.py` (the AUG A1, section "Steyr AUG A1"); `scripts/make_foregrip_radial.py` (the Fold / Unfold
  Foregrip radial icons, moved from post93/ on 2026-10-27).

## Status and how to continue

See `TODO.md` (open work only; built features are taken as working once played). In short: both mods' code is written and syntax-checked; the Workshop item was last uploaded
2026-10-19 (with the sawn-off stocks, offcuts and sawn-off barrel stats), but nothing has been loaded in game. The Post-93
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
The unaimed rack (2026-10-26, user: "make it slower, or at least make it go back the same as when the right hand goes
back"): from the let-go (frame 26) the left arm and the gun go back together over frames 26-36, the arm's bones blended
from the let-go pose to the pistol idle's hanging arm with a smoothstep (`settle_left_arm`); the hand peaks at 3.6 cm a
frame (it used to drop to the side in 4 frames, 26-30, up to 10, then the gun came home in 6). It cannot be solved
onto the handle meanwhile: the gun coming home takes the handle out of reach and the rig flips the elbow (the build's
out-of-reach / elbow lines for that clip are about the replaced frames). The aimed rack is unchanged.
**Reloads must end on their idle's whole hold** (found 2026-10-26, the user on the P90 rack GIF's last frame: "the
P90 IS REVERSED"): a rig `Key` with `top=None` carries the previous key's top, so the P90 rack's last key (gun home,
`face` given) kept the racking place's top (up) and ended rolled half a turn about the barrel, top to the back, while
vanilla's pistol idle has it to the front: the node then blended into the idle with a half-turn snap (since
2026-10-15). The M249's reloads had the same `top=None` and ended 11 degrees off vanilla's rifle idle. Both now give
`top=rot_of(r.weapon0) @ Vector((0, 0, r.top_sign))`, as smg_reload.py's `idle` does; every reload of ours now starts
and ends exactly on its idle (0.0 degrees, 0.0 cm; scratch check: the gun against the chest at the clip's first /
last frame and the idle's frame 0).
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
required at spawn. (Since 2026-10-27 the fold code below lives in the main mod, `shared/GunsOfTien/Foregrip.lua` with
`Foregrip.Register(gun, { folded, deployed, foldDesc, unfoldDesc })` and `client/GunsOfTien/ForegripMenu.lua`, icons
`ui/GunsOfTien_Radial_*Foregrip.png`, for the AUG A1 too; Post-93's Foregrip.lua only registers the MP7A1: a second
copy would have redefined the global `ISFoldForegripGoT` bound to one mod's gun list.) The fitted part is the state:
`shared/GunsOfTienPost93/Foregrip.lua` swaps them with Gunworks'
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

## MP7A1 reload (2026-10-15; removed 2026-10-26)

Removed on 2026-10-26 (the MP7s play the compact stance's reloads; nothing played these): the six `*MP7A1_GoT.xml`,
`Bob_GunsOfTien_MP7_Unload.x` and `scripts/post93/anim/mp7_reload.py` (in git history). What they were: the MP7's
magazine goes up into the pistol grip, so it reloads like vanilla's pistols: AnimSets `*MP7A1_GoT.xml`
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

## FN SCAR-L and SCAR-H (2026-10-20)

- Builder `scripts/post93/build_scar.py` (both guns, the shared stock, the SCAR-H's magazines and muzzle parts; the
  MP7 kit's slab / lathe / picatinny / bake helpers, with `kit.K` and `kit.MATS` replaced), review renders
  `render_scar.py` (Blender, its own copy of render_ucp.py's helpers: importing render_ucp runs its main()), icons
  and sheet `make_scar_art.py --renders DIR` (`docs/post93_scar_preview.png`). Rebuild: `blender -b --factory-startup
  -P scripts/post93/build_scar.py` (~1 min at the default 1024 bake), `render_scar.py -- DIR`, `make_scar_art.py
  --renders DIR`, then `gen_post93_guns.py` and `check_refs.py`.
- **Rifles at 0.65 of real size** (`K = 0.00065`), not the 0.72 of the MP7 / P90 / pistols: GoM draws its rifles at
  0.61-0.67 (M4A1 0.63, G36 0.61, FAL 0.67 of their real overall lengths), its SMGs and pistols at ~0.72. At 0.65
  GoM's own STANAG magazine mesh matches the replica photo's magazine within 2 mm (depth and length), so the SCAR-L
  just hangs GoM's STANAGs at its `magazine` point (feed lips, photo L 363, H 163).
- **Photo scale from the rails**: both photos scaled by their Picatinny crossbar pitch (MIL-STD-1913, 10.0 mm), found
  by autocorrelating the top edge's row profile along the rail (SCAR-H 18.14 px / 10 mm, SCAR-L 14.90). The SCAR-H
  then measures 1031.5 mm (TPR 20": 1040-1085 published), the SCAR-L replica 789 mm (real CQC ~787 extended).
  The replica photo is turned ~0.66 degrees (rails slope 4.6 mm over 400 mm): `fix_l()` straightens every SCAR-L
  point (H += 0.0115 x (L - 300)) and make_scar_art.py does the same to the traced outline. Silhouette IoU against the
  traced outlines (from the receiver's front; the SCAR-H to just behind the grip, as its photo has the TPRS stock):
  SCAR-L 94.1 %, SCAR-H 95.2 %, the rest being the folded rear sights, the untraced trigger opening and the
  SCAR-L's lengthened barrel (+97 mm ahead of the gas block, CQC 10" to STD 13.8").
- **One stock node for two guns, folded by a rotation**: `SCAR_STOCK` (in the parts FBX, its own 128 texture) is
  modelled deployed with its origin at the hinge (its front face on the bore axis); each gun's `stock` point puts it
  there, and `stock_folded` = the same offset + 2 x the hinge pin's x (on the right, -X) with rotate (0, 0, 180): a
  half turn about Z through the pin (the engine draws a part at offset + rotateXYZ . vertex), so the stock lies
  along the right side, butt forward, as FN's does. GoM instead ships two stock meshes (G36_STOCK_FOLDED /
  _DEPLOYED) or slides one (M4A1 `stock_folded` offset only).
- GoM's bipods (`Bipod_Deployed / _Folded`, a `DA.RegisterPair`) mount on its M4A1 / G36 / FAL... through
  `Picatinny_Rail_Down` (or the G36C's rail) at a `bipod` point 0.0006 under the rail's bottom (its FAL); both SCARs
  take them on their integral bottom rail. GoM's M4A1 has no reload animation entry (Gunworks' default rifle reload);
  its FAL uses `animId = "fal_rifle"` ("FAL" before GoM's 2026-10-23 update; the SCAR-H kept the old id until
  2026-10-27, so its insert matched no node, played a hand raise and never seated the magazine), AA12 / BAR
  `"left_handle_load"`. The SCAR-H now has its own copies of GoM's FAL nodes (`GunsOfTienSCARH`, AnimSets
  `*GunsOfTienSCARH_GoT.xml`, GoM's clips), as an outdated Linux animsets mod can replace GoM's (see "No
  `x_extends`"). GoM's STANAG magazines are one Gunworks magazine profile, "STANAG".
- GoM's FAL magazine icon is blue-grey: the light fitted on it (gains up to 1.9 on blue) washed the tan SCAR-H
  magazines out, so their icons use that camera with the MP7's magazine light (fitted on GoM's MP5 magazine).
- Not in the photos and drawn from FN's layout: the right side (ejection port, ambidextrous selector), the charging
  handle on the left (reversible on the real gun; the SCAR-H photo has it left), the stock's position marks and latch.
- SCAR-H suppressor in real life (searched 2026-10-20): FN made none for the SCAR, and no source ties a can to the
  Mk 17. SureFire's FA762SS (first pick, from memory) is the Marines' M40A5 can; its SOCOM762-RC is the 7.62 can
  USSOCOM adopted (2017 Family of Muzzle Brake Suppressors, sources tie it to the Mk 13): the user chose that one.
- SCAR-H magazines in real life: FN only made 10 and 20 rounds. The 50-round drum (user, 2026-10-20) is ProMag's
  DRM-A41 for the SCAR 17S, modelled as a single drum facing front and back (its axis along the barrel, like the
  MP7's; the user corrected a first build facing the sides), winding knob on the front face; its icon uses the MP7 drum's camera with the MP7 magazine light (the drum light washed it out too).

## H&K UMP45 and UMP9 (2026-10-22)

- Builder `scripts/post93/build_ump.py` (one body and charging handle for both guns, the shared stock, the four
  magazines; the MP7 kit's slab / lathe / picatinny / bake helpers, `kit.K` 0.00072 and `kit.MATS` replaced), review
  renders `render_ump.py`, icons and sheet `make_ump_art.py --renders DIR` (`docs/post93_ump_preview.png`). Rebuild:
  `blender -b --factory-startup -P scripts/post93/build_ump.py` (~2 min at the default 1024 bake), `render_ump.py --
  DIR`, `make_ump_art.py --renders DIR`, then `gen_post93_guns.py` and `check_refs.py`. On the Mac, Python has no numpy:
  `pip3 install --target <scratch>/py numpy` and `PYTHONPATH` it for trace_outline.py / make_*_art.py (`python3 -I`
  ignores PYTHONPATH and user site packages, so run them without it).
- **Both guns are one mesh** (`UMP_BODY`, `UMP_BOLT` in `GunsOfTienPost93_UMP.fbx`, `UMP_STOCK` in the parts file) and
  one `ump_points.json`; the bake is done once and painted twice (`UMP9.png`, `UMP45.png`: only the markings differ),
  and the model scripts `UMP9` / `UMP45` point at the same node with their own texture. `UMP_BOLT`'s model uses
  `UMP9.png` (its texels are the same in both).
- **Photo scale from the rail**: H&K's UMP9 photo (1280 px) measured 18.13 px per 10 mm crossbar on its top rail
  (autocorrelation of the top edge's row profile over L 212-355, as for the SCARs), giving 695 mm with the stock
  deployed against H&K's published 690. The second reference, a third-party render of a UMP .45 (right side), has
  rail crossbars 36 px apart, which would make the gun 501 mm long: its proportions are an artist's and were used only
  for where the right-side features are (stock hinge, ejection port).
- The UMP9's curved 30-round magazine was fitted to the photo's front and rear edges (grid search: top at L 234 /
  H 192, rake 16 degrees under the receiver curving to 36 at its base, 42 mm deep, within 1 mm RMS); the .45
  magazines are straight at 18 degrees, 44 mm deep, with no published drawing. `mag_local()` maps texels back to (along
  the axis, across it) for both shapes.
- Review renders: Workbench's specular highlight lifted the black polymer so that painted dark details (port, slots)
  vanished (body 44 and port 15 sRGB both rendered ~65); `render_ump.py` turns `show_specular_highlight` off. The
  tan SCARs never showed it.
- `canon` (UMP45 only uses it) = the barrel collar's front face, `CANON_L` 21.5 mm behind the muzzle (0.0155 units;
  GoM's MAC-10 has its canon 0.0173 behind its muzzle, its M1911 0.0034). GoM's `Muzzle_Mount_Device` model runs from
  its origin to +0.0824 (r up to 0.0157), `P45_Suppressor` to +0.1303 (r 0.0137), both along +Y from canon; checked in
  a review render (render_ad_guns.py specs with GoM's two parts at canon). Added to ump_points.json by hand with the
  value build_ump.py now writes, so the FBX was not rebuilt.
- Since the 2026-10-26 resize (K 0.000603) the UMP45 draws GoM's P45 and `Muzzle_Mount_Device` at GoM's size, ~19%
  large for the gun (the UMP9's Mk9 goes through `_GoT` models); the SCAR-L's MKI is ~3-5% large. Both left as they
  are (user, 2026-10-27: "no change").
- Not in the photo and drawn from H&K's layout: the right side's ejection port over the magazine well, the stock's
  hinge knuckles on the receiver's right rear (the stock folds about them to the right, `stock_folded` as the SCARs'),
  the selector's two-round burst mark, the calibre markings.

## AWC Mk9 SMG suppressor (2026-10-22)

- Files: `scripts/build_mk9.py` (~20 s; `GunsOfTien_SMG9_parts.fbx` with `Mk9_Suppressor` and
  `SMG9_Muzzle_Mount_Device`, 128 px textures in `textures/weapons/GunsOfTien/`, `scripts/smg9_points.json`),
  `scripts/make_mk9_art.py` (icons, the MP7's suppressor / mount cameras), `gen_scripts.py smg_suppressor()`
  (`items_suppressors.txt`, `models_suppressors.txt`, names), `shared/GunsOfTien/Suppressors.lua` (stats, mount rule,
  GoM's guns' point and lines), `server/GunsOfTien/Loot.lua`, the tooltip lines in `client/GunsOfTien/Tooltips.lua`;
  Post-93 adds the UMP9 (`appendMountOn` in Guns.lua, its own ModelWeaponPart lines from gen_post93_guns.py, its
  tooltip line). Display names "Mk9 Suppressor (9mm SMGs)" and "9x19mm SMG Family Muzzle Mounting Device" (GoM's
  pattern); weights 1.2 / 0.5 (GoM's biggest cans / every mount); stats GoM's 9mm cans' (sound ×0.3, damage ×0.9, no
  flash) plus Aiming Time ×1.1 (GoM's deployed bipod / LR4X: 24 oz on a 12" tube at the muzzle).
- **The MP5SD stays the better quiet gun** (user, 2026-10-22: "make it so that MP5SD is better than the MP5 with
  silencer option"): before, the MP5 + Mk9 was 28 / 8 against the SD's 33 / 9 and hit harder (0.9-1.44 against
  0.8-1.3), so the SD lost on everything but weight. Now sound_model.py drops the SD's supersonic crack (ported barrel,
  -5 dB: 23 / 7; an add-on can on a plain MP5 keeps the crack), and the Mk9 slows aiming ×1.1. The SD: quieter,
  2.1 against 2.0 + 1.2 + 0.5, quicker to bring up; the suppressed MP5: harder hits, 30 against 25 range (the SD's
  slower bullets, as GoM has them). With the 147gr subsonic round (sound ×0.7 on both) the order stays. The earlier
  "MP5SD subsonic rule" the user dropped (2026-10-14) is another thing: rounds fired from the SD treated as subsonic
  ammo (damage too); only its sound changed here. GoM's SD damage (0.8-1.3, ×0.8 of the MP5) already is the slower
  bullet.
- The 147gr subsonic round works in the SD like in any gun (user, 2026-10-24: "I don't know why we made MP5 SD not
  work with subsonic"): sound ×0.7, damage ×0.85. A layer `GunsOfTien_SubsonicInMP5SD` (2026-10-22) used to put the
  SD's sound back with that round, since its ×0.7 stands for the crack the SD's sound already leaves out; it was
  removed. Result (SD at the user's 25 / 6 since 2026-10-24): SD 25 / 6 plain, 17 / 4 with the 147gr; MP5 + Mk9 28 / 8 plain, 18-19 / 5 with the 147gr (Gunworks
  stores whole numbers, and which of its suppressor and ammo layers runs first is unconfirmed).
- Built at GoM's SMG scale (K 0.00072, 0.72 of real size): the can 304.8 x 50.8 mm (0.2195 x r 0.0183 units) with a
  knurled three-lug coupler at the rear and "AWC MK9" painted along the left; the mount is Tim Bixler's adapter, a
  threaded cap with wrench flats and a sleeve with three lugs, 30 mm long, over the barrel. Both start at `canon`.
- **GoM's MP5 and MP5A2 have no `canon` point**, and a second `model MP5 { ... }` block from our scripts would reset
  GoM's mesh and texture (model scripts carry ResetExisting, ZomboidFixesB42 CLAUDE.md). Suppressors.lua adds the point
  at run time, `ModelAttachment.new("canon")` + `getOffset():set` + `ModelScript:addAttachment` on
  `ScriptManager.instance:getModelScript("MarzGuns.MP5")` (42.21 jar: ModelAttachment and ModelScript are exposed,
  ModelScript has `addAttachment` / `getAttachmentById`), at every OnGameBoot and OnInitGlobalModData, and appends the
  guns' ModelWeaponPart lines with `Item.DoParam` (once per script object, as Lasers.lua). Not yet seen in game.
  build_mk9.py measures the point: the front face of the front sight housing (largest y of the body's vertices more
  than 0.0105 off the bore axis, behind the barrel tip) on GoM's muzzle z: MP5 y 0.2796 (barrel tip 42.5 mm full
  size ahead), MP5A2 y 0.2811 (35.6 mm). GoM's MP5K model has an unused `canon` point of its own.
- Real-gun checks (2026-10-22): H&K's three-lug mount dates from about 1966 and was made for flash hiders and blank
  adapters; the first three-lug suppressor adapter in the US was Tim Bixler's (Knight's / AWC, patented 1988). The
  plain MP5K has a flush end cap; the MP5K-N (Navy) has lugs and a 1/2x32 thread. The Mk9 fits MP5s by three lugs or
  thread (specify when ordering), Uzis in place of the barrel nut, MACs on their threads. The pre-1994 TEC-9 had a
  threaded barrel for a suppressor or barrel extension (one of the 1994 ban's pistol features). Shorter SMG cans
  offered and declined: AWC MK9A (10"), Gemtech MK9K (about 7-9", Gemtech founded 1993), AWC Tac-9 (no size found),
  and the KAC / H&K Navy can (7.75" x 1.375", direct thread only, so not for three-lug barrels).

## M249 Light Machine Gun (2026-10-22)

- Files: `scripts/build_m249.py` (Blender, ~2 min: `GunsOfTien_M249.fbx` M249_BODY / M249_COVER / M249_BIPOD_FOLDED /
  _DEPLOYED, `GunsOfTien_M249_box.fbx` the box + belt rounds 556x45_M249_1..9, textures M249.png 256 and
  556x45Box200_M249.png 128, `scripts/m249_points.json`), `scripts/render_m249.py -- DIR` (Blender review renders),
  `scripts/make_m249_art.py [--fit] [--renders DIR]` (icons, `docs/m249_preview.png`; cameras in
  `m249_icon_cameras.json`, fitted on GoM's M60 icons; the box uses the MP7 magazine's camera and light, the M60 box
  fit laid it on its side and turned it yellow), `gen_scripts.py m249()` (items_m249.txt, models_m249.txt,
  fixing_m249.txt, names; run from gen_scripts.py's main because that rebuilds ItemName / Tooltip.json),
  `shared/GunsOfTien/M249.lua`, `client/GunsOfTien/M249Tooltips.lua`, the loot in `server/GunsOfTien/Loot.lua`, Hot
  Brass in `server/GunsOfTien/HotBrass.lua`, AnimSets `AnimSets/player(-vehicle)/actions/*M249_GoT.xml`.
- **Reference**: the USAF's public-domain "M249 Automatic Rifle" photo (Commons File:M249_Automatic_Rifle.jpg, kept
  as docs/m249_usaf.jpg). It shows the **right** side (the cocking handle; muzzle right), not the left as the research
  first said. Its bore slopes 13.0 degrees: the photo was turned 13 degrees clockwise (barrel top level within 1-2
  px over 400 px), traced with trace_outline.py (threshold 225, eps 2) and scaled to FM 23-14's 1038 mm (3.817 px/mm):
  `scripts/m249_reference_outline.json` (its photo_px refer to the turned crop, not kept). Bore H 321, origin (grip
  meets the trigger housing) L 707 / H 251. The box size (112 x 88 x 165 mm) is read off the 1985 and 1989 photos
  against the gun; the 1989 Panama photo (DM-ST-90-02821) shows its stencil.
- Drawn at 0.65 (GoM's rifles; its STANAGs then fit, and GoM's M60 is 0.615 of its real length). The feed cover is one
  node with its origin at its front hinge: points `cover` / `cover_open` (rotate -70 about X lifts the rear). STANAGs
  hang at `magazine` (feed lips L 535 / H 290, 12 mm left of centre) with rotate 0 -45 0, slanting down to the gun's
  left (+X) as the real well does (checked in a front render); a slanted sleeve in the body is the well. The box is
  drawn at `box` (its top middle, 33 mm left of centre) and lies on its side on the floor (floor_point, like the
  offcuts). The belt rounds and both bipods are modelled in the gun's space (points at the origin, GoM's M60 way);
  round 1 sits in the tray under the cover, 9 at the box's mouth.
- Gunworks facts used: one magazine profile per gun but any items in it, insertion checks no type; the nine belt parts
  are GoM's own `MarzGuns.Bullet_1..9` (PartType Animated1..9) drawn with our models through the gun's
  ModelWeaponPart lines, and `Animations.CheckStates` shows them by ammo count whatever the Clip is (M249.lua takes
  them off with a STANAG fitted); `FireModePossibilities = Auto` with `rpm = { 750, 1000 }` should list two Auto
  entries (GoM's BAR does it, untested with Auto alone); gwSetPart markers are read only by Gunworks' "none" style,
  so M249.lua hands the M249's to `ReloadAnim.handleGwSetPartAnimEvent` from the attachments style's
  `handleWeaponPartAnimEvent`, and `partState.ensure = { cover closed }` closes it after a reload; ReapplyAllModifiers
  is not run on a magazine swap, so the STANAG jam layer is refreshed from the per-shot `Ammo.AmmoProfileSetter`
  (only called while the gun has an AmmoList).
- Reload clips: `scripts/anim/m249_reload.py` (TienInspectWeapon's rig, base Bob_IdleRifle, aim Bob_IdleAimRifle;
  left-hand templates: vanilla's handgun reload over the slide turned a half turn about the barrel for a rifle's
  top +Z, its rifle load's magazine hold), 72 / 96 / 45 / 45 frames = M249.lua's durations 2.4 / 3.2 / 1.5. The
  AnimSets' event percentages are the script's OPEN / CLOSE / SWAP frames over the clip length: change both
  together. No `x_extends` except the aimed rack (P90 lesson: inherited events are overridden by position). The box
  shows on Bip01_Prop2 (Gunworks' reload magazine, kept for the M249, unlike the P90), keyed in the hand from / up to
  the swap; a STANAG fed with the same clips sits in the hand at the box's offset.
- Sound 180 / 51 is written in the item (sound_model.py's model: 5.56 from 18.3", +0.38 dB on the M16A2's 20"); the
  main mod's SoundTable.lua is for GoM's guns only.

## Belt links (2026-10-22)

- Design: docs/design.md 4e (user's choices: none lost, found and crafted, M249 and GoM's M60, fired links thrown
  out like Hot Brass casings). Files: `shared/GunsOfTien/BeltLinks.lua` (fill / unload wrappers, per-shot handler,
  `BeltLinks.eject`: Ammo Maker's brass catcher, else Hot Brass's `doSpawnCasing` with the link as its
  `optionalItem` and `ignoreDespawn` true (always a real item, outside Ammo Maker's casing clean-up), else
  `AddWorldInventoryItem` at the feet; a "Link" family added to Hot Brass's `CasingImpactSoundParams` +
  `RegisterItemSound`), `client/GunsOfTien/BeltLinks.lua` (MP: shots counted per gun, sent twice a second as
  `GunsOfTien` / `beltLinks`), `server/GunsOfTien/BeltLinks.lua` (checks the gun in hand has a belt box, caps the
  count at 1000 rpm since the last report, 40 a message, throws two a tick), `scripts/make_link_sounds.py` (Blender's
  numpy + `aud` write Ogg Vorbis; 36 synthesised landing sounds (six a surface, noise-driven resonant modes: pure sines stacked in a burst sounded like a chime, user 2026-10-22), events in sounds_links.txt; each link 3 dB under Hot
  Brass's casing on the same surface, user 2026-10-22). Hot Brass 42.15 flies every casing on every nearby client
  (the server's `spawnCasingVisual` goes to all) but plays its landing sound only on the shooter's game, on the
  shooter's emitter (`getPlayer():getEmitter():playSound`, Client.lua ~33-58; a client's character emitter also
  sends a PlaySoundPacket, so others hear it too, at the shooter). Links use that same
  path unchanged (user, 2026-10-22: "use the hot brass way"; a local landing-point emitter,
  `getWorld():getFreeEmitter(x, y, z)`, was tried and removed), `scripts/build_links.py` (after the user's photos of M27 links, 2026-10-22: a wide loop round one round with
  a stamped hole, and round the next a pair of narrow loops, one at each end of the wide loop, so the gap between them
  is the wide loop's length (where the next link's wide loop sits); S-bends join them, small rounded tabs end the
  narrow loops; two earlier guesses were wrong) (links and link boxes, `links_bounds.json`), icons in
  make_m249_art.py, `gen_scripts.py belt_links()` (items_links / models_links / recipes_links, names, tooltips),
  loot in `server/GunsOfTien/Loot.lua` (a link box group added to GoM's own M60 kits, taken out again on reload).
- Engine facts (42.21): `OnWeaponSwingHitPoint` fires on the shooter's game for every shot (vanilla's `onShoot`),
  but on a dedicated server only from the hit packet (`zombie/network/fields/hit/Player`, once per shot ID and only
  for `hitCount` > 0), so a missed shot never reaches the server's event: links from firing are counted by the
  client. Gunworks' magazine loading (`ISLoadBulletsInMagazine:animEvent` InsertBullet) and unloading
  (`ISUnloadBulletsFromMagazine:animEvent` RemoveBullet) change the magazine where `not isClient()`; the wrappers
  compare the count before and after there. `isLoadFinished` returning true ends the load cleanly (Gunworks checks it
  before every round), so "no link left" is put there. `ItemContainer.getFirstType` takes a full type (compareType).
  Racking (bug reported 2026-10-22: neither the round nor the link came out): Hot Brass (PermanentCasings) replaces
  `ISRackFirearm:removeBullet` (no round into the inventory, `emptyRack = false`) and throws the live round at the
  rack's `ejectCasing` only when `not emptyRack` (an MP client falls back to `hadRoundChambered`), so `rackBullet`
  must come before `ejectCasing` in the rack AnimSet: Hot Brass's own XMLs list it first; RackM249_GoT.xml had them
  at the same time the other way round, so in single player the round vanished. The link comes from a
  `rackBullet` wrapper (Hot Brass re-wraps `removeBullet` at every OnInitGlobalModData, so not there).
  Our shared files load after Gunworks' (mod order), so the wrappers sit on top of its own.

## Uzi family (2026-10-23)

- Files: `scripts/build_uzi.py` (Blender, ~2 min: `GunsOfTien_UZI.fbx` UZI_BODY / UZI_BOLT / UZI_STOCK_FOLDED /
  _DEPLOYED, `GunsOfTien_MINIUZI.fbx` and `GunsOfTien_MICROUZI.fbx` <GUN>_BODY / _BOLT / _STOCK,
  `GunsOfTien_UZI_magazines.fbx` 9x19Magazine20/25/32/40/50_UZI, a 256 atlas per gun, 128 per magazine,
  `scripts/uzi_points.json`), `scripts/render_uzi.py -- DIR` (Blender review renders, the Mini / Micro turned upright),
  `scripts/make_uzi_art.py [--renders DIR]` (icons with Post-93's MP7 gun / magazine cameras, sheet
  `docs/uzi_preview.png`), `gen_scripts.py uzi()` (items_uzi.txt, models_uzi.txt, fixing_uzi.txt, names; the Uzis are
  in `SMG9_GUNS`, the Mk9 parts' MountOn), `shared/GunsOfTien/Uzi.lua`, `client/GunsOfTien/UziTooltips.lua`, loot in
  `server/GunsOfTien/Loot.lua`, Hot Brass in `server/GunsOfTien/HotBrass.lua`, AnimSets
  `AnimSets/player(-vehicle)/actions/*UziGrip_GoT.xml` and `anims_X/Bob/Bob_GunsOfTien_Uzi_Unload.x`. Rebuild: build,
  render, art, then `gen_scripts.py` and `check_refs.py`.
- **References** (none in the repo; kept in `tmp/ref/uzi`, gitignored): the Uzi from the Commons photo "Uzi of the
  israeli armed forces" (Uziel Galishto, CC BY-SA 3.0; left side, stock folded, Action Arms markings), scaled to IMI's
  470 mm folded; the user's two angled Uzi photos cannot be traced. The Mini from the user's side photo (stock
  deployed) at the published 600 mm (its folded length then comes out at the published 360; scaling it by the
  magazine instead gave 571). The Micro from the user's side photo (stock folded, butt hanging under the barrel) scaled
  by its magazine, the same IMI part as in the Uzi photo (83 px = 32.9 mm there): 257 mm (published 250 to 282). The
  user's sixth photo is an IMI Uzi Pistol (semi-auto, no stock), used only for the receiver's look. Traced with
  `post93/trace_outline.py`; silhouette IoU against the traces 0.92 / 0.92 / 0.91 (the traced outline fills the
  trigger-guard openings).
- The three photos disagree by up to ~15 mm on the height under the receiver (bore to trigger-guard bottom: Uzi 67,
  Mini 56), so each gun keeps its own photo's proportions; only the magazines are shared. Every gun's `magazine` point
  (straight down, no rake: the Uzi grip is upright) puts the 20-round's base 22 mm under its own grip as all three
  photos show; magazines are 118 mm from lips to base for 20, +4.8 mm a round (25 142, 32 175.6, 40 214, 50 262).
- Mini and Micro are pistol-held: built and baked upright, turned at export (`kit.turned`, the magazine `TURN`, world
  -0.025 0 0 as GoM's MP5K / MAC-10). Their stock is one node modelled deployed with its origin at a vertical hinge
  pin on the receiver's right rear; `stock_folded` = the same offset with rotate 0 0 180 (a half turn about Z
  commutes with the turn about Y, so the rotate stays in the turned model). The Micro's deployed shape is its photo's
  folded stock mirrored about the pin (L' = 500 - L). The Uzi's stock folds down and under (not a single rotation),
  so it is two in-place nodes drawn at the origin, GoM's MAC-10 way (its lines name a `stock` point the model lacks).
- `canon` = the barrel nut's front face (Uzi L 64, Mini 40, Micro 38): the 9x19mm SMG mount device and the Mk9 start
  there (the real Mk9 replaced the nut; the mount device stands in for that adapter). The Mk9's own coupler collar
  shows as a short cylinder in front of the nut, as on the MP5.
- Loot: the police SMG spawner gets the Uzi only, because GoM's `gunOnBackSWAT` hangs that spawner's gun on SWAT
  zombies' backs, no place for a holstered Mini; GoM's crime spawner (user, 2026-10-23, "as long as it is the GoM
  way": a kit in GoM's own spawner, no loot insertion of ours) the Uzi only too, for the same reason
  (`gunOnBackCrime`, the bandits' melee-or-gun back lists).
- Not traced: the right side (ejection port painted over the magazine well, as on the left's stamped recess), the
  selector's A / R / S letters (painted, positions read off the photos' grip-top lever), the Uzi's deployed stock
  (from IMI's 640 mm: struts straight back from the hinge to a butt plate at L 612-640).

## Steyr AUG A1 (2026-10-27)

- Files: `scripts/build_aug.py` (Blender, ~1 min: `GunsOfTien_AUG.fbx` AUG_BODY / AUG_BOLT / AUG_FOREGRIP,
  `GunsOfTien_AUG_magazines.fbx` 556x45Magazine30/42_AUG, AUG.png 256, 128 per magazine, `scripts/aug_points.json`),
  `scripts/render_aug.py -- DIR` (Blender review renders, GoM's FAMAS at the same scale), `scripts/make_aug_art.py
  [--renders DIR]` (icons: the SCARs' rifle camera, fitted on GoM's M4A1 icon, for the gun; the magazines from the side
  in the gun's light, the 30 at the 42's scale (the MP7's blue-heavy magazine light ringed them in blue); sheet `docs/aug_preview.png` with the photo's outline over the left side),
  `gen_scripts.py aug()` (items_aug.txt, models_aug.txt, fixing_aug.txt, names), `shared/GunsOfTien/AUG.lua`
  (registries), `client/GunsOfTien/AUGTooltips.lua`, loot in `server/GunsOfTien/Loot.lua`, Hot Brass in
  `server/GunsOfTien/HotBrass.lua`, the fold in `shared/GunsOfTien/Foregrip.lua` + `client/GunsOfTien/ForegripMenu.lua`.
  Rebuild: build, render, art, then `gen_scripts.py` and `check_refs.py`.
- **Reference** (not in the repo; tmp/ref/aug): Commons "Steyr AUG 5,56 mm" (MoserB, public domain, 4475 px) and its
  background-removed copy "Steyr AUG 5,56 mm noBG.png" (CC BY-SA 4.0, 5000 px, used for the edges): an Austrian StG 77,
  left side, muzzle left, front grip down, magazine out and lying beside it, a sling over the butt (so the outline was
  read by hand on a millimetre grid, `scripts/aug_photo_grid.py`, not traced: the sling joins the gun). Scaled to Steyr's
  790 mm (5.629 px/mm in the noBG copy, muzzle tip x 270, heel y 2190); the bore is level (barrel centre within 1 px
  over 1000 px). Dark pixels (luminance < 130) separate the gun from the drop shadow (~150). Silhouette overlap with
  those pixels 0.76-0.81 (the sling counts against it).
- Drawn at K 0.000603 (every Guns of Tien gun). Origin = the grip's back meeting the stock's underside (photo L 455,
  H 100); bore H 143.5. The scope and carrying handle are part of AUG_BODY (the A1's are cast with the receiver); the
  scope's stats come from the hidden part AUG_Integrated_Scope with no ModelWeaponPart line.
- The front grip is one node with its origin at its pin (photo L 249, H 115), modelled down: `foregrip_deployed` =
  the pin, `foregrip_folded` = the pin with rotate (90, 0, 0), a quarter turn forward about X (the engine draws a part
  at offset + rotateXYZ . vertex; +90 about X takes -Z to +Y), so it lies under the barrel 3 mm below it, as the real
  A1's folds forward. Baked alone (its node is not in the gun's space).
- Magazines: curved forward along an arc (`MAG_R` 800 mm, 8 degrees rake at the lips, ~20 at the 30's base;
  `mag_frame` / `mag_local`), 60 mm front to back, 30 across, 165 mm lips to base for the 30 (measured on the loose one
  in the photo), the 42 55 mm longer. GoM's textures have no alpha, so the translucent smoke polymer is painted with the
  rounds inside (brass cases bullets forward, staggered, a dark line between rounds). Lips at photo L 577, H 90, 13 mm
  above the well's mouth.
- `charging handle` = AUG_BOLT on the left, `bolt_fired` 92 mm back (the A1's handle rides with the bolt carrier).
- Hold and reload: the bullpup set, shared with GoM's FAMAS (section "Bullpup set" below). Before it the AUG borrowed
  GoM's FAMAS reload clips, and vanilla's rifle hold put its left palm (0.218 ahead of the grip) on the bare barrel
  9 cm behind the flash hider, 4 cm under it (hold_preview.py `aug`).

## Bullpup set (2026-10-27)

- User: "that is why we now need a bullpup animation set", for the AUG A1 and GoM's FAMAS, reloads included (design:
  docs/design.md 4h). Choices: one hold set for both (the AUG's unfolded grip gets no hold of its own), GoM-style
  reloads (no magazine in the hand), the gun moved 3-4 cm from the face when aiming. Lua: `shared/GunsOfTien/Bullpup.lua`
  (Gunworks grip animId `GunsOfTien_CompactBullpup` at OnGameBoot; reload handlers `GunsOfTienCompactBullpupAUG` /
  `...FAMAS`, style "none", 1.2 / 1.5 / 1.2 / 1.2 s, registered after GoM's so they replace its FAMAS's).
- Measured (game units, from each gun's grip): magazine lips AUG (0, -0.074, -0.006), FAMAS (0, -0.076, 0.015): 2 mm
  apart front to back but 2 cm in height (FAMAS well bottom z -0.033, AUG's mouth -0.014), so each gun has its own four
  reload clips. Left-hand places: the FAMAS's handguard underside z -0.005 over y 0.10-0.22, the AUG's folded grip
  y 0.12-0.19, its bottom z -0.002; vanilla's palm (0.218 idle, 0.204 aimed) is the FAMAS's handguard tip and the
  AUG's bare barrel. FAMAS cocking lever = the front of FAMAS_BOLT under the carry handle's bar (y 0.08-0.12, z
  0.026-0.060, |x| < 0.004; the bar at z ~0.075), back 0.061 with the bolt.
- Since 2026-10-28 only this set's **aimed** frames ship (the carry is draft B, section "Bullpup stance (built)");
  the rest of this section describes the rifle_hand.py build those aims come from.
- Hold: `scripts/anim/rifle_hand.py` SETS "Bullpup" (scale 0.72: palm 0.157 idle / 0.147 aimed; `push` 0.02: the gun
  moved forward along its own Y every frame, the right arm solved after it and the gun put back from where the hand
  landed). 116 clips (every vanilla firearm clip with a gun in its name). Needs `GUNWORKS_ANIMSETS` on Windows (the
  default is the Mac path) or `firearm_clips` finds nothing and the build silently writes no clips.
- No clipping (user, 2026-10-28, after the reloads: "we wanted to fix the clipping issues"). Measured with
  TienInspectWeapon's clearance (chest / neck / head, arms by their bones a limb's radius out): vanilla's rifle idle
  reads L 0.011, compact_build's CONTACT 0.022 is the forearm's centre line on the skin (half inside), and the set had
  the left forearm 1 cm deeper than vanilla in 67 of 116 clips (0.021-0.028), the right up to 4.1 against 1.6 (bite
  reacts, where the push re-solves the arm), and the guns' butts 2.4 (AUG) / 3.2 (FAMAS) in the shoulder on every aim
  (through the jaw in the side view; vanilla's aim has GoM's M16A2 1.8 in). The grips sit alike on the hand
  (M16A2 / AUG / FAMAS within 1 cm); the bullpups are longer behind it (butts at -0.164 / -0.201 / -0.216). Now
  (`contact` 0.008, `guns`): every frame of every clip, both arms no deeper than vanilla's own in that frame or 0.008
  where vanilla is clearer, and both guns no deeper than 0.008 (checked against vanilla's M16A2 per frame: none over).
  How: (1) the push grows by EXTRA_PUSH 0.063 with `shouldered` (butt-to-right-shoulder distance: 0.02-0.04 in every
  aim, 0.25-0.37 lowered; full below 0.06, none above 0.16), so all aims hold the gun alike (~10 cm off the eye now,
  not the user's 3-4) and aim-to-idle eases down with the gun; searched per frame it crept 2.5 cm a frame in still aims
  (depth is not monotonic in the push), one per clip flipped aim-to-idle's left elbow and left its end off the idle;
  (2) the right arm eased toward vanilla's (push and arm) where it went in; (3) a gun still in (the AUG's scope in the
  face in bite reacts, the FAMAS's carry handle in the chest in a bump; pushing on made those worse) moved straight out
  (mean of nearest-body-point minus vertex over the vertices inside), kept in Bip01_Spine1's frame, spread by
  `spread_vectors`; (4) the right arm eased again for what (3) put in; (5) the left elbow swung (`clip_swing`: one
  direction per clip of SWINGS, out / out-back / back / out-up / up in the idle chest's terms turned with the chest,
  the one clearing most frames with the least swing, up to 0.4; rig.RIGHT is the character's, and in the seated
  stand-up, body turned, an elbow swung that way left the upper arm 2.8 cm in the chest's side; per-frame directions
  handed frames a neighbour's swing that did not clear them); (6) what is left: the gun moved out with both hands
  (`arm_escape`), then the left chain eased toward vanilla's (`release_share`, the hand sliding along the gun); neither
  is needed by any clip now. The right elbow is solved in the plane of vanilla's own (`carry`: swivel off, pole =
  vanilla's elbow): searched by the wrist's cost it flipped 16-22 cm between two frames in the sprint vault and
  FallIdle04 (there since the first build). The left shoulder comes forward (clavicle turned up to 25 degrees,
  `left_solve`) where the arm falls short of a gun pushed out (aim up 75: 1.2 cm). Each per-frame need is `spread`
  over RAMP 5 frames either side: compact_build's Declip.arms chose its swing frame by frame and popped, and its
  release bisects from 0.5 and never reaches vanilla's arm. Result (2026-10-28): every clip clear, the left hand on its
  place in every frame of every clip, no frame-to-frame move more than 1.6 cm over vanilla's (the walk into the aim,
  the gun rising and pushing out at once). RIFLE_HAND_DEBUG prints every frame.
- Reload: `scripts/anim/smg_reload.py` `aug` / `famas` (`bullpup()`: the Uzi spec's rifle hand, rack and hip places, the
  set's idle / aim as base, clip names `GunsOfTien_CompactBullpup<Gun>_Reload<clip>`). The magazine change's work place
  had to change: the Uzi's stood a full-length bullpup almost upright, muzzle by the face; a flatter one further out
  took the well (behind the grip) out of reach (scanned with SMG_WORK / _ALONG / _TOP / _WRIST / _TWIST; `off` turns
  the wrist settle off). First draft ch(0, 0.62, 0.10) / FAMAS ch(0, 0.64, 0.08), its rear against the chest; moved
  out and up (user, 2026-10-28): pos ch(0, 0.70, 0.16) for both, along ch(-0.70, 0.15, 0.70), top ch(0.30, 0.95, 0),
  settle wrist (-45, -35) (option B). Straight out alone lost the well again (2-6 cm short); raised, every frame is in
  reach. The settle wrist decides how upright the gun stands there, not along / top (no settle: tilted across but
  the right wrist at -55 / -39 whatever the orientation or chest twist; the Uzi's (-30, -20): upright, muzzle by the
  face). `[short] f0` entries are `hand_away`'s probe, not frames. The left arm crossed the belly 1.1-1.8 cm on its way
  from the idle to the work place and back (frames 1-6 / 37-44, the same at every place): `declip_left` (spec
  `contact` 0.008) swings its elbow out with rifle_hand's smoothed swing, the clip's ends left as built (the idle's own
  0.9-1.1, the limit easing from that to 0.008 over 5 frames); right arm at most 0.8, guns 0. Racks moved too: the
  Uzi's place had the left arm 1.3 cm in reaching the FAMAS's lever; AUG ch(0.10, 0.62, 0.14), FAMAS ch(0.10, 0.62,
  0.16) (scanned with SMG_RACK). Racks: each hand from
  the left side (the UMP's turn (-60, 30, -45)); the aimed rack stays in the aim (its right wrist reads -91 / -91 every
  frame, the aim clip's own grip; not visible in renders). Out dir must be absolute on Windows (a relative one under
  Blender lands in C:	mp).
- Shipped: `compact_pack.py` (RELOAD_SETS: Bullpup packs both guns' reloads under their own names; 124 clips, 4 files,
  8.8 MB, main mod anims_X/Bob), `compact_animsets.py ... Bullpup` (255 hold nodes) and `write_reload_nodes(...,
  mag_event=False)` for BullpupAUG / BullpupFAMAS (16 nodes, player + player-vehicle; no changeWeaponPart: GoM's FAMAS
  nodes have none either, its `InsertMag` event is read by nothing). Previews: `HOLD_SET=Bullpup hold_preview.py ...
  aug aug_folded famas`, smg_reload.py `--preview`.

## Bullpup stance drafts (2026-10-28; B chosen: "B looks good. implement B")

How bullpups are held (research, 2026-10-28): the support hand near the muzzle on the handguard or the AUG's front
grip folded down; the rearward balance makes a low ready easy and the raise to aim a hinge; the magazine is the part
by the armpit; the length of pull is a rifle's, so shouldered hands sit where a rifle's do with the support hand
10-15 cm nearer. One left-hand place fits both guns (just ahead of the trigger guard).

`scripts/anim/bullpup_stance.py -- <Bob> <out> A B now` (~10 s for all three on Windows; out dir absolute), sheet
`tmp/anim/bullpup_stance/bullpup_drafts.png`. Character space (ch: right, up, forward) from vanilla's rifle idle: the
right shoulder joint (0.10, 0.75, -0.035), the elbow (0.15, 0.63, -0.05), the eye (0, 0.855, 0.01); vanilla's idle
rifle grip (0.064, 0.491, 0.048), muzzle 27 degrees **up**, and a bullpup's butt (0.21 behind the grip) at (0.24,
0.40, 0.00), out at the right hip: the dangle. Vanilla's aim: grip (0.07, 0.741, 0.119), level.
- A, shouldered low ready: the aim's torso and hand relation, the gun at the set's aim place (push + aim_push 0.083)
  swung 30 degrees down about the butt (0.07, 0.74, -0.01). Wrists L (-48, -4, 35), R (-28, -1, 0); arms clear; gun
  0.010 (AUG) / 0.007 (FAMAS) in, the AUG 2 mm over the 0.008 rule. 35-45 degrees cost more (wrists, gun 0.012-0.015
  in). Vanilla's `Bob_IdleAimRifle_Down` as the base hunched over the gun with the head bowed into the FAMAS's carry
  handle (dropped).
- B, tucked carry: the rifle idle's body, the grip held with the **pistol** idle's hand relation (`idle_down.x_rig`;
  with the rifle idle's the right hand fell 10 cm short and the wrist went to (-50, -45)), butt pinned at (0.14,
  0.68, -0.10), behind the upper arm (its bone line 1 cm off), muzzle 25 down and 30 across to the left, twist 15,
  the gun touching the side. Wrists L (-28, 44, 42), R (-10, -11, -25); every depth 0.005 or less. Unconstrained the
  scan drifts to vanilla's butt-behind-the-hip carry or to a 15-degree hip ready; the pin and BS_B_DOWN keep it a
  carry. Its best still sits on the grid's edge (x 0.14, forward -0.10, 30 across), so a build should rescan wider.
- The left hand is the set's place in both (palm x 0.72); the AUG's unfolded grip hangs just behind it.
- B moving (`BS_MOVE=1 ... B`: vanilla's Bob_RunRifle / Bob_Sprint_Rifle, frame by frame as compact_build's carried
  clips; GIFs `tmp/anim/bullpup_stance/B_Bob_<clip>.gif`, FAMAS). Held rigid to the chest, the gun went 4.6-4.9 cm
  into the hips and the right arm 2-3 cm in; with the short SMG stance's approved drift shares (vanilla's gun drift
  against the chest, 0.2 out / 0.4 up) run: gun 0.7, left arm 0.9 cm, butt 3.6-5.4 cm from the upper arm's bone line;
  sprint: gun 1.0, left arm 1.4 cm (vanilla's own arms 0 in both), butt 0.4-3.1 cm. Over the 0.8 rule by up to 0.6
  cm, for a build's de-clip. Worst wrists: run R (-45, -16, -67) at frame 0, sprint L twist 71. The run's forward lean
  turns the hold's 25-degree muzzle near vertical in the side view.

## Bullpup stance (built 2026-10-28, not played)

Draft B on every clip played with a gun, by `compact_build.py ... Bullpup` (as the short SMG stance), replacing
rifle_hand.py's set in the shipped packs (Bullpup.lua unchanged: grip animId `GunsOfTien_CompactBullpup`).
- Set (`compact_build.SETS["Bullpup"]`): `hold` = B (`_bullpup_hold`: butt at ch(0.14, 0.68, -0.10), 25 down, 30
  across, twist 15, no look / lean), held with the pistol idle's hand relation (`idle_down.x_rig`, as every
  compact set); left palm at the idle template's palm x 0.72 (`palm_scale`); carried frames keep 0.2 / 0.4 of
  vanilla's gun drift (the module default). `aims`: the aimed frames are rifle_hand.py's earlier build, unchanged
  (vanilla's aim, gun pushed off the face, de-clipped), read from `tmp/anim/bullpup_aims` (`extract_aims` copied
  all 120 clips out of the old packs on the first run; it leaves an existing folder alone, so that copy is the only
  source of the old aims now: keep it, or rebuild rifle_hand.py "Bullpup" to get them back). `gun_path`: frames
  between carry and aim (`path_pose`) blend the body bone by bone but move the gun on a straight path between its
  two places on the chest, both hands solved onto it; blending the arm bones (the compact sets' way) swung the gun
  through the right side, 6 cm in mid-raise. `gun_clear`: carried and between frames move the gun straight out of
  chest + pelvis (`Declip.gun`, `clear_gun`) to 0.008. `Declip.gun` turns the escape direction from Blender's world
  into the clip's space through the armature's object matrix (x_import.OBJECT_MATRIX swaps Y and Z); rifle_hand.py's
  `gun_escape` applies it without that turn.
- Build: 244 clips + generic copies = 267 (`tmp/anim/compact/Bullpup`), ~5 s a clip; run as 6 Blender processes
  with `--clips` lists and `--no-pack` (the four UNDERLYING clips first, the generic copies read them from out_dir),
  then manifest.txt = every built clip. Packed with the reloads: 271 clips, 7 packs, 28.2 MB (was 3 packs, 8.8 MB).
  Nodes: `compact_animsets.py ... Bullpup` rewrote the same 255 files; every packed clip referenced, none missing.
- Measured (chest; the build's own report): aim clips (19) as shipped, all within 0.008. Carried / between (81):
  gun over 0.008 in 4 (SprintToAimRifle 2.8 cm, EmotePainLeftArmRifle 2.2), arms over 0.022 in 4 (VaultOver_End 3.1,
  BiteReact_Rifle_L 2.9, EmotePainLeftArmRifle 2.7, RunRifle_BumpL 2.4). Generic copies (151): the gun is the carry's
  under a gesture, not movable per clip: over 0.008 in 50, over 2.5 cm in 6 (crouched pain emotes, StealthEmote
  PainStomach02 6.0 cm), arms up to 8.6 (EmoteYawn2H on the ground, right arm). Not the "No clipping" rule's 0.008
  everywhere: compact_build's own de-clip (CONTACT 0.022), as on the short SMG stance; declip_pass was not used.
- Reloads (`smg_reload.py aug`, base now the new idle and aim, `BULLPUP_CLIPS`): unload, load and aimed rack as
  placed before; the rack's place moved to ch(0.08, 0.60, 0.06) (at ch(0.10, 0.62, 0.14) the right hand fell 4 cm
  short with the arm straight: the carry's pistol relation puts the barrel along the forearm). Arms: unload / load
  1.4-2.1 cm in at the hip end (the magazine in the hand) and the load's frame 10; rack and aimed rack within 0.008.
- Previews: `tmp/anim/bullpup_gifs` (idle, raise, walk, run, sprint, sneak walk; reload sheets).

## No clipping: every set we ship (2026-10-28)

User, after the bullpup reloads: "we wanted to fix the clipping issues"; then "the arms not to pass through the body",
the guns kept out of it too ("a nice extra"). Rule for every animation set: on every frame, each arm no deeper than
vanilla's own in that frame, or 0.008 where vanilla's is clearer; each gun and its parts no deeper than 0.008. Measure
before showing anything (TienInspectWeapon's clearance: chest / neck / head; arms by their bones a limb's radius out,
vanilla's rifle idle reads 0.011; compact_build's old CONTACT 0.022 was half the forearm inside), the clip a clip starts
from too, and frame-to-frame moves against vanilla's and the clips before (a de-clip can pop).

- **Reverted for the short SMG stance (Uzi, UziT, MP7, MP5K), user 2026-10-28: "your current changes are worse".**
  Their packs and compact_build.py are back to the 2026-10-27 commit (no `declip_pass` call), and the stance
  reloads' `compact` spec has no `contact` again (no `match_ends` / `declip_left`). What looked worse was not said;
  ask before trying again, and show it first. The compact_build bullet below records what was tried. The
  de-clipped builds are still in `tmp/anim/compact` and `tmp/anim/full`: rebuild before packing from there.
- **Reverted for the UMP set too (2026-10-28)**, after the merge with `models-resize` (the set now ships in the main
  mod and also holds GoM's MP5A3 / MP5A2 / MP5SD; our fixes were measured on the UMP's shape only). User: the old set
  for everyone. Its three packs are back to the 2026-10-27 build (the UMP's reload clips in them too). The code is
  back too (2026-10-28): rifle_hand.py's "UMP" entry is `scale` only (its no-`contact` path is the 2026-10-26 build
  exactly) and smg_reload.py `ump_spec` has no `contact`; to try again, add the MP5s' meshes to `guns` and ask
  first. `tmp/anim/rifle/UMP` / `tmp/anim/reload` still hold the de-clipped clips: rebuild before packing from
  there. The Bullpup set keeps its fixes.

- Found (shipped before): the bullpup set's left forearm 1 cm deeper than vanilla's in 67 of 116 clips, its butts
  through the jaw on every aim; the UMP set (52 clips), Uzi / UziT (76), MP7 (75), MP5K (67) up to 2.2 cm deeper; the
  UMP's unfolded stock 2.3 in the shoulder on vanilla's aim; the sprint vault's and FallIdle04's right elbows flipping
  16-22 cm in a frame; the stance reloads' ends 1.7-2.5 cm in.
- rifle_hand.py sets (Bullpup, UMP): `contact`, `guns` (bodies and parts at their model points: the AUG's grip both
  ways and 42-round, the FAMAS's STANAG, the UMP's stock unfolded / folded and 25), `aim_push` (Bullpup 0.063, UMP
  0.045). Steps in CLAUDE.md "Bullpup set" (No clipping). Gun moves out of the body come in rounds: the spread hands a
  frame a neighbour's move that can push it in (the UMP's aimed strafe: 1.3 cm), so whatever is still in is moved out
  again from where it is. Results: every frame of both sets clear, the left hand on its place everywhere, nothing
  released.
- (Reverted, see above) compact_build.py (Uzi, MP7, MP5K; UziT packs the Uzi set): the variants and solvers as before, then
  `declip_pass.run` on every clip written: (1) the gun out of the body with the hands on it (`move_gun`), the least
  move of GUN_DIRS (forward, forward-up, forward to either side, up, in the chest's terms) and the buried vertices' way
  out (`gun_escape`'s way alone ran along the chest: the Uzi idle's gun went 7 cm for 0.3 cm in), in rounds;
  (2-3) each elbow swung, one direction per clip (`clip_swing_keep`; SWINGS / SWINGS_R), the hand kept, re-solved in
  its own elbow plane at no swing (`solve_keep`: swivel off, pole = the pose's own elbow) so frames needing nothing are
  unchanged; a frame no swing clears takes the swing that helps most (the maximum taken blindly was a 5 cm pop in the
  pain emote); swings fade in over SWING_RAMP 10 frames; (4) an arm still in: the gun moved out with the hands, the
  least move that clears both arms and the gun, in rounds; (5) a right arm still in: eased toward vanilla's own, the
  gun with the hand (EmotePainLeftArmRifle: the stance carries the gun across the body where vanilla's hangs at the
  side, 2.5 cm -> 0.6); (6) the left arm toward vanilla's own, then per frame from where it is. Masked gesture copies
  (generic clips): their clip bones are not what the game shows (`masked(qu, qc, masks)` over the state underneath,
  bone by bone), so the pass runs on the shown pose and the arm bones go back through `unmask` as
  `generic_masked_pose` does; no gun moves there (the gun bone comes from the state underneath) and bones a mask
  leaves at weight 0 cannot be steered. The raw-bone numbers (4-6.7 cm for the emotes) meant nothing.
- smg_reload.py (spec `contact`: bullpups, UMP; the stance's `compact` specs had it too, reverted): `match_ends` gives a clip end that is
  one of the clips it joins (first frames of `base_clips`; gun within 5 mm and 3 degrees) both arms from it, faded in
  over RAMP frames (the rig solves its own elbows there); `declip_left` swings both elbows with declip_pass's
  per-clip choice and moves the gun out with both hands for what is left; the left shoulder comes forward where the
  arm falls short (`rifle_hand.shoulder_forward`, wrapped around the rig's solve_arm: the UMP's aimed rack was 2 cm
  short with its aim pushed out). Rack places moved for the bullpups (CLAUDE.md "Bullpup set").
- A masked copy keeps the pass only if its shown pose comes out no worse (`over_limits` before / after): through the
  masks the MP5K's sneaking stomach-pain gestures went from 2.5 to 7 cm (kept as solved: clear as shown).
- The short SMG stance as shipped (the committed build) keeps its old clipping: arms up to 2.2 cm deeper than
  vanilla's, its reloads' ends 1.7-2.5 cm in. The de-clipped build had left over: the Uzi / MP7 sneaking stomach-pain
  gestures' right arm 1.7-2.1 as shown, EmotePainLeftArmRifle's right arm 0.6, the MP7 unload 3 mm, run-to-stop
  1-4 mm, frame-to-frame moves up to 1.7 cm (EmoteWipeRightLegRifle).
- Tools: RIFLE_HAND_DEBUG / DECLIP_DEBUG print every frame; `tmp/anim/compact/run.sh <Set>` rebuilds a stance set in
  six Blender processes (its underlying idles first, then five chunks; GUNWORKS_ANIMSETS set inside), `run_gen.sh` the
  gestures only; the stance reloads read their bases from `tmp/anim/full/<Set>` (copy the build there with a
  manifest of the shipped names). Pack with compact_pack.py per set (UziT from the Uzi build).

## Gun tooltips (2026-10-18)

The user's screenshot showed raw keys in a gun's tooltip. 42.21 `HandWeapon.DoTooltip` adds one row per fitted part,
labelled `Tooltip_weapon_<PartType>`, then `WeaponPart.DoBatteryTooltip`: for a part tagged `base:usesbattery` (GoM's
weapon lights) a "Remaining:" row with a charge bar (`IGUI_invpanel_Remaining`, vanilla's): that row is the light's
battery, not a bug. GoM translates most part types; nobody translated `LaserRifle`, `LightRifle`,
`BayonetIntegrated`, `BayonetKnife`, `BoosterScope`, `Shellholder`, `UnderbarrelChamber`, `Animated1-9` (the M60's
visible belt rounds), so `gen_scripts.py` writes them into the main mod's Tooltip.json, and `gen_post93_guns.py`
writes `ForegripIntegrated` into Post-93's. GoM's own gun lines said only "Has Integrated Stock" / "Has Integrated
Bipod" (eight guns) and nothing for other guns with one; `scripts/gen_handling_tooltips.py` reads GoM's Stocks.lua,
Bipods.lua and AttachmentCustomStats.lua and writes `client/GunsOfTien/HandlingTooltips.lua`, the lines of each gun in
the style of GoM's part tooltips ("Collapsible stock deployed:" then "Aiming Time reduced by 25%", "Hit Chance
increased by 15%"; folding vs collapsible by the real gun), in place of the vague line or after the others; the MP7s'
lines in Post-93's Tooltips.lua use the same style. **Only the current state shows** (user, 2026-10-19: "only
display the proper CURRENT stats if they are active"): each integrated part's lines are kept in the global
`GunsOfTien_TooltipStates` (part full type -> heading + effects; HandlingTooltips.lua for GoM's stocks, bipods and
selectors, Post-93's Tooltips.lua for the MP7 stock and grip, Tooltips.lua for the sawn-off stocks), and GoM's vague
"Has Integrated Stock / Bipod" lines are removed. GoM's table is per item type, so `client/GunsOfTien/Tooltips.lua`
wraps `ISToolTipInv.render` and `ISToolTipItemSlot.render` on the first tick after OnGameStart (outside GoM's
file-load and ZomboidFixesB42's OnGameStart wrappers, which both read `tooltipsPergun[item:getFullType()]` when they
draw) and sets the type's lines from `self.item`: GoM's own lines (kept per type the first time) plus those of the
parts fitted on it (`getAllWeaponParts`), and a sawn-off gun's holster line. A state without effects (most folded
stocks, the M4A1 / XM177 / M24 parts with no stats) shows nothing. Vanilla gives a tooltip its item with
`ISToolTipInv:new(item)` as well as `setItem`, so render is the one sure place. GoM registers no stats for the M4A1 and XM177 stocks or the M24 bipod, so
their lines say "has no effect on handling".
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

Second audit (user, 2026-10-19: "let's fix every bad tooltip"), every line of GoM's table against its registries:
- **Wear is "one chance in N"**: `ConditionLowerChanceOneIn` × m changes the chance by 1 / m, so ×1.5 is a third
  *less* wear, ×0.85 is 18% more, ×0.5 doubles it. GoM's round lines (and ours, copied from them) quoted m − 1:
  .223 / .308 civilian "−50%" (really −33%), 5.56 HP "+15%" (+18%), overpressured "+50%" (doubled), subsonic "−100%"
  (halved); ours: steel core +15% (+18%), 9mm +P+ +40% (+67%), .45 +P +30% (+43%), and SP / HP rounds' +11% unsaid.
  GoM's lines also left out critical damage / chance changes, had typos ("Change to degrade", "decrease by",
  "maximun", "One single slug rounds", "Required rack after shoot") and gave the 5.56 subsonic's sound twice; the .38
  Special has a profile and had no line. `scripts/gen_round_tooltips.py` now writes every round's lines from both
  mods' profiles (`client/GunsOfTien/RoundTooltips.lua`, replacing GoM's per round; NOTES for what a number cannot
  say; the plain rounds' RealisticPiercing lines added on OnGameStart, when the option is known). Post-93's hand
  written round lines matched its profiles.
- **Parts and guns** (gen_handling_tooltips.py `info_rows`): shell holder "fire 40% faster" = Recoil Delay ×0.6;
  bayonets: any of the five fits any of 16 guns (`Bayonet.RegisterMountableWeapon` in Bayonets.lua; the M4A1 and XM177
  take them but did not say so), a fixed bayonet stabs as `MarzGuns.Attack_Bayonet` (1.2-1.7 damage, reach 1.48,
  crit 20%), and none fits with a suppressor, muzzle device or M203 (`SetExclusives`); the Picatinny Rail becomes the
  slot picked in the upgrade menu (UniversalAttachments.lua); speedloaders per gun in SpeedLoader.lua (the Mosin's
  5-round stripper clip had no line); the Remington 700 / Model 70 slings are `WeightModifier = -1`, the VP70M stock
  has no stats; the Camp Carbine, Glock 17, VP70M, Double Deuce (2-bore) and four magazines had no lines.
- **Two GoM registrations miss their target**, fixed in `shared/GunsOfTien/GoMFixes.lua`: the Karabiner 98k
  bayonet's attachment is left out of `RegisterMountableWeapon` (its item script mounts on the same 16 guns), so
  `Bayonet.CanAttachBayonet` refused it everywhere; the overpressured 5.56's spread penalty is registered as
  `MarzGuns.556x45_Bullet_Overpressured`, but the round is `SWMG.` and `RateOfFire.getSpreadProfile` looks rounds up
  by their own type, so it never applied (now: automatic fire spread doubled, as GoM meant).
- **GoM's muzzle points** (2026-10-26, `shared/GunsOfTien/MuzzlePoints.lua`, measured by `scripts/muzzle_audit.py` +
  `muzzle_audit_sheet.py`, side views in tmp/muzzle): the flash and the bullet / tracer start at the model's `muzzle`
  point; on 21 of GoM's 72 gun models it sat 1-7 (game units x 100) ahead of the barrel's end or inside it (only the
  distance along the barrel was off; height within 0.5). Moved to the bore's front at OnGameBoot and OnInitGlobalModData
  (`getAttachmentById("muzzle"):getOffset():set`). The AR-15 / M16s' point was at the front of GoM's AR muzzle
  mount device (5.4 cm): with GoM's flash hider, compensator or brake (3.5-4.3 cm) the flash now starts inside the
  device; suppressors turn it off (AttachmentCustomStats.lua). Left: guns under 1 cm off, the MP5K (compact stance),
  the `*_M203_Underbarrel` launcher models (CAR-15's point 19 cm ahead of its launcher, M16A2's at the rifle's).

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
for the critical chance; a tooltip line on each laser part). Radial icons `media/ui/GunsOfTien_Radial_Laser{On,Off}.png`
(`scripts/make_laser_radial.py`, Gunworks' palette like the foregrip's; they replaced vanilla's vehicle headlight
icons, which the user found ugly, 2026-10-18).
Battery fixes (user, 2026-10-18: "can't be installed with batteries... the remaining bar... empty"; decompiled
42.21): (1) a craftRecipe's `tags[...]` input matches only items in its own `itemScriptCache` (`InputScript.containsItem`),
filled from `ItemTags` at PostWorldDictionaryInit; ItemTags is built when the scripts load, before any Lua, so a
tag given by `DoParam("Tags")` never reaches a recipe. `addToBatteryRecipes` adds the lasers to Remove / Insert
Battery's input lists and `getUsedInRecipes` at OnLoadMapZones (ZomboidFixesB42's `ScriptFixes.addTag` does the same
for every recipe; not used here, the third flashlight-tag recipe dismantles electronics). (2) `InventoryItem.uses`
starts at 1 and `Item.InstanceItem` never fills a WeaponPart's (`WeaponPart.getCurrentUsesFloat` = uses x useDelta),
so a new laser shows 0.03% and Insert Battery (`IsEmpty`: `getCurrentUses() > 0` refuses) cannot take one; GoM's
lights spawn at 1 / 1000 the same way. The server now gives every carried laser without the mark its full battery
every game minute (`chargeNew`, `syncItemFields` for a loose one, `syncHandWeaponFields` on a gun).
(3) Remove Battery deleted the laser: `InheritUsesAndEmpty` sets the kept input to 0 uses, and
`ItemUser.UseItem` then removes any input at 0 uses that is not `KeepOnDeplete` (= `DisappearOnUse = false`, read
from the script every time; default true). GoM's lights set it; patchScripts now does for the lasers.
The inventory right-click lists a craft only when it can be done now (`CraftRecipeManager.getUniqueRecipeItems`:
`canPerformCurrentRecipe` for the clicked item), the crafting window lists it anyway: Insert Battery shows on a
laser only at 0 charge with a charged battery carried. `InitCharge` fills only a laser at exactly its starting 1
charge, so one emptied before the server marked it stays empty.
Dismantling (user, 2026-10-18): GoM's lights are in vanilla's DismantleElectronics through the static flashlight tag,
so their right-click shows an item-name submenu (two crafts; one craft goes straight into the main menu); the lasers
are added to it the same way (`BATTERY_RECIPES`). Its `dismantleFlashlight` returns a battery only from a
DrainableComboItem, so a laser's (and a GoM light's) charge is lost. Seen 2026-10-18: Insert Battery showed on a
laser's right-click in single player but not on the server (not traced; check after the Workshop copy is updated).
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
(two crossed quads, 0.26 game units (~0.4 tiles) since the user saw it unlit and asked for it longer; first
0.065, a laser unit's length; GoM's are 0.055-0.069; narrowing to a point at the tip) and `LaserBeam.png` (solid
red; see the fade notes below). `gen_scripts.py` `lasers()` writes one model per laser (`LaserBeam_<laser>`, its attachment named
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
Seen in game (user's screenshots, 2026-10-18): the unlit shader loads from the mod and the beam shows in full
darkness, but a long soft fade ((1 - u)^1.3) read shorter in the dark (the faint tail vanishes on black, still tints a
lit floor). Then solid for 70% and smoothstepped to 0: the tail turned black, because **the engine draws weapon parts
opaque** (texture alpha is not blended, only cut below 0.01 in basicEffect.frag; no model-script key changes that),
so a colour premultiplied by the fade is just a darker red, black at the end. A screen-door fade in the shader
(discard when texture alpha < interleaved gradient noise of `gl_FragCoord`) is real see-through but looked dotted
at game size (Blender previews, no anti-aliasing, of three endings). User's choice (option B): solid plain red,
narrowing to a point, no alpha fade; the shader only drops the lighting.
The first pointed mesh (each quad's two tip corners on one spot) never loaded: `MeshAssetManager.loadCallback >
Failed to load asset: AssetPath{ "weapons/parts/GunsOfTien_LaserBeam|GunsOfTien_LaserBeam" }` in the debug log, no
other error, and no beam. Its export held two zero-area triangles; the earlier full-width quads loaded. Not traced
in Java (Assimp import with JOIN_IDENTICAL_VERTICES etc., see ZomboidFixesB42's CLAUDE.md), but the rule is: never
export degenerate faces; the beam is now one real triangle per plane.

## Sawn-off stocks (2026-10-19)

User: "the barrel can be sawn off. i want it also to be able to saw off the stock so that it's more compact and can
be fitted into a holster"; scope (user): "only the wooden stocks of the older shotguns can be sawn... or rather those
whose barrels can be sawn off" = GoM's Double Barrel, Stevens 555, TOZ-34 (their barrels are `Barrel` parts and
GoM's craftRecipe `SawnOffShotgunBarrels` saws a detached barrel). The pump guns' barrels and every GoM shotgun stock
are modelled into the body mesh. Code: `shared/GunsOfTien/SawnStock.lua` (its header has the design), scripts
from `gen_scripts.py sawn_stocks()`, mesh from `scripts/build_sawn_stocks.py`. Not run in game yet. Engine facts
behind it (42.21):
- `HandWeapon.weaponSprite` is per gun **and saved** (`HandWeapon.save` flag 4194304 when it differs from the
  script), so it is in every item send too; `InventoryItem.attachmentType` is per gun but **not saved** (copied from
  the script at `InstanceItem`), hence the `getAttachmentType` wrapper rather than `setAttachmentType`.
- Gunworks `ConditionalModel.Register(gun, { rules = { { parts = { <partType> = type | {types}, ... }, model } },
  default })` is a StatsFactory layer (after CustomStatsAttachments) that sets WeaponSprite from the fitted parts on
  every ReapplyAllModifiers; a gun no rule matches gets the script's sprite back. Nothing in GoM uses it yet.
- `Item.DoParam("ModelWeaponPart", ...)` reuses an entry of the same part type but adds it to the list again
  (Lasers.lua patches once); `InstanceItem` hands the script's list itself to the gun, so a patch reaches guns that
  already exist. Not needed here: the barrels are drawn at the gun's origin, which the stockless model keeps.
- **`AimingTime` is the aim-in time and the post-shot cap**, higher is worse (42.21, re-traced 2026-10-19 after a
  wrong first reading). Raising the gun sets the character's aiming delay to AimingTime (×0.8 Dextrous, ×1.2 All
  Thumbs, ×1.5 in a vehicle; `IsoGameCharacter.resetAimingDelay`), which drops 0.625 × `GameTime.getMultiplier()` ×
  (1 + 0.05 × Aiming level, + 0.1 Marksman) per update while aiming with the recoil settled (`updateAimingDelay`);
  every shot adds RecoilDelay × 0.25 + AimingTime × 0.05, clamped to 0..AimingTime (`CombatManager.setAimingDelay`
  from `SwipeStatePlayer.doAttack`), and the hit chance loses the remaining delay, scaled by distance
  (`CombatManager` ~2731, `getAimDelayPenalty`). In real time that is 30 delay units a second at Aiming 0 whatever
  the frame rate (fpsMultiplier = 60 / fps, × 0.8), so AimingTime 40 takes 1.33 s to aim in (1.07 s at Aiming 5);
  recoil delay falls at the same rate and must reach RecoilDelay × Aiming / 30 before the aiming delay starts to
  fall. Modelled for a shotgun (sights 2-8 tiles, Aiming 0, standing, no moodles): each 10 units of remaining
  delay cost about 8 points of hit chance at 5 tiles, 10 at 8 tiles, 12 at 10; under 3.5 tiles the point-blank
  rules make it matter little. Gunworks adds AimingTime × (0.15 − 0.01 × Reloading) to the delay
  during its reload (`ReloadAnim/Timing.lua`). **Every GoM gun sets it**: GoM writes `Aimingtime` and `Item.Load`
  matches keys with `equalsIgnoreCase`, so a case-sensitive grep finds none (that was the wrong reading: it claimed
  0 everywhere and GoM's multipliers dead). Shotguns are 40, pistols 18-40, rifles up to 70; GoM's stock, bipod,
  sight and laser multipliers work, as our HandlingTooltips lines say.
- **Gunworks fires through vanilla.** Its `Hook.Attack` wrapper (`CustomSystemHooks.lua` ~720, swapped for
  `RAFattackHook` at `OnInitGlobalModData`) sets the round's ammo profile and, for guns in GoM's `RPM.lua`
  (`RateOfFire.RegisterWeapon`), refuses a shot until 60000 / RPM ms have passed and runs bursts from OnTick; then
  it calls vanilla's `ISReloadWeaponAction.attackHook` → `DoAttack` → SwipeStatePlayer / CombatManager, so recoil
  delay, aiming delay and hit chance are vanilla's. Automatic fire is fast because its StatsFactory layer sets
  RecoilDelay 1 in RealAuto / RealBurst, leaving the RPM timer as the limit (and adds spread per shot). The
  break-action shotguns are not in `RPM.lua`: single shots limited by RecoilDelay 30 (`Shellholder` ×0.6).
- Sawing off barrels gives nothing back, in GoM (`SawnOffShotgunBarrels`, no OnCreate, barrels 3.0 → 1.0 weight
  for all three guns) and in vanilla (`SawOffShotgun`, 4.0 → 3.0; `RecipeCodeOnCreate.shotgunSawnoff` only moves
  modData and weapon parts). Smelting (42.21, `recipes_blacksmith_furnaces_i.txt`) goes by item tag:
  `base:smeltablesteel` small / medium / mediumplus / large add 1 / 2 / 3 / 4 uses to a steel crucible
  (`smeltIronOrSteel`), and a Steel Bar casts from 4 uses (`CastSteelBar`), so vanilla keeps weight (2.0 large item
  → 2.0 bar). Only the large recipe is tagged `Furnace`; small, medium and medium plus need `AdvancedFurnace`.
  `Base.SteelScrap` (0.5, `base:smeltablesteelsmall`) also forges straight into a Steel Chunk or Steel Bar Quarter at
  a primitive forge (`ForgeScrapIntoChunk` / `ForgeScrapIntoBarQuarter`).
- **Offcuts** (user, 2026-10-19: "we should just introduce new items"): `<GUN>_StockOffcut` (0.5, Junk, `isfirefuel`
  + `makewoodcharcoalsmall` like Unusable Wood; vanilla fire fuel burns by weight, `ISCampingMenu.getFuelDuration
  ForItemInHours`) and `<GUN>_BarrelOffcuts` (2.0, Material, `hasmetal` + `smeltablesteellarge`). Meshes from
  build_sawn_stocks.py (the body behind the stock cut; GoM's `<GUN>_BARREL_CLOSE` ahead of its sawn-off barrel's
  front, capped by `bmesh.ops.triangle_fill`, whose scanfill keeps the bore loops open as holes), icons from
  make_offcut_art.py (cameras fitted on GoM's barrel / gun icons). The stock recipe has no outputs (vanilla's gas mask
  filter recipes have none either); `SawnStock.Saw` hands the offcut over with `Actions.addOrDropItem`. GoM's barrel
  recipe gets `OnCreate = GunsOfTien_SawnStock.OnCreateBarrels` by `recipe:Load` at OnLoadMapZones (display name kept
  with `overrideTranslationName`, as ZomboidFixesB42's Barricade fix does).
- **Sawing sounds** (42.21): a craft's sound is its timedAction script's `sound` (`ISHandcraftAction:start` /
  `animEvent`, from `self.actionScript`, set in `new` from `craftRecipe:getTimedActionScript()`). Vanilla's
  `SawOffShotgun` plays `Sawing` (Carpentry, also SawLogs); the only other saw sound is `CraftMetalSawing`
  (SawSmallItemMetal). `CraftRecipe` resolves `timedAction` in `OnScriptsLoaded` (a later `Load` only sets the name)
  and has no setter, so GoM's barrel recipe gets our `GunsOfTien_SawOffShotgunBarrels` (timedactions_sawnstocks.txt,
  SawOffShotgun with the metal sound) through a wrapper of `ISHandcraftAction.new`; the stock cut keeps the wood saw.
  Vanilla's own Saw Off Shotgun (Base.Shotgun / DoubleBarrelShotgun) has the same wood sound on metal: a
  ZomboidFixesB42 candidate, not done.
- **Floor pose of a WorldStaticModel** (42.21 `ItemModelRenderer.init`, derived, not yet seen in game):
  transform = rotationZ(90 + flip) · [HandWeapons only: rotateXYZ(0, π, π/2)] · inverse(translate(world offset) ·
  rotateXYZ(world rotate)) · mesh transform, so a model point p lands at R⁻¹(p − offset): the offset is the model
  point put at the item's floor spot. GoM's part pose rotate 90 0 −90 gives (−(z − oz), x − ox, −(y − oy)), and the
  guns' pose (0.02 0.13 0 / 180 0 180, through the weapon fix) gives (y − 0.13, 0.02 − x, z): the gun lies on its
  side 0.02 up, about its half width, so the second axis is up. On that reading GoM's barrels (offset −0.2 0 0) hang
  0.2 above the floor and its magazines / scopes (offset 0) sink half into it. The offcuts use offset (min x, mid y,
  mid z): on their side, resting on the floor (`floor_point` in gen_scripts.py).
- Only the Double Barrel's sawn-off barrels have stats in GoM (AttachmentCustomStats: AimingTime set to 30 from 40,
  HitChance 70 from 65, ProjectileSpread 2.0 from 0.6, MaxRange 15 from 20; the three guns' base stats are the same);
  the Stevens / TOZ ones changed nothing but weight. SawnStock.lua registers GoM's own modifier list for them too
  (`CustomStatsAttachments.RegisteredParts`, `RegisterPart`; user, 2026-10-19: "give the same stats to the sawn off
  barrels and stocks"; the sawn-off stock's numbers were already the same on all three).
- Decided with the user (2026-10-19): any saw cuts the stock, no sandbox option, holster only with sawn-off barrels
  too, all three holster slots.
- `CraftRecipeData:getAllKeepInputItems()` lists the kept inputs (the gun); a recipe-wide `OnTest` is asked per
  candidate input item (`(item, character)`), so it refuses a gun already sawn. Vanilla's `SawOffShotgun` timed
  action / anim is reused. `HandWeapon.getActualWeight` adds every fitted part's `WeightModifier`, negatives too.
- Vanilla holster slots (ISHotbarAttachDefinition) take `attachments.Holster`: HolsterRight / HolsterLeft (belts) and
  HolsterShoulder; their body points are `holster_right`, `holster_left`, `ShoulderHolster` (AttachedLocations.lua),
  and an attached item's own model attachment of the same name is applied, so the stockless models carry those three
  with `rotate = -180 0 -180` (GoM's pistols, which those points are made for, are modelled upside down). Hang
  position and clipping into the leg (the gun is about twice a pistol's length) are unchecked.
- Cut planes (game y, z; `CUTS` in build_sawn_stocks.py) were read off textured side renders: Double Barrel
  (-0.028, 0.010)-(-0.047, -0.052), Stevens (-0.022, 0.006)-(-0.045, -0.046), TOZ-34 (-0.037, 0.009)-(-0.049,
  -0.044). The cap's UVs copy the middle of the largest walnut-coloured stock face along the cut (taking each corner's
  UV from a neighbour face squeezed it into a strip over dark seams).

## Compact SMG stance (2026-10-23, full coverage built, not loaded in game yet)

Superseded on 2026-10-28 by one short SMG stance ("Animations are generic" above): the per-gun sets below no longer
ship, but how the Uzi set (now ShortSMG) was built still holds.

- User's choice ("Option B"): the full-size Uzi, Mini Uzi and GoM's MP5K share one custom idle / aim stance; the
  Micro Uzi and Post-93's P90 stay pistol-held (the MP7 was not decided). Option A (just make them two-handed and
  use vanilla's rifle stance) was declined. Draft stills: `scripts/anim/compact_stance.py` (sheet in
  tmp/anim/stance/).
- Gunworks has a held-pose registry for this: `WeaponSystems/Utils/GripAnim.lua` (Gunworks_gang_framework 42.13).
  `GripAnim.RegisterWeapon(fullType, { animId = ..., matches = fn|nil })`; while a registered gun is in the primary
  hand Gunworks sets the animation variable `GunworksGripAnim` = animId (local player from OnPlayerUpdate, remote
  players from a 3-tick OnTick sweep in MP, only on change). AnimSet nodes gate on it: Heavy Ordnance (workshop
  3802070967) adds `GunworksGripAnim == "RPG"` + `Weapon == firearm` with `m_ConditionPriority` 100 to ~90 copies of
  vanilla rifle nodes (idle, aim, aim-strafe, strafe, walk, run, sprint, ranged Auto / Burst / Single / Empty, shove,
  bumps, climbfence, falling, getup, sitting, ext, emote) and ships 114 `RPG_*.x` clips (23 MB, ~200 KB each).
- The class decides every state we do not author (TienInspectWeapon CLAUDE.md: `TwoHandWeapon` alone picks
  `firearm` vs `handgun` for guns), so all three must be two-handed: the MP5K and the Mini Uzi get
  `TwoHandWeapon = true` and are drawn upright in the hand by a `Bip01_Prop1` attachment `rotate = 0 180 0` on their
  model scripts (GoM's MP5K model redeclared whole in our scripts: a second block resets it). 394 vanilla player
  nodes are class-conditioned; outside idle / aim / aim-strafe / strafe / ranged they are whole-body clips.
- Bob's arm reaches 0.274 from the shoulder; the MP5K's vertical foregrip is ~0.18 ahead of its grip, the Uzis'
  handguards ~0.07, so a muzzle-down forward low ready leaves the MP5K's foregrip out of the left hand's reach. The
  stance is one body pose with two left-hand places: two clip sets ("Uzi" for the Uzi and Mini Uzi, "MP5K"), two
  Gunworks animIds. The draft places were scanned over both sets (reach, wrists, clearance, a muzzle-down
  preference): low ready across the body (grip ch(0.06, 0.60, 0.08), muzzle (-0.8, -0.3, 0.5), twist 15), aim =
  the rifle aim's torso with the grip at eye + ch(0.08, -0.10, 0.18), twist 15; the MP5K hand is turned (0, 0, -60)
  round its foregrip.
- Aim, chosen 2026-10-23 out of three drafts (square push-pull, compressed square, cheeked): the cheeked one, "more
  like the rifle's, except the hand controlling the recoil should move in closer". So the gun takes the rifle aim's
  place exactly (rig `at_aux`: the right arm and wrist are vanilla's, -99/-93/-67), and the left hand is slid back
  from the rifle's 0.20 ahead of the grip to the gun's support place with vanilla's left-wrist angles kept (3/54/20;
  `lgrip_with_wrist`: solve, set the wrist, re-anchor the palm, a few rounds). The first draft (the gun placed by
  hand, pushed 6 cm out, twist 15) was "terrible". The MP7 joins (user): its own set, support 0.142.
- Then (user: "copy the right hand style in the vanilla one and just adjust the left arm. still looks terrible"):
  `at_aux` still re-solves the right arm (the rig picks its own elbow) on the idle's legs, so the stance is now built
  on vanilla's own clips: every bone and Bip01_Prop1 as the vanilla rifle clip has them, only the left arm solved
  onto the gun's support place (`scripts/anim/stance_vanilla.py`, `left_only`), the hand turned about the gun by a
  scanned amount per set and pose (`TURN`; left wrists then within ~20 degrees of natural). The idle follows the
  same rule (vanilla's rifle idle, left hand pulled in). This is also how the full clip set gets built: per frame
  of each vanilla rifle clip, left arm only. The Uzis then hold forward like the MP7 / MP5K (user: "uzi should use
  the style of mp7 and mp5k"): support (0, 0.130, -0.014), under the front of the receiver, as far forward as the
  Mini Uzi allows (receiver ends ~0.13, its folded stock's butt hangs under the barrel at 0.10-0.11); turns Idle
  (0, -15, 15), Aim (0, 0, 0). The aim is approved (user, 2026-10-23: "the aiming are now correct").
- Idle muzzle down (user: "the guns should be pointing downwards rather than up"): no vanilla rifle idle points down
  (Bob_IdleRifle / NoAim / Ext / Sneak all aim up-left; only Bob_IdleAimRifle_Down(75) do, with the aiming hunch).
  With vanilla's rifle grip a relaxed right wrist puts the barrel ~50 degrees above the forearm, so a down muzzle
  needs the forearm hanging and the right hand at the hip, from where the left hand cannot reach the gun's front:
  a scan (`idle_down.py`, grip places x directions x twist x lean, the left hand anywhere from 0.04 along) found only
  4 reachable two-handed holds 25+ degrees down, all with the left hand against the right (0.04) and both wrists
  1.3-1.6x past their natural range. Tipping the two-handed hold down gives ~5 degrees before the right wrist stops it.
  What fits: one-handed, muzzle 53 degrees down-forward at the right side, the left arm hanging (vanilla's handgun
  idle body, natural wrists): `idle_down.py` O1, shown to the user.
- User then: "keep the gun close to themselves. like the vanilla one except the right hand is on the upper side and
  the left hand on the lower side" (vanilla's diagonal reversed). Vanilla's clips do not keep one hand-to-gun
  relation: Bip01_Prop1 hangs off Bip01 and the hand bones barely move (the right wrist reads (-16, -5, 0) = rest in
  Bob_IdleRifle, Bob_IdleAimRifle, walk, run), so each clip holds the gun at its own angle in the hand. The rig's
  `grip_r` (from its base clip) is only one choice: with the rifle idle's, the reversed diagonal asked a -100 degree
  right wrist; with the pistol idle's (barrel along the forearm, composed with the half turn for an upright gun) it
  is natural (`idle_down.py` X / X2, `x_rig`). X: grip ch(0.02, 0.58, 0.04), muzzle 38 down to the forward-left; X2:
  grip ch(0.02, 0.58, 0.12), muzzle (-0.8, -0.5, 0.3), 30 down, across the belly like vanilla's; twist 15, left hand
  turned per set (scanned), every wrist natural, nothing in the body. User: X2 "terrible and not natural", X "better,
  but keep the gun closer": X3 = X's 38 degrees with the grip at ch(0.06, 0.58, -0.02), the gun's middle 6 cm nearer
  the chest (the closest a scan found with gun and arms out of the body, every wrist natural); left turns Uzi
  (45, 30, -15), MP7 (45, 15, -15), MP5K (30, 15, -30). Not what the user meant: "closer" = "less pointing forward
  and more to the side". S1: grip ch(0.06, 0.56, 0.0), muzzle (-0.77, -0.61, 0.20); S2: grip ch(0.02, 0.56, 0.0),
  muzzle (-0.78, -0.62, 0.12); both 38 degrees down, twist 0, the gun lying across the front of the belly
  (`idle_down.py` ID_S); every wrist natural, the gun touching the body by at most 0.006. Their top faced forward,
  so the magazine pointed into the belly (user: "rotate the held gun so that the mag doesn't hit the body"). ID_M:
  S1's direction rolled so the magazine hangs down and a little forward (top = -(0.25, -1, 0.2)); the gun has to
  sit ~10 cm further out (grip ch(0.02, 0.64, 0.10), twist 15) or the hanging magazine hits the belly; ~40 degrees
  off straight down is the least with the gun on a 38-degree diagonal; right wrist (-43, 5, -35), left turns Uzi
  (30, 0, 0), MP7 (30, -15, 0), MP5K (45, -15, 0), nothing in the body. The rig's soft wrist limit rolls a gun back
  to the wrist's comfort when it can: scan rolls with `limit` off and check the wrist the roll really asks. Approved
  ("alright this is good").
- Built (`scripts/anim/compact_build.py`, ~1 min a set): 33 clips per set from vanilla's rifle clips frame by frame
  (`CLIPS`: idle + heavy breathing, 4 sneak idles, aim at 5 pitches, IdleToAim / AimToIdle, 12 strafe-aim, 6
  attack, 2 shove), named GunsOfTien_Compact<Set>_<vanilla name without Bob_>; ~190 KB each, 5.7 MB a set. Kinds:
  aim = vanilla untouched but the left arm; idle = the approved hold rigid with the chest plus the vanilla gun's
  drift relative to it, both arms solved (rig `grip_r` = the pistol idle's relation, wrist easing off: the hold is
  already a landed pose); transitions = idle-kind and aim-kind poses blended bone by bone by smoothstep progress,
  the gun put back in the right hand with the blended hand relation, the left arm re-solved. A per-frame de-clip
  (`Declip`: elbows swung outward in 0.025 steps, then an idle-kind gun moved forward) keeps arms at contact level;
  left over: the Uzi / MP7 heavy-breathing idle's left arm 3.3 / 3.5 cm in (vanilla 1.0), the shove's first frame
  2.6-3.1 cm; the upward aims sink the gun's rear 2.7 cm into the face exactly as vanilla's rifle does.
- Nodes (`scripts/anim/compact_animsets.py`, system python3): 18 per set, vanilla's rifle nodes (idle, sneak idles,
  aim, aim-strafe, strafe + slow, ranged firearm Default / Auto / Burst / Single / Empty*, shoveAim) flattened with a
  port of PZXmlUtil.resolve (42.21: a child element replaces the parent's of the same tag and x_name, an unnamed one
  the parent's of the same tag at the same index among that tag, the rest is appended), our clips swapped in, the
  GunworksGripAnim condition + m_ConditionPriority 100 added, transitions into replaced nodes copied to ours.
- Shipped into the mods' anims_X/Bob and AnimSets/player (main: Uzi + MP5K sets, 11 MB; Post-93: MP7, 5.7 MB).
  Lua: main `GunsOfTien/CompactStance.lua` (Gunworks.RegisterWeapon(fullType, { grip = { animId } }) at OnGameBoot,
  which only reaches GripAnim; `turnUpright`: the Bip01_Prop1 point (0 180 0) on the model script + DoParam
  TwoHandWeapon = true, at OnGameBoot / OnInitGlobalModData) for the Uzi, Mini Uzi, GoM's MP5K; Post-93's own file
  for the MP7A1 / A2. The turn applies in every hand clip, so the pistol reloads of the Mini Uzi (UziGrip), MP5K
  (GoM's handgun2) and MP7 (MP7A1) draw those guns upside down until their reloads are rebuilt on the stance.
  Not covered (rifle class fallback): walk / run / sprint / sneak-walk, vehicles (player-vehicle AnimSets), fence
  vaults, falls, sitting, emotes, ext fidgets. The MP7's folded foregrip (and the A2) use the unfolded-grip set.
- After the in-game test (user: "move the gun closer to the body without rotating the gun"): the hold slid straight
  back 4 cm (MP5K also 3 cm right; `idle_down.py` ID_MC) is the most before the gun's rear, high on the right chest,
  goes into it; the gun's mean stand-off (clearance.gap against chest + pelvis) drops 8.5 -> 5 cm (MP5K 10 -> 5.5).
  Closer needs the front end turned in (the gun angles slightly forward). The gun / magazine check must include the
  pelvis (`clearance.Body(arm_ob, BODY | {"Bip01_Pelvis"})`): the default body is the chest and up. Built in
  (`SETS[set]["closer"]`, applied to `Stance.hold_rel` in the character's frame); approved ("the closer is good now").
- Walking and running (user: "when walking and running, let's keep the gun closer still"): the hold adds vanilla's
  rifle drift relative to the chest, and vanilla carries its rifle out and up on the move (walk +4.5 cm out / +5 up,
  run +12 / +14, sprint +10 / +18, sneaking +11 / +20). `hold_at` keeps 20 % of the outward part and 40 % of the
  upward part (`DRIFT_OUT_KEEP` / `DRIFT_UP_KEEP`, env overrides for drafts); lowering only the outward part was not
  enough, because with the full rise the crossing left arm meets the chest and the de-clip pushes the gun back out.
  Result (gun's mean distance out from the idle hold): walk 5 -> 1.5 cm, run 12.5 -> 4, sneak 11 -> 2, sprint 11 -> 5
  (the sprint's arm swing still makes the de-clip push it out to 11 cm at times). Not while crouched (user: "The
  crouch Short SMG stance have a bad left arm"): the chest leans 53-85 degrees in the sneak clips (walk 14, run 43,
  sprint 40), and there vanilla's drift is what keeps the gun out in front of the hips; cut back, the gun sat in the
  belly and the left forearm crossed over it. Clips named Sneak / Sgun (`CROUCH_NAME`, 14) keep all of it; a lean
  threshold cannot split them (running 43, the sprint start reaches 64). That alone left the wrists broken (user:
  "the wrists are unnatural"): the hold turns with the chest, so a 53-85 degree lean took the right wrist to 70-85
  degrees of bend and the left to 60-70 (rig limits 50 / 45; the approved idle has the right at 41). Crouched clips
  now (1) turn the gun with vanilla's gun against the chest (`follow_turn`, its rotation change in the chest's frame,
  about our gun's own origin), then (2) `settle_turn`: a local search per frame over a turn about the grip (X, Y, Z,
  steps 8 / 4 / 2, at most 40) for the least `wrist_cost` of both hands, plus a little per degree away and a lot per
  hand falling short, (3) `plan_turns`: run twice (the second pass starting from the first's end), then smoothed
  (kernel 1-2-3-4-3-2-1, twice, circular for loops). Without the smoothing the search hopped between comfortable turns
  (up to 18 degrees a frame, a 16-degree loop seam); with it, at most 5 degrees a frame and no seam. Every crouched
  clip of all three sets: wrists within the limits (right bend 25-44, left 5-29 / twist 32-55, vanilla's own crouched
  shotgun twists 50), arms at most 1 cm in. The gun points down and forward more than the standing hold.
  Then (user: "the sneakrun seems to be snappy at the end of the animation and replaying it to start"): the clips
  loop exactly (pelvis-relative seam 0, no quaternion sign flips, the packs end at 3200 ticks like vanilla), and the
  gun moved smoothly; the arms did not. With all of vanilla's outward drift the hands sat at full reach (shoulder to
  hand 0.27 of the arm's 0.274), where a hand moving 1 cm swings the elbow 2.5-3 cm (upper arm 10-14 degrees in a
  frame, vanilla's at most 5): the elbow snapped twice a cycle, once at the loop. Crouched clips now keep 30 % of
  the outward drift and all of the upward (`CROUCH_KEEP`): reach 0.17-0.24 (vanilla 0.13-0.20; the MP5K's left
  0.23-0.27, its foregrip is 18 cm out, also at 0 %), elbow steps at most 1.4 cm (vanilla 1.5), the gun carried
  more level, muzzle forward. Tried and dropped on the way: a mean / per-frame-free gun turn, riding vanilla's gun
  rigidly, smoother turns and elbow swing hints (the rig's `swivel_hint`, kept: the swings were already smooth).
  Sneaking has two node families, both firearm-gated and covered: in the open (sneakidleRifle, sneakWalkRifle,
  sneakRunRifle) and by a wall (`nearWallCrouching`: sneakIdleLowRifle, sneakWalkLowRifle, sneakRunLowRifle).
- Coverage check (2026-10-23): every node gated on Weapon == firearm (vanilla 248, Gunworks 6) and the one rifle node
  gated only by its state (`shoveWithFirearm/firearm/FirearmShoveNoAim`, the shove without aiming: the game enters
  that state only with a gun; `GUN_STATE_NODES`), 255 nodes a set. Left on vanilla on purpose, as for any weapon:
  states with no rifle node at all (turning in place, 90 / 180 turns, climbing windows / walls / ropes, opening
  windows, hit / shot reactions, knock-downs, falls, death, corpse dragging, animals, fishing, fitness, beds) and
  the actions (looting, crafting, `AttachItem_Back` / `DetachItem_Back` with `Bob_Equip_Rifle_Back`): the gun bone
  follows vanilla's hand there, and the turned guns sit 4-9 cm off it (the bore turn).
- Node names in transitions match ignoring case (AnimNode uses equalsIgnoreCase; vanilla's transitions name
  "walkRifle" / "sneakIdleRifle" for the nodes "walkrifle" / "sneakidleRifle"). The inventory compared exactly and
  missed 4 transition clips (WalkSneakToStop_Sgun, IdleToWalk_Rifle, WalkAimRifleToWalk, ActionToSitIdle_rifle) and
  their copies aimed at our nodes; now lowercased: 244 clips, 248 a set with the reloads. Gun in the body over 2.5 cm after
  it: BiteReact_Rifle_R ~6.5, EmoteWipeRightLegRifle ~4, IdleAimRifle_Up75 2.7 (all the same with the full drift; the
  Up75 aim is vanilla's own), and new with it the failed running vault on the MP7 / MP5K sets (4-5 cm, one moment).
- Tracers off the barrel (user: "the projectiles do not line up from where the bullets are coming out"): the game
  shoots from the gun bone × the model's `muzzle` point without the model's `Bip01_Prop1` point (TienInspectWeapon
  CLAUDE.md), so the turned guns' tracers started 2 × the muzzle's z off the drawn barrel (MP5K 8.9 cm, Mini Uzi 4.8,
  MP7 4.1; the full Uzi is modelled upright and was right). Fix without Java: `turnUpright` turns them about their
  bore (point offset (0, 0, 2 × muzzle z), read from the model's `muzzle`), which also keeps the flash on the muzzle,
  and `compact_pack.py` moves the gun bone of those sets back by as much (`compact_animsets.TURNED_SETS`: set -> muzzle
  z), so the drawn gun stays in the hands. A set's clips only fit guns turned alike, so the Uzi set is packed twice:
  "Uzi" (the full Uzi) and "UziT" (`SOURCE_SET`: the Mini Uzi, the MP7A1 folded, the MP7A2; z -0.0222, the mean of
  -0.0238 and -0.0205, 3 mm either way), with its own reload nodes (GunsOfTienCompactUziT); +18 MB in the main mod.
- One-handed after equipping (user: "MP7 and mini uzi when equipped is using the handgun style. when i unfold stock,
  it corrects itself"): `TwoHandWeapon` alone still lets a gun sit in the right hand only ("Equip Primary", or any
  equip passing twoHands false), and a gun not in both hands is a "handgun" to `WeaponType`, so none of the stance's
  firearm nodes play. Gunworks' stock fold re-equips with `CallSyncHandWeaponFields` (both hands when
  `isTwoHandWeapon`), which is why folding fixed it. Every vanilla rifle and the full Uzi also have
  `RequiresEquippedBothHands = true` (instance field copied from the script at `InstanceItem`, not saved; forces
  twoHands in `ISEquipWeaponAction:new`, hides "Equip Primary"), as do all of GoM's two-handed guns (16 of 16
  assault rifles, 4 of 4 two-handed SMGs); only the guns we made two-handed (Mini Uzi, MP7s, GoM's one-handed MP5K)
  lacked it.
  Our Mini Uzi and MP7A1 / A2 scripts declared both flags for a while (user: "let's require them to be 2-handed").
- One hand allowed again (user, 2026-10-26: "when you hold MP7 and other guns we have in one hand, they were
  reversed ... they can be held in one hand, but they can also be held with 2 hands"): the turn is a Bip01_Prop1 point
  on the model script, so it applied in one hand too, where the pistol clips (which these models are made for) drew
  the gun upside down. Only the turned guns had it (Mini Uzi, MP7A1 / A2, GoM's MP5K); the full Uzi is modelled
  upright, the Micro Uzi, P90 and pistols are never turned, the SCARs, UMPs and M249 need both hands. Fix
  (`lua/shared/GunsOfTien/OneHand.lua`): `TwoHandWeapon` only (no `RequiresEquippedBothHands`: hotbar and Equip Two
  Hands still go to both hands, "Equip Primary" is offered), a second model without the turn per gun (`MINIUZI_1H`,
  `MP7A1_1H`, `MP7A2_1H` from the generators; `GunsOfTien.MP5K_1H` in `models_onehand.txt`, a copy of GoM's block
  that `OneHand.copyModel` refreshes from GoM's live script with `ModelScript:Load` at boot and world load: mesh,
  texture, every point but the turn), and every client swaps `setWeaponSprite` for a gun of its own players and every
  other player it sees while it is in the primary hand alone (back when it leaves that hand and on `OnSave`, so items
  keep the script's model; nothing is sent, the hands sync). Reload in one hand: a Gunworks handler with `matches`
  (tried before the full type index) per gun: the Mini Uzi the Micro's "UziGrip", the MP7s the old "MP7A1" pistol
  clips (restored from git, no hand magazine), the MP5K GoM's "handgun2" (style none, 1.296 / 1.296 / 1.0 s).
  Gunworks' `Animations.CallSyncHandWeaponFields` re-equips both hands for any two-handed gun after every magazine
  insert / eject, fold, part swap and, for guns in GoM's `AnimationsFiring` (the MP5K: `Bolt`), every shot, so it is
  wrapped to put back what the other hand held for these guns in one hand. The engine's one-hand rules for a
  two-handed weapon apply (`CombatManager.applyOneHandedDamagePenalty`: damage x `DAMAGE_PENALTY_ONE_HANDED_
  TWO_HANDED_WEAPON_MULTIPLIER` 0.5, in `IsoGameCharacter.processHitDamage`, ranged included; combat speed x 0.77).
  Renders of the one-hand hold: `HOLD_EVERY=1000 blender ... hold_preview.py -- <Bob> <out> miniuzi mp7 mp5k`
  (pistol clips, no turn: all three upright).
- Shooting and dry firing with Gunworks (in-game test: "shooting will move the left hand like vanilla way", seen
  firing an empty magazine): Gunworks sets the `FireMode` variable to `RealSingle` / `RealAuto` / `RealBurst` for every
  gun it fires, so vanilla's FirearmSingle / Auto / Burst / Empty* (FireMode Single / Auto / Burst / "") never play
  with it; its own six nodes do (F `AnimSets/player/ranged/firearm/Firearm(Empty)Real*.xml`, vanilla rifle clips,
  player only). Dry fire is no separate action: `ISReloadWeaponAction.attackHook` runs `DoAttack(0)` +
  `setRangedWeaponEmpty(true)` and the ranged state picks the Empty node (Java `WeaponEmptyCheck` only plays the
  click). `compact_animsets.MOD_ANIMSETS` adds Gunworks' AnimSets to the inventory (x_extends resolved against
  vanilla; its spear nodes extend nodes we lack and are skipped): 254 nodes, the same 240 clips.
- Then full coverage (user: "in known gaps, let's produce all the animations to match this"). Inventory
  (`compact_animsets.firearm_nodes` / `firearm_clips`): 248 vanilla nodes resolve to Weapon == firearm (player and
  player-vehicle), playing 240 clips (each node's own and 2D-blend clips, and its transitions into firearm nodes or
  with no target). 104 of them are generic (gestures, pains, signals, 2H-melee and 1H clips) played through bone masks
  that take the arms (25-100 %) but never Bip01_Prop1 from the clip: the gun bone comes from the state underneath, so
  those are converted on the plain hold (no drift) with the left hand free. All 240 are converted per set and every
  firearm node gets a copy per set (with Gunworks' six: 762 XML).
- One rule per frame (`compact_build.frame_pose`): aim clips (by name, and the vehicle aim clips) = vanilla but the
  left arm; others by how aimed vanilla's rifle is (its place relative to the chest between the idle and aim places,
  times its muzzle agreeing with the aim's: port arms sits near the aim place muzzle up), carried = the hold, between
  = both poses blended as the transitions; the left hand follows vanilla's on / off its rifle (gestures keep vanilla's
  arm). Declip then swings elbows, moves a carried gun forward along the chest's real forward (a bone's local axes are
  not the character's: measured once on the idle), then eases the left arm toward vanilla's own by the least amount
  that clears.
- Packing: every AnimationSet of a .x file is a clip (TienInspectWeapon CLAUDE.md), so each set ships as 7 files of
  40 clips behind one Bob mesh, every key kept (`compact_pack.py`, ~26 MB a set, main mod 85 MB, Post-93 31 MB). The
  game's importer (a jassimp harness) read 40 animations from a pack. Keys were first reduced (within 2e-4 / 2e-5,
  ~18 MB a set): in game the sneak run then jumped for one frame at every loop point (user: "snappy at the end of
  the animation and replaying it to start"; a 60 fps recording showed the arms and gun wrong on one frame every 43-44
  frames = one 0.725 s cycle; vanilla's M16 sneak run had none; the Uzi set packed with every key ran smooth). The
  clips' data looped exactly and the cause was not found in the game's code, so every key is kept
  (`COMPACT_PACK_LOSSY` = a clip-name regex still reduced, unset).
- MP7 sets by Gunworks `when`: the A1 with GunsOfTienPost93.MP7A1_Integrated_Foregrip_Deployed = "GunsOfTien_CompactMP7",
  otherwise (folded, and the A2) "GunsOfTien_CompactUzi" (the hand under the handguard sits within ~1 cm of the Uzi's).
- Reloads on the stance (`smg_reload.py` specs compact_uzi / compact_mp5k / compact_mp7: rifle rig on the set's own
  idle / aim clips, pistol-modelled guns turned with FLIP, places from scans for the stance's hand relation:
  `COMPACT_PLACES`): Uzi set work ch(0.04, 0.70, 0.08) / rack ch(0.10, 0.68, 0.10); MP5K the approved places, the
  lever taken from the left side (turn (15, 165, -75)); MP7 rack muzzle turned up and right so its rear T handle comes
  to the left hand (muzzle left, the arm crossed the chest 4-5 cm in), and its aimed rack comes off the aim
  (`rack_in_aim=False`; in the aim the handle is by the cheek, the hand went 8 cm into the face). Action nodes
  (`compact_animsets.write_reload_nodes`, player + player-vehicle): WeaponReloadType GunsOfTienCompact<Set>, magazine
  swap 10/36 (unload) and 30/45 (load), rack 12 / 19 (rackBullet before ejectCasing) / 22 of 36, the aimed rack back to
  IdleRifle_GoTCompact<Set> (the MP7's to both its sets) with the set's AimToIdle clip. Lua: Uzi.lua (Uzi, Mini Uzi;
  the Micro keeps UziGrip), CompactStance.lua (GoM's MP5K, replacing its handgun2 entry: Gunworks' registry replaces
  by id = full type), Post-93 Guns.lua (MP7s); all style "attachments" with the magazine shown in the hand (the MP7's
  old "no magazine in the hand" was for the pistol clips); `ReloadAnim.GunsOfTienPointMag` lists the animIds whose
  magazine part spec Uzi.lua's wrapper points at the magazine involved. The rig gives way silently when a key is out of reach (the gun moves to where the arms end):
  print `r.warnings` when drafting places.
- Aim in / aim out (user, 2026-10-23: "aiming in has a twisted wrist on the left hand. aiming out jitters the left
  arm"): a clip's rig takes its natural wrists from **its own file's bind pose** and its elbow directions from its
  first frame, and vanilla's files differ (forearm-to-hand bind: Bob_IdleRifle / Bob_IdleToAim_Rifle 60 degrees (L) /
  76 (R) off Bob_IdleAimRifle / Bob_AimToIdle_Rifle, Bob_WalkRifle a third). So AimToIdle solved its carried half
  against the aim's references: the left elbow flipped to a second solution at frame 8 (19-23 cm in a frame, all
  sets), stayed winged out with the wrist twisted 55-73 degrees and ended 7-9 cm off the idle clip; IdleToAim ended
  1-2 cm off the aim clip on the MP5K / MP7. Now (`Stance.refs`, `joins_idle_and_aim`) the two clips that join the
  idle and the aim solve carried frames with Bob_IdleRifle's references, aimed ones with Bob_IdleAimRifle's, blended
  between, the left elbow's swing steered from the carried solution's to the aimed one's, then smoothed with the ends
  pinned: elbow steps at most 4-5 cm (the raise's own speed), both ends equal to the idle / aim clips, and the game's
  cross-fade (sequence.py's blend, 0.5 s / 1.5x in, 0.3 s / 1.2x out) keeps both hands within 1 cm of the gun.
  Only these two clips changed (a wider rule caught 62, runs and sneaks among them); they were swapped into the
  packs in place (a rebuild of the idle / aim matched the shipped clips to 2e-6). No defect was found in the aim
  in beyond its end on the MP5K / MP7: its left wrist moves steadily into the approved aim, within vanilla's range.
- Encumbered walk (user, 2026-10-23: "the encumbered walk is not yet updated to match with the rest of the 'closer
  gun to the person' feel"): encumbered = WalkSpeed low = the walk blend's `Bob_WalkSlow_Rifle` corner (defaultWalk
  m_Scalar WalkInjury, m_Scalar2 WalkSpeed). Ours held the gun 10.9 cm out (the walk 1.4): the same per-file
  references swung the left elbow 65 degrees (the walk's 25), the forearm went 3.5 cm into the belly, and the
  de-clip pushed the gun forward to its 10-step (10 cm) limit without clearing it. 52 of 60 carried standing clips
  did that with their own references (limps, IdleRifleExt01-03, heavy breathing, IdleNoAim / WalkNoAim / strafe
  NoAim, walking backwards, sitting, bites, emotes; 10-13 cm out). `idle_refs_clear` now gives a carried clip
  (not crouched, not generic) the idle clip's references when they keep the left arm shallower on the plain hold
  (sampled, before de-clip); the walk, run and sprint stay on their own (shallower there; rebuilt identical to
  2e-6). Slow walk 1.3 cm out, the fidget 0.4, heavy breathing 1.0, walking backwards 1.8. Of the 72 carried
  clips 51 (Uzi) / 50 (MP7) / 48 (MP5K) switched, the sprint and sprint-into-aim among them on the Uzi / MP7 (11.6
  -> 5.2 cm at most); none came out further than shipped (compare a turned set's packed clip only after undoing the
  pack's gun-bone move). Still 6-10 cm out: the diagonal unaimed walks (WalkNoAim / WalkBwdNoAim _DiagL) and the
  left heavy limp on the MP7 / MP5K, sitting on the ground (9), vaults (5).
- Audit of every clip (2026-10-24; scratch scripts audit.py / audit_generic.py / eval_generic.py / node_audit.py,
  not in the repo): per clip and set, against vanilla's own clip, arms in the chest, the gun in chest + pelvis, the
  gun out on carried frames, each hand off its grip while vanilla's holds, wrists against the idle's natural range,
  the largest per-frame jerk of elbows, hands and gun, loop seams; nodes for conditions, ids, coverage, transitions.
  Artifacts to ignore: aimed clips keep vanilla's right hand (a butt strike moves the gun in it), a carried frame's
  right hand sits on a grip blended between the idle's and the aim's, reloads let go on purpose, and a **masked**
  node (emotes, pains, signals: `m_SubStateBoneWeights`, Bip01_Prop1 weight 0) takes the gun and the unmasked bones
  from the state underneath, so a generic clip can only be judged blended over it. Vanilla's own sneak walk nodes
  name a node `sprintRifle` that does not exist (it is `sprintFirearm`); our copies inherit it, harmless.
- Fixes from it (same day): (1) `Scorer` + the variant chooser in `build_clip`: each carried clip is built with its
  own and with the idle's references, each with and without elbow smoothing and `filter_poses` (the gun's place on
  the chest, each hand's hold and each elbow's place smoothed, then both arms solved again onto them, elbows steered
  to the smoothed places; smoothing bone rotations let the left hand drift 3-10 cm), scored as the audit does; the
  shipped choice is kept unless another scores better by more than 1. Jitter flags 108 -> 0 (tree walks 38 -> 2 cm
  of jerk, running bump 14 -> 4, sprint 11 -> 3), gun held out 137 -> 47, left hand letting go 58 -> 24, wrists
  40 -> 24; the approved idle, walk, run and every crouched, aimed and transition clip unchanged (1e-6). Traded:
  bite reactions and the shotgun run vault let the left hand go 3-4 cm more (their 11-16 cm jerk gone), the tree
  walks hold the gun 1.5-2 cm further out. (2) Masked generic clips are built once per (context, masks) they play
  with (`compact_animsets.generic_variants`: 126 clips -> 149 copies `<clip>__Stand / __Sneak / __Ground /
  __Chair`), each solved in the blended pose the game draws over the context's idle (`generic_masked_solve`: IK in
  the blended skeleton, each arm bone's local then un-blended through its mask weight, `unmask`); the node writer
  points each masked node at its own copy (604 node files, one line each). Right hand off the gun in the game's
  blend, median: standing 2.9 -> 0.5 cm, sneaking 14.3 -> 1.1, ground 11.8 -> 1.5, chair 7.1 -> 0.7 (vanilla's own
  rifle 7-15); left worst sneaking 24.7 -> 5.1. Left: 7 chair copies (wiping the brow, holding the head) 6-8 cm
  against vanilla's 3-4, whose masks leave the right hand bone to the chair idle. Sets are now 271 clips (28.4 MB).
  Partial rebuilds are assembled from the shipped packs (scratch assemble.py: unchanged clips extracted with the
  pack's gun-bone move undone, compact_pack.main, compact_animsets.build, CRLF kept).
- Sprint arm (user, 2026-10-24: "the full sprint animation ... there are times the left arm go in the body"): on the
  half of the stride where the right arm swings back the gun crosses the belly and the left forearm lay along the
  chest at CONTACT (0.021-0.022: the bone's centre line on the skin, half the forearm inside, more under a jacket),
  and the de-clip's body is the chest only, so the belly took the MP5K's 3.4-3.6 cm unseen; vanilla's sprint arm never
  touches (0.000). `compact_build.SPRINT_NAME` clips (Sprint_Rifle, SprintToStop_Rifle, SprintToAimRifle, standing)
  are de-clipped and scored against chest + pelvis to `SPRINT_CONTACT` 0.008: arm 0.021-0.034 -> 0.008 in every set,
  scores better on all three (gun ~1 cm further out on average). Fully clear (0.002) let the left hand slip 4 cm off
  the gun. IdleToSprint_Rifle keeps CONTACT (still 2.2 cm in, MP5K 3.6 in the belly for a moment): cleared even to
  0.016 its left hand jerked 2.5-3 cm a frame more than the shipped clip. The run (in the sprint node's blend at
  WalkSpeed 0.5) reads 0.015-0.022 too and was left as approved. Swapped into the Pack5 files in place (each clip
  rewritten as compact_pack.main does, gun bone moved for the turned sets; a round trip of the shipped clip was
  byte-identical).
- preview11.png (2026-10-24): four game characters in the stance (survivor + Uzi carried, police + MP5K aimed, a
  woman in a hoodie + MP7 sneaking, a soldier + Uzi running), `scripts/anim/render_stance_ad.py` (Blender: dressed
  from the game's own files, posed from the shipped clips; `OUTFITS` / `SHOTS`) then `make_workshop_art.py
  preview11`. How the game dresses a character (media/clothing/clothingItems): items with `m_BaseTextures` only
  (shirts, T-shirts, boots, shoes) are textures over the skin (`textures/Body/MaleBody01..`), items with
  `m_MaleModel` / `m_FemaleModel` are skinned meshes with a `textureChoices` texture (jackets, trousers, vests,
  hoodies; `TINT` items tinted), `m_Static` items (helmets) are static meshes on `m_AttachBone`, hair is a skinned
  mesh from media/hairStyles with `F_Hair_White` tinted. Body masks (parts hidden under clothes) were left out.
- A sandbox option to turn the stance off was built and dropped (user, 2026-10-26: "there's too much work"), its
  work discarded. The user wanted off to be a look only. What a one-handed (pistol class) gun would
  change in 42.21: the off hand free (flashlight, TienDualwield's dual handguns); vehicles (`CombatManager` ~2681: a
  driver with a two-handed gun hits nothing; `IsoPlayer` ~4389: a driver aiming a FIREARM loses control; passengers'
  angle penalties x1.5); reload times (Gunworks ends a reload on the clip's *Finished event in SP, times the server on
  the profile durations in MP); shot / shove timing (`m_TimePc` events of the node's clips); root motion
  (`doDeferredMovement`, Translation_Data). HANDGUN and FIREARM share attack types, damage, hit and crit rules, and
  Gunworks' reload `style` is visual only. The stash's way: keep the guns two-handed, a grip `GunsOfTien_PistolHeld`
  whose 255 nodes are the stance's again with vanilla's pistol clips (handgun twin node, else the weapon-agnostic one,
  a table for the shooting nodes; `scripts/anim/pistol_animsets.py`), clips differing in length or Translation_Data
  retimed to the rifle clip's span with its Translation_Data (49 of 191, 5.9 MB), reloads played to the stance's
  durations with `m_SpeedScaleRandomMultiplierMin/Max`. Left undone there: 96 masked nodes keep the rifle's bone
  masks where vanilla's pistol node has others (11 none), the 3 PvP `HitRGun*` nodes, an in-game test.
  Engine notes from it: `Anim2DBlend.speedScale` is parsed but never used (every 2D blend track runs at the node's
  speed, so only retimed clips can match per-clip lengths); the speed multiplier applies on top of a variable speed
  scale (`AnimLayer.startLiveNodeTracks`); vanilla's locomotion clips of every weapon class share length and root
  motion (walk 0.667 s / 0.945, run 2.094, sprint 2.756, sneak run 1.496), and the stance's clips keep vanilla's rifle
  Translation_Data exactly; B42 ballistics start at the drawn muzzle along the barrel
  (`BallisticsController.calculateMuzzlePosition`; targets near that line count as well as the reticle's), its
  `1 / (1 + muzzle offset)` spread scale only for RangeFalloff guns; GoM's .glb clips also carry Blender's stashed
  actions (a clip's length is the animation named like it).
- Gunworks grip cache (found 2026-10-26, fixed in ZomboidFixesB42 `*_GunworksGripSync.lua`): `GripAnim.lua`'s `lastGripByOnlineId` remembers the last grip set
  per online ID, not per character, and only writes the variable on a change. A character rebuilt with the same ID
  (a remote player back in range after the 5 s timeout, a relog, a respawn, another world without a Lua reload)
  never gets `GunworksGripAnim` again until its weapon changes: others see the turned guns in vanilla's rifle nodes,
  4-9 cm off the hands.

## Gun scale (2026-10-25; built 2026-10-26 in GunScale.lua, removed the same day: `docs/gom_gun_scale.md`)

- Sizes: vanilla's MaleBody.x is 0.98 units tall (a ~1.78 m man at ~0.55); vanilla's M16_Rifle.x 0.546 long = 0.54
  of 1006 mm (true to the body), M9 0.70, pump shotgun / MSR788 ~0.60-0.65. GoM's rifle-stance guns: median 0.63
  (0.53..0.73), pistols and SMGs ~0.70; the M16A2 0.60, MP5A2 0.73. Measured by `scripts/scale_audit.py` (Blender)
  + `scripts/scale_audit_report.py` (real lengths and variants in its `REAL` table).
- Vanilla's left palm (between `Bip01_L_Hand` and `Bip01_L_Finger1`, in `Bip01_Prop1` = gun space) does not move
  through a clip: Bob_IdleRifle / Bob_WalkRifle y 0.218 z -0.004, Bob_IdleAimRifle y 0.204 z -0.021 (the right hand
  at the grip origin). On vanilla's rifles the gun's underside there is 1.1 cm above it idle, 2.8 aimed; GoM's M16s
  match that exactly, its MP5s sit ~2 cm higher (the hand floats).
- Model `scale` (42.21 jar): `ModelInstance.applyModelScriptScale` copies `ModelScript.scale` into the instance when
  it is created; `AnimatedModelInstanceRenderData.transformToParent` (in-world characters too, via
  `ModelSlotRenderData`) starts a child from the parent's xfrm, which ends with the parent's scale, so weapon parts,
  the muzzle flash (`EffectsManager.initMuzzleFlashModel`, a child at `muzzle`) and their attachment offsets all scale
  with the gun about its origin. Floor items (`ItemModelRenderer`): inverse `world` point, mesh, then the scale, then
  the parts: the `world` offset is not scaled. `BallisticsController.calculateMuzzlePosition` →
  `ModelInstance.getAttachmentWorldPosition` = bone transform x the raw `muzzle` offset, no scale. GoM's muzzle
  devices hang on `canon`, not `muzzle`. `ModelScript.Load` without `reset()` (only a re-declared block resets) keeps
  mesh and points, and its `scale` key sets the scale; `ModelScript` is `@UsedFromLua`, the `scale` field has no
  setter (`scaleAttachmentOffset(f)` multiplies every point). Gunworks' reload magazine is an attached item at a
  location named `Bip01_Prop2` (`ReloadAnim/AttachLocations.lua`), drawn with the magazine's own model.
- Which model a gun draws for a part is in the **gun's** item script (`ModelWeaponPart = <part item> <model> <self
  point> <gun point>`, one line per part), so a gun can be given a part model of its own. GoM puts its `magazine`
  point at the same offset on every gun of a family (all seven ARs 0.1015 / 0.0144, the four MP5s 0.1191, AK-74 /
  AKS-74U 0.1238, G36 / G36C 0.1101): one receiver size per family. FNC, FAMAS and SCAR-L take STANAG magazines
  on receivers of their own. GoM's FAMAS is an F1 (small trigger guard), which really takes only its own 25-round
  magazines (STANAG came with the 1994 G2); GoM gives it STANAG for gameplay. Rule (user, 2026-10-26): guns sharing
  a magazine share one scale (`docs/gom_gun_scale.md`).
- Where the scale sits (42.21): an attached / held model is parent bone x parent point x **the model's own point of
  the same name** x mesh transform x `ModelInstance.scale` (`AnimatedModel$AnimatedModelInstanceRenderData
  .transformToParent`; `invertAttachmentSelfTransform` is false); a floor item is rotation x inverse `world` point x
  mesh x scale (`ItemModelRenderer.init`, HandWeapon floor model = `getStaticModel()` = the WeaponSprite). So a
  gun's own placing points (`world`, holsters, back, `Bip01_Prop1`) are not scaled, while points parts hang from
  are (the child starts from the parent's xfrm, scale included). `GunScale.lua` (removed) scaled the placing points' offsets
  by the same factor (T(s o) R S = S T(o) R), so the gun scales about the body point / floor spot. No GoM or Guns
  of Tien gun mesh node has a translation, so the mesh transform does not shift that centre. ModelScript has no
  `scale` getter and Kahlua does not read its public field; GoM's gun models set none (the `scale = 1.1703` in
  DOUBLEBARREL is its `shellholder` point's).
- Gunworks' reload magazine in the left hand (`ReloadAnim.attachReloadMagazine`) needs the handler's `magItem`;
  GoM's `magazineProfile` handlers have none, so only our compact stance guns show one.
- **Guns of Tien's own guns are drawn at the M16A2's proportion, in their meshes** (user, 2026-10-26: "fix our own
  guns and remodel and resize them from the model itself and not the scale"): every builder's K = 0.000603 game units
  per real mm (was 0.00072 for the SMGs, P90, MP7 and pistols, 0.00065 for the M249 and SCARs), `K_OLD` kept to scale
  the GoM-convention floor points (`world`) with the gun. Everything measured in mm follows K; offsets written in game
  units for GoM's parts (rail standoffs 0.0055, bipod 0.0006) stay. The builders that import `build_mp7.py` as their
  kit set `kit.K` themselves. The loose belt links (`build_links.py`) stay at 0.65: floor items next to GoM's rounds.
  The Mk9 and its mount device stay at GoM's SMG size for GoM's MP5s; our Uzis and the UMP9 draw them through
  `Mk9_Suppressor_GoT` / `SMG9_Muzzle_Mount_Device_GoT`, the same mesh with `scale = 0.8375` (gen_scripts.py
  `GOT_PART_SCALE`; a part model's own `scale` scales it about its origin, here its `canon` point). GoM's STANAG
  magazines (meshes at 0.65) are drawn in the SCAR-L and M249 through `GunsOfTien.<mag>_GoT` (GoM's mesh, scale
  0.9277; gen_scripts.py `stanag_got`), and the M249's reload shows the hidden item `<mag>_Hand` with that model in
  the left hand (M249.lua swaps `ReloadAnim.resolveReloadMagItem` for the call of `attachReloadMagazine`, which looks
  it up on the table at call time); GoM's own ARs keep GoM's size. GoM's parts
  on our guns (optics, lights, lasers, foregrips, GoM's suppressors) keep GoM's sizes. Icons are framed to the icon box,
  so they barely change. Animations: hold_preview.py reads the MP7 and Uzi points and their size factor (MP7_S,
  UZI_S) for the stance's support places and parts; compact_animsets.TURNED_SETS takes the muzzle z from the points
  (UziT = the mean of the Mini Uzi's and the MP7's); smg_reload.py, m249_reload.py and p90_reload.py take K from the
  points files and scale offsets measured on the gun, never the hand's own contact offsets (`hold_fix`, CONTACT).
  The guns on vanilla's or GoM's clips (SCARs, UMPs, Five-seveN, UCP) needed no new clips. A HEAD worktree (`git
  worktree add`) runs the old-size pipeline for like-for-like comparisons.
- **GoM's MP5 family at the Uzis' proportion** (user, 2026-10-27: the 9x19mm SMGs share the Mk9, so they must be one
  size; "based on Uzi's"): `scripts/build_mp5.py` (Blender, seconds) scales GoM's own MP5 / MP5SD / MP5A2 / MP5K meshes
  and its five MP5 magazines by one factor about the model origin (`GunsOfTien_MP5.fbx`,
  `GunsOfTien_MP5_magazines.fbx`, GoM's node names and UVs) and writes GoM's points times it to `mp5_points.json`;
  `gen_scripts.py mp5_family()` declares GoM's 15 model blocks again (`models_mp5.txt`, `module MarzGuns`) with our
  meshes and GoM's textures. A later block of the same name resets mesh, texture, scale and the name
  (`ModelScript.reset`, decompiled 2026-10-27; `getName()` is then nil, as on Plysken's re-declared body models) but
  keeps the attachment list, so every point is written. GoM's items and their ModelWeaponPart lines are untouched.
  The factor: GoM draws the family consistently at ~0.72 of real size (MP5A2 0.726 of Wikipedia's 680 mm, MP5K 0.721
  of 325 mm), so SCALE = 0.603 / their mean = 0.8332 (MP5A2 then 0.605, MP5K 0.601); the doc's earlier -13% rested
  on an unsourced 700 mm for the MP5 (modernfirearms.net's 660 mm, retractable stock extended, gives GoM's MP5 0.738).
  Our earlier fixes of these models moved into the JSON before scaling: the MP5 / MP5A2 muzzle at the barrel's end (out
  of MuzzlePoints.lua) and their `canon` for the Mk9 (out of Suppressors.lua's run-time point); the Mk9 and its mount
  are drawn on them through the `_GoT` models, one size on every gun. GoM's shared parts (rails, optics, foregrips,
  lights, lasers) keep GoM's size (user, 2026-10-27). GoM's MP5 is named "MP5A3 Submachine Gun" (retractable stock;
  the MP5A1 has none; translation override in gen_scripts.py `MP5_NAMES`). Not redone: the MP5K's compact stance clips
  and reloads are solved for its old size (compact_animsets.TURNED_SETS MP5K -0.0445, now -0.0371: the gun drawn
  ~1.5 cm off the hands, its foregrip 3 cm nearer the grip than the left hand's place; user: "we'll judge later"),
  GoM's Hot Brass ejection offsets for the four (relative to the player), the MP5 reloads (GoM's MP5 clips; the
  magazine well is 2 cm nearer the grip).
- **Fit audit** (`scripts/fit_audit.py`, `--solve` for point shifts): every part placement on our guns against the
  same part on GoM's guns, measured against the body **plus the gun's rail and mount parts** (GoM fits rails and
  mounts as parts, so its optics float 1-3 x 0.001 above its bare bodies; without them our rail-in-body guns all
  looked sunk). Inside test by ray parity in three directions (GoM's meshes are double-sided, face normals do not
  tell). Our points were derived from GoM's own part relations (scope 0.0032 under the rail top, foregrip 0.003
  above the rail bottom, as on GoM's MP5), so they agree; the one exception, the PSO-1 on the UMPs, is drawn through
  `PSO1_Scope_UMP` with its own `scope` point raised. A part model's own point named like the gun's point is applied
  after the gun's (`T(o) R` of the gun's, then the part's), so a per-gun copy of a GoM part can be offset that way.
- **Short guns on vanilla's rifle clips**: vanilla holds the left palm ~0.22 ahead of the grip (an M16's handguard).
  `scripts/anim/rifle_hand.py` rebuilds every rifle clip whose left hand holds the gun with the palm's place scaled
  about the grip (vanilla otherwise; faded off where vanilla's hand leaves the rifle), packed and noded as a compact
  set (`GunsOfTien_Compact<Set>`, Gunworks grip registry): the UMPs ("UMP", 116 clips, 8.3 MB). Since 2026-10-27 the
  set's packs (which also hold the UMP's four reload clips) and its 255 stance nodes (`*_GoTCompactUMP.xml`) ship in
  the main mod, because GoM's MP5 / MP5A2 / MP5SD use it too (user: rifle stance for the full-size MP5s, the MP5K in
  the short SMG stance; CompactStance.lua registers them): at 0.8332 of GoM's size their handguard sits where the
  set's palm (vanilla's x 0.8375) goes, so the hand lands where vanilla's held GoM's own MP5 (stills 2026-10-27,
  hold_preview.py `mp5` on rifle_hand.py's idle / aim). The UMP's reload nodes (`*GunsOfTienCompactUMP_GoT.xml`) stay
  in Post-93; clips are found by name from any mod. Rebuilding the set: pack and write nodes into the main mod's
  media. GoM's own reload clips
  are glTF from a Blender rig whose bone axes differ from the .x files' and whose first frame is no vanilla pose, so
  they cannot be retargeted by our pipeline (no shared pose to take the per-bone axis offsets from).
- compact_build's variant chooser also scores `+filter+declip` (the filter re-solves arms without the de-clip; the
  MP7's diagonal walk had its left arm 3.9 cm in after it).
- Hot Brass offsets are in tiles from the player (`forwardOffset` along the facing): a gun resized about its grip
  moves its port by (1 - s) x the port's distance ahead of the grip x 1.5 tiles a game unit.

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
  cartons. Weights: box = 0.9 × its rounds (GoM's `AmmoPatch.lua` round weights), carton = 0.8 × 12 boxes, crate =
  0.8 × 4 cartons, each rounded to 3 decimals, so every packing step is lighter per round; every one of ours
  follows it (user, 2026-10-25: packing must always pay; Post-93's `packed_weights`, link boxes 0.9 of their links).
  GoM's recipes (G/scripts/MarzWeapons/recipes/ammunition.txt) use closed `itemMapper` lists, so an
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

## Ammo Maker (workshop 2788256295, mod id `ammomaker`, optional)

- **Optional, the way GoM does it** (user, 2026-10-24: Marz asked for it). GoM only ships a Lua table
  (`MarzWeapons/ammomaker_apiTablesGoM.lua`, `ammoMakerAddAmmoTypesMap0`) and uses Ammo Maker's own placeholders, so
  it has no Ammo Maker script at all. Ours keep scripts that must load without it (42.21, traced 2026-10-24):
  an unknown `timedAction` throws in `CraftRecipe.OnScriptsLoaded` and an `itemMapper` naming a missing item throws
  in `OutputMapper.OnPostWorldDictionaryInit`; both are caught by `ScriptManager` around the **whole** pass, so every
  recipe after ours would break. An unknown item in an `inputs` line is only skipped (an error in `-debug`). So the
  placeholders use `GunsOfTien_MakeAmmo` / `GunsOfTien_ProduceAmmo` (copies of its MakeAmmo / ProduceAmmo,
  scripts/GunsOfTien/timedactions_ammomaker.txt; Post-93 uses them too), the soft point recipe is an empty placeholder
  that shared/GunsOfTien/AmmoMaker.lua fills with `recipe:Load` at OnInitGlobalModData only with Ammo Maker (after
  its handler, so a part recipe it hid, `getOnAddToMenu() == "False"`, stays hidden), and without it both
  AmmoMaker.lua files hide every recipe of ours that needs it the way its `updateRecipesInactive` does (inputs and
  outputs cleared, `{ OnAddToMenu = False, NeedToBeLearn = True, }`; the crafting lists call OnAddToMenu through
  `callLuaBool`, a missing function = false = skipped) and move the belt link recipes from its `AmmoMakerParts`
  category to vanilla's `Welding`. Presence test: its global `ammoMakerAmmoData` / `ammoMakerAmmoParts` (its shared
  files load before ours through `loadModAfter`). The parts' items still name its world models (unreachable
  without it: only its loot code and these recipes make them).

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
  "MP5", MP5K / TEC9 = "handgun2", FAMAS = "famas_rifle", FAL = "fal_rifle"; GoM renames ids between versions, so
  re-check a borrowed id after a GoM update: a stale one matches no node; better, copy the nodes under an id of
  our own, since another mod's same-path node file can replace GoM's). AnimSet XMLs (both `AnimSets/player/actions/` and
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
