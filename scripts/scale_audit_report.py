#!/usr/bin/env python3
"""Report how big every GoM / Guns of Tien gun is drawn against its real size (Python 3, no dependencies).

    python3 scripts/scale_audit_report.py <scale_audit.json> [anchor ratio, default GoM's M16A2's own]

Reads what `scale_audit.py` measured. Per gun: drawn length / real length (the ratio), the gun's own `scale` that
puts it in the M16A2's proportion (anchor / ratio; the M16A2 itself 1.00), and for guns held on vanilla's rifle clips
where the left palm meets the gun before and after that scale (the gun scales about its grip origin; the palm stays
where the clip has it).

Reference sizes (measured 2026-10-25):
- vanilla's male body mesh is 0.98 units tall, so a ~1.78 m man is drawn at ~0.55; vanilla's M16 (M16_Rifle.x,
  0.546 long) is 0.54 of its real 1006 mm, i.e. true to the body; vanilla's M9 is 0.70 (pistols drawn larger).
- vanilla's left palm (between Bip01_L_Hand and Bip01_L_Finger1, in Bip01_Prop1 space = gun space) is fixed through
  each clip: Bob_IdleRifle / Bob_WalkRifle y 0.218, z -0.004; Bob_IdleAimRifle y 0.204, z -0.021.
- on vanilla's own rifles (M16, M14, MSR788) the gun's underside at the palm is 1.1 cm above it idle and 2.8 cm aimed
  (the 870-style pump 0.3 / 2.0): what the clips were made for. GAP below is that distance; a gun far off it shows a
  floating (larger) or buried (negative) left hand.
"""
import json
import statistics
import sys

# real overall length in mm (stock extended / unfolded) and the variant assumed; '?' = variant guessed from the model
REAL = {
    "MarzGuns.M16A1": (1003, "M16A1 20in"), "MarzGuns.M16A2": (1006, "M16A2"), "MarzGuns.M16A2_M203": (1006, "M16A2"),
    "MarzGuns.M16A3": (1006, "M16A3"), "MarzGuns.AR15": (991, "SP1 20in"), "MarzGuns.FNC": (997, "FNC"),
    "MarzGuns.CAR15": (838, "14.5in Colt carbine?"), "MarzGuns.XM177": (787, "XM177E2?"),
    "MarzGuns.M4A1": (838, "M4A1"), "MarzGuns.G36C": (720, "G36C"), "MarzGuns.G36": (999, "G36"),
    "MarzGuns.AK74": (943, "AK-74"), "MarzGuns.AKS74U": (730, "AKS-74U"), "MarzGuns.ASVAL": (875, "AS Val"),
    "MarzGuns.FAMAS": (757, "FAMAS F1"), "MarzGuns.AK47": (870, "AK-47"), "MarzGuns.M14": (1120, "M14"),
    "MarzGuns.M1_GARAND": (1107, "M1"), "MarzGuns.FAL": (1090, "FAL 50.00"), "MarzGuns.G3": (1025, "G3A3"),
    "MarzGuns.MOSIN": (1232, "M91/30"), "MarzGuns.M24": (1092, "M24"), "MarzGuns.M1903": (1097, "M1903"),
    "MarzGuns.REMINGTON_700": (1100, "24in?"), "MarzGuns.MODEL_70": (1067, "22in?"),
    "MarzGuns.W1894": (965, "20in carbine?"), "MarzGuns.M1895": (1029, "22in?"),
    "MarzGuns.W1887": (1232, "30in original?"), "MarzGuns.W1873": (1092, "24in rifle?"),
    "MarzGuns.W1873_CARBINE": (620, "cut-down stock, mare's leg?"), "MarzGuns.M60": (1105, "M60"),
    "MarzGuns.BAR": (1214, "M1918A2"), "MarzGuns.SVD": (1225, "SVD"), "MarzGuns.SKS": (1020, "SKS"),
    "MarzGuns.PSG1": (1208, "PSG1"), "MarzGuns.CAMP_CARBINE": (902, "Camp 9 / 45"),
    "MarzGuns.MINI_14": (946, "Ranch 18.5in"), "MarzGuns.MOSSBERG_590": (1041, "20in"),
    "MarzGuns.TRENCHGUN": (1003, "M1897 trench"), "MarzGuns.BENELLI_M4": (1011, "M4"),
    "MarzGuns.SPAS12": (1041, "SPAS-12"), "MarzGuns.STEVENS_555": (1143, "28in?"),
    "MarzGuns.DOUBLEBARREL": (1170, "28-30in SxS?"), "MarzGuns.AA12": (966, "AA-12"),
    "MarzGuns.REMINGTON_870": (1219, "28in field?"), "MarzGuns.TOZ34": (1145, "TOZ-34 28in"),
    "MarzGuns.M79": (737, "M79"), "MarzGuns.THOMPSON": (813, "M1A1?"), "MarzGuns.MP5": (700, "A3 sliding stock"),
    "MarzGuns.MP5SD": (805, "SD3"), "MarzGuns.MP5A2": (680, "A2"), "MarzGuns.MP5K": (325, "MP5K"),
    "MarzGuns.TEC9": (317, "TEC-DC9"), "MarzGuns.MAC10": (548, ".45, stock out"), "MarzGuns.M92FS": (217, "M92FS"),
    "MarzGuns.M93R": (240, "93R"), "MarzGuns.HIPOWER": (197, "Hi-Power"), "MarzGuns.P226": (196, "P226"),
    "MarzGuns.M1911": (210, "M1911A1"), "MarzGuns.USP": (201, "USP45"), "MarzGuns.DEAGLE": (270, "6in"),
    "MarzGuns.VP70M": (204, "no stock"), "MarzGuns.GLOCK17": (202, "G17"), "MarzGuns.SW629": (349, "8-3/8in?"),
    "MarzGuns.PYTHON": (290, "6in"), "MarzGuns.RHINO": (265, "6in?"), "MarzGuns.MP412": (240, "5in?"),
    "MarzGuns.COLT_SINGLE": (330, "7.5in?"), "MarzGuns.DETECTIVE_38": (171, "2in"),
    "GunsOfTien.M249": (1041, "M249"), "GunsOfTien.UZI": (640, "stock out"), "GunsOfTien.MINIUZI": (600, "stock out"),
    "GunsOfTien.MICROUZI": (460, "stock out"), "GunsOfTienPost93.MP7A1": (638, "stock out"),
    "GunsOfTienPost93.MP7A2": (638, "stock out"), "GunsOfTienPost93.P90TR": (500, "P90 TR"),
    "GunsOfTienPost93.UMP45": (690, "stock out"), "GunsOfTienPost93.UMP9": (690, "stock out"),
    "GunsOfTienPost93.SCARL": (889, "STD 14in"), "GunsOfTienPost93.SCARH": (1062, "20in"),
    "MarzGuns.FIVESEVEN": (208, "Five-seveN"), "GunsOfTienPost93.UCP": (198, "UCP"),
}
# launcher-only items sharing a gun's model, and GoM's fictional 2-bore (no real size to hold it to)
SKIP = {"MarzGuns.CAR15_M203_Weapon", "MarzGuns.M203_Weapon", "MarzGuns.MASTERKEY_Weapon", "MarzGuns.DOUBLE_DEUCE"}
COMPACT = {"GunsOfTien.UZI", "GunsOfTien.MINIUZI", "MarzGuns.MP5K"}  # our compact stance (CLAUDE.md)
PALM = {"idle": (0.218, -0.004), "aim": (0.204, -0.021)}


def kind(name, gun):
    if name in COMPACT:
        return "compact stance"
    if gun["swing"] != "Handgun":
        return "rifle stance"
    short = name.split(".")[-1]
    if short in ("MP7A1", "MP7A2", "P90TR", "MAC10", "TEC9", "MICROUZI"):
        return "SMG held as a pistol"
    return "pistol"


def section(gun, y):
    """(bottom, top) of the gun's side silhouette at y, or None past its ends."""
    zs = []
    for poly in gun["sil"]:
        for (y1, z1), (y2, z2) in zip(poly, poly[1:] + poly[:1]):
            if (y1 - y) * (y2 - y) <= 0 and y1 != y2:
                zs.append(z1 + (y - y1) * (z2 - z1) / (y2 - y1))
    return (min(zs), max(zs)) if zs else None


def hand(gun, s):
    """'gap / thickness' (cm) at each palm with the gun scaled by s about its origin."""
    out = []
    for name, (py, pz) in PALM.items():
        sec = section(gun, py / s)
        out.append("%s off the gun" % name if sec is None else
                   "%s %+.1f / %.1f" % (name, (s * sec[0] - pz) * 100, s * (sec[1] - sec[0]) * 100))
    return ", ".join(out)


def main():
    guns = json.load(open(sys.argv[1]))["guns"]
    rows = [(k, g, REAL[k], g["length"] / REAL[k][0] * 1000) for k, g in guns.items() if k in REAL and k not in SKIP]
    target = float(sys.argv[2]) if len(sys.argv) > 2 else next(r for k, _, _, r in rows if k == "MarzGuns.M16A2")
    missing = sorted(set(guns) - set(REAL) - SKIP)
    long_gom = [r for k, g, _, r in rows if kind(k, g) == "rifle stance" and k.startswith("MarzGuns.")]
    print("GoM rifle-stance guns: median %.3f, mean %.3f, %.3f..%.3f (%d)" % (
        statistics.median(long_gom), statistics.mean(long_gom), min(long_gom), max(long_gom), len(long_gom)))
    print("anchor %.4f; hand = vanilla palm gap / gun thickness there in cm, now -> scaled\n" % target)
    for k, g, (real, variant), r in sorted(rows, key=lambda x: (kind(x[0], x[1]), x[3]), reverse=True):
        s = target / r
        line = "%-21s %-24s %-28s %.3f u  %4d mm  ratio %.2f  scale %.2f" % (
            kind(k, g), k, variant, g["length"], real, r, s)
        if kind(k, g) == "rifle stance":
            line += "  | %s -> %s" % (hand(g, 1.0), hand(g, s))
        if g["muzzle_y"] is not None and abs(g["muzzle_y"] - g["y"][1]) >= 0.01:
            line += "  | muzzle point %+.1f cm from the barrel's end" % ((g["muzzle_y"] - g["y"][1]) * 100)
        print(line)
    if missing:
        print("\nno real size known:", ", ".join(missing))


if __name__ == "__main__":
    main()
