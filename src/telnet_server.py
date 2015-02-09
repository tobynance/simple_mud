import logging
from twisted.conch.telnet import TelnetTransport, TelnetProtocol
from twisted.internet import reactor, endpoints
from twisted.internet.protocol import ServerFactory
from enum import Enum

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

newline = "\r\n\x1B[0m"

TelnetStates = Enum("TelnetStates", "USERNAME PASSWORD COMMAND")


########################################################################
class MudTelnetProtocol(TelnetProtocol):
    state_enum = TelnetStates
    initial_state = TelnetStates.USERNAME

    ####################################################################
    def __init__(self):
        self.state = self.initial_state
        self.username = None
        self.password = None

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
    def handle_username(self, username):
        self.username = username
        self.state = TelnetStates.PASSWORD

    ####################################################################
    def handle_password(self, password):
        self.password = password
        self.state = TelnetStates.COMMAND

    ####################################################################
    def handle_command(self, data):
        print "do something..."

    ####################################################################
    def handle(self, data):
        raise NotImplementedError

    ####################################################################
    def send(self, data):
        self.transport.write(data)

    ####################################################################
    def dataReceived(self, data):
        logger.info("self: %s", self)
        data = data.strip()
        self.send("I received %r from you while in state %s\r\n" % (data, self.state_enum(self.state).name))

        if self.state in self.state_enum:
            method_name = ("handle_%s" % self.state_enum(self.state).name).lower()
            logger.info("Received '%s', passing it to handler %s", data, method_name)
            getattr(self, method_name)(data)
        else:
            logger.warn("In unknown state '%s', using generic handler", self.state)
            self.handle(data)

    ####################################################################
    def connectionMade(self):
        logger.info("test")
        self.transport.write('Username: ')


########################################################################
def initialize_logger(logging_level=logging.INFO):
    logging.basicConfig(level=logging_level, format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s", datefmt="%d/%b/%Y %H:%M:%S")


########################################################################
def run():
    initialize_logger(logging.INFO)
    factory = ServerFactory()
    factory.protocol = lambda: TelnetTransport(MudTelnetProtocol)

    endpoints.serverFromString(reactor, "tcp:8023").listen(factory)
    reactor.run()
