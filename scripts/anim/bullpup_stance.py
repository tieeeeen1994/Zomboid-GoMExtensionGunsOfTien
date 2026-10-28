"""
Bullpup stance drafts (TODO "Bullpup stance drafts"; user, 2026-10-28: the bullpup set's hold, vanilla's rifle hold
with the palm moved back, "looks weird": the gun hangs back past the hip, front up and left). Stills of two holds for
the AUG A1 and GoM's FAMAS to choose from (Blender 5.2, headless; TienInspectWeapon's rig).

    blender -b --factory-startup -P scripts/anim/bullpup_stance.py -- <vanilla anims_X/Bob> <out_dir> [A|B|now ...]

Writes <out_dir>/<draft>_<gun>_<view>.png (guns aug_folded, aug, famas; views front, side, top) and logs each pose's
wrists, reach and depth in the body (chest + pelvis). Both drafts put the left palm on the set's one place (the base
clip's own palm x 0.72 about the grip: 0.157 ahead of it idle, under the FAMAS's handguard and the AUG's folded grip,
just ahead of the trigger guard), the hand turned as vanilla's.
A    shouldered low ready: vanilla's rifle aim (its torso and hand-to-gun relation), the gun where the set's aim holds
     it (pushed forward by push + aim_push) swung down about its butt, so the butt stays in the shoulder pocket; the
     angle scanned 30-45 (30 wins); eyes ahead. Vanilla's own Bob_IdleAimRifle_Down was tried first: it hunches over
     the gun with the head bowed into the FAMAS's carry handle.
B    tucked carry: vanilla's rifle idle body, the butt pinned between the upper arm and the ribs (the upper arm's bone
     line within PIN of it), the gun along the right forearm, muzzle 25-45 down (BS_B_DOWN; left free the scan settles
     on 15, a hip-level ready); held with the pistol idle's hand-to-gun relation (idle_down.x_rig): the rifle idle's
     tips the barrel ~50 degrees above the forearm. Scanned for reach, wrists, the gun touching the side but no deeper
     than 0.008, arms no deeper than vanilla's idle.
now  the shipped set's idle for comparison (vanilla's rifle idle, push, palm moved back; before its de-clip).
Env: BS_PROBE=1 prints the body's landmarks and vanilla's guns in character space (ch: right, up, forward) instead.
"""

import itertools
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_stance as C  # noqa: E402  (also puts TienInspectWeapon's scripts/anim on the path)
import clearance  # noqa: E402
import hold_preview as HP  # noqa: E402
import idle_down as ID  # noqa: E402
import pose  # noqa: E402
import rifle_hand as RH  # noqa: E402
import rig  # noqa: E402
import stance_vanilla as SV  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
from rig import Key, ch  # noqa: E402

SCALE = RH.SETS["Bullpup"]["scale"]           # the set's palm place: vanilla's x 0.72 about the grip
PUSH, AIM_PUSH = RH.SETS["Bullpup"]["push"], RH.SETS["Bullpup"]["aim_push"]
BUTT = 0.21                                   # grip to butt plate (AUG 0.201, FAMAS 0.216)
GUNS = ["aug_folded", "aug", "famas"]
BODY_LOW = clearance.BODY | {"Bip01_Pelvis"}  # a gun carried low meets the belly and hips too
PIN = 0.045                                   # B: the upper arm's bone line this close to the butt (arm radius ~0.022)


def cv(v):
    """A world (skeleton space) vector as ch(right, up, forward), rounded, for the log."""
    return tuple(round(v.dot(a), 3) for a in (rig.RIGHT, rig.UP, rig.FWD))


def down_deg(W):
    a = C.rot_of(W) @ Vector((0, 1, 0))
    return -math.degrees(math.asin(max(-1.0, min(1.0, a.dot(rig.UP)))))


def probe(src_dir):
    for clip in ("Bob_IdleRifle.x", "Bob_IdleAimRifle.x", "Bob_IdleAimRifle_Down.x"):
        xa, base, r = SV.vanilla_rig(src_dir, clip)
        w = pose.world(xa, base)
        W = w["Bip01_Prop1"]
        print("[probe] %s: grip %s butt %s muzzle down %.0f, palm %s" % (
            clip, cv(W.translation), cv(W @ Vector((0, -BUTT, 0))), down_deg(W), cv(w["Bip01_L_Hand"].translation)))
        for b in ("Bip01_R_Clavicle", "Bip01_R_UpperArm", "Bip01_R_Forearm", "Bip01_R_Hand", "Bip01_Spine1",
                  "Bip01_Pelvis", "Bip01_Neck", "Bip01_L_UpperArm"):
            print("[probe]   %s %s" % (b, cv(w[b].translation)))
        print("[probe]   eye %s, shouldered %.2f" % (cv(r.eye0), RH.shouldered(xa, base)))


def left_grip(r, at_scale=SCALE, turn=(0.0, 0.0, 0.0)):
    """The set's left-hand place on the gun: the base clip's own hand, its palm moved to `at_scale` of its distance
    from the grip (rifle_hand's rule), turned about the palm by `turn`."""
    return C.grip_on(r.support_base, C.palm(r.support_base) * at_scale, turn)


def draft_a(src_dir, arm_ob, body, gun_obs):
    """The aim's upright torso (vanilla's Bob_IdleAimRifle_Down hunches over the gun, head bowed into the FAMAS's
    carry handle), the gun where the set's aim holds it (vanilla's rifle place pushed forward by push + aim_push)
    swung down about its butt, so the butt stays in the shoulder pocket; eyes ahead. Angle scanned 30-45 degrees."""
    # the aim clip as base (its own hand-to-gun relation: the idle's bent the right wrist 78 degrees here)
    xa, r = C.build_rig(src_dir, "Bob_IdleAimRifle.x", "Bob_IdleAimRifle.x")
    W0 = r.weapon_aux
    along0 = C.rot_of(W0) @ Vector((0, 1, 0))
    grip0 = W0.translation + along0 * (PUSH + AIM_PUSH)
    butt = grip0 - along0 * BUTT
    side = along0.cross(rig.UP).normalized()                       # the character's right, square to the gun
    lg = C.grip_on(r.support_aux, C.palm(r.support_aux) * SCALE)
    best = None
    for deg in (30, 35, 40, 45):
        R = Matrix.Rotation(math.radians(-deg), 3, side)
        along = R @ along0
        top = R @ rig.UP
        r.warnings.clear()
        p = r.build([Key(0, pos=butt + along * BUTT, along=along, top=top, look=0.0, lean=0, aux=1.0, twist=0,
                         support=1, lgrip=lg)], 1, breath=(0, None))[0]
        head = pose.world(xa, p)["Bip01_Head"].translation
        r.look_at(p, head + rig.FWD * 2.0 + rig.UP * -0.4, 1.0)    # eyes ahead and a little down, off the sights
        x_import.apply_pose(arm_ob, pose.world(xa, p))
        d = body.now({"gun": gun_obs})
        short = sum(float(x.rsplit(" ", 1)[1]) for x in r.warnings)
        cost = r.wrist_cost(p, "L") + r.wrist_cost(p, "R") + short * 60 + max(0.0, d["gun"] - 0.008) * 400
        print("[draft] A cand %d deg: cost %.2f depth %s" % (deg, cost, {k: round(x, 3) for k, x in d.items()}))
        if best is None or cost < best[0] - 0.05:                  # the shallowest that is about as good
            best = (cost, deg, p, list(r.warnings))
    r.warnings[:] = best[3]
    print("[draft] A: %d degrees down about the butt" % best[1])
    return xa, r, best[2], "Bob_IdleAimRifle.x"


def draft_now(src_dir, arm_ob, body, gun_obs):
    """For comparison, the shipped set's idle (rifle_hand.py "Bullpup" before its de-clip): vanilla's rifle idle, the
    gun pushed forward by `push`, the left palm at the set's place."""
    xa, base, r = SV.vanilla_rig(src_dir, "Bob_IdleRifle.x")
    q, _ = RH.carry(xa, r, base, PUSH)
    return xa, r, SV.left_only(r, xa, q, left_grip(r)), "Bob_IdleRifle.x"


MOVE_CLIPS = ("Bob_RunRifle", "Bob_Sprint_Rifle")
MOVE_EVERY = int(os.environ.get("BS_MOVE_EVERY", "2"))


def move_preview(src_dir, out_dir, name, xa0, r0, q0, gun="famas"):
    """A draft's hold on vanilla's rifle run and sprint, frame by frame as compact_build's carried clips: the gun at
    the draft's place against the chest plus shares of vanilla's own gun drift against it (BS_DRIFT="out,up", default
    the short SMG stance's approved 0.2, 0.4; rigid, B's gun went 4.6-4.9 cm into the hips and the right arm 2-3 cm
    in, with 0.2 / 0.4 about 1 cm and the butt still at the upper arm), both arms solved onto it with the draft's
    grips, the rest of the body vanilla's. Renders <out_dir>/<name>_<clip>/<view>_<frame>.png (gif.py) and logs the worst of each measure."""
    w0 = pose.world(xa0, q0)
    hold = w0["Bip01_Spine1"].inverted() @ w0["Bip01_Prop1"]
    lg = w0["Bip01_Prop1"].inverted() @ w0["Bip01_L_Hand"]
    wi = pose.world(xa0, r0.base)
    gun_idle = (wi["Bip01_Spine1"].inverted() @ wi["Bip01_Prop1"]).translation
    keep_out, keep_up = (float(v) for v in os.environ.get("BS_DRIFT", "0.2,0.4").split(","))
    fwd_l = (wi["Bip01_Spine1"].to_3x3().inverted() @ rig.FWD).normalized()
    up_l = (wi["Bip01_Spine1"].to_3x3().inverted() @ rig.UP).normalized()
    s = dict(look=0.0, lean=0.0, aux=0.0, support=1.0, elbow=0.0, twist=0.0)
    for clip in MOVE_CLIPS:
        path = os.path.join(src_dir, clip + ".x")
        xa = RH.xanim.read(path, with_mesh=True)
        frames = RH.CB.frames_of(xa)
        n = len(frames) - 1
        r = RH.CB.no_limit(rig.Rig(xa, frames[0], poi=0.6, top=1, rest=x_import.rest_matrices(xa)))
        r.grip_r = r0.grip_r.copy()
        poses, short = [], 0.0
        for f, p in enumerate(frames):
            r.base = p
            w = pose.world(xa, p)
            drift = (w["Bip01_Spine1"].inverted() @ w["Bip01_Prop1"]).translation - gun_idle
            drift = fwd_l * drift.dot(fwd_l) * keep_out + up_l * drift.dot(up_l) * keep_up
            r.warnings.clear()
            poses.append(r.pose_for(w["Bip01_Spine1"] @ Matrix.Translation(drift) @ hold, s, f, (0, None), n,
                                    lgrip=lg))
            short = max([short] + [float(x.rsplit(" ", 1)[1]) for x in r.warnings])
        bpy.ops.wm.read_factory_settings(use_empty=True)
        arm_ob = x_import.load(path)
        pose.bake(arm_ob, xa, poses, "%s_%s" % (name, clip))
        obs = load_gun(arm_ob, gun)
        body = clearance.Body(arm_ob, BODY_LOW)
        worst = body.check(range(n + 1), {"gun": obs})
        wr = {side: max(range(n + 1), key=lambda f: r.wrist_cost(poses[f], side)) for side in "LR"}
        pins = []
        for q in poses:
            w = pose.world(xa, q)
            pins.append(seg_dist(w["Bip01_Prop1"] @ Vector((0, -BUTT + 0.03, 0.0)),
                                 w["Bip01_R_UpperArm"].translation, w["Bip01_R_Forearm"].translation))
        print("[move] %s %s (%d frames): depth %s; worst wrists L %s @%d, R %s @%d; hand short %.3f; butt to upper "
              "arm %.3f-%.3f" % (
                  name, clip, n + 1, ", ".join("%s %.3f@%d" % (k, v[0], v[1]) for k, v in sorted(worst.items())),
                  tuple(round(a) for a in r.wrist_angles(poses[wr["L"]], "L")), wr["L"],
                  tuple(round(a) for a in r.wrist_angles(poses[wr["R"]], "R")), wr["R"], short, min(pins), max(pins)))
        # vanilla's own arms in the same clip, for the no-clipping rule
        vb = vanilla_depths(src_dir, clip, frames)
        print("[move]   vanilla %s: arms %s" % (clip, ", ".join("%s %.3f@%d" % (k, v[0], v[1])
                                                               for k, v in sorted(vb.items()))))
        bpy.ops.wm.read_factory_settings(use_empty=True)
        arm_ob = x_import.load(path)
        pose.bake(arm_ob, xa, poses, "%s_%s" % (name, clip))
        load_gun(arm_ob, gun)
        scene = bpy.context.scene
        x_preview.setup_render(scene)
        scene.render.resolution_x = scene.render.resolution_y = 420
        d = os.path.join(out_dir, "%s_%s" % (name, clip))
        os.makedirs(d, exist_ok=True)
        cams = {}
        for view in ("front", "side"):
            loc, tgt = HP.VIEWS[view]
            cams[view] = x_preview.camera("Cam_" + view, loc, tgt)
            cams[view].data.ortho_scale = 0.9
        for f in range(0, n + 1, MOVE_EVERY):
            scene.frame_set(f)
            for view, cam in cams.items():
                scene.camera = cam
                scene.render.filepath = os.path.join(d, "%s_%03d.png" % (view, f))
                bpy.ops.render.render(write_still=True)


def vanilla_depths(src_dir, clip, frames):
    """Vanilla's own arms in the clip (the limit the no-clipping rule measures against)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm_ob = x_import.load(os.path.join(src_dir, clip + ".x"))
    return clearance.Body(arm_ob, BODY_LOW).check(range(len(frames)))


def b_key(pos, along, lg, twist=0.0):
    return Key(0, pos=pos, along=along, top=rig.UP, look=0.0, lean=0, aux=0.0, twist=twist, support=1, lgrip=lg)


def draft_b(src_dir, arm_ob, body, gun_obs):
    # the right hand holds the grip as the pistol idle does (barrel along the forearm; idle_down's x_rig): with the
    # rifle idle's relation a relaxed wrist points the barrel ~50 degrees above the forearm
    xa, r = ID.x_rig(src_dir)
    w = pose.world(xa, r.base)
    lg = left_grip(r)
    # vanilla idle's own depths: the arms may go no deeper than these, or 0.008
    x_import.apply_pose(arm_ob, w)
    v = body.now()
    lim = {s: max(0.008, v[s]) for s in "LR"}
    best = []
    # the butt under the arm, between the upper arm and the ribs (the shoulder joint is at ch(0.10, 0.75, -0.035),
    # the idle's elbow at ch(0.15, 0.63, -0.05), the chest's side about 0.09 out): pinned there, so the upper arm
    # must pass within PIN of it
    # muzzle at least 25 degrees down (left free, the scan settles on 15: a hip-level low ready, not this carry)
    downs = [int(a) for a in os.environ.get("BS_B_DOWN", "25,35,45").split(",")]
    for x, u, f, a, b, tw in itertools.product((0.08, 0.10, 0.12, 0.14), (0.60, 0.64, 0.68, 0.72),
                                               (-0.10, -0.07, -0.04, -0.01), downs, (0, 10, 20, 30), (0.0, 15.0)):
        along = ch(-math.cos(math.radians(a)) * math.sin(math.radians(b)), -math.sin(math.radians(a)),
                   math.cos(math.radians(a)) * math.cos(math.radians(b)))
        butt = ch(x, u, f)
        pos = butt + along * BUTT
        r.warnings.clear()
        p = r.build([b_key(pos, along, lg, tw)], 1, breath=(0, None))[0]
        short = sum(float(s.rsplit(" ", 1)[1]) for s in r.warnings)
        wp = pose.world(xa, p)
        # where the gun landed (the wrist limit gives way): off the asked direction costs too
        got = C.rot_of(wp["Bip01_Prop1"]) @ Vector((0, 1, 0))
        arm = seg_dist(wp["Bip01_Prop1"] @ Vector((0, -BUTT + 0.03, 0.0)), wp["Bip01_R_UpperArm"].translation,
                       wp["Bip01_R_Forearm"].translation)
        cost = (r.wrist_cost(p, "L") + r.wrist_cost(p, "R") + short * 60 + (got - along).length * 5
                + max(0.0, arm - PIN) * 100)
        best.append((cost, (x, u, f, a, b, tw), pos, along, p))
    best.sort(key=lambda e: e[0])
    scored = []
    for cost, prm, pos, along, p in best[:80]:
        x_import.apply_pose(arm_ob, pose.world(xa, p))
        d = body.now({"gun": gun_obs})
        # the butt pinned at the side: the gun clear (<= 0.008 in) and no more than 2 cm off the body
        g = gun_gap(body, gun_obs)
        pen = sum(max(0.0, d[s] - lim[s]) for s in "LR") + max(0.0, d["gun"] - 0.008)
        total = cost + pen * 400 + max(0.0, g - 0.02) * 100
        scored.append((total, prm, cost, d, g, pos, along, p))
    scored.sort(key=lambda e: e[0])
    for s in scored[:5]:
        print("[draft] B cand %.2f %s wrists+short+off %.2f depth %s gun gap %.3f" % (
            s[0], s[1], s[2], {k: round(x, 3) for k, x in s[3].items()}, s[4]))
    _, prm, _, _, _, pos, along, _ = scored[0]
    print("[draft] B: butt at ch(%.2f, %.2f, %.2f), %d down, %d in, twist %d (limits %s)" % (
        prm[0], prm[1], prm[2], prm[3], prm[4], prm[5], {k: round(v, 3) for k, v in lim.items()}))
    r.warnings.clear()
    p = r.build([b_key(pos, along, lg, prm[5])], 1, breath=(0, None))[0]
    return xa, r, p, "Bob_IdleRifle.x"


def seg_dist(p, a, b):
    """The distance from p to the segment a-b."""
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(1e-9, ab.dot(ab))))
    return (a + ab * t - p).length


def gun_gap(body, obs):
    """How close the gun comes to the body (as it stands): the least distance from a vertex outside it to its
    nearest face, 0 when any vertex is inside."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.body.evaluated_get(dg).to_mesh()
    mw = body.body.matrix_world
    tree = clearance.BVHTree.FromPolygons([mw @ v.co for v in ev.vertices], body.polys)
    body.body.evaluated_get(dg).to_mesh_clear()
    best = 1.0
    for ob in obs:
        ow = ob.matrix_world
        for v in ob.data.vertices:
            best = min(best, tree.find_nearest(ow @ v.co)[3])
    return best


def load_gun(arm_ob, gun):
    before = set(bpy.data.objects)
    for path, node, mat in HP.GUNS[gun]["parts"]:
        HP.load_part(arm_ob, path, node, mat)
    return [o for o in bpy.data.objects if o not in before]


def render(src_dir, out_dir, name, xa, r, q, clip):
    short = list(r.warnings)
    W = pose.world(xa, q)["Bip01_Prop1"]
    for gun in GUNS:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        arm_ob = x_import.load(os.path.join(src_dir, clip))
        pose.bake(arm_ob, xa, [q, q], name)
        obs = load_gun(arm_ob, gun)
        body = clearance.Body(arm_ob, BODY_LOW)
        d = body.frame(0, {"gun": [o for o in obs if "Magazine" not in o.name],
                           "mag": [o for o in obs if "Magazine" in o.name]})
        w = pose.world(xa, q)
        fa = (w["Bip01_R_Hand"].translation - w["Bip01_R_Forearm"].translation).normalized()
        pin = seg_dist(W @ Vector((0, -BUTT + 0.03, 0.0)), w["Bip01_R_UpperArm"].translation,
                       w["Bip01_R_Forearm"].translation)
        print("[draft] %s %s: grip %s butt %s (upper arm %.3f off), muzzle down %.0f, gun to R forearm %.0f deg, "
              "L wrist %s R wrist %s short %s depth %s" % (
            name, gun, cv(W.translation), cv(W @ Vector((0, -BUTT, 0))), pin, down_deg(W),
            math.degrees(fa.angle(C.rot_of(W) @ Vector((0, 1, 0)))), tuple(round(a) for a in r.wrist_angles(q, "L")),
            tuple(round(a) for a in r.wrist_angles(q, "R")), short[:1], {k: round(v, 3) for k, v in d.items()}))
        scene = bpy.context.scene
        x_preview.setup_render(scene)
        scene.render.resolution_x = scene.render.resolution_y = 420
        os.makedirs(out_dir, exist_ok=True)
        for view, (loc, tgt) in HP.VIEWS.items():
            cam = x_preview.camera("Cam_" + view, loc, tgt)
            cam.data.ortho_scale = 0.9
            scene.camera = cam
            scene.render.filepath = os.path.join(out_dir, "%s_%s_%s.png" % (name, gun, view))
            bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    if os.environ.get("BS_PROBE"):
        probe(args[0])
    else:
        for which in args[2:] or ["A", "B"]:
            bpy.ops.wm.read_factory_settings(use_empty=True)
            arm = x_import.load(os.path.join(args[0], "Bob_IdleRifle.x"))
            obs = load_gun(arm, "famas") + load_gun(arm, "aug")
            res = {"A": draft_a, "B": draft_b, "now": draft_now}[which](args[0], arm, clearance.Body(arm, BODY_LOW), obs)
            if os.environ.get("BS_MOVE"):
                move_preview(args[0], args[1], which, *res[:3])
            else:
                render(args[0], args[1], which, *res)
