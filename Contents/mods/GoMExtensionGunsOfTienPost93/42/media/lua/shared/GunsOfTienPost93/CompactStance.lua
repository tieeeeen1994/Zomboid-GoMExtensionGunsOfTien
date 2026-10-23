--[[
    Guns of Tien - Post-93 -- the MP7A1 and MP7A2 in the main mod's compact SMG stance (user, 2026-10-23: "MP7 needs
    to join the new stance"; the P90 stays pistol-held). See the main mod's GunsOfTien/CompactStance.lua: Gunworks'
    grip registry plays our AnimSet nodes (AnimSets/player/*/*_GoTCompactMP7.xml) while the gun is in hand, and the
    gun is made two-handed and turned upright in the hand (it is modelled upside down for the pistol clips).

    Its own clip set ("GunsOfTien_CompactMP7") while the A1's foregrip is unfolded: the left hand on it, ~0.14 ahead
    of the grip (the Uzis' handguard ~0.13, the MP5K's foregrip ~0.18); folded and on the A2 the hand goes under the
    handguard, within ~1 cm of the Uzi's place, so they use the Uzi's clips for turned guns ("GunsOfTien_CompactUziT",
    in the main mod).
--]]

local CompactStance = require("GunsOfTien/CompactStance")
local okGW, Gunworks = pcall(require, "WeaponSystems/Gunworks")

local M = "GunsOfTienPost93."
local GUNS = { M .. "MP7A1", M .. "MP7A2" }
-- The MP7A1 with its foregrip unfolded: its own set (the hand on the foregrip); folded, and the MP7A2: the Uzi's
-- clips for guns turned upright in the hand (UziT; the hand under the handguard sits within ~1 cm of the Uzi's
-- place). Gunworks checks `when` variants first.
local DEPLOYED = M .. "MP7A1_Integrated_Foregrip_Deployed"

local function registerGrips()
    if not okGW or type(Gunworks) ~= "table" or not Gunworks.RegisterWeapon then
        return
    end
    Gunworks.RegisterWeapon(M .. "MP7A1", { grip = {
        { animId = "GunsOfTien_CompactMP7", when = { attach = DEPLOYED, present = true } },
        { animId = "GunsOfTien_CompactUziT" },
    } })
    Gunworks.RegisterWeapon(M .. "MP7A2", { grip = { animId = "GunsOfTien_CompactUziT" } })
end
Events.OnGameBoot.Add(registerGrips)

local function patchScripts()
    for _, fullType in ipairs(GUNS) do
        CompactStance.turnUpright(fullType)
    end
end
Events.OnGameBoot.Add(patchScripts)
Events.OnInitGlobalModData.Add(patchScripts)
