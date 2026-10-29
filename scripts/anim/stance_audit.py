"""
Audits the short SMG packs against vanilla for the two faults the user saw on 2026-10-29 (Blender 5.2, headless):

    blender -b --factory-startup -P scripts/anim/stance_audit.py -- <vanilla anims_X/Bob> <vanilla AnimSets>
        <mod anims_X/Bob> <out.txt> [--depth] [clip,clip,...]

- snaps: a hand or the gun jumping relative to the chest (Bip01_Spine1) faster than vanilla's own does in that
  frame (FallLanding_Heavy_Rifle's left hand: 5.6 cm in one frame where vanilla's moved 0.9, "an insta move on the
  left arm"). A frame counts past SNAP_OVER cm beyond max(vanilla's step x SNAP_RATIO, vanilla's step + SNAP_PAD),
  unless the hand stays on the gun (under ON_GUN against it: a raise turns the gun fast, and our support hand sits
  further out on it than vanilla's, so it travels further with it).
- with --depth, hands in the body: the hand and wrist (clearance.SEGMENTS' forearm end and hand) against chest,
  belly and pelvis (clearance.BODY + Bip01_Pelvis; the arm audit measures the chest only, so a hand sinking into the
  belly of a seated pose was never seen), against vanilla's own deepest + DEPTH_PAD.

Every clip of the packs with a vanilla counterpart (Bob_<name>, the generic copies' __<context> suffix dropped) is
read; reloads have none and are skipped. Generic copies are judged as the game shows them (compact_build.masked over
the context's idle, ours over the stance's, vanilla's over vanilla's; shown_compare.py), never from the file.
One line per clip with a finding, worst first per kind.
"""

import os
import re
import sys

import bpy
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arm_swivel as AS  # noqa: E402  (puts TienInspectWeapon's scripts/anim on the path)
import compact_animsets as CA  # noqa: E402
import compact_build as CB  # noqa: E402
import clearance  # noqa: E402
import pose  # noqa: E402
import x_import  # noqa: E402
import xanim  # noqa: E402

SNAP_RATIO, SNAP_PAD, SNAP_OVER = 1.5, 1.0, 1.0       # cm
ON_GUN = 1.0                                          # cm a frame against the gun: still holding it
DEPTH_PAD = 1.0                                       # cm
TRACKED = ("Bip01_L_Hand", "Bip01_R_Hand", "Bip01_Prop1")
BELLY = clearance.BODY | {"Bip01_Pelvis"}


def rel_path(xa, frames):
    out = []
    for q in frames:
        w = pose.world(xa, q)
        s = w["Bip01_Spine1"].inverted()
        row = {b: (s @ w[b]).translation for b in TRACKED}
        g = w["Bip01_Prop1"].inverted()
        row.update({b + "@gun": (g @ w[b]).translation for b in TRACKED[:2]})
        out.append(row)
    return out


def snaps(ours, van):
    """[(excess cm, bone, frame, our step, vanilla's step)] past SNAP_OVER."""
    found = []
    n = min(len(ours), len(van))
    for b in TRACKED:
        for f in range(1, n):
            mine = (ours[f][b] - ours[f - 1][b]).length * 100
            theirs = (van[f][b] - van[f - 1][b]).length * 100
            excess = mine - max(theirs * SNAP_RATIO, theirs + SNAP_PAD)
            if b != "Bip01_Prop1" and (ours[f][b + "@gun"] - ours[f - 1][b + "@gun"]).length * 100 < ON_GUN:
                continue        # the hand rides the gun (a raise turning the gun fast): the gun's own move
            if excess > SNAP_OVER:
                found.append((excess, b[6:], f, mine, theirs))
    return sorted(found, reverse=True)


def hand_depths(path):
    """Per frame, per side: how deep the wrist and hand sink into chest + belly + pelvis (m)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm = x_import.load(path)
    body = clearance.Body(arm, BELLY)
    mw = arm.matrix_world
    end = int(arm.animation_data.action.frame_range[1])
    out = []
    for f in range(end + 1):
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ob = body.body
        ev = ob.evaluated_get(dg).to_mesh()
        tree = BVHTree.FromPolygons([ob.matrix_world @ v.co for v in ev.vertices], body.polys)
        ob.evaluated_get(dg).to_mesh_clear()
        pb = arm.pose.bones
        row = {}
        for side in "LR":
            fa, ha, fi = (mw @ pb["Bip01_%s_%s" % (side, b)].head for b in ("Forearm", "Hand", "Finger1"))
            pts = [(fa.lerp(ha, 0.5 + 0.5 * k / 4.0), 0.018) for k in range(5)]
            pts += [(ha.lerp(fi, k / 4.0), 0.014) for k in range(5)]
            row[side] = max(clearance.sink(tree, p, r) for p, r in pts)
        out.append(row)
    return out


def vanilla_name(name):
    return "Bob_" + re.sub(r"__\w+$", "", name[len(AS.PREFIX):])


def shown(frames, under, masks):
    return [CB.masked(under, q, masks) for q in frames] if masks else frames


def main(vanilla_bob, animsets, bob, out_path, depth, only):
    info = AS.split(bob)
    variants = CA.generic_variants(animsets)
    unders = {}

    def under(ctx, which):
        """The context's idle, frame 0: ours (from the packs) or vanilla's."""
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
    work = os.path.join(os.path.dirname(out_path) or ".", "_audit")
    os.makedirs(work, exist_ok=True)
    lines = []
    for name in sorted(info):
        short = name[len(AS.PREFIX):]
        if only and short not in only:
            continue
        vpath = os.path.join(vanilla_bob, vanilla_name(name) + ".x")
        if not os.path.exists(vpath):
            continue
        mine = os.path.join(work, "clip.x")
        with open(mine, "w", encoding="latin-1", newline="\n") as fh:
            fh.write(info[name][3].replace("\r\n", "\n"))
        xa, xv = xanim.read(mine), xanim.read(vpath)
        _, fa = AS.frames_of(xa)
        _, fv = AS.frames_of(xv)
        m = re.search(r"__(\w+)$", short)
        if m:
            sfx = "__" + m.group(1)
            row = next((v for v in variants.get(vanilla_name(name), []) if v[0] == sfx), None)
            if row is None:
                continue
            fa, fv = shown(fa, under(row[1], "ours"), row[2]), shown(fv, under(row[1], "van"), row[2])
        found = snaps(rel_path(xa, fa), rel_path(xv, fv))
        parts = []
        if found:
            parts.append("snaps: " + ", ".join("%s f%d %.1f cm (vanilla %.1f)" % (b, f, m, t)
                                               for e, b, f, m, t in found[:4]))
        if depth:
            dm, dv = hand_depths(mine), hand_depths(vpath)
            for side in "LR":
                worst = max(range(len(dm)), key=lambda f: dm[f][side])
                lim = max(r[side] for r in dv) * 100 + DEPTH_PAD
                if dm[worst][side] * 100 > lim:
                    parts.append("%s hand in body %.1f cm at f%d (vanilla's deepest %.1f)" % (
                        side, dm[worst][side] * 100, worst, lim - DEPTH_PAD))
        if parts:
            line = "%s: %s" % (short, "; ".join(parts))
            print("[audit] " + line)
            lines.append(line)
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("[audit] %d clips with findings" % len(lines))


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    flags = [x for x in a if x.startswith("--")]
    pos = [x for x in a if not x.startswith("--")]
    main(pos[0], pos[1], pos[2], pos[3], "--depth" in flags, set(pos[4].split(",")) if len(pos) > 4 else None)
