# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished features are not listed: they are taken as
working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.
Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Bugs

- [ ] **No firing animation in one hand with the left hand full** (user, 2026-10-26: "Our guns in GoT that can be
      held with one hand has no shooting animation when the left hand is holding something else like an
      umbrella"). Not traced yet, and the one-handed guns changed since (GoM's animations, 2026-10-29), so first see
      whether it still happens. To find out: which guns (ours only, or GoM's one-handed guns too); whether
      vanilla's pistol with an umbrella animates (engine) or only with Gunworks (its `RealSingle` / `RealAuto` /
      `RealBurst` nodes and their conditions); what `WeaponType.getWeaponType` gives for a two-handed gun in the
      primary hand with another item in the secondary.

## Next release: the HK416 / HK417 set (Post-93)

Agreed with the user 2026-11-13: four guns, two receivers. Not designed in `docs/post93_design.md` yet; follow the
rules in CLAUDE.md (GoM's animations only, vanilla rifle / pistol hold + a GoM reload animId; sizes from the M16).

- [ ] **HK416 D14.5RS**: the standard 14.5" carbine (2004-05, original pattern, not the A5). 5.56 on GoM's STANAG
      magazines, rifle-held, GoM's `ar15_rifle` reload with `boltCatchAfterEmptyInsert` (as the SR-25 / Mk 11).
- [ ] **HK416 .22 LR Pistol**: H&K-licensed rimfire built by Umarex / Walther (H&K USA relaunch 2019, models
      81000403 / 81000404): 8.5" threaded barrel, blowback, top rail, about 4.5 lb, its own 10 / 20-round magazines
      (they join the ".22 LR" family). Proposed pistol-held, GoM's MP5K way like the Vector SDP (`handgun2`); confirm.
- [ ] **HK417 D16RS "Recce"**: the standard 16" 7.62x51 rifle; its own 10 / 20-round magazines (real HK417
      magazines do not fit the SR-25, so not the SR-25's).
- [ ] **HK417 D20RS "Sniper"**: the longest, original pattern: 20" barrel, 1,085 / 1,005 mm, 4.23 kg; the Recce's
      receiver, stock and magazines with a longer barrel and handguard. Same job as the Mk 11 Mod 0, so give it
      stats of its own.
- [x] **.22 LR round** (main mod, built 2026-11-13, not played): items, ammo type, family, Ammo Maker, Hot Brass, box
      art (CLAUDE.md ".22 LR").
- [ ] **.22 LR loot**: GoM spawns each calibre's standard box, so the .22 box should spawn; decide where with the
      .22 pistol.
- [ ] **Change notes** for that release: the 4.6x30 / 5.7x28 boxes got new art (own layouts, MP7A1 / UCP pictures,
      the IRON WASP maker on 5.7x28) besides the new guns and the .22 LR.

## New Mod - EQUAL LOOT DISTRIBUTION

This will modify all loot so that all guns spawn without discrimination. Ammo and mags will still spawn beside the gun.
