# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished features are not listed: they are taken as
working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.
Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Play-test before releasing 3.10.0

Built, never played. Tick each once seen working in game; details in the CLAUDE.md section named.

- [ ] **GoM's guns with Guns of Tien on** (the bug Marz reported, 2026-11-03; "The charging handle and the bolt are
      not always the same part"): GoM's M4A1 / M16 charging handle moves on the rack; a Python / SW629 cylinder
      swings out to reload.
- [ ] **Our charging handles** (same section): the AUG, Uzi, MP7, P90, UMP and M249 handles go back only while
      racked, the bolt still moves on each shot; an old gun without the handle gets it at its first rack.
- [ ] **Bipod stance** (Gunworks' BipodSystem, 2026-11-04): the M249, RPD, RPK / RPK-74 and AUG HBAR with the bipod
      deployed rest on a low wall or table while aiming, as GoM's M60, and leave the stance when moving.
- [ ] **US round and the PBS-1, on a server** (Gunworks' StatsSync, 2026-11-04): fit a PBS-1 to a held AK or RPK
      loaded with US Subsonic and it stops needing a rack after each shot; take it off and it needs one again.
- [ ] **P90 with its ring sight** (main mod, "P90 with its ring sight"): the turned model in the hand and on the back,
      GoM's side rails and what sits on them; 5.7x28mm (moved from Post-93 under the same ids) still works in old
      saves, with Post-93 on and off.
- [ ] **P90 trigger and stippled grips, every P90** ("Trigger and grips"): the trigger and stippling read at play
      distance, and the hand still sits right on the grip.
- [ ] **PS90 Carbine** (Post-93, "PS90 Carbine"): the hold with vanilla's rifle clips, GoM's FAMAS reload with the P90
      magazine in the off hand (its `Bip01_Prop2` worked out from GoM's STANAG, never seen), the Hot Brass drop from
      the chute.
- [ ] **Vector .45 Carbine** (Post-93, "Vector CRB"): in the hands and on the back, the stock folded and deployed,
      GoM's foregrips under the handguard, the .45 mount device and P45 on the shroud's face, the shared Vector .45
      loot.
- [ ] **Vector 9mm Pistol** (Post-93, "Vector SDP"): the one-handed hold and GoM's MP5K reload with the turned model,
      on the back, the Mk9's mount device over the thread protector, the shared Vector 9mm loot.

## Bugs

- [ ] **No firing animation in one hand with the left hand full** (user, 2026-10-26: "Our guns in GoT that can be
      held with one hand has no shooting animation when the left hand is holding something else like an
      umbrella"). Not traced yet, and the one-handed guns changed since (GoM's animations, 2026-10-29), so first see
      whether it still happens. To find out: which guns (ours only, or GoM's one-handed guns too); whether
      vanilla's pistol with an umbrella animates (engine) or only with Gunworks (its `RealSingle` / `RealAuto` /
      `RealBurst` nodes and their conditions); what `WeaponType.getWeaponType` gives for a two-handed gun in the
      primary hand with another item in the secondary.

## New Mod - EQUAL LOOT DISTRIBUTION

This will modify all loot so that all guns spawn without discrimination. Ammo and mags will still spawn beside the gun.
