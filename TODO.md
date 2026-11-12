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

## New Mod - EQUAL LOOT DISTRIBUTION

This will modify all loot so that all guns spawn without discrimination. Ammo and mags will still spawn beside the gun.
