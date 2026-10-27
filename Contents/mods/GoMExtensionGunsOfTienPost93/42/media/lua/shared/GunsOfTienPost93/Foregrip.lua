--[[
    Guns of Tien - Post-93 -- the MP7A1's integral folding front grip.

    The real MP7A1 has a vertical front grip that folds up under the receiver: two hidden parts of part type
    ForegripIntegrated, MP7A1_Integrated_Foregrip_Folded (drawn at the gun's origin, the mesh is modelled folded) and
    ..._Deployed (drawn at the model's foregrip_deployed point, turned 90 degrees down about the hinge pin), their
    stats in Guns.lua. The fold itself (parts swap, timed action ISFoldForegripGoT, the "Fold / Unfold Foregrip"
    menu and radial slice) is the main mod's shared GunsOfTien/Foregrip.lua since 2026-10-27, which the Steyr AUG A1
    uses too; this file only registers the MP7A1 with it.
--]]

local Foregrip = require("GunsOfTien/Foregrip")

local M = "GunsOfTienPost93."

Foregrip.Register(M .. "MP7A1", {
    folded = M .. "MP7A1_Integrated_Foregrip_Folded",
    deployed = M .. "MP7A1_Integrated_Foregrip_Deployed",
    foldDesc = "IGUI_GunsOfTienPost93_FoldForegripDesc",
    unfoldDesc = "IGUI_GunsOfTienPost93_UnfoldForegripDesc",
})

return Foregrip
