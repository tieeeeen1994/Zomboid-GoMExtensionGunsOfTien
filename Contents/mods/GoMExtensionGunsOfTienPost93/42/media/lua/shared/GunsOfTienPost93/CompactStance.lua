--[[
    Guns of Tien - Post-93 -- the MP7A1 and MP7A2 in the main mod's short SMG stance (user, 2026-10-23: "MP7 needs to
    join the new stance"; one stance for every short SMG since 2026-10-28, CLAUDE.md "Animations are generic"; the P90
    stays pistol-held). See the main mod's GunsOfTien/CompactStance.lua: Gunworks' grip registry plays its AnimSet
    nodes while the gun is in hand, the stance holds the gun in the pistol orientation the MP7s are modelled in, and
    the guns are made two-handed. Held in one hand they play the pistol clips (the main mod's OneHand.lua, Guns.lua).
    The left hand takes the stance's one place (the Uzi's, under the handguard), the A1's front grip unfolded or not.
--]]

local CompactStance = require("GunsOfTien/CompactStance")
local okGW, Gunworks = pcall(require, "WeaponSystems/Gunworks")

local M = "GunsOfTienPost93."
local GUNS = { M .. "MP7A1", M .. "MP7A2" }

local function registerGrips()
    if not okGW or type(Gunworks) ~= "table" or not Gunworks.RegisterWeapon then
        return
    end
    for _, fullType in ipairs(GUNS) do
        Gunworks.RegisterWeapon(fullType, { grip = { animId = CompactStance.SHORT_SMG } })
    end
end
Events.OnGameBoot.Add(registerGrips)

local function patchScripts()
    for _, fullType in ipairs(GUNS) do
        CompactStance.makeTwoHanded(fullType)
    end
end
Events.OnGameBoot.Add(patchScripts)
Events.OnInitGlobalModData.Add(patchScripts)
