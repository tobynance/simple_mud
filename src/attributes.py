from enum import Enum

ItemType = Enum("ItemType", "WEAPON ARMOR HEALING SPECIAL")

PlayerRank = Enum("PlayerRank", "REGULAR WARRIOR MAGE ARCHER ADMIN")

RoomType = Enum("RoomType", "PLAINROOM CENTRAL SAVEROOM STORE LOCKEDROOM")

Area = Enum("Area", "METROPOLIS MOUNTAIN FOREST")


########################################################################
class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    ####################################################################
    def opposite_direction(self):
        return Direction((self.value + 2) % 4)


########################################################################
Attributes = Enum("Attributes", "STRENGTH HEALTH AGILITY MAX_HIT_POINTS "
                                "ACCURACY DODGING STRIKE_DAMAGE DAMAGE_ABSORB HP_REGEN")


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
            item = getattr(Attributes, item)
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
