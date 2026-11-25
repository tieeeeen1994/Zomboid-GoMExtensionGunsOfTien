# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished features are not listed: they are taken as
working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.
Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Next guns (locked 2026-11-23, in this order)

Picked by the user from their wish list. Releases ship two or more guns each.

### 1. Tokarev release (main mod: round and guns all predate 1993)

- [ ] **Tokarev TT-33**: built and wired 2026-11-25 (docs/tt_preview.png, docs/design.md 4q, CLAUDE.md "Tokarev
      TT-33"). Play it: held and reloaded as GoM's pistols, the slide back with its tube in the dust cover, the
      magazine in the off hand, Steel Core and Subsonic loads, Hot Brass, its kits in World_Oldies_Spawner and the
      import pistols, its numbers against GoM's Hi-Power and M1911. Model passed (user, 2026-11-26).
- [ ] Release art, made 2026-11-25: preview44 (the PPSh-41 and TT-33 on one page; render_ad_guns.py `ppsh41` /
      `tt33`, make_workshop_art.py preview44) and the loot pages regenerated (preview35 and preview36 changed: the
      import pistols, the World War guns). Add preview44 to the Steam page with the upload.
- [ ] **PPSh-41**: built and wired 2026-11-25 (docs/ppsh41_preview.png, docs/design.md 4r, CLAUDE.md "PPSh-41").
      Play it: GoM's Thompson reload and SMG stance on a straight stock (the hand's place: the origin follows
      GoM's M24 rule), the drum and the box in the off hand, the handle running back, Auto / Single, cases up out
      of the top, its kits in the Oldies spawners. Model passed (user, 2026-11-26).

### 1b. Makarov release (user, 2026-11-26: "For makarov guns, let's add Skorpion and Kedr")

Built and wired 2026-11-26 in one sitting; both models passed (user, the same day: "mdoels pass"). They do not
share magazines (asked 2026-11-26): each gun its own, both the 9x18mm round.

- [ ] **Skorpion vz. 82** (main mod): docs/skorpion_preview.png, docs/design.md 4s, CLAUDE.md "Skorpion vz. 82". Play
      it: held and holstered as the TMP, GoM's MP5K reload with the straight 12 / 24 / 30
      magazines, the wire stock folded and open (Gunworks' stock key), both cocking knobs running with the bolt,
      cases up out of the top, Auto / Single at 850 rpm; its kit with the Russian guns (drug labs, stashes), and
      with Extend Loot Areas on with the short SMGs instead; 9x18mm boxes in gun stores.
- [ ] **PP-91 Kedr** (Post-93): docs/post93_kedr_preview.png, docs/post93_design.md "PP-91 Kedr", CLAUDE.md "PP-91
      Kedr". Play it: held and holstered as the
      MP7, the stock folded (its butt plate round the barrel) and open, the bolt in the right port and the handle on
      the left, 1000 rpm, the PMM and RG028 loads in it, its kit with the Russian guns (with Extend Loot Areas on
      with the short SMGs instead).
- [ ] Release art, made 2026-11-26, one page per mod (user): preview45 the Skorpion (main mod), preview46 the Kedr
      (Post-93), preview47 the main mod's new ammunition of 3.25.0 (two calibres, eleven special loads), preview48
      Post-93's thirteen later loads; and the loot pages preview33-37 regenerated. All five loot pages changed, not
      only the two with the new guns: they also picked up the "no maker names" renames another session made the same
      night (gen_scripts.py GOM_NAMES), which had not been regenerated. Add preview45-48 to the Steam page with the
      upload. preview44 (TT-33 and PPSh-41) is all main mod and stays one page. preview41 (suppressor support)
      regenerated too: none of the new guns takes a can, but its heading counts every gun (now 42 of 87, 79 of 123
      with Post-93), so it goes stale with any new gun; upload it again.

### 2. Bizon family (Post-93, later: waits for more rounds)

The 9x18mm Makarov round exists since 2026-11-25 (main mod, plain only; boxes TUSKER). Its later loads (PMM 1994,
SP-7, RG028) belong in Post-93, with the PP-9 Klin.

- [ ] **PP-19 Bizon**, one gun per real version, named by its round: **Bizon Parabellum** (Bizon-2-01, 9x19, 53-round
      helical magazine), **Bizon Makarov** (Bizon-2, 9x18, 64-round), **Bizon Tokarev** (Bizon-2-07, 7.62x25; confirm
      it was real), and if their rounds come, the .380 Bizon-2-02 and the suppressed 9x18 Bizon-2-03. Each its own
      helical magazine (the calibres differ in barrel and bolt too, so no magazine swap between them). Built on GoM's
      AKS-74U (the real gun is mostly AKS-74 parts), held as a rifle, GoM's AK reload. The 9x18 Makarov round has
      its first guns since 2026-11-26 (the Skorpion vz. 82 and the PP-91 Kedr, above); it would also serve the CZ-83
      and the PP-9 Klin (a strengthened Kedr for the PMM load: the Kedr's model with other markings).

## Release 3.25.0 (built 2026-11-25, not uploaded)

- [ ] Play the new rounds: box and carton icons, open / pack recipes, Ammo Maker's Tokarev loads, Hot Brass casings.
- [ ] Upload GoT 3.25.0: **one release** for everything (user, 2026-11-26: "let's do one release only"): the
      A-91M 39 and A-91M 54 Prototype, the 20-round SV-98 magazine, the TT-33, PPSh-41, Skorpion vz. 82 and Kedr,
      the two calibres and the special loads; changenotes.txt is written. The user commits it and play-tests it on
      the live server (user, 2026-11-26), so it is uploaded before it is played. Previews built 2026-11-25: preview43 (the two guns), loot pages preview34 / 36 and the
      suppressor page preview41 regenerated; add preview43 to the Steam page.

## The A-91M (Post-93, rebuilt 2026-11-25 in eight remodel passes; model accepted 2026-11-25: "good enough")

- The A-91M Prototype's model (`A91MPROTO`, CLAUDE.md "A-91M Prototype") is accepted with its openings as they
  are (user, 2026-11-25: "looks like it's correct for the proto").
- [ ] Play it: the launcher swap and its raised sight leaf, the 20-round magazine in the well and in the off hand
      on the FAMAS reload (our own magazine, no hand copy: as the 9A-91's), the SV-98 with the 20 in (it hangs
      55 mm under the stock; not rendered), the charging hook riding back, optics on the handle, Hot Brass forward, loot, its numbers
      against the SVU and HK417.
- The decisions in docs/post93_design.md "KBP A-91M" were reviewed 2026-11-26: launcher integral and loot kept,
  the A-91M 39 takes GoM's PBS-1 (user: "let's allow A-91M 34 to be used with PBS please"; read as the 39, the
  PBS-1 being a 7.62x39 can). The shotgun loads' numbers (birdshot, flechette, Dragon's Breath) were approved
  the same day (user: "12g ammo stats are good to go too").
- [ ] Play it: the launcher swap (Gunworks radial), GoM's FAMAS reload with the AK magazines in the off hand, the
      charging hook riding back, optics on the handle rail, muzzle parts, Hot Brass forward, loot.

## Special rounds audit (2026-11-25: all built the same day; CLAUDE.md "Special rounds audit")

- [ ] Play them: each load's box, icon and Ammo Maker recipe; the flechette part recipe; the B-32 and Dragon's
      Breath fire in single player and on a server (a zombie run by another client), that no ground fire starts
      and corpses do not burn.

## Smaller open items

