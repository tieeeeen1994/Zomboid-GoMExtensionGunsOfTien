# Attachment and tooltip audit (2026-11-23)

How it was checked: `scripts/attachment_audit.py` reads every item script of Gunworks, GoM and both our mods, then
runs every Lua file of those four mods in lupa against mocks, in the game's load order, and fires OnGameBoot,
OnInitGlobalModData, OnLoadMapZones and OnGameStart. So every MountOn appended from Lua (`Rails.lua`, Post-93's
`Guns.lua` / `AUG.lua`, `Suppressors.lua`...), every Gunworks registry (UniversalAttachment, RequiredAttachment,
magazine profiles), GoM's spawn table and every tooltip line is the one the game ends up with. A part counts as
fittable on a gun when its MountOn lists the gun (Java `WeaponPart.canAttach`, traced in the 42.22 jar) and one of its
required parents is integrated on the gun (GoM's spawn table "required") or fittable itself. Full per-gun output:
run the script (`--json` for the data).

## 1. What every gun can take

### Our guns (main mod and Post-93): no broken attachment found

All 46 of our guns are consistent: every rail side has something that fits on it, every accessory in a MountOn has a
rail or mount to sit on, the universal Picatinny Rail offers exactly the sides that can be fitted, every fittable part
has a ModelWeaponPart line, and every spawn entry can really be fitted. If you saw one of **our** guns refuse a rail
in game, tell me which: nothing in the data explains it, so it would be a runtime problem (sync, load order) the
static check cannot see.

| Gun | Integrated rails | Optional rail slots | Mount | Optics allowed | Muzzle |
|---|---|---|---|---|---|
| AUG A1 | – (1.5x scope) | Left, Right | – | none | – |
| Glock 21 | – | – | Beretta Mount | pistol sights | .45 |
| M249 | – | Up, Down, Left, Right | – | 10 of 14 (no TR06X, LR10X, LRX-12X, PSO-1) | – |
| Uzi / Uzi (two-handed) | – | Up, Down, Left | – | 7 red dots | 9mm |
| Mini Uzi | – | Up, Down, Left | – | Reflex S2 only | 9mm |
| Micro Uzi | – | – | – | – | 9mm |
| P90 | – (ring sight) | Left, Right | – | none | 5.7 |
| TMP | – | Up, Left, Right | – | 7 red dots | 9mm |
| PPK, RPD, SR-25 | – | – | – | – (SR-25: integrated scope) | – |
| RPK, RPK-74 | – | – | AK Mount | all 14 | AK |
| SVU | – | – | AK Mount | all 14 | – |
| AUG A3 / Para / HBAR | Up, Right | Left | – | all 14 | AR / 9mm / – |
| Groza-1 / -1 GP-25 / -2 / -4 | – | Up | – | all 14 | AK / AK / AK / integral |
| HK416, HK417, HK417 Marksman, Mk 11, SCAR-L, SCAR-H, UMP45, UMP9, MP7A2, PS90, HK416 .22 | Up, Down, Left, Right | – | – | all 14 | per gun |
| MP7A1, P90 TR | Up, Left, Right | – | – | all 14 | own can |
| MDRx .223 | Up, Down | Left, Right | – | all 14 | AR |
| MDRx .308 | Up | Left, Right | – | all 14 | 7.62x51 |
| Vector .45 / 9mm / CRB / SDP | Up, Down | Left, Right | – | all 14 | .45 / 9mm |
| SV-98, SV-99 | Up | – | – | all 14 | – / integral |
| Five-seveN, UCP | – | – | Beretta Mount | pistol sights | 5.7 / 4.6 |

### GoM's own guns: real bugs (fixable from our `GoMFixes.lua`, as we already fix two GoM registrations)

- **CAR-15 bottom rail promised but never there.** Its model draws `Picatinny_Rail_Down` and the three foregrips, its
  tooltip promises "Up, Down, Left, Right" and the foregrips' MountOn list it, but `Picatinny_Rail_Down`'s MountOn and
  GoM's universal rail registration both leave it out. Result: no bottom rail, and the foregrips can never be fitted.
  (Second look while fixing: GoM's CAR-15 always carries its M203 under the barrel, an integrated part from its spawn
  table, so the right fix is the other way round: no bottom rail, the foregrips out of their MountOn, the tooltip
  generated.)
- **M16A2 cannot take the AimRight laser**: its spawn table gives it one 2% of the time on the right rail, but the
  laser's MountOn leaves out the M16A2 (the LRX-7 has it).
- **AA-12 side rails are invisible**: Left and Right rails, lights and lasers can be fitted, but the gun has no
  ModelWeaponPart line for any of them (only our laser beams), so they are drawn nowhere.
- **Bipods are invisible** on the G36, G36C, M4A1, XM177, MP5, MP5A2 and MP5SD: fittable on their bottom rail, no
  model line.
- **Tooltips that lie** (GoM's lines, shown as is): AR-15 says "Up, Down" (really Down, Left, Right: no top rail,
  carry handle); Mini-14 says "Up, Down" (really Up only); G36C says "Up, Down, Left, Right" as slots (Up and Down are
  integrated, only Left and Right are slots).

## 2. The tooltips

### Where the gun lines come from

Eleven hand-written per-gun files (`AUGTooltips.lua`, `Glock21Tooltips.lua`, `M249Tooltips.lua`, `P90Tooltips.lua`,
`PPKTooltips.lua`, `RPDTooltips.lua`, `RPKTooltips.lua`, `SR25Tooltips.lua`, `SVUTooltips.lua`, `TMPTooltips.lua`,
`UziTooltips.lua`), Post-93's `Tooltips.lua`, and `HandlingTooltips.lua` rewriting GoM's. Each was worded "like
the last one", so the wording drifted. `scripts/list_tooltips.py` (the tooltip review list in TODO.md) does not read
the eleven per-gun files, so they were never in a review.

### Formats in use on our 46 guns (count of guns)

| Kind | Formats in use |
|---|---|
| Rails | "Available Picatinny Slots: …" (20, with and without a full stop) · "Integrated Picatinny rails: …" (19, side order differs: MP7A2 "Up, Left, Right, Down") · "Integrated Picatinny rail: Up" (5) · "M-LOK handguard: Down" / "Left, Right, Down" (2; in game these are plain integrated rails) |
| Magazines | "Compatible Magazines: RPK 40Rds, RPK 75Rds Drum, AK-47" (RPK; "AK-47" means GoM's 7.62x39 30 and 75) · "Compatible Magazines: AK-74" (RPK-74) · "… SVD" · "… M249 200Rds Box, STANAG" · "… RPD 100Rds Belt Drum" (its only magazine) · "Takes Glock 21 magazines." (Vectors) · "Takes SR-25 pattern magazines." (SR-25 family) · nothing at all on the Groza (AK magazines), SCAR-L, MDRx .223, HK416 (STANAG). On magazines: "Fits the RPK and AK-47" vs "Fits the Glock-17 and the 9mm Vectors." |
| Integrated parts | "Integrated Scope: 1.5x" · "Integrated ring sight" · "Integrated 3.5-10x scope and folding bipod." · "Has Integrated Bipod" · "Has Integrated Suppressor" · "Integrated suppressor." · "Heavy barrel with an integrated folding bipod." · "ALX handguard with an integrated folding bipod." · "Integrated GP-25 grenade launcher." (9 phrasings for one idea) |
| Optic limits | "Compatible Optics: red dots only" (Uzi) · "Compatible Optics: Reflex S2 Sight only" (Mini Uzi) · **nothing** on the TMP (red dots only too) or the M249 (no long scopes) |
| Trivia, no game effect | "16-inch barrel" / "20-inch barrel" · "No stock" · "H&K prototype" · "Ejects spent cases to the right / forward / downward." · "50-round magazine on top." · "Iron sights fold under an optic." / "Iron sights come off under an optic." |
| Round facts on a gun | "Standard rounds pierce and can hit up to 2 targets." (6 guns; the round's own tooltip already says it) |
| Punctuation | GoM's "Uses … rounds." ends with a full stop, our stat lines do not, the rest is mixed |

## 3. Proposed single format

Every gun's Information block, from one generator instead of hand-written files, only facts the game acts on,
always in this order, no full stops, sides always in the order Up, Down, Left, Right, a line left out when empty:

```
Uses <calibre> rounds
Integrated: <1.5x scope | folding bipod | suppressor | GP-25 launcher | ...>
Integrated Picatinny Rails: Up, Down
Integrated M-LOK Slots: Down, Left, Right           (an M-LOK handguard with no rail drawn: PS90, MDRx .223)
Available Picatinny Slots: Left, Right
Compatible Optics: Red dots only                 (only where some optics are refused)
Compatible Mounting Device: AK Mount
Compatible Muzzle Device: AK Muzzle Mount
Can attach a bayonet
<rule lines: Jam Chance doubled with STANAG magazines / Fits an ankle holster>
<state lines, unchanged: "Folding stock deployed:" + its stats>
```

- Rails, mount, muzzle, bayonet and optic-limit lines are **built from the live registries** at game start (what the
  audit script computes), for GoM's guns too, so a tooltip can no longer say something the gun cannot do (fixes
  AR-15, Mini-14, G36C, CAR-15 at once, and the TMP / M249 missing optic lines).
- M-LOK: first folded into "Integrated Picatinny Rails" (that is how the game treats it), then given its own
  "Integrated M-LOK Slots" line (user: "how about the MLOK?"): the PS90's bottom and sides and the MDRx .223's bottom
  have no rail on the model, accessories clamp onto the slots. The MDRx's bolt-on side sections are GoM's Picatinny
  Rail upgrades, so they stay Available Picatinny Slots.
- Magazines: see the question below.
- Dropped: barrel lengths, "No stock", "H&K prototype", case ejection, "magazine on top", iron sights folding, the
  pierce line on guns (it stays on the round).

## 4. What was done (2026-11-23, user: "yes that is a sound decision" / "remove flavor as it adds bloat" / GoM fixes
"follow what was written ... add the missing model lines ... render the picatinny rail ... if you find yourself
needing to overlap from the foregrip, let's drop the bipod support ... force existing guns ... to uninstall")

- `client/GunsOfTien/GunLines.lua`: every gun's and magazine's lines rebuilt on the first tick from the registries in
  the format above (Tooltips.lua calls it before its render wrappers). The per-gun files and Post-93's Tooltips.lua
  now give a gun only its "Uses" line; magazines get "Fits: <guns>" (short names). Mounting and muzzle devices are
  named by their item names ("AK Mounting Rail", "AR Family Muzzle Mounting Device"), so a line never names a gun
  for a part again.
- `shared/GunsOfTien/GoMAttachments.lua`: AA-12 `rail_left` / `rail_right` / `light_left` / `laser_right` points and
  model lines (measured by `scripts/gom_points.py`); G36 `bipod` point and lines; AimRight laser on the M16A2; the
  bipods out of the G36C, M4A1, XM177, MP5, MP5A2 and MP5SD (placed as on the M16A2 they overlap the foregrips by
  15 mm; the G36C has no bottom rail point), the foregrips out of the CAR-15.
- `server/GunsOfTien/RemovedParts.lua`: a gun saved with a part it no longer takes (`GunsOfTien_RemovedParts`) gets
  it taken off and put beside it, in the same container, or on the floor at the gun's spot: chunks as they load,
  players 10 s after joining, vehicles once loaded. `tests/removed_parts_test.py` runs it against mocks.
- Re-run `scripts/attachment_audit.py`: no issue left on any gun of the three mods.

## 5. Muzzle parts (2026-11-23, user: "MAKE IT CONSISTENT!")

One mount device per calibre family now (9mm: GoM's pistol mount renamed "9x19mm Family Muzzle Mounting Device",
our old 9x19mm SMG mount swapped for it in existing worlds by `RemovedParts.lua`), the Groza-2 takes the AK mount and
PBS-1, found guns carry no mount device (GoM's way), and every can and mount tooltip is in GoM's wording with the guns
it fits. Details: CLAUDE.md "Muzzle parts audit". Re-run of `attachment_audit.py`: every fittable muzzle part has a
model line on every gun; the 17 9mm guns all show "Compatible Muzzle Device: 9x19mm Family Muzzle Mounting Device".
