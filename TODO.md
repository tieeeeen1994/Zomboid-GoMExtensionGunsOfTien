# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished and built features are not listed: they
are taken as working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings:
`CLAUDE.md`. Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## GoM's animations (2026-10-29; CLAUDE.md "GoM's animations only")

- [ ] **Play every gun on Guns of Marz's animations** (branch gom-anims): no "animation not found" in the log, no gun
      drawn upside down, each reload ends and swaps the magazine. Uzi held as a rifle (its model back to the upright
      one of before 2026-10-28; on the back too) on GoM's MP5 reload; Mini and Micro Uzi, MP7A1 / A2, P90 one-handed on
      its MP5K's ("handgun2"); Five-seveN, UCP on its pistol reload; AUG A1 / A3 / Para / HBAR on its FAMAS's; SCAR-L
      and SCAR-H on its BAR's (racked on the left, at the SCAR's handle); UMPs on its MP5's; M249 on its M60's (cover shut throughout); GoM's MP5s, MP5K
      and FAMAS back on GoM's own. Also a gun saved held in both hands (Mini Uzi, MP7s) and an MP5K saved with its
      old two-hand model.
- [ ] **Charging handles** (2026-10-29, CLAUDE.md "Charging handles move as GoM's do"): on every Uzi, MP7, P90, UMP
      and the M249 the handle flicks back on each shot, stays back when empty, moves with the rack, in the hands of the
      shooter and of other players; the Uzis' top slot, the P90's steel tracks, the MP7's new T-handle look right; an
      M249 from an older save shows its handle once equipped.

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
      umbrella"). Not traced yet; the Mini Uzi, MP7s and MP5K were two-handed then and are one-handed again since
      2026-10-29 (GoM's animations), so first see whether it still happens. To find out: which guns (the Mini Uzi, MP7s and MP5K only, or the P90 / Micro Uzi /
      pistols too, and whether GoM's own one-handed guns do the same); whether vanilla's pistol with an umbrella
      animates (engine) or only with Gunworks (its `RealSingle` / `RealAuto` / `RealBurst` nodes and their
      conditions); what `WeaponType.getWeaponType` gives for a two-handed gun in the primary hand with another item
      in the secondary.

## Check in game

- [ ] **Steyr AUG A3, AUG Para, AUG HBAR** (Post-93, built 2026-10-28, docs/aug3_preview.png): held and reloaded on
      GoM's FAMAS reload (no "animation not found"), each magazine in the well (the Para's 9mm through its adapter, the
      HBAR's 50), the charging handle cycling, Fold / Unfold Foregrip, the HBAR's bipod toggle and its stats; GoM's
      optics on the top rail, lasers on the right, Picatinny Rail (Left) installed (drawn as our short rail, the
      universal rail offering only Left) with a light on it; the A3's AR muzzle parts, the Para's Mk9; found guns'
      parts, spawns, Hot Brass ejection from the port behind the grip.
