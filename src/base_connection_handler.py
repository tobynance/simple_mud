########################################################################
class BaseConnectionHandler(object):
    ####################################################################
    def enter(self):
        """Connection enters state"""
        raise NotImplementedError

    ####################################################################
    def leave(self):
        """Connection leaves state"""
        raise NotImplementedError

    ####################################################################
    def hung_up(self):
        """Connection hangs up"""
        raise NotImplementedError

    ####################################################################
    def flooded(self):
        """Connection floods"""
        raise NotImplementedError

    ####################################################################
    def no_room(self, connection):
        pass
