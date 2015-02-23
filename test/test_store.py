import unittest
from attributes import Direction
import item
import player
from store import Store, StoreDatabase
import store


########################################################################
class RoomTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        self.store = Store()
        self.store.id = 3
        self.store.name = "Walmart Grocery"
        self.store.available_items = [40, 43, 45, 47]

    ####################################################################
    def test_deserialize_from_dict(self):
        store_data = {
            "id": 5,
            "name": "Sea Shanty",
            "available_items": [69, 70, 71, 72]}

        this_store = Store.deserialize_from_dict(store_data)
        self.assertEqual(this_store.id, 5)
        self.assertEqual(this_store.name, "Sea Shanty")
        self.assertEqual(this_store.available_items, [69, 70, 71, 72])

    ####################################################################
    def test_load(self):
        self.assertEqual(store.store_database.find(5).name, "Sea Shanty")
