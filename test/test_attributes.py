import unittest
from attributes import AttributeSet, Attributes, PlayerAttributeSet


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
        self.fail()

    ####################################################################
    def test_deserialize_from_dict(self):
        self.fail()


########################################################################
class PlayerAttributeSetTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        self.attr_set = PlayerAttributeSet()
        self.attr_set.BASE_AGILITY = 3
        self.attr_set.BASE_MAX_HIT_POINTS = 12
        self.attr_set.MODIFIER_STRIKE_DAMAGE = 2
        self.attr_set.MODIFIER_HEALTH = 11
        self.attr_set.MODIFIER_AGILITY = -8

    ####################################################################
    def test_recalculate_stats(self):
        self.fail()

    ####################################################################
    def test_set_field(self):
        self.fail()

    ####################################################################
    def test_add_dynamic_bonuses(self):
        self.fail()

    ####################################################################
    def test_set_base_attr(self):
        self.fail()

    ####################################################################
    def test_add_bonuses(self):
        self.fail()

    ####################################################################
    def test_serialize_to_dict(self):
        self.fail()

    ####################################################################
    def test_deserialize_from_dict(self):
        self.fail()

    ####################################################################
    def test_use_enum_for_key(self):
        self.fail()

    ####################################################################
    def test_use_int_for_key(self):
        self.fail()

    ####################################################################
    def test_use_string_for_key(self):
        self.fail()

    ####################################################################
    def test_use_attributes_directly(self):
        self.fail()

    ####################################################################
    def test_setting(self):
        self.fail()
