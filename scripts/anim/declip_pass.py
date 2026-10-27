"""
The final de-clip of a built clip (Blender 5.2; compact_build.py runs it on every clip it writes): no arm deeper in
the body than vanilla's own in that frame (or `contact` where vanilla's is clearer), no gun or gun part deeper than
`contact` (user, 2026-10-28: "we wanted to fix the clipping issues"; CLAUDE.md "No clipping"). The same steps as
rifle_hand.py's sets, on finished poses instead of vanilla's:

1. the gun (and the hands on it) moved straight out of the body, in rounds, each frame's move spread over RAMP frames;
2. the right elbow swung (one direction per clip, in the chest's terms), the hand kept;
3. the left elbow the same;
4. a left arm still in: the gun moved out with both hands;
5. what is left: the left arm eased toward vanilla's own (the hand slides along the gun).

Every re-solve keeps the arm's own elbow plane at zero swing (`solve_keep`), so a frame that needs nothing is not
changed and a swing fades in from the pose as built. Generic clips (gestures played through masks) take the gun bone
from the state underneath in game: there only the arms are fixed (2, 3, 5).
"""

import os
import sys

from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rifle_hand as RH  # noqa: E402  (TienInspectWeapon's scripts/anim on the path)
import compact_build as CB  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
from rig import rot_of  # noqa: E402

ARM_BONES = RH.LEFT_CHAIN + RH.RIGHT_CHAIN

# the right arm's swings: SWINGS mirrored (out is the character's right)
SWINGS_R = [v - rig.RIGHT.normalized() * 2.0 * v.dot(rig.RIGHT.normalized()) for v in RH.SWINGS]


def solve_keep(r, xa, q, side, target, extra=None):
    """`side`'s arm to `target` with its elbow in the plane it has in `q`, swung by `extra` (world)."""
    U, F, _ = rig.ARM[side]
    w = pose.world(xa, q)
    spine = rot_of(w["Bip01_Spine1"])
    elbow = w[F].translation - w[U].translation
    keep, r.swivel_scale = r.swivel_scale, 0.0
    r.solve_arm(q, side, target, pole_extra=elbow - spine @ r.pole_local[side] + (extra if extra is not None else Vector()))
    r.swivel_scale = keep


def move_gun(r, xa, q, off, left):
    """The gun moved by `off` (world) with the right hand on it, and the left hand when `left`."""
    q = pose.copy(q)
    w = pose.world(xa, q)
    W = w["Bip01_Prop1"]
    gr = W.inverted() @ w["Bip01_R_Hand"]
    gl = W.inverted() @ w["Bip01_L_Hand"]
    solve_keep(r, xa, q, "R", Matrix.Translation(off) @ W @ gr)
    w = pose.world(xa, q)
    W2 = w["Bip01_R_Hand"] @ gr.inverted()
    q["Bip01_Prop1"] = w["Bip01"].inverted() @ W2
    if left:
        solve_keep(r, xa, q, "L", W2 @ gl)
    return q


# the gun's moves tried, in the idle chest's terms (turned with the chest each frame): forward, forward and up, forward
# and to either side, up; with the way out of the body found from the buried vertices (`gun_escape`), which alone
# can run along the chest's surface (the Uzi idle's gun went 7 cm for 0.3 cm in)
GUN_DIRS = [rig.FWD, (rig.FWD + rig.UP).normalized(), (rig.FWD + rig.RIGHT).normalized(),
            (rig.FWD - rig.RIGHT).normalized(), rig.UP]
GUN_MOVE_MAX = 0.08
SWING_RAMP = 10                 # a swing fades in over this many frames (over RAMP, 0.4 came in within 3: a 5 cm pop)


def least_move(test, dirs, cap=GUN_MOVE_MAX):
    """Of `dirs` (world, unit), the shortest move that passes `test`, or None."""
    best = None
    for d in dirs:
        if d.length < 1e-9:
            continue
        top = cap if best is None else min(cap, best.length)
        if not test(d * top):
            continue
        k = top * RH.least(lambda t: test(d * top * t))
        if best is None or k < best.length:
            best = d * k
    return best


def side_depth(dc, q, side):
    return dc.depth(q)[0 if side == "L" else 1]


def clip_swing_keep(dc, r, xa, poses, limits, turns, side, dirs, only):
    """One swing direction for the clip (of `dirs`, idle-chest terms turned with the chest) for `side`, the hand kept
    where it is; per frame the least along it, spread over RAMP frames. Frames not in `only` are left alone."""
    aims = [pose.world(xa, q)[rig.ARM[side][2]] for q in poses]

    def depth(f, v):
        t = pose.copy(poses[f])
        solve_keep(r, xa, t, side, aims[f], v)
        return side_depth(dc, t, side)
    best = None
    need_any = [f for f in only if side_depth(dc, poses[f], side) > limits[f] + 0.0005]
    if not need_any:
        return [Vector() for _ in poses]
    for d in dirs:
        need = [0.0] * len(poses)
        missed = 0
        for f in need_any:
            dd = turns[f] @ d
            lo, got = 0.0, None
            tried = [(side_depth(dc, poses[f], side), 0.0)]
            for k in (0.025, 0.05, 0.1, 0.15, 0.2, 0.3, RH.SWING_MAX):
                dk = depth(f, dd * k)
                tried.append((dk, k))
                if dk <= limits[f] + 0.0005:
                    hi = k
                    for _ in range(3):
                        mid = (lo + hi) / 2
                        lo, hi = (lo, mid) if depth(f, dd * mid) <= limits[f] + 0.0005 else (mid, hi)
                    got = hi
                    break
                lo = k
            if got is None:
                # none clears: the swing that helps most, if it helps at all (the maximum taken blindly swung the right
                # elbow of the pain emote 0.4 for nothing; the gun's move below does the rest)
                missed += 1
                got = min(tried)[1]
            need[f] = got
        score = (missed, sum(need))
        if best is None or score < best[0]:
            best = (score, d, need)
    _, d, need = best
    out = [turns[f] @ d * k for f, k in enumerate(RH.spread(need, SWING_RAMP))]
    for f, v in enumerate(out):
        if v.length > 0 and f in only:
            solve_keep(r, xa, poses[f], side, aims[f], v)
    return out


def over_limits(xa, frames, poses, arm_ob, contact=0.008):
    """(left, right): how far each arm is over its limit at worst."""
    dc = CB.Declip(arm_ob, xa)
    over = [0.0, 0.0]
    for p, q in zip(frames, poses):
        v, d = dc.depth(p), dc.depth(q)
        over[0] = max(over[0], d[0] - max(contact, v[0]))
        over[1] = max(over[1], d[1] - max(contact, v[1]))
    return tuple(over)


def report(st, xa, frames, poses, arm_ob, tag, contact=0.008):
    """One line: how far each arm is over its limit at worst (a masked copy after its bones went back through the masks)."""
    dc = CB.Declip(arm_ob, xa)
    over = {"L": 0.0, "R": 0.0}
    for p, q in zip(frames, poses):
        v, d = dc.depth(p), dc.depth(q)
        over["L"] = max(over["L"], d[0] - max(contact, v[0]))
        over["R"] = max(over["R"], d[1] - max(contact, v[1]))
    print("[declip_pass] %s: over limits L %.3f R %.3f" % (tag, over["L"], over["R"]))


def run(st, r, xa, frames, poses, arm_ob, parts, generic, src_dir, contact=0.008):
    """The passes above on `poses` (changed in place and returned); prints one line of what it did."""
    dc = CB.Declip(arm_ob, xa)
    n = len(poses)
    vdep = [dc.depth(p) for p in frames]
    lim = {"L": [max(contact, d[0]) for d in vdep], "R": [max(contact, d[1]) for d in vdep]}
    glim = contact + 0.0005
    chests = [pose.world(xa, p)["Bip01_Spine1"].to_3x3() for p in frames]
    idle_chest = RH.chest_frame(src_dir).inverted()
    turns = [pose.world(xa, q)["Bip01_Spine1"].to_3x3() @ idle_chest for q in poses]
    on = [st.left_on(pose.world(xa, p)) > 0.5 for p in frames]
    moved = 0
    if parts and not generic:
        offs = [Vector() for _ in range(n)]
        base = [pose.copy(q) for q in poses]
        for _ in range(4):
            need, left = [], 0
            for f in range(n):
                add = Vector()
                d, way = RH.gun_escape(dc, xa, move_gun(r, xa, base[f], offs[f], on[f]), parts)
                if d > glim:
                    clear = lambda v: RH.gun_depth(dc, xa, move_gun(r, xa, base[f], offs[f] + v, on[f]), parts) <= glim
                    add = least_move(clear, [turns[f] @ g for g in GUN_DIRS] + [way])
                    if add is None:         # none clears: the escape's steps, as far as they go
                        add = Vector()
                        for _ in range(8):
                            d, way = RH.gun_escape(dc, xa, move_gun(r, xa, base[f], offs[f] + add, on[f]), parts)
                            if d <= glim or way.length == 0:
                                break
                            add = add + way * (d - glim + 0.003)
                left += add.length > 0
                need.append(chests[f].inverted() @ add)
            if os.environ.get("DECLIP_DEBUG"):
                print("[declip_pass] round: %d frames in, moves %s, after: %s" % (left, " ".join(
                    "%.3f" % v.length for v in need), " ".join("%.3f" % RH.gun_depth(
                        dc, xa, move_gun(r, xa, base[f], offs[f] + chests[f] @ need[f], on[f]), parts) for f in range(n))))
            if not left:
                break
            offs = [o + c @ v for o, c, v in zip(offs, chests, RH.spread_vectors(need))]
        for f in range(n):
            if offs[f].length > 0:
                poses[f] = move_gun(r, xa, base[f], offs[f], on[f])
                moved += 1
    everyone = list(range(n))
    sw_r = clip_swing_keep(dc, r, xa, poses, lim["R"], turns, "R", SWINGS_R, everyone)
    sw_l = clip_swing_keep(dc, r, xa, poses, lim["L"], turns, "L", RH.SWINGS, everyone)
    # 4. an arm still in (either: the pain emote's right hand holds the gun alone against the body): the gun moved out
    # with the hands on it, the least move that clears both arms and keeps the gun clear; in rounds from where each
    # frame is, spread over RAMP frames
    out_l = 0
    if parts and not generic:
        for _ in range(3):
            need, left = [], 0
            for f in range(n):
                add = Vector()
                dl, dr = dc.depth(poses[f])
                if dl > lim["L"][f] + 0.0005 or dr > lim["R"][f] + 0.0005:
                    side = "L" if dl - lim["L"][f] >= dr - lim["R"][f] else "R"
                    _, way = RH.arm_escape(dc, xa, poses[f], side, lim[side][f])

                    def clear(v):
                        t = move_gun(r, xa, poses[f], v, on[f])
                        d = dc.depth(t)
                        return d[0] <= lim["L"][f] + 0.0005 and d[1] <= lim["R"][f] + 0.0005 and \
                            RH.gun_depth(dc, xa, t, parts) <= glim
                    add = least_move(clear, [turns[f] @ g for g in GUN_DIRS] + [way]) or Vector()
                    left += add.length > 0
                need.append(chests[f].inverted() @ add)
            if not left:
                break
            for f, v in enumerate(RH.spread_vectors(need)):
                if v.length > 0:
                    poses[f] = move_gun(r, xa, poses[f], chests[f] @ v, on[f])
                    out_l += 1
    # 5. a right arm still in (the pain emote's, the gun alone in it across the body where vanilla's carries its rifle
    # low at the side): eased toward vanilla's own right arm by the least share, the gun going with the hand; not for
    # a masked copy, whose gun bone comes from the state underneath
    share_r = [0.0] * n
    if not generic:
        def toward_r(q, p, t):
            w = pose.world(xa, q)
            gr = w["Bip01_Prop1"].inverted() @ w["Bip01_R_Hand"]
            out = pose.copy(q)
            r.blend_local(out, p, RH.RIGHT_CHAIN, t)
            w2 = pose.world(xa, out)
            out["Bip01_Prop1"] = w2["Bip01"].inverted() @ (w2["Bip01_R_Hand"] @ gr.inverted())
            return out
        share_r = RH.spread([RH.least(lambda t: side_depth(dc, toward_r(q, p, t), "R") <= lim["R"][f] + 0.0005)
                             if side_depth(dc, q, "R") > lim["R"][f] + 0.0005 else 0.0
                             for f, (q, p) in enumerate(zip(poses, frames))], SWING_RAMP)
        for f, t in enumerate(share_r):
            if t > 0:
                poses[f] = toward_r(poses[f], frames[f], t)
    share = RH.spread([RH.release_share(dc, r, q, p, l) for q, p, l in zip(poses, frames, lim["L"])])
    for f, t in enumerate(share):
        if t > 0:
            poses[f] = RH.toward(r, poses[f], frames[f], t)
    # a frame the spread share still leaves in (the blend is not monotonic: the MP5K's heavy fall landing kept 1 cm
    # at a neighbour's share): its own share from where it is
    for f in range(n):
        if side_depth(dc, poses[f], "L") > lim["L"][f] + 0.0005:
            t = RH.release_share(dc, r, poses[f], frames[f], lim["L"][f])
            poses[f] = RH.toward(r, poses[f], frames[f], t)
            share[f] = max(share[f], t)
    worst = {"L": 0.0, "R": 0.0, "gun": 0.0}
    for f, q in enumerate(poses):
        dl, dr = dc.depth(q)
        if os.environ.get("DECLIP_DEBUG"):
            print("[declip_pass] f%d on %d L %.3f/%.3f R %.3f/%.3f swing L %.3f R %.3f share %.2f" % (
                f, on[f], dl, lim["L"][f], dr, lim["R"][f], sw_l[f].length, sw_r[f].length, share[f]))
        worst["L"] = max(worst["L"], dl - lim["L"][f])
        worst["R"] = max(worst["R"], dr - lim["R"][f])
        if parts and not generic:
            worst["gun"] = max(worst["gun"], RH.gun_depth(dc, xa, q, parts))
    print("[declip_pass] gun moved %d, right swing %d, left swing %d, gun out for the arms %d, right released %d "
          "(largest %.2f), released %d (largest %.2f); over limits: L %.3f R %.3f, guns %.3f" % (
              moved, sum(1 for v in sw_r if v.length > 0), sum(1 for v in sw_l if v.length > 0), out_l,
              sum(1 for t in share_r if t > 0), max(share_r) if share_r else 0.0,
              sum(1 for t in share if t > 0), max(share) if share else 0.0, worst["L"], worst["R"], worst["gun"]))
    return poses
