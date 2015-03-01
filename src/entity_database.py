########################################################################
class EntityDatabase(object):
    ####################################################################
    def __init__(self):
        self.by_name = {}
        self.by_id = {}

    ####################################################################
    def clear(self):
        self.by_name.clear()
        self.by_id.clear()

    ####################################################################
    def find_full(self, name):
        if name is None:
            return None
        return self.by_name.get(name.lower())

    ####################################################################
    def find(self, name_or_id):
        if name_or_id is None:
            return None
        if isinstance(name_or_id, int):
            return self.by_id.get(name_or_id)
        else:
            result = self.find_full(name_or_id)
            if result:
                return result
            else:
                name = name_or_id.lower()
                for entity in self.by_name.values():
                    if entity.match(name):
                        return entity

    ####################################################################
    def __getitem__(self, item_id):
        return self.by_id.get(item_id)

    ####################################################################
    def has(self, name_or_id):
        return self.find(name_or_id) is not None

    ####################################################################
    def has_full(self, name):
        return self.find_full(name) is not None

    ####################################################################
    def all(self):
        return self.by_id.values()

    ####################################################################
    def __len__(self):
        return len(self.by_id)
