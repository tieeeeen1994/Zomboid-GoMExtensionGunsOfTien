"""
Reload clips for the full-size Uzi and Guns of Marz's MP5K (Blender 5.2, headless), built with TienInspectWeapon's
animation pipeline (as scripts/anim/m249_reload.py and Post-93's p90_reload.py).

    blender -b --factory-startup -P scripts/anim/smg_reload.py -- <vanilla anims_X/Bob> <out_dir> <gun> [clip ...] [--preview]

gun: uzi | mp5k. clips: Unload Load Rack AimRack (default: all). Writes
<out_dir>/Bob_GunsOfTien_<Uzi|MP5K>_<clip>.x (+ .blend); with --preview renders every 2nd frame with the gun in the
hand into <out_dir>/prev_<gun>_<clip>/ (TienInspectWeapon's sheet.py / gif.py lay them out). Ship the .x files to
Contents/mods/GoMExtensionGunsOfTien/42/media/anims_X/Bob/; the AnimSets *UziRifle_GoT.xml / *MP5K_GoT.xml play them.

Why (user, 2026-10-23): GoM's clips put the left hand where those guns' magazines are not. The Uzi is held as a
rifle but its magazine goes up the pistol grip, about 10 cm behind the MP5 well GoM's MP5 clips reach for; the MP5K
is held like a pistol, its magazine ahead of the trigger guard, and GoM's handgun2 clips do not meet it either.
- Unload: the gun comes up and is canted so the magazine faces the left hand, which takes the magazine by its body
  just under the well (every magazine of the gun shows there, from the shortest up: the hand grips that one place
  whatever is fitted), pulls it straight out along its axis and carries it away to the left hip.
- Load: the hand brings the new magazine up under the well, lines it up, pushes it home (the "load" click), gives it
  a tap and goes back to the support grip.
- Rack: the Uzi's knob on top, pulled back over the top with the left hand and let go (AimRack: the same without
  leaving the aim); the MP5K's cocking lever at the front of its tube on the left, pulled back and let go.
The magazine leaves the gun with the hand at the changeWeaponPart "mag" marker (SWAP): Gunworks' "attachments" style
shows it on Bip01_Prop2, keyed here in the left hand from / up to the swap (its offset taken at the swap frame, so
any magazine of the gun, its lips at the gun's `magazine` point, moves with the hand without a jump).

Weapon space is the game's (the model scripts'): +Y the muzzle. The Uzi is rifle-held and upright (+Z top, +X its
left); the MP5K is pistol-held and modelled upside down (+Z its bottom, +X its right), as all of GoM's handgun-held guns.
"""

import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ANIM = os.environ.get("TIEN_ANIM") or os.path.normpath(os.path.join(ROOT, "..", "TienInspectWeapon", "scripts", "anim"))
sys.path.insert(0, ANIM)
import pose  # noqa: E402
import rig  # noqa: E402
import x_export  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
import xanim  # noqa: E402
from rig import Key, ch, rot_of  # noqa: E402

MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
GOM = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                          "3722134990/mods/GunsOfMarz/42.16/media"),
                       "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                       "42.16/media") if os.path.isdir(p))
FPS = 30
# frames: GoM's magazine reload durations (unload 1.2, load 1.5, rack 1.2 s), as Uzi.lua / MP5K.lua register them
LENGTHS = {"Unload": 36, "Load": 45, "Rack": 36, "AimRack": 36}
SWAP = {"Unload": 16, "Load": 30}           # changeWeaponPart "mag" (AnimSets: 16/36 = 0.44, 30/45 = 0.67)
CLICK = {"Load": 30}                        # the load sound, the magazine seated


def mat_of(pt):
    rx, ry, rz = [math.radians(a) for a in pt.get("rotate", [0, 0, 0])]
    return (Matrix.Translation(Vector(pt["offset"])) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Rotation(ry, 4, 'Y')
            @ Matrix.Rotation(rz, 4, 'Z'))


# ==================================================================================================
# The two guns: points in weapon space (game units), the clips' places (character space)
# ==================================================================================================

def uzi_spec():
    p = json.load(open(os.path.join(ROOT, "scripts/uzi_points.json")))["UZI"]
    K = p["_extras"]["k"]
    L0, H0 = p["_extras"]["photo_origin_mm"]
    wp = lambda L, H, x=0.0: Vector((x * K, (L0 - L) * K, (H - H0) * K))
    mag = mat_of(p["magazine"])
    down = (mag.to_3x3() @ Vector((0, 0, -1))).normalized()          # along the magazine, out of the well
    return dict(
        name="Uzi", rifle=True, points=p, mag_point=mag, out=down,
        # the magazine's axis 14 mm under the grip's bottom (H 46.5): every magazine shows there
        grab=wp(290.0, 46.5 - 14.0),
        # measured with SMG_CAL (hand_offset): the vanilla grip's hand centre lands this far from the axis point
        hold_fix=Vector((0.0023, 0.0427, 0.0233)),
        travel=0.085,                                                 # lips (H 142.5) clear of the grip (46.5)
        knob=wp(187.5, 221.0), knob_back=wp(187.5 + 70.0, 221.0),     # the cocking knob, pulled back 70 mm
        # under the right arm, muzzle forward-left, canted so the grip's bottom and the left side face the left hand
        work=dict(pos=ch(-0.02, 0.68, 0.10), along=ch(-0.45, 0.32, 0.83), top=ch(0.45, 0.88, -0.15)),
        rack=dict(pos=ch(0.05, 0.64, 0.14), along=ch(-0.42, 0.28, 0.86), top=ch(0.05, 0.96, -0.28)),
        away=ch(-0.12, 0.56, 0.12),               # the left hip, within the arm's reach (0.274 from the shoulder)
        fbx=os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_UZI.fbx"),
        nodes=["UZI_BODY", "UZI_BOLT", "UZI_STOCK_FOLDED"],
        mag_fbx=os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_UZI_magazines.fbx"),
        mag_node="9x19Magazine32_UZI",
    )


def mp5k_spec():
    # GoM's MP5K model script (models/weapons/smgs.txt): magazine point, the cocking lever's knob measured on
    # MP5K_BOLT (its left end: y 0.196-0.206, z -0.059), the well's bottom on MP5K_BODY (z 0.014, y 0.10-0.14).
    # Upside down: +Z is the gun's bottom, +X its right.
    mag = mat_of({"offset": [0.0, 0.1196, -0.0388], "rotate": [171.7924, 0.0, 180.0]})
    down = (mag.to_3x3() @ Vector((0, 0, -1))).normalized()
    well_s = (0.014 - mag.translation.z) / down.z                     # along the axis from the lips to the well
    return dict(
        name="MP5K", rifle=False, mag_point=mag, out=down,
        grab=mag.translation + down * (well_s + 0.010),                  # the axis, just under the well
        hold_fix=Vector((0.0044, 0.0524, -0.0181)),                       # measured as the Uzi's
        travel=well_s + 0.012,
        knob=Vector((-0.026, 0.201, -0.059)), knob_back=Vector((-0.026, 0.201 - 0.036, -0.059)),
        # held like a pistol, close in front of the chest and turned across it (the model's origin is at its rear
        # end, the well 0.12 and the lever 0.20 ahead of it, so further out both are beyond the left hand's reach),
        # muzzle to the left, canted so the well faces the left hand
        work=dict(pos=ch(0.08, 0.64, 0.10), along=ch(-0.75, 0.30, 0.59), top=ch(0.30, 0.90, -0.30)),
        # racking (from the idle or the aim): drawn in at the chest and turned a little left, still pointing
        # forward (the lever is 0.20 ahead of the grip, beyond the left hand in a full aim), then back. Tried and
        # rejected: across the belly, muzzle to the left (user, 2026-10-23: "unacceptable"), and up in front of the face.
        rack=dict(pos=ch(0.10, 0.62, 0.06), along=ch(-0.60, 0.20, 0.75), top=ch(0.0, 1.0, 0.0)),
        away=ch(-0.13, 0.52, 0.12),
        fbx=os.path.join(GOM, "models_X/weapons/firearms/MP5K.fbx"),
        nodes=["MP5K_BODY", "MP5K_BOLT"],
        mag_fbx=os.path.join(GOM, "models_X/weapons/magazines/smgs.fbx"),
        mag_node="9x19Magazine30_MP5",
    )


SPECS = {"uzi": uzi_spec, "mp5k": mp5k_spec}


# ==================================================================================================
# Rig and hand templates
# ==================================================================================================

HALF_TURN = Matrix.Rotation(math.pi, 4, 'Y')       # rifle space (top +Z) <-> handgun space (top -Z)


def build_rig(src_dir, g):
    idle, aim = ("Bob_IdleRifle.x", "Bob_IdleAimRifle.x") if g["rifle"] else ("Bob_IdleHandgun.X",
                                                                              "Bob_IdleAimHandgun.X")
    xa = xanim.read(os.path.join(src_dir, idle), with_mesh=True)
    base = pose.from_clip(xa, 0)
    aux = pose.copy(base)
    found = pose.from_clip(xanim.read(os.path.join(src_dir, aim)), 0)
    aux.update({b: m for b, m in found.items() if b in base})
    if g["rifle"]:
        r = rig.Rig(xa, base, aux=aux, poi=0.2, top=1, rest=x_import.rest_matrices(xa))
    else:
        r = rig.Rig(xa, base, aux=aux, poi=0.0, top=-1, support_from_aux=True, rest=x_import.rest_matrices(xa))

    def sample(clip, frame):
        p = pose.copy(base)
        p.update({b: m for b, m in pose.from_clip(xanim.read(os.path.join(src_dir, clip)), frame * 160).items()
                  if b in base})
        return p

    # holding a magazine by its body in the well: vanilla's rifle load, magazine in the well (frame 30; rifle space)
    mag_hold = r.sample_lgrip(sample("Bob_Reload_Rifle_Load.x", 30))
    # over the top, palm down: vanilla's handgun reload over the slide (frame 48; handgun space)
    over = r.sample_lgrip(sample("Bob_Reload_Handgun.X", 48))
    if g["rifle"]:
        over = HALF_TURN @ over
    else:
        mag_hold = HALF_TURN @ mag_hold
    belt_world = pose.world(xa, sample("Bob_Reload_Handgun.X", 16))["Bip01_L_Hand"]
    support = r.support_base if g["rifle"] else r.support_aux
    # vanilla's magazine (Bip01_Prop2) sits on the hand bone, the wrist, beside the magazine it holds: in the rifle
    # load's frame the magazine's axis runs on the weapon's centre line (x 0) at the wrist's height and depth
    return xa, r, {"mag": mag_hold, "over": over, "support": support, "belt_world": belt_world}


def palm(template):
    """The middle of the palm in the template's weapon space (the hand bone runs along its local X to the fingers)."""
    return template @ Vector((0.045, 0.0, 0.012))


def grip_mag(template, at, rot=(0.0, 0.0, 0.0)):
    """The magazine hold with vanilla's magazine axis (x 0 at the wrist's y and z, in its weapon space) moved onto
    `at`, a point on our magazine's axis, the hand turned by `rot` (degrees, weapon X, Y, Z) about it."""
    contact = Vector((0.0, template.translation.y, template.translation.z))
    R = (Matrix.Rotation(math.radians(rot[0]), 3, 'X') @ Matrix.Rotation(math.radians(rot[1]), 3, 'Y')
         @ Matrix.Rotation(math.radians(rot[2]), 3, 'Z'))
    q = (R @ template.to_3x3()).to_quaternion()
    return Matrix.LocRotScale(at + R @ (template.translation - contact), q, None)


def grip_on(template, at, rot=(0.0, 0.0, 0.0)):
    """A left-hand placement with the template's palm on `at` (weapon space), turned by `rot` (degrees about the
    weapon's X, Y, Z) about that point."""
    R = (Matrix.Rotation(math.radians(rot[0]), 3, 'X') @ Matrix.Rotation(math.radians(rot[1]), 3, 'Y')
         @ Matrix.Rotation(math.radians(rot[2]), 3, 'Z'))
    q = (R @ template.to_3x3()).to_quaternion()
    return Matrix.LocRotScale(at + R @ (template.translation - palm(template)), q, None)


def weapon_at(r, place):
    return r.weapon_at(dict(at_aux=0.0, top=place["top"], along=place["along"], face=None, pos=place["pos"],
                            roll=0.0, turn=0.0, drop=0.0, pitch=0.0), r.eye0)


def hand_away(r, g, grips, place):
    W = weapon_at(r, place)
    return W.inverted() @ Matrix.LocRotScale(g["away"], grips["belt_world"].to_quaternion(), None)


# ==================================================================================================
# Keys
# ==================================================================================================

def keys_for(clip, r, g, grips):
    sup = grips["support"]
    fix = Vector() if os.environ.get("SMG_CAL") == "raw" else g["hold_fix"]     # SMG_CAL=raw measures it again
    on_mag = lambda s, rot=(0, 0, 0): grip_mag(grips["mag"], g["grab"] + g["out"] * s - fix, rot)
    over = lambda at, rot=(0, 0, 0): grip_on(grips["over"], at, rot)
    n = LENGTHS[clip]
    W = dict(look=0.85, lean=5, aux=0.15, **g["work"])
    idle = dict(look=0, lean=0, aux=0, pos=r.weapon0.translation, along=rot_of(r.weapon0) @ Vector((0, 1, 0)),
                top=None, face=rot_of(r.weapon0) @ Vector((1, 0, 0)))
    t = g["travel"]
    if clip == "Unload":
        away = hand_away(r, g, grips, g["work"])
        return [
            Key(0, look=0, lean=0, support=0, lgrip=on_mag(0.02)),
            Key(8, support=1, lgrip=on_mag(0.008), ease=True, **W),                # under the well
            Key(10, lgrip=on_mag(0.0)),                                             # on the magazine, the release
            Key(SWAP["Unload"], lgrip=on_mag(t), ease=True),                        # pulled out clear
            Key(n, lgrip=away, ease=True),                                          # away to the hip
        ]
    if clip == "Load":
        away = hand_away(r, g, grips, g["work"])
        return [
            Key(0, support=1, lgrip=away, ease=True, **W),
            Key(14, lgrip=on_mag(t + 0.012, (0, 0, 6)), ease=True),                # lined up under the well
            Key(21, lgrip=on_mag(t * 0.6)),                                         # the lips in the well
            Key(SWAP["Load"], lgrip=on_mag(0.0), ease=True),                        # pushed home: the click
            Key(33, lgrip=on_mag(0.006)),
            Key(36, lgrip=on_mag(-0.002)),                                          # a tap on it
            Key(41, lgrip=sup, ease=True),                                          # back to the support grip
            Key(n, ease=True, **idle),
        ]
    if clip in ("Rack", "AimRack"):
        place = g["rack"]
        R = dict(look=0.8, lean=4, aux=0.15, **place)
        side = (0, 0, 0) if g["rifle"] else (0, 90, 0)        # the Uzi's knob from above, the MP5K's lever from the left
        if clip == "Rack":
            first = Key(0, support=1, lgrip=sup, ease=True, **idle)
            last = Key(n, lgrip=sup, ease=True, **idle)
        else:
            first = Key(0, support=1, lgrip=sup, ease=True, at_aux=True, aux=1.0, look=0, lean=0)
            last = Key(n, lgrip=sup, ease=True, at_aux=True, aux=1.0, look=0, lean=0)
        # AimRack stays in the aim (the knob / lever is in reach of the left hand there); Rack brings the gun in
        aimed = clip == "AimRack" and g["rifle"]
        R = dict(at_aux=True, aux=1.0, look=0, lean=0) if aimed else R
        A = dict(at_aux=True, aux=1.0) if aimed else {}
        return [
            first,
            Key(12, lgrip=over(g["knob"], side), ease=True, **R),                   # on the knob (rackStart)
            Key(19, lgrip=over(g["knob_back"], side), ease=True, **A),              # all the way back
            Key(22, lgrip=over(g["knob_back"] + Vector((0, 0.004, 0)), side), **A),  # let go: it flies forward
            Key(30, lgrip=sup, ease=True, **A),
            last,
        ]
    raise ValueError(clip)


def key_prop2(xa, poses, g, swap, in_hand_after):
    """Bip01_Prop2 (Gunworks' reload magazine) on every pose: at the gun's magazine point, or, on the hand's side of
    the swap, in the left hand with the offset it has at the swap frame."""
    M = g["mag_point"]
    w = pose.world(xa, poses[swap])
    offset = w["Bip01_L_Hand"].inverted() @ (w["Bip01_Prop1"] @ M)
    for f, p in enumerate(poses):
        w = pose.world(xa, p)
        in_hand = f >= swap if in_hand_after else f <= swap
        world = w["Bip01_L_Hand"] @ offset if in_hand else w["Bip01_Prop1"] @ M
        p["Bip01_Prop2"] = w["Bip01"].inverted() @ world


# ==================================================================================================
# Preview
# ==================================================================================================

def gun_objects(arm_ob, g):
    obs = {}

    def load(path, node, mat_world=None, colour=(0.16, 0.16, 0.17, 1.0), bone="Bip01_Prop1", name=None):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=path)
        new = list(set(bpy.data.objects) - before)
        src = next(o for o in new if o.name.split(".")[0] == node)
        name = name or node
        me = bpy.data.meshes.new(name)
        verts = [Vector((v.co.x, v.co.y, -v.co.z)) for v in src.data.vertices]      # file -> game space
        if mat_world is not None:
            verts = [mat_world @ v for v in verts]
        me.from_pydata([tuple(v) for v in verts], [], [tuple(reversed(p.vertices)) for p in src.data.polygons])
        me.update()
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        m = bpy.data.materials.new(name)
        m.diffuse_color = colour
        me.materials.append(m)
        x_preview.attach_to_bone(ob, arm_ob, bone)
        obs[name] = ob

    for node in g["nodes"]:
        load(g["fbx"], node)
    mc = (0.35, 0.36, 0.4, 1.0)
    load(g["mag_fbx"], g["mag_node"], g["mag_point"], mc, name="MagOnGun")
    load(g["mag_fbx"], g["mag_node"], None, mc, bone="Bip01_Prop2", name="MagInHand")
    return obs


CLOSEUPS = {
    # name: (camera location, look-at), Blender space (Z up, the character faces -Y, its left is +X)
    "front": ((0.45, -1.7, 0.95), (0.0, -0.12, 0.6)),
    "top": ((0.45, -0.6, 1.95), (0.0, -0.12, 0.6)),
    "side": ((1.75, -0.45, 0.85), (0.0, -0.12, 0.6)),
}


def render_closeups(out_dir, frames, state):
    os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    x_preview.setup_render(scene)
    scene.render.resolution_x = scene.render.resolution_y = 420
    cams = {}
    for name, (loc, tgt) in CLOSEUPS.items():
        cam = x_preview.camera("Cam_" + name, loc, tgt)
        cam.data.ortho_scale = 0.8
        cams[name] = cam
    obj = bpy.data.objects
    for frame in frames:
        scene.frame_set(frame)
        on_gun, in_hand = state(frame)
        obj["MagOnGun"].hide_render, obj["MagInHand"].hide_render = not on_gun, not in_hand
        for name, cam in cams.items():
            scene.camera = cam
            scene.render.filepath = os.path.join(out_dir, "%s_%03d.png" % (name, frame))
            bpy.ops.render.render(write_still=True)


def hand_offset(arm_ob, g, frame):
    """Where the left hand really holds: the centre of Bob's left hand and finger vertices (weight > 0.5) at `frame`,
    in weapon space, minus the magazine axis point the hand was sent to (g["grab"]). Used once per gun to measure
    hold_fix (with SMG_CAL=raw; SMG_CAL=1 checks it): the vanilla grip's own magazine contact is not readable from
    its bones."""
    scene = bpy.context.scene
    scene.frame_set(frame)
    body = next(o for o in arm_ob.children if o.type == 'MESH')
    groups = {vg.index for vg in body.vertex_groups if vg.name == "Bip01_L_Hand" or vg.name.startswith("Bip01_L_Finger")}
    picked = [v.index for v in body.data.vertices if any(e.group in groups and e.weight > 0.5 for e in v.groups)]
    ev = body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    centre = sum((body.matrix_world @ ev.vertices[i].co for i in picked), Vector()) / len(picked)
    probe = bpy.data.objects.new("probe", None)
    scene.collection.objects.link(probe)
    x_preview.attach_to_bone(probe, arm_ob, "Bip01_Prop1")
    bpy.context.view_layer.update()
    local = probe.matrix_world.inverted() @ centre
    return local - g["grab"]


def build(src_dir, out_dir, gun, clip, preview=False):
    g = SPECS[gun]()
    for key in ("work", "rack"):                         # tuning: SMG_WORK / SMG_RACK = "right,up,forward"
        v = os.environ.get("SMG_" + key.upper())
        if v:
            g[key] = dict(g[key], pos=ch(*[float(x) for x in v.split(",")]))
        for part in ("along", "top"):
            v = os.environ.get("SMG_%s_%s" % (key.upper(), part.upper()))
            if v:
                g[key] = dict(g[key], **{part: ch(*[float(x) for x in v.split(",")])})
    xa, r, grips = build_rig(src_dir, g)
    n = LENGTHS[clip]
    poses = r.build(keys_for(clip, r, g, grips), n, breath=(0, None), from_base=(clip in ("Unload", "Rack")))
    if clip in SWAP:
        key_prop2(xa, poses, g, SWAP[clip], clip == "Unload")
    if os.environ.get("SMG_DEBUG"):
        for f in range(0, n + 1, 6):
            w = pose.world(xa, poses[f])
            print("[debug] f%d Prop1 %s  L hand %s  Bip01 %s" % (f, tuple(round(c, 3) for c in w["Bip01_Prop1"].translation),
                  tuple(round(c, 3) for c in w["Bip01_L_Hand"].translation), tuple(round(c, 3) for c in w["Bip01"].translation)))
        print("[debug] work pos", tuple(round(c, 3) for c in g["work"]["pos"]))
    tag = "[%s] %s" % (gun, clip)
    if r.warnings:
        print("%s: %d frames out of reach, worst: %s" % (tag, len(r.warnings),
                                                         max(r.warnings, key=lambda w: float(w.rsplit(" ", 1)[1]))))
    if r.wrist_warnings:
        print("%s: %d arm-frames with the wrist past its natural range, e.g. %s" % (tag, len(r.wrist_warnings),
                                                                                    r.wrist_warnings[0]))
    for s in "RL":
        sw = [d for side, d in r.swivels if side == s]
        if len(sw) > 1:
            print("%s: %s elbow swing %.0f..%.0f, largest step %.1f" % (
                tag, s, min(sw), max(sw), max(abs(b - a) for a, b in zip(sw, sw[1:]))))
    os.makedirs(out_dir, exist_ok=True)
    name = "Bob_GunsOfTien_%s_%s" % (g["name"], clip)
    src = os.path.join(src_dir, "Bob_IdleRifle.x" if g["rifle"] else "Bob_IdleHandgun.X")
    arm_ob = x_import.load(src)
    pose.bake(arm_ob, xa, poses, name)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, name + ".blend"))
    x_export.export(src, os.path.join(out_dir, name + ".x"), name, arm_ob)
    if os.environ.get("SMG_CAL") and clip == "Unload":
        print("[cal] %s hand centre - magazine axis (weapon space): %s" % (gun, tuple(round(v, 4) for v in
                                                                                   hand_offset(arm_ob, g, 10))))
    if preview:
        gun_objects(arm_ob, g)

        def state(f):
            if clip == "Unload":
                return f < SWAP[clip], f >= SWAP[clip]
            if clip == "Load":
                return f >= SWAP[clip], f < SWAP[clip]
            return True, False
        render_closeups(os.path.join(out_dir, "prev_%s_%s" % (gun, clip)), list(range(0, n + 1, 3)), state)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    preview = "--preview" in args
    args = [a for a in args if a != "--preview"]
    gun = args[2]
    clips = args[3:] or ["Unload", "Load", "Rack", "AimRack"]
    for c in clips:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        build(args[0], args[1], gun, c, preview)
