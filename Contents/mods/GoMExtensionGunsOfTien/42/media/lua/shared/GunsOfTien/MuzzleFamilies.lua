--[[
    Guns of Tien -- every gun takes its calibre family's muzzle mount device (user, 2026-11-23: "I want every gun to
    have a muzzle device so that they can attach stuff here so long as our current muzzle device family supports it
    in that calibre. The suppressors on the other hand need real life checking")

    Families: GoM's AR (5.56: mount, LR2 compensator, LX flash hider, Trix42 brake, MKI and NDR cans), AK (5.45 and
    7.62x39: mount, PBS-1), .45 (mount, P45), the 9x19mm mount (GoM's, Suppressors.lua: M&P and Shh9 pistol cans, the
    Mk9, every one on every 9mm gun) and Post-93's 7.62x51mm mount with the SOCOM762-RC. The flash hider, compensator and brake go on
    every gun of their family; a can only where the real gun takes one (threaded, a known adapter, or routine
    gunsmith threading), checked on 2026-11-23:
    - AUG A1 (M13x1 LH, Rat Worx / Dead Air mounts), Model 70 (threaded by a gunsmith), XM177 (its moderator screws
      onto 1/2-28 and came off for birdcages): the AR cans. The M249 takes the AR muzzle devices (1/2-28) but no
      rifle can: real M249 cans are machine-gun cans (SureFire SOCOM556-MG, KAC), a rifle can cooks.
    - SKS (Chinese 14x1 LH threading kits and slip-on adapters, the AK's thread): the AK mount and PBS-1.
    - Thompson (Maxim silencers were sold for it in the 1920s) and Camp Carbine (blowback, threaded by a gunsmith):
      the P45.
    - TEC-9 (its 3/4x10 thread is the MAC's, so AWC's Mk9 screws straight on; a blowback pistol, so pistol cans need
      no booster): every 9mm can, drawn with the main mod's adapter at the shroud's front. Every 9mm can fits every
      9mm gun with the mount since 2026-11-23 (Suppressors.lua: the same stats on all three
      apart).
    - SR-25, FAL, G3, M14 (SureFire SF3P-762 / SFMB-762 devices for each), Remington 700, M24 and PSG-1 (threaded by
      a gunsmith, as the Model 70): the SOCOM762-RC (Post-93; every line and MountOn here is a no-op without it).
    No mount at all where nothing of the family would fit: the RPD (belt fed, the PBS-1 is a rifle can), M60 (the
    SOCOM762-RC is not SureFire's belt-fed can), AUG HBAR (a Steyr AUG, not an AK: the AK family is the AK's 14x1 LH
    thread, which no AUG has), Colt Single Action Army (the cylinder gap), MP5K (its barrel ends
    flush, only the MP5K-N had threads) and MP5SD (integral can).

    `canon` sits where the real device would screw on: the rear of the gun's own flash hider (G3, M14 ahead of
    its front sight, XM177's moderator, M249, as GoM's AR-15 birdcage and our HK417) or the TEC-9's barrel
    shroud, else the bore's front, on the bore axis;
    measured from muzzle_audit.py's bore front and the barrel's vertex rings (game units). Our own guns (AUG A1,
    M249, SR-25) have the point and the model lines in their scripts (gen_scripts.py,
    gen_post93_guns.py); GoM's get both here, through GoMAttachments.lua's tables (points on GoM's loaded models,
    lines with DoParam once per script object, MountOn read and written back whole).
--]]

local GoMAttachments = require("GunsOfTien/GoMAttachments")

local MOUNT_MODEL = "MarzGuns.Muzzle_Mount_Device"         -- GoM draws every one of its mounts with this
local AR_MOUNT = "MarzGuns.AR_Muzzle_Mount_Device"
local AR_DEVICES = { "MarzGuns.LR2_Compensator", "MarzGuns.LX_Flashhider", "MarzGuns.Trix42_Muzzlebreak" }
local AR_CANS = { "MarzGuns.MKI_Suppressor", "MarzGuns.NDR_Suppressor" }
local AK = { "MarzGuns.AK_Muzzle_Mount_Device", "MarzGuns.PBS-1_Suppressor" }
local ACP45 = { "MarzGuns.45_Muzzle_Mount_Device", "MarzGuns.P45_Suppressor" }
local NINE_MOUNTS = { "MarzGuns.Pistol_Muzzle_Mount_Device", "GunsOfTien.SMG9_Muzzle_Mount_Device" }
local NINE_CANS = { "GunsOfTien.Mk9_Suppressor", "MarzGuns.M&P_Suppressor", "MarzGuns.Shh9_Suppressor" }
local NATO762 = { "GunsOfTienPost93.SCARH_Muzzle_Mount_Device", "GunsOfTienPost93.SCARH_Suppressor" }

local function join(...)
    local out = {}
    for _, list in ipairs({ ... }) do
        for _, part in ipairs(list) do out[#out + 1] = part end
    end
    return out
end
local AR_ALL = join({ AR_MOUNT }, AR_DEVICES, AR_CANS)

-- part -> the model GoM's guns draw it with (others: the part's own name)
local MODELS = {
    [AR_MOUNT] = MOUNT_MODEL,
    [AK[1]] = MOUNT_MODEL,
    [ACP45[1]] = MOUNT_MODEL,
    [NINE_MOUNTS[1]] = "GunsOfTien.SMG9_Muzzle_Mount_Device",  -- the TEC-9's, at GoM's size (the Mk9's adapter)
    [NINE_MOUNTS[2]] = "GunsOfTien.SMG9_Muzzle_Mount_Device",
}

-- gun -> { parts it takes, `canon` on GoM's model (nil: the gun's script has the point and lines) }
local GUNS = {
    ["MarzGuns.FNC"] = { parts = AR_DEVICES, lines = true },          -- GoM gives it the mount and cans, `canon`
    ["MarzGuns.MINI_14"] = { parts = AR_DEVICES, lines = true },
    ["MarzGuns.MODEL_70"] = { parts = AR_ALL, canon = { 0.0, 0.4700, 0.0148 } },
    ["MarzGuns.XM177"] = { parts = AR_ALL, canon = { 0.0, 0.3292, 0.0256 } },     -- the moderator's rear
    ["GunsOfTien.AUG"] = { parts = AR_ALL },
    ["GunsOfTien.M249"] = { parts = join({ AR_MOUNT }, AR_DEVICES) },
    ["MarzGuns.SKS"] = { parts = AK, canon = { 0.0, 0.5310, 0.0221 } },
    ["MarzGuns.THOMPSON"] = { parts = ACP45, canon = { 0.0, 0.3140, 0.0451 } },
    ["MarzGuns.CAMP_CARBINE"] = { parts = ACP45, canon = { 0.0, 0.4466, 0.0151 } },
    ["MarzGuns.TEC9"] = { parts = join(NINE_MOUNTS, NINE_CANS), canon = { 0.0, 0.2088, -0.0405 } },  -- shroud's front
    ["GunsOfTien.SR25"] = { parts = NATO762 },
    -- the FAL's own hider is 9 cm long: from its rear a 4 cm SureFire device left 5 cm of it sticking out ahead, so
    -- `canon` sits 3.98 cm (the SF3P's length) behind the bore's front and the devices cover its front instead
    ["MarzGuns.FAL"] = { parts = NATO762, canon = { 0.0, 0.5114, 0.0259 } },
    ["MarzGuns.G3"] = { parts = NATO762, canon = { 0.0, 0.4277, 0.0362 } },       -- the flash hider's rear
    ["MarzGuns.M14"] = { parts = NATO762, canon = { 0.0, 0.4962, 0.0288 } },      -- the flash suppressor's rear
    ["MarzGuns.M24"] = { parts = NATO762, canon = { 0.0, 0.5043, 0.0137 } },
    ["MarzGuns.PSG1"] = { parts = NATO762, canon = { 0.0, 0.5344, 0.0268 } },
    ["MarzGuns.REMINGTON_700"] = { parts = NATO762, canon = { 0.0, 0.5037, 0.0137 } },
}

for gun, entry in pairs(GUNS) do
    for _, part in ipairs(entry.parts) do
        GoMAttachments.MOUNT_ADD[part] = GoMAttachments.MOUNT_ADD[part] or {}
        table.insert(GoMAttachments.MOUNT_ADD[part], gun)
    end
    if entry.canon or entry.lines then
        local lines = {}
        for _, part in ipairs(entry.parts) do
            lines[#lines + 1] = { part, MODELS[part] or part, "canon" }
        end
        GoMAttachments.LINES[gun] = lines
    end
    if entry.canon then
        GoMAttachments.POINTS[gun] = { canon = entry.canon }        -- GoM's gun models are named as their items
    end
end

-- The real muzzle devices (user, 2026-11-23: "Option A", "Real fit only"; scripts/muzzle_devices.py, generated into
-- MuzzleDevicesTable.lua): flash hiders, compensators and brakes per family, each fitting the guns the real one was made
-- for (MountOn in the devices' own scripts, the main mod's and Post-93's). Stats are GoM's by kind (its LX / Trix42
-- sound and volume x0.95, its LR2 x0.90, all remove the flash), each needs its family's mount, and GoM's guns get their
-- model lines here (ours have them in their scripts). A device built into a gun's mesh (the AK-74's brake, the
-- AR-15's birdcage) stays cosmetic, as GoM has it: the bare gun's stats, the fitted device's full effect (user).
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local DEVICES = require("GunsOfTien/MuzzleDevicesTable")

local stats = {}
for device, d in pairs(DEVICES) do
    stats[device] = {
        SF.Multiply("SoundRadius", d.sound),
        SF.Multiply("SoundVolume", d.sound),
        SF.Set("MuzzleFlashModelKey", nil),
    }
    RequiredAttachment.RegisterRequired({ device }, d.mounts)
    for _, gun in ipairs(d.guns) do
        if string.sub(gun, 1, 9) == "MarzGuns." then
            GoMAttachments.LINES[gun] = GoMAttachments.LINES[gun] or {}
            table.insert(GoMAttachments.LINES[gun], { device, device, "canon" })
        end
    end
end
CSA.RegisterMultipleParts(stats)
