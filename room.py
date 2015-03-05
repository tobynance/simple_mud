import os
import logging
import json
from enum import Enum
from attributes import Direction
from entity import Entity
from entity_database import EntityDatabase
from item import ItemDatabase
import utils

logger = logging.getLogger(__name__)

base = os.path.dirname(__file__)

RoomType = Enum("RoomType", "PLAIN_ROOM TRAINING_ROOM STORE")
MAX_ITEMS = 32

room_database = None


########################################################################
class Room(Entity):
    ####################################################################
    def __init__(self):
        super(Room, self).__init__()
        self.type = RoomType.PLAIN_ROOM
        self.description = ""
        self.connecting_rooms = {}
        self.spawn_which_enemy = None
        self.max_enemies = 0
        self.data = None

        # volatile data
        self.items = []
        self.money = 0
        self.players = set()  # not serialized
        self.enemies = set()  # not serialized

    ####################################################################
    def get_adjacent_room(self, direction):
        room_id = self.connecting_rooms.get(direction)
        if room_id:
            return room_database.by_id[room_id]

    ####################################################################
    def add_player(self, player):
        self.players.add(player)

    ####################################################################
    def remove_player(self, player):
        self.players.remove(player)

    ####################################################################
    def find_item(self, item_name):
        return utils.double_find_by_name(item_name, self.items)

    ####################################################################
    def add_item(self, item):
        while len(self.items) >= MAX_ITEMS:
            self.items.pop(0)
        self.items.append(item)

    ####################################################################
    def remove_item(self, item):
        self.items.remove(item)

    ####################################################################
    def find_enemy(self, enemy_name):
        return utils.double_find_by_name(enemy_name, self.enemies)

    ####################################################################
    def add_enemy(self, enemy):
        self.enemies.add(enemy)

    ####################################################################
    def remove_enemy(self, enemy):
        self.enemies.remove(enemy)

    ####################################################################
    def send_room(self, text):
        for player in self.players:
            player.send_string(text)
