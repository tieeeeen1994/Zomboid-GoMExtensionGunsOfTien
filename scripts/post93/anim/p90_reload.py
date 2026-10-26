"""
The FN P90 TR's reload clips (Blender 5.2, headless), built with TienInspectWeapon's animation pipeline.

    blender -b --factory-startup -P scripts/post93/anim/p90_reload.py -- <vanilla anims_X/Bob> <out_dir> [clip ...] [--preview]

clips: Unload Load Rack AimRack (default: all). Writes <out_dir>/Bob_GunsOfTien_P90_<clip>.x (+ .blend); with
--preview renders every 2nd frame with the P90 in the hand into <out_dir>/prev_<clip>/ (gif.py / sheet.py from
TienInspectWeapon/scripts/anim turn them into a GIF or a contact sheet). Ship the .x files to
Contents/mods/GoMExtensionGunsOfTienPost93/42/media/anims_X/Bob/; the AnimSets P90TR_GoT.xml play them.

The P90 is held like a pistol (vanilla's handgun idle and aim are the base and second pose) and its 50-round
magazine lies on top of the receiver, so the left hand works on top of the gun, not under the grip:
- Unload: the gun comes up in front of the chest, the left hand takes the magazine's rear end, lifts it and pulls it
  back off the gun, and carries it away to the hip.
- Load: the left hand brings the new magazine up over the gun, engages its front under the rail block, swings the
  rear down and presses it until it clicks (the "load" sound), and goes back to the support grip.
- The magazine leaves the gun with the hand: the P90 is registered with Gunworks' "attachments" reload style
  (Guns.lua), so the AnimSets' changeWeaponPart events take the magazine part off the gun at SWAP["Unload"] (the hand
  has the magazine) and put it back at SWAP["Load"] (pressed home). Gunworks would also show a magazine in the left
  hand (its reload-magazine location = Bip01_Prop2); Guns.lua turns that off for the P90 (user, 2026-10-15). These
  clips still key Bip01_Prop2 (rigidly in the hand from / up to the swap, where the magazine sat on the gun), so it
  can be turned back on by dropping that wrapper.
- Rack: the left hand pulls the charging handle on the gun's left side all the way back and lets it go, then the
  gun goes back down to the idle. AimRack: the same without leaving the aim.
The left hand's grips are vanilla's (sampled from Bob_Reload_Handgun: over the slide while racking, reaching to the
belt for a magazine), moved onto the P90's magazine and charging handle (rig.Key lgrip).

Weapon space is the game's (what the model scripts use): +Y the muzzle, and since the P90 is held like a pistol its
model is upside down: its top is -Z and its left side -X (CLAUDE.md, "P90 TR reference and model"). Points on the
gun are written in the photo's coordinates (L back from the muzzle tip, H up from the lowest point, mm) and wp()
turns them into weapon space.
"""

import json
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
ANIM = os.environ.get("TIEN_ANIM") or os.path.normpath(os.path.join(ROOT, "..", "TienInspectWeapon", "scripts", "anim"))
sys.path.insert(0, ANIM)
import pose  # noqa: E402
import rig  # noqa: E402
import x_export  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
import xanim  # noqa: E402
from rig import Key, ch, UP, rot_of  # noqa: E402

MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
# game units per real mm, from the builder (0.603 since 2026-10-26, the M16A2's proportion; the places below were
# drafted at 0.72, so offsets measured on the gun are scaled by S; CONTACT is the hand's own, not scaled)
K = 1.0 / json.load(open(os.path.join(ROOT, "scripts/post93/p90_points.json")))["_extras"]["real_mm_per_game_unit"]
S = K / 0.00072
L0, H0 = 237.0, 80.0                       # the model origin in the photo (build_p90.py)
FPS = 30
LENGTHS = {"Unload": 42, "Load": 54, "Rack": 36, "AimRack": 36}   # frames (Guns.lua durations 1.4 / 1.8 / 1.2 s)
SWAP = {"Unload": 16, "Load": 36}          # frames of the changeWeaponPart events (AnimSets: 16/42 = 0.38, 36/54 = 0.66)


def wp(L, H, x=0.0):
    """Photo (L, H) mm and x mm to the gun's left -> weapon space (game units): held like a pistol, the model is
    turned upside down (x -> -x, z -> -z)."""
    return Vector((-x * K, (L0 - L) * K, -(H - H0) * K))


# Points on the P90 (photo coordinates, see build_p90.py).
MAG_REAR_ON = wp(330.0, 142.5)             # palm on the magazine's rear cap (top H 141.8)
MAG_REAR = MAG_REAR_ON + wp(0.0, H0 + 8.0) - wp(0.0, H0)   # 8 mm above it
MAG_MID = wp(260.0, 142.5)
HANDLE = wp(78.0, 103.5, 28.0)             # palm on the charging handle (gun's left side)
HANDLE_BACK = wp(78.0 + 60.0, 103.5, 28.0)  # pulled 60 mm back


def build_rig(src_dir):
    xa = xanim.read(os.path.join(src_dir, "Bob_IdleHandgun.X"), with_mesh=True)
    base = pose.from_clip(xa, 0)
    aux = pose.copy(base)
    found = pose.from_clip(xanim.read(os.path.join(src_dir, "Bob_IdleAimHandgun.X")), 0)
    aux.update({b: m for b, m in found.items() if b in base})
    r = rig.Rig(xa, base, aux=aux, poi=0.0, top=-1, support_from_aux=True, rest=x_import.rest_matrices(xa))
    # left-hand grips from vanilla's handgun reload: over the slide (racking) and out at the belt
    rel = xanim.read(os.path.join(src_dir, "Bob_Reload_Handgun.X"))

    def at(frame):
        p = pose.copy(base)
        p.update({b: m for b, m in pose.from_clip(rel, frame * 160).items() if b in base})
        return r.sample_lgrip(p)

    def world_hand(frame):
        p = pose.copy(base)
        p.update({b: m for b, m in pose.from_clip(rel, frame * 160).items() if b in base})
        return pose.world(xa, p)["Bip01_L_Hand"]

    grips = {"over": at(48), "support": r.support_aux, "belt_world": world_hand(16)}
    return xa, r, grips


# Where the palm touches in each vanilla grip (weapon space of vanilla's M9, whose top is -Z): over the slide's top,
# in the middle of the hand (Bob_Reload_Handgun frame 48).
CONTACT = {"over": Vector((0.0, 0.064, -0.036))}


def grip_on(template, contact, at, rot=(0.0, 0.0, 0.0)):
    """A left-hand placement with the template's palm on `at` (weapon space): the template's wrist-to-palm offset
    and hand orientation kept, turned by `rot` (degrees about the weapon's X, Y, Z) about the contact point."""
    import math
    R = (Matrix.Rotation(math.radians(rot[0]), 3, 'X') @ Matrix.Rotation(math.radians(rot[1]), 3, 'Y')
         @ Matrix.Rotation(math.radians(rot[2]), 3, 'Z'))
    q = (R @ template.to_3x3()).to_quaternion()
    return Matrix.LocRotScale(at + R @ (template.translation - contact), q, None)


# The gun's places (character space, ch(right, up, forward); the shoulders are at right +-0.095, up 0.74, forward
# -0.03 and a hand reaches 0.274 from its shoulder). Held like a pistol, the P90's butt runs 0.19 back from the hand,
# so the gun is held across the chest, muzzle forward-left.
MAG = dict(pos=ch(0.05, 0.65, 0.20), along=ch(-0.45, 0.4, 0.8), top=ch(-0.25, 0.85, -0.45))     # top to the eyes
RACK = dict(pos=ch(0.04, 0.66, 0.11), along=ch(-0.85, 0.25, 0.46), top=ch(-0.1, 0.9, -0.4))    # handle to the body
AWAY = ch(-0.13, 0.52, 0.12)          # the left hand in front of the left hip, holding a magazine


def weapon_at(r, place):
    return r.weapon_at(dict(at_aux=0.0, top=place["top"], along=place["along"], face=None, pos=place["pos"],
                            roll=0.0, turn=0.0, drop=0.0, pitch=0.0), r.eye0)


def hand_away(r, g, place):
    """lgrip for the left hand at AWAY (vanilla's belt-reach hand orientation) while the gun is at `place`."""
    W = weapon_at(r, place)
    rot = g["belt_world"].to_quaternion()
    return W.inverted() @ Matrix.LocRotScale(AWAY, rot, None)


def keys_for(clip, r, g):
    over, sup = g["over"], g["support"]
    on_top = lambda at, rot=(0, 0, 0): grip_on(over, CONTACT["over"], at, rot)
    side = lambda at: grip_on(over, CONTACT["over"], at, (0, 90, 0))
    n = LENGTHS[clip]
    M = dict(look=0.9, lean=5, aux=0.2, **MAG)
    if clip == "Unload":
        away = hand_away(r, g, MAG)
        return [
            Key(0, look=0, lean=0, support=0, lgrip=on_top(MAG_REAR)),
            Key(9, support=1, lgrip=on_top(MAG_REAR), ease=True, **M),
            Key(15, lgrip=on_top(MAG_REAR_ON), ease=True),
            # lift the rear end out of its catch and pull the magazine back off the gun
            Key(23, lgrip=on_top(MAG_REAR_ON + Vector((0, -0.008, -0.016)) * S, (18, 0, 0))),
            Key(31, lgrip=on_top(MAG_REAR_ON + Vector((0, -0.060, -0.028)) * S, (10, 0, 0))),
            # and away, in front of the hip
            Key(n, lgrip=away, ease=True),
        ]
    if clip == "Load":
        away = hand_away(r, g, MAG)
        return [
            Key(0, support=1, lgrip=away, ease=True, **M),
            # the new magazine up over the gun, its front end first, the rear held high
            Key(14, lgrip=on_top(MAG_MID + Vector((0, 0.030, -0.030)) * S, (20, 0, 0))),
            Key(22, lgrip=on_top(MAG_MID + Vector((0, 0.020, -0.010)) * S, (12, 0, 0)), ease=True),
            # swing the rear down and press it home (the click and the swap at 0.66)
            Key(30, lgrip=on_top(MAG_REAR)),
            Key(36, lgrip=on_top(MAG_REAR_ON), ease=True),
            Key(42, lgrip=on_top(MAG_REAR + Vector((0, 0, -0.014)) * S)),
            # back to the support grip
            Key(n, lgrip=sup, ease=True),
        ]
    if clip in ("Rack", "AimRack"):
        R = dict(look=0.8, lean=4, aux=0.2, **RACK)
        if clip == "Rack":
            first = Key(0, support=1, lgrip=sup, ease=True, **M)
            last = Key(n, look=0, lean=0, aux=0, lgrip=sup, pos=r.weapon0.translation,
                       along=rot_of(r.weapon0) @ Vector((0, 1, 0)), top=None, face=rot_of(r.weapon0) @ Vector((1, 0, 0)),
                       ease=True)
        else:
            first = Key(0, support=1, lgrip=sup, ease=True, at_aux=True, aux=1.0, look=0, lean=0)
            last = Key(n, lgrip=sup, ease=True, at_aux=True, aux=1.0, look=0, lean=0)
        return [
            first,
            Key(11, lgrip=side(HANDLE), ease=True, **R),                       # on the handle (rackStart at 0.4)
            Key(21, lgrip=side(HANDLE_BACK), ease=True),                       # all the way back (rackBullet 0.6)
            Key(26, lgrip=side(HANDLE_BACK + Vector((-0.02, 0, 0.0)) * S)),         # let go (rackEnd 0.75)
            *([Key(30, support=0)] if clip == "Rack" else []),                 # the left hand drops to the side
            last,
        ]
    raise ValueError(clip)


def mag_on_gun():
    """The magazine's place on the gun (weapon space): the model script's `magazine` point, offset then rotateXYZ."""
    import json
    import math
    pt = json.load(open(os.path.join(ROOT, "scripts/post93/p90_points.json")))["magazine"]
    rx, ry, rz = [math.radians(a) for a in pt["rotate"]]
    return (Matrix.Translation(Vector(pt["offset"])) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Rotation(ry, 4, 'Y')
            @ Matrix.Rotation(rz, 4, 'Z'))


def key_prop2(xa, poses, swap, in_hand_after):
    """Bip01_Prop2 (Gunworks' reload magazine) on every pose: where the magazine sits on the gun, or, on the hand's side
    of the swap, held in the left hand with the offset it has at the swap frame (so the swap shows no jump)."""
    M = mag_on_gun()
    w = pose.world(xa, poses[swap])
    offset = w["Bip01_L_Hand"].inverted() @ (w["Bip01_Prop1"] @ M)
    for f, p in enumerate(poses):
        w = pose.world(xa, p)
        in_hand = f >= swap if in_hand_after else f <= swap
        world = w["Bip01_L_Hand"] @ offset if in_hand else w["Bip01_Prop1"] @ M
        p["Bip01_Prop2"] = w["Bip01"].inverted() @ world


def gun_objects(arm_ob):
    """The P90 (body, charging handles, magazine at its point) in weapon space, parented to Bip01_Prop1."""
    import json
    points = json.load(open(os.path.join(ROOT, "scripts/post93/p90_points.json")))
    obs = []

    def load(path, node, mat_world=None, colour=(0.18, 0.18, 0.2, 1.0), bone="Bip01_Prop1", name=None):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=path)
        new = list(set(bpy.data.objects) - before)
        src = next(o for o in new if o.name.split(".")[0] == node)
        me = bpy.data.meshes.new(name or "P90_" + node)
        verts = [Vector((v.co.x, v.co.y, -v.co.z)) for v in src.data.vertices]      # file -> game space
        if mat_world is not None:
            verts = [mat_world @ v for v in verts]
        me.from_pydata([tuple(v) for v in verts], [], [tuple(reversed(p.vertices)) for p in src.data.polygons])
        me.update()
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
        ob = bpy.data.objects.new(name or "P90_" + node, me)
        bpy.context.scene.collection.objects.link(ob)
        m = bpy.data.materials.new(name or "P90_" + node)
        m.diffuse_color = colour
        me.materials.append(m)
        x_preview.attach_to_bone(ob, arm_ob, bone)
        obs.append(ob)

    gun = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx")
    load(gun, "P90TR_BODY")
    load(gun, "P90TR_BOLT")
    import math
    pt = points["magazine"]
    rx, ry, rz = [math.radians(a) for a in pt["rotate"]]
    mag_m = (Matrix.Translation(Vector(pt["offset"])) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Rotation(ry, 4, 'Y')
             @ Matrix.Rotation(rz, 4, 'Z'))
    mags = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx")
    load(mags, "57x28Magazine50_P90", mag_m, (0.35, 0.22, 0.12, 1.0), name="P90_MagOnGun")
    load(mags, "57x28Magazine50_P90", None, (0.35, 0.22, 0.12, 1.0), bone="Bip01_Prop2", name="P90_MagInHand")
    return {o.name: o for o in obs}


CLOSEUPS = {
    # name: (camera location, look-at), Blender space (Z up, the character faces -Y, its left is +X)
    "front": ((0.95, -1.45, 1.05), (0.02, -0.12, 0.62)),
    "top": ((0.35, -0.75, 1.95), (0.02, -0.15, 0.62)),
    "side": ((-1.7, -0.25, 0.72), (0.0, -0.12, 0.62)),
}


def render_closeups(out_dir, frames, arm_ob, mag_in_hand=None, show_in_hand=True):
    """Upper-body views of each frame (out_dir/<view>_<frame>.png), for sheet.py / gif.py."""
    os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    x_preview.setup_render(scene)
    scene.render.resolution_x = scene.render.resolution_y = 480
    cams = {}
    for name, (loc, tgt) in CLOSEUPS.items():
        cam = x_preview.camera("Cam_" + name, loc, tgt)
        cam.data.ortho_scale = 0.7
        cams[name] = cam
    on_gun, in_hand = bpy.data.objects.get("P90_MagOnGun"), bpy.data.objects.get("P90_MagInHand")
    for frame in frames:
        scene.frame_set(frame)
        held = bool(mag_in_hand and mag_in_hand(frame))
        if on_gun and in_hand:
            on_gun.hide_render, in_hand.hide_render = held, not (held and show_in_hand)
        for name, cam in cams.items():
            scene.camera = cam
            scene.render.filepath = os.path.join(out_dir, "%s_%03d.png" % (name, frame))
            bpy.ops.render.render(write_still=True)


def build(src_dir, out_dir, clip, preview=False):
    xa, r, grips = build_rig(src_dir)
    n = LENGTHS[clip]
    keys = keys_for(clip, r, grips)
    poses = r.build(keys, n, breath=(0, None), from_base=(clip == "Unload"))
    if clip in SWAP:
        key_prop2(xa, poses, SWAP[clip], clip == "Unload")
    if r.warnings:
        print("[p90] %s: %d frames out of reach, worst: %s" % (clip, len(r.warnings),
                                                               max(r.warnings, key=lambda w: float(w.rsplit(" ", 1)[1]))))
    if r.wrist_warnings:
        print("[p90] %s: %d arm-frames with the wrist past its natural range, e.g. %s" % (clip, len(r.wrist_warnings),
                                                                                           r.wrist_warnings[0]))
    for s in "RL":
        sw = [d for side, d in r.swivels if side == s]
        if len(sw) > 1:
            print("[p90] %s: %s elbow swing %.0f..%.0f, largest step %.1f" % (
                clip, s, min(sw), max(sw), max(abs(b - a) for a, b in zip(sw, sw[1:]))))
    os.makedirs(out_dir, exist_ok=True)
    name = "Bob_GunsOfTien_P90_" + clip
    src = os.path.join(src_dir, "Bob_IdleHandgun.X")
    arm_ob = x_import.load(src)
    pose.bake(arm_ob, xa, poses, name)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, name + ".blend"))
    x_export.export(src, os.path.join(out_dir, name + ".x"), name, arm_ob)
    if preview:
        gun_objects(arm_ob)
        # the magazine is on the gun until the unload's swap and from the load's; the hand shows none (Guns.lua)
        swap = SWAP.get(clip)
        off = None if swap is None else (lambda f: f >= swap) if clip == "Unload" else (lambda f: f < swap)
        render_closeups(os.path.join(out_dir, "prev_" + clip), list(range(0, len(poses), 2)), arm_ob, off,
                        show_in_hand=False)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    preview = "--preview" in args
    args = [a for a in args if a != "--preview"]
    for c in args[2:] or list(LENGTHS):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        build(args[0], args[1], c, preview)
