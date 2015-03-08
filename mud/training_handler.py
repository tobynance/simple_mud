import logging
from utils import HandlerType
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


########################################################################
def handle(player, data):
    if data == "quit":
        player.set_handler(HandlerType.GAME_HANDLER)
        return
    if data in ["1", "2", "3"]:
        if player.stat_points > 0:
            player.stat_points -= 1
            if data == "1":
                player.base_strength += 1
                player.save(update_fields=["base_strength", "stat_points"])
            elif data == "2":
                player.base_health += 1
                player.save(update_fields=["base_health", "stat_points"])
            else:
                player.base_agility += 1
                player.save(update_fields=["base_agility", "stat_points"])
        print_stats(player, True)
    else:
        logger.warn("unknown command: %s", data)
        player.send_string("<clearscreen><p class='red'>Unknown Command '%s'</p>" % data)
        print_stats(False)


####################################################################
def enter(player):
    player.active = False
    if player.newbie:
        player.send_string(("<p class='bold magenta'>Welcome to SimpleMUD, %s!<br/>" +
                            "You must train your character with your desired stats,<br/>" +
                            "before you enter the realm.<br/></p>") % player.name)
        player.newbie = False
    player.save(update_fields=["active", "newbie"])
    print_stats(False)


########################################################################
def leave(player):
    pass


####################################################################
def print_stats(player, clear_screen=True):
    context = {"name": player.name,
               "strength": player.strength,
               "health": player.health,
               "agility": player.agility,
               "stat_points": player.stat_points}
    message = render_to_string("mud/training_stats.html", context)
    if clear_screen:
        return "<clearscreen>" + message
    else:
        return message
