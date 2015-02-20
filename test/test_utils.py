import tempfile
import shutil
from contextlib import contextmanager
from telnet import MudTelnetProtocol


########################################################################
@contextmanager
def temp_dir(suffix, prefix="tmp"):
    td = tempfile.mkdtemp(prefix=prefix, suffix=suffix)
    try:
        yield td
    finally:
        shutil.rmtree(td, ignore_errors=True)


########################################################################
class MockProtocol(MudTelnetProtocol):
    ####################################################################
    def __init__(self):
        MudTelnetProtocol.__init__(self)
        self.handlers = []
        self.handlers.append(self.handler_class(self))
        self.drop_connection_calls = 0
        self.send_data = []

    ####################################################################
    def get_remote_address(self):
        return "192.168.99.99"

    ####################################################################
    def drop_connection(self):
        self.drop_connection_calls += 1

    ####################################################################
    def send(self, data):
        self.send_data.append(data)


welcome_message = """\
<magenta><bold>Welcome to SimpleMUD, jerry!\r
You must train your character with your desired stats,\r
before you enter the realm.\r\n\r\n"""

stats_message = """\
<white><bold>---------------------- Your Stats ----------------------\r
<dim>Player: jerry\r
Stat Points Left: 18\r
1) Strength: 1\r
2) Health: 1\r
3) Agility: 1\r
<bold>--------------------------------------------------------\r
Enter 1, 2, or 3 to add a stat point, or "quit" to go back: """
