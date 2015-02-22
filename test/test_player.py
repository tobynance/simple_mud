import os
os.environ["SIMPLE_MUD_LOAD_PLAYERS"] = "false"
import unittest
from item import ItemDatabase
from player import Player, PlayerDatabase, PlayerRank
import player
from player import PlayerAttributes, PlayerAttributeSet
import test_utils

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
                            "attributes": {"BASE_ACCURACY": 0,
                                           "BASE_AGILITY": 3,
                                           "BASE_DAMAGE_ABSORB": 0,
                                           "BASE_DODGING": 0,
                                           "BASE_HEALTH": 1,
                                           "BASE_HP_REGEN": 0,
                                           "BASE_MAX_HIT_POINTS": 12,
                                           "BASE_STRENGTH": 1,
                                           "BASE_STRIKE_DAMAGE": 0},
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
        self.maxDiff = None
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
        self.assertEqual(test_player.attributes.MODIFIER_HEALTH, 0)
        self.assertEqual(test_player.attributes.MODIFIER_AGILITY, 0)
        self.assertEqual(test_player.attributes.MODIFIER_MAX_HIT_POINTS, 0)
        self.assertEqual(test_player.attributes.MODIFIER_ACCURACY, 0)
        self.assertEqual(test_player.attributes.MODIFIER_DODGING, 0)
        self.assertEqual(test_player.attributes.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(test_player.attributes.MODIFIER_DAMAGE_ABSORB, 0)
        self.assertEqual(test_player.attributes.MODIFIER_HP_REGEN, 0)

        self.assertEqual(test_player.attributes.STRENGTH, 1)
        self.assertEqual(test_player.attributes.HEALTH, 1)
        self.assertEqual(test_player.attributes.AGILITY, 3)
        self.assertEqual(test_player.attributes.MAX_HIT_POINTS, 22)
        self.assertEqual(test_player.attributes.ACCURACY, 9)
        self.assertEqual(test_player.attributes.DODGING, 9)
        self.assertEqual(test_player.attributes.STRIKE_DAMAGE, 0)
        self.assertEqual(test_player.attributes.DAMAGE_ABSORB, 0)
        self.assertEqual(test_player.attributes.HP_REGEN, 1)


########################################################################
class PlayerDatabaseTest(unittest.TestCase):
    ####################################################################
    @classmethod
    def setUpClass(cls):
        cls.player_data = open(os.path.join(data_folder, "players.json")).read()

    ####################################################################
    def setUp(self):
        self.player_database = PlayerDatabase()
        self.player = Player(28)
        self.player.name = "user"
        self.player_database.add_player(self.player)

    ####################################################################
    def test_load_from_string(self):
        self.fail()

    ####################################################################
    def test_load(self):
        player_database = PlayerDatabase.load(self.player_data, force=True)
        db_id = id(player_database)
        player_database = PlayerDatabase.load()
        self.assertEqual(db_id, id(player_database))

    ####################################################################
    def test_save_to_string(self):
        self.fail()

    ####################################################################
    def test_save(self):
        try:
            os.environ["SIMPLE_MUD_LOAD_PLAYERS"] = "true"
            with test_utils.temp_dir(prefix="player", suffix="json") as temp_dir:
                file_path = os.path.join(temp_dir, "players.json")
                user_player = self.player_database.by_id.values()[0]
                self.assertEqual(user_player.stat_points, 18)
                user_player.stat_points = 7
                self.player_database.save(file_path)

                player_database = PlayerDatabase.load(file_path, force=True)
                user_player = player_database.find(user_player.id)
                self.assertEqual(user_player.stat_points, 7)
        finally:
            os.environ["SIMPLE_MUD_LOAD_PLAYERS"] = "false"

    ####################################################################
    def test_add_player(self):
        user_player = self.player_database.by_id.values()[0]
        self.assertEqual(user_player.stat_points, 18)
        user_player.stat_points = 7
        result = self.player_database.save_to_string()

        player_database = PlayerDatabase()
        player_database.load_from_string(result)
        user_player = player_database.by_id.values()[0]
        self.assertEqual(user_player.stat_points, 7)

    ####################################################################
    def test_find_active(self):
        self.assertEqual(None, self.player_database.find_active("user"))
        user = self.player_database.find("user")
        user.active = True
        self.assertEqual(user, self.player_database.find_active("user"))

    ####################################################################
    def test_find_logged_in(self):
        self.assertEqual(None, self.player_database.find_logged_in("user"))
        user = self.player_database.find("user")
        user.logged_in = True
        self.assertEqual(user, self.player_database.find_logged_in("user"))

    ####################################################################
    def test_logout(self):
        user = self.player_database.find("user")
        user.logged_in = True
        self.assertTrue(self.player_database.find_logged_in("user").logged_in)
        self.player_database.logout(user.id)
        self.assertEqual(self.player_database.find_logged_in("user"), None)

    ####################################################################
    def add_players(self):
        player_database = player.PlayerDatabase()
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
        names = set([p.name for p in all])
        self.assertEqual(names, {"a", "b", "c", "d"})

    ####################################################################
    def test_all_logged_in(self):
        player_database = self.add_players()
        all = list(player_database.all_logged_in())
        names = set([p.name for p in all])
        self.assertEqual(names, {"a", "c"})

    ####################################################################
    def test_all_active(self):
        player_database = self.add_players()
        all = list(player_database.all_active())
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
        self.attr_set.MODIFIER_STRIKE_DAMAGE = 2
        self.attr_set.MODIFIER_MAX_HIT_POINTS = -15

    ####################################################################
    def test_recalculate_stats(self):
        self.attr_set.recalculating = True

        self.assertEqual(self.attr_set.BASE_AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(self.attr_set.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 0)

        self.assertEqual(self.attr_set.BASE_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.BASE_HEALTH, 1)

        self.assertEqual(self.attr_set.AGILITY, 3)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 22)
        self.assertEqual(self.attr_set.STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.HEALTH, 1)

        self.attr_set.BASE_HEALTH = 3
        self.assertEqual(self.attr_set.HEALTH, 1)
        self.attr_set.MODIFIER_HEALTH = 3
        self.assertEqual(self.attr_set.HEALTH, 1)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 3)

        ### Now allow recalculating to automatically happen again
        self.attr_set.recalculating = False
        self.attr_set.recalculate_stats()

        self.assertEqual(self.attr_set.BASE_AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(self.attr_set.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 0)

        self.assertEqual(self.attr_set.BASE_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.BASE_HEALTH, 3)

        self.assertEqual(self.attr_set.AGILITY, 3)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 24)
        self.assertEqual(self.attr_set.STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.HEALTH, 3)

        self.attr_set.BASE_HEALTH = 4
        self.assertEqual(self.attr_set.HEALTH, 4)
        self.attr_set.MODIFIER_HEALTH = 4
        self.assertEqual(self.attr_set.HEALTH, 4)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 0)

    ####################################################################
    def test_add_and_remove_item(self):
        item_db = ItemDatabase.load()
        item = item_db.find(55)
        self.attr_set.player.use_armor(item)
        self.assertEqual(self.attr_set.ACCURACY, 19)
        self.assertEqual(self.attr_set.AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_ACCURACY, 0)
        self.assertEqual(self.attr_set.BASE_AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_DAMAGE_ABSORB, 0)
        self.assertEqual(self.attr_set.BASE_DODGING, 0)
        self.assertEqual(self.attr_set.BASE_HEALTH, 1)
        self.assertEqual(self.attr_set.BASE_HP_REGEN, 0)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(self.attr_set.BASE_STRENGTH, 1)
        self.assertEqual(self.attr_set.BASE_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.DAMAGE_ABSORB, 5)
        self.assertEqual(self.attr_set.DODGING, 69)
        self.assertEqual(self.attr_set.HEALTH, 1)
        self.assertEqual(self.attr_set.HP_REGEN, 1)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 22)
        self.assertEqual(self.attr_set.MODIFIER_ACCURACY, 10)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(self.attr_set.MODIFIER_DAMAGE_ABSORB, 5)
        self.assertEqual(self.attr_set.MODIFIER_DODGING, 60)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_HP_REGEN, 0)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 0)
        self.assertEqual(self.attr_set.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_STRIKE_DAMAGE, 10)
        self.assertEqual(self.attr_set.STRENGTH, 1)
        self.assertEqual(self.attr_set.STRIKE_DAMAGE, 10)

        self.attr_set.player.remove_armor()
        self.assertEqual(self.attr_set.ACCURACY, 9)
        self.assertEqual(self.attr_set.AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_ACCURACY, 0)
        self.assertEqual(self.attr_set.BASE_AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_DAMAGE_ABSORB, 0)
        self.assertEqual(self.attr_set.BASE_DODGING, 0)
        self.assertEqual(self.attr_set.BASE_HEALTH, 1)
        self.assertEqual(self.attr_set.BASE_HP_REGEN, 0)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(self.attr_set.BASE_STRENGTH, 1)
        self.assertEqual(self.attr_set.BASE_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.DAMAGE_ABSORB, 0)
        self.assertEqual(self.attr_set.DODGING, 9)
        self.assertEqual(self.attr_set.HEALTH, 1)
        self.assertEqual(self.attr_set.HP_REGEN, 1)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 22)
        self.assertEqual(self.attr_set.MODIFIER_ACCURACY, 0)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(self.attr_set.MODIFIER_DAMAGE_ABSORB, 0)
        self.assertEqual(self.attr_set.MODIFIER_DODGING, 0)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_HP_REGEN, 0)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 0)
        self.assertEqual(self.attr_set.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.STRENGTH, 1)
        self.assertEqual(self.attr_set.STRIKE_DAMAGE, 0)

    ####################################################################
    def test_set_field(self):
        self.assertEqual(self.attr_set.BASE_AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 0)
        self.assertEqual(self.attr_set.AGILITY, 3)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 22)

        self.attr_set.BASE_AGILITY = 4
        self.attr_set.BASE_MAX_HIT_POINTS = 6
        self.attr_set.MODIFIER_AGILITY = 17
        self.attr_set.MODIFIER_MAX_HIT_POINTS = 17
        with self.assertRaises(AttributeError):
            self.attr_set.AGILITY = 17

        self.assertEqual(self.attr_set.BASE_AGILITY, 4)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 6)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 0)
        self.assertEqual(self.attr_set.AGILITY, 4)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 16)

        ### Now using __set_field()
        set_field = getattr(self.attr_set, "_PlayerAttributeSet__set_field")
        set_field("BASE_AGILITY", 4)
        set_field("BASE_MAX_HIT_POINTS", 40)
        set_field("MODIFIER_AGILITY", 17)
        set_field("MODIFIER_MAX_HIT_POINTS", 17)
        set_field("AGILITY", 17)

        self.assertEqual(self.attr_set.BASE_AGILITY, 4)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 40)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 17)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 17)
        self.assertEqual(self.attr_set.AGILITY, 17)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 16)

    ####################################################################
    def test_add_dynamic_bonuses(self):
        item_db = ItemDatabase.load()
        item = item_db.find(55)
        self.attr_set.player.use_armor(item)
        self.assertEqual(self.attr_set.ACCURACY, 19)
        self.assertEqual(self.attr_set.AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_ACCURACY, 0)
        self.assertEqual(self.attr_set.BASE_AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_DAMAGE_ABSORB, 0)
        self.assertEqual(self.attr_set.BASE_DODGING, 0)
        self.assertEqual(self.attr_set.BASE_HEALTH, 1)
        self.assertEqual(self.attr_set.BASE_HP_REGEN, 0)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(self.attr_set.BASE_STRENGTH, 1)
        self.assertEqual(self.attr_set.BASE_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.DAMAGE_ABSORB, 5)
        self.assertEqual(self.attr_set.DODGING, 69)
        self.assertEqual(self.attr_set.HEALTH, 1)
        self.assertEqual(self.attr_set.HP_REGEN, 1)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 22)
        self.assertEqual(self.attr_set.MODIFIER_ACCURACY, 10)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(self.attr_set.MODIFIER_DAMAGE_ABSORB, 5)
        self.assertEqual(self.attr_set.MODIFIER_DODGING, 60)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_HP_REGEN, 0)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 0)
        self.assertEqual(self.attr_set.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_STRIKE_DAMAGE, 10)
        self.assertEqual(self.attr_set.STRENGTH, 1)
        self.assertEqual(self.attr_set.STRIKE_DAMAGE, 10)

    ####################################################################
    def test_add_bonuses(self):
        item_db = ItemDatabase.load()
        item = item_db.find(55)
        self.assertEqual(item.attributes.STRENGTH, 0)
        self.assertEqual(item.attributes.HEALTH, 0)
        self.assertEqual(item.attributes.AGILITY, 0)
        self.assertEqual(item.attributes.MAX_HIT_POINTS, 0)
        self.assertEqual(item.attributes.ACCURACY, 10)
        self.assertEqual(item.attributes.DODGING, 60)
        self.assertEqual(item.attributes.STRIKE_DAMAGE, 10)
        self.assertEqual(item.attributes.DAMAGE_ABSORB, 5)
        self.assertEqual(item.attributes.HP_REGEN, 0)

        self.attr_set.add_bonuses(item)
        self.assertEqual(self.attr_set.ACCURACY, 19)
        self.assertEqual(self.attr_set.AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_ACCURACY, 10)
        self.assertEqual(self.attr_set.BASE_AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_DAMAGE_ABSORB, 5)
        self.assertEqual(self.attr_set.BASE_DODGING, 60)
        self.assertEqual(self.attr_set.BASE_HEALTH, 1)
        self.assertEqual(self.attr_set.BASE_HP_REGEN, 0)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(self.attr_set.BASE_STRENGTH, 1)
        self.assertEqual(self.attr_set.BASE_STRIKE_DAMAGE, 10)
        self.assertEqual(self.attr_set.DAMAGE_ABSORB, 5)
        self.assertEqual(self.attr_set.DODGING, 69)
        self.assertEqual(self.attr_set.HEALTH, 1)
        self.assertEqual(self.attr_set.HP_REGEN, 1)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 22)
        self.assertEqual(self.attr_set.MODIFIER_ACCURACY, 0)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(self.attr_set.MODIFIER_DAMAGE_ABSORB, 0)
        self.assertEqual(self.attr_set.MODIFIER_DODGING, 0)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_HP_REGEN, 0)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 0)
        self.assertEqual(self.attr_set.MODIFIER_STRENGTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.STRENGTH, 1)
        self.assertEqual(self.attr_set.STRIKE_DAMAGE, 10)

    ####################################################################
    def test_serialize_to_dict(self):
        serialized = self.attr_set.serialize_to_dict()
        attribute_data = {"BASE_ACCURACY": 0,
                          "BASE_AGILITY": 3,
                          "BASE_DAMAGE_ABSORB": 0,
                          "BASE_DODGING": 0,
                          "BASE_HEALTH": 1,
                          "BASE_HP_REGEN": 0,
                          "BASE_MAX_HIT_POINTS": 12,
                          "BASE_STRENGTH": 1,
                          "BASE_STRIKE_DAMAGE": 0}
        self.maxDiff = None
        self.assertEqual(attribute_data, serialized)

    ####################################################################
    def test_deserialize_from_dict(self):
        attribute_data = {"BASE_ACCURACY": 0,
                          "BASE_AGILITY": 3,
                          "BASE_DAMAGE_ABSORB": 0,
                          "BASE_DODGING": 0,
                          "BASE_HEALTH": 1,
                          "BASE_HP_REGEN": 0,
                          "BASE_MAX_HIT_POINTS": 12,
                          "BASE_STRENGTH": 1,
                          "BASE_STRIKE_DAMAGE": 0}

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
        self.assertEqual(attr_set.MODIFIER_HEALTH, 0)
        self.assertEqual(attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(attr_set.MODIFIER_MAX_HIT_POINTS, 0)
        self.assertEqual(attr_set.MODIFIER_ACCURACY, 0)
        self.assertEqual(attr_set.MODIFIER_DODGING, 0)
        self.assertEqual(attr_set.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(attr_set.MODIFIER_DAMAGE_ABSORB, 0)
        self.assertEqual(attr_set.MODIFIER_HP_REGEN, 0)

        self.assertEqual(attr_set.STRENGTH, 1)
        self.assertEqual(attr_set.HEALTH, 1)
        self.assertEqual(attr_set.AGILITY, 3)
        self.assertEqual(attr_set.MAX_HIT_POINTS, 22)
        self.assertEqual(attr_set.ACCURACY, 9)
        self.assertEqual(attr_set.DODGING, 9)
        self.assertEqual(attr_set.STRIKE_DAMAGE, 0)
        self.assertEqual(attr_set.DAMAGE_ABSORB, 0)
        self.assertEqual(attr_set.HP_REGEN, 1)

        ### And if we had armor on at the time...
        item_db = ItemDatabase.load()
        armor = item_db.find(55)
        p.use_armor(armor)
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
        self.assertEqual(attr_set.MODIFIER_HEALTH, 0)
        self.assertEqual(attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(attr_set.MODIFIER_MAX_HIT_POINTS, 0)
        self.assertEqual(attr_set.MODIFIER_ACCURACY, 10)
        self.assertEqual(attr_set.MODIFIER_DODGING, 60)
        self.assertEqual(attr_set.MODIFIER_STRIKE_DAMAGE, 10)
        self.assertEqual(attr_set.MODIFIER_DAMAGE_ABSORB, 5)
        self.assertEqual(attr_set.MODIFIER_HP_REGEN, 0)

        self.assertEqual(attr_set.STRENGTH, 1)
        self.assertEqual(attr_set.HEALTH, 1)
        self.assertEqual(attr_set.AGILITY, 3)
        self.assertEqual(attr_set.MAX_HIT_POINTS, 22)
        self.assertEqual(attr_set.ACCURACY, 19)
        self.assertEqual(attr_set.DODGING, 69)
        self.assertEqual(attr_set.STRIKE_DAMAGE, 10)
        self.assertEqual(attr_set.DAMAGE_ABSORB, 5)
        self.assertEqual(attr_set.HP_REGEN, 1)

    ####################################################################
    def test_use_enum_for_key(self):
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_AGILITY], 3)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_MAX_HIT_POINTS], 12)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_STRIKE_DAMAGE], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_HEALTH], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_AGILITY], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_MAX_HIT_POINTS], 0)

        self.assertEqual(self.attr_set[PlayerAttributes.BASE_STRIKE_DAMAGE], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_HEALTH], 1)

        self.assertEqual(self.attr_set[PlayerAttributes.AGILITY], 3)
        self.assertEqual(self.attr_set[PlayerAttributes.MAX_HIT_POINTS], 22)
        self.assertEqual(self.attr_set[PlayerAttributes.STRIKE_DAMAGE], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.HEALTH], 1)

    ####################################################################
    def test_use_int_for_key(self):
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_AGILITY.value], 3)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_MAX_HIT_POINTS.value], 12)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_STRIKE_DAMAGE.value], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_HEALTH.value], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_AGILITY.value], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.MODIFIER_MAX_HIT_POINTS.value], 0)

        self.assertEqual(self.attr_set[PlayerAttributes.BASE_STRIKE_DAMAGE.value], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.BASE_HEALTH.value], 1)

        self.assertEqual(self.attr_set[PlayerAttributes.AGILITY.value], 3)
        self.assertEqual(self.attr_set[PlayerAttributes.MAX_HIT_POINTS.value], 22)
        self.assertEqual(self.attr_set[PlayerAttributes.STRIKE_DAMAGE.value], 0)
        self.assertEqual(self.attr_set[PlayerAttributes.HEALTH.value], 1)

    ####################################################################
    def test_use_string_for_key(self):
        self.assertEqual(self.attr_set["BASE_AGILITY"], 3)
        self.assertEqual(self.attr_set["BASE_MAX_HIT_POINTS"], 12)
        self.assertEqual(self.attr_set["MODIFIER_STRIKE_DAMAGE"], 0)
        self.assertEqual(self.attr_set["MODIFIER_HEALTH"], 0)
        self.assertEqual(self.attr_set["MODIFIER_AGILITY"], 0)
        self.assertEqual(self.attr_set["MODIFIER_MAX_HIT_POINTS"], 0)

        self.assertEqual(self.attr_set["BASE_STRIKE_DAMAGE"], 0)
        self.assertEqual(self.attr_set["BASE_HEALTH"], 1)

        self.assertEqual(self.attr_set["AGILITY"], 3)
        self.assertEqual(self.attr_set["MAX_HIT_POINTS"], 22)
        self.assertEqual(self.attr_set["STRIKE_DAMAGE"], 0)
        self.assertEqual(self.attr_set["HEALTH"], 1)

    ####################################################################
    def test_use_attributes_directly(self):
        self.assertEqual(self.attr_set.BASE_AGILITY, 3)
        self.assertEqual(self.attr_set.BASE_MAX_HIT_POINTS, 12)
        self.assertEqual(self.attr_set.MODIFIER_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.MODIFIER_HEALTH, 0)
        self.assertEqual(self.attr_set.MODIFIER_AGILITY, 0)
        self.assertEqual(self.attr_set.MODIFIER_MAX_HIT_POINTS, 0)

        self.assertEqual(self.attr_set.BASE_STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.BASE_HEALTH, 1)

        self.assertEqual(self.attr_set.AGILITY, 3)
        self.assertEqual(self.attr_set.MAX_HIT_POINTS, 22)
        self.assertEqual(self.attr_set.STRIKE_DAMAGE, 0)
        self.assertEqual(self.attr_set.HEALTH, 1)

        self.attr_set.BASE_HEALTH = 3
        self.assertEqual(self.attr_set.HEALTH, 3)
        self.attr_set.MODIFIER_HEALTH = 3
        self.assertEqual(self.attr_set.HEALTH, 3)

    ####################################################################
    def test_setting(self):
        p = Player()
        attr_set = p.attributes
        attr_set[PlayerAttributes.BASE_STRENGTH] = 1
        attr_set[PlayerAttributes.MODIFIER_HEALTH] = 3
        attr_set[PlayerAttributes.MODIFIER_STRIKE_DAMAGE] = 3
        attr_set[PlayerAttributes.BASE_STRIKE_DAMAGE] = 5
        attr_set[PlayerAttributes.BASE_HP_REGEN] = 7

        self.assertEqual(attr_set[PlayerAttributes.BASE_STRENGTH], 1)
        self.assertEqual(attr_set[PlayerAttributes.STRIKE_DAMAGE], 5)
        self.assertEqual(attr_set[PlayerAttributes.MODIFIER_HEALTH], 0)
        self.assertEqual(attr_set[PlayerAttributes.BASE_STRIKE_DAMAGE], 5)
        self.assertEqual(attr_set[PlayerAttributes.BASE_HP_REGEN], 7)
        self.assertEqual(attr_set[PlayerAttributes.DAMAGE_ABSORB], 0)
