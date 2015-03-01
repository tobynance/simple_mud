import logging
import re
from enum import Enum
from game_handler import GameHandler
from mud.models import Player
import telnet

logger = logging.getLogger(__name__)

MAX_ERRORS = 6
LogonState = Enum("LogonState", "NEW_CONNECTION ENTER_PASSWORD")


########################################################################
class LogonHandler(telnet.BaseStateDispatchHandler):
    state_enum = LogonState
    initial_state = LogonState.NEW_CONNECTION
    login_prompt = '<white>Please enter your name: <reset>'

    ####################################################################
    def __init__(self, protocol):
        super(LogonHandler, self).__init__(protocol)
        self.state = self.initial_state
        self.num_errors = 0
        self.player_id = None

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
            player = Player.objects.filter(user__username=username).first()
            if player is None:
                self.num_errors += 1
                self.send("<bold><red>Sorry, user <green>%s<red> does not exist.\r\n%s" % (username, self.login_prompt))
            elif player.logged_in:
                self.num_errors += 1
                self.send("<bold><red>Sorry, user <green>%s<red> is logged in.\r\n%s" % (username, self.login_prompt))
            else:
                self.state = LogonState.ENTER_PASSWORD
                self.player_id = player.id
                self.send("<bold><white>Please enter your password: <reset><concealed>")

    ####################################################################
    def handle_enter_password(self, password):
        player = Player.objects.get(id=self.player_id)
        if password == player.user.password:
            self.send("<clearscreen><reset><bold><white>Thank you! You are now entering the realm...\r\n<reset>")
            self.enter_game(newbie=False)
        else:
            self.num_errors += 1
            self.state = LogonState.NEW_CONNECTION
            self.send("<reset><bold><red>The password is incorrect.\r\n" + self.login_prompt)

    ####################################################################
    def enter_game(self, newbie):
        player = Player.objects.filter(id=self.player_id).first()
        if player is None:
            self.send("Cannot find player!")
            self.protocol.drop_connection()
            return
        if player.logged_in:
            player.protocol.drop_connection()
            player.protocol.handler.hung_up()
            player.protocol.clear_handlers()
        player.newbie = newbie
        player.logged_in = True

        player.protocol = self.protocol
        player.protocol.remove_handler()
        player.protocol.add_handler(GameHandler(self.protocol, player))

    ####################################################################
    def enter(self):
        super(LogonHandler, self).enter()
        self.send('<bold><green>Welcome to my game world! \r\n<white>Please enter your name: <reset>')

    ####################################################################
    def is_invalid_name(self, name):
        if name.lower() == "new":
            return True
        name_pattern = re.compile("^([a-zA-Z][a-zA-Z_0-9]{2,15})$")
        match = name_pattern.match(name)
        return match is None
