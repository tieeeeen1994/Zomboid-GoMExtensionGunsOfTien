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
- [ ] Upload GoT 3.25.0 once played; changenotes.txt is written (A-91M 39 and A-91M 54 Prototype, the 20-round
      SV-98 magazine). Previews built 2026-11-25: preview43 (the two guns), loot pages preview34 / 36 and the
      suppressor page preview41 regenerated; add preview43 to the Steam page.

## The A-91M (Post-93, rebuilt 2026-11-25 in eight remodel passes; model accepted 2026-11-25: "good enough")

- [ ] **The A-91M Prototype** (`A91MPROTO`: the launcher-over-the-barrel body, in the game a 7.62x54R battle rifle
      on the SV-98's magazines, a 20 made for it; built 2026-11-25, the model liked by the user as the 7.62x39 gun, then stretched and
      rechambered at the user's word without a reference; CLAUDE.md "A-91M Prototype"; sheet
      docs/post93_a91m_proto_preview.png): look over the stretched body (rear 23 mm longer, barrel 35 mm longer).
      Open: the remaining see-through places are the handle, the finger opening, the frame's opening, the sling
      ring and a 12 px gap under the tube's mouth; say if any of those should be solid too.
- [ ] Play it: the launcher swap and its raised sight leaf, the 20-round magazine in the well and in the off hand
      on the FAMAS reload (our own magazine, no hand copy: as the 9A-91's), the SV-98 with the 20 in (it hangs
      55 mm under the stock; not rendered), the charging hook riding back, optics on the handle, Hot Brass forward, loot, its numbers
      against the SVU and HK417.
- [ ] Review the decisions in docs/post93_design.md "KBP A-91M" (launcher integral, no PBS-1, loot).
- [ ] Play it: the launcher swap (Gunworks radial), GoM's FAMAS reload with the AK magazines in the off hand, the
      charging hook riding back, optics on the handle rail, muzzle parts, Hot Brass forward, loot.

## Special rounds audit (2026-11-25: all built the same day; CLAUDE.md "Special rounds audit")

- [ ] Play them: each load's box, icon and Ammo Maker recipe; the flechette part recipe; the B-32 and Dragon's
      Breath fire in single player and on a server (a zombie run by another client), that no ground fire starts
      and corpses do not burn.
- [ ] Flechette part art shows pellets (the birdshot's in steel), not darts.

## Open questions for the user (2026-11-25, left on the PC switch)

- [ ] A-91M 54 Prototype: which see-through places should be solid? The handle, the finger opening, the frame's
      opening, the sling ring, the 12 px gap under the tube's mouth (sheet docs/post93_a91m_proto_preview.png,
      openings panel).
- [ ] Pistol subsonics (9x19 147gr, 7.62x25, .22 LR, 4.6x30, 5.7x28 SB193) kept their numbers in the GoM
      rebalance; GoM's subsonic is x0.4 (a rifle bullet slowed down). Keep, or rebalance too?
- [ ] Shotgun loads (birdshot, flechette, Dragon's Breath) kept their numbers: GoM has only buck and slug.
- [ ] +P (.38, .45) at x1.25, wear x0.75: an invented half step, GoM has no +P. Keep?
- [ ] 7.62x25 / 9x18 loot: none until their guns exist (decided overnight, never confirmed).
- [ ] A zombie lit by an incendiary round that despawns alive keeps fire spread 0 on its reused object (only
      matters if a Molotov later lights that object). Fix by resetting on reuse?
- [ ] The A-91M's left lever (left of the lower, ahead of the trigger guard): no source says what it is. Look for
      a KBP manual or a Russian source if it matters.

## Smaller open items

