"""
Side views of the front of Guns of Marz's guns with their muzzle points, from muzzle_audit.py's JSON.

    py scripts/muzzle_audit_sheet.py <muzzle.json> <sheet.png> [min_cm] [model ...]

Each cell: the gun from its left side (muzzle to the right, top up), the `muzzle` point as a red cross, the bore's
front (muzzle_audit.py) as a green line, the `canon` point as a blue dot and the front of each fitted flash hider /
compensator / mount (canon parts that are not suppressors) as orange ticks under the bore. Only guns whose muzzle
point is at least `min_cm` (game units x 100, default 0.5) off the bore's front, or the models named.
"""

import json
import sys

from PIL import Image, ImageDraw, ImageFont

data = json.load(open(sys.argv[1]))
out = sys.argv[2]
min_cm = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
only = set(sys.argv[4:])
PX = 2400                          # pixels per game unit
W, H = 620, 300
COLS = 3

cells = []
for name, g in sorted(data.items(), key=lambda kv: -abs(kv[1]["muzzle"][1] - (kv[1]["bore_front"] or kv[1]["muzzle"][1]))):
    bore = g["bore_front"]
    d = (g["muzzle"][1] - bore) * 100 if bore is not None else None
    if only and name.split(".")[-1] not in only and name not in only:
        continue
    if not only and (d is None or abs(d) < min_cm):
        continue
    cells.append((name, g, d))

try:
    font = ImageFont.truetype("arial.ttf", 15)
except OSError:
    font = ImageFont.load_default()
rows = (len(cells) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * W, max(rows, 1) * H), "white")
for n, (name, g, d) in enumerate(cells):
    img = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(img)
    my, mz = g["muzzle"][1], g["muzzle"][2]
    right = max(my, g["bore_front"] or my) + 0.03
    devs = [x for x in g["devices"] if not x["suppressor"]]
    if devs:
        right = max(right, max(x["front"] for x in devs) + 0.01)
    ox, oy = W - 20 - right * PX, H / 2 + 20 + mz * PX

    def pt(y, z):
        return (ox + y * PX, oy - z * PX)

    for poly in g["side"]:
        if len(poly) >= 3:
            dr.polygon([pt(*v) for v in poly], fill=(200, 200, 200), outline=(120, 120, 120))
    if g["bore_front"] is not None:
        x = pt(g["bore_front"], 0)[0]
        dr.line([(x, 40), (x, H - 10)], fill=(0, 160, 0), width=2)
    for k, x in enumerate(devs):
        px = pt(x["front"], 0)[0]
        ty = pt(0, mz)[1] + 25 + 8 * k
        dr.line([(px, ty), (px, ty + 14)], fill=(240, 130, 0), width=3)
    if g["canon"]:
        cx, cy = pt(g["canon"][1], g["canon"][2])
        dr.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(0, 90, 255))
    x, y = pt(my, mz)
    dr.line([(x - 9, y), (x + 9, y)], fill=(230, 0, 0), width=3)
    dr.line([(x, y - 9), (x, y + 9)], fill=(230, 0, 0), width=3)
    dr.rectangle([0, 0, W - 1, H - 1], outline=(0, 0, 0))
    label = "%s  muzzle %s cm" % (name.split(".")[-1], "%+.1f" % d if d is not None else "?")
    if devs:
        label += "  devices: " + ", ".join("%s %+.1f" % (x["part"].split(".")[-1], (x["front"] - (g["bore_front"] or my)) * 100)
                                           for x in devs)
    dr.text((8, 6), label, fill="black", font=font)
    sheet.paste(img, ((n % COLS) * W, (n // COLS) * H))
sheet.save(out)
print("%d guns -> %s" % (len(cells), out))
