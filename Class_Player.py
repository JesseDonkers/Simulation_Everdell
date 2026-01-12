class Player:
    def __init__(self):
        self.cards = [] # Initiate a hand without cards
        self.city = [] # Initiate an empty city without cards
        self.workers = 0 # Initiate the number of workers to zero
        self.season = 'winter' # A player starts in winter

        self.points = dict(cards=0, tokens=0, prosperity=0, journey=0, events=0) # Initiate the points
        self.resources = dict(twig=0, resin=0, pebble=0, berry=0) # Initiate the resources

    def __str__(self):
        return str(self.cards, self.city, self.season, self.workers, self.points, self.resources)

    # Function to add a card to the player's hand
    def cards_add(self, card):
        self.cards.append(card)
        return self.cards
    
    # Function to remove a card from the player's hand
    def cards_discard(self, card):
        self.cards.remove(card)
        return self.cards

    # Function to advance to the next season
    def season_advance(self):
        seasons = ['winter', 'spring', 'summer', 'autumn']
        current_index = seasons.index(self.season)
        self.season = seasons[(current_index + 1)]
        return self.season


# Add card to city
# Remove card from city

# Add workers
# Remove workers


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
