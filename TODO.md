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

### 2. Bizon / Vityaz release (Post-93; back from the shelf 2026-11-27, design: docs/post93_design.md "PP-19 Bizon family")

Four guns (user, 2026-11-27: "We can build 4 guns. Bizon Parabellum, Bizon Tokarev, Bizon Makarov and Vityaz"),
no new rounds. Every Vityaz is 9x19 (none in another calibre), the .380 Bizon-2-02 / -06 is out (no .380 round).
Names: real designations + "Submachine Gun" (user: "Let's use Bizon Submachine Gun"); every one two-handed and
never holstered (the stockless Makarov too). Vityaz = the plain PP-19-01, not the SN (Q1 answered).
Everything agreed (2026-11-27). The -07's aftermarket parts are game-style, not a real product (user: "maybe you
can refer to call of duty longer barrel or stuff. So basically just lengthen the barrel"): the same barrel drawn
longer, 345 mm (the Saiga-9's civilian 9mm barrel, a real Kalashnikov length), out past the railed handguard.

| | PP-19 Bizon Submachine Gun | Bizon-2-01 Submachine Gun | Bizon-2-07 Submachine Gun | Vityaz Submachine Gun |
|---|---|---|---|---|
| Item | `BIZON` | `BIZON201` | `BIZON207` | `VITYAZ` |
| Real | Bizon (1993), 9x18 | Bizon-2-01, 9x19 | Bizon-2-07 (1997), 7.62x25 | PP-19-01 (2004), 9x19 |
| Barrel | 195 mm (real) | 225 mm (real) | 345 mm, lengthened (aftermarket, game-style; real 225, one source) | factory |
| Stock | none, end cap (user: smallest round = stockless) | AK folding | fixed AK-74-style polymer stock (Q4) | AK folding |
| Hold | rifle, two-handed, not holstered | rifle | rifle | rifle |
| Magazine | own 64 helical | own 53 helical | real 35 box + invented helical (Q3) | own 30 box + clipped 2x30 pair (Q2) |
| Optics | GoM's AK side mount on the modelled dovetail rail, or the optional top rail | the same | the integrated top rail (dovetail rail modelled too) | GoM's AK side mount only (real plain cover) |
| Rails (Q5) | optional Up, Left, Right | optional Up, Left, Right | integrated Up, Left, Right (railed handguard), no Down | optional Down, Left, Right (no Up: user, 2026-11-27) |
| Muzzle | own Bizon compensator, modelled | 9x19 family mount | 7.62x25 mount | 9x19 family mount |

- [x] **Q1**: plain PP-19-01 Vityaz (user, 2026-11-27: "let's use the non-SN version call it Vityaz Submachine Gun").
- [x] **Q2**: the Vityaz's clipped 2x30 pair as an extra magazine item, Gunworks' stacked packs as GoM's jungle 2x30
      (user, 2026-11-27: "Yes").
- [x] **Q3**: the Bizon-2-07 takes both (user, 2026-11-27: "the real 35 round box, as well as an invented helical
      mag"): the real 35 box and an invented helical, named as invented (45 rounds, agreed: 53 x 29.7 / 34.9 mm,
      the 9x19 and 7.62x25 cartridge lengths). One Gunworks profile (as the RPK's 40 + drum), a magazine point each.
      No bottom rail on the -07 (user, 2026-11-27), so no foregrip clashes with the helical.
- [x] **Q4**: the Bizon-2-07's stock is a fixed AK-74-style polymer stock (user, 2026-11-27).
- [x] **Q5**: GoM's optional Picatinny rails (`Picatinny_Rail_<side>`, as the TMP / Uzis; user, 2026-11-27: "table as
      it is"): PP-19 Bizon and Bizon-2-01 optional Up, Left, Right (the helical blocks Down); Bizon-2-07 integrated
      Up, Left, Right on its railed handguard, nothing optional; Vityaz optional Down, Left, Right, no Up (user,
      2026-11-27: "Vityaz gets ak mount rail and maybe optional picatinny on down left and right"). All four have the
      real AK dovetail side rail modelled on the left (real Bizons have it too: commons_040, cca_020); the two
      Bizons and the Vityaz take GoM's AK side mount on it.
- [x] Reference hunt (2026-11-27, three passes; per file in docs/post93_design.md "Hunt so far"): references/bizon/
      130 (Commons' whole Category:PP-19 less its Vityaz subcategory, Chester County Armory's studio set `cca_*`,
      Hexagon's box-fed tuned Bizon `hexagon_*`, the one -07 photo `vpk_000`, assorted web; `gom_aks74u/`) and
      references/vityaz/ 96 (all of Commons' Category:PP-19-01 and Saiga-9, RIA's KP-9 and KR-9 at 2400-4800 px,
      modernfirearms, vpk). Measuring photos: Bizon `commons_040` (left, white) / `cca_*`; Vityaz `ria_001-003`
      and `commons_014`. The -07 has one photo: the rest of it is reasoned from the Bizon (user: "we can make smart
      guesses based on the description and how the guns work").
- [x] Models: first build done 2026-11-27 (docs/post93_bizon_preview.png); user: "they're honestly good".
      Polished the same day (user: "polish it. let's also do different colors for each bizon if available"): the
      -07's stock in two rounded pieces (25 mm wrist, 32 mm body), the Vityaz's lower handguard rounded and ribbed,
      its magazine well black; colours per gun (build_bizon.py BODY_COLOURS): PP-19 plum grip, -2-01 all black,
      -2-07 plum AK-74 stock and grip, Vityaz all black (user: "leave vityaz black"). Then the user questioned the
      shapes ("they're not truly accurate"): overlaid on the KP-9 photo the Vityaz had the Bizon's grip (now its own
      AK-74M-pattern grip, 10 mm longer, toe 20 mm further back), a straight magazine 4 mm too thin (now curved,
      35 mm deep) and its folded stock riding 20 mm over the cover (now under it). The user disliked the Vityaz's
      handguard / receiver joint: it had a 29 mm gap under the rear sight base (barrel and a see-through slit only);
      now the handguard runs to the receiver (finger stop rising into it as on the KP-9) and the receiver's front
      is one piece with the rear sight base (no seam line), merged 4 mm into the handguard, with its rivets. Overlay sheet: docs/post93_bizon_overlay.png.
      Second overlay pass (render_bizon.py photo views, all four on docs/post93_bizon_overlay.png): the PP-19's cover
      end re-read at 12 px a mm (was 3-5 mm full) with the recoil spring button, the end cap cut to 5 mm past the
      rear face under the cover's end; the Vityaz's rear sight base front raised to the KP-9's, slider 3.5 mm lower,
      leaf notch ears; the AKS-74 stock x 0.97 behind the hinge (660 mm open as published, it made 667; cca_000
      stretched 1/0.88 agrees); the -2-07's box 38 mm deep (was 31, under a 35 mm round), radius 360, 171 long, lips
      at L 277 (vpk_000, scaled by the trigger guard). The Vityaz follows the real PP-19-01 (user,
      2026-11-27: "let's follow the real one"): plain AK-74 cover, the AK dovetail side rail on the left of the
      receiver (SIDE_RAIL, Kuzmin's commons_005; on every body), where GoM's AK side mount goes. The AKS-74 stock's
      butt and strut re-read off cca_019 (the user disliked the hooked butt): a straight-backed plate, its front
      curving into the strut (growing out of the hinge lug flush with its bottom, 20 mm deep at the butt), the top tube into the butt; the hinge
      block kept at its old depth (lowered to H 84 it read badly proportioned). The -2-07's stock wrist fills the
      corner under the cover's rounded end (no crevice). Third pass (user, 2026-11-27: "fix then" to a defect sweep,
      the -07 stock, the Vityaz magazine): no floating parts, the folded stocks only meet the body at the hinge;
      the folds re-fitted on photos laid on the model frame by hand (commons_040 for the Bizon, commons_005 for the
      Vityaz: tmp/bizon/c040m_trace.json, c005m_trace.json; the old trace was scaled to the sling): the hinge pin at
      the receiver's rear face (L 422.5, the open butt at L 660 folds to the photo's L 185), Bizon fold pitch 9.5
      no lift, Vityaz 12 down 6, the hinge block 15 mm long; the -07 stock lofted in one piece (ak_stock: rounded
      sections, 25 mm wrist flaring to 33, the side groove pressed in, no seam); the Vityaz 30's stepped sleeve over
      its lower half (V_MAG_SLEEVE, the pair's clamps round it); the body atlas 1024 (painted rivets and ribs were
      blocky at 512). Cross-sections: see "Smaller open items".
      `scripts/post93/build_bizon.py` (all four bodies on one AK receiver: the Vityaz's is the same receiver, laid on
      by the KP-9 photo; BIZON_BOLT, the AKS-74 stock open / folded for the -2-01 and a flatter fold for the
      Vityaz; magazines: three helicals of one shape, the -07's curved 35, the Vityaz 30 and its clipped pair;
      BIZON.png 1024), `render_bizon.py -- DIR` (absolute DIR), `make_bizon_preview.py DIR`. Measuring photo
      references/bizon/raw/cca_007.jpg (tmp/bizon/cca007_trace.json, overlay within 1-2 mm). Weak still: the
      -07's AK-74 stock reads as a plank, the Vityaz's lower handguard is boxy, textures are plain (few
      markings), the selector / ejection side details are flat. GoM's optional rails are not placed yet.
- [ ] Wiring (models done 2026-11-27; user: "add the wiring in TODO"). Items BIZON, BIZON201, BIZON207, VITYAZ;
      magazines 9x18Magazine64_BIZON, 9x19Magazine53_BIZON, 762x25Magazine35_BIZON, 762x25Magazine45_BIZON (invented,
      named so), 9x19Magazine30_VITYAZ, 9x19Magazine30_VITYAZ_PAIR. All rifle-held, two-handed, never holstered.
  - [ ] Item scripts: guns and magazines (weights, capacities, display names, icons), Post-93 add-on only.
  - [ ] Model scripts: GunsOfTienPost93_BIZON.fbx bodies (BIZON_BODY, BIZON201_BODY, BIZON207_BODY, VITYAZ_BODY),
        BIZON_BOLT, stocks (BIZON_STOCK_DEPLOYED / _FOLDED, VITYAZ_STOCK_FOLDED), the magazines fbx; attachment
        points from scripts/post93/bizon_points.json (muzzle, canon, magazine / magazine_box per gun). The model
        script file must sort after GoM's MarzWeapons/ (re-declared models are reset by later blocks).
  - [ ] Gunworks registration the GoM way (no wrapping): profiles, reload anims (rifle hold + a GoM reload animId:
        helicals and the box like GoM's AKs), the -2-01 / Vityaz folding stock swap (open / folded models), the
        Vityaz 2x30 pair as a stacked pack like GoM's jungle 2x30 (Q2), the -2-07's two magazines on one profile
        (box 35 + helical 45, one point each, as the RPK's 40 + drum).
  - [ ] Rails / optics (Q5, updated 2026-11-27): every body has the modelled AK dovetail side rail; GoM's AK side
        mount on the two Bizons and the Vityaz; optional Picatinny rails: PP-19 and -2-01 Up / Left / Right, -2-07
        integrated Up / Left / Right (no Down), Vityaz Down / Left / Right (no Up). Place the rail points.
  - [ ] Muzzles: the PP-19's own compensator (modelled), -2-01 and Vityaz the 9x19 muzzle family, -2-07 the
        7.62x25 mount.
  - [ ] Stats against their peers: PP-19 (9x18) vs Kedr / Skorpion, -2-01 vs GoM's MP5, -2-07 vs PPSh-41, Vityaz
        vs GoM's MP5; the -2-07's longer barrel (345 mm).
  - [ ] Sounds, Hot Brass casings, generated tooltips (GunLines.lua only, no hand-written lines), translations.
  - [ ] Loot with the Russian guns (police / military), magazines and ammo alongside.
  - [ ] Play-test in game: holding, aiming, reloads (all four magazine kinds and the pair), folding, attachments.
  - [ ] README / forum post / changenotes, a Workshop preview page; release with 2+ new guns (here four).

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

- [ ] Boxy cross-sections (user, 2026-11-27: "we can make them polygonal ... HK416, HK417 and Scars have this
      problem too. Note them for now."): parts built as a side outline pushed out to a width read square in section in
      3/4 views. Make them polygonal (rounded or stepped sections, lofted like build_bizon.py ak_stock): the Bizons and
      the Vityaz (receiver, Bizon handguard, Vityaz lower handguard, grips), the HK416, HK417s and SCARs.

