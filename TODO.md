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

### 2. Bizon / Vityaz release, 3.26.0 (Post-93; wired 2026-11-28, not played)

The four guns (PP-19 Bizon 9x18, Bizon-2-01 9x19, Bizon-2-07 7.62x25, Vityaz 9x19) are built and wired: items,
models, Gunworks registries, rails, muzzles, stats, Hot Brass, tooltips, loot, icons, preview49, README / forum /
mod.info, changenotes.txt (3.26.0; both mod.info bumped). Everything as decided in docs/post93_design.md "PP-19
Bizon family" and CLAUDE.md "PP-19 Bizon family", except the two points below.

- [ ] **Decide**: no optional Picatinny top rail on the PP-19 and Bizon-2-01 (Q5 listed Up, Left, Right). GoM's AK
      mount and Picatinny_Rail_Up are both PartType RailUp (one or the other on a gun) and every optic has one
      `scope` point, which sits 12 mm higher on the AK mount than it would on a top rail; both on one gun would leave
      optics floating or sunk on one of them. Kept the AK mount (the real guns' optics mount). A top rail would need a
      riser model of ours drawn for Picatinny_Rail_Up on these two guns (its top at the AK mount's height).
- [ ] **Decide**: the Bizon-2-07 has no muzzle parts (TODO said "the 7.62x25 mount"): no 7.62x25mm muzzle family
      exists in either mod (the PPSh-41 and TT-33 take none). Making one = a mount device and a can of ours.
- [ ] Play it on a server: holding (rifle clips, all four upright), GoM's AK reload with each magazine in the off
      hand (the helicals are long; `_mag_prop2` puts their middle where GoM's AS VAL 20's is), the -2-07's box at
      `magazine_box` and helical at `magazine`, the Vityaz pair flipping sides (GoM's jungle animation; side 2 drawn
      at `magazine_2`, one magazine over) and the tape / part recipes, the -2-01 / Vityaz stock folding, the AK mount
      and optics, GoM's side / bottom rails and their lights, lasers and foregrip (the Vityaz's side rails are at
      its lower handguard's sides, read off the builder, never rendered), the 9mm cans, Hot Brass, loot.
- [ ] Upload with preview49 (the four guns) and the regenerated preview34 / 35 / 36 (loot) and preview41
      (suppressors: 42 of 87, 82 of 127) on the Steam page.
- Weak still (models, not blocking): the -2-07's AK-74 stock reads as a plank, the Vityaz's lower handguard is boxy,
  textures are plain (few markings), the selector / ejection side details are flat.

## Release 3.25.0 (uploaded 2026-11-26, not played)

- [ ] Play the new rounds: box and carton icons, open / pack recipes, Ammo Maker's Tokarev loads, Hot Brass casings.

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

- [ ] Boxy cross-sections (user, 2026-11-27: "we can make them polygonal ... HK416, HK417 and Scars have this
      problem too. Note them for now."): parts built as a side outline pushed out to a width read square in section in
      3/4 views. Make them polygonal (rounded or stepped sections, lofted like build_bizon.py ak_stock): the Bizons and
      the Vityaz (receiver, Bizon handguard, Vityaz lower handguard, grips), the HK416, HK417s and SCARs.

