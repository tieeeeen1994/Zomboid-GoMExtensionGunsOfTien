"""Steyr TMP model and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_tmp.py -- [--size 1024] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_TMP.fbx        TMP_BODY, TMP_BOLT (the bolt in the right ejection port),
                                                          TMP_HANDLE (the cocking knob at the rear top)
    M/models_X/weapons/magazines/GunsOfTien_TMP_magazines.fbx  9x19Magazine15_TMP, 9x19Magazine30_TMP
    M/textures/weapons/GunsOfTien/TMP.png                 256, the gun's three nodes
    M/textures/weapons/GunsOfTien/9x19Magazine<n>_TMP.png 128 each
    scripts/tmp_points.json                               attachment points (game space)

User, 2026-11-11 (docs/design.md 4m): Steyr's 9x19mm machine pistol (designed 1989 by Friedrich Aigner, made
1992-2001), 15 and 30-round magazines only, held like a pistol and holstered as the Mini Uzi, GoM's MP5K reload,
the main mod's 9x19mm SMG mount device and AWC Mk9 on its threaded barrel. Polymer upper and lower, a fixed front grip
moulded into the frame with a hand stop ahead of it, a cross-bolt safety over the grip, closed bolt.

Traced from the public-domain Commons photo "Steyr TMP 9mmPara 001.jpg" (Spectrums; the LEFT side, muzzle left, a
30-round magazine; references/steyr_tmp, not in the repo) with post93/trace_outline.py at Steyr's 282 mm
(3.656 px/mm): scripts/tmp_reference_outline.json. The height then comes out at 158 mm from the rear sight to the
grip's bottom. Profiles are in that photo's (L, H) mm: L back from the muzzle tip, H up from the lowest point (the
30-round magazine's base). The bore is at H 204.5. Not in the photo, so drawn from the TMP's layout: the right side
(the ejection port on the upper over the trigger) and the widths (the upper 38 mm, the frame 35, the grips 31 / 26).

GoM's conventions (CLAUDE.md, "Gun assets in GoM"): +Y muzzle, +Z top, +X the gun's LEFT, origin at the rear-top of
the pistol grip, 0.603 of real size. Held like a pistol (GoM's MP5K / MAC-10 way), so the gun's nodes are modelled
and baked upright and turned 180 degrees about the bore axis at export with their points (build_mp7.py's TURN /
turned()); the magazines stay upright and get TURN at their point, as the Mini Uzi's.
The cocking knob (`TMP_HANDLE`) is pulled straight back out of the upper's rear only while racked (`handle_back`,
ChargingHandle.lua: it does not reciprocate); what moves on each shot, and stays back on an empty gun, is the bolt in
the ejection port on the right (`TMP_BOLT`, GoM's bolt swap, `bolt_fired`), drawn as the Uzis' plate over the port's
front half.
"""

import sys as _sys
_sys.dont_write_bytecode = True
import json
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
import build_mp7 as kit  # noqa: E402

MEDIA = os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_TMP.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_TMP_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "tmp_points.json")

K = 0.000603
K_OLD = 0.00072
kit.K = K
MATS = ["polymer", "grip", "metal", "dark", "magpoly", "brass", "copper"]
kit.MATS[:] = MATS
kit.FONT.setdefault("T", ["111", "010", "010", "010", "010"])
kit.FONT.setdefault("5", ["111", "100", "111", "001", "111"])         # build_uzi.py's glyph
ZERO = [0.0, 0.0, 0.0]

# photo (L, H) of the model origin: the grip's rear edge meets the frame. game y = L0 - L, z = H - H0.
L0, H0 = 207.0, 172.0
BORE = 204.5
W_UPPER, W_LOWER, W_GRIP, W_FGRIP = 19.0, 17.5, 15.5, 13.0
PARTING = 208.0                    # the upper / lower seam on both sides
CANON_L = 30.0                     # the upper's front face: the barrel's threaded end stands out ahead of it
MAG = (185.0, 188.0)               # the magazine's feed lips (axis straight down, centred in the grip)
PORT = (112.0, 150.0, 211.0, 227.0)   # the ejection port on the upper's right: L front, L rear, H low, H high
KNOB = (262.0, 281.0, 225.0, 240.5)   # the cocking knob: L front, L rear, H low, H top
KNOB_TRAVEL = 25.0                 # pulled straight back out of the upper's rear when racked

# ==================================================================================================
# Profiles (photo L, H mm), read off the traced photo on a 5 mm grid
# ==================================================================================================

UPPER = [(30.0, 200.0), (30.0, 214.0), (32.0, 219.0), (37.0, 227.0), (41.0, 232.0), (47.0, 234.5), (244.0, 235.0),
         (247.0, 232.0), (252.0, 227.5), (258.0, 225.0), (262.0, 224.5), (279.0, 224.5), (281.0, 222.0),
         (281.0, 200.0)]
LOWER = [(28.0, 203.0), (28.0, 192.0), (30.0, 186.0), (34.0, 182.0), (47.0, 181.0), (60.0, 178.0), (90.0, 176.0),
         (100.0, 177.0), (155.0, 178.0), (207.0, 176.0), (212.0, 176.0), (230.0, 177.5), (250.0, 179.0),
         (270.0, 181.0), (277.0, 185.0), (280.0, 192.0), (280.0, 203.0)]
FRONT_GRIP = [(47.0, 181.0), (53.0, 175.0), (55.0, 168.0), (52.0, 155.0), (48.0, 145.0), (45.0, 130.0),
              (42.0, 112.0), (39.0, 94.0), (39.5, 89.0), (44.0, 85.0), (55.0, 83.0), (66.0, 82.0), (70.0, 84.0),
              (72.0, 95.0), (74.0, 112.0), (76.0, 130.0), (77.0, 150.0), (78.0, 165.0), (82.0, 172.0),
              (90.0, 176.0), (90.0, 181.0)]
GRIP = [(155.0, 180.0), (157.0, 165.0), (159.0, 155.0), (161.0, 140.0), (164.0, 128.0), (165.5, 118.0),
        (165.0, 100.0), (165.0, 82.0), (216.0, 82.0), (216.5, 110.0), (214.0, 120.0), (211.0, 130.0),
        (208.0, 142.0), (205.0, 158.0), (206.0, 168.0), (207.0, 176.0), (207.0, 180.0)]
GUARD_OUT = [(97.0, 177.5), (104.0, 168.0), (111.0, 158.0), (117.0, 152.0), (122.0, 150.0), (145.0, 150.0),
             (150.0, 153.0), (153.0, 158.0), (155.0, 165.0), (155.5, 177.5)]
GUARD_IN = [(106.0, 177.5), (110.0, 166.0), (116.0, 157.0), (121.0, 153.5), (144.0, 153.5), (148.0, 156.0),
            (150.0, 162.0), (150.5, 168.0), (150.3, 173.0), (149.5, 177.5)]   # as many points as GUARD_OUT
TRIGGER = [(131.0, 178.0), (134.5, 173.0), (137.0, 166.0), (136.0, 160.0), (131.5, 156.0), (129.0, 156.5),
           (133.0, 161.0), (134.0, 166.0), (131.5, 172.0), (127.5, 178.0)]
HAND_STOP = [(25.0, 190.0), (29.5, 190.0), (27.5, 180.0), (23.5, 164.5), (20.5, 165.5), (24.0, 180.0)]
FRONT_SIGHT = [(50.0, 234.0), (53.0, 237.5), (57.0, 238.5), (61.0, 237.5), (63.0, 234.0)]
REAR_SIGHT = [(230.0, 234.0), (234.0, 237.5), (237.0, 240.5), (241.0, 241.0), (243.0, 239.0), (244.0, 234.0)]
BUMPER = [(279.0, 193.0), (283.0, 194.0), (283.0, 205.0), (279.0, 206.0)]
SLING = (180.0, 189.0, 197.0, 212.0)  # the sling clip on the left, across the seam


def P(L, H):
    return L0 - L, H - H0


def PL(points):
    return [P(L, H) for L, H in points]


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="polymer", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="polymer", bevel=0.0):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel)


def gp(L, H, x=0.0):
    return [round(x * K, 4) + 0.0, round((L0 - L) * K, 4) + 0.0, round((H - H0) * K, 4) + 0.0]


def port_open():
    La, Lb, Ha, Hb = PORT
    return La, Lb, Ha + 1.5, Hb - 1.5


def carrier_travel():
    La, Lb, _, _ = port_open()
    return (Lb - La) / 2.0 - 0.5


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    slab(b, UPPER, half=W_UPPER, bevel=1.6, res=1)
    slab(b, LOWER, half=W_LOWER, bevel=1.4, res=1)
    slab(b, FRONT_GRIP, half=W_FGRIP, bevel=3.5, res=1, mat="grip")
    slab(b, GRIP, half=W_GRIP, bevel=3.5, res=1, mat="grip")
    b.strip(PL(GUARD_OUT), PL(GUARD_IN), -4.0, 4.0, mat="polymer", bevel=0.8)
    slab(b, TRIGGER, half=3.0, bevel=0.6, mat="dark")
    slab(b, HAND_STOP, half=4.5, bevel=1.0)
    slab(b, FRONT_SIGHT, half=4.0, bevel=0.8)
    slab(b, REAR_SIGHT, half=6.0, bevel=0.8)
    slab(b, BUMPER, half=10.0, bevel=1.0, mat="dark")
    # the barrel: its threaded end out of the upper's front face (the TMP's own thread for a suppressor)
    zb = BORE - H0
    y = lambda L: L0 - L  # noqa: E731
    b.lathe("y", (0, 0, zb), [(y(33.0), 0), (y(33.0), 9.3), (y(14.0), 9.3), (y(13.5), 9.8), (y(0.8), 9.8),
                              (y(0.0), 9.0), (y(0.0), 0)], seg=20, mat="metal", phase=0.5)
    # the cross-bolt safety over the grip (out of both sides), the magazine release on the grip's left, the sling clip
    box(b, 152.5, 162.5, 176.5, 183.0, -(W_LOWER + 1.2), W_LOWER + 1.2, mat="dark", bevel=0.8)
    b.lathe("x", (0, y(162.0), 162.0 - H0), [(W_GRIP - 1.0, 0), (W_GRIP - 1.0, 3.6), (W_GRIP + 1.0, 3.6),
                                             (W_GRIP + 1.4, 3.0), (W_GRIP + 1.4, 0)], seg=14, mat="dark")
    box(b, SLING[0], SLING[1], SLING[2], SLING[3], W_UPPER - 0.6, W_UPPER + 2.2, mat="metal", bevel=0.6)
    return b.to_object("TMP_BODY")


def build_carrier():
    """The bolt's side in the right ejection port's front half (bolt_lock); bolt_fired slides it back over the
    port's rear half. A plate 0.35 mm proud of the upper's right face (-X upright), reaching 0.4 mm into it."""
    La, Lb, Ha, Hb = port_open()
    b = kit.Builder()
    box(b, La + 0.5, (La + Lb) / 2.0 - 0.2, Ha + 0.5, Hb - 0.5, -(W_UPPER + 0.35), -(W_UPPER - 0.4), mat="metal",
        bevel=0.1)
    return b.to_object("TMP_BOLT")


def build_handle():
    """The cocking knob in its recess at the upper's rear top, flush with the rear face: two wings ribbed on their
    sides (as photographed), joined over the bolt's tail."""
    La, Lb, Ha, Hb = KNOB
    b = kit.Builder()
    slab(b, [(La, Ha), (La, Hb - 2.5), (La + 2.0, Hb), (Lb - 2.0, Hb), (Lb, Hb - 2.0), (Lb, Ha)], half=15.0,
         bevel=1.2, mat="dark")
    # the bolt's tail block the knob sits on, as wide as the knob and filling the channel's height (its bottom 1.5 mm
    # inside the upper), its front 10 mm past the travel: racked, the knob comes out of the upper's rear on a solid
    # block, never on a thin bar (user, 2026-11-11: "still disconnected")
    box(b, La - KNOB_TRAVEL - 10.0, La + 1.0, 223.0, Hb - 3.0, -14.0, 14.0, mat="dark", bevel=0.8)
    return b.to_object("TMP_HANDLE")


MAG_LEN = {15: 106.0, 30: 188.0}   # feed lips to base: the 15 ends flush with the grip, the 30 82 mm under it
MAG_W, MAG_D = 12.0, 18.0          # half width, half depth (the photo's 36 mm front to back)
MAG_BASE = 5.0


def mag_name(r):
    return "9x19Magazine%d_TMP" % r


def build_magazine(r):
    """Origin at the feed lips (top centre); the polymer body straight down along -Z, a narrower lip section at the
    top, the base plate a little proud, the top round with its bullet forward (+Y)."""
    b = kit.Builder()
    L = MAG_LEN[r]
    b.box(-MAG_W, MAG_W, -MAG_D, MAG_D, -(L - MAG_BASE), -7.0, mat="magpoly", bevel=1.2)
    b.box(-MAG_W + 3.0, MAG_W - 3.0, -MAG_D + 2.0, MAG_D - 4.0, -7.5, 0.0, mat="magpoly", bevel=0.8)
    b.box(-MAG_W - 0.8, MAG_W + 0.8, -MAG_D - 1.0, MAG_D + 1.0, -L, -(L - MAG_BASE), mat="magpoly", bevel=1.2)
    b.lathe("y", (0, -2.0, -4.6), [(-12.5, 0), (-12.5, 4.9), (6.0, 4.9), (6.5, 4.5)], seg=8, mat="brass")
    b.lathe("y", (0, -2.0, -4.6), [(6.5, 4.5), (11.0, 4.2), (14.5, 2.4), (15.7, 0)], seg=8, mat="copper")
    return b.to_object(mag_name(r))


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: Steyr's black polymer, a slightly greyer grip, the blued barrel, black steel, the magazine's polymer
    "polymer": (60, 60, 63), "grip": (54, 54, 57), "metal": (70, 71, 75), "dark": (32, 32, 34),
    "magpoly": (64, 64, 67), "brass": (150, 118, 62), "copper": (140, 82, 52),
}
rounded_rect = kit.rounded_rect


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "dark", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.93 + 0.14 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.98 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 70.0, 40.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.32 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def pin(col, L, H, sel, cL, cH, r=2.4):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] += 12


def ribs(col, sel, coord, pitch, dark=0.55, light=6.0):
    col[sel & (np.mod(coord, pitch) < pitch * 0.4)] *= dark
    col[sel & (np.mod(coord, pitch) >= pitch * 0.4)] += light


def paint_body(maps, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    top = n[..., 2] > 0.7
    poly = mat == MATS.index("polymer")
    upper = poly & side & (np.abs(x) > W_UPPER - 0.6)
    lower = poly & side & (np.abs(x) > W_LOWER - 0.6) & (np.abs(x) < W_LOWER + 0.6)
    # the seam between upper and lower, the long groove under it, the fine ribs at the front of the upper
    col[(upper | lower) & (np.abs(H - PARTING) < 0.7) & (L > 31.0) & (L < 280.0)] *= 0.45
    col[upper & (np.abs(H - 198.5) < 0.6) & (L > 31.0) & (L < 95.0)] *= 0.55
    ribs(col, upper & (L > 33.0) & (L < 92.0) & (H > 211.0) & (H < 229.0), H, 2.0, 0.7, 4.0)
    ribs(col, lower & (L > 33.0) & (L < 70.0) & (H > 185.0) & (H < 205.0), H, 2.0, 0.7, 4.0)
    # slots along the top, the takedown latch's slot on the left, the recess round the cocking knob
    for La, Lb in ((96.0, 117.0), (186.0, 205.0)):
        col[poly & top & (np.abs(x) < 7.0) & (L > La) & (L < Lb)] = 10
    col[upper & left & rounded_rect(L, H, 69.0, 73.0, 184.0, 200.0, 1.5)] = 12
    col[upper & left & rounded_rect(L, H, 142.0, 172.0, 191.5, 194.5, 1.5)] *= 0.5
    col[upper & (L > 244.0) & (L < 262.5) & (H > 223.5) & (np.abs(H - (230.0 - 0.33 * (L - 244.0))) < 0.8)] *= 0.5
    # the ejection port on the right: the open chamber in its front half (the TMP_BOLT plate covers it while the bolt
    # is forward), the bolt's grooved steel side in the rear half
    La, Lb, Ha, Hb = port_open()
    port = upper & right & rounded_rect(L, H, La, Lb, Ha, Hb, 2.0)
    split = (La + Lb) / 2.0
    chamber = port & (L < split)
    col[chamber] = col[chamber] * 0.2 + 10
    bolt = port & ~chamber
    col[bolt] = np.array(BASE["metal"]) * 1.45
    mid = (Ha + Hb) / 2.0
    col[bolt & ((np.abs(H - mid + 3.0) < 0.5) | (np.abs(H - mid - 3.0) < 0.5))] *= 0.6
    col[bolt & (L < split + 0.8)] *= 0.5
    # markings: "STEYR" and "TMP" on the left (u = +L), "TMP" on the right (u = -L)
    col[upper & left & kit.text_mask(L, H, "STEYR", 214.0, 214.5, 4.0)] += 30
    col[upper & left & kit.text_mask(L, H, "TMP", 100.0, 216.0, 4.0)] += 30
    col[upper & right & kit.text_mask(-L, H, "TMP", -240.0, 214.5, 4.0)] += 30
    for cL, cH in ((247.0, 196.0), (209.0, 194.0), (120.0, 196.0), (62.0, 191.0)):
        pin(col, L, H, upper | lower, cL, cH, 2.6)
    # the grips' horizontal grooves (front grip H 113-145, main grip H 92-145, round its front and back too)
    grip = (mat == MATS.index("grip")) & (np.abs(n[..., 2]) < 0.6)
    ribs(col, grip & (L < 100.0) & (H > 113.0) & (H < 146.0), H, 3.3)
    ribs(col, grip & (L > 150.0) & (H > 92.0) & (H < 146.0), H, 3.3)
    # the barrel's thread and bore
    metal = mat == MATS.index("metal")
    r = np.hypot(x, z - (BORE - H0))
    thread = metal & (L < 13.5) & (r > 9.0)
    col[thread & (np.mod(L, 1.25) < 0.55)] *= 0.55
    col[metal & (L < 0.6) & (r < 4.6)] = 6


def paint_mag(maps, col, r):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, z = p[..., 0], p[..., 2]
    s = -z
    side = np.abs(n[..., 0]) > 0.7
    body = (mat == MATS.index("magpoly")) & side & (np.abs(x) > MAG_W - 0.6)
    back = MAG_LEN[r] - s
    # the photo's witness window down the side's front half and the round count moulded on both sides
    win = body & (p[..., 1] > -2.0) & (p[..., 1] < 4.0) & (back > MAG_BASE + 20.0) & (back < MAG_LEN[r] - 100.0)
    col[win] *= 0.8
    for face, uu in ((body & (n[..., 0] > 0.7), p[..., 1]), (body & (n[..., 0] < -0.7), -p[..., 1])):
        col[face & kit.text_mask(uu, back, str(r), -5.0, MAG_BASE + 6.0, 5.0)] += 30


def paint(maps, kind):
    p, mat = maps["pos"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    if kind == "body":
        paint_body(maps, col)
    elif kind == "handle":
        n = maps["nrm"]
        side = np.abs(n[..., 0]) > 0.7
        ribs(col, side & (L0 - p[..., 1] > KNOB[0] + 3.0), L0 - p[..., 1], 1.8, 0.5, 4.0)
    elif isinstance(kind, int):
        paint_mag(maps, col, kind)
    col = common(maps, col, mat)
    return np.clip(col, 0, 255)


def bake(ob, ctx, size):
    bake_size = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    maps = kit.bake_maps(ob, ctx, bake_size)
    if kit.DEBUG:
        kit.dump_maps(maps, os.path.join(kit.DEBUG, ob.name))
    return maps


def texture(maps_list, kinds, size, path):
    bake_size = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake_size, bake_size, 3), np.float32)
    cover = np.zeros((bake_size, bake_size), bool)
    for maps, kind in zip(maps_list, kinds):
        c = paint(maps, kind)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = kit.dilate(col, cover, 4 * (bake_size // size))
    kit.save_png(col, size, path)


# ==================================================================================================
# Attachment points
# ==================================================================================================

def points(bounds):
    pts = {
        "muzzle": {"offset": gp(0.0, BORE), "rotate": [-90.0, 0.0, -180.0]},
        # the upper's front face on the bore: the 9x19mm SMG mount device and the Mk9 start here, along +Y
        "canon": {"offset": gp(CANON_L, BORE), "rotate": ZERO},
        "magazine": {"offset": gp(*MAG), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-carrier_travel() * K, 4), 0.0], "rotate": ZERO},
        "handle_back": {"offset": [0.0, round(-KNOB_TRAVEL * K, 4), 0.0], "rotate": ZERO},
    }
    notes = {
        "canon": "the upper's front face (%.0f mm behind the muzzle): GunsOfTien.SMG9_Muzzle_Mount_Device and "
                 "Mk9_Suppressor start here, over the threaded barrel" % CANON_L,
        "magazine": "9x19Magazine15_TMP / 30_TMP hang straight down from here (their feed lips); the 15's base is "
                    "flush with the grip, the 30's 82 mm under it",
        "bolt_fired": "TMP_BOLT (the bolt in the right ejection port) back %.1f mm real: each shot and held open when "
                      "empty (GoM's Bolt_Fired)" % carrier_travel(),
        "handle_back": "TMP_HANDLE (the cocking knob) pulled %.0f mm straight back out of the upper, only while racked"
                       % KNOB_TRAVEL,
    }
    # held like a pistol: everything turned with the gun; the magazine gets TURN; GoM's MP5K floor pose
    pts = {k: kit.turned(v) for k, v in pts.items()}
    pts["magazine"]["rotate"] = list(kit.TURN)
    pts["world"] = {"offset": [round(-0.025 * K / K_OLD, 4), 0.0, 0.0], "rotate": ZERO}
    pts["_notes"] = dict(notes, units="game units (0.603 of real size, the M16A2's proportion); +Y muzzle; held like "
                         "a pistol, so modelled upside down as GoM's MP5K / MAC-10: +Z the gun's BOTTOM, +X its RIGHT; "
                         "origin = rear-top of the grip (photo L %.0f, H %.0f)" % (L0, H0))
    pts["_extras"] = {"handgun_hold": True, "photo_origin_mm": [L0, H0], "bore_mm": BORE, "k": K}
    pts["_bounds"] = bounds
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
    os.makedirs(TEX_DIR, exist_ok=True)

    body, bolt, handle = build_body(), build_carrier(), build_handle()
    gun = [body, bolt, handle]
    mags = [build_magazine(r) for r in MAG_LEN]
    kit.unwrap(gun, 0.006)
    for m in mags:
        kit.unwrap([m], 0.012)

    # the bolt is baked with the body only (it moves, so the knob's shadow would not stay on it)
    maps = [bake(body, [body, handle], 256), bake(bolt, [body, bolt], 256), bake(handle, [body, handle], 256)]
    texture(maps, ["body", "bolt", "handle"], 256, os.path.join(TEX_DIR, "TMP.png"))
    for r, m in zip(MAG_LEN, mags):
        texture([bake(m, [m], 128)], [r], 128, os.path.join(TEX_DIR, m.name + ".png"))

    for o in gun:                                      # held like a pistol: turned 180 degrees about the bore
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: kit.bounds_of(o) for o in gun}
    bounds["TMP_BOLT_fired"] = kit.bounds_of(bolt, (0, -carrier_travel() * K, 0))
    bounds["TMP_HANDLE_back"] = kit.bounds_of(handle, (0, -KNOB_TRAVEL * K, 0))
    pts = points(bounds)
    pts["_mags"] = {m.name: kit.bounds_of(m) for m in mags}
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    kit.export(gun, FBX_GUN)
    kit.export(mags, FBX_MAGS)
    for name, bd in list(bounds.items()) + list(pts["_mags"].items()):
        print("%-26s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
