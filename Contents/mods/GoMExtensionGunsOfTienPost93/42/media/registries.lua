-- Ammo types and item tags of GoM Extension: Guns of Tien - Post-93.
-- An AmmoType's item key (second argument) must be the round's full type: vanilla reload code finds rounds in the
-- inventory by getAmmoType():getItemKey(). Own namespace: Gunworks registers swmg:bullet_57x28 with no item, and Guns
-- of Marz names MarzGuns.57x28_* items it does not define yet, so those names are left alone.

GunsOfTienPost93_AmmoTypes = {}

GunsOfTienPost93_AmmoTypes.BULLET_46x30 = AmmoType.register("gunsoftienpost93:bullet_46x30", "GunsOfTienPost93.46x30_Bullet")
GunsOfTienPost93_AmmoTypes.BULLET_46x30_Subsonic = AmmoType.register("gunsoftienpost93:bullet_46x30_subsonic", "GunsOfTienPost93.46x30_Bullet_Subsonic")

-- SS190 is registered by the main mod since 2026-11-03 (its P90): its registries.lua runs first (mod.info loadModAfter),
-- and this line never throws if it did not, so the registrations below always happen
GunsOfTienPost93_AmmoTypes.BULLET_57x28 = GunsOfTien_AmmoTypes and GunsOfTien_AmmoTypes.BULLET_57x28 or nil
GunsOfTienPost93_AmmoTypes.BULLET_57x28_SB193 = AmmoType.register("gunsoftienpost93:bullet_57x28_sb193", "GunsOfTienPost93.57x28_Bullet_SB193")
GunsOfTienPost93_AmmoTypes.BULLET_57x28_SS197SR = AmmoType.register("gunsoftienpost93:bullet_57x28_ss197sr", "GunsOfTienPost93.57x28_Bullet_SS197SR")
-- a load for the main mod's 7.62x25mm Tokarev (its registries.lua registers the calibre)
GunsOfTienPost93_AmmoTypes.BULLET_762x25_HollowPoint = AmmoType.register("gunsoftienpost93:bullet_762x25_hollow_point", "GunsOfTienPost93.762x25_Bullet_HollowPoint")
-- Special rounds audit (2026-11-25): later or undated loads for the main mod's and Guns of Marz's calibres
GunsOfTienPost93_AmmoTypes.BULLET_46x30_DM21 = AmmoType.register("gunsoftienpost93:bullet_46x30_dm21", "GunsOfTienPost93.46x30_Bullet_DM21")
GunsOfTienPost93_AmmoTypes.BULLET_9x18_PMM = AmmoType.register("gunsoftienpost93:bullet_9x18_pmm", "GunsOfTienPost93.9x18_Bullet_PMM")
GunsOfTienPost93_AmmoTypes.BULLET_9x18_RG028 = AmmoType.register("gunsoftienpost93:bullet_9x18_rg028", "GunsOfTienPost93.9x18_Bullet_RG028")
GunsOfTienPost93_AmmoTypes.BULLET_762x54_SP = AmmoType.register("gunsoftienpost93:bullet_762x54_sp", "GunsOfTienPost93.762x54_Bullet_SP")
GunsOfTienPost93_AmmoTypes.BULLET_762x54_7N13 = AmmoType.register("gunsoftienpost93:bullet_762x54_7n13", "GunsOfTienPost93.762x54_Bullet_7N13")
GunsOfTienPost93_AmmoTypes.BULLET_545x39_7N22 = AmmoType.register("gunsoftienpost93:bullet_545x39_7n22", "GunsOfTienPost93.545x39_Bullet_7N22")
GunsOfTienPost93_AmmoTypes.BULLET_9x19_7N21 = AmmoType.register("gunsoftienpost93:bullet_9x19_7n21", "GunsOfTienPost93.9x19_Bullet_7N21")
GunsOfTienPost93_AmmoTypes.BULLET_762x39_HollowPoint = AmmoType.register("gunsoftienpost93:bullet_762x39_hollow_point", "GunsOfTienPost93.762x39_Bullet_HollowPoint")
GunsOfTienPost93_AmmoTypes.BULLET_3030_FTX = AmmoType.register("gunsoftienpost93:bullet_3030_ftx", "GunsOfTienPost93.3030_Bullet_FTX")
GunsOfTienPost93_AmmoTypes.BULLET_50_HollowPoint = AmmoType.register("gunsoftienpost93:bullet_50_hollow_point", "GunsOfTienPost93.50_Bullet_HollowPoint")
GunsOfTienPost93_AmmoTypes.SHELL_12G_DragonsBreath = AmmoType.register("gunsoftienpost93:shell_12g_dragons_breath", "GunsOfTienPost93.12Gauge_Shell_DragonsBreath")

GunsOfTienPost93_Tags = {}
GunsOfTienPost93_Tags.AmmoBox50 = ItemTag.register("gunsoftienpost93:ammobox50")
GunsOfTienPost93_Tags.AmmoBox = ItemTag.register("gunsoftienpost93:ammobox")
GunsOfTienPost93_Tags.AmmoCarton = ItemTag.register("gunsoftienpost93:ammocarton")
GunsOfTienPost93_Tags.AmmoCrate = ItemTag.register("gunsoftienpost93:ammocrate")
