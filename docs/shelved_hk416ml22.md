# Shelved: H&K USA's HK416 .22 LR M-LOK pistol (`HK416ML22`)

Shelved 2026-11-13. The user first wanted both HK416 .22 LR pistol generations ("WHY NOT BOTH???"), then, while the
two were being wired, chose only Walther's quad-rail one ("let's use walther's"). The second generation was modelled
for review and never wired; nothing of it ships.

**The gun**: Umarex's HK416 .22 LR Pistol for H&K USA, from 2019: 8.5" (217 mm) barrel, 425 mm, 2050 g without
magazine, an HK416 A5-style M-LOK handguard with a Mil-STD-1913 top rail, polymer flip-up sights (sight radius
304.6 mm), a 4-prong flash hider on a 1/2x28 thread. Decided for it before it was shelved: HK bronze, named "HK416 .22
M-LOK Pistol", Auto and Single as the Walther, no suppressor part, H&K's .22 magazines shared with the Walther.
References: `references/hk416_22/gen2/` (measuring photo `bing_037.jpg`, 3.66 px a mm).

**What exists**:
- `scripts/post93/build_hk416_22.py` still holds its code (`build_ml22`, `sights_ml22`, `remap_bronze`, `STATES["ML22"]`:
  sights up, `_RD` rear folded, `_FD` both folded, `_RDX` / `_FDX` rear off). Add `"ML22"` to `GENS` to build it again:
  it writes `GunsOfTienPost93_HK416ML22.fbx` and its points into `hk416_22_points.json`.
- `scripts/post93/make_hk416_22_art.py`: set `ML22 = True` for its texture `HK416ML22.png` (GoM's AR15 texture and
  the same in bronze side by side; faces with the `bronze` layer take the right half).
- The FBX and texture built on 2026-11-13 are in git at commit a0f0bc6.

**Open points when it was shelved**: the flip-up sights are plain blocks; lights and lasers sat straight on the
M-LOK handguard (its `light_left` / `laser_right` points), where the design wanted GoM's optional Picatinny side rails
drawn as short M-LOK sections (the Vector SDP's way: `rail_left` / `rail_right` points and rail nodes still to make);
GoM's AR muzzle parts were not decided (the real thread takes a .22 suppressor once the flash hider is off).
To finish it: the Walther's wiring (`gen_post93_guns.py hk416qr22()`, `shared/GunsOfTienPost93/HK416_22.lua`) is
the template, with IronSights' `_RDX` / `_FDX` rules measured again with fit_audit against the states.
