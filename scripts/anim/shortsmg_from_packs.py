"""
The short SMG stance's packs made from the shipped per-gun sets (one-off, 2026-10-28; CLAUDE.md "Animations are
generic"). System python3:

    python3 scripts/anim/shortsmg_from_packs.py <vanilla anims_X/Bob> <work dir>

The per-gun builds (compact_build.py / smg_reload.py output) lived in tmp/ on another machine, so their clips are taken
back out of the packs as shipped on 2026-10-27: the Uzi set (its stance and its reload: the pistol family), the MP5K's
reload (the H&K family) and the MP7's rack (the rear T-handle family). The UziT, MP5K and MP7 packs had their gun bone
moved by their guns' muzzle height (the old TURNED_SETS); that move is measured against vanilla's Bob_IdleAimRifle,
whose gun bone the sets' aim kept exactly, and undone, so every clip is in the rifle relation compact_build.py works
in. Then compact_pack.py packs them as "ShortSMG" (turned into the pistol orientation) into the main mod's anims_X/Bob.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.environ.get("TIEN_ANIM") or os.path.join(ROOT, "..", "TienInspectWeapon", "scripts", "anim"))
sys.path.insert(0, HERE)
import xanim  # noqa: E402
import compact_pack as CP  # noqa: E402

MAIN_BOB = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media/anims_X/Bob")
P93_BOB = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media/anims_X/Bob")
SOURCES = {"Uzi": MAIN_BOB, "MP5K": MAIN_BOB, "MP7": P93_BOB}
# reload family <- (source set, kinds)
FAMILIES = {"ShortSMGPistol": ("Uzi", CP.RELOADS), "ShortSMGHK": ("MP5K", CP.RELOADS),
            "ShortSMGRearT": ("MP7", ("Rack", "AimRack"))}


def split(set_name):
    """name -> single-clip .x text, from the set's packs."""
    out = {}
    for fn in sorted(os.listdir(SOURCES[set_name])):
        if not fn.startswith("GunsOfTien_Compact%s_Pack" % set_name):
            continue
        text = open(os.path.join(SOURCES[set_name], fn), encoding="latin-1").read().replace("\r\n", "\n")
        starts = [m.start() for m in re.finditer(r"^AnimationSet ", text, re.M)]
        head = text[:starts[0]]
        for i, s in enumerate(starts):
            e = starts[i + 1] if i + 1 < len(starts) else len(text)
            out[re.match(r"AnimationSet (\S+)", text[s:]).group(1)] = head + text[s:e]
    return out


def prop_matrix(xa, t):
    tr = next(x for x in xa.tracks if x.bone == "Bip01_Prop1")
    return xanim.srt_to_mat4(xanim.sample(tr, "S", t) or [1.0, 1.0, 1.0], xanim.sample(tr, "R", t),
                             xanim.sample(tr, "T", t))


def inv_rigid(m):
    r = [[m[j][i] for j in range(3)] for i in range(3)]
    t = [-sum(r[i][j] * m[j][3] for j in range(3)) for i in range(3)]
    return [r[0] + [t[0]], r[1] + [t[1]], r[2] + [t[2]], [0.0, 0.0, 0.0, 1.0]]


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def measured_shift(vanilla_bob, set_name, clips, work):
    """The set's gun-bone move: vanilla's aim gun bone^-1 x the set's, over the clip's keys (a pure move along the
    gun's Z; the turn and anything else would show as a spread)."""
    p = os.path.join(work, "_aim_%s.x" % set_name)
    open(p, "w", encoding="latin-1", newline="\n").write(clips["GunsOfTien_Compact%s_IdleAimRifle" % set_name])
    ours, van = xanim.read(p), xanim.read(os.path.join(vanilla_bob, "Bob_IdleAimRifle.x"))
    tr = next(x for x in van.tracks if x.bone == "Bip01_Prop1")
    ds = []
    for t in sorted(set(tr.R) | set(tr.T)):
        d = mul(inv_rigid(prop_matrix(van, t)), prop_matrix(ours, t))
        ds.append([d[i][3] for i in range(3)] + [max(abs(d[i][j] - (i == j)) for i in range(3) for j in range(3))])
    n = float(len(ds))
    mean = [sum(d[i] for d in ds) / n for i in range(3)]
    spread = max(max(abs(d[i] - mean[i]) for i in range(3)) for d in ds)
    rot = max(d[3] for d in ds)
    print("[shortsmg] %s: gun bone moved by %s (spread %.1e, rotation off by %.1e)"
          % (set_name, ["%.4f" % v for v in mean], spread, rot))
    if spread > 1e-4 or rot > 1e-4:
        raise SystemExit("%s: its aim's gun bone is not vanilla's moved along a line" % set_name)
    return mean


def write(text, out_path, name, d):
    tmp = out_path + ".src"
    open(tmp, "w", encoding="latin-1", newline="\n").write(text)
    xa = xanim.read(tmp)
    if any(abs(v) > 1e-6 for v in d):
        CP.shift_gun_bone(xa, [-v for v in d])
    xanim.write_clip(tmp, out_path, name, xa.tracks, xa.ticks_per_second)
    os.remove(tmp)


def main(vanilla_bob, work):
    set_dir, reload_dir = os.path.join(work, "set"), os.path.join(work, "reload")
    os.makedirs(os.path.join(set_dir, "clips"), exist_ok=True)
    os.makedirs(reload_dir, exist_ok=True)
    clips = {s: split(s) for s in SOURCES}
    shift = {s: measured_shift(vanilla_bob, s, clips[s], work) for s in SOURCES}
    names = [n for n in clips["Uzi"] if "_Reload" not in n]
    for n in names:
        write(clips["Uzi"][n], os.path.join(set_dir, "clips", n + ".x"), n, shift["Uzi"])
    with open(os.path.join(set_dir, "manifest.txt"), "w", newline="\n") as fh:
        fh.write("\n".join(names) + "\n")
    for fam, (src, kinds) in FAMILIES.items():
        for k in kinds:
            n = "GunsOfTien_Compact%s_Reload%s" % (fam, k)
            write(clips[src]["GunsOfTien_Compact%s_Reload%s" % (src, k)], os.path.join(reload_dir, n + ".x"), n,
                  shift[src])
    CP.main(set_dir, reload_dir, MAIN_BOB, "ShortSMG")


if __name__ == "__main__":
    main(*sys.argv[1:3])
