"""
Smooths the snaps stance_audit.py finds in the short SMG packs (Blender 5.2, headless; user, 2026-10-29:
"FallLanding_Heavy_Rifle has an insta move on the left arm to the proper position.... smoothen this please", then
"check for other animations that has a similar effect and fix them"):

    blender -b --factory-startup -P scripts/anim/smooth_snaps.py -- <vanilla anims_X/Bob> <vanilla AnimSets>
        <mod anims_X/Bob> <work dir> <clip,clip,... | all> [--write]

A snap is a hand or the gun jumping relative to the chest much faster than vanilla's own does in that frame
(stance_audit.snaps). The builds switch the left hand between vanilla's free arm and its place on the gun by a weight
that can rise in two or three frames (compact_build left_on), and the generic copies' shown arm can jump the same
way; FallLanding_Heavy_Rifle's left hand moved 5.6 and 5.2 cm in two frames where vanilla's moved 1.

Each cluster of snapping frames c0..c1 gets a window [a, b] long enough to spread its jump (the bone's travel
relative to the chest over those frames) at about WINDOW_SPEED cm a frame (at least MIN_WINDOW, widened on a later
pass), and over it the jump is taken out of the motion and put back spread by a smootherstep (`layered`): every
other step of the clip's own motion is kept (a gesture stays a gesture; an earlier try that blended between the ends'
attachments froze a wipe emote's whole left arm), and a and b are unchanged.
- a hand: its place and turn relative to the chest, its elbow direction and its fingers layered so; the arm solved
  onto it with rig._place (forearm a pure hinge, the hand taking the twist) keeping each frame's own difference from
  that solution (`arm_deltas`, so an unmoved frame is exactly the clip's).
- the gun (and the hands holding it): its place relative to the chest layered so, each hand kept in its relation
  to the gun with its own elbow and roll. Not for generic copies (their gun is the state underneath's).
Generic copies are fixed as the game shows them (compact_build.masked over the context's idle) and written back
through compact_build.unmask. Up to PASSES passes per clip, a window widened where a snap is left. Every changed
clip is reported (snaps before / after, the arms' and hands' depth before / after); --write splices them into the
packs (arm_swivel.splice), every other clip byte for byte as it was.
"""

import math
import os
import re
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arm_swivel as AS  # noqa: E402  (puts TienInspectWeapon's scripts/anim on the path)
import compact_animsets as CA  # noqa: E402
import compact_build as CB  # noqa: E402
import stance_audit as AU  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import x_import  # noqa: E402
import xanim  # noqa: E402

WINDOW_SPEED = 1.5      # cm a frame the blend may add at its fastest
MIN_WINDOW = 8          # frames
PASSES = 4
CHEST, GUN = "Bip01_Spine1", "Bip01_Prop1"


def smootherstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)


def blend_m(a, b, t):
    qa, qb = a.to_quaternion(), b.to_quaternion()
    if qa.dot(qb) < 0:
        qb.negate()
    return Matrix.LocRotScale(a.translation.lerp(b.translation, t), qa.slerp(qb, t), None)


def rot_delta(a, b):
    """The local rotation taking a to b (a @ d = b), as a quaternion."""
    return (a.to_quaternion().inverted() @ b.to_quaternion()).normalized()


def descendants(xa, bone):
    kids = {}
    for f in x_import.bone_frames(xa):
        kids.setdefault(f.parent, []).append(f.name)
    out, todo = [], list(kids.get(bone, []))
    while todo:
        b = todo.pop()
        out.append(b)
        todo += kids.get(b, [])
    return out


def clusters(found, bone, gap=3):
    frames = sorted({f for e, b, f, m, t in found if b == bone})
    out = []
    for f in frames:
        if out and f - out[-1][1] <= gap:
            out[-1][1] = f
        else:
            out.append([f, f])
    return out


def ik(r, p, w, side, target, pole_dir):
    """rig._place onto target with the elbow toward pole_dir (world), arm lengths from the pose."""
    U, F, H = rig.ARM[side]
    S = w[U].translation
    l1, l2 = p[F].translation.length, p[H].translation.length
    T = target.translation
    d = (T - S).length
    dirv = (T - S) / d
    d = min(d, (l1 + l2) * 0.999)
    d = max(d, abs(l1 - l2) + 1e-3)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    n = pole_dir - dirv * pole_dir.dot(dirv)
    if n.length < 1e-6:
        n = rig.FWD.cross(dirv)
    r._place(p, w, side, target, S, dirv, d, a, h, n.normalized())


def elbow_dir(w, side):
    U, F, H = rig.ARM[side]
    return w[F].translation - w[U].translation


def layered(mats, c0, c1, a, b):
    """mats[f] (one bone in some frame of reference) with the jump of frames c0..c1 taken out and put back spread
    over [a, b] by a smootherstep. The jump is what those frames' steps add over the motion around them (each step
    less the step blended from the one before c0 to the one after c1), so the clip keeps moving through them as it
    did around them; every other step is kept, and a and b are unchanged. {f: corrected matrix} for f in [a, b]."""
    n = len(mats)

    def step(f):
        f = max(1, min(n - 1, f))
        return mats[f].translation - mats[f - 1].translation, rot_delta(mats[f - 1], mats[f])

    (p0, q0), (p1, q1) = step(c0 - 1), step(c1 + 1)
    jp, jq = Vector(), Quaternion()
    cum = {}
    for f in range(a, b + 1):
        if c0 <= f <= c1 and f > 0:
            t = (f - c0 + 1) / float(c1 - c0 + 2)
            sp, sq = step(f)
            bq = q0.slerp(q1 if q0.dot(q1) >= 0 else -q1, t)
            jp = jp + sp - p0.lerp(p1, t)
            jq = jq @ (bq.inverted() @ sq)
        cum[f] = (jp.copy(), jq.copy())
    total_p, total_q = jp, jq
    out = {}
    for f in range(a, b + 1):
        s = smootherstep((f - a) / float(b - a))
        cp, cq = cum[f]
        m = mats[f]
        q = m.to_quaternion() @ cq.inverted() @ Quaternion().slerp(total_q, s)
        out[f] = Matrix.LocRotScale(m.translation - cp + total_p * s, q.normalized(), None)
    return out


def arm_deltas(r, xa, q, w, side):
    """The pose's own difference from rig._place's solution of its own hand and elbow (per arm bone, a local
    rotation), so a solve onto a moved target keeps the clip's roll and an unmoved one gives the clip back."""
    base = pose.copy(q)
    ik(r, base, w, side, w[rig.ARM[side][2]], elbow_dir(w, side))
    return {b: rot_delta(base[b], q[b]) for b in rig.ARM[side]}


def solve_with(r, xa, q, side, target, pole, deltas):
    ik(r, q, pose.world(xa, q), side, target, pole)
    for bone, d in deltas.items():
        m = q[bone]
        q[bone] = Matrix.LocRotScale(m.translation, (m.to_quaternion() @ d).normalized(), None)


def fix_hand(r, xa, poses, side, a, b, c0, c1, fingers):
    """The side's hand jump (frames c0..c1, relative to the chest) spread over [a, b] (see `layered`), its elbow
    direction and fingers the same way; the arm solved onto it keeping each frame's own roll (arm_deltas)."""
    U, F, H = rig.ARM[side]
    ws = [pose.world(xa, q) for q in poses]
    rel = [w[CHEST].inverted() @ w[H] for w in ws]
    elb = [Matrix.Translation(w[CHEST].to_3x3().inverted() @ elbow_dir(w, side)) for w in ws]
    hand = layered(rel, c0, c1, a, b)
    elbow = layered(elb, c0, c1, a, b)
    fing = {fb: layered([q[fb] for q in poses], c0, c1, a, b) for fb in fingers if fb in poses[a]}
    out = [pose.copy(q) for q in poses]
    for f in range(a + 1, b):
        q, w = out[f], ws[f]
        deltas = arm_deltas(r, xa, poses[f], w, side)
        solve_with(r, xa, q, side, w[CHEST] @ hand[f], w[CHEST].to_3x3() @ elbow[f].translation, deltas)
        for fb, ms in fing.items():
            q[fb] = Matrix.LocRotScale(poses[f][fb].translation, ms[f].to_quaternion(), None)
    return out


def fix_gun(r, xa, poses, a, b, c0, c1):
    """The gun's jump relative to the chest (frames c0..c1) spread over [a, b], each hand kept in its own relation
    to the gun with its own elbow and roll."""
    ws = [pose.world(xa, q) for q in poses]
    rel = [w[CHEST].inverted() @ w[GUN] for w in ws]
    gun = layered(rel, c0, c1, a, b)
    parent = r.parent[GUN]
    out = [pose.copy(q) for q in poses]
    for f in range(a + 1, b):
        q, w = out[f], ws[f]
        g = w[CHEST] @ gun[f]
        q[GUN] = w[parent].inverted() @ g
        for side in "LR":
            H = rig.ARM[side][2]
            deltas = arm_deltas(r, xa, poses[f], w, side)
            solve_with(r, xa, q, side, g @ (w[GUN].inverted() @ w[H]), elbow_dir(w, side), deltas)
    return out


def window(found, bone, c0, c1, n, gap_cm, gap_deg, widen=1.0):
    """[a, b] round the cluster c0..c1, long enough for the gap at WINDOW_SPEED (x widen on a later pass)."""
    need = max(MIN_WINDOW, int(math.ceil(1.875 * gap_cm / WINDOW_SPEED)), int(math.ceil(1.875 * gap_deg / 10.0)))
    need = int(math.ceil(need * widen))
    a, b = c0 - 1, c1
    while b - a < need:
        if a > 0:
            a -= 1
        if b - a < need and b < n - 1:
            b += 1
        if a == 0 and b == n - 1:
            break
    return a, b


def jump(xa, poses, bone, c0, c1):
    """How far the bone travels relative to the chest over the steps of frames c0..c1: (cm, degrees)."""
    rel = [pose.world(xa, poses[f]) for f in (max(c0 - 1, 0), c1)]
    m0, m1 = (w[CHEST].inverted() @ w[bone] for w in rel)
    ang = math.degrees(m0.to_quaternion().rotation_difference(m1.to_quaternion()).angle)
    return (m1.translation - m0.translation).length * 100, min(ang, 360 - ang)


def process(name, text, van_rel, masks, under, work):
    src = os.path.join(work, "clips", "before_" + name + ".x")
    with open(src, "w", encoding="latin-1", newline="\n") as fh:
        fh.write(text.replace("\r\n", "\n"))
    xa = xanim.read(src, with_mesh=True)
    step, raw = AS.frames_of(xa)
    n = len(raw)
    loop = AS.is_loop(xa, raw)
    shown = AU.shown(raw, under, masks)
    r = rig.Rig(xa, raw[0], rest=x_import.rest_matrices(xa))
    poses = [pose.copy(q) for q in shown]
    first = AU.snaps(AU.rel_path(xa, poses), van_rel)
    if not first:
        return None, None
    windows = []
    best = (sum(e for e, *_ in first), poses, [])
    for pas in range(PASSES):
        found = AU.snaps(AU.rel_path(xa, poses), van_rel)
        score = sum(e for e, *_ in found)
        if score < best[0]:
            best = (score, poses, list(windows))
        if not found:
            break
        done = False
        gun_frames = {f for e, b, f, m, t in found if b == "Prop1"}
        if gun_frames and not masks:
            for c0, c1 in clusters(found, "Prop1"):
                g = jump(xa, poses, GUN, c0, c1)
                a, b = window(found, "Prop1", c0, c1, n, *g, widen=1.6 ** pas)
                poses = fix_gun(r, xa, poses, a, b, c0, c1)
                windows.append(("gun", a, b))
                done = True
        for side in "LR":
            H = rig.ARM[side][2]
            if masks and any(masks.get(bn, 0.0) <= 1e-3 for bn in rig.ARM[side]):
                continue
            for c0, c1 in clusters(found, H[6:]):
                if any(c0 - 1 <= f <= c1 for f in gun_frames):
                    continue            # moved with the gun: the gun's fix carries the hand
                g = jump(xa, poses, H, c0, c1)
                a, b = window(found, H[6:], c0, c1, n, *g, widen=1.6 ** pas)
                if b - a < 2:
                    continue
                poses = fix_hand(r, xa, poses, side, a, b, c0, c1, descendants(xa, H))
                windows.append((side, a, b))
                done = True
        if not done:
            break
    found = AU.snaps(AU.rel_path(xa, poses), van_rel)
    if sum(e for e, *_ in found) < best[0]:
        best = (0, poses, list(windows))
    _, poses, windows = best             # the pass that left the least (a wider window can make it worse)
    if not windows:
        return None, None
    after = AU.snaps(AU.rel_path(xa, poses), van_rel)
    # back to the file: generic copies through unmask, only bones the fix touched
    touched = set()
    for kind, a, b in windows:
        bones = [GUN] + list(rig.ARM["L"]) + list(rig.ARM["R"]) if kind == "gun" else \
            list(rig.ARM[kind]) + descendants(xa, rig.ARM[kind][2])
        touched.update(bones)
    tracks = {t.bone: t for t in xa.tracks}
    for f in range(n):
        for bn in touched:
            if bn not in tracks or bn not in raw[f] or bn not in poses[f]:
                continue        # end nubs: no keys
            want = poses[f][bn]
            if masks:
                wgt = masks.get(bn, 0.0)
                if wgt <= 1e-3:
                    continue
                want = CB.unmask(under[bn], want, wgt)
            if (want.to_quaternion().rotation_difference(raw[f][bn].to_quaternion()).angle < 1e-7 and
                    (want.translation - raw[f][bn].translation).length < 1e-9):
                continue
            sc, q, t = xanim.mat4_to_srt([list(row) for row in want])
            tr = tracks[bn]
            tr.R[f * step], tr.T[f * step] = q, t
            if not tr.S:
                continue
            tr.S[f * step] = sc
    for bn in touched:
        if bn in tracks:
            AS.fix_signs(tracks[bn])
    dst = os.path.join(work, "clips", "after_" + name + ".x")
    xanim.write_clip(src, dst, name, xa.tracks, xa.ticks_per_second)
    line = "[snaps] %s: %s -> %s; windows %s" % (
        name[len(AS.PREFIX):], describe(first), describe(after) or "none",
        ", ".join("%s %d-%d" % w for w in windows))
    print(line)
    return dst, line


def describe(found):
    return ", ".join("%s f%d %.1f (vanilla %.1f)" % (b, f, m, t) for e, b, f, m, t in found[:3])


def main(vanilla_bob, animsets, bob, work, names, write):
    os.makedirs(os.path.join(work, "clips"), exist_ok=True)
    info = AS.split(bob)
    variants = CA.generic_variants(animsets)
    unders = {}

    def under(ctx, which):
        key = (ctx, which)
        if key not in unders:
            clip = CB.UNDERLYING[ctx]
            if which == "van":
                path = os.path.join(vanilla_bob, clip + ".x")
            else:
                path = os.path.join(work, "under_%s.x" % ctx)
                with open(path, "w", encoding="latin-1", newline="\n") as fh:
                    fh.write(info[AS.PREFIX + clip[4:]][3].replace("\r\n", "\n"))
            unders[key] = AS.frames_of(xanim.read(path))[1][0]
        return unders[key]

    outputs, lines = {}, []
    for name in sorted(info):
        short = name[len(AS.PREFIX):]
        if names != ["all"] and short not in names:
            continue
        vpath = os.path.join(vanilla_bob, AU.vanilla_name(name) + ".x")
        if not os.path.exists(vpath):
            continue
        xv = xanim.read(vpath)
        _, fv = AS.frames_of(xv)
        masks, qu = None, None
        m = re.search(r"__(\w+)$", short)
        if m:
            row = next((v for v in variants.get(AU.vanilla_name(name), []) if v[0] == "__" + m.group(1)), None)
            if row is None:
                continue
            masks, qu = row[2], under(row[1], "ours")
            fv = AU.shown(fv, under(row[1], "van"), masks)
        dst, line = process(name, info[name][3], AU.rel_path(xv, fv), masks, qu, work)
        if dst:
            outputs[name] = dst
            lines.append(line)
    with open(os.path.join(work, "report.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    if write and outputs:
        AS.splice(bob, info, outputs)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    main(a[0], a[1], a[2], a[3], a[4].split(","), "--write" in a)
