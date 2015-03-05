from django.db import models
import random
from django.utils import timezone
from utils import ItemType, RoomType, clamp
from django.contrib.auth.models import User


########################################################################
class Item(models.Model):
    name = models.CharField(max_length=60, db_index=True, unique=True)
    type = models.PositiveSmallIntegerField(choices=ItemType.choices(), default=ItemType.ARMOR)
    min = models.PositiveSmallIntegerField(default=0)
    max = models.PositiveSmallIntegerField(default=0)
    speed = models.PositiveSmallIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    strength = models.PositiveSmallIntegerField(default=0)
    health = models.PositiveSmallIntegerField(default=0)
    agility = models.PositiveSmallIntegerField(default=0)
    max_hit_points = models.PositiveSmallIntegerField(default=0)
    accuracy = models.PositiveSmallIntegerField(default=0)
    dodging = models.PositiveSmallIntegerField(default=0)
    strike_damage = models.PositiveSmallIntegerField(default=0)
    damage_absorb = models.PositiveSmallIntegerField(default=0)
    hp_regen = models.PositiveSmallIntegerField(default=0)

    ####################################################################
    def __unicode__(self):
        return self.name


########################################################################
class Room(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    type = models.PositiveSmallIntegerField(choices=ItemType.choices(), default=RoomType.PLAIN_ROOM)
    description = models.TextField()
    north = models.ForeignKey("Room", null=True, default=None, related_name="+")
    east = models.ForeignKey("Room", null=True, default=None, related_name="+")
    south = models.ForeignKey("Room", null=True, default=None, related_name="+")
    west = models.ForeignKey("Room", null=True, default=None, related_name="+")
    enemy_type = models.ForeignKey("EnemyTemplate", null=True, default=None)
    max_enemies = models.PositiveSmallIntegerField(default=0)
    items = models.ManyToManyField(Item)
    money = models.PositiveIntegerField(default=0)

    ####################################################################
    def __unicode__(self):
        return self.name

    ####################################################################
    def send_room(self, message):
        for player in self.player_set.all():
            player.send_string(message)


########################################################################
class Store(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT)

    ####################################################################
    def __unicode__(self):
        return self.room.name


########################################################################
class StoreItem(models.Model):
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("store", "item")

    ####################################################################
    def __unicode__(self):
        return self.item.name


########################################################################
class EnemyTemplate(models.Model):
    name = models.CharField(max_length=60, db_index=True, unique=True)
    hit_points = models.SmallIntegerField()
    accuracy = models.SmallIntegerField(default=0)
    dodging = models.SmallIntegerField(default=0)
    strike_damage = models.SmallIntegerField(default=0)
    damage_absorb = models.SmallIntegerField(default=0)
    experience = models.SmallIntegerField()
    weapon = models.ForeignKey(Item, null=True, blank=True, default=None, related_name="+")
    money_min = models.SmallIntegerField(default=0)
    money_max = models.SmallIntegerField(default=0)
    loot = models.ManyToManyField(Item, through="EnemyLoot")

    ####################################################################
    def __unicode__(self):
        return self.name

    ####################################################################
    def create_enemy(self, room):
        return Enemy.objects.create(template=self, hit_points=self.hit_points, room=room)


########################################################################
class EnemyLoot(models.Model):
    enemy_template = models.ForeignKey(EnemyTemplate, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    percent_chance = models.SmallIntegerField()

    class Meta:
        unique_together = ("enemy_template", "item")

    ####################################################################
    def __unicode__(self):
        return self.item.name


########################################################################
class Enemy(models.Model):
    template = models.ForeignKey(EnemyTemplate, on_delete=models.PROTECT)
    hit_points = models.SmallIntegerField()
    room = models.ForeignKey(Room)
    next_attack_time = models.SmallIntegerField(default=1)

    class Meta:
        verbose_name_plural = "Enemies"

    ####################################################################
    def __unicode__(self):
        return "(%s) %s" % (self.id, self.template.name)

    ####################################################################
    @property
    def name(self):
        return self.template.name

    ####################################################################
    @property
    def accuracy(self):
        return self.template.accuracy

    ####################################################################
    @property
    def dodging(self):
        return self.template.dodging

    ####################################################################
    @property
    def strike_damage(self):
        return self.template.strike_damage

    ####################################################################
    @property
    def damage_absorb(self):
        return self.template.damage_absorb

    ####################################################################
    @property
    def experience(self):
        return self.template.experience

    ####################################################################
    @property
    def weapon(self):
        return self.template.weapon

    ####################################################################
    @property
    def money_min(self):
        return self.template.money_min

    ####################################################################
    @property
    def money_max(self):
        return self.template.money_max

    ####################################################################
    @property
    def loot(self):
        return self.template.loot_set

    ####################################################################
    def add_hit_points(self, hit_points):
        self.hit_points += hit_points
        self.hit_points = clamp(self.hit_points, 0, self.template.hit_points)

    ####################################################################
    def attack(self):
        # attack a random player in the room
        p = random.choice(list(self.room.players))
        if not self.weapon:  # fists, 1-3 damage, 1 second swing time
            damage = random.randint(1, 3)
            self.next_attack_time = 1
        else:
            damage = random.randint(self.weapon.min, self.weapon.max)
            self.next_attack_time = self.weapon.speed

        if random.randint(0, 99) >= (self.accuracy - p.attributes.dodging):
            self.room.send_room("<white>{} swings at {} but misses!".format(self.name, p.name))
            return
        damage += self.strike_damage
        damage -= p.attributes.damage_absorb
        if damage < 1:
            damage = 1

        p.add_hit_points(-damage)
        self.room.send_room("<red>{} hits {} for {} damage!".format(self.name, p.name, damage))
        if p.hit_points <= 0:
            p.killed()

    ####################################################################
    def killed(self, killer):
        self.room.send_room("<cyan><bold>%s has died!" % self.name)

        # drop the money
        money = random.randint(self.money_min, self.money_max)
        if money > 0:
            self.room.money += money
            self.room.send_room("<cyan>$%s drops to the ground." % money)

        for item, chance in self.loot:
            if random.randint(0, 99) < chance:
                self.room.add_item(item)
                self.room.send_room("<cyan>%s drops to the ground." % item.name)
        killer.experience += self.experience
        killer.send_string("<cyan><bold>You gain %s experience." % self.experience)
        Enemy.objects.filter(id=self.id).delete()


########################################################################
class Player(models.Model):
    user = models.ForeignKey(User)
    last_command = models.CharField(max_length=60, default="look")
    name = models.CharField(max_length=60, db_index=True, unique=True)
    stat_points = models.PositiveIntegerField(default=18)
    experience = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1)
    money = models.PositiveIntegerField(default=0)
    next_attack_time = models.PositiveIntegerField(default=0)
    hit_points = models.PositiveIntegerField(default=1)
    weapon = models.ForeignKey(Item, null=True, blank=True, default=None, related_name="+")
    armor = models.ForeignKey(Item, null=True, blank=True, default=None, related_name="+")
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    logged_in = models.BooleanField(db_index=True, default=False)
    active = models.BooleanField(db_index=True, default=False)
    newbie = models.BooleanField(default=True)
    base_strength = models.PositiveSmallIntegerField(default=1)
    base_health = models.PositiveSmallIntegerField(default=1)
    base_agility = models.PositiveSmallIntegerField(default=1)
    base_max_hit_points = models.PositiveSmallIntegerField(default=0)
    base_accuracy = models.PositiveSmallIntegerField(default=0)
    base_dodging = models.PositiveSmallIntegerField(default=0)
    base_strike_damage = models.PositiveSmallIntegerField(default=0)
    base_damage_absorb = models.PositiveSmallIntegerField(default=0)
    base_hp_regen = models.PositiveSmallIntegerField(default=0)

    modifier_strength = models.PositiveSmallIntegerField(default=0)
    modifier_health = models.PositiveSmallIntegerField(default=0)
    modifier_agility = models.PositiveSmallIntegerField(default=0)
    modifier_max_hit_points = models.PositiveSmallIntegerField(default=0)
    modifier_accuracy = models.PositiveSmallIntegerField(default=0)
    modifier_dodging = models.PositiveSmallIntegerField(default=0)
    modifier_strike_damage = models.PositiveSmallIntegerField(default=0)
    modifier_damage_absorb = models.PositiveSmallIntegerField(default=0)
    modifier_hp_regen = models.PositiveSmallIntegerField(default=0)

    strength = models.PositiveSmallIntegerField(default=0)
    health = models.PositiveSmallIntegerField(default=0)
    agility = models.PositiveSmallIntegerField(default=0)
    max_hit_points = models.PositiveSmallIntegerField(default=0)
    accuracy = models.PositiveSmallIntegerField(default=0)
    dodging = models.PositiveSmallIntegerField(default=0)
    strike_damage = models.PositiveSmallIntegerField(default=0)
    damage_absorb = models.PositiveSmallIntegerField(default=0)
    hp_regen = models.PositiveSmallIntegerField(default=0)

    ####################################################################
    def __unicode__(self):
        return self.name

    ####################################################################
    def recalculate_stats(self):
        raise NotImplementedError

    ####################################################################
    @property
    def max_hit_points(self):
        return int(10 + (self.level * self.health / 1.5)) + self.modifier_max_hit_points + self.base_max_hit_points

    ####################################################################
    @property
    def health(self):
        return self.base_health + self.modifier_health

    ####################################################################
    def perform_heal_cycle(self):
        self.add_hit_points(self.hp_regen)

    ####################################################################
    def send_string(self, message):
        print "sending message to %s: %s" % (self, message)


########################################################################
class PlayerMessage(models.Model):
    player = models.ForeignKey(Player)
    text = models.TextField()
    created = models.DateTimeField(default=timezone.now)
