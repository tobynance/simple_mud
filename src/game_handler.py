from attributes import PlayerRank, GameState
import telnet
from telnet import magenta, bold, white, reset


########################################################################
class GameHandler(telnet.MudTelnetHandler):
    state_enum = []
    initial_state = None
    timer = None
    running = False

    ####################################################################
    def __init__(self, connection, player):
        super(GameHandler, self).__init__(connection)
        self.player = player
        self.last_command = None

    ####################################################################
    # Handler Methods                                                ###
    ####################################################################
    ####################################################################
    def handle(self, data):
        """
        This handles incoming commands. Anything passed into this
        function is assumed to be a complete command from a client.
        """

        # check if the player wants to repeat a command
        if data == "/":
            data = self.last_command
        else:
            # if not, record the command
            self.last_command = data

        first_word, rest = data.split(None, 1)

        # REGULAR access commands
        if first_word in ["chat", ":"]:
            message = "".join([magenta, bold, self.player.get_name(), " chats: ", white, reset])
            self.send_game(message)
            return

    ####################################################################
    def goto_train(self): pass

    ####################################################################
    # Sending Methods                                                ###
    ####################################################################
    ####################################################################
    @staticmethod
    def send_global(text): pass

    ####################################################################
    @staticmethod
    def send_game(text): pass

    ####################################################################
    @staticmethod
    def logout_message(reason): pass

    ####################################################################
    @staticmethod
    def announce(announcement): pass

    ####################################################################
    def whisper(self, message, player): pass

    ####################################################################
    # various status-printing methods                                ###
    ####################################################################
    ####################################################################
    @staticmethod
    def who_list(who): pass

    ####################################################################
    @staticmethod
    def print_help(player_rank=PlayerRank.REGULAR): pass

    ####################################################################
    def print_stats(self): pass

    ####################################################################
    def print_experience(self): pass

    ####################################################################
    def print_inventory(self): pass

    ####################################################################
    def print_products(self): pass

    ####################################################################
    def buy_product(self, obj_name_or_id): pass

    ####################################################################
    def print_map(self): pass

    ####################################################################
    def print_item_stats(self, item_name): pass

    ####################################################################
    def print_skills(self, player_rank): pass

    ####################################################################
    def sell_item(self, item_name): pass

    ####################################################################
    # Inventory Methods                                              ###
    ####################################################################
    ####################################################################
    def use_item(self, item_name): pass

    ####################################################################
    def remove_item(self, item_name): pass

    ####################################################################
    # Accessors                                                      ###
    ####################################################################
    ####################################################################
    @staticmethod
    def get_timer():
        return GameHandler.timer

    ####################################################################
    @staticmethod
    def get_running():
        return GameHandler.running

    ####################################################################
    # Map Functions Added in Chapter 9                               ###
    ####################################################################
    ####################################################################
    @staticmethod
    def print_room(room): pass

    ####################################################################
    @staticmethod
    def send_room(text, room): pass

    ####################################################################
    def move(self, direction): pass

    ####################################################################
    def get_item(self, item_name): pass

    ####################################################################
    def drop_item(self, item_name): pass

    ####################################################################
    # Enemy Functions Added in Chapter 10                            ###
    ####################################################################
    ####################################################################
    @staticmethod
    def enemy_attack(enemy): pass

    ####################################################################
    @staticmethod
    def player_killed(player): pass

    ####################################################################
    def player_attack(self, enemy): pass

    ####################################################################
    @staticmethod
    def enemy_killed(enemy, player): pass
