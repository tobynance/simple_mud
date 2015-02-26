import logging
import player
import telnet

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
            player.player_database.save()
            self.protocol.remove_handler()
            return
        if data in ["1", "2", "3"]:
            if self.player.stat_points > 0:
                self.player.stat_points -= 1
                if data == "1":
                    self.player.attributes.BASE_STRENGTH += 1
                elif data == "2":
                    self.player.attributes.BASE_HEALTH += 1
                else:
                    self.player.attributes.BASE_AGILITY += 1
            self.print_stats(True)
        else:
            logger.warn("unknown command: %s", data)
            self.send("<reset><clearscreen><red>Unknown Command '%s'<newline>" % data)
            self.print_stats(False)

    ####################################################################
    def enter(self):
        self.player.active = False
        if self.player.newbie:
            self.send(("<magenta><bold>Welcome to SimpleMUD, %s!\r\n" +
                       "You must train your character with your desired stats,\r\n" +
                       "before you enter the realm.\r\n\r\n") % self.player.name)
            self.player.newbie = False
        self.print_stats(False)

    ####################################################################
    def hung_up(self):
        logger.warn("%s - hung up in %s", self.protocol.get_remote_address(), self.__class__.__name__)
        player.player_database.logout(self.player.id)

    ####################################################################
    def flooded(self):
        logger.warn("%s - flooded in %s", self.protocol.get_remote_address(), self.__class__.__name__)
        player.player_database.logout(self.player.id)

    ####################################################################
    def print_stats(self, clear_screen=True):
        message = []
        if clear_screen:
            message.append("<clearscreen>")

        message += ["<white><bold>"]
        message.append("---------------------- Your Stats ----------------------\r\n")
        message.append("<dim>")
        message.append("Player: %s\r\n" % self.player.name)
        message.append("Stat Points Left: %s\r\n" % self.player.stat_points)
        message.append("1) Strength: %s\r\n" % self.player.attributes.STRENGTH)
        message.append("2) Health: %s\r\n" % self.player.attributes.HEALTH)
        message.append("3) Agility: %s\r\n" % self.player.attributes.AGILITY)
        message.append("<bold>")
        message.append("--------------------------------------------------------\r\n")
        message.append("Enter 1, 2, or 3 to add a stat point, or \"quit\" to go back: ")
        self.send("".join(message))
