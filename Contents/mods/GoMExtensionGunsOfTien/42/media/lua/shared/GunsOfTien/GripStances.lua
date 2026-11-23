--[[
    Guns of Tien -- Guns of Marz's grip stances on our guns (GoM's November 2026 update: "new stances for MP5,
    Thompson and Famas including foregrip animation").

    GoM registers its MP5s, Thompson and FAMAS with Gunworks' GripAnim as { animId = "SMG", variants = { Foregrip =
    "ForegripSMG" } } (its Registries/GripStances.lua): GoM's own SMG idle / move / aim nodes, and their foregrip
    versions while a registered foregrip is fitted. Every one of our two-handed guns that reloads with GoM's MP5 or
    FAMAS reload (GoMReloads.lua) is registered the same way, so it is held as GoM holds the gun it already borrows
    the reload from: here the AUG A1, the SVU and the unused two-handed Uzi (Post-93's GripStances.lua does its own).
    These are GoM's nodes, not ours (CLAUDE.md, "GoM's animations only"); they need Weapon = firearm, a two-handed
    gun in both hands, so our one-handed guns (pistol clips) are left as they are. Other two-handed guns carrying
    GoM's Stub, MKC or MK2 foregrip take GoM's rifle foregrip stance by themselves (Gunworks finds the part).
--]]

local GripAnim = require("WeaponSystems/Utils/GripAnim")
pcall(require, "MarzWeapons/Registries/GripStances")
pcall(require, "MarzWeapons/Registries/Foregrips")

local SMG = { animId = "SMG", variants = { [GripAnim.FOREGRIP] = "ForegripSMG" } }

GripAnim.RegisterMultipleWeapons({
    ["GunsOfTien.AUG"] = SMG,
    ["GunsOfTien.SVU"] = SMG,
    ["GunsOfTien.UZI_2H"] = SMG,
})

return SMG
