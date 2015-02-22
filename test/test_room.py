import unittest
from attributes import Direction
import item
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
        self.fail()
        # self.players.add(player)

    ####################################################################
    def test_remove_player(self):
        self.fail()
        # self.players.remove(player)

    ####################################################################
    def test_find_item(self):
        self.fail()
        # return utils.double_find_by_name(item_name, self.items)

    ####################################################################
    def test_add_item(self):
        self.fail()
        # while len(self.items) >= MAX_ITEMS:
        #     self.items.pop(0)
        # self.items.append(item)

    ####################################################################
    def test_remove_item(self):
        self.fail()
        # self.items.remove(item)

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
        item.item_database = ItemDatabase.load(force=True)
        self.assertEqual(len(item.item_database.by_id), 72)
        self.assertEqual(len(item.item_database.by_name), 72)

        self.assertEqual(item.item_database.find(40).name, "Rusty Knife")
        self.assertEqual(item.item_database.find_full("Dagger").id, 42)
        self.assertEqual(item.item_database.find("Rusty").id, 40)
        self.assertEqual(item.item_database.find("Short").id, 2)

        this_item = item.item_database.find(1)
        self.assertEqual(this_item.id, 1)
        self.assertEqual(this_item.name, "LIES!!!@~")
        self.assertEqual(this_item.type, ItemType.HEALING)
        self.assertEqual(this_item.min, 0)
        self.assertEqual(this_item.max, 0)
        self.assertEqual(this_item.price, 1)
        self.assertEqual(this_item.speed, 0)
        self.assertEqual(this_item.attributes.STRENGTH, 0)
        self.assertEqual(this_item.attributes.HEALTH, 0)
        self.assertEqual(this_item.attributes.AGILITY, 0)
        self.assertEqual(this_item.attributes.MAX_HIT_POINTS, 0)
        self.assertEqual(this_item.attributes.ACCURACY, 0)
        self.assertEqual(this_item.attributes.DODGING, 0)
        self.assertEqual(this_item.attributes.STRIKE_DAMAGE, 0)
        self.assertEqual(this_item.attributes.DAMAGE_ABSORB, 0)
        self.assertEqual(this_item.attributes.HP_REGEN, 0)

        this_item = item.item_database.find("Platemail armor of power")
        self.assertEqual(this_item.id, 55)
        self.assertEqual(this_item.name, "Platemail Armor of Power")
        self.assertEqual(this_item.type, ItemType.ARMOR)
        self.assertEqual(this_item.min, 0)
        self.assertEqual(this_item.max, 0)
        self.assertEqual(this_item.price, 15000)
        self.assertEqual(this_item.speed, 0)
        self.assertEqual(this_item.attributes.STRENGTH, 0)
        self.assertEqual(this_item.attributes.HEALTH, 0)
        self.assertEqual(this_item.attributes.AGILITY, 0)
        self.assertEqual(this_item.attributes.MAX_HIT_POINTS, 0)
        self.assertEqual(this_item.attributes.ACCURACY, 10)
        self.assertEqual(this_item.attributes.DODGING, 60)
        self.assertEqual(this_item.attributes.STRIKE_DAMAGE, 10)
        self.assertEqual(this_item.attributes.DAMAGE_ABSORB, 5)
        self.assertEqual(this_item.attributes.HP_REGEN, 0)
