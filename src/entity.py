########################################################################
class Entity(object):
    ####################################################################
    def __init__(self):
        self.name = "UNDEFINED"
        self.id = 0

    ####################################################################
    def __str__(self):
        return "(%s)%s" % (self.id, self.name)

    ####################################################################
    def get_comparison_name(self):
        return self.name.lower()

    ####################################################################
    def match_full(self, name):
        return self.name.lower() == name

    ####################################################################
    def match(self, name):
        if self.match_full(name):
            return True
        for part in self.name.lower().split():
            if part.startswith(name):
                return True
        return False
