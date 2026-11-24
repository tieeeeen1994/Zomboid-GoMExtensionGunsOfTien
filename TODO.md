# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished features are not listed: they are taken as
working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.
Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Next guns (locked 2026-11-23, in this order)

Picked by the user from their wish list. Releases ship two or more guns each.

### 1. Tokarev release (main mod: round and guns all predate 1993)

- [ ] With the guns: the 7.62x25mm round's loot beside their kits and their magazines in its Gunworks family (the
      round, its Steel Core and Subsonic loads and the SAKER boxes are built: CLAUDE.md "7.62x25mm Tokarev and
      9x18mm Makarov"; not played).
- [ ] **TT-30 pistol** (the user's choice). The wish list said TT-33, the simplified 1933 version made in the millions;
      check the two in the reference hunt and, by "build every real variant", propose both if they differ visibly.
      GoM's pistol reload (`pistol_reload`), holster.
- [ ] **PPSh-41**: its 71-round drum and 35-round box magazine, held as a rifle, GoM's Thompson reload
      (`thompson_marz`). Loot with GoM's Russian guns (to design).

### 2. Bizon family (Post-93, later: waits for more rounds)

The 9x18mm Makarov round exists since 2026-11-25 (main mod, plain only; boxes TUSKER). Its later loads (PMM 1994,
SP-7, RG028) belong in Post-93, with the PP-9 Klin.

- [ ] **PP-19 Bizon**, one gun per real version, named by its round: **Bizon Parabellum** (Bizon-2-01, 9x19, 53-round
      helical magazine), **Bizon Makarov** (Bizon-2, 9x18, 64-round), **Bizon Tokarev** (Bizon-2-07, 7.62x25; confirm
      it was real), and if their rounds come, the .380 Bizon-2-02 and the suppressed 9x18 Bizon-2-03. Each its own
      helical magazine (the calibres differ in barrel and bolt too, so no magazine swap between them). Built on GoM's
      AKS-74U (the real gun is mostly AKS-74 parts), held as a rifle, GoM's AK reload. The 9x18 Makarov round it
      waits for would also serve the CZ-83, Skorpion vz. 82, PP-91 Kedr and PP-9 Klin (PMM as its [+P] load);
      Ammo Maker has `9x18Mak`, Hot Brass no 9x18 casing (its 9x19 one would do).

## Release 3.25.0 (built 2026-11-25, not uploaded)

- [ ] Look over docs/762x25_9x18_art_sheet.png (SAKER and TUSKER boxes, round icons).
- [ ] Play the new rounds: box and carton icons, open / pack recipes, Ammo Maker's Tokarev loads, Hot Brass casings.
- [ ] Decide: loot for the two rounds now, or only with the Tokarev guns (none for now).
- [ ] Upload GoT 3.25.0 and Post-93 (A-91M) once played; changenotes.txt is written.

## To review: the A-91M and 5.56A-91 (Post-93, built overnight 2026-11-25)

- [ ] Review the model on docs/post93_a91m_preview.png and the decisions in docs/post93_design.md "KBP A-91M and
      5.56A-91" (launcher integral on both, no PBS-1 on the 7.62, the charging handle's side, loot).
- [ ] Choose whether to build the first over-barrel 7.62-A91M and the late 5.56 gun with a railed forearm.
- [ ] Play them: the launcher swap (Gunworks radial), GoM's FAMAS reload with the AK magazines in the off hand, the
      5.56A-91's own magazine, optics on the handle rail, muzzle parts, Hot Brass forward, loot.
- [ ] A Workshop preview (render_ad_guns.py / make_workshop_art.py).

## Smaller open items

- [ ] Re-run build_mk9.py some time so smg9_points.json (render art only) has GoM's new MP5 canon.
- [ ] The older Workshop previews show the pre-audit triggers (a few pixels); redoing them needs the MP7 / SCAR / Vector
      specs moved to their `_RD` / `_FD` bodies first (CLAUDE.md, Workshop art).
- [ ] The HK416 .22's 30-round magazine length is an estimate (no measurable photo of a 30); re-measure if one
      turns up.
- [ ] Tien's Inspect Weapon: decide whether to also show laser on / off, Gunworks swap-pair states and the
      fixed-bayonet gun's load (proposed 2026-11-25).
- [ ] The SV-98 variant left out (the aluminium one), if wanted. The SV-99 stays one gun (user, 2026-11-20).

## New Mod - EQUAL LOOT DISTRIBUTION

This will modify all loot so that all guns spawn without discrimination. Ammo and mags will still spawn beside the gun.
Sub-mod "Loot Equalizer", parked 2026-11-15: decisions, the spawner-table takeover idea and the open questions are in
`docs/equal_loot_design.md`.
