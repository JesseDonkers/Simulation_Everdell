class Player:
    def __init__(self):
        self.index = 0
        self.strategy = None
        self.hand = [] # Initiate a hand without cards
        self.city = [] # Initiate an empty city without cards
        self.workers = 0 # Initiate the number of workers to zero
        self.season = "winter" # A player starts in winter
        self.points = dict(card=0, token=0, prosperity=0, journey=0, event=0)
        self.resources = dict(twig=0, resin=0, pebble=0, berry=0)
        self.finished = False # Track if the player has finished their game

    def __str__(self):
        a = str("Index: " + str(self.index))
        b = str("Strategy: " + str(self.strategy))
        c = str("Hand: " + str(self.hand))
        d = str("City: " + str(self.city))
        e = str("Workers: " + str(self.workers))
        f = str("Season: " + str(self.season))
        g = str("Points: " + str(self.points))
        h = str("Resources: " + str(self.resources))
        i = str("Finished: " + str(self.finished))

        return (a + "\n" + b + "\n" + c + "\n" + d + "\n" 
                + e + "\n" + f + "\n" + g + "\n" + h + "\n" + i)

    # Function to add cards to the player"s hand or city
    def cards_add(self, listofcards, handorcity):
        target = self.hand if handorcity == "hand" else self.city
        target.extend(listofcards)
        return target
    
    # Function to remove cards from the player"s hand or city
    def cards_remove(self, listofcards, handorcity):
        target = self.hand if handorcity == "hand" else self.city
        for card in listofcards:
            target.remove(card)
        return target
    
    # Function to check the open spaces in hand or city
    def cards_get_open_spaces(self, handorcity):
        target = self.hand if handorcity == "hand" else self.city
        if handorcity == "hand":
            return 8 - len(target) # Max hand size is 8
        else:
            return 15 - len(target) # Max city size is 15

    # Function to add workers
    def workers_add(self, amount):
        self.workers += amount
        return self.workers
    
    # Function to remove workers
    def workers_remove(self, amount):
        self.workers -= amount
        return self.workers

    # Function to add resources to a specific category
    def resources_add(self, resource, amount):
        self.resources[resource] += amount
        return self.resources
    
    # Function to remove resources from a specific category
    def resources_remove(self, resoure, amount):
        self.resources[resoure] -= amount
        return self.resources

    # Function to add points to a specific category
    def points_add(self, category, points):
        self.points[category] += points
        return self.points
    
    # Function to remove points from a specific category
    def points_remove(self, category, points):
        self.points[category] -= points
        return self.points

    # Calculate the total points of the player
    def points_total(self):
        return sum(self.points.values())

    # Function to make a decision based on the strategy and game state
    def decide(self, game_state, decision_kind, options):
        return self.strategy.decide(game_state, decision_kind, options)
