import unittest
from attributes import AttributeSet, Attributes, ItemType
from item import Item


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

