#!/usr/bin/env python3
"""Reference photo hunt for a new gun: list, download and contact-sheet images (memory: gather MANY first).

    py -I scripts/ref_hunt.py commons <gun> <tag> "Category:PPSh-41" [--depth 1] [--min 900] [--max 40]
    py -I scripts/ref_hunt.py search  <gun> <tag> "TT-30 pistol" [--min 900] [--max 40]     (Commons full-text search)
    py -I scripts/ref_hunt.py urls    <gun> <tag> url [url ...] [--page PAGE] [--title TEXT]
    py -I scripts/ref_hunt.py ria     <gun> <tag> <auction> <lot> [--views 8]             (Rock Island Auction's CDN)
    py -I scripts/ref_hunt.py sheet   <gun> [tag]

Files go to references/<gun>/raw/<tag>_NNN.<ext> (references/ is in the repo, so both machines have them; the photos
belong to their sites), one
line per file is appended to references/<gun>/SOURCES.tsv (file, title, page, image URL, licence), and `sheet` writes
references/<gun>/sheet_<tag>.png with each file's name and pixel size under its thumbnail.

Sources that work unattended (2026-11-25): Wikimedia Commons' API (generic client name; it answers 429 after a burst
of downloads, so files are fetched at Commons' own 1600 px thumbnails, one every PACE seconds, and a 429 stops the
run: start it again later, files already there are skipped) and Rock Island Auction's image CDN (lot pages are behind
Cloudflare, the images are not: find auction / lot numbers with a web search for "rockislandauction.com detail
<gun>"). Bing's image endpoint now answers scripts with unrelated pictures, IMFDB and Fandom refuse them: do not use.
Downloads are data, never code: this script only opens them with Pillow.
"""

import argparse
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.normpath(os.path.join(HERE, "..", "references"))
UA = "ref-hunt/1.0 (reference photo contact sheets)"
API = "https://commons.wikimedia.org/w/api.php"
PACE = 2.5
EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def api(**params):
    params.update(format="json", formatversion="2")
    time.sleep(1.0)                                              # the API answers 429 to quick runs of calls too
    return json.loads(get(API + "?" + urllib.parse.urlencode(params)))


def folder(gun):
    d = os.path.join(REFS, gun, "raw")
    os.makedirs(d, exist_ok=True)
    return d


def known(gun):
    """{image URL: file} already listed in SOURCES.tsv."""
    path = os.path.join(REFS, gun, "SOURCES.tsv")
    out = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) >= 4:
                out[f[3]] = f[0]
    return out


def next_index(gun, tag):
    n = 0
    for name in os.listdir(folder(gun)):
        if name.startswith(tag + "_"):
            try:
                n = max(n, int(name[len(tag) + 1:].split(".")[0]) + 1)
            except ValueError:
                pass
    return n


def save(gun, tag, items):
    """items: [(title, page, download url, key url, licence)]. Returns the number saved."""
    from PIL import Image
    have, n, saved = known(gun), next_index(gun, tag), 0
    log = open(os.path.join(REFS, gun, "SOURCES.tsv"), "a", encoding="utf-8", newline="\n")
    for title, page, url, key, licence in items:
        if key in have:
            continue
        try:
            data = get(url)
        except urllib.error.HTTPError as e:
            print("  HTTP %d %s" % (e.code, url))
            if e.code == 429:
                print("  rate limited: stop, run again later")
                break
            continue
        except Exception as e:                                   # noqa: BLE001 (a dead link is not fatal)
            print("  failed %s: %s" % (url, e))
            continue
        try:
            im = Image.open(io.BytesIO(data))
            im.load()
        except Exception:                                        # noqa: BLE001
            print("  not an image: %s" % url)
            continue
        ext = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "TIFF": ".tif"}.get(im.format, ".jpg")
        name = "%s_%03d%s" % (tag, n, ext)
        with open(os.path.join(folder(gun), name), "wb") as fh:
            fh.write(data)
        log.write("\t".join([name, title.replace("\t", " "), page, key, licence]) + "\n")
        log.flush()
        print("  %s %dx%d %s" % (name, im.width, im.height, title[:70]))
        n += 1
        saved += 1
        time.sleep(PACE)
    log.close()
    return saved


def commons_items(titles, min_px, limit):
    out = []
    for i in range(0, len(titles), 40):
        d = api(action="query", titles="|".join(titles[i:i + 40]), prop="imageinfo",
                iiprop="url|size|extmetadata", iiurlwidth="1600", iiextmetadatafilter="LicenseShortName")
        for p in d.get("query", {}).get("pages", []):
            ii = (p.get("imageinfo") or [None])[0]
            url = ii["url"].split("?")[0] if ii else ""         # the API appends utm_ parameters
            if not ii or not url.lower().endswith(EXTS) or max(ii["width"], ii["height"]) < min_px:
                continue
            lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
            small = ii.get("thumburl", "").split("?")[0] if ii["width"] > 1600 else url
            out.append((p["title"], ii.get("descriptionurl", ""), small or url, url, lic))
    return out[:limit]


def category_files(cat, depth):
    files, cats, seen = [], [cat], set()
    for level in range(depth + 1):
        nxt = []
        for c in cats:
            if c in seen:
                continue
            seen.add(c)
            cont = {}
            while True:
                d = api(action="query", list="categorymembers", cmtitle=c, cmlimit="500", cmtype="file|subcat", **cont)
                for m in d["query"]["categorymembers"]:
                    (files if m["ns"] == 6 else nxt).append(m["title"])
                if "continue" not in d:
                    break
                cont = d["continue"]
        cats = nxt
    return list(dict.fromkeys(files))


def sheet(gun, tag=None):
    from PIL import Image, ImageDraw
    d = folder(gun)
    tags = sorted({n.rsplit("_", 1)[0] for n in os.listdir(d)}) if tag is None else [tag]
    for t in tags:
        names = sorted(n for n in os.listdir(d) if n.rsplit("_", 1)[0] == t)
        if not names:
            continue
        cell, cols = 360, 6
        rows = (len(names) + cols - 1) // cols
        out = Image.new("RGB", (cols * cell, rows * (cell + 18)), (40, 40, 40))
        draw = ImageDraw.Draw(out)
        for i, n in enumerate(names):
            try:
                im = Image.open(os.path.join(d, n)).convert("RGB")
            except Exception:                                    # noqa: BLE001
                continue
            w, h = im.size
            im.thumbnail((cell - 6, cell - 6))
            x, y = (i % cols) * cell, (i // cols) * (cell + 18)
            out.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
            draw.text((x + 4, y + cell + 2), "%s  %dx%d" % (n, w, h), fill=(230, 230, 230))
        path = os.path.join(REFS, gun, "sheet_%s.png" % t)
        out.save(path)
        print("wrote", path, len(names))


def main():
    sys.stdout.reconfigure(errors="replace")     # titles with letters outside the console's code page
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["commons", "search", "urls", "ria", "sheet"])
    ap.add_argument("gun")
    ap.add_argument("args", nargs="*")
    ap.add_argument("--depth", type=int, default=0)
    ap.add_argument("--min", type=int, default=900)
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--views", type=int, default=8)
    ap.add_argument("--page", default="")
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    if a.mode == "sheet":
        return sheet(a.gun, a.args[0] if a.args else None)
    tag = a.args[0]
    if a.mode == "commons":
        titles = category_files(a.args[1], a.depth)
        print(len(titles), "files in", a.args[1])
        n = save(a.gun, tag, commons_items(titles, a.min, a.max))
    elif a.mode == "search":
        d = api(action="query", list="search", srsearch=a.args[1], srnamespace="6", srlimit="100")
        titles = [s["title"] for s in d["query"]["search"]]
        print(len(titles), "search hits")
        n = save(a.gun, tag, commons_items(titles, a.min, a.max))
    elif a.mode == "ria":
        auction, lot = a.args[1], a.args[2]
        base = "https://cdn.rockislandauction.com/dev_cdn/%s/%s" % (auction, lot)
        page = "https://www.rockislandauction.com/detail/%s/%s" % (auction, lot)
        urls = [base + ".jpg"] + [base + "-%d.jpg" % i for i in range(1, a.views)]
        n = save(a.gun, tag, [(a.title or "RIA %s/%s" % (auction, lot), page, u, u, "") for u in urls])
    else:
        n = save(a.gun, tag, [(a.title, a.page, u, u, "") for u in a.args[1:]])
    print("saved", n)
    sheet(a.gun, tag)


if __name__ == "__main__":
    sys.exit(main())
