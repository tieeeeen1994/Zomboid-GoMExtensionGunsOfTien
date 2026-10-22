# GoM Extension: Guns of Tien — design (approved 2026-10-14, building)

Mod id `GoMExtensionGunsOfTien`, item module `GunsOfTien`, ammo type namespace `gunsoftien:`.
`require=SWMG,GunsOfMarz,ammomaker`, `loadModAfter=HBVCEFb42,SWMG,GunsOfMarz,ammomaker`. Every new round can be
assembled with Ammo Maker (own Ammo Maker types, see CLAUDE.md). Build 42 folder `42/`.
Setting: Kentucky, July 1993. Only loads that existed and could plausibly be found there then.

## 1. New rounds

Each round gets a Gunworks AmmoType, a round item, a box, a carton and a crate (like GoM's 5.56 variants), own
open / pack recipes, a stat profile, a GoM tooltip, Hot Brass casing + pressure entries, loot, and its own icons.

| Round | Family (fits) | Damage | Crit | Other | Sound | Wear | 1993 basis |
|---|---|---|---|---|---|---|---|
| 7.62x39mm US Subsonic | 7.62x39 (AK-47, SKS) | ×0.5 | ×0.8 dmg | rack after every shot **unless a PBS-1 is fitted** (option) | ×0.5 | ×2 condition (less wear) | Soviet "US" round made for the AKM + PBS-1; 200 gr at ~300 m/s |
| 7.62x39mm Soft Point | 7.62x39 | ×1.2 | ×1.15 dmg, ×1.05 chance | | | ×0.9 | Winchester / S&B hunting loads sold in the US |
| 7.62x39mm Steel Core | 7.62x39 | ×0.9 | ×0.95 dmg, ×0.9 chance | pierces, hits up to 3 | | ×0.85 | Cheap Norinco steel-core surplus, legal until 1994 |
| 9x19mm 147gr Subsonic | 9x19 (pistols, MP5s, TEC-9) | ×0.85 | | | ×0.7 (no supersonic crack) | | FBI adopted the 147 gr load in 1988; police stock |
| 9x19mm Hollow Point | 9x19 | ×1.2 | ×1.15 dmg, ×1.05 chance | | | ×0.9 | Standard police / defence load |
| .45 ACP Hollow Point | .45 ACP (M1911, USP, Thompson, MAC-10, Camp Carbine, Colt SA) | ×1.2 | ×1.15 dmg, ×1.05 chance | | | ×0.9 | Hydra-Shok, Silvertip... |
| .45 ACP +P | .45 ACP | ×1.15 | ×1.1 dmg | | ×1.1 | ×0.7 | Hotter defence loads |
| 9x39mm SP-6 | 9x39 (AS VAL) | ×0.9 | ×0.95 dmg | pierces, hits up to 3 | | | The AS VAL's AP round (Soviet / Russian issue) |
| 9x19mm +P+ | 9x19 | ×1.2 | ×1.1 dmg | | ×1.1 | ×0.6 | Hot 115 gr police load (Illinois State Police, Border Patrol) |
| .30-06 / .308 Soft Point | .30-06, 7.62x51 | ×1.2 | ×1.15 dmg, ×1.1 chance | **no piercing, one target** | | | Deer hunting loads, the commonest rifle ammo in rural Kentucky |
| 12 ga Birdshot | 12 ga (every shotgun) | ×0.3 per pellet | ×0.4 chance, ×0.5 dmg | 9 pellets as buckshot (the engine's cap), spread ×2, half the range | | | The most common shell in any house |

GoM's plain rounds renamed to what they really are (translation override only): `SWMG.9x39_Bullet` → **9x39mm SP-5**,
`SWMG.545x39_Bullet` → **5.45x39mm 7N6**, which also gets a profile (GoM defines none): steel core, pierces, hits up
to 3, ×1.1 crit chance (tumbles). Its boxes are renamed to match.

**Realistic piercing** (sandbox option, see 4): plain .30-06 and 7.62x51 / .308 rounds pierce, hitting up to 2
targets in a line (GoM sets PiercingBullets on the bolt rifles, BAR, M60 and PSG-1 but gives every rifle MaxHitCount 1,
so nothing actually pierces), so soft points (no piercing, more damage) are always a trade-off. Done as a StatsFactory
layer keyed by the gun's current round, because Gunworks never applies an ammo profile to a gun's own script round. GoM's plain .30-30 keeps its name but is what real .30-30 almost
always is, a flat-nosed soft point (pointed bullets are unsafe in a tube magazine): it stops piercing (the W1894 script
pierces). No separate .30-30 soft point. 7.62x39 keeps GoM's plain round; its
trade-off is soft point against steel core.
Multipliers follow GoM's own 5.56 set (its subsonic is ×0.4 / ×0.5, HP ×1.2, AP ×0.85 + pierce 5).

Decided against (2026-10-14): PBS-1 wipe wear, extra wear when suppressed, MP5SD subsonic rule, hollow points jamming
M1911s. Left as GoM has it: .223 as a weaker "civilian" 5.56.

## 2. Loot (realistic rarity, sandbox multiplier)

**Superseded 2026-10-17: no loot.** Guns of Marz never spawns its own special loads (its 5.56 Hollow Point / Armor
Piercing / Subsonic / Overpressured), only each calibre's standard box, so these rounds are not loot either (user):
they come from Ammo Maker. The plan below was built and then removed.

- Police stations and police zombies: 9mm and .45 hollow points, 9mm subsonic (common), .45 +P (uncommon).
- Gun stores / hunting: 7.62x39 soft point and steel core (common, like GoM's 7.62x39 box), 9mm / .45 hollow point.
- Military / Russian spawners: 7.62x39 US subsonic (rare), 9x39 SP-6 (very rare, alongside the AS VAL's boxes).
- Added next to vanilla and GoM boxes (`Distribution.Insert`, GoM spawner bonus groups), never replacing them.
- Sandbox `GunsOfTien.AmmoLootMultiplier` (0-100, default 1). (Removed 2026-10-17: GoM's `MarzGuns.LootMultiplier` is used.)

## 3. Realistic gun sounds, M16 = reference (always on, no sandbox option)

Every GoM gun's `SoundRadius` and `SoundVolume` set to M16 × f (M16A1-A3 stay 175 / 50), applied to the item scripts
at world load so ammo and suppressor multipliers stack on top as before. Launchers (M79, M203) are left alone
(their loudness is the explosion). `SoundGain` (what players hear) is left alone.

How f is worked out (a model, the inputs are real; `scripts/sound_model.py`):
- **Blast**: propellant burnt per shot, 10·log10(grains / 25) dB (5.56 ≈ 25 gr, .308 ≈ 45, 9mm ≈ 6, 12 ga ≈ 27).
- **Barrel**: +3 dB per halving of the barrel against the calibre's usual barrel (short barrels are louder).
- **Crack**: a subsonic round (.45, .38, 9x39) has no supersonic crack: −5 dB.
- **Integral suppressor** (AS VAL, MP5SD): −17 dB, the same ×0.3 GoM gives a fitted suppressor. The MP5SD's barrel is
  ported to slow standard rounds below the speed of sound, so it has no crack either (−5 dB more; 2026-10-22, so it
  beats a plain MP5 with the Mk9, which keeps the crack).
- dB to game: f = 2^(ΔdB / 10) (perceived loudness doubles every 10 dB), which keeps GoM's scale (pistols ~100,
  rifles ~175-220).

| Gun | GoM radius / volume | Corrected | | Gun | GoM | Corrected |
|---|---|---|---|---|---|---|
| M16A1/A2/A3, M203 | 175 / 50 | 175 / 50 | | M92FS | 100 / 30 | 111 / 32 |
| AR-15 | 150 / 35 | 173 / 49 | | M93R | 100 / 30 | 104 / 30 |
| FNC | 170 / 40 | 182 / 52 | | Hi-Power | 120 / 40 | 112 / 32 |
| CAR-15 | 145 / 32 | 207 / 59 | | P226 | 120 / 40 | 115 / 33 |
| XM177 | 145 / 32 | 215 / 62 | | VP70M | 100 / 30 | 113 / 32 |
| M4A1 | 145 / 32 | 193 / 55 | | M1911 | 120 / 50 | 81 / 23 |
| G36C | 145 / 30 | 222 / 64 | | USP | 120 / 50 | 84 / 24 |
| G36 | 145 / 30 | 178 / 51 | | Desert Eagle | 180 / 100 | 185 / 53 |
| FAMAS | 170 / 40 | 177 / 51 | | SW 629 (.44) | 120 / 75 | 168 / 48 |
| AK-74 | 200 / 40 | 166 / 47 | | Python (.357) | 120 / 75 | 144 / 41 |
| AKS-74U | 200 / 40 | 205 / 59 | | Rhino (.357) | 100 / 65 | 162 / 46 |
| AK-47 | 200 / 40 | 175 / 50 | | MP-412 (.38) | 60 / 25 | 76 / 22 |
| AS VAL | 50 / 25 | **33 / 9** | | Detective .38 | 60 / 25 | 94 / 27 |
| SKS | 170 / 30 | 165 / 47 | | Colt SA (.45) | 100 / 65 | 78 / 22 |
| Mini-14 | 170 / 40 | 177 / 51 | | Camp Carbine (.45) | 120 / 50 | 56 / 16 |
| M14 | 200 / 30 | 210 / 60 | | Thompson | 150 / 35 | 64 / 18 |
| M1 Garand | 220 / 50 | 216 / 62 | | MAC-10 | 100 / 30 | 77 / 22 |
| FAL | 190 / 45 | 213 / 61 | | MP5, MP5A2 | 150 / 35 | 93 / 27 |
| G3 | 190 / 40 | 224 / 64 | | MP5K | 100 / 30 | 114 / 33 |
| SVD | 170 / 30 | 224 / 64 | | MP5SD | 50 / 15 | **23 / 7** |
| PSG-1 | 170 / 30 | 201 / 57 | | TEC-9 | 100 / 30 | 110 / 32 |
| M60 | 230 / 45 | 210 / 60 | | 12 ga pumps / semis | 200 / 200 | 175-185 / 50-53 |
| BAR | 230 / 45 | 216 / 62 | | 12 ga doubles | 200 / 200 | 162-166 / 46-47 |
| Mosin | 220 / 250 | 213 / 61 | | Masterkey (7" 12 ga) | 200 / 200 | 245 / 70 |
| M24 | 220 / 250 | 205 / 59 | | W1887 | 175 / 250 | 179 / 51 |
| M1903 | 220 / 250 | 216 / 62 | | W1894 (.30-30) | 150 / 180 | 185 / 53 |
| Remington 700 | 220 / 250 | 202 / 58 | | M1895 (.45-70) | 175 / 230 | 209 / 60 |
| Model 70 (.223) | 220 / 250 | 168 / 48 | | W1873 / carbine (.357) | 150 / 180 | 95-100 / 27-29 |

Biggest changes: bolt and lever rifles and shotguns lose GoM's very high volume (180-250 → about 50-60); short
carbines become louder than the M16; .45 guns become quiet (subsonic); the AS VAL and MP5SD become the quietest guns.

## 4. Sandbox options (page GunsOfTien)

- `AmmoLootMultiplier` (double, 1). (Removed 2026-10-17.)
- `RealisticPiercing` (bool, true): FMJ rifle rounds pierce, .30-30 does not (section 1).
- `SubsonicRackRule` (enum: 1 always rack / 2 rack unless a PBS-1 is fitted (default) / 3 never): 7.62x39 US.
  A gas-operated AK short-strokes on the low-powder US round; the PBS-1's back pressure pushes enough gas into the
  gas port to cycle it (the round and the suppressor were designed as a pair). Approved by the user.

## 4b. Sawn-off stocks (2026-10-19)

GoM's break-action shotguns (Double Barrel, Stevens 555, TOZ-34; the ones whose barrels GoM saws off) can also have
their walnut buttstock sawn off behind the pistol grip: craft "Saw Off Shotgun Stock" (Weaponry, in hand, any saw,
the gun kept). Permanent. A shell holder (it sits on the stock) comes off into the inventory.
- Offcuts (user, 2026-10-19): what is sawn away is kept, weighing what the gun loses. The stock gives
  "<gun> Stock Offcut" (0.5, scrap wood: fuel and charcoal like Unusable Wood); GoM's Saw Off Shotgun Barrels gives
  "<gun> Barrel Offcuts" ("Double Barrel Offcuts"; 2.0, GoM's barrels 3.0 -> 1.0; scrap steel tagged large for
  smelting, 4 crucible uses = one Steel Bar). One item per gun: the models are the pieces cut off GoM's own meshes,
  with that gun's texture.
- Handling: Aiming Time x0.75 (quicker to bring up, like the sawn-off barrels; both: 40 to 22); Hit Chance x0.87,
  Recoil Delay x1.3 (no shoulder to steady it or take the kick, so it also settles slower after a shot); 0.5
  lighter.
- Carry: with the sawn-off barrels too (or no barrel) the gun fits vanilla's belt and shoulder holsters; a sawn-off
  stock with full barrels stays on the back. Held two-handed as before.
- Shown: the stockless body (GoM's mesh cut behind the grip) while the sawn-off stock is fitted; its muzzle point at
  the sawn-off barrels' end when they are fitted.
- Sawn-off barrels: the Stevens 555's and TOZ-34's get the Double Barrel's (GoM gives stats only to those): Aiming
  Time 30, Hit Chance 70, pellet spread 2.0, range 15, from 40 / 65 / 0.6 / 20 on all three guns.
- No sandbox option, like the lasers (user).

## 4c. AWC Mk9 SMG suppressor (2026-10-22)

GoM's 9mm suppressors (M&P, Shh9) need its Pistol mount and fit its pistols only. A 9mm SMG can of the time, on its
own "9x19mm SMG Family Muzzle Mounting Device" (GoM's rule: every can needs its mount first), for the 9mm SMGs whose
real barrels take one (user: "only if supported", "no pistol"):
- GoM's MP5 and MP5A2 (H&K's three-lug barrel) and Post-93's UMP9 (threaded). Not the MP5K (flush end cap), the
  MP5SD (integral can) or the TEC-9 (user's choice, though its threaded barrel would take one).
- The can: AWC's Mk9 (user), AWC's SMG can for the Uzi, MAC and MP5, made in the 1980s, 12" x 2", fitted to the MP5's
  lugs with Tim Bixler's adapter (1988), which is the mount device. Big; the user kept it over the shorter options.
- GoM's 9mm cans' stats (sound and volume ×0.3, damage ×0.9, no muzzle flash) plus Aiming Time ×1.1 (a 24 oz can
  out at the muzzle), weights 1.2 / 0.5 as GoM's.
- The MP5SD stays the better quiet gun (user): 23 / 7 (no crack, see section 3) against the suppressed MP5's 28 / 8,
  lighter and quicker to aim; the suppressed MP5 hits harder and reaches further. The 147gr subsonic round makes no
  sound difference in the SD (its ×0.7 is the crack, which the SD does not have; its damage ×0.85 stays), so a
  suppressed MP5 comes close only with that round (about 20 / 6).
- Loot as GoM's parts: one more choice in its suppressor and muzzle device spawners, and the mount among GoM's mounts
  that replace vanilla's Improved Choke Tube. Found guns never come with one.

## 4d. M249 Light Machine Gun (2026-10-22, designed, building)

The main mod's first gun (adopted 1982, issued from the mid-1980s, so it belongs in July 1993; Fort Campbell and Fort
Knox are in Kentucky). The **PIP** version (user: "M249E2", the informal name of a PIP gun): M240-style polymer
stock with buffer, heat shield over the barrel, folding carrying handle, PIP handguard. The January 1994 field
manual still lists guns without the kit, so both looks were in service; the PIP's public-domain USAF side photo
(white background, left side, muzzle right) is the modelling reference. No civilian had one in 1993 (no semi-auto
until FN's M249S in 2015): military loot only.

| | `GunsOfTien.M249` "M249 Light Machine Gun" |
|---|---|
| Real | 5.56x45 (M855), 465 mm barrel, 1038 mm, 7.4 kg empty (PIP), gas operated, open bolt, full auto only |
| Feed | Its own 200-round box, `GunsOfTien.556x45Box200_M249` "M249 200Rds 5.56x45mm Box" (olive drab plastic, clipped under the receiver, the belt rising into the feed tray on the left; stencil "200 CARTRIDGES / 5.56 MM / 4 M855 - 1 M856 / M27 / FOR MG M249"), **plus every GoM STANAG** (20 to 150) in the M249's own magazine profile (user, 2026-10-22). A STANAG sits in the left-side well, tilted about 45 degrees down. |
| Belt | Nine visible belt rounds from the box to the feed tray, shortening one a shot under nine rounds (GoM's M60 way), shown only while the box is fitted |
| STANAG feed | Jam chance x2 while a STANAG is fitted (user, 2026-10-22: the manual's "will increase the chance of stoppages") |
| Family | `5.56x45mm` (the box joins it): GoM's 5.56 and its AP / HP / [+P] / Subsonic, .223, `Base.556Bullets` |
| Fire | Auto only, two Auto rates as two fire modes, **750 and 1000 rpm** (user, 2026-10-22: the original gun's gas regulator, normal / adverse, as GoM's BAR has two), spread 0.2 / 3.5 (M60 0.35 / 5.0) |
| Stats | damage 1.0-1.8 (GoM's M16A2: same round), HitChance 35 (M60 20, M16A2 50), Aimingtime 60, crit 25, range 55, jam 0.9, condition 1 in 210, ConditionMax 10 (M60) |
| Bipod | Integrated (`M249_Integrated_Bipod_Folded / _Deployed`), GoM's M60 bipod stats |
| Weight | 5.3 (GoM's M60 ratio, 0.71 of real), box 0.8 |
| Sound | 180 / 51 (realistic model, 18.3" barrel), M16 events |
| Reload | Custom clips (user, 2026-10-22): unload = open the feed cover, lift the belt, unhook the box; load = hang the box, lay the belt in the tray, close the cover; rack = the right-side cocking handle. STANAGs use the same clips. Gunworks `attachments` style, the box and magazine leaving with the hand. |
| Casings | Down and to the right (Hot Brass). No links (user, 2026-10-22). |
| Repair | RepairPack, Aiming 6 (GoM's LMGs) |

No rails, optics, lights, lasers, muzzle devices or bayonet: a 1993 M249 had none. Chambered round kept (no
`HaveChamber = false`, as GoM's M60): a box changed mid-belt fires on, a gun run dry is cocked again.
Loot (user, 2026-10-22: where GoM's M60 spawns): one alternative each in GoM's `Zombie_Army_Rifle_Spawner` (army
zombies' backs) and `World_Army_Heavy_Spawner` (army storage, heavy truck beds), packed as the M60's (gun, up to 2
boxes, up to 4 5.56 ammo boxes), and loose 200-round boxes in army ammunition storage as GoM's M60 box. Found guns
carry the box at GoM's M60 chance (50 %).

## 4e. Belt links (2026-10-22, designed, building)

The belt-fed guns' boxes are belts: each round held by a disintegrating link. User's choices (2026-10-22): links are
a supply of their own, consumed when a belt box is filled and given back when it is emptied, none lost, found and
crafted, for the M249 and GoM's M60 alike; a fired round's link is thrown out of the gun as real guns do and is
picked up off the ground (first decided "straight into the inventory", changed the same day to "follow the
realistic rules, treat links like hot brass").
- Items: `GunsOfTien.M27_Link` "M27 5.56mm Belt Link" (the M249's) and `GunsOfTien.M13_Link` "M13 7.62mm Belt Link"
  (GoM's M60), weight 0.002 each, and a box of each holding one belt ("Box of M27 Belt Links", 200; "Box of M13 Belt
  Links", 100) with Open / Pack recipes.
- Filling a belt box (the M249's 200-round box, GoM's M60 100-round box) with Gunworks' Load Rounds takes one link
  from the main inventory with each round, any round of the family (belts mix loads freely, as the real 4 ball : 1
  tracer). Without links the action does not start (a "Needs M27 belt links" halo); running out stops it. STANAG
  magazines never need links. Unloading rounds from a belt box gives each round's link back, and racking a
  chambered round out (belt box fitted) throws its link out with the round (2026-10-22).
- Firing from a fitted belt box throws each fired round's empty link out of the gun's right side: with Hot Brass it
  flies and lands as a real item (never despawned) with its own landing sound per surface (synthesised: a short dry
  steel tick on hard floors, a muffled tap on dirt and grass, a plip in water); without Hot Brass it drops at the
  shooter's feet; Ammo Maker's brass catchers catch links as they catch casings. A box fitted to a found gun counts
  as linked.
- Getting links: boxes of links in army ammunition storage (beside the 200-round boxes) and in the M249 / M60 kits;
  crafted at any surface from a small sheet of metal with sheet metal snips, a hammer and a metalworking punch
  (Metalworking 2, 50 links a sheet; vanilla's metalworking conventions); recovered by firing or unloading.

## 4f. Uzi, Mini Uzi and Micro Uzi (2026-10-23, designed, building)

IMI's open-bolt 9x19mm family, all of it 1993 material: the Uzi (1954; Action Arms imported the semi-automatic Uzi
carbine to the US 1980-1989, and US police units carried the submachine gun), the Mini Uzi (1980) and the Micro Uzi
(1986). Main mod, module `GunsOfTien`. The user's photos (2026-10-23): two angled views of an Uzi with its stock
folded, an angled Mini Uzi (compensator cuts), a side-on Mini Uzi (left side, stock deployed), a side-on Micro Uzi
(left side, stock folded forward, its butt plate a front grip) and a side-on IMI Uzi **Pistol** (right side; the
1984 semi-automatic, no stock), which the user chose to use for the Micro Uzi's receiver only. The full Uzi is
traced from the Commons photo "Uzi of the israeli armed forces" (Uziel Galishto, CC BY-SA 3.0; left side, side-on,
stock folded, Action Arms markings). No photo is kept in the repo (tmp/ref/uzi).

| | `GunsOfTien.UZI` "Uzi Submachine Gun" | `GunsOfTien.MINIUZI` "Mini Uzi Submachine Gun" | `GunsOfTien.MICROUZI` "Micro Uzi Submachine Gun" |
|---|---|---|---|
| Real | 260 mm barrel, 3.5 kg, 470 / 640 mm, 600 rpm | 197 mm, about 2.7 kg, 360 / 600 mm, 950 rpm | 117 mm, about 1.95 kg, 282 / 486 mm, 1200 rpm |
| Held | as a rifle: two hands, back slot (GoM's MP5) | **like a pistol, fits a holster** (user, 2026-10-23: GoM's MP5K / MAC-10 way), modelled upside down | the same, and **fits an ankle holster too** (user, 2026-10-23: `HolsterSmall` as GoM's Detective .38; vanilla's belt and shoulder holsters take it as well) |
| Stock | twin-strut metal stock folding down under the receiver; GoM's MP5 stock stats (HitChance ×1.15, AimingTime ×0.75) | single-strut stock folding forward along the right side; GoM's MAC-10 stock stats (×1.1, ×0.9) | the same, shorter |
| Damage | 1.0-1.6 (GoM's MP5) | 0.9-1.4 | 0.6-1.0 (GoM's MP5K, the same barrel) |
| HitChance / Aimingtime / RecoilDelay / range / crit | 50 / 40 / 15 / 30 / 20 | 48 / 30 / 13 / 27 / 20 | 45 / 25 / 12 / 25 / 25 |
| Spread (sustained / max) | 0.08 / 1.3 (slow, heavy) | 0.18 / 2.2 | 0.25 / 2.8 (MAC-10 0.2 / 2.0 at 1000) |
| Weight (GoM's SMG ratio ~0.78) | 2.7 | 2.1 | 1.5 |
| Sound (sound_model.py) | 89 / 25 | 97 / 28 | 113 / 32 |

All three: Auto / Single, one magazine profile "Uzi" for all, every magazine fits every gun (IMI's steel double-stack
magazines): **20, 25 and 32 rounds, plus 40 and 50** (user, 2026-10-23), "Uzi 32Rds 9x19mm Magazine", the 40 / 50
"... Extended Magazine" (GoM's MAC-10 40); weights 0.08 / 0.12 / 0.15 / 0.2 / 0.22. The magazine goes up the pistol
grip. The **AWC Mk9** fits all three (user, 2026-10-23) on the main mod's 9x19mm SMG mount device (the real Mk9 took
the Uzi barrel nut's place; the mount device stands in for that adapter), at a `canon` point on the barrel nut's
front face. No rails, optics, lights, lasers, other muzzle devices or bayonet (none on a 1993 Uzi). Ejection to the
right (Hot Brass: GoM's MP5 for the Uzi, its MP5K for the Mini / Micro). Repair: RepairPack, Aiming 3 (GoM's SMGs).
Family `9x19mm` (GoM's 9mm, the main mod's 147gr / Hollow Point / [+P+]). Models built in Blender by script at 0.72
(GoM's SMGs), the Uzi's top cocking knob does not reciprocate (bolt_fired = bolt_lock), the Uzi's grip safety and
the Mini's compensator cuts in the model.

Reload: the Mini / Micro as the MP7 (vanilla's handgun load, its reverse baked forward as the unload, handgun rack;
the main mod's own AnimSets and clip, since Post-93 is optional); the Uzi on GoM's MP5 clips first (its magazine well
is the grip, about 10 cm behind the MP5's; custom clips later if it shows).
Loot (GoM's routes), one alternative per spawner whose gun slot picks one Uzi at random (GoM's MP5 family, Post-93's
MP7s), so GoM's own guns keep most of their share: GoM's `World_Short_SMG_Spawner` (gun stores, pawn shops,
survivalist glove boxes, bandit bags; beside its MP5K, TEC-9, MAC-10) any of the three + up to 6 magazines of 20 / 25
/ 32 + up to 6 9x19mm boxes; `Zombie_Police_SMG_Spawner` (SWAT zombies, police bags, prison riot storage, SWAT
vehicles) the Uzi alone + up to 4 and 4 as GoM's MP5 kit (that spawner also hangs its gun on SWAT zombies' backs,
no place for a holstered Mini Uzi; first proposed with the Mini too); `Zombie_Crime_Rifle_Spawner` (user,
2026-10-23: the drug-trade gun of the 1980s; criminal and bounty hunter zombies' backs, bandit bags, pawn shops'
special guns, plank stashes) the Uzi alone + up to 4 32-round magazines and 4 boxes as GoM's FNC / XM177 kit there,
which leaves the Uzi half of that spawner's kits; the 40 and 50 loose in
`World_HighCap_Tactical_Magazine_Spawner` (GoM's SpawnHighCapMags) only. Magazines on a
found gun (GoM's MP5 rule, shortest likeliest, with each gun's standard first): Uzi 32:30, 25:20, 20:5; Mini and
Micro 20:30, 25:20, 32:5.

## 5. Open checks before building

- Can a mod add its own StatsFactory layer (for the PBS-1 rule), or does it need a hook in the attack path?
- Does `DoParam("SoundRadius = n")` on a gun script reach guns already in a save (HandWeapon copies the value at
  creation; Gunworks re-applies stats from a script-built shadow item)?
- Whether a round script needs an `AmmoType =` line.
- Exact loot table names for police / gun store / military (vanilla `ProceduralDistributions` + GoM spawners).
