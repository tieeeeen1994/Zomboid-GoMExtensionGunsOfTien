"""
Brings the short SMG stance's arms to the set's level (arm_target 0.011) in shipped clips by swivelling the elbows,
frame-smoothed, with nothing else moved (Blender 5.2, headless; TienInspectWeapon's importer):

    blender -b --factory-startup -P scripts/anim/arm_swivel.py -- <vanilla anims_X/Bob> <mod anims_X/Bob> <work dir>
        <clip,...> [--write]

Written 2026-10-29 for the 12 clips the arms-at-vanilla's-level rebuild left at the old level (2.0-2.2 cm): there
the rebuild's per-frame elbow swing (Declip.arms, a pole push re-solved every frame) moved the gun or added jitter
(CLAUDE.md "Arms at vanilla's level"). Here each arm turns about its own shoulder-to-hand line (a swivel), so the
shoulder, the hand and its grip on the gun stay exactly where the shipped clip has them and only the elbow moves;
the wrist takes up the turn. Per frame the least swivel outward that brings the arm to ARM_TARGET (clearance.Body,
measured as compact_build does) is found in SWIVEL_STEP degrees; per arm the swivels are held and averaged over the
frames round the ones that need them (`spread`), never below a frame's own need, so the elbow moves out and back
without a pop. The forearm stays a pure hinge (its local keys are not touched: every vanilla clip and every clip
of the stance has zero forearm twist, the skin is weighted for the hand to take it, rig._place); a forearm roll tried
first twisted the elbow skin and flicked back on every blend into a neighbouring clip (the user: "twitching across
all your reworks"). The hand takes the swivel as twist. No wrist ends past max(WRIST_LIMIT, vanilla's own +
WRIST_OVER) or the shipped clip's worst (the Scorer's ratio, never worse than shipped): where the target needs more,
the swivel stops at that cap (`wrist_cap`, `capped`) and the arm stays a little deeper. Only the swivelled arm's
UpperArm and Hand keys change (the hand's world stays); the gun bone is not touched.

The clips are taken out of the ShortSMG packs, measured, swivelled, written to <work dir>/clips (before_ / after_
copies for stance_compare.py) with a report line each; --write splices the new AnimationSets into the packs in place
(every other clip byte for byte as it was).
"""

import math
import os
import re
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.environ.get("TIEN_ANIM") or os.path.join(ROOT, "..", "TienInspectWeapon", "scripts", "anim"))
sys.path.insert(0, HERE)
import clearance  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import x_import  # noqa: E402
import xanim  # noqa: E402

ARM_TARGET = 0.011          # compact_build.py SETS["Uzi"]["arm_target"]
SWIVEL_STEP = 1.0           # degrees
SWIVEL_MAX = float(os.environ.get("SWIVEL_MAX", "60"))
# compact_build.Scorer: a wrist past max(1.2, vanilla's + 0.2) counts against a clip
WRIST_LIMIT = float(os.environ.get("SWIVEL_WRIST_LIMIT", "1.2"))
WRIST_OVER = 0.2
SPREAD = 3                  # frames (compact_build.GENERIC_PUSH_SPREAD; see spread)
PREFIX = "GunsOfTien_CompactShortSMG_"
JERK_BONES = ("Bip01_L_Forearm", "Bip01_R_Forearm", "Bip01_L_Hand", "Bip01_R_Hand", "Bip01_Prop1")


def split(bob):
    """name -> (pack file, start, end, single-clip .x text) from the ShortSMG packs."""
    out = {}
    for fn in sorted(os.listdir(bob)):
        if not re.match(r"GunsOfTien_CompactShortSMG_Pack\d+\.x$", fn):
            continue
        text = open(os.path.join(bob, fn), encoding="latin-1", newline="").read()
        starts = [m.start() for m in re.finditer(r"^AnimationSet ", text, re.M)]
        head = text[:starts[0]]
        for i, s in enumerate(starts):
            e = starts[i + 1] if i + 1 < len(starts) else len(text)
            name = re.match(r"AnimationSet (\S+)", text[s:]).group(1)
            out[name] = (fn, s, e, head + text[s:e])
    return out


def frames_of(xa):
    step = xa.ticks_per_second // 30
    last = 0
    for tr in xa.tracks:
        for keys in (tr.R, tr.S, tr.T):
            if keys:
                last = max(last, max(keys))
    return step, [pose.from_clip(xa, f * step) for f in range(last // step + 1)]


def is_loop(xa, frames):
    a, b = pose.world(xa, frames[0]), pose.world(xa, frames[-1])
    return all((a[k].translation - b[k].translation).length < 1e-3
               for k in ("Bip01_Spine1", "Bip01_Prop1", "Bip01_R_Hand", "Bip01_L_Hand"))


def swivel(w, side, deg):
    """The arm's upper arm and forearm turned by deg about the shoulder-to-hand line: {bone: new world}."""
    ua, fa, ha = ("Bip01_%s_%s" % (side, b) for b in ("UpperArm", "Forearm", "Hand"))
    s, h = w[ua].translation, w[ha].translation
    rot = Quaternion((h - s).normalized(), math.radians(deg)).to_matrix().to_4x4()
    m = Matrix.Translation(s) @ rot @ Matrix.Translation(-s)
    return {ua: m @ w[ua], fa: m @ w[fa]}


class Probe:
    """Arm depth as clearance.Body measures it, the body built once per frame (a swivel moves no body vertex)."""

    def __init__(self, arm_ob):
        self.arm_ob = arm_ob
        self.body = clearance.Body(arm_ob)
        self.mw = arm_ob.matrix_world.copy()

    def frame(self, w):
        x_import.apply_pose(self.arm_ob, w)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ob = self.body.body
        ev = ob.evaluated_get(dg).to_mesh()
        verts = [ob.matrix_world @ v.co for v in ev.vertices]
        ob.evaluated_get(dg).to_mesh_clear()
        self.tree = BVHTree.FromPolygons(verts, self.body.polys)

    def depth(self, w, side, moved=None):
        moved = moved or {}

        def at(b):
            b = "Bip01_%s_%s" % (side, b)
            return self.mw @ (moved[b] if b in moved else w[b]).translation

        best = 0.0
        for a, b, t0, r in clearance.SEGMENTS:
            pa, pc = at(a), at(b)
            for k in range(9):
                best = max(best, clearance.sink(self.tree, pa.lerp(pc, t0 + (1 - t0) * k / 8.0), r))
        return best


def need(probe, w, side, sign):
    """The least swivel (degrees, sign's way) that brings the arm to ARM_TARGET, else the one that went deepest
    out (0 when nothing helps)."""
    d0 = probe.depth(w, side)
    if d0 <= ARM_TARGET:
        return 0.0, d0, d0
    best = (d0, 0.0)
    k = SWIVEL_STEP
    while k <= SWIVEL_MAX:
        d = probe.depth(w, side, swivel(w, side, sign * k))
        if d < best[0] - 0.0005:
            best = (d, k)
        if d <= ARM_TARGET:
            return k, d0, d
        k += SWIVEL_STEP
    return best[1], d0, best[0]


def spread(ks, loop):
    """Held SPREAD x 2 frames either side (a max filter), then averaged twice over SPREAD either side: never below
    a frame's own need (every value averaged into frame f holds a need from within 2 x SPREAD of f, f's own among
    them) and without the plateaus' corners, which a max hold plus a ramp left (jitter in the idles)."""
    n = len(ks)

    def idx(g):
        return g % n if loop else min(max(g, 0), n - 1)

    held = [max(ks[idx(g)] for g in range(f - 2 * SPREAD, f + 2 * SPREAD + 1)) for f in range(n)]
    for _ in range(2):
        held = [sum(held[idx(g)] for g in range(f - SPREAD, f + SPREAD + 1)) / (2.0 * SPREAD + 1) for f in range(n)]
    return [h if any(ks) else 0.0 for h in held]


def jerk(ws):
    best = 0.0
    for i in range(1, len(ws) - 1):
        for b in JERK_BONES:
            p = [(w["Bip01_Pelvis"].inverted() @ w[b]).translation for w in ws[i - 1:i + 2]]
            best = max(best, (p[0] - 2 * p[1] + p[2]).length)
    return best


def set_key(tr, tick, m):
    _, q, _ = xanim.mat4_to_srt([list(r) for r in m])
    tr.R[tick] = q


def fix_signs(tr):
    prev = None
    for t in sorted(tr.R):
        q = tr.R[t]
        if prev is not None and sum(a * b for a, b in zip(q, prev)) < 0:
            q = tuple(-c for c in q)
            tr.R[t] = q
        prev = q


def wrist_ratio(r, w, side, deg):
    """The hand's wrist after a swivel of deg, as compact_build's Scorer reads it: the largest of bend Y / 50,
    bend Z / 45, twist / 80 (1 = the edge of vanilla's range)."""
    fa, ha = "Bip01_%s_Forearm" % side, "Bip01_%s_Hand" % side
    fw = swivel(w, side, deg)[fa] if deg else w[fa]
    y, z, tw = r.wrist_angles({ha: fw.inverted() @ w[ha]}, side)
    return max(abs(y) / rig.WRIST_BEND[0], abs(z) / rig.WRIST_BEND[1], abs(tw) / rig.WRIST_TWIST)


def wrist_cap(r, w, side, sign, limit):
    """The largest swivel (degrees, from 0 the sign's way, at most SWIVEL_MAX) whose wrist stays within limit:
    stepped, then bisected to 0.05 degrees so the cap moves smoothly from frame to frame."""
    if wrist_ratio(r, w, side, 0.0) > limit:
        return 0.0
    lo = 0.0
    while lo + SWIVEL_STEP <= SWIVEL_MAX and wrist_ratio(r, w, side, sign * (lo + SWIVEL_STEP)) <= limit:
        lo += SWIVEL_STEP
    if lo + SWIVEL_STEP > SWIVEL_MAX:
        return lo
    hi = lo + SWIVEL_STEP
    while hi - lo > 0.05:
        mid = (lo + hi) / 2
        if wrist_ratio(r, w, side, sign * mid) <= limit:
            lo = mid
        else:
            hi = mid
    return lo


def vanilla_wrist(vanilla_bob, name, side):
    """The largest wrist ratio of vanilla's own clip (Bob_<clip>.x), 0 when it is not there."""
    path = os.path.join(vanilla_bob, "Bob_%s.x" % name[len(PREFIX):])
    if not os.path.exists(path):
        return 0.0
    xv = xanim.read(path, with_mesh=True)
    _, fv = frames_of(xv)
    rv = rig.Rig(xv, fv[0], rest=x_import.rest_matrices(xv))
    return max(max(abs(y) / rig.WRIST_BEND[0], abs(z) / rig.WRIST_BEND[1], abs(tw) / rig.WRIST_TWIST)
               for y, z, tw in (rv.wrist_angles(q, side) for q in fv))


def capped(ks, cap, loop):
    """spread(ks) kept under cap: held and averaged, then pressed under the cap and averaged again (three rounds),
    finally under the cap."""
    th = spread([min(k, c) for k, c in zip(ks, cap)], loop)
    n = len(th)

    def idx(g):
        return g % n if loop else min(max(g, 0), n - 1)

    for _ in range(3):
        th = [min(t, c) for t, c in zip(th, cap)]
        th = [sum(th[idx(g)] for g in range(f - SPREAD, f + SPREAD + 1)) / (2.0 * SPREAD + 1) for f in range(n)]
    return [min(t, c) for t, c in zip(th, cap)]


def process(name, text, work, vanilla_bob):
    src = os.path.join(work, "clips", "before_" + name + ".x")
    with open(src, "w", encoding="latin-1", newline="\n") as fh:
        fh.write(text.replace("\r\n", "\n"))
    xa = xanim.read(src, with_mesh=True)
    step, frames = frames_of(xa)
    loop = is_loop(xa, frames)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm_ob = x_import.load(src)
    probe = Probe(arm_ob)
    r = rig.Rig(xa, frames[0], rest=x_import.rest_matrices(xa))
    ws = [pose.world(xa, q) for q in frames]
    n = len(ws)
    plan, report = {}, []
    for side in "LR":
        trial = {1.0: [], -1.0: []}
        for f, w in enumerate(ws):
            probe.frame(w)
            for sign in (1.0, -1.0):
                trial[sign].append(need(probe, w, side, sign))
        # one way per arm for the whole clip: the way that reaches the target in more frames, then with less turning
        sign = min((1.0, -1.0), key=lambda s: (sum(1 for k, d0, d in trial[s] if d > ARM_TARGET),
                                                sum(k for k, d0, d in trial[s])))
        ks = [k for k, d0, d in trial[sign]]
        before = max(d0 for k, d0, d in trial[sign])
        if not any(ks):
            report.append((side, before, 0.0, 0, 0.0, 0.0))
            continue
        # the wrist may go no further than WRIST_LIMIT, vanilla's own + WRIST_OVER, or the shipped clip's worst wrist
        limit = max(WRIST_LIMIT, vanilla_wrist(vanilla_bob, name, side) + WRIST_OVER,
                    max(wrist_ratio(r, w, side, 0.0) for w in ws))
        cap = [wrist_cap(r, w, side, sign, limit) for w in ws]
        th = capped(ks, cap, loop)
        plan[side] = (sign, th)
        report.append((side, before, max(th), sum(1 for k in ks if k > 0), limit,
                       sum(1 for k, c in zip(ks, cap) if k > c)))
    tracks = {t.bone: t for t in xa.tracks}
    for f, w in enumerate(ws):
        for side, (sign, ks) in plan.items():
            ua, fa, ha, cl = ("Bip01_%s_%s" % (side, b) for b in ("UpperArm", "Forearm", "Hand", "Clavicle"))
            w2 = dict(w)
            w2.update(swivel(w, side, sign * ks[f]))
            set_key(tracks[ua], f * step, w2[cl].inverted() @ w2[ua])
            set_key(tracks[ha], f * step, w2[fa].inverted() @ w2[ha])
    for side in plan:
        for b in ("UpperArm", "Hand"):
            fix_signs(tracks["Bip01_%s_%s" % (side, b)])
    dst = os.path.join(work, "clips", "after_" + name + ".x")
    xanim.write_clip(src, dst, name, xa.tracks, xa.ticks_per_second)
    # measured again from the written file: depths, what moved, jitter
    xb = xanim.read(dst)
    _, fb = frames_of(xb)
    wb = [pose.world(xb, q) for q in fb]
    after = {"L": 0.0, "R": 0.0}
    moved, wrist = 0.0, 0.0
    for f, w in enumerate(wb):
        for side in "LR":
            ha, fa = "Bip01_%s_Hand" % side, "Bip01_%s_Forearm" % side
            a = (ws[f][fa].inverted() @ ws[f][ha]).to_quaternion()
            b = (w[fa].inverted() @ w[ha]).to_quaternion()
            turn = math.degrees(a.rotation_difference(b).angle)
            wrist = max(wrist, min(turn, 360.0 - turn))
        probe.frame(w)
        for side in "LR":
            after[side] = max(after[side], probe.depth(w, side))
        for b in ("Bip01_Prop1", "Bip01_L_Hand", "Bip01_R_Hand", "Bip01_L_UpperArm", "Bip01_R_UpperArm"):
            moved = max(moved, (w[b].translation - ws[f][b].translation).length)
    wr = max(wrist_ratio(r, w, side, 0.0) for w in wb for side in plan) if plan else 0.0
    wr0 = max(wrist_ratio(r, w, side, 0.0) for w in ws for side in plan) if plan else 0.0
    line = ("[swivel] %s (%d frames%s): %s; hands/gun/shoulders moved %.5f; wrist turned up to %.0f deg, "
            "worst %.2f -> %.2f; jerk %.2f -> %.2f cm") % (
        name[len(PREFIX):], n, ", loop" if loop else "",
        ", ".join("%s %.1f -> %.1f cm (swivel max %.0f deg, %d frames need it, wrist limit %.2f, %d frames held by it)"
                  % (s, b * 100, after[s] * 100, k, c, lim, held) for s, b, k, c, lim, held in report),
        moved, wrist, wr0, wr, jerk(ws) * 100, jerk(wb) * 100)
    print(line)
    return dst, line


def splice(bob, info, outputs):
    """Each pack rewritten with the new AnimationSets in place of the old (the rest of the file as it was)."""
    by_pack = {}
    for name, dst in outputs.items():
        fn, s, e, _ = info[name]
        new = open(dst, encoding="latin-1").read()
        new = new[re.search(r"^AnimationSet ", new, re.M).start():].rstrip() + "\n"
        by_pack.setdefault(fn, []).append((s, e, new))
    for fn, edits in by_pack.items():
        path = os.path.join(bob, fn)
        text = open(path, encoding="latin-1", newline="").read()
        for s, e, new in sorted(edits, reverse=True):
            old = text[s:e]
            tail = old[len(old.rstrip()):]          # keep the blank line(s) that separated it from the next set
            text = text[:s] + new.rstrip() + (tail or "\n") + text[e:]
        with open(path, "w", encoding="latin-1", newline="") as fh:
            fh.write(text)
        print("[swivel] wrote %s (%d clips)" % (fn, len(edits)))


def main(vanilla_bob, bob, work, names, write):
    os.makedirs(os.path.join(work, "clips"), exist_ok=True)
    info = split(bob)
    outputs, lines = {}, []
    for short in names:
        name = PREFIX + short
        if name not in info:
            raise SystemExit("no clip %s in the packs" % name)
        dst, line = process(name, info[name][3], work, vanilla_bob)
        outputs[name] = dst
        lines.append(line)
    with open(os.path.join(work, "report.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    if write:
        splice(bob, info, outputs)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    main(a[0], a[1], a[2], a[3].split(","), "--write" in a)
