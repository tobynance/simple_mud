

########################################################################
class Logon(object):
    ####################################################################
    def __init__(self, connection):
        self.state = None
        self.num_errors = None
        self.name = None
        self.password = None

    ####################################################################
    def enter(self):
        raise NotImplementedError

    ####################################################################
    def leave(self):
        raise NotImplementedError

    ####################################################################
    def hung_up(self):
        raise NotImplementedError

    ####################################################################
    def flooded(self):
        raise NotImplementedError

    ####################################################################
    def no_room(self):
        raise NotImplementedError

    ####################################################################
    def handle(self, data):
        raise NotImplementedError

    ####################################################################
    def goto_game(self, newbie=False):
        raise NotImplementedError

    ####################################################################
    def acceptable_name(self, name):
        raise NotImplementedError
