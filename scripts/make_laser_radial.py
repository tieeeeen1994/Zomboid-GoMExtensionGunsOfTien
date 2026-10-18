"""Radial menu icons for switching a laser on and off, in Gunworks' radial icon style (GunworksRadial_FoldStock /
UnfoldBipod: 32x32 olive pixel art, black outline, pure red accents), as scripts/post93/make_foregrip_radial.py.
They replace vanilla's vehicle headlight icons (user, 2026-10-18: "the icon... is ugly... let's make our own").

    py scripts/make_laser_radial.py

Writes Contents/mods/GoMExtensionGunsOfTien/42/media/ui/GunsOfTien_Radial_Laser{On,Off}.png: a laser unit seen from
the side (rail clamp on top, ribbed battery cap, adjustment knob, emitter tube and lens bezel at the front), its lens lit and a red beam leaving it (Turn
Laser On), or its lens dark and no beam (Turn Laser Off), as vanilla's light toggles show the state the option gives.
"""

import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.normpath(os.path.join(HERE, "../Contents/mods/GoMExtensionGunsOfTien/42/media/ui"))

# Gunworks' palette (sampled from its radial icons), plus the beam's lit core
OUTLINE = (0, 0, 0, 255)
DARK = (52, 51, 45, 255)
BASE = (69, 68, 59, 255)
MID = (82, 82, 71, 255)
LIGHT = (94, 95, 83, 255)
SHINE = (112, 109, 81, 255)
RED = (255, 0, 0, 255)
CORE = (255, 150, 140, 255)
GLASS = (30, 30, 34, 255)

# rows are (y, x0, x1) inclusive
BODY = [(12, 2, 15)] + [(y, 1, 16) for y in range(13, 21)] + [(21, 2, 15)]
CLAMP = [(9, 4, 12), (10, 3, 13), (11, 3, 13)]            # the rail clamp on top, its jaws a pixel wider
TUBE = [(y, 17, 19) for y in range(14, 20)]               # the emitter tube
BEZEL = [(13, 20, 21)] + [(y, 20, 22) for y in range(14, 20)] + [(20, 20, 21)]
LENS = [(21, y) for y in range(15, 19)] + [(22, y) for y in range(15, 19)]
KNOBS = [(11, 16)]                                        # the adjustment knob, centre
RIBS = (4, 6)                                             # the ribbed battery cap at the rear, columns


def draw(lit):
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = im.load()
    filled = set()
    for y, x0, x1 in BODY + CLAMP + TUBE + BEZEL:
        for x in range(x0, x1 + 1):
            filled.add((x, y))
    for x, y in filled:
        px[x, y] = BASE
    # light from the upper left, as Gunworks' icons
    for x in range(3, 15):
        px[x, 13] = SHINE
    for y in range(14, 20):
        px[2, y] = LIGHT
    for x in range(2, 16):
        px[x, 20] = DARK
    for x in range(4, 13):
        px[x, 10] = MID
    for x in range(3, 14):
        px[x, 11] = DARK                                   # the clamp's shadow line on the body
    px[15, 13] = MID
    for y in range(14, 20):
        px[15, y] = DARK                                   # the front edge of the body
    for x in range(17, 20):                                # the tube: lit top, shaded bottom
        px[x, 14] = LIGHT
        px[x, 19] = DARK
    for y in range(13, 21):                                # the bezel ring: lit back edge
        if (20, y) in filled:
            px[20, y] = LIGHT
    for x in RIBS:
        for y in range(14, 20):
            px[x, y] = DARK
            px[x + 1, y] = LIGHT
    for y in range(13, 21):
        px[8, y] = DARK                                    # the battery cap's seam
    # the knob: a raised disc, lit upper left, shaded lower right
    for cx, cy in KNOBS:
        for dx, dy in ((0, -1), (-1, 0), (0, 0), (1, 0), (0, 1)):
            px[cx + dx, cy + dy] = MID
        px[cx - 1, cy - 1] = DARK
        px[cx + 1, cy - 1] = DARK
        px[cx - 1, cy + 1] = DARK
        px[cx + 1, cy + 1] = DARK
        px[cx, cy - 1] = SHINE
        px[cx + 1, cy] = DARK
        px[cx, cy + 1] = DARK
    # one-pixel black outline round the shape
    for x, y in list(filled):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in filled and 0 <= q[0] < 32 and 0 <= q[1] < 32:
                px[q] = OUTLINE
    # the lens
    for x, y in LENS:
        px[x, y] = RED if lit else GLASS
    px[21, 15] = CORE if lit else MID                      # its glint
    if lit:
        # the beam: four pixels thick at the lens, two, then one to the edge, with a bright core near the lens
        for x in range(23, 26):
            for y in range(15, 19):
                px[x, y] = RED
        for x in range(26, 29):
            px[x, 16] = px[x, 17] = RED
        for x in range(29, 32):
            px[x, 16] = RED
        for x in range(21, 27):
            px[x, 16] = CORE
    return im


def main():
    os.makedirs(UI, exist_ok=True)
    for name, lit in (("LaserOn", True), ("LaserOff", False)):
        path = os.path.join(UI, "GunsOfTien_Radial_%s.png" % name)
        draw(lit).save(path)
        print("wrote", path)


if __name__ == "__main__":
    main()
