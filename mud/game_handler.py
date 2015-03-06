import logging
import re
import datetime
import random
from attributes import Direction
from mud.models import Player, Store, StoreItem
#from training_handler import TrainingHandler
from utils import find_all_by_name, double_find_by_name, ItemType, PlayerRank, RoomType

logger = logging.getLogger(__name__)


HELP = "<table class='help'>" + \
       "--------------------------------- Command List ---------------------------------<br/>" + \
       " /                            - Repeats your last command exactly.<br/>" + \
       " chat <msg>                   - Sends message to everyone in the game<br/>" + \
       " experience                   - Shows your experience statistics<br/>" + \
       " help                         - Shows this menu<br/>" + \
       " inventory                    - Shows a list of your items<br/>" + \
       " quit                         - Allows you to leave the realm.<br/>" + \
       " remove <'weapon'/'armor'>    - Removes your weapon or armor<br/>" + \
       " stats                        - Shows all of your statistics<br/>" + \
       " editstats                    - Edit your statistics<br/>" + \
       " train                        - Go to train using StatPoints<br/>" + \
       " time                         - Shows the current system time.<br/>" + \
       " use <item>                   - Use an item in your inventory<br/>" + \
       " whisper <who> <msg>          - Sends message to one person<br/>" + \
       " who                          - Shows a list of everyone online<br/>" + \
       " who all                      - Shows a list of everyone<br/>" + \
       " look                         - Shows you the contents of a room<br/>" + \
       " north/east/south/west        - Moves in a direction<br/>" + \
       " get/drop <item>              - Picks up or drops an item on the ground<br/>" + \
       " attack <enemy>               - Attacks an enemy<br/>" + \
       " talk                         - Talks to NPC's in the room<br/>" + \
       " list                         - List the items an NPC has for sale<br/>" + \
       " buy <item name / id>         - Buys an item from the store<br/>" + \
       " sell <item name>             - Sells an item to the store<br/>" + \
       " inspect <item name>          - Shows stats of an item<br/>" + \
       " map                          - Shows the map</p>"

ADMIN_HELP = "<p class='green'>" + \
             "-------------------------------- Admin Commands --------------------------------<br/>" + \
             " announce <msg>               - Makes a global system announcement</p>"
HELP_END = "<p class='bold'>%s</p>" % ("-" * 80)

system_start_time = datetime.datetime.now()

########################################################################
# Handler Methods                                                    ###
########################################################################
########################################################################
def handle_last_command(player, data, first_word, rest):
    handle(player, player.last_command)


####################################################################
def handle_chat(player, data, first_word, text):
    message = "<p class='bold'>{name} chats: {text}</p>".format(name=player.name, text=text)
    send_game(message)


####################################################################
def handle_say(player, data, first_word, text):
    message = "<p class='bold'>{name} says: {text}</p>".format(name=player.name, text=data)
    player.room.send_room(message)


####################################################################
def handle_experience(player, data, first_word, rest):
    player.send_string(print_experience(player))


####################################################################
def handle_help(player, data, first_word, rest):
    player.send_string(print_help(player.rank))


####################################################################
def handle_inventory(player, data, first_word, rest):
    player.send_string(print_inventory(player))


####################################################################
def handle_stats(player, data, first_word, rest):
    player.send_string(print_stats(player))


####################################################################
def handle_quit(player, data, first_word, rest):
    player.set_active(False)
    logout_message("%s has left the realm." % player.name)


####################################################################
def handle_remove(player, data, first_word, remove_target):
    remove_item(player, remove_target)


####################################################################
def handle_use(player, data, first_word, item_name):
    use_item(player, item_name)


####################################################################
def handle_time(player, data, first_word, rest):
    message = "<p class='bold cyan'>The current system time is %s<br/>System uptime: %02d:%02d</p>"
    now = datetime.datetime.now()
    now_string = now.strftime("%Y-%m-%d %I:%M:%S %p")
    up_time = now - system_start_time
    total_minutes = up_time.seconds // 60
    hours, minutes = divmod(total_minutes, 60)
    message = message % (now_string, hours, minutes)
    player.send_string(message)


####################################################################
def handle_whisper(player, data, first_word, rest):
    name, message = rest.split(None, 1)
    whisper(player, message, name)


####################################################################
def handle_who(player, data, first_word, rest):
    if rest:
        who = rest.split(None, 1)[0]
    else:
        who = None
    player.send_string(who_list(who))


####################################################################
# Moderator Methods                                              ###
####################################################################
####################################################################
def handle_kick(player, data, first_word, player_name):
    if player.rank < PlayerRank.MODERATOR:
        logger.warn("player %s tried to use the kick command, but doesn't have permission to do so", player.name)
        player.send_string("<p class='red'>You do not have permission to do so</p>")
        return
    kicked_player = Player.objects.filter(logged_in=True, name=player_name).first()
    if kicked_player is None:
        player.send_string("<p class='bold red'>Player could not be found.</p>")
        return
    if kicked_player.rank > player.rank:
        player.send_string("<p class='bold red'>You can't kick that player!</p>")
        return

    kicked_player.set_active(False)
    logout_message("%s has been kicked by %s!!!" % (kicked_player.name, player.name))


####################################################################
def handle_announce(player, data, first_word, announcement):
    if player.rank < PlayerRank.ADMIN:
        logger.warn("player %s tried to use the announce command, but doesn't have permission to do so", player.name)
        player.send_string("<p class='red'>You do not have permission to do so</p>")
        return
    announce(announcement)


####################################################################
def handle_train(player, data, first_word, rest):
    if player.room.type != RoomType.TRAINING_ROOM:
        player.send_string("<p class='bold red'>You cannot train here!</p>")
        return
    if player.train():
        player.send_string("<p class='bold green'>You are now level {}</p>".format(player.level))
    else:
        player.send_string("<p class='bold red'>You don't have enough experience to train!</p>")


####################################################################
def handle_editstats(player, data, first_word, rest):
    if player.room.type != RoomType.TRAINING_ROOM:
        player.send_string("<p class='bold red'>You cannot edit your stats here!</p>")
        return
    goto_train(player)


####################################################################
def goto_train(player):
    player.set_active(False)
    # TODO: Figure out different states, such as training
    # self.protocol.add_handler(TrainingHandler(self.protocol, self.player))
    logout_message("%s leaves to edit stats" % player.name)


####################################################################
def handle_look(player, data, first_word, rest):
    player.send_string(print_room(player))


####################################################################
def handle_north(player, data, first_word, rest):
    move(player, Direction.NORTH)


####################################################################
def handle_east(player, data, first_word, rest):
    move(player, Direction.EAST)


####################################################################
def handle_south(player, data, first_word, rest):
    move(player, Direction.SOUTH)


####################################################################
def handle_west(player, data, first_word, rest):
    move(player, Direction.WEST)


####################################################################
def handle_get(player, data, first_word, rest):
    get_item(player, rest)


####################################################################
def handle_drop(player, data, first_word, rest):
    drop_item(player, rest)


####################################################################
def handle_list(player, data, first_word, rest):
    if player.room.type != RoomType.STORE:
        player.send_string("<p class='bold red'>You're not in a store!</p>")
    player.send_string(store_list(player))


####################################################################
def handle_buy(player, data, first_word, rest):
    if player.room.type != RoomType.STORE:
        player.send_string("<p class='bold red'>You're not in a store!</p>")
    buy(player, rest)


####################################################################
def handle_sell(player, data, first_word, rest):
    if player.room.type != RoomType.STORE:
        player.send_string("<p class='bold red'>You're not in a store!</p>")
    sell(player, rest)


####################################################################
def handle_clear(player, data, first_word, rest):
    player.send_string("<p></p>" * 80)


####################################################################
def handle_attack(player, data, first_word, rest):
    player.attack(rest)


####################################################################
def store_list(player):
    store = Store.objects.get(room=player.room)
    output = ["<reset><p class='bold'>%s" % ("-" * 80),
              " {:<30} | {}".format("Item", "Price"),
              "-" * 80]
    for item in StoreItem.objects.filter(store=store):
        output.append(" {:<30} | {}".format(item.name, item.price))
    output.append("-" * 80)
    return "</p>".join(output)


####################################################################
def buy(player, item_name):
    store = Store.objects.get(room=player.room)
    items = StoreItem.objects.filter(store=store)
    purchase_item = double_find_by_name(item_name, items)
    if purchase_item is None:
        player.send_string("<p class='bold red'>Sorry, we don't have that item!</p>")
        return
    elif player.money < purchase_item.price:
        player.send_string("<p class='bold red'>Sorry, but you can't afford that!</p>")
        return
    elif player.buy_item(purchase_item):
        player.room.send_room("<p class='bold cyan'>{} buys a {}</p>".format(player.name, purchase_item.name))
    else:
        player.send_string("<p class='bold red'>Sorry, but you can't carry that much!</p>")


####################################################################
def sell(player, item_name):
    store = Store.objects.get(room=player.room)
    item = double_find_by_name(item_name, player.inventory)
    if item is None:
        player.send_string("<p class='bold red'>Sorry, you don't have that!</p>")
        return
    if not StoreItem.objects.filter(store=store, item=item).exists():
        player.send_string("<p class='bold red'>Sorry, we don't want that item!</p>")
        return
    player.sell_item(item)
    player.room.send_room("<p class='bold cyan'>{} sells a {}</p>".format(player.name, item.name))


####################################################################
# Base Handler Methods                                           ###
####################################################################
####################################################################
# def enter(player):
#     logger.info("%s - enter called in %s", self.protocol.get_remote_address(), self.__class__.__name__)
#     self.last_command = ""
#     self.send_game("<bold><green>{} has entered the realm.".format(self.player.name))
#     self.player.active = True
#     self.player.logged_in = True
#     self.player.room.add_player(self.player)
#     if self.player.newbie:
#         self.goto_train()
#     else:
#         player.send_string(print_room(player))
#
# ####################################################################
# def leave(self):
#     self.player.active = False
#     if self.protocol.closed:
#         player.player_database.logout(self.player.id)
#     self.player.room.remove_player(self.player)
#     self.send_game("<bold><green>{} has left the realm.".format(self.player.name))


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
        player.send_string(text)


########################################################################
def logout_message(reason):
    """Sends a logout message"""
    send_game("<p class='bold red'>%s</p>" % reason)


########################################################################
def announce(announcement):
    """Sends a system announcement"""
    send_global("<p class='bold cyan'>System Announcement: %s</p>" % announcement)


########################################################################
def whisper(player, message, player_name):
    """Sends a whisper string to the requested player"""
    other_player = Player.objects.filter(active=True, name=player_name).first()
    if other_player is None:
        player.send_string("<p class='bold red'>" + "Error, cannot find user.")
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

    message = ["<p class='bold'>{}<br/>".format("-" * 80),
               " Name             | Level     | Activity | Rank<br/>",
               "-" * 80, "<br/>"]

    for player in players:
        message.append(player.who_text())

    message.append("-" * 80)
    message.append("</p>")
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
    # TODO: Write this as a table
    stats = ["<bold><white>"]
    stats.append("--------------------------------- Your Stats ----------------------------------<br/>")
    stats.append("Name:        %s<br/>" % player.name)
    stats.append("Rank:        %s<br/>" % player.rank.name)
    stats.append("HP/Max:      %s/%s     (%s%%)<br/>" % (player.hit_points, player.attributes.MAX_HIT_POINTS, 100 * player.hit_points // player.attributes.MAX_HIT_POINTS))
    stats.append(print_experience(player))
    stats.append("Strength:    {:<5} Accuracy:       {}<br/>".format(player.attributes.STRENGTH, player.attributes.ACCURACY))
    stats.append("Health:      {:<5} Dodging:        {}<br/>".format(player.attributes.HEALTH, player.attributes.DODGING))
    stats.append("Agility:     {:<5} Strike Damage:  {}<br/>".format(player.attributes.AGILITY, player.attributes.STRIKE_DAMAGE))
    stats.append("StatPoints:  {:<5} Damage Absorb:  {}</p>".format(player.stat_points, player.attributes.DAMAGE_ABSORB))
    return "".join(stats)

####################################################################
def print_experience(self):
    """This prints up the experience of the player"""
    # TODO: Write this as a table
    need_for_level = player.need_for_level()
    percentage = 100 * player.experience // need_for_level

    experience_text = ["<bold><white>"]
    experience_text.append("Level:       {}<newline>".format(player.level))
    experience_text.append("Experience:  {}/{} ({}%)<newline>".format(player.experience, need_for_level, percentage))
    return "".join(experience_text)

####################################################################
def print_inventory(self):
    # TODO: Write this as a table
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
# Inventory Methods                                              ###
####################################################################
####################################################################
def use_item(player, item_name):
    for item in find_all_by_name(item_name, player.inventory):
        if item.type == ItemType.WEAPON:
            player.use_weapon(item)
            player.room.send_room("<p class='bold green'>{} arms a {}.</p>".format(player.name, item.name))
            return True
        elif item.type == ItemType.ARMOR:
            player.use_armor(item)
            player.room.send_room("<p class='bold green'>{} puts on a {}.</p>".format(player.name, item.name))
            return True
        elif item.type == ItemType.HEALING:
            player.add_bonuses(item)
            player.add_hit_points(random.randint(item.min, item.max))
            player.drop_item(item)
            player.room.send_room("<p class='bold green'>{} uses a {}.</p>".format(player.name, item.name))
            return True
    player.send_string("<p class='bold red'>Could not find that item!</p>")
    return False


####################################################################
def remove_item(player, item_name):
    if item_name == "weapon":
        if player.weapon:
            player.send_string("<p class='bold cyan'>You are no longer wielding %s.</p>" % player.weapon.name)
            player.remove_weapon()
            return True
    elif item_name == "armor":
        if player.armor:
            player.send_string("<p class='bold cyan'>You are no longer wearing %s.</p>" % player.armor.name)
            player.remove_armor()
            return True
    player.send_string("<p class='bold red'>" + "Could not remove item!</p>")
    return False


####################################################################
# Map Functions Added in Chapter 9                               ###
####################################################################
####################################################################
def print_room(player):
    current_room = player.room
    description = ["<p class='strong'>{room.name}</p>",
                   "<p class='magenta'>{room.description}</p>",
                   "<p class='green'>exits: "]

    paths = ", ".join([d.name for d in Direction if d in current_room.connecting_rooms])
    description.append(paths)
    description.append("</p>")

    items = [item.name for item in current_room.items.all()]
    if current_room.money:
        items.insert(0, "${}".format(current_room.money))
    if items:
        description.append("<p class='yellow'>You see: ")
        description.append(", ".join(items))
        description.append("</p>")

    player_names = [p.name for p in current_room.player_set.filter(active=True).exclude(id=player.id)]
    if player_names:
        description.append("<p>People: ")
        description.append(", ".join(player_names))
        description.append("</p>")
    enemies = current_room.enemy_set.all()
    if enemies:
        description.append("<p class='cyan'>Enemies: ")
        description.append(", ".join([e.name for e in enemies]))
        description.append("</p>")

    return ("".join(description)).format(room=current_room)


####################################################################
def move(player, direction):
    current_room = player.room
    if direction in current_room.connecting_rooms:
        new_room = current_room.get_adjacent_room(direction)
        current_room.remove_player(player)
        current_room.send_room("<p class='green'>{} leaves to the {}.</p>".format(player.name, direction.name))
        new_room.send_room("<p class='green'>{} enters from the {}.</p>".format(player.name, direction.opposite_direction().name))
        player.send_string("<p class='green'>You walk {}.</p>".format(direction.name))
        player.room = new_room
        new_room.add_player(player)
        player.send_string(print_room(player))
    else:
        player.send_string("<p class='bold red'>You can't go that way!</p>")


####################################################################
def get_item(player, item_name):
    if not item_name and player.room.items:
        i = random.choice(player.room.items)
        if not player.pick_up_item(i):
            player.send_string("<p class='bold red'>You can't carry that much!</p>")
            return
        else:
            player.room.remove_item(i)
            player.room.send_room("<p class='bold cyan'>{} picks up {}.</p>".format(player.name, i.name))
            return
    if not item_name and player.room.money:
        amount = player.room.money
        player.room.money -= amount
        player.money += amount
        player.room.send_room("<p class='bold cyan'>{p.name} picks up ${amount}</p>".format(p=player, amount=amount))
        return
    if item_name.startswith("$"):
        amount = item_name[1:]
        if amount.isdigit():
            amount = int(amount)
            if amount <= player.room.money:
                player.room.money -= amount
                player.money += amount
                player.room.send_room("<p class='bold cyan'>{p.name} picks up ${amount}</p>".format(p=player, amount=amount))
            else:
                player.send_string("<p class='bold red'>There isn't that much there!</p>")
        else:
            player.send_string("<p class='bold red'>Invalid amount!</p>")
    else:
        i = player.room.find_item(item_name)
        if i is None:
            player.send_string("<p class='bold red'>You don't see that here!</p>")
        elif not player.pick_up_item(i):
            player.send_string("<p class='bold red'>You can't carry that much!</p>")
        else:
            player.room.remove_item(i)
            player.room.send_room("<p class='bold cyan'>{} picks up {}.</p>".format(player.name, i.name))

####################################################################
def drop_item(player, item_name):
    if item_name.startswith("$"):
        amount = item_name[1:]
        if amount.isdigit():
            amount = int(amount)
            if amount <= player.money:
                player.money -= amount
                player.room.money += amount
                player.room.send_room("<p class='bold cyan'>{p.name} drops ${amount}</p>".format(p=player, amount=amount))
            else:
                player.send_string("<p class='bold red'>You don't have that much money!</p>")
        else:
            player.send_string("<p class='bold red'>Invalid amount!</p>")
    else:
        i = player.find_in_inventory(item_name)
        if i is None:
            player.send_string("<p class='bold red'>You don't have that item!</p>")
        elif not player.drop_item(i):
            player.send_string("<p class='bold red'>You can't drop that!</p>")
        else:
            player.room.add_item(i)
            player.room.send_room("<p class='bold cyan'>{} drops {}.</p>".format(player.name, i.name))


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
