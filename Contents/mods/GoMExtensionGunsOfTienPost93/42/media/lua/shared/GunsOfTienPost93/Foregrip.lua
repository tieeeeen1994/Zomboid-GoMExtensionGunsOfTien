--[[
    Guns of Tien - Post-93 -- the MP7A1's integral folding front grip.

    The real MP7A1 has a vertical front grip that folds up under the receiver: two hidden parts of part type
    ForegripIntegrated, MP7A1_Integrated_Foregrip_Folded (drawn at the gun's origin, the mesh is modelled folded) and
    ..._Deployed (drawn at the model's foregrip_deployed point, turned 90 degrees down about the hinge pin), their
    stats in Guns.lua. Since Guns of Marz's November 2026 update the fold is Gunworks' swap pair ("Swap to ..." in the
    context and radial menus, its ISSwapAttachment action), through the main mod's GunsOfTien/Foregrip.lua. The MP7A1
    is held one-handed, so its grip is no foregrip for GoM's rifle-held grip stances.
--]]

local Foregrip = require("GunsOfTien/Foregrip")

local M = "GunsOfTienPost93."

Foregrip.Register(M .. "MP7A1_Integrated_Foregrip_Folded", M .. "MP7A1_Integrated_Foregrip_Deployed", false)

return Foregrip
