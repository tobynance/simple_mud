import os
import tempfile
import unittest
from attributes import PlayerRank
from player import Player, PlayerDatabase
import player
from player import PlayerAttributes, PlayerAttributeSet

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
        self.player.attributes.BASE_AGILITY = 3
        self.player.attributes.BASE_MAX_HIT_POINTS = 12
        self.player.attributes.MODIFIER_STRIKE_DAMAGE = 2
        self.player.attributes.MODIFIER_HEALTH = 11
        self.player.attributes.MODIFIER_AGILITY = -8

        self.player_data = {"id": 1,
                            "armor": None,
                            "attributes": {"ACCURACY": 3,
                                           "AGILITY": 1,
                                           "BASE_ACCURACY": 0,
                                           "BASE_AGILITY": 3,
                                           "BASE_DAMAGE_ABSORB": 0,
                                           "BASE_DODGING": 0,
                                           "BASE_HEALTH": 1,
                                           "BASE_HP_REGEN": 0,
                                           "BASE_MAX_HIT_POINTS": 12,
                                           "BASE_STRENGTH": 1,
                                           "BASE_STRIKE_DAMAGE": 0,
                                           "DAMAGE_ABSORB": 0,
                                           "DODGING": 3,
                                           "HEALTH": 12,
                                           "HP_REGEN": 3,
                                           "MAX_HIT_POINTS": 30,
                                           "MODIFIER_ACCURACY": 3,
                                           "MODIFIER_AGILITY": -8,
                                           "MODIFIER_DAMAGE_ABSORB": 0,
                                           "MODIFIER_DODGING": 3,
                                           "MODIFIER_HEALTH": 11,
                                           "MODIFIER_HP_REGEN": 3,
                                           "MODIFIER_MAX_HIT_POINTS": 18,
                                           "MODIFIER_STRENGTH": 0,
                                           "MODIFIER_STRIKE_DAMAGE": 0,
                                           "STRENGTH": 1,
                                           "STRIKE_DAMAGE": 0},
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
        m = ' jerry_john       | 1         | <red>Offline <white> | <yellow>MODERATOR<white>\r\n'
        self.assertEqual(self.player.who_text(), m)

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

        self.assertEqual(test_player.attributes.BASE_STRENGTH, 1)
        self.assertEqual(test_player.attributes.BASE_HEALTH, 1)
        self.assertEqual(test_player.attributes.BASE_AGILITY, 3)
        self.assertEqual(test_player.attributes.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(test_player.attributes.BASE_ACCURACY, 0)
        self.assertEqual(test_player.attributes.BASE_DODGING, 0)
        self.assertEqual(test_player.attributes.BASE_STRIKE_DAMAGE, 0)
        self.assertEqual(test_player.attributes.BASE_DAMAGE_ABSORB, 0)
        self.assertEqual(test_player.attributes.BASE_HP_REGEN, 0)

        self.assertEqual(test_player.attributes.MODIFIER_STRENGTH, 0)
        self.assertEqual(test_player.attributes.MODIFIER_HEALTH, 11)
        self.assertEqual(test_player.attributes.MODIFIER_AGILITY, -8)
        self.assertEqual(test_player.attributes.MODIFIER_MAX_HIT_POINTS, 18)
        self.assertEqual(test_player.attributes.MODIFIER_ACCURACY, 3)
        self.assertEqual(test_player.attributes.MODIFIER_DODGING, 3)
        self.assertEqual(test_player.attributes.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(test_player.attributes.MODIFIER_DAMAGE_ABSORB, 0)
        self.assertEqual(test_player.attributes.MODIFIER_HP_REGEN, 3)

        self.assertEqual(test_player.attributes.STRENGTH, 1)
        self.assertEqual(test_player.attributes.HEALTH, 12)
        self.assertEqual(test_player.attributes.AGILITY, 1)
        self.assertEqual(test_player.attributes.MAX_HIT_POINTS, 30)
        self.assertEqual(test_player.attributes.ACCURACY, 3)
        self.assertEqual(test_player.attributes.DODGING, 3)
        self.assertEqual(test_player.attributes.STRIKE_DAMAGE, 0)
        self.assertEqual(test_player.attributes.DAMAGE_ABSORB, 0)
        self.assertEqual(test_player.attributes.HP_REGEN, 3)


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
        player.player_database = PlayerDatabase()

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
    def add_players(self):
        player_database = player.player_database
        p = Player()
        p.name = "a"
        p.logged_in = True
        p.active = True
        player_database.add_player(p)

        p = Player()
        p.name = "b"
        p.logged_in = False
        p.active = True
        player_database.add_player(p)

        p = Player()
        p.name = "c"
        p.logged_in = True
        p.active = False
        player_database.add_player(p)

        p = Player()
        p.name = "d"
        p.logged_in = False
        p.active = False
        player_database.add_player(p)
        return player_database

    ####################################################################
    def test_all(self):
        player_database = self.add_players()
        all = player_database.all()
        self.assertEqual(len(all), 4)
        names = set([p.name for p in all])
        self.assertEqual(names, {"a", "b", "c", "d"})

    ####################################################################
    def test_all_logged_in(self):
        player_database = self.add_players()
        all = list(player_database.all_logged_in())
        self.assertEqual(len(all), 2)
        names = set([p.name for p in all])
        self.assertEqual(names, {"a", "c"})

    ####################################################################
    def test_all_active(self):
        player_database = self.add_players()
        all = list(player_database.all_active())
        self.assertEqual(len(all), 2)
        names = set([p.name for p in all])
        self.assertEqual(names, {"a", "b"})


########################################################################
class PlayerAttributeSetTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        p = Player()
        self.attr_set = p.attributes
        self.attr_set.BASE_AGILITY = 3
        self.attr_set.BASE_MAX_HIT_POINTS = 12
        self.attr_set.MODIFIER_STRIKE_DAMAGE = 2
        self.attr_set.MODIFIER_HEALTH = 11
        self.attr_set.MODIFIER_AGILITY = -8
        self.attr_set.MODIFIER_MAX_HIT_POINTS = -15

    ####################################################################
    def test_recalculate_stats(self):
        self.fail()

    ####################################################################
    def test_set_field(self):
        self.fail()

    ####################################################################
    def test_add_dynamic_bonuses(self):
        self.fail()

    ####################################################################
    def test_set_base_attr(self):
        self.fail()

    ####################################################################
    def test_add_bonuses(self):
        self.fail()

    ####################################################################
    def test_serialize_to_dict(self):
        self.fail()

    ####################################################################
    def test_deserialize_from_dict(self):
        self.fail()

    ####################################################################
    def test_use_enum_for_key(self):
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_AGILITY], 3)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_MAX_HIT_POINTS], 12)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_STRIKE_DAMAGE], 0)  # Changed, since this is a calculated value
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_HEALTH], 11)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_AGILITY], -8)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_MAX_HIT_POINTS], -15)

        self.assertEqual(self.attr_set[PlayerAttributes.BASE_STRIKE_DAMAGE], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_HEALTH], 0)

        self.assertEqual(self.attr_set[PlayerAttributes.AGILITY], 1)
        self.assertEqual(self.attr_set[PlayerAttributes.MAX_HIT_POINTS], -3)
        self.assertEqual(self.attr_set[PlayerAttributes.STRIKE_DAMAGE], 2)
        self.assertEqual(self.attr_set[PlayerAttributes.HEALTH], 11)

    ####################################################################
    def test_use_int_for_key(self):
        self.fail()

    ####################################################################
    def test_use_string_for_key(self):
        self.fail()

    ####################################################################
    def test_use_attributes_directly(self):
        self.fail()

    ####################################################################
    def test_setting(self):
        self.fail()
