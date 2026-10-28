# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished and built features are not listed: they
are taken as working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings:
`CLAUDE.md`. Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Generic animations (release 3.4.0 held for these; CLAUDE.md "Animations are generic")

Done 2026-10-28 (built; the MP5 family, the MP5K on the MP5A3's hold and their H&K reload approved in game the same
day, the rest not played; see "Check in game"): one short SMG stance in the pistol orientation, reloads
by family (short SMG: pistol, H&K, pistol + rear T-handle; GoM's MP5s on the UMPs' H&K reload; one bullpup family),
the full Uzi re-exported in pistol orientation, the bullpup stance (draft B, a tucked carry) with its reloads rebuilt
on it. Still to do:

- [ ] To decide: the SCAR-H's own reload under the rule (a side-forward charging handle family with the SCAR-L and
      FAL, maybe the H&K guns).

## Bugs

- [ ] **No firing animation in one hand with the left hand full** (user, 2026-10-26: "Our guns in GoT that can be
      held with one hand has no shooting animation when the left hand is holding something else like an
      umbrella"). Not traced yet. To find out: which guns (the Mini Uzi, MP7s and MP5K only, or the P90 / Micro Uzi /
      pistols too, and whether GoM's own one-handed guns do the same); whether vanilla's pistol with an umbrella
      animates (engine) or only with Gunworks (its `RealSingle` / `RealAuto` / `RealBurst` nodes and their
      conditions); what `WeaponType.getWeaponType` gives for a two-handed gun in the primary hand with another item
      in the secondary.
- [ ] M249 belt reload clips (`scripts/anim/m249_reload.py`): the left elbow flips (AimRack worst). The stock in the
      chest and the left hand 1-3 cm short of the cover and handle are accepted.

## Decide

- [ ] One-hand penalty: the Mini Uzi, MP5K and MP7A1 / A2 held in one hand get the engine's rule for a two-handed
      weapon in one hand (half damage, 0.77 combat speed). Keep it, or not?

## Check in game

- [ ] **FAMAS on the bullpup stance** (the AUG approved in game 2026-10-28, chest square): GoM's FAMAS carried, aimed
      and reloaded like the AUG (its carry handle and STANAG in the same places), no "animation not found".
- [ ] **Short SMG stance** (2026-10-28, CLAUDE.md "Animations are generic"): Uzi, Mini Uzi, MP7A1 / A2 in both
      hands: right way up, grip in the hand, the left hand at the one shared place (MP7 ~1-2 cm off it, accepted), tracers and muzzle flash at the barrel's end; no "animation not found" in the log (the old
      `GunsOfTien_CompactUzi` / `UziT` / `MP5K` / `MP7` names are gone). Reloads: Uzi / Mini Uzi (pistol family), MP7s
      (pistol magazine + rear T-handle rack); in one hand: Mini Uzi and MP7s on `UziGrip`, MP5K on GoM's
      `handgun2`, all upright with the same model. The full Uzi's new model (re-exported, new texture bake) in the hand,
      on the back (upright: its `rifle_back` points), on the floor. FAMAS on the one bullpup reload (the AUG's approved).
