"""Belt link models and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_links.py -- [--size 1024] [--samples 48]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/parts/GunsOfTien_Links.fbx     M27_Link, M13_Link (one loose link each), LinkBox_M27,
                                                      LinkBox_M13 (a box holding one belt's worth)
    M/textures/weapons/GunsOfTien/<node>.png          64 px (links), 128 px (boxes)
    scripts/links_bounds.json                         each node's bounds (gen_scripts.py rests them on the floor)

The M27 (5.56mm, M249) and M13 (7.62mm, M60) disintegrating links, after the user's photos of M27 links: a wide loop
round one round and a pair of narrow loops round the next, one at each end of it, joined by S-bends (LINKS); a fired
round's link falls free (docs/design.md 4e). Drawn at GoM's rifle scale (0.65, as the guns they feed and the M249's box), the round's axis
along +Y, loops sized to the cases they hold. The boxes are olive drab
cardboard cartons stencilled in yellow with the link and its count.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import json
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
import build_mp7 as kit  # noqa: E402

MEDIA = os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
FBX = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTien_Links.fbx")
BOUNDS_JSON = os.path.join(HERE, "links_bounds.json")

K = 0.00065
kit.K = K
MATS = ["steel", "card", "ink"]
kit.MATS[:] = MATS
for ch, rows in {"C": ["111", "100", "100", "100", "111"], "T": ["111", "010", "010", "010", "010"],
                 "O": ["111", "101", "101", "101", "111"], "5": ["111", "100", "111", "001", "111"],
                 "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"],
                 "L": ["100", "100", "100", "100", "111"], "K": ["101", "101", "110", "101", "101"],
                 "B": ["110", "101", "110", "101", "110"], "H": ["101", "101", "111", "101", "101"]}.items():
    kit.FONT.setdefault(ch, rows)

# Each link is one piece of stamped steel, modelled on the user's photos of M27 links (2026-10-22): a WIDE loop round
# one cartridge (a U open at the top, a round hole stamped in its side) and, round the next cartridge, a PAIR of narrow
# loops, one at each end of the wide loop and directly beside it along the round, so the gap between them is exactly
# the wide loop's length (the next link's wide loop sits there: that is how they chain into a belt). Each narrow loop
# joins the wide loop at its end through a short S-bend under the two cartridges, and ends in a small rounded tab.
# name: (loop radius, wide loop length, narrow loop width, round pitch, opening degrees), mm
LINKS = {
    "M27_Link": (4.9, 11.0, 4.5, 10.4, 150.0),
    "M13_Link": (6.2, 13.5, 5.5, 12.8, 150.0),
}
BOXES = {  # name: (size x, y, z mm, stencil lines)
    "LinkBox_M27": ((60.0, 95.0, 70.0), ("LINK M27", "200")),
    "LinkBox_M13": ((70.0, 110.0, 80.0), ("LINK M13", "100")),
}


def ring(b, cx, cz, y0, y1, r, t, gap_deg, seg=12):
    """An open steel loop about +Y (the round's axis) at (cx, cz), from y0 to y1, sheet thickness t, open at the top
    over gap_deg degrees (the round snaps in there), closed at the bottom where the joining strip runs."""
    a0 = math.radians(90.0 + gap_deg / 2.0)
    a1 = math.radians(450.0 - gap_deg / 2.0)
    outer = [(cx + (r + t) * math.cos(a0 + (a1 - a0) * k / seg), cz + (r + t) * math.sin(a0 + (a1 - a0) * k / seg))
             for k in range(seg + 1)]
    inner = [(cx + r * math.cos(a0 + (a1 - a0) * k / seg), cz + r * math.sin(a0 + (a1 - a0) * k / seg))
             for k in range(seg + 1)]
    # strip() bands two polylines in the YZ plane along X: built there, then x and y swapped (a mirror, so the
    # faces are turned back round), which puts the loop about +Y
    import bmesh
    verts = b.strip(outer, inner, y0, y1, mat="steel")
    for v in verts:
        v.co.x, v.co.y = v.co.y, v.co.x
    bmesh.ops.reverse_faces(b.bm, faces=list({f for v in verts for f in v.link_faces}))
    return verts


def s_bend(b, r, pitch, t, y0, y1, steps=8):
    """The S-bend joining a narrow loop (round at x 0) to the wide loop (round at x pitch) under the two rounds: from
    the bottom of one loop up over the gap between the rounds and down to the bottom of the other."""
    pts = []
    for k in range(steps + 1):
        u = k / steps
        x = pitch * u
        z = -r + 0.45 * r * math.sin(math.pi * u) ** 2          # rises between the rounds
        pts.append((x, z))
    outer = [(x, z - t) for x, z in pts]
    import bmesh
    verts = b.strip(outer, pts, y0, y1, mat="steel")
    for v in verts:
        v.co.x, v.co.y = v.co.y, v.co.x
    bmesh.ops.reverse_faces(b.bm, faces=list({f for v in verts for f in v.link_faces}))


def build_link(name):
    r, length, w, pitch, opening = LINKS[name]
    b = kit.Builder()
    t = 0.8                                    # thicker than the real 0.5 mm sheet, so it reads at icon size
    half = length / 2.0
    ring(b, pitch, 0.0, -half, half, r, t, opening)                       # the wide loop
    for y0, y1 in ((half, half + w), (-half - w, -half)):                 # the pair, one at each end
        ring(b, 0.0, 0.0, y0, y1, r, t, opening)
        s_bend(b, r + t * 0.5, pitch, t, y0, y1)
        # the rounded tab at the free end of the narrow loop (the side away from the wide loop)
        a = math.radians(90.0 + opening / 2.0)
        cx, cz = (r + t / 2.0) * math.cos(a), (r + t / 2.0) * math.sin(a)
        b.lathe("y", (cx, 0.0, cz), [(y0 + w * 0.2, 0.0), (y0 + w * 0.2, 0.9), (y1 - w * 0.2, 0.9),
                                     (y1 - w * 0.2, 0.0)], seg=8, mat="steel")
    return b.to_object(name)


def build_box(name):
    (sx, sy, sz), _ = BOXES[name]
    b = kit.Builder()
    b.box(-sx / 2.0, sx / 2.0, -sy / 2.0, sy / 2.0, 0.0, sz, mat="card", bevel=1.2)
    b.box(-sx / 2.0 - 0.6, sx / 2.0 + 0.6, -sy / 2.0 - 0.6, sy / 2.0 + 0.6, sz - 12.0, sz + 0.6, mat="card",
          bevel=0.8)                                                          # the lid's rim
    return b.to_object(name)


# blackened (phosphated) steel, as the photographed links; olive drab card; yellow stencil ink
BASE = {"steel": (34, 34, 36), "card": (96, 98, 70), "ink": (190, 165, 70)}


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, m in enumerate(MATS):
        col[mat == i] = BASE[m]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    if kind in LINKS:
        r, length, w, pitch, _ = LINKS[kind]
        steel = mat == MATS.index("steel")
        side = np.hypot(np.abs(x - pitch) - 0.0, z) > r - 0.2                  # the loop's outer skin
        hole = steel & side & (x > pitch + r * 0.55) & (np.hypot(y, z + r * 0.35) < 1.8)
        col[hole] = 18
    if kind in BOXES:
        (sx, sy, sz), lines = BOXES[kind]
        card = mat == MATS.index("card")
        # the stencil on both long sides, reading the right way in game (left side u = +L: along -y; right side -L)
        for side, sign in ((n[..., 0] > 0.7, -1.0), (n[..., 0] < -0.7, 1.0)):
            u = sign * y
            for k, text in enumerate(lines):
                col[card & side & kit.text_mask(u, z, text, -sy / 2.0 + 10.0, sz - 30.0 - k * 16.0, 9.0)] = \
                    BASE["ink"]
        col[card & (np.abs(z - (sz - 12.0)) < 0.6)] *= 0.6
    p_n = kit.vnoise(p, 2.0, 7)
    col *= (0.9 + 0.2 * p_n)[..., None]
    ao = maps["occ"][..., 1]
    col *= (0.75 + 0.25 * np.clip(ao, 0, 1))[..., None]
    e = np.clip(maps["occ"][..., 2] * 9.0, 0, 1)
    col += (e * 40.0)[..., None] * (mat == MATS.index("steel"))[..., None]
    return np.clip(col, 0, 255)


def texture(ob, kind, size, path):
    bake = max(size * 4, 512)
    maps = kit.bake_maps(ob, [ob], bake)
    col = paint(maps, kind)
    col = kit.dilate(col, maps["cover"], 4 * (bake // size))
    kit.save_png(col, size, path)


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
    objs = [build_link(n) for n in LINKS] + [build_box(n) for n in BOXES]
    for o in objs:
        kit.unwrap([o], 0.02)
    os.makedirs(TEX_DIR, exist_ok=True)
    for o in objs:
        texture(o, o.name, 64 if o.name in LINKS else 128, os.path.join(TEX_DIR, o.name + ".png"))
    bounds = {o.name: kit.bounds_of(o) for o in objs}
    with open(BOUNDS_JSON, "w") as fh:
        json.dump(bounds, fh, indent=2)
        fh.write("\n")
    kit.export(objs, FBX)
    for name, bd in bounds.items():
        print("%-14s tris %4d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
