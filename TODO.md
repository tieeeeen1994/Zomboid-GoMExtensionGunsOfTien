# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished and built features are not listed: they
are taken as working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings:
`CLAUDE.md`. Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Bugs

- [ ] **No firing animation in one hand with the left hand full** (user, 2026-10-26: "Our guns in GoT that can be
      held with one hand has no shooting animation when the left hand is holding something else like an
      umbrella"). Not traced yet; the Mini Uzi, MP7s and MP5K were two-handed then and are one-handed again since
      2026-10-29 (GoM's animations), so first see whether it still happens. To find out: which guns (the Mini Uzi, MP7s and MP5K only, or the P90 / Micro Uzi /
      pistols too, and whether GoM's own one-handed guns do the same); whether vanilla's pistol with an umbrella
      animates (engine) or only with Gunworks (its `RealSingle` / `RealAuto` / `RealBurst` nodes and their
      conditions); what `WeaponType.getWeaponType` gives for a two-handed gun in the primary hand with another item
      in the secondary.

## Community Wishlist

- [✔] Mosin Nagant (Obrez; Sawn off barrel and stock)
- [ ] MCX Spear
- [ ] Honey Badger
- [ ] M4A1 Family
- [ ] H&K MK23
- [ ] MDR 7.62
- [ ] MDR 5.56
- [ ] G28
- [ ] SR-25
- [ ] M32A1
- [ ] RPD
- [ ] KS-23
- [ ] PP-9 Klin
- [ ] Vector 45 and 9mm
- [ ] Glock 18
- [ ] MP-43 sawed off
- [ ] Mk18
- [ ] KelTec Family
- [ ] Taurus Judge
- [ ] HK33
- [ ] Barrett M82 (.50 BMG / 12.7x99mm) (not sure about this one)
- [ ] АН-94
- [ ] Galil
- [ ] LR-300SFR
- [ ] VSK-94
- [ ] ASh-12
- [ ] SR-1MP Gyurza
- [ ] KSVK 12.7
- [ ] VSSK Vykhlop
- [✔] AUG Family
- [ ] RPK
- [ ] PPSH-41
- [ ] rp-46(dp-28 variant)
- [ ] tt-33
- [ ] SV-98
- [ ] Walther PPK
- [ ] Seecamp
- [ ] CZ-83
- [ ] Kahr P series
- [ ] Charter Arms Bulldog
- [ ] Ruger Sp101
- [ ] .357 J-frames