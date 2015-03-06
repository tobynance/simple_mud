from django.contrib import admin
import mud.models


########################################################################
class ItemAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "type", "min", "max", "speed", "price",
                    "strength", "health", "agility", "max_hit_points",
                    "accuracy", "dodging", "strike_damage",
                    "damage_absorb", "hp_regen")

admin.site.register(mud.models.Item, ItemAdmin)


########################################################################
class RoomAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "type", "north_name", "east_name", "south_name", "west_name", "money")

    ####################################################################
    def north_name(self, obj):
        if obj.north:
            return obj.north.name

    ####################################################################
    def east_name(self, obj):
        if obj.east:
            return obj.east.name

    ####################################################################
    def south_name(self, obj):
        if obj.south:
            return obj.south.name

    ####################################################################
    def west_name(self, obj):
        if obj.west:
            return obj.west.name

admin.site.register(mud.models.Room, RoomAdmin)


########################################################################
class EnemyTemplateAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "hit_points", "accuracy", "dodging",
                    "strike_damage", "damage_absorb", "experience",
                    "weapon_name", "money_min", "money_max")

    ####################################################################
    def weapon_name(self, obj):
        if obj.weapon:
            return obj.weapon.name

admin.site.register(mud.models.EnemyTemplate, EnemyTemplateAdmin)


########################################################################
class EnemyAdmin(admin.ModelAdmin):
    search_fields = ("template", "room")
    list_display = ("template", "room", "hit_points", "next_attack_time")

admin.site.register(mud.models.Enemy, EnemyAdmin)


########################################################################
class StoreAdmin(admin.ModelAdmin):
    search_fields = ["room"]
    list_display = ["room"]

admin.site.register(mud.models.Store, StoreAdmin)


########################################################################
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ["user", "name", "room"]
    list_display = ["user", "name", "room", "level", "logged_in", "active", "newbie"]

admin.site.register(mud.models.Player, PlayerAdmin)
