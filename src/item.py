from attributes import ItemType, AttributeSet
from entity import Entity


########################################################################
class Item(Entity):
    ####################################################################
    def __init__(self):
        super(Item, self).__init__()
        self.type = ItemType.ARMOR
        self.min = 0
        self.max = 0
        self.speed = 0
        self.price = 0
        self.attributes = AttributeSet()
