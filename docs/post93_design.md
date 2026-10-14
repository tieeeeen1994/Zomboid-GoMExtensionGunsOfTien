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

Guns `MP7A1`, `P90TR`; models `MP7A1` (+ `MP7A1_BOLT`, `MP7A1_STOCK`), `P90TR` (+ `P90TR_BOLT`); stock parts
`MP7A1_Integrated_Stock_Folded / _Deployed`; magazines `46x30Magazine20_MP7`, `46x30Magazine30_MP7`,
`46x30Magazine40_MP7`, `57x28Magazine50_P90`; suppressors `MP7_Suppressor`, `P90_Suppressor`; mounts
`MP7_Muzzle_Mount_Device`, `P90_Muzzle_Mount_Device`; rounds `46x30_Bullet` (DM11), `46x30_Bullet_Subsonic`,
`57x28_Bullet` (SS190), `57x28_Bullet_SB193`, `57x28_Bullet_SS197SR`. Files (one set per gun): models_X/weapons/firearms/
GunsOfTienPost93_MP7A1.fbx and _P90TR.fbx, models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx and
_P90_magazines.fbx, models_X/weapons/parts/GunsOfTienPost93_MP7_parts.fbx and _P90_parts.fbx; textures under
textures/weapons/GunsOfTienPost93/. The charging handles do not reciprocate on either gun, so no animated bolt.
