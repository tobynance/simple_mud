import logging
import datetime
import random
from attributes import Direction
import item
import player
import enemy
import room
import store
import telnet
from training_handler import TrainingHandler
from utils import find_all_by_name, double_find_by_name

logger = logging.getLogger(__name__)

HELP = "<white><bold>" + \
       "--------------------------------- Command List ---------------------------------<newline>" + \
       " /                            - Repeats your last command exactly.<newline>" + \
       " chat <msg>                   - Sends message to everyone in the game<newline>" + \
       " experience                   - Shows your experience statistics<newline>" + \
       " help                         - Shows this menu<newline>" + \
       " inventory                    - Shows a list of your items<newline>" + \
       " quit                         - Allows you to leave the realm.<newline>" + \
       " remove <'weapon'/'armor'>    - Removes your weapon or armor<newline>" + \
       " stats                        - Shows all of your statistics<newline>" + \
       " editstats                    - Edit your statistics<newline>" + \
       " train                        - Go to train using StatPoints<newline>" + \
       " time                         - Shows the current system time.<newline>" + \
       " use <item>                   - Use an item in your inventory<newline>" + \
       " whisper <who> <msg>          - Sends message to one person<newline>" + \
       " who                          - Shows a list of everyone online<newline>" + \
       " who all                      - Shows a list of everyone<newline>" + \
       " look                         - Shows you the contents of a room<newline>" + \
       " north/east/south/west        - Moves in a direction<newline>" + \
       " get/drop <item>              - Picks up or drops an item on the ground<newline>" + \
       " attack <enemy>               - Attacks an enemy<newline>" + \
       " talk                         - Talks to NPC's in the room<newline>" + \
       " list                         - List the items an NPC has for sale<newline>" + \
       " buy <item name / id>         - Buys an item from the store<newline>" + \
       " sell <item name>             - Sells an item to the store<newline>" + \
       " inspect <item name>          - Shows stats of an item<newline>" + \
       " map                          - Shows the map<newline>"

MODERATOR_HELP = "<yellow><bold>" + \
                 "------------------------------ Moderator Commands ------------------------------<newline>" + \
                 " kick <who>                   - Kicks a user from the realm<newline>"

ADMIN_HELP = "<green><bold>" + \
             "-------------------------------- Admin Commands --------------------------------<newline>" + \
             " kick <who>                   - Kicks a user from the realm<newline>" + \
             " announce <msg>               - Makes a global system announcement<newline>" + \
             " changerank <who> <rank>      - Changes the rank of a player<newline>" + \
             " reload <db>                  - Reloads the requested database<newline>" + \
             " shutdown                     - Shuts the server down<newline>"
HELP_END = "<white><bold>%s<newline>" % ("-" * 80)


########################################################################
class GameHandler(telnet.BaseCommandDispatchHandler):
    system_start_time = datetime.datetime.now()

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
        self._register_data_handler("editstats", self.handle_editstats)
        self._register_data_handler(["look", "l"], self.handle_look)
        self._register_data_handler(["north", "n"], self.handle_north)
        self._register_data_handler(["east", "e"], self.handle_east)
        self._register_data_handler(["south", "s"], self.handle_south)
        self._register_data_handler(["west", "w"], self.handle_west)
        self._register_data_handler("get", self.handle_get)
        self._register_data_handler("drop", self.handle_drop)
        self._register_data_handler("list", self.handle_list)
        self._register_data_handler("buy", self.handle_buy)
        self._register_data_handler("sell", self.handle_sell)
        self._register_data_handler("clear", self.handle_clear)
        self._register_data_handler(["attack", "a"], self.handle_attack)
        self._register_data_handler(True, self.handle_say)  # send whole message to room chat

    ####################################################################
    # Handler Methods                                                ###
    ####################################################################
    ####################################################################
    def handle_last_command(self, data, first_word, rest):
        self.handle(self.last_command)

    ####################################################################
    def handle_chat(self, data, first_word, text):
        message = "<white><bold>{name} chats: {text}".format(name=self.player.name, text=text)
        self.send_game(message)

    ####################################################################
    def handle_say(self, data, first_word, text):
        message = "<white><bold>{name} says: {text}".format(name=self.player.name, text=data)
        self.send_room(message)

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
        player.player_database.logout(self.player.id)
        self.player.room.remove_player(self.player)
        self.logout_message("%s has left the realm." % self.player.name)

    ####################################################################
    def handle_remove(self, data, first_word, remove_target):
        self.remove_item(remove_target)

    ####################################################################
    def handle_use(self, data, first_word, item_name):
        self.use_item(item_name)

    ####################################################################
    def handle_time(self, data, first_word, rest):
        message = "The current system time is %s<newline>System uptime: %02d:%02d"
        now = datetime.datetime.now()
        now_string = now.strftime("%Y-%m-%d %I:%M:%S %p")
        up_time = now - self.system_start_time
        total_minutes = up_time.seconds // 60
        hours, minutes = divmod(total_minutes, 60)
        message = message % (now_string, hours, minutes)
        self.player.send_string("<bold><cyan>" + message)

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
        if self.player.rank < player.PlayerRank.MODERATOR:
            logger.warn("player %s tried to use the kick command, but doesn't have permission to do so", self.player.name)
            self.player.send_string("<red>You do not have permission to do so<newline>")
            return
        kicked_player = player.player_database.find_logged_in(player_name)
        if kicked_player is None:
            self.player.send_string("<red><bold>Player could not be found.")
            return
        if kicked_player.rank > self.player.rank:
            self.player.send_string("<red><bold>You can't kick that player!")
            return

        player.player_database.logout(kicked_player.id)
        self.logout_message("%s has been kicked by %s!!!" % (kicked_player.name, self.player.name))

    ####################################################################
    # Admin Methods                                                  ###
    ####################################################################
    ####################################################################
    def handle_announce(self, data, first_word, announcement):
        if self.player.rank < player.PlayerRank.ADMIN:
            logger.warn("player %s tried to use the announce command, but doesn't have permission to do so", self.player.name)
            self.player.send_string("<red>You do not have permission to do so<newline>")
            return
        self.announce(announcement)

    ####################################################################
    def handle_change_rank(self, data, first_word, rest):
        if self.player.rank < player.PlayerRank.ADMIN:
            logger.warn("player %s tried to use the changerank command, but doesn't have permission to do so", self.player.name)
            self.player.send_string("<red>You do not have permission to do so<newline>")
            return
        rest = rest.split()
        if len(rest) != 2:
            self.player.send_string("<red><bold>Error: Bad Command")
            return
        name, rank = rest
        other_player = player.player_database.find(name)
        if other_player is None:
            self.player.send_string("<red><bold>Error: Could not find user " + name)
            return

        if not hasattr(player.PlayerRank, rank):
            self.player.send_string("<red><bold>Error: Cannot understand rank '%s'" % rank)
            return

        other_player.rank = player.PlayerRank[rank]
        self.send_game("<green><bold>{name}'s rank has been changed to: {rank}".format(name=other_player.name, rank=other_player.rank.name))

    ####################################################################
    def handle_reload(self, data, first_word, db):
        if self.player.rank < player.PlayerRank.ADMIN:
            logger.warn("player %s tried to use the reload command, but doesn't have permission to do so", self.player.name)
            self.player.send_string("<red>You do not have permission to do so<newline>")
            return

        room.room_database.save()
        player.player_database.save()
        enemy.enemy_database.save()
        item.item_database = item.ItemDatabase.load(force=True)
        room.room_database = room.RoomDatabase.load(force=True)
        store.store_database = store.StoreDatabase.load(force=True)
        for p in player.player_database.all_logged_in():
            p.room = room.room_database.by_id[p.room.id]
            inventory = [i.id for i in p.inventory]
            p.inventory = []
            for item_id in inventory:
                p.inventory.append(item.item_database.by_id[item_id])

        self.player.send_string("<bold><cyan>Item & Room Databases Reloaded!")

    ####################################################################
    def handle_shutdown(self, data, first_word, rest):
        if self.player.rank < player.PlayerRank.ADMIN:
            logger.warn("player %s tried to use the shutdown command, but doesn't have permission to do so", self.player.name)
            self.player.send_string("<red>You do not have permission to do so<newline>")
            return
        self.announce("SYSTEM IS SHUTTING DOWN")
        room.room_database.save()
        player.player_database.save()
        enemy.enemy_database.save()
        telnet.stop()

    ####################################################################
    def handle_train(self, data, first_word, rest):
        if self.player.room.type != room.RoomType.TRAINING_ROOM:
            self.player.send_string("<red><bold>You cannot train here!")
            return
        if self.player.train():
            self.player.send_string("<green><bold>You are now level {}".format(self.player.level))
        else:
            self.player.send_string("<red><bold>You don't have enough experience to train!")

    ####################################################################
    def handle_editstats(self, data, first_word, rest):
        if self.player.room.type != room.RoomType.TRAINING_ROOM:
            self.player.send_string("<red><bold>You cannot edit your stats here!")
            return
        self.goto_train()

    ####################################################################
    def goto_train(self):
        self.player.active = False
        self.protocol.add_handler(TrainingHandler(self.protocol, self.player))
        self.logout_message("%s leaves to edit stats" % self.player.name)

    ####################################################################
    def handle_look(self, data, first_word, rest):
        self.player.send_string(self.print_room(self.player.room))

    ####################################################################
    def handle_north(self, data, first_word, rest):
        self.move(Direction.NORTH)

    ####################################################################
    def handle_east(self, data, first_word, rest):
        self.move(Direction.EAST)

    ####################################################################
    def handle_south(self, data, first_word, rest):
        self.move(Direction.SOUTH)

    ####################################################################
    def handle_west(self, data, first_word, rest):
        self.move(Direction.WEST)

    ####################################################################
    def handle_get(self, data, first_word, rest):
        self.get_item(rest)

    ####################################################################
    def handle_drop(self, data, first_word, rest):
        self.drop_item(rest)

    ####################################################################
    def handle_list(self, data, first_word, rest):
        if self.player.room.type != room.RoomType.STORE:
            self.player.send_string("<red><bold>You're not in a store!")
        self.player.send_string(self.store_list(self.player.room.data))

    ####################################################################
    def handle_buy(self, data, first_word, rest):
        if self.player.room.type != room.RoomType.STORE:
            self.player.send_string("<red><bold>You're not in a store!")
        self.buy(rest)

    ####################################################################
    def handle_sell(self, data, first_word, rest):
        if self.player.room.type != room.RoomType.STORE:
            self.player.send_string("<red><bold>You're not in a store!")
        self.sell(rest)

    ####################################################################
    def handle_clear(self, data, first_word, rest):
        self.player.send_string("<newline>" * 80)

    ####################################################################
    def handle_attack(self, data, first_word, rest):
        self.player.attack(rest)

    ####################################################################
    def store_list(self, store_id):
        this_store = store.store_database.by_id[store_id]
        output = ["<reset><white><bold>%s" % ("-" * 80),
                  " {:<30} | {}".format("Item", "Price"),
                  "-" * 80]
        items = [item.item_database.by_id[item_id] for item_id in this_store.available_items]
        for this_item in items:
            output.append(" {:<30} | {}".format(this_item.name, this_item.price))
        output.append("-" * 80)
        return "<newline>".join(output)

    ####################################################################
    def buy(self, item_name):
        this_store = store.store_database.by_id[self.player.room.data]
        items = [item.item_database.by_id[item_id] for item_id in this_store.available_items]
        purchase_item = double_find_by_name(item_name, items)
        if purchase_item is None:
            self.player.send_string("<red><bold>Sorry, we don't have that item!")
            return
        elif self.player.money < purchase_item.price:
            self.player.send_string("<red><bold>Sorry, but you can't afford that!")
            return
        elif not self.player.pick_up_item(purchase_item):
            self.player.send_string("<red><bold>Sorry, but you can't carry that much!")
            return
        else:
            self.player.money -= purchase_item.price
            self.send_room("<cyan><bold>{} buys a {}".format(self.player.name, purchase_item.name))

    ####################################################################
    def sell(self, item_name):
        this_store = store.store_database.by_id[self.player.room.data]
        sell_item = double_find_by_name(item_name, self.player.inventory)
        if sell_item is None:
            self.player.send_string("<red><bold>Sorry, you don't have that!")
            return
        if not this_store.has(sell_item.id):
            self.player.send_string("<red><bold>Sorry, we don't want that item!")
            return
        self.player.drop_item(sell_item)
        self.player.money += sell_item.price
        self.send_room("<cyan><bold>{} sells a {}".format(self.player.name, sell_item.name))

    ####################################################################
    # Base Handler Methods                                           ###
    ####################################################################
    ####################################################################
    def enter(self):
        logger.info("%s - enter called in %s", self.protocol.get_remote_address(), self.__class__.__name__)
        self.last_command = ""
        self.send_game("<bold><green>{} has entered the realm.".format(self.player.name))
        self.player.active = True
        self.player.logged_in = True
        self.player.room.add_player(self.player)
        if self.player.newbie:
            self.goto_train()
        else:
            self.player.send_string(self.print_room(self.player.room))

    ####################################################################
    def leave(self):
        self.player.active = False
        if self.protocol.closed:
            player.player_database.logout(self.player.id)
        self.player.room.remove_player(self.player)
        self.send_game("<bold><green>{} has left the realm.".format(self.player.name))

    ####################################################################
    def hung_up(self):
        """
        This notifies the handler that a connection has unexpectedly
        hung up.
        """
        player.player_database.logout(self.player.id)
        self.logout_message("%s has suddenly disappeared from the realm." % self.player.name)

    ####################################################################
    def flooded(self):
        """
        This notifies the handler that a connection is being kicked
        due to flooding the server.
        """
        player.player_database.logout(self.player.id)
        self.logout_message("%s has been kicked out for flooding!" % self.player.name)

    ####################################################################
    # Sending Methods                                                ###
    ####################################################################
    ####################################################################
    @staticmethod
    def send_global(text):
        """Sends a string to everyone connected."""
        for p in player.player_database.all_logged_in():
            p.send_string(text)

    ####################################################################
    @staticmethod
    def send_game(text):
        """Sends a string to everyone 'within the game'"""
        for p in player.player_database.all_active():
            p.send_string(text)

    ####################################################################
    @staticmethod
    def logout_message(reason):
        """Sends a logout message"""
        GameHandler.send_game("<red><bold>%s" % reason)

    ####################################################################
    @staticmethod
    def announce(announcement):
        """Sends a system announcement"""
        GameHandler.send_global("<cyan><bold>System Announcement: %s<newline>" % announcement)

    ####################################################################
    def whisper(self, message, player_name):
        """Sends a whisper string to the requested player"""
        other_player = player.player_database.find_active(player_name)
        if other_player is None:
            self.player.send_string("<red><bold>" + "Error, cannot find user.")
        else:
            other_player.send_string("<yellow>{} whispers to you: <reset>{}".format(self.player.name, message))

    ####################################################################
    # various status-printing methods                                ###
    ####################################################################
    ####################################################################
    @staticmethod
    def who_list(who):
        """This prints up the who-list for the realm."""
        if who == "all":
            players = player.player_database.all()
        else:
            players = player.player_database.all_logged_in()

        message = ["<white><bold>{}<newline>".format("-" * 80),
                   " Name             | Level     | Activity | Rank<newline>",
                   "-" * 80, "<newline>"]

        for p in players:
            message.append(p.who_text())

        message.append("-" * 80)
        message.append("<newline>")
        return "".join(message)

    ####################################################################
    @staticmethod
    def print_help(player_rank=None):
        """Prints out a help listing based on a user's rank."""
        if player_rank is None:
            player_rank = player.PlayerRank.REGULAR
        help_text = [HELP]
        if player_rank >= player.PlayerRank.MODERATOR:
            help_text.append(MODERATOR_HELP)
        if player_rank >= player.PlayerRank.ADMIN:
            help_text.append(ADMIN_HELP)
        help_text.append(HELP_END)
        return "".join(help_text)

    ####################################################################
    def print_stats(self):
        """This prints up the stats of the player"""
        stats = ["<bold><white>"]
        stats.append("--------------------------------- Your Stats ----------------------------------<newline>")
        stats.append("Name:        %s<newline>" % self.player.name)
        stats.append("Rank:        %s<newline>" % self.player.rank.name)
        stats.append("HP/Max:      %s/%s     (%s%%)<newline>" % (self.player.hit_points, self.player.attributes.MAX_HIT_POINTS, 100 * self.player.hit_points // self.player.attributes.MAX_HIT_POINTS))
        stats.append(self.print_experience())
        stats.append("Strength:    {:<5} Accuracy:       {}<newline>".format(self.player.attributes.STRENGTH, self.player.attributes.ACCURACY))
        stats.append("Health:      {:<5} Dodging:        {}<newline>".format(self.player.attributes.HEALTH, self.player.attributes.DODGING))
        stats.append("Agility:     {:<5} Strike Damage:  {}<newline>".format(self.player.attributes.AGILITY, self.player.attributes.STRIKE_DAMAGE))
        stats.append("StatPoints:  {:<5} Damage Absorb:  {}<newline>".format(self.player.stat_points, self.player.attributes.DAMAGE_ABSORB))
        return "".join(stats)

    ####################################################################
    def print_experience(self):
        """This prints up the experience of the player"""
        need_for_level = self.player.need_for_level()
        percentage = 100 * self.player.experience // need_for_level

        experience_text = ["<bold><white>"]
        experience_text.append("Level:       {}<newline>".format(self.player.level))
        experience_text.append("Experience:  {}/{} ({}%)<newline>".format(self.player.experience, need_for_level, percentage))
        return "".join(experience_text)

    ####################################################################
    def print_inventory(self):
        inventory_text = ["<bold><white>"]
        inventory_text.append("-------------------------------- Your Inventory --------------------------------<newline>")
        inventory_text.append(" Items:  ")
        inventory_text.append(", ".join([item.name for item in self.player.inventory]))
        inventory_text.append("<newline>")
        inventory_text.append(" Weapon: ")
        if self.player.weapon:
            inventory_text.append(self.player.weapon.name)
        else:
            inventory_text.append("NONE!")
        inventory_text.append("<newline> Armor:  ")
        if self.player.armor:
            inventory_text.append(self.player.armor.name)
        else:
            inventory_text.append("NONE!")
        inventory_text.append("<newline> Money:  ${}".format(self.player.money))
        inventory_text.append("<newline>--------------------------------------------------------------------------------")
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
        for i in find_all_by_name(item_name, self.player.inventory):
            if i.type == item.ItemType.WEAPON:
                self.player.use_weapon(i)
                self.send_room("<green><bold>{} arms a {}.".format(self.player.name, i.name))
                return True
            elif i.type == item.ItemType.ARMOR:
                self.player.use_armor(i)
                self.send_room("<green><bold>{} puts on a {}.".format(self.player.name, i.name))
                return True
            elif i.type == item.ItemType.HEALING:
                self.player.add_bonuses(i)
                self.player.add_hit_points(random.randint(i.min, i.max))
                self.player.drop_item(i)
                self.send_room("<green><bold>{} uses a {}.".format(self.player.name, i.name))
                return True
        self.player.send_string("<red><bold>Could not find that item!")
        return False

    ####################################################################
    def remove_item(self, item_name):
        if item_name == "weapon":
            if self.player.weapon:
                self.player.send_string("<cyan><bold>You are no longer wielding %s." % self.player.weapon.name)
                self.player.remove_weapon()
                return True
        elif item_name == "armor":
            if self.player.armor:
                self.player.send_string("<cyan><bold>You are no longer wearing %s." % self.player.armor.name)
                self.player.remove_armor()
                return True
        self.player.send_string("<red><bold>" + "Could not remove item!")
        return False

    ####################################################################
    # Map Functions Added in Chapter 9                               ###
    ####################################################################
    ####################################################################
    def print_room(self, current_room):
        description = ["<newline><bold><white>{room.name}<newline>",
                       "<reset><magenta>{room.description}<newline>",
                       "<reset><green>exits: "]

        paths = ", ".join([d.name for d in Direction if d in current_room.connecting_rooms])
        description.append(paths)
        description.append("<newline>")

        items = [item.name for item in current_room.items]
        if current_room.money:
            items.insert(0, "${}".format(current_room.money))
        if items:
            description.append("<reset><yellow>You see: ")
            description.append(", ".join(items))
            description.append("<newline>")

        player_names = [p.name for p in current_room.players if p.active and p != self.player]
        if player_names:
            description.append("<reset><white>People: ")
            description.append(", ".join(player_names))
            description.append("<newline>")
        if current_room.enemies:
            description.append("<reset><cyan>Enemies: ")
            description.append(", ".join([e.name for e in current_room.enemies]))
            description.append("<newline>")

        return ("".join(description)).format(room=current_room)

    ####################################################################
    def send_room(self, text, this_room=None):
        if this_room is None:
            this_room = self.player.room
        this_room.send_room(text)

    ####################################################################
    def move(self, direction):
        current_room = self.player.room
        if direction in current_room.connecting_rooms:
            new_room = current_room.get_adjacent_room(direction)
            current_room.remove_player(self.player)
            self.send_room("<green>{} leaves to the {}.".format(self.player.name, direction.name), current_room)
            self.send_room("<green>{} enters from the {}.".format(self.player.name, direction.opposite_direction().name), new_room)
            self.player.send_string("<green>You walk {}.".format(direction.name))
            self.player.room = new_room
            new_room.add_player(self.player)
            self.player.send_string(self.print_room(new_room))
        else:
            self.player.send_string("<bold><red>You can't go that way!")

    ####################################################################
    def get_item(self, item_name):
        if not item_name and self.player.room.items:
            i = random.choice(self.player.room.items)
            if not self.player.pick_up_item(i):
                self.player.send_string("<red><bold>You can't carry that much!")
                return
            else:
                self.player.room.remove_item(i)
                self.send_room("<cyan><bold>{} picks up {}.".format(self.player.name, i.name))
                return
        if not item_name and self.player.room.money:
            amount = self.player.room.money
            self.player.room.money -= amount
            self.player.money += amount
            self.send_room("<cyan><bold>{p.name} picks up ${amount}".format(p=self.player, amount=amount))
            return
        if item_name.startswith("$"):
            amount = item_name[1:]
            if amount.isdigit():
                amount = int(amount)
                if amount <= self.player.room.money:
                    self.player.room.money -= amount
                    self.player.money += amount
                    self.send_room("<cyan><bold>{p.name} picks up ${amount}".format(p=self.player, amount=amount))
                else:
                    self.player.send_string("<red><bold>There isn't that much there!")
            else:
                self.player.send_string("<red><bold>Invalid amount!")
        else:
            i = self.player.room.find_item(item_name)
            if i is None:
                self.player.send_string("<red><bold>You don't see that here!")
            elif not self.player.pick_up_item(i):
                self.player.send_string("<red><bold>You can't carry that much!")
            else:
                self.player.room.remove_item(i)
                self.send_room("<cyan><bold>{} picks up {}.".format(self.player.name, i.name))

    ####################################################################
    def drop_item(self, item_name):
        if item_name.startswith("$"):
            amount = item_name[1:]
            if amount.isdigit():
                amount = int(amount)
                if amount <= self.player.money:
                    self.player.money -= amount
                    self.player.room.money += amount
                    self.send_room("<cyan><bold>{p.name} drops ${amount}".format(p=self.player, amount=amount))
                else:
                    self.player.send_string("<red><bold>You don't have that much money!")
            else:
                self.player.send_string("<red><bold>Invalid amount!")
        else:
            i = self.player.find_in_inventory(item_name)
            if i is None:
                self.player.send_string("<red><bold>You don't have that item!")
            elif not self.player.drop_item(i):
                self.player.send_string("<red><bold>You can't drop that!")
            else:
                self.player.room.add_item(i)
                self.send_room("<cyan><bold>{} drops {}.".format(self.player.name, i.name))
