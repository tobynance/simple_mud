import unittest
from attributes import Direction
import item
import player
from room import Room, RoomDatabase, RoomType
import room


########################################################################
class RoomTest(unittest.TestCase):
    ####################################################################
    def setUp(self):
        self.room = Room()
        self.room.type = RoomType.TRAINING_ROOM
        self.room.id = 3
        self.room.description = "Just a plain room"

    ####################################################################
    def test_deserialize_from_dict(self):
        short_sword = item.item_database.find(2)
        leather_armor = item.item_database.find(3)
        healing_potion = item.item_database.find(5)
        room_template_data = {
            "id": 50,
            "name": "Sewage Trench",
            "description": "You're in a sewage trench, filled with all sorts of liquid refuse, slowly flowing eastward into the town sewers.",
            "type": "PLAIN_ROOM",
            "data": 0,
            "north": 49,
            "east": 51,
            "south": 0,
            "west": 0,
            "spawn_which_enemy": 9,
            "max_enemies": 1,
            "starting_items": [2, 3],
            "starting_money": 30
        }
        this_room = Room.deserialize_from_dict(room_template_data, {})
        self.assertEqual(this_room.id, 50)
        self.assertEqual(this_room.name, "Sewage Trench")
        self.assertEqual(this_room.type, RoomType.PLAIN_ROOM)
        # self.assertEqual(this_room.data, 0)
        self.assertEqual(len(this_room.connecting_rooms), 2)
        self.assertEqual(this_room.connecting_rooms[Direction.NORTH], 49)
        self.assertEqual(this_room.connecting_rooms[Direction.EAST], 51)
        self.assertEqual(this_room.spawn_which_enemy, 9)
        self.assertEqual(this_room.max_enemies, 1)
        self.assertEqual(this_room.items, [short_sword, leather_armor])
        self.assertEqual(this_room.money, 30)

        room_dynamic_data = {"id": 50,
                             "items": [5],
                             "money": 2}

        this_room = Room.deserialize_from_dict(room_template_data, room_dynamic_data)
        self.assertEqual(this_room.id, 50)
        self.assertEqual(this_room.name, "Sewage Trench")
        self.assertEqual(this_room.type, RoomType.PLAIN_ROOM)
        # self.assertEqual(this_room.data, 0)
        self.assertEqual(len(this_room.connecting_rooms), 2)
        self.assertEqual(this_room.connecting_rooms[Direction.NORTH], 49)
        self.assertEqual(this_room.connecting_rooms[Direction.EAST], 51)
        self.assertEqual(this_room.spawn_which_enemy, 9)
        self.assertEqual(this_room.max_enemies, 1)
        self.assertEqual(this_room.items, [healing_potion])
        self.assertEqual(this_room.money, 2)

    ####################################################################
    def test_serialize_to_dict(self):
        self.fail()
        # output = {"items": [], "money": self.money}
        # for item in self.items:
        #     output["items"].append(item.id)
        # return output

    ####################################################################
    def test_get_adjacent_room(self):
        self.fail()
        # return self.connecting_rooms.get(direction)

    ####################################################################
    def test_add_player(self):
        self.assertEqual(self.room.players, set())
        p = player.Player(22)
        p.name = "jerry"
        player.player_database.add_player(p)
        self.room.add_player(p)
        self.assertEqual(self.room.players, {p})

    ####################################################################
    def test_remove_player(self):
        p = player.Player(22)
        p.name = "jerry"
        player.player_database.add_player(p)
        self.room.add_player(p)
        self.assertEqual(self.room.players, {p})

        self.room.remove_player(p)
        self.assertEqual(self.room.players, set())

    ####################################################################
    def test_find_item(self):
        power_armor = item.item_database.find(55)
        darkness_armor = item.item_database.find(54)
        self.room.add_item(power_armor)
        self.room.add_item(darkness_armor)
        self.assertEqual(self.room.find_item("darkness"), darkness_armor)
        self.assertEqual(self.room.find_item("power"), power_armor)
        self.assertEqual(self.room.find_item("armor"), power_armor)

    ####################################################################
    def test_add_item(self):
        armor = item.item_database.find(55)
        self.assertEqual(self.room.items, [])
        self.room.add_item(armor)
        self.assertEqual(self.room.items, [armor])

        self.room.remove_item(armor)

        # Test MAX_ITEMS limit
        for i in range(1, room.MAX_ITEMS + 3):
            self.room.add_item(item.item_database.find(i))

        items_ids_left = [x.id for x in self.room.items]
        self.assertEqual(items_ids_left, range(3, room.MAX_ITEMS + 3))

    ####################################################################
    def test_remove_item(self):
        armor = item.item_database.find(55)
        self.room.add_item(armor)
        self.assertEqual(self.room.items, [armor])
        self.room.remove_item(armor)
        self.assertEqual(self.room.items, [])

    ####################################################################
    def test_find_enemy(self):
        self.fail()
        # return utils.double_find_by_name(enemy_name, self.enemies)

    ####################################################################
    def test_add_enemy(self):
        self.fail()
        # self.enemies.add(enemy)

    ####################################################################
    def test_remove_enemy(self):
        self.fail()
        # self.enemies.remove(enemy)


########################################################################
class RoomDatabaseTest(unittest.TestCase):
    ####################################################################
    def test_load(self):
        room.room_database = RoomDatabase.load(force=True, room_data_path="some_random_place")
        self.assertEqual(len(room.room_database.by_id), 57)
        self.assertEqual(len(room.room_database.by_name), 38)

        self.assertEqual(room.room_database.find(40).name, "Rusty Knife")
        self.assertEqual(room.room_database.find_full("Dagger").id, 42)
        self.assertEqual(room.room_database.find("Rusty").id, 40)
        self.assertEqual(room.room_database.find("Short").id, 2)

        this_room = room.room_database.find(1)
        self.assertEqual(this_room.id, 1)
        self.assertEqual(this_room.name, "Town Square")
        self.assertEqual(this_room.description, "You are in the town square. This is the central meeting place for the realm.")
        self.assertEqual(this_room.type, RoomType.PLAIN_ROOM)
        self.assertEqual(this_room.connecting_rooms, {Direction.NORTH: 2, Direction.EAST: 25, Direction.SOUTH: 4, Direction.WEST: 5})
        self.assertEqual(this_room.spawn_which_enemy, None)
        self.assertEqual(this_room.max_enemies, 0)
        self.assertEqual(this_room.items, 0)
        self.assertEqual(this_room.money, 0)

        this_room = room.room_database.find("Platemail armor of power")
        self.assertEqual(this_room.id, 55)
        self.assertEqual(this_room.name, "Platemail Armor of Power")
        self.assertEqual(this_room.type, RoomType.ARMOR)
        self.assertEqual(this_room.min, 0)
        self.assertEqual(this_room.max, 0)
        self.assertEqual(this_room.price, 15000)
        self.assertEqual(this_room.speed, 0)
        self.assertEqual(this_room.attributes.STRENGTH, 0)
        self.assertEqual(this_room.attributes.HEALTH, 0)
        self.assertEqual(this_room.attributes.AGILITY, 0)
        self.assertEqual(this_room.attributes.MAX_HIT_POINTS, 0)
        self.assertEqual(this_room.attributes.ACCURACY, 10)
        self.assertEqual(this_room.attributes.DODGING, 60)
        self.assertEqual(this_room.attributes.STRIKE_DAMAGE, 10)
        self.assertEqual(this_room.attributes.DAMAGE_ABSORB, 5)
        self.assertEqual(this_room.attributes.HP_REGEN, 0)
