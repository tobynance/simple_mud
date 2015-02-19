import unittest
import os
os.environ["SIMPLE_MUD_LOAD_PLAYERS"] = "false"
from player import PlayerDatabase, Player
import game_handler
from logon_handler import LogonHandler
from test_utils import MockProtocol, stats_message


########################################################################
class GameHandlerTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        MockProtocol.set_handler_class(handler_class=LogonHandler)
        self.protocol = MockProtocol()
        PlayerDatabase.db = None
        game_handler.player_database = PlayerDatabase.load()
        self.player = Player(28)
        self.player.name = "jerry"
        game_handler.player_database.add_player(self.player)

        self.protocol.remove_handler()
        self.player.protocol = self.protocol
        self.protocol.add_handler(game_handler.GameHandler(self.protocol, self.player))
        self.handler = self.protocol.handler
        self.assertEqual(len(list(game_handler.player_database.all())), 1)
        self.protocol.send_data = []
        self.maxDiff = None

    ####################################################################
    def test_handle_last_command(self):
        self.fail()

    ####################################################################
    def test_handle_chat(self):
        self.fail()

    ####################################################################
    def test_handle_experience(self):
        self.fail()

    ####################################################################
    def test_handle_help(self):
        self.fail()

    ####################################################################
    def test_handle_inventory(self):
        self.fail()

    ####################################################################
    def test_handle_stats(self):
        self.fail()

    ####################################################################
    def test_handle_quit(self):
        self.fail()

    ####################################################################
    def test_handle_remove(self):
        self.fail()

    ####################################################################
    def test_handle_use(self):
        self.fail()

    ####################################################################
    def test_handle_time(self):
        self.fail()

    ####################################################################
    def test_handle_whisper(self):
        self.fail()

    ####################################################################
    def test_handle_who(self):
        self.fail()

    ####################################################################
    def test_handle_kick(self):
        self.fail()

    ####################################################################
    def test_handle_announce(self):
        self.fail()

    ####################################################################
    def test_handle_change_rank(self):
        self.fail()

    ####################################################################
    def test_handle_reload(self):
        self.fail()

    ####################################################################
    def test_handle_shutdown(self):
        self.fail()

    ####################################################################
    def test_enter(self):
        self.fail()

    ####################################################################
    def test_leave(self):
        self.fail()

    ####################################################################
    def test_hung_up(self):
        self.fail()

    ####################################################################
    def test_flooded(self):
        self.fail()

    ####################################################################
    def test_send_global(self):
        self.fail()

    ####################################################################
    def test_send_game(self):
        self.fail()

    ####################################################################
    def test_logout_message(self):
        self.fail()

    ####################################################################
    def test_announce(self):
        self.fail()

    ####################################################################
    def test_whisper(self):
        self.fail()

    ####################################################################
    def test_who_list(self):
        self.fail()

    ####################################################################
    def test_print_help(self):
        self.fail()

    ####################################################################
    def test_print_stats(self):
        self.fail()

    ####################################################################
    def test_print_experience(self):
        self.fail()

    ####################################################################
    def test_print_inventory(self):
        self.fail()
