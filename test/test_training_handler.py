import unittest
from logon_handler import LogonHandler
from player import PlayerDatabase, Player
import training_handler
from training_handler import TrainingHandler
from test_utils import MockProtocol


########################################################################
class TrainingHandlerTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        MockProtocol.set_handler_class(handler_class=LogonHandler)
        self.protocol = MockProtocol()
        PlayerDatabase.db = None
        training_handler.player_database = PlayerDatabase.load()
        self.player = Player(28)
        self.protocol.remove_handler()
        self.protocol.add_handler(TrainingHandler(self.protocol, self.player))
        self.handler = self.protocol.handler
        self.assertEqual(len(list(training_handler.player_database.all())), 1)
        self.maxDiff = None

    ####################################################################
    def test_handle(self):
        self.fail()

    ####################################################################
    def test_enter(self):
        self.player.active = True
        self.player.newbie = False
        self.handler.enter()
        self.assertEqual(self.player.active, False)
        self.assertEqual(self.player.newbie, False)
        self.assertEqual(self.protocol.send_data, [])

    ####################################################################
    def test_hung_up(self):
        self.fail()

    ####################################################################
    def test_flooded(self):
        self.fail()

    ####################################################################
    def test_print_stats(self):
        self.fail()
