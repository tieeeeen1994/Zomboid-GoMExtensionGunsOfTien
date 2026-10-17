#!/usr/bin/env python3
"""Every translation key Guns of Marz and Gunworks make the game look up, and which have no English text in vanilla,
GoM, Gunworks, Ammo Maker or this repo's two mods.

    python3 scripts/check_gom_translations.py

Keys come from their Lua (getText / getTextOrNull with a literal; keys built from a variable are listed for a look by
hand), their item scripts (an ItemName per item without DisplayName, Tooltip = ..., IGUI_ItemCat_<DisplayCategory>,
Tooltip_weapon_<PartType> for the gun tooltip's part rows), their craftRecipe names and ToolTips, and their sandbox
options. Missing English goes in this mod's Translate/EN files (gen_scripts.py writes ItemName / Tooltip; IG_UI.json
and ContextMenu.json are by hand). Exits 1 while anything is missing. Run after a GoM or Gunworks update.
"""
import glob
import json
import os
import re
import sys

WS = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600"),
                      "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600") if os.path.isdir(p))
PZ = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/ProjectZomboid/"
                                         "Project Zomboid.app/Contents/Java/media"),
                      "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media") if os.path.isdir(p))
GOM = WS + "/3722134990/mods/GunsOfMarz"
GW = WS + "/3722064198/mods/Gunworks_gang_framework"
AM = WS + "/2788256295/mods"
TIEN = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Contents/mods"))
# GoM's ReloadAllMagazines_Compac.lua only looks these up to remove another mod's menu options by their text; English
# from us would not match that mod's and must not be added.
IGNORE = {"ContextMenu_ReloadAllMagazines_LoadAllMagazines", "ContextMenu_ReloadAllMagazines_UnloadAllMagazines"}
SOURCES = {"GoM": GOM, "Gunworks": GW}


def files(root, pattern):
    return [f for f in glob.glob(root + "/**/" + pattern, recursive=True) if "PreviousVersion" not in f]


def load_json(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    try:
        return json.loads(txt)
    except Exception:
        # tolerate trailing commas / comments
        return dict(re.findall(r'"([^"]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', txt))


# ---- English text available, by file kind (IG_UI, ItemName, Tooltip...) -------------------------------------------
have = {}
origin = {}
for name, root in (("vanilla", PZ), ("GoM", GOM), ("Gunworks", GW), ("AmmoMaker", AM), ("Tien", TIEN)):
    for f in files(root, "*.json"):
        if "/Translate/EN/" not in f.replace("\\", "/") and "\\Translate\\EN\\" not in f:
            continue
        kind = os.path.splitext(os.path.basename(f))[0]
        for k, v in load_json(f).items():
            have.setdefault(kind, {})[k] = v
            origin[(kind, k)] = name
    # old txt format (Gunworks root EN folder, older mods)
    for f in files(root, "*_EN.txt"):
        kind = os.path.basename(f).split("_EN")[0]
        for k, v in re.findall(r'^\s*([\w.\-]+)\s*=\s*"(.*)"', open(f, encoding="utf-8", errors="ignore").read(), re.M):
            have.setdefault(kind, {})[k] = v
            origin[(kind, k)] = name


def known(kind, key):
    return key in have.get(kind, {})


def any_kind(key):
    return any(key in d for d in have.values())


missing = {}


def need(kind, key, where):
    if key in IGNORE:
        return
    if not known(kind, key):
        missing.setdefault((kind, key), set()).add(where)


# ---- Lua getText -------------------------------------------------------------------------------------------------
dynamic = set()
for src, root in SOURCES.items():
    for f in files(root, "*.lua"):
        txt = open(f, encoding="utf-8", errors="ignore").read()
        rel = src + ":" + f.replace("\\", "/").split("/media/")[-1]
        for m in re.finditer(r'getText(?:OrNull)?\(\s*"([^"]+)"\s*([,)\.])', txt):
            key, nxt = m.group(1), m.group(2)
            if nxt == ".":
                dynamic.add((key + "..", rel))
                continue
            if not any_kind(key) and key not in IGNORE:
                missing.setdefault(("(any)", key), set()).add(rel)
        for m in re.finditer(r'getText(?:OrNull)?\(\s*([A-Za-z_][\w.]*)\s*\.\.', txt):
            dynamic.add((m.group(1) + "..", rel))

# ---- item scripts --------------------------------------------------------------------------------------------------
cats = set()
for src, root in SOURCES.items():
    for f in files(root, "*.txt"):
        if "/scripts/" not in f.replace("\\", "/"):
            continue
        txt = open(f, encoding="utf-8", errors="ignore").read()
        rel = src + ":" + f.replace("\\", "/").split("/scripts/")[-1]
        for m in re.finditer(r'(?m)^\s*item\s+([\w\-]+)\s*\{(.*?)\n\s*\}', txt, re.S):
            name, body = m.group(1), m.group(2)
            module = re.findall(r'module\s+(\w+)', txt[:m.start()])[-1]
            full = module + "." + name
            if not re.search(r'(?im)^\s*DisplayName\s*=', body):
                need("ItemName", full, rel)
            for t in re.findall(r'(?im)^\s*Tooltip\s*=\s*([\w\-]+)', body):
                need("Tooltip", t, rel)
            for c in re.findall(r'(?im)^\s*DisplayCategory\s*=\s*(\w+)', body):
                cats.add(c)
                need("IG_UI", "IGUI_ItemCat_" + c, rel)
            for pt in re.findall(r'(?im)^\s*PartType\s*=\s*(\w+)', body):
                need("Tooltip", "Tooltip_weapon_" + pt, rel)
        for m in re.finditer(r'(?m)^\s*craftRecipe\s+([\w\-]+)\s*\{(.*?)\n\s*\}', txt, re.S):
            name, body = m.group(1), m.group(2)
            need("Recipes", name, rel)
            for t in re.findall(r'(?im)^\s*ToolTip\s*=\s*([\w\-]+)', body):
                need("Tooltip", t, rel)

# ---- sandbox options -----------------------------------------------------------------------------------------------
for src, root in SOURCES.items():
    for f in files(root, "sandbox-options.txt"):
        txt = open(f, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r'option\s+([\w.]+)\s*\{(.*?)\}', txt, re.S):
            body = m.group(2)
            tr = re.search(r'translation\s*=\s*(\w+)', body)
            page = re.search(r'page\s*=\s*(\w+)', body)
            key = tr.group(1) if tr else m.group(1).replace(".", "_")
            need("Sandbox", "Sandbox_" + key, src + ":sandbox " + m.group(1))
            if page:
                need("Sandbox", "Sandbox_" + page.group(1), src + ":sandbox page")
            if re.search(r'type\s*=\s*enum', body):
                n = int(re.search(r'numValues\s*=\s*(\d+)', body).group(1))
                vt = re.search(r'valueTranslation\s*=\s*(\w+)', body)
                base = vt.group(1) if vt else key
                for i in range(1, n + 1):
                    need("Sandbox", "Sandbox_%s_option%d" % (base, i), src + ":sandbox " + m.group(1))

# ---- report --------------------------------------------------------------------------------------------------------
by_kind = {}
for (kind, key), where in sorted(missing.items()):
    by_kind.setdefault(kind, []).append((key, sorted(where)))
for kind, rows in sorted(by_kind.items()):
    print("== %s: %d missing" % (kind, len(rows)))
    for key, where in rows:
        print("   %-55s %s" % (key, ", ".join(where[:3]) + (" +%d" % (len(where) - 3) if len(where) > 3 else "")))
print("== dynamic getText (prefix .. variable):")
for k, rel in sorted(dynamic):
    print("   ", k, rel)
print("display categories:", sorted(cats))
if not by_kind:
    print("nothing missing")
sys.exit(1 if by_kind else 0)
