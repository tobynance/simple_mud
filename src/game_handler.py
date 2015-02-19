import logging
import datetime
import random
from attributes import PlayerRank, ItemType
from item import ItemDatabase
from player import player_database
import telnet
from telnet import bold, white, reset, green, cyan, red, yellow
from training_handler import TrainingHandler

logger = logging.getLogger(__name__)

HELP = white + bold + \
       "--------------------------------- Command List ---------------------------------\r\n" + \
       " /                            - Repeats your last command exactly.\r\n" + \
       " chat <msg>                   - Sends message to everyone in the game\r\n" + \
       " experience                   - Shows your experience statistics\r\n" + \
       " help                         - Shows this menu\r\n" + \
       " inventory                    - Shows a list of your items\r\n" + \
       " quit                         - Allows you to leave the realm.\r\n" + \
       " remove <'weapon'/'armor'>    - Removes your weapon or armor\r\n" + \
       " stats                        - Shows all of your statistics\r\n" + \
       " train                        - Go to train using StatPoints\r\n" + \
       " time                         - Shows the current system time.\r\n" + \
       " use <item>                   - Use an item in your inventory\r\n" + \
       " whisper <who> <msg>          - Sends message to one person\r\n" + \
       " who                          - Shows a list of everyone online\r\n" + \
       " who all                      - Shows a list of everyone\r\n" + \
       " look                         - Shows you the contents of a room\r\n" + \
       " north/east/south/west        - Moves in a direction\r\n" + \
       " get/drop <item>              - Picks up or drops an item on the ground\r\n" + \
       " attack <enemy>               - Attacks an enemy\r\n" + \
       " talk                         - Talks to NPC's in the room\r\n" + \
       " buy <item name / id>         - Buys an item from the store\r\n" + \
       " sell <item name>             - Sells an item to the store\r\n" + \
       " inspect <item name>          - Shows stats of an item\r\n" + \
       " map                          - Shows the map\r\n"

MODERATOR_HELP = yellow + bold + \
                 "------------------------------ Moderator Commands ------------------------------\r\n" + \
                 " kick <who>                   - Kicks a user from the realm\r\n"

ADMIN_HELP = green + bold + \
             "-------------------------------- Admin Commands --------------------------------\r\n" + \
             " kick <who>                   - Kicks a user from the realm\r\n" + \
             " announce <msg>               - Makes a global system announcement\r\n" + \
             " changerank <who> <rank>      - Changes the rank of a player\r\n" + \
             " reload <db>                  - Reloads the requested database\r\n" + \
             " shutdown                     - Shuts the server down\r\n"
HELP_END = white + bold + ("-" * 80) + "\r\n"


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
        self._register_data_handler(["experience", "exp"], self.handle_experience)
        self._register_data_handler(["help", "commands"], self.handle_help)
        self._register_data_handler(["inventory", "i"], self.handle_inventory)
        self._register_data_handler(["stats", "st"], self.handle_stats)
        self._register_data_handler("quit", self.handle_quit)
        self._register_data_handler("remove", self.handle_remove)
        self._register_data_handler("use", self.handle_use)
        self._register_data_handler("time", self.handle_time)
        self._register_data_handler("whisper", self.handle_whisper)
        self._register_data_handler("who", self.handle_who)
        self._register_data_handler("kick", self.handle_kick)
        self._register_data_handler("announce", self.handle_announce)
        self._register_data_handler("changerank", self.handle_change_rank)
        self._register_data_handler("reload", self.handle_reload)
        self._register_data_handler("shutdown", self.handle_shutdown)
        self._register_data_handler("train", self.handle_train)
        self._register_data_handler(True, lambda d, fw, r: self.handle_chat(d, fw, d))  # send whole message to chat

    ####################################################################
    # Handler Methods                                                ###
    ####################################################################
    ####################################################################
    def handle_last_command(self, data, first_word, rest):
        self.handle(self.last_command)

    ####################################################################
    def handle_chat(self, data, first_word, text):
        message = "".join([white, bold, self.player.name, " chats: ", text])
        self.send_game(message)

    ####################################################################
    def handle_experience(self, data, first_word, rest):
        self.player.send_string(self.print_experience())

    ####################################################################
    def handle_help(self, data, first_word, rest):
        self.player.send_string(self.print_help(self.player.rank))

    ####################################################################
    def handle_inventory(self, data, first_word, rest):
        self.player.send_string(self.print_inventory())

    ####################################################################
    def handle_stats(self, data, first_word, rest):
        self.player.send_string(self.print_stats())

    ####################################################################
    def handle_quit(self, data, first_word, rest):
        self.protocol.drop_connection()
        self.logout_message("%s has left the realm." % self.player.name)
        player_database.logout(self.player.id)

    ####################################################################
    def handle_remove(self, data, first_word, remove_target):
        self.remove_item(remove_target)

    ####################################################################
    def handle_use(self, data, first_word, item_name):
        self.use_item(item_name)

    ####################################################################
    def handle_time(self, data, first_word, rest):
        message = "The current system time is %s\r\nSystem uptime: %02d:%02d"
        now = datetime.datetime.now()
        now_string = now.strftime("%Y-%m-%d %I:%M:%S %p")
        up_time = now - self.system_start_time
        total_minutes = up_time.seconds // 60
        hours, minutes = divmod(total_minutes, 60)
        message = message % (now_string, hours, minutes)
        self.player.send_string(bold + cyan + message)

    ####################################################################
    def handle_whisper(self, data, first_word, rest):
        name, message = rest.split(None, 1)
        self.whisper(message, name)

    ####################################################################
    def handle_who(self, data, first_word, rest):
        if rest:
            who = rest.split(None, 1)[0]
        else:
            who = None
        self.player.send_string(self.who_list(who))

    ####################################################################
    # Moderator Methods                                              ###
    ####################################################################
    ####################################################################
    def handle_kick(self, data, first_word, player_name):
        if self.player.rank < PlayerRank.MODERATOR:
            logger.warn("player %s tried to use the kick command, but doesn't have permission to do so", self.player.name)
            return
        kicked_player = player_database.find_logged_in(player_name)
        if kicked_player is None:
            self.player.send_string(red + bold + "Player could not be found.")
            return
        if kicked_player.rank > self.player.rank:
            self.player.send_string(red + bold + "You can't kick that player!")
            return

        kicked_player.protocol.drop_connection()
        self.logout_message("%s has been kicked by %s!!!" % (kicked_player.name, self.player.name))
        player_database.logout(kicked_player.id)

    ####################################################################
    # Admin Methods                                                  ###
    ####################################################################
    ####################################################################
    def handle_announce(self, data, first_word, announcement):
        if self.player.rank < PlayerRank.ADMIN:
            logger.warn("player %s tried to use the announce command, but doesn't have permission to do so", self.player.name)
            return
        self.announce(announcement)

    ####################################################################
    def handle_change_rank(self, data, first_word, rest):
        if self.player.rank < PlayerRank.ADMIN:
            logger.warn("player %s tried to use the changerank command, but doesn't have permission to do so", self.player.name)
            return
        rest = rest.split()
        if len(rest) != 2:
            self.player.send_string(red + bold + "Error: Bad Command")
            return
        name, rank = rest
        other_player = player_database.find(name)
        if other_player is None:
            self.player.send_string(red + bold + "Error: Could not find user " + name)
            return

        if not hasattr(PlayerRank, rank):
            self.player.send_string(red + bold + "Error: Cannot understand rank '%s'" % rank)
            return

        other_player.rank = PlayerRank[rank]
        self.send_game(green + bold + other_player.name + "'s rank has been changed to: %s" + other_player.rank.name)

    ####################################################################
    def handle_reload(self, data, first_word, db):
        if self.player.rank < PlayerRank.ADMIN:
            logger.warn("player %s tried to use the reload command, but doesn't have permission to do so", self.player.name)
            return

        if db == "items":
            ItemDatabase.load()
            self.player.send_string(bold + cyan + "Item Database Reloaded!")

    ####################################################################
    def handle_shutdown(self, data, first_word, rest):
        if self.player.rank < PlayerRank.ADMIN:
            logger.warn("player %s tried to use the shutdown command, but doesn't have permission to do so", self.player.name)
            return
        self.announce("SYSTEM IS SHUTTING DOWN")
        GameHandler.running = False

    ####################################################################
    def handle_train(self, data, first_word, rest):
        self.goto_train()

    ####################################################################
    def goto_train(self):
        self.player.active = False
        self.protocol.add_handler(TrainingHandler(self.protocol, self.player))
        self.logout_message("%s leaves to edit stats" % self.player.name)

    ####################################################################
    # Base Handler Methods                                           ###
    ####################################################################
    ####################################################################
    def enter(self):
        logger.info("%s - enter called in %s", self.protocol.get_remote_address(), self.__class__.__name__)
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
            player_database.logout(self.player.id)

    ####################################################################
    def hung_up(self):
        """
        This notifies the handler that a connection has unexpectedly
        hung up.
        """
        self.logout_message("%s has suddenly disappeared from the realm." % self.player.name)

    ####################################################################
    def flooded(self):
        """
        This notifies the handler that a connection is being kicked
        due to flooding the server.
        """
        self.logout_message("%s has been kicked out for flooding!" % self.player.name)

    ####################################################################
    # Sending Methods                                                ###
    ####################################################################
    ####################################################################
    @staticmethod
    def send_global(text):
        """Sends a string to everyone connected."""
        for player in player_database.all_logged_in():
            player.send_string(text)

    ####################################################################
    @staticmethod
    def send_game(text):
        """Sends a string to everyone 'within the game'"""
        for player in player_database.all_active():
            player.send_string(text)

    ####################################################################
    @staticmethod
    def logout_message(reason):
        """Sends a logout message"""
        GameHandler.send_game(red + bold + reason)

    ####################################################################
    @staticmethod
    def announce(announcement):
        """Sends a system announcement"""
        GameHandler.send_global(cyan + bold + "System Announcement: " + announcement)

    ####################################################################
    def whisper(self, message, player_name):
        """Sends a whisper string to the requested player"""
        other_player = player_database.find_active(player_name)
        if other_player is None:
            self.player.send_string(red + bold + "Error, cannot find user.")
        else:
            other_player.send_string(yellow + self.player.name + " whispers to you: " + reset + message)

    ####################################################################
    # various status-printing methods                                ###
    ####################################################################
    ####################################################################
    @staticmethod
    def who_list(who):
        """This prints up the who-list for the realm."""
        if who == "all":
            players = player_database.all()
        else:
            players = player_database.all_logged_in()

        message = [white, bold]
        message.append("-" * 80)
        message.append("\r\n")
        message.append(" Name             | Level     | Activity | Rank\r\n")
        message.append("-" * 80)
        message.append("\r\n")

        for player in players:
            message.append(player.who_text())

        message.append("-" * 80)
        message.append("\r\n")
        return "".join(message)

    ####################################################################
    @staticmethod
    def print_help(player_rank=PlayerRank.REGULAR):
        """Prints out a help listing based on a user's rank."""
        help_text = [HELP]
        if player_rank >= PlayerRank.MODERATOR:
            help_text.append(MODERATOR_HELP)
        if player_rank >= PlayerRank.ADMIN:
            help_text.append(ADMIN_HELP)
        help_text.append(HELP_END)
        return "".join(help_text)

    ####################################################################
    def print_stats(self):
        """This prints up the stats of the player"""
        stats = [bold, white]
        stats.append("--------------------------------- Your Stats ----------------------------------\r\n")
        stats.append("Name:        %s\r\n" % self.player.name)
        stats.append("Rank:        %s\r\n" % self.player.rank.name)
        stats.append("HP/Max:      %s/%s     (%s%%)\r\n" % (self.player.hit_points, self.player.attributes.MAX_HIT_POINTS, 100 * self.player.hit_points // self.player.attributes.MAX_HIT_POINTS))
        stats.append(self.print_experience())
        stats.append("Strength:    {:<5} Accuracy:       {}\r\n".format(self.player.attributes.STRENGTH, self.player.attributes.ACCURACY))
        stats.append("Health:      {:<5} Dodging:        {}\r\n".format(self.player.attributes.HEALTH, self.player.attributes.DODGING))
        stats.append("Agility:     {:<5} Strike Damage:  {}\r\n".format(self.player.attributes.AGILITY, self.player.attributes.STRIKE_DAMAGE))
        stats.append("StatPoints:  {:<5} Damage Absorb:  {}\r\n".format(self.player.stat_points, self.player.attributes.DAMAGE_ABSORB))
        return "".join(stats)

    ####################################################################
    def print_experience(self):
        """This prints up the experience of the player"""
        need_for_next_level = self.player.need_for_next_level()
        percentage = 100 * self.player.experience // need_for_next_level

        experience_text = [bold, white]
        experience_text.append("Level:       {}\r\n".format(self.player.level))
        experience_text.append("Experience:  {}/{} ({}%)\r\n".format(self.player.experience, need_for_next_level, percentage))
        return "".join(experience_text)

    ####################################################################
    def print_inventory(self):
        inventory_text = [white, bold]
        inventory_text.append("-------------------------------- Your Inventory --------------------------------\r\n")
        inventory_text.append(" Items:  ")
        inventory_text.append(", ".join([item.name for item in self.player.inventory]))
        inventory_text.append("\r\n")
        inventory_text.append(" Weapon: ")
        if self.player.weapon:
            inventory_text.append(self.player.weapon.name)
        else:
            inventory_text.append("NONE!")
        inventory_text.append("\r\n Armor:  ")
        if self.player.armor:
            inventory_text.append(self.player.armor.name)
        else:
            inventory_text.append("NONE!")
        inventory_text.append("\r\n Money:  ${}".format(self.player.money))
        inventory_text.append("\r\n--------------------------------------------------------------------------------")
        return "".join(inventory_text)

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
    def sell_item(self, item_name):
        raise NotImplementedError

    ####################################################################
    # Inventory Methods                                              ###
    ####################################################################
    ####################################################################
    def use_item(self, item_name):
        for item in self.player.inventory:
            if item.name == item_name:
                if item.type == ItemType.WEAPON:
                    self.player.use_weapon(item)
                    return True
                elif item.type == ItemType.ARMOR:
                    self.player.use_armor(item)
                    return True
                elif item.type == ItemType.HEALING:
                    self.player.add_bonuses(item)
                    self.player.add_hit_points(random.randint(item.min, item.max))
                    self.player.drop_item(item)
                    return True
        self.player.send_string(red + bold + "Could not find that item!")
        return False

    ####################################################################
    def remove_item(self, item_name):
        if item_name == "weapon":
            if self.player.weapon:
                self.player.remove_weapon()
                return True
        elif item_name == "armor":
            if self.player.armor:
                self.player.remove_armor()
                return True
        self.player.send_string(red + bold + "Could not remove item!")
        return False

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
