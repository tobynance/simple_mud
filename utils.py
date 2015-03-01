from collections import OrderedDict


########################################################################
def clamp(value, minimum=0.0, maximum=1.0):
    return min(maximum, max(minimum, value))


########################################################################
def find_all_by_name(name, list_entities):
    name = name.lower()
    for entity in list_entities:
        if entity.match(name):
            yield entity


########################################################################
def double_find_by_name(name, list_entities):
    """First try to find an exact match, then try to do a less exact match"""
    name = name.lower()
    for entity in list_entities:
        if entity.match_full(name):
            return entity
    for entity in list_entities:
        if entity.match(name):
            return entity


########################################################################
class DjangoChoiceEnum(object):
    """
    An attempt to make writing choices simpler.
    Look at AgeRangeType for an example.  If you don't pass in a
    descriptive name, then the variable_name will be used in its place.
    """
    def __init__(self):
        self._descriptions = OrderedDict()
        self._variables = OrderedDict()

    ####################################################################
    def __get_reversed_dict(self):
        return {value: key for key, value in self._descriptions.items()}

    ###################################################################
    def __call__(self, key):
        if key in self._descriptions:
            return self._descriptions[key]
        else:
            return self.__get_reversed_dict()[key]

    ###################################################################
    def __iter__(self):
        for key in self._descriptions.keys():
            yield key

    ####################################################################
    def add(self, num, variable_name, descriptive_name=None):
        if descriptive_name is None:
            descriptive_name = variable_name
        object.__setattr__(self, variable_name, num)
        self._descriptions[num] = descriptive_name
        self._variables[num] = variable_name

    ####################################################################
    def choices(self):
        return [(key, value) for key, value in self._descriptions.items()]

    ####################################################################
    def get_dict(self):
        return self._descriptions.copy()

    ####################################################################
    def get_variable_dict(self):
        return self._variables.copy()

    ####################################################################
    def to_variable_name(self, key):
        return self._variables[key]

########################################################################
########################################################################
ItemType = DjangoChoiceEnum()
ItemType.add(0, "WEAPON")
ItemType.add(1, "ARMOR")
ItemType.add(2, "HEALING")

PlayerRank = DjangoChoiceEnum()
PlayerRank.add(0, "REGULAR")
PlayerRank.add(1, "MODERATOR")
PlayerRank.add(2, "ADMIN")

RoomType = DjangoChoiceEnum()
RoomType.add(0, "PLAIN_ROOM")
RoomType.add(1, "TRAINING_ROOM")
RoomType.add(2, "STORE")


########################################################################
# Temporary conversion util
########################################################################
from collections import OrderedDict


########################################################################
def convert_item(initial_item_data):
    output_data = OrderedDict()
    output_data["model"] = "mud.item"
    output_data["pk"] = initial_item_data["id"]
    output_data["fields"] = OrderedDict()
    fields = output_data["fields"]
    for field_name in ["name", "type", "min", "max", "speed", "price",
                       "STRENGTH", "HEALTH", "AGILITY", "MAX_HIT_POINTS",
                       "ACCURACY", "DODGING", "STRIKE_DAMAGE",
                       "DAMAGE_ABSORB", "HP_REGEN"]:
        fields[field_name] = initial_item_data[field_name]
    return output_data


########################################################################
def convert_enemy_template(initial_template_data):
    output_data = OrderedDict()
    output_data["model"] = "mud.enemytemplate"
    output_data["pk"] = initial_template_data["id"]
    output_data["fields"] = OrderedDict()
    fields = output_data["fields"]
    for field_name in ["name", "hit_points", "accuracy", "dodging",
                       "strike_damage", "damage_absorb", "experience",
                       "weapon", "money_min", "money_max"]:
        fields[field_name] = initial_template_data[field_name]
    return output_data


########################################################################
def convert_enemy_loot(initial_template_data, current_count, output_list):
    for item_id, chance in initial_template_data.get("loot", []):
        output_data = OrderedDict()
        output_data["model"] = "mud.enemyloot"
        current_count += 1
        output_data["pk"] = current_count
        output_data["fields"] = OrderedDict()
        fields = output_data["fields"]
        fields["enemy_template"] = initial_template_data["id"]
        fields["item"] = item_id
        fields["percent_chance"] = chance
        output_list.append(output_data)
    return current_count

#
# import json
# from collections import OrderedDict
# initial_data = json.load(open("enemy_templates.json"))
# output_list_data = []
# for et in initial_data:
#     output_list_data.append(convert_enemy_template(et))
#
# current_count = 0
# for et in initial_data:
#     current_count = convert_enemy_loot(et, current_count, output_list_data)
