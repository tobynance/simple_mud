import unittest
import os
os.environ["SIMPLE_MUD_LOAD_PLAYERS"] = "false"

from logon_handler import LogonHandler
from player import PlayerDatabase, Player
import training_handler
from training_handler import TrainingHandler
from test_utils import MockProtocol, stats_message


########################################################################
class TrainingHandlerTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        MockProtocol.set_handler_class(handler_class=LogonHandler)
        self.protocol = MockProtocol()
        PlayerDatabase.db = None
        training_handler.player_database = PlayerDatabase.load()
        self.player = Player(28)
        self.player.name = "jerry"
        training_handler.player_database.add_player(self.player)

        self.protocol.remove_handler()
        self.player.protocol = self.protocol
        self.protocol.add_handler(TrainingHandler(self.protocol, self.player))
        self.handler = self.protocol.handler
        self.assertEqual(len(list(training_handler.player_database.all())), 1)
        self.protocol.send_data = []
        self.maxDiff = None

    ####################################################################
    def test_handle__quit(self):
        self.assertEqual(len(self.player.protocol.handlers), 1)
        self.assertEqual(self.player.protocol.handlers, [self.handler])
        self.handler.handle("quit")
        self.assertEqual(len(self.player.protocol.handlers), 0)

    ####################################################################
    def test_handle(self):
        self.assertEqual(self.player.stat_points, 18)
        self.assertEqual(self.player.attributes.HEALTH, 1)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 1)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 1)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 1)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 1)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 1)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)

        self.handler.handle("1")
        self.assertEqual(self.player.stat_points, 17)
        self.assertEqual(self.player.attributes.HEALTH, 1)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 1)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 2)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 2)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 1)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 1)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)

        self.handler.handle("1")
        self.assertEqual(self.player.stat_points, 16)
        self.assertEqual(self.player.attributes.HEALTH, 1)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 1)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 3)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 1)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 1)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)

        self.handler.handle("2")
        self.assertEqual(self.player.stat_points, 15)
        self.assertEqual(self.player.attributes.HEALTH, 2)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 2)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 3)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 1)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 1)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)

        self.handler.handle("2")
        self.assertEqual(self.player.stat_points, 14)
        self.assertEqual(self.player.attributes.HEALTH, 3)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 3)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 1)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 1)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)

        self.handler.handle("3")
        self.assertEqual(self.player.stat_points, 13)
        self.assertEqual(self.player.attributes.HEALTH, 3)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 3)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 2)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 2)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)

        self.handler.handle("3")
        self.assertEqual(self.player.stat_points, 12)
        self.assertEqual(self.player.attributes.HEALTH, 3)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 3)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 3)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 3)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)

        self.player.stat_points = 1

        self.handler.handle("3")
        self.assertEqual(self.player.stat_points, 0)
        self.assertEqual(self.player.attributes.HEALTH, 3)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 3)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 4)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 4)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)

        self.handler.handle("3")
        self.assertEqual(self.player.stat_points, 0)
        self.assertEqual(self.player.attributes.HEALTH, 3)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 3)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 3)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 4)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 4)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)

    ####################################################################
    def test_handle__unknown_command(self):
        self.handler.handle("beep")
        self.assertEqual(self.player.stat_points, 18)
        self.assertEqual(self.player.attributes.HEALTH, 1)
        self.assertEqual(self.player.attributes.BASE_HEALTH, 1)
        self.assertEqual(self.player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(self.player.attributes.STRENGTH, 1)
        self.assertEqual(self.player.attributes.BASE_STRENGTH, 1)
        self.assertEqual(self.player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.player.attributes.AGILITY, 1)
        self.assertEqual(self.player.attributes.BASE_AGILITY, 1)
        self.assertEqual(self.player.attributes.MODIFIER_AGILITY, 0)
        self.assertEqual(self.protocol.send_data, ["<reset><clearscreen><red>Unknown Command 'beep'", stats_message])

    ####################################################################
    def test_enter(self):
        self.player.logged_in = True
        self.player.active = True
        self.player.newbie = False
        self.handler.enter()
        self.assertEqual(self.player.active, False)
        self.assertEqual(self.player.newbie, False)
        self.assertEqual(self.protocol.send_data, [stats_message])

    ####################################################################
    def test_hung_up(self):
        self.player.logged_in = True
        self.handler.hung_up()
        self.assertEqual(self.protocol.send_data, [])
        self.assertEqual(self.player.logged_in, False)

    ####################################################################
    def test_flooded(self):
        self.player.logged_in = True
        self.handler.hung_up()
        self.assertEqual(self.protocol.send_data, [])
        self.assertEqual(self.player.logged_in, False)

    ####################################################################
    def test_print_stats(self):
        self.handler.print_stats()
        self.assertEqual(self.protocol.send_data, ["<clearscreen>" + stats_message])
        self.handler.print_stats(clear_screen=False)
        self.assertEqual(self.protocol.send_data, ["<clearscreen>" + stats_message, stats_message])
