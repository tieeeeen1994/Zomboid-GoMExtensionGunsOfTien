#!/usr/bin/env python3
"""Inventory icons (32x32 RGBA) for the P90 TR assets, rendered from the exported FBX files and textures with the
framing of GoM's own icons (Python 3 + Pillow, no Blender).

GoM's icons are orthographic renders. make_art.fit_camera fitted a camera (yaw, pitch, roll for
make_art._rotate) to GoM's MP5 / FAMAS / suppressor / mount / magazine icons from their own meshes (CAMERAS
below, `--fit` repeats it); the P90 parts reuse those cameras and GoM's icon bounding boxes, so they lie at the
same angle and fill the icon the same way: guns diagonal with the muzzle top right, neutral grey and
anti-aliased; parts and magazines with GoM's cool blue cast and hard edges (measured on GoM's icons).

Usage: python3 p90_icons.py MEDIA          render the icons
       python3 p90_icons.py --fit [KEY]    re-fit CAMERAS (gun, supp, mount, mag) to GoM's icons
Writes MEDIA/textures/item_GunsOfTienPost93_{P90TR, 57x28Magazine50_P90, P90_Suppressor,
P90_Muzzle_Mount_Device}.png.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import make_art  # noqa: E402
import p90_geometry as G  # noqa: E402
import p90_meshio as IO  # noqa: E402

GOM = make_art.GOM

# Cameras from make_art.fit_camera on GoM's own icons and meshes (`--fit`, game space, scores in brackets):
#   mount  Muzzle_Mount_Device: yaw 268.0, pitch -0.5, roll 45.0 [33.2]: a plain side view turned 45 degrees,
#          rear bottom left; GoM's FAMAS icon fits the same view (silhouette 100 against 324 for its mirror).
#   supp   MKI_Suppressor fits yaw 196.0, pitch -61.5, roll -30.0 [27.8], the same silhouette for a cylinder;
#          the mount's view is used so text and ends face the same way.
#   mag    9x19Magazine30_MP5 fits yaw 231.0, pitch -4.0, roll 35.0 [29.1] (a 3/4 view of a curved box mag);
#          the flat P90 magazine gets the side view pitched 35 degrees so its top and rounds show.
#   gun    GoM's MP5 / FAMAS: see GUN_FIT below.
# bbox = the icon pixels GoM's render fills (make_art.alpha_bbox of item_MP5 / MKI / Mount / 9x19 mag).
CAMERAS = {
    "gun": dict(yaw=270.0, pitch=0.0, roll=45.0, bbox=(0, 1, 32, 31)),
    "supp": dict(yaw=268.0, pitch=-0.5, roll=45.0, bbox=(0, 1, 32, 31)),
    "mount": dict(yaw=268.0, pitch=-0.5, roll=45.0, bbox=(0, 1, 31, 32)),
    "mag": dict(yaw=270.0, pitch=35.0, roll=40.0, bbox=(1, 1, 31, 32)),
}

LIGHT = (-0.45, -0.65, 0.62)          # screen space: x right, y down, z towards the viewer


def _norm(v):
    n = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / n for c in v)


def render(meshes, camera, size=32, ss=8, gain=1.0, tint=(1.0, 1.0, 1.0), hard=False, ambient=0.5, diffuse=0.8):
    """meshes = [(tris, texture)]; returns an RGBA icon."""
    yaw, pitch, roll = camera["yaw"], camera["pitch"], camera.get("roll", 0.0)
    light = _norm(LIGHT)
    proj = []
    for tris, tex in meshes:
        px = tex.convert("RGB").load()
        tw, th = tex.size
        for ps, uvs in tris:
            q = [make_art._rotate(p, yaw, pitch, roll) for p in ps]
            a, b, c = q
            n = _norm(((b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]),
                       (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]),
                       (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])))
            if n[2] < 0:
                n = tuple(-k for k in n)
            lit = ambient + diffuse * max(0.0, sum(n[k] * light[k] for k in range(3)))
            proj.append((q, uvs, px, tw, th, lit))
    xs = [p[0] for q, *_ in proj for p in q]
    ys = [p[1] for q, *_ in proj for p in q]
    bx0, by0, bx1, by1 = camera["bbox"]
    scale = min((bx1 - bx0) / (max(xs) - min(xs)), (by1 - by0) / (max(ys) - min(ys))) * ss
    ox = bx0 * ss + ((bx1 - bx0) * ss - (max(xs) - min(xs)) * scale) / 2
    oy = by0 * ss + ((by1 - by0) * ss - (max(ys) - min(ys)) * scale) / 2
    side = size * ss
    col = [[None] * side for _ in range(side)]
    depth = [[-1e30] * side for _ in range(side)]
    for q, uvs, px, tw, th, lit in proj:
        pts = [((p[0] - min(xs)) * scale + ox, (p[1] - min(ys)) * scale + oy, p[2]) for p in q]

        def store(x, y, d, uv, px=px, tw=tw, th=th, lit=lit):
            if d > depth[y][x]:
                depth[y][x] = d
                c = px[min(tw - 1, max(0, int(uv[0] % 1.0 * tw))), min(th - 1, max(0, int((1 - uv[1] % 1.0) * th)))]
                col[y][x] = tuple(c[k] * lit * gain * tint[k] for k in range(3))

        make_art._fill_triangle(pts, uvs, side, side, store)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    o = out.load()
    for y in range(size):
        for x in range(size):
            acc, n = [0.0, 0.0, 0.0], 0
            for j in range(ss):
                for i in range(ss):
                    c = col[y * ss + j][x * ss + i]
                    if c is not None:
                        acc = [acc[k] + c[k] for k in range(3)]
                        n += 1
            if not n:
                continue
            a = n / (ss * ss)
            if hard:
                if a < 0.5:
                    continue
                a = 1.0
            o[x, y] = tuple(make_art.clamp8(acc[k] / n) for k in range(3)) + (make_art.clamp8(a * 255),)
    return out


def centred(tris):
    pts = [p for ps, _ in tris for p in ps]
    c = [(min(p[k] for p in pts) + max(p[k] for p in pts)) / 2 for k in range(3)]
    return [(tuple(tuple(p[k] - c[k] for k in range(3)) for p in ps), uv) for ps, uv in tris]


def assets(media):
    fx = os.path.join(media, "models_X/weapons")
    tx = os.path.join(media, "textures/weapons/GunsOfTienPost93")
    pts = G.points()
    gun = IO.load_game_mesh(os.path.join(fx, "firearms/GunsOfTienPost93_P90TR.fbx"), "P90TR_BODY") + \
        IO.load_game_mesh(os.path.join(fx, "firearms/GunsOfTienPost93_P90TR.fbx"), "P90TR_BOLT")
    magf = os.path.join(fx, "magazines/GunsOfTienPost93_P90_magazines.fbx")
    mag_on = IO.load_game_mesh(magf, "57x28Magazine50_P90", pts["magazine"]["offset"])
    mag = IO.load_game_mesh(magf, "57x28Magazine50_P90")
    partf = os.path.join(fx, "parts/GunsOfTienPost93_P90_parts.fbx")
    supp = IO.load_game_mesh(partf, "P90_Suppressor")
    mount = IO.load_game_mesh(partf, "P90_Muzzle_Mount_Device")
    tex = {k: Image.open(os.path.join(tx, k + ".png")) for k in
           ("P90TR", "57x28Magazine50_P90", "P90_Suppressor", "P90_Muzzle_Mount_Device")}
    # One common centre for the gun and its fitted magazine.
    allp = [p for ps, _ in gun + mag_on for p in ps]
    c = [(min(p[k] for p in allp) + max(p[k] for p in allp)) / 2 for k in range(3)]
    shift = lambda tris: [(tuple(tuple(p[k] - c[k] for k in range(3)) for p in ps), uv) for ps, uv in tris]
    return {
        "gun": [(shift(gun), tex["P90TR"]), (shift(mag_on), tex["57x28Magazine50_P90"])],
        "mag": [(centred(mag), tex["57x28Magazine50_P90"])],
        "supp": [(centred(supp), tex["P90_Suppressor"])],
        "mount": [(centred(mount), tex["P90_Muzzle_Mount_Device"])],
    }


BLUE = (0.86, 0.95, 1.22)          # GoM's part icons: B about 15 above R at lum ~40


def main(media):
    a = assets(media)
    out = os.path.join(media, "textures")
    jobs = (("gun", "item_GunsOfTienPost93_P90TR.png", dict(gain=1.25)),
            ("mag", "item_GunsOfTienPost93_57x28Magazine50_P90.png", dict(gain=1.15, tint=BLUE, hard=True)),
            ("supp", "item_GunsOfTienPost93_P90_Suppressor.png", dict(gain=0.95, tint=BLUE, hard=True)),
            ("mount", "item_GunsOfTienPost93_P90_Muzzle_Mount_Device.png", dict(gain=1.05, tint=BLUE, hard=True)))
    for key, name, kw in jobs:
        icon = render(a[key], CAMERAS[key], **kw)
        path = os.path.join(out, name)
        icon.save(path, optimize=False)
        print("[p90_icons] wrote", path)


def fit():
    """Fit cameras to GoM's icons from GoM's meshes (slow: minutes)."""
    g = GOM + "/"
    rot = lambda p, d: (p[0], p[1] * math.cos(math.radians(d)) - p[2] * math.sin(math.radians(d)),
                        p[1] * math.sin(math.radians(d)) + p[2] * math.cos(math.radians(d)))
    body = IO.load_game_mesh(g + "models_X/weapons/firearms/MP5.fbx", "MP5_BODY") + \
        IO.load_game_mesh(g + "models_X/weapons/firearms/MP5.fbx", "MP5_BOLT")
    m = IO.load_game_mesh(g + "models_X/weapons/magazines/smgs.fbx", "9x19Magazine20_MP5")
    m = [(tuple(tuple(a + b for a, b in zip(rot(p, 10.2946), (0, 0.1191, 0.0377))) for p in ps),
          ((0.001, 0.999),) * 3) for ps, _ in m]
    jobs = {
        "gun": (centred(body + m), g + "textures/weapons/firearms/smgs/MP5.png", g + "textures/item_MP5.png"),
        "supp": (centred(IO.load_game_mesh(g + "models_X/weapons/parts/suppressors.fbx", "MKI_Suppressor")),
                 g + "textures/weapons/parts/suppressors/MKI_Suppressor.png", g + "textures/item_MKI_Suppressor.png"),
        "mount": (centred(IO.load_game_mesh(g + "models_X/weapons/parts/muzzles.fbx", "Muzzle_Mount_Device")),
                  g + "textures/weapons/parts/muzzles/Muzzle_Mount_Device.png",
                  g + "textures/item_Muzzle_Mount_Device.png"),
        "mag": (centred(IO.load_game_mesh(g + "models_X/weapons/magazines/smgs.fbx", "9x19Magazine30_MP5")),
                g + "textures/weapons/magazines/smgs/9x19Magazine30_MP5.png",
                g + "textures/item_9x19Magazine30_MP5.png"),
    }
    only = [a for a in sys.argv[2:] if not a.startswith("-")]
    for key, (tris, tex, icon) in jobs.items():
        if only and key not in only:
            continue
        err, cam = make_art.fit_camera(Image.open(icon), tris, Image.open(tex))
        print('    "%s": dict(yaw=%.1f, pitch=%.1f, roll=%.1f, bbox=%r),  # score %.1f'
              % (key, cam["yaw"], cam["pitch"], cam["roll"], tuple(cam["bbox"]), err))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--fit"]:
        fit()
    else:
        main(sys.argv[1])
