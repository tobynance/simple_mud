from django.core.management.base import BaseCommand
from logon_handler import LogonHandler
import telnet


########################################################################
class Command(BaseCommand):
    help = 'Run the game as a telnet server'

    ####################################################################
    def handle(self, *args, **options):
        telnet.MudTelnetProtocol.set_handler_class(handler_class=LogonHandler)
        telnet.run()
