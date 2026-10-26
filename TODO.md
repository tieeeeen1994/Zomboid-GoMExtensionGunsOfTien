# TODO

State of GoM Extension: Guns of Tien and its Post-93 sub-mod (written 2026-10-14). Nothing has been run in game yet.
Design: `docs/design.md` (main mod), `docs/post93_design.md` (Post-93). Findings: `CLAUDE.md`.

## Main mod `GoMExtensionGunsOfTien` — code complete, untested

Done: 12 rounds (box / carton / crate, own open / pack recipes) with profiles, realistic gun sounds (always on,
`SoundTable.lua` from `scripts/sound_model.py`), realistic piercing (option), 7.62x39 US + PBS-1 cycling (option), GoM
plain rounds renamed (9x39 SP-5, 5.45 7N6), no loot (special loads, as GoM's: Ammo Maker only), Hot Brass, tooltips, Ammo Maker for all 12
rounds incl. this mod's parts (soft point bullets S / M filed from standard bullets; birdshot pellets poured through
`Base.Strainer` + water), all art (`scripts/make_art.py`, `scripts/make_ammomaker_art.py`), generator
`scripts/gen_scripts.py`.

- [x] First load in single player: no Lua / script errors; spawn and fire every round (tracer = AmmoType line);
      7.62x39 US with and without a PBS-1; birdshot close / far; piercing option on / off; sounds in an existing save.
- [x] Ammo Maker: Make / Produce recipes of every new type fill in; Make Soft Point Bullet; Pour Birdshot Pellets
      (the water input at a furnace is copied from the pottery wheel, unverified at a furnace).
- [x] Workshop: workshop.txt, preview.png (1024, ad), both posters / icons, README, mod.info texts (2026-10-15;
      art from scripts/render_ad_guns.py + scripts/make_workshop_art.py). Upload from the game's Workshop menu.
      The game's uploader refuses any preview.png that is not exactly 256x256 (seen 2026-10-15): preview.png is a
      simple 256 one, the 1024 ad is preview2.png, added on the Steam page by hand. Uploaded again 2026-10-19 with
      the sawn-off stocks, offcuts and sawn-off barrel stats; preview2-5 are on the Steam page.
- [x] Sawn-off stocks (2026-10-19, SawnStock.lua): Saw Off Shotgun Stock on a Double Barrel, Stevens 555 and TOZ-34
      (any saw; listed only for a gun with its stock; a shell holder comes back); the stockless
      model in hand, on the back and on the floor, with full and sawn-off barrels, open and closed while reloading;
      the muzzle flash at the sawn-off barrels' end; the "Stock (Integrated)" tooltip row and the gun line; stats
      (Hit Chance, Recoil Delay; Aiming Time 30, 22 with sawn-off barrels); with
      sawn-off barrels too it attaches to a belt
      and a shoulder holster: hang it the right way up and not through the leg (holster points in gen_scripts.py,
      `HOLSTER_POINTS`), draw from the holster; Shell holder's Upgrade option hidden on a sawn-off stock; in MP the
      owner's copy changes model at once, another player sees it after the gun is next equipped.
- [ ] AWC Mk9 SMG suppressor (2026-10-22, Suppressors.lua, build_mk9.py, make_mk9_art.py): "Mk9 Suppressor (9mm SMGs)"
      and "9x19mm SMG Family Muzzle Mounting Device" on GoM's MP5 and MP5A2 (Post-93: the UMP9). To check in game:
      both attach to the MP5, MP5A2 and UMP9 only (not the MP5K, MP5SD, TEC-9 or the pistols), the wrench needed,
      the can only over the mount; GoM's MP5 / MP5A2 get the run-time `canon` point (no "model script not found" in
      the log; mount on the barrel, can's rear against the front sight housing, on the bore axis, in hand, on the
      back and on the floor); the parts lying on the floor (`world` pose) and their icons; quieter shots and no
      muzzle flash; Aiming Time ×1.1 with the can on; the MP5SD (25 / 6) quieter than an MP5 with the Mk9 (28 / 8),
      and the 147gr subsonic round making the SD quieter too (17 / 4, against the MP5 + Mk9's 18-19 / 5); the AS VAL at 22 / 6;
      preview8.png to add on the Steam page by hand; the tooltip lines (both parts, "Compatible Muzzle Device: 9x19mm SMG Muzzle Mount" on the three
      guns); both turning up from GoM's suppressor and muzzle device spawners (debug: spawn
      `MarzGuns.World_Suppressor_Spawner` / `MarzGuns.World_Muzzle_Device_Spawner` into a container a few times),
      and the mount (and Post-93's MP7 / P90 / SCAR-H mounts) from vanilla's Improved Choke Tube with GoM's
      VanillaAttachmentReplacement on (debug: spawn `Base.ChokeTubeImproved` a few times).
- [x] Sawn-off stocks, choices (2026-10-19): stats (Hit Chance x0.87, Recoil
      Delay x1.3, weight -0.5; Aiming Time x0.75 is the user's); holster only with sawn-off barrels too; all three holster slots (both
      belts and the shoulder holster), any saw and no sandbox option confirmed by the user; the Stevens 555's and
      TOZ-34's sawn-off barrels now get the Double Barrel's stats (user): check their tooltip and that Aiming Time /
      Hit Chance / spread / range change when they are fitted (gun tooltip), as on the Double Barrel.
- [x] Sawn-off offcuts (2026-10-19, SawnStock.lua, build_sawn_stocks.py, make_offcut_art.py): sawing the stock gives
      "<gun> Stock Offcut" (0.5), GoM's Saw Off Shotgun Barrels gives "<gun> Barrel Offcuts" (2.0; GoM's recipe gets
      our OnCreate at OnLoadMapZones, check its name still reads "Saw Off Shotgun Barrels" in the crafting window).
      Check: both arrive in the inventory (MP: the owner sees them at once), dropped at the feet when over capacity;
      icons next to GoM's (docs/sawn_offcuts_preview.png); on the floor they lie on their side resting on the
      ground, not sunk or floating (`world` points from sawn_offcuts.json, gen_scripts.py `floor_point`); the stock
      offcut burns in a campfire and goes into the charcoal recipe; the barrel offcuts smelt in a furnace (Smelt Large
      Steel Item, 4 uses into a steel crucible).
- [x] Sawing sounds (2026-10-19): Saw Off Shotgun Stock plays the wood saw (vanilla `Sawing`), GoM's Saw Off Shotgun
      Barrels the metal saw (`CraftMetalSawing`, our timed action handed over in `ISHandcraftAction.new`); the barrel
      cut keeps its anim and saw in hand; in MP other players hear it too.
- [x] Tooltips fixed 2026-10-19 (RoundTooltips.lua, HandlingTooltips.lua, GoMFixes.lua): a round of each kind (ours,
      GoM's 5.56 variants, .38 Special, slug) shows one line per stat and no typos; with RealisticPiercing on,
      plain .30-06 / .308 / 7.62x51 and the 7N6 add their piercing lines, off they do not (option change needs a
      rejoin); the shell holder, a bayonet, the Picatinny Rail, the speedloader, a sling, the VP70M stock, the Glock 17,
      Camp Carbine, VP70M and Double Deuce have their new lines; a Karabiner 98k bayonet now fixes on an M16 (Attach
      Bayonet in the gun's menu) and stabs; the overpressured 5.56 widens full-auto spread. The sawn-off stock's lines
      show on a sawn-off break-action shotgun only, a whole one of the same type shows none, in the inventory, the
      hotbar and a crafting slot ("Fits a holster." with sawn-off barrels, else "Fits a holster if barrels are sawed off."). The
      same for every gun with integrated parts: an MP5 / G36C / MP7 shows its stock's lines only while deployed
      (fold it with the tooltip open: the lines go on the next frame), the M60 its deployed or folded bipod's, the
      SPAS-12 its pump or semi lines, the MP7A1 its grip's only while unfolded.
- [x] preview5.png (1024, the sawn-off shotguns) on the Steam page (2026-10-19). Rebuild:
      `blender -b --factory-startup -P scripts/render_ad_guns.py -- tmp/ad db_full db_sawn`, then
      `python3 scripts/make_workshop_art.py preview5`.
- [x] preview3.png (1024, the Five-seveN and the UCP fitted out) on the Steam page (2026-10-19).
      Rebuild: `blender -b --factory-startup -P scripts/render_ad_guns.py -- tmp/ad fiveseven ucp`, then
      `python3 scripts/make_workshop_art.py preview3` (names select what it writes; on the Mac it uses DIN Alternate
      Bold, the nearest to Windows' Bahnschrift that preview2 was drawn with).

## Tooltip review (2026-10-19)

Every tooltip text both mods show, as the game will draw it: Information lines are listed only where Guns of Tien
changes or adds them (GoM's other lines are untouched), joined here with " / " (one line each in game). Generated
from the real files by `scripts/list_tooltips.py` (needs lupa, see its header); run it again after a tooltip change.
Tick each one that reads right; note what to change. Corrections: rewrite the text after the colon and leave the
key in backticks as it is (the item type, the translation key, or `File.lua NAME` for a text in Lua code); `python3
scripts/list_tooltips.py --diff TODO.md` lists every entry whose text differs from the code.

### Rounds: Information lines (RealisticPiercing off; on, the plain .30-06 / .308 / 7.62x51 add "Piercing targets / Able to hit up to 2 targets", the 7N6 "Critical Chance increased by 10% / Piercing targets / Able to hit up to 3 targets")

- [x] .223 Remington Round (`SWMG.223_Bullet`): Damage to targets decreased by 30% / Critical Damage decreased by 20% / Critical Chance decreased by 10% / Chance to degrade weapon condition decreased by 33%
- [x] .30-06 Springfield Soft Point Round (`GunsOfTien.3006_Bullet_SP`): Damage to targets increased by 20% / Critical Damage increased by 15% / Critical Chance increased by 10% / Does not pierce
- [x] .30-30 Round (`SWMG.3030_Bullet`): Does not pierce
- [x] .30-30 Round (Vanilla) (`Base.3030Bullets`): Does not pierce
- [x] .308 Winchester Round (`SWMG.308_Bullet`): Damage to targets decreased by 25% / Critical Damage decreased by 15% / Critical Chance decreased by 10% / Chance to degrade weapon condition decreased by 33%
- [x] .308 Winchester Soft Point Round (`GunsOfTien.308_Bullet_SP`): Damage to targets increased by 20% / Critical Damage increased by 15% / Critical Chance increased by 10% / Does not pierce
- [x] .38 Special Round (`SWMG.38_Bullet`): Damage to targets decreased by 20% / Critical Damage decreased by 20% / Critical Chance decreased by 10% / Chance to degrade weapon condition decreased by 17%
- [x] .38 Special Round (Vanilla) (`Base.Bullets38`): Damage to targets decreased by 20% / Critical Damage decreased by 20% / Critical Chance decreased by 10% / Chance to degrade weapon condition decreased by 17%
- [x] .45 ACP Hollow Point Round (`GunsOfTien.45_Bullet_HollowPoint`): Damage to targets increased by 20% / Critical Damage increased by 15% / Critical Chance increased by 5% / Chance to degrade weapon condition increased by 11%
- [x] .45 ACP [+P] Round (`GunsOfTien.45_Bullet_P`): Damage to targets increased by 15% / Critical Damage increased by 10% / Sound Radius and Volume increased by 10% / Chance to degrade weapon condition increased by 43%
- [x] 12 Gauge Birdshot Shell (`GunsOfTien.12Gauge_Shell_Birdshot`): Damage to targets decreased by 70% / Critical Damage decreased by 50% / Critical Chance decreased by 60% / Range reduced by 50% / Pellet spread doubled
- [x] 12 Gauge Slug Shell (`SWMG.12Gauge_Shell_Slug`): Damage to targets increased by 100% / Piercing targets / Able to hit up to 3 targets / One slug per shell
- [x] 5.56x45mm Armor Piercing Round (`SWMG.556x45_Bullet_ArmorPiercing`): Damage to targets decreased by 15% / Critical Damage decreased by 5% / Critical Chance decreased by 10% / Piercing targets / Able to hit up to 5 targets
- [x] 5.56x45mm Hollow Point Round (`SWMG.556x45_Bullet_HollowPoint`): Damage to targets increased by 20% / Critical Damage increased by 15% / Critical Chance increased by 5% / Chance to degrade weapon condition increased by 18%
- [x] 5.56x45mm Subsonic Round (`SWMG.556x45_Bullet_Subsonic`): Damage to targets decreased by 60% / Sound Radius and Volume reduced by 50% / Chance to degrade weapon condition halved / Needs racking every shot / Stacks with suppressors for maximum effectiveness
- [x] 5.56x45mm [+P] Round (`SWMG.556x45_Bullet_Overpressured`): Damage to targets increased by 50% / Critical Damage increased by 50% / Critical Chance increased by 5% / Automatic fire spread doubled / Chance to degrade weapon condition doubled / Piercing targets / Able to hit up to 2 targets
- [x] 7.62x39mm Soft Point Round (`GunsOfTien.762x39_Bullet_SP`): Damage to targets increased by 20% / Critical Damage increased by 15% / Critical Chance increased by 5% / Chance to degrade weapon condition increased by 11% / Does not pierce
- [x] 7.62x39mm Steel Core Round (Armor Piercing) (`GunsOfTien.762x39_Bullet_SteelCore`): Damage to targets decreased by 10% / Critical Damage decreased by 5% / Critical Chance decreased by 10% / Chance to degrade weapon condition increased by 18% / Piercing targets / Able to hit up to 3 targets
- [x] 7.62x39mm US Round (Subsonic) (`GunsOfTien.762x39_Bullet_US`): Damage to targets decreased by 50% / Critical Damage decreased by 20% / Sound Radius and Volume reduced by 50% / Chance to degrade weapon condition halved / Needs racking every shot / Cycles normally with a PBS-1 suppressor / Stacks with suppressors for maximum effectiveness
- [x] 9x19mm 147gr Round (Subsonic) (`GunsOfTien.9x19_Bullet_Subsonic`): Damage to targets decreased by 15% / Sound Radius and Volume reduced by 30% / Stacks with suppressors for maximum effectiveness
- [x] 9x19mm Hollow Point Round (`GunsOfTien.9x19_Bullet_HollowPoint`): Damage to targets increased by 20% / Critical Damage increased by 15% / Critical Chance increased by 5% / Chance to degrade weapon condition increased by 11%
- [x] 9x19mm [+P+] Round (`GunsOfTien.9x19_Bullet_PPP`): Damage to targets increased by 20% / Critical Damage increased by 10% / Sound Radius and Volume increased by 10% / Chance to degrade weapon condition increased by 67%
- [x] 9x39mm SP-6 Round (Armor Piercing) (`GunsOfTien.9x39_Bullet_SP6`): Damage to targets decreased by 10% / Critical Damage decreased by 5% / Piercing targets / Able to hit up to 3 targets

### Guns and parts: Information lines (always shown)

- [x] .50 Desert Eagle (`MarzGuns.DEAGLE`): Uses .50 rounds. / Compatible Mounting Device: Heavy Pistol Rail
- [x] 5.7x28mm Five-SeveN (`MarzGuns.FIVESEVEN`): Uses 5.7x28mm rounds. / Compatible Mounting Device: Beretta Mount / Compatible Muzzle Device: 5.7x28mm Muzzle Mount / Standard rounds pierce and can hit up to 2 targets.
- [x] 6Rds .38 Special/.357 Magnum Speedloader (`MarzGuns.38357SpeedLoader6`): Uses .38Special/.357 Magnum rounds. / Reloads the revolver faster when fully loaded.
- [x] 9x39mm 10Rds Magazine (`MarzGuns.9x39Magazine10`): Uses 9x39mm rounds.
- [x] 9x39mm 20Rds Magazine (`MarzGuns.9x39Magazine20`): Uses 9x39mm rounds.
- [x] AA-12 Automatic Shotgun (`MarzGuns.AA12`): Uses 12-gauge shells. / Available Picatinny Slots: Down, Left, Right
- [x] AK-47 Assault Rifle (`MarzGuns.AK47`): Uses 7.62x39mm rounds. / Compatible Mounting Device: AK Mount / Compatible Muzzle Device: AK Muzzle Mount
- [x] AK-74 Assault Rifle (`MarzGuns.AK74`): Uses 5.45x39mm rounds. / Compatible Mounting Device: AK Mount / Compatible Muzzle Device: AK Muzzle Mount
- [x] AKS-74U Assault Rifle (`MarzGuns.AKS74U`): Uses 5.45x39mm rounds. / Compatible Mounting Device: AK Mount / Available Picatinny Slots: Down / Compatible Muzzle Device: AK Muzzle Mount
- [x] AR-15 Civilian Rifle (`MarzGuns.AR15`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down / Can attach a bayonet.
- [x] AS VAL Assault Rifle (`MarzGuns.ASVAL`): Uses 9x39mm rounds. / Compatible Mounting Device: AK Mount / Available Picatinny Slots: Down, Left, Right
- [x] Bakelite 60Rds Extended 5.45x39mm Magazine (`MarzGuns.545x39Magazine60_Bakelite`): Uses 5.45x39mm rounds.
- [x] Benelli M4 Semi-Shotgun (`MarzGuns.BENELLI_M4`): Uses 12-gauge shells. / Available Picatinny Slots: Up / Can attach a bayonet.
- [x] Beretta Burst M93R (`MarzGuns.M93R`): Uses 9x19mm rounds. / Compatible Mounting Device: Beretta Mount / Compatible Muzzle Device: Pistol Muzzle Mount
- [x] Beretta M92FS (`MarzGuns.M92FS`): Uses 9x19mm rounds. / Compatible Mounting Device: Beretta Mount / Compatible Muzzle Device: Pistol Muzzle Mount
- [x] Bipod (Deployed) (`MarzGuns.Bipod_Deployed`): Aiming Time increased by 10% / Critical and Hit Chance increased by 15% / Automatic fire spread reduced by 35% / Needs Screwdriver to install or remove.
- [x] BrightPoint-5 Light (`MarzGuns.BrightPoint-5_Light`): Provides Weapon Light / Aiming Time increased by 5 / Needs Screwdriver to install or remove.
- [x] Browning Automatic Rifle (`MarzGuns.BAR`): Uses .30-06 Springfield rounds.
- [x] Browning Hi-Power (`MarzGuns.HIPOWER`): Uses 9x19mm rounds. / Compatible Mounting Device: Beretta Mount / Compatible Muzzle Device: Pistol Muzzle Mount
- [x] CAR-15 Assault Rifle (`MarzGuns.CAR15`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down, Left, Right / Compatible Muzzle Device: AR Muzzle Mount
- [x] Colt M1911 (`MarzGuns.M1911`): Uses .45 rounds. / Compatible Mounting Device: Colt Mount / Compatible Muzzle Device: .45 Muzzle Mount
- [x] Colt Python Revolver (`MarzGuns.PYTHON`): Uses .38Special/.357 Magnum rounds. / Compatible with 6-round speedloader.
- [x] Detective .38 Revolver (`MarzGuns.DETECTIVE_38`): Uses .38Special/.357 Magnum rounds. / Compatible with 6-round speedloader.
- [x] Double Barrel Sawnoff (`MarzGuns.DOUBLEBARREL_Barrel_Sawnoff_Open`): Aiming Time reduced by 25% / Hit Chance increased by 8% / Pellet spread increased by 233% / Range reduced by 25%
- [x] Double Barrel Sawnoff (`MarzGuns.DOUBLEBARREL_Barrel_Sawnoff_Close`): Aiming Time reduced by 25% / Hit Chance increased by 8% / Pellet spread increased by 233% / Range reduced by 25%
- [x] FAMAS Assault Rifle (`MarzGuns.FAMAS`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down / Compatible Muzzle Device: AR Muzzle Mount / Can attach a bayonet.
- [x] FN FAL Battle Rifle (`MarzGuns.FAL`): Uses .308/7.62x51mm NATO rounds. / Available Picatinny Slots: Up, Down, Left, Right
- [x] FN FNC Assault Rifle (`MarzGuns.FNC`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up
- [x] G3 Battle Rifle (`MarzGuns.G3`): Uses .308/7.62x51mm NATO rounds. / Available Picatinny Slots: Up, Down, Left, Right / Can attach a bayonet.
- [x] G36 Assault Rifle (`MarzGuns.G36`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Down, Left, Right / Compatible Muzzle Device: AR Muzzle Mount
- [x] G36C Assault Rifle (`MarzGuns.G36C`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down, Left, Right / Compatible Muzzle Device: AR Muzzle Mount
- [x] Glock-17 (`MarzGuns.GLOCK17`): Uses 9x19mm rounds. / Compatible Mounting Device: Beretta Mount / Compatible Muzzle Device: Pistol Muzzle Mount
- [x] Glock-17 17Rds 9x19mm Magazine (`MarzGuns.9x19Magazine17_GLOCK17`): Uses 9x19mm rounds.
- [x] Heckler & Koch USP (`MarzGuns.USP`): Uses .45 rounds. / Compatible Mounting Device: Colt Mount / Compatible Muzzle Device: .45 Muzzle Mount
- [x] Heckler & Koch VP70M (`MarzGuns.VP70M`): Uses 9x19mm rounds.
- [x] Ingram MAC-10 Machine Pistol (`MarzGuns.MAC10`): Uses .45 rounds. / Compatible Muzzle Device: .45 Muzzle Mount
- [x] Karabiner 98k Bayonet (`MarzGuns.K98_BAYONET`): Attachable on compatible guns. / Cannot install if a muzzle device or M203 is installed.
- [x] LP Tactical Light (`MarzGuns.LP_Light`): Provides Weapon Light / Aiming Time increased by 5 / Needs Screwdriver to install or remove.
- [x] M1 Bayonet (`MarzGuns.M1_BAYONET`): Attachable on compatible guns. / Cannot install if a muzzle device or M203 is installed.
- [x] M1 Garand Battle Rifle (`MarzGuns.M1_GARAND`): Uses .30-06 Springfield rounds. / Can attach a bayonet.
- [x] M14 Battle Rifle (`MarzGuns.M14`): Uses .308/7.62x51mm NATO rounds. / Available Picatinny Slots: Up, Down / Can attach a bayonet.
- [x] M16A1 Assault Rifle (`MarzGuns.M16A1`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down / Compatible Muzzle Device: AR Muzzle Mount / Can attach a bayonet.
- [x] M16A2 Assault Rifle (`MarzGuns.M16A2`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down, Left, Right / Compatible Muzzle Device: AR Muzzle Mount / Can attach a bayonet.
- [x] M16A2 Assault Rifle with M203 (`MarzGuns.M16A2_M203`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up / Compatible Muzzle Device: AR Muzzle Mount
- [x] M16A3 Assault Rifle (`MarzGuns.M16A3`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down, Left, Right / Compatible Muzzle Device: AR Muzzle Mount / Can attach a bayonet.
- [x] M1903 Springfield Bolt Rifle (`MarzGuns.M1903`): Uses .30-06 Springfield rounds. / Compatible Mounting Device: Sniper Mount / Can attach a bayonet.
- [x] M1905 Bayonet (`MarzGuns.M1905_BAYONET`): Attachable on compatible guns. / Cannot install if a muzzle device or M203 is installed.
- [x] M24 Sniper Rifle (`MarzGuns.M24`): Uses .308/7.62x51mm NATO rounds. / Available Picatinny Slots: Up
- [x] M4A1 Assault Rifle (`MarzGuns.M4A1`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down, Left, Right / Compatible Muzzle Device: AR Muzzle Mount / Can attach a bayonet.
- [x] M5 Bayonet (`MarzGuns.M5_BAYONET`): Attachable on compatible guns. / Cannot install if a muzzle device or M203 is installed.
- [x] M60 Machine Gun (`MarzGuns.M60`): Uses .308/7.62x51mm NATO rounds.
- [x] M9 Bayonet (`MarzGuns.M9_BAYONET`): Attachable on compatible guns. / Cannot install if a muzzle device or M203 is installed.
- [x] MK2 Foregrip (`MarzGuns.MK2_Foregrip`): Aiming Time reduced by 25% / Critical and Hit Chance increased by 10% / Automatic fire spread reduced by 10% / Needs Screwdriver to install or remove.
- [x] MKC Foregrip (`MarzGuns.MKC_Foregrip`): Aiming Time reduced by 5% / Critical and Hit Chance increased by 25% / Automatic fire spread reduced by 10% / Needs Screwdriver to install or remove.
- [x] MP5 Submachine Gun (`MarzGuns.MP5`): Uses 9x19mm rounds. / Available Picatinny Slots: Up, Down, Left, Right
- [x] MP5A2 Submachine Gun (`MarzGuns.MP5A2`): Uses 9x19mm rounds. / Available Picatinny Slots: Up, Down, Left, Right
- [x] MP5K Submachine Gun (`MarzGuns.MP5K`): Uses 9x19mm rounds. / Available Picatinny Slots: Up
- [x] MP5SD Submachine Gun (`MarzGuns.MP5SD`): Uses 9x19mm rounds. / Available Picatinny Slots: Up, Down, Left, Right
- [x] Marlin 1895 Rifle (`MarzGuns.M1895`): Uses .45-70 Government rounds. / Available Picatinny Slots: Up
- [x] Marlin Camp Carbine (`MarzGuns.CAMP_CARBINE`): Uses .45 rounds.
- [x] Mini-14 Semi-Automatic Rifle (`MarzGuns.MINI_14`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down
- [x] Model 70 Bolt Rifle (`MarzGuns.MODEL_70`): Uses .223/5.56x45mm NATO rounds. / Compatible Mounting Device: Sniper Mount
- [x] Model 70 Sling (`MarzGuns.Model_70_Sling`): Reduces encumbrance. / Needs Screwdriver to install or remove.
- [x] Mosin-Nagant Bolt Rifle (`MarzGuns.MOSIN`): Uses 7.62x54mmR rounds. / Compatible Mounting Device: Sniper Mount / Can attach a bayonet. / Compatible with 5-round stripper clip.
- [x] Mossberg 590 Shotgun (`MarzGuns.MOSSBERG_590`): Uses 12-gauge shells. / Available Picatinny Slots: Up / Can attach a bayonet.
- [x] PSG-1 Semi-Automatic Rifle (`MarzGuns.PSG1`): Uses .308/7.62x51mm NATO rounds. / Available Picatinny Slots: Up, Down
- [x] Picatinny Rail (`MarzGuns.Picatinny_Rail`): Adds a rail on one of the slots of the gun. / Options will be presented in the upgrade menu / Needs Screwdriver to install or remove.
- [x] Remington 700 Bolt Rifle (`MarzGuns.REMINGTON_700`): Uses .308/7.62x51mm NATO rounds. / Compatible Mounting Device: Sniper Mount
- [x] Remington 700 Sling (`MarzGuns.Rem700_Sling`): Reduces encumbrance. / Needs Screwdriver to install or remove.
- [x] Remington 870 Shotgun (`MarzGuns.REMINGTON_870`): Uses 12-gauge shells. / Available Picatinny Slots: Up / Can attach a bayonet.
- [x] Rhino Revolver (`MarzGuns.RHINO`): Uses .38Special/.357 Magnum rounds. / Compatible with 6-round speedloader.
- [x] SR7 Tactical Light (`MarzGuns.SR7_Light`): Provides Weapon Light / Aiming Time increased by 5 / Needs Screwdriver to install or remove.
- [x] SVD Semi-Automatic Rifle (`MarzGuns.SVD`): Uses 7.62x54mmR rounds. / Compatible Mounting Device: AK Mount / Available Picatinny Slots: Down
- [x] Shellholder (`MarzGuns.Shellholder`): Recoil Delay reduced by 40% / Attachable on stocks. / Needs Screwdriver to install or remove.
- [x] Sig Sauer P226 (`MarzGuns.P226`): Uses 9x19mm rounds. / Compatible Mounting Device: Beretta Mount / Compatible Muzzle Device: Pistol Muzzle Mount
- [x] Stevens 555 Barrel Sawnoff (`MarzGuns.STEVENS_555_Barrel_Sawnoff_Open`): Aiming Time reduced by 25% / Hit Chance increased by 8% / Pellet spread increased by 233% / Range reduced by 25%
- [x] Stevens 555 Barrel Sawnoff (`MarzGuns.STEVENS_555_Barrel_Sawnoff_Close`): Aiming Time reduced by 25% / Hit Chance increased by 8% / Pellet spread increased by 233% / Range reduced by 25%
- [x] Stolzer & Son of Kansas 2-Bore Rifle (`MarzGuns.DOUBLE_DEUCE`): Uses 2-bore rounds.
- [x] Stub Foregrip (`MarzGuns.Stub_Foregrip`): Aiming Time reduced by 20% / Critical and Hit Chance increased by 15% / Automatic fire spread reduced by 15% / Needs Screwdriver to install or remove.
- [x] TL Tactical Light (`MarzGuns.TL_Light`): Provides Weapon Light / Aiming Time increased by 5 / Needs Screwdriver to install or remove.
- [x] TOZ-34 Barrel Sawnoff (`MarzGuns.TOZ34_Barrel_Sawnoff_Close`): Aiming Time reduced by 25% / Hit Chance increased by 8% / Pellet spread increased by 233% / Range reduced by 25%
- [x] TOZ-34 Barrel Sawnoff (`MarzGuns.TOZ34_Barrel_Sawnoff_Open`): Aiming Time reduced by 25% / Hit Chance increased by 8% / Pellet spread increased by 233% / Range reduced by 25%
- [x] Trench Shotgun (`MarzGuns.TRENCHGUN`): Uses 12-gauge shells. / Can attach a bayonet.
- [x] VP70M Stock (`MarzGuns.VP70M_Stock`): No Direct Stat Changes / Needs Screwdriver to install or remove.
- [x] Winchester 1873 Rifle (`MarzGuns.W1873`): Uses .38Special/.357 Magnum rounds. / Available Picatinny Slots: Up
- [x] Winchester 1887 Shotgun (`MarzGuns.W1887`): Uses 12-gauge shells. / Available Picatinny Slots: Up
- [x] Winchester 1894 Rifle (`MarzGuns.W1894`): Uses .30-30 Winchester rounds. / Available Picatinny Slots: Up
- [x] XM177 Assault Rifle (`MarzGuns.XM177`): Uses .223/5.56x45mm NATO rounds. / Available Picatinny Slots: Up, Down, Left, Right / Can attach a bayonet.
- [x] Every laser, AimRight Laser, LRX-7 Laser, PJ-3 Laser, PX1 Laser, TR-1 Laser (`LaserMenu.lua NOTE`): Bonuses only apply when on.

### Post-93: Information lines (always shown)

- [x] 4.6x30mm DM11 Round (`GunsOfTienPost93.46x30_Bullet`): DM11 solid copper-plated steel bullet / Piercing targets / Able to hit up to 2 targets
- [x] 4.6x30mm Family Muzzle Mounting Device (`GunsOfTienPost93.MP7_Muzzle_Mount_Device`): No Direct Stat Changes / Enables its Suppressor / Needs Wrench to install or remove.
- [x] 4.6x30mm Subsonic Round (`GunsOfTienPost93.46x30_Bullet_Subsonic`): Damage to targets decreased by 40% / Sound radius and volume reduced by 30% / Does not pierce / Stacks with suppressors for maximum effect
- [x] 5.7x28mm Family Muzzle Mounting Device (`GunsOfTienPost93.P90_Muzzle_Mount_Device`): No Direct Stat Changes / Enables its Suppressor / Needs Wrench to install or remove.
- [x] 5.7x28mm SB193 Round (Subsonic) (`GunsOfTienPost93.57x28_Bullet_SB193`): Damage to targets decreased by 30% / Sound radius and volume reduced by 30% / Does not pierce / Stacks with suppressors for maximum effect
- [x] 5.7x28mm SS190 Round (`GunsOfTienPost93.57x28_Bullet`): SS190 steel and aluminium penetrator / Piercing targets / Able to hit up to 2 targets
- [x] 5.7x28mm SS197SR Round (Hollow Point) (`GunsOfTienPost93.57x28_Bullet_SS197SR`): Polymer tip, expands / Damage to targets increased by 15% / Critical damage increased by 10% / Does not pierce
- [x] Five-SeveN 20Rds 5.7x28mm Magazine (`GunsOfTienPost93.57x28Magazine20_FIVESEVEN`): Uses 5.7x28mm rounds.
- [x] Five-SeveN 30Rds 5.7x28mm Extended Magazine (`GunsOfTienPost93.57x28Magazine30_FIVESEVEN`): Uses 5.7x28mm rounds.
- [x] MP7 20Rds 4.6x30mm Magazine (`GunsOfTienPost93.46x30Magazine20_MP7`): Uses 4.6x30mm rounds.
- [x] MP7 30Rds 4.6x30mm Magazine (`GunsOfTienPost93.46x30Magazine30_MP7`): Uses 4.6x30mm rounds.
- [x] MP7 40Rds 4.6x30mm Magazine (`GunsOfTienPost93.46x30Magazine40_MP7`): Uses 4.6x30mm rounds.
- [x] MP7 60Rds Drum 4.6x30mm Magazine (`GunsOfTienPost93.46x30Magazine60_MP7`): Uses 4.6x30mm rounds.
- [x] MP7A1 Submachine Gun (`GunsOfTienPost93.MP7A1`): Uses 4.6x30mm rounds. / Integrated Picatinny rails: Up, Left, Right / Standard rounds pierce and can hit up to 2 targets.
- [x] MP7A2 Submachine Gun (`GunsOfTienPost93.MP7A2`): Uses 4.6x30mm rounds. / Integrated Picatinny rails: Up, Left, Right, Down / Standard rounds pierce and can hit up to 2 targets.
- [x] P90 50Rds 5.7x28mm Magazine (`GunsOfTienPost93.57x28Magazine50_P90`): Uses 5.7x28mm rounds.
- [x] P90 Submachine Gun (`GunsOfTienPost93.P90TR`): Uses 5.7x28mm rounds. / Integrated Picatinny rails: Up, Left, Right / 50-round magazine on top. Ejects spent cases downward. / Standard rounds pierce and can hit up to 2 targets.
- [x] Rotex-II Suppressor (4.6x30mm Weapons) (`GunsOfTienPost93.MP7_Suppressor`): Sound Radius and Volume reduced by 70% / Damage to targets decreased by 10% / Removes Muzzle Flash / Needs its Muzzle Mount Device
- [x] SFN-57 Suppressor (`GunsOfTienPost93.FIVESEVEN_Suppressor`): Sound Radius and Volume reduced by 70% / Damage to targets decreased by 10% / Removes Muzzle Flash / Needs its Muzzle Mount Device
- [x] SP90 Suppressor (`GunsOfTienPost93.P90_Suppressor`): Sound Radius and Volume reduced by 70% / Damage to targets decreased by 10% / Removes Muzzle Flash / Needs its Muzzle Mount Device
- [x] UCP 20Rds 4.6x30mm Magazine (`GunsOfTienPost93.46x30Magazine20_UCP`): Uses 4.6x30mm rounds.
- [x] UCP 40Rds Drum 4.6x30mm Magazine (`GunsOfTienPost93.46x30Magazine40_UCP`): Uses 4.6x30mm rounds.
- [x] UCP Prototype (`GunsOfTienPost93.UCP`): Uses 4.6x30mm rounds. / H&K prototype / Compatible Mounting Device: Beretta Mount / Compatible Muzzle Device: 4.6x30mm Muzzle Mount / Standard rounds pierce and can hit up to 2 targets.

### Guns: lines shown only while that part is fitted (after the gun's own lines)

- [x] AKS-74U Integrated Stock (Deployed) (`MarzGuns.AKS74U_Integrated_Stock_Deployed`): Folding stock deployed: / Aiming Time reduced by 15% / Hit Chance increased by 25% / Automatic fire spread reduced by 25%
- [x] AS VAL Integrated Stock (Deployed) (`MarzGuns.ASVAL_Integrated_Stock_Deployed`): Folding stock deployed: / Aiming Time reduced by 10% / Hit Chance increased by 15% / Automatic fire spread reduced by 25%
- [x] BAR Integrated Bipod (Deployed) (`MarzGuns.BAR_Integrated_Bipod_Deployed`): Folding bipod deployed: / Aiming Time increased by 20% / Critical and Hit Chance increased by 25%
- [x] CAR-15 Integrated Stock (Deployed) (`MarzGuns.CAR15_Integrated_Stock_Deployed`): Collapsible stock deployed: / Aiming Time reduced by 15% / Hit Chance increased by 15%
- [x] Double Barrel Stock Sawnoff (`GunsOfTien.DOUBLEBARREL_Stock_Sawnoff`): Sawn-off stock: / Aiming Time reduced by 25% / Hit Chance reduced by 13% / Recoil Delay increased by 30%
- [x] FN FNC Integrated Stock (Deployed) (`MarzGuns.FNC_Integrated_Stock_Deployed`): Folding stock deployed: / Aiming Time reduced by 5% / Hit Chance increased by 15%
- [x] G36 Integrated Stock (Deployed) (`MarzGuns.G36_Integrated_Stock_Deployed`): Folding stock deployed: / Aiming Time reduced by 15% / Hit Chance increased by 15%
- [x] G36C Integrated Stock (Deployed) (`MarzGuns.G36C_Integrated_Stock_Deployed`): Folding stock deployed: / Aiming Time reduced by 25% / Hit Chance increased by 15% / Automatic fire spread reduced by 25%
- [x] M60 Integrated Bipod (Deployed) (`MarzGuns.M60_Integrated_Bipod_Deployed`): Folding bipod deployed: / Aiming Time increased by 30% / Critical and Hit Chance increased by 10% / No endurance used to fire
- [x] M60 Integrated Bipod (Folded) (`MarzGuns.M60_Integrated_Bipod_Folded`): Folding bipod folded: / Hit Chance reduced by 20% / Firing uses endurance
- [x] MAC10 Integrated Stock (Deployed) (`MarzGuns.MAC10_Integrated_Stock_Deployed`): Collapsible stock deployed: / Aiming Time reduced by 10% / Hit Chance increased by 10%
- [x] MP5 Integrated Stock (Deployed) (`MarzGuns.MP5_Integrated_Stock_Deployed`): Collapsible stock deployed: / Aiming Time reduced by 25% / Hit Chance increased by 15%
- [x] MP5SD Integrated Stock (Deployed) (`MarzGuns.MP5SD_Integrated_Stock_Deployed`): Collapsible stock deployed: / Aiming Time reduced by 25% / Hit Chance increased by 15%
- [x] MP7 Integrated Foregrip (Deployed) (`GunsOfTienPost93.MP7A1_Integrated_Foregrip_Deployed`): Folding front grip unfolded: / Aiming Time reduced by 20% / Critical and Hit Chance increased by 15% / Automatic fire spread reduced by 15%
- [x] MP7 Integrated Stock (Deployed) (`GunsOfTienPost93.MP7A1_Integrated_Stock_Deployed`): Collapsible stock deployed: / Aiming Time reduced by 25% / Hit Chance increased by 15%
- [x] SPAS-12 Integrated Stock (Deployed) (`MarzGuns.SPAS12_Integrated_Stock_Deployed`): Folding stock deployed: / Aiming Time reduced by 10% / Hit Chance increased by 10%
- [x] SPAS-12 Mode Selector (Pump) (`MarzGuns.SPAS12_Selector_Pump`): Pump action: / Needs racking every shot
- [x] SPAS-12 Mode Selector (Semi) (`MarzGuns.SPAS12_Selector_Semi`): Semi-automatic: / Jam Chance increased by 60% / Recoil Delay reduced by 50%
- [x] Stevens 555 Stock Sawnoff (`GunsOfTien.STEVENS_555_Stock_Sawnoff`): Sawn-off stock: / Aiming Time reduced by 25% / Hit Chance reduced by 13% / Recoil Delay increased by 30%
- [x] TOZ-34 Stock Sawnoff (`GunsOfTien.TOZ34_Stock_Sawnoff`): Sawn-off stock: / Aiming Time reduced by 25% / Hit Chance reduced by 13% / Recoil Delay increased by 30%
- [x] Sawn-off stock, also (`Tooltips.lua FITS_HOLSTER / NEEDS_BARRELS`): Fits a holster. (with sawn-off barrels) / Fits a holster if barrels are sawed off. (with full barrels)

### Item, recipe and part-row tooltips (main mod Tooltip.json)

- [x] `Tooltip_Recipe_Make762x39SS`: Assemble 7.62x39mm US sub sonic round - 1960s.
- [x] `Tooltip_Recipe_Produce762x39SS`: Assemble 7.62x39mm US rounds with reloading press.
- [x] `Tooltip_Recipe_Make762x39SP`: Assemble 7.62x39mm SP soft point round - 1980s.
- [x] `Tooltip_Recipe_Produce762x39SP`: Assemble 7.62x39mm SP rounds with reloading press.
- [x] `Tooltip_Recipe_Make9x19ParaSS`: Assemble 9mm Luger SS 147gr sub sonic round - 1988.
- [x] `Tooltip_Recipe_Produce9x19ParaSS`: Assemble 9mm Luger SS rounds with reloading press.
- [x] `Tooltip_Recipe_Make9x19ParaHP`: Assemble 9mm Luger HP hollow point round - 1970s.
- [x] `Tooltip_Recipe_Produce9x19ParaHP`: Assemble 9mm Luger HP rounds with reloading press.
- [x] `Tooltip_Recipe_Make9x19ParaPPP`: Assemble 9mm Luger +P+ high pressure round - 1980s.
- [x] `Tooltip_Recipe_Produce9x19ParaPPP`: Assemble 9mm Luger +P+ rounds with reloading press.
- [x] `Tooltip_Recipe_Make45ACPHP`: Assemble .45 ACP HP hollow point round - 1970s.
- [x] `Tooltip_Recipe_Produce45ACPHP`: Assemble .45 ACP HP rounds with reloading press.
- [x] `Tooltip_Recipe_Make45ACPP`: Assemble .45 ACP +P high pressure round - 1980s.
- [x] `Tooltip_Recipe_Produce45ACPP`: Assemble .45 ACP +P rounds with reloading press.
- [x] `Tooltip_Recipe_Make3006SpringSP`: Assemble .30-06 Springfield SP soft point round - 1910s.
- [x] `Tooltip_Recipe_Produce3006SpringSP`: Assemble .30-06 Springfield SP rounds with reloading press.
- [x] `Tooltip_Recipe_Make308WinSP`: Assemble .308 Winchester SP soft point round - 1952.
- [x] `Tooltip_Recipe_Produce308WinSP`: Assemble .308 Winchester SP rounds with reloading press.
- [x] `Tooltip_Recipe_Make12Bird`: Assemble 12 bore birdshot (aka. 12-gauge) - 18.5mm - 1860.
- [x] `Tooltip_Recipe_Produce12Bird`: Assemble 12 bore birdshot rounds with reloading press.
- [x] `Tooltip_Recipe_GunsOfTien_MakeSoftPointBullet`: File the jacket off the nose of a standard rifle bullet so the lead shows.
- [x] `Tooltip_Recipe_GunsOfTien_MakeBirdshot`: Pour molten iron from small iron items through a strainer into water.
- [x] `Tooltip_Recipe_GunsOfTien_ProduceBirdshot`: Pour molten iron from a crucible through a strainer into water.
- [x] `Tooltip_Item_GunsOfTien_BulletRifleSSP`: Small size soft point rifle bullet. Craftable from standard bullets with a file.
- [x] `Tooltip_Item_GunsOfTien_BulletRifleMSP`: Medium size soft point rifle bullet. Craftable from standard bullets with a file.
- [x] `Tooltip_Item_GunsOfTien_Birdshot`: Birdshot pellets for shotgun shells. Poured through a strainer into water at any furnace.
- [x] `Tooltip_Item_GunsOfTien_BoxBulletsRifleSSP`: Box of 25 Bullets Rifle S SP
- [x] `Tooltip_Item_GunsOfTien_BoxBulletsRifleMSP`: Box of 25 Bullets Rifle M SP
- [x] `Tooltip_Item_GunsOfTien_BoxBirdshot`: Box of 25 Birdshot Pellets
- [x] `Tooltip_weapon_LaserRifle`: Laser
- [x] `Tooltip_weapon_LightRifle`: Weapon Light
- [x] `Tooltip_weapon_BayonetIntegrated`: Bayonet (Integrated)
- [x] `Tooltip_weapon_BayonetKnife`: Bayonet
- [x] `Tooltip_weapon_BoosterScope`: Magnifier
- [x] `Tooltip_weapon_Shellholder`: Shell Holder
- [x] `Tooltip_weapon_UnderbarrelChamber`: Underbarrel Chamber
- [x] `Tooltip_weapon_Animated1`: Belt Round 1
- [x] `Tooltip_weapon_Animated2`: Belt Round 2
- [x] `Tooltip_weapon_Animated3`: Belt Round 3
- [x] `Tooltip_weapon_Animated4`: Belt Round 4
- [x] `Tooltip_weapon_Animated5`: Belt Round 5
- [x] `Tooltip_weapon_Animated6`: Belt Round 6
- [x] `Tooltip_weapon_Animated7`: Belt Round 7
- [x] `Tooltip_weapon_Animated8`: Belt Round 8
- [x] `Tooltip_weapon_Animated9`: Belt Round 9
- [x] `Tooltip_DOUBLEBARREL_Barrel_Close`: Full-length barrels for the double-barrel shotgun.
- [x] `Tooltip_DOUBLEBARREL_Barrel_Open`: Full-length barrels for the double-barrel shotgun.
- [x] `Tooltip_DOUBLEBARREL_Barrel_Sawnoff_Close`: Sawn-off barrels for the double-barrel shotgun.
- [x] `Tooltip_DOUBLEBARREL_Barrel_Sawnoff_Open`: Sawn-off barrels for the double-barrel shotgun.
- [x] `Tooltip_DOUBLE_DEUCE_Barrel_Close`: Full-length barrels for the Double Deuce.
- [x] `Tooltip_DOUBLE_DEUCE_Barrel_Open`: Full-length barrels for the Double Deuce.
- [x] `Tooltip_STEVENS_555_Barrel_Close`: Full-length barrels for the Stevens 555.
- [x] `Tooltip_STEVENS_555_Barrel_Open`: Full-length barrels for the Stevens 555.
- [x] `Tooltip_STEVENS_555_Barrel_Sawnoff_Close`: Sawn-off barrels for the Stevens 555.
- [x] `Tooltip_TOZ34_Barrel_Close`: Full-length barrels for the TOZ-34.
- [x] `Tooltip_TOZ34_Barrel_Open`: Full-length barrels for the TOZ-34.
- [x] `Tooltip_TOZ34_Barrel_Sawnoff_Close`: Sawn-off barrels for the TOZ-34.
- [x] `Tooltip_Rail`: Underbarrel 12 gauge shotgun for the M16A2, 5 buckshot shells. Switch between rifle and shotgun from the firearm radial menu.
- [x] `Tooltip_weapon_LaserBeam`: Laser Beam
- [x] `Tooltip_Recipe_GunsOfTien_SawOffShotgunStock`: Saws the stock off behind the grip.
- [x] `Tooltip_GunsOfTien_StockOffcut`: As good as scrap wood.
- [x] `Tooltip_GunsOfTien_BarrelOffcuts`: As good as a steel bar.

### Post-93 Tooltip.json

- [x] `Tooltip_Recipe_Make46x30SS`: Assemble 4.6x30mm SS sub sonic round - 2001.
- [x] `Tooltip_Recipe_Produce46x30SS`: Assemble 4.6x30mm SS rounds with reloading press.
- [x] `Tooltip_Recipe_Make57x28SS`: Assemble 5.7x28mm SB193 sub sonic round - 1990s.
- [x] `Tooltip_Recipe_Produce57x28SS`: Assemble 5.7x28mm SB193 rounds with reloading press.
- [x] `Tooltip_Recipe_Make57x28SR`: Assemble 5.7x28mm SS197SR polymer tip round - 2000s.
- [x] `Tooltip_Recipe_Produce57x28SR`: Assemble 5.7x28mm SS197SR rounds with reloading press.
- [x] `Tooltip_weapon_ForegripIntegrated`: Foregrip (Integrated)

### Menu and option texts (main mod IG_UI.json)

- [x] `IGUI_GunsOfTien_LaserOn`: Turn Laser On
- [x] `IGUI_GunsOfTien_LaserOff`: Turn Laser Off
- [x] `IGUI_GunsOfTien_LaserOnDesc`: Switch the laser on. Aiming bonuses apply.
- [x] `IGUI_GunsOfTien_LaserOffDesc`: Switch the laser off. No aiming bonus while off.
- [x] `IGUI_GunsOfTien_LaserEmpty`: The laser's battery is empty. Take the laser off the gun and insert a new battery.
- [x] `IGUI_ItemCat_Casings`: Casings
- [x] `IGUI_ClickToRemove`: Click to remove
- [x] `IGUI_SelectAmmunition`: Select Ammunition

### Post-93 IG_UI.json

- [x] `IGUI_GunsOfTienPost93_FoldForegrip`: Fold Foregrip
- [x] `IGUI_GunsOfTienPost93_UnfoldForegrip`: Unfold Foregrip
- [x] `IGUI_GunsOfTienPost93_FoldForegripDesc`: Fold the front grip up under the receiver.
- [x] `IGUI_GunsOfTienPost93_UnfoldForegripDesc`: Swing the front grip down for a steadier hold.

### Sandbox options (main mod Sandbox.json)

- [x] `Sandbox_GunsOfTien`: Guns of Tien
- [x] `Sandbox_GunsOfTien_RealisticPiercing`: Adjusted Piercing
- [x] `Sandbox_GunsOfTien_RealisticPiercing_tooltip`: Plain (full metal jacket) .30-06, 7.62x51mm and .308 rounds can pass through a zombie and hit the one behind it in every gun that fires them, as they would in reality. Guns of Marz lets only some of those guns pierce. Soft points never pierce but hit harder, so choosing between them is always a trade-off. Plain .30-30 rounds are flat-nosed soft points in reality (pointed bullets are unsafe in a tube magazine), so they no longer pierce. Off = Guns of Marz's own piercing.
- [x] `Sandbox_GunsOfTien_SubsonicRackRule`: 7.62x39mm US Subsonic Cycling
- [x] `Sandbox_GunsOfTien_SubsonicRackRule_tooltip`: The Soviet US subsonic round burns too little powder to work an AK's gas system, so the gun has to be racked by hand after every shot. A PBS-1 suppressor traps gas and raises the pressure in the barrel, which pushes enough gas into the gas port to cycle the gun. The round and the suppressor were made as a pair.
- [x] `Sandbox_GunsOfTien_SubsonicRackRule_option1`: Always rack after every shot
- [x] `Sandbox_GunsOfTien_SubsonicRackRule_option2`: Rack unless a PBS-1 is fitted
- [x] `Sandbox_GunsOfTien_SubsonicRackRule_option3`: Never rack

## Post-93 sub-mod `GoMExtensionGunsOfTienPost93` — in progress

Done (Lua syntax-checked): `registries.lua` (5 ammo types), ammo items / models / recipes / Ammo Maker placeholders +
names (`scripts/post93/gen_post93_ammo.py`), ammo art (`scripts/post93/make_ammo_art.py`, sheet
`docs/post93_ammo_art_sheet.png`), `Ammunition.lua` (families 4.6x30mm / 5.7x28mm, profiles), `AmmoMaker.lua`,
`Guns.lua` (magazine profiles, RPM 950 / 900, animated bolt, reload anims MP7 = "MP7A1" / P90 = "P90TR", magazine shown leaving the gun with the hand, MP7 folding
stock, suppressor stats, integrated rails as parents of GoM optics / lights / lasers, permanent parts, spawn parts,
MountOn appends), `HotBrass.lua`, `Loot.lua` (GoM Anachronistic + Police SMG spawners, rare boxes), `Tooltips.lua`,
reload AnimSet XMLs (`AnimSets/player(-vehicle)/actions/*P90TR_GoT.xml`, clips `Bob_GunsOfTien_P90_Load / Unload
/ Rack / AimRack`; `*MP7A1_GoT.xml`, vanilla's pistol clips + `Bob_GunsOfTien_MP7_Unload`), gun generator `scripts/post93/gen_post93_guns.py` (items, models, parts, fixing, names; reads
`mp7_points.json` / `p90_points.json`).

- [x] MP7A1 rebuilt from the user's photos 2026-10-14 (the first, dimensions-only model had a raked block grip, a
      deep trigger guard and straight magazines; 73% silhouette overlap, now 96.1%): FBX, textures, icons,
      `mp7_points.json`, `docs/post93_mp7_preview.png`; rebuild: `build_mp7.py` (~1 min) → `render_mp7.py` →
      `make_mp7_art.py`. To check in game: the hand on the upright grip, magazines (no attachment rotation now, the
      30 / 40 curve forward by themselves), the `world` floor pose (GoM default kept). Not yet shown to the user.
- [x] P90 TR assets rebuilt from the user's photos and approved 2026-10-14 (FBX, textures, icons, `p90_points.json`,
      `docs/post93_p90_preview.png` with the photo outline overlay, 98.7% overlap; rebuild: `build_p90.py` (~1 min) →
      `render_p90.py` → `make_p90_art.py`). To check in game: the grip in the hand (origin = rear-top of the grip
      column), the `world` floor pose (GoM default kept), optic height on the top rail.
- [x] P90 held like a pistol (user, 2026-10-14): item as GoM's MP5K (Handgun, handgun reload, one hand) but never in a
      holster (Rifle: back slot, turned upright there by its rifle_back attachments), model exported upside down like
      GoM's handgun-held guns. `gen_post93_guns.py` run (items_guns / models_guns / fixing_guns,
      names). To check in game: the hold, the gun upright on the back (with and without a bag), the `world` floor pose.
- [x] Every name in both mods' scripts resolves (`python3 scripts/check_refs.py`, 642 references, 2026-10-15); the
      only misses are the four P90 reload clips below. Re-run it after any generator.
- [x] P90 reload clips (pistol stance, top magazine) built and approved 2026-10-15:
      `anims_X/Bob/Bob_GunsOfTien_P90_{Unload,Load,Rack,AimRack}.x` from `scripts/post93/anim/p90_reload.py`
      (TienInspectWeapon's pipeline). Without them the magazine insert hung (a reload ends on its clip's events). To
      check in game: the whole reload, the load click on the press, the rack's events, aiming racks.
- [x] MP7A1 held like a pistol (user, 2026-10-15), exactly as the P90: Handgun item block, back slot (never a
      holster), model exported upside down (`handgun_points()` in build_mp7.py, shared with build_p90.py, whose files
      came out byte-identical). Reload = vanilla's pistol clips with its own AnimSets and the P90's magazine
      behaviour, the right magazine of the three swapped (CLAUDE.md "MP7A1 reload"). To check in game: the hold, the
      gun upright on the back, the `world` floor pose, the reload with each magazine size (the right one leaves and
      comes back), the rack's casing.
- [x] MP7 60-round drum (user, 2026-10-15): model, texture, icon, item, name, tooltip, profile, 2% spawn on found
      MP7s. To check in game: the drum under the grip, the reload with it (the drum leaves and comes back).
- [x] FN Five-seveN (user, 2026-10-16) as `MarzGuns.FIVESEVEN`, GoM's own unused name: model from an ATF side photo
      (96.0% silhouette overlap), slide, 20 / 30-round magazines, textures, icons (cameras fitted on GoM's Glock 17
      icons), item / model / repair scripts, magazine profile, animated slide, ammo family, GoM pistol parts, its own
      SFN-57 suppressor on the 5.7x28mm mount device it shares with the P90, spawn parts, loot, Hot Brass, tooltips; sheet
      `docs/post93_fiveseven_preview.png`. Rebuild: `build_fiveseven.py` → `render_fiveseven.py` →
      `make_fiveseven_art.py --renders DIR` → `gen_post93_guns.py`. To check in game: the hold in the hand (origin
      placed like the Glock's), the slide moving back on each shot, the default pistol reload with each magazine,
      the 30-round magazine under the grip, the Beretta mount with a sight, the LP and TL lights under the rail (lasers must
      not fit), the
      mount device on the Five-seveN (shown as a threaded-barrel adapter) and the SFN-57 over it (and that the SP90
      no longer fits it), in the holster and on the floor (GoM's pistol `world` pose), the casing
      thrown right, the name shown is GoM's "5.7x28mm Five-SeveN".
- [x] H&K UCP Prototype (user, 2026-10-17): `GunsOfTienPost93.UCP`, built and registered like the Five-seveN from a
      photo of the about-2004 prototype (97.3% silhouette overlap), a 20-round magazine and a small 40-round drum, the MP7's mount device (drawn
      as a threaded-barrel adapter) and Rotex-II, GoM's Beretta mount + pistol sights and pistol lights, Anachronistic
      spawner only; sheet `docs/post93_ucp_preview.png`. To check in game: the hold, the slide, the default pistol
      reload with both magazines (the drum under the grip leaves and comes back), holster and floor pose, the Beretta mount with a sight, both lights, the mount device and Rotex-II at the
      muzzle (and that the MP7 still takes them), the name "UCP Prototype", casings thrown right.
- [x] MP7 30 / 40-round magazines matched to the user's photos of H&K's (2026-10-17): every box magazine (20, 30, 40)
      curves from its feed lips down on one radius and is tilted back so its part inside the grip stays centred; the
      30 and 40 carry their lower part in a wider polymer sleeve. To check in game: the magazines in the grip (nothing
      showing through), the reload with each.
- [x] 2026-10-17: MP7 / P90 markings read the right way in game (they were mirrored); our weights set to GoM's
      standard (suppressors, mount devices, magazines, guns); GoM's Glock 17 added to the main mod's sound table. To
      check in game: the markings read correctly (and which side the P90's FN panel is on, against a photo).
- [x] 2026-10-17: the Five-seveN and UCP never spawn in civilian homes (out of GoM's Anachronistic spawner, which sits
      in vanilla's late survivor safehouses): both in GoM's police / SWAT handgun spawners (the UCP like any other
      gun, not rare, user 2026-10-17) and (with a magazine and a box) in survivor and bandit zombies' late bags. To
      check in game: none in houses, both on police zombies and in police cars as often as the Glock / M92FS.
- [x] 2026-10-17: loot matched to GoM: special loads never spawn (the main mod's loot removed; Post-93 keeps only
      DM11 / SS190 boxes and cartons, now also cartons beside vanilla 9mm cartons in police / SWAT / gun stores), the
      high-capacity magazines in GoM's tactical high-cap spawner. To check in game: no special loads in loot, DM11 /
      SS190 cartons and loose drums turn up; nothing of the Five-seveN / UCP in houses.
- [x] Lasers (2026-10-18): Turn Laser On / Off from the gun's menu and the radial (its own icons); the short beam part on the laser's lens (GoM rifles,
      pistols, MP7 / P90; solid red narrowing to a point, the same length on a lit floor and in the dark; does the unlit shader
      gunsoftien_laser load from the mod's media/shaders, so it stays bright at night), on a slung gun, for another player in MP; the bonus only while on (gun tooltip stats); drain and the
      empty switch-off; a picked-up laser shows a full Remaining bar within a game minute; Remove Battery then Insert
      Battery on a detached laser (its right-click menu offers only what can be done now: Remove while charged, Insert
      while empty with a charged battery carried; the laser stays empty after Remove; in MP too, seen only in SP so far); Dismantle Simple Electronic Item on a laser
      (a screwdriver, gives Electronics Scrap); the new tooltip lines and part-row names.
- [x] Test in game (as above, plus folding stock, the MP7A1's front grip (fold / unfold from the context and radial menus, stats), the MP7A2 (spawns half of found MP7s, GoM's foregrips on its bottom rail: fit, look, stats), rails, suppressors, spawns, Hot Brass downward ejection).

- [x] FN SCAR-L (Mk 16 STD) and SCAR-H (Mk 17 LB) built 2026-10-20 from the user's photos (silhouette IoU 94.1 /
      95.2 %; sheet `docs/post93_scar_preview.png`): models, textures, icons, item / model / repair scripts, names,
      magazine profiles (GoM's STANAG for the L), 625 / 600 rpm, animated charging handle, reload (L default, H GoM's FAL
      clips), shared folding stock, four integral rails, GoM's optics / foregrips / bipods / lights / lasers, the L's GoM
      AR muzzle parts, the H's own mount device and SOCOM762-RC suppressor, spawn parts, loot (military since
      2026-10-20: GoM's world and zombie army rifle spawners), Hot Brass, tooltips. Suppressor: SureFire's SOCOM762-RC (user, 2026-10-20; FN made none for the SCAR-H). To check in game:
      the hold (grip in the hand, both guns), the stock folding to the right and back (context / radial), the charging
      handle moving back on each shot, GoM's STANAG magazines seated in the SCAR-L (all eight, the 60 / 100 / 150
      drums under it), the SCAR-H's 20 and 10, the reloads (L default rifle, H FAL clips), optics on the top rail over
      the folded rear sight, foregrip and bipod on the bottom rail, light left / laser right, GoM's AR mount + MKI /
      NDR / compensator / flash hider / brake on the SCAR-L, the SCAR-H's mount device + suppressor, on the back and on
      the floor (GoM's rifle `world` pose), casings to the right, SCAR kits from GoM's army rifle
      spawners (debug: spawn `MarzGuns.World_Army_Rifle_Spawner` into a container a few times) and on army zombies' backs.
- [x] SCAR-H 50-round drum (ProMag DRM-A41, user 2026-10-20): model, texture, icon, item, name, tooltip, profile, 2 %
      on found SCAR-Hs, GoM's high-capacity tactical magazine spawner. To check in game: the drum under the magazine
      well (clear of the trigger guard and the hand), the reload with it, the "50" reading the right way on both faces.
- [ ] H&K UMP45 and UMP9 built 2026-10-22 from the user's photo (silhouette IoU 86.9 %; sheet
      `docs/post93_ump_preview.png`): one model and stock for both guns, each with its own texture (markings), magazines
      (UMP45 25 / 20 / 10 smoked translucent, UMP9 30 curved), item / model / repair scripts, names, magazine profiles,
      600 / 700 rpm with a two-round burst, GoM's MP5 reload clips, the folding stock (GoM's G36C stats and spread),
      four integral rails with GoM's MP5 accessories, spawn parts (magazines by GoM's MP5 rule), loot (Anachronistic and
      police SMG spawners, as the MP7 / P90), Hot Brass (the MP5's), tooltips, realistic sound (96 / 28, 70 / 20). To
      check in game: the hold (grip in the hand), the stock folding to the right and back (context / radial) and its
      stats, Auto / Burst / Single on the selector and the burst firing two, the magazines seated in the magazine well
      (the curved 30, the 25 / 20 / 10), the MP5 reload clips lining up with the magazine, optics on the top rail, foregrip
      on the bottom rail, light left / laser right, on the back and on the floor (GoM's rifle `world` pose), casings to
      the right, the markings reading the right way ("HK UMP" and the calibre on the left, "UMP45" / "UMP9" on the
      right), the .45 magazines' translucent look, UMP kits from the Anachronistic spawner (debug: spawn
      `MarzGuns.World_Anachronistic_Spawner` into a container a few times) and on SWAT zombies. UMP45 + GoM's .45
      mount device and P45 suppressor (added 2026-10-22): the mount fits only with the wrench, the suppressor only
      over the mount, both drawn on the barrel (mount on the collar in front of the nose, can on the bore axis), quieter
      shots (×0.3) and no muzzle flash, the tooltip's "Compatible Muzzle Device: .45 Muzzle Mount" line; the UMP9
      refuses both and takes the main mod's Mk9 and its mount instead (same canon point).
- [ ] M249 Light Machine Gun (PIP), main mod, building since 2026-10-22 (design: docs/design.md 4d): model, textures,
      icons, sheet `docs/m249_preview.png` (traced from the public-domain USAF photo docs/m249_usaf.jpg), item / model /
      repair scripts and names (gen_scripts.py `m249()`), shared/GunsOfTien/M249.lua (its own magazine profile: the
      200-round box + GoM's STANAGs, the box in GoM's 5.56 family, 750 / 1000 rpm, the nine belt rounds hidden with a
      STANAG, the M60's bipod stats, STANAG jam x2, reload handler, spawn parts, STANAG MountOn), loot (GoM's M60
      spawners, loose boxes in army ammunition storage), Hot Brass, tooltips. Custom belt reload clips (user liked the draft,
      2026-10-22) shipped as anims_X/Bob/Bob_GunsOfTien_M249_{Unload,Load,Rack,AimRack}.x from
      scripts/anim/m249_reload.py; still to polish: the stock passing into the chest while the hand works, the left
      hand 1-3 cm short on the open cover and the right-side handle, left elbow flips (AimRack worst). Then docs
      (README, workshop.txt, mod.info, forum). To check in game: everything above,
      the two Auto entries in the fire mode menu, the feed cover opening and closing during a reload (gwSetPart through
      the attachments style), the box drawn on the gun and lying on its side on the floor, STANAGs slanting down to the
      left, belt rounds vanishing from nine down and gone with a STANAG.
- [ ] Uzi, Mini Uzi, Micro Uzi built 2026-10-23 (docs/design.md 4f, CLAUDE.md "Uzi family"): models, textures, icons,
      sheet `docs/uzi_preview.png`, scripts (gen_scripts.py `uzi()`), Uzi.lua, AnimSets + unload clip, loot, Hot Brass,
      tooltips, README / workshop.txt / mod.info. Not loaded in game yet. To check: all three spawn from the debug item
      list with the stock folded and a magazine; the Uzi held two-handed and on the back, the Mini / Micro one-handed,
      upright in the hand and in a belt / shoulder holster, the Micro in an ankle holster too (HolsterSmall; no holster
      points of their own, as GoM's MP5K / Detective .38; the Micro is 257 mm with its stock, so check it clears the
      leg and the floor; if one hangs wrong, add points like the sawn-off stocks'); Fold / Unfold Stock (the Mini's and Micro's swing forward along the
      right side, the butt hanging under the barrel; the Uzi's two nodes swap), the stock lines in the tooltip; every
      magazine fits every gun, sits flush at the grip's bottom (20) and hangs straight; Auto at 600 / 950 / 1200 and
      Single; the Mini / Micro reload with vanilla's pistol clips and no magazine in the left hand, the magazine
      leaving and returning at the clip's events; the Uzi's reload on GoM's MP5 clips (the hand goes ahead of the
      grip: custom clips if the user wants); the mount device and Mk9 on all three (wrench, can on the bore axis
      against the nut); casings out to the right (Hot Brass); kits from `MarzGuns.World_Short_SMG_Spawner`,
      `Zombie_Police_SMG_Spawner` and `Zombie_Crime_Rifle_Spawner` (debug: spawn them into a container), the 40 / 50 from the high-cap spawner; the
      muzzle flash at the barrel's end; the floor pose of guns and magazines.
- [ ] Own reload clips for the full-size Uzi and GoM's MP5K (user, 2026-10-23: GoM's MP5 clips put the Uzi's left
      hand ~10 cm ahead of its grip magazine, GoM's handgun2 clips miss the MP5K's magazine too). Drafts only, not
      wired into the game. Third round (2026-10-23) waits for the user's look at the GIFs.
      Builder `scripts/anim/smg_reload.py` (Blender, ~15 s a gun; TienInspectWeapon's rig, as m249_reload.py):
      `blender -b --factory-startup -P scripts/anim/smg_reload.py -- "<vanilla media/anims_X/Bob>" "<ABSOLUTE
      repo>/tmp/anim/smg" uzi|mp5k [Unload Load Rack AimRack] --preview` writes `Bob_GunsOfTien_<Uzi|MP5K>_<clip>.x`
      + previews; GIFs: `py ../TienInspectWeapon/scripts/anim/gif.py tmp/anim/smg/prev_<gun>_<clip> out.gif 3 0.7`,
      key frames: `sheet.py <dir> out.png 6,12,...`. (tmp/ is gitignored: regenerate the previews on the other
      computer.) Clips 36 / 45 / 36 / 36 frames = GoM's magazine durations 1.2 / 1.5 / 1.2 s; SWAP Unload 10, Load 30.
      Every build prints body clearance per clip (`... into the body by D (frame f)`; ~0.02 = an arm resting on the
      side, as vanilla's idle) and, with `SMG_CLEAR=1`, per-frame depths and reach shortfalls. The magazine in the
      hand renders orange.
      Done so far, from the user's notes on the first two rounds:
      - the left hand takes the magazine by its body just under the well (works for every magazine length, 20-50 and
        GoM's MP5 drums), vanilla's rifle-load grip (frame 30) moved by `hold_fix`, measured with `SMG_CAL=raw` (the
        centre of Bob's left hand / finger vertices against the magazine axis: Uzi 0.0023 0.0427 0.0233, MP5K 0.0044
        0.0524 -0.0181; `SMG_CAL=1` checks it lands at 0); before that the hand floated ~5 cm under the magazine
        ("weird animation when taking off the mag")
      - no stall: the unload reaches the hip on its last frame (it used to hold 9 frames)
      - Uzi work place found by grid search (`SMG_WORK="right,up,forward"`, also `SMG_RACK`, `SMG_RACK_ALONG`,
        `SMG_RACK_TOP` env overrides for tuning; count "frames out of reach" / elbow steps in the output): pos
        -0.02 0.68 0.10 (3 frames short, the blend-in)
      - Uzi AimRack stays in the aim (no reach warnings, smooth elbow); Uzi Rack over the top (L elbow swings 88
        degrees once)
      - MP5K Rack: first version (across the belly, muzzle left) "outright unacceptable"; up in front of the face
        rejected by me; now the AimRack's place (drawn in at the chest, turned a little left, still pointing forward):
        15 frames short by up to 13 cm. GoM's MP5K origin is at its rear end, the well 0.12 and the lever 0.20 ahead,
        and GoM draws guns large next to Bob (arm reach 0.274 from the shoulder), so a forward-pointing gun puts the
        lever out of reach.
      - MP5K AimRack added (user: "I don't see an MP5K aiming"; GoM's handgun2 has none)
      - third round, from the user's notes: "the racking of MP5K makes their racking arm go in their body... just
        no" and "why is the uzi unload magazine model just rotates? It doesn't go with the hand". Unload swap moved
        16 -> 10 (the hand closes on the magazine; at 16 the seated magazine stayed while the hand slid 8.5 cm down
        it, then hung from the hand like a lever) and the hand keeps its turn on the way to the hip (no "belt" grip),
        the hip target worked out from where the gun really lands (it was 8 cm short). MP5K: the left hand joins the
        gun only once it is up and lets go before it goes down (the pistol idle's gun hangs at the right thigh: the
        left arm went through the belly to reach it, also in the Load's end); rack place scanned (reach, clearance,
        wrist, straight arms) with the rig's new torso twist: close in front of the right shoulder, muzzle forward
        and a little left, chest turned 15 degrees; work place ch(0.04, 0.68, 0.10). Uzi Rack had the same fault
        (left upper arm 7 cm into the chest, an 88-degree elbow flip): now low in front of the belly, canted left,
        twist 15, hand and gun back together after the let-go. The return-to-idle key turned the gun across the
        thigh (it carried the rack's `top`): fixed. All clips now at contact level or clear.
      - fourth round: user liked the MP5K AimRack; "mp5k rack ... after racking the gun the racking arm is not
        smooth and looks like a fast snap", "the uzi unload looks like the wrist is broken". The MP5K's free left
        hand stays on IK and is steered to / from exactly the idle's hanging hand (`free` = the rig's support_base)
        instead of fading support over 5 frames (rack, unload start, load end). Uzi: the work place settles the gun
        to a right wrist of -30/-20 (`wrist`, was -52/-49), the hip hand settles to a natural wrist (was bent 55),
        the unload's elbows leave the idle's by frame 8 (rig `ramp`; held near it the left forearm twisted -98),
        the load's hand goes back to its grip with the gun, the rack's hand turns (-60, 30, 0) on the knob (twist
        -100 -> -62). `SMG_CLEAR=1` also prints both wrists every 2nd frame. Left: Uzi AimRack's right wrist is
        vanilla's rifle aim (kept on purpose); a few frames as the hands first reach the gun.
      Still to do once approved: AnimSets player + player-vehicle (`*UziRifle_GoT.xml`, `*MP5K_GoT.xml`; Load: Start
      insertAmmoStart, load sound + changeWeaponPart "mag" at 30/45, loadFinished End; Unload: ejectAmmoStart,
      unload sound + changeWeaponPart at 10/36, unloadFinished; Rack / RackAim (RackAiming condition, as GoM's
      RackMP5Aim): rack sound, rackStart ~12/36, **rackBullet before ejectCasing** (~0.55 / 0.56: Hot Brass; GoM's own
      MP5 rack has them the other way), rackEnd, rackingFinished); ship the .x files to anims_X/Bob; Uzi.lua: the UZI
      handler animId "UziRifle", style "attachments" with the magazine shown in the hand (Gunworks shows the real
      magazine, resolveReloadMagItem) and the pointMagPart wrapper extended to it; a new shared file registering
      MarzGuns.MP5K the same way (animId "MP5K_GoT", after GoM's ReloadAnims, a GoM fix: say so in README /
      workshop.txt / mod.info's fix list); CLAUDE.md notes.
- [ ] Compact SMG stance (user, 2026-10-23, Option B; CLAUDE.md "Compact SMG stance"): Uzi, Mini Uzi, MP5K, MP7A1 /
      A2. Idle and aim approved; full coverage built and shipped (3 sets x 240 clips + 4 reloads, packed 7 files a
      set, 4 sets (Uzi, UziT, MP5K, MP7), 1016 stance nodes (with Gunworks' RealSingle / Auto / Burst shooting and
      dry-fire nodes), 32 reload nodes;
      idle hold moved 4 cm in after the first test; CompactStance.lua x2, Uzi.lua and Post-93 Guns.lua reloads; README /
      workshop / mod.info, beta). Reload clips not yet reviewed by the user. To check in game: the packed clips load
      (no "animation not found" in the log), the stance on all five guns (MP too: GunworksGripAnim on remote
      players), the MP7A1 switching sets as its foregrip folds, idle / aim / every pitch / walking aimed / shooting
      Auto / Single / empty (the left hand staying on the gun) / shove, crouching in the open and by a wall (idle,
      walk, run, stopping: wrists natural, the gun low and forward), standing to walking and aimed walk to walk, tracers and muzzle flash leaving the drawn
      muzzle on every gun (the turned ones: Mini Uzi, MP5K, MP7s, on the UziT / MP5K / MP7 clips), sneaking, walking, running, sprinting, vaults, falls, get-ups, sitting, fidgets,
      emotes, vehicle aiming, the reloads (magazine leaving with the hand, racks, Hot Brass casing at the rack), the
      guns upright in hand and unchanged in holsters / on the back / on the floor, the Micro Uzi still one-handed.
      Gunworks' grip cache (CLAUDE.md "Compact SMG stance"): fixed in ZomboidFixesB42 (GunworksGripSync), tested there.
- [ ] Belt links built 2026-10-22 (docs/design.md 4e): M27 / M13 links and their boxes (models, icons, open / pack /
      make recipes), filling and unloading belt boxes takes / gives links, every shot from a belt box throws its link
      out (Hot Brass physics and our landing sounds, at the feet without Hot Brass, into Ammo Maker's brass catcher;
      SP direct, MP batched to the server and thrown two a tick), loot (army ammunition storage, M249 and GoM's M60 kits), tooltip lines. To
      check in game: Load Rounds into an empty M249 box with and without links (halo, stops when links run out), the
      links count going down one a round, links flying out the right side when firing and landing as items with
      their clink (SP and MP, misses too), the landing sounds per surface, brass catchers, unloading rounds gives
      links, STANAG fire gives none, GoM's M60 box the same with M13 links, Open / Pack / Make recipes, the icons and
      floor models, link boxes in army storage and in M60 / M249 kits.

## Gun scale audit (2026-10-25)

User: "the MP5A1 and MP5A2 seem a little bit big ... compared to human size ... does it follow the size proportion
from M16?", then "audit all of the guns from GoM and GoT and list them in TODO. we will try to fix them... but that
also means we need to fix the stances", then "edit each gun so that they have their own scales rather than apply a
global scale". So: **every gun gets its own `scale`**, worked out for that gun from its own real size, so that it
stands in the M16A2's proportion (the M16A2 = 1.00; scale = M16A2's ratio 0.603 / the gun's ratio). Measured, not
applied yet. Tools: `blender -b --factory-startup -P scripts/scale_audit.py -- <out.json>` (every gun as drawn: body +
deployed integrated stock / full barrels, plus every part model), then `python3 scripts/scale_audit_report.py
<out.json>` (each gun's ratio, its own scale, the left palm on it before / after). "Ratio" = drawn length / real
overall length (stock extended). Reference sizes and the engine trace: CLAUDE.md "Gun scale".

- Vanilla draws people at ~0.55 (body 0.98 units for a ~1.78 m man), its M16 at 0.54, its M9 at 0.70. GoM's
  rifle-stance guns run 0.53..0.73 (median 0.63), its pistols and SMGs ~0.70-0.73; ours were built at 0.65 (rifles)
  and 0.72 (SMGs, pistols). The M16A2 is 0.60, the MP5A2 0.73: **the MP5A2 is ~20% too big next to the M16**.
- [ ] Variants guessed from the models (`?` below and in the report): check each with a render against a photo before
      fixing its scale: CAR-15 (14.5" assumed, same length as GoM's M4A1), XM177 (E2), Thompson (M1A1 813 mm vs
      1928A1 852), Remington 870 (28" field assumed: 1.10; a 20" would be 0.91), W1887 (30" original assumed: 1.14;
      a 22" reproduction 0.93), W1894 (20" carbine), W1873 (24" rifle), W1873 Short Carbine (cut stock, 620 mm
      assumed), M1895, Model 70, Remington 700, Stevens 555, Double Barrel, S&W 629 (8-3/8"), Rhino (6"), MP-412
      (5"), Colt SAA (7.5"). GoM's Stolzer & Son 2-bore has no real size: give it a scale by eye.
- [ ] Pistols: their scales below put them in the M16's proportion too, smaller than vanilla's own pistols (0.70);
      say per pistol if one should stay larger.

### How a fix works (traced in the 42.21 jar, CLAUDE.md "Gun scale")

- [ ] **Built, not yet seen in game (2026-10-26)**: `lua/shared/GunsOfTien/GunScale.lua` (+ Post-93's
      `GunScale.lua` for its guns) sets each model's `scale` with `ModelScript:Load` at OnInitGlobalModData,
      behind sandbox "[Beta] Rescale guns (Requires Restart)" (`RescaleGuns`, default on), and scales the gun's
      own placing points (`world`, and every point named after a FemaleBody / MaleBody point: holsters, back,
      Bip01_Prop1), which the engine applies before the model scale. Check in game, also with the option off (sizes
      as before) and switched between two loads; one gun of each kind: in hand idle / aimed / walking, a reload and a rack, on the back and in a holster, on the
      floor (not sunk or floating), parts (magazine, sight, suppressor, bayonet, the Mk9 on the MP5), the muzzle flash
      at the muzzle, a sawn-off break-action in its holster; after leaving to the menu and loading again; in MP, as
      seen by another player.
- [ ] Not scaled: the ballistic muzzle (bullet origin, tracer start; raw `muzzle` offset: starts (1 - s) x muzzle y
      ahead of the drawn muzzle, 3.9 cm on the MP5A2 at 0.87; pre-scaling the offset would sink the flash into the
      barrel instead); Hot Brass ejection offsets (relative to the player, so the casing leaves (1 - s) x the port's
      distance off the drawn port; GoM's `HotBrass/CustomParams.lua` and ours): look in game, then decide.
- [ ] Gunworks' reload magazine in the left hand (an attached item at `Bip01_Prop2`, drawn at the magazine's own
      size) shows only for handlers with a `magItem`: none of GoM's (its `magazineProfile` has none, style "none"),
      only our compact stance (MP5K, Uzi, Mini Uzi, MP7s; the P90's is suppressed). Those guns are left out until
      their clips are rebuilt; then the hand magazine needs a scaled model or reload point per magazine group.
- [ ] Left out, on our own clips solved for today's sizes: MP5K, Uzi, Mini Uzi, Micro Uzi, MP7A1 / A2, P90, M249;
      and GoM's Stolzer & Son 2-bore (no real size). Rebuild their clips from the scaled points, then add them
      (plan below).

### Rebuilding our clips at the new sizes (decided with the user, 2026-10-26; not started)

User: "let's do it. let's rebuild the animations in this branch." Choice taken: these seven guns **always** use the
new sizes, whatever "[Beta] Rescale guns" says (the stance and the reloads are ours, so their guns follow our sizes;
one clip set each, no second set kept for the old sizes, which would add ~85 MB to the main mod and ~31 MB to
Post-93). The option then covers only the guns on vanilla's and GoM's clips. Scales: MP5K **0.87** (the MP5 magazine
group), Uzi / Mini Uzi / Micro Uzi **0.84** (Uzi group), MP7A1 / A2 **0.84**, P90 **0.84**, M249 **0.94**.
Everything is generated, so the work is giving each generator a per-gun scale and running it again; the guns scale
about the grip origin (Bip01_Prop1), so every place in weapon space is x s:
- [ ] `scripts/anim/compact_build.py` `SETS[*].support` (left-hand place on the gun) and
      `scripts/anim/compact_stance.py` `GUNS[*].support`: x s. The hold itself (`HOLD`, character space) stays; the
      de-clip / clearance checks use the gun's meshes, so they must load them scaled.
- [ ] `scripts/anim/hold_preview.py` `GUNS[*].parts`: the meshes (preview, clearance) and each part's point x s
      (the point's offset only; the part mesh is scaled with the gun).
- [ ] Turned guns (MP5K, Mini Uzi, MP7s): `compact_animsets.TURNED_SETS` (set -> muzzle z, used by `compact_pack.py`
      to move the gun bone back, and by `compact_build.stance_clip` for shipped clips) x s, matching `GunScale.lua`,
      which scales the `Bip01_Prop1` turn point the same way (T(s o) R S = S T(o) R).
- [ ] Reloads: `scripts/anim/smg_reload.py` (`COMPACT_PLACES` work / rack places for Uzi, MP5K, MP7; the guns'
      points from `scripts/uzi_points.json`, `post93/mp7_points.json`, GoM's smgs.txt), `m249_reload.py`
      (`scripts/m249_points.json`), `post93/anim/p90_reload.py` (`post93/p90_points.json`), and the Micro Uzi's
      pistol-rack clips ("UziGrip", find their generator): places and points x s.
- [ ] Gunworks' reload magazine in the left hand (compact stance guns: MP5K, Uzis, MP7s): drawn at the magazine's own
      size while the one in the gun is scaled. Give it the gun's scale (a hand-only magazine model with `scale` = the
      group's, swapped in by `ReloadAnim.resolveReloadMagItem`, or a scaled copy of the `Bip01_Prop2` location's point).
- [ ] `GunScale.lua`: add these models (GoM's MP5K; our UZI, MINIUZI, MICROUZI, M249; Post-93's MP7A1, MP7A2, P90TR)
      in a second table applied whatever the option says.
- [ ] Run order per set: compact_build (all clips, ~1 min a set for 33 clips, much longer for the full 240-clip
      inventory) -> compact_pack -> compact_animsets (nodes unchanged unless names change) -> reloads; ship into
      anims_X/Bob, keep CRLF where the shipped files have it. Check the build's clearance report against the shipped
      one (arms at contact level, gun out of the body), then the user approves the stance again in game.
- [ ] Recheck what we fitted to today's sizes: Lasers.lua beams (a part: scaled with the gun, beam length too), the
      sawn-off holster points (scaled as holster points now).

### Guns sharing a magazine share one scale (user, 2026-10-26)

User: "when they share a mag like uzi, they [must] still [be] consistent ... while still basing on a basis". A
magazine is a weapon part, drawn at its gun's scale, so guns that mount the same magazine get **one scale per
group**, taken from a basis gun whose real size is sure (its own value in the list below). This overrides the
per-gun values in the list for every other member. It also makes the reload fix possible: one hand-only model per
magazine (or one scaled reload point) only fits if every gun using that magazine has the same scale.
Groups = merged `MountOn` lists of the `PartType = Clip` items (GoM + ours). GoM put the `magazine` point at the
same offset on every member of each family below (AR 0.1015 / 0.0144, MP5 0.1191, AK 0.1238, G36 0.1101), so their
receivers are built at one size and the spread in the list comes from barrels / stocks drawn long or short, or from
a guessed variant. Scaling each by its overall length would shrink or grow the receiver and the magazine with it.
- [ ] AR (STANAG): basis M16A2 **1.00** for M16A1 (0.99), M16A3, M16A2 M203, AR-15 (0.98), M4A1 (0.96), CAR-15
      (0.96?), XM177 (0.86?). The XM177 then draws 16% longer than a real XM177E2 (787 mm): its barrel / stock or the
      variant guess is off, look at a render.
- [ ] STANAG guns of other designs, own receivers: FNC (0.96), SCAR-L (0.93; its STANAG mounting is ours). Both
      take STANAG magazines for real. At 1.00 they draw 4 / 7% longer than real; at their own value the STANAG
      magazine is drawn that much smaller in them than in an M16. Decide.
- [ ] FAMAS (0.88): GoM's model is an **F1** (small trigger guard in front of the grip, not the G2's full-hand
      guard; side silhouette from `scale_audit.py`), and the F1 takes only its own 25-round magazines. STANAG
      magazines came with the G2 (1994, after our 1993). GoM mounts STANAG anyway (`Magazines.lua` "STANAG" profile,
      the magazines' `MountOn`), a gameplay choice. So no real magazine size ties it to the M16: own scale 0.88
      (the STANAG magazine drawn 12% smaller in it), unless it gets a 25-round F1 magazine of its own (decide).
- [ ] MP5: basis MP5 **0.87** (the MP5SD agrees) for MP5SD, MP5K (0.84), MP5A2 (0.83). The MP5A2 then draws ~5%
      long: its stock is the odd one (see its line below).
- [ ] AK-74 magazines: basis AK-74 **0.93** for the AKS-74U (0.89).
- [ ] G36: basis G36 **0.98** for the G36C (0.97).
- [ ] Uzi (ours): basis Uzi **0.84** for the Mini Uzi (0.84) and Micro Uzi (0.85).
- [ ] MP7: MP7A1 / MP7A2 **0.84** (already equal).
- [ ] .45 M1911 magazines: basis M1911 **0.86** for the Camp Carbine (0.85).
- Guns on one model share its scale anyway (Mossberg 590 / Masterkey, CAR-15 / its M203, UMP45 / UMP9). Sights,
  suppressors and bayonets are shared across families and stay at each gun's scale (GoM sized them loosely).

### Each gun's own scale (model script; ratio now -> scale)

Rifle stance (vanilla's rifle clips):
- [ ] MarzGuns.MP5A2: 0.73 -> **0.83** (GoM's MP5A2 is drawn longer than its MP5, 0.494 / 0.487, real 680 / 700 mm:
      one of the two stocks is off; check before both get their scale)
- [ ] GunsOfTienPost93.UMP45 / UMP9: 0.73 -> **0.83** (the idle palm then lands on a 0.9 cm thin part: check the hand)
- [ ] MarzGuns.CAMP_CARBINE: 0.71 -> **0.85**
- [ ] MarzGuns.XM177: 0.70 -> **0.86**?
- [ ] MarzGuns.MP5: 0.70 -> **0.87**
- [ ] MarzGuns.MP5SD: 0.69 -> **0.87**
- [ ] MarzGuns.FAMAS: 0.69 -> **0.88**
- [ ] MarzGuns.AKS74U: 0.68 -> **0.89**
- [ ] MarzGuns.W1894: 0.67 -> **0.90**?
- [ ] MarzGuns.FAL: 0.67 -> **0.91**
- [ ] MarzGuns.SKS: 0.66 -> **0.91**
- [ ] MarzGuns.SVD: 0.66 -> **0.91**
- [ ] MarzGuns.THOMPSON: 0.66 -> **0.91**?
- [ ] MarzGuns.MINI_14: 0.65 -> **0.92**
- [ ] GunsOfTienPost93.SCARH / SCARL: 0.65 -> **0.93**
- [ ] MarzGuns.AK74: 0.65 -> **0.93**
- [ ] MarzGuns.W1873: 0.64 -> **0.94**?
- [ ] MarzGuns.AK47: 0.64 -> **0.94**
- [ ] GunsOfTien.M249: 0.64 -> **0.94**
- [ ] MarzGuns.G3: 0.64 -> **0.94**
- [ ] MarzGuns.STEVENS_555: 0.64 -> **0.94**?
- [ ] MarzGuns.W1873_CARBINE: 0.64 -> **0.95**?
- [ ] MarzGuns.M79: 0.63 -> **0.95**
- [ ] MarzGuns.M1903: 0.63 -> **0.95**
- [ ] MarzGuns.ASVAL: 0.63 -> **0.95**
- [ ] MarzGuns.FNC: 0.63 -> **0.96**
- [ ] MarzGuns.M1895: 0.63 -> **0.96**?
- [ ] MarzGuns.MOSSBERG_590 (and MASTERKEY_Weapon, same model): 0.63 -> **0.96**
- [ ] MarzGuns.DOUBLEBARREL: 0.60 -> **1.01**? (was 0.63 -> 0.96: the audit took the `scale` of its
      `shellholder` point for the model's; fixed in scale_audit.py)
- [ ] MarzGuns.M4A1: 0.63 -> **0.96**
- [ ] MarzGuns.CAR15 (and CAR15_M203_Weapon): 0.63 -> **0.96**?
- [ ] MarzGuns.REMINGTON_700: 0.62 -> **0.97**?
- [ ] MarzGuns.M24: 0.62 -> **0.97**
- [ ] MarzGuns.G36C: 0.62 -> **0.97**
- [ ] MarzGuns.TOZ34: 0.61 -> **0.98**
- [ ] MarzGuns.M60: 0.61 -> **0.98**
- [ ] MarzGuns.M14: 0.61 -> **0.98**
- [ ] MarzGuns.G36: 0.61 -> **0.98**
- [ ] MarzGuns.AR15: 0.61 -> **0.98**
- [ ] MarzGuns.MOSIN: 0.61 -> **0.99**
- [ ] MarzGuns.M16A1: 0.61 -> **0.99**
- MarzGuns.M16A2, M16A3, M16A2_M203 (and M203_Weapon): **1.00**, the anchor.
- [ ] MarzGuns.SPAS12, M1_GARAND, PSG1: 0.60 -> **1.00**; MODEL_70: 0.60 -> **1.00**?
- [ ] MarzGuns.TRENCHGUN: 0.58 -> **1.04**
- [ ] MarzGuns.AA12: 0.58 -> **1.05**
- [ ] MarzGuns.BENELLI_M4: 0.58 -> **1.05**
- [ ] MarzGuns.BAR: 0.56 -> **1.07**
- [ ] MarzGuns.REMINGTON_870: 0.55 -> **1.10**?
- [ ] MarzGuns.W1887: 0.53 -> **1.14**?
- [ ] MarzGuns.DOUBLE_DEUCE (Stolzer & Son 2-bore): by eye.

Our compact stance:
- [ ] MarzGuns.MP5K: 0.72 -> **0.84**
- [ ] GunsOfTien.UZI, MINIUZI: 0.72 -> **0.84**

SMGs held as pistols:
- [ ] GunsOfTienPost93.P90TR, MP7A1, MP7A2: 0.72 -> **0.84**
- [ ] GunsOfTien.MICROUZI: 0.71 -> **0.85**
- [ ] MarzGuns.MAC10: 0.70 -> **0.87**
- [ ] MarzGuns.TEC9: 0.69 -> **0.88**

Pistols:
- [ ] MarzGuns.DETECTIVE_38: 0.87 -> **0.69** (a 2" snub drawn the size of a 4")
- [ ] MarzGuns.MP412: 0.81 -> **0.75**?
- [ ] MarzGuns.COLT_SINGLE: 0.74 -> **0.82**?
- [ ] MarzGuns.RHINO: 0.73 -> **0.82**?
- [ ] MarzGuns.HIPOWER: 0.73 -> **0.83**
- [ ] MarzGuns.P226: 0.72 -> **0.83**
- [ ] MarzGuns.GLOCK17, FIVESEVEN (ours, module MarzGuns), GunsOfTienPost93.UCP: 0.72 -> **0.84**
- [ ] MarzGuns.M93R: 0.71 -> **0.85**
- [ ] MarzGuns.PYTHON: 0.70 -> **0.86**
- [ ] MarzGuns.M1911: 0.70 -> **0.86**
- [ ] MarzGuns.SW629: 0.69 -> **0.87**?
- [ ] MarzGuns.M92FS: 0.69 -> **0.88**
- [ ] MarzGuns.USP: 0.67 -> **0.90**
- [ ] MarzGuns.DEAGLE: 0.64 -> **0.94**
- [ ] MarzGuns.VP70M: 0.60 -> **1.01**

### Stances and animations

- [ ] Rifle-stance guns (vanilla's rifle clips: the left palm sits 0.20-0.22 ahead of the grip, fixed): with the
      scales above the palm's distance to the gun's underside changes by under 3 mm on every gun but the UMPs, so
      resizing alone needs no new clips there. The UMPs at 0.83: the idle palm lands on a 0.9 cm thin part (was a
      4.9 cm deep one) and the aimed one on a deeper one: check, maybe a left-hand place of their own.
- [ ] Left hands already off today, whatever the size (vanilla's own rifles: 1.1 cm under the gun idle, 2.8 aimed):
      GoM's MP5 / MP5A2 / MP5SD ~2 cm lower (3.0 / 4.6: the hand floats under the handguard), our SCAR-L / H, G3,
      Thompson ~1.1-1.3 cm lower, FAL / FNC / AS VAL / Mossberg ~0.8; FAMAS: the palm is ahead of its handguard (1.4
      cm thick there: the barrel). Bolt rifles, M79, Stevens, BAR, Camp Carbine: palm 0.5-2 cm into the forend
      (probably just the fingers round the wood; look). Fixing these = per-gun left-hand places (Gunworks `GripAnim`
      clip sets, as the compact stance), a separate job from the size: which ones?
- [ ] Reloads after resizing: the magazine well moves back (1 - s) x its y (MP5 at 0.87: 1.5 cm) and cocking handles
      likewise (MP5 ~3.1 cm), so check every resized gun's reload and rack in game: vanilla's clips per reload type
      (magazine rifles, no-magazine bolts, pump, break-action, lever, revolver, handgun) and GoM's own (bullpup, FAL
      rack, handgun2).
- [ ] Our clips were solved for today's sizes: the compact stance (4 sets, 1016 nodes: Uzi, UziT, MP5K, MP7) and the
      reloads (smg_reload.py compact_uzi / mp5k / mp7, m249_reload.py, the P90's, the Uzi's): rebuild them from the
      scaled points (places x s); plan in "Rebuilding our clips at the new sizes".
- [ ] Pistols on vanilla's handgun clips hold the grip only; scaling about the grip origin keeps both hands on it,
      the grip just gets smaller: check the fingers.

### Found on the way

- [ ] Muzzle points away from the barrel's end (flash / tracer start): ahead: AR-15, M16A2 / A3 / A2 M203 +5.4 cm,
      AS VAL +5.6, W1887 +5.7, Detective .38 +5.5, Model 70 +4.0, M14 and M1 +2.8, AK-47 +2.1, P226 +1.1, FAMAS
      +1.0; inside: W1894 -7.0, FAL -4.9, Remington 870 -2.1, PSG1 -2.0, 93R -1.9, MP5 -1.4, Rhino -1.2, MP5A2 -1.0.
      Look in game before touching (the M16s' may sit past a flash hider that is a part).
- Shared parts are sized loosely (ratio to real): M9 bayonet 0.54, K98 0.54, M5 0.57, M1905 0.60, M1 0.64, PSO-1
  0.51, EXPS3 0.38. They take the gun's scale, so a resized gun shrinks or grows its parts with it.
