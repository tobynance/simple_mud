########################################################################
def clamp(value, minimum=0.0, maximum=1.0):
    return min(maximum, max(minimum, value))


########################################################################
def find_all_by_name(name, list_entities):
    for entity in list_entities:
        if entity.match(name):
            yield entity

########################################################################
def double_find_by_name(name, list_entities):
    """First try to find an exact match, then try to do a less exact match"""
    name = name.lower()
    for entity in list_entities:
        if entity.name == name:
            return entity
    for entity in list_entities:
        if entity.match(name):
            return entity
