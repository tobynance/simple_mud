from enum import Enum, IntEnum


########################################################################
class Direction(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    ####################################################################
    def opposite_direction(self):
        return Direction((self.value + 2) % 4)


attribute_string = "STRENGTH HEALTH AGILITY MAX_HIT_POINTS ACCURACY DODGING STRIKE_DAMAGE DAMAGE_ABSORB HP_REGEN"
attribute_string_list = attribute_string.split()
primary_attribute_list = ["STRENGTH", "HEALTH", "AGILITY"]
secondary_attribute_list = ["MAX_HIT_POINTS", "ACCURACY", "DODGING", "STRIKE_DAMAGE", "DAMAGE_ABSORB", "HP_REGEN"]

Attributes = Enum("Attributes", attribute_string)


########################################################################
class AttributeSet(dict):
    ####################################################################
    def __init__(self):
        super(AttributeSet, self).__init__()
        for attr in Attributes:
            self[attr] = 0

    ####################################################################
    def __get_attribute(self, item):
        if isinstance(item, basestring):
            item = Attributes[item]
        elif isinstance(item, int):
            item = Attributes(item)
        return item

    ####################################################################
    def __getitem__(self, item):
        item = self.__get_attribute(item)
        return super(AttributeSet, self).__getitem__(item)

    ####################################################################
    def __setitem__(self, key, value):
        item = self.__get_attribute(key)
        return super(AttributeSet, self).__setitem__(item, value)

    ####################################################################
    def __getattr__(self, name):
        return self[name]

    ####################################################################
    def __setattr__(self, name, value):
        self[name] = value

    ####################################################################
    def serialize_to_dict(self):
        return {key.name: value for key, value in self.items()}

    ####################################################################
    @staticmethod
    def deserialize_from_dict(data_dict):
        attr_set = AttributeSet()
        for key, value in data_dict.items():
            attr_set[Attributes[key]] = value
        return attr_set
