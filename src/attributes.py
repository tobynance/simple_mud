from enum import Enum, IntEnum

ItemType = Enum("ItemType", "WEAPON ARMOR HEALING")

PlayerRank = IntEnum("PlayerRank", "REGULAR MODERATOR ADMIN")

RoomType = Enum("RoomType", "PLAIN_ROOM TRAINING_ROOM STORE")


########################################################################
class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    ####################################################################
    def opposite_direction(self):
        return Direction((self.value + 2) % 4)


attribute_string = "STRENGTH HEALTH AGILITY MAX_HIT_POINTS ACCURACY DODGING STRIKE_DAMAGE DAMAGE_ABSORB HP_REGEN"
primary_attribute_list = ["STRENGTH", "HEALTH", "AGILITY"]
########################################################################
Attributes = Enum("Attributes", attribute_string)

########################################################################

player_attribute_strings = []
for attr in attribute_string.split():
    player_attribute_strings.append("BASE_" + attr)
    player_attribute_strings.append("MODIFIER_" + attr)
    player_attribute_strings.append(attr)

PlayerAttributes = Enum("PlayerAttributes", " ".join(player_attribute_strings))


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


########################################################################
class PlayerAttributeSet(dict):
    ####################################################################
    def __init__(self, player=None):
        super(PlayerAttributeSet, self).__init__()
        self.player = player
        self.recalculating = False
        for attr in PlayerAttributes:
            self.__set_field(attr, 0)

    ####################################################################
    def set_player(self, player):
        self.player = player
        self.recalculate_stats()

    ####################################################################
    def __get_attribute(self, item):
        if isinstance(item, basestring):
            item = PlayerAttributes[item]
        elif isinstance(item, int):
            item = PlayerAttributes(item)
        return item

    ####################################################################
    def __getitem__(self, item):
        item = self.__get_attribute(item)
        return super(PlayerAttributeSet, self).__getitem__(item)

    ####################################################################
    def __set_field(self, key, value):
        item = self.__get_attribute(key)
        return super(PlayerAttributeSet, self).__setitem__(item, value)

    ####################################################################
    def __setitem__(self, key, value):
        item = self.__get_attribute(key)
        if item.name.startswith("BASE_") or item.name.startswith("MODIFIER_"):
            result = self.__set_field(item, value)
            self.recalculate_stats()
            return result
        else:
            raise AttributeError("%s is a read-only field" % item.name)

    ####################################################################
    def recalculate_stats(self):
        if self.recalculating:
            return
        try:
            self.recalculating = True
            self._recalculate_stats()
        finally:
            self.recalculating = False

    ####################################################################
    def _recalculate_stats(self):
        if self.player is None:
            return
        for attr in primary_attribute_list:
            value = self["BASE_" + attr] + self["MODIFIER_" + attr]
            value = max(1, value)
            self.__set_field(attr, value)

        self.__set_field("MODIFIER_MAX_HIT_POINTS", int(10 + (self.player.level * self.HEALTH / 1.5)))
        self.__set_field("MODIFIER_HP_REGEN", (self.HEALTH // 5) + self.player.level)
        self.__set_field("MODIFIER_ACCURACY", self.AGILITY * 3)
        self.__set_field("MODIFIER_DODGING", self.AGILITY * 3)
        self.__set_field("MODIFIER_DAMAGE_ABSORB", self.STRENGTH // 5)
        self.__set_field("MODIFIER_STRIKE_DAMAGE", self.STRENGTH // 5)
        # make sure the hit points don't overflow if your max goes down
        if self.player.hit_points > self.MAX_HIT_POINTS:
            self.player.hit_points = self.MAX_HIT_POINTS

        if self.player.weapon:
            self.add_dynamic_bonuses(self.player.weapon)
        if self.player.armor:
            self.add_dynamic_bonuses(self.player.armor)

        for attr in attribute_string.split():
            value = self["BASE_" + attr] + self["MODIFIER_" + attr]
            if attr in primary_attribute_list:
                value = max(1, value)
            self.__set_field(attr, value)

    ####################################################################
    def add_dynamic_bonuses(self, item):
        if item:
            for attr in Attributes:
                self["MODIFIER_" + attr.name] += item.attributes[attr]

    ####################################################################
    def set_base_attr(self, attr, val):
        self["BASE_" + attr.name] = val

    ####################################################################
    def add_bonuses(self, item):
        if item:
            for attr in Attributes:
                self["BASE_" + attr.name] += item.attributes[attr]

    ####################################################################
    def __getattr__(self, name):
        if name in player_attribute_strings:
            return self[name]
        else:
            return super(PlayerAttributeSet, self).__getattribute__(name)

    ####################################################################
    def __setattr__(self, name, value):
        if name in player_attribute_strings:
            self[name] = value
        else:
            super(PlayerAttributeSet, self).__setattr__(name, value)

    ####################################################################
    def serialize_to_dict(self):
        return {key.name: value for key, value in self.items()}

    ####################################################################
    @staticmethod
    def deserialize_from_dict(data_dict):
        attr_set = PlayerAttributeSet()
        attr_set.recalculating = True

        calculated_attributes = attribute_string.split()
        for key, value in data_dict.items():
            if key not in calculated_attributes:
                attr_set[PlayerAttributes[key]] = value
        attr_set.recalculating = False
        return attr_set
