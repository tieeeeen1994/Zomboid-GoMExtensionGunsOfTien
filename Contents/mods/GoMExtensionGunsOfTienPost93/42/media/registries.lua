-- Ammo types and item tags of GoM Extension: Guns of Tien - Post-93.
-- An AmmoType's item key (second argument) must be the round's full type: vanilla reload code finds rounds in the
-- inventory by getAmmoType():getItemKey(). Own namespace: Gunworks registers swmg:bullet_57x28 with no item, and Guns
-- of Marz names MarzGuns.57x28_* items it does not define yet, so those names are left alone.

GunsOfTienPost93_AmmoTypes = {}

GunsOfTienPost93_AmmoTypes.BULLET_46x30 = AmmoType.register("gunsoftienpost93:bullet_46x30", "GunsOfTienPost93.46x30_Bullet")
GunsOfTienPost93_AmmoTypes.BULLET_46x30_Subsonic = AmmoType.register("gunsoftienpost93:bullet_46x30_subsonic", "GunsOfTienPost93.46x30_Bullet_Subsonic")

GunsOfTienPost93_AmmoTypes.BULLET_57x28 = AmmoType.register("gunsoftienpost93:bullet_57x28", "GunsOfTienPost93.57x28_Bullet")
GunsOfTienPost93_AmmoTypes.BULLET_57x28_SB193 = AmmoType.register("gunsoftienpost93:bullet_57x28_sb193", "GunsOfTienPost93.57x28_Bullet_SB193")
GunsOfTienPost93_AmmoTypes.BULLET_57x28_SS197SR = AmmoType.register("gunsoftienpost93:bullet_57x28_ss197sr", "GunsOfTienPost93.57x28_Bullet_SS197SR")

GunsOfTienPost93_Tags = {}
GunsOfTienPost93_Tags.AmmoBox50 = ItemTag.register("gunsoftienpost93:ammobox50")
GunsOfTienPost93_Tags.AmmoBox = ItemTag.register("gunsoftienpost93:ammobox")
GunsOfTienPost93_Tags.AmmoCarton = ItemTag.register("gunsoftienpost93:ammocarton")
GunsOfTienPost93_Tags.AmmoCrate = ItemTag.register("gunsoftienpost93:ammocrate")
