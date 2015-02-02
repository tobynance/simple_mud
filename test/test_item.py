import unittest
from attributes import AttributeSet, Attributes, ItemType
from item import Item, ItemDatabase


########################################################################
class ItemTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        self.item = Item()
        self.item.type = ItemType.HEALING
        self.item.id = 3
        self.item.max = 10
        self.item.min = 4
        self.item.price = 500
        self.item.speed = 2
        self.item.attributes.AGILITY = 3
        self.item.attributes.MAX_HIT_POINTS = 12
        self.item.attributes.STRIKE_DAMAGE = 2

    ####################################################################
    def test_saving(self):
        self.attr_set = AttributeSet()
        self.attr_set[Attributes.STRENGTH] = 1
        self.attr_set[Attributes.HEALTH] = 3
        self.attr_set[Attributes.STRIKE_DAMAGE] = 5
        self.attr_set[Attributes.HP_REGEN] = 7

        self.assertEqual(self.attr_set[Attributes.STRENGTH], 1)
        self.assertEqual(self.attr_set[Attributes.HEALTH], 3)
        self.assertEqual(self.attr_set[Attributes.STRIKE_DAMAGE], 5)
        self.assertEqual(self.attr_set[Attributes.HP_REGEN], 7)
        self.assertEqual(self.attr_set[Attributes.DAMAGE_ABSORB], 0)

    ####################################################################
    def test_loading(self):
        items = Item.load_data()
        self.assertEqual(len(items), 72)
        item = items[0]
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

        item = items[54]
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


########################################################################
class ItemDatabaseTest(unittest.TestCase):
    ####################################################################
    def test_load(self):
        item_database = ItemDatabase.load()
        self.assertEqual(item_database, ItemDatabase.db)
        ItemDatabase.load()
        self.assertEqual(item_database, ItemDatabase.db)
        self.assertEqual(len(item_database.by_id), 72)
        self.assertEqual(len(item_database.by_name), 72)

        self.assertEqual(item_database.find(40).name, "Rusty Knife")
        self.assertEqual(item_database.find_full("Dagger").id, 42)
        self.assertEqual(item_database.find("Rusty").id, 40)
        self.assertEqual(item_database.find("Short").id, 2)
