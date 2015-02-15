import logging
from attributes import Attributes
from player import PlayerDatabase
import telnet
from telnet import bold, white, reset, red, clearscreen, magenta, dim

logger = logging.getLogger(__name__)


########################################################################
class TrainingHandler(telnet.MudTelnetHandler):
    ####################################################################
    def __init__(self, protocol, player):
        super(TrainingHandler, self).__init__(protocol)
        self.player = player

    ####################################################################
    def handle(self, data):
        if data == "quit":
            PlayerDatabase.load().save()
            self.player.protocol.remove_handler()
            # tell the previous handler that it now has control again
            self.player.protocol.handler.enter()
            return
        if data in ["1", "2", "3"]:
            data = int(data)
            if self.player.stat_points > 0:
                self.player.stat_points -= 1
                self.player.add_to_base_attr(data, 1)
            self.print_stats(True)
        else:
            self.send(reset + clearscreen + red + "Unknown Command '%s'" % data)
            self.print_stats(False)

    ####################################################################
    def enter(self):
        self.player.active = False
        if self.player.newbie:
            self.send("".join([magenta, bold, "Welcome to SimpleMUD, ",
                               self.player.name, "!\r\n",
                               "You must train your character with your desired stats,\r\n",
                               "before you enter the realm.\r\n\r\n"]))
            self.player.newbie = False
        self.print_stats(False)

    ####################################################################
    def hung_up(self):
        logger.warn("%s - hung up in %s", self.protocol.transport.getPeer(), self.__class__.__name__)
        PlayerDatabase.load().logout(self.player.id)

    ####################################################################
    def flooded(self):
        logger.warn("%s - flooded in %s", self.protocol.transport.getPeer(), self.__class__.__name__)
        PlayerDatabase.load().logout(self.player.id)

    ####################################################################
    def print_stats(self, clear_screen=True):
        message = []
        if clear_screen:
            message.append(clearscreen)

        message += [white, bold]
        message.append("---------------------- Your Stats ----------------------\r\n")
        message.append(dim)
        message.append("Player: %s\r\n" % self.player.name)
        message.append("Stat Points Left: %s\r\n" % self.player.stat_points)
        message.append("1) Strength: %s\r\n" % self.player.attributes[Attributes.STRENGH])
        message.append("2) Health: %s\r\n" % self.player.attributes[Attributes.HEALTH])
        message.append("3) Agility: %s\r\n" % self.player.attributes[Attributes.AGILITY])
        message.append(bold)
        message.append("--------------------------------------------------------\r\n")
        message.append("Enter 1, 2, or 3 to add a stat point, or \"quit\" to go back: ")
        self.send("".join(message))
