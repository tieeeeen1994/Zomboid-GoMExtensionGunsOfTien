--[[
    Guns of Tien - Post-93 -- 4.6x30mm and 5.7x28mm in Gunworks' ammo families, and their stat profiles; the UMPs'
    magazines in Guns of Marz's .45 ACP and 9x19mm families, the SCAR-H's in its 7.62x51mm family.

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
    ["5.7x28mm"] = {
        M .. "57x28Magazine50_P90",
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
    -- the SCAR-H's magazines, so they take GoM's .308 and the main mod's .308 Soft Point as well as its 7.62x51
    ["7.62x51mm"] = {
        M .. "762x51Magazine20_SCARH",
        M .. "762x51Magazine10_SCARH",
        M .. "762x51Magazine50_SCARH",
    },
})

Ammo.RegisterMultipleAmmoFamilies({
    ["4.6x30mm"] = {
        { type = M .. "46x30_Bullet", enum = T.BULLET_46x30, profile = "GunsOfTienPost93_46x30DM11" },
        { type = M .. "46x30_Bullet_Subsonic", enum = T.BULLET_46x30_Subsonic, profile = "GunsOfTienPost93_46x30Subsonic" },
    },
    ["5.7x28mm"] = {
        { type = M .. "57x28_Bullet", enum = T.BULLET_57x28, profile = "GunsOfTienPost93_57x28SS190" },
        { type = M .. "57x28_Bullet_SB193", enum = T.BULLET_57x28_SB193, profile = "GunsOfTienPost93_57x28SB193" },
        { type = M .. "57x28_Bullet_SS197SR", enum = T.BULLET_57x28_SS197SR, profile = "GunsOfTienPost93_57x28SS197SR" },
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

local function subsonic()
    local a, b = pierce(1)
    return {
        SF.Multiply("MaxDamage", 0.6), SF.Multiply("MinDamage", 0.6),
        SF.Multiply("SoundRadius", 0.5), SF.Multiply("SoundVolume", 0.5),
        a, b,
    }
end

Ammo.RegisterMultipleAmmoStats({
    ["GunsOfTienPost93_46x30DM11"] = standard(),
    ["GunsOfTienPost93_57x28SS190"] = standard(),
    ["GunsOfTienPost93_46x30Subsonic"] = subsonic(),
    ["GunsOfTienPost93_57x28SB193"] = subsonic(),
    ["GunsOfTienPost93_57x28SS197SR"] = (function()
        local a, b = pierce(1)
        return {
            SF.Multiply("MaxDamage", 1.15), SF.Multiply("MinDamage", 1.15),
            SF.Multiply("CritDmgMultiplier", 1.1),
            a, b,
        }
    end)(),
})
