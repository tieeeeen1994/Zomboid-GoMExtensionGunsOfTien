"""
The compact SMG stance on vanilla's own clips (user, 2026-10-23: "copy the right hand style in the vanilla one and
just adjust the left arm"): every bone as the vanilla rifle clip has it, the gun where the rifle is (Bip01_Prop1
untouched), and only the left arm solved onto the gun's support place. Blender 5.2, headless; TienInspectWeapon's rig.

    blender -b --factory-startup -P scripts/anim/stance_vanilla.py -- <vanilla anims_X/Bob> <out_dir> [gun ...]

Env: SV_SCAN=1 scans the left hand's turn about the gun (palm kept on the support place) for the most natural wrist
and prints the best; SV_TURN_<SET>="x,y,z" sets a set's turn (degrees about the gun's X, Y, Z) for the renders.
"""

import itertools
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_stance as C  # noqa: E402  (also puts TienInspectWeapon's scripts/anim on the path)
import clearance  # noqa: E402
import hold_preview as HP  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
import xanim  # noqa: E402

CLIPS = {"Idle": "Bob_IdleRifle.x", "Aim": "Bob_IdleAimRifle.x"}
# turn of the left hand about the gun per clip set and pose (degrees about X, Y, Z), from SV_SCAN
TURN = {("Uzi", "Idle"): (0, -15, 15), ("Uzi", "Aim"): (0, 0, 0),
        ("MP7", "Idle"): (-15, -15, 0), ("MP7", "Aim"): (0, 0, 0),
        ("MP5K", "Idle"): (0, -15, 0), ("MP5K", "Aim"): (0, -15, 0)}


def vanilla_rig(src_dir, clip):
    xa = xanim.read(os.path.join(src_dir, clip), with_mesh=True)
    base = pose.from_clip(xa, 0)
    return xa, base, rig.Rig(xa, base, poi=0.6, top=1, rest=x_import.rest_matrices(xa))


def left_only(r, xa, p, lgrip):
    """Vanilla's pose p with only the left arm solved onto lgrip (weapon -> hand) on the gun where p has it."""
    q = pose.copy(p)
    W = pose.world(xa, q)["Bip01_Prop1"]
    r.solve_arm(q, "L", W @ lgrip, pole_extra=rig.UP * -0.05)
    return q


def turned(r, spec, turn):
    return C.grip_on(r.support_base, spec["support"], turn)


def scan(src_dir, gun):
    spec = C.GUNS[gun]
    out = []
    for name, clip in CLIPS.items():
        xa, base, r = vanilla_rig(src_dir, clip)
        res = []
        for t in itertools.product(range(-60, 61, 15), range(-180, 180, 15), range(-60, 61, 15)):
            r.warnings.clear()
            q = left_only(r, xa, base, turned(r, spec, t))
            short = sum(float(w.rsplit(" ", 1)[1]) for w in r.warnings)
            res.append((r.wrist_cost(q, "L") + short * 60 + (abs(t[0]) + abs(t[2])) / 400.0, t,
                        tuple(round(a) for a in r.wrist_angles(q, "L"))))
        res.sort()
        for o in res[:5]:
            print("[sv] %s %s cost %.2f turn %s wrist %s" % (gun, name, o[0], o[1], o[2]))


def render(src_dir, out_dir, gun):
    spec = C.GUNS[gun]
    for name, clip in CLIPS.items():
        xa, base, r = vanilla_rig(src_dir, clip)
        env = os.environ.get("SV_TURN_%s_%s" % (spec["set"].upper(), name.upper()))
        t = tuple(float(x) for x in env.split(",")) if env else TURN.get((spec["set"], name), (0, 0, 0))
        r.warnings.clear()
        q = left_only(r, xa, base, turned(r, spec, t))
        bpy.ops.wm.read_factory_settings(use_empty=True)
        arm_ob = x_import.load(os.path.join(src_dir, clip))
        pose.bake(arm_ob, xa, [q, q], "sv")
        for path, node, mat in HP.GUNS[gun]["parts"]:
            HP.load_part(arm_ob, path, node, (C.FLIP @ mat) if (spec["flip"] and mat is not None) else
                         (C.FLIP if spec["flip"] else mat))
        body = clearance.Body(arm_ob)
        d = body.frame(0, {"gun": [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == arm_ob
                                  and o.name != body.body.name]})
        print("[sv] %s %s: turn %s, L wrist %s, short %s, body %s" % (
            gun, name, t, tuple(round(a) for a in r.wrist_angles(q, "L")), r.warnings[:1],
            {k: round(v, 3) for k, v in d.items()}))
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


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    for gun in args[2:] or ["uzi", "miniuzi", "mp7", "mp5k"]:
        (scan(args[0], gun) if os.environ.get("SV_SCAN") else render(args[0], args[1], gun))
