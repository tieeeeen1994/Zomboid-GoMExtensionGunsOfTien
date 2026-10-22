"""
The M249's belt reload clips (Blender 5.2, headless), built with TienInspectWeapon's animation pipeline (as
Post-93's scripts/post93/anim/p90_reload.py).

    blender -b --factory-startup -P scripts/anim/m249_reload.py -- <vanilla anims_X/Bob> <out_dir> [clip ...] [--preview]

clips: Unload Load Rack AimRack (default: all). Writes <out_dir>/Bob_GunsOfTien_M249_<clip>.x (+ .blend); with
--preview renders every 2nd frame with the M249 in the hand into <out_dir>/prev_<clip>/ (gif.py / sheet.py from
TienInspectWeapon/scripts/anim turn them into a GIF or a contact sheet). Ship the .x files to
Contents/mods/GoMExtensionGunsOfTien/42/media/anims_X/Bob/; the AnimSets *M249_GoT.xml play them.

FM 23-14's drills, standing, the gun held under the right arm in front of the body and canted so its top and left
side face the left hand:
- Unload: thumb the cover latches and raise the feed cover, lift the belt out of the tray, press the cover shut, then
  take the box by its side, unhook it from the receiver and carry it away to the left hip.
- Load: bring the new box up from the hip and hook it under the receiver, raise the cover, take the belt's end from
  the box's mouth and lay it in the tray, press the cover shut (the "load" click), back to the handguard and down.
- Rack: the left hand reaches under the receiver to the cocking handle on the right side, palm up, pulls it all the
  way back and pushes it forward again (the M249's handle does not ride with the bolt), back to the handguard.
  AimRack: the same without leaving the aim.
The cover opens and closes with Gunworks' gwSetPart markers (AnimSets, OPEN / CLOSE frames below) and the box leaves
the gun with the hand at the changeWeaponPart "mag" marker (SWAP): Gunworks' "attachments" reload style
(shared/GunsOfTien/M249.lua) then shows it on Bip01_Prop2, keyed here in the left hand from / up to the swap.

Weapon space is the game's (the model scripts'): +Y the muzzle, +Z the top, +X the gun's left; points on the gun are
written in build_m249.py's photo coordinates (L back from the muzzle tip, H up from the lowest point, mm) and wp()
turns them into weapon space.
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
POINTS = json.load(open(os.path.join(ROOT, "scripts/m249_points.json")))
K = POINTS["_extras"]["k"]
L0, H0 = POINTS["_extras"]["photo_origin_mm"]
FPS = 30
LENGTHS = {"Unload": 72, "Load": 96, "Rack": 45, "AimRack": 45}   # frames (M249.lua durations 2.4 / 3.2 / 1.5 s)
SWAP = {"Unload": 51, "Load": 20}           # changeWeaponPart "mag" (AnimSets: 51/72, 20/96)
OPEN = {"Unload": 15, "Load": 33}           # gwSetPart cover open
CLOSE = {"Unload": 38, "Load": 66}          # gwSetPart cover closed (the load click with it)


def wp(L, H, x=0.0):
    """Photo (L, H) mm and x mm to the gun's left -> weapon space (game units)."""
    return Vector((x * K, (L0 - L) * K, (H - H0) * K))


def point(name):
    pt = POINTS[name]
    rx, ry, rz = [math.radians(a) for a in pt["rotate"]]
    return (Matrix.Translation(Vector(pt["offset"])) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Rotation(ry, 4, 'Y')
            @ Matrix.Rotation(rz, 4, 'Z'))


def opened(v, deg=None):
    """A point on the closed cover where it is with the cover open (cover_open about the hinge), or swung up `deg`
    degrees only (the hand lifts it part way and the spring takes it the rest)."""
    if deg is None:
        return point("cover_open") @ (point("cover").inverted() @ v)
    hinge = point("cover").translation
    return hinge + Matrix.Rotation(math.radians(-deg), 3, 'X') @ (v - hinge)


# Points on the M249 (build_m249.py's photo coordinates).
LATCH = wp(704.0, 362.0)                    # the cover's rear, over the latch block
LATCH_UP = opened(LATCH, 30.0)              # lifted 30 degrees: the cover springs open from there
COVER_TOP = wp(600.0, 361.0)                # the cover's middle
COVER_TOP_OPEN = opened(COVER_TOP)
TRAY = wp(515.0, 326.0, 20.0)               # the belt's lead rounds in the tray (round 1-2)
TRAY_OUT = wp(515.0, 334.0, 52.0)           # lifted out to the left
BOX_SIDE = wp(538.0, 200.0, 33.0 + 47.0)    # the box's outer (left) face, half way down
MOUTH = wp(538.0, 275.0, 58.0)              # the belt's end at the box's mouth
HANDLE = wp(506.0, 306.0, -40.0)            # under the cocking handle's knob (right side)
HANDLE_BACK = wp(506.0 + 95.0, 306.0, -40.0)


def build_rig(src_dir):
    xa = xanim.read(os.path.join(src_dir, "Bob_IdleRifle.x"), with_mesh=True)
    base = pose.from_clip(xa, 0)
    aux = pose.copy(base)
    found = pose.from_clip(xanim.read(os.path.join(src_dir, "Bob_IdleAimRifle.x")), 0)
    aux.update({b: m for b, m in found.items() if b in base})
    r = rig.Rig(xa, base, aux=aux, poi=0.2, top=1, rest=x_import.rest_matrices(xa))

    def sample(clip, frame):
        p = pose.copy(base)
        p.update({b: m for b, m in pose.from_clip(xanim.read(os.path.join(src_dir, clip)), frame * 160).items()
                  if b in base})
        return p

    # over the top, palm down: vanilla's handgun reload over the slide (frame 48), turned from the handgun's
    # upside-down Prop1 (top -Z) to a rifle's (top +Z) by a half turn about the barrel
    over = r.sample_lgrip(sample("Bob_Reload_Handgun.X", 48))
    over = Matrix.Rotation(math.pi, 4, 'Y') @ over
    # holding a magazine under the receiver: vanilla's rifle load, magazine in the well (frame 30)
    under = r.sample_lgrip(sample("Bob_Reload_Rifle_Load.x", 30))
    belt_world = pose.world(xa, sample("Bob_Reload_Handgun.X", 16))["Bip01_L_Hand"]
    return xa, r, {"over": over, "under": under, "support": r.support_base, "belt_world": belt_world}


def palm(template):
    """The middle of the palm in the template's weapon space (the hand bone runs along its local X to the fingers)."""
    return template @ Vector((0.045, 0.0, 0.012))


def grip_on(template, at, rot=(0.0, 0.0, 0.0)):
    """A left-hand placement with the template's palm on `at` (weapon space), turned by `rot` (degrees about the
    weapon's X, Y, Z) about that point."""
    R = (Matrix.Rotation(math.radians(rot[0]), 3, 'X') @ Matrix.Rotation(math.radians(rot[1]), 3, 'Y')
         @ Matrix.Rotation(math.radians(rot[2]), 3, 'Z'))
    q = (R @ template.to_3x3()).to_quaternion()
    return Matrix.LocRotScale(at + R @ (template.translation - palm(template)), q, None)


# The gun's places (character space, ch(right, up, forward); the left shoulder is at right -0.095, up 0.74, forward
# -0.03 and a hand reaches 0.274 from it). Under the right arm in front of the body, muzzle forward-left, canted to the
# right so the top and the left side (feed tray, box) face the left hand.
WORK = dict(pos=ch(0.06, 0.58, 0.10), along=ch(-0.40, 0.35, 0.85), top=ch(0.35, 0.92, -0.2))
# canted the other way for the cocking handle on the right side
RACK = dict(pos=ch(0.06, 0.58, 0.10), along=ch(-0.40, 0.30, 0.86), top=ch(-0.45, 0.88, -0.2))
AWAY = ch(-0.15, 0.50, 0.10)                # the left hand in front of the left hip, holding the box


def weapon_at(r, place):
    return r.weapon_at(dict(at_aux=0.0, top=place["top"], along=place["along"], face=None, pos=place["pos"],
                            roll=0.0, turn=0.0, drop=0.0, pitch=0.0), r.eye0)


def hand_away(r, g, place):
    """lgrip for the left hand at AWAY (vanilla's belt-reach hand orientation) while the gun is at `place`."""
    W = weapon_at(r, place)
    return W.inverted() @ Matrix.LocRotScale(AWAY, g["belt_world"].to_quaternion(), None)


def keys_for(clip, r, g):
    over, under, sup = g["over"], g["under"], g["support"]
    top = lambda at, rot=(0, 0, 0): grip_on(over, at, rot)
    side = lambda at, rot=(0, 0, 0): grip_on(under, at, rot)
    n = LENGTHS[clip]
    W = dict(look=0.85, lean=6, aux=0.15, **WORK)
    idle = dict(look=0, lean=0, aux=0, pos=r.weapon0.translation, along=rot_of(r.weapon0) @ Vector((0, 1, 0)),
                top=None, face=rot_of(r.weapon0) @ Vector((1, 0, 0)))
    if clip == "Unload":
        away = hand_away(r, g, WORK)
        return [
            Key(0, look=0, lean=0, support=0, lgrip=top(LATCH)),
            Key(10, support=1, lgrip=top(LATCH + wp(0, H0 + 6) - wp(0, H0)), ease=True, **W),
            Key(OPEN["Unload"], lgrip=top(LATCH_UP, (-30, 0, 0))),                  # the cover up
            Key(21, lgrip=top(TRAY, (0, -30, 0)), ease=True),                       # on the belt in the tray
            Key(27, lgrip=top(TRAY_OUT, (0, -50, 0))),                              # lifted out
            Key(33, lgrip=top(COVER_TOP_OPEN, (-70, 0, 0)), ease=True),             # on the open cover
            Key(CLOSE["Unload"], lgrip=top(COVER_TOP), ease=True),                  # pressed shut
            Key(46, lgrip=side(BOX_SIDE), ease=True),                               # the box's side
            Key(SWAP["Unload"], lgrip=side(BOX_SIDE + wp(0, H0 - 30, 6) - wp(0, H0))),   # unhooked
            Key(62, lgrip=away, ease=True),
            Key(n, lgrip=away),
        ]
    if clip == "Load":
        away = hand_away(r, g, WORK)
        return [
            Key(0, support=1, lgrip=away, ease=True, **W),
            Key(13, lgrip=side(BOX_SIDE + wp(0, H0 - 40, 10) - wp(0, H0))),         # the box up under the receiver
            Key(SWAP["Load"], lgrip=side(BOX_SIDE), ease=True),                     # hooked on
            Key(27, lgrip=top(LATCH + wp(0, H0 + 6) - wp(0, H0)), ease=True),
            Key(OPEN["Load"], lgrip=top(LATCH_UP, (-30, 0, 0))),                    # the cover up
            Key(41, lgrip=top(MOUTH, (0, -60, 0)), ease=True),                      # the belt's end at the box
            Key(49, lgrip=top(TRAY_OUT, (0, -50, 0))),
            Key(55, lgrip=top(TRAY, (0, -30, 0)), ease=True),                       # laid in the tray
            Key(60, lgrip=top(COVER_TOP_OPEN, (-70, 0, 0)), ease=True),
            Key(CLOSE["Load"], lgrip=top(COVER_TOP), ease=True),                    # pressed shut, the click
            Key(76, lgrip=sup, ease=True),                                          # back on the handguard
            Key(n, ease=True, **idle),
        ]
    if clip in ("Rack", "AimRack"):
        R = dict(look=0.8, lean=4, aux=0.15, **RACK)
        under_r = lambda at: grip_on(under, at, (0, 180, 0))
        if clip == "Rack":
            first = Key(0, support=1, lgrip=sup, ease=True, **idle)
            last = Key(n, lgrip=sup, ease=True, **idle)
        else:
            first = Key(0, support=1, lgrip=sup, ease=True, at_aux=True, aux=1.0, look=0, lean=0)
            last = Key(n, lgrip=sup, ease=True, at_aux=True, aux=1.0, look=0, lean=0)
        return [
            first,
            Key(12, lgrip=under_r(HANDLE), ease=True, **R),                     # on the handle (rackStart)
            Key(19, lgrip=under_r(HANDLE_BACK), ease=True),                      # all the way back
            Key(25, lgrip=under_r(HANDLE)),                                      # pushed forward again
            Key(34, lgrip=sup, ease=True),
            last,
        ]
    raise ValueError(clip)


def key_prop2(xa, poses, swap, in_hand_after):
    """Bip01_Prop2 (Gunworks' reload magazine: here the box) on every pose: at the box's point on the gun, or, on the
    hand's side of the swap, in the left hand with the offset it has at the swap frame."""
    M = point("box")
    w = pose.world(xa, poses[swap])
    offset = w["Bip01_L_Hand"].inverted() @ (w["Bip01_Prop1"] @ M)
    for f, p in enumerate(poses):
        w = pose.world(xa, p)
        in_hand = f >= swap if in_hand_after else f <= swap
        world = w["Bip01_L_Hand"] @ offset if in_hand else w["Bip01_Prop1"] @ M
        p["Bip01_Prop2"] = w["Bip01"].inverted() @ world


def gun_objects(arm_ob):
    """The M249 (body, cover closed and open, folded bipod, box and belt) in weapon space, on Bip01_Prop1; the box
    also on Bip01_Prop2 (in the hand)."""
    obs = {}

    def load(path, node, mat_world=None, colour=(0.16, 0.16, 0.17, 1.0), bone="Bip01_Prop1", name=None):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=path)
        new = list(set(bpy.data.objects) - before)
        src = next(o for o in new if o.name.split(".")[0] == node)
        name = name or "M249_" + node
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

    gun = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_M249.fbx")
    box = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_M249_box.fbx")
    load(gun, "M249_BODY")
    load(gun, "M249_BIPOD_FOLDED")
    load(gun, "M249_COVER", point("cover"), name="M249_CoverClosed")
    load(gun, "M249_COVER", point("cover_open"), name="M249_CoverOpen")
    od = (0.3, 0.32, 0.2, 1.0)
    load(box, "556x45Box200_M249", point("box"), od, name="M249_BoxOnGun")
    load(box, "556x45Box200_M249", None, od, bone="Bip01_Prop2", name="M249_BoxInHand")
    for i in range(1, 10):
        load(box, "556x45_M249_%d" % i, None, (0.55, 0.45, 0.2, 1.0), name="M249_Belt%d" % i)
    return obs


CLOSEUPS = {
    # name: (camera location, look-at), Blender space (Z up, the character faces -Y, its left is +X)
    "front": ((0.35, -1.8, 0.95), (0.0, -0.12, 0.6)),
    "top": ((0.45, -0.6, 1.95), (0.0, -0.12, 0.58)),
    "side": ((1.75, -0.45, 0.95), (0.0, -0.12, 0.6)),
}


def render_closeups(out_dir, frames, arm_ob, state):
    """Upper-body views of each frame (out_dir/<view>_<frame>.png), for sheet.py / gif.py; state(frame) ->
    (cover open, box on the gun, box in the hand)."""
    os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    x_preview.setup_render(scene)
    scene.render.resolution_x = scene.render.resolution_y = 480
    cams = {}
    for name, (loc, tgt) in CLOSEUPS.items():
        cam = x_preview.camera("Cam_" + name, loc, tgt)
        cam.data.ortho_scale = 0.85
        cams[name] = cam
    obj = bpy.data.objects
    for frame in frames:
        scene.frame_set(frame)
        cover_open, on_gun, in_hand = state(frame)
        obj["M249_CoverOpen"].hide_render, obj["M249_CoverClosed"].hide_render = not cover_open, cover_open
        obj["M249_BoxOnGun"].hide_render, obj["M249_BoxInHand"].hide_render = not on_gun, not in_hand
        for i in range(1, 10):
            obj["M249_Belt%d" % i].hide_render = not on_gun
        for name, cam in cams.items():
            scene.camera = cam
            scene.render.filepath = os.path.join(out_dir, "%s_%03d.png" % (name, frame))
            bpy.ops.render.render(write_still=True)


def build(src_dir, out_dir, clip, preview=False):
    xa, r, grips = build_rig(src_dir)
    n = LENGTHS[clip]
    keys = keys_for(clip, r, grips)
    poses = r.build(keys, n, breath=(0, None), from_base=(clip in ("Unload", "Rack")))
    if clip in SWAP:
        key_prop2(xa, poses, SWAP[clip], clip == "Unload")
    if r.warnings:
        print("[m249] %s: %d frames out of reach, worst: %s" % (clip, len(r.warnings),
                                                                max(r.warnings, key=lambda w: float(w.rsplit(" ", 1)[1]))))
    if r.wrist_warnings:
        print("[m249] %s: %d arm-frames with the wrist past its natural range, e.g. %s" % (
            clip, len(r.wrist_warnings), r.wrist_warnings[0]))
    for s in "RL":
        sw = [d for side, d in r.swivels if side == s]
        if len(sw) > 1:
            print("[m249] %s: %s elbow swing %.0f..%.0f, largest step %.1f" % (
                clip, s, min(sw), max(sw), max(abs(b - a) for a, b in zip(sw, sw[1:]))))
    os.makedirs(out_dir, exist_ok=True)
    name = "Bob_GunsOfTien_M249_" + clip
    src = os.path.join(src_dir, "Bob_IdleRifle.x")
    arm_ob = x_import.load(src)
    pose.bake(arm_ob, xa, poses, name)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, name + ".blend"))
    x_export.export(src, os.path.join(out_dir, name + ".x"), name, arm_ob)
    if preview:
        gun_objects(arm_ob)

        def state(f):
            cover = OPEN.get(clip, 1e9) <= f < CLOSE.get(clip, -1)
            if clip == "Unload":
                return cover, f < SWAP[clip], f >= SWAP[clip]
            if clip == "Load":
                return cover, f >= SWAP[clip], f < SWAP[clip]
            return False, True, False
        render_closeups(os.path.join(out_dir, "prev_" + clip), list(range(0, len(poses), 2)), arm_ob, state)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    preview = "--preview" in args
    args = [a for a in args if a != "--preview"]
    for c in args[2:] or list(LENGTHS):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        build(args[0], args[1], c, preview)
