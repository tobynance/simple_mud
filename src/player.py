import os
import time
import math
import logging
import json
from attributes import PlayerRank, PlayerAttributes, PlayerAttributeSet
from entity import Entity
from entity_database import EntityDatabase
from item import ItemDatabase
from utils import clamp, double_find_by_name
from telnet import green, white, yellow, red, newline, bold, clearline, reset

base = os.path.dirname(__file__)
data_file = os.path.join(base, "..", "data", "players.json")

MAX_PLAYER_ITEMS = 16
logger = logging.getLogger(__name__)

SIMPLE_FIELDS = ["name", "password", "stat_points", "experience", "level", "room", "money", "next_attack_time"]


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
        self.newbie = True
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
    def need_for_level(self, level):
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
    def set_base_attr(self, attr, val):
        self.attributes.set_base_attr(attr, val)

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

        text = str(text)
        # print "text:", text
        # print "text type:", type(text)
        self.protocol.send(text + newline)
        if self.active:
            self.print_status_bar()

    ####################################################################
    def print_status_bar(self):
        status_bar = clearline + "\r" + white + bold + "["
        ratio = 100 * self.hit_points // self.attributes.MAX_HIT_POINTS
        if ratio < 33:
            status_bar += red
        elif ratio < 67:
            status_bar += yellow
        else:
            status_bar += green
        status_bar += "{hit_points}{white}/{max_hit_points}] {reset}".format(hit_points=self.hit_points, white=white, max_hit_points=self.attributes.MAX_HIT_POINTS, reset=reset)
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
            text.append(green + "Online  " + white)
        elif self.logged_in:
            text.append(yellow + "Inactive" + white)
        else:
            text.append(red + "Offline " + white)

        text.append(" | ")
        if self.rank == PlayerRank.REGULAR:
            text.append(white)
        elif self.rank == PlayerRank.ADMIN:
            text.append(green)
        else:
            text.append(yellow)
        text.append(self.rank.name)
        text.append(white + "\r\n")
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
    db = None

    ####################################################################
    @staticmethod
    def load():
        if PlayerDatabase.db is None:
            db = PlayerDatabase()
            if os.path.exists(data_file):
                players_data = json.load(open(data_file))
            else:
                players_data = []
            for player_data in players_data:
                player = Player.deserialize_from_dict(player_data)
                db.by_id[player.id] = player
                db.by_name[player.name.lower()] = player
            PlayerDatabase.db = db
        return PlayerDatabase.db

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
    def save(self):
        players = []
        for player in self.by_id.values():
            players.append(player.serialize_to_dict())
        player_text = json.dumps(players, indent=4)
        with open(data_file, "w") as out_file:
            out_file.write(player_text)

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
