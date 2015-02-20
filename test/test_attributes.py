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
    def test_setting(self):
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

    ####################################################################
    def test_serialize_to_dict(self):
        attr_set = AttributeSet()
        attr_set[Attributes.STRENGTH] = 1
        attr_set[Attributes.HEALTH] = 3
        attr_set[Attributes.STRIKE_DAMAGE] = 5
        attr_set[Attributes.HP_REGEN] = 7
        serialized = attr_set.serialize_to_dict()
        expected = {"ACCURACY": 0,
                    "AGILITY": 0,
                    "DAMAGE_ABSORB": 0,
                    "DODGING": 0,
                    "HEALTH": 3,
                    "HP_REGEN": 7,
                    "MAX_HIT_POINTS": 0,
                    "STRENGTH": 1,
                    "STRIKE_DAMAGE": 5}
        self.assertEqual(expected, serialized)

    ####################################################################
    def test_deserialize_from_dict(self):
        data = {"ACCURACY": 0,
                "AGILITY": 0,
                "DAMAGE_ABSORB": 0,
                "DODGING": 0,
                "HEALTH": 3,
                "HP_REGEN": 7,
                "MAX_HIT_POINTS": 0,
                "STRENGTH": 1,
                "STRIKE_DAMAGE": 5}
        attr_set = AttributeSet.deserialize_from_dict(data)
        self.assertEqual(attr_set[Attributes.ACCURACY], 0)
        self.assertEqual(attr_set[Attributes.STRENGTH], 1)
        self.assertEqual(attr_set[Attributes.HEALTH], 3)
        self.assertEqual(attr_set[Attributes.STRIKE_DAMAGE], 5)
        self.assertEqual(attr_set[Attributes.HP_REGEN], 7)
        self.assertEqual(attr_set[Attributes.DAMAGE_ABSORB], 0)

        self.assertEqual(attr_set.ACCURACY, 0)
        self.assertEqual(attr_set.STRENGTH, 1)
        self.assertEqual(attr_set.HEALTH, 3)
        self.assertEqual(attr_set.STRIKE_DAMAGE, 5)
        self.assertEqual(attr_set.HP_REGEN, 7)
        self.assertEqual(attr_set.DAMAGE_ABSORB, 0)
