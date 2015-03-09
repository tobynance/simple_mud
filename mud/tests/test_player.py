from django.test import TestCase
from mud.models import Player, Room, User
from mud import game_handler


########################################################################
class PlayerTest(TestCase):
    ####################################################################
    def test_print_experience(self):
        print "Users:", User.objects.all().count()
        u = User.objects.create(username="test.user")
        r = Room.objects.create(name="Town Square")
        p = Player.objects.create(name="test.user", user=u, room=r)
        game_handler.print_experience(p)
