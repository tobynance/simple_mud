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
        self.attr_set.MODIFIER_HEALTH = 11
        self.attr_set.MODIFIER_AGILITY = -8

    ####################################################################
    def test_read_only_fields_are_read_only(self):
        with self.assertRaises(AttributeError):
            self.attr_set.MODIFIER_STRIKE_DAMAGE = 2
        with self.assertRaises(AttributeError):
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
        attr_set = PlayerAttributeSet()
        attr_set[PlayerAttributes.STRENGTH] = 1
        attr_set[PlayerAttributes.HEALTH] = 3
        attr_set[PlayerAttributes.STRIKE_DAMAGE] = 5
        attr_set[PlayerAttributes.HP_REGEN] = 7
        serialized = attr_set.serialize_to_dict()
        expected = {"ACCURACY": 0,
                    "AGILITY": 0,
                    "DAMAGE_ABSORB": 0,
                    "DODGING": 0,
                    "HEALTH": 3,
                    "HP_REGEN": 7,
                    "MAX_HIT_POINTS": 0,
                    "STRENGTH": 1,
                    "STRIKE_DAMAGE": 5}
        self.assertEqual(expected, serialized)

    ####################################################################
    def test_deserialize_from_dict(self):
        attribute_data = {"ACCURACY": 3,
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
                          "STRIKE_DAMAGE": 0}

        p = Player()
        attr_set = PlayerAttributeSet.deserialize_from_dict(attribute_data, player=p)

        self.assertEqual(attr_set.BASE_STRENGTH, 1)
        self.assertEqual(attr_set.BASE_HEALTH, 1)
        self.assertEqual(attr_set.BASE_AGILITY, 3)
        self.assertEqual(attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(attr_set.BASE_ACCURACY, 0)
        self.assertEqual(attr_set.BASE_DODGING, 0)
        self.assertEqual(attr_set.BASE_STRIKE_DAMAGE, 0)
        self.assertEqual(attr_set.BASE_DAMAGE_ABSORB, 0)
        self.assertEqual(attr_set.BASE_HP_REGEN, 0)

        self.assertEqual(attr_set.MODIFIER_STRENGTH, 0)
        self.assertEqual(attr_set.MODIFIER_HEALTH, 11)
        self.assertEqual(attr_set.MODIFIER_AGILITY, -8)
        self.assertEqual(attr_set.MODIFIER_MAX_HIT_POINTS, 18)
        self.assertEqual(attr_set.MODIFIER_ACCURACY, 3)
        self.assertEqual(attr_set.MODIFIER_DODGING, 3)
        self.assertEqual(attr_set.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(attr_set.MODIFIER_DAMAGE_ABSORB, 0)
        self.assertEqual(attr_set.MODIFIER_HP_REGEN, 3)

        self.assertEqual(attr_set.STRENGTH, 1)
        self.assertEqual(attr_set.HEALTH, 12)
        self.assertEqual(attr_set.AGILITY, 1)
        self.assertEqual(attr_set.MAX_HIT_POINTS, 30)
        self.assertEqual(attr_set.ACCURACY, 3)
        self.assertEqual(attr_set.DODGING, 3)
        self.assertEqual(attr_set.STRIKE_DAMAGE, 0)
        self.assertEqual(attr_set.DAMAGE_ABSORB, 0)
        self.assertEqual(attr_set.HP_REGEN, 3)

    ####################################################################
    def test_use_enum_for_key(self):
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_AGILITY], 3)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_MAX_HIT_POINTS], 12)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_STRIKE_DAMAGE], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_HEALTH], 11)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_AGILITY], -8)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_MAX_HIT_POINTS], 18)

        self.assertEqual(self.attr_set[PlayerAttributes.BASE_STRIKE_DAMAGE], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_HEALTH], 1)

        self.assertEqual(self.attr_set[PlayerAttributes.AGILITY], 1)
        self.assertEqual(self.attr_set[PlayerAttributes.MAX_HIT_POINTS], 30)
        self.assertEqual(self.attr_set[PlayerAttributes.STRIKE_DAMAGE], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.HEALTH], 12)

    ####################################################################
    def test_use_int_for_key(self):
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_AGILITY.value], 3)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_MAX_HIT_POINTS.value], 12)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_STRIKE_DAMAGE.value], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_HEALTH.value], 11)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_AGILITY.value], -8)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_MAX_HIT_POINTS.value], 18)

        self.assertEqual(self.attr_set[PlayerAttributes.BASE_STRIKE_DAMAGE.value], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_HEALTH.value], 1)

        self.assertEqual(self.attr_set[PlayerAttributes.AGILITY.value], 1)
        self.assertEqual(self.attr_set[PlayerAttributes.MAX_HIT_POINTS.value], 30)
        self.assertEqual(self.attr_set[PlayerAttributes.STRIKE_DAMAGE.value], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.HEALTH.value], 12)

    ####################################################################
    def test_use_string_for_key(self):
        self.assertEqual(self.attr_set["BASE_AGILITY"], 3)
        self.assertEqual(self.attr_set["BASE_MAX_HIT_POINTS"], 12)
        self.assertEqual(self.attr_set["MODIFIER_STRIKE_DAMAGE"], 0)
        self.assertEqual(self.attr_set["MODIFIER_HEALTH"], 11)
        self.assertEqual(self.attr_set["MODIFIER_AGILITY"], -8)
        self.assertEqual(self.attr_set["MODIFIER_MAX_HIT_POINTS"], 18)

        self.assertEqual(self.attr_set["BASE_STRIKE_DAMAGE"], 0)
        self.assertEqual(self.attr_set["BASE_HEALTH"], 1)

        self.assertEqual(self.attr_set["AGILITY"], 1)
        self.assertEqual(self.attr_set["MAX_HIT_POINTS"], 30)
        self.assertEqual(self.attr_set["STRIKE_DAMAGE"], 0)
        self.assertEqual(self.attr_set["HEALTH"], 12)

    ####################################################################
    def test_use_attributes_directly(self):
        self.assertEqual(self.attr_set.BASE_AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(self.attr_set.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 11)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, -8)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 18)

        self.assertEqual(self.attr_set.BASE_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.BASE_HEALTH, 1)

        self.assertEqual(self.attr_set.AGILITY, 1)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 30)
        self.assertEqual(self.attr_set.STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.HEALTH, 12)

        self.attr_set.BASE_HEALTH = 3
        self.assertEqual(self.attr_set.HEALTH, 14)
        self.attr_set.MODIFIER_HEALTH = 3
        self.assertEqual(self.attr_set.HEALTH, 6)

    ####################################################################
    def test_setting(self):
        attr_set = PlayerAttributeSet()
        attr_set[PlayerAttributes.BASE_STRENGTH] = 1
        attr_set[PlayerAttributes.MODIFIER_HEALTH] = 3
        attr_set[PlayerAttributes.BASE_STRIKE_DAMAGE] = 5
        attr_set[PlayerAttributes.BASE_HP_REGEN] = 7

        self.assertEqual(attr_set[PlayerAttributes.BASE_STRENGTH], 1)
        self.assertEqual(attr_set[PlayerAttributes.MODIFIER_HEALTH], 3)
        self.assertEqual(attr_set[PlayerAttributes.BASE_STRIKE_DAMAGE], 5)
        self.assertEqual(attr_set[PlayerAttributes.BASE_HP_REGEN], 7)
        self.assertEqual(attr_set[PlayerAttributes.DAMAGE_ABSORB], 0)
