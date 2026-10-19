--[[
    Guns of Tien -- two Guns of Marz registrations that miss their target (found 2026-10-19 while fixing its tooltips)

    - The Karabiner 98k bayonet fits no gun. Its attachment's item script mounts on the same sixteen guns as the
      other bayonets, but Registries/Bayonets.lua leaves "MarzGuns.K98_Bayonet_Attachment" out of
      Bayonet.RegisterMountableWeapon, and Gunworks' Bayonet.CanAttachBayonet asks only that registry. It is added
      to every gun that takes the M5 bayonet.
    - The overpressured 5.56's automatic fire spread penalty never applies: Registries/RPM.lua registers it as
      "MarzGuns.556x45_Bullet_Overpressured", but the round is SWMG.556x45_Bullet_Overpressured, and Gunworks'
      RateOfFire.getSpreadProfile looks modifiers up by the round's own full type. It is registered under that too.
    GoM's lua/shared loads before ours, so its registrations are in place here.
--]]

local ok, Bayonet = pcall(require, "WeaponSystems/Utils/Bayonet")
if ok and type(Bayonet) == "table" and Bayonet.BayonetMountableWeapons and Bayonet.RegisterMountableWeapon then
    local guns = {}
    for gun, accepted in pairs(Bayonet.BayonetMountableWeapons) do
        if accepted["MarzGuns.M5_Bayonet_Attachment"] and not accepted["MarzGuns.K98_Bayonet_Attachment"] then
            guns[#guns + 1] = gun
        end
    end
    if #guns > 0 then
        Bayonet.RegisterMountableWeapon("MarzGuns.K98_Bayonet_Attachment", guns)
    end
end

local okRof, RateOfFire = pcall(require, "WeaponSystems/Utils/RateOfFire")
if okRof and type(RateOfFire) == "table" and RateOfFire.SpreadPartModifiers then
    local wrong = RateOfFire.SpreadPartModifiers["MarzGuns.556x45_Bullet_Overpressured"]
    if wrong and not RateOfFire.SpreadPartModifiers["SWMG.556x45_Bullet_Overpressured"] then
        RateOfFire.RegisterSpreadAmmoModifier("SWMG.556x45_Bullet_Overpressured", wrong)
    end
end
