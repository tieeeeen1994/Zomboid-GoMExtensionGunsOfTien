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
      FNC / AS VAL / Mossberg ~0.8 (the FAMAS is done: the bullpup set, 2026-10-27). Bolt
      rifles, M79, Stevens, BAR, Camp Carbine: palm 0.5-2 cm into the forend (probably just the fingers round the
      wood; look). Our SCAR-L / H were ~1.1-1.3 cm lower before the resize (measure again; the MP5 / MP5A2 / MP5SD
      too, now at 0.833 of GoM's size). Fixing = per-gun left-hand places (Gunworks `GripAnim` clip sets, as the
      compact stance and the UMPs): which ones?
- [ ] MP5K in the compact stance at its new size (user, 2026-10-27: "we'll judge later"): its clips and reloads were
      solved for GoM's size (the gun now drawn ~1.5 cm off the hands, the foregrip 3 cm nearer the grip than the left
      hand's place). Rebuild the MP5K set (TURNED_SETS -0.0371, hold_preview / smg_reload places) if it looks off.

## New guns

- [ ] **Steyr AUG A1** (user, 2026-10-27: "start with AUG A1"; main mod, 1977). Not in GoM or Gunworks. Proposal,
      not approved yet:
      - Size: the M16 as the basis (user, 2026-10-27), i.e. K = 0.000603 per real mm as every gun of ours: 790 mm
        real → 0.476 units. Its magazines are its own, so no shared-magazine scale applies.
      - Stats from GoM's M16A1 (same round, same 508 mm barrel, Auto / Single): damage 1.0-1.8, range 50, crit 20,
        jam 1, condition 1 in 150, ConditionMax 10; the built-in 1.5x optic baked in (HitChance and crit ×1.05, sight
        range ×1.15, between GoM's Aimpoint and LR4X); about 700 rpm, spread 0.12 / 2.2 (M16A1 0.15 / 2.5, FAMAS 0.1 /
        2.0); weight 3.6 (GoM's rifles weigh real); sound as the M16A1 (sound_model.py).
      - Magazines: profile "AUG", Steyr translucent 30 and 42 (the HBAR's), family `5.56x45mm`; not STANAG, not
        GoM's G36 magazine.
      - Folding vertical front grip on its own toggle (the MP7A1's way); no rails, optics, lights, lasers or
        suppressors on a 1993 A1.
      - Reload on GoM's FAMAS bullpup clips (`famas_rifle`) first; Hot Brass from GoM's FAMAS values, to the right;
        RepairPack at GoM's assault rifles' Aiming level.
      - To decide with the user: select-fire A1 only, or also the semi-automatic AUG SA on the same model (the one a
        1993 Kentucky civilian could own, imported 1983-1989) and where each spawns; green, black or both textures;
        bayonet (Austrian Glock knife; a lug on the SA not confirmed); a side-on reference photo (the user's, or a
        public-domain / CC one from Commons).
      - Later AUGs: 9mm Para (late 1980s) in the main mod; USR, A2, A3, NATO stock (STANAG) in Post-93.

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

- [ ] **Short SMG stance (Uzi, UziT, MP7, MP5K), before the 3.4.0 release** (user, 2026-10-28: release held for it):
      arms up to 2.2 cm deeper into the body than vanilla's, the reloads' ends 1.7-2.5 cm in. Goal: **only the arms**
      out of the body, a natural movement ("I'm generally fine with guns clipping. I just hate unnatural movement in
      the body"): gun and hands stay where the clips have them; elbows / shoulders only, eased over several frames.
      The first de-clip (gun moved, elbows swung) was reverted ("your current changes are worse"; CLAUDE.md "No
      clipping"). Show old and new side by side (GIF) before packing. Also judge the MP5K at its new size here.
- [ ] UMP rifle-hand set (UMPs, GoM's MP5A3 / MP5A2 / MP5SD): same old clipping, its de-clip reverted 2026-10-28 (user:
      the old set for everyone); rifle_hand.py / smg_reload.py still carry the UMP's fixes (CLAUDE.md "No clipping").

- [ ] M249 belt reload clips (`scripts/anim/m249_reload.py`): the stock passes into the chest while the hand works,
      the left hand stops 1-3 cm short on the open cover and the right-side handle, left elbow flips (AimRack worst).
