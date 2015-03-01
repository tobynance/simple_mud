from django.core.management.base import BaseCommand
from logon_handler import LogonHandler
import telnet
import item
import store
import room
import player
import enemy


########################################################################
class Command(BaseCommand):
    help = 'Run the game as a telnet server'

    ####################################################################
    def handle(self, *args, **options):
        store.StoreDatabase.load()
        item.ItemDatabase.load()
        room.RoomDatabase.load()
        enemy.EnemyTemplateDatabase.load()
        enemy.EnemyDatabase.load()
        player.PlayerDatabase.load()
        telnet.MudTelnetProtocol.set_handler_class(handler_class=LogonHandler)
        telnet.run()
