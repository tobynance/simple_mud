########################################################################
class EntityDatabase(object):
    ####################################################################
    def __init__(self):
        self.by_name = {}
        self.by_id = {}

    ####################################################################
    def find_full(self, name):
        return self.by_name.get(name.lower())

    ####################################################################
    def find(self, name_or_id):
        if isinstance(name_or_id, int):
            return self.by_id.get(name_or_id)
        else:
            result = self.find_full(name_or_id)
            if result:
                return result
            else:
                for entity in self.by_name.values():
                    if entity.match(name_or_id):
                        return entity

    ####################################################################
    def has(self, name_or_id):
        return self.find(name_or_id) is not None

    ####################################################################
    def has_full(self, name):
        return self.find_full(name) is not None

    ####################################################################
    def __len__(self):
        return len(self.by_id)
