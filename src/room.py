import os
import json
from enum import Enum
from attributes import Direction
from entity import Entity
from entity_database import EntityDatabase
from item import ItemDatabase
import utils

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

        # volatile data
        self.items = []
        self.money = 0
        self.players = set()  # not serialized
        self.enemies = set()  # not serialized

    ####################################################################
    @staticmethod
    def deserialize_from_dict(room_template_data, room_volatile_data):
        item_db = ItemDatabase.load()
        room = Room()
        for field, value in room_template_data.items():
            if field in ["id", "name", "description", "max_enemies"]:
                setattr(room, field, value)
            elif field == "type":
                room.type = getattr(RoomType, value)
            elif field == "spawn_which_enemy":
                if value:
                    room.spawn_which_enemy = value
            elif field == "north":
                if value:
                    room.connecting_rooms[Direction.NORTH] = value
            elif field == "south":
                if value:
                    room.connecting_rooms[Direction.SOUTH] = value
            elif field == "east":
                if value:
                    room.connecting_rooms[Direction.EAST] = value
            elif field == "west":
                if value:
                    room.connecting_rooms[Direction.WEST] = value
            elif field == "data":
                pass  # TODO: Not implemented yet
            elif field == "starting_items":
                for item_id in value:
                    item = item_db.find(item_id)
                    room.items.append(item)
            elif field == "starting_money":
                room.money = value

        if room_volatile_data:
            for field, value in room_volatile_data.items():
                if field == "items":
                    room.items = []
                    for item_id in value:
                        item = item_db.find(item_id)
                        room.items.append(item)
                elif field == "money":
                    room.money = value
        return room

    ####################################################################
    def serialize_to_dict(self):
        output = {"items": [], "money": self.money}
        for item in self.items:
            output["items"].append(item.id)
        return output

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


########################################################################
class RoomDatabase(EntityDatabase):
    room_data_path = os.path.join(base, "..", "data", "room_data.json")
    room_templates_path = os.path.join(base, "..", "data", "room_templates.json")

    ####################################################################
    def save(self, room_data_path=None):
        if room_data_path is None:
            room_data_path = self.room_data_path
        room_data = {room.id: room.serialize_to_dict() for room in self.by_id.values()}
        with open(room_data_path, "w") as out_file:
            json.dump(room_data, out_file, indent=4, sort_keys=True)

    ####################################################################
    @classmethod
    def load(cls, room_data_path=None, room_templates_path=None, force=False):
        global room_database
        if room_database is None or force:
            room_database = RoomDatabase()
            if room_data_path is None:
                room_data_path = cls.room_data_path
            if room_templates_path is None:
                room_templates_path = cls.room_templates_path

            template_data = json.load(open(room_templates_path))
            if os.path.exists(room_data_path):
                room_data = json.load(open(room_data_path))
            else:
                room_data = {}
            for room_template_data in template_data:
                room = Room.deserialize_from_dict(room_template_data, room_data.get(room_template_data["id"]))
                room_database.by_id[room.id] = room
                room_database.by_name[room.name.lower()] = room
            return room_database

room_database = RoomDatabase.load()
