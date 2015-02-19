########################################################################
class MockProtocol(object):
    handler_class = None
    closed = False

    ####################################################################
    def __init__(self):
        self.handlers = []
        self.handlers.append(self.handler_class(self))
        self.drop_connection_calls = 0
        self.send_data = []

    ####################################################################
    @classmethod
    def set_handler_class(cls, handler_class):
        cls.handler_class = handler_class

    ####################################################################
    @property
    def handler(self):
        if self.handlers:
            return self.handlers[-1]

    ####################################################################
    def get_remote_address(self):
        return "192.168.99.99"

    ####################################################################
    def add_handler(self, handler):
        if self.handler:
            self.handler.leave()
        self.handlers.append(handler)
        self.handler.enter()

    ####################################################################
    def drop_connection(self):
        self.drop_connection_calls += 1

    ####################################################################
    def remove_handler(self):
        if self.handler:
            self.handler.leave()
            self.handlers.pop(-1)
            if self.handler:
                self.handler.enter()

    ####################################################################
    def clear_handlers(self):
        if self.handler:
            self.handler.leave()
        self.handlers = []

    ####################################################################
    def send(self, data):
        self.send_data.append(data)

    ####################################################################
    def dataReceived(self, data):
        data = data.strip()
        self.handler.handle(data)

    ####################################################################
    def connectionMade(self):
        self.handler.enter()

    ####################################################################
    def connectionLost(self, reason=None):
        self.closed = True
