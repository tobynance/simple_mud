import unittest
import os
import mock
from attributes import PlayerRank
from game_handler import GameHandler
from test_utils import MockProtocol
from training_handler import TrainingHandler

os.environ["SIMPLE_MUD_LOAD_PLAYERS"] = "false"
import logon_handler
from logon_handler import LogonHandler, LogonState
from player import PlayerDatabase, Player

welcome_message = """\
<magenta><bold>Welcome to SimpleMUD, jerry!\r
You must train your character with your desired stats,\r
before you enter the realm.\r\n\r\n"""

stats_message = """\
<white><bold>---------------------- Your Stats ----------------------\r
<dim>Player: jerry\r
Stat Points Left: 18\r
1) Strength: 1\r
2) Health: 1\r
3) Agility: 1\r
<bold>--------------------------------------------------------\r
Enter 1, 2, or 3 to add a stat point, or "quit" to go back: """


########################################################################
class LogonHandlerTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        MockProtocol.set_handler_class(handler_class=LogonHandler)
        self.protocol = MockProtocol()
        self.handler = self.protocol.handler
        PlayerDatabase.db = None
        logon_handler.player_database = PlayerDatabase.load()
        self.assertEqual(len(list(logon_handler.player_database.all())), 0)

    ####################################################################
    def test_handle_new_connection__bad_login(self):
        self.assertEqual(self.handler.num_errors, 0)
        self.assertEqual(self.handler.data_handlers, [])
        self.assertEqual(self.handler.password, None)
        self.assertEqual(self.handler.username, None)
        self.assertEqual(self.handler.state, LogonState.NEW_CONNECTION)
        self.assertEqual(self.handler.state_enum, LogonState)
        self.assertEqual(self.protocol.send_data, [])

        user_does_not_exist_message = "<bold><red>Sorry, user <green>jerry<red> does not exist.\r\n%s" % self.handler.login_prompt
        for i in range(1, 7):
            self.handler.handle_new_connection("jerry")
            self.assertEqual(self.handler.num_errors, i)
            self.assertEqual(self.handler.data_handlers, [])
            self.assertEqual(self.handler.password, None)
            self.assertEqual(self.handler.username, None)
            self.assertEqual(self.handler.state, LogonState.NEW_CONNECTION)
            self.assertEqual(self.handler.state_enum, LogonState)
            self.assertEqual(len(self.protocol.send_data), i)
            self.assertEqual(self.protocol.send_data, [user_does_not_exist_message] * i)
            self.assertEqual(self.handler.protocol.drop_connection_calls, 0)

        ### try again...
        self.handler.handle_new_connection("jerry")
        self.assertEqual(self.handler.protocol.drop_connection_calls, 1)
        self.assertEqual(self.handler.num_errors, 6)  # doesn't actually send another message

    ####################################################################
    def test_handle_new_connection(self):
        self.assertEqual(self.handler.state, LogonState.NEW_CONNECTION)

        new_user_message = "<bold><white>Please enter your new login name: <reset>"
        self.handler.handle_new_connection("new")
        self.assertEqual(self.handler.num_errors, 0)
        self.assertEqual(self.handler.password, None)
        self.assertEqual(self.handler.username, None)
        self.assertEqual(self.handler.state, LogonState.NEW_USER)
        self.assertEqual(self.handler.state_enum, LogonState)
        self.assertEqual(self.protocol.send_data, [new_user_message])
        self.assertEqual(self.handler.protocol.drop_connection_calls, 0)

    ####################################################################
    def test_handle_new_user__invalid_name(self):
        self.handler.state = LogonState.NEW_USER

        user_name_invalid = "<bold><red>Sorry, the name <green>new<red> contains invalid characters.\r\n%s" % self.handler.login_prompt
        self.handler.handle_new_user("new")
        self.assertEqual(self.handler.num_errors, 1)
        self.assertEqual(self.handler.password, None)
        self.assertEqual(self.handler.username, None)
        self.assertEqual(self.handler.state, LogonState.NEW_CONNECTION)
        self.assertEqual(self.handler.state_enum, LogonState)
        self.assertEqual(self.protocol.send_data, [user_name_invalid])
        self.assertEqual(self.handler.protocol.drop_connection_calls, 0)

    ####################################################################
    def test_handle_new_user__username_taken(self):
        self.handler.state = LogonState.NEW_USER
        player = Player()
        player.name = "jerry"
        logon_handler.player_database.add_player(player)

        user_name_invalid = "<bold><red>Sorry, the name <green>jerry<red> is already used.\r\n%s" % self.handler.login_prompt
        self.handler.handle_new_user("jerry")
        self.assertEqual(self.handler.num_errors, 1)
        self.assertEqual(self.handler.password, None)
        self.assertEqual(self.handler.username, None)
        self.assertEqual(self.handler.state, LogonState.NEW_CONNECTION)
        self.assertEqual(self.handler.state_enum, LogonState)
        self.assertEqual(self.protocol.send_data, [user_name_invalid])
        self.assertEqual(self.handler.protocol.drop_connection_calls, 0)

    ####################################################################
    def test_handle_new_user(self):
        self.handler.state = LogonState.NEW_USER
        player = Player()
        player.name = "jerry"
        logon_handler.player_database.add_player(player)

        message = "<reset><bold><white>Please enter your new password: <reset><concealed>"
        self.handler.handle_new_user("johnny")
        self.assertEqual(self.handler.num_errors, 0)
        self.assertEqual(self.handler.password, None)
        self.assertEqual(self.handler.username, "johnny")
        self.assertEqual(self.handler.state, LogonState.ENTER_NEW_PASSWORD)
        self.assertEqual(self.handler.state_enum, LogonState)
        self.assertEqual(self.protocol.send_data, [message])
        self.assertEqual(self.handler.protocol.drop_connection_calls, 0)

    ####################################################################
    def test_handle_enter_new_password(self):
        self.handler.state = LogonState.ENTER_NEW_PASSWORD
        self.handler.username = "johnny"
        player = Player(player_id=17)
        player.name = "jerry"
        logon_handler.player_database.add_player(player)

        message = "<clearscreen><reset><bold><white>Thank you! You are now entering the realm...\r\n<reset>"

        self.assertEqual(logon_handler.player_database.find("johnny"), None)
        self.handler.handle_enter_new_password("pass")
        self.assertEqual(self.handler.num_errors, 0)
        self.assertEqual(self.handler.password, None)
        self.assertEqual(self.handler.username, "johnny")
        self.assertEqual(self.handler.state, LogonState.ENTER_NEW_PASSWORD)
        self.assertEqual(self.handler.state_enum, LogonState)
        self.maxDiff = None
        self.assertEqual(self.protocol.send_data, [message, welcome_message.replace("jerry", "johnny"), stats_message.replace("jerry", "johnny")])
        self.assertEqual(self.handler.protocol.drop_connection_calls, 0)
        player = logon_handler.player_database.find("johnny")
        self.assertEqual(player.name, "johnny")
        self.assertEqual(player.password, "pass")
        self.assertEqual(player.active, False)
        self.assertEqual(player.logged_in, True)
        self.assertEqual(player.armor, None)
        self.assertEqual(player.weapon, None)
        self.assertEqual(player.rank, PlayerRank.REGULAR)
        self.assertEqual(player.newbie, False)
        self.assertEqual(player.protocol, self.handler.protocol)
        self.assertEqual(self.handler.protocol.drop_connection_calls, 0)

    ####################################################################
    def test_handle_enter_password(self):
        self.handler.state = LogonState.ENTER_PASSWORD
        self.handler.username = "jerry"
        self.handler.password = "something"
        player = Player()
        player.name = "jerry"
        player.password = "something"
        logon_handler.player_database.add_player(player)

        message = "<reset><bold><red>The password is incorrect.\r\n" + self.handler.login_prompt
        self.assertEqual(self.handler.num_errors, 0)
        self.handler.handle_enter_password("wrong")
        self.assertEqual(self.handler.num_errors, 1)
        self.assertEqual(self.handler.password, "something")
        self.assertEqual(self.handler.username, "jerry")
        self.assertEqual(self.handler.state, LogonState.NEW_CONNECTION)
        self.assertEqual(self.protocol.send_data, [message])
        self.assertEqual(self.handler.protocol.drop_connection_calls, 0)

        message = "<clearscreen><reset><bold><white>Thank you! You are now entering the realm...\r\n<reset>"
        self.protocol.send_data = []
        self.handler.num_errors = 0
        self.handler.state = LogonState.ENTER_PASSWORD
        self.handler.handle_enter_password("something")
        self.assertEqual(self.handler.num_errors, 0)
        self.assertEqual(self.handler.state, LogonState.ENTER_PASSWORD)
        self.assertEqual(self.protocol.send_data, [message])

    ####################################################################
    def test_enter_game(self):
        player = Player(player_id=17)
        player.name = "jerry"
        player.protocol = self.handler.protocol
        logon_handler.player_database.add_player(player)
        self.handler.username = "jerry"

        self.handler.hung_up = mock.MagicMock()

        self.handler.enter_game(newbie=True)
        self.assertEqual(self.handler.protocol.drop_connection_calls, 0)
        self.assertEqual(self.handler.hung_up.call_count, 0)

        self.assertEqual(len(self.protocol.handlers), 2)
        self.assertIsInstance(self.protocol.handlers[0], GameHandler)
        self.assertIsInstance(self.protocol.handlers[1], TrainingHandler)
        self.assertEqual(self.protocol.send_data, [welcome_message, stats_message])
        self.assertEqual(player.active, False)
        self.assertEqual(player.newbie, False)

    ####################################################################
    def test_enter_game__already_logged_in(self):
        player = Player(player_id=17)
        player.name = "jerry"
        player.logged_in = True
        player.protocol = self.handler.protocol
        logon_handler.player_database.add_player(player)
        self.handler.username = "jerry"

        self.handler.hung_up = mock.MagicMock()

        self.handler.enter_game(newbie=True)
        self.assertEqual(self.handler.protocol.drop_connection_calls, 1)
        self.assertEqual(self.handler.hung_up.call_count, 1)

        self.assertEqual(len(self.protocol.handlers), 2)
        self.assertIsInstance(self.protocol.handlers[0], GameHandler)
        self.assertIsInstance(self.protocol.handlers[1], TrainingHandler)
        welcome_message = """\
<magenta><bold>Welcome to SimpleMUD, jerry!\r
You must train your character with your desired stats,\r
before you enter the realm.\r\n\r\n"""
        stats_message = """\
<white><bold>---------------------- Your Stats ----------------------\r
<dim>Player: jerry\r
Stat Points Left: 18\r
1) Strength: 1\r
2) Health: 1\r
3) Agility: 1\r
<bold>--------------------------------------------------------\r
Enter 1, 2, or 3 to add a stat point, or "quit" to go back: """
        self.maxDiff = None
        self.assertEqual(self.protocol.send_data, [welcome_message, stats_message])
        self.assertEqual(player.active, False)
        self.assertEqual(player.newbie, False)

    ####################################################################
    def test_enter_game__no_player(self):
        self.handler.username = "jerry"
        self.assertEqual(self.protocol.send_data, [])
        self.handler.enter_game(newbie=True)
        self.assertEqual(self.handler.protocol.drop_connection_calls, 1)
        self.assertEqual(self.protocol.send_data, ["Cannot find player!"])

    ####################################################################
    def test_is_invalid_name(self):
        self.assertEqual(self.handler.is_invalid_name(""), True)
        self.assertEqual(self.handler.is_invalid_name("new"), True)
        self.assertEqual(self.handler.is_invalid_name("1jerry"), True)
        self.assertEqual(self.handler.is_invalid_name("j1jerry"), False)
        self.assertEqual(self.handler.is_invalid_name("jerry"), False)

    ####################################################################
    def test_handle(self):
        self.handler.handle_new_connection = mock.MagicMock()
        self.handler.handle_new_user = mock.MagicMock()
        self.handler.handle_enter_new_password = mock.MagicMock()
        self.handler.handle_enter_password = mock.MagicMock()

        self.handler.state = LogonState.NEW_CONNECTION
        self.assertEqual(self.handler.handle_new_connection.call_count, 0)
        self.assertEqual(self.handler.handle_new_user.call_count, 0)
        self.assertEqual(self.handler.handle_enter_new_password.call_count, 0)
        self.assertEqual(self.handler.handle_enter_password.call_count, 0)
        self.handler.handle("abc")
        self.assertEqual(self.handler.handle_new_connection.call_count, 1)
        self.assertEqual(self.handler.handle_new_user.call_count, 0)
        self.assertEqual(self.handler.handle_enter_new_password.call_count, 0)
        self.assertEqual(self.handler.handle_enter_password.call_count, 0)

        self.handler.state = LogonState.NEW_USER
        self.handler.handle("abc")
        self.assertEqual(self.handler.handle_new_connection.call_count, 1)
        self.assertEqual(self.handler.handle_new_user.call_count, 1)
        self.assertEqual(self.handler.handle_enter_new_password.call_count, 0)
        self.assertEqual(self.handler.handle_enter_password.call_count, 0)

        self.handler.state = LogonState.ENTER_NEW_PASSWORD
        self.handler.handle("abc")
        self.assertEqual(self.handler.handle_new_connection.call_count, 1)
        self.assertEqual(self.handler.handle_new_user.call_count, 1)
        self.assertEqual(self.handler.handle_enter_new_password.call_count, 1)
        self.assertEqual(self.handler.handle_enter_password.call_count, 0)

        self.handler.state = LogonState.ENTER_PASSWORD
        self.handler.handle("abc")
        self.assertEqual(self.handler.handle_new_connection.call_count, 1)
        self.assertEqual(self.handler.handle_new_user.call_count, 1)
        self.assertEqual(self.handler.handle_enter_new_password.call_count, 1)
        self.assertEqual(self.handler.handle_enter_password.call_count, 1)

    ####################################################################
    def test_enter(self):
        self.handler.enter()
        self.assertEqual(self.protocol.send_data, ['<bold><green>Welcome to my game world! \r\n<white>Please enter your name, or "new" if you are a new user: <reset>'])
        self.assertEqual(self.handler.protocol.drop_connection_calls, 0)
