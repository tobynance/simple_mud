import os
import json
from enum import Enum
from attributes import AttributeSet
from entity import Entity
from entity_database import EntityDatabase

ItemType = Enum("ItemType", "WEAPON ARMOR HEALING")

base = os.path.dirname(__file__)
data_file = os.path.join(base, "..", "data", "items.json")

item_database = None


########################################################################
class Item(Entity):
    ####################################################################
    def __init__(self):
        super(Item, self).__init__()
        self.type = ItemType.ARMOR
        self.min = 0
        self.max = 0
        self.speed = 0
        self.price = 0
        self.attributes = AttributeSet()

    ####################################################################
    @staticmethod
    def deserialize_from_dict(item_data):
        item = Item()
        for field, value in item_data.items():
            if field in ["id", "name", "min", "max", "speed", "price"]:
                setattr(item, field, value)
            elif field == "type":
                item.type = getattr(ItemType, value)
            else:
                setattr(item.attributes, field, value)
        return item


########################################################################
class ItemDatabase(EntityDatabase):
    ####################################################################
    def __init__(self):
        super(ItemDatabase, self).__init__()
        global item_database
        item_database = self

    ####################################################################
    @staticmethod
    def load(force=False):
        global item_database
        if item_database is None or force:
            item_database = ItemDatabase()
            items_data = json.load(open(data_file))
            for item_data in items_data:
                item = Item.deserialize_from_dict(item_data)
                item_database.by_id[item.id] = item
                item_database.by_name[item.name.lower()] = item
        return item_database

ItemDatabase.load()
