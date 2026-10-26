# Resizing Guns of Marz's guns (shelved)

Shelved on 2026-10-26 (user: "remove that option for now and all the resizing in GoM in our mod"). The sandbox
option "[BETA] Resize Guns of Marz" (`GunsOfTien.RescaleGuns`, default off) and `GunScale.lua` were removed; GoM's
guns are drawn at GoM's own sizes. Our own guns were resized in their meshes instead (all at 0.603 of their real
length, the M16A2's proportion) and are not affected. This file keeps what is needed to pick it up again.

- The last `GunScale.lua` (the final per-model table with the group scales below applied, and the scaling of the
  gun's own placing points): `git show 6f1f88e:Contents/mods/GoMExtensionGunsOfTien/42/media/lua/shared/GunsOfTien/GunScale.lua`.
- How the engine applies a model's `scale` (parts, muzzle flash, floor items, placing points): CLAUDE.md "Gun scale".
- Tools: `blender -b --factory-startup -P scripts/scale_audit.py -- <out.json>` (every gun as drawn: body + deployed
  integrated stock / full barrels, plus every part model), then `python3 scripts/scale_audit_report.py <out.json>`
  (each gun's ratio, its own scale, the left palm on it before / after).

## Method

User (2026-10-25): "the MP5A1 and MP5A2 seem a little bit big ... compared to human size ... does it follow the size
proportion from M16?", then "edit each gun so that they have their own scales rather than apply a global scale".
Every gun gets its own `scale`, so that it stands in the M16A2's proportion: scale = the M16A2's ratio (0.603) / the
gun's ratio, where ratio = drawn length / real overall length (stock extended).

- Vanilla draws people at ~0.55 (body 0.98 units for a ~1.78 m man), its M16 at 0.54, its M9 at 0.70. GoM's
  rifle-stance guns run 0.53..0.73 (median 0.63), its pistols and SMGs ~0.70-0.73. The M16A2 is 0.60, the MP5A2 0.73:
  the MP5A2 is ~20% too big next to the M16.
- Left out: GoM's MP5K (held in our compact stance, whose clips are solved for its size) and the Stolzer & Son
  2-bore (no real size; by eye). Our sawn-stock bodies of GoM's break-actions take their gun's scale.

## Guns sharing a magazine share one scale

User (2026-10-26): "when they share a mag like uzi, they [must] still [be] consistent ... while still basing on a
basis". A magazine is a weapon part, drawn at its gun's scale, so guns that mount the same magazine get one scale per
group, from a basis gun whose real size is sure; this overrides the per-gun values below for the other members.
Groups = merged `MountOn` lists of the `PartType = Clip` items. GoM put the `magazine` point at the same offset on
every member of each family (AR 0.1015 / 0.0144, MP5 0.1191, AK 0.1238, G36 0.1101), so their receivers are one size
and the spread comes from barrels / stocks drawn long or short, or a guessed variant.

- AR (STANAG): basis M16A2 **1.00** for M16A1 (0.99), M16A3, M16A2 M203, AR-15 (0.98), M4A1 (0.96), CAR-15 (0.96?),
  XM177 (0.86?). The XM177 then draws 16% longer than a real XM177E2 (787 mm): its barrel / stock or the variant
  guess is off, look at a render.
- STANAG guns of other designs, own receivers: FNC (0.96). At 1.00 it draws 4% longer than real; at its own value
  the STANAG is drawn 4% smaller in it than in an M16. Undecided (GunScale.lua used 1.00).
- FAMAS (0.88): GoM's model is an F1 (small trigger guard), which takes only its own 25-round magazines; STANAG came
  with the G2 (1994). GoM mounts STANAG anyway (gameplay), so no real magazine size ties it to the M16: own scale 0.88
  (the STANAG 12% smaller in it), unless it gets an F1 magazine of its own.
- MP5: basis MP5 **0.87** (the MP5SD agrees) for MP5SD, MP5K (0.84, left out), MP5A2 (0.83). The MP5A2 then draws
  ~5% long: its stock is the odd one.
- AK-74 magazines: basis AK-74 **0.93** for the AKS-74U (0.89).
- G36: basis G36 **0.98** for the G36C (0.97).
- .45 M1911 magazines: basis M1911 **0.86** for the Camp Carbine (0.85).
- Guns on one model share its scale anyway (Mossberg 590 / Masterkey, CAR-15 / its M203).

## Each gun's own scale (ratio now -> scale; `?` = variant guessed from the model)

Rifle stance (vanilla's rifle clips): MP5A2 0.73 -> **0.83** (drawn longer than GoM's MP5, 0.494 / 0.487 for real
680 / 700 mm: one of the two stocks is off), CAMP_CARBINE 0.71 -> **0.85**, XM177 0.70 -> **0.86?**, MP5 0.70 ->
**0.87**, MP5SD 0.69 -> **0.87**, FAMAS 0.69 -> **0.88**, AKS74U 0.68 -> **0.89**, W1894 0.67 -> **0.90?**, FAL 0.67
-> **0.91**, SKS 0.66 -> **0.91**, SVD 0.66 -> **0.91**, THOMPSON 0.66 -> **0.91?**, MINI_14 0.65 -> **0.92**, AK74
0.65 -> **0.93**, W1873 0.64 -> **0.94?**, AK47 0.64 -> **0.94**, G3 0.64 -> **0.94**, STEVENS_555 0.64 -> **0.94?**,
W1873_CARBINE 0.64 -> **0.95?**, M79 0.63 -> **0.95**, M1903 0.63 -> **0.95**, ASVAL 0.63 -> **0.95**, FNC 0.63 ->
**0.96**, M1895 0.63 -> **0.96?**, MOSSBERG_590 (and MASTERKEY) 0.63 -> **0.96**, DOUBLEBARREL 0.60 -> **1.01?**,
M4A1 0.63 -> **0.96**, CAR15 (and CAR15_M203) 0.63 -> **0.96?**, REMINGTON_700 0.62 -> **0.97?**, M24 0.62 ->
**0.97**, G36C 0.62 -> **0.97**, TOZ34 0.61 -> **0.98**, M60 0.61 -> **0.98**, M14 0.61 -> **0.98**, G36 0.61 ->
**0.98**, AR15 0.61 -> **0.98**, MOSIN 0.61 -> **0.99**, M16A1 0.61 -> **0.99**, M16A2 / M16A3 / M16A2_M203
**1.00** (the anchor), SPAS12 / M1_GARAND / PSG1 0.60 -> **1.00**, MODEL_70 0.60 -> **1.00?**, TRENCHGUN 0.58 ->
**1.04**, AA12 0.58 -> **1.05**, BENELLI_M4 0.58 -> **1.05**, BAR 0.56 -> **1.07**, REMINGTON_870 0.55 -> **1.10?**,
W1887 0.53 -> **1.14?**, DOUBLE_DEUCE by eye.

SMGs held as pistols: MAC10 0.70 -> **0.87**, TEC9 0.69 -> **0.88**.

Pistols (these put them smaller than vanilla's own pistols, 0.70; say per pistol if one should stay larger):
DETECTIVE_38 0.87 -> **0.69** (a 2" snub drawn the size of a 4"), MP412 0.81 -> **0.75?**, COLT_SINGLE 0.74 ->
**0.82?**, RHINO 0.73 -> **0.82?**, HIPOWER 0.73 -> **0.83**, P226 0.72 -> **0.83**, GLOCK17 0.72 -> **0.84**, M93R
0.71 -> **0.85**, PYTHON 0.70 -> **0.86**, M1911 0.70 -> **0.86**, SW629 0.69 -> **0.87?**, M92FS 0.69 -> **0.88**,
USP 0.67 -> **0.90**, DEAGLE 0.64 -> **0.94**, VP70M 0.60 -> **1.01**.

Variants to check against a photo before trusting their scale: CAR-15 (14.5" assumed), XM177 (E2), Thompson (M1A1
813 mm vs 1928A1 852), Remington 870 (28" field assumed: 1.10; a 20" would be 0.91), W1887 (30" original assumed:
1.14; a 22" reproduction 0.93), W1894 (20" carbine), W1873 (24" rifle), W1873 Short Carbine (620 mm assumed), M1895,
Model 70, Remington 700, Stevens 555, Double Barrel, S&W 629 (8-3/8"), Rhino (6"), MP-412 (5"), Colt SAA (7.5").

## What else a resize touches

- Not scaled by the engine: the ballistic muzzle (bullet origin, tracer start: `BallisticsController` reads the raw
  `muzzle` offset, so it starts (1 - s) x muzzle y ahead of the drawn muzzle, 3.9 cm on the MP5A2 at 0.87;
  pre-scaling the offset would sink the flash into the barrel instead) and Hot Brass ejection offsets (relative to
  the player; GoM's `HotBrass/CustomParams.lua`).
- Parts take the gun's scale (sights, suppressors, bayonets, magazines, the muzzle flash). GoM sized its shared
  parts loosely anyway (ratio to real): M9 bayonet 0.54, K98 0.54, M5 0.57, M1905 0.60, M1 0.64, PSO-1 0.51, EXPS3
  0.38. Keeping a part's size on a resized gun would need a part model per gun at 1 / s (the gun's item script names
  the part model, `ModelWeaponPart`).
- Rifle-stance left hand (vanilla's palm sits 0.20-0.22 ahead of the grip, fixed): with these scales its distance to
  the gun's underside changes by under 3 mm, so no new clips.
- Reloads: the magazine well moves back (1 - s) x its y (MP5 at 0.87: 1.5 cm), cocking handles likewise (MP5
  ~3.1 cm): check every resized gun's reload and rack (vanilla's clips per reload type, GoM's bullpup, FAL rack,
  handgun2).
- Pistols on vanilla's handgun clips hold the grip only; scaling about the grip origin keeps the hand on it: check
  the fingers.
