import unittest


########################################################################
class BaseStateDispatchHandlerTest(unittest.TestCase):
    ####################################################################
    def test_handle(self):
        self.fail()


########################################################################
class BaseCommandDispatchHandlerTest(unittest.TestCase):
    ####################################################################
    def test_handle(self):
        self.fail()

    ####################################################################
    def test_check_predicate(self):
        self.fail()

    ####################################################################
    def test_register_data_handler(self):
        self.fail()


########################################################################
class MudTelnetProtocolTest(unittest.TestCase):
    ####################################################################
    def test_connectionMade(self):
        self.fail()

    ####################################################################
    def test_connectionLost(self):
        self.fail("This should be calling hung_up() on the handler")

    ####################################################################
    def test_dataReceived(self):
        self.fail()

    ####################################################################
    def test_set_handler_class(self):
        self.fail()

    ####################################################################
    def test_handler(self):
        self.fail()

    ####################################################################
    def test_create(self):
        self.fail()

    ####################################################################
    def test_get_remote_address(self):
        self.fail()

    ####################################################################
    def test_add_handler(self):
        self.fail()

    ####################################################################
    def test_remove_handler(self):
        self.fail()

    ####################################################################
    def test_clear_handlers(self):
        self.fail()
