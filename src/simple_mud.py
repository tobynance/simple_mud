from logon_handler import LogonHandler
import telnet


########################################################################
if __name__ == "__main__":
    telnet.MudTelnetProtocol.set_handler_class(handler_class=LogonHandler)
    telnet.run()
