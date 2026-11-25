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

- [ ] Look over docs/762x25_9x18_art_sheet.png (SAKER and TUSKER boxes, round icons). The user reviews the two
      calibres later.
- [ ] Play the new rounds: box and carton icons, open / pack recipes, Ammo Maker's Tokarev loads, Hot Brass casings.
- [ ] Decide: loot for the two rounds now, or only with the Tokarev guns (none for now).
- [ ] Upload GoT 3.25.0 once played; changenotes.txt is written (A-91M only since the 5.56A-91 was removed).

## The A-91M (Post-93, rebuilt 2026-11-25 in eight remodel passes; model accepted 2026-11-25: "good enough")

- [ ] **The first 7.62-A91M, launcher over the barrel** (user, 2026-11-25: "let's add the 7.62 version instead
      with the launcher on top"; nothing built yet, noted only). A different body: references/a91/762-a91m.jpg
      (left side), more photos to gather first. It is also the test of the remodel-passes rule (CLAUDE.md
      Decisions, six since 2026-11-25): first build, then six part-by-part passes before the user sees it. It replaces the
      removed 5.56A-91 as the release's second gun.
- [ ] Review the decisions in docs/post93_design.md "KBP A-91M" (launcher integral, no PBS-1, loot).
- [ ] Play it: the launcher swap (Gunworks radial), GoM's FAMAS reload with the AK magazines in the off hand, the
      charging hook riding back, optics on the handle rail, muzzle parts, Hot Brass forward, loot.
- [ ] A Workshop preview (render_ad_guns.py / make_workshop_art.py).

## Smaller open items

- [ ] The SV-98 variant left out (the aluminium one), if wanted. The SV-99 stays one gun (user, 2026-11-20).
