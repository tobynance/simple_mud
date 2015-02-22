import os
import time
import math
import logging
import json
from enum import Enum
from attributes import PlayerRank, Attributes, primary_attribute_list, attribute_string_list
from entity import Entity
from entity_database import EntityDatabase
from item import ItemDatabase
from utils import clamp, double_find_by_name

base = os.path.dirname(__file__)
data_file = os.path.join(base, "..", "data", "players.json")

MAX_PLAYER_ITEMS = 16
logger = logging.getLogger(__name__)

SIMPLE_FIELDS = ["name", "password", "stat_points", "experience", "level", "room", "money", "next_attack_time"]

player_attribute_strings = []
for attr in attribute_string_list:
    player_attribute_strings.append("BASE_" + attr)
    player_attribute_strings.append("MODIFIER_" + attr)
    player_attribute_strings.append(attr)

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

    ####################################################################
    def serialize_to_dict(self):
        return {key.name: value for key, value in self.items() if key.name.startswith("BASE_")}

    ####################################################################
    @staticmethod
    def deserialize_from_dict(data_dict, player=None):
        attr_set = PlayerAttributeSet()
        attr_set.recalculating = True
        attr_set.player = player

        for key, value in data_dict.items():
            if key not in attribute_string_list:
                attr_set[PlayerAttributes[key]] = value
        attr_set.recalculating = False
        attr_set.recalculate_stats()
        return attr_set


########################################################################
class Player(Entity):
    ####################################################################
    def __init__(self, player_id=None):
        super(Player, self).__init__()
        self.id = player_id or PlayerDatabase.get_next_id()
        self.password = "UNDEFINED"
        self.rank = PlayerRank.REGULAR
        self.stat_points = 18
        self.experience = 0
        self.level = 1
        self.room = 0
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
    def able_to_attack(self):
        now = time.clock()
        return now >= self.next_attack_time

    ####################################################################
    def raise_level(self):
        raise NotImplementedError

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
    def add_to_base_attr(self, attr, val):
        raise NotImplementedError

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
        # print "status_bar:", status_bar
        self.protocol.send(status_bar)

    ####################################################################
    def serialize_to_dict(self):
        output = {"id": self.id}
        for field in SIMPLE_FIELDS:
            output[field] = getattr(self, field)
        output["rank"] = self.rank.value
        output["attributes"] = self.attributes.serialize_to_dict()
        output["inventory"] = [item.id for item in self.inventory]

        if self.weapon:
            output["weapon"] = self.weapon.id
        else:
            output["weapon"] = None

        if self.armor:
            output["armor"] = self.armor.id
        else:
            output["armor"] = None
        return output

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
    @staticmethod
    def deserialize(string_data):
        return Player.deserialize_from_dict(json.loads(string_data))

    ####################################################################
    @staticmethod
    def deserialize_from_dict(data_dict):
        player = Player(data_dict["id"])
        for field in SIMPLE_FIELDS:
            setattr(player, field, data_dict[field])

        item_db = ItemDatabase.load()

        player.rank = PlayerRank(data_dict["rank"])

        player.attributes = PlayerAttributeSet.deserialize_from_dict(data_dict["attributes"])
        player.inventory = []
        for item_id in data_dict["inventory"]:
            player.inventory.append(item_db[item_id])
        if data_dict["weapon"]:
            player.weapon = item_db[data_dict["weapon"]]
        if data_dict["armor"]:
            player.weapon = item_db[data_dict["armor"]]
        player.attributes.set_player(player)
        return player


########################################################################
class PlayerDatabase(EntityDatabase):
    ####################################################################
    def __init__(self):
        super(PlayerDatabase, self).__init__()
        global player_database
        player_database = self

    ####################################################################
    @staticmethod
    def load(path=None, force=False):
        global player_database
        if player_database is None or force:
            if path is None:
                path = data_file
            player_database = PlayerDatabase()
            if os.environ.get("SIMPLE_MUD_LOAD_PLAYERS", "true") == "true" and os.path.exists(path):
                player_database.load_from_string(open(path).read())
        return player_database

    ####################################################################
    def load_from_string(self, text):
        players_data = json.loads(text)
        for player_data in players_data:
            player = Player.deserialize_from_dict(player_data)
            self.by_id[player.id] = player
            self.by_name[player.name.lower()] = player

    ####################################################################
    @classmethod
    def get_next_id(cls):
        return len(player_database.by_id) + 1

    ####################################################################
    def all(self):
        return self.by_id.values()

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
    def save(self, path=None):
        if path is None:
            path = data_file
        player_text = self.save_to_string()
        if os.environ.get("SIMPLE_MUD_LOAD_PLAYERS", "true") == "true":
            with open(path, "w") as out_file:
                out_file.write(player_text)

    ####################################################################
    def save_to_string(self):
        players = []
        for player in self.by_id.values():
            players.append(player.serialize_to_dict())
        player_text = json.dumps(players, indent=4)
        return player_text

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

player_database = PlayerDatabase.load()
