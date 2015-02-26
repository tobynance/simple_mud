import item
import room
import player
import enemy
import time
import logging

logger = logging.getLogger(__name__)


# LoadDatabases(); # load all databases
# SaveDatabases(); # save all databases
# Load(); # load gameloop data
# Save(); # save gameloop data
# Loop(); # perform one loop iteration
# PerformRound(); # perform combat round
# PerformRegen(); # perform enemy regen round
# PerformHeal();  # perform healing round
#
# m_savedatabases;
# m_nextround;
# m_nextregen;
# m_nextheal;

#DB_SAVE_TIME = 15 * 60
DB_SAVE_TIME = 1 * 60
ROUND_TIME = 1
REGEN_TIME = 2 * 60
HEAL_TIME = 1 * 60


########################################################################
def perform_round():
    """Have enemies attack players."""
    logger.debug("Performing attack cycle...")
    for e in enemy.enemy_database.all():
        e.next_attack_time = max(0, e.next_attack_time - ROUND_TIME)
        # check if enemy can attack
        if e.next_attack_time == 0 and len(e.room.players) > 0:
            e.attack()
    for p in player.player_database.all():
        p.next_attack_time = max(0, p.next_attack_time - ROUND_TIME)


########################################################################
def perform_regen():
    """Spawn enemies into any room that can hold more."""
    logger.info("Performing regen cycle...")
    for r in room.room_database.all():
        if r.spawn_which_enemy and len(r.enemies) < r.max_enemies:
            # create a new enemy in the room
            enemy.enemy_database.create_enemy(r.spawn_which_enemy, r)
            spawned_enemy_type = enemy.enemy_template_database.find(r.spawn_which_enemy)
            logger.info("For room %s(%s) we should spawn enemy %s" % (r.name, r.id, spawned_enemy_type.name))
            r.send_room("<red><bold>{} enters the room!".format(spawned_enemy_type.name))


########################################################################
def perform_heal():
    logger.debug("Performing heal cycle...")
    for p in player.player_database.all():
        if p.active:
            p.add_hit_points(p.attributes.HP_REGEN)
            p.print_status_bar()  # TODO: I need to see if this is obnoxious to the user


########################################################################
def save_databases():
    logger.info("Performing DB save cycle...")
    player.player_database.save()
    room.room_database.save()
    enemy.enemy_database.save()


item.ItemDatabase.load()
room.RoomDatabase.load()
enemy.EnemyDatabase.load()
enemy.EnemyTemplateDatabase.load()
player.PlayerDatabase.load()
