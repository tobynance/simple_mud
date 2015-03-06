import os
import random
import time
import math
import logging
from enum import Enum, IntEnum
from attributes import Attributes, primary_attribute_list, attribute_string_list
from entity import Entity
from entity_database import EntityDatabase
import room
import enemy
from utils import clamp, double_find_by_name

base = os.path.dirname(__file__)
data_file = os.path.join(base, "..", "data", "players.json")

MAX_PLAYER_ITEMS = 16
logger = logging.getLogger(__name__)

SIMPLE_FIELDS = ["name", "password", "stat_points", "experience", "level", "money", "next_attack_time", "hit_points"]

player_attribute_strings = []
for attr in attribute_string_list:
    player_attribute_strings.append("BASE_" + attr)
    player_attribute_strings.append("MODIFIER_" + attr)
    player_attribute_strings.append(attr)

PlayerRank = IntEnum("PlayerRank", "REGULAR MODERATOR ADMIN")
PlayerAttributes = Enum("PlayerAttributes", " ".join(player_attribute_strings))

player_database = None


########################################################################
class PlayerAttributeSet(dict):
    ####################################################################
    def __init__(self, player=None):
        super(PlayerAttributeSet, self).__init__()
        self.player = player
        self.recalculating = False
        for attr in PlayerAttributes:
            self.__set_field(attr, 0)

    ####################################################################
    def set_player(self, player):
        self.player = player
        self.recalculate_stats()

    ####################################################################
    def __get_attribute(self, item):
        if isinstance(item, basestring):
            item = PlayerAttributes[item]
        elif isinstance(item, int):
            item = PlayerAttributes(item)
        return item

    ####################################################################
    def __getitem__(self, item):
        item = self.__get_attribute(item)
        return super(PlayerAttributeSet, self).__getitem__(item)

    ####################################################################
    def __set_field(self, key, value):
        item = self.__get_attribute(key)
        return super(PlayerAttributeSet, self).__setitem__(item, value)

    ####################################################################
    def __setitem__(self, key, value):
        logger.debug("setitem: %s %s", key, value)
        item = self.__get_attribute(key)

        if item.name.startswith("BASE_") or item.name.startswith("MODIFIER_"):
            result = self.__set_field(item, value)
            self.recalculate_stats()
            return result
        else:
            raise AttributeError("%s is a read-only field" % item.name)

    ####################################################################
    def recalculate_stats(self):
        if self.recalculating:
            return
        try:
            self.recalculating = True
            self._recalculate_stats()
        finally:
            self.recalculating = False

    ####################################################################
    def _recalculate_stats(self):
        logger.debug("Recalculating...")
        if self.player is None:
            logger.warn("Cannot recalculate player attributes: player is None")
            return

        for attr in attribute_string_list:
            self.__set_field("MODIFIER_" + attr, 0)

        if self.player.weapon:
            self.add_dynamic_bonuses(self.player.weapon)
        if self.player.armor:
            self.add_dynamic_bonuses(self.player.armor)

        for attr in primary_attribute_list:
            value = self["BASE_" + attr] + self["MODIFIER_" + attr]
            value = max(1, value)
            self.__set_field(attr, value)

        self.__set_field("MAX_HIT_POINTS", int(10 + (self.player.level * self.HEALTH / 1.5)) + self.MODIFIER_MAX_HIT_POINTS + self.BASE_MAX_HIT_POINTS)
        self.__set_field("HP_REGEN", (self.HEALTH // 5) + self.player.level + self.MODIFIER_HP_REGEN + self.BASE_HP_REGEN)
        self.__set_field("ACCURACY", self.AGILITY * 3 + self.MODIFIER_ACCURACY + self.BASE_ACCURACY)
        self.__set_field("DODGING", self.AGILITY * 3 + self.MODIFIER_DODGING + self.BASE_DODGING)
        self.__set_field("DAMAGE_ABSORB", (self.STRENGTH // 5) + self.MODIFIER_DAMAGE_ABSORB + self.BASE_DAMAGE_ABSORB)
        self.__set_field("STRIKE_DAMAGE", (self.STRENGTH // 5) + self.MODIFIER_STRIKE_DAMAGE + self.BASE_STRIKE_DAMAGE)
        # make sure the hit points don't overflow if your max goes down
        if self.player.hit_points > self.MAX_HIT_POINTS:
            self.player.hit_points = self.MAX_HIT_POINTS

    ####################################################################
    def add_dynamic_bonuses(self, item):
        if item:
            for attr in Attributes:
                self.__set_field("MODIFIER_" + attr.name, self["MODIFIER_" + attr.name] + item.attributes[attr])
            self.recalculate_stats()

    ####################################################################
    def add_bonuses(self, item):
        if item:
            for attr in Attributes:
                self.__set_field("BASE_" + attr.name, self["BASE_" + attr.name] + item.attributes[attr])
            self.recalculate_stats()

    ####################################################################
    def __getattr__(self, name):
        if name in player_attribute_strings:
            return self[name]
        else:
            return super(PlayerAttributeSet, self).__getattribute__(name)

    ####################################################################
    def __setattr__(self, name, value):
        if name in player_attribute_strings:
            self[name] = value
        else:
            super(PlayerAttributeSet, self).__setattr__(name, value)


########################################################################
class Player(Entity):
    ####################################################################
    def __init__(self, player_id=None):
        super(Player, self).__init__()
        self.id = player_id or player_database.get_next_id()
        self.password = "UNDEFINED"
        self.rank = PlayerRank.REGULAR
        self.stat_points = 18
        self.experience = 0
        self.level = 1
        self.room = room.room_database.by_id[1]
        self.money = 0
        self.next_attack_time = 0
        self.hit_points = 0

        self.inventory = []
        self.weapon = None
        self.armor = None

        self.protocol = None
        self.logged_in = False
        self.active = False
        self.newbie = False
        self.attributes = PlayerAttributeSet(self)
        self.attributes.BASE_STRENGTH = 1
        self.attributes.BASE_HEALTH = 1
        self.attributes.BASE_AGILITY = 1

        self.recalculate_stats()
        self.hit_points = self.attributes.MAX_HIT_POINTS

    ####################################################################
    def get_remote_address(self):
        if self.protocol is not None:
            return self.protocol.get_remote_address()

    ####################################################################
    def need_for_level(self, level=None):
        if level is None:
            level = self.level + 1
        return int(100 * math.pow(1.4, level - 1) - 1)

    ####################################################################
    def need_for_next_level(self):
        return self.need_for_level(self.level + 1) - self.experience

    ####################################################################
    def train(self):
        if self.need_for_next_level() <= 0:
            self.stat_points += 2
            self.attributes.BASE_MAX_HIT_POINTS += self.level
            self.level += 1
            self.recalculate_stats()
            return True
        return False

    ####################################################################
    def recalculate_stats(self):
        self.attributes.recalculate_stats()

    ####################################################################
    def add_dynamic_bonuses(self, item):
        self.attributes.add_dynamic_bonuses(item)

    ####################################################################
    def add_hit_points(self, hit_points):
        self.hit_points += hit_points
        self.hit_points = clamp(self.hit_points, 0, self.attributes.MAX_HIT_POINTS)

    ####################################################################
    def set_hit_points(self, hit_points):
        self.hit_points = hit_points
        self.hit_points = clamp(self.hit_points, 0, self.attributes.MAX_HIT_POINTS)

    ####################################################################
    def pick_up_item(self, item):
        if len(self.inventory) < self.get_max_items():
            self.inventory.append(item)
            return True
        else:
            return False

    ####################################################################
    def find_in_inventory(self, item_name):
        return double_find_by_name(item_name, self.inventory)

    ####################################################################
    def drop_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            if item == self.weapon:
                self.weapon = None
            if item == self.armor:
                self.armor = None
            return True
        else:
            return False

    ####################################################################
    def add_bonuses(self, item):
        self.attributes.add_bonuses(item)

    ####################################################################
    def remove_weapon(self):
        self.weapon = None
        self.recalculate_stats()

    ####################################################################
    def remove_armor(self):
        self.armor = None
        self.recalculate_stats()

    ####################################################################
    def use_weapon(self, item):
        self.remove_weapon()
        self.weapon = item
        self.recalculate_stats()

    ####################################################################
    def use_armor(self, item):
        self.remove_armor()
        self.armor = item
        self.recalculate_stats()

    ####################################################################
    def get_max_items(self):
        return MAX_PLAYER_ITEMS

    ####################################################################
    def get_item_index(self, name):
        """This gets the index of an item within the player's inventory given a name."""
        item = double_find_by_name(name, self.inventory)
        if item:
            self.inventory.index(item)

    ####################################################################
    def send_string(self, text):
        """This sends a string to the player's connection protocol."""
        if self.protocol is None:
            logger.error("Trying to send string to player %s but player is not connected." % self.name)
            return

        if not text.endswith("<newline>"):
            text += "<newline>"
        self.protocol.send(text)
        if self.active:
            self.print_status_bar()

    ####################################################################
    def print_status_bar(self):
        status_bar = "<clearline><carriage_return><white><bold>["
        ratio = 100 * self.hit_points // self.attributes.MAX_HIT_POINTS
        if ratio < 33:
            status_bar += "<red>"
        elif ratio < 67:
            status_bar += "<yellow>"
        else:
            status_bar += "<green>"
        status_bar += "{hit_points}<white>/{max_hit_points}] <reset>".format(hit_points=self.hit_points,
                                                                             max_hit_points=self.attributes.MAX_HIT_POINTS)
        self.protocol.send(status_bar)

    ####################################################################
    def who_text(self):
        """Return a string describing the player"""
        text = [" {:<17}| {:<10}| ".format(self.name, self.level)]
        if self.active:
            text.append("<green>Online  <white>")
        elif self.logged_in:
            text.append("<yellow>Inactive<white>")
        else:
            text.append("<red>Offline <white>")

        text.append(" | ")
        if self.rank == PlayerRank.REGULAR:
            text.append("<white>")
        elif self.rank == PlayerRank.ADMIN:
            text.append("<green>")
        else:
            text.append("<yellow>")
        text.append(self.rank.name)
        text.append("<white>\r\n")
        return "".join(text)

    ####################################################################
    def killed(self):
        self.room.send_room("<red><bold>{} has died!".format(self.name))
        money = self.money // 10
        # calculate how much money to drop
        if money > 0:
            self.room.money += money
            self.money -= money
            self.room.send_room("<cyan>${} drops to the ground.".format(money))
        if self.inventory:
            some_item = random.choice(self.inventory)
            self.drop_item(some_item)
            self.room.add_item(some_item)
            self.room.send_room("<cyan>{} drops to the ground.".format(some_item.name))

        exp = self.experience // 10
        self.experience -= exp  # subtract 10% of player experience
        self.room.remove_player(self)
        self.room = room.room_database.by_id[1]
        self.room.add_player(self)

        # set player HP to 70%
        self.set_hit_points(int(self.attributes.MAX_HIT_POINTS * 0.7))

        self.send_string("<white><bold>You have died, but you have resurrected in %s" % self.room.name)
        self.send_string("<red><bold>You have lost %s experience!" % exp)
        self.room.send_room("<white><bold>%s appears out of nowhere!!" % self.name)

    ####################################################################
    def attack(self, enemy_name):
        # check if the player can attack yet
        if self.next_attack_time > 0:
            self.send_string("<red><bold>You can't attack yet!")
            return
        if enemy_name is None:
            # If there are no enemies to attack, tell the player
            if not self.room.enemies:
                self.send_string("<red><bold>You don't see anything to attack here!")
                return
            e = random.choice(list(self.room.enemies))
        else:
            e = self.room.find_enemy(enemy_name)
            # if we can't find the enemy, tell the player
            if e is None:
                self.send_string("<red><bold>You don't see that here!")
                return

        if e.id not in enemy.enemy_database.by_id:
            message = "Cannot find enemy %s(%s) of template %s in room %s(%s)" % (e.name, e.id, e.template.id, self.room.name, self.room.id)
            logger.error(message)
            self.send_string("<red><bold>" + message)
            return

        if self.weapon is None:  # fists, 1-3 damage, 1 second swing time
            damage = random.randint(1, 3)
            self.next_attack_time = 1
        else:
            damage = random.randint(self.weapon.min, self.weapon.max)
            self.next_attack_time = self.weapon.speed

        if random.randint(0, 99) >= (self.attributes.ACCURACY - e.dodging):
            self.room.send_room("<white>{} swings at {} but misses!".format(self.name, e.name))
            return
        damage += self.attributes.STRIKE_DAMAGE
        damage -= e.damage_absorb
        if damage < 1:
            damage = 1

        e.add_hit_points(-damage)
        self.room.send_room("<red>{} hits {} for {} damage!".format(self.name, e.name, damage))
        if e.hit_points <= 0:
            e.killed(self)


########################################################################
class PlayerDatabase(EntityDatabase):
    ####################################################################
    def all_logged_in(self):
        for player in self.all():
            if player.logged_in:
                yield player

    ####################################################################
    def all_active(self):
        for player in self.all():
            if player.active:
                yield player

    ####################################################################
    def add_player(self, player):
        if self.has(player.id):
            return False
        if self.has_full(player.name):
            return False
        self.by_id[player.id] = player
        self.by_name[player.name.lower()] = player
        self.save()
        return True

    ####################################################################
    def find_active(self, name):
        players = [player for player in self.by_id.values() if player.active]
        return double_find_by_name(name, players)

    ####################################################################
    def find_logged_in(self, name):
        players = [player for player in self.by_id.values() if player.logged_in]
        return double_find_by_name(name, players)

    ####################################################################
    def logout(self, player_id):
        player = self[player_id]
        logger.info("%s - User %s logged off", player.get_remote_address(), player.name)
        if player.protocol and player.protocol.closed is False:
            player.protocol.drop_connection()
        player.protocol = None
        player.logged_in = False
        player.active = False
        self.save()
