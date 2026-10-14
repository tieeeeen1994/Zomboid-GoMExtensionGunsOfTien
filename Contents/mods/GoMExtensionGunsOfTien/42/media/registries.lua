-- Ammo types and item tags of GoM Extension: Guns of Tien.
-- An AmmoType's item key (second argument) must be the round's full type: vanilla reload code finds rounds in the
-- inventory by getAmmoType():getItemKey().

GunsOfTien_AmmoTypes = {}

GunsOfTien_AmmoTypes.BULLET_762x39_US = AmmoType.register("gunsoftien:bullet_762x39_us", "GunsOfTien.762x39_Bullet_US")
GunsOfTien_AmmoTypes.BULLET_762x39_SP = AmmoType.register("gunsoftien:bullet_762x39_sp", "GunsOfTien.762x39_Bullet_SP")
GunsOfTien_AmmoTypes.BULLET_762x39_SteelCore = AmmoType.register("gunsoftien:bullet_762x39_steel_core", "GunsOfTien.762x39_Bullet_SteelCore")

GunsOfTien_AmmoTypes.BULLET_9x19_Subsonic = AmmoType.register("gunsoftien:bullet_9x19_subsonic", "GunsOfTien.9x19_Bullet_Subsonic")
GunsOfTien_AmmoTypes.BULLET_9x19_HollowPoint = AmmoType.register("gunsoftien:bullet_9x19_hollow_point", "GunsOfTien.9x19_Bullet_HollowPoint")
GunsOfTien_AmmoTypes.BULLET_9x19_PPP = AmmoType.register("gunsoftien:bullet_9x19_ppp", "GunsOfTien.9x19_Bullet_PPP")

GunsOfTien_AmmoTypes.BULLET_45_HollowPoint = AmmoType.register("gunsoftien:bullet_45_hollow_point", "GunsOfTien.45_Bullet_HollowPoint")
GunsOfTien_AmmoTypes.BULLET_45_P = AmmoType.register("gunsoftien:bullet_45_p", "GunsOfTien.45_Bullet_P")

GunsOfTien_AmmoTypes.BULLET_9x39_SP6 = AmmoType.register("gunsoftien:bullet_9x39_sp6", "GunsOfTien.9x39_Bullet_SP6")

GunsOfTien_AmmoTypes.BULLET_3006_SP = AmmoType.register("gunsoftien:bullet_3006_sp", "GunsOfTien.3006_Bullet_SP")
GunsOfTien_AmmoTypes.BULLET_308_SP = AmmoType.register("gunsoftien:bullet_308_sp", "GunsOfTien.308_Bullet_SP")

GunsOfTien_AmmoTypes.SHELL_12G_Birdshot = AmmoType.register("gunsoftien:shell_12g_birdshot", "GunsOfTien.12Gauge_Shell_Birdshot")

-- Box / carton / crate tags of this mod's own open and pack recipes (GoM's recipes use closed item mappers).
GunsOfTien_Tags = {}
GunsOfTien_Tags.AmmoBox20 = ItemTag.register("gunsoftien:ammobox20")
GunsOfTien_Tags.AmmoBox25 = ItemTag.register("gunsoftien:ammobox25")
GunsOfTien_Tags.AmmoBox50 = ItemTag.register("gunsoftien:ammobox50")
GunsOfTien_Tags.AmmoBox = ItemTag.register("gunsoftien:ammobox")
GunsOfTien_Tags.AmmoCarton = ItemTag.register("gunsoftien:ammocarton")
GunsOfTien_Tags.AmmoCrate = ItemTag.register("gunsoftien:ammocrate")
