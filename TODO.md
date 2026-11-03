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

## Planned

- [ ] **PS90 Carbine** (Post-93, `PS90`): built 2026-11-03, not played (CLAUDE.md, "PS90 Carbine"). To check in game:
      the hold with vanilla's rifle clips, GoM's FAMAS reload with the P90 magazine in the off hand (its
      `Bip01_Prop2` was worked out from GoM's STANAG, never seen), the Hot Brass drop from the chute.
- [ ] **P90 with its ring sight** (main mod, `GunsOfTien.P90`): built 2026-11-03, not played (CLAUDE.md, "P90 with its
      ring sight"). To check in game: the turned model in the hand and on the back, GoM's optional side rails and what
      sits on them, and that 5.7x28mm (moved from Post-93 under the same ids) still works in old saves, with
      Post-93 on and off.
- [ ] **P90 lower / grip remodel, every P90** (user, 2026-11-03: "they look wrong", with a photo of a real lower):
      the front opening should be a big rounded loop with the trigger inside it (ours is small and irregular, only
      a sliver of trigger), and the grip surfaces under both openings are stippled (ours are smooth). One fix in
      Post-93's build_p90.py (`FRAME`, `TRIGGER_HOLE`, `THUMBHOLE`, the trigger box, painting) covers the P90 TR, the
      PS90 and the main mod's P90; rebuild all three (restore build_p90.py's magazine / parts outputs from git if
      only their bytes change). Reference: the Commons P90 Standard photo already used for the P90
      (references/p90/p90_standard_mirrored.png, L = (x - 120) / 3.714, H = (970 - y) / 3.714); read off a grid
      there, 2026-11-03: trigger opening a near-circle, about L 116-152, H 47-85, with a notch at its top front; the
      trigger blade sticking back into it at about L 150-171, H 57-63; the thumbhole about L 230-300, H 41-82.
- [ ] **Vector CRB** (.45 and 9mm, Post-93; user, 2026-11-03): KRISS's civilian carbine, a variant of our Vectors
      (build_vector.py): the 16" barrel in a long shroud, otherwise the Vector. Release policy (user, 2026-11-03):
      always two or more guns per release; meant to go out with the PS90. Open: one item per calibre as the Vectors
      are, or only the .45; held as a rifle (the Vector 9mm is pistol-held); stats and loot.
- [ ] **Vector SDP** (.45 and 9mm, Post-93; user, 2026-11-03): KRISS's pistol, the Vector without a stock and with
      a short barrel. Open: how it is held (one hand like GoM's MP5K and our Vector 9mm, or two) and which slot it
      takes (holster or back), one item per calibre or not, stats and loot.

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
- [✔] RPD
- [ ] KS-23
- [ ] PP-9 Klin
- [✔] Vector 45 and 9mm
- [✔] Glock 21
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
- [✔] RPK (and RPK-74)
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

## New Mod - EQUAL LOOT DISTRIBUTION

This will modify all loot so that all guns spawn without discrimination. Ammo and mags will still spawn beside the gun.
