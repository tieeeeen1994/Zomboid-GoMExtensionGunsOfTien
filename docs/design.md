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
- **Integral suppressor** (AS VAL, MP5SD): −17 dB, the same ×0.3 GoM gives a fitted suppressor.
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
| SVD | 170 / 30 | 224 / 64 | | MP5SD | 50 / 15 | **33 / 9** |
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

## 5. Open checks before building

- Can a mod add its own StatsFactory layer (for the PBS-1 rule), or does it need a hook in the attack path?
- Does `DoParam("SoundRadius = n")` on a gun script reach guns already in a save (HandWeapon copies the value at
  creation; Gunworks re-applies stats from a script-built shadow item)?
- Whether a round script needs an `AmmoType =` line.
- Exact loot table names for police / gun store / military (vanilla `ProceduralDistributions` + GoM spawners).
