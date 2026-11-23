--[[
    Guns of Tien -- integral folding front grips (the main mod's Steyr AUG A1, Post-93's AUG A3 / Para / HBAR and
    MP7A1).

    A gun's folding grip is two hidden parts of part type ForegripIntegrated, the folded one and the deployed one,
    each drawn through the gun's own ModelWeaponPart line at its point. The fitted part is the state, so there is
    nothing else to save or restore; its stats come from Gunworks' CustomStatsAttachments layer (registered beside
    each gun: GoM's Stub Foregrip numbers on the deployed part).

    Since Guns of Marz's November 2026 update the fold is Gunworks' generic pair swap, as GoM does its rail bipod,
    Beretta stock and SPAS-12 selector (its AttachmentCustomStats.lua): `DynamicAttachment.RegisterPair(folded,
    deployed)` gives Gunworks' "Swap to <part>" in the gun's context menu and firearm radial menu, and its
    ISSwapAttachment timed action swaps the part (server side in multiplayer, then StatsSync and
    CallSyncHandWeaponFields) and re-applies the stats. Our own fold action (ISFoldForegripGoT), menu
    (ForegripMenu.lua) and radial icons were removed with it. Guns saved folded or unfolded keep the same two items,
    so they swap as before; a gun saved before its grip parts existed (neither fitted) has nothing to swap, as
    GoM's guns saved before a part existed.

    A two-handed gun's deployed grip is also a foregrip for Gunworks' grip stances (`GripAnim.RegisterForegrip`, as
    GoM registers its Stub, MKC and MK2): GoM's foregrip nodes, or the gun's own "ForegripSMG" variant
    (GripStances.lua). GoM's nodes are rifle-held only (Weapon = firearm), so a one-handed gun's grip (the MP7A1's)
    is not registered.
--]]

local DynamicAttachment = require("WeaponSystems/Utils/DynamicAttachment")
local GripAnim = require("WeaponSystems/Utils/GripAnim")

local Foregrip = {}

--- Register a folding grip's two parts as a Gunworks swap pair; `twoHanded` also makes the deployed one a foregrip
--- for GoM's grip stances.
---@param folded string
---@param deployed string
---@param twoHanded boolean
function Foregrip.Register(folded, deployed, twoHanded)
    DynamicAttachment.RegisterPair(deployed, folded)
    if twoHanded then GripAnim.RegisterForegrip(deployed) end
end

return Foregrip
