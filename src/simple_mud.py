from attributes import LogonState
from player import PlayerDatabase
import telnet_server
from telnet_server import bold, green, white, reset, red, bwhite


########################################################################
class LogonHandler(telnet_server.MudTelnetHandler):
    state_enum = LogonState
    initial_state = LogonState.NEW_CONNECTION

    ####################################################################
    def __init__(self, protocol):
        super(LogonHandler, self).__init__(protocol)
        self.state = self.initial_state
        self.num_errors = 0
        self.username = None
        self.password = None

    ####################################################################
    def handle_new_connection(self, username):
        login_prompt = "Please enter your name, or \"new\" if you are a new user: " + reset
        if username == "new":
            self.state = LogonState.NEW_USER
            self.send(bold + white + "Please enter your new login name: " + reset)
        else:
            player_database = PlayerDatabase.load()
            player = player_database.find_full(username)
            if player is None:
                self.num_errors += 1
                self.send(bold + red + "Sorry, user " + green + username + red +
                          " does not exist.\r\n" + login_prompt)
            elif player.logged_in:
                self.num_errors += 1
                self.send(bold + red + "Sorry, user " + green + username + red +
                          " is logged in.\r\n" + login_prompt)
            else:
                self.state = LogonState.ENTER_PASSWORD
                self.username = username
                self.password = player.password
                self.send(bold + white + "Please enter your password: " + reset + bwhite)

    ####################################################################
    def handle_new_user(self, username):
        raise NotImplementedError

    ####################################################################
    def initial_connection(self):
        self.send(bold + green + "Welcome to my game world! \r\n" +
                             white + "Please enter your name, or \"new\" if you are a new user: " +
                             reset)


########################################################################
if __name__ == "__main__":
    telnet_server.MudTelnetProtocol.set_handler_class(handler_class=LogonHandler)
    telnet_server.run()
