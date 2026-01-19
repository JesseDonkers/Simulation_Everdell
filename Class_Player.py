class Player:
    def __init__(self):
        self.hand = [] # Initiate a hand without cards
        self.city = [] # Initiate an empty city without cards
        self.workers = 0 # Initiate the number of workers to zero
        self.season = 'winter' # A player starts in winter
        self.points = dict(cards=0, tokens=0, prosperity=0, journey=0, events=0) # Initiate the points
        self.resources = dict(twig=0, resin=0, pebble=0, berry=0) # Initiate the resources
        self.finished = False # Track if the player has finished their game

    def __str__(self):
        h = str("Hand: " + str(self.hand))
        c = str("City: " + str(self.city))
        w = str("Workers: " + str(self.workers))
        s = str("Season: " + str(self.season))
        p = str("Points: " + str(self.points))
        r = str("Resources: " + str(self.resources))
        f = str("Finished: " + str(self.finished))

        return h + "\n" + c + "\n" + w + "\n" + s + "\n" + p + "\n" + r + "\n" + f

    # Function to check the open spaces in hand or city
    def cards_check_open_spaces(self, handorcity):
        target = self.hand if handorcity == 'hand' else self.city
        if handorcity == 'hand':
            return 8 - len(target) # Max hand size is 8
        else:
            return 15 - len(target) # Max city size is 15

    # Function to add cards to the player's hand or city
    def cards_add(self, listofcards, handorcity):
        target = self.hand if handorcity == 'hand' else self.city
        target.extend(listofcards)
        return target
    
    # Function to remove cards from the player's hand or city
    def cards_remove(self, listofcards, handorcity):
        target = self.hand if handorcity == 'hand' else self.city
        for card in listofcards:
            target.remove(card)
        return target
    
    # Function to count the number of cards in hand or city
    def cards_count(self, handorcity):
        target = self.hand if handorcity == 'hand' else self.city        
        return len(target)

    # Function to advance to the next season
    def season_advance(self):
        seasons = ['winter', 'spring', 'summer', 'autumn']
        current_index = seasons.index(self.season)
        self.season = seasons[(current_index + 1)]
        return self.season

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

    # Caluclate the total points of the player
    def points_total(self):
        return sum(self.points.values())
