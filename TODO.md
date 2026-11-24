# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished features are not listed: they are taken as
working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.
Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Next guns (locked 2026-11-23, in this order)

Picked by the user from their wish list. Releases ship two or more guns each.

### 1. Tokarev release (main mod: round and guns all predate 1993)

- [ ] **7.62x25mm Tokarev**, a new calibre in the main mod (as .22 LR was): the plain round in boxes, cartons and
      crates, AmmoType `gunsoftien:...`, its own Gunworks family, loot beside the guns. Ammo Maker already has the
      base type `762x25Tok` (no AP / TR copies), so only the special loads need copies. Hot Brass has no 7.62x25
      casing: borrow the nearest. Special loads to settle in the reference hunt, real loads only: steel core Pst
      (Armor Piercing, Soviet issue), a hot load (Czech M48 surplus is the usual candidate), Soft Point or Hollow
      Point only if a real commercial load exists.
- [ ] **TT-30 pistol** (the user's choice). The wish list said TT-33, the simplified 1933 version made in the millions;
      check the two in the reference hunt and, by "build every real variant", propose both if they differ visibly.
      GoM's pistol reload (`pistol_reload`), holster.
- [ ] **PPSh-41**: its 71-round drum and 35-round box magazine, held as a rifle, GoM's Thompson reload
      (`thompson_marz`). Loot with GoM's Russian guns (to design).

### 2. Bizon family (Post-93, later: waits for more rounds)

- [ ] **PP-19 Bizon**, one gun per real version, named by its round: **Bizon Parabellum** (Bizon-2-01, 9x19, 53-round
      helical magazine), **Bizon Makarov** (Bizon-2, 9x18, 64-round), **Bizon Tokarev** (Bizon-2-07, 7.62x25; confirm
      it was real), and if their rounds come, the .380 Bizon-2-02 and the suppressed 9x18 Bizon-2-03. Each its own
      helical magazine (the calibres differ in barrel and bolt too, so no magazine swap between them). Built on GoM's
      AKS-74U (the real gun is mostly AKS-74 parts), held as a rifle, GoM's AK reload. The 9x18 Makarov round it
      waits for would also serve the CZ-83, Skorpion vz. 82, PP-91 Kedr and PP-9 Klin (PMM as its [+P] load);
      Ammo Maker has `9x18Mak`, Hot Brass no 9x18 casing (its 9x19 one would do).

## Smaller open items

- [ ] Re-run build_mk9.py some time so smg9_points.json (render art only) has GoM's new MP5 canon.
- [ ] The older Workshop previews show the pre-audit triggers (a few pixels); redoing them needs the MP7 / SCAR / Vector
      specs moved to their `_RD` / `_FD` bodies first (CLAUDE.md, Workshop art).
- [ ] The HK416 .22's 30-round magazine length is an estimate (no measurable photo of a 30); re-measure if one
      turns up.
- [ ] The SV-98 variant left out (the aluminium one), if wanted. The SV-99 stays one gun (user, 2026-11-20).

## New Mod - EQUAL LOOT DISTRIBUTION

This will modify all loot so that all guns spawn without discrimination. Ammo and mags will still spawn beside the gun.
Sub-mod "Loot Equalizer", parked 2026-11-15: decisions, the spawner-table takeover idea and the open questions are in
`docs/equal_loot_design.md`.
