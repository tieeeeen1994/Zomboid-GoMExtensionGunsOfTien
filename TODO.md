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

### 2. 9x39 release (Post-93, both on GoM's 9x39 and our SP-6)

- [ ] **9A-91** (1994), the compact Russian police carbine: its own 20-round magazine (check whether GoM's AS VAL
      magazine fits it, real or not), held as a rifle, GoM's AK reload (`ak_rifle`, as its AKS-74U and AS VAL). Its
      detachable suppressor: own can or none, ask.
- [ ] **VSK-94** (1995), the 9A-91's sniper version on the same receiver and magazines: built-in suppressor, skeleton
      stock, optic mount for GoM's optics.

### 3. Bizon family (Post-93, later: waits for more rounds)

- [ ] **PP-19 Bizon**, one gun per real version, named by its round: **Bizon Parabellum** (Bizon-2-01, 9x19, 53-round
      helical magazine), **Bizon Makarov** (Bizon-2, 9x18, 64-round), **Bizon Tokarev** (Bizon-2-07, 7.62x25; confirm
      it was real), and if their rounds come, the .380 Bizon-2-02 and the suppressed 9x18 Bizon-2-03. Each its own
      helical magazine (the calibres differ in barrel and bolt too, so no magazine swap between them). Built on GoM's
      AKS-74U (the real gun is mostly AKS-74 parts), held as a rifle, GoM's AK reload. The 9x18 Makarov round it
      waits for would also serve the CZ-83, Skorpion vz. 82, PP-91 Kedr and PP-9 Klin (PMM as its [+P] load);
      Ammo Maker has `9x18Mak`, Hot Brass no 9x18 casing (its 9x19 one would do).

## Attachments and muzzle parts audit (3.20.0, built 2026-11-23, not played)

- [ ] Load a world saved before it with an old 9x19mm SMG mount on an Uzi / MP5 and one loose: both become GoM's
      "9x19mm Family Muzzle Mounting Device" (server log `[GunsOfTien] removed parts: swapped ...`), the Mk9 stays on.
- [ ] GoM's 9mm mount on the SMGs is drawn as our adapter; the Groza-2's AK mount and PBS-1 sit on its barrel.
- [ ] The AA-12's side rails, lights and lasers and the G36's bipod are drawn where gom_points.py put them; a bipod
      saved on an M4A1 / MP5 comes off beside the gun; gun and magazine tooltips read as GunLines.lua writes them.
- [ ] Update Parts on Saved Guns off: nothing is swapped or taken off; on again: the next load does it.

- [ ] After the 3.20.0 upload: put preview39 (muzzle devices), preview40 (SureFire devices) and preview41
      (suppressors) on the Steam page by hand.

## Ammo Maker part cartons (3.19.0, built 2026-11-21, not played)

- [ ] After the 3.19.0 upload: put preview38 (part cartons and crates) on the Steam page by hand.

## Loot (3.18.0, built 2026-11-21, not played)

- [ ] After the 3.18.0 upload: put preview33-37 (where the guns are found) on the Steam page by hand.

## SVU, SV-98, SV-99 (3.17.0, built 2026-11-20, not played)

- [ ] Play them: the SVU's FAMAS reload and folding sights, the SV-98 / SV-99 magazine bolt-action reload (GoM's
      `*Rifle_HB.xml` nodes with a Gunworks "boltaction" profile, never used by GoM itself), the rack after every shot,
      the SV-99's lever swing, the integrated bipods, loot.
- [ ] After the 3.17.0 upload: put preview31 (the SVU) and preview32 (the SV-98 / SV-99) on the Steam page by hand.
- [ ] The variant left out (the aluminium SV-98), if wanted. The SV-99 stays one gun (user, 2026-11-20).

## After the 3.16.0 upload

- [ ] Put preview30 (the Walther PPK) on the Steam page by hand.

## After the 3.15.0 upload

- [ ] Put preview27 / preview28 (3.15.0) on the Steam page by hand. The older previews still show the pre-audit
      triggers (a few pixels); redoing them needs the MP7 / SCAR / Vector specs moved to their `_RD` / `_FD` bodies
      first (CLAUDE.md, Workshop art).
- [ ] The HK416 .22's 30-round magazine length is an estimate (no measurable photo of a 30); re-measure if one
      turns up.

## GoM resized its MP5s itself (found 2026-11-14)

- [ ] Decide whether to drop our MP5 resize (`scripts/build_mp5.py`, `zz_GunsOfTien/models_mp5.txt`). GoM's update of
      2026-11-10 shrank the MP5 / MP5A2 / MP5SD / MP5K meshes, their five magazines and every point by one factor,
      **0.7793** (MP5A2 body 0.4938 -> 0.3848 long, MP5K 0.2344 -> 0.1826); ours is 0.8332 of his old meshes, so ours
      still replaces his in game (his textures are unchanged, so ours still draw right). scale_audit.py on GoM alone:
      MP5A2 / MP5K 0.57 / 0.56 of real size, MP5 / MP5SD 0.54, against his unchanged M16A2 at 0.603, i.e. ~7% under
      our guns' proportion (ours sit at 0.605). Tried and reverted 2026-11-14 (too many knock-ons for now). Dropping it
      means:
  - remove `zz_GunsOfTien/models_mp5.txt`, `GunsOfTien_MP5.fbx`, `GunsOfTien_MP5_magazines.fbx`, `build_mp5.py`,
    `mp5_points.json`, `gen_scripts.py mp5_family()` (keep the "MP5A3 Submachine Gun" name, `MP5_NAMES`);
  - `models_onehand.txt` MP5K_1H / MP5K_2H: point at GoM's `weapons/firearms/MP5K|MP5K_BODY` (SavedModels.lua copies
    the points);
  - Mk9: GoM's MP5 / MP5A2 still have no `canon`, so Suppressors.lua adds it at run time again (measured on the new
    meshes: MP5 0.2178, MP5A2 0.2190, z 0.0301, exactly 0.7793 x the old; build_mk9.py `GOM_GUNS` z 0.0301 and its
    radii x 0.7793), and draws the parts through new `<part>_MP5` models at scale 0.7793 so the mount fits the barrel
    (`_GoT` stays for the Uzis, TMP, UMP9);
  - MuzzlePoints.lua: GoM's MP5 / MP5A2 / MP5K muzzles are at the barrel's end now, but the MP5SD's is at the MP5's
    place (0.2422), 5.4 cm inside its can: set it to 0.2964;
  - README / forum.txt / mod.info lose the "drawn to the Uzis' scale" line, a changenote, CLAUDE.md "Gun scale" and
    docs/gom_gun_scale.md;
  - check in game: the Mk9 seated on GoM's MP5 / MP5A2, the MP5SD's flash at the can's end, GoM's MP5s next to our
    Uzis / UMP9 (~7% smaller).
  Nothing else of GoM's is redrawn by us (GoM's magazine files other than smgs.fbx last changed before our STANAG /
  AK `_GoT` scales were set).

## New Mod - EQUAL LOOT DISTRIBUTION

This will modify all loot so that all guns spawn without discrimination. Ammo and mags will still spawn beside the gun.
Sub-mod "Loot Equalizer", parked 2026-11-15: decisions, the spawner-table takeover idea and the open questions are in
`docs/equal_loot_design.md`.
