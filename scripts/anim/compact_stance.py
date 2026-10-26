"""
The compact SMG stance (full-size Uzi, Mini Uzi, GoM's MP5K; user, 2026-10-23: "Option B", the Micro Uzi and the P90
stay pistol-held): its key poses on vanilla's two-handed (rifle) base, drafted as stills for approval (Blender 5.2,
headless; TienInspectWeapon's rig).

    blender -b --factory-startup -P scripts/anim/compact_stance.py -- <vanilla anims_X/Bob> <out_dir> [gun ...]

All three guns are two-handed (`firearm`) and drawn upright in the hand: the Mini Uzi and the MP5K are modelled upside
down for the pistol clips and turned a half turn about their length by their model scripts' `Bip01_Prop1` attachment.
The stance is one body pose with two left-hand places: under the handguard (Uzi, Mini Uzi, ~0.07 ahead of the grip) or
on the MP5K's vertical foregrip (~0.18 ahead), so it ships as two clip sets built from the same keys.
"""

import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ANIM = os.environ.get("TIEN_ANIM") or os.path.normpath(os.path.join(ROOT, "..", "TienInspectWeapon", "scripts", "anim"))
sys.path.insert(0, ANIM)
sys.path.insert(0, HERE)
import clearance  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
import xanim  # noqa: E402
from rig import Key, ch, rot_of  # noqa: E402
import hold_preview as HP  # noqa: E402

FLIP = Matrix.Rotation(math.pi, 4, 'Y')            # upside-down (pistol) export -> upright in the hand

# per gun: drawn upright? (False = turned by FLIP), the left hand's place (palm, upright weapon space)
GUNS = {
    # forward on the gun like the MP7 / MP5K (user, 2026-10-23: "uzi should use the style of mp7 and mp5k"): under the
    # front of the receiver, as far forward as the Mini Uzi allows (its receiver ends ~0.13, its folded stock's butt
    # hangs under the barrel at 0.10-0.11)
    "uzi": dict(flip=False, support=Vector((0.0, 0.130, -0.014)) * HP.UZI_S, set="Uzi"),
    "miniuzi": dict(flip=True, support=Vector((0.0, 0.130, -0.014)) * HP.UZI_S, set="Uzi"),     # shares the Uzi's clips
    "mp5k": dict(flip=True, support=Vector((0.0, 0.180, -0.032)), set="MP5K", vertical=True),
    # Post-93's MP7A1 with its foregrip unfolded (0.13-0.155 ahead, hanging under the gun); folded / MP7A2: under the
    # handguard about as far
    "mp7": dict(flip=True, support=Vector((0.0, 0.142, -0.040)) * HP.MP7_S, set="MP7", vertical=True),
}


def palm(template):
    return template @ Vector((0.045, 0.0, 0.012))


def grip_on(template, at, rot=(0.0, 0.0, 0.0)):
    R = (Matrix.Rotation(math.radians(rot[0]), 3, 'X') @ Matrix.Rotation(math.radians(rot[1]), 3, 'Y')
         @ Matrix.Rotation(math.radians(rot[2]), 3, 'Z'))
    q = (R @ template.to_3x3()).to_quaternion()
    return Matrix.LocRotScale(at + R @ (template.translation - palm(template)), q, None)


def lgrip_with_wrist(r, key, at, wrist, start, rounds=6):
    """A left-hand placement with its palm on `at` (weapon space) and the left wrist at `wrist` (bend Y, bend Z,
    twist) from the natural one: solve the arm, set the wrist, take the hand's new turn, put the palm back on `at`,
    a few rounds (the palm moves as the hand turns). `start`: the first guess (a template)."""
    lg = grip_on(start, at)
    n, nw, nr = len(r.swivels), len(r.wrist_warnings), len(r.warnings)
    for _ in range(rounds):
        p = r.build([Key(0, support=1, lgrip=lg, **key)], 1, breath=(0, None))[0]
        r.set_wrist(p, "L", *wrist)
        w = pose.world(r.xa, p)
        W = w["Bip01_Prop1"]
        hand = W.inverted() @ w["Bip01_L_Hand"]
        lg = grip_on(hand, at)
    del r.swivels[n:], r.wrist_warnings[nw:], r.warnings[nr:]
    return lg


def build_rig(src_dir, base_clip="Bob_IdleRifle.x", aux_clip="Bob_IdleAimRifle.x"):
    xa = xanim.read(os.path.join(src_dir, base_clip), with_mesh=True)
    base = pose.from_clip(xa, 0)
    aux = pose.copy(base)
    aux.update({b: m for b, m in pose.from_clip(xanim.read(os.path.join(src_dir, aux_clip)), 0).items()
                if b in base})
    r = rig.Rig(xa, base, aux=aux, poi=0.6, top=1, rest=x_import.rest_matrices(xa))
    return xa, r


# The two key poses, in character space, found by a scan over places both clip sets can hold (reach of both hands, both
# wrists, body clearance, a muzzle-down preference): Bob's arm reaches only 0.274 from the shoulder, so with the MP5K's
# foregrip 0.18 ahead of its grip a muzzle-down low ready pointing forward is out of the left hand's reach.
# Idle: a low ready across the body, the grip in front of the right side at chest-low, muzzle forward-left and down,
# the chest turned a little right. Aim: vanilla's rifle-aim torso with the gun pushed out ~6 cm past the shouldered
# rifle (no stock at the shoulder), the sights on the eye line, the chest turned a little right.
def env_v(name, default):
    v = os.environ.get(name)
    return ch(*([float(x) for x in v.split(",")] if v else default))


def poses(r):
    E = r.eye0
    return {
        "Idle": dict(pos=env_v("CS_IDLE_POS", (0.06, 0.60, 0.08)), along=env_v("CS_IDLE_ALONG", (-0.80, -0.30, 0.50)),
                     top=ch(0.40, 0.90, 0.0), look=0.15, lean=2, aux=0.0, twist=15),
        # vanilla's rifle aim, the gun exactly where a rifle's grip is (at_aux: the right arm and wrist untouched), the
        # left hand keeping the rifle's grip but slid back along the gun to its support place (user, 2026-10-23: the
        # cheeked option, "more like the rifle's, except the hand controlling the recoil should move in closer")
        "Aim": dict(pos=E + env_v("CS_AIM_POS", (0.08, -0.10, 0.18)), along=ch(0, 0, 1), top=rig.UP,
                    look=0.0, lean=0, aux=1.0, twist=0, at_aux=True),
        # square push-pull: vanilla's two-handed pistol aim body (square to the target), the gun centred, its sights
        # on the eye line, both arms forward; drafted at a few distances from the face (CS_SQ_OUT)
        "AimSquare": dict(pos=None, along=ch(0, 0, 1), top=rig.UP, look=0.0, lean=float(os.environ.get("CS_SQ_LEAN", "0")),
                          aux=0.0,
                          twist=float(os.environ.get("CS_SQ_TWIST", "0")), base="Bob_IdleAimHandgun.x"),
    }


def render(src_dir, out_dir, gun):
    spec = GUNS[gun]
    xa, r = build_rig(src_dir)
    if os.environ.get("CS_SHOW_TEMPLATE"):
        print("[stance] rifle aim left palm on the rifle (weapon space):", tuple(round(c, 3) for c in palm(r.support_aux)),
              " idle:", tuple(round(c, 3) for c in palm(r.support_base)))
    for name, k in poses(r).items():
        if os.environ.get("CS_ONLY") and name != os.environ["CS_ONLY"]:
            continue
        templates = {"Idle": r.support_base, "Aim": r.support_aux}
        if k.get("base"):
            # the rifle aim's left hand (under a handguard) on vanilla's pistol-aim body: the pistol aim's own left
            # hand cups the right one
            templates["AimSquare"] = r.support_aux
            xa, r = build_rig(src_dir, k["base"], k["base"])
            k = dict(k, pos=r.eye0 + env_v("CS_SQ_POS", (0.0, -0.075, 0.20)))
        tmpl = templates[name]
        rot = (0.0, 0.0, -60.0) if spec.get("vertical") else (0.0, 0.0, 0.0)   # a fist round the foregrip (scanned)
        lg = grip_on(tmpl, spec["support"], rot)
        if k.get("at_aux"):
            # the rifle aim's left arm, closer in: its wrist angles kept (measured with the hand on the rifle)
            akey = dict(pos=k["pos"], along=k["along"], top=k["top"], look=k["look"], lean=k["lean"], aux=k["aux"],
                        twist=k["twist"], at_aux=True)
            p0 = r.build([Key(0, support=1, lgrip=tmpl, **akey)], 1, breath=(0, None))[0]
            vanilla_wrist = r.wrist_angles(p0, "L")
            r.warnings.clear()
            print("[stance] %s %s: vanilla's rifle-aim left wrist %s" % (gun, name, tuple(round(a) for a in vanilla_wrist)))
            lg = lgrip_with_wrist(r, akey, spec["support"], vanilla_wrist, tmpl)
        keys = [Key(0, pos=k["pos"], along=k["along"], top=k["top"], look=k["look"], lean=k["lean"], aux=k["aux"],
                    support=1, lgrip=lg, twist=k["twist"], at_aux=k.get("at_aux", False))]
        p = r.build(keys, 1, breath=(0, None))[0]
        if r.warnings:
            print("[stance] %s %s: out of reach %s" % (gun, name, r.warnings[:2]))
        landed = pose.world(xa, p)["Bip01_Prop1"]
        print("[stance] %s %s: grip asked %s landed %s (eye %s); muzzle %s" % (
            gun, name, tuple(round(k["pos"].dot(v), 3) for v in (rig.RIGHT, rig.UP, rig.FWD)),
            tuple(round(landed.translation.dot(v), 3) for v in (rig.RIGHT, rig.UP, rig.FWD)),
            tuple(round(r.eye0.dot(v), 3) for v in (rig.RIGHT, rig.UP, rig.FWD)),
            tuple(round((rot_of(landed) @ Vector((0, 1, 0))).dot(v), 2) for v in (rig.RIGHT, rig.UP, rig.FWD))))
        r.warnings.clear()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        arm_ob = x_import.load(os.path.join(src_dir, k.get("base") or "Bob_IdleRifle.x"))
        pose.bake(arm_ob, xa, [p, p], "draft")
        for path, node, mat in HP.GUNS[gun]["parts"]:
            HP.load_part(arm_ob, path, node, (FLIP @ mat) if (spec["flip"] and mat is not None) else
                         (FLIP if spec["flip"] else mat))
        body = clearance.Body(arm_ob)
        d = body.frame(0, {"gun": [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == arm_ob
                                  and o.name != body.body.name]})
        print("[stance] %s %s: L wrist %s, R wrist %s, body %s" % (
            gun, name, tuple(round(a) for a in r.wrist_angles(p, "L")), tuple(round(a) for a in r.wrist_angles(p, "R")),
            {k_: round(v, 3) for k_, v in d.items()}))
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
    for gun in args[2:] or list(GUNS):
        render(args[0], args[1], gun)
