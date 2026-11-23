"""The real muzzle devices of both mods (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_muzzle_devices.py -- [--size 1024] [--debug DIR]

Writes the meshes and 128 px textures of every device in scripts/muzzle_devices.py (user, 2026-11-23: "Option A",
real devices built from scratch):
    main    Contents/mods/GoMExtensionGunsOfTien/42/media/models_X/weapons/parts/GunsOfTien_muzzle_devices.fbx
            .../textures/weapons/GunsOfTien/<node>.png
    Post-93 Contents/mods/GoMExtensionGunsOfTienPost93/42/media/models_X/weapons/parts/GunsOfTienPost93_muzzle_devices.fbx
            .../textures/weapons/GunsOfTienPost93/<node>.png

Each device is modelled in real millimetres (references in references/muzzle/<device>/, SOURCES.txt) with its origin
at its rear face on the bore axis, along +Y (where the gun's `canon` point is: the barrel's threads or lugs), then
scaled by its `scale` (game units per mm, the proportion of the guns that wear it). Turned parts are lathes; ports,
windows, slots and the slant cut are Boolean differences (exact solver) before the scale.
"""

import sys as _sys
_sys.dont_write_bytecode = True
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.path.insert(0, HERE)
import build_mp7 as kit  # noqa: E402
import muzzle_devices as MD  # noqa: E402

MEDIA = {"main": os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media"),
         "post93": os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")}
TEX = {"main": "textures/weapons/GunsOfTien", "post93": "textures/weapons/GunsOfTienPost93"}
FBX = {"main": "models_X/weapons/parts/GunsOfTien_muzzle_devices.fbx",
       "post93": "models_X/weapons/parts/GunsOfTienPost93_muzzle_devices.fbx"}
MATS = ["metal", "dark"]
kit.MATS[:] = MATS
SEG = 24


# ==================================================================================================
# Helpers
# ==================================================================================================

def solid(build, name):
    """A Builder filled by `build(b)`, as an object in mm (z already mirrored as the FBX wants)."""
    b = kit.Builder()
    build(b)
    return b.to_object(name, scale_mm=False)


def cut(ob, *cutters):
    """Boolean difference of every cutter from `ob`, applied; the cutters are removed."""
    for c in cutters:
        mod = ob.modifiers.new("cut", 'BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
        mod.object = c
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(c)
    return ob


def tube(b, y0, y1, r_out, r_in, mat="metal"):
    b.lathe("y", (0, 0, 0), [(y0, r_in), (y0, r_out), (y1, r_out), (y1, r_in)], seg=SEG, mat=mat)


def cyl_cutter(name, y0, y1, r, axis="y", at=(0, 0, 0), rot=None, seg=16):
    """A cylinder to cut with: along `axis` from y0 to y1 (its own length), radius r, moved to `at`, turned by `rot`."""
    def build(b):
        b.lathe("y", (0, 0, 0), [(y0, 0), (y0, r), (y1, r), (y1, 0)], seg=seg, mat="dark")
    ob = solid(build, name)
    m = Matrix.Identity(4)
    if axis == "x":
        m = Matrix.Rotation(math.radians(90), 4, 'Z')
    elif axis == "z":
        m = Matrix.Rotation(math.radians(90), 4, 'X')
    if rot is not None:
        m = rot @ m
    m = Matrix.Translation(Vector((at[0], at[1], -at[2]))) @ m      # object space has z mirrored
    ob.data.transform(m)
    return ob


def box_cutter(name, x0, x1, y0, y1, z0, z1, rot=None):
    def build(b):
        b.box(x0, x1, y0, y1, z0, z1, mat="dark", xf=rot)
    return solid(build, name)


def finish(ob, scale):
    """mm -> game units; z was mirrored by Builder.to_object."""
    ob.data.transform(Matrix.Scale(scale, 4))
    return ob


# ==================================================================================================
# The devices (real mm, origin at the rear face on the bore axis, +Y forward, +Z up, +X the gun's left)
# ==================================================================================================

def akm_slant():
    """AKM slant compensator (Soviet, 1959): 14x1 LH, about 44 x 22 mm. A rear flange with the retaining notch, a
    groove, the body, and the front cut away on a slant over its top and right so the gas pushes the muzzle down and
    left; the lower left lip stays (references/muzzle/akm_slant: roninsgrips' side view, Arsenal's Bulgarian one)."""
    def build(b):
        b.lathe("y", (0, 0, 0), [(0, 4.2), (0, 11.8), (3.4, 11.8), (3.6, 9.9), (7.0, 9.9), (7.2, 11.0),
                                  (44.0, 11.0), (44.0, 4.2)], seg=SEG, mat="metal")
    ob = solid(build, "AKM_Slant_Compensator")
    tilt = Matrix.Rotation(math.radians(-30), 4, 'Y')            # the cut faces up and to the shooter's right
    wedge = box_cutter("w", -20, 20, 22.0, 60.0, 0.0, 30.0,
                       rot=Matrix.Translation(Vector((0, 22.0, 2.5))) @ Matrix.Rotation(math.radians(-22), 4, 'X')
                       @ Matrix.Translation(Vector((0, -22.0, 0))))
    wedge.data.transform(tilt)
    cavity = cyl_cutter("c", 14.0, 46.0, 7.0)
    return cut(ob, wedge, cavity)


def ak74_brake():
    """AK-74 muzzle brake (Izhmash, 1974): 24x1.5 RH, about 82 x 26.5 mm. Rear collar with the pin notches, the body
    with three small vent holes on top, the big window through both sides near the front, and the front nose
    (references/muzzle/ak74_brake: Arsenal's AK-141, measured on its side view, 0.1 mm a pixel)."""
    def build(b):
        b.lathe("y", (0, 0, 0), [(0, 9.0), (0, 13.7), (15.5, 13.7), (16.0, 13.25), (73.5, 13.25), (74.0, 8.0),
                                  (82.0, 8.0), (82.0, 2.9)], seg=SEG, mat="metal")
    ob = solid(build, "AK74_Muzzle_Brake")
    chamber = cyl_cutter("c", 20.0, 73.8, 9.5)
    window = box_cutter("wnd", -20, 20, 57.0, 73.5, -9.0, 9.0)
    holes = [cyl_cutter("h%d" % i, -15.0, 15.0, 1.5, axis="z", at=(0, 31.0 + 2.5 * i, 0),
                        rot=Matrix.Rotation(math.radians(a), 4, 'Y')) for i, a in enumerate((-35, 0, 35))]
    notches = [box_cutter("n%d" % i, -2.0, 2.0, -1.0, 3.0, 11.5, 15.0, rot=Matrix.Rotation(math.radians(a), 4, 'Y'))
               for i, a in enumerate((0, 180))]
    bore = cyl_cutter("b", -1.0, 83.0, 2.9)
    return cut(ob, chamber, window, *holes, *notches, bore)


def aks74u_booster():
    """AKS-74U muzzle booster (about 1979): 24x1.5 RH, about 80 mm. A narrow rear section on the barrel, the
    expansion chamber, a rounded shoulder down to a waist, then the flash cone flaring forward to a wide mouth with
    two notches (references/muzzle/aks74u_booster: Commons' AKS74U (noBG), proportions only; no drawing found)."""
    def build(b):
        b.lathe("y", (0, 0, 0), [(0, 9.0), (0, 12.0), (11.0, 12.0), (12.0, 14.0), (52.0, 14.0), (55.0, 12.5),
                                  (58.0, 8.5), (61.0, 8.5), (80.0, 14.0), (80.0, 12.8), (62.0, 6.5), (60.0, 3.0)],
                seg=SEG, mat="metal")
    ob = solid(build, "AKS74U_Muzzle_Booster")
    chamber = cyl_cutter("c", 13.0, 54.0, 11.5)
    bore = cyl_cutter("b", -1.0, 62.0, 3.0)
    notches = [box_cutter("n%d" % i, -1.5, 1.5, 74.0, 81.0, 8.0, 16.0, rot=Matrix.Rotation(math.radians(a), 4, 'Y'))
               for i, a in enumerate((0, 180))]
    return cut(ob, chamber, bore, *notches)


def mp5_flash_hider():
    """H&K's three-lug flash hider for the MP5 (HK 221127): a knurled latch collar that slips over the lugs, then a
    tube with four long pointed slots and a closed front; about 78 x 30 mm (B&T's copy 84 x 30; measured on H&K's
    own photo, references/muzzle/mp5_flash_hider/mp5_flash_hider_12.jpg, collar taken as 30 mm)."""
    def build(b):
        b.lathe("y", (0, 0, 0), [(0, 7.5), (0, 15.0), (19.0, 15.0), (19.5, 12.0), (20.5, 10.0), (76.5, 10.0),
                                  (78.0, 9.0), (78.0, 7.0)], seg=SEG, mat="metal")
    ob = solid(build, "MP5_Flash_Hider")
    inner = cyl_cutter("i", 28.0, 79.0, 7.5)
    sleeve = cyl_cutter("s", -1.0, 28.5, 7.5)
    latch = box_cutter("l", -4.0, 4.0, 3.0, 9.0, -16.0, -13.0)
    slots = []
    for i in range(4):
        r = Matrix.Rotation(math.radians(45 + 90 * i), 4, 'Y')
        slots.append(box_cutter("s%d" % i, -1.6, 1.6, 40.0, 72.0, 5.0, 14.0, rot=r))
        slots.append(box_cutter("t%d" % i, -0.8, 0.8, 37.0, 75.0, 5.0, 14.0, rot=r))     # the pointed ends
    return cut(ob, inner, sleeve, latch, *slots)


def clark_comp(cal):
    """Clark Custom's IPSC race compensator (1980s, 0.575-40 on a race barrel): a short cylinder with flats on its
    sides and two wide ports across its top, about 38 x 24 mm (references/muzzle/clark_comp: Clark's own photo of the
    .38 Super / 9mm and .45 comps side by side, and one on a barrel). The two differ in bore (Clark: .390 / .475 in)."""
    bore = 4.9 if cal == "9mm" else 6.0
    def build(b):
        b.lathe("y", (0, 0, 0), [(0, bore), (0, 11.0), (0.8, 12.0), (37.2, 12.0), (38.0, 11.0), (38.0, bore)],
                seg=SEG, mat="metal")
    ob = solid(build, "Clark_Compensator_" + ("9mm" if cal == "9mm" else "45"))
    flats = [box_cutter("f%d" % i, x0, x1, -1.0, 39.0, -14.0, 14.0)
             for i, (x0, x1) in enumerate(((10.5, 14.0), (-14.0, -10.5)))]
    chamber = cyl_cutter("c", 7.0, 34.0, 7.5)
    ports = [box_cutter("p%d" % i, -8.5, 8.5, y, y + 6.5, 3.0, 14.0) for i, y in enumerate((13.0, 24.0))]
    return cut(ob, *flats, chamber, *ports)


def cutts():
    """The Cutts compensator (Thompson 1928, 1927): screwed on the 3/4-28 muzzle and pinned. A rear collar (the
    front sight's base on the gun; the blade stays the gun's own), the body with four slots across its top and a
    domed nose; about 58 x 24 mm (measured on an original, references/muzzle/cutts/cutts_06.jpg, body taken as 24 mm)."""
    def build(b):
        b.lathe("y", (0, 0, 0), [(0, 7.0), (0, 13.0), (13.0, 13.0), (13.5, 12.0), (48.0, 12.0), (52.0, 11.0),
                                  (55.0, 9.0), (57.0, 6.5), (58.0, 4.5)], seg=SEG, mat="metal")
    ob = solid(build, "Cutts_Compensator")
    chamber = cyl_cutter("c", 9.0, 52.0, 9.0)
    slots = [box_cutter("s%d" % i, -13.0, 13.0, y, y + 2.6, 2.4, 16.0)
             for i, y in enumerate((18.0, 23.0, 28.0, 33.0))]
    bore = cyl_cutter("b", -1.0, 59.0, 5.8)
    pin = cyl_cutter("p", -15.0, 15.0, 1.6, axis="x", at=(0, 6.5, -4.0))
    return cut(ob, chamber, bore, pin, *slots)


def sf3p():
    """SureFire SF3P-762 (5/8-24, SR25, M15x1, FAL and M14 versions), 66 mm: the rear lock collar with the ratchet
    teeth the SOCOM762-RC's latch catches, the bearing surface the can seals on, then three prongs with long open
    slots (references/muzzle/sf3p: SureFire's product shots)."""
    def build(b):
        b.lathe("y", (0, 0, 0), [(0, 6.0), (0, 13.0), (8.5, 13.0), (9.0, 11.5), (10.5, 11.5), (11.0, 12.2), (16.0, 12.2), (17.0, 11.3), (66.0, 11.3), (66.0, 9.2)], seg=SEG, mat="metal")
    ob = solid(build, "SF3P_Flash_Hider")
    inner = cyl_cutter("i", 22.0, 67.0, 9.2)
    tines = [box_cutter("t%d" % i, -2.3, 2.3, 26.0, 67.0, 0.0, 20.0,
                        rot=Matrix.Rotation(math.radians(60 + 120 * i), 4, 'Y')) for i in range(3)]
    teeth = [box_cutter("r%d" % i, -0.9, 0.9, 0.8, 7.5, 12.2, 16.0, rot=Matrix.Rotation(math.radians(15 * i), 4, 'Y'))
             for i in range(24)]
    bore = cyl_cutter("b", -1.0, 67.0, 4.2)
    return cut(ob, inner, *tines, *teeth, bore)


def sfmb():
    """SureFire SFMB-762 brake, 66 mm: the SF3P's collar and bearing surface, then a closed body with two big windows
    through each side, a small round port behind them, and a closed front around the bore (references/muzzle/sfmb)."""
    def build(b):
        b.lathe("y", (0, 0, 0), [(0, 6.0), (0, 13.0), (8.5, 13.0), (9.0, 11.5), (10.5, 11.5), (11.0, 12.2), (16.0, 12.2), (17.0, 11.3), (64.5, 11.3), (66.0, 10.3), (66.0, 4.6)], seg=SEG,
                mat="metal")
    ob = solid(build, "SFMB_Muzzle_Brake")
    inner = cyl_cutter("i", 24.0, 62.0, 8.5)
    windows = [box_cutter("w%d" % i, -15.0, 15.0, y, y + 8.5, -6.0, 6.0) for i, y in enumerate((40.0, 51.5))]
    port = cyl_cutter("p", -15.0, 15.0, 1.8, axis="x", at=(0, 33.0, 0))
    teeth = [box_cutter("r%d" % i, -0.9, 0.9, 0.8, 7.5, 12.2, 16.0, rot=Matrix.Rotation(math.radians(15 * i), 4, 'Y'))
             for i in range(24)]
    bore = cyl_cutter("b", -1.0, 67.0, 4.6)
    return cut(ob, inner, *windows, port, *teeth, bore)


def warcomp():
    """SureFire WarComp-762 (5/8-24, M15x1), 68 mm: the SF3P's collar, bearing surface and three prongs, with a
    cluster of round compensator ports on top behind the slots (references/muzzle/warcomp: SureFire's shot)."""
    def build(b):
        b.lathe("y", (0, 0, 0), [(0, 6.0), (0, 13.0), (8.5, 13.0), (9.0, 11.5), (10.5, 11.5), (11.0, 12.2), (16.0, 12.2), (17.0, 11.5), (68.0, 11.5), (68.0, 9.2)], seg=SEG, mat="metal")
    ob = solid(build, "WarComp_Flash_Hider")
    inner = cyl_cutter("i", 20.0, 69.0, 9.0)
    tines = [box_cutter("t%d" % i, -2.3, 2.3, 34.0, 69.0, 0.0, 20.0,
                        rot=Matrix.Rotation(math.radians(60 + 120 * i), 4, 'Y')) for i in range(3)]
    ports = [cyl_cutter("p%d" % i, 0.0, 15.0, 1.7, axis="z", at=(0, y, 0),
                        rot=Matrix.Rotation(math.radians(a), 4, 'Y'))
             for i, (y, a) in enumerate(((22.0, -25), (22.0, 25), (27.0, -40), (27.0, 0), (27.0, 40)))]
    teeth = [box_cutter("r%d" % i, -0.9, 0.9, 0.8, 7.5, 12.2, 16.0, rot=Matrix.Rotation(math.radians(15 * i), 4, 'Y'))
             for i in range(24)]
    bore = cyl_cutter("b", -1.0, 69.0, 4.2)
    return cut(ob, inner, *tines, *ports, *teeth, bore)


BUILDERS = {
    "AKM_Slant_Compensator": akm_slant,
    "AK74_Muzzle_Brake": ak74_brake,
    "AKS74U_Muzzle_Booster": aks74u_booster,
    "MP5_Flash_Hider": mp5_flash_hider,
    "Clark_Compensator_9mm": lambda: clark_comp("9mm"),
    "Cutts_Compensator": cutts,
    "Clark_Compensator_45": lambda: clark_comp("45"),
    "SF3P_Flash_Hider": sf3p,
    "SFMB_Muzzle_Brake": sfmb,
    "WarComp_Flash_Hider": warcomp,
}


# ==================================================================================================
# Painting: GoM's look (the Mk9's `common`): grain, light from above, AO, bright worn edges
# ==================================================================================================

BASE = {"metal": (46, 46, 48), "dark": (22, 22, 23)}            # sRGB: phosphate / black oxide, the port faces


def paint(maps):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    col *= (0.97 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = 55.0 * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 0.97, 0.92])
    col *= (1.0 - 0.3 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return np.clip(col, 0, 255)


def texture(ob, size, path):
    bake = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    maps = kit.bake_maps(ob, [ob], bake)
    if kit.DEBUG:
        kit.dump_maps(maps, os.path.join(kit.DEBUG, ob.name))
    col = paint(maps)
    m = maps["cover"]
    col = kit.dilate(np.where(m[..., None], col, 0), m, 4 * (bake // size))
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
    for mod in ("main", "post93"):
        obs = []
        for d in MD.of_mod(mod):
            ob = finish(BUILDERS[d["node"]](), d["scale"])
            kit.unwrap([ob], 0.012)
            os.makedirs(os.path.join(MEDIA[mod], TEX[mod]), exist_ok=True)
            texture(ob, 128, os.path.join(MEDIA[mod], TEX[mod], d["node"] + ".png"))
            b = kit.bounds_of(ob)
            print("%-24s tris %5d  min %s  max %s" % (d["node"], b["tris"], b["min"], b["max"]))
            obs.append(ob)
        kit.export(obs, os.path.join(MEDIA[mod], FBX[mod]))


if __name__ == "__main__":
    main()
