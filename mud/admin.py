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
    list_display = ("name", "type", "north", "east", "south", "west", "money")

admin.site.register(mud.models.Room, RoomAdmin)
