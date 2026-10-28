"""
Side-by-side review renders of one clip in several versions (Blender 5.2, headless; TienInspectWeapon's importer).

    blender -b --factory-startup -P scripts/anim/stance_compare.py -- <out_dir> <step> <label=clip.x> [label=clip.x ...]

Each clip is imported on its own (x_import.load; only the body is drawn) and rendered every <step> frames from straight
in front and from above (STANCE_VIEWS: any of front, top, left, right, the character's sides), orthographic, so a chest turned off the facing shows at once, into
<out_dir>/<label>/<view>_<frame>.png; stance_compare_gif.py pastes the versions side by side into a GIF. Written for the short SMG stance's squaring (2026-10-29).
"""

import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_stance as C  # noqa: E402,F401  (puts TienInspectWeapon's scripts/anim on the path)
import x_import  # noqa: E402
import x_preview  # noqa: E402



def render_one(out_dir, step, label, path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    x_preview.setup_render(scene)
    arm = x_import.load(path)
    act = arm.animation_data.action if arm.animation_data else None
    end = int(act.frame_range[1]) if act else 0
    print("[compare] %s %s frames 0-%d" % (label, os.path.basename(path), end))
    # the height looked at (STANCE_Z; "chest" follows the chest bone, for close-ups: STANCE_ORTHO zooms all but top)
    follow = os.environ.get("STANCE_Z") == "chest"
    z = 0.0 if follow else float(os.environ.get("STANCE_Z", "0.9"))
    # iso_l / iso_r: from above at the game camera's slope (about 35 degrees down), from the character's front left /
    # front right
    views = {"front": ((0.0, -4.0, z), (0.0, 0.0, z)), "top": ((0.0, -0.15, 4.0), (0.0, -0.15, 0.0)),
             "left": ((4.0, 0.0, z), (0.0, 0.0, z)), "right": ((-4.0, 0.0, z), (0.0, 0.0, z)),
             "iso_l": ((2.3, -2.3, z + 2.3), (0.0, 0.0, z)), "iso_r": ((-2.3, -2.3, z + 2.3), (0.0, 0.0, z))}
    views = {k: views[k] for k in os.environ.get("STANCE_VIEWS", "front,top").split(",")}
    scene.render.resolution_x, scene.render.resolution_y = 300, 420
    for f in range(0, end + 1, step):
        scene.frame_set(f)
        c = arm.matrix_world @ arm.pose.bones["Bip01_Spine1"].head if follow else Vector()
        for view, (loc, tgt) in views.items():
            if follow:
                if view == "top":            # straight down onto the chest
                    loc, tgt = (0.0, 0.0, 4.0), (0.0, 0.0, 0.0)
                loc, tgt = Vector(loc) + c, Vector(tgt) + c
            cam = x_preview.camera("Cam_" + view, loc, tgt)
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = float(os.environ.get("STANCE_ORTHO", "2.0")) if (follow or view != "top") else 1.4
            if view == "top":
                cam.rotation_euler = (0.0, 0.0, 0.0)
            scene.camera = cam
            scene.render.filepath = os.path.join(out_dir, label, "%s_%d.png" % (view, f))
            bpy.ops.render.render(write_still=True)


def main(out_dir, step, items):
    for label, path in items:
        render_one(out_dir, step, label, path)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    main(args[0], int(args[1]), [a.split("=", 1) for a in args[2:]])
