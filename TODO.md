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

- [ ] **Short SMG arms, what is left** (2026-10-29, CLAUDE.md "The 12 kept clips swivelled" and "Snaps and hands in
      the belly"): the 12 old-level clips swivelled (eight at 1.0-1.2, the landing 1.4, run bump 1.6, sitting shiver
      1.7, tree walk 1.8), snaps smoothed in 30 clips, the gun moved out of the belly in 17; 50 clips changed in all.
      To do: approve from tmp/anim/review/gif, then play them in game (watch the blends in and out). Left: the
      no-aim walks' left wrist on the belly (4-5 cm against chest + pelvis, the stance's design), the sprint vault's
      last frame, 58 of 118 own clips past 1.1 against the chest. The vaults and the left bite reaction are
      vanilla's own depth. The sneaking stomach-pain emotes' right arm 2.8 / 2.4 shown.

## Audit

- [ ] **GoM's optional Picatinny rail upgrades on our guns** (user, 2026-10-28): GoM sells `MarzGuns.Picatinny_Rail_Up
      / _Down / _Left / _Right` as removable parts (MountOn lists in its rails.txt, drawn at the gun's `rail_up` /
      `rail_down` / `rail_left` / `rail_right` points) and ties each side to a kind of part: Up optics, Down foregrips
      and bipods, Left lights, Right lasers. None of our guns is in those lists yet (the AUGs above are the first). Go
      gun by gun through both mods (main: AUG A1, M249, Uzi, Mini Uzi, Micro Uzi; Post-93: MP7A1, MP7A2, P90 TR,
      SCAR-L / H, UMP45 / UMP9, Five-seveN, UCP) and list for each side: integral rail, a real rail that could be
      bolted on (an upgrade), or none (a grip, handle or slot in the way, or never made). Then decide with the user
      which upgrades to add (a model point each, the gun appended to the rail's MountOn).

## Bugs

- [ ] **No firing animation in one hand with the left hand full** (user, 2026-10-26: "Our guns in GoT that can be
      held with one hand has no shooting animation when the left hand is holding something else like an
      umbrella"). Not traced yet. To find out: which guns (the Mini Uzi, MP7s and MP5K only, or the P90 / Micro Uzi /
      pistols too, and whether GoM's own one-handed guns do the same); whether vanilla's pistol with an umbrella
      animates (engine) or only with Gunworks (its `RealSingle` / `RealAuto` / `RealBurst` nodes and their
      conditions); what `WeaponType.getWeaponType` gives for a two-handed gun in the primary hand with another item
      in the secondary.

## Decide

- [ ] One-hand penalty: the Mini Uzi, MP5K and MP7A1 / A2 held in one hand get the engine's rule for a two-handed
      weapon in one hand (half damage, 0.77 combat speed). Keep it, or not?

## Check in game

- [ ] **Steyr AUG A3, AUG Para, AUG HBAR** (Post-93, built 2026-10-28, docs/aug3_preview.png): held and reloaded on
      the bullpup stance (no "animation not found"), each magazine in the well (the Para's 9mm through its adapter, the
      HBAR's 50), the charging handle cycling, Fold / Unfold Foregrip, the HBAR's bipod toggle and its stats; GoM's
      optics on the top rail, lasers on the right, Picatinny Rail (Left) installed (drawn as our short rail, the
      universal rail offering only Left) with a light on it; the A3's AR muzzle parts, the Para's Mk9; found guns'
      parts, spawns, Hot Brass ejection from the port behind the grip.

- [ ] **FAMAS on the bullpup stance** (the AUG approved in game 2026-10-28, chest square): GoM's FAMAS carried, aimed
      and reloaded like the AUG (its carry handle and STANAG in the same places), no "animation not found".
- [ ] **Short SMG stance** (2026-10-28, CLAUDE.md "Animations are generic"): Uzi, Mini Uzi, MP7A1 / A2 in both
      hands: right way up, grip in the hand, the left hand at the one shared place (MP7 ~1-2 cm off it, accepted), tracers and muzzle flash at the barrel's end; no "animation not found" in the log (the old
      `GunsOfTien_CompactUzi` / `UziT` / `MP5K` / `MP7` names are gone). Reloads: Uzi / Mini Uzi (pistol family), MP7s
      (pistol magazine + rear T-handle rack); in one hand: Mini Uzi and MP7s on `UziGrip`, MP5K on GoM's
      `handgun2`, all upright with the same model. The full Uzi's new model (re-exported, new texture bake) in the hand,
      on the back (upright: its `rifle_back` points), on the floor. FAMAS on the one bullpup reload (the AUG's approved).
