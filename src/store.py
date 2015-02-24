import os
import json
from entity import Entity
from entity_database import EntityDatabase

base = os.path.dirname(__file__)
store_database = None


########################################################################
class Store(Entity):
    ####################################################################
    def __init__(self):
        super(Store, self).__init__()
        self.available_items = []

    ####################################################################
    def has(self, item_id):
        for id in self.available_items:
            if id == item_id:
                return True
        return False

    ####################################################################
    @staticmethod
    def deserialize_from_dict(store_data):
        store = Store()
        for field, value in store_data.items():
            setattr(store, field, value)
        return store


########################################################################
class StoreDatabase(EntityDatabase):
    store_path = os.path.join(base, "..", "data", "stores.json")

    ####################################################################
    @classmethod
    def load(cls, store_path=None, force=False):
        global store_database
        if store_database is None or force:
            store_database = StoreDatabase()
            if store_path is None:
                store_path = cls.store_path

            store_data_list = json.load(open(store_path))
            for store_data in store_data_list:
                store = Store.deserialize_from_dict(store_data)
                store_database.by_id[store.id] = store
                store_database.by_name[store.name.lower()] = store
        return store_database

StoreDatabase.load()
