import os
import json
from enum import Enum
from attributes import ItemType, Direction
from entity import Entity
from item import ItemDatabase
import utils

base = os.path.dirname(__file__)
data_file = os.path.join(base, "..", "data", "items.json")

RoomType = Enum("RoomType", "PLAIN_ROOM TRAINING_ROOM STORE")
MAX_ITEMS = 32


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

        # volatile data
        self.items = []
        self.money = 0
        self.players = set()  # not serialized
        self.enemies = set()  # not serialized

    ####################################################################
    @staticmethod
    def deserialize_from_dict(room_template_data, room_volatile_data):
        room = Room()
        for field, value in room_template_data.items():
            if field in ["id", "name", "description", "spawn_which_enemy", "max_enemies"]:
                setattr(room, field, value)
            elif field == "type":
                room.type = getattr(RoomType, value)
            elif field == "north":
                if value:
                    room.connecting_rooms[Direction.NORTH] = value
            elif field == "south":
                if value:
                    room.connecting_rooms[Direction.NORTH] = value
            elif field == "east":
                if value:
                    room.connecting_rooms[Direction.NORTH] = value
            elif field == "west":
                if value:
                    room.connecting_rooms[Direction.NORTH] = value
            elif field == "data":
                pass  # TODO: Not implemented yet

        for field, value in room_volatile_data.items():
            if field == "items":
                item_db = ItemDatabase.load()
                for item_id in value:
                    item = item_db.find(item_id)
                    room.items.append(item)
            elif field == "money":
                room.money = value
        return room

    ####################################################################
    def serialize_to_dict(self):
        raise NotImplementedError

    ####################################################################
    def get_adjacent_room(self, direction):
        return self.connecting_rooms.get(direction)

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
    def load_template(self, data):
        raise NotImplementedError
#
#
# out_file = open("room_templates.json", "w")
#
# def convert_line(line):
#     if line.startswith("["):
#         tag, value = line[1:].split("]", 1)
#         if tag == "ID":
#             text = '{\n  "%s": %s,\n'
#         elif tag == "MAXENEMIES":
#             text = '  "%s": %s\n},\n'
#         elif tag in ["DATA", "NORTH", "EAST", "SOUTH", "WEST", "ENEMY"]:
#             text = '  "%s": %s,\n'
#         else:
#             text = '  "%s": "%s",\n'
#         out_file.write(text % (tag.lower(), value.strip()))
#     else:
#         out_file.write("\n")
#
#
# for line in lines:
#     convert_line(line)
#
# out_file.close()
