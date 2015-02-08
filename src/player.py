import os
import time
import math
import logging
import json
from attributes import PlayerRank, Attributes, AttributeSet
from entity import Entity
from entity_database import EntityDatabase
from item import ItemDatabase
from utils import clamp, double_find_by_name

base = os.path.dirname(__file__)
data_file = os.path.join(base, "..", "data", "players.json")

MAX_PLAYER_ITEMS = 16
logger = logging.getLogger(__name__)

SIMPLE_FIELDS = ["name", "password", "rank", "stat_points", "experience", "level", "room", "money", "next_attack_time"]


########################################################################
class Player(Entity):
    ####################################################################
    def __init__(self):
        super(Player, self).__init__()
        self.password = "UNDEFINED"
        self.rank = PlayerRank.REGULAR
        self.stat_points = 18
        self.experience = 0
        self.level = 1
        self.room = 0
        self.money = 0
        self.next_attack_time = 0
        self.base_attributes = AttributeSet()
        self.base_attributes[Attributes.STRENGTH] = 1
        self.base_attributes[Attributes.HEALTH] = 1
        self.base_attributes[Attributes.AGILITY] = 1

        self.inventory = []
        self.weapon = None
        self.armor = None
        self.hit_points = self.attributes.MAX_HIT_POINTS

        self.connection = None
        self.logged_in = None
        self.active = None
        self.newbie = None
        self.attributes = AttributeSet()

        self.recalculate_stats()

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
            self.base_attributes[Attributes.MAX_HIT_POINTS] += self.level
            self.level += 1
            self.recalculate_stats()
            return True
        return False

    ####################################################################
    def recalculate_stats(self):
        self.attributes.MAX_HIT_POINTS = int(10 + (self.level * self.attributes.HEALTH / 1.5))
        self.attributes.HP_REGEN = (self.attributes.HEALTH / 5) + self.level
        self.attributes.ACCURACY = self.attributes.AGILITY * 3
        self.attributes.DODGING = self.attributes.AGILITY * 3
        self.attributes.DAMAGE_ABSORB = self.attributes.STRENGTH / 5
        self.attributes.STRIKE_DAMAGE = self.attributes.STRENGTH / 5
        # make sure the hit points don't overflow if your max goes down
        if self.hit_points > self.attributes.MAX_HIT_POINTS:
            self.hit_points = self.attributes.MAX_HIT_POINTS

        if self.weapon:
            self.add_dynamic_bonuses(self.weapon)
        if self.armor:
            self.add_dynamic_bonuses(self.armor)

    ####################################################################
    def add_dynamic_bonuses(self, item):
        if item:
            for attr in Attributes:
                self.attributes[attr] += item.attributes[attr]
            self.recalculate_stats()

    ####################################################################
    def set_base_attr(self, attr, val):
        self.base_attributes[attr] = val
        self.recalculate_stats()

    ####################################################################
    def add_to_base_attr(self, attr, val):
        self.base_attributes[attr] += val
        self.recalculate_stats()

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
        if item:
            for attr in Attributes:
                self.base_attributes += item.attributes[attr]
            self.recalculate_stats()

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
        """This sends a string to the player's connection."""
        if self.connection is None:
            logger.error("Trying to send string to player %s but player is not connected." % self.name)
            return

        self.connection.protocol.send_string(text + "\n")
        if self.active:
            self.print_status_bar()

    ####################################################################
    def print_status_bar(self):
        raise NotImplementedError

    ####################################################################
    def serialize_to_dict(self):
        output = {}
        for field in SIMPLE_FIELDS:
            output[field] = getattr(self, field)
        output["base_attributes"] = self.base_attributes.serialize_to_dict()
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
    def serialize(self):
        return json.dumps(self.serialize_to_dict())

    ####################################################################
    @staticmethod
    def deserialize(string_data):
        return Player.deserialize_from_dict(json.loads(string_data))

    ####################################################################
    @staticmethod
    def deserialize_from_dict(data_dict):
        player = Player()
        for field in SIMPLE_FIELDS:
            setattr(player, field, data_dict[field])

        item_db = ItemDatabase.load()

        player.base_attributes = AttributeSet.deserialize_from_dict(data_dict["base_attributes"])
        player.attributes = AttributeSet.deserialize_from_dict(data_dict["attributes"])
        player.inventory = []
        for item_id in data_dict["inventory"]:
            player.inventory.append(item_db[item_id])
        if data_dict["weapon"]:
            player.weapon = item_db[data_dict["weapon"]]
        if data_dict["armor"]:
            player.weapon = item_db[data_dict["armor"]]
        return player


########################################################################
class PlayerDatabase(EntityDatabase):
    db = None

    ####################################################################
    @staticmethod
    def load():
        if PlayerDatabase.db is None:
            db = PlayerDatabase()
            players_data = json.load(open(data_file))
            for player_data in players_data:
                player = Player.deserialize_from_dict(player_data)
                db.by_id[player.id] = player
                db.by_name[player.name.lower()] = player
            PlayerDatabase.db = db
        return PlayerDatabase.db

    ####################################################################
    def save(self):
        players = []
        for player in self.by_id.values():
            players.append(player.serialize())
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
    def log_out(self, player_id):
        player = self[player_id]
        logger.info("%s - User %s logged off", player.connection.get_remote_address(), player.name)
        player.connection = None
        player.logged_in = False
        player.active = False
        self.save()
