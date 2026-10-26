"""
Measure every gun of Guns of Marz and both of our mods as the game draws it (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/scale_audit.py -- <out.json>

For each item with a WeaponSprite (not thrown or melee): the sprite model's mesh plus the parts that set its length
when fitted as found (`*_Integrated_Stock_Deployed`, full-length `*_Barrel_Close`), each placed at its parent point
(offset + rotateXYZ + scale, as `ModelInstanceRenderData.makeAttachmentTransform`). Game space: +Y muzzle, +Z top,
origin at the grip (game = raw x, raw y, -raw z). Written per gun: bounds, length, height, the muzzle point, the
side silhouette (polygons in Y / Z) for `scale_audit_report.py`. Also every other part model (sights, magazines,
muzzle devices, bayonets...) with its size and how many guns list it. Node names are matched case-insensitively
(GoM's MODEL_70 script names `MODEL_70_BODY`, the file `Model_70_Body`).
"""

import glob
import json
import math
import os
import re
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


def _first(*paths):
    return next((p for p in paths if os.path.isdir(p)), None)


STEAM = _first(os.path.expanduser("~/Library/Application Support/Steam/steamapps"),
               "C:/Program Files (x86)/Steam/steamapps")
ROOTS = [os.path.join(STEAM, "workshop/content/108600/3722134990/mods/GunsOfMarz/42.16/media"),
         os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media"),
         os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")]
LENGTH_PART = re.compile(r"(_Integrated_Stock_Deployed|^Barrel_Close|_Barrel_Close)$")
NOT_ACCESSORY = ("Integrated", "Bolt_", "Slide_", "Hammer_", "Cylinder_", "Pump_", "Lever_", "Barrel_", "Underbarrel_",
                 "Bullet_", "Shellholder", "Sling", "M203", "Sawn")


def blocks(text, kind):
    """(module, name, body) of every `kind NAME { ... }` block, braces matched."""
    mod = None
    for m in re.finditer(r"\bmodule\s+(\w+)|\b%s\s+([\w\-]+)\s*\{" % kind, text):
        if m.group(1):
            mod = m.group(1)
            continue
        i, depth = m.end(), 1
        while depth:
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        yield mod, m.group(2), text[m.end():i - 1]


def vec(body, key):
    m = re.search(key + r"\s*=\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)", body)
    return [float(x) for x in m.groups()] if m else [0.0, 0.0, 0.0]


models, items = {}, {}
for root in ROOTS:
    for f in sorted(glob.glob(root + "/scripts/**/*.txt", recursive=True)):
        t = re.sub(r"/\*.*?\*/", "", open(f, encoding="utf-8", errors="ignore").read(), flags=re.S)
        for mod, name, body in blocks(t, "model"):
            mesh = re.search(r"\bmesh\s*=\s*([^,\n]+)", body)
            # the model's own scale, not an attachment point's (GoM's DOUBLEBARREL shellholder point has one)
            scale = re.search(r"^\s*scale\s*=\s*([\d.]+)", re.sub(r"attachment\s+\w+\s*\{.*?\}", "", body, flags=re.S), re.M)
            att = {}
            for a in re.finditer(r"attachment\s+(\w+)\s*\{(.*?)\}", body, re.S):
                s = re.search(r"scale\s*=\s*([-\d.]+)", a.group(2))
                att[a.group(1)] = (vec(a.group(2), "offset"), vec(a.group(2), "rotate"), float(s.group(1)) if s else 1.0)
            models[mod + "." + name] = dict(mesh=mesh.group(1).strip() if mesh else None,
                                            scale=float(scale.group(1)) if scale else 1.0, att=att)
        for mod, name, body in blocks(t, "item"):
            sprite = re.search(r"WeaponSprite\s*=\s*([\w.\-]+)", body)
            if not sprite or not re.search(r"ItemType\s*=\s*base:weapon", body, re.I):
                continue
            field = lambda k: (re.search(k + r"\s*=\s*([^,\n]+)", body) or [None, ""])[1].strip()  # noqa: E731
            items[mod + "." + name] = dict(
                sprite=sprite.group(1), swing=field("SwingAnim"), reload=field("WeaponReloadType"),
                two=field("TwoHandWeapon"),
                parts=re.findall(r"ModelWeaponPart\s*=\s*([\w.\-&]+)\s+([\w.\-]+)\s+(\w+)\s+(\w+)", body))

meshes = {}


def mesh_of(model):
    """(vertices in game space x model scale, polygons) of a model script's mesh."""
    m = models[model]
    path, node = (m["mesh"].split("|") + [None])[:2]
    fbx = next((r + "/models_X/" + path + ".fbx" for r in ROOTS[::-1]
                if os.path.exists(r + "/models_X/" + path + ".fbx")), None)
    if fbx is None:
        raise KeyError("no mesh file " + path)
    if fbx not in meshes:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=fbx)
        meshes[fbx] = {o.name.lower(): ([(v.co.x, v.co.y, -v.co.z) for v in o.data.vertices],
                                        [tuple(p.vertices) for p in o.data.polygons])
                       for o in bpy.data.objects if o.type == "MESH"}
    nodes = meshes[fbx]
    verts, polys = nodes[node.lower()] if node else next(iter(nodes.values()))
    return [tuple(c * m["scale"] for c in v) for v in verts], polys


def rotate_xyz(v, r):
    """JOML rotateXYZ (degrees): Rx * Ry * Rz applied to v."""
    x, y, z = v
    rx, ry, rz = (math.radians(a) for a in r)
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    return x, y, z


def bounds(vs):
    return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]


guns = {}
for full, it in sorted(items.items()):
    sprite = it["sprite"]
    if sprite not in models or not models[sprite]["mesh"] or it["swing"] in ("Throw", "Stab", "Spear"):
        continue
    body, polys = mesh_of(sprite)
    allv = list(body)
    sil = [[(body[i][1], body[i][2]) for i in p] for p in polys]
    used, warn = [], []
    for part, pmodel, a_self, a_parent in it["parts"]:
        pname = part.split(".")[-1]
        if not LENGTH_PART.search(pname) or "Sawnoff" in pname:
            continue
        if pmodel not in models:
            warn.append("no model " + pmodel)
            continue
        pv, pp = mesh_of(pmodel)
        o, r, s = models[sprite]["att"].get(a_parent, ([0, 0, 0], [0, 0, 0], 1.0))
        if a_self in models[pmodel]["att"]:
            warn.append("part has its own %s point: not applied" % a_self)
        placed = [tuple(o[i] + c * s for i, c in enumerate(rotate_xyz(v, r))) for v in pv]
        allv += placed
        sil += [[(placed[i][1], placed[i][2]) for i in p] for p in pp]
        used.append(pname)
    mn, mx = bounds(allv)
    muzzle = models[sprite]["att"].get("muzzle")
    guns[full] = dict(model=sprite, swing=it["swing"], reload=it["reload"], two=it["two"], y=[mn[1], mx[1]],
                      z=[mn[2], mx[2]], length=mx[1] - mn[1], height=mx[2] - mn[2],
                      muzzle_y=muzzle[0][1] if muzzle else None,
                      points={k: v[0] for k, v in models[sprite]["att"].items()}, used=used, warn=warn, sil=sil)

parts = {}
for full, it in items.items():
    for part, pmodel, a_self, a_parent in it["parts"]:
        if any(s in part for s in NOT_ACCESSORY) or pmodel not in models or not models[pmodel]["mesh"]:
            continue
        if pmodel not in parts:
            try:
                mn, mx = bounds(mesh_of(pmodel)[0])
            except KeyError as e:
                parts[pmodel] = dict(error=str(e), users=0)
                continue
            parts[pmodel] = dict(part=part, x=mx[0] - mn[0], y=mx[1] - mn[1], z=mx[2] - mn[2], users=0)
        parts[pmodel]["users"] += 1

out = sys.argv[sys.argv.index("--") + 1]
json.dump(dict(guns=guns, parts=parts), open(out, "w"), indent=1)
print("scale_audit: %d guns, %d parts -> %s" % (len(guns), len(parts), out))
