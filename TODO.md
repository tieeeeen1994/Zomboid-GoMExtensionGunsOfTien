# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished features are not listed: they are taken as
working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.
Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Trigger audit (user, 2026-11-13: "Audit everything"; built, not played)

Every gun's trigger was laid over its measuring photo (renders at the photo's scale, the blade's middle compared
row by row; overlays and numbers in the session scratch `audit_A..D`, method in CLAUDE.md "Triggers must sit where
the photo has them"). Fixed and rebuilt (models only; icons not regenerated, the triggers barely show at 32 px):
HK416 / HK416 .22 / HK417s (GoM's AR15 trigger moved forward 6.7-12.4 mm), Vectors x4 (re-traced from the SDP photo:
15-18 mm too far back and curving the wrong way), AUG A1 / A3 / Para / HBAR (Steyr's deep block, it was a hook 17-21
mm too far forward; the opening's top-front corner rounded), RPD (trigger, guard loop and grip front re-traced from
the full photo: the white PNG had lost the guard's bar), Glock 21 and M249 (blades leaned the wrong way; the M249's
housing front was a post 8 mm too low), TMP (blade and the opening's rear wall), Mini / Micro Uzi (5.1 / 5.4 mm back),
RPK / RPK-74 (GoM's AK trigger 3 / 3.6 mm back), SCAR-L (tip curls forward), SCAR-H (4.5 mm back, low confidence),
Five-seveN, UCP, MDRx, UMP (the guard's top edge sat within two bevels of the opening, so the fill closed the opening
and buried the trigger; the top edge now reaches up inside the frame).

The 2026-11-14 fixes below (SR-25, Mk 11, Groza-1 GP-25, Mini / Micro Uzi, MP7, UCP, MDRx; UMP left as is) were
reviewed by the user on one sheet of outline overlays and approved ("these are fine").

SR-25 and Mk 11 (2026-11-14, checked on IMFDB's 4798 px Mk 11 Mod 0 side view, `SR25.jpg`, KAC's lower with the A2
grip and stock): the 2026-11-13 reading (opening 9 mm too tall, front wall 7 mm back) came from the small, downward
angled pic02 and did not hold. The real fault: `build_sr25.py` pinned the landmarks read from the grip's rear top to
GoM's origin, 35 mm behind it, squeezing GoM's grip, trigger and guard to 0.82 (opening 45 mm long against 51, grip
20 % thin, the magazine and everything ahead 35 mm too close to the hand). Every landmark now sits `GRIP_TOP` = 35 mm
further forward (KNOTS, ring, tube, gas block, stud, muzzle, scope, the Mk 11's handguard, sights and part points;
the overall length stays 1118 / the Mk 11's as before), and `align_trigger` moves GoM's blade 4.8 mm forward. Grip
edges, guard pins, the opening's front wall and floor now land within 1-2 px, the blade's middle within 0.4 mm on
three rows. Models and points rebuilt, scripts regenerated; icons and Workshop previews not redone.

Groza-1 with GP-25 (2026-11-14): the opening is not empty. One trigger fires rifle and launcher (selector), a crescent
forming the opening's rear edge (both photos), and the "rod" is its trigger bar across a window behind, closed below
by the frame. `build_groza.py` now builds that from wl_groza1_gl.jpg on the L / H grid: the opening 30.5 mm at L 156.5
(was 34 at 148), the crescent, the window and bar, the frame's bottom at H 96 (was 90) and its rear edge 10-15 mm
further back. Laid over the photo, all within about 1 mm but the opening's lower front corner (the photo's is squarer,
3-4 mm). The atlas is repacked (GROZA.png changes with the FBX).

Mini and Micro Uzi (2026-11-14, `build_uzi.py`): both guards were 4-7 mm bands where IMI's is a 2-3 mm stamped strip.
Mini (IMFDB MiniUzi_01.jpg, 1.9475 px a mm): the strip with its floor 2.8 mm lower, the housing's underside over the
opening rising from 111 to 114 (was flat at 110): the opening 32 mm tall (was 23); the blade's tip 3.4 mm further
forward and 2 mm lower. Micro (IMFDB Microuziextendedstock.jpg, 1338 px, the body registered at 2.81 px a mm, IoU 0.89;
the earlier "front wall 4-6 mm behind" came from the two small photos and did not hold): the strip, its underside
4 mm higher; the blade reaching to 1 mm over the floor, its tip forward (it stopped 7 mm higher); the housing's lump
at the opening's rear top. Laid over the photos, within about 1 mm. MINIUZI.png / MICROUZI.png are re-baked with the
FBX; the magazine textures were bake noise and restored.

MP7A1 / A2 (2026-11-14, `build_mp7.py` TRIGGER, GUARD_FILLET): measured on IMFDB's studio MP7A1 ("H&K MP71A1.jpg",
1400 px, the whole model registered at 3.18 px a mm, IoU 0.88, its guard on the photo's). The blade now stands upright
(front edge L 215.3-216.2) to H 92 and sweeps forward to its split tips (L 204.6-208, H 78.6-81); its upper body and
bar fill the opening behind it above H 93.5; the opening's lower rear corner is a 7 mm fillet. It was one
forward-leaning blade, its top 6 mm too far back. The angled Bundeswehr cut-out misplaces the tip by 3 mm (perspective):
use flat studio views. MP7A1.png / MP7A2.png re-baked; the magazine and part textures were bake noise and restored.

UCP (2026-11-14, `build_ucp.py` TRIGGER, TRIGGER_BAR): IMFDB's studio "Hk_ucp_3.jpg" (550 px, the model registered at
2.63 px a mm, IoU 0.94): the blade a 4.5 mm C bulging back to L 115.4 at H 83 and hooking forward to its tip at L 103
just over the floor (it bulged lower and further back and stopped at L 107), plus the trigger bar across the opening
behind it. Within about 0.5 mm. UCP.png re-baked; magazine and mount textures were bake noise and restored.

MDRx .223 / .308 (2026-11-14, `build_mdr.py` TRIGGER, TRIGGER_WINDOWS): Desert Tech's skeletonised trigger from its
studio right side (the model registered at 2.23 px a mm, IoU 0.98): curved front blade, straight rear bar, joined at
the tip and by a brace at H 91-92.5, two narrow windows (was a thin diagonal blade, its face about 3 mm back). Within
about 0.5 mm. MDR223.png / MDR308.png re-baked; the PMAG files were bake noise and restored.

M249 (2026-11-14, user: "the M249 might not be good"; `build_m249.py` GUARD_FRONT, GUARD): with the whole model
registered on the levelled USAF photo (IoU 0.83), the blade matched but the housing's curved front met the receiver at
L 594 where the photo shows background back to L 608; re-traced. The guard bar (user: the trigger "should not be
connected" to it, the bar "should be connected" to the grip): a 2 mm strip (it was 4 mm, touching the trigger's tip;
the photo clears it by about 1 mm), its rear a band curving up into the grip's front (it was a wedge meeting the grip
in a point), its front end at L 594.5 (was 597). Within about 1 mm. Approved by the user ("yes this is correct").

RPK-74: judged "good enough" by the user on the sheet (2026-11-14); left as is.

Steyr TMP (2026-11-14, user: "should be rebuilt"; `build_tmp.py` LOWER, GUARD_IN / GUARD_OUT, TRIGGER): the whole
model registered on the Commons photo (3.67 px a mm, IoU 0.93), the opening flood-filled off it and traced: its top at
H 180 (a pocket in the lower; it was 177), Steyr's large rounded top corners, the front wall out to L 107.3, the rear
at L 153.7, a 1.6 mm floor (it was 3 mm), the guard's rear running into the grip (no sliver gap), the blade re-traced.
Within about 1 mm. TMP.png re-baked. Approved by the user ("ok this is better"). The Grozas and the RPK were looked at on the same kind of sheet and judged good.

Accepted as they are (user, 2026-11-14, on the overlay sheets): SR-25 and Mk 11 (the small leftovers of GoM's AR15
shapes), RPK, RPK-74, UMP45 / UMP9, the Grozas, P90 / P90 TR / PS90. The MDRx docstring's photo side is corrected.

Icons regenerated 2026-11-14 for every gun the audit rebuilt (main mod: AUG, Glock 21, M249, Mini / Micro Uzi, RPD,
RPK, RPK-74, SR-25, TMP; Post-93: AUG A3 / HBAR, Five-seveN, Grozas, HK416, HK416 .22, HK417s, MDRx, Mk 11, MP7s,
SCARs, UCP, UMPs, Vectors) with each gun's make_*_art.py; magazine and part icons that came out identical or within a
few levels (bake noise) were restored from git.

- [ ] A look at every fixed trigger in game.
- [ ] Put preview27 / preview28 (3.15.0) on the Steam page by hand. The older previews still show the pre-audit
      triggers (a few pixels); redoing them needs the MP7 / SCAR / Vector specs moved to their `_RD` / `_FD` bodies
      first (CLAUDE.md, Workshop art).

## Next release: the HK416 / HK417 set (Post-93)

Agreed with the user 2026-11-13: four guns, two receivers (then three: the M-LOK .22 pistol was shelved). Only the HK416 is designed in `docs/post93_design.md`
so far; gather many references of each gun from every angle before modelling it, and follow the rules in CLAUDE.md (GoM's animations only, vanilla rifle / pistol hold + a GoM reload animId; sizes from the M16).

- [x] **HK416 D14.5RS** (built 2026-11-13, not played): model approved, items, Lua, loot, icon, docs (CLAUDE.md
      "HK416 D14.5RS", docs/post93_design.md). Its iron sights fold under optics (three bodies). Workshop preview
      (preview27, with the .22 pistol) and change note done; still to do: the in-game check.
- [x] **HK416 .22 Quad Rail Pistol** (built 2026-11-13, not played): Walther's gen-1 pistol only (user: "let's use
      walther's"; H&K USA's M-LOK pistol shelved, docs/shelved_hk416ml22.md): items, model scripts, Lua, loot (with
      the .22 LR box), icons, docs (CLAUDE.md "HK416 .22 Quad Rail Pistol"). Still open from the review: its 30-round
      magazine's length is estimated (no measurable photo of a 30). Workshop preview (preview27, with the rifle) done; still to do:
      the in-game check (pistol hold, sight states, magazines seating, Hot Brass place).
- [x] **HK417 16" "Recce" and 20" "Sniper"** (built 2026-11-13, not played): "HK417 Battle Rifle" / "HK417 Marksman
      Rifle", one receiver, H&K's 10 / 20 magazines, items, Lua, loot, icons, docs (CLAUDE.md "HK417 Recce and
      Sniper", docs/post93_design.md "H&K HK417"). Model approved (user: "it looks great"). Workshop preview (preview28)
      done; still to do: the in-game check.
- [x] **.22 LR round** (main mod, built 2026-11-13, not played): items, ammo type, family, Ammo Maker, Hot Brass, box
      art (CLAUDE.md ".22 LR").
- [x] **.22 LR special loads** (built 2026-11-13, not played): Subsonic, Hollow Point, Hyper Velocity; profiles,
      Ammo Maker types, Hot Brass, tooltips, art (CLAUDE.md ".22 LR"). Not loot, like the other special loads.

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
