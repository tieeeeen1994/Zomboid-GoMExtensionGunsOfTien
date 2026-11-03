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
- [ ] **P90 trigger and stippled grips, every P90** (user, 2026-11-03: "they look wrong"): built 2026-11-03, not
      played (CLAUDE.md, "Trigger and grips"): the round loop with its notch, the trigger blade in its recess behind
      it, the selector paddle, stippled grip panels; the P90 TR, PS90 and P90 rebuilt, previews and icons redone. To
      check in game: the trigger and stippling read at play distance, and the hand still sits right on the grip.
- [ ] **Vector .45 Carbine** (the Vector CRB, Post-93, `VECTORCRB`): built 2026-11-03, not played (CLAUDE.md,
      "Vector CRB"), as KRISS's CRB Enhanced (M-LOK handguard, fat shroud, M4-type stock). To check in game: the long
      gun in the hands and on the back, the stock folded and deployed, GoM's foregrips under the handguard, the
      .45 mount device and P45 on the shroud's face, the shared Vector .45 loot (one of the two guns). Release policy (user, 2026-11-03): two
      or more guns per release; meant to go out with the PS90.
- [ ] **Vector 9mm Pistol** (the Vector SDP, Post-93, `VECTORSDP`): built 2026-11-03, not played (CLAUDE.md,
      "Vector SDP"). To check in game: the one-handed hold and GoM's MP5K reload with the turned model, on the back,
      the Mk9's mount device over the thread protector, the shared Vector 9mm loot (one of the two guns).
- [ ] **Cheek risers** (main mod; user, 2026-11-03: "no cheek pads in GoM. Guns that are bullpups and with long stocks
      and long rifles can possibly take advantage of this"): strap-on / lace-on cheek pads as weapon parts for ours and
      GoM's guns (leather lace-on pads date from WWII, so not Post-93). Traced, nothing built: a new part type
      `CheekRiser` (free string, as our `ChargingHandle`; label `Tooltip_weapon_CheekRiser`), no rail needed, MountOn
      lists GoM's guns too. Stats either plain CustomStatsAttachments (Aiming Time down, a little Hit Chance) or only
      while a magnified optic is fitted, through a Gunworks `StatsFactory.RegisterModifierLayer` layer (proposed).
      Loot: join GoM's `Base.RecoilPad` replacement list and the attachment spawners. Models are the work: one mesh
      per stock family (AR, AK, G3 / MP5, FAL, M14, wooden bolt-action stocks...), placed by a run-time `cheek`
      point added to GoM's model scripts or modelled in place at the gun origin; folding / collapsible stocks need
      the pad hidden and its stats off while folded, or are left out; bullpups (AUG, FAMAS, P90: cheek on the
      receiver, sights already high) only with reference photos; skip the SVD and PSG1 (cheek rest built in).
      Open: which guns (proposed first: fixed-stock long guns: M14, M1 Garand, FAL, G3, bolt rifles, AK-47 / AK-74,
      M16 family, RPK, Mini-14), always-on stats or optic-only, leather lace-on or modern nylon look.

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
