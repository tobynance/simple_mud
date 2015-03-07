import logging
from django.db import models, transaction
import random
import math
from django.utils import timezone
from attributes import Direction
from utils import ItemType, RoomType, clamp, double_find_by_name
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)
MODIFIER_FIELDS = ["modifier_strength", "modifier_health", "modifier_agility", "modifier_max_hit_points", "modifier_accuracy", "modifier_dodging", "modifier_strike_damage", "modifier_damage_absorb", "modifier_hp_regen"]
ATTRIBUTE_FIELDS = ["strength", "health", "agility", "max_hit_points", "accuracy", "dodging", "strike_damage", "damage_absorb", "hp_regen"]


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
    max_items = 32
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

    ####################################################################
    @property
    def connecting_rooms(self):
        rooms = {}
        for d in Direction:
            room = getattr(self, d.name.lower())
            if room:
                rooms[d] = room
        print "rooms:", rooms
        return rooms

    ####################################################################
    def get_adjacent_room(self, direction):
        return self.connecting_rooms[direction]

    ####################################################################
    def find_enemy(self, enemy_name):
        return double_find_by_name(enemy_name, self.enemy_set.all())

    ####################################################################
    def add_item(self, item):
        while self.items.all().count() >= self.max_items:
            self.remove_item(self.items.all().first())
        self.items.add(item)

    ####################################################################
    def remove_item(self, item):
        self.items.remove(item)


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
    def add_hit_points(self, hit_points):
        self.hit_points += hit_points
        self.hit_points = clamp(self.hit_points, 0, self.template.hit_points)

    ####################################################################
    def attack(self):
        # attack a random player in the room
        p = random.choice(list(self.room.player_set.all()))
        if not self.weapon:  # fists, 1-3 damage, 1 second swing time
            damage = random.randint(1, 3)
            self.next_attack_time = 1
        else:
            damage = random.randint(self.weapon.min, self.weapon.max)
            self.next_attack_time = self.weapon.speed

        if random.randint(0, 99) >= (self.accuracy - p.dodging):
            self.room.send_room("<white>{} swings at {} but misses!".format(self.name, p.name))
            return
        damage += self.strike_damage
        damage -= p.damage_absorb
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

        for enemy_loot in EnemyLoot.objects.filter(enemy_template=self.template):
            if random.randint(0, 99) < enemy_loot.chance:
                self.room.add_item(enemy_loot.item)
                self.room.send_room("<cyan>%s drops to the ground." % enemy_loot.item.name)
        killer.experience += self.experience
        killer.send_string("<cyan><bold>You gain %s experience." % self.experience)
        Enemy.objects.filter(id=self.id).delete()


########################################################################
class Player(models.Model):
    max_items = 16
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
    inventory = models.ManyToManyField(Item)
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

    ####################################################################
    @property
    def strength(self):
        return self.base_strength + self.modifier_strength

    ####################################################################
    @property
    def health(self):
        return self.base_health + self.modifier_health

    ####################################################################
    @property
    def agility(self):
        return self.base_agility + self.modifier_agility

    ####################################################################
    @property
    def max_hit_points(self):
        return int(10 + (self.level * self.health / 1.5)) + self.modifier_max_hit_points + self.base_max_hit_points

    ####################################################################
    @property
    def hp_regen(self):
        return (self.health // 5) + self.level + self.modifier_hp_regen + self.base_hp_regen

    ####################################################################
    @property
    def accuracy(self):
        return self.agility * 3 + self.modifier_accuracy + self.base_accuracy

    ####################################################################
    @property
    def dodging(self):
        return self.agility * 3 + self.modifier_dodging + self.base_dodging

    ####################################################################
    @property
    def strike_damage(self):
        return (self.strength // 5) + self.modifier_strike_damage + self.base_strike_damage

    ####################################################################
    @property
    def damage_absorb(self):
        return (self.strength // 5) + self.modifier_damage_absorb + self.base_damage_absorb

    ####################################################################
    def __unicode__(self):
        return self.name

    ####################################################################
    def recalculate_stats(self):
        logger.debug("Recalculating...")

        for field in MODIFIER_FIELDS:
            setattr(self, field, 0)

        if self.weapon:
            self._add_dynamic_bonuses(self.weapon)
        if self.armor:
            self._add_dynamic_bonuses(self.armor)

        # make sure the hit points don't overflow if your max goes down
        if self.hit_points > self.max_hit_points:
            self.hit_points = self.max_hit_points
            self.save(MODIFIER_FIELDS + ["hit_points"])
        else:
            self.save(update_fields=MODIFIER_FIELDS)

    ####################################################################
    def _add_dynamic_bonuses(self, item):
        if item:
            for field in ATTRIBUTE_FIELDS:
                modifier_field = "modifier_" + field
                value = getattr(self, modifier_field) + getattr(item, field)
                setattr(self, modifier_field, value)

    ####################################################################
    def need_for_level(self, level=None):
        if level is None:
            level = self.level + 1
        return int(100 * math.pow(1.4, level - 1) - 1)

    ####################################################################
    def perform_heal_cycle(self):
        self.add_hit_points(self.hp_regen)

    ####################################################################
    def add_hit_points(self, hit_points, save=True):
        self.hit_points += hit_points
        self.hit_points = clamp(self.hit_points, 0, self.attributes.MAX_HIT_POINTS)
        if save:
            self.save(update_fields=["hit_points"])

    ####################################################################
    def set_hit_points(self, hit_points, save=True):
        self.hit_points = hit_points
        self.hit_points = clamp(self.hit_points, 0, self.attributes.MAX_HIT_POINTS)
        if save:
            self.save(update_fields=["hit_points"])

    ####################################################################
    def send_string(self, message):
        PlayerMessage.objects.create(player=self, text=message)

    ####################################################################
    def set_active(self, active):
        if active is True:
            self.active = True
            self.save(update_fields=["active"])
        else:
            self.active = False
            self.last_command = "look"
            self.save(update_fields=["active", "last_command"])

    ####################################################################
    def drop_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            if item == self.weapon:
                self.weapon = None
                self.save(update_fields=["weapon"])
            if item == self.armor:
                self.armor = None
                self.save(update_fields=["armor"])
            return True
        else:
            return False

    ####################################################################
    def pick_up_item(self, item):
        if self.inventory.count() < self.max_items:
            self.inventory.add(item)

    ####################################################################
    def buy_item(self, item):
        if self.money >= item.price and self.inventory.count() < self.max_items:
            with transaction.atomic():
                self.money -= item.price
                self.inventory.add(item)
                self.save(update_fields=["money"])
            return True
        else:
            return False

    ####################################################################
    def sell_item(self, item):
        with transaction.atomic():
            self.drop_item(item)
            self.money += item.price

    ####################################################################
    def remove_weapon(self):
        self.weapon = None
        self.save(update_fields=["weapon"])
        self.recalculate_stats()

    ####################################################################
    def remove_armor(self):
        self.armor = None
        self.save(update_fields=["armor"])
        self.recalculate_stats()

    ####################################################################
    def use_weapon(self, item):
        self.weapon = item
        self.save(update_fields=["weapon"])
        self.recalculate_stats()

    ####################################################################
    def use_armor(self, item):
        self.armor = item
        self.save(update_fields=["armor"])
        self.recalculate_stats()

    ####################################################################
    def killed(self):
        self.room.send_room("<p class='bold red'>{} has died!</p>".format(self.name))
        money = self.money // 10
        # calculate how much money to drop
        if money > 0:
            self.room.money += money
            self.money -= money
            self.room.send_room("<p class='cyan'>${} drops to the ground.</p>".format(money))
        if self.inventory:
            some_item = random.choice(self.inventory)
            self.drop_item(some_item)
            self.room.add_item(some_item)
            self.room.send_room("<p class='cyan'>{} drops to the ground.</p>".format(some_item.name))

        exp = self.experience // 10
        self.experience -= exp  # subtract 10% of player experience
        self.room.remove_player(self)
        self.room = room.room_database.by_id[1]
        self.room.add_player(self)

        # set player HP to 70%
        self.set_hit_points(int(self.attributes.MAX_HIT_POINTS * 0.7))

        self.send_string("<p class='bold white'>You have died, but you have resurrected in %s</p>" % self.room.name)
        self.send_string("<p class='bold red'>You have lost %s experience!</p>" % exp)
        self.room.send_room("<p class='bold white'>%s appears out of nowhere!!</p>" % self.name)

    ####################################################################
    def attack(self, enemy_name):
        # check if the player can attack yet
        if self.next_attack_time > 0:
            self.send_string("<p class='bold red'>You can't attack yet!</p>")
            return
        if enemy_name is None:
            # If there are no enemies to attack, tell the player
            if not Enemy.objects.filter(room=self.room).exists():
                self.send_string("<p class='bold red'>You don't see anything to attack here!</p>")
                return
            e = random.choice(list(self.room.enemy_set.all()))
        else:
            e = self.room.find_enemy(enemy_name)
            # if we can't find the enemy, tell the player
            if e is None:
                self.send_string("<p class='bold red'>You don't see that here!</p>")
                return

        if self.weapon is None:  # fists, 1-3 damage, 1 second swing time
            damage = random.randint(1, 3)
            self.next_attack_time = 1
        else:
            damage = random.randint(self.weapon.min, self.weapon.max)
            self.next_attack_time = self.weapon.speed

        if random.randint(0, 99) >= (self.accuracy - e.dodging):
            self.room.send_room("<p class='white'>{} swings at {} but misses!</p>".format(self.name, e.name))
            return
        damage += self.strike_damage
        damage -= e.damage_absorb
        if damage < 1:
            damage = 1

        e.add_hit_points(-damage)
        self.room.send_room("<p class='bold red'>{} hits {} for {} damage!</p>".format(self.name, e.name, damage))
        if e.hit_points <= 0:
            e.killed(self)


########################################################################
class PlayerMessage(models.Model):
    player = models.ForeignKey(Player)
    text = models.TextField()
    created = models.DateTimeField(default=timezone.now)
