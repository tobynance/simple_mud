import logging
import re
from enum import Enum
from game_handler import GameHandler
import player
import telnet

logger = logging.getLogger(__name__)

MAX_ERRORS = 6
LogonState = Enum("LogonState", "NEW_CONNECTION NEW_USER ENTER_NEW_PASSWORD ENTER_PASSWORD")


########################################################################
class LogonHandler(telnet.BaseStateDispatchHandler):
    state_enum = LogonState
    initial_state = LogonState.NEW_CONNECTION
    login_prompt = '<white>Please enter your name, or "new" if you are a new user: <reset>'

    ####################################################################
    def __init__(self, protocol):
        super(LogonHandler, self).__init__(protocol)
        self.state = self.initial_state
        self.num_errors = 0
        self.username = None
        self.password = None

    ####################################################################
    def may_continue(self):
        if self.num_errors >= MAX_ERRORS:
            self.send("<bold><red>Too many errors\r\n<reset>")
            self.protocol.drop_connection()
            logger.warn("Dropped user for too many errors during login")
            return False
        else:
            return True

    ####################################################################
    def handle_new_connection(self, username):
        if self.may_continue():
            if username == "new":
                self.state = LogonState.NEW_USER
                self.send("<bold><white>Please enter your new login name: <reset>")
            else:
                p = player.player_database.find_full(username)
                if p is None:
                    self.num_errors += 1
                    self.send("<bold><red>Sorry, user <green>%s<red> does not exist.\r\n%s" % (username, self.login_prompt))
                elif p.logged_in:
                    self.num_errors += 1
                    self.send("<bold><red>Sorry, user <green>%s<red> is logged in.\r\n%s" % (username, self.login_prompt))
                else:
                    self.state = LogonState.ENTER_PASSWORD
                    self.username = username
                    self.password = p.password
                    self.send("<bold><white>Please enter your password: <reset><concealed>")

    ####################################################################
    def handle_new_user(self, username):
        if self.may_continue():
            p = player.player_database.find_full(username)
            if p is not None:
                self.num_errors += 1
                self.state = LogonState.NEW_CONNECTION
                self.send("<bold><red>Sorry, the name <green>%s<red> is already used.\r\n%s" % (username, self.login_prompt))
                return
            elif self.is_invalid_name(username):
                self.num_errors += 1
                self.state = LogonState.NEW_CONNECTION
                self.send("<bold><red>Sorry, the name <green>%s<red> contains invalid characters.\r\n%s" % (username, self.login_prompt))
                return
            else:
                self.state = LogonState.ENTER_NEW_PASSWORD
                self.username = username
                self.send("<reset><bold><white>Please enter your new password: <reset><concealed>")
                return

    ####################################################################
    def handle_enter_new_password(self, password):
        if len(password) < 3:
            self.num_errors += 1
            self.send("<reset><bold><red>Password must be at least 3 characters in length\r\n")
            self.send("<reset><bold><white>Please enter your new password: <reset><concealed>")
            return
        else:
            self.send("<clearscreen><reset><bold><white>Thank you! You are now entering the realm...\r\n<reset>")
            p = player.Player()
            p.name = self.username
            p.password = password
            player.player_database.add_player(p)
            self.enter_game(newbie=True)

    ####################################################################
    def handle_enter_password(self, password):
        if password == self.password:
            self.send("<clearscreen><reset><bold><white>Thank you! You are now entering the realm...\r\n<reset>")
            self.enter_game(newbie=False)
        else:
            self.num_errors += 1
            self.state = LogonState.NEW_CONNECTION
            self.send("<reset><bold><red>The password is incorrect.\r\n" + self.login_prompt)

    ####################################################################
    def enter_game(self, newbie):
        p = player.player_database.find_full(self.username)
        if p is None:
            self.send("Cannot find player!")
            self.protocol.drop_connection()
            return
        if p.logged_in:
            p.protocol.drop_connection()
            p.protocol.handler.hung_up()
            p.protocol.clear_handlers()
        p.newbie = newbie
        p.logged_in = True

        p.protocol = self.protocol
        p.protocol.remove_handler()
        p.protocol.add_handler(GameHandler(self.protocol, p))

    ####################################################################
    def enter(self):
        super(LogonHandler, self).enter()
        self.send('<bold><green>Welcome to my game world! \r\n<white>Please enter your name, or "new" if you are a new user: <reset>')

    ####################################################################
    def is_invalid_name(self, name):
        if name.lower() == "new":
            return True
        name_pattern = re.compile("^([a-zA-Z][a-zA-Z_0-9]{2,15})$")
        match = name_pattern.match(name)
        return match is None
