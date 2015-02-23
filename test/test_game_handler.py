import unittest
import os
from item import item_database

os.environ["SIMPLE_MUD_LOAD_PLAYERS"] = "false"
from player import PlayerDatabase, Player, PlayerRank
import game_handler
from logon_handler import LogonHandler
from test_utils import MockProtocol


########################################################################
class GameHandlerTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        game_handler.player_database = PlayerDatabase()
        MockProtocol.set_handler_class(handler_class=LogonHandler)

        self.protocol = MockProtocol()
        self.player = Player(28)
        self.player.name = "jerry"
        game_handler.player_database.add_player(self.player)

        self.protocol.remove_handler()
        self.player.protocol = self.protocol
        self.protocol.add_handler(game_handler.GameHandler(self.protocol, self.player))
        self.handler = self.protocol.handler

        self.other_protocol = MockProtocol()
        self.other_player = Player(29)
        self.other_player.name = "john"
        self.other_player.logged_in = True
        self.other_player.active = True
        game_handler.player_database.add_player(self.other_player)

        self.other_protocol.remove_handler()
        self.other_player.protocol = self.other_protocol
        self.other_protocol.add_handler(game_handler.GameHandler(self.other_protocol, self.other_player))
        self.other_handler = self.other_protocol.handler

        self.other_protocol.send_data = []
        self.protocol.send_data = []

        self.assertEqual(len(list(game_handler.player_database.all())), 2)

        current_room = self.player.room
        current_room.add_item(item_database.find(55))
        current_room.add_item(item_database.find(33))
        current_room.money = 220
        self.status_line = "<clearline><carriage_return><white><bold>[<green>10<white>/10] <reset>"
        self.maxDiff = None

    ####################################################################
    def test_handle_last_command(self):
        self.fail()

    ####################################################################
    def test_handle_chat(self):
        self.handler.handle("chat hello there")
        self.assertEqual(self.protocol.send_data, ["<white><bold>jerry chats: hello there<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, ["<white><bold>jerry chats: hello there<newline>",
                                                         self.status_line])

    ####################################################################
    def test_handle_experience(self):
        self.handler.handle("experience")
        self.assertEqual(self.protocol.send_data, ["<bold><white>Level:       1<newline>Experience:  0/139 (0%)<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, [])
        self.player.experience = 20

        self.protocol.send_data = []
        self.handler.handle("exp")
        self.assertEqual(self.protocol.send_data, ["<bold><white>Level:       1<newline>Experience:  20/139 (14%)<newline>",
                                                   self.status_line])

    ####################################################################
    def test_handle_inventory(self):
        self.handler.handle("inventory")
        self.assertEqual(self.protocol.send_data, ["<bold><white>-------------------------------- Your Inventory --------------------------------<newline>"
                                                   " Items:  <newline>"
                                                   " Weapon: NONE!<newline>"
                                                   " Armor:  NONE!<newline>"
                                                   " Money:  $0<newline>"
                                                   "--------------------------------------------------------------------------------<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, [])

        item = item_database.find(55)
        self.player.use_armor(item)


        self.protocol.send_data = []
        self.handler.handle("i")
        self.assertEqual(self.protocol.send_data, ["<bold><white>-------------------------------- Your Inventory --------------------------------<newline>"
                                                   " Items:  <newline>"
                                                   " Weapon: NONE!<newline>"
                                                   " Armor:  Platemail Armor of Power<newline>"
                                                   " Money:  $0<newline>"
                                                   "--------------------------------------------------------------------------------<newline>",
                                                   self.status_line])

    ####################################################################
    def test_handle_stats(self):
        self.handler.handle("stats")
        self.assertEqual(self.protocol.send_data, ["<bold><white>--------------------------------- Your Stats ----------------------------------<newline>"
                                                   "Name:        jerry<newline>"
                                                   "Rank:        REGULAR<newline>"
                                                   "HP/Max:      10/10     (100%)<newline>"
                                                   "<bold><white>Level:       1<newline>"
                                                   "Experience:  0/139 (0%)<newline>"
                                                   "Strength:    1     Accuracy:       3<newline>"
                                                   "Health:      1     Dodging:        3<newline>"
                                                   "Agility:     1     Strike Damage:  0<newline>"
                                                   "StatPoints:  18    Damage Absorb:  0<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, [])

        item = item_database.find(55)
        self.player.use_armor(item)
        self.player.experience = 110


        self.protocol.send_data = []
        self.handler.handle("st")
        self.assertEqual(self.protocol.send_data, ["<bold><white>--------------------------------- Your Stats ----------------------------------<newline>"
                                                   "Name:        jerry<newline>"
                                                   "Rank:        REGULAR<newline>"
                                                   "HP/Max:      10/10     (100%)<newline>"
                                                   "<bold><white>Level:       1<newline>"
                                                   "Experience:  110/139 (79%)<newline>"
                                                   "Strength:    1     Accuracy:       13<newline>"
                                                   "Health:      1     Dodging:        63<newline>"
                                                   "Agility:     1     Strike Damage:  10<newline>"
                                                   "StatPoints:  18    Damage Absorb:  5<newline>",
                                                   self.status_line])

    ####################################################################
    def test_store_list(self):
        result = self.handler.store_list(5)
        expected = "<reset><white><bold>" \
                   "--------------------------------------------------------------------------------<newline>" \
                   " Item                           | Price<newline>" \
                   "--------------------------------------------------------------------------------<newline>" \
                   " Rapier                         | 1500<newline>" \
                   " Sabre                          | 1600<newline>" \
                   " Cutlass                        | 1700<newline>" \
                   " Golden Rapier                  | 5000<newline>" \
                   "--------------------------------------------------------------------------------"
        self.assertEqual(expected, result)

    ####################################################################
    def test_handle_quit(self):
        self.player.active = True
        self.player.logged_in = True
        self.handler.handle("quit")
        self.assertEqual(self.player.active, False)
        self.assertEqual(self.player.logged_in, False)
        self.assertEqual(self.player.protocol, None)
        self.assertEqual(self.protocol.send_data, [])
        self.assertEqual(self.other_protocol.send_data, ["<red><bold>jerry has left the realm.<newline>", self.status_line])

    ####################################################################
    def test_handle_remove(self):
        self.fail()

    ####################################################################
    def test_handle_use(self):
        self.fail()

    ####################################################################
    def test_handle_whisper(self):
        self.fail()

    ####################################################################
    def test_handle_who(self):
        self.fail()

    ####################################################################
    def test_handle_kick(self):
        self.handler.handle("kick john")
        self.assertEqual(self.protocol.send_data, ["<red>You do not have permission to do so<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, [])
        self.protocol.send_data = []

        self.player.rank = PlayerRank.ADMIN

        self.other_player.active = True
        self.other_player.logged_in = True

        self.handler.handle("kick john")
        self.assertEqual(self.protocol.send_data, ["<red><bold>john has been kicked by jerry!!!<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, [])
        self.assertEqual(self.other_player.protocol, None)
        self.assertEqual(self.other_player.active, False)
        self.assertEqual(self.other_player.logged_in, False)

    ####################################################################
    def test_handle_announce(self):
        self.handler.handle("announce hello there")
        self.assertEqual(self.protocol.send_data, ["<red>You do not have permission to do so<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, [])
        self.protocol.send_data = []

        self.player.rank = PlayerRank.ADMIN

        self.handler.handle("announce hello there")
        self.assertEqual(self.protocol.send_data, ["<cyan><bold>System Announcement: hello there<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, ["<cyan><bold>System Announcement: hello there<newline>",
                                                         self.status_line])

    ####################################################################
    def test_handle_change_rank(self):
        self.handler.handle("changerank john ADMIN")
        self.assertEqual(self.protocol.send_data, ["<red>You do not have permission to do so<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, [])
        self.assertEqual(self.other_player.rank, PlayerRank.REGULAR)

        self.protocol.send_data = []
        self.player.rank = PlayerRank.ADMIN
        self.handler.handle("changerank john ADMIN")
        self.assertEqual(self.protocol.send_data, ["<green><bold>john's rank has been changed to: ADMIN<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, ["<green><bold>john's rank has been changed to: ADMIN<newline>",
                                                         self.status_line])

        self.assertEqual(self.other_player.rank, PlayerRank.ADMIN)

    ####################################################################
    def test_handle_reload(self):
        self.fail()

    ####################################################################
    def test_handle_shutdown(self):
        self.fail()

    ####################################################################
    def test_enter(self):
        self.handler.last_command = "wrong"
        self.player.logged_in = False
        self.player.active = False
        self.handler.enter()
        self.assertEqual(self.handler.last_command, "")
        self.assertEqual(self.player.logged_in, True)
        self.assertEqual(self.player.active, True)
        self.assertEqual(self.protocol.send_data, ["<bold><green>jerry has entered the realm.<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, ["<bold><green>jerry has entered the realm.<newline>",
                                                         self.status_line])

    ####################################################################
    def test_leave(self):
        self.player.logged_in = True
        self.player.active = True
        self.handler.leave()
        self.assertEqual(self.player.logged_in, True)
        self.assertEqual(self.player.active, False)
        self.assertEqual(self.protocol.send_data, [])
        self.assertEqual(self.player.protocol, self.protocol)
        self.assertEqual(self.other_protocol.send_data, ["<bold><green>jerry has left the realm.<newline>",
                                                         self.status_line])

    ####################################################################
    def test_leave__protocol_closed(self):
        self.player.logged_in = True
        self.player.active = True
        self.protocol.closed = True
        self.handler.leave()
        self.assertEqual(self.player.logged_in, False)
        self.assertEqual(self.player.active, False)
        self.assertEqual(self.protocol.send_data, [])
        self.assertEqual(self.player.protocol, None)
        self.assertEqual(self.other_protocol.send_data, ["<bold><green>jerry has left the realm.<newline>",
                                                         self.status_line])

    ####################################################################
    def test_hung_up(self):
        self.player.logged_in = True
        self.player.active = True
        self.assertEqual(self.protocol.drop_connection_calls, 0)
        self.handler.hung_up()
        self.assertEqual(self.player.logged_in, False)
        self.assertEqual(self.player.active, False)
        self.assertEqual(self.protocol.send_data, [])
        self.assertEqual(self.protocol.drop_connection_calls, 1)
        self.assertEqual(self.player.protocol, None)
        self.assertEqual(self.other_protocol.send_data, ["<red><bold>jerry has suddenly disappeared from the realm.<newline>",
                                                         self.status_line])

    ####################################################################
    def test_flooded(self):
        self.player.logged_in = True
        self.player.active = True
        self.assertEqual(self.protocol.drop_connection_calls, 0)
        self.handler.flooded()
        self.assertEqual(self.player.logged_in, False)
        self.assertEqual(self.player.active, False)
        self.assertEqual(self.protocol.send_data, [])
        self.assertEqual(self.protocol.drop_connection_calls, 1)
        self.assertEqual(self.player.protocol, None)
        self.assertEqual(self.other_protocol.send_data, ["<red><bold>jerry has been kicked out for flooding!<newline>",
                                                         self.status_line])

    ####################################################################
    def test_send_global(self):
        self.handler.send_global("This is a test")
        self.assertEqual(self.protocol.send_data, ["This is a test<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, ["This is a test<newline>",
                                                         self.status_line])

    ####################################################################
    def test_send_game(self):
        # Goes to the active players
        self.player.active = False
        self.handler.send_game("This is a test")
        self.assertEqual(self.protocol.send_data, [])

        self.assertEqual(self.other_protocol.send_data, ["This is a test<newline>",
                                                         self.status_line])

    ####################################################################
    def test_logout_message(self):
        # Goes to the active players
        self.player.active = False
        self.handler.logout_message("This is a test")
        self.assertEqual(self.protocol.send_data, [])

        self.assertEqual(self.other_protocol.send_data, ["<red><bold>This is a test<newline>",
                                                         self.status_line])

    ####################################################################
    def test_announce(self):
        self.handler.announce("This is a test")
        self.assertEqual(self.protocol.send_data, ["<cyan><bold>System Announcement: This is a test<newline>",
                                                   self.status_line])

        self.assertEqual(self.other_protocol.send_data, ["<cyan><bold>System Announcement: This is a test<newline>",
                                                         self.status_line])

    ####################################################################
    def test_whisper(self):
        ### whisper to unknown user
        self.handler.whisper("This is a test", "user")

        self.assertEqual(self.protocol.send_data, ["<red><bold>Error, cannot find user.<newline>",
                                                   self.status_line])
        self.assertEqual(self.other_protocol.send_data, [])

        self.protocol.send_data = []
        ### whisper to logged_in user
        self.handler.whisper("This is a test", "john")
        self.assertEqual(self.protocol.send_data, [])
        self.assertEqual(self.other_protocol.send_data, ["<yellow>jerry whispers to you: <reset>This is a test<newline>",
                                                         self.status_line])

    ####################################################################
    def test_who_list(self):
        self.fail()

    ####################################################################
    def test_print_help(self):
        self.fail()

    ####################################################################
    def test_print_room(self):
        description = self.handler.print_room(self.player.room)
        expected = "<newline><bold><white>Town Square<newline>" \
                   "<magenta>You are in the town square. This is the central meeting place for the realm.<newline>" \
                   "<green>exits: NORTH, EAST, SOUTH, WEST<newline>" \
                   "<yellow>You see: $220, Platemail Armor of Power, Cutlass (OBSOLETE, PLEASE DROP IN TOWN SQUARE)<newline>"
        self.assertEqual(description, expected)

    ####################################################################
    def test_print_stats(self):
        self.fail()

    ####################################################################
    def test_print_experience(self):
        self.fail()

    ####################################################################
    def test_print_inventory(self):
        self.fail()
