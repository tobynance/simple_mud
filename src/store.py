from entity import Entity


########################################################################
class Store(Entity):
    ####################################################################
    def __init__(self):
        super(Store, self).__init__()
        self.available_items = []
