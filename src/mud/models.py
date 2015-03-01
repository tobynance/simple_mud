from django.db import models
from utils import PlayerRank, ItemType


########################################################################
class Attributes(models.Model):
    STRENGTH = models.PositiveSmallIntegerField(default=1)
    HEALTH = models.PositiveSmallIntegerField(default=1)
    AGILITY = models.PositiveSmallIntegerField(default=1)
    MAX_HIT_POINTS = models.PositiveSmallIntegerField(default=0)
    ACCURACY = models.PositiveSmallIntegerField(default=0)
    DODGING = models.PositiveSmallIntegerField(default=0)
    STRIKE_DAMAGE = models.PositiveSmallIntegerField(default=0)
    DAMAGE_ABSORB = models.PositiveSmallIntegerField(default=0)
    HP_REGEN = models.PositiveSmallIntegerField(default=0)


########################################################################
class Item(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    type = models.PositiveSmallIntegerField(choices=ItemType.choices(), default=ItemType.ARMOR)
    min = models.PositiveSmallIntegerField(default=0)
    max = models.PositiveSmallIntegerField(default=0)
    speed = models.PositiveSmallIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    attributes = models.ForeignKey(Attributes)


########################################################################
class Player(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    password = models.CharField(max_length=20)
    rank = models.PositiveSmallIntegerField(choices=PlayerRank.choices(), default=PlayerRank.REGULAR)
    stat_points = models.PositiveIntegerField(default=18)
    experience = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1)
    money = models.PositiveIntegerField(default=0)
    next_attack_time = models.PositiveIntegerField(default=0)
    hit_points = models.PositiveIntegerField(default=1)
    base_attributes = models.ForeignKey(Attributes)
    weapon = models.ForeignKey(Item, null=True, blank=True, default=None)
    armor = models.ForeignKey(Item, null=True, blank=True, default=None)
    #room = models.ForeignKey(Room)
    logged_in = models.BooleanField(db_index=True)
    active = models.BooleanField(db_index=True)
    newbie = models.BooleanField()
