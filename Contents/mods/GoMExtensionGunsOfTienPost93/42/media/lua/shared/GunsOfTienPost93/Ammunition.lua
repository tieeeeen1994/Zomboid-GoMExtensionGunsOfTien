--[[
    Guns of Tien - Post-93 -- 4.6x30mm and 5.7x28mm in Gunworks' ammo families, and their stat profiles; the UMPs'
    magazines in Guns of Marz's .45 ACP and 9x19mm families, the SCAR-H's and the MDRx .308's in its 7.62x51mm family
    (the MDRx .223 takes GoM's STANAGs, already in its 5.56x45mm family).

    Two new families. As with Guns of Marz's magazine-fed guns, the magazines are in the family, not the guns.
    The standard rounds (DM11, SS190) are the guns' own script rounds, which Gunworks never gives an ammo profile
    (Ammo.AmmoProfileSetter returns early when the round's enum equals the gun's AmmoType), so their piercing is in
    the gun scripts (PiercingBullets, MaxHitcount 2). The other loads are profiles applied on top of that.
    How the families and profiles work: the main mod's shared/GunsOfTien/Ammunition.lua and CLAUDE.md.
--]]

local Ammo = require("WeaponSystems/Utils/Ammo")
local SF = require("WeaponSystems/Utils/StatsFactory")
pcall(require, "MarzWeapons/Registries/Ammunition")

local T = GunsOfTienPost93_AmmoTypes
local M = "GunsOfTienPost93."

Ammo.RegisterMultipleItemsWithFamilies({
    ["4.6x30mm"] = {
        M .. "46x30Magazine20_MP7",
        M .. "46x30Magazine30_MP7",
        M .. "46x30Magazine40_MP7",
        M .. "46x30Magazine20_UCP",
        M .. "46x30Magazine40_UCP",
    },
    -- the P90's magazine is in the family from the main mod (shared/GunsOfTien/Ammunition.lua)
    ["5.7x28mm"] = {
        M .. "57x28Magazine20_FIVESEVEN",
        M .. "57x28Magazine30_FIVESEVEN",
    },
    -- the UMPs' magazines join Guns of Marz's own families (its rounds and the main mod's special loads)
    [".45 ACP"] = {
        M .. "45Magazine25_UMP",
        M .. "45Magazine20_UMP",
        M .. "45Magazine10_UMP",
    },
    ["9x19mm"] = {
        M .. "9x19Magazine30_UMP",
    },
    -- the SCAR-H's and the MDRx .308's magazines, so they take GoM's .308 and the main mod's .308 Soft Point as well
    -- as its 7.62x51
    ["7.62x51mm"] = {
        M .. "762x51Magazine20_SCARH",
        M .. "762x51Magazine10_SCARH",
        M .. "762x51Magazine50_SCARH",
        M .. "762x51Magazine10_PMAG",
        M .. "762x51Magazine20_PMAG",
        M .. "762x51Magazine25_PMAG",
        M .. "762x51Magazine50_PMAG",
    },
})

Ammo.RegisterMultipleAmmoFamilies({
    ["4.6x30mm"] = {
        { type = M .. "46x30_Bullet", enum = T.BULLET_46x30, profile = "GunsOfTienPost93_46x30DM11" },
        { type = M .. "46x30_Bullet_Subsonic", enum = T.BULLET_46x30_Subsonic, profile = "GunsOfTienPost93_46x30Subsonic" },
    },
    -- SS190 and its profile are the main mod's (moved 2026-11-03 for its P90); these two are added to its family
    ["5.7x28mm"] = {
        { type = M .. "57x28_Bullet_SB193", enum = T.BULLET_57x28_SB193, profile = "GunsOfTienPost93_57x28SB193" },
        { type = M .. "57x28_Bullet_SS197SR", enum = T.BULLET_57x28_SS197SR, profile = "GunsOfTienPost93_57x28SS197SR" },
    },
    -- the main mod's Tokarev family (its plain round, Steel Core and Subsonic); no hollow point dated before 1993
    ["7.62x25mm"] = {
        { type = M .. "762x25_Bullet_HollowPoint", enum = T.BULLET_762x25_HollowPoint, profile = "GunsOfTienPost93_762x25HollowPoint" },
    },
    -- Special rounds audit (2026-11-25, TODO.md): later or undated loads, into the main mod's and GoM's families
    ["4.6x30mm"] = {
        { type = M .. "46x30_Bullet_DM21", enum = T.BULLET_46x30_DM21, profile = "GunsOfTienPost93_46x30DM21" },
    },
    ["9x18mm"] = {
        { type = M .. "9x18_Bullet_PMM", enum = T.BULLET_9x18_PMM, profile = "GunsOfTienPost93_9x18PMM" },
        { type = M .. "9x18_Bullet_RG028", enum = T.BULLET_9x18_RG028, profile = "GunsOfTienPost93_PistolAP" },
    },
    ["7.62x54mm"] = {
        { type = M .. "762x54_Bullet_SP", enum = T.BULLET_762x54_SP, profile = "GunsOfTien_RifleSoftPoint" },
        { type = M .. "762x54_Bullet_7N13", enum = T.BULLET_762x54_7N13, profile = "GunsOfTienPost93_762x54_7N13" },
    },
    ["5.45x39mm"] = {
        { type = M .. "545x39_Bullet_7N22", enum = T.BULLET_545x39_7N22, profile = "GunsOfTienPost93_545x39_7N22" },
    },
    ["9x19mm"] = {
        { type = M .. "9x19_Bullet_7N21", enum = T.BULLET_9x19_7N21, profile = "GunsOfTienPost93_9x19_7N21" },
    },
    ["7.62x39mm"] = {
        { type = M .. "762x39_Bullet_HollowPoint", enum = T.BULLET_762x39_HollowPoint, profile = "GunsOfTienPost93_762x39HollowPoint" },
    },
    [".30-30 Winchester"] = {
        { type = M .. "3030_Bullet_FTX", enum = T.BULLET_3030_FTX, profile = "GunsOfTienPost93_3030FTX" },
    },
    [".50 AE"] = {
        { type = M .. "50_Bullet_HollowPoint", enum = T.BULLET_50_HollowPoint, profile = "GunsOfTien_HandgunHollowPoint" },
    },
    ["9x39mm"] = {
        { type = M .. "9x39_Bullet_PAB9", enum = T.BULLET_9x39_PAB9, profile = "GunsOfTienPost93_9x39PAB9" },
    },
    ["12Gauge"] = {
        { type = M .. "12Gauge_Shell_DragonsBreath", enum = T.SHELL_12G_DragonsBreath, profile = "GunsOfTienPost93_12GaugeDragonsBreath" },
    },
})

local function pierce(targets)
    return SF.Set("PiercingBullets", targets > 1), SF.Set("MaxHitCount", targets)
end

-- Kept explicit so switching back from another load always restores the standard round's piercing, even on a gun
-- whose script were changed.
local function standard()
    local a, b = pierce(2)
    return { a, b }
end

-- Sound x0.7 as the main mod's 147gr 9mm (user, 2026-10-24; it was GoM's 5.56 subsonic x0.5, which made a suppressed
-- MP7 quieter than the MP5SD); damage 4.6x30 x0.6, SB193 x0.7.
local function subsonic(damage)
    local a, b = pierce(1)
    return {
        SF.Multiply("MaxDamage", damage), SF.Multiply("MinDamage", damage),
        SF.Multiply("SoundRadius", 0.7), SF.Multiply("SoundVolume", 0.7),
        a, b,
    }
end

Ammo.RegisterMultipleAmmoStats({
    ["GunsOfTienPost93_46x30DM11"] = standard(),
    ["GunsOfTienPost93_46x30Subsonic"] = subsonic(0.6),
    ["GunsOfTienPost93_57x28SB193"] = subsonic(0.7),
    ["GunsOfTienPost93_57x28SS197SR"] = (function()
        local a, b = pierce(1)
        return {
            SF.Multiply("MaxDamage", 1.15), SF.Multiply("MinDamage", 1.15),
            SF.Multiply("CritDmgMultiplier", 1.1),
            a, b,
        }
    end)(),
    -- the main mod's 9x19 / .45 hollow points' numbers, and no piercing (the Tokarev's plain round is famous for it)
    -- Special rounds audit (2026-11-25). DM21: the soft lead-cored ball beside the DM11's steel penetrator, so it
    -- hits harder and stops in the first target
    ["GunsOfTienPost93_46x30DM21"] = (function()
        local a, b = pierce(1)
        return { SF.Multiply("MaxDamage", 1.1), SF.Multiply("MinDamage", 1.1), SF.Multiply("CritDmgMultiplier", 1.1), a, b }
    end)(),
    -- PMM (early 1990s): the hot Makarov load, as the 9x19 +P+
    ["GunsOfTienPost93_9x18PMM"] = {
        SF.Multiply("MaxDamage", 1.2), SF.Multiply("MinDamage", 1.2),
        SF.Multiply("CritDmgMultiplier", 1.1),
        SF.Multiply("SoundRadius", 1.1), SF.Multiply("SoundVolume", 1.1),
        SF.Multiply("ConditionLowerChanceOneIn", 0.6),
    },
    -- pistol armour piercing (RG028): the main mod's Tokarev steel core
    ["GunsOfTienPost93_PistolAP"] = (function()
        local a, b = pierce(2)
        return {
            SF.Multiply("MaxDamage", 0.9), SF.Multiply("MinDamage", 0.9),
            SF.Multiply("CritDmgMultiplier", 0.95), SF.Multiply("CriticalChance", 0.9),
            SF.Multiply("ConditionLowerChanceOneIn", 0.85),
            a, b,
        }
    end)(),
    -- 7N21: a hot 9x19 with a steel penetrator: the pistol AP's piercing and damage, the +P+'s wear
    ["GunsOfTienPost93_9x19_7N21"] = (function()
        local a, b = pierce(2)
        return {
            SF.Multiply("MaxDamage", 0.9), SF.Multiply("MinDamage", 0.9),
            SF.Multiply("SoundRadius", 1.1), SF.Multiply("SoundVolume", 1.1),
            SF.Multiply("ConditionLowerChanceOneIn", 0.7),
            a, b,
        }
    end)(),
    -- 7N13 (1990s): the better penetrator than the B-32 (1932; x0.9, 3 targets), so a target more and lighter
    ["GunsOfTienPost93_762x54_7N13"] = (function()
        local a, b = pierce(4)
        return {
            SF.Multiply("MaxDamage", 0.85), SF.Multiply("MinDamage", 0.85),
            SF.Multiply("CritDmgMultiplier", 0.95), SF.Multiply("CriticalChance", 0.9),
            SF.Multiply("ConditionLowerChanceOneIn", 0.85),
            a, b,
        }
    end)(),
    -- 7N22 (1998): the AP 5.45, two targets more than the plain 7N6's 3 and one more than the 7N10
    ["GunsOfTienPost93_545x39_7N22"] = (function()
        local a, b = pierce(5)
        return {
            SF.Multiply("MaxDamage", 0.9), SF.Multiply("MinDamage", 0.9),
            SF.Multiply("CritDmgMultiplier", 0.95), SF.Multiply("CriticalChance", 0.9),
            SF.Multiply("ConditionLowerChanceOneIn", 0.85),
            a, b,
        }
    end)(),
    -- 7.62x39 hollow point: opens wider than the main mod's soft point, which reaches a little further in
    ["GunsOfTienPost93_762x39HollowPoint"] = (function()
        local a, b = pierce(1)
        return {
            SF.Multiply("MaxDamage", 1.15), SF.Multiply("MinDamage", 1.15),
            SF.Multiply("CritDmgMultiplier", 1.25), SF.Multiply("CriticalChance", 1.1),
            a, b,
        }
    end)(),
    -- .30-30 FTX (2005): a pointed polymer tip safe in a tube magazine, so it flies flatter and further and opens
    -- on impact
    ["GunsOfTienPost93_3030FTX"] = (function()
        local a, b = pierce(1)
        return {
            SF.Multiply("MaxDamage", 1.15), SF.Multiply("MinDamage", 1.15),
            SF.Multiply("CriticalChance", 1.1),
            SF.Multiply("MaxRange", 1.15),
            a, b,
        }
    end)(),
    -- Dragon's breath: burning magnesium sparks, almost no hitting power and a short reach; the fire is the main
    -- mod's Incendiary.lua
    ["GunsOfTienPost93_12GaugeDragonsBreath"] = {
        SF.Multiply("MaxDamage", 0.15), SF.Multiply("MinDamage", 0.15),
        SF.Multiply("CriticalChance", 0.3),
        SF.Multiply("CritDmgMultiplier", 0.5),
        SF.Multiply("MaxRange", 0.4),
        function(weapon)
            weapon:setProjectileSpread(math.max(0.3, weapon:getProjectileSpread() * 2.5))
        end,
    },
    -- Within a calibre, the better the penetrator, the more targets and the less damage (user, 2026-11-25:
    -- "whatever has a higher pierce tech will get more pierces but lower damage of the family").
    -- PAB-9 (1995): the cheaper armour piercing 9x39, a worse penetrator than the SP-6 (x0.9, 3 targets), so
    -- between it and the plain SP-5
    ["GunsOfTienPost93_9x39PAB9"] = (function()
        local a, b = pierce(2)
        return {
            SF.Multiply("MaxDamage", 0.95), SF.Multiply("MinDamage", 0.95),
            a, b,
        }
    end)(),
    ["GunsOfTienPost93_762x25HollowPoint"] = (function()
        local a, b = pierce(1)
        return {
            SF.Multiply("MaxDamage", 1.2), SF.Multiply("MinDamage", 1.2),
            SF.Multiply("CritDmgMultiplier", 1.15),
            SF.Multiply("CriticalChance", 1.05),
            SF.Multiply("ConditionLowerChanceOneIn", 0.9),
            a, b,
        }
    end)(),
})
