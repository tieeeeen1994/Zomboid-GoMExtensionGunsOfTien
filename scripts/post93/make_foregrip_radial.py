"""Radial menu icons for folding and unfolding the MP7's integral front grip, in Gunworks' radial icon style
(GunworksRadial_FoldStock / UnfoldBipod: 32x32 olive pixel art, black outline, red arrows).

    py scripts/post93/make_foregrip_radial.py

Writes Contents/mods/GoMExtensionGunsOfTienPost93/42/media/ui/GunsOfTienPost93_Radial_{Fold,Unfold}Foregrip.png:
the grip hanging under a strip of receiver, red arrows up (fold) or down (unfold) on both sides, as Gunworks keeps
one picture per part and turns only the arrows.
"""

import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.normpath(os.path.join(HERE, "../../Contents/mods/GoMExtensionGunsOfTienPost93/42/media/ui"))

# Gunworks' palette (sampled from its radial icons)
OUTLINE = (0, 0, 0, 255)
DARK = (52, 51, 45, 255)
BASE = (69, 68, 59, 255)
MID = (82, 82, 71, 255)
LIGHT = (94, 95, 83, 255)
SHINE = (112, 109, 81, 255)
RED = (255, 0, 0, 255)

# The receiver underside (x 4..27, y 3..7) and the grip below it (x 12..19, y 8..28), knuckle rounded at the top,
# the squared catch at the bottom; rows are (x0, x1) inclusive.
RECEIVER = [(y, 4, 27) for y in range(3, 8)]
GRIP = [(8, 12, 19)] + [(y, 11, 20) for y in range(9, 27)] + [(27, 11, 20), (28, 12, 19)]
GROOVES = (13, 16, 19)                           # three grooves across the grip, as on the model


def draw(arrow_up):
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = im.load()
    filled = set()
    for y, x0, x1 in RECEIVER + GRIP:
        for x in range(x0, x1 + 1):
            filled.add((x, y))
    for x, y in filled:
        px[x, y] = BASE
    # light from the upper left: lit left column and top row, shaded right column
    for y, x0, x1 in GRIP:
        px[x0 + 1, y] = LIGHT
        px[x1 - 1, y] = DARK
    for x in range(5, 27):
        px[x, 4] = SHINE
        px[x, 6] = MID
    for y in GROOVES:
        for x in range(12, 20):
            px[x, y] = DARK
    # one-pixel black outline round the shape
    for x, y in list(filled):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in filled and 0 <= q[0] < 32 and 0 <= q[1] < 32:
                px[q] = OUTLINE
    # red arrows either side of the grip: a 2-pixel shaft and a 6-pixel head
    for cx in (6, 25):
        shaft = range(13, 25) if arrow_up else range(10, 22)
        for y in shaft:
            px[cx, y] = px[cx + 1, y] = RED
        tip = 10 if arrow_up else 24
        step = 1 if arrow_up else -1
        for i in range(3):
            for x in range(cx - i, cx + 2 + i):
                px[x, tip + i * step] = RED
    return im


def main():
    os.makedirs(UI, exist_ok=True)
    for name, up in (("FoldForegrip", True), ("UnfoldForegrip", False)):
        path = os.path.join(UI, "GunsOfTienPost93_Radial_%s.png" % name)
        draw(up).save(path)
        print("wrote", path)


if __name__ == "__main__":
    main()
