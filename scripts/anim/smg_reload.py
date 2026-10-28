"""
Reload clips for the full-size Uzi and Guns of Marz's MP5K (Blender 5.2, headless), built with TienInspectWeapon's
animation pipeline (as scripts/anim/m249_reload.py and Post-93's p90_reload.py).

    blender -b --factory-startup -P scripts/anim/smg_reload.py -- <vanilla anims_X/Bob> <out_dir> <gun> [clip ...] [--preview]

gun: uzi | mp5k. clips: Unload Load Rack AimRack (default: all). Writes
<out_dir>/Bob_GunsOfTien_<Uzi|MP5K>_<clip>.x (+ .blend); with --preview renders every 2nd frame with the gun in the
hand into <out_dir>/prev_<gun>_<clip>/ (TienInspectWeapon's sheet.py / gif.py lay them out). Ship the .x files to
Contents/mods/GoMExtensionGunsOfTien/42/media/anims_X/Bob/; the AnimSets *UziRifle_GoT.xml / *MP5K_GoT.xml play them.

Why (user, 2026-10-23): GoM's clips put the left hand where those guns' magazines are not. The Uzi is held as a
rifle but its magazine goes up the pistol grip, about 10 cm behind the MP5 well GoM's MP5 clips reach for; the MP5K
is held like a pistol, its magazine ahead of the trigger guard, and GoM's handgun2 clips do not meet it either.
- Unload: the gun comes up and is canted so the magazine faces the left hand, which takes the magazine by its body
  just under the well (every magazine of the gun shows there, from the shortest up: the hand grips that one place
  whatever is fitted), pulls it straight out along its axis and carries it away to the left hip.
- Load: the hand brings the new magazine up under the well, lines it up, pushes it home (the "load" click), gives it
  a tap and goes back to the support grip.
- Rack: the Uzi's knob on top, pulled back over the top with the left hand and let go (AimRack: the same without
  leaving the aim); the MP5K's cocking lever at the front of its tube on the left, pulled back and let go.
The magazine leaves the gun with the hand at the changeWeaponPart "mag" marker (SWAP): Gunworks' "attachments" style
shows it on Bip01_Prop2, keyed here in the left hand from / up to the swap (its offset taken at the swap frame, so
any magazine of the gun, its lips at the gun's `magazine` point, moves with the hand without a jump). The unload's
swap is the frame the hand closes on the magazine, before it pulls: a later swap (16, the first draft) left the
seated magazine behind while the hand slid down it, then swung it from the hand like a lever (user, 2026-10-23).
Every clip is checked against the body (TienInspectWeapon's clearance.py: arms by their bones, the gun and magazine
by their vertices) and reports what goes in.

Weapon space is the game's (the model scripts'): +Y the muzzle. The Uzi is rifle-held and upright (+Z top, +X its
left); the MP5K is pistol-held and modelled upside down (+Z its bottom, +X its right), as all of GoM's handgun-held guns.
"""

import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ANIM = os.environ.get("TIEN_ANIM") or os.path.normpath(os.path.join(ROOT, "..", "TienInspectWeapon", "scripts", "anim"))
sys.path.insert(0, ANIM)
import clearance  # noqa: E402
import pose  # noqa: E402
import rig  # noqa: E402
import x_export  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
import xanim  # noqa: E402
from rig import Key, ch, rot_of  # noqa: E402

MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
GOM = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                          "3722134990/mods/GunsOfMarz/42.16/media"),
                       "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                       "42.16/media") if os.path.isdir(p))
FPS = 30
# frames: GoM's magazine reload durations (unload 1.2, load 1.5, rack 1.2 s), as Uzi.lua / MP5K.lua register them
LENGTHS = {"Unload": 36, "Load": 45, "Rack": 36, "AimRack": 36}
SWAP = {"Unload": 10, "Load": 30}           # changeWeaponPart "mag" (AnimSets: 10/36 = 0.28, 30/45 = 0.67)
CLICK = {"Load": 30}                        # the load sound, the magazine seated


def mat_of(pt):
    rx, ry, rz = [math.radians(a) for a in pt.get("rotate", [0, 0, 0])]
    return (Matrix.Translation(Vector(pt["offset"])) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Rotation(ry, 4, 'Y')
            @ Matrix.Rotation(rz, 4, 'Z'))


# ==================================================================================================
# The two guns: points in weapon space (game units), the clips' places (character space)
# ==================================================================================================

def uzi_spec():
    p = json.load(open(os.path.join(ROOT, "scripts/uzi_points.json")))["UZI"]
    K = p["_extras"]["k"]
    L0, H0 = p["_extras"]["photo_origin_mm"]
    wp = lambda L, H, x=0.0: Vector((x * K, (L0 - L) * K, (H - H0) * K))
    # modelled for the pistol clips since 2026-10-28 (build_uzi.py): its points and mesh are turned half a turn about
    # Y, so the magazine point is turned back and the mesh drawn turned (model_turn); the places stay upright
    mag = FLIP @ mat_of(p["magazine"])
    down = (mag.to_3x3() @ Vector((0, 0, -1))).normalized()          # along the magazine, out of the well
    return dict(
        name="Uzi", rifle=True, points=p, mag_point=mag, out=down, model_turn=FLIP,
        # the magazine's axis 14 mm under the grip's bottom (H 46.5): every magazine shows there
        grab=wp(290.0, 46.5 - 14.0),
        # measured with SMG_CAL (hand_offset): the vanilla grip's hand centre lands this far from the axis point
        hold_fix=Vector((0.0023, 0.0427, 0.0233)),
        travel=0.085 * K / 0.00072,                                   # lips (H 142.5) clear of the grip (46.5)
        knob=wp(187.5, 221.0), knob_back=wp(187.5 + 70.0, 221.0),     # the cocking knob, pulled back 70 mm
        # the hand's turn on the knob at the racking place (weapon X, Y, Z degrees; scanned): straight over the top
        # it took a forearm twist of -100
        knob_turn=(-60, 30, 0),
        # under the right arm, muzzle forward-left, canted so the grip's bottom and the left side face the left hand
        # the gun settled to a moderate right wrist there (`wrist`): canted by the key alone, the right wrist sat at
        # -52/-49 the whole magazine change (user, 2026-10-23: "looks like the wrist is broken")
        work=dict(pos=ch(-0.02, 0.68, 0.10), along=ch(-0.45, 0.32, 0.83), top=ch(0.45, 0.88, -0.15), wrist=(-30, -20)),
        # racking (Rack only; AimRack stays in the aim): low in front of the belly, muzzle forward-left, canted a
        # little left, the chest turned right so the left hand reaches over the top without its arm crossing the
        # chest (the first draft's place, ch(0.05, 0.64, 0.14), put the left upper arm 7 cm into it; further out,
        # ch(0.10, 0.58, 0.20), held it at arm's length). Found by the same scan as the MP5K's, straight arms penalised.
        rack=dict(pos=ch(0.10, 0.57, 0.11), along=ch(-0.42, 0.28, 0.86), top=ch(-0.35, 0.90, 0.0), twist=15),
        away=ch(-0.15, 0.50, 0.08),               # the left hip, within the arm's reach (0.274 from the shoulder)
        fbx=os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_UZI.fbx"),
        nodes=["UZI_BODY", "UZI_BOLT", "UZI_STOCK_FOLDED"],
        mag_fbx=os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_UZI_magazines.fbx"),
        mag_node="9x19Magazine32_UZI",
    )


def mp5k_spec():
    # GoM's MP5K model script (models/weapons/smgs.txt): magazine point, the cocking lever's knob measured on
    # MP5K_BOLT (its left end: y 0.196-0.206, z -0.059), the well's bottom on MP5K_BODY (z 0.014, y 0.10-0.14).
    # Upside down: +Z is the gun's bottom, +X its right.
    mag = mat_of({"offset": [0.0, 0.1196, -0.0388], "rotate": [171.7924, 0.0, 180.0]})
    down = (mag.to_3x3() @ Vector((0, 0, -1))).normalized()
    well_s = (0.014 - mag.translation.z) / down.z                     # along the axis from the lips to the well
    return dict(
        name="MP5K", rifle=False, mag_point=mag, out=down,
        grab=mag.translation + down * (well_s + 0.010),                  # the axis, just under the well
        hold_fix=Vector((0.0044, 0.0524, -0.0181)),                       # measured as the Uzi's
        travel=well_s + 0.012,
        knob=Vector((-0.026, 0.201, -0.059)), knob_back=Vector((-0.026, 0.201 - 0.036, -0.059)),
        # held like a pistol, close in front of the chest and turned across it (the model's origin is at its rear
        # end, the well 0.12 and the lever 0.20 ahead of it, so further out both are beyond the left hand's reach),
        # muzzle to the left, canted so the well faces the left hand
        # (higher, nearer the middle and less across than the first draft's ch(0.08, 0.64, 0.10), whose left arm went
        # 4 cm into the chest holding the magazine; found by the rack scan, the hand on the seated / drawn magazine)
        work=dict(pos=ch(0.04, 0.68, 0.10), along=ch(-0.55, 0.30, 0.78), top=ch(0.0, 1.0, 0.0), twist=15),
        # racking (from the idle or the aim): raised close in front of the right shoulder, muzzle forward and a
        # little left, the chest turned right (twist) so the left shoulder comes forward to the lever (0.20 ahead of
        # the grip, beyond the left hand in a full aim). Found by scanning places for reach, body clearance and
        # wrist strain at both ends of the pull. Rejected: across the belly, muzzle to the left (user, 2026-10-23:
        # "unacceptable"); drawn in at the chest (grip 0.06 forward, inside the chest's front: the left arm went
        # through the body, user: "just no").
        rack=dict(pos=ch(0.07, 0.72, 0.08), along=ch(-0.60, 0.20, 0.75), top=ch(0.0, 1.0, 0.0), twist=15),
        away=ch(-0.13, 0.52, 0.12),
        fbx=os.path.join(GOM, "models_X/weapons/firearms/MP5K.fbx"),
        nodes=["MP5K_BODY", "MP5K_BOLT"],
        mag_fbx=os.path.join(GOM, "models_X/weapons/magazines/smgs.fbx"),
        mag_node="9x19Magazine30_MP5",
    )


FLIP = Matrix.Rotation(math.pi, 4, 'Y')            # an upside-down (pistol) model turned upright in the hand
COMPACT = os.environ.get("SMG_COMPACT_DIR") or os.path.join(ROOT, "tmp", "anim", "full")


# scanned for the stance's hand relation (reach, wrists, clearance; scan.py MODE=work / rack on compact_uzi)
_UZI_WORK = dict(pos=ch(0.04, 0.70, 0.08), along=ch(-0.45, 0.32, 0.83), top=ch(0.45, 0.88, -0.15), twist=15)
_UZI_RACK = dict(pos=ch(0.10, 0.68, 0.10), along=ch(-0.20, 0.25, 0.95), top=ch(-0.35, 0.90, 0.0), twist=15)
COMPACT_PLACES = {("Uzi", "work"): _UZI_WORK, ("Uzi", "rack"): _UZI_RACK,
                  # the MP5K's approved places (pistol-held, 2026-10-23) carry over: the stance holds it with the
                  # same pistol hand relation; its work place as scanned again (the old one, chest turned 15)
                  ("MP5K", "work"): dict(pos=ch(0.04, 0.68, 0.10), along=ch(-0.55, 0.30, 0.78),
                                         top=ch(0.30, 0.90, -0.30), twist=15),
                  ("MP5K", "rack"): dict(pos=ch(0.07, 0.72, 0.08), along=ch(-0.60, 0.20, 0.75), top=ch(0.0, 1.0, 0.0),
                                         twist=15),
                  ("MP7", "work"): _UZI_WORK,
                  # its handle at the rear above the right hand: the muzzle turned up and right so the rear comes to
                  # the left hand (muzzle left, the left arm crossed the chest 4-5 cm into it)
                  ("MP7", "rack"): dict(pos=ch(0.08, 0.72, 0.14), along=ch(0.35, 0.45, 0.80), top=ch(-0.35, 0.90, 0.0),
                                        twist=0)}


def compact(spec, set_name, turned):
    """A spec for the compact SMG stance (CLAUDE.md "Compact SMG stance"): the gun held upright in both hands (the
    model scripts' Bip01_Prop1 point turns pistol-modelled guns a half turn about their length), the clips starting
    and ending in the set's own idle and aim (built by compact_build.py), named GunsOfTien_Compact<Set>_Reload<clip>."""
    g = dict(spec)
    if turned:
        R = FLIP.to_3x3()
        g["mag_point"] = FLIP @ g["mag_point"]
        g["out"] = (R @ g["out"]).normalized()
        for k in ("grab", "knob", "knob_back"):
            g[k] = FLIP @ g[k]
        g["hold_fix"] = R @ g["hold_fix"]
        g["model_turn"] = FLIP
    # the work / rack places were tuned for vanilla's rifle (or pistol) hand-to-gun relation; the stance holds the gun
    # with the pistol idle's, so a settled wrist turns it elsewhere: no settle, places from compact scans (COMPACT_PLACES)
    for key in ("work", "rack"):
        g[key] = {k: v for k, v in g[key].items() if k != "wrist"}
        g[key].update(COMPACT_PLACES.get((set_name, key), {}))
    d = os.path.join(COMPACT, set_name, "clips")
    g.update(rifle=True, name=set_name, clip_name="GunsOfTien_Compact%s_Reload%s",
             base=(os.path.join(d, "GunsOfTien_Compact%s_IdleRifle.x" % set_name),
                   os.path.join(d, "GunsOfTien_Compact%s_IdleAimRifle.x" % set_name)))
    return g


SHORT_ARMS = {c: 0.011 for c in ("Unload", "Load", "Rack", "AimRack")}


def short_family(spec, places, family, turned):
    """A reload family of the short SMG stance: `places`' work and rack places (compact()), started and ended in the
    stance's own idle and aim (the Uzi build), named GunsOfTien_Compact<family>_Reload<clip> as compact_pack.py packs
    them."""
    g = compact(spec, places, turned)
    d = os.path.join(COMPACT, "Uzi", "clips")
    g.update(name=family, base=(os.path.join(d, "GunsOfTien_CompactUzi_IdleRifle.x"),
                                os.path.join(d, "GunsOfTien_CompactUzi_IdleAimRifle.x")))
    return g


def mp7_spec():
    """Post-93's MP7A1, upside down as modelled (scripts/post93/mp7_points.json): its magazine goes up the grip as the
    Uzi's; the T charging handle at the rear top of the receiver (the MP7A1_BOLT node, y -0.076..-0.062, its top
    0.041-0.053 above the grip's top) is pulled back 0.036 (bolt_fired, 50 mm real)."""
    # resized in its meshes (build_mp7.py's K, 2026-10-26): points from the builder, the gun's own measured places
    # below (taken at 0.72) times s; hold_fix is the hand's contact offset, not the gun's
    pts = json.load(open(os.path.join(ROOT, "scripts/post93/mp7_points.json")))
    s = 1.0 / pts["_extras"]["real_mm_per_game_unit"] / 0.00072
    mag = mat_of({"offset": pts["magazine"]["offset"], "rotate": [-180.0, 0.0, -180.0]})
    down = (mag.to_3x3() @ Vector((0, 0, -1))).normalized()
    well_s = (0.0637 * s - mag.translation.z) / down.z                # the grip's bottom (BODY z max, upside down)
    P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
    return dict(
        name="MP7", rifle=False, mag_point=mag, out=down,
        grab=mag.translation + down * (well_s + 0.010 * s), hold_fix=Vector((0.0023, 0.0427, -0.0233)),   # the hand's own, not scaled
        travel=well_s + 0.012 * s,
        knob=Vector((0.0, -0.069, -0.047)) * s, knob_back=Vector((0.0, -0.069 - 0.036, -0.047)) * s,
        knob_turn=(-60, 30, 0),
        # its handle is at the rear, by the cheek in the aim: the aimed rack comes off the aim to rack, as a real
        # shooter does (in the aim the left hand went 8 cm into the face reaching for it)
        rack_in_aim=False,
        work=uzi_spec()["work"], rack=uzi_spec()["rack"], away=uzi_spec()["away"],
        fbx=os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_MP7A1.fbx"),
        nodes=["MP7A1_BODY", "MP7A1_BOLT"],
        mag_fbx=os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx"),
        mag_node="46x30Magazine30_MP7",
    )


def ump_spec():
    """Post-93's UMP45 / UMP9 (one body), rifle-held and upright (scripts/post93/ump_points.json): the magazine ahead of
    the trigger guard, tilted forward as it goes down; the charging handle on the left of the upper receiver's front
    (UMP_BOLT: y 0.186-0.198, z 0.040-0.046, x 0.011-0.018), pulled back 60 mm. Built 2026-10-26 when the UMPs were
    resized and GoM's MP5 reload clips (glTF, a rig with other bone axes) no longer met their well and handle."""
    p = json.load(open(os.path.join(ROOT, "scripts/post93/ump_points.json")))
    K = p["_extras"]["k"]
    mag = mat_of(p["magazine"])
    down = Vector((0.0, 0.030, -0.110)).normalized()                  # the 25-round's axis, lips to base
    s_grab = (mag.translation.z + 0.026) / -down.z                    # 8 mm under the well's bottom (z -0.018)
    P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
    knob = Vector((0.016, 0.192, 0.043))
    u = uzi_spec()
    return dict(
        name="UMP", rifle=True, points=p, mag_point=mag, out=down,
        grab=mag.translation + down * s_grab,
        hold_fix=u["hold_fix"],                                       # the rifle hand's own contact offset
        travel=s_grab + 0.010,
        knob=knob, knob_back=knob - Vector((0.0, 60.0 * K, 0.0)),
        knob_turn=(-60, 30, -45),
        work=u["work"], rack=u["rack"], away=u["away"],
        fbx=os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_UMP.fbx"),
        nodes=["UMP_BODY", "UMP_BOLT"],
        mag_fbx=os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_UMP_magazines.fbx"),
        mag_node="45Magazine25_UMP",
        # starts and ends in the UMP's own idle and aim (rifle_hand.py: vanilla's with the left palm moved back), and
        # is packed with them (compact_pack.py "UMP"); approved from the draft GIFs (user, 2026-10-26)
        clip_name="GunsOfTien_Compact%s_Reload%s",
        # the unload starts with the left hand where the idle has it, on the handguard: the magazine, 9 cm behind it,
        # was out of its reach on the first frame (2.3 cm short). No `contact` (de-clip reverted with the set, 2026-10-28)
        start_on_support=True,
        base=(os.path.join(ROOT, "tmp", "anim", "rifle", "UMP", "clips", "GunsOfTien_CompactUMP_IdleRifle.x"),
              os.path.join(ROOT, "tmp", "anim", "rifle", "UMP", "clips", "GunsOfTien_CompactUMP_IdleAimRifle.x")),
    )


# the bullpup stance (compact_build.py "Bullpup", draft B's carry, 2026-10-28; before it rifle_hand.py's set in
# tmp/anim/rifle/Bullpup)
BULLPUP_CLIPS = os.environ.get("BULLPUP_CLIPS") or os.path.join(ROOT, "tmp", "anim", "compact", "Bullpup", "clips")


def bullpup(name, **spec):
    """The bullpup set (docs/design.md 4h; user, 2026-10-27): reload clips starting and ending in the set's own idle and
    aim (rifle_hand.py "Bullpup"), one set of four per gun (their wells are 2 cm apart in height, their handles in
    different places), packed with the set (compact_pack.py). GoM's way: no magazine in the hand (user), the
    magazine only leaves the gun at the swap; the clips still key Bip01_Prop2, which the "none" style never shows."""
    u = uzi_spec()
    # the magazine change: the Uzi's place stood a full-length bullpup almost upright, muzzle by the face; a flatter
    # gun further out carried the well (behind the grip) out of the left hand's reach. First draft (2026-10-27):
    # ch(0, 0.62, 0.10), turned ~50 degrees up across the body, its rear against the chest. Moved out and up (user,
    # 2026-10-28: "more forward so that it doesn't go in the body", "we can also raise the gun higher"): straight out
    # alone lost the well again, raised it is in reach on every frame. The settle wrist decides how upright it
    # stands there: (-45, -35) chosen (user, option B) over no settle (tilted across, the right wrist bent 55
    # degrees the whole change) and the Uzi's (-30, -20) (upright, muzzle by the face). Both guns share it
    work = dict(u["work"], pos=ch(0.0, 0.70, 0.16), along=ch(-0.70, 0.15, 0.70), top=ch(0.30, 0.95, 0.0),
                wrist=(-45, -35))
    # racking: the Uzi's place 5 cm higher and 3 cm further out (user, 2026-10-28, no clipping: there the left arm
    # crossed the belly 1.3 cm deep reaching the FAMAS's lever, scanned with SMG_RACK)
    # On the bullpup stance (2026-10-28, its carry holds the grip with the pistol idle's relation, the barrel along
    # the forearm): that place left the right hand 4 cm short with the arm straight out; scanned with SMG_RACK,
    # ch(0.08, 0.60, 0.06) has every frame in reach, the fewest wrists past their range, arms and gun within 0.008
    rack = dict(u["rack"], pos=ch(0.08, 0.60, 0.06))
    g = dict(name=name, rifle=True, hold_fix=u["hold_fix"], work=work, rack=rack, away=u["away"],
             start_on_support=True, contact=0.008, clip_name="GunsOfTien_Compact%s_Reload%s",
             base=(os.path.join(BULLPUP_CLIPS, "GunsOfTien_CompactBullpup_IdleRifle.x"),
                   os.path.join(BULLPUP_CLIPS, "GunsOfTien_CompactBullpup_IdleAimRifle.x")))
    g.update(spec)
    return g


def aug_spec():
    """The main mod's Steyr AUG A1 (scripts/aug_points.json), rifle-held and upright: the magazine behind the grip,
    curving forward (8 degrees at the lips, ~10 at the well's mouth 13 mm under them); the charging handle on the left
    ahead of the scope (AUG_BOLT: y 0.100-0.121, z 0.024-0.043, x 0.011-0.018), pulled back 92 mm."""
    p = json.load(open(os.path.join(ROOT, "scripts/aug_points.json")))
    K = p["_extras"]["k"]
    L0, H0 = p["_extras"]["photo_origin_mm"]
    wp = lambda L, H, x=0.0: Vector((x * K, (L0 - L) * K, (H - H0) * K))
    mag = mat_of(p["magazine"])
    a = math.radians(9.5)
    down = Vector((0.0, math.sin(a), -math.cos(a)))
    s_grab = (13.0 + 10.0) * K                                         # 10 mm under the well's mouth
    knob = wp(272.0, 155.0, 18.0)
    # the bullpup family (built as the AUG's; CLAUDE.md "Animations are generic")
    return bullpup(
        "Bullpup", points=p, mag_point=mag, out=down, grab=mag.translation + down * s_grab,
        travel=s_grab + 0.010,
        knob=knob, knob_back=knob - Vector((0.0, -p["bolt_fired"]["offset"][1], 0.0)),
        knob_turn=(-60, 30, -45),                                      # the UMP's: a handle on the left, front
        fbx=os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_AUG.fbx"), nodes=["AUG_BODY", "AUG_BOLT"],
        mag_fbx=os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx"),
        mag_node="556x45Magazine30_AUG")


def famas_spec():
    """Guns of Marz's FAMAS (models/weapons/assault_rifles.txt), rifle-held and upright: the STANAG's lips at
    (0, -0.0763, 0.0146), the well's bottom at z -0.033 (FAMAS_BODY, y -0.08..-0.06); the cocking lever is the front of
    FAMAS_BOLT under the carry handle's bar (y 0.08-0.12, z 0.026-0.060, x within 0.004; the bar at z ~0.075), pulled
    back 0.061 (bolt_fired), reached from the left side as the AUG's."""
    mag = mat_of({"offset": [0.0, -0.0763, 0.0146]})
    down = Vector((0.0, 0.10, -1.0)).normalized()
    s_grab = (0.0146 + 0.033 + 0.008) / -down.z                        # 8 mm under the well's bottom
    knob = Vector((0.006, 0.100, 0.045))
    # its well is 2 cm lower than the AUG's: the first draft's place needed its own spot for it (2 cm higher and
    # closer); the raised one reaches both
    # its lever 2 cm further out still (at the AUG's place the left arm stayed 0.2 cm over its limit)
    rack = dict(uzi_spec()["rack"], pos=ch(0.10, 0.62, 0.16))
    return bullpup(
        "BullpupFAMAS", rack=rack, mag_point=mag, out=down, grab=mag.translation + down * s_grab, travel=s_grab + 0.010,
        knob=knob, knob_back=knob - Vector((0.0, 0.0611, 0.0)), knob_turn=(-60, 30, -45),
        fbx=os.path.join(GOM, "models_X/weapons/firearms/FAMAS.fbx"), nodes=["FAMAS_BODY", "FAMAS_BOLT"],
        mag_fbx=os.path.join(GOM, "models_X/weapons/magazines/assault_rifles.fbx"),
        mag_node="556x45Magazine30_STANAG")


SPECS = {"uzi": uzi_spec, "mp5k": mp5k_spec, "ump": ump_spec, "aug": aug_spec, "famas": famas_spec,
         "compact_uzi": lambda: compact(uzi_spec(), "Uzi", False),
         # the lever from the left side (the stance's "over the top" template turned ~half a turn; scanned at the rack place)
    "compact_mp5k": lambda: dict(compact(mp5k_spec(), "MP5K", True), knob_turn=(15, 165, -75),
                                 aim_knob_turn=(15, 165, -75)),
         "compact_mp7": lambda: compact(mp7_spec(), "MP7", True),
         # the short SMG stance's families (compact_pack.py RELOAD_SETS "ShortSMG"), each with its own places, all
         # starting and ending in the stance's idle and aim (the Uzi build, squared 2026-10-29)
         # the short SMG families' arms: both elbows swung out to the stance's own level (compact_build's arm_target,
         # vanilla's idle), the gun kept where it is (user, 2026-10-29: the rear T-handle rack's left arm went 3.6 cm
         # into the chest reaching across for the handle, "improve the arms here. they go inside the body"; then the
         # idle itself, "very close but doesn't clip")
         "short_pistol": lambda: dict(short_family(uzi_spec(), "Uzi", "ShortSMGPistol", False),
                                      arms_contact=SHORT_ARMS),
         "short_hk": lambda: dict(short_family(mp5k_spec(), "MP5K", "ShortSMGHK", True), knob_turn=(15, 165, -75),
                                  aim_knob_turn=(15, 165, -75), arms_contact=SHORT_ARMS),
         "short_reart": lambda: dict(short_family(mp7_spec(), "MP7", "ShortSMGRearT", True), arms_contact=SHORT_ARMS)}


# ==================================================================================================
# Rig and hand templates
# ==================================================================================================

HALF_TURN = Matrix.Rotation(math.pi, 4, 'Y')       # rifle space (top +Z) <-> handgun space (top -Z)


def base_clips(src_dir, g):
    """The idle and aim the clip starts / ends in: the compact stance's own (g["base"]: (idle path, aim path)) or
    vanilla's rifle / pistol ones."""
    if g.get("base"):
        return g["base"]
    idle, aim = ("Bob_IdleRifle.x", "Bob_IdleAimRifle.x") if g["rifle"] else ("Bob_IdleHandgun.X",
                                                                              "Bob_IdleAimHandgun.X")
    return os.path.join(src_dir, idle), os.path.join(src_dir, aim)


def build_rig(src_dir, g):
    idle, aim = base_clips(src_dir, g)
    xa = xanim.read(idle, with_mesh=True)
    base = pose.from_clip(xa, 0)
    aux = pose.copy(base)
    found = pose.from_clip(xanim.read(aim), 0)
    aux.update({b: m for b, m in found.items() if b in base})
    if g["rifle"]:
        r = rig.Rig(xa, base, aux=aux, poi=0.2, top=1, rest=x_import.rest_matrices(xa))
    else:
        r = rig.Rig(xa, base, aux=aux, poi=0.0, top=-1, support_from_aux=True, rest=x_import.rest_matrices(xa))

    def sample(clip, frame):
        p = pose.copy(base)
        p.update({b: m for b, m in pose.from_clip(xanim.read(os.path.join(src_dir, clip)), frame * 160).items()
                  if b in base})
        return p

    # holding a magazine by its body in the well: vanilla's rifle load, magazine in the well (frame 30; rifle space)
    mag_hold = r.sample_lgrip(sample("Bob_Reload_Rifle_Load.x", 30))
    # over the top, palm down: vanilla's handgun reload over the slide (frame 48; handgun space)
    over = r.sample_lgrip(sample("Bob_Reload_Handgun.X", 48))
    if g["rifle"]:
        over = HALF_TURN @ over
    else:
        mag_hold = HALF_TURN @ mag_hold
    belt_world = pose.world(xa, sample("Bob_Reload_Handgun.X", 16))["Bip01_L_Hand"]
    support = r.support_base if g["rifle"] else r.support_aux
    # vanilla's magazine (Bip01_Prop2) sits on the hand bone, the wrist, beside the magazine it holds: in the rifle
    # load's frame the magazine's axis runs on the weapon's centre line (x 0) at the wrist's height and depth
    return xa, r, {"mag": mag_hold, "over": over, "support": support, "belt_world": belt_world}


def palm(template):
    """The middle of the palm in the template's weapon space (the hand bone runs along its local X to the fingers)."""
    return template @ Vector((0.045, 0.0, 0.012))


def grip_mag(template, at, rot=(0.0, 0.0, 0.0)):
    """The magazine hold with vanilla's magazine axis (x 0 at the wrist's y and z, in its weapon space) moved onto
    `at`, a point on our magazine's axis, the hand turned by `rot` (degrees, weapon X, Y, Z) about it."""
    contact = Vector((0.0, template.translation.y, template.translation.z))
    R = (Matrix.Rotation(math.radians(rot[0]), 3, 'X') @ Matrix.Rotation(math.radians(rot[1]), 3, 'Y')
         @ Matrix.Rotation(math.radians(rot[2]), 3, 'Z'))
    q = (R @ template.to_3x3()).to_quaternion()
    return Matrix.LocRotScale(at + R @ (template.translation - contact), q, None)


def grip_on(template, at, rot=(0.0, 0.0, 0.0)):
    """A left-hand placement with the template's palm on `at` (weapon space), turned by `rot` (degrees about the
    weapon's X, Y, Z) about that point."""
    R = (Matrix.Rotation(math.radians(rot[0]), 3, 'X') @ Matrix.Rotation(math.radians(rot[1]), 3, 'Y')
         @ Matrix.Rotation(math.radians(rot[2]), 3, 'Z'))
    q = (R @ template.to_3x3()).to_quaternion()
    return Matrix.LocRotScale(at + R @ (template.translation - palm(template)), q, None)


def weapon_at(r, place):
    return r.weapon_at(dict(at_aux=0.0, top=place["top"], along=place["along"], face=None, pos=place["pos"],
                            roll=0.0, turn=0.0, drop=0.0, pitch=0.0), r.eye0)


def weapon_landed(r, place, look=0.85, lean=5, aux=0.15):
    """Where the gun really is at `place`: the rig lets it give way where the right wrist would bend too far, so a
    hand target worked out from weapon_at alone (relative to the gun) lands elsewhere (8 cm off at the Uzi's hip)."""
    n, nw, nr = len(r.swivels), len(r.wrist_warnings), len(r.warnings)
    s = dict(look=look, lean=lean, aux=aux, support=0.0, elbow=0.0, twist=place.get("twist", 0.0))
    Wk = weapon_at(r, place)
    if place.get("wrist"):
        Wk = r.settle(Wk, dict(s, wrist=place["wrist"]))
    W = pose.world(r.xa, r.pose_for(Wk, s, 0, (0, None), 1))["Bip01_Prop1"]
    del r.swivels[n:], r.wrist_warnings[nw:], r.warnings[nr:]
    return W


def hand_away(r, g, place, held):
    """The left hand at the hip holding the magazine it drew out (`held`, weapon -> hand at the work place), its
    wrist settled to its natural bend there (keeping the forearm's twist): kept at the pull-out's angle all the way
    down, the wrist ended bent 55 degrees (user, 2026-10-23: "looks like the wrist is broken"). The magazine stays
    rigid in the hand, so it turns with the hand rather than round it."""
    W = weapon_landed(r, place)
    lg = W.inverted() @ Matrix.LocRotScale(g["away"], (W @ held).to_quaternion(), None)
    n, nw, nr = len(r.swivels), len(r.wrist_warnings), len(r.warnings)
    s = dict(look=0.85, lean=5, aux=0.15, support=1.0, elbow=0.0, twist=place.get("twist", 0.0))
    Wk = weapon_at(r, place)
    if place.get("wrist"):
        Wk = r.settle(Wk, dict(s, wrist=place["wrist"]))
    p = r.pose_for(Wk, s, 0, (0, None), 1, lgrip=lg)
    r.set_wrist(p, "L", 0.0, 0.0, r.wrist_angles(p, "L")[2])
    hand = pose.world(r.xa, p)["Bip01_L_Hand"]
    del r.swivels[n:], r.wrist_warnings[nw:], r.warnings[nr:]
    return W.inverted() @ Matrix.LocRotScale(g["away"], hand.to_quaternion(), None)


# ==================================================================================================
# Keys
# ==================================================================================================

def keys_for(clip, r, g, grips):
    sup = grips["support"]
    fix = Vector() if os.environ.get("SMG_CAL") == "raw" else g["hold_fix"]     # SMG_CAL=raw measures it again
    on_mag = lambda s, rot=(0, 0, 0): grip_mag(grips["mag"], g["grab"] + g["out"] * s - fix, rot)
    over = lambda at, rot=(0, 0, 0): grip_on(grips["over"], at, rot)
    n = LENGTHS[clip]
    W = dict(look=0.85, lean=5, aux=0.15, **g["work"])
    # the pistol idle's left hand hangs free, away from the gun at the right thigh (reaching for it put the arm
    # through the belly). Its hand stays on IK and is steered from / to exactly where the idle's hangs (`free`,
    # relative to the gun at the idle): fading between the free arm and a raised one in a few frames read as a
    # snap (user, 2026-10-23, the MP5K rack's let-go)
    free = r.support_base
    # the idle's own top and no wrist settling (keys carry what they leave out: top=None kept the racking place's
    # "top up", and the gun ended its rack turned across the thigh; `()` turns a carried `wrist` off)
    idle = dict(look=0, lean=0, aux=0, pos=r.weapon0.translation, along=rot_of(r.weapon0) @ Vector((0, 1, 0)),
                top=rot_of(r.weapon0) @ Vector((0, 0, r.top_sign)), face=rot_of(r.weapon0) @ Vector((1, 0, 0)),
                wrist=(), twist=0)
    t = g["travel"]
    if clip == "Unload":
        away = hand_away(r, g, g["work"], on_mag(t))
        return [
            Key(0, look=0, lean=0, support=0, lgrip=on_mag(0.02)) if g["rifle"] and not g.get("start_on_support") else
            Key(0, look=0, lean=0, support=1, lgrip=free),
            Key(8, support=1, lgrip=on_mag(0.008), ease=True, **W),                # under the well
            Key(SWAP["Unload"], lgrip=on_mag(0.0)),                                 # on the magazine, the release
            Key(17, lgrip=on_mag(t), ease=True),                                    # pulled out clear
            Key(n, lgrip=away, ease=True),                                          # away to the hip
        ]
    if clip == "Load":
        away = hand_away(r, g, g["work"], on_mag(t))
        if not g["rifle"]:
            return [
                Key(0, support=1, lgrip=away, ease=True, **W),
                Key(14, lgrip=on_mag(t + 0.012, (0, 0, 6)), ease=True),
                Key(21, lgrip=on_mag(t * 0.6)),
                Key(SWAP["Load"], lgrip=on_mag(0.0), ease=True),
                Key(33, lgrip=on_mag(0.006)),
                Key(36, lgrip=on_mag(-0.002)),
                Key(39, lgrip=on_mag(0.02)),                                        # the hand leaves the gun
                Key(n, lgrip=free, ease=True, **idle),
            ]
        return [
            Key(0, support=1, lgrip=away, ease=True, **W),
            Key(14, lgrip=on_mag(t + 0.012, (0, 0, 6)), ease=True),                # lined up under the well
            Key(21, lgrip=on_mag(t * 0.6)),                                         # the lips in the well
            Key(SWAP["Load"], lgrip=on_mag(0.0), ease=True),                        # pushed home: the click
            Key(33, lgrip=on_mag(0.006)),
            Key(36, lgrip=on_mag(-0.002)),                                          # a tap on it
            # back to the support grip as the gun comes down (taken at the canted work place first, the left wrist
            # bent 68 degrees)
            Key(n, lgrip=sup, ease=True, **idle),
        ]
    if clip in ("Rack", "AimRack"):
        place = g["rack"]
        R = dict(look=0.8, lean=4, aux=0.15, **place)
        side = (0, 0, 0) if g["rifle"] else (0, 90, 0)        # the Uzi's knob from above, the MP5K's lever from the left
        if clip == "Rack" and g.get("knob_turn"):
            side = g["knob_turn"]
        if clip == "AimRack" and g.get("aim_knob_turn"):
            side = g["aim_knob_turn"]
        if clip == "Rack":
            hang = sup if g["rifle"] else free
            first = Key(0, support=1, lgrip=hang, ease=True, **idle)
            last = Key(n, support=1, lgrip=hang, ease=True, **idle)
        else:
            first = Key(0, support=1, lgrip=sup, ease=True, at_aux=True, aux=1.0, look=0, lean=0)
            last = Key(n, lgrip=sup, ease=True, at_aux=True, aux=1.0, look=0, lean=0, twist=0)
        # AimRack stays in the aim (the knob / lever is in reach of the left hand there); Rack brings the gun in
        aimed = clip == "AimRack" and g["rifle"] and g.get("rack_in_aim", True)
        R = dict(at_aux=True, aux=1.0, look=0, lean=0) if aimed else R
        A = dict(at_aux=True, aux=1.0) if aimed else {}
        keys = [
            first,
            Key(12, support=1, lgrip=over(g["knob"], side), ease=True, **R),        # on the knob (rackStart)
            Key(19, lgrip=over(g["knob_back"], side), ease=True, **A),              # all the way back
            Key(22, lgrip=over(g["knob_back"] + Vector((0, 0.004, 0)), side), **A),  # let go: it flies forward
            Key(30, lgrip=sup, ease=True, **A),
            last,
        ]
        if not aimed:
            # straight from the let-go back to the idle or the aim, the hand going to its grip on the way: the
            # support grip at the racking place is out of reach (Uzi) or crosses the left arm over the chest (MP5K)
            keys = keys[:4] + keys[5:]
        return keys
    raise ValueError(clip)


def key_prop2(xa, poses, g, swap, in_hand_after):
    """Bip01_Prop2 (Gunworks' reload magazine) on every pose: at the gun's magazine point, or, on the hand's side of
    the swap, in the left hand with the offset it has at the swap frame."""
    M = g["mag_point"]
    w = pose.world(xa, poses[swap])
    offset = w["Bip01_L_Hand"].inverted() @ (w["Bip01_Prop1"] @ M)
    for f, p in enumerate(poses):
        w = pose.world(xa, p)
        in_hand = f >= swap if in_hand_after else f <= swap
        world = w["Bip01_L_Hand"] @ offset if in_hand else w["Bip01_Prop1"] @ M
        p["Bip01_Prop2"] = w["Bip01"].inverted() @ world


# ==================================================================================================
# Preview
# ==================================================================================================

def gun_objects(arm_ob, g):
    obs = {}

    def load(path, node, mat_world=None, colour=(0.16, 0.16, 0.17, 1.0), bone="Bip01_Prop1", name=None):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=path)
        new = list(set(bpy.data.objects) - before)
        src = next(o for o in new if o.name.split(".")[0] == node)
        name = name or node
        me = bpy.data.meshes.new(name)
        verts = [Vector((v.co.x, v.co.y, -v.co.z)) for v in src.data.vertices]      # file -> game space
        if mat_world is not None:
            verts = [mat_world @ v for v in verts]
        me.from_pydata([tuple(v) for v in verts], [], [tuple(reversed(p.vertices)) for p in src.data.polygons])
        me.update()
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        m = bpy.data.materials.new(name)
        m.diffuse_color = colour
        me.materials.append(m)
        x_preview.attach_to_bone(ob, arm_ob, bone)
        obs[name] = ob

    for node in g["nodes"]:
        load(g["fbx"], node, g.get("model_turn"))
    mc = (0.35, 0.36, 0.4, 1.0)
    load(g["mag_fbx"], g["mag_node"], g["mag_point"], mc, name="MagOnGun")
    # orange in the hand, so a review sees at once whether it travels with the hand
    load(g["mag_fbx"], g["mag_node"], None, (0.85, 0.42, 0.08, 1.0), bone="Bip01_Prop2", name="MagInHand")
    return obs


CLOSEUPS = {
    # name: (camera location, look-at), Blender space (Z up, the character faces -Y, its left is +X)
    "front": ((0.45, -1.7, 0.95), (0.0, -0.12, 0.6)),
    "top": ((0.45, -0.6, 1.95), (0.0, -0.12, 0.6)),
    "side": ((1.75, -0.45, 0.85), (0.0, -0.12, 0.6)),
}


def render_closeups(out_dir, frames, state):
    os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    x_preview.setup_render(scene)
    scene.render.resolution_x = scene.render.resolution_y = 420
    cams = {}
    for name, (loc, tgt) in CLOSEUPS.items():
        cam = x_preview.camera("Cam_" + name, loc, tgt)
        cam.data.ortho_scale = 0.8
        cams[name] = cam
    views = os.environ.get("SMG_PREVIEW_VIEWS")                     # e.g. "front,side" for a GIF
    if views:
        cams = {k: v for k, v in cams.items() if k in views.split(",")}
    obj = bpy.data.objects
    for frame in frames:
        scene.frame_set(frame)
        on_gun, in_hand = state(frame)
        in_hand = in_hand and os.environ.get("SMG_PREVIEW_HAND_MAG") != "0"   # 0: as in game for style "none"
        obj["MagOnGun"].hide_render, obj["MagInHand"].hide_render = not on_gun, not in_hand
        for name, cam in cams.items():
            scene.camera = cam
            scene.render.filepath = os.path.join(out_dir, "%s_%03d.png" % (name, frame))
            bpy.ops.render.render(write_still=True)


def hand_offset(arm_ob, g, frame):
    """Where the left hand really holds: the centre of Bob's left hand and finger vertices (weight > 0.5) at `frame`,
    in weapon space, minus the magazine axis point the hand was sent to (g["grab"]). Used once per gun to measure
    hold_fix (with SMG_CAL=raw; SMG_CAL=1 checks it): the vanilla grip's own magazine contact is not readable from
    its bones."""
    scene = bpy.context.scene
    scene.frame_set(frame)
    body = next(o for o in arm_ob.children if o.type == 'MESH')
    groups = {vg.index for vg in body.vertex_groups if vg.name == "Bip01_L_Hand" or vg.name.startswith("Bip01_L_Finger")}
    picked = [v.index for v in body.data.vertices if any(e.group in groups and e.weight > 0.5 for e in v.groups)]
    ev = body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    centre = sum((body.matrix_world @ ev.vertices[i].co for i in picked), Vector()) / len(picked)
    probe = bpy.data.objects.new("probe", None)
    scene.collection.objects.link(probe)
    x_preview.attach_to_bone(probe, arm_ob, "Bip01_Prop1")
    bpy.context.view_layer.update()
    local = probe.matrix_world.inverted() @ centre
    return local - g["grab"]


def match_ends(r, xa, poses, bases, ramp):
    """A clip end that is one of the clips it joins (`bases`: their first frames; the gun within 5 mm and 3 degrees)
    takes both arms from it, faded into the clip over `ramp` frames. The rig solves its own elbows at the ends, with the
    hand where the idle's is but the elbow elsewhere: the compact stance's de-clipped idle swings its left elbow out,
    and the reloads' first and last frames had the left arm 1.7-2.5 cm in where the idle has it clear."""
    import rifle_hand as RH
    n = len(poses) - 1
    for end, step in ((0, 1), (n, -1)):
        W = pose.world(xa, poses[end])["Bip01_Prop1"]
        for bp in bases:
            Wb = pose.world(xa, bp)["Bip01_Prop1"]
            if (W.translation - Wb.translation).length < 0.005 and \
                    W.to_quaternion().rotation_difference(Wb.to_quaternion()).angle < math.radians(3):
                for k in range(ramp + 1):
                    f = end + step * k
                    if 0 <= f <= n:
                        r.blend_local(poses[f], bp, RH.LEFT_CHAIN + RH.RIGHT_CHAIN, 1.0 - k / float(ramp))
                break


def elbows_to_ends(r, xa, poses, bases, ramp=8):
    """A clip end that is one of the clips it joins (as match_ends) gets that clip's arms exactly, and over `ramp`
    frames each elbow is steered from its own place toward that clip's (in the chest's frame, smoothstep), the hand
    re-solved where it is: the clip leaves and rejoins the idle without the elbow snapping, and without match_ends'
    whole-arm blend, which held the hand back and then moved it 4.5 cm in a frame (the short SMG racks, 2026-10-29,
    when the stance's idle swung its elbows out to vanilla's level and the reloads ended 2.5 cm off it)."""
    import rifle_hand as RH
    n = len(poses) - 1
    hint_cost, scale = rig.SWIVEL_HINT, r.swivel_scale
    rig.SWIVEL_HINT, r.swivel_scale = 1.0, 1.0
    try:
        for end, step in ((0, 1), (n, -1)):
            W = pose.world(xa, poses[end])["Bip01_Prop1"]
            bp = next((bp for bp in bases if
                       (W.translation - pose.world(xa, bp)["Bip01_Prop1"].translation).length < 0.005), None)
            if bp is None:
                continue
            wb = pose.world(xa, bp)
            for side, chain in (("L", RH.LEFT_CHAIN), ("R", RH.RIGHT_CHAIN)):
                U, F, H = rig.ARM[side]
                d_end = wb["Bip01_Spine1"].to_3x3().inverted() @ (wb[F].translation - wb[U].translation)
                for b in chain:
                    poses[end][b] = bp[b].copy()
                for k in range(1, ramp):
                    f = end + step * k
                    if not 0 < f < n:
                        continue
                    t = 1.0 - k / float(ramp)
                    t = t * t * (3 - 2 * t)
                    wp = pose.world(xa, poses[f])
                    d_cur = wp["Bip01_Spine1"].to_3x3().inverted() @ (wp[F].translation - wp[U].translation)
                    saved, hints = r.pole_local[side], r.swivel_hint
                    r.pole_local[side], r.swivel_hint = d_cur.lerp(d_end, t), {side: 0.0}
                    try:
                        r.solve_arm(poses[f], side, wp[H].copy())
                    finally:
                        r.pole_local[side], r.swivel_hint = saved, hints
    finally:
        rig.SWIVEL_HINT, r.swivel_scale = hint_cost, scale


def declip_left(r, xa, arm_ob, poses, contact, src_dir, move_gun=True):
    """The left arm swung out of the body where it went in, the hand kept where it is (user, 2026-10-28: "we wanted
    to fix the clipping issues"; the bullpup's hand went 1.1-1.8 cm into the belly between the handguard and the work
    place, frames 1-6 and 37-44). Each frame no deeper than `contact`, or than the idle at the clip's ends (vanilla's
    own level there, 0.9-1.1 cm), easing to `contact` over RAMP frames; rifle_hand.py's smoothed swing (the swing each
    frame needs spread over RAMP frames either side, faded in from the unswung arm so it never jumps). The first and
    last frames are left as built: they are the idle, or the unload's end the load starts from. move_gun False: the
    swings only, the gun never moved (the user's rule: arms out of the body, the gun where the clip has it)."""
    sys.path.insert(0, HERE)
    import compact_build as CB
    import rifle_hand as RH
    dc = CB.Declip(arm_ob, xa)
    n = len(poses) - 1
    ends = (dc.depth(poses[0])[0], dc.depth(poses[-1])[0])
    limit = [max(contact, ends[0] * (1 - f / RH.RAMP), ends[1] * (1 - (n - f) / RH.RAMP)) for f in range(n + 1)]
    # declip_pass's swing: one direction per clip of rifle_hand's SWINGS in the chest's terms, up to 0.4, the elbow
    # kept in its own plane at no swing (out along the character's left alone, up to 0.2, left the compact stance's
    # left arm 2.1-2.5 cm in on its way between the handguard and the magazine)
    import declip_pass as DP
    idle_chest = RH.chest_frame(src_dir).inverted()
    turns = [pose.world(xa, q)["Bip01_Spine1"].to_3x3() @ idle_chest for q in poses]
    swing = DP.clip_swing_keep(dc, r, xa, poses, limit, turns, "L", RH.SWINGS, list(range(1, n)))
    # the right arm the same (the MP7 stance's aimed rack: 1.6 cm in), its limit from the ends likewise
    rends = (dc.depth(poses[0])[1], dc.depth(poses[-1])[1])
    rlimit = [max(contact, rends[0] * (1 - f / RH.RAMP), rends[1] * (1 - (n - f) / RH.RAMP)) for f in range(n + 1)]
    rswing = DP.clip_swing_keep(dc, r, xa, poses, rlimit, turns, "R", DP.SWINGS_R, list(range(1, n)))
    # what the swings leave (the MP7 stance's hand at the magazine: 1 cm): the gun moved a little out with both hands
    # on it, the least move of declip_pass's directions that clears both arms, spread over RAMP frames
    chests = [pose.world(xa, q)["Bip01_Spine1"].to_3x3() for q in poses]
    need = []
    for f in range(n + 1):
        add = Vector()
        if move_gun and 0 < f < n and (dc.depth(poses[f])[0] > limit[f] + 0.0005 or
                                       dc.depth(poses[f])[1] > rlimit[f] + 0.0005):
            def clear(v):
                d = dc.depth(DP.move_gun(r, xa, poses[f], v, True))
                return d[0] <= limit[f] + 0.0005 and d[1] <= rlimit[f] + 0.0005
            add = DP.least_move(clear, [turns[f] @ g for g in DP.GUN_DIRS], cap=0.05) or Vector()
        need.append(chests[f].inverted() @ add)
    moved = 0
    for f, v in enumerate(RH.spread_vectors(need)):
        if v.length > 0 and 0 < f < n:
            poses[f] = DP.move_gun(r, xa, poses[f], chests[f] @ v, True)
            moved += 1
    over = [(f, dc.depth(q)[0] - limit[f], dc.depth(q)[1] - rlimit[f]) for f, q in enumerate(poses)]
    fl = max(over, key=lambda x: x[1])
    fr = max(over, key=lambda x: x[2])
    print("[declip] arms swung on %d / %d frames (largest %.3f / %.3f), gun moved out on %d; worst over the limits: "
          "left %.3f at f%d, right %.3f at f%d" % (
              sum(1 for s in swing if s.length > 0), sum(1 for s in rswing if s.length > 0),
              max(s.length for s in swing), max(s.length for s in rswing), moved, fl[1], fl[0], fr[2], fr[0]))


def build(src_dir, out_dir, gun, clip, preview=False):
    g = SPECS[gun]()
    for key in ("work", "rack"):                         # tuning: SMG_WORK / SMG_RACK = "right,up,forward"
        v = os.environ.get("SMG_" + key.upper())
        if v:
            g[key] = dict(g[key], pos=ch(*[float(x) for x in v.split(",")]))
        v = os.environ.get("SMG_%s_WRIST" % key.upper())                 # "y,z": settle the gun to that right wrist
        if v:
            g[key] = dict(g[key], wrist=() if v == "off" else tuple(float(x) for x in v.split(",")))
        for part in ("along", "top"):
            v = os.environ.get("SMG_%s_%s" % (key.upper(), part.upper()))
            if v:
                g[key] = dict(g[key], **{part: ch(*[float(x) for x in v.split(",")])})
        v = os.environ.get("SMG_%s_TWIST" % key.upper())                 # the chest turned (degrees)
        if v:
            g[key] = dict(g[key], twist=float(v))
    xa, r, grips = build_rig(src_dir, g)
    if g.get("contact"):
        # the left shoulder forward where the arm falls short (the UMP's aimed rack, 2 cm short of its handle with the
        # aim's gun pushed out)
        sys.path.insert(0, HERE)
        import rifle_hand as RH
        solve = r.solve_arm

        def reach(p, side, target, pole_extra=Vector(), limit=0.0):
            if side == "L":
                RH.shoulder_forward(xa, p, target)
            return solve(p, side, target, pole_extra, limit)
        r.solve_arm = reach
    n = LENGTHS[clip]
    # the unload's arms reach the work place by frame 8: their elbows leave the idle's by then
    poses = r.build(keys_for(clip, r, g, grips), n, breath=(0, None), from_base=(clip in ("Unload", "Rack")),
                    ramp=8 if clip == "Unload" else None)
    arms = g.get("arms_contact", {}).get(clip)
    if g.get("contact") or arms:
        sys.path.insert(0, HERE)
        import rifle_hand as RH
        bases = [pose.from_clip(xanim.read(pth), 0) for pth in base_clips(src_dir, g)]
        if not arms:
            match_ends(r, xa, poses, bases, RH.RAMP)
        declip_left(r, xa, x_import.load(base_clips(src_dir, g)[0]), poses, g.get("contact") or arms, src_dir,
                    move_gun=not arms)
        if arms:
            elbows_to_ends(r, xa, poses, bases)
    if clip in SWAP:
        key_prop2(xa, poses, g, SWAP[clip], clip == "Unload")
    if os.environ.get("SMG_CLEAR"):
        print("[short] %s %s" % (clip, ", ".join("f%s %s %.3f" % x for x in r.short_frames)))
        for f in range(0, n + 1, 2):
            print("[wrist] %s f%d L %s R %s" % (clip, f, *("bend %4.0f/%4.0f twist %4.0f" % r.wrist_angles(poses[f], sd)
                                                          for sd in "LR")))
    if os.environ.get("SMG_DEBUG"):
        for f in range(0, n + 1, 6):
            w = pose.world(xa, poses[f])
            print("[debug] f%d Prop1 %s  L hand %s  Bip01 %s" % (f, tuple(round(c, 3) for c in w["Bip01_Prop1"].translation),
                  tuple(round(c, 3) for c in w["Bip01_L_Hand"].translation), tuple(round(c, 3) for c in w["Bip01"].translation)))
        print("[debug] work pos", tuple(round(c, 3) for c in g["work"]["pos"]))
    tag = "[%s] %s" % (gun, clip)
    if r.warnings:
        print("%s: %d frames out of reach, worst: %s" % (tag, len(r.warnings),
                                                         max(r.warnings, key=lambda w: float(w.rsplit(" ", 1)[1]))))
    if r.wrist_warnings:
        print("%s: %d arm-frames with the wrist past its natural range, e.g. %s" % (tag, len(r.wrist_warnings),
                                                                                    r.wrist_warnings[0]))
    for s in "RL":
        sw = [d for side, d in r.swivels if side == s]
        if len(sw) > 1:
            print("%s: %s elbow swing %.0f..%.0f, largest step %.1f" % (
                tag, s, min(sw), max(sw), max(abs(b - a) for a, b in zip(sw, sw[1:]))))
    os.makedirs(out_dir, exist_ok=True)
    name = g.get("clip_name", "Bob_GunsOfTien_%s_%s") % (g["name"], clip)
    src = base_clips(src_dir, g)[0]
    arm_ob = x_import.load(src)
    pose.bake(arm_ob, xa, poses, name)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, name + ".blend"))
    x_export.export(src, os.path.join(out_dir, name + ".x"), name, arm_ob)
    if os.environ.get("SMG_CAL") and clip == "Unload":
        print("[cal] %s hand centre - magazine axis (weapon space): %s" % (gun, tuple(round(v, 4) for v in
                                                                                   hand_offset(arm_ob, g, 10))))
    obs = gun_objects(arm_ob, g)

    def state(f):
        if clip == "Unload":
            return f < SWAP[clip], f >= SWAP[clip]
        if clip == "Load":
            return f >= SWAP[clip], f < SWAP[clip]
        return True, False
    body = clearance.Body(arm_ob)
    worst = {}
    for f in range(n + 1):
        on_gun, in_hand = state(f)
        parts = {"gun": [obs[node] for node in g["nodes"]],
                 "magazine": [obs["MagOnGun"]] if on_gun else [obs["MagInHand"]] if in_hand else []}
        depths = body.frame(f, parts)
        if os.environ.get("SMG_CLEAR"):
            print("[clear] %s f%d %s" % (clip, f, " ".join("%s %.3f" % kv for kv in sorted(depths.items()))))
        for k, d in depths.items():
            if k not in worst or d > worst[k][0]:
                worst[k] = (d, f)
    clearance.report(tag, worst)
    if preview:
        render_closeups(os.path.join(out_dir, "prev_%s_%s" % (gun, clip)),
                        list(range(0, n + 1, int(os.environ.get("SMG_PREVIEW_STEP") or 3))), state)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    preview = "--preview" in args
    args = [a for a in args if a != "--preview"]
    gun = args[2]
    clips = args[3:] or ["Unload", "Load", "Rack", "AimRack"]
    for c in clips:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        build(args[0], args[1], gun, c, preview)
