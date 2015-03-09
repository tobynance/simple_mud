from django.test import TestCase
from mud.models import Player, Room, User
from mud import game_handler


########################################################################
class PlayerTest(TestCase):
    ####################################################################
    def test_print_experience(self):
        self.assertEqual(User.objects.all().count(), 0)
        u = User.objects.create(username="test.user")
        r = Room.objects.create(name="Town Square")
        p = Player.objects.create(name="test.user", user=u, room=r)
        content = game_handler.print_experience(p)
        self.assertEqual(content, "b")
