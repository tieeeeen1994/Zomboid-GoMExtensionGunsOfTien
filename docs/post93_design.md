# GoM Extension: Guns of Tien - Post-93 — design (approved 2026-10-14, building)

Sub-mod `GoMExtensionGunsOfTienPost93` in the same Workshop item; requires the main mod, GoM, Gunworks and Ammo Maker.
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
| 4.6x30mm Subsonic | ×0.6 damage, sound ×0.5, no pierce |
| 5.7x28mm SS190 (standard, steel / aluminium penetrator) | base stats, pierces 2 |
| 5.7x28mm SB193 Subsonic (made for the suppressed P90) | ×0.6 damage, sound ×0.5, no pierce |
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
textures/weapons/GunsOfTienPost93/. The charging handles do not reciprocate on either gun, so no animated bolt.

## FN Five-seveN (user, 2026-10-16)

Reuses Guns of Marz's own name: GoM's ItemName.json has `"MarzGuns.FIVESEVEN": "5.7x28mm Five-SeveN"` and nothing
else (no item, model, magazine, icon), so the gun is the item `MarzGuns.FIVESEVEN` (block in GoM's module, our
`items_fiveseven.txt`), named by GoM's translation; everything it uses is ours (module GunsOfTienPost93).

| | FN Five-seveN |
|---|---|
| Real | 1998 (FNH USA models 2000s), 5.7x28, 122 mm barrel, 208 mm long, 0.61 kg, semi-automatic |
| Model | built from a side photo of an FNH USA Five-seveN (docs/fiveseven_atf.jpg, U.S. ATF, public domain), 0.72 scale, GoM's pistol conventions (upside down, body + slide, magazines in gun space); silhouette overlap 96.0% |
| Features | "match what GoM has" (user): GoM's Glock 17 / M92FS set: animated slide, Beretta mount + pistol sights (PL4, PM2, PS1), GoM's two pistol lights on the underbarrel rail (LP; TL, a flashlight in a clamp as pistols carried them before rails), no lasers (user 2026-10-16), muzzle mount device + suppressor |
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
| Lights | GoM's two pistol lights (LP, TL), no lasers, as the Five-seveN |
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
and muzzle device spawners, boxes and cartons beside vanilla's boxes and cartons, Ammo Maker parts and their boxes
through Ammo Maker's own loot (every active part). Not spawning, as GoM's own: crates (packed from 4 cartons), and the
cartons of calibres vanilla lacks (GoM's 7.62x39 / 9x39 cartons never spawn, so ours of those don't either); loose
rounds come from boxes; and every special load (4.6x30mm Subsonic, 5.7x28mm SB193 and SS197SR, and all of the main
mod's rounds), since GoM never spawns its own special loads: only the standard 4.6x30mm DM11 and 5.7x28mm SS190 boxes
and cartons are loot. The Five-seveN, the UCP and their ammunition never spawn in civilian homes.
