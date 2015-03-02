import logging
import re
import datetime
import random
from attributes import Direction
from mud.models import Player
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

ADMIN_HELP = "<green><bold>" + \
             "-------------------------------- Admin Commands --------------------------------<newline>" + \
             " announce <msg>               - Makes a global system announcement<newline>"
HELP_END = "<white><bold>%s<newline>" % ("-" * 80)


########################################################################
# Handler Methods                                                    ###
########################################################################
########################################################################
def handle_last_command(player, data, first_word, rest):
    handle(player, player.last_command)


####################################################################
def handle_chat(player, data, first_word, text):
    message = "<white><bold>{name} chats: {text}".format(name=self.player.name, text=text)
    send_game(player, message)


####################################################################
def handle_say(player, data, first_word, text):
    message = "<white><bold>{name} says: {text}".format(name=self.player.name, text=data)
    self.send_room(message)

####################################################################
def handle_experience(player, data, first_word, rest):
    self.player.send_string(self.print_experience())

####################################################################
def handle_help(player, data, first_word, rest):
    self.player.send_string(self.print_help(self.player.rank))

####################################################################
def handle_inventory(player, data, first_word, rest):
    self.player.send_string(self.print_inventory())

####################################################################
def handle_stats(player, data, first_word, rest):
    self.player.send_string(self.print_stats())

####################################################################
def handle_quit(player, data, first_word, rest):
    self.protocol.drop_connection()
    player.player_database.logout(self.player.id)
    self.player.room.remove_player(self.player)
    self.logout_message("%s has left the realm." % self.player.name)

####################################################################
def handle_remove(player, data, first_word, remove_target):
    self.remove_item(remove_target)

####################################################################
def handle_use(player, data, first_word, item_name):
    self.use_item(item_name)

####################################################################
def handle_time(player, data, first_word, rest):
    message = "The current system time is %s<newline>System uptime: %02d:%02d"
    now = datetime.datetime.now()
    now_string = now.strftime("%Y-%m-%d %I:%M:%S %p")
    up_time = now - self.system_start_time
    total_minutes = up_time.seconds // 60
    hours, minutes = divmod(total_minutes, 60)
    message = message % (now_string, hours, minutes)
    self.player.send_string("<bold><cyan>" + message)

####################################################################
def handle_whisper(player, data, first_word, rest):
    name, message = rest.split(None, 1)
    self.whisper(message, name)

####################################################################
def handle_who(player, data, first_word, rest):
    if rest:
        who = rest.split(None, 1)[0]
    else:
        who = None
    self.player.send_string(self.who_list(who))

####################################################################
# Moderator Methods                                              ###
####################################################################
####################################################################
def handle_kick(player, data, first_word, player_name):
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
def handle_announce(player, data, first_word, announcement):
    if self.player.rank < player.PlayerRank.ADMIN:
        logger.warn("player %s tried to use the announce command, but doesn't have permission to do so", self.player.name)
        self.player.send_string("<red>You do not have permission to do so<newline>")
        return
    self.announce(announcement)

####################################################################
def handle_change_rank(player, data, first_word, rest):
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
def handle_reload(player, data, first_word, db):
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
def handle_shutdown(player, data, first_word, rest):
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
def handle_train(player, data, first_word, rest):
    if self.player.room.type != room.RoomType.TRAINING_ROOM:
        self.player.send_string("<red><bold>You cannot train here!")
        return
    if self.player.train():
        self.player.send_string("<green><bold>You are now level {}".format(self.player.level))
    else:
        self.player.send_string("<red><bold>You don't have enough experience to train!")

####################################################################
def handle_editstats(player, data, first_word, rest):
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
def handle_look(player, data, first_word, rest):
    self.player.send_string(self.print_room(self.player.room))

####################################################################
def handle_north(player, data, first_word, rest):
    self.move(Direction.NORTH)

####################################################################
def handle_east(player, data, first_word, rest):
    self.move(Direction.EAST)

####################################################################
def handle_south(player, data, first_word, rest):
    self.move(Direction.SOUTH)

####################################################################
def handle_west(player, data, first_word, rest):
    self.move(Direction.WEST)

####################################################################
def handle_get(player, data, first_word, rest):
    self.get_item(rest)

####################################################################
def handle_drop(player, data, first_word, rest):
    self.drop_item(rest)

####################################################################
def handle_list(player, data, first_word, rest):
    if self.player.room.type != room.RoomType.STORE:
        self.player.send_string("<red><bold>You're not in a store!")
    self.player.send_string(self.store_list(self.player.room.data))

####################################################################
def handle_buy(player, data, first_word, rest):
    if self.player.room.type != room.RoomType.STORE:
        self.player.send_string("<red><bold>You're not in a store!")
    self.buy(rest)

####################################################################
def handle_sell(player, data, first_word, rest):
    if self.player.room.type != room.RoomType.STORE:
        self.player.send_string("<red><bold>You're not in a store!")
    self.sell(rest)

####################################################################
def handle_clear(player, data, first_word, rest):
    self.player.send_string("<newline>" * 80)

####################################################################
def handle_attack(player, data, first_word, rest):
    self.player.attack(rest)

####################################################################
def store_list(player, store_id):
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
def buy(player, item_name):
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
def sell(player, item_name):
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

########################################################################
# Sending Methods                                                    ###
########################################################################
########################################################################
def send_global(text):
    """Sends a string to everyone connected."""
    for player in Player.objects.filter(logged_in=True):
        player.send_string(text)

########################################################################
def send_game(text):
    """Sends a string to everyone 'within the game'"""
    for player in Player.objects.filter(logged_in=True):
    for p in player.player_database.all_active():
        p.send_string(text)


########################################################################
def logout_message(reason):
    """Sends a logout message"""
    send_game("<red><bold>%s" % reason)


########################################################################
def announce(announcement):
    """Sends a system announcement"""
    send_global("<cyan><bold>System Announcement: %s<newline>" % announcement)


########################################################################
def whisper(player, message, player_name):
    """Sends a whisper string to the requested player"""
    other_player = Player.objects.filter(active=True, name=player_name).first()
    if other_player is None:
        player.send_string("<red><bold>" + "Error, cannot find user.")
    else:
        other_player.send_string("<yellow>{} whispers to you: <reset>{}".format(player.name, message))


########################################################################
# various status-printing methods                                    ###
########################################################################
########################################################################
def who_list(who):
    """This prints up the who-list for the realm."""
    if who == "all":
        players = list(Player.objects.all())
    else:
        players = list(Player.objects.filter(logged_in=True))

    message = ["<white><bold>{}<newline>".format("-" * 80),
               " Name             | Level     | Activity | Rank<newline>",
               "-" * 80, "<newline>"]

    for player in players:
        message.append(player.who_text())

    message.append("-" * 80)
    message.append("<newline>")
    return "".join(message)


########################################################################
def print_help(player):
    """Prints out a help listing based on a user's rank."""
    # if player_rank is None:
    #     player_rank = player.PlayerRank.REGULAR
    help_text = [HELP]
    # if player_rank >= player.PlayerRank.ADMIN:
    #     help_text.append(ADMIN_HELP)
    help_text.append(HELP_END)
    return "".join(help_text)

########################################################################
def print_stats(player):
    """This prints up the stats of the player"""
    stats = ["<bold><white>"]
    stats.append("--------------------------------- Your Stats ----------------------------------<newline>")
    stats.append("Name:        %s<newline>" % player.name)
    stats.append("Rank:        %s<newline>" % player.rank.name)
    stats.append("HP/Max:      %s/%s     (%s%%)<newline>" % (player.hit_points, player.attributes.MAX_HIT_POINTS, 100 * player.hit_points // player.attributes.MAX_HIT_POINTS))
    stats.append(print_experience(player))
    stats.append("Strength:    {:<5} Accuracy:       {}<newline>".format(player.attributes.STRENGTH, player.attributes.ACCURACY))
    stats.append("Health:      {:<5} Dodging:        {}<newline>".format(player.attributes.HEALTH, player.attributes.DODGING))
    stats.append("Agility:     {:<5} Strike Damage:  {}<newline>".format(player.attributes.AGILITY, player.attributes.STRIKE_DAMAGE))
    stats.append("StatPoints:  {:<5} Damage Absorb:  {}<newline>".format(player.stat_points, player.attributes.DAMAGE_ABSORB))
    return "".join(stats)

####################################################################
def print_experience(self):
    """This prints up the experience of the player"""
    need_for_level = player.need_for_level()
    percentage = 100 * player.experience // need_for_level

    experience_text = ["<bold><white>"]
    experience_text.append("Level:       {}<newline>".format(player.level))
    experience_text.append("Experience:  {}/{} ({}%)<newline>".format(player.experience, need_for_level, percentage))
    return "".join(experience_text)

####################################################################
def print_inventory(self):
    inventory_text = ["<bold><white>"]
    inventory_text.append("-------------------------------- Your Inventory --------------------------------<newline>")
    inventory_text.append(" Items:  ")
    inventory_text.append(", ".join([item.name for item in player.inventory]))
    inventory_text.append("<newline>")
    inventory_text.append(" Weapon: ")
    if player.weapon:
        inventory_text.append(player.weapon.name)
    else:
        inventory_text.append("NONE!")
    inventory_text.append("<newline> Armor:  ")
    if player.armor:
        inventory_text.append(player.armor.name)
    else:
        inventory_text.append("NONE!")
    inventory_text.append("<newline> Money:  ${}".format(player.money))
    inventory_text.append("<newline>--------------------------------------------------------------------------------")
    return "".join(inventory_text)

####################################################################
def print_products(self):
    raise NotImplementedError

####################################################################
def buy_product(player, obj_name_or_id):
    raise NotImplementedError

####################################################################
def print_map(self):
    raise NotImplementedError

####################################################################
def print_item_stats(player, item_name):
    raise NotImplementedError

####################################################################
def sell_item(player, item_name):
    raise NotImplementedError

####################################################################
# Inventory Methods                                              ###
####################################################################
####################################################################
def use_item(player, item_name):
    for i in find_all_by_name(item_name, player.inventory):
        if i.type == item.ItemType.WEAPON:
            player.use_weapon(i)
            self.send_room("<green><bold>{} arms a {}.".format(player.name, i.name))
            return True
        elif i.type == item.ItemType.ARMOR:
            player.use_armor(i)
            self.send_room("<green><bold>{} puts on a {}.".format(player.name, i.name))
            return True
        elif i.type == item.ItemType.HEALING:
            player.add_bonuses(i)
            player.add_hit_points(random.randint(i.min, i.max))
            player.drop_item(i)
            self.send_room("<green><bold>{} uses a {}.".format(player.name, i.name))
            return True
    player.send_string("<red><bold>Could not find that item!")
    return False

####################################################################
def remove_item(player, item_name):
    if item_name == "weapon":
        if player.weapon:
            player.send_string("<cyan><bold>You are no longer wielding %s." % player.weapon.name)
            player.remove_weapon()
            return True
    elif item_name == "armor":
        if player.armor:
            player.send_string("<cyan><bold>You are no longer wearing %s." % player.armor.name)
            player.remove_armor()
            return True
    player.send_string("<red><bold>" + "Could not remove item!")
    return False

####################################################################
# Map Functions Added in Chapter 9                               ###
####################################################################
####################################################################
def print_room(player, current_room):
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

    player_names = [p.name for p in current_room.players if p.active and p != player]
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
def send_room(player, text, this_room=None):
    if this_room is None:
        this_room = player.room
    this_room.send_room(text)

####################################################################
def move(player, direction):
    current_room = player.room
    if direction in current_room.connecting_rooms:
        new_room = current_room.get_adjacent_room(direction)
        current_room.remove_player(player)
        self.send_room("<green>{} leaves to the {}.".format(player.name, direction.name), current_room)
        self.send_room("<green>{} enters from the {}.".format(player.name, direction.opposite_direction().name), new_room)
        player.send_string("<green>You walk {}.".format(direction.name))
        player.room = new_room
        new_room.add_player(player)
        player.send_string(self.print_room(new_room))
    else:
        player.send_string("<bold><red>You can't go that way!")

####################################################################
def get_item(player, item_name):
    if not item_name and player.room.items:
        i = random.choice(player.room.items)
        if not player.pick_up_item(i):
            player.send_string("<red><bold>You can't carry that much!")
            return
        else:
            player.room.remove_item(i)
            self.send_room("<cyan><bold>{} picks up {}.".format(player.name, i.name))
            return
    if not item_name and player.room.money:
        amount = player.room.money
        player.room.money -= amount
        player.money += amount
        self.send_room("<cyan><bold>{p.name} picks up ${amount}".format(p=player, amount=amount))
        return
    if item_name.startswith("$"):
        amount = item_name[1:]
        if amount.isdigit():
            amount = int(amount)
            if amount <= player.room.money:
                player.room.money -= amount
                player.money += amount
                self.send_room("<cyan><bold>{p.name} picks up ${amount}".format(p=player, amount=amount))
            else:
                player.send_string("<red><bold>There isn't that much there!")
        else:
            player.send_string("<red><bold>Invalid amount!")
    else:
        i = player.room.find_item(item_name)
        if i is None:
            player.send_string("<red><bold>You don't see that here!")
        elif not player.pick_up_item(i):
            player.send_string("<red><bold>You can't carry that much!")
        else:
            player.room.remove_item(i)
            self.send_room("<cyan><bold>{} picks up {}.".format(player.name, i.name))

####################################################################
def drop_item(player, item_name):
    if item_name.startswith("$"):
        amount = item_name[1:]
        if amount.isdigit():
            amount = int(amount)
            if amount <= player.money:
                player.money -= amount
                player.room.money += amount
                self.send_room("<cyan><bold>{p.name} drops ${amount}".format(p=player, amount=amount))
            else:
                player.send_string("<red><bold>You don't have that much money!")
        else:
            player.send_string("<red><bold>Invalid amount!")
    else:
        i = player.find_in_inventory(item_name)
        if i is None:
            player.send_string("<red><bold>You don't have that item!")
        elif not player.drop_item(i):
            player.send_string("<red><bold>You can't drop that!")
        else:
            player.room.add_item(i)
            self.send_room("<cyan><bold>{} drops {}.".format(player.name, i.name))


########################################################################
########################################################################
data_handlers = [
    ("/", handle_last_command),
    (["chat", ":"], handle_chat),
    (["experience", "exp"], handle_experience),
    (["help", "commands"], handle_help),
    (["inventory", "i"], handle_inventory),
    (["stats", "st"], handle_stats),
    ("quit", handle_quit),
    ("remove", handle_remove),
    ("use", handle_use),
    ("time", handle_time),
    ("whisper", handle_whisper),
    ("who", handle_who),
    ("kick", handle_kick),
    ("announce", handle_announce),
    ("changerank", handle_change_rank),
    ("reload", handle_reload),
    ("shutdown", handle_shutdown),
    ("train", handle_train),
    ("editstats", handle_editstats),
    (["look", "l"], handle_look),
    (["north", "n"], handle_north),
    (["east", "e"], handle_east),
    (["south", "s"], handle_south),
    (["west", "w"], handle_west),
    ("get", handle_get),
    ("drop", handle_drop),
    ("list", handle_list),
    ("buy", handle_buy),
    ("sell", handle_sell),
    ("clear", handle_clear),
    (["attack", "a"], handle_attack),
    # send whole message to room chat
    (True, handle_say)]


########################################################################
def refresh(obj):
    return type(obj).objects.get(pk=obj.pk)


########################################################################
def check_predicate(predicate, data):
    if isinstance(predicate, basestring):
        return predicate == data
    elif isinstance(predicate, list) or isinstance(predicate, tuple):
        return data in predicate
    elif isinstance(predicate, bool):
        return predicate
    elif isinstance(predicate, re._pattern_type):
        if predicate.match(data):
            return True
        else:
            return False
    else:
        raise ValueError("I don't know how to use the predicate '%s' of type '%s'" % predicate, type(predicate))


########################################################################
def handle(player, data):
    if data:
        split = data.split(None, 1)
        first_word = data.split(None, 1)[0]
        if len(split) > 1:
            rest = split[1]
        else:
            rest = ""

        for predicate, handler in data_handlers:
            if check_predicate(predicate, first_word):
                handler(player, data, first_word, rest)
                if predicate != "/":
                    player = refresh(player)
                    player.last_command = data
                    player.save(update_fields=["last_command"])
                return
