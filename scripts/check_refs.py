#!/usr/bin/env python3
"""Check that every name the two mods' scripts refer to resolves (Python 3, no dependencies).

    python3 scripts/check_refs.py

Reads every item / model / fixing / craftRecipe script of GoMExtensionGunsOfTien and GoMExtensionGunsOfTienPost93
and checks, against those mods plus Guns of Marz, Gunworks, Ammo Maker, Hot Brass and vanilla:
  - item fields naming items or models: WorldStaticModel, StaticModel, WeaponSprite, AmmoBox, MagazineType, MountOn,
    ModelWeaponPart (part item and model), fixing Require / Fixer, Module.Item tokens in recipes;
  - icons: textures/item_<Icon>.png (vanilla icons live in texture packs, so an icon some vanilla item uses counts);
  - models: mesh file models_X/<path>.fbx and its node, texture textures/<path>.png;
  - AnimSet clips: anims_X/**/<clip>.(x|fbx) in any of the mods or vanilla.
Media paths are resolved case-insensitively, as the engine does (vanilla's own scripts name WorldItems/RifleAmmoBox for
RifleAmmoBox.FBX, GoM's Worlditems/... a worlditems folder), so a case-only match is only a note; item and model names
must match exactly. Each mod's version folder and its common/media are searched.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


def _first(*paths):
    return next((p for p in paths if os.path.isdir(p)), None)


STEAM = _first(os.path.expanduser("~/Library/Application Support/Steam/steamapps"),
               "C:/Program Files (x86)/Steam/steamapps")
WS = os.path.join(STEAM, "workshop/content/108600")
GAME = _first(os.path.join(STEAM, "common/ProjectZomboid/Project Zomboid.app/Contents/Java/media"),
              os.path.join(STEAM, "common/ProjectZomboid/media"))
OURS = [os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media"),
        os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")]
OTHERS = [p for mod, ver in (("3722134990/mods/GunsOfMarz", "42.16"), ("3722064198/mods/Gunworks_gang_framework", "42.13"),
                              ("2788256295/mods/AmmoMaker", "42.20"),
                              ("3610677934/mods/Hot_Brass_Visible_Casing_Ejection_Framework", "42.15"))
          for p in (os.path.join(WS, mod, ver, "media"), os.path.join(WS, mod, "common/media"))
          if os.path.isdir(p)] + ([GAME] if GAME else [])
ROOTS = OURS + OTHERS


def files_under(rel):
    """{lowercase path relative to media: [exact relative paths]} for every file under media/<rel> of every root."""
    out = {}
    for root in ROOTS:
        base = os.path.join(root, rel)
        for p in glob.glob(os.path.join(base, "**", "*"), recursive=True):
            if os.path.isfile(p):
                r = os.path.relpath(p, root).replace("\\", "/")
                out.setdefault(r.lower(), []).append(r)
    return out


def parse_scripts(root):
    """[(kind, Module.Name, {key: [values]}, file)] for item / model / fixing / craftRecipe blocks."""
    blocks = []
    for path in glob.glob(os.path.join(root, "scripts", "**", "*.txt"), recursive=True):
        text = open(path, encoding="utf-8", errors="replace").read()
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        module = None
        depth = 0
        cur = None                                   # the block being read, from its header to its closing brace
        opened = False
        for raw in text.splitlines():
            line = raw.split("//")[0].strip()
            m = re.match(r"module\s+(\w+)", line)
            if m and depth == 0:
                module = m.group(1)
            h = re.match(r"(item|model|fixing|craftRecipe)\s+([^{]+?)\s*(\{|$)", line)
            if h and depth == 1 and module:
                cur = (h.group(1), module + "." + h.group(2).strip(), {}, path)
                blocks.append(cur)
                opened = False
            elif cur and depth >= 2:
                if "=" in line:
                    k, v = line.split("=", 1)
                    cur[2].setdefault(k.strip().lower(), []).append(v.strip().rstrip(","))
                cur[2].setdefault("_lines", []).append(line)
            depth += line.count("{") - line.count("}")
            if cur and depth >= 2:
                opened = True
            elif cur and opened and depth <= 1:
                cur = None
    return blocks


def main():
    errors, notes = [], []
    defs = {"item": {}, "model": {}}
    ours = []
    for root in ROOTS:
        for kind, name, kv, path in parse_scripts(root):
            if kind in defs:
                defs[kind].setdefault(name.lower(), name)
            if root in OURS:
                ours.append((kind, name, kv, path))
    textures = files_under("textures")
    models_x = files_under("models_X")
    anims = files_under("anims_X")
    vanilla_icons = set()
    if GAME:
        for kind, name, kv, path in parse_scripts(GAME):
            for v in kv.get("icon", []):
                vanilla_icons.add(v.lower())

    def resolve(kind, ref, module):
        ref = ref.strip()
        cands = [ref] if "." in ref else [module + "." + ref, "Base." + ref]
        for c in cands:
            if c in defs[kind].values():
                return True
            if c.lower() in defs[kind]:
                errors.append("%s name case differs: %s, defined as %s" % (kind, c, defs[kind][c.lower()]))
                return True
        return False

    def file_check(table, rel, what, where):
        hit = table.get(rel.lower())
        if not hit:
            errors.append("%s: missing %s %s" % (where, what, rel))
            return None
        if rel not in hit:
            notes.append("%s: %s %s resolves case-insensitively to %s" % (where, what, rel, hit[0]))
        return hit[0]

    checked = 0
    for kind, name, kv, path in ours:
        module = name.split(".")[0]
        where = "%s %s" % (kind, name)
        if kind == "item":
            for key in ("worldstaticmodel", "staticmodel", "weaponsprite"):
                for v in kv.get(key, []):
                    checked += 1
                    if not resolve("model", v, module):
                        errors.append("%s: %s model %s not found" % (where, key, v))
            for key in ("ammobox", "magazinetype"):
                for v in kv.get(key, []):
                    checked += 1
                    if not resolve("item", v, module):
                        errors.append("%s: %s item %s not found" % (where, key, v))
            for v in kv.get("mounton", []):
                for ref in v.replace(";", " ").split():
                    checked += 1
                    if not resolve("item", ref, module):
                        errors.append("%s: MountOn item %s not found" % (where, ref))
            for v in kv.get("modelweaponpart", []):
                parts = v.split()
                checked += 2
                if not resolve("item", parts[0], module):
                    errors.append("%s: ModelWeaponPart item %s not found" % (where, parts[0]))
                if len(parts) > 1 and not resolve("model", parts[1], module):
                    errors.append("%s: ModelWeaponPart model %s not found" % (where, parts[1]))
            for v in kv.get("icon", []):
                checked += 1
                rel = "textures/item_%s.png" % v
                if textures.get(rel.lower()):
                    file_check(textures, rel, "icon", where)
                elif v.lower() in vanilla_icons:
                    notes.append("%s: icon %s is a vanilla texture-pack icon" % (where, v))
                else:
                    errors.append("%s: missing icon %s" % (where, rel))
        elif kind == "model":
            for v in kv.get("mesh", []):
                checked += 1
                fpath, _, node = v.partition("|")
                rel = None
                for ext in (".fbx", ".FBX", ".X", ".x"):
                    if models_x.get(("models_X/" + fpath + ext).lower()):
                        rel = file_check(models_x, "models_X/" + fpath + ext, "mesh", where)
                        break
                if rel is None:
                    errors.append("%s: missing mesh models_X/%s.fbx" % (where, fpath))
                elif node:
                    full = next(os.path.join(r, rel) for r in ROOTS if os.path.isfile(os.path.join(r, rel)))
                    if node.encode() not in open(full, "rb").read():
                        errors.append("%s: node %s not in %s" % (where, node, rel))
            for v in kv.get("texture", []):
                checked += 1
                file_check(textures, "textures/%s.png" % v, "texture", where)
        elif kind == "fixing":
            for key in ("require", "fixer"):
                for v in kv.get(key, []):
                    ref = v.split(";")[0].strip()
                    checked += 1
                    if not resolve("item", ref, module):
                        errors.append("%s: %s item %s not found" % (where, key, ref))
        elif kind == "craftRecipe":
            body = " ".join(kv.get("_lines", []))
            body = re.sub(r"tags\[[^\]]*\]", "", body)
            for ref in set(re.findall(r"\b([A-Za-z]\w*\.[A-Za-z0-9_]+)\b", body)):
                if ref.split(".")[0] in ("Base", "GunsOfTien", "GunsOfTienPost93", "MarzGuns", "SWMG", "ammomaker"):
                    checked += 1
                    if not resolve("item", ref, module):
                        errors.append("%s: item %s not found" % (where, ref))
    # AnimSet clips
    for root in OURS:
        for xml in glob.glob(os.path.join(root, "AnimSets", "**", "*.xml"), recursive=True):
            for clip in re.findall(r"<m_AnimName>([^<]+)</m_AnimName>", open(xml, encoding="utf-8").read()):
                checked += 1
                hits = [k for k in anims if os.path.splitext(os.path.basename(k))[0] == clip.lower()]
                if not hits:
                    errors.append("AnimSet %s: clip %s not found in any anims_X" % (os.path.basename(xml), clip))
    print("checked %d references in %d script blocks" % (checked, len(ours)))
    for n in sorted(set(notes)):
        print("note:", n)
    for e in sorted(set(errors)):
        print("ERROR:", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
