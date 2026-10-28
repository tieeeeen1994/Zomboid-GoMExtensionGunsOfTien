"""
Review renders of generic (emote) copies as the game shows them (Blender 5.2, headless; TienInspectWeapon's importer).

    blender -b --factory-startup -P scripts/anim/shown_compare.py -- <vanilla anims_X/Bob> <AnimSets> <out_dir> <step>
        <vanilla clip, e.g. Bob_EmoteSneeze02_2H> <suffix, e.g. __Stand> <label=clip.x|under.x> [label=clip.x|under.x ...]

A generic copy plays in a masked node over the state underneath (compact_build.py "generic clips as the game plays
them"): every bone blended by the node's weight (compact_animsets.generic_variants), the gun from that state. Its file
alone is not what the game draws (a right arm at weight 0.2 is stored five times its swing), so each version is shown
here as compact_build.masked(underlying frame 0, clip frame, masks), on Bob's body, from the front and both sides,
the camera following the chest, into <out_dir>/<label>/<view>_<frame>.png for stance_compare_gif.py (STANCE_VIEWS =
front,left,right). Written 2026-10-29: the short SMG emote review had shown the raw files ("holy crap that looks
terrible"), five of which were clean in game.
"""

import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_build as CB  # noqa: E402
import compact_animsets as CA  # noqa: E402
import pose  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
import xanim  # noqa: E402

VIEWS = {"front": Vector((0.0, -4.0, 0.0)), "left": Vector((4.0, 0.0, 0.0)), "right": Vector((-4.0, 0.0, 0.0))}


def main(van, sets, out_dir, step, clip, sfx, items):
    masks = next(m for s, c, m in CA.generic_variants(sets)[clip] if s == sfx)
    src = os.path.join(van, "Bob_IdleRifle.x")
    xv = xanim.read(src)
    rest = CB.frames_of(xv)[0]
    for label, paths in items:
        clip_path, under_path = paths.split("|")
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = bpy.context.scene
        x_preview.setup_render(scene)
        scene.render.resolution_x, scene.render.resolution_y = 300, 420
        arm = x_import.load(src)
        if arm.animation_data:
            arm.animation_data.action = None
        frames = CB.frames_of(xanim.read(clip_path))
        qu = CB.frames_of(xanim.read(under_path))[0]
        print("[shown] %s %s frames 0-%d" % (label, os.path.basename(clip_path), len(frames) - 1))
        for f in range(0, len(frames), step):
            full = dict(rest)
            full.update(CB.masked(qu, frames[f], masks))
            x_import.apply_pose(arm, pose.world(xv, full))
            bpy.context.view_layer.update()
            c = arm.matrix_world @ arm.pose.bones["Bip01_Spine1"].head
            for view, off in VIEWS.items():
                cam = x_preview.camera("Cam_" + view, c + off, c)
                cam.data.type = 'ORTHO'
                cam.data.ortho_scale = 0.9
                scene.camera = cam
                scene.render.filepath = os.path.join(out_dir, label, "%s_%d.png" % (view, f))
                bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    main(a[0], a[1], a[2], int(a[3]), a[4], a[5], [x.split("=", 1) for x in a[6:]])
