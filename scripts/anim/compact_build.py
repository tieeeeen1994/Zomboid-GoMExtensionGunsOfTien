"""
Builds the compact SMG stance's clips (user, 2026-10-23, "Option B", then "produce all the animations"; CLAUDE.md
"Compact SMG stance") from every vanilla clip played while a two-handed gun is held, frame by frame (Blender 5.2,
headless; TienInspectWeapon's rig).

    blender -b --factory-startup -P scripts/anim/compact_build.py -- <vanilla anims_X/Bob> <vanilla AnimSets> <out_dir>
        [set ...] [--clips Bob_IdleRifle,...] [--preview] [--no-pack]

Sets (one Gunworks grip animId each): Uzi (the Uzi, the Mini Uzi, the MP7s with the foregrip folded or none), MP7
(the MP7A1 with its foregrip unfolded), MP5K (GoM's). The clip list is the vanilla inventory
(compact_animsets.firearm_clips: 240 in 42.21). Each clip is built into <out_dir>/<set>/clips/<name>.x, its body
clearance printed; then the set is packed (PACK clips a file, one Bob mesh each: the game reads every AnimationSet
of a file as a clip) into <out_dir>/<set>/GunsOfTien_Compact<Set>_Pack<n>.x, with <out_dir>/<set>/manifest.txt
listing the clip names. --preview renders every 3rd frame with the set's gun into <out_dir>/<set>/prev_<clip>/.

Per frame:
- aim clips (named as aimed: IdleAim / WalkAim / StrafeAim / WalkBwdAim / AttackRifle / Shove, and the vehicle aim
  clips): every bone and the gun exactly as vanilla, only the left arm solved onto the set's support place (user:
  "copy the right hand style in the vanilla one and just adjust the left arm"), the hand turned per set (AIM_TURN).
- every other clip, by how aimed vanilla's gun is in that frame (its place relative to the chest, between vanilla's
  carried idle place and its aimed place): carried frames take the approved hold (idle_down.py ID_M, rigid with the
  chest plus vanilla's own gun drift relative to it, twist 15, lean 2, look 0.15, both arms solved with the pistol
  idle's hand relation), aimed frames the aim rule above, and frames between both poses blended bone by bone, the gun
  put back in the right hand with the blended hand relation (raising, lowering, sprinting into an aim, flails).
- generic clips (no gun in the name: gestures, pains, signals, the 2H melee and 1H ones, played by the rifle nodes
  through bone masks that take the gun bone from the state underneath): always the plain hold, no drift.
- the left hand stays on the gun only while vanilla's is on its rifle (its place relative to the rifle near vanilla's
  idle or aim hold): where vanilla's leaves it (emotes, scratching, catching a fall) it keeps vanilla's motion.
- Declip: elbows swung outward, then a carried gun moved forward, then the left arm eased toward vanilla's own (clear
  of the body) by the least amount that brings it out, until the arms are at contact level.
"""

import math
import os
import re
import sys

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_stance as C  # noqa: E402  (puts TienInspectWeapon's scripts/anim on the path)
import compact_animsets as CA  # noqa: E402
import hold_preview as HP  # noqa: E402
import idle_down as I  # noqa: E402
import clearance  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import x_export  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
import xanim  # noqa: E402
from rig import ch  # noqa: E402

SETS = {
    # support place (upright weapon space), the left hand's turn in the idle and the aim, the gun drawn in previews,
    # the idle hold's shift towards the body (idle_down.py ID_MC, approved: "the closer is good now")
    "Uzi": dict(support=Vector((0.0, 0.130, -0.014)), idle_turn=(30, 0, 0), aim_turn=(0, 0, 0), gun="uzi",
                closer=ch(0.0, 0.0, -0.04)),
    "MP7": dict(support=Vector((0.0, 0.142, -0.040)), idle_turn=(30, -15, 0), aim_turn=(0, 0, 0), gun="mp7",
                closer=ch(0.0, 0.0, -0.04)),
    "MP5K": dict(support=Vector((0.0, 0.180, -0.032)), idle_turn=(45, -15, 0), aim_turn=(0, -15, 0), gun="mp5k",
                 closer=ch(0.03, 0.0, -0.04)),
}

# the approved idle hold (idle_down.py, ID_M), on vanilla's rifle idle body
HOLD = dict(pos=ch(0.02, 0.64, 0.10), along=ch(-0.77, -0.61, 0.20), top=-(ch(0.25, -1.0, 0.2)), look=0.15, lean=2,
            aux=0.0, twist=15)
HOLD_S = dict(look=0.15, lean=2, aux=0.0, support=1.0, elbow=0.0, twist=15)

AIM_NAME = re.compile(r"IdleAim|WalkAim|StrafeAim|WalkBwdAim|AttackRifle|Shove_Rifle")
PACK = 40
# vanilla's rifle moves out from the chest while walking (4.5 cm) and running (10-12 cm, sneaking too) and up (walk
# 5 cm, run 14, sneaking 20): the hold keeps this much of that drift (user: "when walking and running, let's keep the
# gun closer still"); with all the rise the crossing left arm meets the chest and the de-clip pushes the gun back out
DRIFT_OUT_KEEP = float(os.environ.get("COMPACT_DRIFT_OUT_KEEP", "0.2"))
DRIFT_UP_KEEP = float(os.environ.get("COMPACT_DRIFT_UP_KEEP", "0.4"))
# ...but not crouched: the chest leans 53-85 degrees there, and vanilla's upward drift is what keeps the gun out in
# front of the hips; with less of it the gun went into the belly and the left forearm crossed over it (user: "The
# crouch Short SMG stance have a bad left arm")
CROUCH_NAME = re.compile(r"Sneak|Sgun")
# ...and not all of the outward part either: with all of it the arms reached their full length (shoulder to hand
# 0.27 of 0.274), where a hand moving 1 cm swings the elbow 3 cm, which read as a snap in the sneak run's cycle;
# 30 % keeps them bent as vanilla's (0.17-0.21, vanilla 0.14-0.18)
CROUCH_KEEP = tuple(float(v) for v in os.environ.get("COMPACT_CROUCH_KEEP", "0.3,1.0").split(","))
CROUCH_TURN = float(os.environ.get("COMPACT_CROUCH_TURN", "1.0"))
CROUCH_SEARCH = os.environ.get("COMPACT_CROUCH_SEARCH", "1") == "1"
TURN_SMOOTH = float(os.environ.get("COMPACT_TURN_SMOOTH", "0.01"))        # cost per degree squared of a frame's turn against each neighbour's (5 degrees: 0.25)
TURN_MAX = 40.0
SMOOTH_ELBOWS = os.environ.get("COMPACT_SMOOTH_ELBOWS", "1") == "1"
CONTACT = 0.022       # an arm resting on the body reads up to ~0.02 (vanilla's idle); deeper is in


def out_name(set_name, clip):
    return "GunsOfTien_Compact%s_%s" % (set_name, clip[4:] if clip.startswith("Bob_") else clip)


def clip_ticks(xa):
    last = 0
    for tr in xa.tracks:
        for keys in (tr.R, tr.S, tr.T):
            if keys:
                last = max(last, max(keys))
    return last


def frames_of(xa):
    step = xa.ticks_per_second // 30
    n = clip_ticks(xa) // step
    return [pose.from_clip(xa, f * step) for f in range(n + 1)]


def no_limit(r):
    """The rig without the right wrist's easing: the hold is already a landed (eased) pose, and easing it again per
    frame would move the gun off it a little each frame."""
    solve = r.solve_arm
    r.solve_arm = lambda p, side, target, pole_extra=Vector(), limit=0.0: solve(p, side, target, pole_extra, 0.0)
    return r


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def blend_mat(a, b, t):
    qa, qb = a.to_quaternion(), b.to_quaternion()
    if qa.dot(qb) < 0:
        qb.negate()
    return Matrix.LocRotScale(a.translation.lerp(b.translation, t), qa.slerp(qb, t), None)


class Stance:
    """The per-set pieces shared by every clip: the idle hold relative to the chest, both left-hand placements, the
    pistol hand relation, and vanilla's own carried / aimed rifle places to judge each frame by."""

    def __init__(self, src_dir, set_name):
        spec = SETS[set_name]
        xa, r = I.x_rig(src_dir)
        self.grip_idle = r.grip_r.copy()
        self.lgrip_idle = C.grip_on(r.support_base, spec["support"], spec["idle_turn"])
        r.warnings.clear()
        p = r.build([rig.Key(0, support=1, lgrip=self.lgrip_idle, **HOLD)], 1, breath=(0, None))[0]
        w0 = pose.world(xa, r.base)
        # moved straight in (no turn), in the character's frame: 4 cm back is the most before the gun's rear, high
        # on the right chest, goes into it
        self.hold_rel = w0["Bip01_Spine1"].inverted() @ Matrix.Translation(spec["closer"]) \
            @ pose.world(xa, p)["Bip01_Prop1"]
        self.gun_idle = w0["Bip01_Spine1"].inverted() @ w0["Bip01_Prop1"]
        self.left_idle = w0["Bip01_Prop1"].inverted() @ w0["Bip01_L_Hand"]
        # the character's forward in the chest bone's frame (its local axes are not the character's)
        self.fwd_local = (w0["Bip01_Spine1"].to_3x3().inverted() @ rig.FWD).normalized()
        self.up_local = (w0["Bip01_Spine1"].to_3x3().inverted() @ rig.UP).normalized()
        self.drift_keep = (DRIFT_OUT_KEEP, DRIFT_UP_KEEP)       # per clip (build_clip)
        self.follow_turn = 0.0
        self.turn_search = False
        self.turn_prev = (0.0, 0.0, 0.0)
        self.turn_fixed = None
        xa_a = xanim.read(os.path.join(src_dir, "Bob_IdleAimRifle.x"))
        wa = pose.world(xa_a, pose.from_clip(xa_a, 0))
        self.gun_aim = wa["Bip01_Spine1"].inverted() @ wa["Bip01_Prop1"]
        self.left_aim = wa["Bip01_Prop1"].inverted() @ wa["Bip01_L_Hand"]
        self.lgrip_aim = C.grip_on(self.left_aim, spec["support"], spec["aim_turn"])

    def hold_at(self, xa, w, generic=False):
        """The idle hold's gun in a frame: rigid with the chest, plus the vanilla gun's own drift relative to it (not
        for a generic clip, whose gun bone is wherever an empty hand is: the game takes the gun bone from the state
        underneath there, so the right hand must stay on the plain hold)."""
        drift = Vector()
        if not generic:
            drift = (w["Bip01_Spine1"].inverted() @ w["Bip01_Prop1"]).translation - self.gun_idle.translation
            keep_out, keep_up = self.drift_keep
            out = drift.dot(self.fwd_local)
            if out > 0:
                drift -= self.fwd_local * out * (1.0 - keep_out)
            up = drift.dot(self.up_local)
            if up > 0:
                drift -= self.up_local * up * (1.0 - keep_up)
        hold = self.hold_rel
        if not generic and self.follow_turn > 0:
            # vanilla's gun turns against the chest's lean; turn ours by as much (in the chest's frame, about its own
            # origin)
            turn = self.vanilla_turn(w)
            turn = Quaternion().slerp(turn, self.follow_turn)
            hold = Matrix.Translation(hold.translation) @ turn.to_matrix().to_4x4() @ hold.to_3x3().to_4x4()
        return w["Bip01_Spine1"] @ Matrix.Translation(drift) @ hold

    def vanilla_turn(self, w):
        rel = w["Bip01_Spine1"].inverted() @ w["Bip01_Prop1"]
        return (rel.to_quaternion() @ self.gun_idle.to_quaternion().inverted()).normalized()

    def aimed(self, w):
        """0 = vanilla's rifle carried, 1 = aimed: its place relative to the chest between the idle and aim places,
        and its muzzle the aim's way (port arms in the backing-up carry sits near the aim place, muzzle up)."""
        rel = w["Bip01_Spine1"].inverted() @ w["Bip01_Prop1"]
        g = rel.translation
        di = (g - self.gun_idle.translation).length
        da = (g - self.gun_aim.translation).length
        place = smooth((di / max(1e-6, di + da) - 0.3) / 0.4)
        along = (rel.to_3x3() @ Vector((0, 1, 0))).normalized()
        aim_along = (self.gun_aim.to_3x3() @ Vector((0, 1, 0))).normalized()
        return place * smooth((along.dot(aim_along) - 0.75) / 0.2)

    def left_on(self, w):
        """1 while vanilla's left hand holds its rifle (near its idle or aim hold), 0 once it has let go."""
        l = (w["Bip01_Prop1"].inverted() @ w["Bip01_L_Hand"]).translation
        d = min((l - self.left_idle.translation).length, (l - self.left_aim.translation).length)
        return 1.0 - smooth((d - 0.05) / 0.06)


class Declip:
    """Each frame checked against the body (clearance.Body on the clip's armature): an arm deeper than CONTACT has its
    elbow swung outward step by step; a carried frame still in then moves its gun forward, away from the chest."""

    def __init__(self, arm_ob, xa):
        self.arm_ob, self.xa = arm_ob, xa
        self.body = clearance.Body(arm_ob)
        self.fixed = 0

    def depth(self, q):
        x_import.apply_pose(self.arm_ob, pose.world(self.xa, q))
        d = self.body.now()
        return d["L"], d["R"]

    def release(self, r, q, free):
        """Still in after the elbow swings and the gun moves: ease the left arm toward vanilla's own (`free`, clear
        of the body there) by the least amount that brings it out (bisection, 6 steps)."""
        dl, _ = self.depth(q)
        if dl <= CONTACT:
            return q
        solved = pose.copy(q)
        lo, hi = 0.0, 1.0
        best = None
        for _ in range(6):
            mid = (lo + hi) / 2
            t = pose.copy(solved)
            for b in rig.ARM["L"]:
                t[b] = free[b].copy()
            t2 = pose.copy(solved)
            r.blend_local(t2, t, rig.ARM["L"], mid)
            d, _ = self.depth(t2)
            self.fixed += 1
            if d <= CONTACT:
                best, hi = t2, mid
            else:
                lo = mid
        return best if best is not None else q

    def arms(self, r, q, lgrip, left=True):
        dl, dr = self.depth(q)
        for k in range(1, 9):
            if (dl <= CONTACT or not left) and dr <= CONTACT:
                break
            W = pose.world(self.xa, q)["Bip01_Prop1"]
            if left and dl > CONTACT:
                r.solve_arm(q, "L", W @ lgrip, pole_extra=rig.UP * -0.05 - rig.RIGHT * 0.025 * k)
            if dr > CONTACT:
                r.solve_arm(q, "R", W @ r.grip_r.inverted(), pole_extra=rig.UP * -0.05 + rig.RIGHT * 0.025 * k)
                w = pose.world(self.xa, q)
                q["Bip01_Prop1"] = w["Bip01"].inverted() @ (w["Bip01_R_Hand"] @ r.grip_r)
            dl, dr = self.depth(q)
            self.fixed += 1
        return q, max(dl if left else 0.0, dr)


def left_to(r, xa, q, free, lgrip, on):
    """The left arm onto the gun at lgrip, blended back to vanilla's own left arm (`free`) by 1 - on."""
    if on <= 0.0:
        for b in rig.ARM["L"]:
            q[b] = free[b].copy()
        return q
    W = pose.world(xa, q)["Bip01_Prop1"]
    r.solve_arm(q, "L", W @ lgrip, pole_extra=rig.UP * -0.05)
    if on < 1.0:
        solved = pose.copy(q)
        for b in rig.ARM["L"]:
            q[b] = free[b].copy()
        r.blend_local(q, solved, rig.ARM["L"], on)
    return q


def settle_turn(st, r, xa, p, f, n, on, W, s, extra=None, steps=(8.0, 4.0, 2.0)):
    """The gun turned about its grip (X, Y, Z of its own frame, degrees) to where both wrists are most natural
    (rig.wrist_cost, the left only while it holds the gun), a little cost for every degree away from the hold and
    for a hand falling short: a local search from the previous frame's turn (steps 8, 4, 2), so the turn moves
    smoothly through a clip."""
    def solve(ang):
        Wt = W @ Euler([math.radians(a) for a in ang], 'XYZ').to_matrix().to_4x4()
        r.warnings.clear()
        q = r.pose_for(Wt, s, f, (0, None), n)
        q = left_to(r, xa, q, p, st.lgrip_idle, on)
        cost = r.wrist_cost(q, "R") + (r.wrist_cost(q, "L") if on > 0.5 else 0.0)
        cost += 0.3 * sum((a / 30.0) ** 2 for a in ang) + 5.0 * len(r.warnings)
        if extra is not None:
            cost += extra(ang)
        return cost, Wt, q
    best_ang = list(st.turn_prev)
    best = solve(best_ang)
    for step in steps:
        moved = True
        while moved:
            moved = False
            for i in range(3):
                for d in (step, -step):
                    ang = list(best_ang)
                    ang[i] = max(-TURN_MAX, min(TURN_MAX, ang[i] + d))
                    if ang == best_ang:
                        continue
                    c = solve(ang)
                    if c[0] < best[0] - 1e-4:
                        best, best_ang, moved = c, ang, True
    st.turn_prev = tuple(best_ang)
    return best[1], best[2]


def plan_turns(st, r, xa, frames, n):
    """settle_turn over the whole clip twice (the second pass starts where the first ended, so a looping clip's
    seam meets), then the turns smoothed (circularly for a loop: vanilla's first and last frames alike), so the gun
    never jumps when the search moves from one comfortable turn to another."""
    s = dict(HOLD_S, support=0.0)
    turns = []
    for _ in range(2):
        turns = []
        for f, p in enumerate(frames):
            r.base = p
            w = pose.world(xa, p)
            settle_turn(st, r, xa, p, f, n, st.left_on(w), st.hold_at(xa, w), s)
            turns.append(st.turn_prev)
    a, b = pose.world(xa, frames[0]), pose.world(xa, frames[-1])
    loop = all((a[k].translation - b[k].translation).length < 1e-3 for k in ("Bip01_Spine1", "Bip01_Prop1",
                                                                           "Bip01_R_Hand", "Bip01_L_Hand"))
    m = len(turns)
    turns = smooth_turns(turns, loop, (1, 2, 3, 4, 3, 2, 1), 2)
    # The wrists barely prefer one turn over a nearby one, so the search drifts one way through a cycle and jumps
    # back at a loop's seam (the sneak run: 4 -> 22 degrees, then back in one frame; smoothed, a quick swing at the
    # end of every cycle). So the turns are then settled together: each frame's search also pays for differing from
    # its neighbours (circularly for a loop), sweeping back and forth until it holds.
    last = m - 1 if loop else m             # a loop's last frame repeats its first
    turns = list(turns)
    for sweep in range(6):
        order = range(last) if sweep % 2 == 0 else range(last - 1, -1, -1)
        for f in order:
            nb = []
            if f > 0 or loop:
                nb.append(turns[(f - 1) % last] if loop else turns[f - 1])
            if f < last - 1 or loop:
                nb.append(turns[(f + 1) % last] if loop else turns[f + 1])
            p = frames[f]
            r.base = p
            w = pose.world(xa, p)
            st.turn_prev = turns[f]
            settle_turn(st, r, xa, p, f, n, st.left_on(w), st.hold_at(xa, w), s,
                        extra=lambda ang, nb=nb: TURN_SMOOTH * sum((x - y) ** 2 for t in nb for x, y in zip(ang, t)),
                        steps=(4.0, 2.0, 1.0))
            turns[f] = st.turn_prev
    if loop:
        turns[-1] = turns[0]
    return smooth_turns(turns, loop, (1, 2, 1), 1)


def is_loop(xa, frames):
    """vanilla's first and last frames alike (a looping clip)."""
    a, b = pose.world(xa, frames[0]), pose.world(xa, frames[-1])
    return all((a[k].translation - b[k].translation).length < 1e-3 for k in ("Bip01_Spine1", "Bip01_Prop1",
                                                                           "Bip01_R_Hand", "Bip01_L_Hand"))


def smooth_turns(turns, loop, kernel, times):
    m = len(turns)
    for _ in range(times):
        out = []
        for i in range(m):
            acc, wsum = [0.0, 0.0, 0.0], 0.0
            for k, wk in enumerate(kernel):
                j = i + k - len(kernel) // 2
                if loop:
                    j %= (m - 1)            # the last frame repeats the first
                elif not 0 <= j < m:
                    continue
                acc = [x + wk * y for x, y in zip(acc, turns[j])]
                wsum += wk
            out.append(tuple(x / wsum for x in acc))
        if loop:
            out[-1] = out[0]
        turns = out
    return turns


def carried_pose(st, r, xa, p, f, n, on, dc, generic=False):
    r.base = p
    w = pose.world(xa, p)
    W = st.hold_at(xa, w, generic)
    s = dict(HOLD_S, support=0.0)
    if st.turn_fixed is not None and not generic:
        W = W @ Euler([math.radians(a) for a in st.turn_fixed[f]], 'XYZ').to_matrix().to_4x4()
        q = r.pose_for(W, s, f, (0, None), n)
        q = left_to(r, xa, q, p, st.lgrip_idle, on)
    elif st.turn_search and not generic:
        W, q = settle_turn(st, r, xa, p, f, n, on, W, s)
    else:
        q = r.pose_for(W, s, f, (0, None), n)
        q = left_to(r, xa, q, p, st.lgrip_idle, on)
    if dc is None:
        return q
    q, d = dc.arms(r, q, st.lgrip_idle, on > 0.5)
    fwd = (w["Bip01_Spine1"].to_3x3() @ st.fwd_local).normalized()
    step = 0
    while d > CONTACT and step < 10:
        step += 1
        q = r.pose_for(Matrix.Translation(fwd * 0.01 * step) @ W, s, f, (0, None), n)
        q = left_to(r, xa, q, p, st.lgrip_idle, on)
        q, d = dc.arms(r, q, st.lgrip_idle, on > 0.5)
    if d > CONTACT:
        q = dc.release(r, q, p)
    return q


def aim_pose(st, r, xa, p, on, dc):
    q = left_to(r, xa, pose.copy(p), p, st.lgrip_aim, on)
    if dc is not None:
        q, d = dc.arms(r, q, st.lgrip_aim, on > 0.5)
        if d > CONTACT:
            q = dc.release(r, q, p)
    return q


def frame_pose(st, r, xa, p, f, n, aim_clip, dc, generic=False):
    w = pose.world(xa, p)
    on = st.left_on(w)
    if generic:
        return carried_pose(st, r, xa, p, f, n, on, dc, True)
    a = 1.0 if aim_clip else st.aimed(w)
    if a >= 0.999:
        return aim_pose(st, r, xa, p, on, dc)
    if a <= 0.001:
        return carried_pose(st, r, xa, p, f, n, on, dc)
    qi = carried_pose(st, r, xa, p, f, n, on, None)
    qa = aim_pose(st, r, xa, p, on, None)
    q = pose.copy(qi)
    r.blend_local(q, qa, [b for b in q if b != "Bip01_Prop1"], a)
    wi, wa = pose.world(xa, qi), pose.world(xa, qa)
    rel = blend_mat(wi["Bip01_R_Hand"].inverted() @ wi["Bip01_Prop1"],
                    wa["Bip01_R_Hand"].inverted() @ wa["Bip01_Prop1"], a)
    wq = pose.world(xa, q)
    q["Bip01_Prop1"] = wq["Bip01"].inverted() @ (wq["Bip01_R_Hand"] @ rel)
    lg = blend_mat(st.lgrip_idle, st.lgrip_aim, a)
    q = left_to(r, xa, q, p, lg, on)
    if dc is not None:
        q, d = dc.arms(r, q, lg, on > 0.5)
        if d > CONTACT:
            q = dc.release(r, q, p)
    return q


def build_clip(src_dir, out_dir, set_name, st, clip, aim_clip, preview=False, generic=False):
    path = os.path.join(src_dir, clip + ".x")
    xa = xanim.read(path, with_mesh=True)
    frames = frames_of(xa)
    n = len(frames) - 1
    r = no_limit(rig.Rig(xa, frames[0], poi=0.6, top=1, rest=x_import.rest_matrices(xa)))
    r.grip_r = st.grip_idle.copy()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm_ob = x_import.load(path)
    dc = Declip(arm_ob, xa)
    crouch = bool(CROUCH_NAME.search(clip))
    st.drift_keep = CROUCH_KEEP if crouch else (DRIFT_OUT_KEEP, DRIFT_UP_KEEP)
    st.follow_turn = CROUCH_TURN if crouch else 0.0
    st.turn_search = crouch and CROUCH_SEARCH
    st.turn_prev = (0.0, 0.0, 0.0)
    st.turn_fixed = None
    if st.turn_search and not generic:
        st.turn_fixed = plan_turns(st, r, xa, frames, n)
    poses = []
    swings = []
    for f, p in enumerate(frames):
        r.warnings.clear()
        r.swivel_hint = {}
        k = len(r.swivels)
        poses.append(frame_pose(st, r, xa, p, f, n, aim_clip, dc, generic))
        last = {}
        for side, deg in r.swivels[k:]:
            last[side] = deg
        swings.append(last)
        del r.swivels[k:]
    if crouch and SMOOTH_ELBOWS:
        # each frame's elbow swing is the best of a cost that is often flat, so it hops (a run's upper arm turned
        # 13-14 degrees in one frame, at its loop): solved again with the swings smoothed over the clip as hints
        loop = is_loop(xa, frames)
        hints = {}
        for side in ("L", "R"):
            seq = [sw.get(side) for sw in swings]
            if any(v is None for v in seq):
                continue
            hints[side] = [t[0] for t in smooth_turns([(v, 0.0, 0.0) for v in seq], loop, (1, 2, 3, 2, 1), 2)]
        if hints:
            poses = []
            for f, p in enumerate(frames):
                r.warnings.clear()
                r.swivel_hint = {side: seq[f] for side, seq in hints.items()}
                poses.append(frame_pose(st, r, xa, p, f, n, aim_clip, dc, generic))
            r.swivel_hint = {}
    name = out_name(set_name, clip)
    d = os.path.join(out_dir, set_name, "clips")
    os.makedirs(d, exist_ok=True)
    pose.bake(arm_ob, xa, poses, name)
    x_export.export(path, os.path.join(d, name + ".x"), name, arm_ob)
    gun = SETS[set_name]["gun"]
    spec = C.GUNS[gun]
    parts = []
    for part_path, node, mat in HP.GUNS[gun]["parts"]:
        before = set(bpy.data.objects)
        HP.load_part(arm_ob, part_path, node, (C.FLIP @ mat) if (spec["flip"] and mat is not None) else
                     (C.FLIP if spec["flip"] else mat))
        parts += list(set(bpy.data.objects) - before)
    body = clearance.Body(arm_ob)
    worst = body.check(range(0, n + 1, 3), {"gun": parts})
    print("[build] %s %s (%s, %d frames, %d declip steps): %s" % (
        set_name, clip, "generic" if generic else "aim" if aim_clip else "auto", n + 1, dc.fixed,
        ", ".join("%s %.3f@%d" % (k, v[0], v[1]) for k, v in sorted(worst.items()))))
    if preview:
        scene = bpy.context.scene
        x_preview.setup_render(scene)
        scene.render.resolution_x = scene.render.resolution_y = 420
        pd = os.path.join(out_dir, set_name, "prev_" + clip)
        os.makedirs(pd, exist_ok=True)
        cams = {}
        for view, (loc, tgt) in HP.VIEWS.items():
            cam = x_preview.camera("Cam_" + view, loc, tgt)
            cam.data.ortho_scale = 0.9
            cams[view] = cam
        for f in range(0, n + 1, 3):
            scene.frame_set(f)
            for view, cam in cams.items():
                scene.camera = cam
                scene.render.filepath = os.path.join(pd, "%s_%03d.png" % (view, f))
                bpy.ops.render.render(write_still=True)
    return name


def pack(out_dir, set_name, names):
    """PACK clips a file: the first clip's whole text (templates, frames, Bob's mesh, its AnimationSet), the others'
    AnimationSets appended (from their `^AnimationSet` line)."""
    d = os.path.join(out_dir, set_name)
    for old in os.listdir(d):
        if old.endswith(".x"):
            os.remove(os.path.join(d, old))
    files = []
    for i in range(0, len(names), PACK):
        chunk = names[i:i + PACK]
        texts = [open(os.path.join(d, "clips", nm + ".x"), encoding="latin-1").read() for nm in chunk]
        out = texts[0].rstrip() + "\n"
        for t in texts[1:]:
            out += "\n" + t[re.search(r"^AnimationSet ", t, re.M).start():].rstrip() + "\n"
        fn = "GunsOfTien_Compact%s_Pack%d.x" % (set_name, i // PACK + 1)
        with open(os.path.join(d, fn), "w", encoding="latin-1") as fh:
            fh.write(out)
        files.append(fn)
    with open(os.path.join(d, "manifest.txt"), "w") as fh:
        fh.write("\n".join(names) + "\n")
    print("[pack] %s: %d clips in %s" % (set_name, len(names), ", ".join(files)))


GUN_NAME = re.compile(r"Rifle|Shotgun|SGun|Sgun|Firearm", re.I)


def is_generic(clip):
    """Shared with other weapon classes (gestures, pains, signals, the 2H melee and 1H ones): its gun bone follows an
    empty or other hand, and the rifle nodes that play it take the gun bone from the state underneath."""
    return not GUN_NAME.search(clip)


def is_aim_clip(clip, where):
    return bool(AIM_NAME.search(clip)) or all(w.startswith("player-vehicle") for w in where)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    preview, no_pack = "--preview" in args, "--no-pack" in args
    only = None
    if "--clips" in args:
        only = args[args.index("--clips") + 1].split(",")
    args = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] != "--clips")]
    src_dir, animsets, out_dir = args[0], args[1], args[2]
    inventory = CA.firearm_clips(animsets)
    clips = sorted(inventory) if only is None else only
    for set_name in args[3:] or list(SETS):
        st = Stance(src_dir, set_name)
        names = []
        for clip in clips:
            names.append(build_clip(src_dir, out_dir, set_name, st, clip, is_aim_clip(clip, inventory.get(clip, [])),
                                    preview, is_generic(clip)))
        if not no_pack and only is None:
            pack(out_dir, set_name, names)
