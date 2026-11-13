---
name: generic-stances-not-per-gun
description: Guns of Tien ships no animations of its own; every gun uses vanilla's rifle / pistol hold and one of GoM's reload animIds
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7d0b58b2-5a09-4980-b00f-49411989b0ca
  modified: 2026-11-13T01:10:58.730Z
---

GoMExtensionGunsOfTien (and Post-93) ship no AnimSet nodes or clips (rule since 2026-10-29, CLAUDE.md "GoM's
animations only"). Every gun is held with vanilla's rifle or pistol clips, as GoM's guns are, and reloads with the
closest GoM animId through `shared/GunsOfTien/GoMReloads.lua`. GoM has **no bullpup stance**: its FAMAS is held on
vanilla's rifle clips and only has a bullpup reload, `famas_rifle` (used by the AUGs, PS90, MDRx, Groza). AR-pattern
guns use `ar15_rifle` (SR-25, Mk 11). Our own bullpup / compact stance sets of 2026-10-27/28 were dropped.

**Why:** (user, 2026-10-28/29) per-gun or own animation sets multiplied the work for every other mod that changes
animations and for us on each fix; "let's use EXISTING GOM ANIMATIONS please for our guns".

**How to apply:** fit a new gun to an existing GoM reload and vanilla's hold (model orientation and placement decide
the hold: pistol-held guns are modelled GoM's MP5K way and must not be TwoHandWeapon). Never propose a new stance or
reload animation. Related: [[follow-gom-patterns]], [[gun-sizes-from-m16]].
