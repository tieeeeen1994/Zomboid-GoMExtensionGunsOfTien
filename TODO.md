# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished and built features are not listed: they
are taken as working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings:
`CLAUDE.md`. Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Bugs

- [ ] **No firing animation in one hand with the left hand full** (user, 2026-10-26: "Our guns in GoT that can be
      held with one hand has no shooting animation when the left hand is holding something else like an
      umbrella"). Not traced yet. To find out: which guns (the four OneHand.lua guns only, or the P90 / Micro Uzi /
      pistols too, and whether GoM's own one-handed guns do the same); whether vanilla's pistol with an umbrella
      animates (engine) or only with Gunworks (its `RealSingle` / `RealAuto` / `RealBurst` nodes and their
      conditions); what `WeaponType.getWeaponType` gives for a two-handed gun in the primary hand with another item
      in the secondary.

## Decide

- [ ] One-hand penalty: the Mini Uzi, MP5K and MP7A1 / A2 held in one hand get the engine's rule for a two-handed
      weapon in one hand (half damage, 0.77 combat speed). Keep it, or not?
- [ ] Left hands off on rifle-stance guns (vanilla's own rifles: 1.1 cm under the gun idle, 2.8 aimed): GoM's MP5 /
      MP5A2 / MP5SD ~2 cm lower (3.0 / 4.6: the hand floats under the handguard), G3, Thompson ~1.1-1.3 cm lower, FAL /
      FNC / AS VAL / Mossberg ~0.8; FAMAS: the palm is ahead of its handguard (1.4 cm thick there: the barrel). Bolt
      rifles, M79, Stevens, BAR, Camp Carbine: palm 0.5-2 cm into the forend (probably just the fingers round the
      wood; look). Our SCAR-L / H were ~1.1-1.3 cm lower before the resize (measure again; the MP5 / MP5A2 / MP5SD
      too, now at 0.833 of GoM's size). Fixing = per-gun left-hand places (Gunworks `GripAnim` clip sets, as the
      compact stance and the UMPs): which ones?
- [ ] MP5K in the compact stance at its new size (user, 2026-10-27: "we'll judge later"): its clips and reloads were
      solved for GoM's size (the gun now drawn ~1.5 cm off the hands, the foregrip 3 cm nearer the grip than the left
      hand's place). Rebuild the MP5K set (TURNED_SETS -0.0371, hold_preview / smg_reload places) if it looks off.

## Check in game

- [ ] GoM's MP5 family at the Uzis' size (2026-10-27, scripts/build_mp5.py, models_mp5.txt): no "model script not
      found" / mesh errors in the log; the MP5 (named "MP5A3 Submachine Gun"), MP5A2, MP5SD and MP5K about 17% smaller,
      with GoM's textures, in the hand, on the back / in the holster and on the floor; every magazine (20 / 25 / 30 / 60
      / 100) seated in each of the four; the stocks fold and deploy in place; the bolt moves on each shot; the muzzle
      flash and the tracers at the barrel's end; the Mk9 mount and can on the MP5 / MP5A2 the same size as on an Uzi,
      against the front sight housing on the bore axis; GoM's optics, foregrips, lights and lasers still on their rails
      (GoM's size); the MP5 reload (GoM's clips) and the MP5K's stance reload and one-hand reload.
- [ ] MP5A3 / MP5A2 / MP5SD on the UMP rifle-hand set (2026-10-27, the set moved from Post-93 into the main mod):
      with Post-93 off, no "animation not found" in the log and the left hand on the handguard (not at the muzzle)
      idle, aimed, walking, running, sneaking, shooting; the MP5 reload (GoM's clips) still plays; with Post-93 on, the
      UMPs keep their hold and their own reloads (their reload clips are in the main mod's packs now).

## Polish

- [ ] M249 belt reload clips (`scripts/anim/m249_reload.py`): the stock passes into the chest while the hand works,
      the left hand stops 1-3 cm short on the open cover and the right-side handle, left elbow flips (AimRack worst).
