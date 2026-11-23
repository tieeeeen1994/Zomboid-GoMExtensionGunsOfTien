"""
Where GoM's parts would sit on GoM guns that lack a point for them (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/gom_points.py -- <out.txt>

Written for the 2026-11-23 attachment audit (docs/attachments_audit.md): seven of GoM's guns let a bipod onto their
bottom rail with no `bipod` point and no model line, and the AA-12 lets side rails, lights and lasers on with no
points at all. For each gun this prints, in game units x 1000 along the barrel (Y) and height (Z):
  - the bottom rail as GoM draws it (its `rail_down` point + GoM's rail model) and the foregrips at `foregrip`;
  - the bipods placed the way GoM places them on the M16A2 (the same offset from the front of the rail), whether
    they still sit on the rail, whether they overlap any foregrip along the barrel, and how deep they sink into the
    gun body (fit_audit.py's measure: ray parity);
  - for the AA-12, the body's half width and the rail's height at the handguard, for the side points.
The model / item parsing is scale_audit.py's (run up to its measuring loop), the measuring fit_audit.py's.
"""

import sys

from mathutils import Vector

_src = open(__file__.replace("gom_points.py", "fit_audit.py")).read()
_src = _src[:_src.index("\nlines = []")]           # parsing, place(), body_tree(), measure()
_g = {"__file__": __file__.replace("gom_points.py", "fit_audit.py"), "__name__": "gom_points"}
exec(compile(_src, "fit_audit.py", "exec"), _g)
models, items, mesh_of, place, measure, body_tree = (_g[k] for k in ("models", "items", "mesh_of", "place", "measure",
                                                                      "body_tree"))

GUNS = ["M16A2", "AR15", "M4A1", "XM177", "CAR15", "G36", "G36C", "MP5", "MP5A2", "MP5SD", "AA12"]
FOREGRIPS = ["MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip"]
BIPODS = ["MarzGuns.Bipod_Deployed", "MarzGuns.Bipod_Folded"]
RAIL = "MarzGuns.Picatinny_Rail_Down"
out = []
w = out.append


def ext(verts, axis):
    vs = [v[axis] for v in verts]
    return min(vs), max(vs)


def part_at(gm, pmodel, point_offset):
    """The part's vertices with its parent point at `point_offset` (rotations are all zero here)."""
    saved = models[gm]["att"].get("_probe")
    models[gm]["att"]["_probe"] = (list(point_offset), [0, 0, 0], 1.0)
    pv = place(gm, pmodel, pmodel_point(pmodel), "_probe")
    if saved is None:
        del models[gm]["att"]["_probe"]
    return pv


def pmodel_point(pmodel):
    # GoM's lines use the same name on both sides (bipod bipod, foregrip foregrip, rail_down rail_down)
    for name in ("bipod", "foregrip", "rail_down", "rail_left", "rail_right", "light_left", "laser_right"):
        if name in models[pmodel]["att"]:
            return name
    return "world"


ref = models["MarzGuns.M16A2"]["att"]
# the M16A2's bipod against the front of its bottom rail
rail_y = ext(part_at("MarzGuns.M16A2", RAIL, ref["rail_down"][0]), 1)
BIPOD_FROM_RAIL_FRONT = ref["bipod"][0][1] - rail_y[1]
BIPOD_DZ = ref["bipod"][0][2] - ref["rail_down"][0][2]
w("M16A2: rail Y %.1f..%.1f, bipod point %.1f from the rail's front, %.1f below rail_down"
  % (rail_y[0] * 1000, rail_y[1] * 1000, BIPOD_FROM_RAIL_FRONT * 1000, -BIPOD_DZ * 1000))

for name in GUNS:
    gm = "MarzGuns." + name
    att = models[gm]["att"]
    w("\n== %s (%s)" % (name, models[gm]["mesh"]))
    body = mesh_of(gm)[0]
    by = ext(body, 1)
    w("  body Y %.1f..%.1f" % (by[0] * 1000, by[1] * 1000))
    if "rail_down" not in att:
        w("  no rail_down point")
        continue
    rd = att["rail_down"][0]
    r = ext(part_at(gm, RAIL, rd), 1)
    w("  rail_down at Y %.1f Z %.1f: rail Y %.1f..%.1f" % (rd[1] * 1000, rd[2] * 1000, r[0] * 1000, r[1] * 1000))
    fg = []
    if "foregrip" in att:
        for f in FOREGRIPS:
            e = ext(part_at(gm, f, att["foregrip"][0]), 1)
            fg.append(e)
            w("  %-22s Y %.1f..%.1f" % (f.split(".")[1], e[0] * 1000, e[1] * 1000))
    if "bipod" in att:
        bp = att["bipod"][0]
        w("  bipod point (GoM's) Y %.1f Z %.1f" % (bp[1] * 1000, bp[2] * 1000))
    else:
        bp = [rd[0], r[1] + BIPOD_FROM_RAIL_FRONT, rd[2] + BIPOD_DZ]
        w("  bipod point (as on the M16A2) Y %.1f Z %.1f" % (bp[1] * 1000, bp[2] * 1000))
    for b in BIPODS:
        pv = part_at(gm, b, bp)
        e = ext(pv, 1)
        gap, depth = measure(gm, pv)
        over = max([min(e[1], f[1]) - max(e[0], f[0]) for f in fg] or [0])
        w("  %-22s Y %.1f..%.1f  overlaps foregrips by %.1f  in body %.1f (gap %.1f)"
          % (b.split(".")[1], e[0] * 1000, e[1] * 1000, max(over, 0) * 1000, depth, gap))
    if name == "AA12":
        # half width and top of the body along the handguard (rail_down's span), for side rails
        span = [v for v in body if r[0] <= v[1] <= r[1]]
        xs = ext(span, 0)
        zs = ext(span, 2)
        w("  handguard (Y %.1f..%.1f): X %.1f..%.1f  Z %.1f..%.1f" % (r[0] * 1000, r[1] * 1000, xs[0] * 1000,
                                                                       xs[1] * 1000, zs[0] * 1000, zs[1] * 1000))
        # the handguard is a box with few vertices, so its sides are found by rays from each side
        tree = body_tree(gm, with_mounts=False)
        for y0 in range(140, 341, 20):
            row = []
            for z0 in (5, 10, 15, 20, 25, 30, 35, 40):
                hits = []
                for sx in (1, -1):
                    loc = tree.ray_cast(Vector((sx * 0.2, y0 / 1000, z0 / 1000)), Vector((-sx, 0, 0)))[0]
                    hits.append("%5.1f" % (loc.x * 1000) if loc else "  -  ")
                row.append("Z%2d %s/%s" % (z0, hits[0], hits[1]))
            top = tree.ray_cast(Vector((0, y0 / 1000, 0.2)), Vector((0, 0, -1)))[0]
            bot = tree.ray_cast(Vector((0, y0 / 1000, -0.2)), Vector((0, 0, 1)))[0]
            w("    Y %3d top %s bottom %s | %s" % (y0, "%.1f" % (top.z * 1000) if top else "-",
                                                  "%.1f" % (bot.z * 1000) if bot else "-", "  ".join(row)))
        # side rails at rail_down's Y: for each height, the point X that sinks GoM's rail as deep as GoM sinks it
        # (its base 1.1 into the body), then the light and laser at the M16A2's offsets from that rail
        m16 = models["MarzGuns.M16A2"]["att"]
        d_light = [m16["light_left"][0][i] - m16["rail_left"][0][i] for i in range(3)]
        d_laser = [m16["laser_right"][0][i] - m16["rail_right"][0][i] for i in range(3)]
        for z0 in (16, 18, 20, 22, 24):
            for side, rail, extra, d in ((1, "MarzGuns.Picatinny_Rail_Left", "MarzGuns.BrightPoint-5_Light", d_light),
                                         (-1, "MarzGuns.Picatinny_Rail_Right", "MarzGuns.AimRight_Laser", d_laser)):
                x = 0.010
                while x < 0.030:
                    gap, depth = measure(gm, part_at(gm, rail, (side * x, rd[1], z0 / 1000)))
                    if depth <= 1.2:
                        break
                    x += 0.0001
                pt = (side * x, rd[1], z0 / 1000)
                ex = [pt[i] + d[i] for i in range(3)]
                g2, d2 = measure(gm, part_at(gm, extra, ex))
                g3, d3 = measure(gm, part_at(gm, "MarzGuns.LRX-7_Laser" if side < 0 else "MarzGuns.SR7_Light", ex))
                w("  side Z %d %-5s rail point X %.1f (in %.1f gap %.1f) -> %s point (%.1f, %.1f, %.1f) in %.1f / %.1f"
                  % (z0, "left" if side > 0 else "right", side * x * 1000, depth, gap,
                     "light" if side > 0 else "laser", ex[0] * 1000, ex[1] * 1000, ex[2] * 1000, d2, d3))
        # GoM's side rail parts on the M16A2: their own height against the rail_left point
        for p in ("MarzGuns.Picatinny_Rail_Left", "MarzGuns.BrightPoint-5_Light", "MarzGuns.AimRight_Laser"):
            pv = part_at("MarzGuns.M16A2", p, (0, 0, 0))
            w("  %s at the origin: X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (
                p, *(c * 1000 for a in range(3) for c in ext(pv, a))))

out_path = sys.argv[sys.argv.index("--") + 1]
open(out_path, "w").write("\n".join(out) + "\n")
print("gom_points -> " + out_path)
