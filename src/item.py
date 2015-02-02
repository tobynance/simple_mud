import os
import json
from attributes import ItemType, AttributeSet
from entity import Entity
from entity_database import EntityDatabase

base = os.path.dirname(__file__)
data_file = os.path.join(base, "..", "data", "items.json")


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
    def load_data():
        items_data = json.load(open(data_file))
        items = []
        for item_data in items_data:
            item = Item()
            items.append(item)
            for field, value in item_data.items():
                if field in ["id", "name", "min", "max", "speed", "price"]:
                    setattr(item, field, value)
                elif field == "type":
                    item.type = getattr(ItemType, value)
                else:
                    setattr(item.attributes, field, value)
        return items


########################################################################
class ItemDatabase(EntityDatabase):
    db = None

    ####################################################################
    @staticmethod
    def load():
        if ItemDatabase.db is None:
            items = Item.load_data()
            db = ItemDatabase()
            for item in items:
                db.by_id[item.id] = item
                db.by_name[item.name] = item
            ItemDatabase.db = db
        return ItemDatabase.db
