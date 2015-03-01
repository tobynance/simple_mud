import time

TIME_CHUNK = 16


########################################################################
class Connection(object):
    ####################################################################
    def __init__(self, socket=None):
        self.socket = socket
        self.protocol = None
        self.handler_stack = []
        self.send_buffer = ""
        self.data_rate = 0
        self.last_data_rate = 0
        self.last_receive_time = 0
        self.last_send_time = 0
        self.creation_time = 0
        self.check_send_time = False
        self.buffer = ""
        self.closed = False

    ####################################################################
    def initialize(self):
        self.data_rate = 0
        self.last_data_rate = 0
        self.last_receive_time = 0
        self.last_send_time = 0
        self.check_send_time = False
        self.creation_time = time.clock()
        self.closed = False

    ####################################################################
    def close(self):
        raise NotImplementedError

    ####################################################################
    def close_socket(self):
        raise NotImplementedError

    ####################################################################
    def buffer_data(self, data):
        raise NotImplementedError

    ####################################################################
    def send_buffer(self):
        raise NotImplementedError

    ####################################################################
    def receive(self):
        num_bytes = self.socket.receive(self.buffer)
        now = time.clock()
        if self.last_receive_time // TIME_CHUNK != now // TIME_CHUNK:
            self.last_data_rate = self.data_rate // TIME_CHUNK
            self.data_rate = 0
            self.last_receive_time = now
        self.data_rate += num_bytes
        self.protocol.translate(self, self.buffer, num_bytes)

    ####################################################################
    def switch_handler(self, handler):
        raise NotImplementedError

    ####################################################################
    def add_handler(self, handler):
        raise NotImplementedError

    ####################################################################
    def remove_handler(self):
        raise NotImplementedError

    ####################################################################
    def clear_handlers(self):
        raise NotImplementedError
