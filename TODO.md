# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished features are not listed: they are taken as
working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.
Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Bugs

- [ ] **No firing animation in one hand with the left hand full** (user, 2026-10-26: "Our guns in GoT that can be
      held with one hand has no shooting animation when the left hand is holding something else like an
      umbrella"). Not traced yet, and the one-handed guns changed since (GoM's animations, 2026-10-29), so first see
      whether it still happens. To find out: which guns (ours only, or GoM's one-handed guns too); whether
      vanilla's pistol with an umbrella animates (engine) or only with Gunworks (its `RealSingle` / `RealAuto` /
      `RealBurst` nodes and their conditions); what `WeaponType.getWeaponType` gives for a two-handed gun in the
      primary hand with another item in the secondary.

## Next release: the HK416 / HK417 set (Post-93)

Agreed with the user 2026-11-13: four guns, two receivers. Only the HK416 is designed in `docs/post93_design.md`
so far; gather many references of each gun from every angle before modelling it, and follow the rules in CLAUDE.md (GoM's animations only, vanilla rifle / pistol hold + a GoM reload animId; sizes from the M16).

- [x] **HK416 D14.5RS** (built 2026-11-13, not played): model approved, items, Lua, loot, icon, docs (CLAUDE.md
      "HK416 D14.5RS", docs/post93_design.md). Its iron sights fold under optics (three bodies). Still to do for the
      release: the Workshop preview (render_ad_guns.py / make_workshop_art.py) and the change note.
- [ ] **HK416 .22 LR pistols, both generations** (user, 2026-11-13: "WHY NOT BOTH???"; pistol-held confirmed):
      Walther's quad-rail "HK416 .22 Tactical Pistol" (about 2009/10-2018) and H&K USA's M-LOK "HK416 .22 LR Pistol"
      (2019-), sharing H&K's 10 / 20 / 30-round .22 magazines. References gathered (references/hk416_22/,
      SOURCES.txt, contact sheets); design decided in docs/post93_design.md "H&K HK416 .22 LR pistols" (gen 2 in HK
      bronze, "Quad Rail" / "M-LOK" names, Auto + Single, gen 1's shroud an integral suppressor, no can part).
      Models built for review 2026-11-13 (CLAUDE.md "HK416 .22 LR pistols"), **waiting on the user's verdict**
      (review images: rerun `render_hk416_22.py`; photo overlays as in that section). Open points put to the user:
      the M-LOK pistol's flip-up sights are plain blocks; the 30-round magazine's length is estimated (the 20's curve
      carried on 42 mm, no measurable photo of a 30); the Quad Rail's shroud is an integral suppressor by the user's
      choice, but the real one is only a barrel shroud (realistic = as loud as the M-LOK). After approval: items, model
      scripts, Lua (IronSights.Register, stats, the ".22 LR" magazine family), loot (with the .22 box), icons, the
      clash run against GoM's optics (fit_audit).
- [ ] **HK417 D16RS "Recce"**: the standard 16" 7.62x51 rifle; its own 10 / 20-round magazines (real HK417
      magazines do not fit the SR-25, so not the SR-25's).
- [ ] **HK417 D20RS "Sniper"**: the longest, original pattern: 20" barrel, 1,085 / 1,005 mm, 4.23 kg; the Recce's
      receiver, stock and magazines with a longer barrel and handguard. Same job as the Mk 11 Mod 0, so give it
      stats of its own.
- [x] **.22 LR round** (main mod, built 2026-11-13, not played): items, ammo type, family, Ammo Maker, Hot Brass, box
      art (CLAUDE.md ".22 LR").
- [x] **.22 LR special loads** (built 2026-11-13, not played): Subsonic, Hollow Point, Hyper Velocity; profiles,
      Ammo Maker types, Hot Brass, tooltips, art (CLAUDE.md ".22 LR"). Not loot, like the other special loads.
- [ ] **.22 LR loot**: GoM spawns each calibre's standard box, so the .22 box should spawn; decide where with the
      .22 pistol.

## Iron sights under optics: audit every gun (user, 2026-11-13)

- [x] (built 2026-11-13, not played; CLAUDE.md "Iron sights under optics": the MP7s, SCARs and Vectors got the
      HK416's states, the UMPs' long scopes moved forward, the rest clear) The HK416 folds its iron sights when an
      optic is fitted (Gunworks' `ConditionalModel` on the Scope slot,
      CLAUDE.md "HK416 D14.5RS"); none of our other guns do, so standing sights clip GoM's optics or look wrong under
      them. Go through every gun of both mods that takes an optic: which iron sights it has (fixed, flip-up, carry
      handle, none), what the real gun does with them under a red dot and under a magnified scope (fold, remove, stay
      and co-witness), and build the folded / removed bodies where they differ. Guns with fixed sights that cannot
      fold (front sight towers, AK sights) stay as they are; check whether optics clear them (fit_audit).

## New Mod - EQUAL LOOT DISTRIBUTION

This will modify all loot so that all guns spawn without discrimination. Ammo and mags will still spawn beside the gun.
