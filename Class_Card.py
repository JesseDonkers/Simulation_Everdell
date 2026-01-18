class Card:
    def __init__(self):
        self.name = ""
        self.color = ""
        self.requirements = dict(twig=0, resin=0, pebble=0, berry=0)
        self.unique = False
        self.cardsindeck = 0
        self.points = 0
        self.action = None
        
    def __str__(self):
        return str(self.name)

class Critter(Card):
    def __init__(self):
        super().__init__()
        self.relatedcontruction = ""

class Construction(Card):
    def __init__(self):
        super().__init__()
        self.relatedcritter = ""
        self.relatedoccupied = False
