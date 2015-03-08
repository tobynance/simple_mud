import logging
from django.db import models, transaction
import random
import math
from django.db.models import Sum
from django.utils import timezone
from utils import ItemType, RoomType, HandlerType, clamp, Direction
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)
MODIFIER_FIELDS = ["modifier_strength", "modifier_health", "modifier_agility", "modifier_max_hit_points", "modifier_accuracy", "modifier_dodging", "modifier_strike_damage", "modifier_damage_absorb", "modifier_hp_regen"]
BASE_FIELDS = ["base_strength", "base_health", "base_agility", "base_max_hit_points", "base_accuracy", "base_dodging", "base_strike_damage", "base_damage_absorb", "base_hp_regen"]
ATTRIBUTE_FIELDS = ["strength", "health", "agility", "max_hit_points", "accuracy", "dodging", "strike_damage", "damage_absorb", "hp_regen"]


########################################################################
class Item(models.Model):
    name = models.CharField(max_length=60, db_index=True, unique=True)
    type = models.PositiveSmallIntegerField(choices=ItemType.choices(), default=ItemType.ARMOR)
    min = models.PositiveSmallIntegerField(default=0)
    max = models.PositiveSmallIntegerField(default=0)
    speed = models.PositiveSmallIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    strength = models.SmallIntegerField(default=0)
    health = models.SmallIntegerField(default=0)
    agility = models.SmallIntegerField(default=0)
    max_hit_points = models.SmallIntegerField(default=0)
    accuracy = models.SmallIntegerField(default=0)
    dodging = models.SmallIntegerField(default=0)
    strike_damage = models.SmallIntegerField(default=0)
    damage_absorb = models.SmallIntegerField(default=0)
    hp_regen = models.SmallIntegerField(default=0)

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
    items = models.ManyToManyField(Item, blank=True, through="RoomItem")
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
        return self.enemy_set.filter(template__name__iexact=enemy_name).first() or \
               self.enemy_set.filter(template__name__istartswith=enemy_name).first()

    ####################################################################
    def get_total_inventory_count(self):
        return RoomItem.objects.filter(room=self).aggregate(Sum("quantity"))["quantity__sum"] or 0

    ####################################################################
    def add_item(self, item):
        # Drop items if too many items
        inventory_quantity = self.get_total_inventory_count()
        logger.info("inventory_quantity: %s", inventory_quantity)
        logger.info("max_items: %s", self.max_items)
        while inventory_quantity >= self.max_items:
            oldest = RoomItem.objects.filter(room=self).order_by("created").first()
            if oldest.quantity > 1:
                oldest.quantity -= 1
                oldest.save(update_fields=["quantity"])
            else:
                RoomItem.objects.filter(room=self, item=oldest.item).delete()
            inventory_quantity = self.get_total_inventory_count()

        # Now add item
        inventory_item = RoomItem.objects.filter(room=self, item=item).first()
        if inventory_item:
            inventory_item.quantity += 1
            inventory_item.save(update_fields=["quantity"])
        else:
            RoomItem.objects.create(room=self, item=item)

    ####################################################################
    def find_item(self, item_name):
        return self.items.filter(name__iexact=item_name).first() or \
               self.items.filter(name__istartswith=item_name).first()

    ####################################################################
    def remove_item(self, item):
        inventory_item = RoomItem.objects.filter(room=self, item=item).order_by("created").first()
        if inventory_item:
            if inventory_item.quantity > 1:
                inventory_item.quantity -= 1
                inventory_item.save(update_fields=["quantity"])
            else:
                RoomItem.objects.filter(room=self, item=item).delete()
            return True
        else:
            return False


########################################################################
class RoomItem(models.Model):
    room = models.ForeignKey(Room)
    item = models.ForeignKey(Item)
    quantity = models.PositiveSmallIntegerField(default=1)
    created = models.DateTimeField(default=timezone.now)


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
    loot = models.ManyToManyField(Item, through="EnemyLoot", blank=True)

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
    def add_hit_points(self, hit_points, save=True):
        self.hit_points += hit_points
        self.hit_points = clamp(self.hit_points, 0, self.template.hit_points)
        if save:
            self.save(update_fields=["hit_points"])

    ####################################################################
    def attack(self):
        # attack a random player in the room
        p = random.choice(list(self.room.player_set.all()))
        if not self.weapon:  # fists, 1-3 damage, 1 second swing time
            damage = random.randint(1, 3)
            self.next_attack_time = 1
            self.save(update_fields=["next_attack_time"])
        else:
            damage = random.randint(self.weapon.min, self.weapon.max)
            self.next_attack_time = self.weapon.speed
            self.save(update_fields=["next_attack_time"])

        if random.randint(0, 99) >= (self.accuracy - p.dodging):
            self.room.send_room("<p>{} swings at {} but misses!</p>".format(self.name, p.name))
            return
        damage += self.strike_damage
        damage -= p.damage_absorb
        if damage < 1:
            damage = 1

        p.add_hit_points(-damage)
        self.room.send_room("<p class='red'>{} hits {} for {} damage!</p>".format(self.name, p.name, damage))
        if p.hit_points <= 0:
            p.killed()

    ####################################################################
    def killed(self, killer):
        self.room.send_room("<p class='bold cyan'>%s has died!</p>" % self.name)

        # drop the money
        money = random.randint(self.money_min, self.money_max)
        if money > 0:
            self.room.money += money
            self.room.save(update_fields=["money"])
            self.room.send_room("<p class='cyan'>$%s drops to the ground.</p>" % money)

        for enemy_loot in EnemyLoot.objects.filter(enemy_template=self.template):
            if random.randint(0, 99) < enemy_loot.percent_chance:
                self.room.add_item(enemy_loot.item)
                self.room.send_room("<p class='cyan>%s drops to the ground.</p>" % enemy_loot.item.name)
        killer.experience += self.experience
        killer.save(update_fields=["experience"])
        killer.send_string("<p class='bold cyan'>You gain %s experience.</p>" % self.experience)
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
    hit_points = models.PositiveIntegerField(default=10)
    weapon = models.ForeignKey(Item, null=True, blank=True, default=None, related_name="+")
    armor = models.ForeignKey(Item, null=True, blank=True, default=None, related_name="+")
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    inventory = models.ManyToManyField(Item, blank=True, through="PlayerItem")
    logged_in = models.BooleanField(db_index=True, default=False)
    active = models.BooleanField(db_index=True, default=False)
    newbie = models.BooleanField(default=True)
    handler = models.PositiveSmallIntegerField(choices=HandlerType.choices(), default=HandlerType.TRAINING_HANDLER)

    base_strength = models.SmallIntegerField(default=1)
    base_health = models.SmallIntegerField(default=1)
    base_agility = models.SmallIntegerField(default=1)
    base_max_hit_points = models.SmallIntegerField(default=0)
    base_accuracy = models.SmallIntegerField(default=0)
    base_dodging = models.SmallIntegerField(default=0)
    base_strike_damage = models.SmallIntegerField(default=0)
    base_damage_absorb = models.SmallIntegerField(default=0)
    base_hp_regen = models.SmallIntegerField(default=0)

    modifier_strength = models.SmallIntegerField(default=0)
    modifier_health = models.SmallIntegerField(default=0)
    modifier_agility = models.SmallIntegerField(default=0)
    modifier_max_hit_points = models.SmallIntegerField(default=0)
    modifier_accuracy = models.SmallIntegerField(default=0)
    modifier_dodging = models.SmallIntegerField(default=0)
    modifier_strike_damage = models.SmallIntegerField(default=0)
    modifier_damage_absorb = models.SmallIntegerField(default=0)
    modifier_hp_regen = models.SmallIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)

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
    def need_for_next_level(self):
        return self.need_for_level(self.level + 1) - self.experience

    ####################################################################
    def perform_heal_cycle(self):
        self.add_hit_points(self.hp_regen)

    ####################################################################
    def add_hit_points(self, hit_points, save=True):
        self.hit_points += hit_points
        self.hit_points = clamp(self.hit_points, 0, self.max_hit_points)
        if save:
            self.save(update_fields=["hit_points"])

    ####################################################################
    def set_hit_points(self, hit_points, save=True):
        self.hit_points = hit_points
        self.hit_points = clamp(self.hit_points, 0, self.max_hit_points)
        if save:
            self.save(update_fields=["hit_points"])

    ####################################################################
    def send_string(self, message):
        logger.debug("send_string: %s", message)
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
        inventory_item = PlayerItem.objects.filter(player=self, item=item).order_by("created").first()
        if inventory_item:
            if inventory_item.quantity > 1:
                inventory_item.quantity -= 1
                inventory_item.save(update_fields=["quantity"])
            else:
                PlayerItem.objects.filter(player=self, item=item).delete()
            return True
        else:
            return False

    ####################################################################
    def pick_up_item(self, item):
        logger.info("item: %s", item)
        logger.info("max_items: %s", self.max_items)
        logger.info("inventory: %s", self.inventory.count())
        if self.inventory.count() < self.max_items:
            inventory_item = PlayerItem.objects.filter(player=self, item=item).first()
            if inventory_item:
                inventory_item.quantity += 1
                inventory_item.save(update_fields=["quantity"])
            else:
                PlayerItem.objects.create(player=self, item=item)
            return True
        else:
            return False

    ####################################################################
    def buy_item(self, item):
        if self.money >= item.price and self.inventory.count() < self.max_items:
            with transaction.atomic():
                inventory_item = PlayerItem.objects.filter(player=self, item=item).first()
                if inventory_item:
                    inventory_item.quantity += 1
                    inventory_item.save(update_fields=["quantity"])
                else:
                    PlayerItem.objects.create(player=self, item=item)
                self.money -= item.price
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
            self.room.save(update_fields=["money"])
            self.money -= money
            self.room.send_room("<p class='cyan'>${} drops to the ground.</p>".format(money))
        if self.inventory.exists():
            some_item = random.choice(list(self.inventory.all()))
            self.drop_item(some_item)
            self.room.add_item(some_item)
            self.room.send_room("<p class='cyan'>{} drops to the ground.</p>".format(some_item.name))

        exp = self.experience // 10
        self.experience -= exp  # subtract 10% of player experience
        self.room = Room.objects.get(id=1)

        # set player HP to 70%
        self.set_hit_points(int(self.max_hit_points * 0.7))

        self.send_string("<p class='bold white'>You have died, but you have resurrected in %s</p>" % self.room.name)
        self.send_string("<p class='bold red'>You have lost %s experience!</p>" % exp)
        self.room.send_room("<p class='bold white'>%s appears out of nowhere!!</p>" % self.name)
        self.save(update_fields=["money", "experience", "room", "hit_points"])
        logger.warn("self.room: %s", self.room)

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
            self.save(update_fields=["next_attack_time"])
        else:
            damage = random.randint(self.weapon.min, self.weapon.max)
            self.next_attack_time = self.weapon.speed
            self.save(update_fields=["next_attack_time"])

        if random.randint(0, 99) >= (self.accuracy - e.dodging):
            self.room.send_room("<p class='white'>{} swings at {} but misses!</p>".format(self.name, e.name))
            return
        damage += self.strike_damage
        damage -= e.damage_absorb
        if damage < 1:
            damage = 1

        e.add_hit_points(-damage)
        self.room.send_room("<p class='bold yellow'>{} hits {} for {} damage!</p>".format(self.name, e.name, damage))
        if e.hit_points <= 0:
            e.killed(self)

    ####################################################################
    def who_text(self):
        """Return a string describing the player"""
        text = ["<tr><td>", self.name, "</td>"]
        if self.active:
            text.append("<td class='green'>Online</td>")
        elif self.logged_in:
            text.append("<td class='yellow'>Inactive</td>")
        else:
            text.append("<td class='yellow'>Offline</td>")
        text.append("</tr>")
        return "".join(text)

    ####################################################################
    def get_handler_module(self):
        from mud import game_handler, training_handler
        if self.handler == HandlerType.GAME_HANDLER:
            return game_handler
        elif self.handler == HandlerType.TRAINING_HANDLER:
            return training_handler

    ####################################################################
    def handle(self, text):
        self.get_handler_module().handle(self, text)

    ####################################################################
    def set_handler(self, handler_type):
        self.handler = handler_type
        self.save(update_fields=["handler"])
        logger.info("Leaving handler %s", HandlerType(handler_type))
        self.get_handler_module().leave(self)
        logger.info("Entering handler %s", HandlerType(handler_type))
        self.get_handler_module().enter(self)

    ####################################################################
    def add_bonuses(self, item):
        if item:
            for field in ATTRIBUTE_FIELDS:
                base_field = "base_" + field
                value = getattr(self, base_field) + getattr(item, field)
                setattr(self, base_field, value)
        self.save(update_fields=BASE_FIELDS)
        self.recalculate_stats()

    ####################################################################
    def train(self):
        if self.need_for_next_level() <= 0:
            self.stat_points += 2
            self.base_max_hit_points += self.level
            self.level += 1
            self.save(update_fields=["stat_points", "level", "base_max_hit_points"])
            self.recalculate_stats()
            return True
        return False


########################################################################
class PlayerItem(models.Model):
    player = models.ForeignKey(Player)
    item = models.ForeignKey(Item)
    quantity = models.PositiveSmallIntegerField(default=1)
    created = models.DateTimeField(default=timezone.now)


########################################################################
class PlayerMessage(models.Model):
    player = models.ForeignKey(Player)
    text = models.TextField()
    created = models.DateTimeField(default=timezone.now)
