--[[
    Guns of Tien -- charging handles that do not reciprocate (user, 2026-10-30: "the charging handle and the bolt is
    not always the same, and this is the case for MP7 and AUG").

    On every gun of both mods but the SCARs (whose handle rides with the carrier) the real handle stays forward while
    the gun fires: the Uzi, Mini and Micro Uzi (IMI's top knob), the Steyr TMP (its knob at the rear top), the M249, the Steyr AUGs, and Post-93's MP7s, P90
    and UMPs (2026-10-30). Only the bolt or carrier inside moves, seen through the ejection port (on the right, under
    the P90 and the M249). So on these guns GoM's Bolt part (MarzGuns.Bolt_Lock / Bolt_Fired, which Gunworks swaps on each shot,
    while the gun is empty and during the rack) draws the bolt (`<gun>_BOLT`, a plate over the port's front half),
    and the handle is a part of its own: GunsOfTien.ChargingHandle_Forward / _Back (PartType ChargingHandle,
    items_handles.txt), drawn by each gun's ModelWeaponPart lines at `handle` / `handle_back`.

    The handle goes back only while racked, through Gunworks' own reload route (2026-11-04): a gun's animated parts
    entry may carry a `reload` table that the rack's rackStart / rackEnd (and openWeapon / closeWeapon) use instead
    of the entry, while firing keeps the entry's parts. GoM moves its AR-15s' charging handle that way
    (AnimationsFiring.lua, Bolt_AR15), and so do ours: each gun file registers ChargingHandle.ANIMATED_PARTS with
    Gunworks' own Animations.RegisterWeaponWithAnimatedParts, one entry shared by every such gun as GoM shares
    Bolt_AR15. Nothing of Gunworks' is wrapped (until 2026-11-04 this file wrapped ISRackFirearm and
    Animations.CallAnimationFunction, and the latter dropped the route for every gun: GoM's AR-15 handles and its
    revolvers' swing-out cylinders stopped moving, Marz, 2026-11-03).

    A gun saved before 2026-10-30 has no ChargingHandle part and shows no handle until its first rack fits one, as
    GoM's AR-15s saved before their handle part (user, 2026-11-04: GoM's way, no equip hook); a found or crafted
    gun comes with it (the guns' required parts).
--]]

local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")

local ChargingHandle = {}

ChargingHandle.FORWARD = "GunsOfTien.ChargingHandle_Forward"
ChargingHandle.BACK = "GunsOfTien.ChargingHandle_Back"

local Bolt = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" }

--- The Gunworks animated parts entry of a gun whose handle is the ChargingHandle part (its item script draws both
--- states): GoM's bolt swap (its AnimationsFiring.lua "Bolt") when firing, the bolt and the handle when racking.
ChargingHandle.ANIMATED_PARTS = {
    SingleAttachment = Bolt,
    cycleTicks = 3,
    reload = {
        MultipleAttachment = {
            Bolt = Bolt,
            ChargingHandle = { open = ChargingHandle.BACK, locked = ChargingHandle.FORWARD },
        },
    },
}

PreventRemoval.Register({ ChargingHandle.FORWARD, ChargingHandle.BACK })

return ChargingHandle
