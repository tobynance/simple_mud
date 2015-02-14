from enum import Enum

ItemType = Enum("ItemType", "WEAPON ARMOR HEALING")

PlayerRank = Enum("PlayerRank", "REGULAR MODERATOR ADMIN")

RoomType = Enum("RoomType", "PLAIN_ROOM TRAINING_ROOM STORE")

LogonState = Enum("LogonState", "NEW_CONNECTION NEW_USER ENTER_NEW_PASSWORD ENTER_PASSWORD")


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
        return {key.value: value for key, value in self.items()}

    ####################################################################
    @staticmethod
    def deserialize_from_dict(data_dict):
        attr_set = AttributeSet()
        for key, value in data_dict.items():
            attr_set[Attributes(int(key))] = value
        return attr_set
