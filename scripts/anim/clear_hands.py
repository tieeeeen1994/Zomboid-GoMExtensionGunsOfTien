"""
Keeps the short SMG's hands from sinking into the belly where a clip bends the body onto the gun (Blender 5.2,
headless; user, 2026-10-29: "Emote_Shiver_Sat_Rifle has this thing where by the near end, the wrists go inside the
body... why?"):

    blender -b --factory-startup -P scripts/anim/clear_hands.py -- <mod anims_X/Bob> <work dir> <clip,... | all>
        [--write]

Why: the stance holds the gun rigid with the chest, low in front of the belly. When vanilla's body straightens or
bends at the waist under it (the sitting shiver's last second: the chest comes upright over the hips), a point held
low in front of the chest swings back and down into the belly and lap, and the hands on the gun with it (the
sitting shiver's left wrist 1.9 cm deep most of the clip, 3.4 at frames 81-87). The build's arm audit measures
the chest only (clearance.BODY), so it never saw it.

Each clip's hands are measured per frame against chest + belly + pelvis (stance_audit.hand_depths' points); frames
where a hand holding the gun sinks more than RISE cm past the clip's own median get the gun moved out of the body:
one direction per clip (the mean way out of the hand points inside, in the chest's frame), per frame the least
distance along it (bisected) that brings the hands back to median + RISE / 2, held and averaged over the frames
round them as arm_swivel.spread does (never below a frame's need). The gun moves by that, every hand on the gun
(stance_audit's ON_GUN test against the frames round it) is solved onto its own relation to the moved gun with its
own elbow (rig._place, forearm a hinge), and each frame keeps the clip's own difference from the convention's
solution of its unmoved pose, so a frame with no move is exactly the clip's. Own clips only: a generic copy's gun is
the state underneath's.
"""

import os
import re
import statistics
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arm_swivel as AS  # noqa: E402  (puts TienInspectWeapon's scripts/anim on the path)
import clearance  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import smooth_snaps as SS  # noqa: E402
import stance_audit as AU  # noqa: E402
import x_import  # noqa: E402
import xanim  # noqa: E402

RISE = 1.0          # cm past the clip's median depth that counts as sinking
IN_BODY = 2.5       # cm: shallower is a wrist resting on the skin (the forearm's radius is 1.8), never moved for
MAX_MOVE = 0.12     # m
GUN = "Bip01_Prop1"


class Belly:
    def __init__(self, arm_ob):
        self.arm_ob = arm_ob
        self.body = clearance.Body(arm_ob, AU.BELLY)
        self.mw = arm_ob.matrix_world.copy()

    def frame(self, w):
        x_import.apply_pose(self.arm_ob, w)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ob = self.body.body
        ev = ob.evaluated_get(dg).to_mesh()
        self.tree = BVHTree.FromPolygons([ob.matrix_world @ v.co for v in ev.vertices], self.body.polys)
        ob.evaluated_get(dg).to_mesh_clear()

    def points(self, w, side, shift=Vector()):
        """The wrist and hand points (stance_audit.hand_depths) in Blender's world, the hand moved by shift (file
        space world)."""
        fa, ha, fi = (w["Bip01_%s_%s" % (side, b)].translation for b in ("Forearm", "Hand", "Finger1"))
        pts = [(fa.lerp(ha, 0.5 + 0.5 * k / 4.0) + shift * (0.5 + 0.5 * k / 4.0), 0.018) for k in range(5)]
        pts += [(ha.lerp(fi, k / 4.0) + shift, 0.014) for k in range(5)]
        return [(self.mw @ p, r) for p, r in pts]

    def depth(self, w, side, shift=Vector()):
        return max(clearance.sink(self.tree, p, r) for p, r in self.points(w, side, shift))

    def way_out(self, w, side):
        """Mean (nearest face - point) over the points inside, in file space (Blender's world back through the
        object matrix, its own inverse)."""
        acc = Vector()
        for p, r in self.points(w, side):
            if clearance.inside(self.tree, p):
                near = self.tree.find_nearest(p)[0]
                acc += near - p
        return self.mw.to_3x3().inverted() @ acc


def on_gun(ws, side, f):
    H = rig.ARM[side][2]
    rng = [g for g in range(f - 2, f + 3) if 0 <= g < len(ws)]
    rel = [(ws[g][GUN].inverted() @ ws[g][H]).translation for g in rng]
    return max((rel[i + 1] - rel[i]).length for i in range(len(rel) - 1)) * 100 < AU.ON_GUN


def moved_pose(r, xa, q, w, shift, follow, deltas):
    """q with the gun moved by shift (file space world) and each hand moved by shift x its weight in follow (1 =
    holding the gun) and solved there, each arm bone then carrying the frame's own delta from the convention."""
    q = pose.copy(q)
    parent = r.parent[GUN]
    g = Matrix.Translation(shift) @ w[GUN]
    q[GUN] = w[parent].inverted() @ g
    for side, k in follow.items():
        H = rig.ARM[side][2]
        SS.ik(r, q, pose.world(xa, q), side, Matrix.Translation(shift * k) @ w[H], SS.elbow_dir(w, side))
        for bone in rig.ARM[side]:
            m = q[bone]
            q[bone] = Matrix.LocRotScale(m.translation, (m.to_quaternion() @ deltas[bone]).normalized(), None)
    return q


def process(name, text, work):
    src = os.path.join(work, "clips", "before_" + name + ".x")
    with open(src, "w", encoding="latin-1", newline="\n") as fh:
        fh.write(text.replace("\r\n", "\n"))
    xa = xanim.read(src, with_mesh=True)
    step, frames = AS.frames_of(xa)
    n = len(frames)
    loop = AS.is_loop(xa, frames)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm_ob = x_import.load(src)
    probe = Belly(arm_ob)
    r = rig.Rig(xa, frames[0], rest=x_import.rest_matrices(xa))
    ws = [pose.world(xa, q) for q in frames]
    depth = {"L": [], "R": []}
    ways = Vector()
    held = [[s for s in "LR" if on_gun(ws, s, f)] for f in range(n)]
    for f, w in enumerate(ws):
        probe.frame(w)
        for s in "LR":
            depth[s].append(probe.depth(w, s) * 100)
    # whether the left hand rides the gun, smoothed over the frames round it so it never follows the gun in one
    # frame and not the next (a held / let go flag per frame made the arm jump)
    on = [1.0 if "L" in held[f] else 0.0 for f in range(n)]
    left_on = on
    for _ in range(3):
        left_on = [sum(left_on[min(max(g, 0), n - 1) if not loop else g % n] for g in range(f - 3, f + 4)) / 7.0
                   for f in range(n)]
    limit = {s: max(statistics.median(depth[s]) + RISE, IN_BODY) for s in "LR"}
    goal = {s: max(statistics.median(depth[s]) + RISE / 2, IN_BODY - 0.5) for s in "LR"}
    bad = [f for f in range(n) if any(depth[s][f] > limit[s] and s in held[f] for s in "LR")]
    if not bad:
        return None, None
    for f in bad:
        probe.frame(ws[f])
        for s in held[f]:
            ways += ws[f]["Bip01_Spine1"].to_3x3().inverted() @ probe.way_out(ws[f], s)
    if ways.length < 1e-9:
        return None, None
    way = ways.normalized()                      # in the chest's frame
    need = [0.0] * n
    for f in range(n):
        sides = [s for s in held[f] if depth[s][f] > goal[s]]
        if f not in bad and not any(depth[s][f] > limit[s] for s in sides):
            continue
        probe.frame(ws[f])
        dirw = ws[f]["Bip01_Spine1"].to_3x3() @ way
        lo, hi = 0.0, MAX_MOVE
        if any(probe.depth(ws[f], s, dirw * hi) * 100 > goal[s] for s in sides):
            need[f] = hi
            continue
        for _ in range(12):
            mid = (lo + hi) / 2
            if any(probe.depth(ws[f], s, dirw * mid) * 100 > goal[s] for s in sides):
                lo = mid
            else:
                hi = mid
        need[f] = hi
    amount = AS.spread(need, loop)
    # each frame's own difference from the convention's solution of its unmoved pose
    tracks = {t.bone: t for t in xa.tracks}
    out = []
    for f, (q, w) in enumerate(zip(frames, ws)):
        if amount[f] <= 1e-6:
            out.append(q)
            continue
        follow = {"R": 1.0, "L": left_on[f]}       # the right hand always holds the gun
        base = moved_pose(r, xa, q, w, Vector(), follow, {b: Quaternion() for s in "LR" for b in rig.ARM[s]})
        deltas = {b: SS.rot_delta(base[b], q[b]) for s in "LR" for b in rig.ARM[s]}
        shift = ws[f]["Bip01_Spine1"].to_3x3() @ way * amount[f]
        out.append(moved_pose(r, xa, q, w, shift, follow, deltas))
    touched = [GUN] + list(rig.ARM["L"]) + list(rig.ARM["R"])
    for f in range(n):
        if amount[f] <= 1e-6:
            continue
        for bn in touched:
            sc, qq, t = xanim.mat4_to_srt([list(row) for row in out[f][bn]])
            tr = tracks[bn]
            tr.R[f * step], tr.T[f * step] = qq, t
            if tr.S:
                tr.S[f * step] = sc
    for bn in touched:
        AS.fix_signs(tracks[bn])
    dst = os.path.join(work, "clips", "after_" + name + ".x")
    xanim.write_clip(src, dst, name, xa.tracks, xa.ticks_per_second)
    # measured again
    xb = xanim.read(dst)
    _, fb = AS.frames_of(xb)
    after = {"L": [], "R": []}
    for q in fb:
        w = pose.world(xb, q)
        probe.frame(w)
        for s in "LR":
            after[s].append(probe.depth(w, s) * 100)
    line = "[clear] %s: %d frames sinking (limit L %.1f R %.1f); gun moved up to %.1f cm over %d frames; " \
           "deepest L %.1f -> %.1f, R %.1f -> %.1f; jerk %.2f -> %.2f cm" % (
               name[len(AS.PREFIX):], len(bad), limit["L"], limit["R"], max(amount) * 100,
               sum(1 for a in amount if a > 1e-6), max(depth["L"]), max(after["L"]), max(depth["R"]),
               max(after["R"]), AS.jerk(ws) * 100, AS.jerk([pose.world(xb, q) for q in fb]) * 100)
    print(line)
    return dst, line


def main(bob, work, names, write):
    os.makedirs(os.path.join(work, "clips"), exist_ok=True)
    info = AS.split(bob)
    outputs, lines = {}, []
    for name in sorted(info):
        short = name[len(AS.PREFIX):]
        if names != ["all"] and short not in names:
            continue
        if re.search(r"__\w+$", short) or "_Reload" in short:
            continue
        dst, line = process(name, info[name][3], work)
        if dst:
            outputs[name] = dst
            lines.append(line)
    with open(os.path.join(work, "report.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    if write and outputs:
        AS.splice(bob, info, outputs)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    main(a[0], a[1], a[2].split(","), "--write" in a)
