"""
Where Guns of Marz's `muzzle` points sit against the end of each gun's barrel (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/muzzle_audit.py -- <out.json> [--ours]
    py scripts/muzzle_audit_sheet.py <out.json> <sheet.png>

The engine draws the muzzle flash at the gun model's `muzzle` point and starts the bullet / tracer there
(CLAUDE.md "Gun scale"); GoM fits flash hiders, compensators and suppressors at `canon`, and only its suppressors turn
the flash off (AttachmentCustomStats.lua), so with a flash hider or compensator the flash stays at `muzzle`. Per GoM
gun model (each WeaponSprite once): the body plus the parts that set its length as found (deployed integrated stock,
full-length barrels, scale_audit.py's LENGTH_PART), the bore's front (the frontmost vertex within BORE_R of the
muzzle point's line along +Y), the muzzle and canon points, and the front of every canon part when fitted. The side
view (polygons in Y / Z) of the front of the gun goes to the sheet. The model / item parsing is scale_audit.py's.
"""

import json
import math
import sys

_src = open(__file__.replace("muzzle_audit.py", "scale_audit.py")).read()
_src = _src[:_src.index("\nguns = {}")]
_g = {"__file__": __file__.replace("muzzle_audit.py", "scale_audit.py"), "__name__": "scale_audit_parse"}
exec(compile(_src, "scale_audit.py", "exec"), _g)
models, items, mesh_of, rotate_xyz = _g["models"], _g["items"], _g["mesh_of"], _g["rotate_xyz"]
LENGTH_PART = _g["LENGTH_PART"]
OURS = ("GunsOfTien.", "GunsOfTienPost93.", "MarzGuns.FIVESEVEN")
BORE_R = 0.012                    # game units around the muzzle point's line
WINDOW = 0.20                     # how much of the gun behind the muzzle goes to the side view


def place(pv, o, r, s):
    return [tuple(o[i] + c * s for i, c in enumerate(rotate_xyz(v, r))) for v in pv]


def front_near(verts, m):
    near = [v for v in verts if math.hypot(v[0] - m[0], v[2] - m[2]) < BORE_R]
    return max(v[1] for v in near) if near else None


def front_ring(verts, m, front):
    """Centre (x, z) of the vertices within 3 mm of the bore's front: the barrel's axis at its end."""
    ring = [v for v in verts if math.hypot(v[0] - m[0], v[2] - m[2]) < BORE_R and v[1] > front - 0.003]
    xs, zs = [v[0] for v in ring], [v[2] for v in ring]
    return [(min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2, max(xs) - min(xs), max(zs) - min(zs)]


OURS_ONLY = "--ours" in sys.argv          # this mod's and Post-93's guns instead of GoM's
out = {}
for full, it in sorted(items.items()):
    sprite = it["sprite"]
    if (sprite.startswith(OURS) != OURS_ONLY or not OURS_ONLY and not sprite.startswith("MarzGuns.")
            or sprite in out or sprite not in models
            or not models[sprite]["mesh"] or it["swing"] in ("Throw", "Stab", "Spear")):
        continue
    att = models[sprite]["att"]
    if "muzzle" not in att:
        continue
    verts, polys = mesh_of(sprite)
    verts, polys = list(verts), [list(p) for p in polys]
    used = []
    for part, pmodel, a_self, a_parent in it["parts"]:
        pname = part.split(".")[-1]
        if not LENGTH_PART.search(pname) or "Sawnoff" in pname or pmodel not in models:
            continue
        pv, pp = mesh_of(pmodel)
        o, r, s = att.get(a_parent, ([0, 0, 0], [0, 0, 0], 1.0))
        base = len(verts)
        verts += place(pv, o, r, s)
        polys += [[base + i for i in p] for p in pp]
        used.append(pname)
    m = att["muzzle"][0]
    bore = front_near(verts, m)
    devices = []
    if "canon" in att:
        o, r, s = att["canon"]
        for part, pmodel, a_self, a_parent in it["parts"]:
            if a_parent != "canon" or pmodel not in models or not models[pmodel]["mesh"]:
                continue
            pv, _ = mesh_of(pmodel)
            so, sr, ss = models[pmodel]["att"].get(a_self, ([0, 0, 0], [0, 0, 0], 1.0))
            pv = [tuple(so[i] + c * ss for i, c in enumerate(rotate_xyz(v, sr))) for v in pv]
            placed = place(pv, o, r, s)
            devices.append(dict(part=part, model=pmodel, front=max(v[1] for v in placed),
                                bore_front=front_near(placed, m), suppressor="Suppressor" in part))
    keep = {i for i, v in enumerate(verts) if v[1] > m[1] - WINDOW}
    side = [[(verts[i][1], verts[i][2]) for i in p] for p in polys if any(i in keep for i in p)]
    out[sprite] = dict(items=[k for k, v in items.items() if v["sprite"] == sprite], used=used, muzzle=m,
                       canon=att["canon"][0] if "canon" in att else None, bore_front=bore,
                       ring=front_ring(verts, m, bore) if bore is not None else None,
                       top=[[(verts[i][1], verts[i][0]) for i in p] for p in polys if any(i in keep for i in p)],
                       front=max(v[1] for v in verts), devices=devices, side=side)
    print("%-28s muzzle %+.4f  bore front %s" % (sprite, m[1], "%+.4f" % bore if bore is not None else "-"))

path = sys.argv[sys.argv.index("--") + 1]  # then optionally --ours
json.dump(out, open(path, "w"))
print("muzzle_audit: %d gun models -> %s" % (len(out), path))
