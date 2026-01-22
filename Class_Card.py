class Card:
    def __init__(self, name, color, requirements, cardsindeck, unique, points, action):
        self.name = name
        self.color = color
        self.requirements = requirements # dict(twig=0, resin=0, pebble=0, berry=0)
        self.cardsindeck = cardsindeck
        self.unique = unique
        self.points = points
        self.action = action
        
    def __str__(self):
        return str(self.name)

class Critter(Card):
    def __init__(self, name, color, requirements, cardsindeck, unique, points, action, relatedconstruction):
        super().__init__(name, color, requirements, cardsindeck, unique, points, action)
        self.relatedconstruction = relatedconstruction

class Construction(Card):
    def __init__(self, name, color, requirements, cardsindeck, unique, points, action, relatedcritters):
        super().__init__(name, color, requirements, cardsindeck, unique, points, action)
        self.relatedcritters = relatedcritters
        self.relatedoccupied = False
