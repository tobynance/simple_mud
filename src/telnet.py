import re
import logging
from twisted.conch.telnet import TelnetTransport, TelnetProtocol
from twisted.internet import reactor, endpoints
from twisted.internet.protocol import ServerFactory

logger = logging.getLogger(__name__)

reset = "\x1B[0m"
bold = "\x1B[1m"
dim = "\x1B[2m"
under = "\x1B[4m"
reverse = "\x1B[7m"
hide = "\x1B[8m"

clearscreen = "\x1B[2J"
clearline = "\x1B[2K"

black = "\x1B[30m"
red = "\x1B[31m"
green = "\x1B[32m"
yellow = "\x1B[33m"
blue = "\x1B[34m"
magenta = "\x1B[35m"
cyan = "\x1B[36m"
white = "\x1B[37m"

bblack = "\x1B[40m"
bred = "\x1B[41m"
bgreen = "\x1B[42m"
byellow = "\x1B[43m"
bblue = "\x1B[44m"
bmagenta = "\x1B[45m"
bcyan = "\x1B[46m"
bwhite = "\x1B[47m"
concealed = "\x1B[8m"

newline = "\r\n"
carriage_return = "\r"

TELNET_REPLACEMENTS = dict(reset=reset,
                           bold=bold,
                           dim=dim,
                           under=under,
                           reverse=reverse,
                           hide=hide,
                           clearscreen=clearscreen,
                           clearline=clearline,
                           black=black,
                           red=red,
                           green=green,
                           yellow=yellow,
                           blue=blue,
                           magenta=magenta,
                           cyan=cyan,
                           white=white,
                           bblack=bblack,
                           bred=bred,
                           bgreen=bgreen,
                           byellow=byellow,
                           bblue=bblue,
                           bmagenta=bmagenta,
                           bcyan=bcyan,
                           bwhite=bwhite,
                           concealed=concealed,
                           newline=newline,
                           carriage_return=carriage_return)


########################################################################
def tf(text):
    """
    Replace the telnet tags with the telnet escape values.
    """
    text = str(text)
    for key, value in TELNET_REPLACEMENTS.items():
        text = text.replace("<" + key + ">", value)
    return text


########################################################################
class MudTelnetHandler(object):
    ####################################################################
    def __init__(self, protocol):
        self.protocol = protocol
        self.data_handlers = []

    ####################################################################
    def send(self, data):
        self.protocol.send(data)

    ####################################################################
    def get_remote_address(self):
        if self.protocol:
            return self.protocol.get_remote_address()
        else:
            return "<unknown address>"

    ####################################################################
    def leave(self):
        logger.info("%s - leave called in %s", self.get_remote_address(), self.__class__.__name__)

    ####################################################################
    def enter(self):
        logger.info("%s - enter called in %s", self.get_remote_address(), self.__class__.__name__)

    ####################################################################
    def hung_up(self):
        logger.warn("%s - hung up in %s", self.get_remote_address(), self.__class__.__name__)

    ####################################################################
    def flooded(self):
        logger.warn("%s - flooded in %s", self.get_remote_address(), self.__class__.__name__)

    ####################################################################
    def handle(self, data):
        raise NotImplementedError


########################################################################
class BaseStateDispatchHandler(MudTelnetHandler):
    initial_state = None
    state = None

    ####################################################################
    def handle(self, data):
        method_name = ("handle_%s" % self.state.name).lower()
        logger.info("Received '%s', passing it to handler %s", data, method_name)
        getattr(self, method_name)(data)


########################################################################
class BaseCommandDispatchHandler(MudTelnetHandler):
    last_command = None

    ####################################################################
    def _register_data_handler(self, predicate, handler):
        self.data_handlers.append((predicate, handler))

    ####################################################################
    def handle(self, data):
        if data:
            split = data.split(None, 1)
            first_word = data.split(None, 1)[0]
            if len(split) > 1:
                rest = split[1]
            else:
                rest = ""

            for predicate, handler in self.data_handlers:
                if self.check_predicate(predicate, first_word):
                    handler(data, first_word, rest)
                    if predicate != "/":
                        self.last_command = data
                    return

    ####################################################################
    def check_predicate(self, predicate, data):
        if isinstance(predicate, basestring):
            return predicate == data
        elif isinstance(predicate, list) or isinstance(predicate, tuple):
            return data in predicate
        elif isinstance(predicate, bool):
            return predicate
        elif isinstance(predicate, re._pattern_type):
            if predicate.match(data):
                return True
            else:
                return False
        else:
            raise ValueError("I don't know how to use the predicate '%s' of type '%s'" % predicate, type(predicate))


########################################################################
class MudTelnetProtocol(TelnetProtocol):
    handler_class = None
    closed = False

    ####################################################################
    def __init__(self):
        self.handlers = []
        self.handlers.append(self.handler_class(self))

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
        if self.transport:
            return self.transport.getPeer()
        else:
            return "<unknown address>"

    ####################################################################
    def add_handler(self, handler):
        if self.handler:
            self.handler.leave()
        self.handlers.append(handler)
        self.handler.enter()

    ####################################################################
    def drop_connection(self):
        self.transport.loseConnection()

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
    def enableRemote(self, option):
        return False

    ####################################################################
    def disableRemote(self, option):
        pass

    ####################################################################
    def enableLocal(self, option):
        return False

    ####################################################################
    def disableLocal(self, option):
        pass

    ####################################################################
    def send(self, data):
        if not data.endswith("<concealed>"):
            data += "<reset>"
        data = tf(data)
        self.transport.write(data)

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


########################################################################
def initialize_logger(logging_level=logging.INFO):
    logging.basicConfig(level=logging_level, format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s", datefmt="%d/%b/%Y %H:%M:%S")


########################################################################
def stop():
    logger.info("Shutting down the reactor...")
    reactor.stop()

########################################################################
def run():
    initialize_logger(logging.INFO)
    factory = ServerFactory()
    factory.protocol = lambda: TelnetTransport(MudTelnetProtocol)
    print "running on port 8023..."
    endpoints.serverFromString(reactor, "tcp:8023").listen(factory)
    reactor.run()
