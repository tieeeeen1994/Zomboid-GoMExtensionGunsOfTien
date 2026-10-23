"""
Muzzle-down idle options for the compact SMG stance (user, 2026-10-23: "for the idle, i think the guns should be
pointing downwards rather than up"; no vanilla rifle idle points down). Blender 5.2, headless.

    blender -b --factory-startup -P scripts/anim/idle_down.py -- <vanilla anims_X/Bob> <out_dir> [gun ...]

D0: vanilla's Bob_IdleAimRifle_Down (a shouldered low ready, 45 degrees down) untouched but for the head lifted to
look ahead and the left hand pulled in to the gun's support place (stance_vanilla's rule).
D1-D3: vanilla's rifle idle body, the gun re-posed muzzle down (both arms solved; the grip place per direction picked
by a small scan for reach of every set's support place and natural wrists): D1 across the body down-left, D2 forward
and down 45 degrees, D3 steeply down.
"""

import itertools
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_stance as C  # noqa: E402
import hold_preview as HP  # noqa: E402
import stance_vanilla as SV  # noqa: E402
import clearance  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
from rig import Key, ch  # noqa: E402

DIRS = {"D1": ch(-0.80, -0.45, 0.40), "D2": ch(-0.40, -0.65, 0.65), "D3": ch(-0.30, -0.85, 0.43)}
SETS = ["uzi", "mp7", "mp5k"]


def d0_pose(src_dir, gun):
    spec = C.GUNS[gun]
    xa, base, r = SV.vanilla_rig(src_dir, "Bob_IdleAimRifle_Down.x")
    q = pose.copy(base)
    head = pose.world(xa, q)["Bip01_Head"].translation
    r.look_at(q, head + rig.FWD * 2.0 + rig.UP * -0.3, 1.0)        # eyes ahead, a little down, not on the sights
    q = SV.left_only(r, xa, q, SV.turned(r, spec, (0, 0, 0)))
    return xa, r, q, "Bob_IdleAimRifle_Down.x"


def place_for(r, along):
    best = None
    for pos in (ch(x, u, f) for x in (0.03, 0.07, 0.11) for u in (0.48, 0.54, 0.60) for f in (0.04, 0.09, 0.14)):
        cost = 0.0
        for g in SETS:
            spec = C.GUNS[g]
            r.warnings.clear()
            p = r.build([Key(0, pos=pos, along=along, top=ch(0.3, 0.9, 0.3), look=0.15, lean=2, aux=0.0, support=1,
                             lgrip=C.grip_on(r.support_base, spec["support"]))], 1, breath=(0, None))[0]
            cost += sum(float(w.rsplit(" ", 1)[1]) for w in r.warnings) * 60
            cost += r.wrist_cost(p, "L") + r.wrist_cost(p, "R")
        if best is None or cost < best[0]:
            best = (cost, pos)
    r.warnings.clear()
    return best[1]


def d_pose(src_dir, gun, name, cache={}):
    spec = C.GUNS[gun]
    xa, r = C.build_rig(src_dir)
    if name not in cache:
        cache[name] = place_for(r, DIRS[name])
    pos = cache[name]
    p = r.build([Key(0, pos=pos, along=DIRS[name], top=ch(0.3, 0.9, 0.3), look=0.15, lean=2, aux=0.0, support=1,
                     lgrip=C.grip_on(r.support_base, spec["support"]))], 1, breath=(0, None))[0]
    return xa, r, p, "Bob_IdleRifle.x"


def render(src_dir, out_dir, gun):
    spec = C.GUNS[gun]
    for name in ["D0"] + list(DIRS):
        xa, r, q, clip = d0_pose(src_dir, gun) if name == "D0" else d_pose(src_dir, gun, name)
        short = list(r.warnings)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        arm_ob = x_import.load(os.path.join(src_dir, clip))
        pose.bake(arm_ob, xa, [q, q], name)
        for path, node, mat in HP.GUNS[gun]["parts"]:
            HP.load_part(arm_ob, path, node, (C.FLIP @ mat) if (spec["flip"] and mat is not None) else
                         (C.FLIP if spec["flip"] else mat))
        body = clearance.Body(arm_ob)
        d = body.frame(0, {"gun": [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == arm_ob
                                  and o.name != body.body.name]})
        print("[down] %s %s: L wrist %s R wrist %s short %s body %s" % (
            gun, name, tuple(round(a) for a in r.wrist_angles(q, "L")), tuple(round(a) for a in r.wrist_angles(q, "R")),
            short[:1], {k: round(v, 3) for k, v in d.items()}))
        scene = bpy.context.scene
        x_preview.setup_render(scene)
        scene.render.resolution_x = scene.render.resolution_y = 420
        os.makedirs(out_dir, exist_ok=True)
        for view, (loc, tgt) in HP.VIEWS.items():
            cam = x_preview.camera("Cam_" + view, loc, tgt)
            cam.data.ortho_scale = 0.9
            scene.camera = cam
            scene.render.filepath = os.path.join(out_dir, "%s_%s_%s.png" % (gun, name, view))
            bpy.ops.render.render(write_still=True)


if __name__ == "__main__" and not os.environ.get("ID_ROUND2") and not os.environ.get("ID_ROUND3"):
    args = sys.argv[sys.argv.index("--") + 1:]
    for gun in args[2:] or ["uzi", "mp7", "mp5k"]:
        render(args[0], args[1], gun)


# ---- second round: what fits Bob (a two-handed muzzle-down hold does not: dscan, 2026-10-23) ----
# O1: one-handed, muzzle down-forward, the left arm hanging (vanilla's handgun idle body)
# O2: two hands across the body as vanilla's rifle idle, tipped ~15-20 degrees down
def o1_pose(src_dir, gun):
    xa = C.xanim.read(os.path.join(src_dir, "Bob_IdleHandgun.x"), with_mesh=True)
    base = pose.from_clip(xa, 0)
    r = rig.Rig(xa, base, poi=0.6, top=1, rest=x_import.rest_matrices(xa))
    best = None
    for pos, al in itertools.product([ch(x, u, f) for x in (0.10, 0.13, 0.16) for u in (0.42, 0.46, 0.50)
                                      for f in (0.02, 0.06, 0.10)],
                                     [ch(-0.15, -0.65, 0.74), ch(-0.25, -0.55, 0.8), ch(-0.1, -0.8, 0.6)]):
        r.warnings.clear()
        p = r.build([Key(0, pos=pos, along=al, top=ch(0.2, 0.6, 0.6), look=0.0, lean=0, aux=0.0, support=0)], 1,
                    breath=(0, None))[0]
        W = pose.world(xa, p)["Bip01_Prop1"]
        a = C.rot_of(W) @ Vector((0, 1, 0))
        err = (a - al.normalized()).length
        cost = r.wrist_cost(p, "R") + err * 5 + sum(float(w.rsplit(" ", 1)[1]) for w in r.warnings) * 60
        if best is None or cost < best[0]:
            best = (cost, p)
    r.warnings.clear()
    return xa, r, best[1], "Bob_IdleHandgun.x"


def o2_pose(src_dir, gun):
    spec = C.GUNS[gun]
    xa, r = C.build_rig(src_dir)
    best = None
    for pos, al in itertools.product([ch(x, u, f) for x in (0.04, 0.08) for u in (0.54, 0.60, 0.66) for f in (0.04, 0.09)],
                                     [ch(-0.85, -0.25, 0.45), ch(-0.8, -0.35, 0.45), ch(-0.75, -0.3, 0.6)]):
        cost = 0.0
        for g in SETS:
            r.warnings.clear()
            p = r.build([Key(0, pos=pos, along=al, top=ch(0.3, 0.9, 0.2), look=0.15, lean=2, aux=0.0, twist=15, support=1,
                             lgrip=C.grip_on(r.support_base, C.GUNS[g]["support"]))], 1, breath=(0, None))[0]
            W = pose.world(xa, p)["Bip01_Prop1"]
            a = C.rot_of(W) @ Vector((0, 1, 0))
            cost += r.wrist_cost(p, "L") + r.wrist_cost(p, "R") + sum(float(w.rsplit(" ", 1)[1]) for w in r.warnings) * 60
            cost += max(0.0, a.dot(rig.UP) + 0.25) * 20        # at least ~15 degrees down where it lands
        if best is None or cost < best[0]:
            best = (cost, pos, al)
    r.warnings.clear()
    p = r.build([Key(0, pos=best[1], along=best[2], top=ch(0.3, 0.9, 0.2), look=0.15, lean=2, aux=0.0, twist=15, support=1,
                     lgrip=C.grip_on(r.support_base, spec["support"]))], 1, breath=(0, None))[0]
    return xa, r, p, "Bob_IdleRifle.x"


def render2(src_dir, out_dir, gun):
    spec = C.GUNS[gun]
    for name, fn in (("O1", o1_pose), ("O2", o2_pose)):
        xa, r, q, clip = fn(src_dir, gun)
        short = list(r.warnings)
        W = pose.world(xa, q)["Bip01_Prop1"]
        a = C.rot_of(W) @ Vector((0, 1, 0))
        bpy.ops.wm.read_factory_settings(use_empty=True)
        arm_ob = x_import.load(os.path.join(src_dir, clip))
        pose.bake(arm_ob, xa, [q, q], name)
        for path, node, mat in HP.GUNS[gun]["parts"]:
            HP.load_part(arm_ob, path, node, (C.FLIP @ mat) if (spec["flip"] and mat is not None) else
                         (C.FLIP if spec["flip"] else mat))
        body = clearance.Body(arm_ob)
        d = body.frame(0, {"gun": [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == arm_ob
                                  and o.name != body.body.name]})
        print("[down] %s %s: muzzle down %.0f deg, L wrist %s R wrist %s short %s body %s" % (
            gun, name, -C.math.degrees(C.math.asin(max(-1, min(1, a.dot(rig.UP))))),
            tuple(round(x) for x in r.wrist_angles(q, "L")), tuple(round(x) for x in r.wrist_angles(q, "R")),
            short[:1], {k: round(v, 3) for k, v in d.items()}))
        scene = bpy.context.scene
        x_preview.setup_render(scene)
        scene.render.resolution_x = scene.render.resolution_y = 420
        for view, (loc, tgt) in HP.VIEWS.items():
            cam = x_preview.camera("Cam_" + view, loc, tgt)
            cam.data.ortho_scale = 0.9
            scene.camera = cam
            scene.render.filepath = os.path.join(out_dir, "%s_%s_%s.png" % (gun, name, view))
            bpy.ops.render.render(write_still=True)


if os.environ.get("ID_ROUND2"):
    _a = sys.argv[sys.argv.index("--") + 1:]
    for _g in _a[2:] or ["uzi", "mp7", "mp5k"]:
        render2(_a[0], _a[1], _g)


# ---- third round (user: "keep the gun close to themselves. like the vanilla one except the right hand is on the upper
# side and the left hand on the lower side"): vanilla's rifle idle body, the gun's diagonal reversed: grip high on the
# right chest, muzzle down to the forward-left, left hand low on the front. Vanilla's clips do not keep one
# hand-to-gun relation (Bip01_Prop1 hangs off Bip01, the hand bones barely move), so this hold takes the pistol
# idle's (the barrel along the forearm, turned for an upright gun): with the rifle idle's a relaxed wrist points the
# barrel ~50 degrees above the forearm and the reversed diagonal asked a -100 degree wrist.
X_KEY = dict(pos=ch(0.02, 0.58, 0.04), along=ch(-0.60, -0.60, 0.50), top=ch(0.0, 0.3, 1.0), look=0.15, lean=2, aux=0.0,
             twist=15)
if os.environ.get("ID_X2"):          # across the belly like vanilla's, 30 degrees down (user: "terrible and not natural")
    X_KEY = dict(X_KEY, pos=ch(0.02, 0.58, 0.12), along=ch(-0.80, -0.50, 0.30))
if os.environ.get("ID_S"):           # X turned to the side (user: "make it less pointing forward and more to the side")
    X_KEY = dict(X_KEY, **{"S1": dict(pos=ch(0.06, 0.56, 0.0), along=ch(-0.77, -0.61, 0.20), twist=0),
                           "S2": dict(pos=ch(0.02, 0.56, 0.0), along=ch(-0.78, -0.62, 0.12), twist=0)}[os.environ["ID_S"]])
if os.environ.get("ID_M"):           # S1 rolled so the magazine hangs down, a little away from the belly (user: "rotate
    # the held gun so that the mag doesn't hit the body"; S1's top faced forward, its magazine into the belly). The
    # gun sits ~10 cm further out so the hanging magazine clears the belly; right wrist natural (-43, -3, -35)
    X_KEY = dict(X_KEY, pos=ch(0.02, 0.64, 0.10), along=ch(-0.77, -0.61, 0.20), top=-(ch(0.25, -1.0, 0.2)), twist=15)
if os.environ.get("ID_MC"):          # ID_M moved in, same angle (user: "move the gun closer to the body without rotating
    # the gun"): 4 cm straight back is the most before the gun's rear goes into the chest (MP5K also 3 cm right)
    off = ch(0.03, 0.0, -0.04) if os.environ.get("ID_MC") == "mp5k" else ch(0.0, 0.0, -0.04)
    X_KEY = dict(X_KEY, pos=ch(0.02, 0.64, 0.10), along=ch(-0.77, -0.61, 0.20), top=-(ch(0.25, -1.0, 0.2)), twist=15)
    X_OFFSET = off
if os.environ.get("ID_X3"):          # X closer to the body (user: "X is better, but keep the gun closer if possible"):
    # the grip 4 cm right and 6 cm back, the same 38 degrees; the gun's middle 6 cm nearer the chest, the closest
    # a scan found with the gun and arms out of the body and every wrist natural
    X_KEY = dict(X_KEY, pos=ch(0.06, 0.58, -0.02))


def x_rig(src_dir):
    xa, r = C.build_rig(src_dir)
    hx = C.xanim.read(os.path.join(src_dir, "Bob_IdleHandgun.x"))
    hw = pose.world(hx, pose.from_clip(hx, 0))
    r.grip_r = hw["Bip01_R_Hand"].inverted() @ hw["Bip01_Prop1"] @ C.FLIP
    return xa, r


def x_turn(r, spec):
    best = None
    for t in itertools.product(range(-90, 91, 15), range(-180, 180, 15), range(-90, 91, 15)):
        r.warnings.clear()
        q = r.build([Key(0, support=1, lgrip=C.grip_on(r.support_base, spec["support"], t), **X_KEY)], 1,
                    breath=(0, None))[0]
        cost = r.wrist_cost(q, "L") + sum(float(w.rsplit(" ", 1)[1]) for w in r.warnings) * 60 \
            + (abs(t[0]) + abs(t[2])) / 400.0
        if best is None or cost < best[0]:
            best = (cost, t)
    r.warnings.clear()
    return best[1]


def render3(src_dir, out_dir, gun):
    spec = C.GUNS[gun]
    xa, r = x_rig(src_dir)
    t = x_turn(r, spec)
    q = r.build([Key(0, support=1, lgrip=C.grip_on(r.support_base, spec["support"], t), **X_KEY)], 1,
                breath=(0, None))[0]
    if globals().get("X_OFFSET") is not None:
        W = pose.world(xa, q)["Bip01_Prop1"]
        W.translation = W.translation + X_OFFSET
        solve = r.solve_arm
        r.solve_arm = lambda p, side, target, pole_extra=Vector(), limit=0.0: solve(p, side, target, pole_extra, 0.0)
        r.warnings.clear()
        q = r.pose_for(W, dict(look=0.15, lean=2, aux=0.0, support=1.0, elbow=0.0, twist=15), 0, (0, None), 1,
                       lgrip=C.grip_on(r.support_base, spec["support"], t))
    short = list(r.warnings)
    W = pose.world(xa, q)["Bip01_Prop1"]
    a = C.rot_of(W) @ Vector((0, 1, 0))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm_ob = x_import.load(os.path.join(src_dir, "Bob_IdleRifle.x"))
    pose.bake(arm_ob, xa, [q, q], "X")
    for path, node, mat in HP.GUNS[gun]["parts"]:
        HP.load_part(arm_ob, path, node, (C.FLIP @ mat) if (spec["flip"] and mat is not None) else
                     (C.FLIP if spec["flip"] else mat))
    body = clearance.Body(arm_ob)
    parts = [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == arm_ob and o.name != body.body.name]
    d = body.frame(0, {"gun": [o for o in parts if "Magazine" not in o.name],
                       "mag": [o for o in parts if "Magazine" in o.name]})
    print("[down] %s X: left turn %s, muzzle down %.0f, L wrist %s R wrist %s short %s body %s" % (
        gun, t, -C.math.degrees(C.math.asin(max(-1, min(1, a.dot(rig.UP))))),
        tuple(round(x) for x in r.wrist_angles(q, "L")), tuple(round(x) for x in r.wrist_angles(q, "R")),
        short[:1], {k: round(v, 3) for k, v in d.items()}))
    scene = bpy.context.scene
    x_preview.setup_render(scene)
    scene.render.resolution_x = scene.render.resolution_y = 420
    for view, (loc, tgt) in HP.VIEWS.items():
        cam = x_preview.camera("Cam_" + view, loc, tgt)
        cam.data.ortho_scale = 0.9
        scene.camera = cam
        scene.render.filepath = os.path.join(out_dir, "%s_X%s_%s.png" % (gun, "2" if os.environ.get("ID_X2") else "3" if os.environ.get("ID_X3") else ("MC" if os.environ.get("ID_MC") else "M" if os.environ.get("ID_M") else os.environ.get("ID_S", "")), view))
        bpy.ops.render.render(write_still=True)


if os.environ.get("ID_ROUND3"):
    _a = sys.argv[sys.argv.index("--") + 1:]
    for _g in _a[2:] or ["uzi", "miniuzi", "mp7", "mp5k"]:
        render3(_a[0], _a[1], _g)
