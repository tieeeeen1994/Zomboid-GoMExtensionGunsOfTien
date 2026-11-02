"""RPD light machine gun (first model) for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_rpd.py -- [--size 1024] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_RPD.fbx        RPD_BODY, RPD_BOLT (the operating slide's straight handle,
                                                           forward), RPD_BIPOD_FOLDED, RPD_BIPOD_DEPLOYED
    M/models_X/weapons/magazines/GunsOfTien_RPD_drum.fbx   762x39Drum100_RPD (the belt drum, origin at the middle of
                                                           its dovetail's top)
    M/textures/weapons/GunsOfTien/RPD.png                  256, the gun's four nodes
    M/textures/weapons/GunsOfTien/762x39Drum100_RPD.png    128, the drum
    scripts/rpd_points.json                                attachment points (game space)

User, 2026-11-02 ("Older RPD pls."): Degtyaryov's 7.62x39mm squad machine gun as first made (Small Arms Review, "RPD:
The Last Degtyarev": a straight reciprocating operating handle on the slide, which "oscillated ... back and forth
during firing", no dust covers on the feed, the rear sight's windage knob on the right; the ejection port in the
bottom of the receiver; the drum slides onto a dovetail beneath the receiver; the gas regulator's nut on the left).
Wikipedia: 1037 mm, 520 mm barrel, 7.4 kg, 650-750 rpm, open bolt, full auto only, a 100-round non-disintegrating belt
fed from the left out of a drum under the gun.

Traced from the Finnish army museum's public-domain photo "7,62 mm RPD light machine gun.JPG" (Commons, 5184 px, the
LEFT side, muzzle right, bipod folded back under the barrel, the drum lying beside it; level within 1 px):
scripts/rpd_reference_outline.json, scaled to Wikipedia's 1037 mm (4.420 px/mm). That gun is a later model (a dust
cover hangs under the feed, a left-side windage knob); both are drawn as on the first model here. Profiles are in that
photo's (L, H) mm: L back from the muzzle tip, H up from the lowest point (the butt's toe). The bore is at H 137.
The drum (references/rpd: "RPD belt drum noBG.jpg", Batey ha-Osef's and the Nicaraguan army's RPDs, the RPD-44 photo)
faces forward like every drum (its round faces along the barrel; a side view shows its band), about 162 mm across and
70 deep, hung on its dovetail under the receiver; no belt shows outside it (it feeds straight up into the gun).

GoM's rifle conventions (CLAUDE.md, "Gun assets in GoM"): upright, +Y muzzle, +Z top, +X the gun's LEFT, origin at
the rear-top of the pistol grip, drawn at 0.603 of real size (the M16A2's proportion, every Guns of Tien gun).
"""

import sys as _sys
_sys.dont_write_bytecode = True
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
import build_mp7 as kit  # noqa: E402

MEDIA = os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_RPD.fbx")
FBX_DRUM = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_RPD_drum.fbx")
POINTS_JSON = os.path.join(HERE, "rpd_points.json")

K = 0.000603
K_OLD = 0.00065
kit.K = K
MATS = ["steel", "wood", "metal", "dark", "drum"]
kit.MATS[:] = MATS

# photo (L, H) of the model origin: the pistol grip's rear edge meets the trigger housing. game y = L0 - L, z = H - H0.
L0, H0 = 783.0, 100.0
BORE = 137.0
GAS = 117.0                        # the gas cylinder's axis under the barrel
W_RECV, W_COVER, W_TRIG, W_GRIP, W_STOCK, W_HG = 17.0, 15.0, 13.0, 14.0, 20.0, 26.0
DOVETAIL = (546.0, 600.0, 102.0)   # the drum's dovetail under the receiver: L front, L rear, its bottom H
DRUM_D, DRUM_DEPTH = 162.0, 70.0   # across its faces, front to back
DRUM_GAP = 6.0                     # the drum's top below the dovetail (its own mounting lug fills it)
SLOT = (596.0, 712.0, 114.0, 121.0)   # the operating handle's slot on the right: L front, L rear, H low, H high
HANDLE_L, HANDLE_TRAVEL = 604.0, 100.0   # the handle forward (bolt home); back 100 mm when cocked / firing
PIVOT = (56.0, 104.0, 9.0)         # the bipod legs' hinge under the front sight: L, H, |x|
LEG = 345.0                        # hinge to foot (the folded legs reach the handguard, L 400)
PORT = (612.0, 650.0)              # the ejection port in the receiver's bottom

# ==================================================================================================
# Profiles (photo L, H mm), read off the traced photo on a 5 mm grid
# ==================================================================================================

RECV = [(505.0, 110.0), (505.0, 158.0), (515.0, 163.0), (700.0, 163.0), (782.0, 163.0), (788.0, 160.0),
        (790.0, 150.0), (790.0, 110.0)]
COVER = [(512.0, 162.0), (516.0, 172.0), (528.0, 174.0), (590.0, 176.0), (655.0, 176.0), (660.0, 168.0),
         (660.0, 162.0)]
REAR_SIGHT = [(592.0, 175.0), (596.0, 184.0), (606.0, 187.0), (645.0, 182.0), (652.0, 176.0)]
TRIG_HOUSING = [(640.0, 100.0), (640.0, 111.0), (790.0, 111.0), (790.0, 100.0)]
HANDGUARD = [(380.0, 92.0), (380.0, 163.0), (386.0, 168.0), (395.0, 167.0), (405.0, 162.0), (420.0, 157.0),
             (440.0, 154.0), (460.0, 155.0), (475.0, 158.0), (490.0, 164.0), (500.0, 168.0), (506.0, 165.0),
             (506.0, 92.0), (500.0, 87.0), (490.0, 88.0), (475.0, 93.0), (460.0, 98.0), (440.0, 99.0),
             (420.0, 97.0), (405.0, 92.0), (395.0, 87.0), (386.0, 87.0)]
STOCK = [(788.0, 103.0), (788.0, 150.0), (820.0, 141.0), (860.0, 133.0), (880.0, 131.0), (1032.0, 128.0),
         (1037.0, 124.0), (1036.0, 10.0), (1031.0, 2.0), (1020.0, 0.0), (960.0, 0.0), (930.0, 3.0), (922.0, 10.0),
         (918.0, 20.0), (912.0, 40.0), (906.0, 55.0), (895.0, 64.0), (880.0, 72.0), (860.0, 80.0), (840.0, 87.0),
         (820.0, 93.0), (800.0, 99.0)]
BUTTPLATE = [(1035.0, 4.0), (1040.0, 6.0), (1041.0, 126.0), (1036.0, 128.0)]
GRIP = [(745.0, 101.0), (743.0, 60.0), (742.0, 12.0), (746.0, 4.0), (760.0, 2.0), (776.0, 3.0), (781.0, 10.0),
        (781.0, 50.0), (783.0, 101.0)]
TRIGGER = [(724.0, 101.0), (720.0, 92.0), (716.0, 85.0), (712.0, 82.0), (710.0, 84.0), (714.0, 90.0),
           (717.0, 101.0)]
GUARD_OUT = [(740.0, 100.0), (738.0, 82.0), (730.0, 74.0), (715.0, 71.0), (690.0, 72.0), (683.0, 78.0),
             (683.0, 100.0)]
GUARD_IN = [(736.0, 100.0), (734.0, 84.0), (728.0, 77.5), (715.0, 75.0), (692.0, 76.0), (687.0, 80.0),
            (687.0, 100.0)]
GAS_BLOCK = [(198.0, 104.0), (198.0, 152.0), (205.0, 156.0), (238.0, 156.0), (242.0, 150.0), (242.0, 104.0)]
FRONT_SIGHT = [(13.0, 148.0), (13.0, 170.0), (16.0, 188.0), (20.0, 195.0), (32.0, 195.0), (35.0, 188.0),
               (35.0, 148.0)]
FS_HOLE = [(18.0, 170.0), (19.0, 186.0), (30.0, 186.0), (31.0, 170.0)]
BIPOD_MOUNT = [(40.0, 99.0), (40.0, 128.0), (74.0, 128.0), (74.0, 112.0), (66.0, 99.0)]


def P(L, H):
    return L0 - L, H - H0


def PL(points):
    return [P(L, H) for L, H in points]


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="steel", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="steel", bevel=0.0, xf=None):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel, xf=xf)


def lathe_y(b, H, profile, seg=16, mat="metal", x=0.0, bevel=0.0):
    """Revolved about a line along the barrel at height H: profile [(L, radius)] from the rear forward."""
    b.lathe("y", (x, 0, H - H0), [(L0 - L, r) for L, r in profile], seg=seg, mat=mat, phase=0.5, bevel=bevel)


def gpt(L, H, x=0.0):
    return Vector((x, L0 - L, H - H0))


def along(p0, p1):
    d = Vector(p1) - Vector(p0)
    return Matrix.Translation(Vector(p0)) @ Vector((0, 1, 0)).rotation_difference(d.normalized()).to_matrix().to_4x4(), \
        d.length


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    slab(b, RECV, half=W_RECV, bevel=1.5, mat="steel")
    slab(b, COVER, half=W_COVER, bevel=1.2, mat="steel")
    slab(b, REAR_SIGHT, half=7.0, bevel=0.8, mat="steel")
    # the windage knob on the right (the first model's), the cover's latch at its front
    b.lathe("x", tuple(gpt(603.0, 182.0, -7.0)), [(0.0, 0.0), (0.0, 4.5), (-6.0, 4.5), (-6.0, 0.0)], seg=12,
            mat="dark")
    box(b, 509.0, 520.0, 160.0, 170.0, -W_COVER - 2.0, W_COVER + 2.0, mat="steel", bevel=1.0)
    slab(b, TRIG_HOUSING, half=W_TRIG, bevel=1.2, mat="steel")
    # the drum's dovetail under the feed (no dust cover on the first model)
    box(b, DOVETAIL[0], DOVETAIL[1], DOVETAIL[2], 111.0, -15.0, 15.0, mat="steel", bevel=1.0)
    slab(b, STOCK, half=W_STOCK, bevel=3.5, res=1, mat="wood")
    slab(b, BUTTPLATE, half=W_STOCK + 0.5, bevel=1.5, mat="steel")
    slab(b, GRIP, half=W_GRIP, bevel=3.5, res=1, mat="wood")
    slab(b, TRIGGER, half=2.5, bevel=0.6, mat="dark")
    b.strip(PL(GUARD_OUT), PL(GUARD_IN), -3.5, 3.5, mat="steel", bevel=0.5)
    # forward: the dog-bone handguard, the barrel and the gas cylinder under it, the gas block, the front sight
    slab(b, HANDGUARD, half=W_HG, bevel=4.0, res=1, mat="wood")
    lathe_y(b, BORE, [(512.0, 0.0), (512.0, 11.5), (382.0, 11.5), (380.0, 9.5), (76.0, 9.5), (75.0, 10.5),
                      (14.0, 10.5), (13.0, 9.0), (2.0, 9.0), (0.0, 8.0), (0.0, 3.8), (5.0, 3.8), (5.0, 0.0)],
            seg=16, mat="metal")
    lathe_y(b, GAS, [(385.0, 0.0), (385.0, 6.5), (242.0, 6.5), (242.0, 0.0)], seg=12, mat="metal")
    for La, Lb in ((285.0, 300.0), (372.0, 384.0)):                       # the barrel's bands
        box(b, La, Lb, 109.0, 156.0, -12.5, 12.5, mat="steel", bevel=2.0)
    slab(b, GAS_BLOCK, half=13.0, bevel=2.0, mat="steel")
    b.lathe("x", tuple(gpt(220.0, 121.0, 13.0)), [(0.0, 0.0), (0.0, 12.0), (5.0, 12.0), (6.0, 10.0), (6.0, 0.0)],
            seg=16, mat="metal")                                           # the regulator's nut, on the left
    lathe_y(b, BORE, [(75.0, 0.0), (75.0, 14.5), (14.0, 14.5), (14.0, 0.0)], seg=16, mat="steel")
    slab(b, FRONT_SIGHT, [FS_HOLE], half=8.0, bevel=0.8, mat="steel")
    box(b, 20.5, 27.5, 150.0, 181.0, -1.2, 1.2, mat="dark")               # the post between the ears
    slab(b, BIPOD_MOUNT, half=12.0, bevel=1.5, mat="steel")
    return b.to_object("RPD_BODY")


def build_handle():
    """The first model's straight operating handle, fixed to the slide (the piston and bolt group) on the right,
    forward (bolt home) at HANDLE_L; bolt_fired draws it HANDLE_TRAVEL back, where an open-bolt gun rests cocked."""
    b = kit.Builder()
    box(b, HANDLE_L - 6.0, HANDLE_L + 6.0, SLOT[2] + 0.5, SLOT[3] - 0.5, -W_RECV + 2.0, -W_RECV - 22.0,
        mat="steel", bevel=1.0)
    b.lathe("x", tuple(gpt(HANDLE_L, (SLOT[2] + SLOT[3]) / 2.0, -W_RECV - 22.0)),
            [(0.0, 0.0), (0.0, 7.5), (-10.0, 7.5), (-11.5, 5.5), (-11.5, 0.0)], seg=12, mat="metal")
    return b.to_object("RPD_BOLT")


def leg(b, p0, p1, foot=True):
    xf, n = along(p0, p1)
    b.lathe("y", (0, 0, 0), [(0.0, 0.0), (0.0, 5.0), (n, 5.0), (n, 0.0)], seg=10, mat="steel", xf=xf)
    if foot:                                                                                # a spade, deployed
        b.box(-10.0, 10.0, n - 6.0, n + 1.0, -32.0, 9.0, mat="steel", bevel=1.0, xf=xf)
    b.box(-6.5, 6.5, -2.0, 12.0, -6.5, 6.5, mat="steel", bevel=1.0, xf=xf)                 # the hinge knuckle


def build_bipod(deployed):
    b = kit.Builder()
    for s in (1, -1):
        p0 = gpt(PIVOT[0], PIVOT[1], s * PIVOT[2])
        if deployed:   # down, a little forward and splayed (the Tula museum's RPD)
            p1 = p0 + Vector((s * 0.26, 0.10, -0.96)).normalized() * LEG
        else:          # back under the barrel, the feet hanging down at the handguard (the Finnish photo)
            p1 = gpt(PIVOT[0] + LEG, 92.0, s * PIVOT[2])
        leg(b, p0, p1, foot=deployed)
        if not deployed:
            box(b, PIVOT[0] + LEG - 7.0, PIVOT[0] + LEG + 1.0, 50.0, 96.0, s * PIVOT[2] - 9.0, s * PIVOT[2] + 9.0,
                mat="steel", bevel=1.0)
    return b.to_object("RPD_BIPOD_DEPLOYED" if deployed else "RPD_BIPOD_FOLDED")


def build_drum():
    """The belt drum in its own frame: origin at the middle of its dovetail lug's top (the gun's `drum` point), +Y
    forward, +X the gun's left. A canister facing forward: its round faces along the barrel, the lid on the front
    face (hinged low, latched high), two pressed ribs round the band, the lug on top; the belt's mouth at the top
    left feeds straight up into the gun."""
    b = kit.Builder()
    r, d = DRUM_D / 2.0, DRUM_DEPTH
    cz = -DRUM_GAP - r                                  # its middle
    c = (0.0, 0.0, cz)
    # the band (with its two ribs) and the faces, as one lathe along the drum's axis (y), rear to front
    b.lathe("y", c, [(-d / 2, 0.0), (-d / 2, r - 3.0), (-d / 2 + 2.0, r), (-14.0, r), (-14.0, r + 1.6),
                     (-10.0, r + 1.6), (-10.0, r), (10.0, r), (10.0, r + 1.6), (14.0, r + 1.6), (14.0, r),
                     (d / 2 - 2.0, r), (d / 2, r - 3.0), (d / 2, 0.0)], seg=32, mat="drum")
    # the lid on the front face: a raised ring and its middle
    b.lathe("y", c, [(d / 2 - 0.5, 0.0), (d / 2 - 0.5, r * 0.82), (d / 2 + 1.5, r * 0.80), (d / 2 + 1.5, r * 0.52),
                     (d / 2 + 3.5, r * 0.50), (d / 2 + 3.5, 0.0)], seg=32, mat="drum")
    # the lid's hinge (low) and latch (high), the dovetail lug on top
    b.box(-14.0, 14.0, d / 2 - 2.0, d / 2 + 4.0, cz - r - 2.0, cz - r + 9.0, mat="steel", bevel=1.0)
    b.box(-6.0, 6.0, d / 2 - 2.0, d / 2 + 5.0, cz + r - 12.0, cz + r + 1.0, mat="steel", bevel=0.8)
    b.box(-14.0, 14.0, -24.0, 24.0, -DRUM_GAP - 4.0, 0.0, mat="steel", bevel=1.0)
    # the belt's mouth at the top left, up into the gun
    b.box(4.0, 20.0, -16.0, 16.0, -DRUM_GAP - 6.0, -1.0, mat="dark", bevel=0.8)
    return b.to_object("762x39Drum100_RPD")


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: blued steel, the Finnish gun's red-brown birch, the greyer barrel, black, the drum's dark paint
    "steel": (44, 44, 46), "wood": (112, 58, 36), "metal": (60, 60, 62), "dark": (20, 20, 21),
    "drum": (38, 39, 40),
}


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def pin(col, L, H, sel, cL, cH, r=2.4):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] += 12


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("steel", "metal", "drum")])
    wood = mat == MATS.index("wood")
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    grain = kit.vnoise(p * np.array([0.25, 0.02, 2.2]), 1.0, 7)          # long grain along the wood
    col[wood] *= (0.82 + 0.3 * grain[wood])[..., None]
    col *= (0.97 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 80.0, 45.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 0.98, 0.94])
    col *= (1.0 - 0.3 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    steel = mat == MATS.index("steel")
    wood = mat == MATS.index("wood")
    if kind == "body":
        L, H = L0 - y, z + H0
        recv = steel & side & (np.abs(x) > W_RECV - 0.6) & (L > 505) & (L < 790)
        # the operating handle's slot on the right, the belt's window on the left (under the cover), the feed
        # pawls' recess, the ejection port in the bottom
        col[recv & right & rounded_rect(L, H, SLOT[0], SLOT[1], SLOT[2], SLOT[3], 2.0)] = 12
        col[recv & left & rounded_rect(L, H, 530.0, 600.0, 140.0, 158.0, 2.5)] = 14
        col[steel & (n[..., 2] < -0.7) & (np.abs(x) < 8.0) & (L > PORT[0]) & (L < PORT[1]) & (H < 111.5)] = 10
        for cL, cH in ((520.0, 125.0), (570.0, 125.0), (660.0, 135.0), (700.0, 125.0), (760.0, 140.0),
                       (770.0, 118.0)):
            pin(col, L, H, recv, cL, cH, 3.0)
        # the photo's long lines on both sides: the slide's rail (H 112-114), a groove at H 130, the cover's seam
        # (H 162), and the stepped panel ahead of the stock (L 700-785, H 145-160)
        for hh, w_ in ((113.0, 1.2), (130.0, 0.9), (161.5, 0.8)):
            col[recv & (np.abs(H - hh) < w_) & (L > 512.0) & (L < 786.0)] *= 0.5
        col[recv & rounded_rect(L, H, 700.0, 784.0, 145.0, 160.0, 2.0)] *= 0.82
        # the handguard's oval thumb recesses and screws, the grip's grooves, the stock's sling swivel plate
        hg = wood & side & (np.abs(x) > W_HG - 1.0) & (L > 380.0) & (L < 506.0)
        col[hg & rounded_rect(L, H, 402.0, 470.0, 116.0, 136.0, 10.0)] *= 0.72
        for cL, cH in ((392.0, 160.0), (392.0, 96.0), (498.0, 160.0), (498.0, 96.0)):
            d = np.hypot(L - cL, H - cH)
            col[hg & (d < 4.0)] = (50, 50, 52)
            col[hg & (d < 3.2) & (np.abs(H - cH) < 0.6)] = 18
        grip = wood & side & (L > 742.0) & (L < 784.0) & (H < 100.0)
        for hh in np.arange(14.0, 92.0, 6.0):
            col[grip & (np.abs(H - hh + 0.18 * (L - 760.0)) < 1.0)] *= 0.6
        st = wood & side & (L > 980.0) & (L < 1000.0) & (H > 40.0) & (H < 60.0)
        col[st] = (54, 54, 56)
        # the bore and the front sight's post
        metal = mat == MATS.index("metal")
        col[metal & (np.hypot(x, H - BORE) < 4.0) & (L < 2.0)] = 6
    elif kind == "bolt":
        pass
    elif kind == "bipod":
        pass
    elif kind == "drum":
        dr = mat == MATS.index("drum")
        r = np.hypot(x, z + DRUM_GAP + DRUM_D / 2.0)
        face = dr & (np.abs(n[..., 1]) > 0.7)
        col[face & (np.abs(r - DRUM_D / 2.0 * 0.82) < 0.8)] *= 0.55          # the lid's seam
        col[face & (np.abs(r - DRUM_D / 2.0 * 0.51) < 0.7)] *= 0.6
        band = dr & (np.abs(n[..., 1]) < 0.5)
        col[band & (np.abs(np.abs(y) - 12.0) < 2.2)] *= 1.15                  # the pressed ribs catch the light
    col = common(maps, col, mat)
    return np.clip(col, 0, 255)


def texture(objects, contexts, kinds, size, path):
    bake = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake, bake, 3), np.float32)
    cover = np.zeros((bake, bake), bool)
    for ob, ctx, kind in zip(objects, contexts, kinds):
        maps = kit.bake_maps(ob, ctx, bake)
        c = paint(maps, kind)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = kit.dilate(col, cover, 4 * (bake // size))
    kit.save_png(col, size, path)


# ==================================================================================================
# Attachment points
# ==================================================================================================

def gp(L, H, x=0.0):
    return [round(x * K, 4) + 0.0, round((L0 - L) * K, 4) + 0.0, round((H - H0) * K, 4) + 0.0]


ZERO = [0.0, 0.0, 0.0]


def points(bounds):
    drum_l = (DOVETAIL[0] + DOVETAIL[1]) / 2.0
    pts = {
        "muzzle": {"offset": gp(0.0, BORE), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": gp(drum_l, DOVETAIL[2]), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-HANDLE_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "integrated_bipod": {"offset": ZERO, "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},
    }
    pts["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin = the rear-top of the "
                 "pistol grip (photo L %.0f, H %.0f)" % (L0, H0),
        "magazine": "762x39Drum100_RPD, origin at the middle of its dovetail lug's top, slid onto the gun's dovetail",
        "bolt_fired": "RPD_BOLT (the first model's straight operating handle on the slide, modelled forward) back "
                      "%.0f mm real: each shot, cocked (an open bolt rests back) and while empty (GoM's Bolt_Fired)"
                      % HANDLE_TRAVEL,
        "integrated_bipod": "RPD_BIPOD_FOLDED / _DEPLOYED are modelled in the gun's space",
    }
    pts["_extras"] = {"photo_origin_mm": [L0, H0], "bore_mm": BORE, "k": K,
                      "drum_top": gp(drum_l, DOVETAIL[2]), "handle": gp(HANDLE_L, 117.5, -W_RECV - 22.0)}
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

    body, bolt = build_body(), build_handle()
    bip_f, bip_d = build_bipod(False), build_bipod(True)
    drum = build_drum()
    gun = [body, bolt, bip_f, bip_d]
    kit.unwrap(gun, 0.004)
    kit.unwrap([drum], 0.008)

    os.makedirs(TEX_DIR, exist_ok=True)
    texture(gun, [[o] for o in gun], ["body", "bolt", "bipod", "bipod"], 256, os.path.join(TEX_DIR, "RPD.png"))
    texture([drum], [[drum]], ["drum"], 128, os.path.join(TEX_DIR, "762x39Drum100_RPD.png"))

    bounds = {o.name: kit.bounds_of(o) for o in gun + [drum]}
    pts = points(bounds)
    bounds["RPD_BOLT_fired"] = kit.bounds_of(bolt, (0, -HANDLE_TRAVEL * K, 0))
    bounds["762x39Drum100_RPD_fitted"] = kit.bounds_at(drum, pts["magazine"])
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    kit.export(gun, FBX_GUN)
    kit.export([drum], FBX_DRUM)
    for name, bd in bounds.items():
        print("%-28s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
