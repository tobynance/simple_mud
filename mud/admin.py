from django.contrib import admin
import mud.models


########################################################################
class ItemAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "type", "min", "max", "speed", "price",
                    "STRENGTH", "HEALTH", "AGILITY", "MAX_HIT_POINTS",
                    "ACCURACY", "DODGING", "STRIKE_DAMAGE",
                    "DAMAGE_ABSORB", "HP_REGEN")

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
    search_fields = ("template_name", "room_name")
    list_display = ("template_name", "hit_points", "next_attack_time")

    ####################################################################
    def template_name(self, obj):
        return obj.template.name

    ####################################################################
    def room_name(self, obj):
        return obj.room.name

admin.site.register(mud.models.Enemy, EnemyAdmin)


########################################################################
class StoreAdmin(admin.ModelAdmin):
    search_fields = ["room"]
    list_display = ["room"]

    ####################################################################
    def template_name(self, obj):
        return obj.template.name

    ####################################################################
    def room_name(self, obj):
        return obj.room.name

admin.site.register(mud.models.Store, StoreAdmin)
