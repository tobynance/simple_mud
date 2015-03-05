from __future__ import absolute_import
import logging
from django.conf import settings
from celery import shared_task
from mud.models import Enemy, Player, Room

logger = logging.getLogger(__name__)


########################################################################
@shared_task
def perform_round_task():
    """Have enemies attack players."""
    logger.debug("Performing attack cycle...")
    for enemy in Enemy.objects.all():
        enemy.next_attack_time = max(0, enemy.next_attack_time - settings.ROUND_TIME)
        # check if enemy can attack
        if enemy.next_attack_time == 0 and enemy.room.player_set.count() > 0:
            enemy.attack()

    for player in Player.objects.filter(active=True):
        player.next_attack_time = max(0, player.next_attack_time - settings.ROUND_TIME)


########################################################################
@shared_task
def perform_regen_task():
    """Spawn enemies into any room that can hold more."""
    logger.info("Performing regen cycle...")
    for room in Room.objects.all():
        if room.enemy_set.count() < room.max_enemies:
            # create a new enemy in the room
            enemy = room.enemy_type.create_enemy(room)
            logger.info("Spawning %s in room %s" % (enemy, room))
            room.send_room("<red><bold>{} enters the room!".format(enemy.name))


########################################################################
@shared_task
def perform_heal_task():
    logger.debug("Performing heal cycle...")
    for player in Player.objects.filter(active=True):
        player.perform_heal_cycle()
