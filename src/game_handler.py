import logging
import datetime
from attributes import PlayerRank
from player import PlayerDatabase
import telnet
from telnet import magenta, bold, white, reset, green, cyan

logger = logging.getLogger(__name__)


########################################################################
class GameHandler(telnet.MudTelnetHandler):
    system_start_time = datetime.datetime.now()
    running = False

    ####################################################################
    def __init__(self, protocol, player):
        super(GameHandler, self).__init__(protocol)
        self.player = player
        self.last_command = ""
        self._register_data_handler("/", self.handle_last_command)
        self._register_data_handler(["chat", ":"], self.handle_chat)
        self._register_data_handler(["help", "commands"], self.handle_help)
        self._register_data_handler(["inventory", "i"], self.handle_inventory)
        self._register_data_handler(["stats", "st"], self.handle_stats)
        self._register_data_handler("quit", self.handle_quit)
        self._register_data_handler("remove", self.handle_remove)
        self._register_data_handler("use", self.handle_use)
        self._register_data_handler("time", self.handle_time)
        self._register_data_handler("whisper", self.handle_whisper)
        self._register_data_handler("who", self.handle_who)

    ####################################################################
    # Handler Methods                                                ###
    ####################################################################
    ####################################################################
    def handle_last_command(self, data, first_word, rest):
        self.handle(self.last_command)

    ####################################################################
    def handle_chat(self, data, first_word, rest):
        message = "".join([magenta, bold, self.player.get_name(), " chats: ", white, reset])
        self.send_game(message)

    ####################################################################
    def handle_help(self, data, first_word, rest):
        self.send(self.print_help(self.player.rank))

    ####################################################################
    def handle_inventory(self, data, first_word, rest):
        self.send(self.print_inventory())

    ####################################################################
    def handle_stats(self, data, first_word, rest):
        self.send(self.print_stats())

    ####################################################################
    def handle_quit(self, data, first_word, rest):
        self.protocol.drop_connection()
        self.logout_message("%s has left the realm." % self.player.name)
        PlayerDatabase.load().logout(self.player.id)

    ####################################################################
    def handle_remove(self, data, first_word, rest):
        self.remove_item(rest)

    ####################################################################
    def handle_use(self, data, first_word, rest):
        self.use_item(rest)

    ####################################################################
    def handle_time(self, data, first_word, rest):
        message = "The current system time is %s\r\nSystem uptime: %02d:%02d"
        now = datetime.datetime.now()
        now_string = now.strftime("%Y-%m-%d %I:%M:%S %p")
        up_time = now - self.system_start_time
        total_minutes = up_time.seconds // 60
        hours, minutes = divmod(total_minutes, 60)
        message = message % (now_string, hours, minutes)
        self.send(bold + cyan + message)

    ####################################################################
    def handle_whisper(self, data, first_word, rest):
        name, message = rest.split(None, 1)
        self.whisper(message, name)

    ####################################################################
    def handle_who(self, data, first_word, rest):
        if rest:
            name = rest.split(None, 1)[0]
        else:
            name = None
        self.send(self.who_list(name))

    ####################################################################
    # Moderator Methods                                              ###
    ####################################################################
    ####################################################################
    def handle_kick(self, data, first_word, rest):
        if self.player.rank < PlayerRank.MODERATOR:
            logger.warn("player %s tried to use the kick command, but doesn't have permission to do so", self.player.name)
            return
        #PlayerDatabase.load().

    ####################################################################
    def goto_train(self):
        raise NotImplementedError

    ####################################################################
    # Base Handler Methods                                           ###
    ####################################################################
    ####################################################################
    def enter(self):
        logger.info("%s - enter called in %s", self.protocol.transport.getPeer(), self.__class__.__name__)
        self.last_command = ""
        self.player.active = True
        self.player.logged_in = True
        self.send_game(bold + green + self.player.name + " has entered the realm.")
        if self.player.newbie:
            self.goto_train()

    ####################################################################
    def leave(self):
        self.player.active = False
        if self.protocol.closed:
            PlayerDatabase.load().logout(self.player.id)

    ####################################################################
    def hung_up(self):
        self.logout_message("%s has suddenly disappeared from the realm." % self.player.name)

    ####################################################################
    def flooded(self):
        self.logout_message("%s has been kicked out for flooding!" % self.player.name)

    ####################################################################
    # Sending Methods                                                ###
    ####################################################################
    ####################################################################
    @staticmethod
    def send_global(text):
        raise NotImplementedError

    ####################################################################
    @staticmethod
    def send_game(text):
        raise NotImplementedError

    ####################################################################
    @staticmethod
    def logout_message(reason):
        raise NotImplementedError

    ####################################################################
    @staticmethod
    def announce(announcement):
        raise NotImplementedError

    ####################################################################
    def whisper(self, message, player):
        raise NotImplementedError

    ####################################################################
    # various status-printing methods                                ###
    ####################################################################
    ####################################################################
    @staticmethod
    def who_list(who):
        raise NotImplementedError

    ####################################################################
    @staticmethod
    def print_help(player_rank=PlayerRank.REGULAR):
        raise NotImplementedError

    ####################################################################
    def print_stats(self):
        raise NotImplementedError

    ####################################################################
    def print_experience(self):
        raise NotImplementedError

    ####################################################################
    def print_inventory(self):
        raise NotImplementedError

    ####################################################################
    def print_products(self):
        raise NotImplementedError

    ####################################################################
    def buy_product(self, obj_name_or_id):
        raise NotImplementedError

    ####################################################################
    def print_map(self):
        raise NotImplementedError

    ####################################################################
    def print_item_stats(self, item_name):
        raise NotImplementedError

    ####################################################################
    def print_skills(self, player_rank):
        raise NotImplementedError

    ####################################################################
    def sell_item(self, item_name):
        raise NotImplementedError

    ####################################################################
    # Inventory Methods                                              ###
    ####################################################################
    ####################################################################
    def use_item(self, item_name):
        raise NotImplementedError

    ####################################################################
    def remove_item(self, item_name):
        raise NotImplementedError

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
    def print_room(room):
        raise NotImplementedError

    ####################################################################
    @staticmethod
    def send_room(text, room):
        raise NotImplementedError

    ####################################################################
    def move(self, direction):
        raise NotImplementedError

    ####################################################################
    def get_item(self, item_name):
        raise NotImplementedError

    ####################################################################
    def drop_item(self, item_name):
        raise NotImplementedError

    ####################################################################
    # Enemy Functions Added in Chapter 10                            ###
    ####################################################################
    ####################################################################
    @staticmethod
    def enemy_attack(enemy):
        raise NotImplementedError

    ####################################################################
    @staticmethod
    def player_killed(player):
        raise NotImplementedError

    ####################################################################
    def player_attack(self, enemy):
        raise NotImplementedError

    ####################################################################
    @staticmethod
    def enemy_killed(enemy, player):
        raise NotImplementedError
