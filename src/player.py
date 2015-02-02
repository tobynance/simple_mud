import time
from attributes import PlayerRank, Attributes
from entity import Entity


class Player(Entity):
    ####################################################################
    def __init__(self):
        self.password = "UNDEFINED"
        self.rank = PlayerRank.REGULAR
        self.stat_points = 18
        self.experience = 0
        self.level = 1
        self.room = 1
        self.money = 0
        self.next_attack_time = 0
        self.base_attributes = {}
        self.base_attributes[Attributes.STRENGTH] = 1
        self.base_attributes[Attributes.HEALTH] = 1
        self.base_attributes[Attributes.AGILITY] = 1

        self.items = 0
        self.weapon = -1
        self.armor = -1
        self.recalculate_stats()
        self.hit_points = self.attributes.MAX_HIT_POINTS

    ####################################################################
    def able_to_attack(self):
        now = time.clock()
        return now >= self.next_attack_time

    ####################################################################
    def raise_level(self):
        raise NotImplementedError

    ####################################################################
    def need_for_next_level(self):
        raise NotImplementedError

    ####################################################################
    def train(self):
        raise NotImplementedError

    ####################################################################
    def recalculate_stats(self):
        raise NotImplementedError

    ####################################################################
    def add_dynamic_bonuses(self, item):
        raise NotImplementedError

    ####################################################################
    def set_base_attr(self, attr, val):
        raise NotImplementedError

    ####################################################################
    def add_to_base_attr(self, attr, val):
        raise NotImplementedError

    ####################################################################
    def add_hit_points(self, hit_points):
        raise NotImplementedError

    ####################################################################
    def set_hit_points(self, hit_points):
        raise NotImplementedError

    ####################################################################
    def pick_up_item(self, item):
        raise NotImplementedError

    ####################################################################
    def drop_item(self, index):
        raise NotImplementedError

    ####################################################################
    def add_bonuses(self, item):
        raise NotImplementedError

    ####################################################################
    def remove_weapon(self):
        raise NotImplementedError

    ####################################################################
    def remove_armor(self):
        raise NotImplementedError

    ####################################################################
    def use_weapon(self, index):
        raise NotImplementedError

    ####################################################################
    def use_armor(self, index):
        raise NotImplementedError

    ####################################################################
    def get_item_index(self, name):
        """This gets the index of an item within the player's inventory given a name."""
        raise NotImplementedError

    ####################################################################
    def send_string(self, text):
        """This sends a string to the player's connection."""
        raise NotImplementedError

    ####################################################################
    def print_stat_bar(self, update):
        """This prints the player's "statbar", ie: their hitpoints."""
        raise NotImplementedError

    ####################################################################
    def serialize(self):
        raise NotImplementedError

    ####################################################################
    def deserialize(self):
        raise NotImplementedError
