---
name: follow-gom-patterns
description: "Guns of Tien follows Guns of Marz's patterns, ideology and culture; use Gunworks' public API, never wrap it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e336b3df-8c13-41ce-b1e7-549282a2da3d
  modified: 2026-11-04T00:59:59.558Z
---

Guns of Tien does things the way Guns of Marz (GoM) does: same Gunworks API calls, same registration shapes (e.g. a
shared animated-parts entry like GoM's `Bolt_AR15`, with a `reload` table for parts that move only when racked).

**Why:** user, 2026-11-04: "We follow GoM patterns and ideology and culture." Came right after our wrap of Gunworks'
`Animations.CallAnimationFunction` dropped its new `route` argument and broke GoM's AR-15 handles and revolver
cylinders (Marz complained).

**How to apply:** before building a gun feature, look for how GoM does the same thing in its `Registries/` and use
Gunworks' public registration functions. Don't wrap Gunworks or GoM functions when an API exists; if a wrap is
unavoidable, pass `...` through. Related: [[generic-stances-not-per-gun]].
