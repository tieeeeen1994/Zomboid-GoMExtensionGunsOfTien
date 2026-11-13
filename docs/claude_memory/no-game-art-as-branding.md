---
name: no-game-art-as-branding
description: "Guns of Tien box/brand art must be original (like GoM's made-up brands with fierce mascots), never Project Zomboid's own UI/map symbols"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e728cb42-9f27-42ad-9f0e-899967fb6098
  modified: 2026-11-13T02:59:24.215Z
---

For Guns of Tien ammo boxes and similar branding, never reuse Project Zomboid's own UI art (map symbols such as
`media/ui/LootableMaps/map_bird.png`, moodles, sidebar icons) as a logo or mascot. Make original art in GoM's manner:
a made-up ammo maker with a fierce animal mascot (GoM: "Viper Strike Munitions" snake, "White Cat Precision",
"Blue Jay"), plus the gun that fires the round.

**Why:** user, 2026-11-13, after a vanilla bird map symbol was put on the 5.7x28 boxes: "Don't use zomboid stuff...
use animals that are fierce like how an ammo would brand itself... like how gom does it".

**How to apply:** draw mascots ourselves (the 5.7x28 "IRON WASP" wasp is PIL primitives in
`scripts/post93/make_ammo_art.py` `draw_wasp()`), pick fierce animals, give the maker a name. Renders of our own gun
models are fine. Related: [[follow-gom-patterns]].
