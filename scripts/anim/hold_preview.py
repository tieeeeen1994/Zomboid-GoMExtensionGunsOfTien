"""
How a gun looks held: vanilla's idle and aim clips (the ones the game plays for it) with the gun as it spawns, every
part at its model-script point, rendered front / side / top (Blender 5.2, headless; TienInspectWeapon's pipeline).

    blender -b --factory-startup -P scripts/anim/hold_preview.py -- <vanilla anims_X/Bob> <out_dir> [gun ...]

gun: uzi miniuzi microuzi mp5k mp7 p90 (default: all). Writes <out_dir>/<gun>_<Idle|Aim>/<view>_<frame>.png; lay them out
with TienInspectWeapon's sheet.py / gif.py. Rifle-held guns (SwingAnim Rifle) play Bob_IdleRifle / Bob_IdleAimRifle,
pistol-held ones Bob_IdleHandgun / Bob_IdleAimHandgun: Guns of Marz ships no idle or aim clips of its own.
"""

import json
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
import x_import  # noqa: E402
import x_preview  # noqa: E402
from smg_reload import GOM, MEDIA  # noqa: E402

EVERY = int(os.environ.get("HOLD_EVERY", 3))   # render every 3rd frame (HOLD_EVERY: another step)


def point(offset, rotate=(0, 0, 0)):
    rx, ry, rz = [math.radians(a) for a in rotate]
    return (Matrix.Translation(Vector(offset)) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Rotation(ry, 4, 'Y')
            @ Matrix.Rotation(rz, 4, 'Z'))


UZI_FBX = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_%s.fbx")
# The MP7 is resized in its meshes (build_mp7.py's K; user, 2026-10-26): its points come from the builder's JSON, and
# MP7_S (its size against the 0.72 the stance was solved at) scales the places that were measured by hand.
MP7_POINTS = json.load(open(os.environ.get("GOT_MP7_POINTS") or os.path.join(ROOT, "scripts/post93/mp7_points.json")))
MP7_S = 1.0 / MP7_POINTS["_extras"]["real_mm_per_game_unit"] / 0.00072
P90_POINTS = json.load(open(os.path.join(ROOT, "scripts/post93/p90_points.json")))
# the Uzis likewise (build_uzi.py's K, the same day)
UZI_POINTS = json.load(open(os.path.join(ROOT, "scripts/uzi_points.json")))
UZI_S = UZI_POINTS["UZI"]["_extras"]["k"] / 0.00072


def _pt(gun, name):
    p = UZI_POINTS[gun][name]
    return point(p["offset"], p.get("rotate", (0, 0, 0)))
UZI_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_UZI_magazines.fbx")
AUG_POINTS = json.load(open(os.path.join(ROOT, "scripts/aug_points.json")))
AUG_FBX = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_AUG.fbx")
AUG_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx")


def _aug_pt(name):
    p = AUG_POINTS[name]
    return point(p["offset"], p.get("rotate", (0, 0, 0)))
# GOT_P93_MEDIA / GOT_MP7_POINTS: another copy of the meshes and points (a build of the old size to compare with)
P93 = os.environ.get("GOT_P93_MEDIA") or os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
P93_FBX = os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_%s.fbx")
P93_MAGS = os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx")
# (fbx, node, point in the gun's model script) per part, as models_uzi.txt / GoM's smgs.txt place them: stock
# folded, 32-round magazine (GoM's MP5 30 in the MP5K), bolt forward (bolt_fired, identity)
GUNS = {
    "uzi": dict(rifle=True, parts=[
        (UZI_FBX % "UZI", "UZI_BODY", None),
        (UZI_FBX % "UZI", "UZI_BOLT", None),
        (UZI_FBX % "UZI", "UZI_STOCK_FOLDED", None),          # no `stock` point on the model: drawn at its origin
        (UZI_MAGS, "9x19Magazine32_UZI", _pt("UZI", "magazine")),
    ]),
    "miniuzi": dict(rifle=False, parts=[
        (UZI_FBX % "MINIUZI", "MINIUZI_BODY", None),
        (UZI_FBX % "MINIUZI", "MINIUZI_BOLT", None),
        (UZI_FBX % "MINIUZI", "MINIUZI_STOCK", _pt("MINIUZI", "stock_folded")),
        (UZI_MAGS, "9x19Magazine32_UZI", _pt("MINIUZI", "magazine")),
    ]),
    "microuzi": dict(rifle=False, parts=[
        (UZI_FBX % "MICROUZI", "MICROUZI_BODY", None),
        (UZI_FBX % "MICROUZI", "MICROUZI_BOLT", None),
        (UZI_FBX % "MICROUZI", "MICROUZI_STOCK", _pt("MICROUZI", "stock_folded")),
        (UZI_MAGS, "9x19Magazine32_UZI", _pt("MICROUZI", "magazine")),
    ]),
    # Post-93's MP7A1: stock folded (at its stock_folded point), foregrip unfolded (foregrip_deployed, turned 90),
    # 30-round magazine
    "mp7": dict(rifle=False, parts=[
        (P93_FBX % "MP7A1", "MP7A1_BODY", None),
        (P93_FBX % "MP7A1", "MP7A1_BOLT", None),
        (P93_FBX % "MP7A1", "MP7A1_STOCK", point(MP7_POINTS["stock_folded"]["offset"])),
        (P93_FBX % "MP7A1", "MP7A1_FOREGRIP", point(MP7_POINTS["foregrip_deployed"]["offset"], (-90, 0, 0))),
        (P93_MAGS, "46x30Magazine30_MP7", point(MP7_POINTS["magazine"]["offset"], (-180, 0, -180))),
    ]),
    # Post-93's P90 TR, held like a pistol (vanilla's handgun idle and aim), its 50-round magazine on top
    "p90": dict(rifle=False, parts=[
        (P93_FBX % "P90TR", "P90TR_BODY", None),
        (P93_FBX % "P90TR", "P90TR_BOLT", None),
        (os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx"), "57x28Magazine50_P90",
         point(P90_POINTS["magazine"]["offset"], P90_POINTS["magazine"]["rotate"])),
    ]),
    # the main mod's Steyr AUG A1 (build_aug.py), held as a rifle: 30-round magazine, front grip down (aug) or folded
    # under the barrel (aug_folded)
    "aug": dict(rifle=True, parts=[
        (AUG_FBX, "AUG_BODY", None),
        (AUG_FBX, "AUG_BOLT", None),
        (AUG_FBX, "AUG_FOREGRIP", _aug_pt("foregrip_deployed")),
        (AUG_MAGS, "556x45Magazine30_AUG", _aug_pt("magazine")),
    ]),
    "aug_folded": dict(rifle=True, parts=[
        (AUG_FBX, "AUG_BODY", None),
        (AUG_FBX, "AUG_BOLT", None),
        (AUG_FBX, "AUG_FOREGRIP", _aug_pt("foregrip_folded")),
        (AUG_MAGS, "556x45Magazine30_AUG", _aug_pt("magazine")),
    ]),
    # GoM's FAMAS (models/weapons/assault_rifles.txt: magazine point 0 -0.0763 0.0146), its 30-round STANAG
    "famas": dict(rifle=True, parts=[
        (os.path.join(GOM, "models_X/weapons/firearms/FAMAS.fbx"), "FAMAS_BODY", None),
        (os.path.join(GOM, "models_X/weapons/firearms/FAMAS.fbx"), "FAMAS_BOLT", None),
        (os.path.join(GOM, "models_X/weapons/magazines/assault_rifles.fbx"), "556x45Magazine30_STANAG",
         point((0.0, -0.0763, 0.0146))),
    ]),
    "mp5k": dict(rifle=False, parts=[
        (os.path.join(GOM, "models_X/weapons/firearms/MP5K.fbx"), "MP5K_BODY", None),
        (os.path.join(GOM, "models_X/weapons/firearms/MP5K.fbx"), "MP5K_BOLT", None),
        (os.path.join(GOM, "models_X/weapons/magazines/smgs.fbx"), "9x19Magazine30_MP5",
         point((0.0, 0.1196, -0.0388), (171.7924, 0.0, 180.0))),
    ]),
}
CLIPS = {True: {"Idle": "Bob_IdleRifle.x", "Aim": "Bob_IdleAimRifle.x"},
         False: {"Idle": "Bob_IdleHandgun.x", "Aim": "Bob_IdleAimHandgun.x"}}
# HOLD_SET=<Set>: a rifle-held gun on a built set's idle and aim instead of vanilla's (rifle_hand.py's output under
# tmp/anim/rifle/<Set>/clips, e.g. Bullpup)
HOLD_SET = os.environ.get("HOLD_SET")
if HOLD_SET:
    # HOLD_DIR: another build's output root; HOLD_IDLE / HOLD_AIM: other clips of the set (e.g. IdleNoAimRifle)
    _d = os.path.join(os.environ.get("HOLD_DIR") or os.path.join(ROOT, "tmp", "anim", "rifle"), HOLD_SET, "clips")
    CLIPS[True] = {"Idle": os.path.join(_d, "GunsOfTien_Compact%s_%s.x" % (HOLD_SET, os.environ.get("HOLD_IDLE", "IdleRifle"))),
                   "Aim": os.path.join(_d, "GunsOfTien_Compact%s_%s.x" % (HOLD_SET, os.environ.get("HOLD_AIM", "IdleAimRifle")))}
VIEWS = {
    # name: (camera location, look-at), Blender space (Z up, the character faces -Y, its left is +X)
    "front": ((0.45, -1.7, 0.95), (0.0, -0.16, 0.62)),
    "side": ((1.75, -0.5, 0.85), (0.0, -0.16, 0.62)),
    "top": ((0.45, -0.65, 1.95), (0.0, -0.16, 0.62)),
}


def load_part(arm_ob, path, node, mat):
    """One FBX node as a mesh on Bip01_Prop1, in game space (the file's Z negated), moved to its point."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = list(set(bpy.data.objects) - before)
    src = next(o for o in new if o.name.split(".")[0] == node)
    verts = [Vector((v.co.x, v.co.y, -v.co.z)) for v in src.data.vertices]
    if mat is not None:
        verts = [mat @ v for v in verts]
    me = bpy.data.meshes.new(node)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(reversed(p.vertices)) for p in src.data.polygons])
    me.update()
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    ob = bpy.data.objects.new(node, me)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new(node)
    m.diffuse_color = (0.16, 0.16, 0.17, 1.0) if "Magazine" not in node else (0.35, 0.36, 0.4, 1.0)
    me.materials.append(m)
    x_preview.attach_to_bone(ob, arm_ob, "Bip01_Prop1")


def render(src_dir, out_dir, gun):
    spec = GUNS[gun]
    for name, clip in CLIPS[spec["rifle"]].items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        arm_ob = x_import.load(os.path.join(src_dir, clip))
        for path, node, mat in spec["parts"]:
            load_part(arm_ob, path, node, mat)
        scene = bpy.context.scene
        x_preview.setup_render(scene)
        scene.render.resolution_x = scene.render.resolution_y = 420
        cams = {}
        for view, (loc, tgt) in VIEWS.items():
            cam = x_preview.camera("Cam_" + view, loc, tgt)
            cam.data.ortho_scale = 0.9
            cams[view] = cam
        d = os.path.join(out_dir, "%s_%s" % (gun, name))
        os.makedirs(d, exist_ok=True)
        for f in range(scene.frame_start, scene.frame_end + 1, EVERY):
            scene.frame_set(f)
            for view, cam in cams.items():
                scene.camera = cam
                scene.render.filepath = os.path.join(d, "%s_%03d.png" % (view, f))
                bpy.ops.render.render(write_still=True)
        print("[hold] %s %s: %s, frames %d-%d" % (gun, name, clip, scene.frame_start, scene.frame_end))


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    for gun in args[2:] or list(GUNS):
        render(args[0], args[1], gun)
