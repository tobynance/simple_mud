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
Attributes = Enum("Attributes", "STRENGTH HEALTH AGILITY MAXHITPOINTS "
                                "ACCURACY DODGING STRIKEDAMAGE DAMAGEABSORB HPREGEN")


########################################################################
class AttributeSet(list):
    ####################################################################
    def __init__(self):
        super(AttributeSet, self).__init__()
        for attr in Attributes:
            self.append(0)

    ####################################################################
    def __getitem__(self, item):
        if isinstance(item, Enum):
            return super(AttributeSet, self)[item.value]
        else:
            return super(AttributeSet, self)[item]
