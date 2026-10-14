"""FN P90 TR geometry for GoM Extension: Guns of Tien - Post-93, as plain Python (no Blender, no numpy).

Everything is drawn in real millimetres in a side-view frame, then scaled to game space:
    u = along the gun, 0 at the butt plate, 500 at the muzzle (real overall length 500 mm)
    v = height, 0 at the bottom of the trigger guard / stock
    x = sideways, + = the gun's LEFT (GoM: +X is the gun's left)
Game space (GoM rifle convention): y = (u - U0) * S (+Y muzzle), z = (v - V0) * S (+Z top), x = x * S,
with S = 0.72 / 1000 (GoM draws its SMGs at ~0.72 of real size) and (U0, V0) the rear-top of the pistol grip,
where it meets the receiver. Like GoM's FAMAS (its only bullpup), the body and the magazine lie behind the grip.

build_p90.py (Blender) turns the parts below into meshes; nothing here depends on bpy, so the numbers can be
checked with plain Python:  python3 p90_geometry.py   prints the parts, their triangle counts and the points.

A part is a dict: {"verts": [(x, u, v)], "faces": [(i, j, k, ...)], "mat": name}. Faces may be concave ngons
(Blender triangulates them); winding is fixed afterwards (normals recalculated outwards).
"""

import math

S = 0.72 / 1000.0          # game units per real millimetre
U0, V0 = 235.0, 80.0       # rear-top of the pistol grip (model origin)

BORE_V = 100.0             # bore axis height
NOSE_U = 468.0             # front face of the receiver: the flash hider starts here (= `canon`)
MUZZLE_U = 500.0           # flash hider tip (= `muzzle`)
RAIL_TOP_V = 169.0         # top of the Picatinny teeth
MAG_FRONT_U, MAG_BASE_V = 375.0, 122.0   # magazine origin: front end, centre, on the receiver top
MAG_LEN, MAG_H, MAG_W = 250.0, 25.0, 50.0
HANDLE_U, HANDLE_V = 352.0, 107.0       # charging handle knobs, forward position
HANDLE_TRAVEL = 60.0                    # slot length behind the knobs
EJECT_U = (184.0, 214.0)                # downward ejection port, behind the grip


def to_game(x, u, v):
    return (x * S, (u - U0) * S, (v - V0) * S)


# --------------------------------------------------------------------------------------------------
# 2D helpers
# --------------------------------------------------------------------------------------------------

def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _len(a):
    return math.hypot(a[0], a[1])


def _norm(a):
    n = _len(a) or 1.0
    return (a[0] / n, a[1] / n)


def area2(poly):
    return sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly)))


def ccw(poly):
    return poly if area2(poly) > 0 else list(reversed(poly))


def rounded(points, seg=3):
    """Polygon from corners [(u, v, r)]: each corner with r > 0 becomes a quadratic Bezier fillet of seg+1 points."""
    out = []
    n = len(points)
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        r = p1[2] if len(p1) > 2 else 0.0
        c = (p1[0], p1[1])
        if r <= 0:
            out.append(c)
            continue
        d1 = _sub((p0[0], p0[1]), c)
        d2 = _sub((p2[0], p2[1]), c)
        t1 = min(r, 0.48 * _len(d1))
        t2 = min(r, 0.48 * _len(d2))
        a = (c[0] + _norm(d1)[0] * t1, c[1] + _norm(d1)[1] * t1)
        b = (c[0] + _norm(d2)[0] * t2, c[1] + _norm(d2)[1] * t2)
        for k in range(seg + 1):
            t = k / seg
            out.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
                        (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]))
    return out


def inset(poly, d):
    """Offset a CCW polygon inwards by d (miter, clamped)."""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % n]
        e1 = _norm(_sub(p1, p0))
        e2 = _norm(_sub(p2, p1))
        n1 = (-e1[1], e1[0])
        n2 = (-e2[1], e2[0])
        m = _norm((n1[0] + n2[0], n1[1] + n2[1]))
        cos_half = max(0.35, m[0] * n1[0] + m[1] * n1[1])
        k = d / cos_half
        out.append((p1[0] + m[0] * k, p1[1] + m[1] * k))
    return out


# --------------------------------------------------------------------------------------------------
# Solids
# --------------------------------------------------------------------------------------------------

def part(mat):
    return {"verts": [], "faces": [], "mat": mat}


def merge(dst, src):
    base = len(dst["verts"])
    dst["verts"] += src["verts"]
    dst["faces"] += [tuple(i + base for i in f) for f in src["faces"]]
    dst.setdefault("face_mats", [])
    dst["face_mats"] += src.get("face_mats", [src["mat"]] * len(src["faces"]))
    return dst


def slab(outline, width, radius, steps=2, x0=0.0, mat="polymer"):
    """Side-view outline (u, v) extruded across x (centred on x0) with rounded edges of the given radius."""
    outline = ccw(outline)
    p = part(mat)
    n = len(outline)
    half = width / 2.0
    rings = []           # (x, polygon) from -x cap to +x cap
    profile = []
    for k in range(steps + 1):
        th = (math.pi / 2) * k / steps
        profile.append((radius * (1 - math.cos(th)), (half - radius) + radius * math.sin(th)))
    for d, x in reversed(profile):
        rings.append((x0 - x, inset(outline, d) if d > 1e-6 else outline))
    for d, x in profile:
        rings.append((x0 + x, inset(outline, d) if d > 1e-6 else outline))
    for x, poly in rings:
        p["verts"] += [(x, q[0], q[1]) for q in poly]
    for r in range(len(rings) - 1):
        a, b = r * n, (r + 1) * n
        for i in range(n):
            j = (i + 1) % n
            p["faces"].append((a + i, a + j, b + j, b + i))
    last = (len(rings) - 1) * n
    p["faces"].append(tuple(reversed(range(n))))
    p["faces"].append(tuple(range(last, last + n)))
    return p


def section(sec, u0, u1, mat="polymer"):
    """Cross-section (x, v) extruded along u from u0 to u1, capped."""
    sec = ccw(sec)
    p = part(mat)
    n = len(sec)
    p["verts"] += [(q[0], u0, q[1]) for q in sec] + [(q[0], u1, q[1]) for q in sec]
    for i in range(n):
        j = (i + 1) % n
        p["faces"].append((i, j, n + j, n + i))
    p["faces"].append(tuple(reversed(range(n))))
    p["faces"].append(tuple(range(n, 2 * n)))
    return p


def lathe(rings, segs, axis="u", centre=(0.0, 0.0), mat="metal", cap0=True, cap1=True):
    """Surface of revolution: rings [(t, r)] along the axis ('u' with centre (x, v); 'x' with centre (u, v);
    'v' with centre (x, u)). A ring with r == 0 is a pole."""
    p = part(mat)
    idx = []

    def place(t, c, d):
        if axis == "u":
            p["verts"].append((c, t, d))
        elif axis == "x":
            p["verts"].append((t, c, d))
        else:
            p["verts"].append((c, d, t))
        return len(p["verts"]) - 1

    for t, r in rings:
        if r <= 0:
            idx.append(place(t, centre[0], centre[1]))       # pole
            continue
        ring = []
        for s in range(segs):
            a = 2 * math.pi * (s + 0.5) / segs
            ring.append(place(t, centre[0] + r * math.cos(a), centre[1] + r * math.sin(a)))
        idx.append(ring)
    for a, b in zip(idx, idx[1:]):
        for s in range(segs):
            q = (s + 1) % segs
            if isinstance(a, int):
                p["faces"].append((a, b[q], b[s]))
            elif isinstance(b, int):
                p["faces"].append((a[s], a[q], b))
            else:
                p["faces"].append((a[s], a[q], b[q], b[s]))
    if cap0 and not isinstance(idx[0], int):
        p["faces"].append(tuple(reversed(idx[0])))
    if cap1 and not isinstance(idx[-1], int):
        p["faces"].append(tuple(idx[-1]))
    return p


def box(x0, x1, u0, u1, v0, v1, mat="polymer"):
    return section([(x0, v0), (x1, v0), (x1, v1), (x0, v1)], u0, u1, mat)


# --------------------------------------------------------------------------------------------------
# The P90 TR
# --------------------------------------------------------------------------------------------------

def body_parts():
    parts = []

    # Upper receiver: the wide shell between the holes' tops and the magazine bed, with the rounded nose.
    upper = rounded([
        (60, 79, 0), (430, 79, 0), (452, 83, 8), (467, 94, 8), (468, 110, 6), (458, 121, 8), (440, 123, 0),
        (60, 123, 0)], seg=2)
    parts.append(slab(upper, 54, 9, 2))

    # Butt: wide rounded block, its front edge the back wall of the thumbhole.
    butt = rounded([
        (10, 0, 10), (92, 0, 6), (104, 14, 8), (96, 38, 10), (98, 66, 12), (116, 80, 0), (116, 123, 0),
        (16, 123, 16), (2, 104, 10), (0, 40, 14)], seg=2)
    parts.append(slab(butt, 52, 11, 2))

    # Lower frame: bottom bar, pistol grip, trigger guard and the forward hand stop, in one narrower piece.
    lower = rounded([
        (70, 0, 0), (398, 0, 10), (418, 9, 10), (436, 30, 12), (450, 58, 10), (458, 84, 0), (404, 84, 0),
        (412, 58, 10), (404, 34, 10), (390, 16, 8), (268, 16, 7), (276, 50, 0), (282, 84, 0),
        (234, 84, 0), (227, 50, 0), (212, 16, 9), (104, 16, 0), (70, 16, 0)], seg=2)
    parts.append(slab(lower, 36, 7, 2))

    # Grip swell: the grip is fuller in the middle than the bar it grows from.
    grip = rounded([(214, 20, 4), (264, 20, 4), (280, 76, 4), (230, 76, 4)], seg=1)
    parts.append(slab(grip, 40, 9, 2, mat="grip"))

    # TR front housing: holds the magazine's front end, carries the side rails and the front of the top rail.
    housing = rounded([
        (345, 119, 0), (466, 119, 0), (467, 142, 6), (460, 158, 4), (352, 158, 6), (338, 140, 6)], seg=2)
    parts.append(slab(housing, 48, 7, 2))

    # Rear rail post behind the magazine (magazine catch housing).
    post = rounded([(98, 119, 0), (130, 119, 0), (128, 158, 3), (104, 158, 3), (96, 136, 4)], seg=1)
    parts.append(slab(post, 36, 5, 1))

    # Top Picatinny rail: a stem along the whole post-to-housing span, then the teeth.
    stem = [(-8.5, 157.5), (8.5, 157.5), (8.5, 162.5), (10.6, 164.2), (10.6, 165.6), (-10.6, 165.6),
            (-10.6, 164.2), (-8.5, 162.5)]
    parts.append(section(stem, 100, 462, mat="rail"))
    u = 103.0
    while u + 5.3 <= 461:
        parts.append(section([(-10.6, 165.6), (10.6, 165.6), (10.6, 168.0), (9.4, 169.0), (-9.4, 169.0),
                              (-10.6, 168.0)], u, u + 5.3, mat="rail"))
        u += 10.0

    # Short side rails at the front of the housing (both sides).
    for side in (1, -1):
        sec = [(23.0 * side, 133.0), (27.5 * side, 134.0), (27.5 * side, 131.6), (30.0 * side, 130.0),
               (30.0 * side, 148.0), (27.5 * side, 146.4), (27.5 * side, 144.0), (23.0 * side, 145.0)]
        parts.append(section(sec, 380, 446, mat="rail"))
        u = 382.0
        while u + 5.3 <= 445:
            parts.append(section([(30.0 * side, 130.6), (32.4 * side, 131.4), (32.4 * side, 146.6),
                                  (30.0 * side, 147.4)], u, u + 5.3, mat="rail"))
            u += 10.0

    # Barrel stub and flash hider protruding from the nose.
    parts.append(lathe([(450, 10.5), (NOSE_U + 2, 10.5), (NOSE_U + 2, 9.0), (MUZZLE_U - 2, 9.0), (MUZZLE_U, 8.0),
                        (MUZZLE_U, 4.0), (MUZZLE_U - 6, 3.0), (MUZZLE_U - 6, 0.0)],
                       12, "u", (0.0, BORE_V), mat="metal", cap1=False))

    # Trigger, in the front opening just ahead of the grip.
    trig = rounded([(290, 84, 0), (300, 84, 0), (298, 62, 6), (304, 40, 4), (298, 38, 3), (290, 60, 6)], seg=1)
    parts.append(slab(trig, 8, 2, 1, mat="metal"))

    # Rotary fire selector under the trigger.
    parts.append(lathe([(-2.5, 0.0), (-2.5, 9.0), (1.0, 10.0), (1.0, 0.0)], 12, "v", (0.0, 296.0),
                       mat="metal", cap0=False, cap1=False))

    # Sling loops: small studs at the butt and the nose.
    for (su, sv) in ((20, 112), (448, 112)):
        parts.append(lathe([(26.0, 3.0), (29.5, 3.0), (29.5, 0.0)], 6, "x", (su, sv), mat="metal", cap0=True,
                           cap1=False))
        parts.append(lathe([(-26.0, 3.0), (-29.5, 3.0), (-29.5, 0.0)], 6, "x", (su, sv), mat="metal", cap0=True,
                           cap1=False))
    return parts


def bolt_parts():
    """One charging handle pair (forward position): a knob on each side and the bar joining them."""
    parts = []
    for side in (1, -1):
        rings = [(24.0, 5.5), (31.0, 5.5), (34.0, 4.6), (35.0, 2.5), (35.0, 0.0)]
        rings = [(t * side, r) for t, r in rings]
        parts.append(lathe(rings, 10, "x", (HANDLE_U, HANDLE_V), mat="metal", cap0=True, cap1=False))
    parts.append(lathe([(-24.0, 2.6), (24.0, 2.6)], 6, "x", (HANDLE_U, HANDLE_V), mat="metal"))
    return parts


def magazine_parts():
    """50-round magazine in its own frame: origin at its front end, centred, on the receiver top (u = 0 is the
    front, it extends towards -u; v = 0 is its bottom)."""
    parts = []
    L, H, W = MAG_LEN, MAG_H, MAG_W
    shell = rounded([(-L, 0, 3), (-34, 0, 0), (-34, H, 3), (-L + 4, H, 6), (-L, H - 6, 3)], seg=1)
    parts.append(slab(shell, W, 3.5, 1, mat="smoke"))
    # Black polymer feed section at the front (where the rounds turn 90 degrees) and the rear end cap.
    feed = rounded([(-40, 0.5, 0), (-2, 0.5, 2), (0, 4, 2), (0, 20, 3), (-6, 23.5, 3), (-40, 23.5, 0)], seg=1)
    parts.append(slab(feed, W - 3, 3.0, 1, mat="polymer"))
    cap = rounded([(-L - 1.5, 1, 2), (-L + 10, 1, 0), (-L + 10, H - 1, 0), (-L + 2, H - 1, 4), (-L - 1.5, H - 8, 3)],
                  seg=1)
    parts.append(slab(cap, W + 1.5, 2.5, 1, mat="polymer"))
    # Two low ribs along the top.
    for x in (-12.0, 12.0):
        parts.append(section([(x - 2, H - 0.5), (x + 2, H - 0.5), (x + 1.4, H + 1.2), (x - 1.4, H + 1.2)],
                             -L + 12, -40, mat="smoke"))
    return parts


SUPP_LEN, SUPP_R = 165.0, 19.0
MOUNT_LEN, MOUNT_R = 36.0, 12.0


def suppressor_parts():
    """Origin at the rear mounting face (canon), extending along +u. u = 0 here is the canon point."""
    L, R = SUPP_LEN, SUPP_R
    outer = [(0.0, 13.0), (14.0, 13.0), (16.0, 15.0), (20.0, 15.5), (24.0, R - 1.5), (26.0, R), (L - 6.0, R),
             (L - 2.0, R - 1.2), (L, R - 3.5), (L, 6.0), (L - 3.0, 4.6), (L - 3.0, 0.0)]
    p = lathe([(0.0, 0.0)] + outer, 20, "u", (0.0, 0.0), mat="supp", cap0=False, cap1=False)
    return [p]


def mount_parts():
    """Collar over the flash hider; origin at the face it mounts on (canon), extending along +u."""
    L, R = MOUNT_LEN, MOUNT_R
    rings = [(0.0, 0.0), (0.0, R - 1.0), (1.0, R), (8.0, R), (9.0, R - 1.5), (12.0, R - 1.5), (13.0, R),
             (L - 2.0, R), (L, R - 1.5), (L, 7.0), (L - 4.0, 6.0), (L - 4.0, 0.0)]
    return [lathe(rings, 16, "u", (0.0, 0.0), mat="mount", cap0=False, cap1=False)]


def tri_count(parts):
    n = 0
    for p in parts:
        for f in p["faces"]:
            n += len(f) - 2
    return n


# --------------------------------------------------------------------------------------------------
# Attachment points (game space), for the model script
# --------------------------------------------------------------------------------------------------

def _pt(x, u, v):
    return [round(c, 4) for c in to_game(x, u, v)]


def points():
    return {
        "muzzle": {"offset": _pt(0, MUZZLE_U, BORE_V), "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": _pt(0, NOSE_U, BORE_V), "rotate": [0.0, 0.0, 0.0]},
        "world": {"offset": [0.02, 0.13, 0.0], "rotate": [180.0, 0.0, 180.0]},
        "magazine": {"offset": _pt(0, MAG_FRONT_U, MAG_BASE_V), "rotate": [0.0, 0.0, 0.0]},
        "rail_up": {"offset": _pt(0, 262, RAIL_TOP_V), "rotate": [0.0, 0.0, 0.0]},
        "scope": {"offset": _pt(0, 268, RAIL_TOP_V), "rotate": [0.0, 0.0, 0.0]},
        "rail_left": {"offset": _pt(32.4, 413, 139), "rotate": [0.0, 0.0, 0.0]},
        "rail_right": {"offset": _pt(-32.4, 413, 139), "rotate": [0.0, 0.0, 0.0]},
        "light_left": {"offset": _pt(41.0, 413, 139), "rotate": [0.0, 0.0, 0.0]},
        "laser_right": {"offset": _pt(-41.0, 413, 139), "rotate": [0.0, 0.0, 0.0]},
        "bolt_fired": {"offset": [0.0, round(-HANDLE_TRAVEL * S, 4), 0.0], "rotate": [0.0, 0.0, 0.0]},
    }


def extras():
    """Not model-script attachment points, but needed by other registries."""
    return {
        "ejection_port": _pt(0, sum(EJECT_U) / 2, 0),
        "ejection_port_u_range_game_y": [round((u - U0) * S, 4) for u in EJECT_U],
        "charging_handles_forward": [_pt(35, HANDLE_U, HANDLE_V), _pt(-35, HANDLE_U, HANDLE_V)],
        "real_mm_per_game_unit": round(1 / S, 2),
    }


if __name__ == "__main__":
    import json
    for name, fn in (("body", body_parts), ("bolt", bolt_parts), ("magazine", magazine_parts),
                     ("suppressor", suppressor_parts), ("mount", mount_parts)):
        ps = fn()
        print("%-10s %2d parts  ~%d tris" % (name, len(ps), tri_count(ps)))
    print(json.dumps(points(), indent=1))
    print(json.dumps(extras(), indent=1))
