"""
The M249's belt reload clips (Blender 5.2, headless), built with TienInspectWeapon's animation pipeline (as
Post-93's scripts/post93/anim/p90_reload.py).

    blender -b --factory-startup -P scripts/anim/m249_reload.py -- <vanilla anims_X/Bob> <out_dir> [clip ...] [--preview]

    blender -b --factory-startup -P scripts/anim/m249_reload.py -- --animsets   (the cover events into the AnimSets)

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
The cover swings open and shut a step a frame (cover_events: our gotFeedCover between, Gunworks' gwSetPart markers
at OPEN / CLOSE) and the box leaves
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
# The feed cover swings one COVER_STEP a frame (gen_scripts.py's M249_Feed_Cover_<deg> parts, 10..60; 70 is the Open
# part): up from the frame after LIFT (the hand on the latch) until it is open at OPEN, down from the frame after
# PRESS (the hand on the open cover) until it is shut at CLOSE. The hand rides the cover's rear up to HAND_LIFT
# degrees and lets it go on alone; going down it rides the cover all the way (user, 2026-10-29: the hand floated over
# the gun while the cover was still drawn shut). Every step is an AnimSet event (write_animsets).
COVER_STEP, COVER_OPEN_DEG, HAND_LIFT = 10, 70, 30
LIFT = {"Unload": 13, "Load": 30}
PRESS = {"Unload": 33, "Load": 59}
OPEN = {c: f + COVER_OPEN_DEG // COVER_STEP for c, f in LIFT.items()}      # gwSetPart cover open (20, 37)
CLOSE = {c: f + COVER_OPEN_DEG // COVER_STEP for c, f in PRESS.items()}    # gwSetPart shut, the load click (40, 66)


def cover_deg(clip, f):
    """The cover's angle drawn at frame f (0 shut, 70 open)."""
    if clip not in LIFT or f <= LIFT[clip] or f >= CLOSE[clip]:
        return 0
    if OPEN[clip] <= f <= PRESS[clip]:
        return COVER_OPEN_DEG
    if f < OPEN[clip]:
        return (f - LIFT[clip]) * COVER_STEP
    return COVER_OPEN_DEG - (f - PRESS[clip]) * COVER_STEP
# The left hand's turn about the barrel (degrees about the weapon's Y), found by the elbow (user, 2026-10-29: "let's
# fix the left elbow flip"). Over the top: the handgun slide grip turned a further 60 degrees towards the gun's left,
# so on the canted gun the palm comes down on the cover from above; as it was (0) the wrist could only be kept
# natural with the elbow raised level with the shoulder over the gun, and the rig hopped between that and a low
# elbow, 11-18 cm in a frame (Unload 38, Load 27 / 36 / 57 / 66). 60 is the least that leaves no jump; more only
# moves the palm further off the cover. Under the receiver for the rack: the rifle load's magazine hold as it is,
# palm up, fingers round the handle on the right; it was turned a half turn (palm down), which held the elbow up
# over the gun at the swing limit through the whole pull.
OVER_TURN = 60.0
RACK_TURN = (0.0, 0.0, 0.0)
# Elbow swings (degrees about the shoulder-wrist line) that change more than SWING_JUMP in one frame are eased over
# the frames round them (steer_elbows): leaving and coming back to the aim in AimRack the right elbow jumped 62
# degrees (11 cm) in a frame between the aim's solution and the rack's.
SWING_JUMP = 12.0
# Unload starts on the idle: its elbows swing from the idle's to their own over the first RAMP frames (over the whole
# clip the elbow stayed near the idle's while the hand was already on the cover, the forearm twisted 130-143 degrees)
RAMP = {"Unload": 8}
SWING_RATE = 8.0


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
    degrees only."""
    if deg is None:
        return point("cover_open") @ (point("cover").inverted() @ v)
    hinge = point("cover").translation
    return hinge + Matrix.Rotation(math.radians(-deg), 3, 'X') @ (v - hinge)


# Points on the M249 (build_m249.py's photo coordinates).
LATCH = wp(704.0, 362.0)                    # the cover's rear, over the latch block
COVER_TOP = wp(600.0, 361.0)                # the cover's middle
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


def lift_keys(clip, top):
    """The hand on the latch at LIFT, then on the cover's rear as it swings up, one key a frame to HAND_LIFT."""
    f0 = LIFT[clip]
    keys = [Key(f0, lgrip=top(LATCH), ease=True)]
    for k in range(1, HAND_LIFT // COVER_STEP + 1):
        d = cover_deg(clip, f0 + k)
        keys.append(Key(f0 + k, lgrip=top(opened(LATCH, d), (-d, 0, 0))))
    return keys


def press_keys(clip, top):
    """The hand on the open cover at PRESS, then riding it down, one key a frame, shut at CLOSE."""
    keys = []
    for f in range(PRESS[clip], CLOSE[clip] + 1):
        d = cover_deg(clip, f) if f < CLOSE[clip] else 0
        keys.append(Key(f, lgrip=top(opened(COVER_TOP, d), (-d, 0, 0)), ease=(f in (PRESS[clip], CLOSE[clip]))))
    return keys


def keys_for(clip, r, g):
    over, under, sup = g["over"], g["under"], g["support"]
    over = Matrix.Rotation(math.radians(OVER_TURN), 4, 'Y') @ over
    top = lambda at, rot=(0, 0, 0): grip_on(over, at, rot)
    side = lambda at, rot=(0, 0, 0): grip_on(under, at, rot)
    n = LENGTHS[clip]
    W = dict(look=0.85, lean=6, aux=0.15, **WORK)
    # the idle's own hold, its top included (with `top=None` the work place's top was carried in and the clips ended
    # 11 degrees off vanilla's rifle idle, a snap into it; found 2026-10-26 with the P90's half turn)
    idle = dict(look=0, lean=0, aux=0, pos=r.weapon0.translation, along=rot_of(r.weapon0) @ Vector((0, 1, 0)),
                top=rot_of(r.weapon0) @ Vector((0, 0, r.top_sign)), face=rot_of(r.weapon0) @ Vector((1, 0, 0)))
    if clip == "Unload":
        away = hand_away(r, g, WORK)
        return [
            Key(0, look=0, lean=0, support=0, lgrip=top(LATCH)),
            Key(10, support=1, lgrip=top(LATCH + wp(0, H0 + 6) - wp(0, H0)), ease=True, **W),
        ] + lift_keys("Unload", top) + [                                            # on the latch, the cover up
            Key(23, lgrip=top(TRAY, (0, -30, 0)), ease=True),                       # on the belt in the tray
            Key(28, lgrip=top(TRAY_OUT, (0, -50, 0))),                              # lifted out
        ] + press_keys("Unload", top) + [                                           # on the open cover, shut
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
        ] + lift_keys("Load", top) + [                                              # on the latch, the cover up
            Key(41, lgrip=top(MOUTH, (0, -60, 0)), ease=True),                      # the belt's end at the box
            Key(49, lgrip=top(TRAY_OUT, (0, -50, 0))),
            Key(55, lgrip=top(TRAY, (0, -30, 0)), ease=True),                       # laid in the tray
        ] + press_keys("Load", top) + [                                             # pressed shut, the click
            Key(84, lgrip=sup, ease=True, **idle),     # back on the handguard as the gun comes home (as the racks)
            Key(n, ease=True, **idle),
        ]
    if clip in ("Rack", "AimRack"):
        R = dict(look=0.8, lean=4, aux=0.15, **RACK)
        under_r = lambda at: grip_on(under, at, RACK_TURN)
        home = dict(idle) if clip == "Rack" else dict(at_aux=True, aux=1.0, look=0, lean=0)
        # on the handguard where the aim clip has the hand (the idle's place on the gun, `sup`, put it 6 cm off
        # vanilla's aim and bent the wrist 40 degrees more)
        hold = sup if clip == "Rack" else r.support_aux
        # the gun comes home while the hand goes back to the handguard, both there at 38: with the hand on the
        # handguard at 34 and the gun still canted for the handle, the wrist bent 55-63 degrees (limit 50)
        return [
            Key(0, support=1, lgrip=hold, ease=True, **home),
            Key(12, lgrip=under_r(HANDLE), ease=True, **R),                     # on the handle (rackStart)
            Key(19, lgrip=under_r(HANDLE_BACK), ease=True),                      # all the way back
            Key(25, lgrip=under_r(HANDLE)),                                      # pushed forward again
            Key(38, lgrip=hold, ease=True, **home),
            Key(n, lgrip=hold, ease=True, **home),
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
    hinge = point("cover").translation
    for d in range(0, COVER_OPEN_DEG + 1, COVER_STEP):
        load(gun, "M249_COVER", Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-d), 4, 'X'),
             name="M249_Cover%d" % d)
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
    (cover angle, box on the gun, box in the hand)."""
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
        cover, on_gun, in_hand = state(frame)
        for d in range(0, COVER_OPEN_DEG + 1, COVER_STEP):
            obj["M249_Cover%d" % d].hide_render = d != cover
        obj["M249_BoxOnGun"].hide_render, obj["M249_BoxInHand"].hide_render = not on_gun, not in_hand
        for i in range(1, 10):
            obj["M249_Belt%d" % i].hide_render = not on_gun
        for name, cam in cams.items():
            scene.camera = cam
            scene.render.filepath = os.path.join(out_dir, "%s_%03d.png" % (name, frame))
            bpy.ops.render.render(write_still=True)


def eased_swings(seq):
    """seq (one swing per frame, None where the arm was not solved) with every jump over SWING_JUMP replaced by a
    smoothstep from the frame before the window to the frame after it, the window wide enough for SWING_RATE degrees
    a frame and kept inside the clip (its ends stay as solved: the clip starts and ends on its idle or aim)."""
    out = list(seq)
    n = len(out)
    for i in range(1, n):
        a, b = out[i - 1], out[i]
        if a is None or b is None or abs(b - a) <= SWING_JUMP:
            continue
        half = int(math.ceil(abs(b - a) / SWING_RATE / 2.0))
        lo, hi = max(0, i - 1 - half), min(n - 1, i + half)
        if out[lo] is None or out[hi] is None:
            continue
        for f in range(lo + 1, hi):
            t = (f - lo) / float(hi - lo)
            out[f] = out[lo] + (out[hi] - out[lo]) * t * t * (3 - 2 * t)
    return out


def steer_elbows(r, keys, n, from_base, ramp=None):
    """Build the clip, and if an elbow's swing jumps between two frames build it again with each frame's elbow
    steered (the rig's swivel_hint) along eased_swings of the first build's."""
    seen = []
    orig = r.pose_for
    hints = {}

    def pose_for(W, s, frame, breath, period, lgrip=None):
        r.swivel_hint = {side: seq[frame] for side, seq in hints.items() if seq[frame] is not None}
        start = len(r.swivels)
        p = orig(W, s, frame, breath, period, lgrip=lgrip)
        scale = r.swivel_scale
        seen.append({side: (d / scale if scale > 1e-3 else None) for side, d in r.swivels[start:]})
        return p

    r.pose_for = pose_for
    poses = r.build(keys, n, breath=(0, None), from_base=from_base, ramp=ramp)
    for side in "RL":
        seq = [s.get(side) for s in seen[-len(poses):]]
        eased = eased_swings(seq)
        if eased != seq:
            hints[side] = eased
    if hints:
        del seen[:]
        r.swivels, r.warnings, r.wrist_warnings, r.short_frames = [], [], [], []
        poses = r.build(keys, n, breath=(0, None), from_base=from_base, ramp=ramp)
    r.pose_for = orig
    r.swivel_hint = {}
    return poses


# AimRack: the right hand's grip leaves the aim's over the first frames and comes back over the second (both wrists
# within vanilla's reloads; shorter ones bent the right wrist 10-70 % past them)
AIM_GRIP = ((0, 16), (22, 38))


def aim_grip(r, xa):
    """AimRack: the right hand holds the gun with the aim clip's own grip at the aim and the idle's at the handle,
    blended between (AIM_GRIP). The rig has one hand-to-gun grip, the idle file's, which at the aim's gun place turned
    the hand 67 degrees off vanilla's aim and bent the right wrist 100-130 degrees around the aim."""
    wa = pose.world(xa, r.aux)
    aim = wa["Bip01_R_Hand"].inverted() @ wa["Bip01_Prop1"]
    idle = r.grip_r.copy()
    qa, qi = aim.to_quaternion(), idle.to_quaternion()
    if qa.dot(qi) < 0:
        qi.negate()
    orig = r.pose_for
    (a0, a1), (b0, b1) = AIM_GRIP

    def pose_for(W, s, frame, breath, period, lgrip=None):
        if frame <= a1:
            t = min(1.0, max(0.0, (frame - a0) / float(a1 - a0)))
        else:
            t = 1.0 - min(1.0, max(0.0, (frame - b0) / float(b1 - b0)))
        t = t * t * (3 - 2 * t)       # 0 = the aim's grip, 1 = the idle's
        r.grip_r = Matrix.LocRotScale(aim.translation.lerp(idle.translation, t), qa.slerp(qi, t), None)
        return orig(W, s, frame, breath, period, lgrip=lgrip)

    r.pose_for = pose_for


AIM_ENDS = (4, 8)    # frames blended at the start (longer let the hands leave the gun as it moves off: 3.6 cm at 8)
                     # and at the end


def aim_ends(r, poses):
    """AimRack: the arms (upper arm to fingers, both sides) blended into the aim clip's own over the first and last
    AIM_ENDS frames, so the clip starts and ends on vanilla's aim arms. The rig solves its aimed frames with the
    idle's hand-to-gun grip and wrist references, which left the aim's ends 5 cm / 21 degrees off vanilla's left
    forearm (10 cm off the right): a snap entering and leaving the aimed rack. The gun (Prop1) is the aim's place on
    the chest already and is kept."""
    bones = [b for b in r.aux if any(k in b for k in ("UpperArm", "Forearm", "Hand", "Finger"))]
    n = len(poses) - 1
    for f, p in enumerate(poses):
        d, span = (f, AIM_ENDS[0]) if f < n - f else (n - f, AIM_ENDS[1])
        if d < span:
            t = 1.0 - d / float(span)
            r.blend_local(p, r.aux, bones, t * t * (3 - 2 * t))


def build(src_dir, out_dir, clip, preview=False):
    xa, r, grips = build_rig(src_dir)
    n = LENGTHS[clip]
    keys = keys_for(clip, r, grips)
    if clip == "AimRack":
        aim_grip(r, xa)
    poses = steer_elbows(r, keys, n, clip in ("Unload", "Rack"), RAMP.get(clip))
    if clip == "AimRack":
        aim_ends(r, poses)
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
            cover = cover_deg(clip, f)
            if clip == "Unload":
                return cover, f < SWAP[clip], f >= SWAP[clip]
            if clip == "Load":
                return cover, f >= SWAP[clip], f < SWAP[clip]
            return 0, True, False
        render_closeups(os.path.join(out_dir, "prev_" + clip), list(range(0, len(poses), 2)), arm_ob, state)


def cover_events(clip):
    """(frame, event, value) for every cover step of the clip: our gotFeedCover for the steps between (M249.lua, local
    to the reloading game), Gunworks' gwSetPart for open and shut (synced through the server)."""
    out = []
    prev = 0
    for f in range(LIFT[clip] + 1, CLOSE[clip] + 1):
        d = cover_deg(clip, f)
        if d == prev:
            continue
        prev = d
        if d == 0:
            out.append((f, "gwSetPart", "FeedCover=GunsOfTien.M249_Feed_Cover_Closed"))
        elif d == COVER_OPEN_DEG:
            out.append((f, "gwSetPart", "FeedCover=GunsOfTien.M249_Feed_Cover_Open"))
        else:
            out.append((f, "gotFeedCover", "GunsOfTien.M249_Feed_Cover_%d" % d))
    return out


def write_animsets():
    """Rewrite the cover events (gwSetPart / gotFeedCover) of the Unload and Load AnimSets, both folders, from
    cover_events, after the other events, which stay as they are (their percentages are SWAP / CLOSE over the
    length: change those by hand with the frames above)."""
    import re
    for clip in ("Unload", "Load"):
        events = "".join(
            "\t<m_Events>\n\t\t<m_EventName>%s</m_EventName>\n\t\t<m_Time>Percentage</m_Time>\n"
            "\t\t<m_TimePc>%.4f</m_TimePc>\n\t\t<m_ParameterValue>%s</m_ParameterValue>\n\t</m_Events>\n"
            % (ev, f / float(LENGTHS[clip]), val) for f, ev, val in cover_events(clip))
        for folder in ("player", "player-vehicle"):
            path = os.path.join(MEDIA, "AnimSets", folder, "actions", "%sM249_GoT.xml" % clip)
            raw = open(path, "rb").read().decode("utf-8")
            nl = "\r\n" if "\r\n" in raw else "\n"
            text = raw.replace("\r\n", "\n")
            blocks = re.findall(r"\t<m_Events>\n.*?\t</m_Events>\n", text, re.S)
            keep = [x for x in blocks if "gwSetPart" not in x and "gotFeedCover" not in x]
            first = text.index(blocks[0])
            end = text.index(blocks[-1]) + len(blocks[-1])
            text = text[:first] + "".join(keep) + events + text[end:]
            open(path, "wb").write(text.replace("\n", nl).encode("utf-8"))
            print("[m249] %s: %d cover events" % (path, len(cover_events(clip))))


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    if "--animsets" in args:
        write_animsets()
        sys.exit(0)
    preview = "--preview" in args
    args = [a for a in args if a != "--preview"]
    for c in args[2:] or list(LENGTHS):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        build(args[0], args[1], c, preview)
