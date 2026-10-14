#!/usr/bin/env python3
"""Read GoM-style binary FBX meshes in game space, for the P90 TR assets (icons, checks, previews).

make_art.load_mesh centres every mesh on its bounding box (enough for icons of loose items); a gun needs its parts
where the model script puts them, so this reader keeps the coordinates: game = (raw x, raw y, -raw z), the same
flip Assimp's MAKE_LEFT_HANDED does when Project Zomboid loads the file (node transforms are identity in GoM files).

    tris = load_game_mesh(path, "P90TR_BODY")     # [((p0, p1, p2), (uv0, uv1, uv2)), ...]
    header(path)                                  # FBX version, UnitScaleFactor, model Lcl transforms
"""

import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import make_art  # noqa: E402  (FBX node reader shared with the main mod's art script)


def _roots(path):
    with open(path, "rb") as handle:
        data = handle.read()
    version = struct.unpack_from("<I", data, 23)[0]
    off, roots = 27, []
    while off < len(data) - 160:
        node, off = make_art._read_node(data, off, version)
        if node is None:
            break
        roots.append(node)
    return roots, version


def _child(parent, name):
    return next((c for c in parent["children"] if c["name"] == name), None)


def _name(node):
    return node["props"][1].split(b"\x00")[0].decode()


def geometry_names(path):
    roots, _ = _roots(path)
    return [_name(g) for g in make_art._walk(roots, "Geometry")]


def load_game_mesh(path, geometry, offset=(0.0, 0.0, 0.0)):
    """Triangles of one geometry in game space (+ offset), with UVs."""
    roots, _ = _roots(path)
    geo = next(g for g in make_art._walk(roots, "Geometry") if _name(g) == geometry)
    flat = _child(geo, "Vertices")["props"][0]
    pvi = _child(geo, "PolygonVertexIndex")["props"][0]
    layer = _child(geo, "LayerElementUV")
    uv_index = None
    if layer is not None:
        uvs = _child(layer, "UV")["props"][0]
        if b"IndexToDirect" in _child(layer, "ReferenceInformationType")["props"][0]:
            uv_index = _child(layer, "UVIndex")["props"][0]
    else:
        uvs = None
    ox, oy, oz = offset
    verts = [(flat[i * 3] + ox, flat[i * 3 + 1] + oy, -flat[i * 3 + 2] + oz) for i in range(len(flat) // 3)]

    def uv_of(corner):
        if uvs is None:
            return (0.0, 0.0)
        i = uv_index[corner] if uv_index is not None else corner
        return uvs[i * 2], uvs[i * 2 + 1]

    tris, poly = [], []
    for corner, index in enumerate(pvi):
        last = index < 0
        poly.append((~index if last else index, corner))
        if last:
            for i in range(1, len(poly) - 1):
                trio = (poly[0], poly[i], poly[i + 1])
                tris.append((tuple(verts[v] for v, _ in trio), tuple(uv_of(c) for _, c in trio)))
            poly = []
    return tris


def bounds(tris):
    pts = [p for ps, _ in tris for p in ps]
    return tuple((min(p[k] for p in pts), max(p[k] for p in pts)) for k in range(3))


def header(path):
    """What GoM's files share: version, axes, unit scale, and every Model's Lcl transform."""
    roots, version = _roots(path)
    out = {"version": version, "models": {}, "objects": []}
    for node in roots:
        if node["name"] == "GlobalSettings":
            for p in make_art._walk([node], "P"):
                key = p["props"][0].decode()
                if key in ("UpAxis", "FrontAxis", "CoordAxis", "UnitScaleFactor", "OriginalUnitScaleFactor"):
                    out[key] = p["props"][-1]
        if node["name"] == "Objects":
            out["objects"] = sorted({c["name"] for c in node["children"]})
    for model in make_art._walk(roots, "Model"):
        props = {}
        p70 = _child(model, "Properties70")
        for p in (p70["children"] if p70 else []):
            key = p["props"][0].decode()
            if key.startswith("Lcl"):
                props[key] = tuple(round(v, 6) for v in p["props"][4:])
        out["models"][_name(model)] = props
    return out


if __name__ == "__main__":
    for fbx in sys.argv[1:]:
        print(fbx)
        print("  ", header(fbx))
        for g in geometry_names(fbx):
            t = load_game_mesh(fbx, g)
            b = bounds(t)
            print("   %-28s %5d tris  x %.4f..%.4f  y %.4f..%.4f  z %.4f..%.4f"
                  % (g, len(t), b[0][0], b[0][1], b[1][0], b[1][1], b[2][0], b[2][1]))
