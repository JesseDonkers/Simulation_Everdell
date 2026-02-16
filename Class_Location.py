import Class_Action


class Location:
    def __init__(self, name, type, open, maxworkers, action):
        self.name = name
        self.type = type # Basic, forest, event, haven, journey, destination
        self.open = open # Attribute for destination cards
        self.maxworkers = maxworkers
        self.action = action
        self.workers = {}  # Tracking workers per player: {player: count}
        
    def __str__(self):
        return str(self.name)

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
    
    # Function to check open spaces for workers
    def get_open_spaces(self):
        total_workers = sum(self.workers.values())
        return self.maxworkers - total_workers
    
    # Function to get workers of a specific player
    def get_player_workers(self, player):
        return self.workers.get(player, 0)


init_locations = []

# ============================================
# BASIC
# ============================================

twigs = Location("Basic 1", "basic", False, 1, 
                 Class_Action.action_gain_resource("twig", 3))
resins = Location("Basic 2", "basic", False, 1, 
                  Class_Action.action_gain_resource("resin", 2))
pebble = Location("Basic 3", "basic", False, 1, 
                  Class_Action.action_gain_resource("pebble", 1))
berry = Location("Basic 4", "basic", False, 99, 
                 Class_Action.action_gain_resource("berry", 1))


twigs_point = Location("Basic 5", "basic", False, 99, 
                        Class_Action.CompositeAction(
                        [Class_Action.action_gain_resource("twig", 2), 
                        Class_Action.action_gain_points("token", 1)]))
resins_point = Location("Basic 6", "basic", False, 99, 
                        Class_Action.CompositeAction(
                        [Class_Action.action_gain_resource("resin", 1), 
                        Class_Action.action_gain_points("token", 1)]))
cards_point = Location("Basic 7", "basic", False, 99, 
                        Class_Action.CompositeAction(
                        [Class_Action.action_gain_points("token", 1),
                        Class_Action.action_draw_cards_from_deck(2)]))
berry_card = Location("Basic 8", "basic", False, 1, 
                        Class_Action.CompositeAction(
                        [Class_Action.action_gain_resource("berry", 1),
                        Class_Action.action_draw_cards_from_deck(1)]))

init_locations.extend([twigs, resins, pebble, berry])
init_locations.extend([twigs_point, resins_point, cards_point, berry_card])


# ============================================
# FOREST LOCATIONS
# ============================================

# Add constraint for number of workers per player = max 1


# ============================================
# EVENT
# ============================================

# Player will get its worker back, but event stays in the city of the player


# ============================================
# HAVEN
# ============================================


# ============================================
# JOURNEY
# ============================================

# Only accessible in the last season (autumn)
