# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished features are not listed: they are taken as
working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.
Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

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
