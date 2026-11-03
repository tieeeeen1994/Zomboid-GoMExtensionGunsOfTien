"""KRISS Vector SDP (9mm) model and texture for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_vectorsdp.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_VECTORSDP.fbx   VECTORSDP_BODY (turned: held like a pistol)
    P/textures/weapons/GunsOfTienPost93/VECTORSDP.png             256, the body in the Vector 9mm's sand
    scripts/post93/vectorsdp_points.json                          attachment points (game space, turned)

The Vector SDP (user, 2026-11-03: "2 guns. .45 ACP gets the longer barrel. 9x19 gets the shorter one"; held like a
pistol, back slot, select fire as the SMGs): KRISS's stockless pistol, the Vector 9mm SMG of build_vector.py
(imported: its profiles, painting and points) without the side-folding stock, from the user's photo
(references/vector/sdp_right.png, 2048 x 1717, a Gen II SDP in tan from the right, muzzle right, Glock's 33 in it,
KRISS's bolt-on side rail on; git-ignored). Scaled from parts it shares with our model: the receiver's front face
(L 0) at x 1894, the rail's top (H 171.5) at y 285 and the housing's bottom (H 5) at y 1081 give 4.78 px per mm, and
the grip's lower rear corner then lands on ours (L 341): L = (1894 - x) / 4.78, H = 5 + (1081 - y) / 4.78. Read
there: where the SMG's stock hinges, the tan upper and its top rail run on to L 361 (down to H 139), closed by a
black faceted end cap (L 361-372, 31 mm tall at its front, 23 at its back, about H 155) carrying a QD sling swivel
(a knurled button to L 384, its ring about 27 mm across round it); the barrel out of the front face (r 7) to L -11,
then a knurled thread protector (r 8.9) to L -26.5. 16.75" overall per KRISS / American Rifleman: 425 mm, ours 411.

Held like a pistol (the Vector 9mm's way): built upright, painted, then exported turned (build_vector.turned_copy:
data x and z negated, UVs kept) with its points turned by build_vector.handgun_points; the bolt, charging handle and
side rails are the Vector 9mm's turned nodes (VECTOR9_BOLT / _HANDLE / _RAIL_LEFT / _RAIL_RIGHT on VECTOR9.png). The
Mk9's mount device (30 mm, r 11.6) at `canon` (the receiver's face, as the SMG's) covers the protector.
"""

import sys as _sys
_sys.dont_write_bytecode = True
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_vector as vb  # noqa: E402  (sets build_mp7's K and material list)

kit = vb.kit
K = vb.K
L0, H0, BORE = vb.L0, vb.H0, vb.BORE
FBX_GUN = os.path.join(kit.MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_VECTORSDP.fbx")
POINTS_JSON = os.path.join(HERE, "vectorsdp_points.json")

# the rear of the upper where the SMG's stock hinges: run on to L 361, its underside into the grip's web
REAR = [(336.0, vb.TOP), (355.0, vb.TOP), (359.5, 164.0), (361.0, 159.0), (361.0, 144.0), (359.0, 140.5),
        (355.0, 139.0), (345.0, 138.0), (337.0, 133.5)]
REAR_L = 361.0
RAIL_END = 360.0                     # the top rail runs on over it (the SMG's ends at L 302)
CAP = (REAR_L - 1.0, 372.4, 15.5, 11.8)     # the end cap: L from, L to, front and back half heights
CAP_H = 155.0                        # its axis
BUTTON = (372.0, 385.0, 6.3)         # the swivel's knurled button
RING_L, RING_R, RING_T = 378.0, 12.0, 1.7   # its ring round the button (major radius, wire radius)
BARREL_R, PROTECTOR = 7.0, (-11.0, -26.5, 8.9)
MUZZLE_L = PROTECTOR[1]
CANON_L = -1.0                       # the receiver's face, as the SMG's: a mount device covers the protector


def front_and_rear(b):
    """The SDP's barrel and thread protector, the upper's rear with the rail on it, the end cap and swivel."""
    t = lambda L: vb.P(L, 0)[0]
    pa, pb, pr = PROTECTOR
    b.lathe("y", (0, 0, BORE - H0), [
        (t(6.0), 0), (t(6.0), 8.2), (t(0.0), 8.2), (t(0.0), BARREL_R), (t(pa), BARREL_R), (t(pa), pr),
        (t(pb + 0.6), pr), (t(pb), pr - 0.6), (t(pb), 4.6), (t(pb + 3.5), 4.6), (t(pb + 3.5), 0)],
        seg=16, mat="metal", phase=0.5)
    vb.slab(b, REAR, half=vb.W_UPPER, bevel=1.8, res=1)
    vb.picatinny(b, RAIL_END, vb.RAIL_TOP[1], lambda u, h, yy: Vector((u, yy, vb.TOP - H0 + h)),
                 base_h=vb.RAIL_BASE, tooth_h=vb.RAIL_TEETH, mat="rail")
    La, Lb, ra, rb = CAP
    b.lathe("y", (0, 0, CAP_H - H0), [(t(La), 0), (t(La), ra), (t(Lb - 1.0), rb + 0.6), (t(Lb), rb), (t(Lb), 0)],
            seg=8, mat="dark", phase=0.5)
    ba, bb, br = BUTTON
    b.lathe("y", (0, 0, CAP_H - H0), [(t(ba), 0), (t(ba), br - 1.0), (t(ba + 2.0), br), (t(bb - 1.0), br),
                                      (t(bb), br - 1.2), (t(bb), 0)], seg=14, mat="metal")
    torus(b, t(RING_L), CAP_H - H0, RING_R, RING_T, mat="metal")


def torus(b, y0, z0, R, rt, seg=20, sides=8, mat="metal"):
    """A ring round the Y axis (the lathe would cap its ends with a disc), into the builder's mesh."""
    bm = b.bm
    rings = []
    for i in range(seg):
        a = 2.0 * math.pi * i / seg
        ring = []
        for j in range(sides):
            c = 2.0 * math.pi * j / sides
            rad = R + rt * math.cos(c)
            ring.append(bm.verts.new((rad * math.cos(a), y0 + rt * math.sin(c), z0 + rad * math.sin(a))))
        rings.append(ring)
    faces = []
    for i in range(seg):
        ra, rb = rings[i], rings[(i + 1) % seg]
        for j in range(sides):
            j1 = (j + 1) % sides
            faces.append(bm.faces.new((ra[j], ra[j1], rb[j1], rb[j])))
    b._finish([v for r in rings for v in r], faces, mat, 0.0, None)


def paint(maps):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    base = dict(vb.BASE, **vb.COLOURS["VECTOR9"])
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(vb.MATS):
        col[mat == i] = base[name]
    vb.MUZZLE_L = 0.5                    # the SMG's bare threads: none here (the protector covers them)
    vb.paint_gun(maps, "VECTOR9", col)
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0
    metal = mat == vb.MATS.index("metal")
    zc = z - (BORE - H0)
    r = np.hypot(x, zc)
    pa, pb, pr = PROTECTOR
    col[metal & (r < 4.9) & (L < pb + 4.0)] = 6                                  # the bore
    knurl = metal & (L < pa - 1.0) & (L > pb + 1.0) & (r > pr - 0.5)
    col[knurl & (np.mod(np.arctan2(x, zc) * pr, 1.3) < 0.5)] *= 0.55
    # the swivel's button knurled the same way round its axis
    zb = z - (CAP_H - H0)
    rb = np.hypot(x, zb)
    btn = metal & (L > BUTTON[0] + 2.0) & (L < BUTTON[1] - 1.0) & (rb > BUTTON[2] - 0.5) & (rb < BUTTON[2] + 0.5)
    col[btn & (np.mod(np.arctan2(x, zb) * BUTTON[2], 1.2) < 0.45)] *= 0.55
    # the end cap's seam with the upper
    col[(mat == vb.MATS.index("dark")) & (L < CAP[0] + 0.8)] *= 0.6
    col = vb.common(maps, col, mat)
    return np.clip(col, 0, 255)


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

    body = vb.build_body("VECTORSDP_UPRIGHT", front_and_rear)
    handle = vb.build_handle()                            # occlusion only (the 9mm's node draws it)
    kit.unwrap([body], 0.005)
    os.makedirs(kit.TEX_DIR, exist_ok=True)
    size = 256
    maps = vb.bake(body, [body, handle], size)
    bake = maps["cover"].shape[0]
    col = np.zeros((bake, bake, 3), np.float32)
    c = paint(maps)
    col[maps["cover"]] = c[maps["cover"]]
    col = kit.dilate(col, maps["cover"], 4 * (bake // size))
    kit.save_png(col, size, os.path.join(kit.TEX_DIR, "VECTORSDP.png"))

    # the SMG's points (upright) with the muzzle on the protector, then turned as the Vector 9mm's
    vb.MUZZLE_L, vb.CANON_L = MUZZLE_L, CANON_L
    pts = vb.points({"VECTORSDP_UPRIGHT": kit.bounds_of(body)})
    turned = vb.turned_copy(body, "VECTORSDP_BODY")
    turned.data.name = "VECTORSDP_BODY"                    # the FBX geometry takes the mesh's name
    bounds = {"VECTORSDP_BODY": kit.bounds_of(turned)}
    pts9 = vb.handgun_points(pts, bounds)
    for name in ("stock", "stock_folded"):               # no stock
        pts9.pop(name, None)
    pts9["_notes"]["nodes"] = ("VECTORSDP_BODY (GunsOfTienPost93_VECTORSDP.fbx, turned: held like a pistol); bolt, "
                               "handle and side rails are the Vector 9mm's turned nodes (VECTOR9_*) at these points")
    pts9["_notes"]["muzzle"] = ("the thread protector's end (L %.1f); canon at the receiver's face, where the Mk9's "
                                "mount device covers the protector" % MUZZLE_L)
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts9, fh, indent=2)
        fh.write("\n")
    for name, b in bounds.items():
        print("VECTORSDP %-24s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))
    for o in (handle, body):
        bpy.data.objects.remove(o)
    kit.export([turned], FBX_GUN)


if __name__ == "__main__":
    main()
