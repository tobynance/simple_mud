import os
import logging
import json
import random
from entity import Entity
from entity_database import EntityDatabase
import room
import item
import game_handler
from utils import clamp

logger = logging.getLogger(__name__)

base = os.path.dirname(__file__)
enemy_template_file = os.path.join(base, "..", "data", "enemy_templates.json")
enemy_file = os.path.join(base, "..", "data", "enemies.json")

enemy_template_database = None
enemy_database = None


########################################################################
class EnemyTemplate(Entity):
    ####################################################################
    def __init__(self):
        super(EnemyTemplate, self).__init__()
        self.hit_points = 1    # starting hit points of enemy
        self.accuracy = 0
        self.dodging = 0
        self.strike_damage = 0
        self.damage_absorb = 0
        self.experience = 0    # experience gained when killed
        self.weapon = None
        self.money_min = 0     # min $ enemy drops when it dies
        self.money_max = 0     # max $ enemy drops when it dies
        # list of pairs of (item, int_percent) of items that drop when the
        # enemy dies, and percentage chance on each item for it to drop.
        self.loot = []


########################################################################
class Enemy(Entity):
    ####################################################################
    def __init__(self):
        super(Enemy, self).__init__()
        self.template = None
        self.hit_points = 1
        self.room = None
        self.next_attack_time = 0

    ####################################################################
    @property
    def accuracy(self):
        return self.template.accuracy

    ####################################################################
    @property
    def dodging(self):
        return self.template.dodging

    ####################################################################
    @property
    def strike_damage(self):
        return self.template.strike_damage

    ####################################################################
    @property
    def damage_absorb(self):
        return self.template.damage_absorb

    ####################################################################
    @property
    def experience(self):
        return self.template.experience

    ####################################################################
    @property
    def weapon(self):
        return self.template.weapon

    ####################################################################
    @property
    def money_min(self):
        return self.template.money_min

    ####################################################################
    @property
    def money_max(self):
        return self.template.money_max

    ####################################################################
    @property
    def loot(self):
        return self.template.loot

    ####################################################################
    def add_hit_points(self, hit_points):
        self.hit_points += hit_points
        self.hit_points = clamp(self.hit_points, 0, self.template.hit_points)

    ####################################################################
    def attack(self):
        # attack a random player in the room
        p = random.choice(list(self.room.players))
        if not self.weapon:  # fists, 1-3 damage, 1 second swing time
            damage = random.randint(1, 3)
            self.next_attack_time = 1
        else:
            weapon = item.item_database.by_id[self.weapon]
            damage = random.randint(weapon.min, weapon.max)
            self.next_attack_time = weapon.speed

        if random.randint(0, 99) >= (self.accuracy - p.attributes.DODGING):
            self.room.send_room("<white>{} swings at {} but misses!".format(self.name, p.name))
            return
        damage += self.strike_damage
        damage -= p.attributes.DAMAGE_ABSORB
        if damage < 1:
            damage = 1

        p.add_hit_points(-damage)
        self.room.send_room("<red>{} hits {} for {} damage!".format(self.name, p.name, damage))
        if p.hit_points <= 0:
            p.killed()

    ####################################################################
    def killed(self, killer):
        self.room.send_room("<cyan><bold>%s has died!" % self.name)

        # drop the money
        money = random.randint(self.money_min, self.money_max)
        if money > 0:
            self.room.money += money
            self.room.send_room("<cyan>$%s drops to the ground." % money)

        for item_id, chance in self.loot:
            if random.randint(0, 99) < chance:
                i = item.item_database.by_id[item_id]
                self.room.add_item(i)
                self.room.send_room("<cyan>%s drops to the ground." % i.name)
        killer.experience += self.experience
        killer.send_string("<cyan><bold>You gain %s experience." % self.experience)
        enemy_database.destroy_enemy(self)


########################################################################
class EnemyDatabase(EntityDatabase):
    ####################################################################
    def create_enemy(self, template_id, starting_room):
        e = Enemy()
        self.by_id[e.id] = e
        e.template = enemy_template_database.by_id[template_id]
        e.name = e.template.name
        e.hit_points = e.template.hit_points
        e.room = starting_room
        starting_room.add_enemy(e)
        return e
