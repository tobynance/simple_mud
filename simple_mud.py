from logon_handler import LogonHandler
import telnet
import item
import store
import room
import player
import enemy


########################################################################
if __name__ == "__main__":
    store.StoreDatabase.load()
    item.ItemDatabase.load()
    room.RoomDatabase.load()
    enemy.EnemyTemplateDatabase.load()
    enemy.EnemyDatabase.load()
    player.PlayerDatabase.load()

    telnet.MudTelnetProtocol.set_handler_class(handler_class=LogonHandler)
    telnet.run()
