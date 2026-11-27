#!/usr/bin/env python3
"""Review sheet of the Bizon family and the Vityaz from render_bizon.py's renders (Python 3 + Pillow).

    py scripts/post93/make_bizon_preview.py RENDER_DIR [OUT.png]

One row per gun: its right side (flipped: renders show game space mirrored) and a 3/4 view, on a light background.
Default OUT: docs/post93_bizon_preview.png.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageOps

ROWS = [("PP-19 Bizon Submachine Gun (9x18, 64-round helical)", ["BIZON_right", "BIZON_q"]),
        ("Bizon-2-01 Submachine Gun (9x19, 53-round helical): stock open / folded",
         ["BIZON201_open_right", "BIZON201_folded_q"]),
        ("Bizon-2-07 Submachine Gun (7.62x25): 35-round box / invented 45-round helical",
         ["BIZON207_box_right", "BIZON207_helix_q"]),
        ("Vityaz Submachine Gun (9x19): stock folded, 30 / stock open, the clipped 2x30 pair",
         ["VITYAZ_folded_right", "VITYAZ_open_q"])]
W, BG = 1600, (228, 228, 224)


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "..", "docs",
                                                              "post93_bizon_preview.png")
    rows = []
    for title, names in ROWS:
        ims = []
        for n in names:
            im = Image.open(os.path.join(src, n + ".png")).convert("RGBA")
            if n.endswith("_right"):
                im = ImageOps.mirror(im)
            bg = Image.new("RGBA", im.size, BG + (255,))
            bg.alpha_composite(im)
            box = im.getchannel("A").getbbox()
            im = bg.convert("RGB").crop(box) if box else bg.convert("RGB")
            im.thumbnail((W // 2 - 20, 420))
            ims.append(im)
        row = Image.new("RGB", (W, max(i.height for i in ims) + 44), BG)
        ImageDraw.Draw(row).text((10, 8), title, fill=(20, 20, 20))
        for k, i in enumerate(ims):
            row.paste(i, (10 + k * (W // 2), 34))
        rows.append(row)
    sheet = Image.new("RGB", (W, sum(r.height for r in rows)), BG)
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(out)
    print("wrote", os.path.normpath(out), sheet.size)


if __name__ == "__main__":
    main()
