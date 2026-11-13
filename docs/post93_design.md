# GoM Extension: Guns of Tien - Post-93 — design (approved 2026-10-14, building)

Sub-mod `GoMExtensionGunsOfTienPost93` in the same Workshop item; requires the main mod, GoM and Gunworks (Ammo Maker optional, as in the main mod).
Module `GunsOfTienPost93`, ammo type namespace `gunsoftienpost93:`. Everything is built here: models (Blender,
headless Python), textures, icons, scripts, registries. How GoM builds a gun: CLAUDE.md, "Gun assets in GoM" and
"Gun data and registries in GoM".

## Guns

| | H&K MP7A1 | FN P90 |
|---|---|---|
| Real | 2001 (A1 2005), 4.6x30, 180 mm barrel, 415 / 638 mm, 1.9 kg, 950 rpm | 1990, 5.7x28, 263 mm barrel, 500 mm, 2.6 kg, 900 rpm |
| Model length (×0.72, GoM's MP5 ratio) | 0.30 stock in / 0.46 stock out | 0.36 |
| Hold | two-handed (Rifle anims), like the MP5 | two-handed bullpup, like the FAMAS (grip at the origin, body behind) |
| Carried | back (Rifle slot), as GoM's SMGs | back |
| Fire modes | Auto / Single | Auto / Single |
| Magazines | 20, 30, 40 (in the pistol grip) | 50 (on top, along the receiver) |
| Stock | collapsible (folded / deployed parts, as the MP5) | fixed |
| Front grip | integral, folds under the receiver (folded / deployed parts, own toggle); the MP7A2 has a rail handguard instead (3 / 6 / 9 o'clock) that takes GoM's foregrips | none |
| Rails | top (integral on the real gun), left, right: GoM optics, lights, lasers | see question 1 |
| Damage (GoM MP5 1.0-1.6) | 0.9-1.4, pierces 2 | 1.0-1.5, pierces 2 |
| Sound (realistic model) | about 114 / 33 | about 118 / 34 |
| Reload animation | GoM's MP5 clips | its own top-loading clips (question 3) |
| Spawns | GoM's post-1993 spawner (with G36, AA-12...), SWAT zombies; rare | same |

The armour-piercing small-calibre rounds are the point of both guns: low recoil, high capacity, they pierce.

## Ammo (own module, Ammo Maker types `46x30` / `57x28` already exist)

| Round | Profile |
|---|---|
| 4.6x30mm DM11 (standard; solid copper-plated steel bullet) | base stats, pierces 2 |
| 4.6x30mm Subsonic | ×0.6 damage, sound ×0.7, no pierce |
| 5.7x28mm SS190 (standard, steel / aluminium penetrator) | base stats, pierces 2 |
| 5.7x28mm SB193 Subsonic (made for the suppressed P90) | ×0.7 damage, sound ×0.7, no pierce |
| 5.7x28mm SS197SR (polymer tip, expands) | ×1.15 damage, no pierce |

Boxes / cartons / crates, recipes, loot, Hot Brass casings (`HBVCEF.46x30_Casing`, `57x28_Casing`), Ammo Maker
mapping, tooltips, icons — as in the main mod.

## Decisions (2026-10-14)

1. P90: the **P90 TR** only (1999; top and two side rails, integral to the receiver). No integrated ring sight.
2. **One suppressor each** (new models), each needing its own muzzle mount device, like GoM's; GoM's suppressor stats.
3. P90 gets **its own top-loading reload clips** (load / unload / rack), made with TienInspectWeapon's Blender
   animation pipeline. The MP7 uses GoM's MP5 clips.

Integrated rails (MP7A1 top / left / right, P90 TR top / left / right) are hidden required parts
(`<GUN>_Integrated_Rail_Up/Left/Right`, CannotBeRemoved), added as parents in `RequiredAttachment.RegisterRequired`
for GoM's optics / lights / lasers (as GoM does for the G36C), so no separate rail meshes.

## Names (module GunsOfTienPost93)

Guns `MP7A1`, `MP7A2` (user, 2026-10-18: its own body `MP7A2_BODY` and texture, the A1's bolt, stock, magazines and parts, bottom-rail part `MP7A2_Integrated_Rail_Down`), `P90TR`; models `MP7A1` (+ `MP7A1_BOLT`, `MP7A1_STOCK`, `MP7A1_FOREGRIP`), `P90TR` (+ `P90TR_BOLT`); stock parts
`MP7A1_Integrated_Stock_Folded / _Deployed`, front grip parts `MP7A1_Integrated_Foregrip_Folded / _Deployed`; magazines `46x30Magazine20_MP7`, `46x30Magazine30_MP7`,
`46x30Magazine40_MP7`, `57x28Magazine50_P90`; suppressors `MP7_Suppressor`, `P90_Suppressor`; mounts
`MP7_Muzzle_Mount_Device`, `P90_Muzzle_Mount_Device`; rounds `46x30_Bullet` (DM11), `46x30_Bullet_Subsonic`,
`57x28_Bullet` (SS190), `57x28_Bullet_SB193`, `57x28_Bullet_SS197SR`. Files (one set per gun): models_X/weapons/firearms/
GunsOfTienPost93_MP7A1.fbx and _P90TR.fbx, models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx and
_P90_magazines.fbx, models_X/weapons/parts/GunsOfTienPost93_MP7_parts.fbx and _P90_parts.fbx; textures under
textures/weapons/GunsOfTienPost93/. The charging handles do not reciprocate on either gun: they move only with the rack, while the bolt in the
ejection port takes GoM's Bolt_Lock / Bolt_Fired swap (built 2026-10-30, CLAUDE.md "The charging handle and the bolt
are not always the same part").

## FN Five-seveN (user, 2026-10-16)

Reuses Guns of Marz's own name: GoM's ItemName.json has `"MarzGuns.FIVESEVEN": "5.7x28mm Five-SeveN"` and nothing
else (no item, model, magazine, icon), so the gun is the item `MarzGuns.FIVESEVEN` (block in GoM's module, our
`items_fiveseven.txt`), named by GoM's translation; everything it uses is ours (module GunsOfTienPost93).

| | FN Five-seveN |
|---|---|
| Real | 1998 (FNH USA models 2000s), 5.7x28, 122 mm barrel, 208 mm long, 0.61 kg, semi-automatic |
| Model | built from a side photo of an FNH USA Five-seveN (docs/fiveseven_atf.jpg, U.S. ATF, public domain), 0.72 scale, GoM's pistol conventions (upside down, body + slide, magazines in gun space); silhouette overlap 96.0% |
| Features | "match what GoM has" (user): GoM's Glock 17 / M92FS set: animated slide, Beretta mount + pistol sights (PL4, PM2, PS1), GoM's two pistol lights on the underbarrel rail (LP; TL, a flashlight in a clamp as pistols carried them before rails) and its three pistol lasers (none from 2026-10-16 until 2026-11-13, user: all our pistols take a laser), muzzle mount device + suppressor |
| Magazines | 20 (standard) and 30 (extended, sticks out of the grip) |
| Suppressor | its own "SFN-57 Suppressor" (Gemtech's can for the Five-seveN; about 33 x 170 mm, approximate; weight 0.8 like GoM's P45, the pistol can of the same size: GoM's pistol cans weigh 0.8-1.2), on the 5.7x28mm mount device it shares with the P90 (drawn on the pistol as a threaded-barrel adapter of its own, not the P90's flash hider clamp) (user, 2026-10-16: one suppressor per gun, the mount can be shared; the P90's is now just "SP90 Suppressor", no calibre in either name; the MP7's name unchanged) |
| Damage | 0.6-1.0 (GoM: Glock 0.4-0.9, M92FS 0.5-1.0), pierces 2 with SS190, light recoil (HitChance 57, RecoilDelay 9) |
| Sound (realistic model) | 148 / 42 |
| Reload | Gunworks' default handgun reload, as GoM's pistols |
| Carried | holster |
| Spawns | GoM's police and SWAT handgun spawners; in survivor and bandit zombies' late bags (with a magazine and a box); never in civilian homes (user, 2026-10-17: GoM's Anachronistic spawner goes into vanilla's late survivor safehouses in homes, so it is not used); the 30-round magazine 5% on found guns |

Names: gun `MarzGuns.FIVESEVEN`; models `FIVESEVEN`, `FIVESEVEN_SLIDE`; magazines `57x28Magazine20_FIVESEVEN`,
`57x28Magazine30_FIVESEVEN` ("Five-SeveN 20Rds 5.7x28mm Magazine", "Five-SeveN 30Rds 5.7x28mm Extended Magazine");
files models_X/weapons/firearms/GunsOfTienPost93_FIVESEVEN.fbx, models_X/weapons/magazines/
GunsOfTienPost93_FIVESEVEN_magazines.fbx, suppressor `FIVESEVEN_Suppressor` and the mount device's
pistol look `FIVESEVEN_Muzzle_Mount_Device` (a model only) in models_X/weapons/parts/GunsOfTienPost93_FIVESEVEN_parts.fbx; textures FIVESEVEN.png (256) and one per magazine and the
suppressor (128).

## H&K UCP Prototype (user, 2026-10-17)

H&K's 4.6x30mm companion pistol to the MP7 (also called P46; "Universal" or "Ultimate Combat Pistol"): prototypes from
about 2004, cancelled July 2009, never sold. The only other real 4.6x30mm design besides the MP7 (a 4.6 B&T MP9 was
only mentioned as planned). Item `GunsOfTienPost93.UCP`, shown as **"UCP Prototype"** (user).

| | H&K UCP |
|---|---|
| Real (published, prototype) | 200 mm, 130 mm barrel, 850 g, 20 rounds, 695 m/s |
| Model | traced from a side photo of the about-2004 prototype (guns.fandom.com, 550 px, rights unclear: a reference only, not in the repo), 0.72 scale, GoM's pistol conventions like the Five-seveN; silhouette overlap 97.3%; the right side (not in the photo) gets the ejection port and mirrored ambidextrous controls |
| Optics | none built in: GoM's Beretta Mounting Rail first, then its pistol sights (PL-4, PM-2, PS1), as on the Five-seveN (user: "it needs mounting for optics") |
| Lights | GoM's two pistol lights (LP, TL) and three pistol lasers, as the Five-seveN |
| Suppressor | the MP7's Rotex-II on the MP7's mount device (user: "use the MP7 suppressor"); the mount is drawn on the UCP as a threaded-barrel adapter (`UCP_Muzzle_Mount_Device`) |
| Magazines | `46x30Magazine20_UCP`, "UCP 20Rds 4.6x30mm Magazine", and a small drum `46x30Magazine40_UCP`, "UCP 40Rds Drum 4.6x30mm Magazine" (user, 2026-10-17: the UCP keeps its own magazines, since nothing shows it took the MP7's; a straight and then a curved long 40 were tried first): built like the MP7's 60 drum, facing front and back under the grip, 68 mm across and 50 mm deep, weight 0.2 (GoM's pistol drums: M92FS 50 0.25, M93R 60 0.2), 5% on found UCPs and not in the spawner's magazines (as the Five-seveN's 30); both in the 4.6x30mm family (DM11, Subsonic) |
| Damage | 0.55-0.95 (a little below the Five-seveN: DM11 1.6 g at 695 m/s against SS190 2.0 g at about 650), pierces 2 with DM11 like the MP7 |
| Sound (realistic model) | 125 / 36 |
| Weight | 0.85 (GoM's USP and M92FS weigh about their real kilograms; the Five-seveN 0.6) |
| Spawns | as the Five-seveN (user, 2026-10-17: "treat it like any other gun", not rare): GoM's police and SWAT handgun spawners (4 magazines, 4 boxes; the 20-round on 50% of found guns, the drum on 5%), the drum in GoM's high-capacity magazine spawner, and survivor and bandit zombies' late bags (with a magazine and a box); never in civilian homes |

Files: models_X/weapons/firearms/GunsOfTienPost93_UCP.fbx (`UCP_BODY`, `UCP_SLIDE`), magazines/GunsOfTienPost93_UCP_magazines.fbx,
parts/GunsOfTienPost93_UCP_parts.fbx (`UCP_Muzzle_Mount_Device`); textures UCP.png (256), 46x30Magazine20/40_UCP.png
and UCP_Muzzle_Mount_Device.png (128). Rebuild: `build_ucp.py` → `render_ucp.py` → `make_ucp_art.py --renders DIR [--photo
REFERENCE]` → `gen_post93_guns.py`; outline: `trace_outline.py` into ucp_reference_outline.json.

## Weights (user, 2026-10-17: GoM's standard for our items too)

Suppressors 0.8-1.2 whatever their size (GoM), matched by size: Rotex-II 0.8, SFN-57 0.8 (GoM's P45), SP90 0.9 (GoM's
NDR); every mount device 0.5. Magazines: MP7 20 / 30 / 40 / 60 drum 0.08 / 0.18 / 0.2 / 0.22 (GoM's MP5 20 / 30 / 60),
P90 50 0.25, pistol standard 0.05, the Five-seveN's 30 and the UCP's drum 0.2. Guns by GoM's weight-to-real ratios:
MP7 1.5, P90 2.0 (its SMGs ~0.78 of their kilograms), Five-seveN 0.6, UCP 0.85 (its USP / M92FS ~1.0).

## Loot, matched to GoM (user, 2026-10-17)

Every item spawns the way GoM's own item of the same kind does: guns through GoM's spawners (with magazines and boxes),
high-capacity magazines also loose in GoM's tactical high-cap spawner, suppressors and mount devices in its suppressor
and muzzle device spawners (mount devices also among GoM's replacements for vanilla's Improved Choke Tube), boxes and
cartons beside vanilla's boxes and cartons, Ammo Maker parts and their boxes
through Ammo Maker's own loot (every active part). Not spawning, as GoM's own: crates (packed from 4 cartons), and the
cartons of calibres vanilla lacks (GoM's 7.62x39 / 9x39 cartons never spawn, so ours of those don't either); loose
rounds come from boxes; and every special load (4.6x30mm Subsonic, 5.7x28mm SB193 and SS197SR, and all of the main
mod's rounds), since GoM never spawns its own special loads: only the standard 4.6x30mm DM11 and 5.7x28mm SS190 boxes
and cartons are loot. The Five-seveN, the UCP and their ammunition never spawn in civilian homes.

## FN SCAR-L and SCAR-H (user, 2026-10-20; built)

FN's SOCOM rifles (SCAR program 2004, Mk 16 / Mk 17 fielded about 2009), both in **FDE** (tan): the SCAR-L in its
standard version (Mk 16 STD, 13.8"), the SCAR-H with the **long barrel** (Mk 17 LB, 20"; user, 2026-10-20), select fire
with the standard side-folding stock (the user chose the LB over the TPRS of their photo). No new rounds: both use GoM's
existing families. Modelled from the user's two left-side photos (a SCAR-H TPRS, a licensed SCAR-L CQC replica; neither
kept in the repo), see CLAUDE.md "FN SCAR-L and SCAR-H".

| | `GunsOfTienPost93.SCARL` "FN SCAR-L Assault Rifle" | `GunsOfTienPost93.SCARH` "FN SCAR-H Battle Rifle" |
|---|---|---|
| Real | 5.56x45, 351 mm (13.8") barrel, 3.3 kg | 7.62x51, 508 mm (20") barrel, about 3.9 kg |
| Family | `5.56x45mm`: GoM's 5.56 (and its AP / HP / [+P] / Subsonic), .223, `Base.556Bullets` | `7.62x51mm`: GoM's 7.62x51, .308, our .308 Soft Point, `Base.308Bullets` |
| Magazines | GoM's STANAG magazines (20 to 150), its "STANAG" profile | FN's `762x51Magazine20_SCARH` / `10_SCARH` (0.2 / 0.12) and ProMag's 50-round drum `762x51Magazine50_SCARH` (0.5; user, 2026-10-20) |
| Muzzle | GoM's AR mount device, MKI / NDR suppressors, LR2 compensator, LX flash hider, Trix42 muzzle brake | `SCARH_Muzzle_Mount_Device` + `SCARH_Suppressor` "SOCOM762-RC Suppressor (7.62x51mm Weapons)" (SureFire's 1.5" can USSOCOM adopted in 2017; FN made none for the SCAR-H and none is documented on the Mk 17; user, 2026-10-20; GoM's rifle suppressor stats, weight 1.2) |
| Stats | GoM's M4A1 (1.0-1.4), HitChance 52, RecoilDelay 12, condition 1 in 250, 625 rpm | GoM's FAL (1.3-1.8, range 60), Aimingtime 50 (FAL 65), condition 1 in 240, 600 rpm, default Single |
| Sound (realistic model) | 196 / 56 (M16 events) | 216 / 62 (FAL's M14 events) |
| Reload | Gunworks' default, as GoM's M4A1 | GoM's FAL clips (animId "fal_rifle", "FAL" before GoM's 2026-10-23 update) |
| Weight | 3.3 | 3.9 |

Both: held as rifles (two hands, back slot), Auto / Single, the charging handle on the left reciprocates (GoM's
Bolt_Fired swap), one shared side-folding stock (`SCAR_Integrated_Stock_Folded / _Deployed`, GoM's G36 stock stats:
HitChance x1.15, AimingTime x0.85), folding to the right; four integral rails (`SCAR_Integrated_Rail_Up / Down / Left /
Right`) for GoM's optics, foregrips, bipods, lights and lasers; no bayonet (no lug); ejection to the right (Hot Brass:
GoM's M4A1 / FAL values). Loot (user, 2026-10-20: military, the MP7's way): an alternative each in GoM's army rifle
spawners, packed as GoM's own there: `World_Army_Rifle_Spawner` (M16 family, M14, M24 + the two SCARs, so a SCAR is 2
in 5 of its kits; army storage, army truck beds, army ALICE packs, the old bunker's storage, `RifleCase3`, late civilian
gun finds; up to 6 magazines and 6 boxes) and `Zombie_Army_Rifle_Spawner` (M16 family, M14, M60 + the SCARs: the rifle
on army zombies' backs; up to 4 and 4). Not in GoM's Anachronistic spawner (civilian late safehouses and bags). A
spawner of our own (`World_SCAR_Spawner`, inserted GoM's way in army storage, truck beds and ALICE packs at a quarter
of the army rifle's weight) was built and dropped the same day for this. The suppressor and mount device in GoM's
suppressor and muzzle device spawners.

**SCAR-H 50-round drum** (user, 2026-10-20): FN never made more than 20 (10 and 20, steel then polymer); the only real
larger one found is ProMag's DRM-A41, a 50-round polymer drum for the civilian SCAR 17S (black or FDE; retailer
listings, not ProMag's own page; no 30 or 40 exists outside airsoft). Built in FDE like the gun: a feed tower like
the 20-round body into one round drum facing front and back (its axis along the barrel, as the MP7's drum; the
first build faced the sides, corrected by the user), winding knob on the front face, ~144 mm across and 84 mm
thick (approximate: no published drawing), "50" moulded under the hub. Named "SCAR-H 50Rds Drum 7.62x51mm
Magazine" (as the MP7's 60 drum). Spawns on 2 % of found SCAR-Hs (the MP7 drum's chance) and with up to two boxes
in GoM's high-capacity tactical magazine spawner, as our other drums.

## H&K UMP45 and UMP9 (user, 2026-10-22; built)

H&K's polymer SMG (1999), the MP5's cheaper successor. One body for every calibre: changing calibre means a new
barrel, bolt and magazine, and the magazine is the only outside difference (the UMP9's is curved). Two separate guns
on one model, no conversion recipe (user, 2026-10-22: "different guns would suffice"; Gunworks could do it with a
part-registered magazine profile, `Magazine.RegisterWeaponPartWithProfile`, but stats, sound and name would have to
follow the part in our own code). No UMP40: neither GoM nor Gunworks has a .40 S&W round (Ammo Maker's `40SW` type
waits unused), and the user chose not to add one (2026-10-22). No new rounds: GoM's 9mm and .45 families (with the
main mod's 9mm 147gr / Hollow Point / [+P+] and .45 Hollow Point / [+P]).

| | `GunsOfTienPost93.UMP45` "UMP45 Submachine Gun" | `GunsOfTienPost93.UMP9` "UMP9 Submachine Gun" |
|---|---|---|
| Real | .45 ACP, 200 mm barrel, about 2.5 kg empty | 9x19, 200 mm barrel, about 2.3 kg empty |
| Magazines | H&K's 10, 20 and 25-round straight (user, 2026-10-22) | 30-round curved |
| Rate of fire (real 600-700 / 600-750) | 600 rpm, more spread than GoM's MP5 (0.1 / 1.5), e.g. 0.18 / 2.2 | 700 rpm, close to the MP5's, e.g. 0.11 / 1.6 |
| Damage | a step above GoM's MP5, about 1.1-1.8 (user, 2026-10-22: the .45 hits harder, for its slower fire, recoil and smaller magazine) | GoM's MP5, 1.0-1.6 |
| Sound | the realistic model (`sound_model.py`), .45 quieter than 9mm | same |

Both: held as rifles (two hands, back slot), **Auto / 2-round burst / Single** (user, 2026-10-22; Gunworks
`burstCount = 2`, `FireModePossibilities = Auto/Burst/Single` as one GoM gun already has), the **UMP45 takes GoM's .45
Muzzle Mounting Device and P45 Suppressor** as GoM's MAC-10, M1911 and USP do (user, 2026-10-22, replacing a first
"no suppressor, like GoM's MP5"; the real UMP's barrel is threaded for one), the **UMP9 none** (GoM's 9mm suppressors,
M&P and Shh9 on its Pistol mount, fit its pistols only; it takes the main mod's AWC Mk9 on its 9x19mm SMG mount
device instead, added the same day), no other muzzle device, black, one shared stock folding to the right
(`UMP_Integrated_Stock_Folded / _Deployed`, GoM's G36C stock stats and spread modifier), four integral rails
(`UMP_Integrated_Rail_Up / Down / Left / Right`: receiver top, handguard sides and bottom) for GoM's optics,
foregrips, lights and lasers, ejection to the right, Hot Brass as GoM's MP5. Model at GoM's SMG ratio (0.72).

Reload (user, 2026-10-22): GoM's MP5 clips (animId "MP5", its durations). Loot (user, 2026-10-22: the MP7 / P90
route): an alternative each in GoM's `World_Anachronistic_Spawner` and `Zombie_Police_SMG_Spawner`, packed as the MP7's
(gun + the standard magazine + its box: UMP45 25, UMP9 30, GoM's MP5 kit carries its standard 30 likewise).
Magazines on a found gun (user: "base your decisions on how GoM handles it"): GoM's MP5 rolls 20:30, 25:20, 30:5
(shortest likeliest), its single-magazine guns 50 (AS VAL, M14, Glock), so the UMP45 10:30, 20:20, 25:5 and the UMP9
30:50. Reference photos (user, 2026-10-22, kept out of the repo like the SCAR's): H&K's product photo of a UMP9,
left side, stock deployed, 30-round magazine (marked 9x19); a third-party 3D render of a UMP .45, right side
(muzzle right), stock deployed, 25-round magazine (for the right side: stock hinge, ejection port, selector).
Built 2026-10-22: build notes in CLAUDE.md "H&K UMP45 and UMP9". Stats as GoM's MP5 for the UMP9 (1.0-1.6, HitChance 50,
RecoilDelay 15, range 30), the UMP45 1.1-1.8, HitChance 48, RecoilDelay 17, range 28, crit 25; weights 1.8 / 1.9 (GoM's
SMG ratio ~0.78 of 2.3 / 2.5 kg); magazines 0.18 (UMP9 30), 0.15 / 0.1 / 0.05 (UMP45 25 / 20 / 10); sound 96 / 28 and
70 / 20 (the realistic model, 200 mm barrel). The .45 magazines are named in GoM's style for its G36's: "UMP45 25Rds .45
ACP Translucent Magazine".

## Steyr AUG A3, AUG Para and AUG HBAR (user, 2026-10-28; built, not played in game yet)

Three more AUGs beside the main mod's A1 (docs/design.md 4g), all on the **A3 receiver** (2005: the A1's cast scope
and carry handle replaced by a Picatinny rail), so all in Post-93. The user's reasons: the A3 is post-1993 by itself;
the Para "should be the same as the A3 era" (the 1988 Para on the A1 receiver would belong in the main mod); the HBAR
is "the AK-AUG" (spartanat's name for Steyr's 7.62x39 AUG, shown at Enforce Tac 2025 as a rifle and a stock + barrel
conversion) with the heavy barrel and its integrated bipod. No 7.62x39 HBAR was found in any source (the 621 mm HBAR
barrel is sold in 5.56 only); the user: "it's not a prototype but a possible setup" (the AUG changes calibre by its
barrel and stock), so no "Prototype" in the name.

| | `GunsOfTienPost93.AUGA3` "Steyr AUG A3 Assault Rifle" | `GunsOfTienPost93.AUGPARA` "Steyr AUG Para Submachine Gun" | `GunsOfTienPost93.AUGHBAR` "Steyr AUG HBAR Light Machine Gun" |
|---|---|---|---|
| Real | 5.56x45, 508 mm barrel, 790 mm, 3.6 kg, 680-750 rpm | 9x19, 420 mm barrel, about 665 mm, 3.3 kg, 650-720 rpm, fires from a closed bolt | 7.62x39 on the 621 mm heavy barrel (a possible setup), about 900 mm, about 4.9 kg (the 5.56 HBAR's), 680 rpm (the HBAR's; no figure is published for the 7.62x39 AUG) |
| Family | GoM's 5.56x45mm (its loads, .223), as the A1 | GoM's 9x19mm (its loads, the main mod's 147gr / Hollow Point / [+P+]) | GoM's 7.62x39mm |
| Magazines | the A1's `GunsOfTien.556x45Magazine30_AUG` / `42_AUG` (main mod), profile "5.56x45mm AUG": the standard stock (user, 2026-10-28; the A3 NATO stock's STANAG well was the other choice) | Steyr's 25 and 32-round 9mm (MPi 69 pattern, straight) in the AUG well through an adapter drawn as part of the body: `9x19Magazine25_AUG` / `9x19Magazine32_AUG` (user, 2026-10-28) | Steyr's own: `762x39Magazine30_AUG`, translucent smoke polymer with the AUG's waffle, curved like an AK magazine (TFB's Enforce Tac 2025 video; a retailer lists "Steyr Arms AUG 7.62x39mm 30 Round Magazine"; no longer 7.62x39mm AUG magazine exists). GoM's AK magazines do not fit (user, 2026-10-28). And `762x39Magazine50_AUG` (user, 2026-10-28), the LMG's long box: the 30's curve carried on to 251 mm, wide as a coffin (50 mm across against the 30's 34, the rounds four abreast as in SureFire's high-capacity magazines) from the well to the base plate ("thick all the way"); its base hangs about 5 cm under the deployed bipod's feet, as an RPK's long magazines do. C-Mag style drums (a 150 twin and a one-sided 75; Beta sold a 100-round C-Mag for the AUG / A3 in 5.56) were built and dropped for it |
| Muzzle | GoM's AR muzzle family as the SCAR-L and M16s (user, 2026-10-28): AR Muzzle Mount Device, MKI / NDR suppressors, LR2 compensator, LX flash hider, Trix42 muzzle brake; a `canon` point at the muzzle | the main mod's 9x19mm SMG mount device + AWC Mk9, as the UMP9 (user, 2026-10-28) | none (no 7.62x39 can or device in GoM; user, 2026-10-28); its muzzle brake is part of the barrel mesh |
| Under the barrel | the folding grip (on every AUG the grip belongs to the barrel) | the folding grip (seen in the Para photo) | the folding grip **and** a folding bipod (sold as "AUG barrel, green grip, with bipod") |

All three:
- **Rails** (user, 2026-10-28): the A3's short top rail on the receiver (user: "standard short one", not the A3 M1
  Long Rail) and the A3 SF's right-side rail, both integral: hidden required parts `AUG_Integrated_Rail_Up` (GoM's
  optics) and `AUG_Integrated_Rail_Right` (GoM's lasers), one pair shared by the three guns. **No left rail from the
  factory** (the charging handle runs in a slot along the receiver's left), so the left side takes **GoM's own
  `MarzGuns.Picatinny_Rail_Left` as a removable upgrade** (GoM's lights; Corvus Defensio sells such a rail for either
  side), the guns appended to its MountOn and drawn with **our own short model** `GunsOfTien.AUG_RAIL_LEFT` (in the main
  mod since 2026-10-30, scripts/build_rails.py, when the A1 took it with a right one; the item's
  `ModelWeaponPart` names the model, as the UCP draws the MP7's mount device): 4 crossbars, 41 mm, on the receiver's
  front-left at L 256-297, centred H 129.5, under the charging handle's path (H 140 up, L 255-382) and ahead of the
  stock's shell and the trigger frame (L 298). GoM's own model (125 mm long, 25 mm across) ran into the handle there
  (A3 review renders, 2026-10-28; user: "can't we shorten the rail?"); a barrel clamp was tried in between.
  **No bottom rail** (user,
  2026-10-28: the folding grip is underneath, and an optional `Picatinny_Rail_Down` was dropped). GoM ties each rail
  side to a kind of part: Up optics, Down foregrips and bipods, Left lights, Right lasers.
- **Folding grip**: the A1's (`GunsOfTien.AUG_Integrated_Foregrip_Folded / _Deployed`, its fold code in the main mod's
  Foregrip.lua), drawn at each gun's own `foregrip_*` points. Its display name says "AUG A1"; drop the A1 for all four.
- **Held and reloaded** as the A1: the bullpup stance (grip animId `GunsOfTien_CompactBullpup`) and the AUG's bullpup
  reload (`GunsOfTienCompactBullpupAUG`), no new animation (CLAUDE.md "Animations are generic"); each gun's magazine
  point at the A1's lips, so the Para's straight 9mm and the HBAR's curved 7.62 sit in the same place. Charging handle
  on the left, non-reciprocating as the A1's: forward when firing, back only with the rack; the bolt carrier in the
  ejection port takes GoM's Bolt_Lock / Bolt_Fired swap (every AUG draws the A1's `AUG_BOLT`). Back slot, Auto / Single.
- **HBAR bipod**: integrated, folded on a found gun, through Gunworks' `FoldingBipod` registry as GoM's M60 / BAR / M24
  and the main mod's M249 (`AUGHBAR_Integrated_Bipod_Folded / _Deployed`), beside the grip's own fold.
- **Finish**: the A3 Steyr green with the black receiver and rail (the Interpolitex photo's green gun, the A3 SF), the
  HBAR the same (the green 7.62x39 gun of TFB's video), the **Para sand** (user, 2026-10-28), receiver black.
- **Stats** (user, 2026-10-28: "check reviews if they are better or not, and balance it around the real rate of
  fire"). The rate sets the Gunworks `RateOfFire` entry and the spread growth (this mod's and GoM's guns: slower guns
  spread less per shot fired), the reviews move accuracy, handling and jams against the gun each is measured from.
  | | AUG A3 | AUG Para | AUG HBAR |
  |---|---|---|---|
  | Measured from | the A1 (same barrel, round and rate) | GoM's MP5 (800 rpm, 0.1 / 1.5, 1.0-1.6, HitChance 50, Aimingtime 40, RecoilDelay 15, range 30) and Post-93's UMP9 (700, 0.11 / 1.6) | GoM's AK-47 (650 rpm, 0.3 / 3.5, 1.5-1.8, HitChance 50, Aimingtime 60, RecoilDelay 15, range 50, jam 0.5) |
  | Reviews | A3 M1 reviews: reliable (2 stoppages in 600 rounds, none in 500 over five loads), 2-3 MOA held back by a heavy factory trigger (~9.5 lb); nothing better or worse than the A1 | no independent range test found; Steyr's and reference sheets credit the long barrel (higher velocity than usual for 9mm) and the closed bolt (nothing moves before the shot) with accuracy above other 9mm SMGs; heavy for a 9mm | no review of the 7.62x39 AUG exists yet; the HBAR was made for sustained automatic fire "without loss of accuracy" (its heavy barrel); the conversion's gas system is new |
  | Rate, spread | 700, 0.12 / 2.5 (the A1's) | 685 (650-720), 0.09 / 1.4: slower than the MP5 and steadier (3.3 kg, closed bolt) | 680, 0.2 / 2.8: a little faster than the AK-47 but the heavy barrel and 1.4 kg more hold it far tighter; looser than the 5.56 A1 for the bigger round |
  | Damage | 1.0-1.8 (the A1's) | 1.0-1.7 (the MP5's, + 0.1 for the 420 mm barrel's velocity) | 1.6-1.9 (the AK-47's + 0.1 for 621 mm against its 415) |
  | HitChance, aim, recoil | 45, 45, 15 (the A1's; no gain: same trigger) | 52, 40, 13 (closed bolt, heavy gun, mild 9mm) | 55, 65, 13 (heavier and longer: more accurate, slower to raise; recoil soaked by the weight) |
  | Range, crit | 50, 25 | 35, 20 | 60 (GoM's M60), 25 |
  | Jam, wear | 0.8, 1 in 200 (the A1's; the reviews agree) | 0.8, 1 in 200 | 0.8 (the AUG's, not the AK's 0.5: a new gas system), 1 in 220 (heavy barrel) |
  | Weight | 3.6 | 3.3 (the AUG family keeps real weights, as GoM's FAMAS) | 4.9 |
  Sounds from `sound_model.py`: the A3 175 / 50 (the A1's), the Para 77 / 22 (9mm from 16.5"), the HBAR 155 / 44
  (7.62x39 from 24.4"); the A1's M16 handling sounds, the shot of the round (GoM's MP5 `M9Shoot`, its AK-47's
  `JS14Shoot`). The HBAR's bipod: GoM's rail bipod (deployed Aiming Time x1.1, Hit and Crit x1.15, auto spread
  x0.65), not the M249's M60 numbers (a 7.5 kg belt-fed gun).
- **Loot** (user's "go", 2026-10-28): GoM's routes as the other Post-93 guns: the A3 in GoM's Anachronistic
  spawner (the US A3 M1 is a civilian rifle; the A1's 30s and .223 boxes), the Para there and in its police SMG
  spawner (the UMPs' route), the HBAR in its two army rifle spawners (the SCARs' route); the HBAR's 50 also loose
  in GoM's World_HighCap_Russian_Magazine_Spawner beside its 7.62x39 75. On a found gun: the A3 the A1's 30 at 30%
  and 42 at 5%, the Para 25 / 32 at 30 / 20%, the HBAR 30 / 50 at 50 / 5%, GoM's optics and lasers at its rifles'
  chances, lights with GoM's left rail.
- Built: models scripts/post93/build_aug3.py, review renders render_aug3.py, icons and the preview
  (docs/aug3_preview.png) make_aug3_art.py, scripts gen_post93_guns.py `augs()`, registries
  shared/GunsOfTienPost93/AUG.lua (CLAUDE.md "Steyr AUG A3, Para and HBAR").

References (kept out of the repo in `references/aug_variants`): Commons "Interpolitex 2011 (405-9)" (Vitaly V. Kuzmin,
CC BY-SA 4.0, 2250 px: two A3s, right side, one green with the short top rail, one black with the right-side rail);
Commons "Steyr-AUG-A3-SF" (CC BY-SA 4.0, 650 px, left side, muzzle left); Commons "AUG 9mm 03" (Steyr Mannlicher,
CC BY 2.0, 550 px: the 1988 Para, left side: barrel, straight magazine, magazine-well adapter, grip); TFB's video
thumbnail of the 7.62x39 AUG (1280 px, right side; rights unclear, a reference only, as the UCP's photo). No usable
HBAR photo: its barrel and bipod are built from the published numbers on the A3's receiver.

## KRISS Vector .45 and 9mm (user, 2026-10-30; built, not played in game yet)

KRISS's Super V submachine gun, Gen II SMG with the 5.5" barrel: the .45 ACP gun (2006) and the 9mm (2011), two guns on
one model as the UMPs. Finish (user, 2026-10-30: "Let's not use black ... flat earth and sand. 9mm takes sand"): the
**.45 flat dark earth, the 9mm sand**; rails, handle, magazines and the butt pad black.

| | `GunsOfTienPost93.VECTOR45` "Vector .45 Submachine Gun" | `GunsOfTienPost93.VECTOR9` "Vector 9mm Submachine Gun" |
|---|---|---|
| Magazines | the main mod's Glock 21 13 (standard) and KRISS's MagEx2 30 (`45Magazine30_GLOCK21`, ours, "Glock-21 30Rds .45 ACP Extended Magazine") | GoM's Glock 17 17 (standard), Glock's 33 (`9x19Magazine33_GLOCK`) and KRISS's MagEx2 40 (`9x19Magazine40_GLOCK`), ours, "Glock-17 33Rds / 40Rds 9x19mm Extended Magazine" |
| Rate of fire (real ~1200) | 1200 rpm, two-round burst, spread 0.10 / 1.3 | 1200 rpm, two-round burst, spread 0.08 / 1.1 |
| Damage | 1.0-1.6 (a little under the UMP45's 1.1-1.8: 5.5" against 7.9"), crit 22, stop 2.5 | 0.9-1.4 (under the UMP9's 1.0-1.6), crit 20, stop 2.0 |
| Handling | HitChance 52, Aimingtime 35, RecoilDelay 12 (UMP45 48 / 40 / 17) | 52 / 35 / 11 (UMP9 50 / 40 / 15) |
| Sound (sound_model.py, 5.5") | 78 / 22, GoM's M1911 shot | 107 / 31, GoM's MP5 9mm shot |
| Muzzle | GoM's .45 mount device and P45 (the UMP45's) | the main mod's 9x19mm SMG mount device and Mk9 (the UMP9's) |

Names without the maker (user, 2026-11-01: "drop KRISS in the name"), as GoM's "MP5 Submachine Gun". **The .45 is
held as a rifle** (two hands, GoM's MP5 reload: the well ahead of the trigger and the handle on the front left, as on
the MP5); **the 9mm like a pistol** (user, 2026-11-01), as the MP7s and the P90: one hand when not aiming, Handgun
swing, GoM's MP5K reload ("handgun2"), its model turned upside down, still on the back slot (never a holster).

Both: weight 2.1 / 2.0 (2.7 kg x GoM's SMG ratio), the back slot, **Auto / 2-round burst / Single**, the bolt
in the ejection port (right) through GoM's Bolt_Lock / Bolt_Fired swap and the main mod's non-reciprocating charging
handle (back only while racked); the side-folding stock (`VECTOR_Integrated_Stock_Folded / _Deployed`, GoM's G36C
stats and spread modifier as the UMPs'); the integral top rail (`VECTOR_Integrated_Rail_Up`: every GoM optic) and the
short bottom rail (`_Rail_Down`: GoM's three foregrips); **GoM's optional Picatinny_Rail_Left / _Right** for its lights
and lasers (KRISS's bolt-on side rail kit; the main mod's `Rails.Register`, drawn as our short `VECTOR_RAIL_LEFT /
_RIGHT`; found guns carry them with their accessory, ":PRL" / ":PRR"). Hot Brass: the UMPs' values.

**Magazines shared with the pistols** (user, 2026-10-30: the .45 the Glock 21's 13 plus KRISS's extended one, "fits
the Glock 21 too"; the 9mm "add 33 and 40", fitting GoM's Glock 17 too): the .45 joins the main mod's ".45 ACP Glock
21" profile with the 30; GoM's Glock 17 had no profile (its item MagazineType only), so Vector.lua makes "9x19mm Glock"
(GoM's 17 + our 33 and 40) for the Glock 17 and the Vector 9mm. On a Vector every magazine is drawn by a Vector model
(origin at the feed lips, raked as the well); on the pistols ours are drawn by copies of the pistol's own magazine
mesh stretched below its middle (the 30 the Glock 21's, the 33 / 40 GoM's), added to the pistols' item scripts at run
time (`DoParam("ModelWeaponPart = ...")`, once per script object). Those copies are the items' StaticModel, with the
pistols' textures and a `Bip01_Prop2` point for the reload's off hand.

Loot (the UMPs' route): an alternative each in GoM's `World_Anachronistic_Spawner` (4 boxes) and
`Zombie_Police_SMG_Spawner` (2), the gun with three standard magazines (Glock 21 13 / GoM's Glock 17 17) and GoM's
boxes; the 30, 33 and 40 also on their own in GoM's `World_HighCap_Tactical_Magazine_Spawner`. Found guns: the
standard magazine at 50, the 30 / 33 at 5, the 40 at 2; GoM's MP5 accessories at its chances.

### Vector CRB and Vector SDP (user, 2026-11-03)

KRISS's civilian Vectors: "2 guns. .45 ACP gets the longer barrel. 9x19 gets the shorter one", select fire as the
SMGs (Auto / two-round burst / Single, the user's choice; the real ones are semi-automatic only).

| | `GunsOfTienPost93.VECTORCRB` "Vector .45 Carbine" (built) | `GunsOfTienPost93.VECTORSDP` "Vector 9mm Pistol" (built) |
|---|---|---|
| What | KRISS's CRB Enhanced in the Vector .45's flat dark earth (user, 2026-11-03: "use this version of CRB. keep the same color"): an M-LOK handguard to L -120.5 (top rail carried on, a bottom rail for GoM's foregrips), the 16" barrel in a 48 mm shroud to L -300, an M4-type stock on KRISS's folding adapter | the Vector 9mm without its stock (the user's photo of a Gen II SDP): the upper and top rail run on to L 361, a black end cap with a QD sling swivel, the SMG's 5.5" barrel with a knurled thread protector to L -26.5; sand |
| Held | as a rifle, two hands, back slot, GoM's MP5 reload (the .45's) | like a pistol (one hand), back slot, never a holster, GoM's MP5K reload |
| Magazines, muzzle | the .45's: Glock 21 13, KRISS's 30, GoM's .45 mount device and P45 on the shroud's face; foregrips under the handguard, lights / lasers on KRISS's side rails as the SMG | the 9mm's: GoM's Glock 17 17, Glock's 33, KRISS's 40; the Mk9's mount device and can at the receiver's face (the mount covers the protector) |
| Damage | 1.1-1.8 (the .45 SMG 1.0-1.6; .45 ACP ~1000 ft/s from 16" against ~850), crit 22, stop 2.5 | 0.9-1.4 (the Vector 9mm's barrel), crit 20, stop 2.0 |
| Handling | HitChance 57, Aimingtime 40, RecoilDelay 11, range 32, sight 5-16 (the PS90's step from the TR) | HitChance 50, Aimingtime 33, RecoilDelay 12, range 22, sight 4-12 (the SMG with its stock folded: 52 / 35 / 11 / 25) |
| Spread | 0.08 / 1.1 (the .45 SMG 0.10 / 1.3) | 0.10 / 1.4 (the 9mm SMG 0.08 / 1.1, its stock x 0.75 / 0.85) |
| Weight, sound | 2.7 (7.8 lb x GoM's SMG ratio); 57 / 16 (sound_model.py, .45 from 16") | 1.9 (5.9 lb); 107 / 31 (the Vector 9mm's) |
| Loot | shares the Vector .45's alternative: one of the two guns, as the PS90 shares the P90 TR's | shares the Vector 9mm's alternative the same way |

## Desert Tech MDRx .223 and .308 (user, 2026-11-04: approved and built, not played in game yet)

Desert Tech's bullpup (MDR shown 2014, sold 2017-2019; MDRx 2020-2024), modelled as the **MDRx**: one chassis, the
calibre set by a barrel / bolt / magazine-adapter kit. Two guns, both **semi-automatic only** (the production gun;
the select-fire MDR-A stayed a prototype), each in a configuration Desert Tech sold: the .223 with the **16" barrel
and side ejection**, the .308 with the **20" barrel and forward ejection** (every .308 Desert Tech lists ejects
forward; the user, 2026-11-04: "use the correct ones so long as one of them should side eject or forward eject").
No new rounds. References: `references/mdr/` (git-ignored, SOURCES.txt), see CLAUDE.md "Decisions (Post-93)".

| | `GunsOfTienPost93.MDR223` "MDRx .223 Semi-Automatic Rifle" | `GunsOfTienPost93.MDR308` "MDRx .308 Semi-Automatic Rifle" |
|---|---|---|
| Real | .223 Wylde, 16" (406 mm), side eject, 3.72 kg, 698 mm | 7.62 NATO / .308, 20" (508 mm), forward eject, about 4.1 kg, about 800 mm |
| Family | `5.56x45mm` (GoM's 5.56 and its loads, .223, `Base.556Bullets`) | `7.62x51mm` (GoM's 7.62x51, .308, the main mod's .308 Soft Point, `Base.308Bullets`) |
| Magazines | GoM's STANAG magazines (20 to 150), its "STANAG" profile (Desert Tech ships a 30-round PMAG) | new SR-25-pattern family, one profile like GoM's STANAG: "PMAG 10Rds / 20Rds / 25Rds 7.62x51mm Magazine" (Magpul PMAG LR/SR) + "PMAG 50Rds Drum 7.62x51mm Magazine" (Magpul D-50); fits nothing else yet (GoM has no SR-25-pattern gun, the SCAR-H's are FN's own) |
| Muzzle | GoM's AR mount device and its suppressors / brakes, as the SCAR-L | the SCAR-H's mount device + SOCOM762-RC (both 5/8x24) |
| Stats | GoM's AR-15 (0.8-1.6, crit 20, range 50), HitChance 52, Aimingtime 35, RecoilDelay 13, condition 1 in 220 | GoM's M14 (1.2-2.2 -> 1.2-2.1 for 20" vs 22", crit 40, range 60), HitChance 52, Aimingtime 50, RecoilDelay 16, condition 1 in 240 |
| Sound (sound_model.py) | 187 / 53 (5.56 from 16") | 216 / 62 (7.62x51 from 20", as the SCAR-H) |
| Weight | 3.7 | 4.1 |
| Ejection (Hot Brass) | to the right, from the port behind the grip | forward along the right-side chute, out by the handguard's rear |

Both: held as rifles (two hands, back slot), GoM's FAMAS reload ("famas_rifle", as the AUGs and the PS90), the
ambidextrous charging handle at the front of the chassis drawn as our non-reciprocating `<gun>_HANDLE` with the bolt
carrier plate in the port (section "The charging handle and the bolt are not always the same part"); the full-length
top rail (receiver + handguard, ~14") for GoM's optics, GoM's optional Picatinny_Rail_Left / _Right drawn as
our short M-LOK rail sections for its lights and lasers (user, 2026-11-04, the Vectors' way; they replaced two
hidden integral side rails), no GoM bipod (user, 2026-11-04: the MDRx has its own handguard bipod); no bayonet,
no folding stock. Loot: civilian and post-1993, in GoM's `World_Anachronistic_Spawner`; proposed as one alternative
giving one of the two guns (the PS90 / P90 TR way), built as one alternative each (the UMPs' rule: GoM rolls each
group of an alternative on its own, so a shared one could pack the .223 with PMAGs and .308 boxes), each with three
magazines and GoM's civilian boxes as its AR-15 kit (.223 / .308); the D-50 on 2 % of found .308s and in the
high-capacity magazine spawner, as the SCAR-H drum. Colours (approved with the design): the .223 black, the .308 flat
dark earth (the colour of the reference photos). Build notes: CLAUDE.md "Desert Tech MDRx".

Handguards (user, 2026-11-04): the .223 keeps Desert Tech's polymer handguard, GoM's foregrips under it (a hidden
integral bottom rail). Every .308 has **BLK LBL's 20" ALX bipod handguard** built in (the user chose "built in" over
an optional part): FDE aluminium, M-LOK rows on its sides, its own top rail, two legs hinged at the nose that fold
back flush into its underside. As the AUG HBAR's integrated bipod: `MDR308_Integrated_Bipod_Folded / _Deployed`
(BipodIntegrated, Gunworks' FoldingBipod, found folded), GoM's rail bipod stats deployed (Aiming Time x1.1, Hit and
Crit x1.15; no spread modifier, the gun is semi-automatic), Gunworks' bipod stance. The .308 takes no foregrip: the
folded legs fill the front of the underside (their grooved sides are the real ALX's grip surface), and behind them
the 20" handguard's underside is closed. The legs are the 16"'s (Desert Tech lists one leg height, 6 1/4" to
9 1/8", for every length): aluminium housing, carbon inner leg (drawn out 55 mm deployed), rubber foot, splayed
to a 45 degree V (user: "nearly 45 degrees"), detailed from the user's photos.

## OTs-14 Groza family (user, 2026-11-11: designed; all four built 2026-11-12)

User: "the Groza family that uses 7.62x39, 9x39 and 5.45x39". TsKIB SOO's bullpup on the AKS-74U's mechanism (about
three quarters of its parts), by Telesh and Lebedev: work began in December 1992, prototypes within a year, shown at
MILIPOL Moscow in April 1994, made 1994-1999 (Wikipedia "OTs-14 Groza"). Nothing of it existed in July 1993, so
**Post-93**. Gas piston, rotating bolt, closed bolt; the AK's charging handle on the right, which moves with the
carrier.

| | `GunsOfTienPost93.GROZA1` "Groza-1 Assault Rifle" | `GROZA4` "Groza-4 Assault Rifle" | `GROZA2` "Groza-2 Prototype Assault Rifle" |
|---|---|---|---|
| Real | OTs-14-1A, 7.62x39; the Army adopted it in 1998, production stopped for lack of money | OTs-14-4A, 9x39 subsonic, 240 mm barrel, 610 mm, the main model (MVD 1994, then Spetsnaz) | OTs-14-2A, 5.45x39, a prototype only (never adopted) |
| Magazines | GoM's "762x39" profile: its AK-47 30 and 75 box, the main mod's RPK 40 and 75 drum | GoM's AS VAL 10 / 20 / 30 (the real Groza took the OTs-12's 20, the VSS / AS pattern) | GoM's "545x39" profile: Bakelite 30, 45, 60 and the 100 drum |
| Rounds | GoM's 7.62x39 and ours (US Subsonic, Soft Point, Steel Core) | GoM's SP-5 and our SP-6 | GoM's 7N6 |
| Stats (set while building) | GoM's AKS-74U pattern with the 7.62 round | GoM's AS VAL | GoM's AKS-74U |

All three (proposed): one shared model with a barrel and magazine well per calibre (the UMPs' and Vectors' way), held
as a rifle, GoM's "famas_rifle" reload (the bullpup's magazine behind the grip, as the AUGs and MDRx), the carrier
and handle as one part on GoM's swap (as the RPKs: the AK handle reciprocates, no ChargingHandle part), Auto /
Single at 700 rpm (the real 700-750), loot as an alternative in GoM's `World_Anachronistic_Spawner` with up to 3
magazines and the calibre's GoM box.

Decided (user, 2026-11-11):
- **Muzzle**: the Groza-4 gets its own detachable suppressor, modelled. The Groza-1 takes GoM's PBS-1, so US
  Subsonic cycles it without racking while the PBS-1 is fitted ("PBS-1 groza can benefit from subsonic ammo without
  racking"), the AKs' and RPK's rule.
- **GP-25 grenade launcher** (user, 2026-11-11: "we can add a Groza-2 with GP-25"): a fourth gun, the 5.45x39
  Groza-2 with the GP-25 fitted in place of its trigger group's front, built as GoM's `M16A2_M203`: the rifle with
  the launcher as a permanent part plus a launcher-mode weapon item (GoM's `M203_Weapon`) that Gunworks swaps to,
  firing GoM's 40 mm rounds (the VOG-25 is 40 mm too, GoM has no caseless round). The swap is to be traced in
  GoM / Gunworks before building. The other three stay without a launcher. Read as the 5.45 Groza-2; the user to
  confirm it is not meant for the 9x39 Groza-4, the main real model with the GP-25.

Barrels and the GP-25 (user's photo, 2026-11-11, a Groza-1 with the GP-25, right side): the 7.62x39 Groza-1 (and the
5.45x39 Groza-2) have the long barrel, standing 159 mm out of the front housing past the short gun's muzzle with a
slotted compensator (about 770 mm overall; Wikipedia's 420 mm barrel), the Groza-4 the short one inside its forend
(610 mm). The GP-25 version (rebuilt 2026-11-11 after the user's "looks horrible", from more photos:
wikireading.ru's OTs-14-4A left / right, weaponland.ru's OTs-14-4A and Groza-1 with the launcher, armedman.ru's text;
references/groza, not in the repo): the launcher's casing is the whole gun's handguard (a GP-25-like 40 mm unit
without its own grip or quadrant sight); its front hangs from a coupling clamped round the barrel, which also carries
the folding frame sight; the rifle's trigger base is removed and the launcher's takes its place, one trigger for both
in its round opening, the AV / GR selector on its left above it. Modelled: the tube 72 mm across in a sleeve with four
grooves, the chunky frame (as wide as 30 mm) whose underside sweeps up from the tube's rear to the pistol grip, the
frame sight standing up, perpendicular to the barrel (user, 2026-11-11); the barrel 18 mm across, its muzzle about 148 mm past the
short gun's. The OTs-14-4A (9x39) is the base model with the launcher in every source. The long Groza without the launcher (forend and front grip, the barrel out of it) has no photo
of its own. Three bodies on one texture: scripts/post93/build_groza.py, preview docs/post93_groza_preview.png.

Line-up (user, 2026-11-11: "Groza-1 with GP-25 and the other 3 groza regulars"): Groza-1 (long barrel, forend and
front grip), Groza-1 with the GP-25, Groza-2 (the compact OTs-14-4A of the user's photo: no forend or front grip, the
barrel's collar and threaded tip out of the front housing), Groza-4 (short barrel in the forend, front grip, its own
suppressor).

Built (2026-11-12; `gen_post93_guns.py grozas()`, `shared/GunsOfTienPost93/Groza.lua`, `make_groza_art.py`): the
optics on GoM's Picatinny Rail (Up) over the carrying handle (below), the barrels as the photos show them (above).
- Stats: Groza-1 from GoM's AK-47 (1.5-1.8, HitChance 52, the bullpup's steadier hold), Groza-2 its AKS-74U (1.0-1.6),
  Groza-4 its AS VAL (0.7-1.4, HitChance 52); sounds by sound_model.py (175 / 50, 205 / 59). 700 rpm, spread a
  little under GoM's AK-47 / AKS-74U / AS VAL.
- The Groza-2 is held like a pistol (user, 2026-11-12: "hold Groza-2 using handgun stance"), as GoM's MP5K and the
  MP7: the body turned about the bore (GROZA2_HELD), its parts turned by their points, GoM's MP5K reload.
- The Groza-4's suppressor is built in (user, 2026-11-12: "9x39 default ammo is treated as subsonic... but the gun took
  the stats into its own. groza-4 needs to do the same"), as GoM's AS VAL: the quiet sound in the gun's own stats
  (CapGunRevolverShoot, gain 0.8, no muzzle flash), the can a hidden part that cannot come off. A bit louder than the
  AS VAL (user, 2026-11-12: "louder in real life", "just a bit", "like maybe a 24 / 6"): 24 / 6 against the AS VAL's 22 / 6, whose can wraps
  a ported barrel.
- GoM's AK bolt swap closing on an empty chamber (the RPKs' wrapper, `GunsOfTien_RPK.CLOSES_ON_EMPTY`), GoM's
  "famas_rifle" reload with GoM's magazines in the off hand at our size (the main mod's AK / AK-74 `_Hand` items,
  Post-93's own `9x39Magazine10/20/30_Hand` on `_GoT` models at 0.603 / 0.645).
- Found gun: the bolt, GoM's standard magazine of the calibre mostly, a red dot or low scope now and then with its
  rail (":PRU"). Loot: an alternative each in `World_Anachronistic_Spawner` (up to 3 magazines, up to 3 boxes).
- The Groza-1 with the GP-25 (user, 2026-11-12: "Make the Groza-1 with GP-25 now"), `GROZAGL` "Groza-1 Assault
  Rifle with GP-25", built as GoM's M16A2_M203: the Groza-1 on GROZAGL_BODY, 4.2 kg (GoM's M203 adds 1.3 to its
  M16A2; the GP-25's 1.5 kg replaces the forend), a hidden `GROZAGL_GP25_Integrated` part (PartType Underbarrel) that
  Gunworks' Underbarrel swaps for `GROZAGL_GP25` "GP-25 Grenade Launcher", drawn as the same body with its muzzle at
  the GP-25's bore (`muzzle_gl`); GoM's M203 stats, sounds and reload ("m203_reload", the double-barrel archetype),
  its 40mm family standing in for the VOG-25 (the same bore; GoM has no other grenade round), caseless (no spent case
  to unload). No tube-opening parts (GoM's Underbarrel_Open / _Close slide the M203's tube; the GP-25 is muzzle-loaded).
  Loot: the Groza-1's alternative picks one of the two, as GoM's M16 alternative its M16A2_M203.


## Knight's Mk 11 Mod 0 (user, 2026-11-12: designed and built)

The SR-25 as SOCOM adopted it in May 2000 (Wikipedia "SR-25"), so Post-93: `GunsOfTienPost93.MK11` "Mk 11 Mod 0
Semi-Automatic Rifle" (GoM's naming: its semi-automatic sniper rifles are "PSG-1 / SVD Semi-Automatic Rifle"; the
user: "let's do Mk 11 Mod 0"). The difference with the 1990 SR-25: **moddable** (user: "The Mk 11 will be moddable.
Like no integrated parts. I will have integrated picatinny rails though"): no integrated scope, bipod or suppressor;
integrated Picatinny rails as hidden required parts, modelled in the body (KAC's rail handguard with rails on all
four sides, the receiver's flat top), for GoM's optics on top, foregrips and bipods under, lights left, lasers right.
The muzzle takes the SCAR-H's mount device (renamed "7.62x51mm Family Muzzle Mounting Device", user, 2026-11-12) and
SOCOM762-RC, as the MDRx .308; magazines the main mod's KAC 20 and Post-93's PMAGs. Built on the SR-25's receiver and
stock (scripts/post93/build_mk11.py) from Commons "SR-25 pic02.jpg" (CC BY 2.0, a Mk 11 with its kit), scaled by the
SR-25's stock: the handguard to 545 mm ahead of the grip, the 20" barrel's muzzle at 700, the folded flip-up front
sight on the top rail (GoM's AR15 receiver keeps its fixed rear sight block). Preview docs/post93_mk11_preview.png.

Decided (user, 2026-11-12, the model approved): a found Mk 11 comes mostly with the KAC 20 (what SOCOM issued), the
PMAGs and the D-50 rarer; loot as the SCAR-H (GoM's army rifle spawners, `World_Army_Rifle_Spawner` /
`Zombie_Army_Rifle_Spawner`). The integrated top rail is registered as the parent GoM's optics need (as the MDRx's):
no Sniper Mounting Rail (GoM's `Sniper_Mount` only adds a rail to its bolt-action rifles); GoM's LR10X / LRX12X / TR06X
and every other optic fit straight on it.

Groza optics (user asked "what is realistic?", 2026-11-12; then "that's not how the scope works on groza" to an AK
side mount): the standard kit's optical sight is "mounted directly on the carrying handle" (wikireading.ru: "оптический
прицел, устанавливаемый непосредственно на рукоятку для переноски"); its drawing of a commercial scope shows the mount
block clamped on the handle's top bar just behind the front post, the scope above the handle. The PSO-1 on the
receiver's side rail was only an early 7.62 model or prototype. So GoM's optional `Picatinny_Rail_Up` (user,
2026-11-12: "let's use GoM's Up", over a Groza-only item), drawn on the Groza as `GROZA_RAIL_UP`: a clamp on the
handle's top bar with a short Picatinny rail (the main mod's `Rails.Register`, as the Uzis' top rails), GoM's optics
on it; without it the handle is bare, as on the real gun. Up only: no rails under or beside the forend.

## H&K HK416 D14.5RS (user, 2026-11-13: model built for review, the rest proposed)

The first of the HK416 / HK417 set (TODO.md): H&K's 14.5" carbine in its original pattern (2004-05, Wikipedia
"Heckler & Koch HK416"; not the A5): an M4-type AR with H&K's G36-derived short-stroke piston, a cold hammer-forged
368 mm barrel, the free-floating rail system ("RS": rails on all four sides), rail-mounted flip-up sights and the
six-position telescopic stock with storage. Infobox: 850 rpm, STANAG magazines; the D14.5RS weighs 3.49 kg and is
about 800-900 mm long (stock in / out; sources differ).

**Model** (scripts/post93/build_hk416.py, render_hk416.py, make_hk416_preview.py; preview
docs/post93_hk416_preview.png), rebuilt 2026-11-13 from 28 reference images gathered first (references/hk416/,
SOURCES.txt, contact_sheet.png: IMFDB side views, H&K's 2007 operator's manual, licensed VFC D14.5RS / HK416D replicas
from both ends with close-ups, the user's photo). Measured on IMFDB's clean D14.5RS left side (1.69 px a mm, read
off GoM's receiver; its muzzle lands within 8 mm of GoM's M4A1's, the same barrel): GoM's AR15 receiver, buffer tube,
bolt and handle kept, its flat-top rail carried to the rear; the Free Floating Rail System to 447.6 mm, rails at 12 /
3 / 6 / 9 o'clock, four oval slots over and under each side rail, QD cup at the front, lock boss under the rear; the
gas block with the MP5-type front sight up; the stepped barrel and H&K's flash hider (GoM's birdcage stretched to
54 mm); H&K's diopter rear sight up (as in every photo); H&K's ergonomic grip (traced, replaces GoM's A2 grip); H&K's
telescopic stock (housing, ribbed lower body, butt block with ribbed pad and sling loop), its own node `HK416_STOCK`,
deployed at `stock`, all the way in at `stock_folded` (75 mm). The earliest production guns (2004-05: IMFDB's first
14.5", the 2007 manual's photos) had the M4 six-position stock and an A2-type grip; the H&K stock and grip are what
every later D14.5RS photo and the licensed replica show. On GoM's AR15 texture.

Decided (user, 2026-11-13: "I approve of this HK416"; built the same day, not played):

| | `GunsOfTienPost93.HK416` "HK416 Assault Rifle" (GoM: "M4A1 Assault Rifle") |
|---|---|
| Family / magazines | GoM's 5.56 family and STANAG magazines (20 to 150, profile "STANAG") on GoM's own models (the gun is at GoM's AR15 size), MountOn appended as for the SCAR-L / MDRx .223 |
| Muzzle | GoM's AR mount device and its parts (MKI / NDR, LR2, LX, Trix42), as the SCAR-L |
| Stock | `HK416_Integrated_Stock_Folded / _Deployed` (Gunworks' FoldingStock, as GoM's M4A1) drawing `HK416_STOCK`; out: GoM's CAR-15 / our SCARs' stats (HitChance x1.15, AimingTime x0.85; GoM's M4A1 stock has none) |
| Rails | four integrated rails as hidden required parts (the Mk 11's way): optics, foregrips + bipods, lights left, lasers right |
| Iron sights | follow the optic (user, 2026-11-13, three states): Gunworks' `ConditionalModel` on the Scope slot: none = both up (`HK416`), a red dot / holographic sight (EXPS1, EXPS3, Aimpoint, OKP-7, Reflex S2, JS14, Kobra) = rear folded (`HK416_RD`), a magnified scope (Elcan, LR4X, LR10X, LRX12X, TA28, TR06X, PSO-1) = both folded (`HK416_FD`); other mods' optics leave them up |
| Stats | GoM's M4A1 (1.0-1.4, range 40) with the SCAR-L's HitChance 52 (free-floating barrel), jam 0.75 and condition 1 in 250 (piston guns), 850 rpm (GoM's M4A1's spread), Auto / Single |
| Sound | 193 / 55 (the main mod's realistic model for GoM's M4A1, 5.56 from 14.5"), GoM's M16 sound events |
| Reload | GoM's "ar15_rifle" with "boltCatchAfterEmptyInsert" (as the SR-25 / Mk 11) |
| Weight | 3.5 |
| Loot | the SCAR-L's: an alternative in GoM's `World_Army_Rifle_Spawner` (up to 6 STANAG 30s and boxes) and `Zombie_Army_Rifle_Spawner` (4); a found gun rolls GoM's M4A1 magazines and optics |

No bayonet (no lug on the rail system), ejection to the right (Hot Brass: GoM's M4A1 / the SCAR-L's values), the bolt
and handle GoM's AR15 table. Optics sit 150 mm ahead of the grip, clear of the diopter: on the body each optic picks,
every GoM optic sinks at most 1.4 (fit_audit's units) and red dots float up to 1.2 (fit_audit itself reads the
sights-up body, where the Elcan's rear meets the standing diopter).

## H&K HK417 16" Recce and 20" Sniper (user, 2026-11-13: "start on the HK417 until finished"; built, not played; model approved)

The HK416's 7.62x51mm big brother in its original pattern (2006-; Wikipedia "Heckler & Koch HK417", modernfirearms.net:
short-stroke piston as the G36, seven-lug rotating bolt, cold hammer-forged barrels, the HK416's four-sided free-floating
rail system, H&K's six-position stock, translucent 10 and 20-round polymer magazines, 600 rpm; the 16" 985 / 905 mm
stock out / in). Both from the TODO: the 16" Recce and the 20" Sniper, one receiver, stock and magazines, the Sniper
with a longer barrel and handguard. References: references/hk417/ (SOURCES.txt, contact_sheet.png; about 370 photos,
H&K's own press photo of a 16" the measuring one). Model: scripts/post93/build_hk417.py (see CLAUDE.md "HK417 Recce and
Sniper"); review renders render_hk417.py; icons and the magazine texture make_hk417_art.py.

| | `GunsOfTienPost93.HK417` "HK417 Battle Rifle" (16" Recce) | `GunsOfTienPost93.HK417S` "HK417 Sniper Rifle" (20" Sniper) |
|---|---|---|
| Names | GoM's "G3 Battle Rifle" | GoM's "M24 Sniper Rifle" |
| Magazines | H&K's 20 (standard) and 10, `762x51Magazine20_HK417` / `10` (0.15 / 0.1), profile "7.62x51mm HK417" (real HK417 magazines fit neither the SR-25 nor the SCAR-H), GoM's 7.62x51mm family | the same |
| Stats | our SCAR-H's (the same 16" 7.62x51): 1.3-1.8, crit 30 x5, HitChance 53 (free-floating), aim 50, recoil 15, range 60, jam 0.5 and condition 1 in 250 (piston, as the HK416), weight 4.1 | our Mk 11's role, select fire: 1.3-2.1, crit 40 x5, HitChance 56 (accurized), aim 55, range 65, sight 10 / 20, condition 1 in 260, weight 4.3 |
| Fire | Auto / Single at 600 rpm, spread 0.2 / 3.2 | 600 rpm, 0.18 / 3.0 |
| Sound | sound_model.py's 7.62x51 from 16": 231 / 66, MSR788Shoot at 2.5 (the SCAR-H's) | from 20": 216 / 62 |
| Stock | `HK417_Integrated_Stock_Folded / _Deployed` drawing `HK417_STOCK`; out: HitChance x1.15, AimingTime x0.85 (the HK416's), automatic spread x0.75 / 0.85 | the same |
| Rails | four integrated rails as hidden required parts: optics, foregrips + bipods, lights left, lasers right | the same, longer |
| Muzzle | the SCAR-H's 7.62x51mm mount device and SOCOM762-RC (5/8x24 as the SCAR-H) | the same |
| Iron sights | the HK416's flip-ups and states: rear folded under a red dot, both under a scope; no rear-off states (fit_audit: every optic clears the folded rear) | the same |
| Reload | GoM's "ar15_rifle" with "boltCatchAfterEmptyInsert" (as the Mk 11) | the same |
| Loot | one alternative in GoM's `World_Army_Rifle_Spawner` (6) and `Zombie_Army_Rifle_Spawner` (4) giving one of the two, with up to n of H&K's 20s and 7.62x51mm boxes (the SCAR-H's / Mk 11's way) | |
| Hot Brass | the Mk 11's values | the same |

## H&K HK416 .22 LR pistols (user, 2026-11-13: both decided, then only Walther's built; not played)

User: "Let's start with HK416 pistol", then, shown the two that were sold, "WHY NOT BOTH??? MP5 series has a lot of
variations itself"; held like a pistol (confirmed). References gathered first (references/hk416_22/, SOURCES.txt,
four contact sheets: about 30 photos of the first generation, 80 of the second, 34 of the magazines, the H&K USA
sheet and H&K GmbH's card; no straight top or front view exists among them). Both are civilian .22 trainers made
in Germany under H&K's licence, blowback, semi-automatic, no stock and **no buffer tube** (the receiver ends in a
round cap with a sling point), H&K's ergonomic grip, the HK416's receiver markings, the same polymer magazines.

| | Gen 1: Walther HK416 .22 Tactical Pistol | Gen 2: H&K USA HK416 .22 LR Pistol |
|---|---|---|
| Real | Carl Walther for Walther Arms / Umarex USA, about 2009/10 to 2018 (5780303 = 20 rds, 578030310 = 10) | Umarex for H&K USA, from 2019 (81000403 = 20 rds, 81000404 = 10; grey, FDE, two-tone, bronze variants) |
| Size | 9" barrel, 17.2" (437 mm), 5.0 lb (2.27 kg) without magazine | 8.5" (217 mm) barrel, 425 mm, 63.8 mm wide, 272 mm tall, 2050 g without magazine (H&K USA sheet) |
| Front | short quad rail (RIS, four rails, the HK416 D10RS look), the barrel inside a long round shroud that looks like a can (thread M8x0.75 under it) | HK416 A5-style M-LOK handguard, Mil-STD-1913 top, 4-prong flash hider on a 1/2x28 thread |
| Sights | H&K style: hooded post on the rail's front, rotary diopter rear; clamped on the rail, taken off for an optic | polymer flip-ups (rear fully adjustable, aperture 33 mm high), sight radius 304.6 mm |
| Colour | black only | **HK bronze** (user, 2026-11-13; H&K's brown, the A5's colour) |

Decided (user, 2026-11-13, asked with the colours and the proposal below): gen 2 in **HK bronze**; **named by
their rails**, "HK416 .22 Quad Rail Pistol" (gen 1) and "HK416 .22 M-LOK Pistol" (gen 2); **Auto and Single**
(select fire like the Vector SDP, though both real ones are semi-automatic); **no suppressor part**: "The other
pistol seems integrated suppressor. we won't have a lootable part of it. only integrated for now", so gen 1's
can-like shroud counts as an integral suppressor (sound_model.py's integral rule: 71 / 20 becomes 22 / 6, the AS
VAL's) and gen 2 takes no can. (Flagged to the user: the real gen-1 shroud is a barrel shroud over a .22 liner, not
a suppressor.) Item ids `HK416QR22` / `HK416ML22` replace the proposal's.

Then, while the two were wired (user, 2026-11-13: "let's use walther's"): **only Walther's gen 1 ships**; H&K USA's
M-LOK pistol is shelved (docs/shelved_hk416ml22.md). Built the same day (not played):

| | `GunsOfTienPost93.HK416QR22` "HK416 .22 Quad Rail Pistol" |
|---|---|
| Hold | like a pistol (the Vector SDP's way: turned model, GoM's handgun item lines), back slot, GoM's MP5K reload ("handgun2"; GoM's AR bolt catch rule left out: its close step needs a clip the MP5K reload has not got) |
| Magazines | H&K's 10 / 20 / 30 (`22LRMagazine10/20/30_HK416`, 0.06 / 0.08 / 0.12), profile ".22 LR HK416", the main mod's ".22 LR" family; the 20 as standard (Walther sold it with one) |
| Fire | Auto / Single at 900 rpm (our choice for a light .22 blowback), spread 0.06 / 0.9, the least of our automatics; Single first |
| Stats | the proposal's: 0.3-0.6, crit 25 (x3.0), HitChance 55, aiming 20, recoil 6, range 22, jam 1.0, condition 1 in 180, weight 2.2, stop power 0.8 |
| Sound | a plain shroud after all (user, 2026-11-13: "Plain shroud, loud", over the integral suppressor decided above): .22 LR from 9", 71 / 20, its shot the main mod's synthesised .22 LR sound `GunsOfTien_22LRShoot` (every .22 LR gun's; scripts/make_22lr_sound.py) at GoM's pistol gain 1.5, handgun muzzle flash; GoM's M16 handling sounds; no muzzle parts |
| Rails | all four as hidden integrated parts: optics on top, GoM's foregrips underneath (user, 2026-11-13: "let it take a foregrip", as the pistol-held MP7A2 and Vector SDP; at 330 mm, about 60 mm ahead of the curved 30), lights left, lasers right |
| Iron sights | IronSights.Register: the rear taken off under a red dot (`HK416QR22_RD`), both under a scope (`_FD`); every GoM optic clears the body it draws (fit_audit against each state) |
| Bolt, handle | GoM's AR15 table (HK416.lua's) |
| Loot | an alternative in GoM's `World_Anachronistic_Spawner` (the gun, up to 3 of its 20, up to 4 .22 LR boxes); the .22 LR box (0.1) and carton (0.05) beside vanilla's 9mm box / carton in **every** list, homes included (.22 LR was America's commonest round; Post-93's Loot.lua, as the main mod has no .22 gun) |
| Hot Brass | the SDP's place, lighter (force 0.45); the main mod maps the .22 rounds to HBVCEF.22_Casing |

The proposal (superseded where the decisions above say otherwise):
- **Items** `GunsOfTienPost93.HK416T22` "HK416 .22 Tactical Pistol" (Walther's own product name) and
  `GunsOfTienPost93.HK41622` "HK416 .22 Pistol"; Post-93 (both after 1993).
- **Held like a pistol** (confirmed): the Vector SDP's way, a turned model, SwingAnim Handgun, GoM's MP5K reload
  ("handgun2"), back slot, never a holster. **Semi-automatic only**, as sold (the user took select fire for the SDP;
  say so if wanted here too).
- **Magazines**: H&K's own polymer .22 magazines fit both (same part numbers under Walther, Umarex and H&K USA:
  51000199 / 51000200 / 51000208), charcoal grey as shipped: "HK416 10Rds .22 LR Magazine" (short, straight),
  "HK416 20Rds .22 LR Magazine" (curved), "HK416 30Rds .22 LR Extended Magazine" (long, curved), weights 0.06 / 0.08
  / 0.12, joining the main mod's ".22 LR" family (plain, Subsonic, Hollow Point, Hyper Velocity). Aftermarket 50-round
  drums exist but are not H&K's: left out.
- **Stats** (.22 LR from 8.5-9": about 137 J against a 9 mm pistol's 500): damage 0.3-0.6, crit 25, HitChance 55,
  Aimingtime 20, RecoilDelay 6 (almost no recoil), range 22, condition 1 in 180 (dirty rimfire blowback), weight
  2.0 (gen 2) / 2.2 (gen 1). Sound from sound_model.py (.22 LR, 2 grains, subsonic from these barrels: 326 m/s): 72 /
  21 (8.5") and 71 / 20 (9"), GoM's quietest pistol shot events.
- **Rails**: gen 1 its four integral rails (optics on top; lights left, lasers right; no foregrip: a vertical grip
  makes a US pistol an NFA "AOW", and the pistol hold has no support hand), gen 2 its top rail and GoM's optional
  side rails on the M-LOK handguard for lights and lasers (the Vector SDP's way).
- **Iron sights follow the optic** (IronSights.lua): gen 2 folds like the HK416 (rear folded under a red dot, both
  under a scope); gen 1 has the rear taken off under any optic, the front kept under a red dot and taken off under a
  scope.
- **Muzzle**: gen 2's thread takes a .22 suppressor once the flash hider is off; gen 1's thread is under the shroud
  (an adaptor in real life). GoM has no .22 can: either a .22 suppressor of our own (one per gun family, the
  established rule: a real 1990s-2010s model) or none; to decide.
- **Loot** (civilian guns, the first in Post-93): GoM's `World_Anachronistic_Spawner` (civilian homes and survivor
  stashes, as GoM's other late guns) and the gun store lists; the .22 LR box (still unspawned) beside vanilla's
  9 mm pistol boxes in civilian ammo lists. Details with the build.
- **Hot Brass**: the .22 casing, ejection to the right.
- **Model**: from GoM's AR15 receiver like the HK416 (receiver, bolt, charging handle; buffer tube off, the round
  end cap added), the HK416's traced H&K grip and selector labels; gen 1 the HK416's front sight and diopter on a
  short quad rail and the shroud; gen 2 a new A5-style handguard, polymer flip-ups and flash hider. Exported turned
  (pistol-held) like the Vector SDP.
