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
      wood; look). Our SCAR-L / H were ~1.1-1.3 cm lower before the resize (measure again). Fixing = per-gun
      left-hand places (Gunworks `GripAnim` clip sets, as the compact stance and the UMPs): which ones?

## Polish

- [ ] M249 belt reload clips (`scripts/anim/m249_reload.py`): the stock passes into the chest while the hand works,
      the left hand stops 1-3 cm short on the open cover and the right-side handle, left elbow flips (AimRack worst).
