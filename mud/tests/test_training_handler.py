from django.test import TestCase
from mud.models import Player, Room, User


########################################################################
class TrainingHandlerTest(TestCase):
    fixtures = ["initial_items.json",
                "initial_rooms.json",
                "initial_enemy_templates.json"]

    ####################################################################
    def setUp(self):
        self.user = User.objects.create(username="test.user")
        self.room1 = Room.objects.get(name="Town Square")
        self.room2 = Room.objects.get(id=2)
        self.player = Player.objects.create(name="jerry_john", user=self.user, room=self.room1)

    ####################################################################
    def test_who_text(self):
        m = "<tr><td>jerry_john</td><td class='yellow'>Offline</td></tr>"
        self.assertEqual(self.player.who_text(), m)
