"""
AnimSet nodes for the compact SMG stance (CLAUDE.md "Compact SMG stance"), generated from vanilla's rifle nodes:

    python3 scripts/anim/compact_animsets.py <vanilla media/AnimSets> <clip dir with <Set>/*.x> <out media root> <Set> ...

Per set and per vanilla node in NODES: the node flattened exactly as the game resolves `x_extends` (PZXmlUtil.resolve,
42.21: a child element replaces the parent's of the same tag and x_name, an unnamed one the parent's of the same tag
at the same position among that tag, the rest is appended), then renamed `<name>_GoTCompact<Set>`, every clip we built
swapped for ours (clips we did not build stay vanilla's), the Gunworks grip condition `GunworksGripAnim == <animId>`
added with `m_ConditionPriority` 100 (Heavy Ordnance's way), and every transition aimed at a node we replace copied to
aim at our node too. Written to <out media root>/AnimSets/player/<state>/<file>_GoTCompact<Set>.xml.
"""

import copy
import os
import re
import sys
import xml.etree.ElementTree as ET

# (state folder, vanilla file): the stance's nodes
NODES = [
    ("idle", "IdleRifle.xml"), ("idle", "sneakidleRifle.xml"), ("idle", "sneakIdleLowRifle.xml"),
    ("aim", "aim_rifle.xml"), ("aim-strafe", "aim_rifle.xml"),
    ("strafe", "strafeRifle.xml"), ("strafe", "strafeRifleSlow.xml"),
    ("ranged/firearm", "FirearmDefault.xml"), ("ranged/firearm", "FirearmAuto.xml"),
    ("ranged/firearm", "FirearmBurst.xml"), ("ranged/firearm", "FirearmSingle.xml"),
    ("ranged/firearm", "FirearmEmpty.xml"), ("ranged/firearm", "FirearmEmptyAuto.xml"),
    ("ranged/firearm", "FirearmEmptyBurst.xml"), ("ranged/firearm", "FirearmEmptySingle.xml"),
    ("shoveAim/firearm", "FirearmDefault.xml"), ("shoveAim/firearm", "FirearmShove.xml"),
    ("shoveAim/firearm", "FirearmShoveBehind.xml"),
]
ANIM_ID = "GunsOfTien_Compact%s"
# Guns modelled upside down (pistol models) are turned upright in the hand by a Bip01_Prop1 point on their model
# (CompactStance.lua). The game shoots from the gun bone and the model's `muzzle` point without that turn
# (BallisticsController.calculateMuzzlePosition -> ModelInstance.getAttachmentWorldPosition), so a turn about the
# model's Y axis put the tracers' start 2 x the muzzle's height off the drawn barrel. They are turned about their bore
# instead (the point offset by 2 x the muzzle's z), and their sets' gun bone moved back by as much (compact_pack.py):
# set -> the guns' muzzle z (model space). UziT is the Uzi set for the turned guns that hold like the Uzi (the Mini Uzi
# z -0.0238, the MP7s folded / the A2 -0.0205: the mean, 3 mm either way); the full Uzi is modelled upright.
TURNED_SETS = {"UziT": -0.0222, "MP5K": -0.0445, "MP7": -0.0205}
SOURCE_SET = {"UziT": "Uzi"}
PRIORITY = "100"


def parse(path):
    return ET.parse(path).getroot()


def is_text_only(e):
    return len(e) == 0 and (e.text or "").strip() != ""


def resolve(child, parent):
    """PZXmlUtil.resolve: attributes merged (child wins), elements matched by tag + x_name, or by tag + index."""
    if is_text_only(child):
        return copy.deepcopy(child)
    out = ET.Element(child.tag)
    for k, v in parent.attrib.items():
        out.set(k, v)
    for k, v in child.attrib.items():
        out.set(k, v)
    table = []          # [tag, name, element, index]

    def add(tbl, e):
        idx = sum(1 for t in tbl if t[0] == e.tag)
        entry = [e.tag, e.get("x_name") or "", e, idx]
        tbl.append(entry)
        return entry

    for e in parent:
        add(table, copy.deepcopy(e))
    child_tbl = []
    for e in child:
        add(child_tbl, copy.deepcopy(e))
    for tag, name, e, idx in child_tbl:
        if name:
            match = next((t for t in table if t[0] == tag and t[1] == name), None)
        else:
            match = next((t for t in table if t[0] == tag and t[3] == idx), None)
        if match is None:
            add(table, e)
        else:
            match[2] = resolve(e, match[2])
    for t in table:
        out.append(t[2])
    return out


def find_extended(path, ext, roots=()):
    """An x_extends target: next to the file (with or without .xml), else at the same place under another AnimSets
    root (a mod's node extending vanilla's or another mod's)."""
    here = os.path.dirname(path)
    for root in (None,) + tuple(roots):
        d = here if root is None else os.path.join(root, os.path.relpath(here, roots_base(path, roots)))
        for name in (ext, ext + ".xml"):
            if os.path.isfile(os.path.join(d, name)):
                return os.path.join(d, name)
    raise FileNotFoundError("x_extends %s of %s" % (ext, path))


def roots_base(path, roots):
    """The AnimSets root a node file lies under (the folder holding its player / player-vehicle folder)."""
    d = os.path.dirname(path)
    while os.path.basename(d) not in ("player", "player-vehicle") and os.path.dirname(d) != d:
        d = os.path.dirname(d)
    return os.path.dirname(d)


def load_resolved(path, roots=()):
    root = parse(path)
    ext = root.get("x_extends")
    if ext:
        parent = load_resolved(find_extended(path, ext, roots), roots)
        root = resolve(root, parent)
    if "x_extends" in root.attrib:
        del root.attrib["x_extends"]
    return root


FIREARM = ("Weapon", "firearm")
# Gunworks' own shooting nodes: it sets FireMode to RealSingle / RealAuto / RealBurst for every gun it fires, so
# vanilla's FirearmSingle / Auto / Burst / Empty* (FireMode Single / Auto / Burst / "") never play with it and these
# do (vanilla rifle clips, Weapon == firearm). Without our copies, shooting and dry firing put the left hand back on
# vanilla's rifle place.
MOD_ANIMSETS = [os.environ.get("GUNWORKS_ANIMSETS") or os.path.expanduser(
    "~/Library/Application Support/Steam/steamapps/workshop/content/108600/3722064198/mods/Gunworks_gang_framework/"
    "42.13/media/AnimSets")]


# Rifle nodes with no Weapon condition: their state is only entered with a gun (the game picks shoveWithFirearm for a
# shove that is not aimed), so they would play vanilla's rifle clip with vanilla's left hand.
GUN_STATE_NODES = [("player", "shoveWithFirearm/firearm/FirearmShoveNoAim.xml")]


def firearm_nodes(vanilla_root):
    """Every vanilla node (player and player-vehicle) whose resolved conditions hold Weapon == firearm, as
    (anim set, state folder, file, resolved root). 248 in 42.21, plus Gunworks' 6 (MOD_ANIMSETS) and GUN_STATE_NODES."""
    out = []
    for root in [vanilla_root] + MOD_ANIMSETS:
        if root != vanilla_root and not os.path.isdir(root):
            raise SystemExit("Gunworks AnimSets not found: %s (set GUNWORKS_ANIMSETS)" % root)
        out += _firearm_nodes(root, [vanilla_root])
    for anim, rel in GUN_STATE_NODES:
        path = os.path.join(vanilla_root, anim, rel)
        out.append((anim, os.path.dirname(rel), os.path.basename(rel), load_resolved(path)))
    return out


def _firearm_nodes(animsets_root, fallback=()):
    out = []
    for anim in ("player", "player-vehicle"):
        base = os.path.join(animsets_root, anim)
        for d, _, fs in os.walk(base):
            for f in sorted(fs):
                if not f.endswith(".xml"):
                    continue
                try:
                    r = load_resolved(os.path.join(d, f), fallback)
                except FileNotFoundError:
                    if not fallback:
                        raise
                    continue        # a mod node extending one we do not have (Gunworks' spear nodes)
                conds = [(c.findtext("m_Name"), c.findtext("m_Value") or c.findtext("m_StringValue"))
                         for c in r.findall("m_Conditions")]
                if FIREARM in conds:
                    out.append((anim, os.path.relpath(d, base), f, r))
    return out


def firearm_clips(vanilla_root):
    """The clips played while a two-handed gun is held: each firearm node's own clips (main and 2D blends) and its
    transitions into other firearm nodes or with no target. clip -> set of "anim/state" it plays in."""
    nodes = firearm_nodes(vanilla_root)
    # node names match ignoring case (AnimNode; vanilla's transitions say "walkRifle" / "sneakIdleRifle" for the
    # nodes "walkrifle" / "sneakidleRifle")
    names = {r.findtext("m_Name").lower() for _, _, _, r in nodes}
    clips = {}
    for anim, state, f, r in nodes:
        where = anim + "/" + state
        for e in [r] + r.findall("m_2DBlends"):
            a = (e.findtext("m_AnimName") or "").strip()
            if a:
                clips.setdefault(a, set()).add(where)
        for t in r.findall("m_Transitions"):
            tgt, a = t.findtext("m_Target"), (t.findtext("m_AnimName") or "").strip()
            if a and (not tgt or tgt.lower() in names):
                clips.setdefault(a, set()).add(where)
    return clips


def node_names(vanilla_root):
    """vanilla node name -> (state, file) for every node we replace (to re-aim transitions)."""
    out = {}
    for state, f in NODES:
        r = load_resolved(os.path.join(vanilla_root, "player", state, f))
        n = r.findtext("m_Name")
        if n:
            out[n] = (state, f)
    return out


def indent(e, level=0):
    pad = "\n" + "\t" * level
    if len(e):
        if not (e.text or "").strip():
            e.text = pad + "\t"
        for c in e:
            indent(c, level + 1)
        if not (c.tail or "").strip():
            c.tail = pad
    if level and not (e.tail or "").strip():
        e.tail = pad


GENERIC_NAME = re.compile(r"Rifle|Shotgun|SGun|Sgun|Firearm", re.I)
CONTEXTS = ("Stand", "Sneak", "Ground", "Chair")


def node_masks(r):
    """A node's bone masks: bone -> weight (an empty weight is 1)."""
    out = {}
    for w in r.findall("m_SubStateBoneWeights"):
        b = (w.findtext("boneName") or "").strip()
        if b:
            out[b] = float((w.findtext("weight") or "1").strip() or "1")
    return out


def node_context(state, r):
    """The state a masked node plays over, which keeps the gun bone (weight 0) and the unmasked bones: the standing
    idle, the sneak idle, sitting on the ground or in a chair."""
    conds = {(c.findtext("m_Name") or "").strip(): (c.findtext("m_Value") or c.findtext("m_StringValue") or "").strip()
             for c in r.findall("m_Conditions")}
    top = state.replace("\\", "/").split("/")[0]
    if conds.get("sneaking") == "true":
        return "Sneak"
    if top == "sitext":
        return "Ground" if conds.get("sitonground") == "true" else "Chair"
    return "Stand"


def generic_variants(vanilla_root):
    """Masked nodes playing a generic clip (no gun in its name: gestures, pains, signals, the 2H / 1H ones). The game
    blends such a clip over the state underneath by the node's masks and takes the gun from that state, so a clip is
    built once per (context, masks) it plays with (user, 2026-10-24: crouched emotes pulled the hands 14-25 cm off
    the gun). clip -> [(suffix, context, masks)]; suffix "__<Context>", "__<Context>2" for a second mask set there."""
    seen = {}
    for anim, state, f, r in firearm_nodes(vanilla_root):
        masks = node_masks(r)
        if not masks:
            continue
        ctx = node_context(state, r)
        for e in [r] + r.findall("m_2DBlends"):
            a = (e.findtext("m_AnimName") or "").strip()
            if a and not GENERIC_NAME.search(a):
                key = (ctx, tuple(sorted(masks.items())))
                seen.setdefault(a, {}).setdefault(key, masks)
    out = {}
    for clip, keys in seen.items():
        rows, count = [], {}
        for (ctx, mk) in sorted(keys, key=lambda k: (CONTEXTS.index(k[0]), k[1])):
            count[ctx] = count.get(ctx, 0) + 1
            rows.append(("__%s%s" % (ctx, "" if count[ctx] == 1 else count[ctx]), ctx, keys[(ctx, mk)]))
        out[clip] = rows
    return out


def build(vanilla_root, clip_dir, out_root, set_name):
    """Every firearm node (firearm_nodes: player and player-vehicle) for the set, its clips swapped for the built ones
    (the set's manifest.txt from compact_build.py)."""
    src_set = SOURCE_SET.get(set_name, set_name)
    built = [l.strip() for l in open(os.path.join(clip_dir, src_set, "manifest.txt")) if l.strip()]
    src_prefix, prefix = "GunsOfTien_Compact%s_" % src_set, "GunsOfTien_Compact%s_" % set_name
    swap = {"Bob_" + n[len(src_prefix):]: prefix + n[len(src_prefix):] for n in built if n.startswith(src_prefix)}
    suffix = "_GoTCompact%s" % set_name
    nodes = firearm_nodes(vanilla_root)
    variants = generic_variants(vanilla_root)
    ours = {r.findtext("m_Name").lower(): r.findtext("m_Name") for _, _, _, r in nodes}
    written = []
    for anim, state, f, r in nodes:
        r = copy.deepcopy(r)
        name = r.findtext("m_Name")
        r.find("m_Name").text = name + suffix
        # a generic clip in a masked node: its own copy for this node's context and masks (built when the manifest
        # has it); a generic clip anywhere else (a transition) takes its first copy
        masks = node_masks(r)
        key = (node_context(state, r), tuple(sorted(masks.items())))
        own = set(id(e) for e in [r] + r.findall("m_2DBlends"))
        for e in r.iter():
            a = (e.findtext("m_AnimName") or "").strip() if e.find("m_AnimName") is not None else ""
            if a not in variants:
                continue
            rows = variants[a]
            pick = rows[0][0]
            if id(e) in own and masks:
                pick = next((sfx for sfx, ctx, mk in rows if (ctx, tuple(sorted(mk.items()))) == key), pick)
            nm = prefix + a[4:] + pick if a.startswith("Bob_") else prefix + a + pick
            if (src_prefix + nm[len(prefix):]) in built:
                e.find("m_AnimName").text = nm
        # our clips
        for e in r.iter("m_AnimName"):
            if e.text and e.text.strip() in swap:
                e.text = swap[e.text.strip()]
        # the grip condition and the priority (inserted after m_AnimName, where HO has them)
        pri = r.find("m_ConditionPriority")
        if pri is None:
            pri = ET.Element("m_ConditionPriority")
            r.insert(2, pri)
        pri.text = PRIORITY
        cond = ET.Element("m_Conditions")
        ET.SubElement(cond, "m_Name").text = "GunworksGripAnim"
        ET.SubElement(cond, "m_Type").text = "STRING"
        ET.SubElement(cond, "m_StringValue").text = ANIM_ID % set_name
        first_cond = next((i for i, c in enumerate(list(r)) if c.tag == "m_Conditions"), len(r))
        r.insert(first_cond, cond)
        # transitions into nodes we replace: a copy aimed at ours
        for i, t in reversed(list(enumerate(list(r)))):
            if t.tag != "m_Transitions":
                continue
            tgt = t.findtext("m_Target")
            if tgt and tgt.lower() in ours:
                t2 = copy.deepcopy(t)
                t2.find("m_Target").text = ours[tgt.lower()] + suffix
                r.insert(i + 1, t2)
        for e in r.iter():
            if "x_name" in e.attrib:
                del e.attrib["x_name"]
        indent(r)
        d = os.path.join(out_root, "AnimSets", anim, state)
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, f[:-4] + suffix + ".xml")
        with open(out, "wb") as fh:
            fh.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            fh.write(ET.tostring(r, encoding="utf-8"))
        written.append(out)
    return written


if __name__ == "__main__":
    vanilla_root, clip_dir, out_root = sys.argv[1:4]
    for set_name in sys.argv[4:]:
        for path in build(vanilla_root, clip_dir, out_root, set_name):
            print("[animsets] wrote", path)


# ---- reload actions (smg_reload.py's compact specs; Gunworks' WeaponReloadType = the handler's animId) ----
RELOAD_ID = "GunsOfTienCompact%s"
# frames of smg_reload.py's clips: Unload 36 (the magazine off the gun at 10), Load 45 (seated at 30), Rack / AimRack
# 36 (on the handle 12, back 19, let go 22)
RELOAD_NODES = {
    "Unload": dict(clip="Unload", cond=("isUnloading", "true"), blend="0.20", events=[
        ("unloadFinished", "End", None, ""), ("playReloadSound", "Start", None, "ejectAmmoStart"),
        ("changeWeaponPart", "Percentage", 10 / 36.0, "mag"), ("playReloadSound", "Percentage", 10 / 36.0, "unload")]),
    "Load": dict(clip="Load", cond=("isLoading", "true"), blend="0.20", events=[
        ("loadFinished", "End", None, ""), ("playReloadSound", "Start", None, "insertAmmoStart"),
        ("changeWeaponPart", "Percentage", 30 / 45.0, "mag"), ("playReloadSound", "Percentage", 30 / 45.0, "load")]),
    "Rack": dict(clip="Rack", cond=("isRacking", "true"), blend="0.10", events=[
        ("rackingFinished", "End", None, ""), ("playReloadSound", "Percentage", 12 / 36.0, "rack"),
        ("rackStart", "Percentage", 12 / 36.0, ""),
        # rackBullet before ejectCasing (Hot Brass reads the round the bolt just took)
        ("rackBullet", "Percentage", 19 / 36.0, ""), ("ejectCasing", "Percentage", 19.2 / 36.0, ""),
        ("rackEnd", "Percentage", 22 / 36.0, "")]),
}


def reload_node(set_name, kind, aim=False, idle_sets=()):
    spec = RELOAD_NODES[kind]
    r = ET.Element("animNode")
    ET.SubElement(r, "m_Name").text = "%s%s%s" % (kind, "Aim" if aim else "", RELOAD_ID % set_name)
    ET.SubElement(r, "m_AnimName").text = "GunsOfTien_Compact%s_Reload%s" % (set_name, "AimRack" if aim else spec["clip"])
    for tag, text in (("m_deferredBoneAxis", "Y"), ("m_Looped", "false"), ("m_SyncTrackingEnabled", "false"),
                      ("m_EarlyTransitionOut", "true"), ("m_SpeedScale", "ReloadSpeed"),
                      ("m_BlendTime", spec["blend"]), ("m_ConditionPriority", "10")):
        ET.SubElement(r, tag).text = text
    conds = [("PerformingAction", "STRING", "Reload"), ("WeaponReloadType", "STRING", RELOAD_ID % set_name),
             (spec["cond"][0], "BOOL", spec["cond"][1])]
    if aim:
        conds.append(("RackAiming", "BOOL", "true"))
    for name, typ, val in conds:
        c = ET.SubElement(r, "m_Conditions")
        ET.SubElement(c, "m_Name").text = name
        ET.SubElement(c, "m_Type").text = typ
        ET.SubElement(c, "m_StringValue" if typ == "STRING" else "m_BoolValue").text = val
    for ev, when, pc, param in spec["events"]:
        e = ET.SubElement(r, "m_Events")
        ET.SubElement(e, "m_EventName").text = ev
        ET.SubElement(e, "m_Time").text = when
        if pc is not None:
            ET.SubElement(e, "m_TimePc").text = "%.3f" % pc
        ET.SubElement(e, "m_ParameterValue").text = param
    if aim:
        # back to the stance's idle (every stance this gun can be in), through its own aim-to-idle clip
        for s in idle_sets:
            t = ET.SubElement(r, "m_Transitions")
            ET.SubElement(t, "m_Target").text = "IdleRifle_GoTCompact%s" % s
            ET.SubElement(t, "m_AnimName").text = "GunsOfTien_Compact%s_AimToIdle_Rifle" % s
            ET.SubElement(t, "m_blendInTime").text = "0.5"
            ET.SubElement(t, "m_blendOutTime").text = "0.5"
            ET.SubElement(t, "m_speedScale").text = "1.3"
    indent(r)
    return r


def write_reload_nodes(out_root, set_name, idle_sets):
    out = []
    for anim in ("player", "player-vehicle"):
        d = os.path.join(out_root, "AnimSets", anim, "actions")
        os.makedirs(d, exist_ok=True)
        for kind, aim in (("Unload", False), ("Load", False), ("Rack", False), ("Rack", True)):
            r = reload_node(set_name, kind, aim, idle_sets)
            path = os.path.join(d, "%s%s%s_GoT.xml" % (kind, "Aim" if aim else "", RELOAD_ID % set_name))
            with open(path, "wb") as fh:
                fh.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
                fh.write(ET.tostring(r, encoding="utf-8"))
            out.append(path)
    return out
