#!/usr/bin/env python3
"""The H&K MP7A1's unload clip: vanilla's pistol load played backwards, baked into a forward clip (Python 3).

    py scripts/post93/anim/mp7_reload.py <vanilla anims_X/Bob> <out_dir>

Writes <out_dir>/Bob_GunsOfTien_MP7_Unload.x; ship it to Contents/mods/GoMExtensionGunsOfTienPost93/42/media/anims_X/Bob/.

The MP7 is held like a pistol and its magazine goes up into the pistol grip, so it reloads the way vanilla's pistols
do: the AnimSets *MP7A1_GoT.xml (animId "MP7A1", Guns.lua) play vanilla's Bob_Reload_Handgun_Load for the load and
Bob_Reload_Handgun_Rack for the rack. Vanilla's own pistol unload is that load clip with m_AnimReverse; this file is
the same motion with its key times mirrored instead, so the unload node's m_TimePc / End events count along the
motion the player sees and the magazine swap (changeWeaponPart "mag", Gunworks' "attachments" style) can be put where
the left hand leaves the grip. Keys and the rest of the file (frames, Bob's mesh) are vanilla's, unchanged; uses
TienInspectWeapon's xanim.py (~/Zomboid/Workshop/TienInspectWeapon/scripts/anim, or $TIEN_ANIM).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("TIEN_ANIM") or os.path.join(os.path.expanduser("~"),
                                                               "Zomboid/Workshop/TienInspectWeapon/scripts/anim"))
sys.dont_write_bytecode = True
import xanim  # noqa: E402

SOURCE = "Bob_Reload_Handgun_Load"
NAME = "Bob_GunsOfTien_MP7_Unload"


def reversed_tracks(xa):
    end = max(max(list(t.S) + list(t.R) + list(t.T) + [0]) for t in xa.tracks)
    out = []
    for tr in xa.tracks:
        r = xanim.Track(tr.bone)
        r.S = {end - t: v for t, v in tr.S.items()}
        r.R = {end - t: v for t, v in tr.R.items()}
        r.T = {end - t: v for t, v in tr.T.items()}
        out.append(r)
    return out, end


def main(src_dir, out_dir):
    src = next(os.path.join(src_dir, SOURCE + e) for e in (".X", ".x") if os.path.isfile(os.path.join(src_dir, SOURCE + e)))
    xa = xanim.read(src)
    tracks, end = reversed_tracks(xa)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, NAME + ".x")
    xanim.write_clip(src, out, NAME, tracks, xa.ticks_per_second)
    print("[mp7] %s: %d tracks, %d frames" % (out, len(tracks), end // 160 + 1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
