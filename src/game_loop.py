import room
import player
import enemy
import time


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

DB_SAVE_TIME = 15 * 60
ROUND_TIME = 1
REGEN_TIME = 2 * 60
HEAL_TIME = 1 * 60

current_round_time = time.time()


########################################################################
def perform_round():
    for e in enemy.enemy_database.all():
        now = time.time()
        diff = now - current_round_time
        e.next_attack_time = max(0, e.next_attack_time - diff)
        # check if enemy can attack
        if e.next_attack_time == 0 and len(e.room.players) > 0:
            pass

# void GameLoop::PerformRound() {
#     EnemyDatabase::iterator itr = EnemyDatabase::begin();
#     sint64 now = Game::GetTimer().GetMS();
#     while( itr != EnemyDatabase::end() ) {
#         if( now >= itr->NextAttackTime() &&
#         // make sure enemy can attack
#         itr->CurrentRoom()->Players().size() > 0 ) // check players
#             Game::EnemyAttack( itr->ID() );
#         // tell enemy to attack
#         ++itr;
#     }
# }

########################################################################
def perform_regen():
    pass


########################################################################
def perform_heal():
    pass


########################################################################
def save_databases():
    pass


room.RoomDatabase.load()
player.PlayerDatabase.load()
enemy.EnemyDatabase.load()
enemy.EnemyTemplateDatabase.load()
