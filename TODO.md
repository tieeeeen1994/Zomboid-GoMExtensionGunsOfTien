# TODO

State of GoM Extension: Guns of Tien and its Post-93 sub-mod (written 2026-10-14). Nothing has been run in game yet.
Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.

## Main mod `GoMExtensionGunsOfTien` — code complete, untested

Done: 12 rounds (box / carton / crate, own open / pack recipes) with profiles, realistic gun sounds (always on,
`SoundTable.lua` from `scripts/sound_model.py`), realistic piercing (option), 7.62x39 US + PBS-1 cycling (option), GoM
plain rounds renamed (9x39 SP-5, 5.45 7N6), loot (option multiplier), Hot Brass, tooltips, Ammo Maker for all 12
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
- [ ] Test in game (as above, plus folding stock, rails, suppressors, spawns, Hot Brass downward ejection).

