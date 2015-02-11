import unittest
from attributes import PlayerRank
from player import Player, PlayerDatabase


########################################################################
class PlayerTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        self.player = Player()
        self.player.name = "jerry_john"
        self.player.password = "supersecret"
        self.player.money = 1823
        self.player.experience = 17
        self.player.rank = PlayerRank.MODERATOR
        self.player.room = 3
        self.player.stat_points = 16
        self.player.attributes.AGILITY = 3
        self.player.attributes.MAX_HIT_POINTS = 12
        self.player.attributes.STRIKE_DAMAGE = 2

        self.player_data = {"armor": None,
                            "attributes": {1: 0, 2: 0, 3: 3, 4: 12, 5: 0, 6: 0, 7: 2, 8: 0, 9: 1},
                            "base_attributes": {1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                            "experience": 17,
                            "inventory": [],
                            "level": 1,
                            "money": 1823,
                            "name": "jerry_john",
                            "next_attack_time": 0,
                            "password": "supersecret",
                            "rank": 2,
                            "room": 3,
                            "stat_points": 16,
                            "weapon": None}

    ####################################################################
    def test_serialize_to_dict(self):
        player_data = self.player.serialize_to_dict()
        self.assertEqual(self.player_data, player_data)

    ####################################################################
    def test_deserialize_from_dict(self):
        player = Player.deserialize_from_dict(self.player_data)

        self.assertEqual(player.name, "jerry_john")
        self.assertEqual(player.password, "supersecret")
        self.assertEqual(player.experience, 17)
        self.assertEqual(player.level, 1)
        self.assertEqual(player.rank, PlayerRank.MODERATOR)
        self.assertEqual(player.stat_points, 16)
        self.assertEqual(player.armor, None)
        self.assertEqual(player.weapon, None)
        self.assertEqual(player.attributes.STRENGTH, 0)
        self.assertEqual(player.attributes.HEALTH, 0)
        self.assertEqual(player.attributes.AGILITY, 3)
        self.assertEqual(player.attributes.MAX_HIT_POINTS, 12)
        self.assertEqual(player.attributes.ACCURACY, 0)
        self.assertEqual(player.attributes.DODGING, 0)
        self.assertEqual(player.attributes.STRIKE_DAMAGE, 2)
        self.assertEqual(player.attributes.DAMAGE_ABSORB, 0)
        self.assertEqual(player.attributes.HP_REGEN, 1)

        self.assertEqual(player.base_attributes.STRENGTH, 1)
        self.assertEqual(player.base_attributes.HEALTH, 1)
        self.assertEqual(player.base_attributes.AGILITY, 1)
        self.assertEqual(player.base_attributes.MAX_HIT_POINTS, 0)
        self.assertEqual(player.base_attributes.ACCURACY, 0)
        self.assertEqual(player.base_attributes.DODGING, 0)
        self.assertEqual(player.base_attributes.STRIKE_DAMAGE, 0)
        self.assertEqual(player.base_attributes.DAMAGE_ABSORB, 0)
        self.assertEqual(player.base_attributes.HP_REGEN, 0)


########################################################################
class PlayerDatabaseTest(unittest.TestCase):
    ####################################################################
    def test_load(self):
        self.fail()

    ####################################################################
    def test_save(self):
        self.fail()

    ####################################################################
    def test_add_player(self):
        self.fail()

    ####################################################################
    def test_find_active(self):
        self.fail()

    ####################################################################
    def test_find_logged_in(self):
        self.fail()

    ####################################################################
    def test_log_out(self):
        self.fail()
