import unittest
from attributes import AttributeSet, Attributes


########################################################################
class AttributeSetTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        self.attr_set = AttributeSet()
        self.attr_set[Attributes.STRENGTH] = 1
        self.attr_set[Attributes.HEALTH] = 3
        self.attr_set[Attributes.STRIKE_DAMAGE] = 5
        self.attr_set[Attributes.HP_REGEN] = 7

    ####################################################################
    def test_use_enum_for_key(self):
        self.assertEqual(self.attr_set[Attributes.STRENGTH], 1)
        self.assertEqual(self.attr_set[Attributes.HEALTH], 3)
        self.assertEqual(self.attr_set[Attributes.STRIKE_DAMAGE], 5)
        self.assertEqual(self.attr_set[Attributes.HP_REGEN], 7)
        self.assertEqual(self.attr_set[Attributes.DAMAGE_ABSORB], 0)

    ####################################################################
    def test_use_int_for_key(self):
        self.assertEqual(self.attr_set[Attributes.STRENGTH.value], 1)
        self.assertEqual(self.attr_set[Attributes.HEALTH.value], 3)
        self.assertEqual(self.attr_set[Attributes.STRIKE_DAMAGE.value], 5)
        self.assertEqual(self.attr_set[Attributes.HP_REGEN.value], 7)
        self.assertEqual(self.attr_set[Attributes.DAMAGE_ABSORB.value], 0)

    ####################################################################
    def test_use_string_for_key(self):
        self.assertEqual(self.attr_set[Attributes.STRENGTH.name], 1)
        self.assertEqual(self.attr_set[Attributes.HEALTH.name], 3)
        self.assertEqual(self.attr_set[Attributes.STRIKE_DAMAGE.name], 5)
        self.assertEqual(self.attr_set[Attributes.HP_REGEN.name], 7)
        self.assertEqual(self.attr_set[Attributes.DAMAGE_ABSORB.name], 0)

    ####################################################################
    def test_use_attributes_directly(self):
        self.assertEqual(self.attr_set.STRENGTH, 1)
        self.assertEqual(self.attr_set.HEALTH, 3)

        self.attr_set.HEALTH = 17
        self.assertEqual(self.attr_set.HEALTH, 17)
        self.assertEqual(self.attr_set[Attributes.HEALTH.name], 17)
        self.assertEqual(self.attr_set[Attributes.HEALTH.value], 17)
        self.assertEqual(self.attr_set[Attributes.HEALTH], 17)

    ####################################################################
    def test_saving(self):
        attr_set = AttributeSet()
        attr_set[Attributes.STRENGTH] = 1
        attr_set[Attributes.HEALTH] = 3
        attr_set[Attributes.STRIKE_DAMAGE] = 5
        attr_set[Attributes.HP_REGEN] = 7

        self.assertEqual(attr_set[Attributes.STRENGTH], 1)
        self.assertEqual(attr_set[Attributes.HEALTH], 3)
        self.assertEqual(attr_set[Attributes.STRIKE_DAMAGE], 5)
        self.assertEqual(attr_set[Attributes.HP_REGEN], 7)
        self.assertEqual(attr_set[Attributes.DAMAGE_ABSORB], 0)
