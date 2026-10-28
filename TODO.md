# TODO

Open work on GoM Extension: Guns of Tien and its Post-93 sub-mod. Finished and built features are not listed: they
are taken as working once played. Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings:
`CLAUDE.md`. Shelved: resizing Guns of Marz's guns, `docs/gom_gun_scale.md`.

## Generic animations (release 3.4.0 held for these; CLAUDE.md "Animations are generic")

In order:

- [ ] **Short SMG test render**: the Mini Uzi, MP7 and MP5K drawn with the stance's gun bone in the pistol orientation,
      no upright turn and no per-set gun shift. They should look as they do today, grip in the hand.
- [ ] **One short SMG stance** for the Uzi, Mini Uzi, MP7A1 / A2 and GoM's MP5K (MP5A3 / A2 / SD stay with the UMPs:
      550-680 mm, stocks shouldered), built in the pistol orientation; the approved aim with the Uzi's left-hand place
      for all four. Re-export the full Uzi's mesh in pistol orientation; remove the upright turn, `TURNED_SETS`, the
      Uzi / UziT / MP5K / MP7 sets and OneHand.lua's one-hand models. Small clipping and hands a little off are
      accepted.
- [ ] **Reloads by family** (magazine and rack chosen separately; reload nodes are XML):
      - Uzi, Mini Uzi, and the Micro's `UziGrip`: generic pistol magazine change and rack (GoM's `handgun2`).
      - MP7A1 / A2: pistol magazine change + rear T-handle rack (its current rack, made the generic one; kin: Steyr
        TMP, B&T MP9, ARs). Its one-hand reload on the pistol family too.
      - MP5K: H&K on the short SMG stance.
      - GoM's MP5A3 / A2 / SD: the UMPs' H&K reload instead of GoM's own.
      - AUG and FAMAS: one bullpup family (one magazine place, one rack).
- [ ] **Check in game**: entering a pistol reload from the short SMG stance (0.2 s cross-fade; hands and gun blend
      separately). If they part, build a lead-in / lead-out into that stance + family pair's clips (a transition clip
      cannot do it: CLAUDE.md "Animations are generic").
- [ ] **Bullpup stance drafts** (stills to choose from), for the AUG, FAMAS and later the AUG A1. Ours is vanilla's
      rifle hold with the palm moved back: the gun is held by the grip at the hip, and with the magazine, action and
      butt all behind the grip it hangs back past the hip with the short front up and left (it dangles). Research
      (2026-10-28): the support hand sits near the muzzle on the handguard or the AUG's front grip folded down; the
      rearward balance makes a low ready easy and the raise to aim a hinge; the magazine is the part by the armpit;
      the length of pull is a rifle's, so shouldered hands sit where a rifle's do with the support hand 10-15 cm
      nearer. One left-hand place fits both (just ahead of the trigger guard). Drafts:
      - A. Shouldered low ready: butt in the shoulder pocket, gun tilted 30-45 degrees down, hands as in the aim.
      - B. Tucked carry: butt against the side under the right arm, gun along the forearm, muzzle down and forward,
        support hand on the front grip.
- [ ] Then the bullpup stance built from the chosen draft (the compact_build machinery), replacing the rifle_hand
      Bullpup set.
- [ ] To decide: the SCAR-H's own reload under the rule (a side-forward charging handle family with the SCAR-L and
      FAL, maybe the H&K guns).
- [ ] Cleanup before rebuilding the UMP set: rifle_hand.py's "UMP" entry and smg_reload.py `ump_spec` still carry the
      reverted de-clip (`contact`, `guns`, `aim_push`); take it out (CLAUDE.md "No clipping").

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

## New guns

- [ ] **Steyr AUG A1** (user, 2026-10-27: "start with AUG A1"; main mod, 1977). Not in GoM or Gunworks. Proposal,
      not approved yet:
      - Size: the M16 as the basis (user, 2026-10-27), i.e. K = 0.000603 per real mm as every gun of ours: 790 mm
        real → 0.476 units. Its magazines are its own, so no shared-magazine scale applies.
      - Stats from GoM's M16A1 (same round, same 508 mm barrel, Auto / Single): damage 1.0-1.8, range 50, crit 20,
        jam 1, condition 1 in 150, ConditionMax 10; the built-in 1.5x optic baked in (HitChance and crit ×1.05, sight
        range ×1.15, between GoM's Aimpoint and LR4X); about 700 rpm, spread 0.12 / 2.2 (M16A1 0.15 / 2.5, FAMAS 0.1 /
        2.0); weight 3.6 (GoM's rifles weigh real); sound as the M16A1 (sound_model.py).
      - Magazines: profile "AUG", Steyr translucent 30 and 42 (the HBAR's), family `5.56x45mm`; not STANAG, not
        GoM's G36 magazine.
      - Folding vertical front grip on its own toggle (the MP7A1's way); no rails, optics, lights, lasers or
        suppressors on a 1993 A1.
      - Bullpup stance and bullpup reload family (no animation of its own); Hot Brass from GoM's FAMAS values, to the
        right; RepairPack at GoM's assault rifles' Aiming level.
      - To decide with the user: select-fire A1 only, or also the semi-automatic AUG SA on the same model (the one a
        1993 Kentucky civilian could own, imported 1983-1989) and where each spawns; green, black or both textures;
        bayonet (Austrian Glock knife; a lug on the SA not confirmed); a side-on reference photo (the user's, or a
        public-domain / CC one from Commons).
      - Later AUGs: 9mm Para (late 1980s) in the main mod; USR, A2, A3, NATO stock (STANAG) in Post-93.

## Check in game

- [ ] GoM's MP5 family at the Uzis' size (2026-10-27, scripts/build_mp5.py, models_mp5.txt): no "model script not
      found" / mesh errors in the log; the MP5 (named "MP5A3 Submachine Gun"), MP5A2, MP5SD and MP5K about 17% smaller,
      with GoM's textures, in the hand, on the back / in the holster and on the floor; every magazine (20 / 25 / 30 / 60
      / 100) seated in each of the four; the stocks fold and deploy in place; the bolt moves on each shot; the muzzle
      flash and the tracers at the barrel's end; the Mk9 mount and can on the MP5 / MP5A2 the same size as on an Uzi,
      against the front sight housing on the bore axis; GoM's optics, foregrips, lights and lasers still on their rails
      (GoM's size). Reloads: after the family rework.
- [ ] MP5A3 / MP5A2 / MP5SD on the UMP rifle-hand set (2026-10-27, the set moved from Post-93 into the main mod):
      with Post-93 off, no "animation not found" in the log and the left hand on the handguard (not at the muzzle)
      idle, aimed, walking, running, sneaking, shooting; with Post-93 on, the UMPs keep their hold.
