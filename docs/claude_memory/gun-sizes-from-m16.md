---
name: gun-sizes-from-m16
description: "Gun model sizes (Guns of Tien / GoM) are scaled against GoM's M16A2 (0.603 of real); the per-gun scales live in docs/gom_gun_scale.md on branch models-resize"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9a6c9565-0cfa-4c46-af61-3d32bf6dcdd6
  modified: 2026-10-27T03:00:48.258Z
---

When resizing guns (Guns of Tien, GoM's models), the anchor is GoM's M16A2 at 0.603 of its real length: scale = 0.603
/ the gun's ratio (drawn length / real overall length, stock extended); guns sharing a magazine share one group scale.
The finished per-gun table, method and side effects are in Guns of Tien's `docs/gom_gun_scale.md` (branch
`models-resize`, shelved 2026-10-26; TODO.md points to it). Read that first; never invent per-class targets or use
real lengths from memory.

**Why:** On 2026-10-27 I built a resize list from remembered lengths and my own 0.72 / 0.65 targets while the real
table already existed on another branch; the user had to point me to it.

**How to apply:** For any gun size question, check the current branch (`git branch`) and the doc before measuring
anything; if the doc is missing, ask which branch.
