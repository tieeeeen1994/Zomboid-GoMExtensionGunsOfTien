---
name: three-remodel-passes
description: "A gun model's first pass is always ugly; by default do SIX part-by-part remodel passes, and check every see-through region, shine and seat against the photo before showing it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: daae315a-aa23-4de8-813a-33c1e7bbacd0
  modified: 2026-11-25T03:29:55.177Z
---

The first modelling pass of a gun (Guns of Tien / Post-93) always comes out ugly. Never show or ship it. By default
make **six remodel-check passes** after the first build: render the model, then part by part put the
highest-resolution photo of that part next to the model's same part at 5x zoom or more (trigger guard and
triggers first, then sights, controls, muzzle, grip, stock) and the 3/4 renders beside the 3/4 photos; list what
is wrong, fix, render again. Only the result of the last pass goes to the user.

**Why:** user, 2026-11-25, on the overnight A-91M: "the first pass of modeling you make is always absolutely
disgusting. By default, make 3 passes of remodel checks to make it more beautiful and accurate." Three passes
judged from whole-gun renders were still rejected the same day: "it's still terrible. think we can increase
remodel pass? The triggers still look bad. The circle on trigger guard's front is not correct." The small
measuring photo had been read wrong: the launcher's loop trigger became a free-floating oval, the selector's steel
lever painted white lines, a raised cheek pad a recess.

**How to apply:** every new gun, variant or rework (the user may name another count for one gun: "3 passes" for
the 7.62-A91M, 2026-11-25). Read small parts off the largest photo of the gun family, not the measuring photo.
Check triggers and the guard first, every pass. The outline overlap score says nothing about looks. Put the
photo-over-model panels on the review sheet and note in the gun's CLAUDE.md section what each pass changed.

Three things the user caught on the launcher-over-the-barrel A-91M (now the A-91M Prototype) after its three passes (2026-11-25, each sent with a crop of a
render while the build was still running), to check on every gun before showing it:
- **Shine is not a hole.** "this trigger is bad. in your reference. it's just shine and NOT transparent": a bright
  wedge between the trigger guard's two edges had been built as a gap between two thin bars. A bright area bounded
  by a part's own edges is that polished part, solid.
- **No holes.** "I don't know why your models have holes": 1-3 px slits where bodies only met edge to edge. Bodies
  that meet must overlap.
- **Nothing floats.** "the launcher is floating which is not correct": where the photo is dark from a part down to
  what carries it, the part sits on it.
The check for all three: flood-fill the see-through regions of the photo-scale side render and compare each with
the photo's brightness there (`make_a91m_art.openings` in GoMExtensionGunsOfTien; my interpretation: use it or its
like for every gun). Related: [[gather-many-gun-references]], [[build-every-real-variant]].
