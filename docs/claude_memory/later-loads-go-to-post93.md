---
name: later-loads-go-to-post93
description: "Guns of Tien — a real load (or gun) that fails the main mod's pre-1993 rule, or has no date found, goes into the Post-93 add-on; never drop it for lack of a date"
metadata:
  node_type: memory
  type: feedback
  originSessionId: daae315a-aa23-4de8-813a-33c1e7bbacd0
  modified: 2026-11-25T06:21:37.114Z
---

When a round's special load (or anything else) cannot be shown to exist by 1993, build it in the Post-93 add-on
(GoMExtensionGunsOfTienPost93) instead of leaving it out. The main mod's "real loads of 1993" rule decides **where**
a thing goes, not **whether** it is made.

**Why:** user, 2026-11-25, after learning the 7.62x25 Tokarev got no hollow point because no pre-1993 date was
found: "Then include them in post 1993. What stopped you?" Built that day as
`GunsOfTienPost93.762x25_Bullet_HollowPoint` (Post-93 appends a load to a main-mod calibre's Gunworks family, as
it already did with the 5.7x28 SB193 / SS197SR).

**How to apply:** when planning a calibre's loads, list the later ones too and put them in Post-93 in the same
release, or say plainly they are deferred and why. Open case: the 9x18 Makarov's later loads (PMM 1994 and the
others) were noted as "Post-93 material, with the PP-9 Klin" and not built.
