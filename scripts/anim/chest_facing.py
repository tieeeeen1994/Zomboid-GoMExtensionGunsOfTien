"""
How far a stance's chest turns from vanilla's (Blender 5.2, headless; TienInspectWeapon's pose module).

    blender -b --factory-startup -P scripts/anim/chest_facing.py -- <vanilla anims_X/Bob> <clips dir> <prefix> [clip ...]

For each clip <prefix><name>.x in the clips dir (a stance's single-clip files, e.g. GunsOfTien_CompactUzi_), against
vanilla's Bob_<name>.x frame by frame: the shoulder line's facing (the upper arms' line turned to point forward,
flattened on the ground) and the hips' (the thighs' line), each against vanilla's in the same frame, in degrees.
Prints the mean and worst per clip. Written for the short SMG stance's squaring (user, 2026-10-29: "straighten it so
that the character is facing directly to the player direction"), as the bullpup's was measured (CLAUDE.md "Bullpup
stance (built)": the turned chest read 8-24 degrees off vanilla's in carried frames).
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_stance as C  # noqa: E402,F401  (puts TienInspectWeapon's scripts/anim on the path)
import pose  # noqa: E402
import xanim  # noqa: E402

DEFAULT = ["IdleRifle", "WalkRifle", "RunRifle", "Sprint_Rifle", "WalkSneak_Rifle", "RunSneak_Rifle",
           "StrafeNoAimRifle_Left", "IdleSneak_Shotgun", "IdleNoAimRifle"]


def facing(w, left, right):
    v = w[left].translation - w[right].translation        # from the right one to the left one
    # forward is up x (left - right) for a character whose left is +side; only the angle's change matters here
    return math.degrees(math.atan2(v.y, v.x))


def diff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def frames(xa):
    last = max(max(list(t.R) + list(t.T) + [0]) for t in xa.tracks)
    step = max(1, int(xa.ticks_per_second / 30))
    return list(range(0, int(last) + 1, step))


def measure(src_dir, clips_dir, prefix, name):
    ours = os.path.join(clips_dir, prefix + name + ".x")
    van = os.path.join(src_dir, "Bob_" + name + ".x")
    if not (os.path.exists(ours) and os.path.exists(van)):
        return None
    xo, xv = xanim.read(ours), xanim.read(van)
    chest, hips, spine = [], [], []
    for t in frames(xo):
        wo, wv = pose.world(xo, pose.from_clip(xo, t)), pose.world(xv, pose.from_clip(xv, t))
        # the chest bone's own turn against vanilla's, about the vertical (its rotation difference's yaw)
        rd = wv["Bip01_Spine1"].to_quaternion().rotation_difference(wo["Bip01_Spine1"].to_quaternion())
        spine.append(abs(math.degrees(rd.to_euler('XYZ').z)))
        chest.append(abs(diff(facing(wo, "Bip01_L_UpperArm", "Bip01_R_UpperArm"),
                              facing(wv, "Bip01_L_UpperArm", "Bip01_R_UpperArm"))))
        hips.append(abs(diff(facing(wo, "Bip01_L_Thigh", "Bip01_R_Thigh"), facing(wv, "Bip01_L_Thigh", "Bip01_R_Thigh"))))
    return (sum(chest) / len(chest), max(chest), sum(spine) / len(spine), max(spine), sum(hips) / len(hips),
            max(hips))


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    src_dir, clips_dir, prefix = args[:3]
    for name in args[3:] or DEFAULT:
        m = measure(src_dir, clips_dir, prefix, name)
        if m is None:
            print("[facing] %-28s missing" % name)
        else:
            print("[facing] %-28s shoulders mean %5.1f max %5.1f   Spine1 yaw mean %5.1f max %5.1f   hips mean %4.1f "
                  "max %4.1f" % ((name,) + m))
