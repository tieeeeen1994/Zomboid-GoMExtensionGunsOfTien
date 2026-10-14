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
- [ ] Workshop: workshop.txt, poster / preview / icon, README.

## Post-93 sub-mod `GoMExtensionGunsOfTienPost93` — in progress

Done (Lua syntax-checked): `registries.lua` (5 ammo types), ammo items / models / recipes / Ammo Maker placeholders +
names (`scripts/post93/gen_post93_ammo.py`), ammo art (`scripts/post93/make_ammo_art.py`, sheet
`docs/post93_ammo_art_sheet.png`), `Ammunition.lua` (families 4.6x30mm / 5.7x28mm, profiles), `AmmoMaker.lua`,
`Guns.lua` (magazine profiles, RPM 950 / 900, animated bolt, reload anims MP7 = "MP5" / P90 = "P90TR", MP7 folding
stock, suppressor stats, integrated rails as parents of GoM optics / lights / lasers, permanent parts, spawn parts,
MountOn appends), `HotBrass.lua`, `Loot.lua` (GoM Anachronistic + Police SMG spawners, rare boxes), `Tooltips.lua`,
P90 reload AnimSet XMLs (`AnimSets/player(-vehicle)/actions/*P90TR_GoT.xml`, clips `Bob_GunsOfTien_P90_Load / Unload
/ Rack / AimRack`), gun generator `scripts/post93/gen_post93_guns.py` (items, models, parts, fixing, names; reads
`mp7_points.json` / `p90_points.json`).

- [x] MP7A1 assets done 2026-10-14 (FBX, textures, icons, `mp7_points.json`, `docs/post93_mp7_preview.png`;
      rebuild: `build_mp7.py` (Blender, ~4.5 min) → `render_mp7.py` → `make_mp7_art.py`). To check in game: magazine
      tilt (rotate −14), the `world` floor pose (GoM default kept), the 20-round magazine 5 mm below the grip.
- [x] P90 TR assets rebuilt from the user's photos and approved 2026-10-14 (FBX, textures, icons, `p90_points.json`,
      `docs/post93_p90_preview.png` with the photo outline overlay, 98.7% overlap; rebuild: `build_p90.py` (~1 min) →
      `render_p90.py` → `make_p90_art.py`). To check in game: the grip in the hand (origin = rear-top of the grip
      column), the `world` floor pose (GoM default kept), optic height on the top rail.
- [ ] Run `gen_post93_guns.py`; check every icon / model / texture name resolves.
- [ ] P90 reload clips (top magazine): TienInspectWeapon's Blender pipeline (`scripts/anim/`), `.x` into
      `media/anims_X/Bob/`; tune the AnimSet event times.
- [ ] Test in game (as above, plus folding stock, rails, suppressors, spawns, Hot Brass downward ejection).

