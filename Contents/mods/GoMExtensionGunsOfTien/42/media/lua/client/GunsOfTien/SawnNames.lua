--[[
    Guns of Tien -- sawn-off guns named in this client's language wherever it lists them.

    A sawn gun's name is a per-item string (SawnStock.ApplyLook), set again on whichever machine re-applies the gun:
    the server when it saws it, a client when one of its players equips or picks it up. A gun sawn on a dedicated
    server and never handled since carries the server's name in its bytes, which every client gets with the
    container's contents: before 3.6.1 the translation key ("IGUI_GunsOfTien_MOSIN_SawnBoth"; a dedicated server has
    no mod translations, SawnStock.lua's header), since then English. So before a loot or inventory pane lists a
    container (ISInventoryPane:refreshContainer, run whenever its items change), the client applies the look to our
    sawn guns in it, on its own copy: nothing is sent, and the server's copy is renamed the next time a player handles
    the gun. Found by full type (ItemContainer.containsType in Java), so other containers cost four lookups.
--]]

require "ISUI/ISInventoryPane"
local SawnStock = require("GunsOfTien/SawnStock")

local GUN_TYPES = {}
for fullType in pairs(SawnStock.GUNS) do GUN_TYPES[#GUN_TYPES + 1] = fullType end

local function renameIn(container)
    if not container then return end
    for _, fullType in ipairs(GUN_TYPES) do
        if container:containsType(fullType) then
            local guns = container:getAllType(fullType)
            for i = 0, guns:size() - 1 do
                SawnStock.ApplyLook(guns:get(i))
            end
        end
    end
end

if not ISInventoryPane.GunsOfTien_refreshContainer then
    ISInventoryPane.GunsOfTien_refreshContainer = ISInventoryPane.refreshContainer
    function ISInventoryPane:refreshContainer(...)
        pcall(renameIn, self.inventory)
        return ISInventoryPane.GunsOfTien_refreshContainer(self, ...)
    end
end
