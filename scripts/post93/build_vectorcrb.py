"""KRISS Vector CRB (.45 ACP) model and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_vectorcrb.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_VECTORCRB.fbx   VECTORCRB_BODY, VECTORCRB_STOCK
    P/textures/weapons/GunsOfTienPost93/VECTORCRB.png             256, the body in the Vector .45's flat dark earth
    P/textures/weapons/GunsOfTienPost93/VECTORCRB_STOCK.png       128, the M4-type stock and its folding adapter
    scripts/post93/vectorcrb_points.json                          attachment points (game space)

The Vector CRB (user, 2026-11-03: "2 guns. .45 ACP gets the longer barrel. 9x19 gets the shorter one"), as KRISS's
CRB Enhanced of the user's photo (references/vector/crb_enhanced_left.png, 474 x 150 px, an OD green gun from the
left, muzzle left, the butt cut off by the frame; "keep the same color that we have": flat dark earth): the Vector .45
SMG of build_vector.py (imported: its profiles, painting and points) with an M-LOK handguard ahead of the receiver,
the 16" barrel in a fat shroud ahead of that, and an M4-type collapsible stock on KRISS's folding adapter in place of
the Vector's own stock. The bolt, charging handle, side rails and magazines are the SMG's nodes (VECTOR_BOLT /
_HANDLE / _RAIL_LEFT / _RAIL_RIGHT on VECTOR45.png, the .45 magazines).

The photo is squashed vertically, so it was read with two scales from parts it shares with our model: the front
block's two pins (L 20 and 68, H 113; 27 px apart) give 0.5625 px per mm across, the stock adapter then starts at
L 345 (the receiver's rear is L 341); the pins and the housing's bottom (H 5) give 0.52 px per mm up. L = (x - 177.75)
/ 0.5625, H = 113 - (y - 66) / 0.52. Read there: the handguard L 0 to -120.5 (its top flush with the receiver's at H
166, its bottom H 86, the top front chamfered), three rows of M-LOK slots, a slashed grip band at H 86-101, a short
rail under its front (L -118 to -35); the shroud ~48 mm across, ending at L -296 (the plain-shroud CRB photo, "Kriss
Vector left.JPG": -300 to -313), so L -300, past the 16" barrel's muzzle (L about -286), with diagonal grooves on its
top (L -276 to -159) and "KRISS VECTOR" on its left (L -280 to -227); the adapter L 341-361, the stock's beam flush
with the rail line (H 167, its underside H 120, the lever below it to H 100, a window at its front), the butt from a
slanted front edge (L 461 at the top, 479 at the bottom, H 42) with a slot, a strut, a long slot and a sling cup
(L 506); its rear is just past the photo's frame (L 527), taken as L 535: 835 mm overall. Held as a rifle, modelled upright
as the Vector .45: game +Y muzzle, +Z top, +X the gun's left, the SMG's origin.
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
FBX_GUN = os.path.join(kit.MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_VECTORCRB.fbx")
POINTS_JSON = os.path.join(HERE, "vectorcrb_points.json")

# the shroud's and the handguard's own materials (the SMG's painting leaves them alone), appended to both lists
for m in ("shroud", "hg"):
    vb.MATS.append(m)
    kit.MATS.append(m)
vb.BASE["shroud"] = (50, 51, 54)     # dark grey anodised aluminium
vb.BASE["hg"] = (113, 95, 69)        # the handguard, aluminium finished in the gun's flat dark earth

# --- the handguard (photo L, H mm) ---
HG_TOP, HG_BOTTOM, HG_NOSE = vb.TOP, 86.0, -120.5
W_HG, HG_WALL = 23.0, 2.5            # half width (over the front block's 22), wall thickness
HG = [(0.5, HG_TOP), (-107.0, HG_TOP), (HG_NOSE, 141.0), (HG_NOSE, 92.0), (-117.5, HG_BOTTOM), (0.5, HG_BOTTOM)]
HG_RAIL_TOP = (-104.0, 4.0)          # the top rail carried on to the receiver's (L 4)
HG_RAIL_BOTTOM = (-118.0, -35.0)
HG_RAIL_BASE, HG_RAIL_TEETH = 3.0, 4.5
HG_RAIL_FACE = HG_BOTTOM - HG_RAIL_BASE - HG_RAIL_TEETH + 1.0       # the bottom rail's crossbar faces
# M-LOK slots, three rows: (H from, H to), [(L from, L to)]
SLOT_ROWS = [((147.5, 155.0), [(-95.5, -58.5), (-45.5, -10.5)]),
             ((129.5, 139.0), [(-111.0, -83.0), (-76.0, -37.0), (-26.0, -5.0)]),
             ((106.5, 117.0), [(-114.0, -85.0), (-78.0, -37.0), (-28.0, -5.0)])]
HG_DOTS = [(-79.5, 134.0), (-31.5, 134.0), (-81.5, 112.0), (-32.5, 112.0)]
FOREGRIP_L = -76.0

# --- the shroud ---
SHROUD_R = 24.0                      # 48 mm across
SHROUD_START = -110.0                # inside the handguard
SHROUD_END = -300.0                  # its face: the muzzle, where a mount device or can screws on
BORE_R = 7.6                         # the opening in the face, recessed 4 mm to the crown
GROOVES = (-276.0, -159.0)

# --- the stock (photo L, H mm; its node's origin is the hinge, as VECTOR_STOCK's) ---
W_M4 = 20.0                          # the stock's half width
W_ADAPTER = 16.0
ADAPTER = (vb.HINGE_L, 366.0, 128.0, 165.0)
TUBE_H, TUBE_R = 150.0, 14.5
# the beam (flush with the rail line, a window at its front), the lever under it, the butt behind a slanted front edge
M4 = [(366.0, 167.0), (525.0, 167.0), (525.0, 42.0), (479.0, 42.0), (461.0, 120.0), (380.0, 120.0), (372.0, 126.0),
      (366.0, 140.0)]
PAD = (525.0, 535.0, 40.0, 169.0)    # the butt pad (just past the photo's frame)
LEVER = [(410.0, 121.0), (462.0, 121.0), (462.0, 101.0), (440.0, 100.0), (410.0, 108.0)]   # length adjustment
# the hinge pin, right (-X): folded, the wider stock lies 1 mm off the housing (the SMG's pin is at -20.25)
HINGE_X = -(vb.W_HOUSING + 1.0 + W_M4 + 0.8) / 2.0          # + the butt pad's 0.8 over the beam


def stadium(La, Lb, Ha, Hb, n=6):
    """A slot with round ends, as a polygon (build_ps90.py's)."""
    r = (Hb - Ha) / 2.0
    c = (Ha + Hb) / 2.0
    pts = [(Lb - r + r * math.cos(a), c + r * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, n)]
    pts += [(La + r + r * math.cos(a), c + r * math.sin(a)) for a in np.linspace(math.pi / 2, 3 * math.pi / 2, n)]
    return pts


SLOTS = [stadium(a, b, ha, hb) for (ha, hb), spans in SLOT_ROWS for a, b in spans]


def front_end(b):
    """The handguard (two slotted walls round a solid core, its top and bottom rails) and the shroud."""
    vb.both(lambda s: vb.slab(b, HG, SLOTS, half=HG_WALL / 2.0, bevel=0.6, res=0, mat="hg",
                              x0=s * (W_HG - HG_WALL / 2.0)))
    vb.slab(b, HG, half=W_HG - HG_WALL + 0.3, bevel=1.0, res=0, mat="hg")
    vb.picatinny(b, HG_RAIL_TOP[1], HG_RAIL_TOP[0], lambda u, h, yy: Vector((u, yy, HG_TOP - H0 + h)),
                 base_h=vb.RAIL_BASE, tooth_h=vb.RAIL_TEETH, mat="rail")
    vb.picatinny(b, HG_RAIL_BOTTOM[1], HG_RAIL_BOTTOM[0], lambda u, h, yy: Vector((u, yy, HG_BOTTOM - H0 - h)),
                 base_h=HG_RAIL_BASE, tooth_h=HG_RAIL_TEETH, mat="rail")
    t = lambda L: vb.P(L, 0)[0]
    b.lathe("y", (0, 0, BORE - H0), [
        (t(SHROUD_START), 0), (t(SHROUD_START), SHROUD_R), (t(SHROUD_END + 1.4), SHROUD_R),
        (t(SHROUD_END), SHROUD_R - 1.4), (t(SHROUD_END), BORE_R), (t(SHROUD_END + 4.0), BORE_R),
        (t(SHROUD_END + 4.0), 0)], seg=24, mat="shroud")


def build_stock():
    """Origin = the hinge (the SMG stock's): the adapter's front face on the bore axis; modelled deployed, along -Y."""
    b = kit.Builder()
    q = lambda pts: [(vb.HINGE_L - L, H - BORE) for L, H in pts]
    La, Lb, Ha, Hb = ADAPTER
    b.box(-W_ADAPTER, W_ADAPTER, vb.HINGE_L - Lb, vb.HINGE_L - La, Ha - BORE, Hb - BORE, mat="dark", bevel=2.0)
    b.lathe("y", (0, 0, TUBE_H - BORE), [(vb.HINGE_L - 359.0, 0), (vb.HINGE_L - 359.0, TUBE_R),
                                         (vb.HINGE_L - 390.0, TUBE_R), (vb.HINGE_L - 390.0, 0)], seg=16, mat="dark")
    kit.slab(b, q(M4), [], W_M4, 2.5, 1, "polymer", 0.0)
    La, Lb, Ha, Hb = PAD
    b.box(-W_M4 - 0.8, W_M4 + 0.8, vb.HINGE_L - Lb, vb.HINGE_L - La, Ha - BORE, Hb - BORE, mat="rubber", bevel=2.5)
    kit.slab(b, q(LEVER), [], 6.0, 1.5, 0, "dark", 0.0)
    # the hinge knuckles on the receiver's right rear corner, round the pin (they stay put when it folds)
    for h0, h1 in ((136.0, 146.0), (150.0, 160.0)):
        b.lathe("z", (HINGE_X, 0.0, 0.0), [(h0 - BORE, 0), (h0 - BORE, 4.5), (h1 - BORE, 4.5), (h1 - BORE, 0)],
                seg=12, mat="metal")
    return b.to_object("VECTORCRB_STOCK")


# ==================================================================================================
# Painting
# ==================================================================================================

def base_colours(maps):
    mat = maps["mat"]
    base = dict(vb.BASE, **vb.COLOURS["VECTOR45"])
    col = np.zeros(maps["pos"].shape, np.float32)
    for i, name in enumerate(vb.MATS):
        col[mat == i] = base[name]
    return col


def paint_body(maps):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = base_colours(maps)
    vb.paint_gun(maps, "VECTOR45", col)
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0
    side = np.abs(n[..., 0]) > 0.7
    # the handguard: the core seen through the slots dark, the slashed band, the screws between the slots
    hg = mat == vb.MATS.index("hg")
    inner = hg & (np.abs(x) < W_HG - 0.8) & (H > HG_BOTTOM + 1.0) & (H < HG_TOP - 1.0) & (L > HG_NOSE + 1.0) & (L < 0.0)
    col[inner] *= 0.3
    face = hg & side & (np.abs(x) > W_HG - 0.6)
    band = face & (H > HG_BOTTOM + 1.0) & (H < 101.0) & (L > -112.0) & (L < -10.0)
    col[band & (np.mod(L + (H - HG_BOTTOM) * 0.9, 7.5) < 2.6)] *= 0.6
    for cL, cH in HG_DOTS:
        vb.pin(col, L, H, face, cL, cH, r=1.6)
    # the shroud: the bore, its top grooves, the marking on its left
    sh = mat == vb.MATS.index("shroud")
    zc = z - (BORE - H0)
    r = np.hypot(x, zc)
    col[sh & (r < BORE_R + 0.3) & (L < SHROUD_END + 4.5)] = (14, 14, 15)
    col[sh & (r < 5.8) & (L > SHROUD_END + 3.5)] = 5
    ang = np.arctan2(x, zc)                                                       # 0 = top, + toward the left
    top = sh & (np.abs(ang) < 0.9) & (L > GROOVES[0]) & (L < GROOVES[1]) & (r > SHROUD_R - 0.5)
    col[top & (np.mod(L + ang * SHROUD_R * 0.8, 5.0) < 1.8)] *= 0.45
    left = sh & (x > SHROUD_R * 0.6)
    for word, L1 in (("KRISS", -282.0), ("VECTOR", -264.0)):
        col[left & kit.text_mask(L, H, word, L1, 105.0, 3.5)] = (186, 186, 180)
    col[sh & (L > SHROUD_END + 1.2) & (L < SHROUD_END + 1.6) & (r > SHROUD_R - 1.0)] *= 0.6   # the face's edge
    col = vb.common(maps, col, mat)
    return np.clip(col, 0, 255)


def paint_stock(maps):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = base_colours(maps)
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = vb.HINGE_L - y, z + BORE
    side = np.abs(n[..., 0]) > 0.7
    face = (mat == vb.MATS.index("polymer")) & side & (np.abs(x) > W_M4 - 0.8)
    # the beam's window and groove, the butt's open truss (recessed: a slot, a strut's gap, a long slot), the sling cup
    col[face & vb.rounded_rect(L, H, 378.0, 408.0, 123.0, 131.0, 2.0)] *= 0.35
    col[face & vb.near_line(L, H, [(382.0, 137.0), (452.0, 137.0)], 0.7)] *= 0.6
    col[face & vb.rounded_rect(L, H, 472.0, 502.0, 128.0, 138.0, 2.0)] *= 0.35
    col[face & vb.near_line(L, H, [(484.0, 61.0), (502.0, 92.0)], 2.0)] *= 0.4
    col[face & vb.rounded_rect(L, H, 507.0, 512.0, 51.0, 101.0, 2.0)] *= 0.35
    d = np.hypot(L - 506.0, H - 109.0)
    col[face & (d < 4.0)] = 14
    col[face & (d >= 4.0) & (d < 5.0)] += 14
    rub = mat == vb.MATS.index("rubber")
    col[rub & side & (np.mod(H, 9.0) < 1.2)] *= 0.6
    dark = mat == vb.MATS.index("dark")
    col[dark & side & (L < 362.0) & (np.abs(H - 147.0) < 0.6)] *= 0.5                # the adapter's seam
    col = vb.common(maps, col, mat)
    return np.clip(col, 0, 255)


def texture(ob, ctx, size, paint, path):
    maps = vb.bake(ob, ctx, size)
    bake = maps["cover"].shape[0]
    col = np.zeros((bake, bake, 3), np.float32)
    c = paint(maps)
    col[maps["cover"]] = c[maps["cover"]]
    col = kit.dilate(col, maps["cover"], 4 * (bake // size))
    kit.save_png(col, size, path)


# ==================================================================================================
# Points: the SMG's, with the muzzle and canon on the shroud's face, the foregrip under the handguard and the
# stock's own hinge
# ==================================================================================================

def points(bounds):
    vb.MUZZLE_L = vb.CANON_L = SHROUD_END
    pts = vb.points(bounds)
    face = (HG_RAIL_FACE - H0) * K
    pts["rail_down"] = {"offset": [0.0, round(vb.P(sum(HG_RAIL_BOTTOM) / 2.0, 0)[0] * K, 4), round(face + 0.0055, 4)],
                        "rotate": vb.ZERO}
    pts["foregrip"] = {"offset": [0.0, round(vb.P(FOREGRIP_L, 0)[0] * K, 4), round(face + 0.003, 4)],
                       "rotate": vb.ZERO}
    stock = pts["stock"]["offset"]
    pts["stock_folded"] = {"offset": [round(stock[0] + 2.0 * HINGE_X * K, 4), stock[1], stock[2]],
                           "rotate": [0.0, 0.0, 180.0]}
    notes = pts["_notes"]
    notes["shroud"] = ("the 16\" barrel's shroud, %.0f mm across, out of the handguard's nose (L %.1f) to L %.0f: "
                       "muzzle and canon (GoM's .45 mount device and P45) on its face" % (2 * SHROUD_R, HG_NOSE,
                                                                                         SHROUD_END))
    notes["foregrip"] = ("GoM's foregrips on the handguard's bottom rail (L %.0f to %.0f), 0.003 above its crossbar "
                         "faces" % HG_RAIL_BOTTOM)
    notes["stock"] = ("VECTORCRB_STOCK (this FBX: KRISS's folding adapter, the buffer tube, an M4-type stock) modelled "
                      "deployed, origin at the hinge: the adapter's front face on the bore axis")
    notes["stock_folded"] = ("the same node turned 180 degrees about the hinge pin at x %.2f mm (the right side; the "
                             "SMG's pin is further in: this stock is wider)" % HINGE_X)
    notes["nodes"] = ("VECTORCRB_BODY / _STOCK (GunsOfTienPost93_VECTORCRB.fbx); bolt, handle, side rails and "
                      "magazines are the Vector .45's nodes at these points")
    return pts


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

    body = vb.build_body("VECTORCRB_BODY", front_end)
    handle = vb.build_handle()                            # occlusion only (the SMG's node draws it)
    stock = build_stock()
    kit.unwrap([body], 0.005)
    kit.unwrap([stock], 0.012)
    os.makedirs(kit.TEX_DIR, exist_ok=True)
    texture(body, [body, handle], 256, paint_body, os.path.join(kit.TEX_DIR, "VECTORCRB.png"))
    texture(stock, [stock], 128, paint_stock, os.path.join(kit.TEX_DIR, "VECTORCRB_STOCK.png"))

    bounds = {o.name: kit.bounds_of(o) for o in (body, stock)}
    pts = points(bounds)
    bounds["VECTORCRB_STOCK_deployed"] = kit.bounds_at(stock, pts["stock"])
    bounds["VECTORCRB_STOCK_folded"] = kit.bounds_at(stock, pts["stock_folded"])
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    for name, b in bounds.items():
        print("VECTORCRB %-26s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))
    bpy.data.objects.remove(handle)
    kit.export([body, stock], FBX_GUN)


if __name__ == "__main__":
    main()
