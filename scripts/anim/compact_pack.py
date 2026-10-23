"""
Packs the compact SMG stance's clips for shipping (system python3):

    python3 scripts/anim/compact_pack.py <set dir with clips/ and manifest.txt> <reload dir> <out anims_X/Bob> <Set>

Every clip of the set (compact_build.py's manifest) plus its four reload clips (smg_reload.py's compact specs:
GunsOfTien_Compact<Set>_Reload<Unload|Load|Rack|AimRack>.x) is rewritten with every key kept (only runs of
identical values dropped, as vanilla does; LOSSY names clips for the old lossy reduction, which made looping clips
jump for a frame in game) and packed PACK to a file behind one Bob mesh: the game reads every AnimationSet of a .x
file as a clip (ImportedSkeleton / ModelManager, checked with the game's importer), so 248 clips cost ~26 MB instead
of ~45 MB as single files. Old GunsOfTien_Compact<Set>_*.x files in the output folder are removed first.

Sets of guns modelled upside down (CA.TURNED_SETS) get their gun bone moved by twice the muzzle's height off the model's
Y axis, the other way from the offset CompactStance.lua gives the guns' Bip01_Prop1 point: the guns are drawn where they
were (turned about their own bore instead of the model's Y axis), and the muzzle the game shoots from (the bone and the
`muzzle` point, without the turn) is the drawn muzzle. CA.SOURCE_SET packs one built set under another name (UziT).
"""

import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.environ.get("TIEN_ANIM") or os.path.join(ROOT, "..", "TienInspectWeapon", "scripts", "anim"))
import xanim  # noqa: E402

sys.path.insert(0, HERE)
import compact_animsets as CA  # noqa: E402

PACK = 40
# Clip names packed with lossy key reduction (regex; none by default). Reduced clips played a one-frame jump of the
# arms and gun once a cycle in game, at the loop point (the sneak run; seen in a recording on 2026-10-23, gone with
# every key kept, vanilla's own clips keep every key), for a cause not found in the game's code: keys are kept.
LOSSY = os.environ.get("COMPACT_PACK_LOSSY")
RELOADS = ("Unload", "Load", "Rack", "AimRack")


def shift_gun_bone(xa, d):
    """Bip01_Prop1 moved by d in its own frame (W' = W @ T(d)) on every key: local T' = T + R (S * d), sampled at
    the union of its R / S / T key times."""
    tr = next(t for t in xa.tracks if t.bone == "Bip01_Prop1")
    times = sorted(set(tr.R) | set(tr.S) | set(tr.T))
    out = {}
    for t in times:
        sc = xanim.sample(tr, "S", t) or [1.0, 1.0, 1.0]
        w, x, y, z = xanim.sample(tr, "R", t)
        r = xanim.quat_to_mat3(w, -x, -y, -z)          # the file stores the conjugate
        v = [sc[i] * d[i] for i in range(3)]
        base = xanim.sample(tr, "T", t)
        out[t] = [base[i] + sum(r[i][j] * v[j] for j in range(3)) for i in range(3)]
    tr.T = out
    tr.R = {t: xanim.sample(tr, "R", t) if t not in tr.R else tr.R[t] for t in times}


def main(set_dir, reload_dir, out_dir, set_name):
    """set_dir holds the source set's clips (CA.SOURCE_SET: UziT packs the Uzi set's under its own names)."""
    src_set = CA.SOURCE_SET.get(set_name, set_name)
    src_prefix, prefix = "GunsOfTien_Compact%s_" % src_set, "GunsOfTien_Compact%s_" % set_name
    src_names = [l.strip() for l in open(os.path.join(set_dir, "manifest.txt")) if l.strip()]
    sources = [os.path.join(set_dir, "clips", n + ".x") for n in src_names]
    for r in RELOADS:
        n = src_prefix + "Reload" + r
        src_names.append(n)
        sources.append(os.path.join(reload_dir, n + ".x"))
    names = [prefix + n[len(src_prefix):] for n in src_names]
    muzzle_z = CA.TURNED_SETS.get(set_name)
    for old in os.listdir(out_dir):
        if old.startswith(prefix) and old.endswith(".x"):
            os.remove(os.path.join(out_dir, old))
    tmp = tempfile.mkdtemp()
    texts = []
    for n, src in zip(names, sources):
        dst = os.path.join(tmp, n + ".x")
        xa = xanim.read(src)
        if muzzle_z is not None:
            shift_gun_bone(xa, (0.0, 0.0, -2.0 * muzzle_z))
        lossy = bool(LOSSY and re.search(LOSSY, n))
        saved, xanim.TOLERANCE = xanim.TOLERANCE, ({"R": 2e-4, "T": 2e-5, "S": 1e-6} if lossy else None)
        try:
            xanim.write_clip(src, dst, n, xa.tracks, xa.ticks_per_second)
        finally:
            xanim.TOLERANCE = saved
        texts.append(open(dst, encoding="latin-1").read())
    files = []
    for i in range(0, len(texts), PACK):
        chunk = texts[i:i + PACK]
        out = chunk[0].rstrip() + "\n"
        for t in chunk[1:]:
            out += "\n" + t[re.search(r"^AnimationSet ", t, re.M).start():].rstrip() + "\n"
        fn = "GunsOfTien_Compact%s_Pack%d.x" % (set_name, i // PACK + 1)
        with open(os.path.join(out_dir, fn), "w", encoding="latin-1", newline="\n") as fh:
            fh.write(out)
        files.append(fn)
    total = sum(os.path.getsize(os.path.join(out_dir, f)) for f in files)
    print("[pack] %s: %d clips in %d files, %.1f MB" % (set_name, len(names), len(files), total / 1e6))
    return names


if __name__ == "__main__":
    main(*sys.argv[1:5])
