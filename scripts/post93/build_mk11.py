"""Knight's Mk 11 Mod 0 (SOCOM, 2000) from Guns of Marz's AR15 and the main mod's SR-25 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_mk11.py

User, 2026-11-12 (docs/post93_design.md "Mk 11 Mod 0"): the SR-25's sniper version as SOCOM issued it, Post-93, shown
as "Mk 11 Mod 0 Semi-Automatic Rifle". Unlike the 1990 SR-25 it is moddable: no integrated scope, bipod or suppressor
("The Mk 11 will be moddable. Like no integrated parts. I will have integrated picatinny rails though"); its rails are
modelled in the body (the handguard's four sides, the receiver's flat top) and are hidden required parts in game that
GoM's optics, foregrips, bipods, lights and lasers mount on.

The receiver, grip and stock are the SR-25's (build_sr25.py: GoM's AR15 mapped onto the SR-25's size; the same KAC
lower and A2 stock). The rest from Commons "SR-25 pic02.jpg" (CC BY 2.0: a Mk 11 with its rail handguard, scope,
Harris bipod and suppressor, on white; references/sr25), scaled by the SR-25's own stock and grip (0.935 px a mm: the
upper receiver's front then lands 182 mm ahead of the grip against the model's 194, the magazine well's front 176
against 182): KAC's rail handguard from the receiver to 545 mm ahead of the grip, four Picatinny rails; the 20" barrel
out of it to its muzzle at 700 (the chamber at 187, as on the SR-25); the folded flip-up sights on the top rail.

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_MK11.fbx   MK11_BODY, MK11_BOLT, MK11_CHARGING_HANDLE
    scripts/post93/mk11_points.json                         points: GoM's AR15 ones mapped as on the SR-25, the
                                                            muzzle and canon at the barrel's end, the rails' parts
The gun keeps GoM's AR15 texture; its magazines are the main mod's KAC 20 and Post-93's PMAGs.
"""

import json
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import build_sr25 as sr  # noqa: E402

ROOT = sr.ROOT
P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
OUT_GUN = os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_MK11.fbx")
POINTS = os.path.join(HERE, "mk11_points.json")
SR25_POINTS = os.path.join(HERE, "..", "sr25_points.json")
R = sr.R

HG = (194.0, 545.0)                # the rail handguard: from the receiver's front to its front ring (mm ahead of grip)
RECV_RAIL_TOP = 71.5               # GoM's AR15 flat top's crossbar tops (mm over the grip origin, measured on the mapped
                                   # mesh; its fixed rear sight stands at 78). GoM's AR15 takes no optics: its model's
                                   # scope point is the M16A3's, over a rail on the carry handle, 46 mm higher, so the
                                   # Mk 11's is set by our guns' relation to GoM's optics (0.0032 under the crossbars)
HG_HALF, HG_BOT = 25.0, -30.0      # the handguard's body: half width, bottom under the bore (mm); its top under the top
                                   # rail, whose crossbars are flush with the receiver's
RAIL_BASE, RAIL_TOOTH = (15.6, 3.0), (21.2, 4.0)   # Picatinny: base width / height, crossbar width / height
PITCH, TOOTH_LEN = 10.0, 5.3
MUZZLE, BARREL_R = 700.0, 11.0     # 20" heavy barrel, its end (where the SCAR-H's mount device goes)
FRONT_SIGHT = (520.0, 538.0)       # the folded flip-up front sight on the top rail
SCOPE_Y = 120.0                    # GoM's optics: over the receiver's front half and the handguard's rear


def prism(bm, uv, patch, section, y0, y1):
    """A prism along y (game mm) of a convex cross-section [(x, z)] (counter-clockwise seen from the muzzle), capped."""
    rings = [[bm.verts.new((x * R, y * R, -z * R)) for x, z in section] for y in (y0, y1)]
    n = len(section)
    a, b = rings
    faces = [bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])) for k in range(n)]
    faces.append(bm.faces.new(list(reversed(a))))
    faces.append(bm.faces.new(b))
    sr.paint(uv, patch, faces)


def chamfered(xa, xb, za, zb, c):
    """A rectangle's cross-section with its four corners chamfered by c."""
    return [(xb, za + c), (xb, zb - c), (xb - c, zb), (xa + c, zb), (xa, zb - c), (xa, za + c), (xa + c, za),
            (xb - c, za)]


# Picatinny (MIL-STD-1913) in (across, outward) mm: the spine, and the crossbars with their 45-degree flanks (21.2 mm
# at the widest, flat 15.6 mm faces); rails were plain boxes until 2026-11-12 (user: "why is the Mk 11 blocky")
SPINE = [(-7.8, 0.0), (7.8, 0.0), (7.8, RAIL_BASE[1]), (-7.8, RAIL_BASE[1])]
CROSSBAR = [(-10.6, 0.0), (10.6, 0.0), (10.6, 1.2), (7.8, RAIL_TOOTH[1]), (-7.8, RAIL_TOOTH[1]), (-10.6, 1.2)]


def rail(bm, uv, patch, y0, y1, side, centre_h, base_out, teeth_out):
    """A Picatinny rail along y on one side ("top", "bottom", "left", "right"): the spine from `base_out` (mm from
    the bore axis, or from the middle for the sides), the crossbars from `teeth_out`; `centre_h` the bore (top /
    bottom) or the side rails' height."""
    def section(prof, out0):
        pts = []
        for u, t in prof:
            o = out0 + t
            if side == "top":
                pts.append((u, centre_h + o))
            elif side == "bottom":
                pts.append((-u, centre_h - o))
            elif side == "left":
                pts.append((o, centre_h - u))
            else:
                pts.append((-o, centre_h + u))
        return pts
    prism(bm, uv, patch, section(SPINE, base_out), y0, y1)
    y = y0 + 4.0
    while y + TOOTH_LEN <= y1 - 2.0:
        prism(bm, uv, patch, section(CROSSBAR, teeth_out), y, y + TOOTH_LEN)
        y += PITCH


def build_gun(scope_mm):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f"{sr.GOM}/models_X/weapons/firearms/AR15.fbx")
    objs = {o.name.split(".")[0]: o for o in set(bpy.data.objects) - before if o.type == 'MESH'}
    body = objs["AR15_BODY"]
    bm = bmesh.new()
    bm.from_mesh(body.data)
    uv = bm.loops.layers.uv.active
    comps = sr.islands(bm)
    ahead = [c for c in comps if min(sr.gy(v) for v in c) >= sr.CUT]
    barrel = max((c for c in ahead if max(v.co.x for v in c) / R < 12.0),
                 key=lambda c: max(sr.gy(v) for v in c) - min(sr.gy(v) for v in c))
    guard = max(ahead, key=lambda c: max(abs(v.co.x) for v in c))
    zs = [sr.gz(v) for v in barrel]
    bore = (min(zs) + max(zs)) / 2.0
    steel, black = sr.uv_patch(bm, uv, barrel), sr.uv_patch(bm, uv, guard)
    bmesh.ops.delete(bm, geom=[v for c in ahead for v in c], context='VERTS')
    sr.grow_mesh(bm)
    B = bore * sr.GROW_Z
    old = set(bm.faces)
    # the 20" barrel out of the handguard, a plain end where the SCAR-H's mount device goes
    sr.lathe(bm, uv, steel, B, [(HG[0] - 10.0, BARREL_R), (MUZZLE - 1.5, BARREL_R), (MUZZLE, BARREL_R - 1.2),
                                (MUZZLE, 3.5)], seg=20)
    # the four rails' heights: the top crossbars flush with the receiver's flat top
    top_face = RECV_RAIL_TOP - B
    tbase = top_face - RAIL_TOOTH[1] - RAIL_BASE[1]
    HG_TOP = tbase
    # the handguard: KAC's tube with its corners chamfered away (the rails on its four flats), a slightly larger front
    # ring and a thin collar against the receiver
    za, zb = B + HG_BOT, B + HG_TOP
    prism(bm, uv, black, chamfered(-HG_HALF, HG_HALF, za, zb, 11.0), HG[0] + 6.0, HG[1] - 8.0)
    prism(bm, uv, black, chamfered(-HG_HALF - 1.5, HG_HALF + 1.5, za - 1.5, zb + 1.0, 12.0), HG[1] - 8.0, HG[1])
    prism(bm, uv, black, chamfered(-HG_HALF + 3.0, HG_HALF - 3.0, za + 3.0, zb, 10.0), HG[0], HG[0] + 6.0)
    mid = (za + zb) / 2.0
    rail(bm, uv, black, HG[0], HG[1] - 8.0, "top", B, tbase, tbase + RAIL_BASE[1])
    rail(bm, uv, black, HG[0] + 20.0, HG[1] - 8.0, "bottom", B, -HG_BOT, -HG_BOT + RAIL_BASE[1])
    for side in ("left", "right"):
        rail(bm, uv, black, HG[0] + 120.0, HG[1] - 8.0, side, mid, HG_HALF, HG_HALF + RAIL_BASE[1])
    # the flip-up sights, folded flat on the rails
    # the folded flip-up front sight (GoM's AR15 receiver already has its fixed rear sight block on the flat top)
    y0, y1 = FRONT_SIGHT
    sr.box(bm, uv, black, (0.0, (y0 + y1) / 2.0, B + top_face + 3.0), (17.0, y1 - y0, 6.0))
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in old])
    bm.to_mesh(body.data)
    bm.free()
    for name in ("AR15_BOLT", "AR15_CHARGING_HANDLE"):
        b2 = bmesh.new()
        b2.from_mesh(objs[name].data)
        sr.grow_mesh(b2)
        b2.to_mesh(objs[name].data)
        b2.free()
    for old_name, new in (("AR15_BODY", "MK11_BODY"), ("AR15_BOLT", "MK11_BOLT"),
                          ("AR15_CHARGING_HANDLE", "MK11_CHARGING_HANDLE")):
        objs[old_name].name = objs[old_name].data.name = new
    for o in set(bpy.data.objects) - before:
        if not o.name.startswith("MK11_"):
            bpy.data.objects.remove(o)
    faces = {"top": B + top_face, "bottom": B + HG_BOT - RAIL_BASE[1] - RAIL_TOOTH[1],
             "side": HG_HALF + RAIL_BASE[1] + RAIL_TOOTH[1], "bore": B, "side_h": B + (HG_TOP + HG_BOT) / 2.0}
    return [bpy.data.objects[n] for n in ("MK11_BODY", "MK11_BOLT", "MK11_CHARGING_HANDLE")], faces


def g(v):
    return round(v * R, 4) + 0.0


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sr25 = json.load(open(SR25_POINTS))
    gun, f = build_gun(None)
    B = f["bore"]
    pts = {k: sr25[k] for k in ("magazine", "bolt_fired", "charging_handle_open", "world")}
    # GoM's relations for parts on rails (the main mod's Uzis / MDRx): optics 0.0032 under the top crossbars, foregrips
    # 0.003 above the bottom crossbars' faces, lights 0.0007 out from the side crossbars', lasers 0.0018 out and 0.0008
    # lower; GoM's bipod sits 0.0044 under its foregrip point (its AR15)
    pts.update({
        "muzzle": {"offset": [0.0, g(MUZZLE), g(B)], "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": [0.0, g(MUZZLE), g(B)], "rotate": [0.0, 0.0, 0.0]},
        "scope": {"offset": [0.0, g(SCOPE_Y), round(g(f["top"]) - 0.0032, 4)], "rotate": [0.0, 0.0, 0.0]},
        "foregrip": {"offset": [0.0, g(420.0), round(g(f["bottom"]) + 0.003, 4)], "rotate": [0.0, 0.0, 0.0]},
        "bipod": {"offset": [0.0, g(500.0), round(g(f["bottom"]) + 0.003 - 0.0044, 4)], "rotate": [0.0, 0.0, 0.0]},
        "light_left": {"offset": [round(g(f["side"]) + 0.0007, 4), g(470.0), g(f["side_h"])], "rotate": [0.0, 0.0, 0.0]},
        "laser_right": {"offset": [round(-g(f["side"]) - 0.0018, 4), g(470.0), round(g(f["side_h"]) - 0.0008, 4)],
                        "rotate": [0.0, 0.0, 0.0]},
    })
    pts["_extras"] = {"bore_mm": round(B, 2), "rail_faces_mm": {k: round(v, 2) for k, v in f.items()},
                      "handguard_mm": HG, "muzzle_mm": MUZZLE, "k": R}
    bpy.ops.object.select_all(action='DESELECT')
    for o in gun:
        o.select_set(True)
    os.makedirs(os.path.dirname(OUT_GUN), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=OUT_GUN, use_selection=True, object_types={'MESH'})
    with open(POINTS, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    print("wrote", OUT_GUN, POINTS, json.dumps(pts["_extras"]))


main()
