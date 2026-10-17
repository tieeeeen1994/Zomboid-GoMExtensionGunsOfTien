# TODO

State of GoM Extension: Guns of Tien and its Post-93 sub-mod (written 2026-10-14). Nothing has been run in game yet.
Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.

## Main mod `GoMExtensionGunsOfTien` — code complete, untested

Done: 12 rounds (box / carton / crate, own open / pack recipes) with profiles, realistic gun sounds (always on,
`SoundTable.lua` from `scripts/sound_model.py`), realistic piercing (option), 7.62x39 US + PBS-1 cycling (option), GoM
plain rounds renamed (9x39 SP-5, 5.45 7N6), no loot (special loads, as GoM's: Ammo Maker only), Hot Brass, tooltips, Ammo Maker for all 12
rounds incl. this mod's parts (soft point bullets S / M filed from standard bullets; birdshot pellets poured through
`Base.Strainer` + water), all art (`scripts/make_art.py`, `scripts/make_ammomaker_art.py`), generator
`scripts/gen_scripts.py`.

- [ ] First load in single player: no Lua / script errors; spawn and fire every round (tracer = AmmoType line);
      7.62x39 US with and without a PBS-1; birdshot close / far; piercing option on / off; sounds in an existing save.
- [ ] Ammo Maker: Make / Produce recipes of every new type fill in; Make Soft Point Bullet; Pour Birdshot Pellets
      (the water input at a furnace is copied from the pottery wheel, unverified at a furnace).
- [x] Workshop: workshop.txt, preview.png (1024, ad), both posters / icons, README, mod.info texts (2026-10-15;
      art from scripts/render_ad_guns.py + scripts/make_workshop_art.py). Upload from the game's Workshop menu.
      The game's uploader refuses any preview.png that is not exactly 256x256 (seen 2026-10-15): preview.png is a
      simple 256 one, the 1024 ad is preview2.png, added on the Steam page by hand.
- [ ] Add preview3.png (1024, the Five-seveN and the UCP fitted out, 2026-10-17) on the Steam page by hand.
      Rebuild: `blender -b --factory-startup -P scripts/render_ad_guns.py -- tmp/ad fiveseven ucp`, then
      `python3 scripts/make_workshop_art.py preview3` (names select what it writes; on the Mac it uses DIN Alternate
      Bold, the nearest to Windows' Bahnschrift that preview2 was drawn with).

## Post-93 sub-mod `GoMExtensionGunsOfTienPost93` — in progress

Done (Lua syntax-checked): `registries.lua` (5 ammo types), ammo items / models / recipes / Ammo Maker placeholders +
names (`scripts/post93/gen_post93_ammo.py`), ammo art (`scripts/post93/make_ammo_art.py`, sheet
`docs/post93_ammo_art_sheet.png`), `Ammunition.lua` (families 4.6x30mm / 5.7x28mm, profiles), `AmmoMaker.lua`,
`Guns.lua` (magazine profiles, RPM 950 / 900, animated bolt, reload anims MP7 = "MP7A1" / P90 = "P90TR", magazine shown leaving the gun with the hand, MP7 folding
stock, suppressor stats, integrated rails as parents of GoM optics / lights / lasers, permanent parts, spawn parts,
MountOn appends), `HotBrass.lua`, `Loot.lua` (GoM Anachronistic + Police SMG spawners, rare boxes), `Tooltips.lua`,
reload AnimSet XMLs (`AnimSets/player(-vehicle)/actions/*P90TR_GoT.xml`, clips `Bob_GunsOfTien_P90_Load / Unload
/ Rack / AimRack`; `*MP7A1_GoT.xml`, vanilla's pistol clips + `Bob_GunsOfTien_MP7_Unload`), gun generator `scripts/post93/gen_post93_guns.py` (items, models, parts, fixing, names; reads
`mp7_points.json` / `p90_points.json`).

- [x] MP7A1 rebuilt from the user's photos 2026-10-14 (the first, dimensions-only model had a raked block grip, a
      deep trigger guard and straight magazines; 73% silhouette overlap, now 96.1%): FBX, textures, icons,
      `mp7_points.json`, `docs/post93_mp7_preview.png`; rebuild: `build_mp7.py` (~1 min) → `render_mp7.py` →
      `make_mp7_art.py`. To check in game: the hand on the upright grip, magazines (no attachment rotation now, the
      30 / 40 curve forward by themselves), the `world` floor pose (GoM default kept). Not yet shown to the user.
- [x] P90 TR assets rebuilt from the user's photos and approved 2026-10-14 (FBX, textures, icons, `p90_points.json`,
      `docs/post93_p90_preview.png` with the photo outline overlay, 98.7% overlap; rebuild: `build_p90.py` (~1 min) →
      `render_p90.py` → `make_p90_art.py`). To check in game: the grip in the hand (origin = rear-top of the grip
      column), the `world` floor pose (GoM default kept), optic height on the top rail.
- [x] P90 held like a pistol (user, 2026-10-14): item as GoM's MP5K (Handgun, handgun reload, one hand) but never in a
      holster (Rifle: back slot, turned upright there by its rifle_back attachments), model exported upside down like
      GoM's handgun-held guns. `gen_post93_guns.py` run (items_guns / models_guns / fixing_guns,
      names). To check in game: the hold, the gun upright on the back (with and without a bag), the `world` floor pose.
- [x] Every name in both mods' scripts resolves (`python3 scripts/check_refs.py`, 642 references, 2026-10-15); the
      only misses are the four P90 reload clips below. Re-run it after any generator.
- [x] P90 reload clips (pistol stance, top magazine) built and approved 2026-10-15:
      `anims_X/Bob/Bob_GunsOfTien_P90_{Unload,Load,Rack,AimRack}.x` from `scripts/post93/anim/p90_reload.py`
      (TienInspectWeapon's pipeline). Without them the magazine insert hung (a reload ends on its clip's events). To
      check in game: the whole reload, the load click on the press, the rack's events, aiming racks.
- [x] MP7A1 held like a pistol (user, 2026-10-15), exactly as the P90: Handgun item block, back slot (never a
      holster), model exported upside down (`handgun_points()` in build_mp7.py, shared with build_p90.py, whose files
      came out byte-identical). Reload = vanilla's pistol clips with its own AnimSets and the P90's magazine
      behaviour, the right magazine of the three swapped (CLAUDE.md "MP7A1 reload"). To check in game: the hold, the
      gun upright on the back, the `world` floor pose, the reload with each magazine size (the right one leaves and
      comes back), the rack's casing.
- [x] MP7 60-round drum (user, 2026-10-15): model, texture, icon, item, name, tooltip, profile, 2% spawn on found
      MP7s. To check in game: the drum under the grip, the reload with it (the drum leaves and comes back).
- [x] FN Five-seveN (user, 2026-10-16) as `MarzGuns.FIVESEVEN`, GoM's own unused name: model from an ATF side photo
      (96.0% silhouette overlap), slide, 20 / 30-round magazines, textures, icons (cameras fitted on GoM's Glock 17
      icons), item / model / repair scripts, magazine profile, animated slide, ammo family, GoM pistol parts, its own
      SFN-57 suppressor on the 5.7x28mm mount device it shares with the P90, spawn parts, loot, Hot Brass, tooltips; sheet
      `docs/post93_fiveseven_preview.png`. Rebuild: `build_fiveseven.py` → `render_fiveseven.py` →
      `make_fiveseven_art.py --renders DIR` → `gen_post93_guns.py`. To check in game: the hold in the hand (origin
      placed like the Glock's), the slide moving back on each shot, the default pistol reload with each magazine,
      the 30-round magazine under the grip, the Beretta mount with a sight, the LP and TL lights under the rail (lasers must
      not fit), the
      mount device on the Five-seveN (shown as a threaded-barrel adapter) and the SFN-57 over it (and that the SP90
      no longer fits it), in the holster and on the floor (GoM's pistol `world` pose), the casing
      thrown right, the name shown is GoM's "5.7x28mm Five-SeveN".
- [x] H&K UCP Prototype (user, 2026-10-17): `GunsOfTienPost93.UCP`, built and registered like the Five-seveN from a
      photo of the about-2004 prototype (97.3% silhouette overlap), a 20-round magazine and a small 40-round drum, the MP7's mount device (drawn
      as a threaded-barrel adapter) and Rotex-II, GoM's Beretta mount + pistol sights and pistol lights, Anachronistic
      spawner only; sheet `docs/post93_ucp_preview.png`. To check in game: the hold, the slide, the default pistol
      reload with both magazines (the drum under the grip leaves and comes back), holster and floor pose, the Beretta mount with a sight, both lights, the mount device and Rotex-II at the
      muzzle (and that the MP7 still takes them), the name "UCP Prototype", casings thrown right.
- [x] MP7 30 / 40-round magazines matched to the user's photos of H&K's (2026-10-17): every box magazine (20, 30, 40)
      curves from its feed lips down on one radius and is tilted back so its part inside the grip stays centred; the
      30 and 40 carry their lower part in a wider polymer sleeve. To check in game: the magazines in the grip (nothing
      showing through), the reload with each.
- [x] 2026-10-17: MP7 / P90 markings read the right way in game (they were mirrored); our weights set to GoM's
      standard (suppressors, mount devices, magazines, guns); GoM's Glock 17 added to the main mod's sound table. To
      check in game: the markings read correctly (and which side the P90's FN panel is on, against a photo).
- [x] 2026-10-17: the Five-seveN and UCP never spawn in civilian homes (out of GoM's Anachronistic spawner, which sits
      in vanilla's late survivor safehouses): both in GoM's police / SWAT handgun spawners (the UCP like any other
      gun, not rare, user 2026-10-17) and (with a magazine and a box) in survivor and bandit zombies' late bags. To
      check in game: none in houses, both on police zombies and in police cars as often as the Glock / M92FS.
- [x] 2026-10-17: loot matched to GoM: special loads never spawn (the main mod's loot removed; Post-93 keeps only
      DM11 / SS190 boxes and cartons, now also cartons beside vanilla 9mm cartons in police / SWAT / gun stores), the
      high-capacity magazines in GoM's tactical high-cap spawner. To check in game: no special loads in loot, DM11 /
      SS190 cartons and loose drums turn up; nothing of the Five-seveN / UCP in houses.
- [ ] Lasers (2026-10-18): Turn Laser On / Off from the gun's menu and the radial; the short beam part on the laser's lens (GoM rifles,
      pistols, MP7 / P90; does it fade (texture alpha); does the unlit shader
      gunsoftien_laser load from the mod's media/shaders, so it stays bright at night), on a slung gun, for another player in MP; the bonus only while on (gun tooltip stats); drain and the
      empty switch-off; Remove / Insert Battery on a detached laser; the new tooltip lines and part-row names.
- [ ] Test in game (as above, plus folding stock, the MP7A1's front grip (fold / unfold from the context and radial menus, stats), the MP7A2 (spawns half of found MP7s, GoM's foregrips on its bottom rail: fit, look, stats), rails, suppressors, spawns, Hot Brass downward ejection).

