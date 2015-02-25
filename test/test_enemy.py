import unittest
import unittest
from enemy import Enemy, EnemyTemplate, EnemyDatabase, EnemyTemplateDatabase
import enemy
import room

########################################################################
class EnemyTemplateTest(unittest.TestCase):
    ####################################################################
    def test_deserialize_from_dict(self):
        template_data = {
            "id": 19,
            "name": "Captain Jack",
            "hit_points": 200,
            "accuracy": 200,
            "dodging": 50,
            "strike_damage": 10,
            "damage_absorb": 10,
            "experience": 200,
            "weapon": 34,
            "money_min": 0,
            "money_max": 200,
            "loot": [[71, 1]]
        }
        enemy_template = EnemyTemplate.deserialize_from_dict(template_data)
        self.assertEqual(enemy_template.id, 19)
        self.assertEqual(enemy_template.name, "Captain Jack")
        self.assertEqual(enemy_template.hit_points, 200)
        self.assertEqual(enemy_template.accuracy, 200)
        self.assertEqual(enemy_template.dodging, 50)
        self.assertEqual(enemy_template.strike_damage, 10)
        self.assertEqual(enemy_template.damage_absorb, 10)
        self.assertEqual(enemy_template.experience, 200)
        self.assertEqual(enemy_template.weapon, 34)
        self.assertEqual(enemy_template.money_min, 0)
        self.assertEqual(enemy_template.money_max, 200)
        self.assertEqual(enemy_template.loot, [[71, 1]])


########################################################################
class EnemyTest(unittest.TestCase):
    ####################################################################
    def test_create_enemy(self):
        this_enemy = enemy.enemy_database.create_enemy(2, room.room_database.by_id[1])
        self.assertEqual(this_enemy.id, 1)
        self.assertEqual(this_enemy.name, "Thug")
        self.assertEqual(isinstance(this_enemy.template, EnemyTemplate), True)
        self.assertEqual(this_enemy.hit_points, 15)
        self.assertEqual(this_enemy.accuracy, 70)
        self.assertEqual(this_enemy.dodging, -10)
        self.assertEqual(this_enemy.strike_damage, 0)
        self.assertEqual(this_enemy.damage_absorb, 0)
        self.assertEqual(this_enemy.experience, 10)
        self.assertEqual(this_enemy.weapon, 41)
        self.assertEqual(this_enemy.money_min, 0)
        self.assertEqual(this_enemy.money_max, 4)
        self.assertEqual(this_enemy.loot, [[41, 1], [35, 2]])

    ####################################################################
    def test_serialization(self):
        this_enemy = enemy.enemy_database.create_enemy(2, room.room_database.by_id[1])
        this_enemy.hit_points = 12
        data = this_enemy.serialize_to_dict()
        self.assertEqual(data, {"id": 1,
                                "template_id": 2,
                                "hit_points": 12,
                                "room": 1,
                                "next_attack_time": 0})

        new_enemy = Enemy.deserialize_from_dict(data)
        self.assertEqual(new_enemy.id, 1)
        self.assertEqual(new_enemy.name, "Thug")
        self.assertEqual(isinstance(new_enemy.template, EnemyTemplate), True)
        self.assertEqual(new_enemy.hit_points, 12)
        self.assertEqual(new_enemy.accuracy, 70)
        self.assertEqual(new_enemy.dodging, -10)
        self.assertEqual(new_enemy.strike_damage, 0)
        self.assertEqual(new_enemy.damage_absorb, 0)
        self.assertEqual(new_enemy.experience, 10)
        self.assertEqual(new_enemy.weapon, 41)
        self.assertEqual(new_enemy.money_min, 0)
        self.assertEqual(new_enemy.money_max, 4)
        self.assertEqual(new_enemy.loot, [[41, 1], [35, 2]])
