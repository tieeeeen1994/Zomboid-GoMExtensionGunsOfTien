"""Our short Picatinny rails, drawn for GoM's optional Picatinny_Rail_* items on guns where its 125 mm rail has no
room (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_rails.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/parts/GunsOfTien_rails.fbx   AUG_RAIL_LEFT, AUG_RAIL_RIGHT, UZI_RAIL_UP, UZI_RAIL_DOWN,
                                                    UZI_RAIL_LEFT, MINIUZI_RAIL_UP, MINIUZI_RAIL_DOWN, MINIUZI_RAIL_LEFT
    M/textures/weapons/GunsOfTien/Rails.png         128 atlas, black anodised (the AUG's "dark")

User, 2026-10-30: the AUG A1 takes GoM's left and right rails, the Uzi and Mini Uzi its top, bottom and left ones, each
drawn as a short rail of our own sized to the room the gun has (GoM's model is 125 mm long whatever the gun). The items
stay GoM's (MarzGuns.Picatinny_Rail_Left ...); the gun's ModelWeaponPart line names one of these models instead
(gen_scripts.py; Post-93's gen_post93_guns.py for the A3s). Every rail is modelled upright (+Z top, +X the gun's left,
+Y the muzzle, real mm, kit.picatinny()'s MIL-STD-1913 profile) with its origin at the gun's point for it, and the
gun's own build script keeps where that is:
- AUG_RAIL_LEFT (moved from Post-93's build_aug3.py, where only the A3s drew it) and AUG_RAIL_RIGHT: build_aug.py
  LEFT_RAIL / RIGHT_RAIL, origins on the receiver's faces, drawn on the A1 and on every A3-receiver AUG (left only:
  the A3s have an integral right rail); two screws through the end pads.
- <GUN>_RAIL_UP: build_uzi.py RAILS: a saddle over the top cover with jaws down the receiver's sides (the clamp-on
  rails of Vector Arms and BWE), the rail on it; origin = the saddle's top at the rail's middle.
- <GUN>_RAIL_DOWN under the handguard (origin on its underside), <GUN>_RAIL_LEFT on its left face, as the AUG's.
The Uzis are held like a pistol: their points turn these upright models with the gun (build_uzi.py points()).
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_uzi as uz  # noqa: E402  (sets kit.MATS to the Uzi's; build_aug, imported after it, sets the AUG's)
import build_aug as a1  # noqa: E402

kit = a1.kit
K = a1.K
FBX = os.path.join(a1.MEDIA, "models_X/weapons/parts/GunsOfTien_rails.fbx")
TEXTURE = os.path.join(a1.TEX_DIR, "Rails.png")


def screw(b, at, sign):
    """A screw head standing out along sign * X from a face at `at`."""
    b.lathe("x", at, [(0.0, 0), (0.0, 2.2), (sign * 2.8, 2.2), (sign * 3.2, 1.6), (sign * 3.2, 0)], seg=8,
            mat="metal")


def side_rail(name, length, teeth, sign):
    """Origin on the gun's face, the rail standing out along sign * X (+1 the gun's left, -1 its right)."""
    b = kit.Builder()
    half = length / 2.0
    kit.picatinny(b, -half, half, lambda u, h, yy: Vector((sign * h, yy, u)), base_h=teeth[0], tooth_h=teeth[1],
                  mat="dark")
    for yy in (-half + 3.0, half - 3.0):                   # the two screws through the end pads
        screw(b, (0, yy, 0), sign)
    return b.to_object(name)


def top_rail(name, spec):
    """Origin = the saddle's top (the rail's mounting face) at the rail's middle; jaws down the receiver's sides."""
    b = kit.Builder()
    half = (spec["L"][1] - spec["L"][0]) / 2.0
    w, drop = spec["half"], spec["mount"] - spec["cover_lo"]
    b.box(-w, w, -half, half, -2.2, 0.0, mat="metal", bevel=0.6)
    for s in (1, -1):
        x0, x1 = sorted((s * (w - 2.0), s * w))
        b.box(x0, x1, -half, half, -drop, 0.0, mat="metal", bevel=0.4)
        for yy in (-half + 6.0, half - 6.0):               # the clamp screws through the jaws
            screw(b, (s * w, yy, -drop / 2.0), s)
    kit.picatinny(b, -half, half, lambda u, h, yy: Vector((u, yy, h)), base_h=uz.RAIL_TEETH[0],
                  tooth_h=uz.RAIL_TEETH[1], mat="dark")
    return b.to_object(name)


def bottom_rail(name, spec):
    """Origin on the handguard's underside at the rail's middle, the crossbars facing down."""
    b = kit.Builder()
    half = (spec["L"][1] - spec["L"][0]) / 2.0
    kit.picatinny(b, -half, half, lambda u, h, yy: Vector((u, yy, -h)), base_h=uz.RAIL_TEETH[0],
                  tooth_h=uz.RAIL_TEETH[1], mat="dark")
    return b.to_object(name)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.seed = 0
    scene.cycles.use_denoising = False
    scene.render.bake.margin = 0
    scene.world = bpy.data.worlds.new("w")
    scene.world.color = (0, 0, 0)
    os.makedirs(a1.TEX_DIR, exist_ok=True)

    teeth = (a1.SIDE_RAIL_BASE, a1.SIDE_RAIL_TEETH)
    rails = [side_rail("AUG_RAIL_LEFT", a1.LEFT_RAIL[1] - a1.LEFT_RAIL[0], teeth, 1),
             side_rail("AUG_RAIL_RIGHT", a1.RIGHT_RAIL[1] - a1.RIGHT_RAIL[0], teeth, -1)]
    for kind, r in uz.RAILS.items():
        rails += [top_rail(kind + "_RAIL_UP", r["up"]), bottom_rail(kind + "_RAIL_DOWN", r["down"]),
                  side_rail(kind + "_RAIL_LEFT", r["left"]["L"][1] - r["left"]["L"][0], uz.SIDE_RAIL_TEETH, 1)]
    kit.unwrap(rails, 0.012)
    a1.texture([a1.bake(o, [o], 128) for o in rails], ["bolt"] * len(rails), 128, TEXTURE)
    bounds = {o.name: kit.bounds_of(o) for o in rails}
    kit.export(rails, FBX)
    for name, bb in bounds.items():
        print("RAILS %-20s tris %5d  min %s  max %s" % (name, bb["tris"], bb["min"], bb["max"]))


if __name__ == "__main__":
    main()
