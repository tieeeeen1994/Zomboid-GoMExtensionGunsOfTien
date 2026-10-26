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

import os
import sys

import bpy  # noqa: F401
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_build as CB  # noqa: E402  (TienInspectWeapon's scripts/anim on the path)
import compact_animsets as CA  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import x_export  # noqa: E402
import x_import  # noqa: E402
import xanim  # noqa: E402

# set -> the guns' size against the rifle the clips fit (the palm's place on the gun is scaled by it)
SETS = {
    # the UMPs: their palm place at the old size (0.72 of real), now 0.603
    "UMP": dict(scale=0.000603 / 0.00072),
}
PALM = Vector((0.045, 0.0, 0.012))          # the palm in the hand bone's frame (compact_stance.palm)


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


def build_clip(src_dir, out_dir, set_name, clip, tmpl):
    scale = SETS[set_name]["scale"]
    path = os.path.join(src_dir, clip + ".x")
    xa = xanim.read(path, with_mesh=True)
    frames = CB.frames_of(xa)
    r = CB.no_limit(rig.Rig(xa, frames[0], poi=0.6, top=1, rest=x_import.rest_matrices(xa)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm_ob = x_import.load(path)
    dc = CB.Declip(arm_ob, xa)
    poses = []
    for p in frames:
        q = pose.copy(p)
        w = pose.world(xa, q)
        W = w["Bip01_Prop1"]
        rel = W.inverted() @ w["Bip01_L_Hand"]
        on = on_gun(rel, tmpl)
        if on > 0.0:
            palm = rel @ PALM
            target = Matrix.Translation(palm * (scale - 1.0) * on) @ rel
            r.solve_arm(q, "L", W @ target, pole_extra=rig.UP * -0.05)
            q, _ = dc.arms(r, q, target)
        poses.append(q)
    name = CB.out_name(set_name, clip)
    d = os.path.join(out_dir, set_name, "clips")
    os.makedirs(d, exist_ok=True)
    pose.bake(arm_ob, xa, poses, name)
    x_export.export(path, os.path.join(d, name + ".x"), name, arm_ob)
    print("[rifle_hand] %s %s (%d frames, %d declip steps)" % (set_name, clip, len(frames), dc.fixed))
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
