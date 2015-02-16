import os
import tempfile
import unittest
from attributes import PlayerRank
from player import Player, PlayerDatabase
import player

base = os.path.dirname(__file__)
data_folder = os.path.join(base, "data")


########################################################################
class PlayerTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        self.player = Player(1)
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

        self.player_data = {"id": 1,
                            "armor": None,
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
    def test_player_rank_order(self):
        self.assertTrue(PlayerRank.REGULAR < PlayerRank.MODERATOR)
        self.assertTrue(PlayerRank.MODERATOR < PlayerRank.ADMIN)
        self.assertFalse(PlayerRank.REGULAR > PlayerRank.ADMIN)

    ####################################################################
    def test_who_text(self):
        self.fail()

    ####################################################################
    def test_serialize_to_dict(self):
        player_data = self.player.serialize_to_dict()
        self.assertEqual(self.player_data, player_data)

    ####################################################################
    def test_deserialize_from_dict(self):
        test_player = Player.deserialize_from_dict(self.player_data)

        self.assertEqual(test_player.name, "jerry_john")
        self.assertEqual(test_player.password, "supersecret")
        self.assertEqual(test_player.experience, 17)
        self.assertEqual(test_player.level, 1)
        self.assertEqual(test_player.rank, PlayerRank.MODERATOR)
        self.assertEqual(test_player.stat_points, 16)
        self.assertEqual(test_player.armor, None)
        self.assertEqual(test_player.weapon, None)
        self.assertEqual(test_player.attributes.STRENGTH, 0)
        self.assertEqual(test_player.attributes.HEALTH, 0)
        self.assertEqual(test_player.attributes.AGILITY, 3)
        self.assertEqual(test_player.attributes.MAX_HIT_POINTS, 12)
        self.assertEqual(test_player.attributes.ACCURACY, 0)
        self.assertEqual(test_player.attributes.DODGING, 0)
        self.assertEqual(test_player.attributes.STRIKE_DAMAGE, 2)
        self.assertEqual(test_player.attributes.DAMAGE_ABSORB, 0)
        self.assertEqual(test_player.attributes.HP_REGEN, 1)

        self.assertEqual(test_player.base_attributes.STRENGTH, 1)
        self.assertEqual(test_player.base_attributes.HEALTH, 1)
        self.assertEqual(test_player.base_attributes.AGILITY, 1)
        self.assertEqual(test_player.base_attributes.MAX_HIT_POINTS, 0)
        self.assertEqual(test_player.base_attributes.ACCURACY, 0)
        self.assertEqual(test_player.base_attributes.DODGING, 0)
        self.assertEqual(test_player.base_attributes.STRIKE_DAMAGE, 0)
        self.assertEqual(test_player.base_attributes.DAMAGE_ABSORB, 0)
        self.assertEqual(test_player.base_attributes.HP_REGEN, 0)


########################################################################
class PlayerDatabaseTest(unittest.TestCase):
    ####################################################################
    @classmethod
    def setUpClass(cls):
        cls.player_data = open(os.path.join(data_folder, "players.json")).read()

    ####################################################################
    def setUp(self):
        PlayerDatabase.db = None
        self.temp_data_file = tempfile.NamedTemporaryFile()
        self.temp_data_file.write(self.player_data)
        self.temp_data_file.flush()
        player.data_file = self.temp_data_file.name

    ####################################################################
    def tearDown(self):
        self.temp_data_file.close()
        PlayerDatabase.db = None
        player.data_file = None

    ####################################################################
    def test_load(self):
        self.assertEqual(PlayerDatabase.db, None)
        player_database = PlayerDatabase.load()
        db_id = id(player_database)
        player_database = PlayerDatabase.load()
        self.assertEqual(db_id, id(player_database))

    ####################################################################
    def test_save(self):
        player_database = PlayerDatabase.load()
        user_player = player_database.by_id.values()[0]
        self.assertEqual(user_player.stat_points, 18)
        user_player.stat_points = 7
        player_database.save()

        PlayerDatabase.db = None
        player_database = PlayerDatabase.load()
        user_player = player_database.by_id.values()[0]
        self.assertEqual(user_player.stat_points, 7)

    ####################################################################
    def test_add_player(self):
        player_database = PlayerDatabase.load()
        user_player = player_database.by_id.values()[0]
        self.assertEqual(user_player.stat_points, 18)
        user_player.stat_points = 7
        player_database.save()

        PlayerDatabase.db = None
        player_database = PlayerDatabase.load()
        user_player = player_database.by_id.values()[0]
        self.assertEqual(user_player.stat_points, 7)

    ####################################################################
    def test_find_active(self):
        player_database = PlayerDatabase.load()
        self.assertEqual(None, player_database.find_active("user"))
        user = player_database.find("user")
        user.active = True
        self.assertEqual(user, player_database.find_active("user"))

    ####################################################################
    def test_find_logged_in(self):
        player_database = PlayerDatabase.load()
        self.assertEqual(None, player_database.find_logged_in("user"))
        user = player_database.find("user")
        user.logged_in = True
        self.assertEqual(user, player_database.find_logged_in("user"))

    ####################################################################
    def test_logout(self):
        player_database = PlayerDatabase.load()
        user = player_database.find("user")
        user.logged_in = True
        self.assertTrue(player_database.find_logged_in("user").logged_in)
        player_database.logout(1)
        self.assertEqual(player_database.find_logged_in("user"), None)

    ####################################################################
    def test_all(self):
        self.fail()

    ####################################################################
    def test_all_logged_in(self):
        self.fail()

    ####################################################################
    def test_all_active(self):
        self.fail()
