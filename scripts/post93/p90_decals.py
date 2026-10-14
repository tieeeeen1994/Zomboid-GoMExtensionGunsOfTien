#!/usr/bin/env python3
"""Decal sheets for the P90 TR texture bake (Python 3 + Pillow): molded seams, pins, slots, markings, grip
stippling, the ejection port. build_p90.py projects them onto the baked texel positions (side sheets onto faces
facing +-x, top / bottom sheets onto faces facing up / down) and paints:
    R = dark (seams, slots, engraving, the ejection port), G = light paint / raised lettering, B = stippled area.

Sheets are drawn in real millimetres (p90_geometry frame) at PX_PER_MM, each as seen from outside so lettering
reads the right way round: the left side (+x) is seen with the muzzle on the viewer's left, the right side with
the muzzle on the right; the top with the muzzle right and the gun's left up; the bottom with the muzzle right
and the gun's left down.

Usage: python3 p90_decals.py OUT_DIR     writes p90_side_left.png, p90_side_right.png, p90_top.png, p90_bottom.png
and decals.json (the sheet frames, read by build_p90.py).
"""

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p90_geometry as G  # noqa: E402

PX_PER_MM = 4
U_RANGE = (-10.0, 510.0)
V_RANGE = (-10.0, 190.0)
X_RANGE = (-45.0, 45.0)
FONT = "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf"
FONT_PLAIN = "/System/Library/Fonts/Supplemental/Arial Narrow.ttf"


class Sheet:
    """Image over a (horizontal, vertical) millimetre window; flip_h / flip_v say how the axes map to pixels."""

    def __init__(self, name, h_range, v_range, flip_h=False, flip_v=True):
        self.name = name
        self.h_range, self.v_range = h_range, v_range
        self.flip_h, self.flip_v = flip_h, flip_v
        self.w = int((h_range[1] - h_range[0]) * PX_PER_MM)
        self.h = int((v_range[1] - v_range[0]) * PX_PER_MM)
        self.img = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        self.chan = {c: Image.new("L", (self.w, self.h), 0) for c in "RGB"}

    def px(self, a, b):
        fx = (a - self.h_range[0]) / (self.h_range[1] - self.h_range[0])
        fy = (b - self.v_range[0]) / (self.v_range[1] - self.v_range[0])
        if self.flip_h:
            fx = 1 - fx
        if self.flip_v:
            fy = 1 - fy
        return fx * self.w, fy * self.h

    def draw(self, c):
        return ImageDraw.Draw(self.chan[c])

    def line(self, c, pts, width_mm, value=255):
        self.draw(c).line([self.px(*p) for p in pts], fill=value, width=max(1, int(width_mm * PX_PER_MM)),
                          joint="curve")

    def rect(self, c, a0, b0, a1, b1, value=255, radius_mm=0.0):
        (x0, y0), (x1, y1) = self.px(a0, b0), self.px(a1, b1)
        box = [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]
        self.draw(c).rounded_rectangle(box, radius=radius_mm * PX_PER_MM, fill=value)

    def ring(self, c, a, b, r_mm, width_mm, value=255):
        x, y = self.px(a, b)
        r = r_mm * PX_PER_MM
        self.draw(c).ellipse([x - r, y - r, x + r, y + r], outline=value, width=max(1, int(width_mm * PX_PER_MM)))

    def disc(self, c, a, b, r_mm, value=255):
        x, y = self.px(a, b)
        r = r_mm * PX_PER_MM
        self.draw(c).ellipse([x - r, y - r, x + r, y + r], fill=value)

    def text(self, c, a, b, s, height_mm, value=255, font=FONT, anchor="mm"):
        """Lettering centred at (a, b), always upright and readable in the sheet's own view."""
        size = int(height_mm * PX_PER_MM * 1.35)
        f = ImageFont.truetype(font, size)
        self.draw(c).text(self.px(a, b), s, font=f, fill=value, anchor=anchor)

    def save(self, folder):
        Image.merge("RGB", [self.chan[c] for c in "RGB"]).save(os.path.join(folder, self.name + ".png"))
        return {"file": self.name + ".png", "h_range": self.h_range, "v_range": self.v_range,
                "flip_h": self.flip_h, "flip_v": self.flip_v}


def side(name, left):
    # Seen from the left the muzzle is on the viewer's left, so u runs right-to-left in the picture.
    s = Sheet(name, U_RANGE, V_RANGE, flip_h=left)
    # Charging handle slot (the knob sits at its front end) and its cut-out.
    s.line("R", [(G.HANDLE_U - G.HANDLE_TRAVEL, G.HANDLE_V), (G.HANDLE_U + 3, G.HANDLE_V)], 4.6, 235)
    s.line("R", [(G.HANDLE_U - G.HANDLE_TRAVEL - 2, G.HANDLE_V - 4.2), (G.HANDLE_U + 5, G.HANDLE_V - 4.2)], 0.7, 120)
    s.line("R", [(G.HANDLE_U - G.HANDLE_TRAVEL - 2, G.HANDLE_V + 4.2), (G.HANDLE_U + 5, G.HANDLE_V + 4.2)], 0.7, 120)
    # Moulding seams: butt / receiver joint, the receiver side panel, the front housing joint.
    s.line("R", [(118, 82), (118, 121)], 0.9, 150)
    s.line("R", [(118, 88), (300, 88), (338, 92), (452, 92)], 0.8, 110)
    s.line("R", [(342, 121), (350, 140), (350, 157)], 0.8, 140)
    s.line("R", [(372, 121), (466, 121)], 0.7, 110)
    s.line("R", [(10, 60), (88, 60)], 0.7, 90)
    # Butt plate seam.
    s.line("R", [(7, 4), (2, 40), (3, 100), (12, 121)], 1.0, 170)
    # Take-down pins / screws.
    for (a, b) in ((70, 98), (160, 96), (326, 98), (430, 102), (250, 68), (440, 40)):
        s.ring("R", a, b, 2.6, 0.8, 200)
        s.disc("G", a, b, 1.2, 70)
    # Magazine release lever on the rear post.
    s.rect("R", 100, 140, 126, 143, 120, 1.0)
    # Grip and front hand stop stippling.
    s.rect("B", 216, 22, 280, 78, 255, 6)
    s.rect("B", 410, 12, 458, 80, 200, 8)
    s.rect("B", 4, 6, 70, 118, 90, 12)
    # Lettering.
    if left:
        s.text("G", 60, 101, "P90", 9, 150)
        s.text("G", 190, 111, "FN HERSTAL - BELGIUM", 3.4, 110, FONT_PLAIN)
        s.text("G", 190, 104, "PDW  5,7x28", 3.0, 90, FONT_PLAIN)
        s.rect("R", 34, 92, 86, 111, 70, 3)            # recessed logo panel
    else:
        s.text("G", 175, 111, "FN P90 TR", 3.6, 110)
        s.text("G", 175, 104, "No 2001.0937", 2.6, 80, FONT_PLAIN)
        s.text("G", 400, 112, "5,7x28", 3.0, 90, FONT_PLAIN)
    return s


def top():
    s = Sheet("p90_top", U_RANGE, X_RANGE, flip_h=False, flip_v=True)
    # Seam where the housing meets the receiver, rear post joint.
    s.line("R", [(345, -24), (345, 24)], 0.8, 120)
    s.line("R", [(130, -18), (130, 18)], 0.8, 100)
    # Ambidextrous magazine catch on the rear post top.
    s.rect("R", 104, -8, 112, 8, 140, 1.5)
    # Rear of the receiver top (behind the post): stippled thumb rest.
    s.rect("B", 30, -20, 92, 20, 120, 6)
    return s


def bottom():
    s = Sheet("p90_bottom", U_RANGE, X_RANGE, flip_h=False, flip_v=False)
    # Downward ejection port behind the grip, with a moulded rim.
    a, b = G.EJECT_U
    s.rect("R", a, -8.5, b, 8.5, 255, 2.5)
    s.rect("G", a - 3, -11, b + 3, -9.6, 60)
    s.rect("G", a - 3, 9.6, b + 3, 11, 60)
    # Fire selector markings around the rotary selector (S safe, 1 single, A auto).
    s.text("G", 283, 0, "S", 3.2, 230)
    s.text("G", 296, -12.5, "1", 3.2, 230)
    s.text("G", 309, 0, "A", 3.2, 230)
    s.line("R", [(105, 0), (180, 0)], 0.8, 100)
    s.rect("B", 330, -14, 395, 14, 120, 6)
    return s


def wrap(name, length, radius, text_lines, knurl=None, rings=()):
    """Cylinder wrap sheet: horizontal = distance along the axis (mm), vertical = arc length from the top,
    positive towards the gun's left (+x), i.e. angle * radius with angle = atan2(x, z)."""
    half = math.pi * radius
    s = Sheet(name, (0.0, length), (-half, half), flip_h=False, flip_v=True)
    for (a, b, w, val) in rings:
        s.line("R", [(a, -half), (a, half)], w, val)
    if knurl:
        a0, a1, pitch = knurl
        t = -half
        while t < half:
            s.line("B", [(a0, t), (a1, t)], pitch * 0.45, 255)
            t += pitch
    for (a, b, txt, hmm, val) in text_lines:
        s.text("G", a, b, txt, hmm, val)
    return s


def main(out):
    os.makedirs(out, exist_ok=True)
    info = {
        "px_per_mm": PX_PER_MM,
        "side_left": side("p90_side_left", True).save(out),
        "side_right": side("p90_side_right", False).save(out),
        "top": top().save(out),
        "bottom": bottom().save(out),
        # Text on the suppressor faces the gun's left (+x, arc +pi/2 * r); the mount gets a knurled band.
        "supp_wrap": wrap("p90_supp_wrap", G.SUPP_LEN, G.SUPP_R, [
            (85, math.pi / 2 * G.SUPP_R + 4, "FN HERSTAL", 4.2, 120),
            (85, math.pi / 2 * G.SUPP_R - 3, "5.7x28  P90", 3.4, 100),
            (85, -math.pi / 2 * G.SUPP_R, "SUPPRESSOR  No 0417", 3.0, 80)],
            knurl=(2.0, 13.0, 1.6), rings=((45, 0, 0.8, 140), (128, 0, 0.8, 140))).save(out),
        "mount_wrap": wrap("p90_mount_wrap", G.MOUNT_LEN, G.MOUNT_R, [],
                           knurl=(15.0, 32.0, 1.4), rings=((14.0, 0, 0.6, 160), (33.0, 0, 0.6, 160))).save(out),
    }
    with open(os.path.join(out, "decals.json"), "w") as handle:
        json.dump(info, handle, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
