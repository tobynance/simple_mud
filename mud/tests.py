from django.test import TestCase
from mud.models import Player, Room, User
from mud import game_handler

########################################################################
class PlayerTest(TestCase):
    ####################################################################
    def test_print_experience(self):
        u = User.objects.create(username="test.user")
        r = Room.objects.create(name="Town Square")
        p = Player.objects.create(name="test.user", user=u, room=r)
        game_handler.print_experience(p)
# def print_experience(player):
#     """This prints up the experience of the player"""
#     need_for_level = player.need_for_level()
#     response = """<table class='help'>
#         <tr><td>Level:</td><td>{level}</td><td> </td><td> </td></tr>
#         <tr><td>Experience:</td><td>{experience}/{need_for_level} ({exp_percent})</td><td> </td><td> </td></tr>
#     </table>"""
#     context = {"level": player.level,
#                "experience:": player.experience,
#                "need_for_level": need_for_level,
#                "exp_percent": 100 * player.experience // need_for_level}
#     return response.format(**context)
