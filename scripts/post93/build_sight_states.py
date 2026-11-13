"""The iron sights follow the optic on the Post-93 guns with flip-up sights (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_sight_states.py

User, 2026-11-13 (TODO.md "Iron sights under optics"): the HK416 folds its sights under an optic; every other gun of
both mods that takes one was gone through. Those with flip-up sights get the HK416's three states, picked by
Gunworks' ConditionalModel from the Scope slot (shared/GunsOfTienPost93/IronSights.lua):
    no optic                    both sights up
    red dot / holographic (RD)  the rear folded, the front seen through the optic (co-witness)
    magnified scope (FD)        both folded
plus, where an optic's mount sits on the rear sight's own spot on the rail (measured: the Elcan and the TR06X on
the SCAR-L; the Kobra, the Elcan and the TR06X on the HK416), the same with the rear sight taken off the rail
(RDX / FDX), as one does when a mount needs that slot.
Guns: MP7A1 and MP7A2 (H&K's flip-up front and rear on the top rail, modelled up), SCAR-L and SCAR-H (FN's folding
front sight on the gas block and folding rear on the receiver rail; modelled front up, rear folded), and the four
Vectors (KRISS's flip-up sights at both ends of the top rail, modelled folded). The others keep their sights (see
CLAUDE.md "Iron sights under optics").

Each gun's builder bakes its body's texture with the sights in it, so the other states are made here from the
exported body itself rather than rebuilt: every sight is a mesh island of its own (a slab of the builder's), and
folding or raising it scales it about its base along the gun's up axis (raising also narrows it towards the top, a
leaf rather than a block), keeping its UVs, so it stays painted as the builder painted it. A folded flip-up sight
lies as a low block on its base, as the HK416's (build_hk416.py). Run after the guns' builders; writes, next to each
gun's own file (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_<FILE>_Sights.fbx   <BODY>_UP / _RD / _FD / _FDX (only the
                                                                    states the builder's body is not already in)
The states keep the body's attachment points (gen_post93_guns.py writes one model per state with the same points).

Heights below are in game units x 1000 (0.603 of a real mm), y along the bore from the grip, z up from the gun's own
`scope` point (as the gun stands upright; the MP7s, the Vector 9mm and the Vector SDP are held like pistols and
modelled turned, so their data is turned back first). Fold heights clear every GoM optic of that state
(checked with the sight clash test in CLAUDE.md "Iron sights under optics").
"""

import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_mp7 as mk                                      # noqa: E402  (export, normalize_fbx)

FIREARMS = os.path.join(mk.MEDIA, "models_X/weapons/firearms")

# A sight: its island's y range (the island whose middle lies inside it, above the scope point - 0.001), and what it
# becomes in each state: ("fold", top), ("raise", top, taper) with top in z from the scope point, ("remove",), or
# absent = as the builder made it. Fold heights are the lowest optic underside over each sight's footprint less a
# margin (2026-11-13: MP7 rear 5.4 under the PSO-1, front 6.1 under the LRX12X; SCAR rear 5.1 under the Kobra on
# the SCAR-L, 5.4 under the PSO-1 on the SCAR-H; the rail crossbars' tops are at 3.2), then checked against every
# optic's mesh; the TR06X's rear ring (1.7) and the Elcan's mount jaws sit on the SCAR-L's rear sight whatever its
# height, so it comes off for them (FDX).
MP7_SIGHTS = {"rear": (-50.0, -17.0), "front": (91.0, 122.0)}
MP7_FOLD = 5.0
SCARL_SIGHTS = {"rear": (0.0, 26.0), "front": (222.0, 237.0)}
SCARH_SIGHTS = {"rear": (-23.0, 7.0), "front": (305.0, 326.0)}
SCAR_FOLD_REAR = 4.3
VECTOR_SIGHTS = {"rear": (15.0, 31.0), "front": (165.0, 183.0)}
VECTOR_UP = {"rear": ("raise", 18.0, 0.55), "front": ("raise", 19.5, 0.55)}

GUNS = [
    # file, body node, turned, scope point z (game, from the model script), sights, states {suffix: {sight: op}}
    ("MP7A1", "MP7A1_BODY", True, -0.0439, MP7_SIGHTS, {
        "RD": {"rear": ("fold", MP7_FOLD)},
        "FD": {"rear": ("fold", MP7_FOLD), "front": ("fold", MP7_FOLD)}}),
    ("MP7A2", "MP7A2_BODY", True, -0.0439, MP7_SIGHTS, {
        "RD": {"rear": ("fold", MP7_FOLD)},
        "FD": {"rear": ("fold", MP7_FOLD), "front": ("fold", MP7_FOLD)}}),
    # SCARs: the rear stands as tall as the front sight's top (one sight line), the front folds back onto its base
    ("SCARL", "SCARL_BODY", False, 0.0572, SCARL_SIGHTS, {
        "UP": {"rear": ("raise", 31.0, 0.6)},
        "RD": {"rear": ("fold", SCAR_FOLD_REAR)},
        "FD": {"rear": ("fold", SCAR_FOLD_REAR), "front": ("fold", -1.0)},
        "FDX": {"rear": ("remove",), "front": ("fold", -1.0)}}),
    ("SCARH", "SCARH_BODY", False, 0.0590, SCARH_SIGHTS, {
        "UP": {"rear": ("raise", 26.0, 0.6)},
        "RD": {"rear": ("fold", SCAR_FOLD_REAR)},
        "FD": {"rear": ("fold", SCAR_FOLD_REAR), "front": ("fold", 6.4)}}),
    # Vectors: modelled folded (FD is the builder's body)
    ("VECTOR", "VECTOR_BODY", False, 0.0206, VECTOR_SIGHTS, {
        "UP": dict(VECTOR_UP), "RD": {"front": VECTOR_UP["front"]}}),
    ("VECTOR", "VECTOR9_BODY", True, -0.0206, VECTOR_SIGHTS, {
        "UP": dict(VECTOR_UP), "RD": {"front": VECTOR_UP["front"]}}),
    ("VECTORCRB", "VECTORCRB_BODY", False, 0.0206, VECTOR_SIGHTS, {
        "UP": dict(VECTOR_UP), "RD": {"front": VECTOR_UP["front"]}}),
    ("VECTORSDP", "VECTORSDP_BODY", True, -0.0206, VECTOR_SIGHTS, {
        "UP": dict(VECTOR_UP), "RD": {"front": VECTOR_UP["front"]}}),
]


def islands(bm):
    seen, out = set(), []
    for v in bm.verts:
        if v in seen:
            continue
        stack, comp = [v], []
        seen.add(v)
        while stack:
            a = stack.pop()
            comp.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b not in seen:
                    seen.add(b)
                    stack.append(b)
        out.append(comp)
    return out


def import_file(file):
    """The gun's own FBX, freshly imported: {node name: object}. Normals are recomputed as the builders make them
    (smooth, sharp from 35 degrees), not taken from the file."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(FIREARMS, "GunsOfTienPost93_%s.fbx" % file),
                             use_custom_normals=False)
    return {o.name: o for o in bpy.data.objects if o.type == 'MESH'}


def make_state(src, name, turned, scope_z, sights, ops):
    """A copy of the body with each sight of `ops` folded or raised about its base."""
    me = src.data.copy()
    me.name = name
    bm = bmesh.new()
    bm.from_mesh(me)
    sign = 1.0 if turned else -1.0                      # mesh data z -> upright game z
    sz = (-scope_z if turned else scope_z) * 1000.0
    up = lambda v: sign * v.co.z * 1000.0 - sz          # noqa: E731  height over the scope point, x 1000
    found = {}
    for comp in islands(bm):
        ys = [v.co.y * 1000.0 for v in comp]
        mid = (min(ys) + max(ys)) / 2.0
        if max(up(v) for v in comp) < -1.0:
            continue
        for sight, (y0, y1) in sights.items():
            if y0 <= mid <= y1 and len(comp) > 8:       # 8 = a rail crossbar
                if sight in found:
                    sys.exit("%s: two islands for the %s sight" % (name, sight))
                found[sight] = comp
    for sight, op in ops.items():
        comp = found.get(sight)
        if comp is None:
            sys.exit("%s: no %s sight found" % (name, sight))
        zs = [up(v) for v in comp]
        base, top = min(zs), max(zs)
        if op[0] == "remove":
            bmesh.ops.delete(bm, geom=comp, context='VERTS')
            print("  %-18s %-5s removed" % (name, sight))
            continue
        target = op[1]
        taper = op[2] if op[0] == "raise" else 0.0
        if (op[0] == "fold") != (target < top):
            sys.exit("%s: %s %s to %.1f, but it is %.1f..%.1f" % (name, op[0], sight, target, base, top))
        k = (target - base) / (top - base)
        ys = [v.co.y for v in comp]
        cy = (min(ys) + max(ys)) / 2.0
        for v in comp:
            z = base + (up(v) - base) * k
            f = (z - base) / (target - base)
            v.co.y = cy + (v.co.y - cy) * (1.0 - taper * f)
            v.co.z = sign * (z + sz) / 1000.0
        print("  %-18s %-5s %s: %.1f..%.1f -> top %.1f" % (name, sight, op[0], base, top, target))
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(35))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def main():
    by_file = {}
    for file, node, turned, scope_z, sights, states in GUNS:
        by_file.setdefault(file, []).append((node, turned, scope_z, sights, states))
    for file, bodies in by_file.items():
        imported = import_file(file)
        made = []
        for node, turned, scope_z, sights, states in bodies:
            src = imported[node]
            for suffix, ops in states.items():
                made.append(make_state(src, "%s_%s" % (node, suffix), turned, scope_z, sights, ops))
        for o in list(bpy.data.objects):
            if o not in made:
                bpy.data.objects.remove(o)
        path = os.path.join(FIREARMS, "GunsOfTienPost93_%s_Sights.fbx" % file)
        mk.export(made, path)
        print("wrote", os.path.relpath(path, mk.MEDIA), sorted(o.name for o in made))


if __name__ == "__main__":
    main()
