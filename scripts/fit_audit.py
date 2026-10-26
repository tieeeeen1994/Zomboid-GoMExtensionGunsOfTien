"""
How every part sits on Guns of Tien's guns, against the same part on Guns of Marz's guns (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/fit_audit.py -- <out.txt>

Written after our guns were resized in their meshes (user, 2026-10-26: "audit again all our guns"): GoM's parts keep
GoM's sizes, so the question per part is whether it sits on our gun the way it sits on GoM's own. For every
ModelWeaponPart line of every gun (our 13 and every GoM gun that lists one of the same part models), the part's mesh
is placed as the engine draws it (the gun's parent point, the part model's own point of the same name, the part
model's scale) and measured against the gun's body mesh plus every rail and mount part the gun lists (GoM fits its
rails and mounts as parts, so its optics float above the bare body; ours are partly modelled in the body): `gap` = how far its nearest vertex is from the body (0 when
it touches or goes in), `in` = how deep its deepest vertex is inside the body (ray parity, three directions). Values in
game units x 1000. A part on our gun is flagged when it floats (gap) or sinks (in) more than 3 more than its median on
GoM's guns. Also per gun: the muzzle point against the front of the barrel, the canon point against the barrel.
The model / item parsing is scale_audit.py's (run up to its measuring loop).
"""

import math
import statistics
import sys

from mathutils import Vector
from mathutils.bvhtree import BVHTree

_src = open(__file__.replace("fit_audit.py", "scale_audit.py")).read()
_src = _src[:_src.index("\nguns = {}")]
_g = {"__file__": __file__.replace("fit_audit.py", "scale_audit.py"), "__name__": "scale_audit_parse"}
exec(compile(_src, "scale_audit.py", "exec"), _g)
models, items, mesh_of, rotate_xyz = _g["models"], _g["items"], _g["mesh_of"], _g["rotate_xyz"]
NOT_ACCESSORY = _g["NOT_ACCESSORY"]
OURS = ("GunsOfTien.", "GunsOfTienPost93.", "MarzGuns.FIVESEVEN")
LIMIT = 3.0


def ours(full):
    return full.startswith(OURS)


def place(gun_model, part_model, a_self, a_parent):
    pv, pp = mesh_of(part_model)                  # already x the part model's scale
    o, r, s = models[gun_model]["att"].get(a_parent, ([0, 0, 0], [0, 0, 0], 1.0))
    so, sr, ss = models[part_model]["att"].get(a_self, ([0, 0, 0], [0, 0, 0], 1.0))
    out = []
    for v in pv:
        v = rotate_xyz(v, sr)
        v = tuple(so[i] + c * ss for i, c in enumerate(v))
        v = rotate_xyz(v, r)
        out.append(tuple(o[i] + c * s for i, c in enumerate(v)))
    return out


trees = {}
MOUNT = ("Rail", "Mount")         # parts other parts sit on: GoM's guns carry their rails and mounts as parts, ours
                                  # partly in the body (SCARs, UMPs) and partly as parts (MP7, P90)
MOUNT_FOR = {}                    # gun model -> [(part model, self point, parent point)] of its rails and mounts


def body_tree(gun_model, with_mounts=True):
    key = (gun_model, with_mounts)
    if key not in trees:
        verts, polys = mesh_of(gun_model)
        verts, polys = [Vector(v) for v in verts], list(polys)
        if with_mounts:
            for pmodel, a_self, a_parent in MOUNT_FOR.get(gun_model, []):
                pv, pp = mesh_of(pmodel)
                base = len(verts)
                verts += [Vector(v) for v in place(gun_model, pmodel, a_self, a_parent)]
                polys += [tuple(i + base for i in poly) for poly in pp]
        trees[key] = BVHTree.FromPolygons(verts, polys)
    return trees[key]


DIRS = (Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0.3, 0.2, -0.93)).normalized())


def is_inside(tree, p):
    """Ray parity, majority of three directions (GoM's meshes are double-sided, so face normals cannot tell)."""
    votes = 0
    for d in DIRS:
        o, hits = p.copy(), 0
        for _ in range(64):
            loc, _, _, _ = tree.ray_cast(o, d)
            if loc is None:
                break
            hits += 1
            o = loc + d * 1e-6
        votes += hits % 2
    return votes >= 2


def measure(gun_model, placed):
    tree = body_tree(gun_model)
    gap, depth = 1e9, 0.0
    for v in placed:
        loc, normal, _, dist = tree.find_nearest(Vector(v))
        if loc is None:
            continue
        inside = is_inside(tree, Vector(v))
        if inside:
            depth = max(depth, dist)
            gap = 0.0
        else:
            gap = min(gap, dist)
    return gap * 1000, depth * 1000


def muzzle_check(gun_model):
    att = models[gun_model]["att"]
    if "muzzle" not in att:
        return None
    m = att["muzzle"][0]
    verts, _ = mesh_of(gun_model)
    near = [v for v in verts if math.hypot(v[0] - m[0], v[2] - m[2]) < 0.012]
    if not near:
        return None
    front = max(v[1] for v in near)
    return (m[1] - front) * 1000


for full, it in items.items():
    gm = it["sprite"]
    for part, pmodel, a_self, a_parent in it["parts"]:
        pname = part.split(".")[-1]
        if any(m in pname for m in MOUNT) and pmodel in models and models[pmodel]["mesh"]:
            lst = MOUNT_FOR.setdefault(gm, [])
            if (pmodel, a_self, a_parent) not in lst:
                lst.append((pmodel, a_self, a_parent))

lines = []
results = {}                                       # (part model) -> [(gun, gap, in)]
for full, it in sorted(items.items()):
    gm = it["sprite"]
    if gm not in models or not models[gm]["mesh"] or it["swing"] in ("Throw", "Stab", "Spear"):
        continue
    for part, pmodel, a_self, a_parent in it["parts"]:
        pname = part.split(".")[-1]
        if any(s in pname for s in NOT_ACCESSORY) or pmodel not in models or not models[pmodel]["mesh"]:
            continue
        if any(m in pname for m in MOUNT):
            continue                              # measured as part of the body the others sit on
        try:
            gap, depth = measure(gm, place(gm, pmodel, a_self, a_parent))
        except KeyError:
            continue
        results.setdefault(pmodel, []).append((full, gap, depth, a_parent))

our_guns = sorted(f for f in items if ours(f))
for gun in our_guns:
    gm = items[gun]["sprite"]
    mz = muzzle_check(gm)
    lines.append("== %s (%s)%s" % (gun, gm, "  muzzle point %+.1f from the barrel's front" % mz if mz is not None else ""))
    for pmodel, rows in sorted(results.items()):
        mine = [r for r in rows if r[0] == gun]
        if not mine:
            continue
        _, gap, depth, point = mine[0]
        base = [r for r in rows if not ours(r[0])]
        if base:
            bg = statistics.median(r[1] for r in base)
            bd = statistics.median(r[2] for r in base)
            flag = ""
            if gap - bg > LIMIT:
                flag = "  <- floats %.1f more than on GoM's guns" % (gap - bg)
            elif depth - bd > LIMIT:
                flag = "  <- sinks %.1f deeper than on GoM's guns" % (depth - bd)
            lines.append("  %-44s at %-14s gap %5.1f in %5.1f | GoM's %d guns: gap %5.1f in %5.1f%s" % (
                pmodel, point, gap, depth, len(base), bg, bd, flag))
        else:
            lines.append("  %-44s at %-14s gap %5.1f in %5.1f | ours only" % (pmodel, point, gap, depth))

out = sys.argv[sys.argv.index("--") + 1]
open(out, "w").write("\n".join(lines) + "\n")
print("fit_audit: %d of our guns -> %s" % (len(our_guns), out))


# ---- --solve: for every point of our guns with a flagged part, the shift along the point's outward axis (Z for
# rails, sign from where the parts lie; Y for `canon`) that puts the median signed depth (in, or minus the gap) of
# the parts at that point on the median of the same parts on GoM's guns.
def signed(gun_model, placed):
    gap, depth = measure(gun_model, placed)
    return depth if depth > 0 else -gap


if "--solve" in sys.argv:
    sol = []
    for gun in our_guns:
        gm = items[gun]["sprite"]
        by_point = {}
        for part, pmodel, a_self, a_parent in items[gun]["parts"]:
            if pmodel in results and any(r[0] == gun for r in results[pmodel]):
                by_point.setdefault(a_parent, []).append((pmodel, a_self))
        for point, plist in sorted(by_point.items()):
            if point not in ("scope", "foregrip", "canon", "rail_up", "underbarrel", "bipod", "rail_down"):
                continue
            base, cur = [], []
            for pmodel, a_self in plist:
                rows = [r for r in results[pmodel] if not ours(r[0])]
                if not rows:
                    continue
                base.append(statistics.median((r[2] if r[2] > 0 else -r[1]) for r in rows))
                cur.append((pmodel, a_self))
            if not cur:
                continue
            target = statistics.median(base)
            o = models[gm]["att"][point][0]
            pv = [place(gm, pm, a_s, point) for pm, a_s in cur]
            centre = [sum(v[i] for P in pv for v in P) / sum(len(P) for P in pv) for i in range(3)]
            axis = 1 if point == "canon" else 2
            sgn = 1.0 if centre[axis] >= o[axis] else -1.0

            def med(shift):
                d = [0, 0, 0]
                d[axis] = sgn * shift
                return statistics.median(signed(gm, [tuple(v[i] + d[i] for i in range(3)) for v in P]) for P in pv)

            now = med(0.0)
            if abs(now - target) <= LIMIT:
                continue
            lo, hi = -0.02, 0.02                  # signed depth falls as the shift grows
            for _ in range(30):
                mid = (lo + hi) / 2
                if med(mid) > target:
                    lo = mid
                else:
                    hi = mid
            shift = (lo + hi) / 2
            sol.append("%s %s: median %.1f, GoM's %.1f -> move %+.4f along %s%s (now %.1f)" % (
                gun, point, now, target, sgn * shift, "-" if sgn < 0 else "+", "YZ"[axis - 1], med(shift)))
    open(out.replace(".txt", "_solve.txt"), "w").write("\n".join(sol) + "\n")
    print("\n".join(sol))
