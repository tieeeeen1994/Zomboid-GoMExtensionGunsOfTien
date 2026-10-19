"""Builds the stockless bodies of GoM's three break-action shotguns (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_sawn_stocks.py

Reads GoM's own DOUBLEBARREL / STEVENS_555 / TOZ34 .fbx, takes each <GUN>_BODY and saws the buttstock off just behind
the pistol grip: a plane through two points of the gun's side profile (CUTS, game units: y forward, z up; read off
side renders of GoM's textured models, 2026-10-19), everything behind it removed, the cut closed with a cap whose UVs
are taken from the stock faces around it (so it samples the same walnut). The grip, the receiver and everything ahead
of the cut are GoM's untouched vertices, so the barrels (separate parts drawn at the gun's origin) still fit.

The pieces sawn away become items (user, 2026-10-19: "we should just introduce new items"), so the same run also
writes, per gun:
- <GUN>_STOCK_OFFCUT: the part of <GUN>_BODY behind the same plane (the buttstock), capped the same way;
- <GUN>_BARREL_OFFCUTS: the front of GoM's <GUN>_BARREL_CLOSE ahead of the muzzle of its <GUN>_BARREL_SAWNOFF_CLOSE (what
  GoM's "Saw Off Shotgun Barrels" takes away), the cut closed with a steel cap that leaves the bores open.

Writes media/models_X/weapons/firearms/GunsOfTien_SawnStocks.fbx with those nodes, in GoM's mesh convention (the
imported objects keep rotation (90, 0, 0) and scale 0.01, and the default FBX export writes them back the way GoM's files
are written; see CLAUDE.md "Mesh files"), and scripts/sawn_offcuts.json, each offcut's bounds in game coordinates (x, y,
z up), from which gen_scripts.py sawn_stocks() places them on the floor. The model scripts are written by
gen_scripts.py sawn_stocks(), which also holds the attachment points.
"""

import json
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media/models_X/weapons/firearms/"
                         "GunsOfTien_SawnStocks.fbx")
BOUNDS = os.path.join(HERE, "sawn_offcuts.json")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)

# Cut plane per gun: two points (y, z) of the side profile in game units. The upper one sits in the dip of the comb
# behind the grip, the lower one just behind the step where the grip leaves the stock's lower line, so the cut runs
# down and back like the back strap of a pistol grip and leaves the whole grip.
CUTS = {
    "DOUBLEBARREL": ((-0.028, 0.010), (-0.047, -0.052)),
    "STEVENS_555": ((-0.022, 0.006), (-0.045, -0.046)),
    "TOZ34": ((-0.037, 0.009), (-0.049, -0.044)),
}


def texel(image, uv):
    w, h = image.size
    x = min(w - 1, max(0, int((uv.x % 1.0) * w)))
    y = min(h - 1, max(0, int((uv.y % 1.0) * h)))
    i = 4 * (y * w + x)
    return image.pixels[i], image.pixels[i + 1], image.pixels[i + 2]


def cut(obj, top, bottom, texture, keep_back=False):
    """Remove everything behind the plane through top and bottom (game y, z), then cap the hole. keep_back keeps the
    part behind it instead (the sawn-off buttstock)."""
    (y1, z1), (y2, z2) = top, bottom
    # mesh data is raw FBX coordinates: (game x, game y, -game z)
    p = Vector((0.0, y1, -z1))
    d = Vector((0.0, y2 - y1, -(z2 - z1)))
    n = Vector((1.0, 0.0, 0.0)).cross(d).normalized()
    if n.y > 0:                     # point the normal backwards, at the stock
        n = -n
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv = bm.loops.layers.uv.active
    before = len(bm.verts)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=p, plane_no=n, clear_outer=not keep_back,
                                 clear_inner=keep_back, dist=1e-6)
    on_cut = {v for v in res["geom_cut"] if isinstance(v, bmesh.types.BMVert)}
    boundary = [e for e in bm.edges if e.is_boundary and e.verts[0] in on_cut and e.verts[1] in on_cut]
    # The cap samples the middle of the largest stock face along the cut, at that face's texel density (halved, so
    # it stays inside that face's patch of walnut): taking each corner's UV from a neighbouring face instead
    # squeezed the cap into a thin strip along seams and showed the dark edges.
    def centre_uv(f):
        return sum((l[uv].uv for l in f.loops), Vector((0.0, 0.0))) / len(f.loops)

    def woody(f):                   # the texel there is a warm brown, not the black butt plate or steel
        r, g, b = texel(texture, centre_uv(f))
        return r > 0.12 and r > 1.25 * b

    sides = sorted({f for e in boundary for f in e.link_faces}, key=lambda f: -f.calc_area())
    side = next((f for f in sides if woody(f)), sides[0])
    uv_c = centre_uv(side)
    ratios = [(a[uv].uv - b[uv].uv).length / (a.vert.co - b.vert.co).length
              for a, b in zip(side.loops, side.loops[1:] + side.loops[:1]) if (a.vert.co - b.vert.co).length > 1e-6]
    density = 0.5 * sum(ratios) / len(ratios)
    caps = bmesh.ops.holes_fill(bm, edges=boundary, sides=0)["faces"]
    across = d.normalized()
    centre = sum((v.co for v in on_cut), Vector()) / len(on_cut)
    for f in caps:
        for loop in f.loops:
            rel = loop.vert.co - centre
            loop[uv].uv = uv_c + Vector((rel.x, rel.dot(across))) * density
    bmesh.ops.recalc_face_normals(bm, faces=caps)
    bm.to_mesh(obj.data)
    obj.data.update()
    print(f"  {obj.name}: {before} -> {len(bm.verts)} verts, {len(boundary)} cut edges, {len(caps)} cap faces")
    bm.free()


def cut_barrels(obj, y_cut, texture):
    """Keep the barrels ahead of y_cut (game y) and close the cut with a cap that leaves the bores open: scanfill takes
    the loops inside an outer loop as holes (the bores, or a tube's bore inside its wall)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv = bm.loops.layers.uv.active
    before = len(bm.verts)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    normal = Vector((0.0, -1.0, 0.0))
    res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector((0.0, y_cut, 0.0)), plane_no=normal,
                                 clear_outer=True, dist=1e-6)
    on_cut = {v for v in res["geom_cut"] if isinstance(v, bmesh.types.BMVert)}
    boundary = [e for e in bm.edges if e.is_boundary and e.verts[0] in on_cut and e.verts[1] in on_cut]

    def centre_uv(f):
        return sum((l[uv].uv for l in f.loops), Vector((0.0, 0.0))) / len(f.loops)

    def bright(f):                  # outside steel, not the dark bore
        r, g, b = texel(texture, centre_uv(f))
        return r + g + b > 0.25

    sides = sorted({f for e in boundary for f in e.link_faces}, key=lambda f: -f.calc_area())
    side = next((f for f in sides if bright(f)), sides[0])
    uv_c = centre_uv(side)
    ratios = [(a[uv].uv - b[uv].uv).length / (a.vert.co - b.vert.co).length
              for a, b in zip(side.loops, side.loops[1:] + side.loops[:1]) if (a.vert.co - b.vert.co).length > 1e-6]
    density = 0.5 * sum(ratios) / len(ratios)
    caps = [g for g in bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=boundary,
                                               normal=normal)["geom"] if isinstance(g, bmesh.types.BMFace)]
    centre = sum((v.co for v in on_cut), Vector()) / len(on_cut)
    for f in caps:
        for loop in f.loops:
            rel = loop.vert.co - centre
            loop[uv].uv = uv_c + Vector((rel.x, rel.z)) * density
    bmesh.ops.recalc_face_normals(bm, faces=caps)
    bm.to_mesh(obj.data)
    obj.data.update()
    print(f"  {obj.name}: {before} -> {len(bm.verts)} verts, {len(boundary)} cut edges, {len(caps)} cap faces")
    bm.free()


def bounds(obj):
    """(min, max) in game coordinates: mesh data is (game x, game y, -game z)."""
    ps = [(v.co.x, v.co.y, -v.co.z) for v in obj.data.vertices]
    return [round(min(p[i] for p in ps), 5) for i in range(3)], [round(max(p[i] for p in ps), 5) for i in range(3)]


def main():
    if GOM is None:
        sys.exit("Guns of Marz not found")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    keep, offcuts = [], {}
    for gun, (top, bottom) in CUTS.items():
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=f"{GOM}/models_X/weapons/firearms/{gun}.fbx")
        objs = {o.name: o for o in set(bpy.data.objects) - before}
        texture = bpy.data.images.load(f"{GOM}/textures/weapons/firearms/shotguns/{gun}.png")
        print(gun)
        body = objs.pop(f"{gun}_BODY")
        stock = body.copy()
        stock.data = body.data.copy()
        bpy.context.collection.objects.link(stock)
        body.name = body.data.name = f"{gun}_BODY_SAWNSTOCK"
        cut(body, top, bottom, texture)
        stock.name = stock.data.name = f"{gun}_STOCK_OFFCUT"
        cut(stock, top, bottom, texture, keep_back=True)
        barrels = objs.pop(f"{gun}_BARREL_CLOSE")
        y_cut = max(v.co.y for v in objs[f"{gun}_BARREL_SAWNOFF_CLOSE"].data.vertices)
        barrels.name = barrels.data.name = f"{gun}_BARREL_OFFCUTS"
        cut_barrels(barrels, y_cut, texture)
        keep += [body, stock, barrels]
        offcuts[gun] = {"stock": bounds(stock), "barrels": bounds(barrels)}
        for o in objs.values():
            bpy.data.objects.remove(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in keep:
        o.select_set(True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={'MESH'})
    print("wrote", OUT)
    with open(BOUNDS, "w") as fh:
        json.dump(offcuts, fh, indent=2)
        fh.write("\n")
    print("wrote", BOUNDS)


main()
