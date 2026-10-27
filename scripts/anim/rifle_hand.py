"""
Vanilla's rifle clips with the left hand moved back along the gun, for a rifle-held gun drawn smaller than the rifle
those clips were made for (Blender 5.2, headless; TienInspectWeapon's rig).

    blender -b --factory-startup -P scripts/anim/rifle_hand.py -- <vanilla anims_X/Bob> <vanilla AnimSets> <out_dir> <Set> [--clips a,b]

Why (2026-10-26): vanilla's rifle clips hold the left palm ~0.22 ahead of the grip (an M16's handguard). The UMPs,
resized to the M16A2's proportion (0.84 of their old size), have nothing there any more: the idle palm sat 2.3 cm
under a 0.9 cm thin part. Every clip in which vanilla's left hand holds its rifle is kept as vanilla's (body, right
arm, gun) and only the left arm is solved again so that the palm lands where it held the gun at the old size: the
palm's place on the gun times the set's `scale` (about the grip), the hand's turn kept. Where vanilla's hand leaves
the rifle (emotes, catching a fall) it is faded back to vanilla's own arm, as compact_build.py does; clips with no gun
in their name (gestures played through masks) are not built and stay vanilla's. Then the de-clip (compact_build's
Declip: elbows swung out of the body). Built clips go to <out_dir>/<Set>/clips/GunsOfTien_Compact<Set>_<clip>.x and
are packed as compact_build.py packs (the node writer, compact_animsets.py, swaps in the clips built and leaves the
rest vanilla's); a Gunworks grip animId "GunsOfTien_Compact<Set>" plays them for the guns registered with it.
"""

import math
import os
import sys

import bpy  # noqa: F401
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_build as CB  # noqa: E402  (TienInspectWeapon's scripts/anim on the path)
import clearance  # noqa: E402
import compact_animsets as CA  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import x_export  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
import xanim  # noqa: E402

# set -> the guns' size against the rifle the clips fit (the palm's place on the gun is scaled by it)
SETS = {
    # the UMPs: their palm place at the old size (0.72 of real), now 0.603
    # the UMP: its unfolded stock sat 2.3 cm in the shoulder on vanilla's aim; 0.04 forward clears it (0.007)
    "UMP": dict(scale=0.000603 / 0.00072, contact=0.008, aim_push=0.045,
                guns=(("p93", "models_X/weapons/firearms/GunsOfTienPost93_UMP.fbx", "UMP_BODY"),
                      ("p93", "models_X/weapons/parts/GunsOfTienPost93_UMP_parts.fbx", "UMP_STOCK",
                       {"offset": [0.0, -0.0283, 0.0234]}),
                      ("p93", "models_X/weapons/parts/GunsOfTienPost93_UMP_parts.fbx", "UMP_STOCK",
                       {"offset": [-0.0259, -0.0283, 0.0234], "rotate": [0.0, 0.0, 180.0]}),
                      ("p93", "models_X/weapons/magazines/GunsOfTienPost93_UMP_magazines.fbx", "45Magazine25_UMP",
                       {"offset": [0.0, 0.0959, 0.0127]}))),
    # the bullpups (docs/design.md 4h; user, 2026-10-27): the AUG A1 and GoM's FAMAS in one set. Vanilla's palm (0.218
    # ahead of the grip idle, 0.204 aimed) lies on the FAMAS's handguard tip and the AUG's bare barrel; at 0.72 it
    # comes to 0.157 / 0.147, under the FAMAS's handguard (0.10-0.22) and the AUG's folded grip (0.12-0.19), whose
    # undersides are 3 mm apart. `push`: the gun moved forward along its own length (game units) in every frame, the
    # right arm solved after it, so that aiming leaves a gap between the eye and the AUG's scope (user: 3-4 cm; the
    # eyepiece touched the face on vanilla's rifle aim).
    # `contact`: the arms de-clipped to no deeper than vanilla's own in the same frame, and to this where vanilla's are
    # clearer (user, 2026-10-28, after the reloads: no clipping). compact_build's CONTACT (0.022, the forearm's centre
    # line on the skin, half of it inside) let the hand moved back along the gun fold the forearm 1 cm deeper into the
    # belly than vanilla's (0.021-0.028 against 0.011 in 67 of 116 clips)
    # `guns`: the set's guns (model file, body node) checked against the body too: EXTRA_PUSH more while shouldered,
    # then whatever is still in moved straight out of the body. The bullpups' butts reach 3.7 (AUG) / 5.2 (FAMAS) cm
    # further back than GoM's M16A2's and sat 2.4 / 3.2 cm in the shoulder on every aim, through the jaw in the side
    # view (vanilla's own aim has the M16A2 1.8 in); the user's 3-4 cm gap at the eye (`push`) became ~10 cm
    # The parts that hang off the guns are checked at their model points (the AUG's grip both ways, its long magazine,
    # the FAMAS's STANAG; the UMP's stock unfolded and folded, its 25): a body alone left them unseen
    "Bullpup": dict(scale=0.72, push=0.02, contact=0.008, aim_push=0.063,
                    guns=(("main", "models_X/weapons/firearms/GunsOfTien_AUG.fbx", "AUG_BODY"),
                          ("main", "models_X/weapons/firearms/GunsOfTien_AUG.fbx", "AUG_FOREGRIP",
                           {"offset": [0.0, 0.1242, 0.009], "rotate": [90.0, 0.0, 0.0]}),
                          ("main", "models_X/weapons/firearms/GunsOfTien_AUG.fbx", "AUG_FOREGRIP",
                           {"offset": [0.0, 0.1242, 0.009]}),
                          ("main", "models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx", "556x45Magazine42_AUG",
                           {"offset": [0.0, -0.0736, -0.006]}),
                          ("gom", "models_X/weapons/firearms/FAMAS.fbx", "FAMAS_BODY"),
                          ("gom", "models_X/weapons/magazines/assault_rifles.fbx", "556x45Magazine30_STANAG",
                           {"offset": [0.0, -0.0763, 0.0146]}))),
}
# `aim_push`: the push added while the gun is shouldered (`shouldered`), one value so that every aim clip holds the gun
# alike; the bullpups': what clears the FAMAS's butt in vanilla's aim (0.083 in all; the AUG's needs 0.06).
# RIFLE_HAND_EXTRA_PUSH tries another
EXTRA_PUSH = os.environ.get("RIFLE_HAND_EXTRA_PUSH")
GUN_CONTACT = os.environ.get("RIFLE_HAND_GUN_CONTACT")          # the guns' own limit (default: `contact`)
PALM = Vector((0.045, 0.0, 0.012))          # the palm in the hand bone's frame (compact_stance.palm)


def chest_frame(src_dir):
    """Vanilla's idle chest (Bip01_Spine1 at Bob_IdleRifle's first frame): the elbow swings are chosen in the chest's
    own frame relative to it, so that "out" stays out of the body however the body turns (rig.RIGHT is the
    character's: in the seated stand-up the body is turned and an elbow swung that way stayed 1.4 cm in)."""
    xa = xanim.read(os.path.join(src_dir, "Bob_IdleRifle.x"))
    return pose.world(xa, pose.from_clip(xa, 0))["Bip01_Spine1"].to_3x3()


# elbow swings tried, in the idle chest's terms: out, out and back, back, out and up, up
SWINGS = [(-rig.RIGHT).normalized(), (-rig.RIGHT - rig.FWD).normalized(), (-rig.FWD).normalized(),
          (-rig.RIGHT + rig.UP).normalized(), rig.UP.normalized()]


def templates(src_dir):
    out = []
    for clip in ("Bob_IdleRifle", "Bob_IdleAimRifle"):
        xa = xanim.read(os.path.join(src_dir, clip + ".x"))
        w = pose.world(xa, pose.from_clip(xa, 0))
        out.append((w["Bip01_Prop1"].inverted() @ w["Bip01_L_Hand"]).translation)
    return out


def on_gun(rel, tmpl):
    d = min((rel.translation - t).length for t in tmpl)
    return 1.0 - CB.smooth((d - 0.05) / 0.06)


LEFT_CHAIN = ("Bip01_L_Clavicle", "Bip01_L_UpperArm", "Bip01_L_Forearm", "Bip01_L_Hand")
RIGHT_CHAIN = ("Bip01_R_Clavicle", "Bip01_R_UpperArm", "Bip01_R_Forearm", "Bip01_R_Hand")
RAMP = 5                                    # frames over which a release share fades in and out


def gun_objects(arm_ob, guns):
    """The set's guns and their parts on Bip01_Prop1 (game space: the file's z flipped, as smg_reload's preview loads
    them); a part at its model point (offset, rotate) when one is given."""
    from smg_reload import GOM, MEDIA, mat_of
    p93 = os.path.normpath(os.path.join(MEDIA, "..", "..", "..", "GoMExtensionGunsOfTienPost93", "42", "media"))
    obs = []
    for entry in guns:
        root, rel, node = entry[:3]
        at = mat_of(entry[3]) if len(entry) > 3 else Matrix.Identity(4)
        path = os.path.join({"main": MEDIA, "gom": GOM, "p93": p93}[root], rel)
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=path)
        new = list(set(bpy.data.objects) - before)
        src = next(o for o in new if o.name.split(".")[0] == node)
        me = bpy.data.meshes.new(node)
        me.from_pydata([tuple(at @ Vector((v.co.x, v.co.y, -v.co.z))) for v in src.data.vertices], [],
                       [tuple(reversed(f.vertices)) for f in src.data.polygons])
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
        ob = bpy.data.objects.new(node, me)
        bpy.context.scene.collection.objects.link(ob)
        x_preview.attach_to_bone(ob, arm_ob, "Bip01_Prop1")
        obs.append(ob)
    return obs


def gun_depth(dc, xa, q, obs):
    x_import.apply_pose(dc.arm_ob, pose.world(xa, q))
    return dc.body.now({"gun": obs})["gun"]


def shouldered(xa, p):
    """1 with the butt at the right shoulder, 0 with the gun lowered, smooth between: the distance from a point near
    the butt (0.18 behind the grip) to the right upper arm's head, 0.02-0.04 in every aim clip, 0.25-0.37 lowered
    (idle, sprint, vaults, falls, bite reacts), full below 0.06, none above 0.16."""
    w = pose.world(xa, p)
    d = (w["Bip01_Prop1"] @ Vector((0.0, -0.18, 0.02)) - w["Bip01_R_UpperArm"].translation).length
    return 1.0 - CB.smooth((d - 0.06) / 0.10)


def gun_escape(dc, xa, q, obs):
    """How deep the guns are in the body at `q` and the way out: the mean of (nearest body point - vertex) over the
    vertices inside, normalised (a zero vector when none is)."""
    x_import.apply_pose(dc.arm_ob, pose.world(xa, q))
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    body = dc.body.body
    ev = body.evaluated_get(dg).to_mesh()
    tree = BVHTree.FromPolygons([body.matrix_world @ v.co for v in ev.vertices], dc.body.polys)
    body.evaluated_get(dg).to_mesh_clear()
    deepest, way = 0.0, Vector()
    for ob in obs:
        mw = ob.matrix_world
        for v in ob.data.vertices:
            pt = mw @ v.co
            if clearance.inside(tree, pt):
                near, _, _, d = tree.find_nearest(pt)
                deepest = max(deepest, d)
                way += near - pt
    return deepest, (way.normalized() if way.length > 1e-9 else way)


def spread_vectors(need):
    """spread() for vectors: each frame takes, of every frame's vector faded linearly over RAMP frames, the longest."""
    n = len(need)
    out = []
    for f in range(n):
        best = Vector()
        for g in range(n):
            v = need[g] * max(0.0, 1.0 - abs(f - g) / RAMP)
            if v.length > best.length:
                best = v
        out.append(best)
    return out


def carry(xa, r, p, push, back=0.0, off=None):
    """Vanilla's frame `p` with the gun moved forward along its length by `push`, the right hand following it (where
    the arm falls short, the gun stays in the hand: it is put back from where the hand landed); `back` (0..1) eases
    the push and the right arm toward vanilla's own (1: vanilla's arm and gun); `off` (world) moves the gun out of the
    body on top. Returns the pose and the gun."""
    q = pose.copy(p)
    w = pose.world(xa, q)
    W = w["Bip01_Prop1"]
    if (not push or back >= 1.0) and (off is None or off.length == 0):
        return q, W
    grip = W.inverted() @ w["Bip01_R_Hand"]
    move = Matrix.Translation(off) if off is not None else Matrix.Identity(4)
    # the elbow kept in the plane of vanilla's own (its swing not searched: chosen per frame by the wrist's cost, it
    # flipped 16-22 cm between two frames in the sprint vault and FallIdle04)
    elbow = w["Bip01_R_Forearm"].translation - w["Bip01_R_UpperArm"].translation
    keep, r.swivel_scale = r.swivel_scale, 0.0
    r.solve_arm(q, "R", move @ W @ Matrix.Translation((0.0, push * (1.0 - back), 0.0)) @ grip,
                pole_extra=elbow.normalized() * 10.0)
    r.swivel_scale = keep
    r.blend_local(q, p, RIGHT_CHAIN, back)
    w = pose.world(xa, q)
    W = w["Bip01_R_Hand"] @ grip.inverted()
    q["Bip01_Prop1"] = w["Bip01"].inverted() @ W
    return q, W


def least(ok):
    """The least share in 0..1 for which ok(share) holds: tenths first (not monotonic), then halved between the last
    two; 1.0 if none does."""
    if ok(0.0):
        return 0.0
    lo = 0.0
    for k in range(1, 11):
        hi = k / 10.0
        if ok(hi):
            for _ in range(4):
                mid = (lo + hi) / 2
                lo, hi = (lo, mid) if ok(mid) else (mid, hi)
            return hi
        lo = hi
    return 1.0


def toward(r, q, vanilla, t):
    out = pose.copy(q)
    r.blend_local(out, vanilla, LEFT_CHAIN, t)
    return out


def spread(need, ramp=RAMP):
    """Each frame's need carried `ramp` frames either side, fading linearly, so a fix eases in and out."""
    n = len(need)
    return [max(0.0, max(need[g] - abs(f - g) / ramp * max(need) for g in range(n))) if need else 0.0
            for f in range(n)]


def left_solve(r, xa, q, aim, swing=None):
    """The left arm to `aim`, its elbow swung by `swing` (world vector), the shoulder brought forward first where the
    arm falls short (`shoulder_forward`)."""
    shoulder_forward(xa, q, aim)
    r.solve_arm(q, "L", aim, pole_extra=rig.UP * -0.05 + (swing if swing is not None else Vector()))


def shoulder_forward(xa, q, aim):
    """Where the left arm falls short of `aim` (a gun pushed out: aim up 75, 1.2 cm; the UMP's aimed rack, 2 cm), the
    clavicle turned about its root toward the target, up to 25 degrees, by the least that brings the hand there."""
    w = pose.world(xa, q)
    C = w["Bip01_L_Clavicle"]
    S = w["Bip01_L_UpperArm"].translation
    reach = (q["Bip01_L_Forearm"].translation.length + q["Bip01_L_Hand"].translation.length) * 0.998
    T = aim.translation
    if (T - S).length > reach:
        v0 = S - C.translation
        axis = v0.cross(T - C.translation)
        if axis.length > 1e-9:
            axis.normalize()
            turn = lambda deg: Quaternion(axis, math.radians(deg))
            short = lambda deg: (T - (C.translation + turn(deg) @ v0)).length > reach
            lo, hi = 0.0, 25.0
            if not short(hi):
                for _ in range(10):
                    mid = (lo + hi) / 2
                    lo, hi = (mid, hi) if short(mid) else (lo, mid)
            rl = (C.to_3x3().inverted() @ turn(hi).to_matrix() @ C.to_3x3()).to_4x4()
            q["Bip01_L_Clavicle"] = q["Bip01_L_Clavicle"] @ rl


def arm_escape(dc, xa, q, side, limit):
    """How far `side`'s arm sinks past `limit` at `q` (clearance's limb measure) and the way out: each sunk point's
    direction out of the body (to the nearest body point when inside, away from it when only the limb's skin is in),
    weighted by how far it sinks."""
    x_import.apply_pose(dc.arm_ob, pose.world(xa, q))
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    body = dc.body.body
    ev = body.evaluated_get(dg).to_mesh()
    tree = BVHTree.FromPolygons([body.matrix_world @ v.co for v in ev.vertices], dc.body.polys)
    body.evaluated_get(dg).to_mesh_clear()
    deepest, way = 0.0, Vector()
    for pt, radius in dc.body.segments()[side]:
        near, _, _, d = tree.find_nearest(pt)
        if clearance.inside(tree, pt):
            sink, out = d + radius, near - pt
        else:
            sink, out = radius - d, pt - near
        deepest = max(deepest, sink)
        if sink > limit and out.length > 1e-9:
            way += out.normalized() * (sink - limit)
    return deepest, (way.normalized() if way.length > 1e-9 else way)


SWING_MAX = 0.4


def swing_along(dc, q, aim, contact, solve, d):
    """The least swing along the world direction `d` (up to SWING_MAX) that brings the left arm out to `contact` with
    the hand on its place; None where none does."""
    def depth(k):
        t = pose.copy(q)
        solve(t, aim, d * k)
        return dc.depth(t)[0]
    if depth(0.0) <= contact:
        return 0.0
    lo = 0.0
    for k in (0.025, 0.05, 0.1, 0.15, 0.2, 0.3, SWING_MAX):
        if depth(k) <= contact:
            hi = k
            for _ in range(3):
                mid = (lo + hi) / 2
                lo, hi = (lo, mid) if depth(mid) <= contact else (mid, hi)
            return hi
        lo = k
    return None


def clip_swing(dc, poses, aims, limits, turns, solve):
    """One elbow swing direction for the whole clip (of SWINGS, in the idle chest's terms, turned with the chest each
    frame): the one that clears the most frames, then with the least swing; per frame the least swing along it,
    spread over RAMP frames. Chosen per frame, neighbours took different directions and the spread handed a frame a
    neighbour's swing that did not clear it (the seated sit-down's hand then slid 4 cm)."""
    best = None
    for d in SWINGS:
        need = [swing_along(dc, q, a, lim, solve, t @ d) if a is not None else 0.0
                for q, a, lim, t in zip(poses, aims, limits, turns)]
        missed = sum(1 for k in need if k is None)
        need = [SWING_MAX if k is None else k for k in need]
        score = (missed, sum(need))
        if best is None or score < best[0]:
            best = (score, d, need)
        if score == (0, 0.0):
            break
    _, d, need = best
    return [t @ d * k for t, k in zip(turns, spread(need))]


def release_share(dc, r, q, vanilla, contact):
    """The least share of vanilla's own left arm (clavicle to hand) that brings the arm in `q` out to `contact`: the
    hand slides forward along the gun toward vanilla's hold. Tenths first (the depth is not monotonic in the share),
    then halved between the last two; vanilla's arm itself is at most `contact` deep by construction."""
    return least(lambda t: dc.depth(toward(r, q, vanilla, t))[0] <= contact + 0.0005)


def build_clip(src_dir, out_dir, set_name, clip, tmpl):
    scale = SETS[set_name]["scale"]
    push = SETS[set_name].get("push", 0.0)
    path = os.path.join(src_dir, clip + ".x")
    xa = xanim.read(path, with_mesh=True)
    frames = CB.frames_of(xa)
    r = CB.no_limit(rig.Rig(xa, frames[0], poi=0.6, top=1, rest=x_import.rest_matrices(xa)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm_ob = x_import.load(path)
    contact = SETS[set_name].get("contact")
    dc = CB.Declip(arm_ob, xa)
    poses, aims = [], []
    # each arm no deeper than vanilla's own in that frame, or `contact` where vanilla's is clearer
    vdep = [dc.depth(p) for p in frames] if contact else []
    limits = [max(contact, d[0]) for d in vdep]
    pushes = [push] * len(frames)
    guns = SETS[set_name].get("guns")
    offs = [None] * len(frames)
    glim = float(GUN_CONTACT or contact or 0.0) + 0.0005
    obs = gun_objects(arm_ob, guns) if contact and guns else None
    if obs:
        # 1. forward along its length while shouldered (the aim's butt in the shoulder). Searched per frame, the push
        # crept back and forth in still poses (aim up 45, 2.5 cm a frame: the depth is not monotonic in it); one per
        # clip kept aim-to-idle's aim push down to the idle (its left elbow flipped, its end off the idle's)
        aim_push = float(EXTRA_PUSH or SETS[set_name].get("aim_push", 0.0))
        pushes = [push + aim_push * shouldered(xa, p) for p in frames]
    # the right arm the push put in (bite reacts, emotes, vaults: up to 4 cm against vanilla's 1.6): the push eased
    # off there, spread like the left arm's fixes
    backs = spread([least(lambda t: dc.depth(carry(xa, r, p, pu, t)[0])[1] <= max(contact, d[1]) + 0.0005)
                    for p, d, pu in zip(frames, vdep, pushes)]) if contact and any(pushes) else [0.0] * len(frames)
    if obs:
        # 2. what is still in (a scope in the face, a carry handle in the chest in reactions and bumps; pushing on made
        # those worse): moved straight out of the body, kept in the chest's frame so the spread follows the body
        # In rounds: a frame handed a neighbour's move by the spread can be pushed in the wrong way (a frame clear by
        # itself went 1.3 cm in in the UMP's aimed strafe), and the right arm's easing below can take the gun back in, so
        # whatever is still in is moved out again from where it is, spread, until every frame is clear
        chests = [pose.world(xa, p)["Bip01_Spine1"].to_3x3() for p in frames]
        offs = [Vector() for _ in frames]
        for _ in range(4):
            need, left = [], 0
            for p, pu, bk, off, chest in zip(frames, pushes, backs, offs, chests):
                add = Vector()
                for _ in range(8):
                    d, way = gun_escape(dc, xa, carry(xa, r, p, pu, bk, off + add)[0], obs)
                    if d <= glim or way.length == 0:
                        break
                    add = add + way * (d - glim + 0.003)
                left += add.length > 0
                need.append(chest.inverted() @ add)
            if not left:
                break
            offs = [off + chest @ v for off, chest, v in zip(offs, chests, spread_vectors(need))]
            # a right arm that carrying the gun out put in (a bite react: 0.9 cm) eased toward vanilla's again
            more = spread([least(lambda t: dc.depth(carry(xa, r, p, pu, max(bk, t), off)[0])[1]
                                 <= max(contact, d[1]) + 0.0005)
                           for p, d, pu, bk, off in zip(frames, vdep, pushes, backs, offs)])
            backs = [max(a, c) for a, c in zip(backs, more)]
        if os.environ.get("RIFLE_HAND_DEBUG"):
            for f, (p, pu, bk, off) in enumerate(zip(frames, pushes, backs, offs)):
                print("[debug] f%d gun out %.3f back %.2f -> gun %.3f" % (
                    f, off.length, bk, gun_depth(dc, xa, carry(xa, r, p, pu, bk, off)[0], obs)))
    solve = (lambda q, a, s=None: left_solve(r, xa, q, a, s)) if contact else None
    targets = []
    for p, back, pu, off in zip(frames, backs, pushes, offs):
        w = pose.world(xa, p)
        rel = w["Bip01_Prop1"].inverted() @ w["Bip01_L_Hand"]
        on = on_gun(rel, tmpl)
        q, W = carry(xa, r, p, pu, back, off)
        target = None
        if on > 0.0:
            palm = rel @ PALM
            target = Matrix.Translation(palm * (scale - 1.0) * on) @ rel
            if solve:
                solve(q, W @ target)
            else:
                r.solve_arm(q, "L", W @ target, pole_extra=rig.UP * -0.05)
                q, _ = dc.arms(r, q, target)
        targets.append(target)
        aims.append(W @ target if on > 0.0 else None)
        poses.append(q)
    if contact:
        # Declip.arms chooses its elbow swing frame by frame (steps of 0.025), which pops between neighbours: the
        # swing each frame needs, spread over RAMP frames either side, then for what the swing leaves in, the gun moved
        # out of the body with both hands (the hand stays on its place), and for what is left after that vanilla's own
        # arm by the share each frame needs (the hand slides along the gun), each spread the same way
        idle_chest = chest_frame(src_dir).inverted()
        turns = [pose.world(xa, p)["Bip01_Spine1"].to_3x3() @ idle_chest for p in frames]
        swing = clip_swing(dc, poses, aims, limits, turns, solve)
        for q, a, s in zip(poses, aims, swing):
            if a is not None and s.length > 0:
                solve(q, a, s)

        def refit(f, add):
            q, W = carry(xa, r, frames[f], pushes[f], backs[f], (offs[f] or Vector()) + add)
            solve(q, W @ targets[f], swing[f])
            return q, W
        need = []
        for f, (q, lim) in enumerate(zip(poses, limits)):
            add = Vector()
            if targets[f] is not None:
                t = q
                for _ in range(8):
                    d, way = arm_escape(dc, xa, t, "L", lim)
                    if d <= lim + 0.0005 or way.length == 0:
                        break
                    add = add + way * (d - lim + 0.002)
                    t = refit(f, add)[0]
            need.append(pose.world(xa, frames[f])["Bip01_Spine1"].to_3x3().inverted() @ add)
        moved = 0
        for f, v in enumerate(spread_vectors(need)):
            if v.length > 0 and targets[f] is not None:
                add = pose.world(xa, frames[f])["Bip01_Spine1"].to_3x3() @ v
                poses[f], W = refit(f, add)
                aims[f] = W @ targets[f]
                moved += 1
        share = spread([release_share(dc, r, q, p, lim) for q, p, lim in zip(poses, frames, limits)])
        poses = [toward(r, q, p, t) if t > 0 else q for q, p, t in zip(poses, frames, share)]
        dc.fixed = sum(1 for s, t, k in zip(swing, share, backs) if s.length > 0 or t > 0 or k > 0)
        print("[rifle_hand] %s: gun moved out for the left arm on %d frames, hand released on %d (largest share %.2f)" % (
            clip, moved, sum(1 for t in share if t > 0), max(share)))
        if os.environ.get("RIFLE_HAND_DEBUG"):
            for f, q in enumerate(poses):
                print("[debug] f%d push %.3f off %.3f back %.2f swing %.3f share %.2f depth %.3f %.3f limit %.3f" % (
                    f, pushes[f], offs[f].length if offs[f] is not None else 0.0, backs[f], swing[f].length, share[f],
                    *dc.depth(q), limits[f]))
    if obs:
        gd = [gun_depth(dc, xa, q, obs) for q in poses]
        f = max(range(len(gd)), key=lambda i: gd[i])
        print("[rifle_hand] %s: guns at most %.3f in (f%d)" % (clip, gd[f], f))
        for ob in obs:
            bpy.data.objects.remove(ob, do_unlink=True)
    # where the left hand ended up against where it holds the gun (a straight arm falls short of a gun pushed out)
    off_gun = max(((pose.world(xa, q)["Bip01_L_Hand"].translation - a.translation).length
                   for q, a in zip(poses, aims) if a is not None), default=0.0)
    name = CB.out_name(set_name, clip)
    d = os.path.join(out_dir, set_name, "clips")
    os.makedirs(d, exist_ok=True)
    pose.bake(arm_ob, xa, poses, name)
    x_export.export(path, os.path.join(d, name + ".x"), name, arm_ob)
    print("[rifle_hand] %s %s (%d frames, %d declip steps / released frames, left hand off its place by %.3f)" % (
        set_name, clip, len(frames), dc.fixed, off_gun))
    return name


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    only = None
    if "--clips" in args:
        only = args[args.index("--clips") + 1].split(",")
        args = [a for i, a in enumerate(args) if a != "--clips" and (i == 0 or args[i - 1] != "--clips")]
    src_dir, animsets, out_dir, set_name = args[:4]
    tmpl = templates(src_dir)
    clips = only or sorted(c for c in CA.firearm_clips(animsets) if not CB.is_generic(c))
    names = [build_clip(src_dir, out_dir, set_name, clip, tmpl) for clip in clips]
    if only is None:
        CB.pack(out_dir, set_name, names)
