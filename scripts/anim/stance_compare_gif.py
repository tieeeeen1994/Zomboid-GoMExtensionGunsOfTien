"""Pastes stance_compare.py's per-version renders side by side, its views (STANCE_VIEWS, default front,top) stacked,
into an animated GIF (system python with Pillow); STANCE_MARK=frame,... flags those frames in red:

    py scripts/anim/stance_compare_gif.py <render_dir> <out.gif> <step> label [label ...]
"""
import os
import re
import sys

from PIL import Image, ImageDraw


def main(src, out, step, labels):
    views = os.environ.get("STANCE_VIEWS", "front,top").split(",")
    mark = {int(v) for v in os.environ.get("STANCE_MARK", "").split(",") if v}
    frames = sorted({int(m.group(1)) for n in os.listdir(os.path.join(src, labels[0]))
                     for m in [re.match(r"%s_(\d+)\.png$" % views[0], n)] if m})
    images = []
    for f in frames:
        tiles = []
        for lab in labels:
            shots = [Image.open(os.path.join(src, lab, "%s_%d.png" % (v, f))).convert("RGB") for v in views]
            t = Image.new("RGB", (shots[0].width, sum(s.height for s in shots)), (255, 255, 255))
            y = 0
            for s in shots:
                t.paste(s, (0, y))
                y += s.height
            ImageDraw.Draw(t).text((8, 6), lab, fill=(255, 255, 255))
            tiles.append(t)
        w = sum(t.width for t in tiles)
        img = Image.new("RGB", (w, tiles[0].height), (255, 255, 255))
        x = 0
        for t in tiles:
            img.paste(t, (x, 0))
            x += t.width
        near = any(abs(f - m) <= step for m in mark)
        ImageDraw.Draw(img).text((8, img.height - 18), "frame %d%s" % (f, "  <- deepest" if near else ""),
                                 fill=(255, 80, 80) if near else (255, 255, 255))
        images.append(img)
    images[0].save(out, save_all=True, append_images=images[1:], duration=int(1000 * step / 30), loop=0)
    images[len(images) // 2].save(os.path.splitext(out)[0] + "_mid.png")
    print("wrote", out, len(images), "frames")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4:])
