"""Guns of Marz's MP5 family at Guns of Tien's size (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_mp5.py

The 9x19mm SMGs share the AWC Mk9 and its mount device, so they must stand in one proportion (user, 2026-10-27): the
Uzis' (build_uzi.py, K = 0.000603 game units per real mm, the M16A2's proportion). GoM draws its MP5 family at about
0.72 of real size, consistently across the family: against the lengths Wikipedia's MP5 infobox gives, its MP5A2 is
0.726 (0.4938 units for 680 mm, fixed stock) and its MP5K 0.721 (0.2344 for 325 mm). So the whole family and its five
magazines are scaled by one factor, SCALE = 0.603 / the mean of those two = 0.833, and every magazine still fits every
gun (the MP5, MP5SD, MP5A2 and MP5K mount the same ones). The doc's earlier -13% (docs/gom_gun_scale.md) rested on an
unsourced 700 mm for the MP5; modernfirearms.net's 660 mm (retractable stock, extended) puts GoM's MP5 at 0.738 too.

Reads GoM's own MP5 / MP5SD / MP5A2 / MP5K .fbx and the MP5 nodes of magazines/smgs.fbx, scales every vertex about the
model origin (the grip, the right hand's prop bone), and writes them in GoM's mesh convention (the imported objects keep
rotation (90, 0, 0) and scale 0.01; the default FBX export writes them back the way GoM's files are written: CLAUDE.md
"Mesh files"):
    media/models_X/weapons/firearms/GunsOfTien_MP5.fbx       the guns' BODY / BOLT / STOCK nodes, GoM's names
    media/models_X/weapons/magazines/GunsOfTien_MP5_magazines.fbx  9x19Magazine20/25/30/60/100_MP5
    scripts/mp5_points.json                                    each model block: mesh, GoM's texture, attachment points
The points are GoM's (models/weapons/smgs.txt, models/ammunition/smgs_magazines.txt), times SCALE, after two
corrections Guns of Tien already made on GoM's models: the MP5 / MP5A2 `muzzle` at the end of the barrel
(MuzzlePoints.lua, scripts/muzzle_audit.py) and their `canon` for the Mk9 (Suppressors.lua, scripts/smg9_points.json).
The UVs are GoM's, so the models keep GoM's textures. gen_scripts.py mp5_family() writes the model blocks from the
JSON, under GoM's own model names (a later block replaces GoM's mesh, texture and points; its items are untouched).

The MP5K in both hands (user, 2026-10-28: held like the MP5A3, on the UMPs' rifle-hand set): GoM models it for
vanilla's pistol clips, upside down on rifle clips, and a point that turns it (Bip01_Prop1) would leave the tracers
2 x the muzzle's height off the drawn barrel (the game shoots from the gun bone x the `muzzle` point alone). So the body
is written a second time turned half a turn about the barrel at the grip, MP5K_BODY_2H, and the JSON's "two_hand" holds
its model block, GunsOfTien.MP5K_2H (gen_scripts.py one_hand()): every point turned with it, so the bolt, magazine and
sights (parts keep GoM's meshes) and the muzzle flash come upright, plus a turned `bolt_lock` (absent on GoM's MP5K, so
drawn at the origin, which the turn would otherwise leave upside down). OneHand.lua draws it while the gun is in both
hands.
"""

import json
import math
import os
import re
import sys

import bpy
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
OUT_GUNS = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_MP5.fbx")
OUT_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_MP5_magazines.fbx")
POINTS = os.path.join(HERE, "mp5_points.json")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)

K_UZI = 0.603                                    # the Uzis' proportion (build_uzi.py K x 1000)
GOM_RATIO = {"MP5A2": 0.4938 / 680.0, "MP5K": 0.2344 / 325.0}   # GoM's drawn length (mm x 1000) / real (Wikipedia)
SCALE = round(K_UZI / (1000.0 * sum(GOM_RATIO.values()) / len(GOM_RATIO)), 4)

GUNS = ("MP5", "MP5SD", "MP5A2", "MP5K")
TURN_Y = Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0))   # half a turn about the barrel (game space; the raw FBX data alike)
TWO_HAND = ("MP5K", "MP5K_2H", "MP5K_BODY_2H", ("bolt_lock",))   # GoM model, ours, turned body node, points GoM lacks
MAGAZINES = tuple("9x19Magazine%d_MP5" % n for n in (20, 25, 30, 60, 100))
# Guns of Tien's corrections of GoM's points, in GoM's size (applied before SCALE)
FIXES = {
    ("MP5", "muzzle"): (None, 0.3102, None),     # MuzzlePoints.lua: the end of the barrel (was 0.2966)
    ("MP5A2", "muzzle"): (None, 0.3067, None),   # (was 0.2966)
    ("MP5", "canon"): (0.0, 0.2796, 0.041),      # Suppressors.lua / smg9_points.json: front face of the front sight
    ("MP5A2", "canon"): (0.0, 0.2811, 0.041),    # housing, on the bore axis
}


def gom_models(path):
    """GoM's model blocks in a script file: name -> (mesh, texture, cullFace, [(id, offset, rotate)])."""
    text = open(path, encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r"\bmodel\s+(\w+)\s*\{", text):
        depth, i = 1, m.end()
        while depth:                                     # the block's own closing brace (attachments nest)
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[m.end():i - 1]
        get = lambda k: (re.search(r"\b%s\s*=\s*([^,\n]+)" % k, body) or [None, None])[1]
        atts = []
        for a in re.finditer(r"attachment\s+(\w+)\s*\{(.*?)\}", body, re.S):
            off = re.search(r"offset\s*=\s*([-\d. ]+),", a.group(2))
            rot = re.search(r"rotate\s*=\s*([-\d. ]+),", a.group(2))
            atts.append((a.group(1), [float(v) for v in off.group(1).split()] if off else [0.0, 0.0, 0.0],
                         [float(v) for v in rot.group(1).split()] if rot else [0.0, 0.0, 0.0]))
        out[m.group(1)] = (get("mesh"), get("texture"), get("cullFace"), atts)
    return out


def points():
    gom = gom_models(f"{GOM}/scripts/MarzWeapons/models/weapons/smgs.txt")
    gom.update(gom_models(f"{GOM}/scripts/MarzWeapons/models/ammunition/smgs_magazines.txt"))
    models = {}
    for name in sorted(gom):
        mesh, texture, cull, atts = gom[name]
        if not mesh:
            continue
        file, node = [s.strip() for s in mesh.split("|")]
        if file not in {"weapons/firearms/%s" % g for g in GUNS} and node not in MAGAZINES:
            continue
        ours = "weapons/magazines/GunsOfTien_MP5_magazines" if node in MAGAZINES else "weapons/firearms/GunsOfTien_MP5"
        fixed = []
        for pid, off, rot in atts:
            fix = FIXES.get((name, pid))
            if fix:
                off = [o if f is None else f for o, f in zip(off, fix)]
            fixed.append((pid, off, rot))
        for (gun, pid), fix in FIXES.items():           # points GoM's model lacks (canon on the MP5 / MP5A2)
            if gun == name and pid not in {a[0] for a in fixed}:
                fixed.append((pid, [0.0 if f is None else f for f in fix], [0.0, 0.0, 0.0]))
        models[name] = {
            "mesh": "%s|%s" % (ours, node),
            "texture": texture.strip(),
            "cullFace": cull.strip() if cull else None,
            "attachments": [[pid, [round(v * SCALE, 4) for v in off], rot] for pid, off, rot in fixed],
        }
    return models


def point_matrix(off, rot):
    """A model point as the game builds it (JOML translate . rotateXYZ: Rx . Ry . Rz, degrees)."""
    rx, ry, rz = [math.radians(a) for a in rot]
    return (Matrix.Translation(Vector(off)) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Rotation(ry, 4, 'Y')
            @ Matrix.Rotation(rz, 4, 'Z'))


def turned(off, rot):
    """The point of a mesh turned by TURN_Y that keeps the same place on it: TURN_Y x the point."""
    m = TURN_Y @ point_matrix(off, rot)
    e = m.to_3x3().to_euler('ZYX')                   # Blender's 'ZYX' = Rx . Ry . Rz
    out = ([round(v, 4) + 0.0 for v in m.to_translation()], [round(math.degrees(a), 4) + 0.0 for a in e])
    for a, b in zip(sum(map(list, point_matrix(*out)), []), sum(map(list, m), [])):
        assert abs(a - b) < 1e-3, (off, rot, out)
    return out


def two_hand(models):
    gom, name, node, missing = TWO_HAND
    src = models[gom]
    atts = [[pid, *turned(off, rot)] for pid, off, rot in src["attachments"]]
    atts += [[pid, *turned((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))] for pid in missing
             if pid not in {a[0] for a in src["attachments"]}]
    return {name: {"mesh": "weapons/firearms/GunsOfTien_MP5|%s" % node, "texture": src["texture"],
                   "cullFace": src["cullFace"], "attachments": atts}}


def main():
    if GOM is None:
        sys.exit("Guns of Marz not found")
    print("scale", SCALE, {g: round(SCALE * r * 1000.0, 4) for g, r in GOM_RATIO.items()})
    bpy.ops.wm.read_factory_settings(use_empty=True)
    guns, mags = [], []
    for path, wanted, keep in [(f"{GOM}/models_X/weapons/firearms/{g}.fbx", None, guns) for g in GUNS] + \
                              [(f"{GOM}/models_X/weapons/magazines/smgs.fbx", MAGAZINES, mags)]:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=path)
        for o in set(bpy.data.objects) - before:
            if o.type != 'MESH' or (wanted and o.name not in wanted):
                bpy.data.objects.remove(o)
                continue
            o.data.transform(Matrix.Scale(SCALE, 4))    # raw FBX data, about the model origin
            keep.append(o)
    body = next(o for o in guns if o.name.split(".")[0] == TWO_HAND[0] + "_BODY")
    up = body.copy()
    up.data = body.data.copy()
    up.data.transform(TURN_Y)                           # a rotation: winding and UVs unchanged
    up.name = up.data.name = TWO_HAND[2]
    bpy.context.scene.collection.objects.link(up)
    guns.append(up)
    for objs, out in ((guns, OUT_GUNS), (mags, OUT_MAGS)):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs:
            o.select_set(True)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={'MESH'})
        print("wrote", out, sorted(o.name for o in objs))
    data = {
        "_notes": {
            "scale": "every vertex and point of GoM's model x SCALE about the model origin (the Uzis' 0.603 of real "
                     "size / GoM's 0.72 for its MP5A2 and MP5K); textures and UVs are GoM's",
            "fixes": "MP5 / MP5A2 muzzle at the barrel's end (MuzzlePoints.lua) and canon for the Mk9 "
                     "(Suppressors.lua), applied before scaling",
        },
        "scale": SCALE,
        "models": points(),
    }
    data["_notes"]["two_hand"] = ("the MP5K held in both hands (OneHand.lua): its body turned half a turn about the "
                                  "barrel at the grip, every point turned with it (GunsOfTien.MP5K_2H)")
    data["two_hand"] = two_hand(data["models"])
    with open(POINTS, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    print("wrote", POINTS, sorted(data["models"]))


main()
