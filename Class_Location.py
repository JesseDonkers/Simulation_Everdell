class Location:
    """
    Basic location
    Forest location (add constraint for number of workers per player = max 1)
    Basic event
    Special event
    Haven
    Journey
    Destination card
    """
    def __init__(self):
        self.exclusive = False
        self.occupied = False
        self.open = False # Attribute for destination cards
        self.workers = {}  # Tracking workers per player: {player: count}
        self.maxworkers = 0
        self.actions = [] # List of actions available at this location
    
    # Function to check open spaces for workers
    def check_open_spaces(self):
        total_workers = sum(self.workers.values())
        return self.maxworkers - total_workers
    
    # Function to add a worker from a player
    def add_worker(self, player):
        if player not in self.workers:
            self.workers[player] = 0
        self.workers[player] += 1
    
    # Function to remove a worker from a player
    def remove_worker(self, player):
        self.workers[player] -= 1
        if self.workers[player] == 0:
            del self.workers[player]
    
    # Function to get workers of a specific player
    def get_player_workers(self, player):
        return self.workers.get(player, 0)
