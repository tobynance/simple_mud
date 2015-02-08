import logging
from twisted.conch.telnet import TelnetTransport, TelnetProtocol
from twisted.internet import reactor, endpoints
from twisted.internet.protocol import ServerFactory
from enum import Enum

logging.basicConfig()
logger = logging.getLogger(__name__)

TelnetStates = Enum("TelnetStates", "USERNAME PASSWORD COMMAND")


########################################################################
class TelnetEcho(TelnetProtocol):
    ####################################################################
    def __init__(self):
        self.state = TelnetStates.USERNAME
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
    def dataReceived(self, data):
        print "self:", self
        data = data.strip()
        self.transport.write("I received %r from you while in state %s\r\n" % (data, TelnetStates(self.state)))

        if self.state == TelnetStates.USERNAME:
            self.username = data
            self.state = TelnetStates.PASSWORD
        elif self.state == TelnetStates.PASSWORD:
            self.password = data
            self.state = TelnetStates.COMMAND

    ####################################################################
    def connectionMade(self):
        print "test"
        logger.info("test")
        self.transport.write('Username: ')


########################################################################
factory = ServerFactory()
factory.protocol = lambda: TelnetTransport(TelnetEcho)

endpoints.serverFromString(reactor, "tcp:8023").listen(factory)
reactor.run()
