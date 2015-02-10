import unittest
from attributes import AttributeSet, Attributes, PlayerRank
from item import Item, ItemDatabase
from player import Player, PlayerDatabase


########################################################################
class PlayerTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        self.player = Player()
        self.player.name = "jerry_john"
        self.player.attributes.AGILITY = 3
        self.player.attributes.MAX_HIT_POINTS = 12
        self.player.attributes.STRIKE_DAMAGE = 2

        self.player_data = {"armor": None,
                            "attributes": {1: 0, 2: 0, 3: 3, 4: 12, 5: 0, 6: 0, 7: 2, 8: 0, 9: 1},
                            "base_attributes": {1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                            "experience": 0,
                            "inventory": [],
                            "level": 1,
                            "money": 0,
                            "name": "jerry_john",
                            "next_attack_time": 0,
                            "password": "UNDEFINED",
                            "rank": 1,
                            "room": 0,
                            "stat_points": 18,
                            "weapon": None}

    ####################################################################
    def test_serialize_to_dict(self):
        player_data = self.player.serialize_to_dict()
        self.assertEqual(self.player_data, player_data)

    ####################################################################
    def test_deserialize_from_dict(self):
        player = Player.deserialize_from_dict(self.player_data)

        self.assertEqual(item.id, 1)
        self.assertEqual(item.name, "LIES!!!@~")
        self.assertEqual(item.type, ItemType.HEALING)
        self.assertEqual(item.min, 0)
        self.assertEqual(item.max, 0)
        self.assertEqual(item.price, 1)
        self.assertEqual(item.speed, 0)
        self.assertEqual(item.attributes.STRENGTH, 0)
        self.assertEqual(item.attributes.HEALTH, 0)
        self.assertEqual(item.attributes.AGILITY, 0)
        self.assertEqual(item.attributes.MAX_HIT_POINTS, 0)
        self.assertEqual(item.attributes.ACCURACY, 0)
        self.assertEqual(item.attributes.DODGING, 0)
        self.assertEqual(item.attributes.STRIKE_DAMAGE, 0)
        self.assertEqual(item.attributes.DAMAGE_ABSORB, 0)
        self.assertEqual(item.attributes.HP_REGEN, 0)

        item_data = {"id": 55,
                     "name": "Platemail Armor of Power",
                     "type": "ARMOR",
                     "min": 0,
                     "max": 0,
                     "speed": 0,
                     "price": 15000,
                     "STRENGTH": 0,
                     "HEALTH": 0,
                     "AGILITY": 0,
                     "MAX_HIT_POINTS": 0,
                     "ACCURACY": 10,
                     "DODGING": 60,
                     "STRIKE_DAMAGE": 10,
                     "DAMAGE_ABSORB": 5,
                     "HP_REGEN": 0}

        item = Item.deserialize_from_dict(item_data)
        self.assertEqual(item.id, 55)
        self.assertEqual(item.name, "Platemail Armor of Power")
        self.assertEqual(item.type, ItemType.ARMOR)
        self.assertEqual(item.min, 0)
        self.assertEqual(item.max, 0)
        self.assertEqual(item.price, 15000)
        self.assertEqual(item.speed, 0)
        self.assertEqual(item.attributes.STRENGTH, 0)
        self.assertEqual(item.attributes.HEALTH, 0)
        self.assertEqual(item.attributes.AGILITY, 0)
        self.assertEqual(item.attributes.MAX_HIT_POINTS, 0)
        self.assertEqual(item.attributes.ACCURACY, 10)
        self.assertEqual(item.attributes.DODGING, 60)
        self.assertEqual(item.attributes.STRIKE_DAMAGE, 10)
        self.assertEqual(item.attributes.DAMAGE_ABSORB, 5)
        self.assertEqual(item.attributes.HP_REGEN, 0)
