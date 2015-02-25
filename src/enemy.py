import os
import json
from entity import Entity
from entity_database import EntityDatabase
import room

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

    ####################################################################
    @staticmethod
    def deserialize_from_dict(enemy_template_data):
        this_enemy = EnemyTemplate()
        for field, value in enemy_template_data.items():
            setattr(this_enemy, field, value)
        return this_enemy


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
    @staticmethod
    def deserialize_from_dict(enemy_data):
        this_enemy = Enemy()
        for field, value in enemy_data.items():
            if field == "template_id":
                this_enemy.template = enemy_template_database.by_id[value]
            elif field == "room":
                this_enemy.room = room.room_database.by_id[value]
            else:
                setattr(this_enemy, field, value)
        this_enemy.name = this_enemy.template.name
        return this_enemy

    ####################################################################
    def serialize_to_dict(self):
        output = {"id": self.id,
                  "template_id": self.template.id,
                  "hit_points": self.hit_points,
                  "room": self.room.id,
                  "next_attack_time": self.next_attack_time}
        return output


########################################################################
class EnemyDatabase(EntityDatabase):
    ####################################################################
    def __init__(self):
        super(EnemyDatabase, self).__init__()
        global enemy_database
        enemy_database = self

    ####################################################################
    @staticmethod
    def load(path=None, force=False):
        global enemy_database
        if enemy_database is None or force:
            if path is None:
                path = enemy_file
            enemy_database = EnemyDatabase()
            if os.path.exists(path):
                enemy_database.load_from_string(open(path).read())
        return enemy_database

    ####################################################################
    def load_from_string(self, text):
        data = json.loads(text)
        for enemy_data in data:
            enemy = Enemy.deserialize_from_dict(enemy_data)
            self.by_id[enemy.id] = enemy

    ####################################################################
    def save(self, path=None):
        if path is None:
            path = enemy_file
        enemy_text = self.save_to_string()
        with open(path, "w") as out_file:
            out_file.write(enemy_text)

    ####################################################################
    def save_to_string(self):
        enemies = []
        for enemy in self.by_id.values():
            enemies.append(enemy.serialize_to_dict())
        enemy_text = json.dumps(enemies, indent=4)
        return enemy_text

    ####################################################################
    def get_next_id(self):
        return len(self.by_id) + 1

    ####################################################################
    def create_enemy(self, template_id, starting_room):
        e = Enemy()
        e.id = self.get_next_id()
        e.template = enemy_template_database.by_id[template_id]
        e.name = e.template.name
        e.hit_points = e.template.hit_points
        e.room = starting_room
        starting_room.add_enemy(e)
        return e

    ####################################################################
    def destroy_enemy(self, enemy):
        enemy.room.remove_enemy(enemy)
        del self.by_id[enemy.id]


########################################################################
class EnemyTemplateDatabase(EntityDatabase):
    ####################################################################
    def __init__(self):
        super(EnemyTemplateDatabase, self).__init__()
        global enemy_template_database
        enemy_template_database = self

    ####################################################################
    @staticmethod
    def load(force=False):
        global enemy_template_database
        if enemy_template_database is None or force:
            enemy_template_database = EnemyTemplateDatabase()
            data = json.load(open(enemy_template_file))
            for enemy_template_data in data:
                enemy_template = EnemyTemplate.deserialize_from_dict(enemy_template_data)
                enemy_template_database.by_id[enemy_template.id] = enemy_template
                enemy_template_database.by_name[enemy_template.name.lower()] = enemy_template
        return enemy_template_database

EnemyTemplateDatabase.load()
EnemyDatabase.load()
