# SV-98, SV-99 and SVU: research (2026-11-20; all three built the same day)

The user asked (2026-11-20) for the Izhmash SV-98 with partners, picked the SV-99 and the SVU, and asked for research
only. Photos and per-file sources: `references/sv98/`, `references/sv99/`, `references/svu/` (each `SOURCES.txt`
opens with a facts summary per variant, the best measuring / 3/4 / close-up files and the missing angles; a contact
sheet per folder), kept in git. Figures below are from those headers; where sources disagree both are given.

## Where each goes

| Gun | Dates | Mod |
|---|---|---|
| SVU (OTs-03), semi-auto | series production 1991 (Vympel request; troop trials 106th Guards Airborne) | main mod (user: "use the pre-1993 model") |
| SVU-A (OTs-03A), select fire | 1993-1995 (rifles seen stamped 1994) | not now (Post-93 if ever) |
| SVU-AS (OTs-03AS), bipod | 1995 | not now (Post-93 if ever) |
| SV-98 (6V10) | designed 1998-2000, shown 2000, adopted 2003 | Post-93 |
| SV-99 | shown 1999-2000, FSB 2004, MVD 2005 | Post-93 |

## SV-98 (Izhmash, 7.62x54R)

- From the Record-CISM target rifle; bolt action, three front lugs, handle on the right with a ball knob, safety lever
  at the right rear of the receiver, large magazine button. Own 10-round double-stack polymer magazine (not SVD's),
  slid straight up into the well.
- 1200 mm (1375 with the suppressor), barrel 650 mm, 5.8 kg bare / 7.8 kg with optic and suppressor (6.2 elsewhere).
- Hooded front post near the muzzle, drum rear sight to 600 m, rail on the receiver; PKS-07 7x scope early, 1P69 later.
- Green laminated plywood thumbhole stock (bottle green early, teal later), adjustable cheek and butt plate, bipod
  folding into the forend, monopod in the butt, detachable carry handle, mirage strap; muzzle sleeve, flash hider or
  the factory suppressor.
- Real variants: **plywood SV-98** (the one that existed by 2000; 306 photos incl. a 101-photo walkaround), **aluminium
  chassis SV-98** (2016 army rifles, black side-folding skeleton stock, pistol grip, Picatinny; English sources wrongly
  call it SV-98M; 41 photos), **SV-98M** (2023-24 prototype, SVD magazines, M-LOK tube; 17 photos, no clean side view),
  7.62x51 export (no visible difference), SV-338 family (.338 Lapua, unusable photos), Record target rifles (civilian
  KO-13 Record looks exactly like an SV-98, so its photos double as references).
- Ammo: GoM's 7.62x54R boxes / cartons / crates (its Mosin and SVD round); a new 10-round magazine item.

## SV-99 (Izhmash, .22 LR)

- Straight-pull toggle action from the BI-7-2 biathlon rifle, lever on the right (left-hand to order), two-stage
  trigger, push-button safety at the front of the guard, no iron sights (dovetail early, rail on the receiver from
  2007), factory baffle suppressor (~150 mm, 25.5x1.5 thread), plastic 5-round magazines (10 optional), two spares
  in the butt.
- 1030 mm with butt and suppressor, barrel 350 mm, 3.4 kg (4.5 with suppressor; sources vary 3.35-4.5).
- Real variants, each its own stock: **early lacquered wood** (~1999-2006, thumbhole; photos all small), **green
  plywood** (2007-2009, the SV-98's stock copied; best coverage, 53 photos), **black polymer** (2009 on, open butt,
  box cheek riser; best measuring photo, an official 2120 px left side). Civilian BI-7-2KO carbines are relatives,
  not SV-99s.
- Ammo: this mod's .22 LR (the third .22 gun after the PPK and the HK416 .22). A manual action, so the subsonic
  rack rule for self-loaders does not apply.

## SVU (TsKIB SOO, 7.62x54R), the 1991 model

- The SVD rebuilt as a bullpup by L. V. Bondarev: barrel cut to 520 mm, three-chamber muzzle brake / flash hider
  (~145-150 mm long, ~40-45 mm across, estimated from a photo), folding aperture rear sight and hooded front post,
  SVD side rail moved forward for the PSO-1, SVD handguards, fixed cheek rest on the receiver cover, butt plate on a
  leaf spring, usually camouflage painted (red-brown / black). Bayonet in the delivery kit (one source says none).
- 900 mm (MVD poster; 870 in other sources), 4.4 kg with empty magazine and PSO-1, SVD 10-round magazine.
- Telling the 1991 SVU from the SVU-A in photos: the SVU-A's right-side lever is stamped ПР / АВ / ОД; the base
  SVU has a two-position safety. The two detailed walkaround sets (Kuzmin 2014, 2015) are SVU-As, outwardly the same
  gun, so they serve as its references; only the MVD poster and one small photo are confirmed base SVUs.
- Ammo: GoM's 7.62x54R and GoM's SVD 10-round magazine.

## Animations: GoM's only (user, 2026-11-20)

- GoM ships an unused node set for a **magazine-fed bolt action** (`AnimSets/player/actions/Rifle/`: Load / Unload
  `Bob_Reload_Rifle_Load` on `WeaponReloadType = boltaction`, rack `Bob_Reload_Bolt_Rack`, aimed rack
  `Bob_AttackRifle_AimBoltRack`), the base game's hunting rifle reload. Every GoM magazine rifle's script says
  `boltaction` but is re-pointed by its Gunworks profile; GoM's bolt rifles (Mosin, M24, M1903, Remington 700,
  Model 70) are all `boltactionnomag` (BOLT_ACTION profile, stripper clips). So the SV-98 and SV-99 would use the
  `boltaction` nodes with `RackAfterShoot = true`. Not tried in game: check whether they need a Gunworks profile
  (animId "boltaction", durations from the clips) or play on the script's reload type alone.
- The SVU: a bullpup, magazine behind the grip, so "famas_rifle" as the AUGs, PS90, MDRx and Groza; the handle is
  the SVD's on the right (GoM's SVD is on "svd_marz", its AKs on "ak_rifle"), to be weighed against the FAMAS rack
  when it is built.

## Built (2026-11-20)

The SVU (main mod, CLAUDE.md "SVU"), the plywood SV-98 and one SV-99, the polymer stock's shape in green plywood
(Post-93, CLAUDE.md "SV-98 and SV-99"). Not built: the aluminium-chassis SV-98, the SV-98M, the SV-99's early wooden
stock, the SVU-A and SVU-AS.

## Open questions for the build (as they stood before it)

- Which SV-98s: plywood (and aluminium as a later pair?), and which SV-99 stocks (green plywood, black polymer,
  wood) ("build every real variant").
- Missing angles everywhere: no straight top or bottom view of any of the three; SV-99 front / rear and magazine
  photos; a sharp set of a confirmed 1991 SVU; the SV-98 suppressor and muzzle sleeve are unmeasured.
